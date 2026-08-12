# Investigation Report: Flask App `/api/divine` & Backend Test Suite (Milestone M1)

**Agent**: Explorer 3  
**Milestone**: M1 (Backend Engines & API Upgrade)  
**Target Path**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\`  
**Date**: 2026-08-12  

---

## 1. Executive Summary

This investigation analyzes the Flask application (`omni_oracle_app/backend/app.py`), backend engines (`omni_oracle_app/backend/app/engines/*.py`), and the existing unit/integration test suite (`omni_oracle_app/backend/tests/`) to support the Milestone M1 upgrade.

### Key Discoveries:
1. **API Endpoint Gap**: The current `/api/divine` route in `app.py` reads legacy inputs (`birth_day_of_week`, `birth_month_lunar`, `birth_year_animal`) and does not accept `birth_time` or `selected_tarot_cards`. It returns an un-structured response lacking `status`, `chart.lunar_calendar`, `heat_index`, and `number_origins`.
2. **Engine Support Status**:
   - `mahabote.py` and `thai_astrology.py` already support `birth_time` parameter internally.
   - `tarot.py` needs signature update in `draw_celtic_cross(selected_cards=None)` to map candidate card indices `[0..77]` to positions 1..10.
   - `lottery_stats.py` contains basic frequency calculation (`get_digit_frequencies`, `get_hot_cold_numbers`) but needs `calculate_heat_index(recommended_numbers)` to evaluate win counts across 24 historical draw records in `lottery_results_past_1_year.json`.
   - `number_recommender.py` needs provenance tracking to generate `number_origins` mapping.
3. **Test Infrastructure**: Tests run via `pytest` (`python -m pytest omni_oracle_app/backend/tests/`). 12 test files currently exist covering individual engines and test tiers 1-4.

---

## 2. Flask API Schema & Route Diff Analysis

### 2.1 Current vs Target Endpoint Comparison (`POST /api/divine`)

| Aspect | Current Implementation (`app.py`) | Target Contract (`PROJECT.md`) | Gap / Action Required |
|---|---|---|---|
| **Input Fields** | `birth_date`, `birth_day_of_week`, `birth_month_lunar`, `birth_year_animal` | `birth_date` (YYYY-MM-DD), `birth_time` (HH:MM), `selected_tarot_cards` (`[int]*10`), `birth_province`, `full_name` | Remove manual lunar dropdown fields; add validation for `birth_time` and `selected_tarot_cards`. |
| **Lunar Calculation** | Manual inputs expected in request body | Auto-calculated from `birth_date` + `birth_time` with Bangkok 06:00 AM cutoff rule | Calculate lunar day, month (1-12), zodiac year (1-12), and `cutoff_applied` boolean in backend. |
| **Tarot Drawing** | Random secret selection in backend (`draw_celtic_cross()`) | Interactive selection (`selected_tarot_cards` array of 10 integers 0..77) | Pass `selected_tarot_cards` to `tarot_engine.draw_celtic_cross(selected_cards)`. |
| **Response Fields** | `numerology`, `mahabote`, `astrology`, `tarot`, `lucky_numbers`, `synthesis`, `disclaimer` | `status`, `chart`, `tarot_reading`, `lucky_numbers`, `heat_index`, `number_origins`, `synthesis`, `disclaimer` (+ legacy keys for backward compat) | Wrap response into specified JSON contract schema; include `heat_index` and `number_origins`. |

---

## 3. Validation Rules & Request Payload Specification

### 3.1 Request Payload Contract

```json
{
  "full_name": "Somchai Jaidee",
  "birth_date": "1992-05-15",
  "birth_time": "05:30",
  "birth_province": "Bangkok",
  "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
}
```

### 3.2 Field Validation Rules

1. **`birth_date`**:
   - Required string in `YYYY-MM-DD` ISO format.
   - Validation: Must parse successfully via `datetime.strptime(birth_date, "%Y-%m-%d")`.
   - Error on failure: HTTP 400 Bad Request `{"status": "error", "message": "Invalid birth_date format. Expected YYYY-MM-DD."}`.

2. **`birth_time`**:
   - String in `HH:MM` or `HH:MM:SS` format (e.g. `"05:30"`, `"14:15"`).
   - Validation: Regex `^([01]\d|2[0-3]):[0-5]\d$` or `datetime.strptime`.
   - Default: If omitted or empty, default to `"12:00"` for backwards compatibility.
   - Error on invalid format: HTTP 400 Bad Request `{"status": "error", "message": "Invalid birth_time format. Expected HH:MM."}`.

3. **`selected_tarot_cards`**:
   - Array of exactly 10 integers, each between `0` and `77` inclusive.
   - Validation:
     - Must be a Python `list`.
     - `len(selected_tarot_cards) == 10`.
     - `all(isinstance(x, int) and 0 <= x <= 77 for x in selected_tarot_cards)`.
     - All 10 indices should be unique (`len(set(selected_tarot_cards)) == 10`).
   - Default: If omitted in legacy calls, gracefully fallback to random draw of 10 unique cards.
   - Error on invalid payload: HTTP 400 Bad Request `{"status": "error", "message": "selected_tarot_cards must be an array of 10 unique integers between 0 and 77."}`.

4. **`birth_province` & `full_name`**:
   - Optional strings. Default `birth_province` to `"Bangkok"` or `"กรุงเทพมหานคร"`.

---

## 4. Target Response JSON Structure Specification

```json
{
  "status": "success",
  "chart": {
    "birth_date": "1992-05-15",
    "birth_time": "05:30",
    "lunar_calendar": {
      "day_of_week": "Thursday",
      "lunar_month": 6,
      "zodiac_year": "Monkey",
      "cutoff_applied": true
    }
  },
  "tarot_reading": {
    "spread": [
      {
        "position_index": 1,
        "position_name": "สถานการณ์ปัจจุบัน",
        "card_id": "major_0",
        "card_name": "The Fool",
        "type": "Major Arcana",
        "is_reversed": false,
        "meaning": "ความหมายเชิงบวกของ The Fool"
      }
    ],
    "interpretation": "การอ่านไพ่ 10 ใบ"
  },
  "lucky_numbers": {
    "two_digit": ["15", "84"],
    "three_digit": ["485", "792"],
    "six_digit": ["485792"]
  },
  "heat_index": {
    "two_digit": [
      {"number": "15", "win_count": 3, "level": "HOT"},
      {"number": "84", "win_count": 1, "level": "WARM"}
    ],
    "three_digit": [
      {"number": "485", "win_count": 0, "level": "COLD"},
      {"number": "792", "win_count": 2, "level": "HOT"}
    ],
    "six_digit": [
      {"number": "485792", "win_count": 0, "level": "COLD"}
    ]
  },
  "number_origins": {
    "15": ["Mahabote: Thanang + Phoka", "Thai Astrology: Lagna Lord 1"],
    "84": ["Tarot Card #3: The Empress", "Numerology 7x9: Base 4"],
    "485": ["Combined: Lagna 4 + Mahabote 85"],
    "792": ["Tarot Card #1: The Magician + Numerology 792"],
    "485792": ["Synthesis of Top Engine Predictions"]
  },
  "synthesis": "Omni-Oracle วิเคราะห์ดวงชะตาของคุณ...",
  "disclaimer": "คำทำนายและตัวเลขแนะนำเป็นเพียงสถิติ...",
  "numerology": { "...": "legacy field for backward compatibility" },
  "mahabote": { "...": "legacy field for backward compatibility" },
  "astrology": { "...": "legacy field for backward compatibility" },
  "tarot": { "...": "legacy field for backward compatibility" }
}
```

### Heat Index Classification Rules:
- `win_count >= 2`: Level `"HOT"`
- `win_count == 1`: Level `"WARM"`
- `win_count == 0`: Level `"COLD"`

---

## 5. Existing Test Suite Analysis & Test Commands

### 5.1 Test Inventory

The backend test directory `omni_oracle_app/backend/tests/` contains 12 python test modules:

1. `conftest.py`: Test configuration & `sys.path` setup.
2. `test_tarot.py`: Unit tests for `TarotEngine`.
3. `test_lottery_stats.py`: Unit tests for `LotteryStatsEngine`.
4. `test_mahabote.py`: Unit tests for Mahabote engine calculations.
5. `test_numerology_7x9.py`: Unit tests for 7x9 numerology matrix.
6. `test_numerology_7x9_stress.py`: Stress testing for numerology grid.
7. `test_thai_astrology.py`: Unit tests for natal chart calculations.
8. `test_tier1_feature_coverage.py`: 55 opaque-box feature coverage test cases across 11 system features.
9. `test_tier2_boundary_safety.py`: 55 boundary & safety test cases.
10. `test_tier3_pairwise_integration.py`: 11 pairwise component integration test cases.
11. `test_tier4_realworld_scenarios.py`: 6 real-world E2E journey test scenarios.

### 5.2 Exact Test Execution Commands

- **Run all backend tests with Pytest**:
  ```bash
  cd e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend
  python -m pytest tests/ -v
  ```
- **Run specific test file**:
  ```bash
  python -m pytest tests/test_tier1_feature_coverage.py -v
  ```
- **Run API integration tests only**:
  ```bash
  python -m pytest tests/test_api_divine.py -v
  ```
- **Run with Python Unittest (Fallback)**:
  ```bash
  python -m unittest discover -s tests -p "test_*.py"
  ```

---

## 6. Milestone M1 Comprehensive Test Plan

To verify all M1 requirements (R1, R2, R3, R4, `/api/divine`), the following test cases must be implemented in `tests/test_api_divine.py` and updated engine test files:

### 6.1 Requirement R1: Thai Lunar Calendar Auto-Calculation Tests
- `test_r1_lunar_calc_before_6am_cutoff`:
  - Input: `birth_date = "1992-05-15"`, `birth_time = "05:30"`.
  - Assert: `cutoff_applied == True`, day of week calculated using Thursday (rolled back from Friday 6am cutoff).
- `test_r1_lunar_calc_after_6am_no_cutoff`:
  - Input: `birth_date = "1992-05-15"`, `birth_time = "08:30"`.
  - Assert: `cutoff_applied == False`, day of week is Friday.
- `test_r1_lunar_calc_exact_6am_boundary`:
  - Input: `birth_time = "06:00"`.
  - Assert: Boundary condition handled cleanly (`cutoff_applied == False`).
- `test_r1_lunar_month_and_zodiac_year`:
  - Assert: `lunar_month` is integer 1..12 and `zodiac_year` is valid string (e.g. `"Monkey"`).

### 6.2 Requirement R2: Interactive Tarot Selection Tests
- `test_r2_tarot_accepts_10_selected_cards`:
  - Input: `selected_tarot_cards = [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]`.
  - Assert: Response contains 10 cards corresponding to indices `[0, 12, 25, 31, 44, 50, 61, 72, 5, 18]` mapped to Celtic Cross positions 1..10.
- `test_r2_tarot_rejects_invalid_array_length`:
  - Input: `selected_tarot_cards = [0, 1, 2]`.
  - Assert: HTTP 400 Bad Request returned with descriptive error.
- `test_r2_tarot_rejects_out_of_range_indices`:
  - Input: `selected_tarot_cards = [0, 1, 2, 3, 4, 5, 6, 7, 8, 99]`.
  - Assert: HTTP 400 Bad Request returned.
- `test_r2_tarot_rejects_duplicate_cards`:
  - Input: `selected_tarot_cards = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8]`.
  - Assert: HTTP 400 Bad Request returned.

### 6.3 Requirement R3: Heat Index Backtesting Tests
- `test_r3_heat_index_structure_and_levels`:
  - Input: Recommended numbers `{"two_digit": ["15", "84"], "three_digit": ["485", "792"], "six_digit": ["485792"]}`.
  - Assert: `heat_index` contains `two_digit`, `three_digit`, `six_digit` lists with fields `number`, `win_count`, `level`.
  - Assert: `level` is `"HOT"` if `win_count >= 2`, `"WARM"` if `win_count == 1`, `"COLD"` if `win_count == 0`.
- `test_r3_heat_index_historical_accuracy`:
  - Verify win counts against 24 historical draw records in `lottery_results_past_1_year.json`.

### 6.4 Requirement R4: Divination Transparency Origin Tracking Tests
- `test_r4_number_origins_mapping_completeness`:
  - Assert: Every number in `lucky_numbers.two_digit`, `three_digit`, `six_digit` has a non-empty list of origins in `number_origins`.
- `test_r4_number_origins_engine_provenance`:
  - Assert: Provenance strings reference specific source engines (e.g., `"Mahabote: Thanang + Phoka"`, `"Tarot Card #3: The Empress"`, `"Thai Astrology: Lagna Lord"`).

### 6.5 `/api/divine` Full Integration Tests
- `test_api_divine_full_contract_success`:
  - POST payload matching `PROJECT.md § Interface Contracts`.
  - Assert: HTTP 200 OK, JSON schema matching contract with all required sections.
- `test_api_divine_backward_compatibility`:
  - POST payload missing `birth_time` or `selected_tarot_cards`.
  - Assert: Returns HTTP 200 OK using default values (`birth_time="12:00"`, random tarot selection).
- `test_api_divine_invalid_json_body`:
  - POST malformed JSON or empty body.
  - Assert: HTTP 400 Bad Request.

---

## 7. Conclusion & Next Steps

1. `app.py` and `app/engines/` require specific implementation updates to fulfill M1 requirements without breaking existing engine logic.
2. Legacy field keys should be maintained alongside the new contract fields to ensure backward compatibility.
3. Test suite in `omni_oracle_app/backend/tests/` should be expanded with `test_api_divine.py` covering all R1-R4 test cases.
