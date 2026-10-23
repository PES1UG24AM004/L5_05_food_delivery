"""Automated test suite for food delivery order queue manager.

Tests order creation, validation, status progression, revenue calculation,
fallback configuration, and secure JSON persistence.
"""

import json
import os
import tempfile
import unittest

import delivery_system


class TestDeliverySystem(unittest.TestCase):
    """Unit test suite for delivery_system module functionality."""

    def setUp(self):
        """Reset application state before each test case."""
        delivery_system.reset_system()
        delivery_system.read_menu_config("__nonexistent_menu_file__.json")

    def tearDown(self):
        """Clean up state after each test case."""
        delivery_system.reset_system()

    def test_default_menu_loaded(self):
        """Test default menu fallback loads expected standard prices."""
        self.assertIn("pizza", delivery_system.menu)
        self.assertEqual(delivery_system.menu["pizza"], 250)
        self.assertEqual(delivery_system.menu["burger"], 150)
        self.assertEqual(delivery_system.menu["fries"], 90)
        self.assertEqual(delivery_system.menu["coke"], 40)

    def test_read_menu_config_from_valid_file(self):
        """Test reading custom menu configuration from a valid JSON file."""
        custom_menu = {"noodles": 120, "ice_cream": 80}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(custom_menu, tmp)
            tmp_path = tmp.name

        try:
            delivery_system.read_menu_config(tmp_path)
            self.assertEqual(delivery_system.menu, custom_menu)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_create_valid_order(self):
        """Test creating an order with valid customer and menu items."""
        order_id = delivery_system.create_order("Asha", ["pizza", "coke"])
        self.assertEqual(order_id, 1)
        self.assertIn(1, delivery_system.orders)
        order = delivery_system.orders[1]
        self.assertEqual(order["customer"], "Asha")
        self.assertEqual(order["items"], ["pizza", "coke"])
        self.assertEqual(order["total"], 290)
        self.assertEqual(order["status"], "placed")

    def test_create_order_empty_customer_rejected(self):
        """Test that empty or whitespace customer names raise ValueError."""
        with self.assertRaises(ValueError):
            delivery_system.create_order("", ["pizza"])
        with self.assertRaises(ValueError):
            delivery_system.create_order("   ", ["pizza"])

    def test_create_order_empty_items_rejected(self):
        """Test that an empty item list raises ValueError."""
        with self.assertRaises(ValueError):
            delivery_system.create_order("Ravi", [])

    def test_create_order_invalid_item_rejected(self):
        """Test ordering an item not present on the menu raises ValueError."""
        with self.assertRaises(ValueError):
            delivery_system.create_order("Ravi", ["burger", "sushi"])

    def test_create_order_history_independence(self):
        """Test that default order_history does not leak state across calls."""
        hist_1 = []
        id1 = delivery_system.create_order("User1", ["pizza"], hist_1)
        hist_2 = []
        id2 = delivery_system.create_order("User2", ["burger"], hist_2)

        self.assertEqual(hist_1, [id1])
        self.assertEqual(hist_2, [id2])

        # Test with default argument
        id3 = delivery_system.create_order("User3", ["fries"])
        self.assertEqual(id3, 3)

    def test_update_order_status_success(self):
        """Test valid status transitions for an existing order."""
        order_id = delivery_system.create_order("Asha", ["pizza"])
        self.assertTrue(
            delivery_system.update_order_status(order_id, "cooking")
        )
        self.assertEqual(
            delivery_system.orders[order_id]["status"], "cooking"
        )

        self.assertTrue(
            delivery_system.update_order_status(order_id, "out_for_delivery")
        )
        self.assertTrue(
            delivery_system.update_order_status(order_id, "delivered")
        )
        self.assertEqual(
            delivery_system.orders[order_id]["status"], "delivered"
        )

    def test_update_order_status_invalid_status_rejected(self):
        """Test that invalid statuses like 'teleported' are rejected."""
        order_id = delivery_system.create_order("Ravi", ["burger"])
        result = delivery_system.update_order_status(order_id, "teleported")
        self.assertFalse(result)
        self.assertEqual(delivery_system.orders[order_id]["status"], "placed")

    def test_update_order_status_nonexistent_order_rejected(self):
        """Test that updating a nonexistent order returns False."""
        result = delivery_system.update_order_status(999, "delivered")
        self.assertFalse(result)

    def test_daily_revenue_calculation(self):
        """Test daily revenue calculation sums only delivered orders."""
        o1 = delivery_system.create_order("Asha", ["pizza", "coke"])  # 290
        o2 = delivery_system.create_order("Ravi", ["burger", "fries"])  # 240
        o3 = delivery_system.create_order("Kiran", ["coke"])  # 40

        delivery_system.update_order_status(o1, "delivered")
        delivery_system.update_order_status(o2, "cooking")
        delivery_system.update_order_status(o3, "placed")

        # Only o1 is delivered: 290
        self.assertEqual(delivery_system.daily_revenue(), 290)

        delivery_system.update_order_status(o2, "delivered")
        # o1 + o2: 290 + 240 = 530
        self.assertEqual(delivery_system.daily_revenue(), 530)

    def test_safe_backup_and_restore_json(self):
        """Test safe order queue backup and restoration using JSON."""
        delivery_system.create_order("Asha", ["pizza"])
        delivery_system.create_order("Ravi", ["burger"])

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name

        try:
            delivery_system.backup_orders(tmp_path)
            self.assertTrue(os.path.exists(tmp_path))

            # Clear in-memory orders
            delivery_system.orders.clear()
            self.assertEqual(len(delivery_system.orders), 0)

            # Restore orders from file
            delivery_system.restore_orders(tmp_path)
            self.assertEqual(len(delivery_system.orders), 2)
            self.assertIn(1, delivery_system.orders)
            self.assertIn(2, delivery_system.orders)
            self.assertEqual(delivery_system.orders[1]["customer"], "Asha")
            self.assertEqual(delivery_system.orders[2]["customer"], "Ravi")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
