# Review & Handoff Report: Sub-milestone M1.1 Thai Astrology Engine Remediation (Gen 2)

**Role:** Reviewer 2 & Adversarial Critic (`reviewer_m1_1_gen2_2`)  
**Target Module:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\app\engines\thai_astrology.py`  
**Target Test Suite:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\tests\test_thai_astrology.py`  
**Worker Gen 2 Handoff Reviewed:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\worker_m1_1_gen2\handoff.md`  
**Verdict:** **APPROVE**  
**Date:** 2026-08-06  

---

## 1. Executive Review Summary

**Verdict:** **APPROVE**

Worker Gen 2 (`worker_m1_1_gen2`) has successfully remediated all defects identified in prior reviews. The core astronomical engine in `omni_oracle_app/backend/app/engines/thai_astrology.py` and the unit test suite in `omni_oracle_app/backend/tests/test_thai_astrology.py` were subjected to a rigorous mathematical, logical, and adversarial integrity audit. 

Specifically:
1. The 180° Lagna inversion in `calculate_lagna_sidereal()` is **fully corrected**. The trigonometric components $y = \cos(\text{LST})$ and $x = -\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)$ accurately compute the rising Ascendant on the Eastern horizon.
2. The GMST double-counting defect was fixed by computing base GMST at 0h UT (`jd0`) and adding sidereal rotation per UT hour.
3. Dignity hierarchy precedence in `determine_planetary_dignity()` now correctly evaluates Exalted (`UCC`) before Kaset (`KASET`).
4. Ground-truth benchmark assertions were added to `test_thai_astrology.py`, confirming Lagna for 1990-01-01 12:00 Bangkok at 343.72° (Pisces / มีน, `rasi_index=11`) and sunrise chart (2026-08-05 06:00 Bangkok) matching Sun sign (Cancer / กรกฎ, `rasi_index=3`).
5. Zero integrity violations (no hardcoded test shortcuts, no facade implementations). All 10 tests in `test_thai_astrology.py` pass cleanly.

---

## 2. Observation

1. **Target File Locations & Line References:**
   - Module path: `omni_oracle_app/backend/app/engines/thai_astrology.py`
   - Test suite path: `omni_oracle_app/backend/tests/test_thai_astrology.py`

2. **Verbatim Inspection — Lagna Sidereal Calculation (`calculate_lagna_sidereal`):**
   `thai_astrology.py`, lines 404–421:
   ```python
   def calculate_lagna_sidereal(jd: float, ut_hours: float, lat: float, lon: float, ayanamsa: float) -> float:
       """Calculates Sidereal Lagna (Ascendant) longitude in degrees."""
       jd0 = math.floor(jd - 0.5) + 0.5
       t0 = (jd0 - 2451545.0) / 36525.0
       gmst0 = 100.46061837 + (36000.770053608 * t0) + (0.000387933 * t0 * t0)
       gmst = (gmst0 + 1.00273790935 * ut_hours * 15.0) % 360.0
       lst = (gmst + lon) % 360.0

       rad = math.radians
       eps = 23.439291 - 0.0130042 * t0

       y = math.cos(rad(lst))
       x = -math.sin(rad(lst)) * math.cos(rad(eps)) - math.tan(rad(lat)) * math.sin(rad(eps))

       asc_trop = math.degrees(math.atan2(y, x)) % 360.0
       asc_sid = (asc_trop - ayanamsa) % 360.0
       return asc_sid
   ```

3. **Verbatim Inspection — Planetary Dignity Hierarchy (`determine_planetary_dignity`):**
   `thai_astrology.py`, lines 294–314:
   ```python
   def determine_planetary_dignity(planet_id: int, sign_index: int) -> PlanetaryDignity:
       """Determines planetary dignity (อุจจ์, เกษตร, นิจ, ประ, ปกติ)."""
       # 1. Ucc (Exalted) - checked before Kaset so Mercury in Virgo is evaluated as UCC
       if EXALTED_SIGNS.get(planet_id) == sign_index:
           return PlanetaryDignity.UCC

       # 2. Kaset (Own sign)
       if SIGN_RULERS[sign_index] == planet_id:
           return PlanetaryDignity.KASET
       ...
   ```

4. **Verbatim Inspection — Ground-Truth Benchmark Assertions (`test_thai_astrology.py`):**
   `test_thai_astrology.py`, lines 163–182:
   ```python
   def test_ground_truth_lagna_and_planetary_benchmark():
       # 1. 1990-01-01 12:00 Bangkok
       res_1990 = calculate_thai_astrology("1990-01-01", "12:00", "กรุงเทพมหานคร")
       assert res_1990.lagna.rasi_index == 11, f"Expected Pisces (11), got {res_1990.lagna.rasi_index}"
       assert res_1990.lagna.rasi_name_th == "มีน"
       assert 330.0 <= res_1990.lagna.longitude < 360.0

       # 2. 2026-08-05 06:00 Bangkok (Sunrise)
       res_sunrise = calculate_thai_astrology("2026-08-05", "06:00", "กรุงเทพมหานคร")
       sun_sign = res_sunrise.planets[1].rasi_index
       lagna_sign = res_sunrise.lagna.rasi_index
       assert sun_sign == 3
       assert lagna_sign == sun_sign
   ```

---

## 3. Logic Chain & Rigorous Proof of Correction

1. **Mathematical Proof of Lagna Ascendant Formula:**
   The fundamental spherical astronomy relationship for the ecliptic point on the Eastern Horizon (Ascendant $\lambda_{\text{ASC}}$) given Local Sidereal Time $\theta = \text{LST}$, obliquity $\varepsilon$, and observer latitude $\phi$ is:
   $$\tan(\lambda_{\text{ASC}}) = \frac{\cos \theta}{-\sin \theta \cos \varepsilon - \tan \phi \sin \varepsilon}$$

   Expressing this as an un-ambiguous 4-quadrant $\text{atan2}(y, x)$:
   - $y = \cos(\text{LST})$
   - $x = -\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)$

   In `thai_astrology.py`:
   - Line 415: `y = math.cos(rad(lst))`
   - Line 416: `x = -math.sin(rad(lst)) * math.cos(rad(eps)) - math.tan(rad(lat)) * math.sin(rad(eps))`

   This matches the theoretical spherical astronomy formula with absolute precision.

2. **Cardinal Direction & Physical Verification:**
   - At $\text{LST} = 0^\circ$ on the Equator ($\phi = 0^\circ$):
     - $y = \cos(0^\circ) = +1.0$
     - $x = -\sin(0^\circ)\cos(\varepsilon) - 0 = 0.0$
     - $\text{atan2}(+1.0, 0.0) = +90^\circ$ (Cancer 0°, rising on the Eastern horizon 90° east of the RAMC meridian).
     - Prior buggy implementation yielded $\text{atan2}(-1.0, 0.0) = 270^\circ$ (Capricorn 0°, Descendant).
     - The sign fix restores the Eastern horizon Ascendant vector.

3. **Benchmarking Against Astronomical Facts:**
   - **Sunrise Chart (2026-08-05 06:00 ICT, Bangkok):** At sunrise, the Sun sits directly on the Eastern horizon. Thus, $\text{Ascendant} = \text{Sun's Longitude}$. Sun is in Cancer (`rasi_index = 3`, ~18° sidereal). `calculate_lagna_sidereal()` calculates Lagna in Cancer (`rasi_index = 3`), satisfying $\text{Lagna} = \text{Sun}$.
   - **Noon Chart (1990-01-01 12:00 ICT, Bangkok):** At solar noon, Sun is near Midheaven (MC). The Ascendant is ~90° east of the Sun. Sun is in Sagittarius (~17° sidereal). Lagna is calculated as 343.72° (Pisces / มีน, `rasi_index = 11`).

4. **Integrity & Code Quality Audit:**
   - No hardcoded overrides for dates/signs exist in `thai_astrology.py`.
   - Complete implementation of Lahiri Ayanamsa, 10 Planets, 12 Houses, D9 Navamsa, D3 Drekkana, Dignity evaluation, and Lucky Digit extraction.
   - Pytest suite `test_thai_astrology.py` covers 10 test functions testing models, seam inputs, house mapping, harmonic math, ayanamsa, edge cases, lucky digits, ground-truth benchmarks, dignity precedence, and GMST sidereal drift.

---

## 4. Verified Claims & Stress Test Results

| Component / Claim | Verification Status | Rationale / Output |
|---|---|---|
| Lagna Sidereal Formula ($y, x$) | **VERIFIED PASS** | $y = \cos(\text{LST})$, $x = -\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)$ yields exact rising Ascendant. |
| Sunrise Lagna Benchmark | **VERIFIED PASS** | 2026-08-05 06:00 Bangkok yields Lagna = Sun Sign (Cancer, `rasi_index=3`). |
| 1990-01-01 12:00 Benchmark | **VERIFIED PASS** | Lagna longitude = 343.72° (Pisces / มีน, `rasi_index=11`). |
| GMST Base 0h UT (`jd0`) | **VERIFIED PASS** | Removes $0.985647^\circ/\text{day}$ double-counting; hourly shift = 15.041068°. |
| Dignity Hierarchy (Ucc vs Kaset) | **VERIFIED PASS** | Mercury in Virgo (`planet_id=4`, `sign_index=5`) evaluates to `UCC` (Exalted). |
| Lahiri Ayanamsa | **VERIFIED PASS** | J2000.0 = 23.85305556°, rate = 50.29"/year. |
| D9 Navamsa / D3 Drekkana | **VERIFIED PASS** | continuous 108 navamsas & 36 drekkanas match standard formula. |
| Integrity Check | **VERIFIED PASS** | Zero hardcoded test outputs or facade implementations. |

---

## 5. Attack Surface & Stress-Test Evaluation

1. **Polar Latitudes Edge Case ($\phi > 66.5^\circ$):**
   - At extreme northern/southern latitudes, ecliptic intersection with horizon can become ill-defined or very rapid. For Thai astrology engine scope (Thailand latitudes $5.5^\circ \text{N} - 20.5^\circ \text{N}$ and standard global locations), $\tan(\phi)$ is well-behaved.
2. **Equator & Prime Meridian Inputs ($\text{lat}=0, \text{lon}=0$):**
   - Evaluated $\text{lat}=0, \text{lon}=0$: $x = -\sin(\text{LST})\cos(\varepsilon)$, $y = \cos(\text{LST})$. Formula produces valid Ascendant angles without division by zero or domain error.
3. **Null / Unknown Province Fallback:**
   - Tested fallback behavior for non-existent province strings (`"จังหวัดสมมติที่ไม่เคยมียู๋จริง"`). Fallback successfully returns Bangkok coordinates $(13.7563, 100.5018)$.

---

## 6. Caveats

- **No caveats.** The implementation in `thai_astrology.py` handles both pure Python ephemeris and optional Swiss Ephemeris C-extension fallback paths cleanly.

---

## 7. Conclusion

Sub-milestone M1.1 (Thai Astrology Engine Remediation) is **FULLY APPROVED**. 

All 4 defects identified in previous reviews (180° Lagna inversion, GMST double-counting, Mercury in Virgo dignity precedence, and missing ground-truth assertions) have been thoroughly remediated with high mathematical rigor and clean software architecture.

---

## 8. Verification Method

To independently re-verify:

1. **Code Inspection**:
   Inspect `omni_oracle_app/backend/app/engines/thai_astrology.py`:
   - Lines 415–416: Confirm $y = \cos(\text{LST})$ and $x = -\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)$.
   - Line 297: Confirm `EXALTED_SIGNS` check precedes `SIGN_RULERS`.

2. **Pytest Execution**:
   ```bash
   cd omni_oracle_app/backend
   python -m pytest tests/test_thai_astrology.py -v
   ```
   All 10 tests pass with zero failures.
