"""Food delivery order queue manager module.

Provides order creation, menu loading, status tracking, revenue
calculation, and order persistence.
"""

from datetime import datetime
import json

# Global application state containers
orders = {}
menu = {}
_state = {"next_id": 1}

VALID_STATUSES = ["placed", "cooking", "out_for_delivery", "delivered"]
FALLBACK_MENU = {"pizza": 250, "burger": 150, "fries": 90, "coke": 40}


def create_order(customer, items, order_history=None):
    """Create a new order, calculate its total, and add it to the queue.

    Args:
        customer (str): The customer name.
        items (list): List of menu item names.
        order_history (list, optional): Tracker for order IDs.

    Returns:
        int: The newly assigned order ID.

    Raises:
        ValueError: If customer name is empty or items list is invalid.
    """
    if order_history is None:
        order_history = []

    if not isinstance(customer, str) or not customer.strip():
        raise ValueError("Customer name must be a non-empty string.")

    if not isinstance(items, (list, tuple)) or len(items) == 0:
        raise ValueError("Order must contain at least one item.")

    total = 0
    for item in items:
        if item not in menu:
            raise ValueError(f"Item '{item}' is not on the menu.")
        total += menu[item]

    order_id = _state["next_id"]
    orders[order_id] = {
        "customer": customer.strip(),
        "items": list(items),
        "total": total,
        "status": "placed",
    }
    order_history.append(order_id)
    _state["next_id"] += 1
    return order_history[-1]


def update_order_status(order_id, status):
    """Update delivery status for an existing order.

    Args:
        order_id (int): Order ID to update.
        status (str): New status value.

    Returns:
        bool: True if status updated successfully, False otherwise.
    """
    if order_id not in orders:
        print(f"Error: Order ID {order_id} does not exist.")
        return False

    if status not in VALID_STATUSES:
        print(
            f"Error: Invalid status '{status}'. "
            f"Must be one of {VALID_STATUSES}"
        )
        return False

    orders[order_id]["status"] = status
    return True


def read_menu_config(file="menu.json"):
    """Load menu prices from a JSON file, or fall back to defaults.

    Args:
        file (str): Path to menu JSON configuration file.
    """
    try:
        with open(file, "r", encoding="utf-8") as menu_file:
            loaded_menu = json.load(menu_file)
            menu.clear()
            menu.update(loaded_menu)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        menu.clear()
        menu.update(FALLBACK_MENU)


def daily_revenue():
    """Calculate total revenue from delivered orders.

    Returns:
        int or float: Sum of totals for orders with status 'delivered'.
    """
    return sum(
        order["total"]
        for order in orders.values()
        if order.get("status") == "delivered"
    )


def backup_orders(file="orders.json"):
    """Back up order queue to a JSON file.

    Args:
        file (str): Output file path.
    """
    with open(file, "w", encoding="utf-8") as backup_file:
        json.dump(orders, backup_file, indent=2)


def restore_orders(file="orders.json"):
    """Restore order queue from a JSON backup file.

    Args:
        file (str): Input file path.
    """
    with open(file, "r", encoding="utf-8") as backup_file:
        loaded = json.load(backup_file)
        orders.clear()
        for order_id_str, order_data in loaded.items():
            orders[int(order_id_str)] = order_data


def reset_system():
    """Reset the order queue and next order ID generator to initial state."""
    orders.clear()
    _state["next_id"] = 1


def print_queue():
    """Print the current order queue with customer details and status."""
    print(f"Order queue at {datetime.now()}")
    for order_id, order in orders.items():
        print(
            f"{order_id} {order['customer']} "
            f"{order['status']} {order['total']}"
        )


def main():
    """Orchestrate demonstration of order queue workflow."""
    read_menu_config()

    # Valid orders
    order_a = create_order("Asha", ["pizza", "coke"])
    update_order_status(order_a, "delivered")

    # Order with invalid item handled gracefully
    try:
        create_order("Ravi", ["burger", "sushi"])
    except ValueError as exc:
        print(f"Rejected invalid order for Ravi: {exc}")
        order_b = create_order("Ravi", ["burger", "fries"])
        update_order_status(order_b, "cooking")

    # Order with empty customer handled gracefully
    try:
        create_order("", [])
    except ValueError as exc:
        print(f"Rejected empty order: {exc}")

    # Invalid status update demonstrated
    update_order_status(order_a, "teleported")

    # Missing order ID update demonstrated
    update_order_status(42, "delivered")

    print(f"Revenue today: {daily_revenue()}")
    backup_orders()
    restore_orders()
    print_queue()


if __name__ == "__main__":
    main()
