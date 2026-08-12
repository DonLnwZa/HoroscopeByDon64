# Review & Handoff Report: Sub-milestone M1.1 Thai Astrology Engine

**Role:** Reviewer 2 & Adversarial Critic (`reviewer_m1_1_2`)  
**Target Module:** `omni_oracle_app/backend/app/engines/thai_astrology.py`  
**Target Test Suite:** `omni_oracle_app/backend/tests/test_thai_astrology.py`  
**Worker Handoff Reviewed:** `.agents/worker_m1_1/handoff.md`  
**Verdict:** `REQUEST_CHANGES`  
**Date:** 2026-08-06  

---

## Review Summary

**Verdict:** **REQUEST_CHANGES**

During rigorous adversarial mathematical auditing of `omni_oracle_app/backend/app/engines/thai_astrology.py`, a **Critical Astronomical Math Error** was discovered in the Lagna (Ascendant) calculation routine `calculate_lagna_sidereal()`. Both $y$ and $x$ trigonometric components have inverted signs, causing the function to calculate the **Descendant (Western Horizon / 7th House / ปัตนิ)** instead of the **Ascendant (Eastern Horizon / 1st House / ตนุ)**, shifting the entire natal chart by 180 degrees (6 zodiac signs).

---

## 1. Observation

1. **Target File Inspection:**
   - Module path: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\app\engines\thai_astrology.py`
   - Test suite path: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\tests\test_thai_astrology.py`

2. **Verbatim Code Analysis — Lagna Calculation (`calculate_lagna_sidereal`):**
   `thai_astrology.py`, lines 404-419:
   ```python
   def calculate_lagna_sidereal(jd: float, ut_hours: float, lat: float, lon: float, ayanamsa: float) -> float:
       t0 = (jd - 2451545.0) / 36525.0
       gmst0 = 100.46061837 + (36000.770053608 * t0) + (0.000387933 * t0 * t0)
       gmst = (gmst0 + 360.98564736629 * (ut_hours / 24.0)) % 360.0
       lst = (gmst + lon) % 360.0

       rad = math.radians
       eps = 23.439291 - 0.0130042 * t0

       y = -math.cos(rad(lst))
       x = (math.sin(rad(lst)) * math.cos(rad(eps))) + (math.tan(rad(lat)) * math.sin(rad(eps)))

       asc_trop = math.degrees(math.atan2(y, x)) % 360.0
       asc_sid = (asc_trop - ayanamsa) % 360.0
       return asc_sid
   ```

3. **Verbatim Code Analysis — Test Suite (`test_lagna_and_house_mapping`):**
   `test_thai_astrology.py`, lines 77-86:
   ```python
   def test_lagna_and_house_mapping():
       res = calculate_thai_astrology("2026-08-05", "08:00", "กรุงเทพมหานคร")
       lagna_sign = res.lagna.rasi_index
       assert res.houses[0].rasi_index == lagna_sign

       for i in range(12):
           expected_sign = (lagna_sign + i) % 12
           assert res.houses[i].rasi_index == expected_sign
           assert res.houses[i].house_number == i + 1
   ```

---

## 2. Logic Chain & Mathematical Proof of Bug

1. **Standard Astronomical Definition of Ascendant (Lagna):**
   The Ascendant ($\text{ASC}$) is the ecliptic longitude rising on the Eastern horizon.
   The mathematical relationship between Local Sidereal Time ($\theta = \text{LST}$), Obliquity of the Ecliptic ($\varepsilon$), and Observer's Latitude ($\phi$) is:
   $$\tan(\text{ASC}) = \frac{\cos \theta}{-\sin \theta \cos \varepsilon - \tan \phi \sin \varepsilon}$$

   Expressing this as $\text{atan2}(y, x)$:
   - $y_{\text{true}} = \cos \theta$
   - $x_{\text{true}} = -\sin \theta \cos \varepsilon - \tan \phi \sin \varepsilon$

2. **Implementation in `thai_astrology.py`:**
   Lines 414-415 implement:
   - $y_{\text{code}} = -\cos \theta = -y_{\text{true}}$
   - $x_{\text{code}} = \sin \theta \cos \varepsilon + \tan \phi \sin \varepsilon = -x_{\text{true}}$

3. **Effect of Double Sign Inversion:**
   For any $(x, y)$, $\text{atan2}(-y, -x) = \text{atan2}(y, x) + 180^\circ \pmod{360^\circ}$.
   Therefore:
   $$\text{asc\_trop}_{\text{code}} = (\text{Ascendant}_{\text{true}} + 180^\circ) \pmod{360^\circ}$$
   This calculates the **Descendant (Western Horizon)** rather than the **Ascendant (Eastern Horizon)**.

4. **Concrete Numerical Test Case:**
   - Case: $\text{LST} = 0^\circ$ (RAMC = $0^\circ$), Latitude $\phi = 13.7563^\circ$ (Bangkok), Obliquity $\varepsilon = 23.44^\circ$.
   - True Ascendant: $y = \cos(0^\circ) = +1.0$, $x = -\sin(0^\circ)\cos(\varepsilon) - \tan(13.7563^\circ)\sin(23.44^\circ) = -0.09737$.
     $\text{atan2}(+1.0, -0.09737) = +95.57^\circ$ (Cancer $5.57^\circ$, Eastern Horizon).
   - Code Output: $y = -\cos(0^\circ) = -1.0$, $x = +0.09737$.
     $\text{atan2}(-1.0, +0.09737) = -84.43^\circ \equiv 275.57^\circ$ (Capricorn $5.57^\circ$, Western Horizon).
   - Difference: **Exactly $180^\circ$ error** (Descendant instead of Ascendant).

5. **Test Suite Blindspot:**
   `test_lagna_and_house_mapping` in `test_thai_astrology.py` checked if `res.houses[0].rasi_index == res.lagna.rasi_index`. Because `res.houses[0]` was constructed from `res.lagna.rasi_index`, the test passed tautologically despite `res.lagna.rasi_index` being 6 signs off from the true astronomical Lagna.

---

## 3. Findings & Detailed Defect Report

### [Critical] Finding 1: 180° Inversion in Sidereal Lagna Calculation
- **What**: `calculate_lagna_sidereal()` calculates the Descendant (7th house / ปัตนิ) instead of the Ascendant (1st house / ตนุ).
- **Where**: `omni_oracle_app/backend/app/engines/thai_astrology.py`, lines 414-417.
- **Why**: Trigonometric components $y$ and $x$ have inverted signs.
- **Impact**: All natal chart readings, Lagna signs, house lords, primary lucky planets, and lucky digit extractions are wrong.
- **Suggestion**: Change lines 414-415 to:
  ```python
  y = math.cos(rad(lst))
  x = -math.sin(rad(lst)) * math.cos(rad(eps)) - math.tan(rad(lat)) * math.sin(rad(eps))
  ```

### [Major] Finding 2: Tautological Lagna Assertions in Test Suite
- **What**: Test suite does not verify Lagna against ground-truth astronomical reference dates.
- **Where**: `omni_oracle_app/backend/tests/test_thai_astrology.py`, `test_lagna_and_house_mapping()`.
- **Why**: Asserts `res.houses[0].rasi_index == res.lagna.rasi_index` without checking against known external Lagna positions.
- **Suggestion**: Add test cases with known birth dates/times and explicit expected Lagna signs (e.g. verifying morning sunrise chart in Bangkok has Lagna matching Sun's sign).

---

## 4. Verified Claims & Stress Test Results

| Component / Claim | Verification Status | Notes |
|---|---|---|
| Lahiri Ayanamsa Polynomial | **PASS** | J2000.0 returns ~23.853°, rate ~50.29"/yr matches N.C. Lahiri standard. |
| 10 Planets (0-9 Enums & Keys) | **PASS** | Includes Uranus (0), Sun (1) .. Ketu (9). |
| D9 Navamsa Formula | **PASS** | `floor((sid_deg * 60) / 200) % 12` accurately computes continuous 108 navamsas. |
| D3 Drekkana Formula | **PASS** | `(sign_idx + 4 * decan_idx) % 12` correctly computes 1st, 5th, 9th decans. |
| Planetary Dignities | **PASS** | Kaset, Ucc, Nit, Pra, Normal evaluated correctly. |
| Edge Cases & Defaults | **PASS** | Handles missing time ("12:00"), unknown province fallback, degree % 360. |
| Lucky Digits Extraction | **PASS** | Returns single-digit list (0-9) padded to minimum length. |
| Lagna Sidereal Math | **FAIL** | 180° inversion bug ($y, x$ sign negation). |

---

## 5. Caveats

- **Dual Engine (Swisseph vs Pure Python)**: If `swisseph` is installed, planetary positions use C extension, but Lagna calculation in pure Python still suffers from the sign inversion bug unless corrected.
- No other caveats.

---

## 6. Conclusion

Sub-milestone M1.1 (`thai_astrology.py`) cannot be approved in its current state due to the Critical calculation error in `calculate_lagna_sidereal()`. 

**Action Required from Implementer (`worker_m1_1`):**
1. Correct the $y$ and $x$ signs in `calculate_lagna_sidereal()` in `thai_astrology.py`.
2. Add ground-truth Lagna test assertion in `test_thai_astrology.py`.
3. Re-run Pytest suite and submit updated handoff.

---

## 7. Verification Method

After implementer fixes `thai_astrology.py`:

1. Inspect line 414-415 of `thai_astrology.py` to ensure $y = \cos(\text{LST})$ and $x = -\sin(\text{LST})\cos(\varepsilon) - \tan(\phi)\sin(\varepsilon)$.
2. Run pytest suite:
   ```bash
   cd omni_oracle_app/backend
   pytest tests/test_thai_astrology.py -v
   ```
3. Test a known morning chart: e.g. 2026-08-05 06:00 AM (Sunrise) in Bangkok. Sun is in Cancer (~18° sidereal). Since it's sunrise, Lagna MUST also be in Cancer.
