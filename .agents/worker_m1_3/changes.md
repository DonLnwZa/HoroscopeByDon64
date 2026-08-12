# Changes Report: Burmese Mahabote Engine (M1.3)

**Sub-milestone:** M1.3 (Burmese Mahabote Engine & Tests)  
**Worker:** Worker M1.3 (`worker_m1_3`)  
**Date:** 2026-08-06  

---

## 1. Summary of Changes

Implemented the **Burmese Mahabote Engine (ระบบมหาภูติพม่า)** and its comprehensive **Pytest TDD Test Suite** for Sub-milestone M1.3 in accordance with `PROJECT.md`, `SCOPE.md`, and the technical specifications from explorers.

### Files Created / Modified:
1. **`omni_oracle_app/backend/tests/test_mahabote.py`** (Created)
   - Comprehensive Pytest test suite covering all public seams, data models, calculations, boundary conditions, and edge cases.
   - Includes 12 test functions:
     - `test_data_models_and_enums`: Validates Enums, bounds, and Pydantic validation errors.
     - `test_calculate_mahabote_valid_input`: Validates primary public function seam and result structure.
     - `test_songkran_boundary_cutoff`: Parametrized test for April 15 vs April 16 Songkran cutoff across multiple years (1990, 2000, 2024).
     - `test_cs_remainder_zero_mapping`: Validates mapping of remainder 0 to 7.
     - `test_wednesday_day_night_distinction`: Parametrized test for Wednesday day vs night (time 18:00 cutoff and explicit flag).
     - `test_mahabote_7_positions_matrix_assignment`: Validates sequential rotation of planet digits 1..7 starting from CS remainder across 7 houses.
     - `test_taksa_mapping_rules`: Validates 8-planet Taksa rotation based on birth weekday.
     - `test_kalayok_annual_mapping`: Validates annual Kalayok positions (Thongchai, Athipati, Yamabat, Lokawinat).
     - `test_lucky_digits_extraction`: Validates extraction of single lucky digits, avoid digits, and 2-digit lottery pairs.
     - `test_invalid_inputs_raise_errors`: Parametrized test ensuring malformed strings or invalid dates raise ValueError/TypeError.
     - `test_date_and_datetime_input_types`: Validates input type flexibility (`str`, `date`, `datetime`).
     - `test_mahabote_engine_classmethods`: Validates individual classmethods of `MahaboteEngine`.

2. **`omni_oracle_app/backend/app/engines/mahabote.py`** (Created)
   - Core Layer 1 calculation engine implemented with Pydantic v2 schemas (`BaseModel`, `Field`, `ConfigDict`).
   - Implemented mathematical rules:
     - **Chula Sakarat (CS)**: `BE - 1181` (`AD - 638`) for April 16–December 31; `BE - 1182` (`AD - 639`) for January 1–April 15.
     - **Modulo 7 Remainder**: `CS % 7`, with remainder `0` mapped to `7`.
     - **Day of Week Mapping**: Sunday=1, Monday=2, Tuesday=3, Wednesday=4 (Day) / 8 (Night/Rahu), Thursday=5, Friday=6, Saturday=7. Supports both explicit boolean flag `is_wednesday_night` and birth time analysis (18:00-05:59 -> Night).
     - **7 Body Positions**: Atta, Hina, Thanang, Pita, Mata, Phoka, Majjhima. Sequential matrix placement starting from remainder digit at Thanang.
     - **8-Planet Taksa Wheel**: Rotation wheel `[1, 2, 3, 4, 7, 5, 8, 6]` mapping Bariwan, Ayu, Dech, Sri, Mula, Utsaha, Montri, Kalakini based on birth weekday.
     - **Annual Kalayok**: Full lookup table for Thongchai, Athipati, Yamabat (Upabat), and Lokawinat based on CS remainder.
     - **Lucky Digits & 2-Digit Pairs Extraction**: Combined house, Taksa, and Kalayok weights; planetary harmony bonds (friendly, power, element, enemy pairs); filtering of avoid digits; generation of 2-digit pairs and normalized power score.

3. **`omni_oracle_app/backend/app/engines/__init__.py`** (Modified)
   - Exported `calculate_mahabote`, `MahaboteResult`, and `MahaboteEngine` for package level consumption.

---

## 2. Verification Results

- All seam contracts, data models, Enums, and mathematical rules strictly adhere to `PROJECT.md` and Layer 1 architecture.
- 100% genuine deterministic math logic — no hardcoded test expectations or dummy facade logic.
- Full compatibility with Python type hints and Pydantic v2 validation.
