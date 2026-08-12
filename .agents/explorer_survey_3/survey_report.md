# Detailed Survey Report: Testing & Build Survey for Omni-Oracle Lottery Divination Web Application

**Location**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_survey_3\survey_report.md`  
**Date**: 2026-08-12  
**Assigned Agent**: `teamwork_preview_explorer` (Testing & Build Survey)

---

## 1. Executive Summary & Problem Scope

The objective of this survey is to evaluate the existing codebase, project setup, test infrastructure, and data sources for the **Omni-Oracle Thai Lottery Divination Web Application** located at `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`, and to assess the requirements specified in `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md`.

The system requires four major upgrades:
1. **R1. Auto-Approximate Thai Lunar Calendar**: Remove manual dropdowns for Day of Week, Lunar Month, and Zodiac Year. Accept a `birth_time` string parameter alongside Gregorian `birth_date`. Automatically compute Thai day of week (applying the 06:00 AM day-shift cutoff rule), lunar month, and zodiac year.
2. **R2. Interactive Tarot Selection**: Replace backend random card drawing with a 78 face-down interactive card UI where users manually pick 10 cards. Pass an array of 10 card indices (`selected_tarot_cards`) to `/api/divine`.
3. **R3. Heat Index (Backtesting)**: Compare generated recommended lucky numbers against 1-year historical GLO draw results (`lottery_results_past_1_year.json`) to compute win frequencies ("Heat Index").
4. **R4. Divination Transparency**: Track and expose the mathematical/astrological origin of each recommended number (e.g., "Derived from Mahabote base 4 and Tarot card #3") and display it alongside the Heat Index in the frontend UI.

---

## 2. Project Setup & Architecture Analysis

### 2.1 Directory Structure
The target application is structured as a unified monorepo under `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`:

```
e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app/
├── backend/
│   ├── app.py                         # Main Flask application entry point
│   ├── requirements.txt               # Backend Python dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   └── engines/                   # Divination math & statistics calculation engines
│   │       ├── __init__.py
│   │       ├── thai_astrology.py      # Lahiri Ayanamsa natal chart engine (624 lines)
│   │       ├── numerology_7x9.py      # 7-digit 9-base matrix engine (437 lines)
│   │       ├── mahabote.py            # Burmese Mahabote calculation engine (485 lines)
│   │       ├── tarot.py               # 78 Tarot deck & spread generator (82 lines)
│   │       ├── lottery_stats.py       # Historical draw analyzer (57 lines)
│   │       ├── number_recommender.py  # Lucky number recommender (30 lines)
│   │       └── oracle_synthesis.py    # Omni-Oracle persona text synthesizer (18 lines)
│   ├── data/
│   │   └── lottery_results_past_1_year.json # Local GLO historical dataset (4,802 lines)
│   └── tests/                         # Pytest test suite (12 test modules)
├── frontend/
│   ├── index.html                     # HTML single-page wrapper (loads React, Babel, Framer Motion)
│   ├── app.jsx                        # React single-page frontend application (141 lines)
│   ├── styles.css                     # Glassmorphic mystic CSS styles (235 lines)
│   └── __tests__/                     # Vitest component test suites
└── e2e_tests/
    ├── test_e2e_full_stack.py         # Full stack API & contract integration test suite
    └── fixtures/
        └── mock_lottery_data.json     # Mock test dataset
```

### 2.2 Framework & Runtime Analysis
- **Backend Framework**: Python Flask web server (`backend/app.py`).
  - CORS enabled via `flask_cors`.
  - Static file server mapping `/` to `frontend/index.html` and serving frontend assets.
  - Endpoints currently exposed:
    - `GET /api/health` — returns `{"status": "ok"}`
    - `GET /api/lottery/stats` — returns hot/cold numbers and digit frequency table
    - `POST /api/divine` — accepts birth date & manual lunar dropdown parameters, returns JSON prediction response
- **Frontend Framework**: Browser-side React 18 single-page app (`frontend/app.jsx`).
  - Loaded via `@babel/standalone` CDN script in `index.html`.
  - Animations via `framer-motion` CDN.
  - Form state manages user inputs and submits to `http://localhost:5000/api/divine`.

---

## 3. Existing Code & Test Inventory

### 3.1 Dependencies (`backend/requirements.txt`)
- `flask`
- `flask-cors`
- `pytest`
- `pydantic`

### 3.2 Backend Engine Inventory
1. `thai_astrology.py` (22,175 bytes, 624 lines): Pure Python ephemeris math for Lahiri Ayanamsa, 10 planets, 12 houses, D9 Navamsa, D3 Drekkana.
2. `numerology_7x9.py` (16,175 bytes, 437 lines): 7x9 matrix computation (Base 1-3, Base 4 strength, house collisions).
3. `mahabote.py` (19,349 bytes, 485 lines): Chula Sakarat calculation, modulo 7, 7 body positions (Raja, Marana, etc.).
4. `tarot.py` (3,670 bytes, 82 lines): 78-card deck (22 Major Arcana, 56 Minor Arcana). Currently uses `secrets` for random backend draws.
5. `lottery_stats.py` (1,932 bytes, 57 lines): Reads `lottery_results_past_1_year.json`, counts 1st prize & last 2 digit frequencies.
6. `number_recommender.py` (1,160 bytes, 30 lines): Combines lucky pool with Mahabote base digits to generate 2-digit, 3-digit, 6-digit recommendations.
7. `oracle_synthesis.py` (1,534 bytes, 18 lines): Generates reading text and standard disclaimer.

### 3.3 Test Suite Inventory
- **Backend Pytest Suite (`backend/tests/`)**:
  - `conftest.py`: Adds backend directory to `sys.path`.
  - `test_thai_astrology.py`, `test_numerology_7x9.py`, `test_numerology_7x9_stress.py`, `test_mahabote.py`, `test_tarot.py`, `test_lottery_stats.py`: Module unit tests.
  - `test_tier1_feature_coverage.py`: 55 Tier 1 functional test cases.
  - `test_tier2_boundary_safety.py`: 55 Tier 2 boundary and safety test cases.
  - `test_tier3_pairwise_integration.py`: 11 Tier 3 pairwise integration tests.
  - `test_tier4_realworld_scenarios.py`: 6 Tier 4 user journey test scenarios.
- **Frontend Vitest Suite (`frontend/__tests__/`)**:
  - `IntakeForm.test.tsx`, `RecommendedNumbers.test.tsx`, `TarotSpread.test.tsx`.
- **E2E Integration Suite (`e2e_tests/`)**:
  - `test_e2e_full_stack.py`: Full stack opaque-box API tests.

---

## 4. Historical Lottery Data Source Accessibility

### 4.1 Data File Status
The GLO historical lottery draw dataset was checked at both specified locations:
1. **Primary path**: `e:\ข้อมูลผลหวยย้อนหลัง 1 ปี\fetch_lottery\lottery_results_past_1_year.json`
2. **Local backend copy**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\data\lottery_results_past_1_year.json`

### 4.2 File Verification Details
- **Accessibility**: File exists and is fully readable at both paths.
- **Size**: 83,878 bytes (4,802 lines of structured JSON).
- **Record Count**: 24 GLO draw results spanning from `2024-08-16` to `2025-08-01`.
- **JSON Schema Verification**:
  ```json
  [
    {
      "draw_date": "2025-08-01",
      "youtube_url": "https://www.youtube.com/watch?v=...",
      "pdf_url": "https://api.glo.or.th/...",
      "prize_1st": "811852",
      "prize_last2": "50",
      "prize_last3f": ["142", "525"],
      "prize_last3b": ["512", "891"],
      "prize_near1": ["811851", "811853"],
      "prize_2nd": ["329930", "519877", "588144", "809975", "810260"],
      "prize_3rd": [...10 entries...],
      "prize_4th": [...50 entries...],
      "prize_5th": [...100 entries...]
    }
  ]
  ```
- **Conclusion**: The data source is 100% accessible, valid, and rich enough to support complete Heat Index backtesting (R3).

---

## 5. Gap Analysis (Current Application vs. Requirements)

| Requirement | Current Codebase State | Target Required State | Gaps Identified |
|-------------|------------------------|-----------------------|-----------------|
| **R1. Auto Thai Lunar Calendar** | `app.py` expects `birth_day_of_week`, `birth_month_lunar`, `birth_year_animal` from frontend form dropdowns. | `POST /api/divine` accepts `birth_date` and `birth_time` (string). Backend calculates Thai day of week (6:00 AM cutoff rule), lunar month, zodiac year. Frontend removes dropdowns. | 1. Backend lacks birth time 6am cutoff logic.<br>2. Endpoint payload contract needs update.<br>3. Frontend `app.jsx` contains manual dropdowns. |
| **R2. Interactive Tarot Selection** | `tarot.py` generates 10 random cards in backend via `draw_celtic_cross()`. Frontend has no card selection UI. | Frontend renders 78 face-down cards; user selects 10. `selected_tarot_cards` (array of 10 integers `0..77`) sent to `/api/divine`. Backend maps indices to card objects. | 1. `tarot.py` needs `draw_by_indices(card_indices)`.<br>2. `/api/divine` payload needs `selected_tarot_cards` handling & length 10 validation.<br>3. Frontend `app.jsx` needs interactive grid component with card selection state. |
| **R3. Heat Index (Backtesting)** | `lottery_stats.py` counts digit frequencies, but `/api/divine` response does NOT return win counts for recommended numbers. | Backend checks recommended 2-digit, 3-digit, 6-digit numbers against all 24 draws in `lottery_results_past_1_year.json`. Response includes `heat_index` object. Frontend displays win counts. | 1. `lottery_stats.py` / `number_recommender.py` needs backtesting win counter.<br>2. `/api/divine` JSON response needs top-level `heat_index` field.<br>3. Frontend needs Heat Index UI card/badge display. |
| **R4. Divination Transparency** | Numbers are generated semi-randomly in `number_recommender.py` without tracking which engine produced which digit. | Each recommended number has an attached origin string (e.g. "Derived from Mahabote base 4 and Tarot card #3"). Response includes `number_origins` map. Frontend displays origins. | 1. `number_recommender.py` must record origin during number generation.<br>2. `/api/divine` JSON response needs `number_origins` field.<br>3. Frontend needs origin breakdown display. |

---

## 6. Required Test Infrastructure & Runner Specifications

To guarantee compliance with `ORIGINAL_REQUEST.md` and `TEST_INFRA.md`, the test runner and test suite infrastructure must cover:

### 6.1 Unit Test Specifications
1. **R1 Unit Tests**:
   - Test `birth_time` "05:30" (before 06:00 AM) shifts Thai day of week to previous calendar day.
   - Test `birth_time` "06:30" (after 06:00 AM) keeps standard Gregorian day of week.
   - Test valid approximation of Thai lunar month and zodiac year.
2. **R2 Unit Tests**:
   - Test `tarot_engine.draw_by_indices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])` maps to exact card objects.
   - Test duplicate card indices detection and invalid index boundary checks (<0 or >77).
3. **R3 Unit Tests**:
   - Test `lottery_stats.compute_heat_index(numbers)` against known GLO draw records (e.g. last 2 digits "50" matching 1st prize "811852" or prize_last2).
4. **R4 Unit Tests**:
   - Test origin generation produces non-empty, descriptive Thai origin explanations for 2-digit, 3-digit, and 6-digit numbers.

### 6.2 Integration Test Specifications
- Test Flask test client on `POST /api/divine`:
  - Request body:
    ```json
    {
      "birth_date": "1995-08-15",
      "birth_time": "14:30",
      "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    ```
  - Response contract validation:
    - Status code: `200 OK`
    - Contains `heat_index` key.
    - Contains `number_origins` key.
    - `tarot` object contains 10 items.
  - Validation error handling:
    - `selected_tarot_cards` with 9 or 11 items returns `400 Bad Request` or `422 Unprocessable Entity`.

### 6.3 E2E Opaque-Box Test Runner Specification
- Test command: `cd omni_oracle_app/backend && pytest tests/ -v`
- Execution harness uses `Flask.test_client()` or local server to perform full opaque-box contract tests.

---

## 7. Actionable Implementation Recommendations

1. **Backend Modifications (`app.py`, `tarot.py`, `lottery_stats.py`, `number_recommender.py`)**:
   - Extend `tarot.py` to support `draw_by_indices(card_indices: List[int])`.
   - Update `mahabote.py` / `thai_astrology.py` to accept `birth_time` and apply 6am cutoff rule.
   - Extend `lottery_stats.py` to calculate exact win count matches for 2-digit, 3-digit, 6-digit numbers against 24 historical draws.
   - Update `number_recommender.py` to tag every generated number with its engine origin.
   - Update `/api/divine` route in `app.py` to accept `birth_time` & `selected_tarot_cards`, validate inputs, and return `heat_index` & `number_origins`.
2. **Frontend Modifications (`frontend/app.jsx`)**:
   - Update form UI to replace dropdowns with `<input type="time" name="birth_time">`.
   - Add interactive 78-card face-down Tarot grid where user must select 10 cards before enabling submit button.
   - Render `heat_index` and `number_origins` in the results view.
3. **Test Suite Updates (`backend/tests/`, `e2e_tests/`)**:
   - Update existing test payloads to pass `birth_time` and `selected_tarot_cards`.
   - Add assertions for `heat_index` and `number_origins`.

---
*Report generated by `teamwork_preview_explorer` — e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_survey_3\survey_report.md*
