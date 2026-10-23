# Issues Log: Food Delivery Order Queue Manager

**Student Name:** Aarav Yuval B G  
**USN:** PES1UG24AM004  
**Target File:** `delivery_system.py`  
**Repository:** https://github.com/SETAPESU26/L5_05_food_delivery.git  

---

## 1. Summary of Issues

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Insecure Deserialization via Pickle | Bandit B301 / B403 (Security: Medium / Low) | 2, 43, 49 | The application imports `pickle` and calls `pickle.load()` on `orders.pkl`. Python's `pickle` module allows arbitrary code execution during deserialization if untrusted data is supplied. | Removed `import pickle`. Replaced persistence with standard `json` serialization (`backup_orders` and `restore_orders`), converting deserialized keys back to integers for consistent dictionary indexing. Verified with Bandit (0 issues). |
| Error Suppression via Bare Except | Bandit B110 / Pylint W0702 / Flake8 E722 | 24–25 | In `update_order_status`, a bare `except: pass` block silently suppresses all exceptions (including `KeyError` on invalid order IDs, `KeyboardInterrupt`, etc.), hiding errors from caller and operators. | Removed `try...except: pass`. Replaced with explicit pre-condition checks verifying order existence in `orders` and returning boolean status indicators with clear diagnostic messages. |
| Dangerous Mutable Default Argument | Pylint W0102 (Correctness / Warning) | 11 | `create_order(customer, items, order_history=[])` binds an empty list at function definition time. Subsequent calls that do not provide an argument mutate and share the same list instance across calls. | Changed parameter default to `order_history=None` and initialized `if order_history is None: order_history = []` inside the function body. Verified independence across calls with automated tests. |
| Missing Order Status Validation | Manual Review / Logic Defect | 21–25 | `update_order_status` accepts arbitrary string statuses without validating against `VALID_STATUSES`. In `main()`, order `b` was set to the invalid status `"teleported"`. | Added explicit validation ensuring `status in VALID_STATUSES`. Returns `False` and issues a diagnostic error if an invalid status is passed. Verified via unit test `test_update_order_status_invalid_status_rejected`. |
| Missing Input Validation & Arbitrary Fallback Pricing | Manual Review / Logic Defect | 11–16 | `create_order` accepted empty customer names (`""`) and empty item lists (`[]`). Furthermore, non-existent menu items were silently billed at an arbitrary default of 99 (`menu.get(i, 99)`), masking order entry mistakes. | Added validation raising `ValueError` if customer name is non-string or whitespace-only, if items list is empty, or if an item is not present in `menu`. Handled gracefully in `main()` and verified in unit tests. |
| Unmanaged File Resources and Missing Character Encoding | Pylint R1732 / W1514 (Resource Management) | 30, 43, 49 | Files were opened using bare `open()` calls without context managers (`with` statements) and without explicit `encoding="utf-8"`, risking resource descriptor leaks and platform-dependent decoding issues. | Wrapped all file operations in `with open(..., encoding="utf-8")` blocks, guaranteeing automatic file handle closure upon block exit across `read_menu_config`, `backup_orders`, and `restore_orders`. |
| Broad Exception Catching | Pylint W0718 (Code Quality) | 32 | `read_menu_config` caught broad `Exception`, catching bugs unrelated to file presence or parsing (such as `KeyboardInterrupt` or unexpected attribute errors). | Replaced `except Exception:` with specific expected exception types `except (FileNotFoundError, json.JSONDecodeError, OSError):` falling back to `FALLBACK_MENU`. |
| Code Formatting, Naming Conventions, and Missing Documentation | Pylint C0114, C0116, C0103, C0209; Flake8 E302, E501, E305 | 1–71 | Missing module and function docstrings, non-snake_case function name `printQueue`, line lengths exceeding 79 characters, insufficient blank lines around functions, and un-guarded global script execution. | Added comprehensive docstrings to module and all functions, renamed `printQueue` to `print_queue`, formatted code to strict PEP 8 (<= 79 chars, 2 blank lines), replaced `%` formatting with f-strings, and guarded `main()` with `if __name__ == "__main__":`. |

---

## 2. Issue Breakdown by Tool Origin

### Static Analysis Security Findings (Bandit)
- **B403 (`import pickle`):** High confidence, Low severity. Unsafe module import.
- **B301 (`pickle.load()`):** High confidence, Medium severity. Potential remote code execution vulnerability.
- **B110 (`try: ... except: pass`):** High confidence, Low severity. Silent failure pattern in order status updates.

### Static Analysis Quality Findings (Pylint)
- **W0102 (`dangerous-default-value`):** Mutable default argument `order_history=[]`.
- **W0702 (`bare-except`):** No exception types specified in status handler.
- **W0718 (`broad-exception-caught`):** Catching general `Exception` in configuration loader.
- **W1514 (`unspecified-encoding`):** Unspecified encoding in `open()`.
- **R1732 (`consider-using-with`):** Unmanaged file resources.
- **C0103 (`invalid-name`):** Module-level variable `next_id` and function `printQueue`.
- **C0114 / C0116:** Missing module and function docstrings.
- **C0209 (`consider-using-f-string`):** Legacy `%` string formatting.

### Static Analysis Style Findings (Flake8)
- **E722:** Bare `except` on line 24.
- **E501:** Lines exceeding 79 characters (lines 16, 54).
- **E302:** Expected 2 blank lines before top-level function definitions (lines 11, 21, 27, 35, 42, 47, 51, 56).
- **E305:** Expected 2 blank lines after class/function definition (line 70).

### Manual Review Findings
- **Data Integrity:** `update_order_status` accepted illegal statuses like `"teleported"`.
- **Input Validation:** Empty customer name `""` and empty items `[]` created dummy zero-value orders.
- **Pricing Correctness:** Unknown dishes were silently assigned a price of 99 rather than rejecting invalid items or alerting kitchen staff.
- **Top-Level Execution:** `main()` executed upon module import, preventing clean importing in test runners.

---

## 3. Verification Summary

All issues were remediated and verified through automated test suites and re-running static analysis tools:
- **Pylint Score:** Raised from **6.27/10** to **10.00/10**.
- **Bandit Findings:** Reduced from **3 issues** to **0 issues**.
- **Flake8 Violations:** Reduced from **12 violations** to **0 violations**.
- **Automated Tests:** 12 passed out of 12 tests (`pytest` and `unittest`).
