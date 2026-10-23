# Repository Audit: Food Delivery Order Queue Manager

**Project:** Food Delivery Order Queue Manager (`delivery_system.py`)  
**Student:** Aarav Yuval B G (USN: PES1UG24AM004)  
**Repository:** https://github.com/SETAPESU26/L5_05_food_delivery.git  
**Working Branch:** `lab5-pes1ug24am004-static-analysis`  
**Date:** 2026-10-23  

---

## 1. Inventory of Files

| File | Type | Description |
|---|---|---|
| `delivery_system.py` | Python Script | Primary application file (71 lines). Implements in-memory order queue, pricing calculation, status updates, disk backup/restore, and a demo driver in `main()`. |
| `README.md` | Markdown Documentation | Assignment instructions, workflow guidance, tool execution instructions, and deliverable specifications. |
| `.gitignore` | Git Configuration | Specifies ignore patterns (`__pycache__/`, `.venv/`). |

---

## 2. Application Workflow and Architecture

The application is an in-memory queue manager for a food delivery kitchen:

1. **Menu Configuration (`read_menu_config`):**
   - Attempts to read menu prices from `menu.json`.
   - Defaults to a hard-coded fallback dictionary (`{"pizza": 250, "burger": 150, "fries": 90, "coke": 40}`) if the file is absent or fails to load.

2. **Order Creation (`create_order`):**
   - Receives customer name, list of item names, and an optional order history list.
   - Computes total cost using `menu.get(i, 99)`.
   - Increments global `next_id` and records the order dictionary into global `orders`.
   - Appends order ID to `order_history` and returns the new order ID.

3. **Order Status Progression (`update_order_status`):**
   - Updates `orders[order_id]["status"]` to a new status.
   - Intended to accept `placed`, `cooking`, `out_for_delivery`, or `delivered`.

4. **Revenue Calculation (`daily_revenue`):**
   - Sums the `total` of all orders whose status is `"delivered"`.

5. **Persistence (`backup_orders`, `restore_orders`):**
   - Serializes and deserializes the `orders` dictionary to/from `orders.pkl` using Python's `pickle` module.

6. **Queue Reporting (`printQueue`):**
   - Prints timestamped summary of order IDs, customer names, statuses, and order totals.

7. **Entry Point (`main`):**
   - Orchestrates sample orders (including invalid items, invalid statuses, and empty inputs), displays revenue, tests backup/restore, and prints queue.

---

## 3. Current State and Discovered Flaws

Running `delivery_system.py` in its baseline state produces:
```
Revenue today: 290
Order queue at 2026-10-23 08:52:14.255465
1 Asha delivered 290
2 Ravi teleported 249
3  delivered 0
```

### Critical Flaws Identified:
1. **Security Vulnerability (Bandit B301, B403):** Use of `pickle` for order serialization and deserialization allows arbitrary code execution if an untrusted `orders.pkl` is loaded.
2. **Error Suppression & Missing Status Validation (Bandit B110, Flake8 E722, Pylint W0702):** `update_order_status` uses bare `except: pass`, silently swallowing `KeyError` on nonexistent orders and allowing arbitrary, invalid statuses (e.g., `"teleported"`).
3. **Dangerous Mutable Default Argument (Pylint W0102):** `order_history=[]` retains state across separate function calls when not passed explicitly.
4. **Input Validation Deficiencies:** Empty customer names (`""`) and empty item lists (`[]`) are accepted without validation. Unknown items silently fall back to an arbitrary hard-coded cost of 99.
5. **Resource Leaks (Pylint R1732, W1514):** Files are opened without context managers (`with open(...)`) and without explicit character encodings in `read_menu_config`, `backup_orders`, and `restore_orders`.
6. **Code Style & PEP 8 Violations (Pylint C0103, C0114, C0116, C0209; Flake8 E302, E501, E305):** Missing module and function docstrings, non-snake_case function name `printQueue`, non-conforming constant naming, lines over 79 characters, insufficient blank lines, and percent-formatting instead of f-strings.
7. **Module Execution Side-Effect:** `main()` is invoked at top level unconditionally rather than guarded by `if __name__ == "__main__":`.

---

## 4. Existing Test and Tool Configuration

- **Test Suite:** No existing test suite was provided in the repository. A focused test suite (`test_delivery_system.py`) using `unittest` / `pytest` will be added to test all core operations, validation rules, error cases, and safe persistence.
- **Static Analysis Tools:** Configured and verified in `.venv`:
  - Python: 3.12.10
  - Pylint: 4.1.3
  - Bandit: 1.9.4
  - Flake8: 7.4.1
- **Tool Baseline Metrics:**
  - Pylint Score: 6.27 / 10
  - Bandit Findings: 3 issues (1 Medium, 2 Low)
  - Flake8 Violations: 12 violations
