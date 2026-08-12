# Handoff Report: Public Seam & TDD Pytest Architecture for Burmese Mahabote Engine (M1.3)

**Agent:** Explorer 3 (`explorer_m1_3_3`)  
**Working Directory:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_3_3`  
**Date:** 2026-08-06  

---

## 1. Observation

1. **Module & File Locations:**
   - Public seam engine target location: `omni_oracle_app/backend/app/engines/mahabote.py`
   - Test suite target location: `omni_oracle_app/backend/tests/test_mahabote.py`
   - Configured in `PROJECT.md` lines 70 & 85, and `SCOPE.md` lines 10 & 15.

2. **Existing Codebase Standards:**
   - Examined `omni_oracle_app/backend/app/engines/numerology_7x9.py` (lines 1-100) and `omni_oracle_app/backend/tests/test_numerology_7x9.py` (lines 1-100).
   - Core engines use Pydantic `BaseModel` with `model_config = ConfigDict(arbitrary_types_allowed=True)`.
   - Expose both functional seams (e.g. `calculate_numerology_7x9`) and class-based engines (e.g. `Numerology7x9Engine`).

3. **Key Domain Rules for Burmese Mahabote:**
   - **Songkran Cutoff:** Jan 1 – April 15 uses `CS = Year - 639`; April 16 – Dec 31 uses `CS = Year - 638`.
   - **CS Modulo 7 Remainder:** Calculated as `CS % 7`. If remainder is `0`, it must be mapped to `7`.
   - **Day of Week:** Supports 7 standard days (1=Sun .. 7=Sat) plus Wednesday Night / Rahu (8) when Wednesday birth time is between 18:00 and 05:59 or `is_wednesday_night=True`.
   - **7 Body Positions:** Atta, Hina, Thanang, Pita, Mata, Phoka, Matchima.
   - **Taksa & Kalayok Alignments:** Identifies Sri, Kalakini, Thongchai, Atipati, Yamabat, Lokavinas planets and derives lucky digits and 2-digit lottery pairs.

---

## 2. Logic Chain

1. **Observation Ref 1 & 2:** `PROJECT.md` and `SCOPE.md` dictate that Layer 1 engines in `omni_oracle_app/backend/app/engines/` must follow consistent Pydantic schema and pytest structure.
2. **Observation Ref 2:** Existing engines `numerology_7x9.py` and `thai_astrology.py` export a primary `calculate_<engine>` function that returns a Pydantic result model (`MahaboteResult`), wrapping a class-based engine (`MahaboteEngine`).
3. **Observation Ref 3:** Mahabote mathematical rules require precise boundary handling for Chula Sakarat year calculation (April 15 vs 16), modulo 7 zero-mapping (`0 -> 7`), and Wednesday day/night day-digit determination (4 vs 8).
4. **Conclusion:** Designing explicit Pydantic schemas (`PositionDetail`, `MahaboteChart`, `TaksaInfo`, `KalayokInfo`, `LuckyDigitsResult`, `MahaboteResult`), a class seam (`MahaboteEngine`), and a standalone function seam (`calculate_mahabote`), alongside a 7-tier Pytest suite in `analysis.md`, provides a complete, deterministic blueprint for Worker implementation.

---

## 3. Caveats

- **Calculation Algorithms for Placement & Taksa:** Explorer 3 focused on public seam contracts, input validation, data models, edge cases, and pytest architecture. Internal algorithm details for 7-position grid placement and Taksa/Kalayok interactions are documented in detail in `analysis.md` and synthesized alongside findings from Explorer 1 (`explorer_m1_3_1`) and Explorer 2 (`explorer_m1_3_2`).
- **No Direct Implementation:** Per read-only Explorer constraints, no direct modifications to `omni_oracle_app/backend` files were performed. All specifications are provided in `analysis.md`.

---

## 4. Conclusion

The Public Seam and TDD Pytest Architecture for the Burmese Mahabote Engine (`M1.3`) has been fully specified and documented in `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_3_3\analysis.md`. The design includes:
1. Complete Pydantic schemas and Enums for all inputs, outputs, positions, Taksa, Kalayok, and lucky digits.
2. Public function seam `calculate_mahabote(...)` and class seam `MahaboteEngine`.
3. Input normalization rules supporting strings, dates, times, and Wednesday day/night flags.
4. Comprehensive edge case definitions (Songkran April 15/16, CS % 7 zero mapping, leap years, Wednesday boundary times, invalid input handling).
5. A 7-tier strict TDD Pytest suite architecture for `omni_oracle_app/backend/tests/test_mahabote.py`.

---

## 5. Verification Method

To verify this report:
1. Read `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_3_3\analysis.md` to review the complete Pydantic models, function signatures, edge case matrix, and 7-tier pytest specification.
2. Cross-check model structures against existing engines in `omni_oracle_app/backend/app/engines/numerology_7x9.py` and `omni_oracle_app/backend/app/engines/thai_astrology.py`.
3. Verify that all 6 required task areas (Module location, test location, contracts, input types, edge cases, strict TDD requirements) are fully addressed.
