# Presentation Summary: Food Delivery Static Code Analysis

**Student:** Aarav Yuval B G (USN: PES1UG24AM004)  
**Course:** Software Engineering Lab (Lab 5)  
**Target:** `delivery_system.py`  

---

### Objective
Audit, refactor, and harden a food delivery order queue manager using static code analysis tools (Pylint, Bandit, Flake8), address all actionable issues, establish automated test verification, and record changes across three structured Git commits.

---

### Key Findings in Baseline Code
- **Security (Bandit):** Insecure deserialization via `pickle` allowing arbitrary code execution (CWE-502), and silent failure via bare `except: pass` (CWE-703).
- **Code Quality (Pylint):** Mutable default argument `order_history=[]` leaking state across calls, unclosed file descriptors, missing docstrings, and old string formatting. Score: 6.27/10.
- **Style (Flake8):** 12 violations of PEP 8 including line lengths over 79 characters, bare `except`, and non-standard whitespace.
- **Business Logic (Manual Review):** Allowed invalid order statuses (`"teleported"`), accepted empty customer names and items, and billed unknown items at arbitrary fallback prices (99).

---

### Key Improvements Made
1. **Security:** Replaced `pickle` with safe `json.dump`/`json.load` persistence with integer key restoration. Eliminated bare exception handling.
2. **Correctness:** Replaced mutable default argument with `None` sentinel. Added strict customer name and menu item validation.
3. **Robustness:** Added explicit pre-condition checks for order existence and status transitions (`placed` -> `cooking` -> `out_for_delivery` -> `delivered`).
4. **Clean Code & Style:** Implemented PEP 8 layout (<= 79 characters, 2 blank lines), complete docstrings, and context managers (`with open(..., encoding="utf-8")`).
5. **Testing:** Added 12-test automated unit test suite covering normal flow, edge cases, error conditions, and safe persistence.

---

### Verification Outcomes

| Tool / Metric | Before | After | Status |
|---|---|---|---|
| **Pylint Score** | 6.27 / 10 | **10.00 / 10** | **Passed** (> 9.5 target) |
| **Bandit Issues** | 3 (1 Med, 2 Low) | **0 Issues** | **Passed** (All resolved) |
| **Flake8 Violations** | 12 violations | **0 Violations** | **Passed** (Strict PEP 8) |
| **Automated Tests** | None (0) | **12 / 12 Passed** | **Passed** (100% success) |

---

### Three Git Commits
1. `Fix Pylint code quality and correctness issues` — Mutable default, error handling, docstrings, validation.
2. `Resolve Bandit security findings` — Replaced pickle with JSON, added unit test suite.
3. `Fix Flake8 style issues and finalize lab deliverables` — PEP 8 formatting, final reports, documentation.

---

### Core Learning Points
- **Defense in Depth:** Pylint, Bandit, and Flake8 address distinct layers: quality, security, and formatting.
- **Fail Fast:** Never hide errors behind `try/except: pass`. Validate pre-conditions explicitly.
- **Format Safety:** Deserializing untrusted byte streams with `pickle` is dangerous; structured formats like JSON protect data integrity.
- **Testing Complements Analysis:** Static linters enforce structure and hygiene; unit tests verify business logic.
