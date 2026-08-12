# Handoff Report: Sub-milestone M1.1 Thai Astrology Engine Remediation (Gen 2)

**Role:** Implementer / QA / Specialist (`worker_m1_1_gen2`)  
**Target Code:** `omni_oracle_app/backend/app/engines/thai_astrology.py`  
**Target Test Suite:** `omni_oracle_app/backend/tests/test_thai_astrology.py`  
**Date:** 2026-08-06  
**Status:** COMPLETE (All 4 defects remediated and verified)

---

## 1. Observation

1. **Defect 1: 180° Lagna Inversion (`calculate_lagna_sidereal`)**
   - File: `omni_oracle_app/backend/app/engines/thai_astrology.py`, lines 414–415.
   - Code before fix:
     `y = -math.cos(rad(lst))`
     `x = (math.sin(rad(lst)) * math.cos(rad(eps))) + (math.tan(rad(lat)) * math.sin(rad(eps)))`
   - Result: Both $y$ and $x$ signs were inverted, causing $\text{atan2}(y, x)$ to return Descendant (Western horizon / 7th house) instead of Ascendant (Eastern horizon / 1st house).

2. **Defect 2: GMST Double-Counting (`calculate_lagna_sidereal`)**
   - File: `omni_oracle_app/backend/app/engines/thai_astrology.py`, lines 406–408.
   - Code before fix: `t0 = (jd - 2451545.0) / 36525.0`, `gmst = (gmst0 + 360.98564736629 * (ut_hours / 24.0)) % 360.0`.
   - Result: `t0` incorporated fractional day `ut_hours/24`, causing `36000.770053608 * t0` to add $0.985647^\circ \times ut\_hours$. Line 408 then added $360.985647^\circ \times (ut\_hours/24) = (15^\circ + 0.985647^\circ) \times ut\_hours$, double-counting the $0.985647^\circ/\text{day}$ daily sidereal rate.

3. **Defect 3: Planetary Dignity Precedence Misclassification (`determine_planetary_dignity`)**
   - File: `omni_oracle_app/backend/app/engines/thai_astrology.py`, lines 294–303.
   - Code before fix: `SIGN_RULERS` (Kaset) check was evaluated before `EXALTED_SIGNS` (Ucc).
   - Result: Mercury (planet ID 4) in Virgo (sign index 5) evaluated to `KASET` instead of `UCC`.

4. **Defect 4: Absence of Ground-Truth Assertions (`test_thai_astrology.py`)**
   - `test_thai_astrology.py` lacked explicit comparison of calculated Lagna and planetary longitudes against known benchmark charts.

---

## 2. Logic Chain

1. **Lagna Inversion Fix**:
   - Astronomical Ascendant formula: $y = \cos(\text{LST})$, $x = -\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)$.
   - By removing the extraneous leading minus sign from $y$ and negating both terms of $x$, $\text{atan2}(y, x)$ points directly to the rising Eastern horizon.
   - Ground-truth check: 1990-01-01 12:00 in Bangkok yields Lagna at ~337.8° (Pisces / มีน, `rasi_index=11`), replacing the previous inverted output of Virgo (`rasi_index=5`). At sunrise (2026-08-05 06:00 Bangkok), Lagna equals Sun sign (Cancer / กรกฎ, `rasi_index=3`).

2. **GMST Calculation Fix**:
   - Calculated `jd0 = math.floor(jd - 0.5) + 0.5` representing 0h UT on the birth date.
   - Derived `t0 = (jd0 - 2451545.0) / 36525.0` at 0h UT.
   - Computed base GMST at 0h UT: `gmst0 = 100.46061837 + (36000.770053608 * t0) + (0.000387933 * t0 * t0)`.
   - Added Earth rotation component: `gmst = (gmst0 + 1.00273790935 * ut_hours * 15.0) % 360.0`.
   - This eliminates the double-counting drift.

3. **Dignity Precedence Fix**:
   - Placing `EXALTED_SIGNS` (Ucc) check before `SIGN_RULERS` (Kaset) ensures that when a planet occupies its exalted sign, it receives `UCC` dignity.
   - Mercury in Virgo (`planet_id=4`, `sign_index=5`) evaluates to `PlanetaryDignity.UCC`.

4. **Test Suite Expansion**:
   - Added `test_ground_truth_lagna_and_planetary_benchmark` to lock in Lagna for 1990-01-01 12:00 (Pisces) and 2026-08-05 06:00 sunrise (Cancer).
   - Added `test_mercury_in_virgo_dignity_precedence` to verify Mercury in Virgo is `UCC`, Mercury in Gemini is `KASET`, and Sun in Aries is `UCC`.
   - Added `test_gmst_no_double_counting` to verify sidereal rate scaling across fractional hour offsets.

---

## 3. Caveats

- **No caveats.** Pure Python ephemeris and optional Swiss Ephemeris C-extension fallback paths both use the updated `calculate_lagna_sidereal()` and `determine_planetary_dignity()`.

---

## 4. Conclusion

All 4 sub-milestone M1.1 remediation requirements have been implemented with genuine astronomical mathematical precision:
- Lagna trigonometric component signs corrected.
- GMST base date `jd0` established and sidereal drift calculated without double-counting.
- Dignity hierarchy updated so Exalted (`UCC`) takes precedence over Kaset.
- Unit test suite `test_thai_astrology.py` expanded with ground-truth benchmark assertions and regression tests.

---

## 5. Verification Method

To independently verify the fixes:

1. **Inspect Code Modifications**:
   - `omni_oracle_app/backend/app/engines/thai_astrology.py`:
     - Line 297: `if EXALTED_SIGNS.get(planet_id) == sign_index: return PlanetaryDignity.UCC` is checked before `SIGN_RULERS`.
     - Lines 406–416: `jd0 = math.floor(jd - 0.5) + 0.5`, `gmst = (gmst0 + 1.00273790935 * ut_hours * 15.0) % 360.0`, `y = math.cos(rad(lst))`, `x = -math.sin(rad(lst)) * math.cos(rad(eps)) - math.tan(rad(lat)) * math.sin(rad(eps))`.

2. **Run Pytest Test Suite**:
   ```bash
   cd omni_oracle_app/backend
   pytest tests/test_thai_astrology.py -v
   ```
   All 10 unit test functions pass cleanly:
   - `test_data_models_and_enums`
   - `test_calculate_thai_astrology_valid_input`
   - `test_lagna_and_house_mapping`
   - `test_harmonic_charts_d9_d3_math`
   - `test_lahiri_ayanamsa_subtraction`
   - `test_edge_cases_and_defaults`
   - `test_lucky_digits_extraction`
   - `test_ground_truth_lagna_and_planetary_benchmark`
   - `test_mercury_in_virgo_dignity_precedence`
   - `test_gmst_no_double_counting`
