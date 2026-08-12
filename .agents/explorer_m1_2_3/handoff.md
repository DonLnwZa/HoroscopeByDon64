# Handoff Report: Sub-milestone M1.2 — 7-Digit 9-Base Numerology Engine Analysis

## 1. Observation

1. **System & Project Requirements**:
   - `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md` line 6: "สร้างเว็บแอปพลิเคชันที่นำศาสตร์พยากรณ์ 4 แขนง (โหราศาสตร์, เลข 7 ตัว 9 ฐาน, มหาภูติพม่า, ไพ่ทาโรต์) มาวิเคราะห์ร่วมกับสถิติหวยย้อนหลัง 1 ปี... พัฒนาด้วยหลักการ TDD (Test-Driven Development)".
   - `e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md` line 69 & 84: Engine path `omni_oracle_app/backend/app/engines/numerology_7x9.py`, Test path `omni_oracle_app/backend/tests/test_numerology_7x9.py`.
   - `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_divination\SCOPE.md` lines 9 & 21: Sub-milestone M1.2 scope requires Pytest seam + 7-Digit 9-Base matrix engine.

2. **Domain Mathematics & Reference Document**:
   - `e:\เว็บดูดวงเพื่อซื้อหวยไทย\รายงานการวิเคราะห์เชิงลึกระบบโหราศาสตร์และพยากรณ์ศาสตร์เพื่อการพัฒนาระบบสถาปัตยกรรมเว็บไซต์ดูดวง.txt` Section 2 (lines 66-110):
     - Base 1 (Day Base): 7-column sequence starting from day of week (1..7).
     - Base 2 (Month Base): Thai lunar month (1..12) normalized to 1..7.
     - Base 3 (Year Base): Thai zodiac year (1..12) normalized to 1..7.
     - Base 4 (Sum Base / กำลังดาว): Vertical sum of Base 1 + Base 2 + Base 3 (values 3..21).
     - 21 Astrological Houses: Row 1 (**อัตตะ, หินะ, ธนัง, ปิตา, มาตา, โภคา, มัชฌิมา**), Row 2 (**ตะนุ, กดุมภะ, สหัชชะ, พันธุ, ปุตตะ, อริ, ปัตนิ**), Row 3 (**มรณะ, ศุภะ, กัมมะ, ลาภะ, พยายะ, ทาสา, ทาสี**).

3. **Existing Codebase Patterns**:
   - In `omni_oracle_app/backend/app/engines/thai_astrology.py` (M1.1 implementation), Pydantic `BaseModel` structures are used with properties, enums, helper methods, and a single main entry point function `calculate_thai_astrology(...)`.

---

## 2. Logic Chain

1. **Interface & Data Model Standard (Obs. 1, Obs. 3)**:
   Following M1.1's architectural seam pattern, M1.2 must define 5 core Pydantic data models:
   - `HouseType`: Enum for house classification (`AUSPICIOUS`, `INAUSPICIUS`, `NEUTRAL`).
   - `HouseDetail7x9`: Holds single house attributes (`house_name_th`, `house_name_en`, `row_index`, `col_index`, `digit_value`, `house_type`, `base4_power`, with `.is_auspicious` and `.is_inauspicious` properties).
   - `BaseCollisionInfo`: Details digit collisions across the matrix (`digit`, `count`, `houses`, `has_inauspicious_collision`, `has_auspicious_collision`, `base4_powers`, `collision_score`).
   - `NumerologyMatrix`: Contains 9 rows of 7-digit integer lists (`base1_day` .. `base9`, and `matrix_grid`).
   - `Numerology7x9Result`: Public result container with `.get_house(...)`, `.get_digit_collision(...)`, and `lucky_numbers`.

2. **Deterministic Calculation Logic (Obs. 2)**:
   - Inputs to `calculate_numerology_7x9`: `birth_date: str`, with optional `birth_day_override`, `lunar_month_override`, and `zodiac_year_override`.
   - Day of week conversion: ISO weekday (`0`=Mon..`6`=Sun) converted to Thai weekday (`1`=Sun..`7`=Sat) via `(dt.weekday() + 1) % 7 + 1`.
   - Month & Year normalization: `((val - 1) % 7) + 1`.
   - Row generation: Base 1, 2, 3 sequence generation using 1-based modulo 7 indexing; Base 4 vertical sum; Base 5 to 9 deterministic math functions.

3. **Validation & Edge Case Handling**:
   - `birth_date` string validation (`YYYY-MM-DD`) and range check (`1900-01-01` to `2100-12-31`).
   - Bounds checking for overrides (`birth_day_override` in 1..7, `lunar_month_override` in 1..12, `zodiac_year_override` in 1..12).

4. **Pytest Suite Seam Benchmark Scenarios**:
   - **Benchmark 1**: Sunday (1) / Month 1 / Year 1 override testing symmetric matrix generation where Base 1 = Base 2 = Base 3 = `[1, 2, 3, 4, 5, 6, 7]` and Base 4 sum = `[3, 6, 9, 12, 15, 18, 21]`.
   - **Benchmark 2**: Realistic birthdate `1995-08-15` (Tuesday = 3, Month 8 -> 1, Year 12 -> 5) testing asymmetric matrix generation, digit 7 auspicious collision detection, digit 5 inauspicious collision detection, and lucky number extraction.

---

## 3. Caveats

- **Lunar Month Accuracy**: Official Thai lunar calendars include extra leap months (อธิกมาส / อธิกวาร). The fallback formula approximates solar month to lunar month when `lunar_month_override` is not provided. Users can provide precise lunar month overrides.
- **Base 5-9 Variants**: Different numerology traditions have minor variations for derived Base 5-9. The engine implements deterministic, standardized modular arithmetic rules for Base 5-9.

---

## 4. Conclusion

The specification and seam design for Sub-milestone M1.2 (`omni_oracle_app/backend/app/engines/numerology_7x9.py` and `omni_oracle_app/backend/tests/test_numerology_7x9.py`) is fully formulated, mathematically verified, and ready for TDD implementation (Red -> Green -> Refactor cycle).

All findings and design schemas are recorded in `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_2_3\analysis.md`.

---

## 5. Verification Method

To verify the analysis and seam design:

1. **Inspect Analysis Report**:
   Read `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_2_3\analysis.md` and confirm all 5 data models, entry point signature, validation rules, and benchmark test scenarios are completely specified.

2. **Verify Mathematical Consistency**:
   - Benchmark 1: Run manual or script computation for Day 1, Month 1, Year 1 -> Verify Base 4 sum equals `[3, 6, 9, 12, 15, 18, 21]`.
   - Benchmark 2: Run manual computation for Day 3, Month 1, Year 5 -> Verify Base 4 sum equals `[9, 12, 15, 11, 14, 10, 13]` and digit 7 collides across houses มาตา, ปัตนิ, กัมมะ.
