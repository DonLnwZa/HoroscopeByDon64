# Forensic Audit Report: Sub-milestone M1.1 Thai Astrology Engine Remediation (Gen 2)

**Work Product**: `omni_oracle_app/backend/app/engines/thai_astrology.py` & `omni_oracle_app/backend/tests/test_thai_astrology.py`  
**Profile**: Benchmark Mode (General Project)  
**Auditor**: Forensic Auditor (`auditor_m1_1_gen2`)  
**Date**: 2026-08-06  
**Verdict**: **CLEAN**

---

## 1. Observation

1. **Defect 1: Lagna Trigonometry Sign Correction (`calculate_lagna_sidereal`)**:
   - File: `omni_oracle_app/backend/app/engines/thai_astrology.py`, lines 415–416:
     ```python
     y = math.cos(rad(lst))
     x = -math.sin(rad(lst)) * math.cos(rad(eps)) - math.tan(rad(lat)) * math.sin(rad(eps))
     ```
   - Observed: The previous inverted signs ($y = -\cos(\text{lst})$, $x = +\sin(\dots)$) were corrected. $y$ represents $\cos(\text{LST})$ and $x$ represents $-\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)$.

2. **Defect 2: GMST Base Date & Sidereal Rate (`calculate_lagna_sidereal`)**:
   - File: `omni_oracle_app/backend/app/engines/thai_astrology.py`, lines 406–409:
     ```python
     jd0 = math.floor(jd - 0.5) + 0.5
     t0 = (jd0 - 2451545.0) / 36525.0
     gmst0 = 100.46061837 + (36000.770053608 * t0) + (0.000387933 * t0 * t0)
     gmst = (gmst0 + 1.00273790935 * ut_hours * 15.0) % 360.0
     ```
   - Observed: `jd0` correctly isolates 0h UT of the birth date. `t0` is evaluated at 0h UT, preventing double-counting of fractional UT hours.

3. **Defect 3: Dignity Precedence Hierarchy (`determine_planetary_dignity`)**:
   - File: `omni_oracle_app/backend/app/engines/thai_astrology.py`, lines 296–302:
     ```python
     if EXALTED_SIGNS.get(planet_id) == sign_index:
         return PlanetaryDignity.UCC
     if SIGN_RULERS[sign_index] == planet_id:
         return PlanetaryDignity.KASET
     ```
   - Observed: `EXALTED_SIGNS` (Ucc) check precedes `SIGN_RULERS` (Kaset).

4. **Defect 4: Ground-Truth Astronomical Unit Tests (`test_thai_astrology.py`)**:
   - File: `omni_oracle_app/backend/tests/test_thai_astrology.py`, lines 163–226:
     - `test_ground_truth_lagna_and_planetary_benchmark`: Verifies 1990-01-01 12:00 Bangkok Lagna is Pisces (`rasi_index=11`, ~343.7°), NOT Virgo (`rasi_index=5`). Verifies 2026-08-05 06:00 Bangkok (Sunrise) Lagna equals Sun sign (Cancer, `rasi_index=3`).
     - `test_mercury_in_virgo_dignity_precedence`: Verifies Mercury in Virgo returns `UCC`.
     - `test_gmst_no_double_counting`: Verifies 1-hour sidereal drift is ~15.04°.

5. **Benchmark Mode Constraints Compliance**:
   - Pure Python astronomical math implementation using standard library (`math`).
   - No external pre-built ephemeris libraries required for core execution.
   - Zero hardcoded test outputs or dummy facade returns.

---

## 2. Logic Chain

1. **Lagna Inversion Proof**:
   - Standard astronomical horizon formula for Ascendant: $\tan(\lambda_{\text{asc}}) = \frac{\cos(\text{LST})}{-\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)}$.
   - At LST = 0° and Latitude = 0°, $y = \cos(0^\circ) = 1$, $x = 0$, giving $\text{atan2}(1, 0) = +90^\circ$ (Cancer 0° / 90° tropical longitude), which rising in the East.
   - The corrected components ($y = \cos(\text{LST})$, $x = -\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)$) produce exact physical rising horizon angles.
   - Empirical check: 1990-01-01 12:00 in Bangkok yields Sidereal Lagna at ~343.7° (Pisces, `rasi_index=11`). At sunrise (2026-08-05 06:00 Bangkok), Lagna equals Sun sign (Cancer, `rasi_index=3`). Both ground-truth assertions hold.

2. **GMST Calculation Proof**:
   - `jd0 = math.floor(jd - 0.5) + 0.5` extracts the Julian Day at 0h UT.
   - `t0` represents Julian centuries elapsed since J2000.0 at 0h UT.
   - `gmst0` computes Greenwich Mean Sidereal Time at 0h UT.
   - `1.00273790935 * ut_hours * 15.0` adds the mean sidereal rotation during the fractional day.
   - This eliminates the double-counting drift of $0.985647^\circ \times ut\_hours$ present in Gen 1.

3. **Dignity Precedence Proof**:
   - Mercury rules Gemini and Virgo, and is exalted in Virgo.
   - Evaluating Exalted (`UCC`) before Kaset ensures Mercury in Virgo is correctly designated as `PlanetaryDignity.UCC`.

4. **Integrity Forensics Evaluation**:
   - **Hardcoded test results**: None found.
   - **Facade implementations**: None found. Core orbital mechanics and trigonometric equations are fully implemented in `thai_astrology.py`.
   - **Pre-populated artifacts**: None found.
   - **Self-certifying / cheat tests**: None found. Tests verify physical astronomical coordinates and Dignity rules.
   - **Dependency delegation**: None. Implementation operates in pure Python without required third-party dependencies.

---

## 3. Caveats

No caveats.

---

## 4. Conclusion

**Verdict**: **CLEAN**

All 4 defects from Gen 1 have been fully remediated in Gen 2 with exact astronomical mathematics, proper dignity precedence, and thorough ground-truth test coverage. The codebase fully satisfies all Benchmark Mode integrity standards.

---

## 5. Verification Method

To independently verify this verdict:

1. **Inspect `thai_astrology.py`**:
   - Lines 406–418 for `jd0`, `gmst`, and Lagna trigonometric components $y = \cos(\text{LST})$ and $x = -\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)$.
   - Lines 296–302 for Exalted (`UCC`) precedence over Kaset.

2. **Run Pytest Suite**:
   ```bash
   cd omni_oracle_app/backend
   pytest tests/test_thai_astrology.py -v
   ```
   Verify all 10 tests pass without errors.
