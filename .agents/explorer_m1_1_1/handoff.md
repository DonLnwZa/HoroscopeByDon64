# Handoff Report: Sub-milestone M1.1 — Thai Astrology Engine Requirements & Seam Design

## 1. Observation
- **Project Structure**: Target directory specified in `PROJECT.md` is `omni_oracle_app/backend/app/engines/thai_astrology.py` and Pytest suite seam at `omni_oracle_app/backend/tests/test_thai_astrology.py`.
- **System Specifications**:
  - `ORIGINAL_REQUEST.md`: Requires Real-time natal chart calculation via 4 divination systems + TDD (Red -> Green -> Refactor) using Pytest.
  - `PROJECT.md`: Feature 1 specifies Natal chart calculation (Lahiri Ayanamsa, 10 planets 0-9, 12 houses Tanu to Vinasa, D9 Navamsa, D3 Drekkana).
  - `รายงานการวิเคราะห์เชิงลึก...txt` (Section 4): Sidereal Zodiac (นิรายนะ) using Lahiri Ayanamsa (~23°-24° offset), 10 planets (0-9), 12 houses (ตนุ ถึง วินาศ), divisional charts D9 (นวางค์) and D3 (ตรียางค์), and optional fallback integration with Swiss Ephemeris (`swisseph`).

## 2. Logic Chain
- **Observation -> Standard Choice**: Thai astrology strictly uses the Sidereal Zodiac frame of reference offset by Lahiri Ayanamsa. Therefore, calculations must subtract Lahiri Ayanamsa from Tropical ecliptic longitudes before assigning Rasi signs.
- **Observation -> Planet Digit Mapping**: The 10 planets map to single digits `0` to `9`:
  - 1=Sun, 2=Moon, 3=Mars, 4=Mercury, 5=Jupiter, 6=Venus, 7=Saturn, 8=Rahu, 9=Ketu, 0=Uranus.
- **Observation -> House Placement**: Lagna (Ascendant) Rasi sign forms House 1 (ตนุ). The 12 houses progress in zodiacal order (ตนุ, กดุมภะ, สหัชชะ, พันธุ, ปุตตะ, อริ, ปัตนิ, มรณะ, ศุภะ, กัมมะ, ลาภะ, วินาศ).
- **Observation -> Divisional Harmonics**:
  - D9 Navamsa divides each sign into 9 parts ($3^\circ 20'$ each), starting sign determined by element ($S \pmod 4$: Fire->Aries, Earth->Capricorn, Air->Libra, Water->Cancer).
  - D3 Drekkana divides each sign into 3 parts ($10^\circ$ each), pointing to 1st (same sign), 2nd (5th sign), 3rd (9th sign).
- **Observation -> Resilience & Dependency Strategy**: To avoid environment compilation/installation failures, `thai_astrology.py` should implement a dual-engine architecture: primary try `pyswisseph`, fallback to pure Python Jean Meeus / Keplerian formulas.

## 3. Caveats
- Timezone handling: Thai birth times are local ICT (UTC+7). Input conversion must account for UTC offset when computing Julian Day ($JD$).
- Default coordinates: If `birth_province` is not specified or unrecognized, fallback to Bangkok coordinates ($13.7563^\circ\text{ N}, 100.5018^\circ\text{ E}$).

## 4. Conclusion
The requirements, data contracts, and public interface for Sub-milestone M1.1 (Thai Astrology Engine & Pytest Suite) are fully specified and documented in `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_1_1\analysis.md`. Implementer can proceed directly to TDD Red stage by writing `omni_oracle_app/backend/tests/test_thai_astrology.py` followed by `omni_oracle_app/backend/app/engines/thai_astrology.py`.

## 5. Verification Method
- Inspect analysis file: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_1_1\analysis.md`.
- Inspect handoff report: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_1_1\handoff.md`.
- When code is implemented: Run `pytest omni_oracle_app/backend/tests/test_thai_astrology.py` from project root.
