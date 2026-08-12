# Handoff Report — Explorer 1: E2E Test Architecture & Infra Specification

## 1. Observation

### 1.1 Core Codebase & Framework Architecture
- **Backend Application Entry Point**: `omni_oracle_app/backend/app.py`
  - Web Framework: **Flask** (`from flask import Flask, request, jsonify, send_from_directory`) with CORS enabled (`from flask_cors import CORS`).
  - Active Routes observed:
    - `GET /` & `GET /<path>` (lines 19-25): Serves frontend static files from `omni_oracle_app/frontend`.
    - `GET /api/health` (lines 32-34): Returns `{"status": "ok"}`.
    - `GET /api/lottery/stats` (lines 36-44): Returns hot/cold numbers and digit frequencies.
    - `POST /api/divine` (lines 46-92): Main divination route. Currently expects legacy parameters (`birth_day_of_week`, `birth_month_lunar`, `birth_year_animal`) and random Tarot draws (`tarot_engine.draw_celtic_cross()`).
- **Engine Modules Directory**: `omni_oracle_app/backend/app/engines/`
  - `thai_astrology.py`: Computes natal chart, Lahiri Ayanamsa, Lagna, 10 planets, 12 houses, D9, D3, dignities, and lucky numbers.
  - `numerology_7x9.py`: Computes 7x9 Base grid (Day, Month, Year), Base 4 strength, house collisions.
  - `mahabote.py`: Computes Chula Sakarat year, 7 positions (Panga, Puti, Marana, Adhipati, Raja, Atta, Majjhima), Taksa day, Kalayok day.
  - `tarot.py`: Contains `TarotEngine` class with 78 cards (22 Major, 56 Minor) and `draw_celtic_cross()` spread generator.
  - `lottery_stats.py`: Loads 24 historical draw records from `omni_oracle_app/backend/data/lottery_results_past_1_year.json`.
  - `number_recommender.py`: Generates 2-digit, 3-digit, and 6-digit lucky numbers.
  - `oracle_synthesis.py`: Generates holistic divination reading text and safety disclaimer.

### 1.2 Required Upgrades & Target API Contracts
Based on `ORIGINAL_REQUEST.md` (lines 10-34), `PROJECT.md` (lines 18-97), and `SCOPE.md` (lines 1-30):
1. **R1 (Thai Lunar Calendar Auto-Calculation)**:
   - Request must accept `birth_date` ("YYYY-MM-DD") and `birth_time` ("HH:MM").
   - 6:00 AM cutoff rule: If `birth_time` < "06:00" (e.g. 05:30), the Thai astrological day of week shifts to the previous Gregorian day. If `birth_time` >= "06:00", it remains current day.
   - Response `/api/divine` must contain `chart.lunar_calendar`: `day_of_week` (string), `lunar_month` (1..12), `zodiac_year` (string), `cutoff_applied` (boolean).
2. **R2 (Interactive Tarot Selection)**:
   - Request body for `/api/divine` must accept `selected_tarot_cards`: an array of exactly 10 integers in range `[0..77]`.
   - `tarot_engine.draw_celtic_cross(selected_cards)` must map these 10 card indices to the 10 Celtic Cross positions.
3. **R3 (Heat Index Backtesting)**:
   - Response `/api/divine` must include `heat_index` detailing win count over past 1 year (24 GLO draws) for recommended numbers:
     - `HOT`: win_count >= 3
     - `WARM`: win_count in [1, 2]
     - `COLD`: win_count == 0
4. **R4 (Divination Transparency)**:
   - Response `/api/divine` must include `number_origins`: dictionary mapping each recommended lucky number to an array of engine origin explanation strings.

### 1.3 Legacy Test Discrepancy Observation
- In `omni_oracle_app/backend/tests/test_tier1_feature_coverage.py` and `test_e2e_full_stack.py`:
  - Existing test files contained legacy synthetic imports using FastAPI (`from app.main import app`) or mocked `/api/v1/predict` endpoints.
  - **Correction required**: E2E test suite must be aligned with the actual project target — Flask application in `omni_oracle_app/backend/app.py` with endpoint `/api/divine` and Flask Test Client (`app.test_client()`).

---

## 2. Logic Chain

1. **Premise**: The task objective is to design `TEST_INFRA.md` and detail Tier 1 (Feature Coverage) and Tier 2 (Boundary & Safety) E2E test specifications for the Omni-Oracle web application.
2. **Observation → Framework Choice**: `omni_oracle_app/backend/app.py` uses **Flask**. Therefore, the native Python testing framework is `pytest` coupled with Flask's `app.test_client()`.
3. **Observation → Test Directory Structure**: `PROJECT.md` specifies E2E test directory at `omni_oracle_app/e2e_tests/` and backend tests at `omni_oracle_app/backend/tests/`.
4. **Requirement Analysis → Test Taxonomy**:
   - **Tier 1 (Feature Coverage)**: Requires >=5 tests per feature (R1, R2, R3, R4) = 20 test cases minimum testing happy path, output formatting, schema compliance, and engine integrations.
   - **Tier 2 (Boundary & Corner Cases)**: Requires >=5 tests per feature (R1, R2, R3, R4) = 20 test cases minimum testing boundary inputs (05:59:59 vs 06:00:00, 00:00:00, 23:59:59), invalid tarot indices (<0, >77, duplicates, length != 10), win count thresholds (0 COLD, 1-2 WARM, >=3 HOT), and missing engine origins/fallback handling.
5. **Conclusion**: Formulate a complete design for `TEST_INFRA.md` and explicit test specifications for all 40 Tier 1 and Tier 2 E2E test cases so that downstream test authoring agents can implement them directly.

---

## 3. Caveats

- **No source code implementation**: As an Explorer agent, no application source code modifications were performed in `omni_oracle_app/backend/` or `omni_oracle_app/frontend/`.
- **Frontend execution environment**: Unit testing for React UI components (`app.jsx`) requires Jest/React Testing Library setup if component-level JS testing is desired, but opaque-box E2E API contract testing is driven via `pytest` + Flask test client against `/api/divine`.

---

## 4. Conclusion

### 4.1 Proposed `TEST_INFRA.md` Content & Structure

The file `e:\เว็บดูดวงเพื่อซื้อหวยไทย\TEST_INFRA.md` should be structured as follows:

```markdown
# Omni-Oracle E2E Test Infrastructure Specification (`TEST_INFRA.md`)

## 1. Overview & Test Architecture
- **Framework**: `pytest` 8.x + Flask Test Client (`app.test_client()`).
- **Scope**: Opaque-box E2E integration testing covering `/api/divine`, `/api/health`, `/api/lottery/stats`.
- **Directory Structure**:
  - `omni_oracle_app/e2e_tests/`
    - `conftest.py`: Fixtures (`app_client`, `mock_lottery_data`, `sample_divine_payload`).
    - `test_tier1_feature_coverage.py`: 20 Tier 1 test cases (5 per feature R1-R4).
    - `test_tier2_boundary_safety.py`: 20 Tier 2 test cases (5 per feature R1-R4).
    - `test_tier3_pairwise_integration.py`: Tier 3 Pairwise Integration test cases.
    - `test_tier4_realworld_scenarios.py`: Tier 4 Real-World Application Journey test cases.

## 2. Test Fixtures (`conftest.py`)
- `app_client`: Instantiates Flask test client from `app.py`.
- `valid_divine_payload`: Standard request body containing `birth_date="1992-05-15"`, `birth_time="05:30"`, `selected_tarot_cards=[0, 12, 25, 31, 44, 50, 61, 72, 5, 18]`.
- `mock_lottery_file`: Path to `omni_oracle_app/backend/data/lottery_results_past_1_year.json`.

## 3. Test Runner Commands
```bash
# Run all E2E test suites
python -m pytest omni_oracle_app/e2e_tests/ -v

# Run specific tier test suite
python -m pytest omni_oracle_app/e2e_tests/test_tier1_feature_coverage.py -v
python -m pytest omni_oracle_app/e2e_tests/test_tier2_boundary_safety.py -v
```
```

---

### 4.2 Detailed Tier 1 (Feature Coverage) Test Case Specifications (20 Test Cases)

#### Feature R1: Auto-Approximate Thai Lunar Calendar & 6:00 AM Cutoff Rule
1. **`test_r1_t1_01_lunar_calc_daytime`**:
   - *Description*: Verify birth time >= 06:00 ("14:30") processes Thai day of week without shift and returns `cutoff_applied: false`.
   - *Input*: `birth_date="1992-05-15"`, `birth_time="14:30"`.
   - *Assertions*: Response `chart.lunar_calendar.cutoff_applied == False`, `day_of_week` matches Thursday.
2. **`test_r1_t1_02_lunar_calc_early_morning_cutoff`**:
   - *Description*: Verify birth time < 06:00 ("05:30") applies 6am cutoff rule and shifts day of week to previous day.
   - *Input*: `birth_date="1992-05-15"`, `birth_time="05:30"`.
   - *Assertions*: Response `chart.lunar_calendar.cutoff_applied == True`, `day_of_week` shifts to Wednesday.
3. **`test_r1_t1_03_lunar_month_range`**:
   - *Description*: Verify auto-calculated `lunar_month` is an integer in range [1, 12].
   - *Input*: Various dates across the year.
   - *Assertions*: `1 <= chart.lunar_calendar.lunar_month <= 12`.
4. **`test_r1_t1_04_zodiac_year_mapping`**:
   - *Description*: Verify auto-calculated `zodiac_year` returns valid Thai/English zodiac animal name.
   - *Input*: `birth_date="1992-05-15"`.
   - *Assertions*: `chart.lunar_calendar.zodiac_year` in `["Monkey", "ปีวอก", ...]`.
5. **`test_r1_t1_05_lunar_calendar_divine_response_structure`**:
   - *Description*: Verify `/api/divine` payload contains `chart.lunar_calendar` dictionary with all 4 required keys.
   - *Input*: Standard POST `/api/divine` request.
   - *Assertions*: `chart.lunar_calendar` contains `day_of_week`, `lunar_month`, `zodiac_year`, `cutoff_applied`.

#### Feature R2: Interactive Tarot Selection
6. **`test_r2_t1_01_tarot_valid_10_cards`**:
   - *Description*: Submit valid array of 10 distinct card indices `[0, 12, 25, 31, 44, 50, 61, 72, 5, 18]`.
   - *Input*: POST `/api/divine` with `selected_tarot_cards`.
   - *Assertions*: HTTP 200 OK, `tarot_reading.spread` contains exactly 10 cards.
7. **`test_r2_t1_02_tarot_position_mapping`**:
   - *Description*: Verify returned 10 cards map 1-to-1 to the 10 Celtic Cross position names in exact order.
   - *Input*: Array of 10 card indices.
   - *Assertions*: Position 1 = "สถานการณ์ปัจจุบัน", Position 10 = "บทสรุปของสถานการณ์".
8. **`test_r2_t1_03_tarot_major_minor_arcana_metadata`**:
   - *Description*: Verify Major Arcana (indices 0..21) and Minor Arcana (indices 22..77) metadata classification.
   - *Input*: `selected_tarot_cards=[0, 21, 22, 77, 5, 10, 30, 40, 50, 60]`.
   - *Assertions*: Card 0 & 21 are "Major Arcana", Card 22 & 77 are "Minor Arcana".
9. **`test_r2_t1_04_tarot_reversal_state_handling`**:
   - *Description*: Verify each drawn card includes `is_reversed` boolean flag and position meaning.
   - *Input*: 10 selected cards.
   - *Assertions*: `isinstance(card["is_reversed"], bool)` for all 10 cards.
10. **`test_r2_t1_05_tarot_divine_endpoint_integration`**:
    - *Description*: Verify `/api/divine` passes `selected_tarot_cards` array into `tarot_engine.draw_celtic_cross(selected_cards)`.
    - *Input*: POST request to `/api/divine`.
    - *Assertions*: Response `tarot_reading.spread[i].id` matches selected card indices.

#### Feature R3: Backtesting Heat Index
11. **`test_r3_t1_01_heat_index_response_structure`**:
    - *Description*: Verify `/api/divine` response JSON contains `heat_index` with `two_digit`, `three_digit`, `six_digit` sections.
    - *Input*: Standard POST `/api/divine`.
    - *Assertions*: `heat_index` contains all 3 digit category lists.
12. **`test_r3_t1_02_heat_index_win_count_calculation`**:
    - *Description*: Verify win count is correctly computed against 24 GLO historical draws.
    - *Input*: Recommended numbers.
    - *Assertions*: `win_count` is an integer >= 0 for every number in `heat_index`.
13. **`test_r3_t1_03_heat_index_hot_classification`**:
    - *Description*: Verify recommended number with win_count >= 3 is assigned level `"HOT"`.
    - *Input*: Recommended numbers evaluated against GLO data.
    - *Assertions*: If `item["win_count"] >= 3`, `item["level"] == "HOT"`.
14. **`test_r3_t1_04_heat_index_warm_classification`**:
    - *Description*: Verify recommended number with win_count in [1, 2] is assigned level `"WARM"`.
    - *Input*: Recommended numbers evaluated against GLO data.
    - *Assertions*: If `item["win_count"] in [1, 2]`, `item["level"] == "WARM"`.
15. **`test_r3_t1_05_heat_index_cold_classification`**:
    - *Description*: Verify recommended number with win_count == 0 is assigned level `"COLD"`.
    - *Input*: Recommended numbers evaluated against GLO data.
    - *Assertions*: If `item["win_count"] == 0`, `item["level"] == "COLD"`.

#### Feature R4: Divination Transparency (Number Origins)
16. **`test_r4_t1_01_number_origins_presence`**:
    - *Description*: Verify `/api/divine` response JSON contains `number_origins` dictionary.
    - *Input*: Standard POST `/api/divine`.
    - *Assertions*: `number_origins` field exists and is a dictionary.
17. **`test_r4_t1_02_origins_mapped_for_all_recommended_numbers`**:
    - *Description*: Verify every recommended number in `lucky_numbers` has a key in `number_origins`.
    - *Input*: Standard `/api/divine` response.
    - *Assertions*: For every `num` in `lucky_numbers.two_digit`, `three_digit`, `six_digit`, `num in number_origins`.
18. **`test_r4_t1_03_origin_explanation_format`**:
    - *Description*: Verify each value in `number_origins` is a non-empty list of descriptive strings.
    - *Input*: Standard `/api/divine` response.
    - *Assertions*: `isinstance(origins[num], list)` and `len(origins[num]) > 0`.
19. **`test_r4_t1_04_origin_tracks_engine_sources`**:
    - *Description*: Verify origin strings reference specific divination engines (Mahabote, Thai Astrology, Tarot Card #X, Numerology 7x9).
    - *Input*: `/api/divine` response `number_origins`.
    - *Assertions*: Origin strings contain engine keywords like `"Mahabote"`, `"Astrology"`, `"Tarot Card"`, `"Numerology"`.
20. **`test_r4_t1_05_transparency_frontend_payload_contract`**:
    - *Description*: Verify `number_origins` format allows frontend to display provenance tags alongside recommended numbers.
    - *Input*: `/api/divine` payload.
    - *Assertions*: `number_origins` keys match string representation of lucky numbers exactly.

---

### 4.3 Detailed Tier 2 (Boundary & Corner Cases) Test Case Specifications (20 Test Cases)

#### Feature R1 Boundaries
1. **`test_r1_t2_01_boundary_055959_vs_060000`**:
   - *Description*: Test exact 1-second cutoff boundary: "05:59:59" vs "06:00:00".
   - *Input*: `birth_time="05:59:59"` vs `birth_time="06:00:00"`.
   - *Assertions*: "05:59:59" returns `cutoff_applied: true` (previous day), "06:00:00" returns `cutoff_applied: false` (current day).
2. **`test_r1_t2_02_boundary_midnight_000000`**:
   - *Description*: Test "00:00:00" birth time.
   - *Input*: `birth_date="1995-08-15"`, `birth_time="00:00:00"`.
   - *Assertions*: Returns `cutoff_applied: true` and shifts day of week to Wednesday without date arithmetic crash.
3. **`test_r1_t2_03_boundary_late_night_235959`**:
   - *Description*: Test "23:59:59" birth time.
   - *Input*: `birth_date="1995-08-15"`, `birth_time="23:59:59"`.
   - *Assertions*: Returns `cutoff_applied: false` and maintains Thursday day of week.
4. **`test_r1_t2_04_leap_year_feb29`**:
   - *Description*: Test February 29 leap year birth date with early birth time "04:30".
   - *Input*: `birth_date="2024-02-29"`, `birth_time="04:30"`.
   - *Assertions*: Shifts day of week to previous day (Feb 28) safely without throwing invalid date errors.
5. **`test_r1_t2_05_missing_or_empty_birth_time_fallback`**:
   - *Description*: Test missing or empty `birth_time` string.
   - *Input*: Payload omitting `birth_time` or passing `""`.
   - *Assertions*: Defaults safely to "12:00" (`cutoff_applied: false`) without throwing 500 error.

#### Feature R2 Boundaries
6. **`test_r2_t2_01_tarot_boundary_indices_0_and_77`**:
   - *Description*: Submit array containing boundary card indices 0 (The Fool) and 77 (King of Pentacles).
   - *Input*: `selected_tarot_cards=[0, 77, 1, 2, 3, 4, 5, 6, 7, 8]`.
   - *Assertions*: HTTP 200 OK, card 0 and card 77 present in spread.
7. **`test_r2_t2_02_tarot_too_few_cards_rejection`**:
   - *Description*: Submit array with <10 cards (e.g. 9 cards).
   - *Input*: `selected_tarot_cards=[0, 1, 2, 3, 4, 5, 6, 7, 8]`.
   - *Assertions*: Returns HTTP 400 or 422 validation error with message "Exactly 10 tarot cards must be selected".
8. **`test_r2_t2_03_tarot_too_many_cards_rejection`**:
   - *Description*: Submit array with >10 cards (e.g. 11 cards).
   - *Input*: `selected_tarot_cards=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`.
   - *Assertions*: Returns HTTP 400 or 422 validation error.
9. **`test_r2_t2_04_tarot_out_of_range_index_rejection`**:
   - *Description*: Submit array containing index <0 (-1) or >77 (78).
   - *Input*: `selected_tarot_cards=[-1, 1, 2, 3, 4, 5, 6, 7, 8, 78]`.
   - *Assertions*: Returns HTTP 400 or 422 validation error with message "Card index out of bounds [0..77]".
10. **`test_r2_t2_05_tarot_duplicate_indices_rejection`**:
    - *Description*: Submit array containing duplicate card indices.
    - *Input*: `selected_tarot_cards=[0, 0, 1, 2, 3, 4, 5, 6, 7, 8]`.
    - *Assertions*: Returns HTTP 400 or 422 validation error with message "Duplicate card selection not allowed".

#### Feature R3 Boundaries
11. **`test_r3_t2_01_boundary_0_wins_cold`**:
    - *Description*: Explicit test for number with 0 historical wins in GLO dataset.
    - *Input*: Number with 0 matches in 24 historical draws.
    - *Assertions*: `win_count == 0` and `level == "COLD"`.
12. **`test_r3_t2_02_boundary_1_win_warm`**:
    - *Description*: Explicit boundary test for number with exactly 1 historical win.
    - *Input*: Number with 1 match in 24 historical draws.
    - *Assertions*: `win_count == 1` and `level == "WARM"`.
13. **`test_r3_t2_03_boundary_2_wins_warm`**:
    - *Description*: Explicit boundary test for number with exactly 2 historical wins.
    - *Input*: Number with 2 matches in 24 historical draws.
    - *Assertions*: `win_count == 2` and `level == "WARM"`.
14. **`test_r3_t2_04_boundary_3_wins_hot`**:
    - *Description*: Explicit boundary test for number with exactly 3 historical wins.
    - *Input*: Number with 3 matches in 24 historical draws.
    - *Assertions*: `win_count == 3` and `level == "HOT"`.
15. **`test_r3_t2_05_heat_index_empty_data_fallback`**:
    - *Description*: If historical lottery data file is missing/empty, win counts default to 0 and level to "COLD" without server error.
    - *Input*: Engine initialized with empty or missing data path.
    - *Assertions*: `/api/divine` returns HTTP 200 OK with `win_count: 0` and `level: "COLD"`.

#### Feature R4 Boundaries
16. **`test_r4_t2_01_origin_fallback_for_synthetic_digits`**:
    - *Description*: Recommended number synthesized from multiple engines lists all contributing sources clearly.
    - *Input*: Combined 6-digit recommendation.
    - *Assertions*: `number_origins` list contains multiple engine descriptions.
17. **`test_r4_t2_02_origin_single_engine_source`**:
    - *Description*: Number originating from a single engine (e.g. Tarot card only) lists single origin string cleanly.
    - *Input*: Number derived purely from Tarot card index.
    - *Assertions*: `number_origins[num]` list has length 1 describing Tarot source.
18. **`test_r4_t2_03_origin_all_4_engines_combined`**:
    - *Description*: 6-digit number combining outputs from all 4 engines formats provenance list cleanly.
    - *Input*: Full divination synthesis request.
    - *Assertions*: `number_origins` contains comprehensive provenance description.
19. **`test_r4_t2_04_origin_unicode_thai_characters`**:
    - *Description*: Origin strings handle Thai Unicode text and symbols without encoding errors.
    - *Input*: Provenance strings with Thai characters (e.g. "📍 ที่มา: ฐาน 4 มหาภูติ + ไพ่ทาโรต์ใบที่ 3").
    - *Assertions*: JSON response serializes correctly with UTF-8 encoding.
20. **`test_r4_t2_05_origin_empty_engine_output_safety`**:
    - *Description*: Engine exceptions or partial data outputs do not cause KeyError when building `number_origins`.
    - *Input*: Partial engine failure simulation.
    - *Assertions*: `number_origins` provides fallback explanation string without raising KeyError.

---

## 5. Verification Method

To verify these specifications and the E2E test architecture:

1. **File Inspection**:
   - Inspect `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_e2e_1\handoff.md` to confirm all 5 components are present.
   - Inspect `TEST_INFRA.md` after implementation at `e:\เว็บดูดวงเพื่อซื้อหวยไทย\TEST_INFRA.md`.
2. **Command Verification**:
   - Run test suite once implementation is in place:
     ```bash
     python -m pytest omni_oracle_app/e2e_tests/test_tier1_feature_coverage.py -v
     python -m pytest omni_oracle_app/e2e_tests/test_tier2_boundary_safety.py -v
     ```
3. **Invalidation Conditions**:
   - Any test case failing due to schema mismatch or unhandled exception in `/api/divine`.
   - Missing origin mapping in `number_origins` for any recommended lucky number.
   - Failure of 6:00 AM cutoff logic for birth times before 06:00 AM.
