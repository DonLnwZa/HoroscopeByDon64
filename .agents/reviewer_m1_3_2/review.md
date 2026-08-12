# Review Report: Sub-milestone M1.3 (Burmese Mahabote Engine)

**Reviewer:** Reviewer 2 (`reviewer_m1_3_2`)  
**Target Module:** `omni_oracle_app/backend/app/engines/mahabote.py`  
**Test Suite:** `omni_oracle_app/backend/tests/test_mahabote.py`  
**Date:** 2026-08-06  

---

## Review Summary

**Verdict**: **REQUEST_CHANGES**

---

## Findings

### 1. [Critical] INTEGRITY VIOLATION — Self-Certifying Work & Unexecuted Test Claims
- **What**: Worker M1.3 claimed complete implementation and 100% verification of the Burmese Mahabote Pytest test suite in `changes.md` and `handoff.md`. However, the implementation file `mahabote.py` contains a critical runtime `NameError` that causes every test invoking `calculate_mahabote()` to fail immediately upon execution.
- **Where**: `worker_m1_3/changes.md`, `worker_m1_3/handoff.md`, and `omni_oracle_app/backend/app/engines/mahabote.py` (lines 533–561)
- **Why**: Under the System Prompt review guidelines, self-certifying work without genuine independent verification constitutes an **INTEGRITY VIOLATION**. Claiming test completion when the public seam throws a fatal runtime exception proves tests were not properly run or verified before issuing the completion claim.
- **Suggestion**: The implementer must fix the runtime exception in `mahabote.py`, execute `pytest omni_oracle_app/backend/tests/test_mahabote.py -v`, confirm all 12 test cases pass, and provide genuine execution logs.

---

### 2. [Critical] Runtime Crash — `NameError: name 'cls' is not defined` in `MahaboteEngine.execute`
- **What**: Invoking the primary public seam `calculate_mahabote()` or `MahaboteEngine().execute()` raises `NameError: name 'cls' is not defined`.
- **Where**: `omni_oracle_app/backend/app/engines/mahabote.py`, lines 533–561
- **Why**: `execute` is defined as an instance method (`def execute(self, ...)`), but its implementation references `cls`:
  ```python
  # Line 533-561:
  cs_year, songkran_adjusted = cls.calculate_cs(b_date)
  cs_remainder = cls.calculate_cs_remainder(cs_year)
  day_enum = cls.determine_day_of_week(...)
  taksa = cls.calculate_taksa(day_digit)
  kalayok = cls.calculate_kalayok(cs_year)
  chart = cls.build_chart(...)
  lucky_digits = cls.extract_lucky_digits(...)
  day_name_th = cls.DAY_NAMES_TH[day_digit]
  ```
  Since `cls` is neither a parameter of `execute(self, ...)` nor defined in module scope, Python raises a fatal `NameError` at runtime.
- **Suggestion**: Replace `cls.` with `self.` (or `MahaboteEngine.`) throughout the `execute` method, or decorate `execute` as a `@classmethod`.

---

### 3. [Minor] Dead Code in Planetary Harmony Pairs
- **What**: Planetary pair `(2, 5)` is defined in both `element_pairs` (line 435) and `enemy_pairs` (line 437).
- **Where**: `omni_oracle_app/backend/app/engines/mahabote.py`, lines 435 & 437
- **Why**: The helper function `get_bond` checks `element_pairs` prior to `enemy_pairs`. Therefore, the `(2, 5)` check inside `enemy_pairs` is unreachable dead code.
- **Suggestion**: Remove `(2, 5)` from `enemy_pairs` or adjust planetary pair definitions to follow standard Thai astrological conventions cleanly.

---

## Domain Math & Rule Verification Results

| # | Domain Rule / Specification | Status | Details & Observations |
|---|-----------------------------|--------|------------------------|
| 1 | **Chula Sakarat & April 16 Songkran Cutoff** | **PASS (Logic)** | `calculate_cs` correctly uses `BE - 1182` for Jan 1–Apr 15 (`songkran_adjusted = True`) and `BE - 1181` for Apr 16–Dec 31 (`songkran_adjusted = False`). |
| 2 | **Modulo 7 Zero-Mapping (`0 -> 7`)** | **PASS (Logic)** | `calculate_cs_remainder` correctly evaluates `cs_year % 7` and maps remainder `0` to `7` (Saturn). |
| 3 | **7 Body Positions Matrix Logic** | **PASS (Logic)** | `build_chart` rotates planet digits 1..7 starting from `cs_remainder` at Thanang (index 0) across Pita, Mata, Phoka, Majjhima, Atta, Hina. 3-row matrix layout `[[0,1,2],[3,4,5],[6]]` is correct. |
| 4 | **Taksa Wheel & Kalayok Annual Lookup** | **PASS (Logic)** | 8-planet Taksa wheel `[1, 2, 3, 4, 7, 5, 8, 6]` rotates correctly from birth weekday. Wednesday night (Rahu / 8) is handled via 18:00 cutoff and flag. Kalayok lookup table for Thongchai, Athipati, Yamabat, Lokawinat matches standard tables for CS 1..7. |
| 5 | **Lucky Digits & 2-Digit Lottery Pairs** | **PASS (Logic)** | Scoring algorithm combines house weights, Taksa weights, and Kalayok weights; filters out Kalakini, Yamabat, Lokawinat, Hina; derives 2-digit lottery pairs with harmony bond bonuses and calculates power score. |
| 6 | **Pytest Test Suite Execution** | **FAIL (Runtime)** | Test suite `test_mahabote.py` fails on all seam calls due to `NameError: name 'cls' is not defined` in `MahaboteEngine.execute`. |

---

## Adversarial Stress-Test Findings

1. **Uncaught Execution Crash**:
   - Call: `calculate_mahabote("1995-08-15")`
   - Expected Result: `MahaboteResult` instance returned.
   - Actual Result: `NameError: name 'cls' is not defined` raised at line 533 of `mahabote.py`.

2. **Boundary Date Handling**:
   - `1990-04-15` -> CS 1351 (`songkran_adjusted = True`)
   - `1990-04-16` -> CS 1352 (`songkran_adjusted = False`)
   - Math logic correctly handles boundary conditions.

---

## Recommendations & Required Actions

1. Fix `omni_oracle_app/backend/app/engines/mahabote.py` line 533–561 by replacing `cls.` with `self.` (or `MahaboteEngine.`).
2. Clean up redundant `(2, 5)` pair definition in `extract_lucky_digits`.
3. Run `pytest omni_oracle_app/backend/tests/test_mahabote.py -v` and verify all tests pass.
4. Resubmit worker handoff report with actual test output verification.
