# Mahabote Engine (M1.3) Empirical Challenge Report

**Target File:** `omni_oracle_app/backend/app/engines/mahabote.py`  
**Test Suite:** `omni_oracle_app/backend/tests/test_mahabote.py`  
**Challenger:** Challenger 2 (`challenger_m1_3_2`)  
**Date:** 2026-08-06  
**Verdict:** **APPROVE**

---

## 1. Executive Summary

- **Overall Risk Assessment:** **LOW**
- **Verification Verdict:** **APPROVE**
- **Tested Scope:** 
  1. All 49 combinations of (7 Weekdays x 7 Chula Sakarat Remainders).
  2. All 8 Taksa Planetary Wheels (Sunday to Wednesday Night / Rahu).
  3. 1,000 random birthdates stress sweep (1940 to 2030) for lucky digit extraction, NaN/null safety, and 2-digit lottery pair formatting.
  4. Full Pytest unit test coverage in `test_mahabote.py`.

---

## 2. Stress Test Results

| Test Suite / Scenario | Expected Behavior | Actual Behavior | Result |
|-----------------------|-------------------|-----------------|--------|
| **49 Combos (7 Weekdays x 7 CS Rem)** | 7 houses correctly populated, matrix shape 3x3 ragged, no index error | All 49 combinations correctly assigned without array out-of-bounds or misaligned mappings | **PASS** |
| **8-Planet Taksa Wheel** | Rotation `[1, 2, 3, 4, 7, 5, 8, 6]` starting at birth weekday index for all 8 day digits | Accurate mapping of Bariwan, Ayu, Dech, Sri, Mula, Industah, Montrii, Kalakini | **PASS** |
| **Songkran April 16 Cutoff** | Pre-April 16 -> `BE-1182` (`AD-639`); Post-April 16 -> `BE-1181` (`AD-638`) | Tested on 1990, 2000, 2024 boundary dates; CS calculation & flag strictly correct | **PASS** |
| **CS Remainder 0 Mapping** | Remainder 0 mapped to 7 | `CS 1386 % 7 == 0` mapped to remainder 7 | **PASS** |
| **Wednesday Day vs Night** | Cutoff 18:00-05:59 or `is_wednesday_night` flag assigns Day 4 vs Night 8 | Parametrized tests verify correct day_of_week and Rahu assignments | **PASS** |
| **Lucky Digits & 2-Digit Pairs (1,000 Sweep)** | Single digits in [0..9], pairs formatted '00'-'99', power_score in [0.0..100.0], zero NaNs/nulls | 1,000 random birthdates executed with zero NaNs, nulls, or invalid digit formats | **PASS** |

---

## 3. Challenge Analysis & Dimension Findings

### Challenge 1: Matrix Alignment & 7-House Rotation
- **Hypothesis:** Modulo 7 arithmetic `((cs_remainder - 1 + i) % 7) + 1` across houses could cause index displacement or out-of-bounds values.
- **Verification:** Evaluated `i` from 0 to 6 for all `cs_remainder` values (1 to 7). Output is strictly within `{1, 2, 3, 4, 5, 6, 7}`. The 7 body positions (`thanang`, `pita`, `mata`, `phoka`, `matchima`, `atta`, `hina`) match Burmese Mahabote conventions.
- **Result:** **ROBUST (0 Defects)**

### Challenge 2: Taksa Planetary Wheel Integrity
- **Hypothesis:** Wednesday Night (Rahu = 8) or Thursday/Friday offsets could break the 8-element wheel `[1, 2, 3, 4, 7, 5, 8, 6]`.
- **Verification:** Checked wheel index lookups for all 8 `day_digit` inputs. Correctly assigns Sri and Kalakini planets across all 8 day digits without KeyError or Indexing mismatches.
- **Result:** **ROBUST (0 Defects)**

### Challenge 3: Lucky Digits & Lottery Pairs Degradation Under High Avoid-Set Load
- **Hypothesis:** When Kalakini, Yamabat, Lokavinas, Hina, and negative total scores populate `avoid_set`, candidate lists could collapse and produce empty lottery pair lists or NaNs.
- **Verification:** Evaluated `extract_lucky_digits` logic. `Thanang` house weight (+3.0) and Sri planet (+3.0) guarantee positive scored planets in every possible chart configuration. Candidate digits and fallbacks ensure 6 valid 2-digit lottery pairs formatted as `'00'`-`'99'` are generated for 100% of tested inputs.
- **Result:** **ROBUST (0 Defects)**

---

## 4. Unchallenged Areas

- **FastAPI Endpoint Integration:** Handled in Milestone M3 (out of scope for Layer 1 core engine).
- **Tarot & Historical Lottery Matching:** Handled in M1.4 / M2.

---

## 5. Verdict

**FINAL VERDICT: APPROVE**

The Burmese Mahabote Engine (`app.engines.mahabote`) passes all empirical stress tests, boundary conditions, and mathematical verification. Code design strictly follows TDD, Pydantic v2 validation, and Layer 1 architecture standards.
