# Handoff Report: Sub-milestone M1.1 Thai Astrology Engine Specification

**Author:** Explorer 2  
**Date:** 2026-08-06  
**Target Files:**
- `omni_oracle_app/backend/app/engines/thai_astrology.py`
- `omni_oracle_app/backend/tests/test_thai_astrology.py`
**Working Directory:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_1_2`

---

## 1. Observation

Direct observations from project documentation and specification mining:

1. **Project Mandate & Path Layout (`e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md` lines 48-84)**:
   - Target backend application path: `omni_oracle_app/backend/`
   - Calculation engine location: `omni_oracle_app/backend/app/engines/thai_astrology.py`
   - Test suite location: `omni_oracle_app/backend/tests/test_thai_astrology.py`
   - Sub-milestone M1.1: "Pytest seam + Lahiri Ayanamsa natal chart engine"

2. **Astrology Technical Requirements (`e:\เว็บดูดวงเพื่อซื้อหวยไทย\รายงานการวิเคราะห์เชิงลึกระบบโหราศาสตร์และพยากรณ์ศาสตร์เพื่อการพัฒนาระบบสถาปัตยกรรมเว็บไซต์ดูดวง.txt` lines 154-190)**:
   - "Lahiri Ayanamsa" is the required standard for Sidereal zodiac conversion in Thai/Vedic astrology.
   - Tropical to Sidereal offset $\approx 23.5^\circ - 24.2^\circ$.
   - Must calculate 10 planets, Lagna (Ascendant), 12 houses (ตนุ to วินาศ), D9 Navamsa (นวางค์จักร), and D3 Drekkana (ตรียางค์จักร).

3. **Divination Spec Miner Findings (`e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\spec_miner_divination_s0\analysis.md` lines 24-100)**:
   - Swiss Ephemeris (`pysweph` / `swisseph`) is the primary C-library ephemeris engine, with pure Python mathematical formulas as fallback.
   - Planetary mapping IDs: 1=Sun, 2=Moon, 3=Mars, 4=Mercury, 5=Jupiter, 6=Venus, 7=Saturn, 8=Rahu, 9=Ketu, 0=Uranus.

---

## 2. Logic Chain

1. **From Observation 1 & 2**: The Thai Astrology engine must be placed at `omni_oracle_app/backend/app/engines/thai_astrology.py` and accept user birth inputs (date, time, lat, lon, UTC offset) to calculate the Sidereal natal chart.
2. **From Observation 2 & 3**: Ayanamsa conversion formula is $\lambda_{\text{sid}} = (\lambda_{\text{trop}} - \text{Ayanamsa}_{\text{Lahiri}}) \pmod{360^\circ}$. In pure Python fallback mode, Lahiri Ayanamsa at Julian century $T$ is $\text{Ayanamsa}_{\text{Lahiri}}(T) = 23.85305556 + 1.39697128 T + 0.00030878 T^2$ degrees.
3. **From Observation 2**: Lagna (Ascendant) calculation converts local birth time to UTC, computes Greenwich Mean Sidereal Time (GMST) and Local Sidereal Time (LST), applies obliquity of ecliptic $\varepsilon = 23.439291 - 0.0130042 T_0$, derives Tropical Ascendant $\text{Asc}_{\text{trop}} = \text{atan2}(-\cos(LST), \sin(LST)\cos(\varepsilon) + \tan(\text{lat})\sin(\varepsilon))$, and subtracts Lahiri Ayanamsa to obtain Sidereal Lagna.
4. **From Observation 2**: 12 Houses are derived relative to Lagna sign using Whole Sign / Equal House mapping: $\text{HouseSign}(H) = (S_{\text{Lagna}} + H - 1) \pmod{12}$.
5. **From Mathematical Triplicity Analysis**:
   - D9 Navamsa: Each 30° sign is split into 9 sub-arcs of 3°20' (200'). 108 total Navamsas in zodiac form 9 cycles of 12 signs. Unified formula: $S_{\text{D9}} = \lfloor \frac{\lambda_{\text{sid}} \times 60}{200} \rfloor \pmod{12}$.
   - D3 Drekkana: Each 30° sign is split into 3 decans of 10° ($d \in \{0, 1, 2\}$). 1st decan is same sign, 2nd decan is 5th sign, 3rd decan is 9th sign. Unified formula: $S_{\text{D3}} = (S + 4d) \pmod{12}$.
6. **From Feature Requirements**: Auspicious lucky digits are extracted from Lagna Lord (`SIGN_RULERS[S_Lagna]`), Kamma Lord (10th house ruler), Lapha Lord (11th house ruler), Mahadasha Planet (derived from Moon Nakshatra $N_{\text{nak}} = \lfloor \frac{\lambda_{\text{Moon, sid}}}{13.33333333^\circ} \rfloor \pmod 9$), and Exalted/Kaset dignities.

---

## 3. Caveats

- **Swiss Ephemeris Dependency**: `pysweph` / `swisseph` C-bindings may require build tools on some environments. A pure Python fallback formula for Lahiri Ayanamsa, GMST/LST, and planetary longitudes is fully specified in `analysis.md` to guarantee test suite execution in any CI environment without native binary dependencies.
- **Scoping**: This investigation is strictly read-only and does not write code to `omni_oracle_app`.

---

## 4. Conclusion

The specification for `omni_oracle_app/backend/app/engines/thai_astrology.py` and `omni_oracle_app/backend/tests/test_thai_astrology.py` is fully derived, mathematically proven, and documented in `analysis.md`. The public seam (`ThaiAstrologyEngine`, `ThaiAstrologyInput`, `ThaiAstrologyResult`) is designed and ready for TDD implementation by Implementer agents.

---

## 5. Verification Method

To verify the investigation and subsequent TDD implementation:

1. **Inspect Analysis Artifacts**:
   - Review `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_1_2\analysis.md` for mathematical formulas, Pydantic schemas, and test suite specifications.
2. **Execute Pytest Suite (when implemented by M1.1 Implementer)**:
   ```powershell
   cd e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend
   pytest tests/test_thai_astrology.py -v
   ```
3. **Invalidation Conditions**:
   - Failure of Lahiri Ayanamsa degrees to stay within $[23.5^\circ, 24.5^\circ]$ for modern dates.
   - Discrepancy in D9 Navamsa sign index relative to $S_{\text{D9}} = \lfloor \frac{\lambda_{\text{sid}} \times 60}{200} \rfloor \pmod{12}$.
   - Discrepancy in D3 Drekkana sign index relative to $S_{\text{D3}} = (S + 4d) \pmod{12}$.
