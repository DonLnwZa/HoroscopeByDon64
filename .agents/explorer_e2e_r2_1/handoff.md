# Explorer R2-1 Handoff Report: Integrity Violation Remediation & Defect Strategy

**Role**: Explorer R2-1 (Integrity Violation Remediation & Test Suite Alignment)  
**Working Directory**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_e2e_r2_1`  
**Parent Conversation ID**: `4546dcb1-3bf4-432f-ac29-2a6314dcdbd9`  
**Date**: 2026-08-12  
**Target Application**: Omni-Oracle Thai Lottery Prediction Web Application (`omni_oracle_app`)  

---

## 1. Observation

Direct empirical observations from source code static analysis and forensic audit review:

### Observation 1.1: Business Logic Defect in Heat Index Threshold (`lottery_stats.py`)
- **File**: `omni_oracle_app/backend/app/engines/lottery_stats.py` (Line 101)
- **Verbatim Code**:
  ```python
  level = "HOT" if win_count >= 2 else ("WARM" if win_count == 1 else "COLD")
  ```
- **Contract Specification**:
  - `SCOPE.md` (Line 15): "numbers with 0 wins (COLD), 1-2 wins (WARM), >=3 wins (HOT)."
  - `TEST_INFRA.md` (Lines 90–92 & 120–122): `win_count >= 3` -> `HOT`, `win_count` in `[1, 2]` -> `WARM`, `win_count == 0` -> `COLD`.
  - `TEST_READY.md` (Line 61): "Win frequency level classification (HOT for >=3 wins, WARM for 1-2 wins, COLD for 0 wins)."
  - `test_tier1_feature_coverage.py` (`test_r3_t1_04`) & `test_tier2_boundary_cases.py` (`test_r3_t2_03_boundary_2_wins_warm`):
    ```python
    two_win_items = [item for item in all_items if item["win_count"] == 2]
    for item in two_win_items:
        assert item["level"] == "WARM"
    ```
- **Impact**: `lottery_stats.py` sets `level = "HOT"` when `win_count == 2`. Any lucky number with 2 historical wins gets classified as `"HOT"` instead of `"WARM"`, causing `test_r3_t2_03_boundary_2_wins_warm` to fail with `AssertionError: 'HOT' == 'WARM'`.

### Observation 1.2: Hardcoded Mock Client / Integrity Violation #1 (`test_e2e_full_stack.py`)
- **File**: `omni_oracle_app/e2e_tests/test_e2e_full_stack.py` (Lines 19–59)
- **Verbatim Code**:
  ```python
  try:
      from fastapi.testclient import TestClient
      from app.main import app
      client = TestClient(app)
  except Exception:
      class MockResponse:
          def __init__(self, status_code=200, json_data=None):
              self.status_code = status_code
              self._json_data = json_data or {}
          def json(self):
              return self._json_data

      class MockClient:
          def post(self, url, json=None, **kwargs):
              if url == "/api/v1/predict":
                  ...
                  return MockResponse(200, {
                      "astrology": {"lagna": {"rasi_index": 4, "rasi_name": "สิงห์"}},
                      "numerology_7x9": {"matrix": [[1,2,3,4,5,6,7]], "base4_strength": "High"},
                      "mahabote": {"positions": {"raja": 5, "marana": 2}},
                      "tarot": {"spread": [{"card_id": i, "name": f"Card {i}", "is_reversed": False} for i in range(10)]},
                      "recommended_lottery_numbers": {
                          "two_digits": ["52", "85", "50"],
                          "three_digits": ["142", "525", "891"],
                          "six_digits": ["811852", "123456"],
                          "confidence_score": 0.88
                      },
                      "omni_oracle_reading": "ชะตาชีวิตของคุณอยู่ในเกณฑ์ดี มีดาวพฤหัสบดีส่งเสริม...",
                      "safety_metadata": {"passed": True, "flags_triggered": []}
                  })
              return MockResponse(404, {"detail": "Not Found"})

          def get(self, url, **kwargs):
              if url == "/api/v1/health":
                  return MockResponse(200, {"status": "UP", "version": "1.0.0"})
              elif url == "/api/v1/lottery/stats":
                  return MockResponse(200, {"total_draws": 24, "top_two_digits": ["50", "52", "85"]})
              return MockResponse(404, {"detail": "Not Found"})

      client = MockClient()
  ```
- **Impact**: `test_e2e_full_stack.py` attempts to import `fastapi` and non-existent `app.main`. The exception forces execution into `MockClient`, which returns static hardcoded JSON dicts for `/api/v1/predict`. Test cases in this file self-certify pass by asserting against `MockClient`'s hardcoded returns without ever reaching `omni_oracle_app/backend/app.py`.

### Observation 1.3: Fake Mock Seams in Backend Tests / Integrity Violation #2 (`backend/tests/`)
- **Files**: `omni_oracle_app/backend/tests/` (`test_tier1_feature_coverage.py` lines 14–141, `test_tier2_boundary_safety.py` lines 14–118, `test_tier3_pairwise_integration.py`, `test_tier4_realworld_scenarios.py`)
- **Verbatim Code**:
  ```python
  try:
      from app.services.lottery_processor import process_historical_lottery
  except ImportError:
      def process_historical_lottery(file_path: str):
          ... # Returns fake dictionary

  try:
      from app.services.lottery_recommender import recommend_lottery_numbers
  except ImportError:
      def recommend_lottery_numbers(divination_digits: List[int], lottery_stats: Dict[str, Any]):
          ... # Returns fake dictionary

  try:
      from app.core.safety_guardrails import validate_and_sanitize_reading
  except ImportError:
      def validate_and_sanitize_reading(text: str):
          ... # Returns fake dictionary
  ```
- **Impact**: Backend unit test files contain `except ImportError:` stubs targeting non-existent service/core modules. These stubs return fake dictionaries, causing tests to pass artificially on dummy data instead of invoking real backend engines (`app.engines.*`).

---

## 2. Logic Chain

1. **Defect Logic (`lottery_stats.py:101`)**:
   - The contract specified in `SCOPE.md`, `TEST_INFRA.md`, and `TEST_READY.md` dictates:
     - `win_count == 0` -> `"COLD"`
     - `win_count == 1` or `win_count == 2` -> `"WARM"`
     - `win_count >= 3` -> `"HOT"`
   - `lottery_stats.py:101` implements: `level = "HOT" if win_count >= 2 else ("WARM" if win_count == 1 else "COLD")`.
   - When a number has `win_count == 2`, `lottery_stats.py` returns `"HOT"`.
   - `test_r3_t2_03_boundary_2_wins_warm` asserts `item["level"] == "WARM"`.
   - Result: Assertion fails (`"HOT" == "WARM"`). Updating line 101 to `level = "HOT" if win_count >= 3 else ("WARM" if win_count >= 1 else "COLD")` resolves the defect.

2. **Integrity Violation #1 Logic (`test_e2e_full_stack.py`)**:
   - FastAPI is not used in this project; the real application is Flask (`omni_oracle_app/backend/app.py`).
   - `test_e2e_full_stack.py` catches `ImportError` on FastAPI and falls back to `MockClient`.
   - `MockClient` intercepts `/api/v1/predict` calls and returns hardcoded JSON data.
   - Assertions in `test_e2e_full_stack.py` pass against the mock client, never executing backend code.
   - Deleting `test_e2e_full_stack.py` or refactoring it to use Flask `app_client` targeting `/api/divine` eliminates this integrity violation.

3. **Integrity Violation #2 Logic (`backend/tests/`)**:
   - Backend tier files attempt to import non-existent modules (`app.services.*`, `app.core.*`).
   - The `except ImportError:` fallback defines stub functions that return synthetic responses.
   - Running backend tests executes stub functions rather than `app.engines.*`.
   - Refactoring `backend/tests/` to import real engine modules (`app.engines.thai_astrology`, `app.engines.numerology_7x9`, `app.engines.mahabote`, `app.engines.tarot`, `app.engines.lottery_stats`, `app.engines.number_recommender`, `app.engines.oracle_synthesis`) and removing `except ImportError:` mock stubs restores full test integrity.

---

## 3. Caveats

- **Terminal Command Execution**: `run_command` timed out on interactive terminal permission prompt during this turn; verification was conducted via static code inspection and empirical contract comparison.
- **E2E Suite Integrity**: The primary E2E test suite in `omni_oracle_app/e2e_tests/` (`test_tier1_feature_coverage.py`, `test_tier2_boundary_cases.py`, `test_tier3_cross_feature.py`, `test_tier4_real_world.py`) is genuine and properly uses Flask `app_client` against `/api/divine`. Only `test_e2e_full_stack.py` and `backend/tests/` require mock purge.

---

## 4. Conclusion & Actionable Remediation Plan

### Remediation Strategy for Worker Agent:

#### Step 1: Fix Business Logic Defect in `lottery_stats.py`
- **Target File**: `omni_oracle_app/backend/app/engines/lottery_stats.py`
- **Line**: 101
- **Change**:
  ```python
  # Old:
  level = "HOT" if win_count >= 2 else ("WARM" if win_count == 1 else "COLD")

  # New:
  level = "HOT" if win_count >= 3 else ("WARM" if win_count >= 1 else "COLD")
  ```

#### Step 2: Remove / Refactor `test_e2e_full_stack.py`
- **Target File**: `omni_oracle_app/e2e_tests/test_e2e_full_stack.py`
- **Action**: Either delete `test_e2e_full_stack.py` or refactor it into `test_e2e_flask_app.py` using Flask `app_client` from `conftest.py` targeting real endpoints (`/api/divine`, `/api/health`, `/api/lottery/stats`). Completely remove `MockClient`, `MockResponse`, and FastAPI imports.

#### Step 3: Purge Mock Fallback Stubs in `omni_oracle_app/backend/tests/`
- **Target Files**: `omni_oracle_app/backend/tests/test_tier1_feature_coverage.py`, `test_tier2_boundary_safety.py`, `test_tier3_pairwise_integration.py`, `test_tier4_realworld_scenarios.py`
- **Action**:
  1. Remove all `try...except ImportError:` fallback mock definitions returning fixed dictionaries.
  2. Directly import real engine modules:
     - `from app.engines.thai_astrology import calculate_thai_astrology, calculate_thai_lunar_calendar`
     - `from app.engines.numerology_7x9 import calculate_numerology_7x9`
     - `from app.engines.mahabote import calculate_mahabote`
     - `from app.engines.tarot import TarotEngine`
     - `from app.engines.lottery_stats import LotteryStatsEngine`
     - `from app.engines.number_recommender import NumberRecommender`
     - `from app.engines.oracle_synthesis import OracleSynthesis`
  3. Ensure all tests call real backend engines and assert against real calculation outputs.

#### Step 4: Verify Master E2E Runner Execution
- Execute `python omni_oracle_app/e2e_tests/run_e2e_tests.py` to confirm all 57 E2E tests pass 100%.

---

## 5. Verification Method

To independently verify remediation completion:

1. **Inspect Code**:
   - `omni_oracle_app/backend/app/engines/lottery_stats.py`: line 101 reads `win_count >= 3` for `"HOT"` and `win_count >= 1` for `"WARM"`.
   - `omni_oracle_app/e2e_tests/test_e2e_full_stack.py`: `MockClient` is removed.
   - `omni_oracle_app/backend/tests/`: 0 `except ImportError:` mock stubs remaining.

2. **Execute Commands**:
   ```bash
   # Run master E2E test runner
   python omni_oracle_app/e2e_tests/run_e2e_tests.py

   # Run boundary case tests directly
   pytest omni_oracle_app/e2e_tests/test_tier2_boundary_cases.py -k test_r3_t2_03_boundary_2_wins_warm -v
   ```

3. **Invalidation Conditions**:
   - `test_r3_t2_03_boundary_2_wins_warm` fails with `AssertionError: 'HOT' == 'WARM'`.
   - Presence of any `MockClient` or fake service import stubs in test suites.
