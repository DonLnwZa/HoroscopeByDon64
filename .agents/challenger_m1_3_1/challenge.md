# Empirical Challenge Report: Burmese Mahabote Engine (M1.3)

**Target Module:** `omni_oracle_app/backend/app/engines/mahabote.py`  
**Test Suite:** `omni_oracle_app/backend/tests/test_mahabote.py`  
**Stress Suite:** `.agents/challenger_m1_3_1/stress_test_mahabote.py`  
**Challenger:** Challenger 1 (`challenger_m1_3_1`)  
**Date:** 2026-08-06  
**Verdict:** **APPROVE**

---

## Challenge Summary

**Overall risk assessment**: LOW

The Burmese Mahabote Engine implementation in `mahabote.py` and its accompanying TDD Pytest suite `test_mahabote.py` demonstrate excellent mathematical precision, strict adherence to Pydantic v2 schemas, complete 100-year cycle continuity, correct Songkran boundary adjustments across leap years and century boundaries, and robust Wednesday Day/Night Rahu flag and birth time handling. No critical flaws, regressions, or mathematical inconsistencies were discovered during empirical stress testing.

---

## Challenges & Attack Scenarios Evaluated

### 1. [Low Risk] Songkran Cutoff Boundary at April 15 23:59 vs April 16 00:00 & Century Leap Years

- **Assumption challenged:** That Songkran boundary cutoff handling (April 16 cutoff day) functions correctly across standard years, leap years (2000, 2024), century non-leap years (1900, 2100), and `datetime` objects at midnight boundaries (23:59:59 vs 00:00:00).
- **Attack scenario:** Passing a birth date of April 15 at 23:59:59 vs April 16 at 00:00:00, or leap year Feb 29 dates, to see if Chula Sakarat (CS) year calculation (`BE - 1182` vs `BE - 1181`) off-by-one errors or leap year invalid date exceptions occur.
- **Stress Test Result:**
  - `1900-02-28`: CS = 1261, `songkran_adjusted = True` (PASS)
  - `1900-04-15`: CS = 1261, `songkran_adjusted = True` (PASS)
  - `1900-04-16`: CS = 1262, `songkran_adjusted = False` (PASS)
  - `2000-02-29` (Leap Year): CS = 1361, `songkran_adjusted = True` (PASS)
  - `2000-04-15`: CS = 1361, `songkran_adjusted = True` (PASS)
  - `2000-04-16`: CS = 1362, `songkran_adjusted = False` (PASS)
  - `2024-02-29` (Leap Year): CS = 1385, `songkran_adjusted = True` (PASS)
  - `2024-04-15`: CS = 1385, `songkran_adjusted = True` (PASS)
  - `2024-04-16`: CS = 1386, `songkran_adjusted = False` (PASS)
  - `2100-04-15` (Century Non-Leap): CS = 1461, `songkran_adjusted = True` (PASS)
  - `2100-04-16`: CS = 1462, `songkran_adjusted = False` (PASS)
  - `datetime(2024, 4, 15, 23, 59, 59)`: CS = 1385, `songkran_adjusted = True` (PASS)
  - `datetime(2024, 4, 16, 0, 0, 0)`: CS = 1386, `songkran_adjusted = False` (PASS)
- **Blast radius:** None observed.
- **Mitigation:** Existing implementation strictly handles all boundary conditions.

---

### 2. [Low Risk] CS Remainder Modulo 7 Cycle Continuity Across 100-Year Span (1920–2030)

- **Assumption challenged:** That the Chula Sakarat modulo 7 calculation (`CS % 7` with remainder 0 mapped to 7) remains strictly continuous, monotonic across Songkran transitions, and bounded in `{1..7}` for every single day across a 100-year span (40,542 consecutive days).
- **Attack scenario:** Iterating every single day from 1920-01-01 to 2030-12-31 to detect any discontinuities, unexpected remainder skips, out-of-bound values (0, negative, >7), or non-monotonic CS year jumps.
- **Stress Test Result:**
  - Evaluated 40,542 consecutive days from 1920-01-01 to 2030-12-31.
  - On every April 16, `cs_year` increased by exactly 1, and `cs_remainder` transitioned in exact cyclic mod 7 order (`1->2->3->4->5->6->7->1`).
  - On all other 40,431 days, `cs_year` and `cs_remainder` remained perfectly constant.
  - 0 violations found.
- **Blast radius:** None observed.
- **Mitigation:** N/A (100% verified continuous).

---

### 3. [Low Risk] Wednesday Day vs Night Flag & Birth Time Handling

- **Assumption challenged:** That Wednesday births properly differentiate between Wednesday Day (พุธกลางวัน, digit 4) and Wednesday Night / Rahu (พุธกลางคืน - ราหู, digit 8) across explicit boolean flags (`is_wednesday_night`), birth times (18:00–05:59 cutoff), and non-Wednesday dates.
- **Attack scenario:**
  - Explicit flag `is_wednesday_night=True` / `False` on Wednesday date (`2024-05-15`).
  - Birth times `00:00`, `02:00`, `05:59`, `06:00`, `12:00`, `17:59`, `18:00`, `23:59`.
  - Non-Wednesday date (`2024-05-12` Sunday) with `is_wednesday_night=True`.
- **Stress Test Result:**
  - `2024-05-15` (Wed) + `is_wednesday_night=True`: `day_of_week=8`, `is_wednesday_night=True`, `day_name_th="พุธ (กลางคืน - ราหู)"` (PASS)
  - `2024-05-15` (Wed) + `is_wednesday_night=False`: `day_of_week=4`, `is_wednesday_night=False`, `day_name_th="พุธ (กลางวัน)"` (PASS)
  - `2024-05-15` + birth time `18:00`: `day_of_week=8`, `is_wednesday_night=True` (PASS)
  - `2024-05-15` + birth time `05:59`: `day_of_week=8`, `is_wednesday_night=True` (PASS)
  - `2024-05-15` + birth time `06:00`: `day_of_week=4`, `is_wednesday_night=False` (PASS)
  - `2024-05-15` + birth time `17:59`: `day_of_week=4`, `is_wednesday_night=False` (PASS)
  - `2024-05-12` (Sun) + `is_wednesday_night=True`: `day_of_week=1` (Sunday), `is_wednesday_night=False` (PASS — correctly ignores flag on non-Wednesday dates)
- **Blast radius:** None observed.
- **Mitigation:** Implementation handles all flag and time precedence rules cleanly.

---

### 4. [Low Risk] 7 Body Positions Matrix Permutation & Invariants

- **Assumption challenged:** That the 7 body positions (`thanang`, `pita`, `mata`, `phoka`, `matchima`, `atta`, `hina`) always form a valid 1..7 permutation starting from `cs_remainder` at `thanang`, and `chart_matrix` maintains a 3x3 layout with 7 elements.
- **Attack scenario:** Inspecting matrix placement across multiple years and months.
- **Stress Test Result:**
  - For all test dates, `thanang` held `cs_remainder`.
  - The 7 positions contained digits `1..7` exactly once (valid permutation).
  - Matrix layout was 3 rows: row 0 (3 elements), row 1 (3 elements), row 2 (1 element).
  - All position Pydantic models validated successfully.
- **Blast radius:** None.
- **Mitigation:** N/A.

---

## Stress Test Results Summary

| Stress Test Scenario | Expected Behavior | Actual Behavior | Result |
|----------------------|-------------------|-----------------|--------|
| Songkran Cutoff Boundary (Apr 15 vs Apr 16) | CS year shifts by +1 on Apr 16 | CS year shifts by +1 on Apr 16 (`songkran_adjusted` updates) | PASS |
| Leap Years (2000, 2024) Feb 29 | Valid date parsing & correct CS calculation | Handled cleanly with `songkran_adjusted=True` | PASS |
| Century Non-Leap Years (1900, 2100) | Correct CS adjustment without invalid date errors | Handled cleanly | PASS |
| 100-Year CS Remainder Continuity (1920–2030) | 40,542 consecutive days continuous mod 7 cycle | 0 skips, 0 out-of-bounds, 100% continuous | PASS |
| Wednesday Night Rahu Flag & Time (18:00–05:59) | `day_of_week=8`, `is_wednesday_night=True` | Returned digit 8 and correct Thai name | PASS |
| Non-Wednesday Date with Wed Night Flag | Return calendar day (e.g. 1 for Sunday), flag False | Returned digit 1, flag False | PASS |
| Chart Positions Matrix Permutation | Exact permutation of digits 1..7 | Permutation intact across all dates | PASS |
| Avoid Digits Invariants | Includes Kalakini, Yamabat, Lokavinas, Hina | All negative/incurred digits included in avoid set | PASS |
| Invalid Input Format Handling | Raise `ValueError` / `TypeError` | Correctly raised expected exception types | PASS |

---

## Unchallenged Areas

- **FastAPI Endpoint Integration:** Out of scope for M1.3 (assigned to M3 API milestone).
- **GLO 1-Year Lottery Frequency Weighting:** Out of scope for M1.3 (assigned to M2 Recommender milestone).

---

## Final Verdict

**APPROVE**  
The Burmese Mahabote Engine (`mahabote.py`) and its test suite (`test_mahabote.py`) meet all technical requirements and empirical stress test criteria with zero bugs or defects.
