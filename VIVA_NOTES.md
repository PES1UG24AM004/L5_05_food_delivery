# Viva & Presentation Guide: Food Delivery Static Code Analysis

**Student:** Aarav Yuval B G  
**USN:** PES1UG24AM004  
**Project:** Food Delivery Order Queue Manager (`delivery_system.py`)  
**Tools:** Pylint, Bandit, Flake8  

---

## 1. What the Application Does
The application is a backend order queue manager for a food delivery service. It loads a menu configuration, places orders, validates items, computes customer bill totals, transitions order status from placement to delivery, aggregates daily revenue, and persists the active queue to disk for backup and restore.

## 2. Main Workflow
1. **Config:** Loads menu pricing from `menu.json` (or uses built-in default prices).
2. **Order Placement:** Customers create orders with dish lists; total prices are computed and stored in an in-memory queue.
3. **Status Lifecycle:** Order status transitions through `placed` -> `cooking` -> `out_for_delivery` -> `delivered`.
4. **Accounting:** `daily_revenue()` calculates financial earnings strictly from delivered orders.
5. **Persistence:** `backup_orders()` saves orders to disk; `restore_orders()` reloads the queue state into memory.

## 3. What Static Code Analysis Means
Static code analysis inspects source code without running it. It parses code into an Abstract Syntax Tree (AST) to evaluate syntax, structure, security hazards, potential runtime bugs, and styling adherence before testing or deployment.

## 4. Role of Each Tool
- **Pylint:** Deep semantic analyzer and code quality rater. Checks for logic flaws, mutable default arguments, unclosed resources, docstrings, and naming standards. (Produces a score out of 10).
- **Bandit:** Security scanner built for Python. Scans for Common Weakness Enumeration (CWE) vulnerabilities such as insecure deserialization (`pickle`) and suppressed error blocks.
- **Flake8:** Lightweight, fast linter. Checks PEP 8 formatting rules, line lengths (<= 79 chars), indentation, and syntax problems.

## 5. Key Bugs & Vulnerabilities Found
1. **Pickle Deserialization (Bandit B301, B403):** Using `pickle.load()` on disk files creates an arbitrary code execution vulnerability if an untrusted file is provided.
2. **Silent Failure / Bare Except (Bandit B110, Flake8 E722, Pylint W0702):** `try...except: pass` in status updates silently ignored invalid order IDs and allowed arbitrary statuses like `"teleported"`.
3. **Mutable Default Parameter (Pylint W0102):** `create_order(..., order_history=[])` reused the exact same list across multiple calls, leaking order history between users.
4. **Missing Input Validation (Logic Defect):** Empty customer names, empty item lists, and unknown items were allowed (with unknown items silently costing 99).
5. **Resource Leaks (Pylint R1732, W1514):** Files opened without `with open(...)` and without specifying UTF-8 encoding.

## 6. How the Fixes Work (Simple Explanation)
- **Pickle -> JSON:** Swapped `pickle` for `json.dump` / `json.load`. Added an integer-conversion loop so order ID numbers remain integers in Python.
- **Bare Except -> Validation:** Removed `try/except: pass`. Added `if order_id not in orders` and `if status not in VALID_STATUSES`.
- **Default Argument -> Sentinel:** Changed default to `order_history=None` and initialized `order_history = []` inside the function.
- **Input Validation:** Added `ValueError` checks for customer name, item presence on menu, and non-empty item lists.
- **Resource Cleanup:** Used `with open(..., encoding="utf-8") as f:` for all file operations.
- **PEP 8:** Formatted lines to <= 79 characters, added 2 blank lines around functions, and added descriptive docstrings.

## 7. Genuine Before & After Results
- **Pylint:** 6.27 / 10 -> **10.00 / 10**
- **Bandit:** 3 issues -> **0 issues**
- **Flake8:** 12 violations -> **0 violations**
- **Automated Tests:** 0 tests -> **12 tests passed (100%)**

## 8. What Automated Tests Prove
The 12 unit tests prove that:
- Core operations (order placement, menu fallback, revenue calculation) work correctly.
- Invalid statuses (like "teleported") and non-existent IDs are properly rejected.
- Invalid customer names and items raise `ValueError` as expected.
- Backup and restore via JSON preserves all data without data loss or type corruption.

## 9. What Static Analysis Cannot Guarantee
Static analysis cannot guarantee business correctness. Linters check syntax and standard practices, but cannot know whether charging 99 for unknown dishes or accepting empty orders makes business sense. Automated unit tests and human code review are essential to ensure the code behaves as intended.

## 10. The Three Git Commits
1. `Fix Pylint code quality and correctness issues`: Code quality refactoring, docstrings, resource handling, input validation, and mutable argument fix.
2. `Resolve Bandit security findings`: Removed `pickle`, implemented safe JSON persistence, and added the 12-case test suite.
3. `Fix Flake8 style issues and finalize lab deliverables`: PEP 8 formatting, report generation, and final documentation deliverables.

---

## 11. Six Likely Viva Questions & Model Answers

### Q1: Why is Python's `pickle` considered dangerous for data persistence?
**Answer:** `pickle` is not just a data format; it is an execution protocol. When `pickle.load()` deserializes a byte stream, it can call arbitrary callable objects and methods (such as `os.system` via `__reduce__`). If an attacker replaces `orders.pkl` with a malicious payload, the application will execute arbitrary code with the application's operating system privileges. JSON avoids this because it only represents text data structures.

### Q2: What causes the Pylint "dangerous-default-value" (W0102) warning?
**Answer:** In Python, default parameter values are evaluated once when the function is defined, not upon invocation. If a mutable object like a list `[]` is used as a default, that single list is shared across all function calls that omit the parameter. Modifying it in one call contaminates all subsequent calls. The fix is to use `None` as the default and initialize a new list inside the function.

### Q3: Why is a bare `except:` block considered bad practice?
**Answer:** A bare `except:` catches `BaseException`, including `SystemExit`, `KeyboardInterrupt`, and `MemoryError`. This prevents the developer from halting the program with Ctrl+C and masks critical programming bugs (like typos or `KeyError`). Furthermore, combining it with `pass` silently swallows failures without logging, making debugging nearly impossible.

### Q4: What is the difference between PyFlakes and PyCodeStyle in Flake8?
**Answer:** Flake8 bundles PyFlakes and PyCodeStyle. PyFlakes analyzes semantic errors (such as undefined variables, unused imports, or duplicate arguments) without executing the code. PyCodeStyle checks visual layout and styling against PEP 8 rules (line lengths, blank lines, indentation, and spacing).

### Q5: If your code receives a perfect 10.00/10 on Pylint, can you assume it is bug-free?
**Answer:** No. Pylint evaluates structural syntax, idioms, and documentation adherence. It cannot verify domain business rules. For example, a function calculating bill totals with incorrect tax arithmetic would still receive a 10.00/10 from Pylint as long as its variables, docstrings, and structure are clean. Dynamic automated tests are necessary to verify runtime behavior.

### Q6: How does using a context manager (`with open(...)`) prevent resource leaks on Windows?
**Answer:** An unclosed file handle consumes an operating system file descriptor. On Windows, open file descriptors lock the underlying file, preventing deletion, renaming, or access by other processes. If an exception occurs before `.close()` is called, the file remains locked. A `with` statement guarantees that `__exit__` is called, closing the file handle immediately, even if an exception is raised.
