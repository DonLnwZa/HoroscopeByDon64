# Handoff Report: E2E Test Harness, Test Environment & Verification Strategy

**Author**: Explorer 3 (Frontend & End-to-End Test Harness & Verification Strategy)  
**Date**: 2026-08-12  
**Working Directory**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_e2e_3`  
**Target Project**: Omni-Oracle (`e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`)  

---

## 1. Observation

### 1.1 Project Structure & Tech Stack
- **Backend**: Flask application at `omni_oracle_app/backend/app.py`.
  - Dependencies (`omni_oracle_app/backend/requirements.txt`): `flask`, `flask-cors`, `pytest`, `pydantic`.
  - Serving static frontend assets directly from `omni_oracle_app/frontend/` at route `/`.
  - Core routes: `GET /`, `GET /api/health`, `GET /api/lottery/stats`, `POST /api/divine`.
- **Frontend**: Single Page Application at `omni_oracle_app/frontend/index.html` + `app.jsx` + `styles.css`.
  - Uses React 18 + Babel Standalone + Framer Motion (loaded via CDN).
  - Communicates via JSON POST request to `/api/divine`.
- **Existing E2E Files**: `omni_oracle_app/e2e_tests/test_e2e_full_stack.py`.
  - Currently contains legacy mock/fastapi path references (`/api/v1/predict`) which will be refactored into the modular Tier 1-4 structure.

### 1.2 Target API & Payload Contract (`PROJECT.md` & `ORIGINAL_REQUEST.md`)
- **`POST /api/divine` Request JSON**:
  ```json
  {
    "full_name": "Somchai Jaidee",
    "birth_date": "1992-05-15",
    "birth_time": "05:30",
    "birth_province": "Bangkok",
    "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
  }
  ```
- **`POST /api/divine` Response JSON**:
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
    "tarot_reading": { ... },
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
    "synthesis": "...",
    "disclaimer": "..."
  }
  ```

---

## 2. Logic Chain

1. **Test Environment Strategy**:
   - Since the Flask app is self-contained in `omni_oracle_app/backend/app.py`, Flask's `test_client()` provides a fast, deterministic, in-process HTTP client.
   - Tests execute against the exact app instance without needing external HTTP servers or browser setup, preventing port collision or environment state pollution.

2. **Directory Layout Design for `omni_oracle_app/e2e_tests/`**:
   To satisfy `SCOPE.md` requirements (Tiers 1-4) and cleanly separate test concerns:
   - `omni_oracle_app/e2e_tests/conftest.py`: Shared pytest fixtures (`client`, sample valid payload, edge-case payloads, mock lottery draw data).
   - `omni_oracle_app/e2e_tests/test_tier1_feature_coverage.py`: Tier 1 Feature Coverage (>=5 tests per feature across R1, R2, R3, R4).
   - `omni_oracle_app/e2e_tests/test_tier2_boundary_cases.py`: Tier 2 Boundary & Corner Cases (>=5 tests per feature across birth time cutoff 05:59:59 vs 06:00:00, Tarot selection <10/>10/duplicates/out of bounds, Heat Index 0/1-2/>=3 win thresholds, missing origin fields).
   - `omni_oracle_app/e2e_tests/test_tier3_cross_feature.py`: Tier 3 Cross-Feature Pairwise Integration (full R1+R2+R3+R4 schema verification and cross-engine consistency).
   - `omni_oracle_app/e2e_tests/test_tier4_real_world.py`: Tier 4 Real-World Application Scenarios (end-to-end user divination sessions, repeated queries, real birth dates).
   - `omni_oracle_app/e2e_tests/run_e2e_tests.py`: Python CLI test runner script that executes pytest across all 4 tier files, aggregates counts, prints formatted summary tables, and enforces 100% pass rate.

3. **Test Tier Categorization & Detailed Test Plans**:

   - **Tier 1: Feature Coverage**
     - R1: Test `birth_time` input accepted and `lunar_calendar` computed in response.
     - R1: Test 6:00 AM cutoff flag in response (`cutoff_applied: true` before 06:00, `false` after).
     - R2: Test array of 10 Tarot indices accepted and mapped to 10-card reading.
     - R3: Test `heat_index` structure returned with `win_count` and `level` (HOT/WARM/COLD) for all recommended numbers.
     - R4: Test `number_origins` returned with non-empty origin explanations for all recommended numbers.

   - **Tier 2: Boundary & Corner Cases**
     - R1 Boundary: `05:59:59` vs `06:00:00` cutoff transition; `00:00:00` midnight; `23:59:59` late night.
     - R2 Boundary: Rejecting array length < 10 (returns HTTP 400/422); array length > 10; invalid card indices (e.g. -1, 78, 100); duplicate card indices (e.g. [0, 0, ...]).
     - R3 Boundary: Heat Index for numbers with 0 wins (level COLD), 1-2 wins (level WARM), >=3 wins (level HOT).
     - R4 Boundary: Handling missing or empty string fields gracefully without server 500 errors.

   - **Tier 3: Cross-Feature Pairwise Integration**
     - Combined R1+R2+R3+R4 full payload validation.
     - Ensuring `lucky_numbers`, `heat_index`, and `number_origins` contain matching keys for two_digit, three_digit, and six_digit recommendations.

   - **Tier 4: Real-World Scenarios**
     - User full session journey simulation (Health check -> Lottery stats -> Divination prediction request -> Retrying with different Tarot selection).
     - Robust performance/latency checks across sequential user requests.

---

## 3. Caveats

1. **Pre-Implementation State**:
   - The current repository code in `omni_oracle_app/backend/app.py` is pre-M1 and does not yet handle `birth_time`, `selected_tarot_cards`, `heat_index`, or `number_origins`.
   - The E2E test suite in `omni_oracle_app/e2e_tests/` will pass 100% once M1 (Backend) and M2 (Frontend) are implemented.

2. **No External Browser Dependency Needed**:
   - The E2E strategy leverages Flask `test_client()` for opaque-box contract verification. This avoids Selenium/Playwright installation overhead and ensures zero flakiness across environments.

---

## 4. Conclusion

- **Test Execution Environment**: Python `pytest` using Flask `app.test_client()`.
- **E2E Test Directory Structure**:
  ```
  omni_oracle_app/e2e_tests/
  ├── conftest.py
  ├── test_tier1_feature_coverage.py
  ├── test_tier2_boundary_cases.py
  ├── test_tier3_cross_feature.py
  ├── test_tier4_real_world.py
  └── run_e2e_tests.py
  ```
- **Verification Commands**:
  - Full suite runner: `python omni_oracle_app/e2e_tests/run_e2e_tests.py`
  - Pytest direct: `python -m pytest omni_oracle_app/e2e_tests/`

---

## 5. Verification Method

To verify the test suite once implemented:
1. Run pytest directly:
   `python -m pytest omni_oracle_app/e2e_tests/`
2. Run custom E2E test runner:
   `python omni_oracle_app/e2e_tests/run_e2e_tests.py`
3. Confirm all test cases pass with exit code `0`.
