# Omni-Oracle Thai Lottery Web Application — E2E Test Infrastructure Specification (`TEST_INFRA.md`)

## 1. Overview & Test Architecture

This document defines the End-to-End (E2E) opaque-box test infrastructure and specification for the upgraded **Omni-Oracle Thai Lottery Prediction Web Application** (`omni_oracle_app`).

### Test Philosophy
- **Opaque-box API Testing**: Testing is conducted against the HTTP endpoint interface (`POST /api/divine`, `GET /api/health`, `GET /api/lottery/stats`) of the Flask application without mutating or relying on internal implementation details.
- **Deterministic & In-Process**: Harness uses pytest with Flask's native `test_client()` in `omni_oracle_app/backend/app.py` for rapid, repeatable, and isolated test execution.
- **Contract Enforcement**: Strictly verifies request/response schemas specified in `PROJECT.md` and `ORIGINAL_REQUEST.md` for features R1, R2, R3, and R4.

---

## 2. Directory Layout & Module Structure

All E2E test files are co-located under `omni_oracle_app/e2e_tests/`:

```
omni_oracle_app/e2e_tests/
├── conftest.py                       # Shared Pytest fixtures & environment setup
├── test_tier1_feature_coverage.py    # Tier 1: 20 Feature Coverage tests (5 per R1-R4)
├── test_tier2_boundary_cases.py      # Tier 2: 20 Boundary & Corner Case tests (5 per R1-R4)
├── test_tier3_cross_feature.py       # Tier 3: 11 Cross-Feature Pairwise Integration tests
├── test_tier4_real_world.py          # Tier 4: 6 Real-World User Journey tests
└── run_e2e_tests.py                  # Master test runner & summary aggregator
```

---

## 3. Shared Fixtures & Test Data (`conftest.py`)

The test suite relies on standard pytest fixtures defined in `conftest.py`:

- **`app_client`**: Instantiates Flask test client from `omni_oracle_app/backend/app.py`.
- **`valid_divine_payload`**: Standard valid request payload:
  ```json
  {
    "full_name": "Somchai Jaidee",
    "birth_date": "1992-05-15",
    "birth_time": "05:30",
    "birth_province": "Bangkok",
    "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
  }
  ```
- **`mock_lottery_data_path`**: Absolute path to `omni_oracle_app/backend/data/lottery_results_past_1_year.json` containing 24 historical draw records.

---

## 4. Test Runner & Execution Commands

### Execution via Master Runner
```bash
python omni_oracle_app/e2e_tests/run_e2e_tests.py
```

### Execution via Pytest
```bash
# Run all E2E test modules
pytest omni_oracle_app/e2e_tests/ -v

# Run individual tiers
pytest omni_oracle_app/e2e_tests/test_tier1_feature_coverage.py -v
pytest omni_oracle_app/e2e_tests/test_tier2_boundary_cases.py -v
pytest omni_oracle_app/e2e_tests/test_tier3_cross_feature.py -v
pytest omni_oracle_app/e2e_tests/test_tier4_real_world.py -v
```

---

## 5. Comprehensive Test Breakdown (57 Test Cases)

### Tier 1: Feature Coverage (20 Test Cases)
- **R1: Thai Lunar Calendar Auto-Calculation & 6:00 AM Cutoff (5 tests)**
  - `test_r1_t1_01_lunar_calc_daytime`: Birth time >= 06:00 ("14:30") retains current solar day (`cutoff_applied: false`).
  - `test_r1_t1_02_lunar_calc_early_morning_cutoff`: Birth time < 06:00 ("05:30") shifts Thai day of week to previous solar day (`cutoff_applied: true`).
  - `test_r1_t1_03_lunar_month_range`: Verify `lunar_month` is an integer bounded in `[1..12]`.
  - `test_r1_t1_04_zodiac_year_mapping`: Verify `zodiac_year` returns valid Thai/English zodiac animal string.
  - `test_r1_t1_05_lunar_calendar_response_structure`: Verify `/api/divine` payload contains `chart.lunar_calendar` with all mandatory keys (`day_of_week`, `lunar_month`, `zodiac_year`, `cutoff_applied`).

- **R2: Interactive Tarot Card Selection (5 tests)**
  - `test_r2_t1_01_tarot_valid_10_cards`: Submit valid 10 card indices `[0, 12, 25, 31, 44, 50, 61, 72, 5, 18]` and verify HTTP 200.
  - `test_r2_t1_02_tarot_position_mapping`: Verify 10 cards map 1-to-1 to 10 Celtic Cross spread positions in exact order.
  - `test_r2_t1_03_tarot_major_minor_arcana_metadata`: Verify Major Arcana (indices 0..21) vs Minor Arcana (indices 22..77) classification.
  - `test_r2_t1_04_tarot_reversal_state_handling`: Verify each drawn card includes `is_reversed` boolean flag.
  - `test_r2_t1_05_tarot_divine_endpoint_integration`: Verify `/api/divine` passes `selected_tarot_cards` into Tarot Celtic Cross spread generator.

- **R3: Backtesting Heat Index (5 tests)**
  - `test_r3_t1_01_heat_index_response_structure`: Verify `/api/divine` JSON contains `heat_index` with `two_digit`, `three_digit`, `six_digit`.
  - `test_r3_t1_02_heat_index_win_count_calculation`: Verify `win_count` is calculated against 24 historical GLO draw records.
  - `test_r3_t1_03_heat_index_hot_classification`: Verify win_count >= 3 is classified as `HOT`.
  - `test_r3_t1_04_heat_index_warm_classification`: Verify win_count in [1, 2] is classified as `WARM`.
  - `test_r3_t1_05_heat_index_cold_classification`: Verify win_count == 0 is classified as `COLD`.

- **R4: Divination Transparency (Number Origins) (5 tests)**
  - `test_r4_t1_01_number_origins_presence`: Verify `/api/divine` response JSON contains `number_origins` dictionary.
  - `test_r4_t1_02_origins_mapped_for_all_recommended_numbers`: Verify every number in `lucky_numbers` has corresponding entry in `number_origins`.
  - `test_r4_t1_03_origin_explanation_format`: Verify `number_origins` values are non-empty lists of descriptive origin strings.
  - `test_r4_t1_04_origin_tracks_engine_sources`: Verify origin descriptions explicitly cite divination sources (Mahabote, Thai Astrology, Tarot Card #X, Numerology 7x9).
  - `test_r4_t1_05_transparency_frontend_payload_contract`: Verify origins key mapping matches lucky number strings exactly for UI rendering.

---

### Tier 2: Boundary & Corner Cases (20 Test Cases)
- **R1 Boundaries (5 tests)**
  - `test_r1_t2_01_boundary_055959_vs_060000`: Exact 1-second cutoff boundary test: "05:59:59" (`cutoff_applied: true`) vs "06:00:00" (`cutoff_applied: false`).
  - `test_r1_t2_02_boundary_midnight_000000`: Midnight birth time "00:00:00" handles date arithmetic safely.
  - `test_r1_t2_03_boundary_late_night_235959`: Late night birth time "23:59:59" retains current day without overflow.
  - `test_r1_t2_04_leap_year_feb29`: Leap year Feb 29 birth date with early birth time "04:30" shifts to Feb 28 safely.
  - `test_r1_t2_05_missing_or_empty_birth_time_fallback`: Omitted/empty `birth_time` defaults to "12:00" (`cutoff_applied: false`) safely.

- **R2 Boundaries (5 tests)**
  - `test_r2_t2_01_tarot_boundary_indices_0_and_77`: Boundary indices 0 (The Fool) and 77 (King of Pentacles) process successfully.
  - `test_r2_t2_02_tarot_too_few_cards_rejection`: Array with <10 cards (9 cards) returns HTTP 400/422 validation error.
  - `test_r2_t2_03_tarot_too_many_cards_rejection`: Array with >10 cards (11 cards) returns HTTP 400/422 validation error.
  - `test_r2_t2_04_tarot_out_of_range_index_rejection`: Array with indices <0 (-1) or >77 (78) returns HTTP 400/422 validation error.
  - `test_r2_t2_05_tarot_duplicate_indices_rejection`: Array with duplicate indices returns HTTP 400/422 validation error.

- **R3 Boundaries (5 tests)**
  - `test_r3_t2_01_boundary_0_wins_cold`: Number with 0 historical wins evaluates to `win_count: 0` and level `COLD`.
  - `test_r3_t2_02_boundary_1_win_warm`: Number with 1 historical win evaluates to `win_count: 1` and level `WARM`.
  - `test_r3_t2_03_boundary_2_wins_warm`: Number with 2 historical wins evaluates to `win_count: 2` and level `WARM`.
  - `test_r3_t2_04_boundary_3_wins_hot`: Number with 3 historical wins evaluates to `win_count: 3` and level `HOT`.
  - `test_r3_t2_05_heat_index_empty_data_fallback`: Missing/corrupt historical data defaults safely to `win_count: 0` and level `COLD` without 500 error.

- **R4 Boundaries (5 tests)**
  - `test_r4_t2_01_origin_fallback_for_synthetic_digits`: Synthesized multi-engine recommendations list all contributing sources cleanly.
  - `test_r4_t2_02_origin_single_engine_source`: Single-engine recommendations list single origin string clearly.
  - `test_r4_t2_03_origin_all_4_engines_combined`: Multi-engine recommendations combine provenance from all 4 systems cleanly.
  - `test_r4_t2_04_origin_unicode_thai_characters`: Provenance strings handle Thai Unicode text without encoding failures.
  - `test_r4_t2_05_origin_empty_engine_output_safety`: Engine exceptions fallback gracefully without raising KeyError in origin dictionary assembly.

---

### Tier 3: Cross-Feature Pairwise Integration (11 Test Cases)
- `test_t3_pairwise_01_r1_r2_lunar_cutoff_with_tarot_selection`: R1 ↔ R2 interaction: Lunar cutoff calculation preserves selected Tarot cards.
- `test_t3_pairwise_02_r1_r3_lunar_lucky_digits_to_heat_index`: R1 ↔ R3 interaction: Birth time calculation outputs flow to backtesting engine.
- `test_t3_pairwise_03_r1_r4_lunar_astrology_to_number_origins`: R1 ↔ R4 interaction: Astrology and lunar origins tracked in provenance tags.
- `test_t3_pairwise_04_r2_r3_tarot_cards_to_heat_index`: R2 ↔ R3 interaction: Tarot card selections flow into Heat Index evaluation.
- `test_t3_pairwise_05_r2_r4_tarot_cards_to_number_origins`: R2 ↔ R4 interaction: Tarot card indices reflected in `number_origins`.
- `test_t3_pairwise_06_r3_r4_heat_index_origins_structural_parity`: R3 ↔ R4 interaction: `heat_index` keys match `number_origins` keys 1-to-1.
- `test_t3_pairwise_07_full_single_request_integration`: Combined R1+R2+R3+R4 full payload schema validation.
- `test_t3_pairwise_08_multi_request_sequential_isolation`: Sequential client requests with different birth times maintain state isolation.
- `test_t3_pairwise_09_multi_request_tarot_variation`: Sequential client requests with varied Tarot selections keep chart constant.
- `test_t3_pairwise_10_error_boundary_invalid_r2_valid_r1`: Invalid R2 input fails fast before R1 processing.
- `test_t3_pairwise_11_error_boundary_invalid_r1_valid_r2`: Invalid R1 input fails fast before R2 processing.

---

### Tier 4: Real-World Application Scenarios (6 Test Cases)
- `test_t4_scenario_01_early_morning_birth_cutoff_journey`: Complete user session for pre-sunrise birth time (05:30 AM).
- `test_t4_scenario_02_post_cutoff_morning_birth_journey`: Complete user session for post-sunrise birth time (06:30 AM).
- `test_t4_scenario_03_songkran_new_year_boundary_journey`: Complete user session across Songkran traditional new year transition.
- `test_t4_scenario_04_midnight_birth_boundary_cards_journey`: Complete user session with midnight birth time and boundary Tarot cards (0 & 77).
- `test_t4_scenario_05_invalid_input_resilience_journey`: Recovery from user validation error to successful submission.
- `test_t4_scenario_06_glo_historical_backtesting_sync_journey`: Full end-to-end backtesting verification against 24 GLO draw records.

---

## 6. Integrity & Compliance Statement

- All test cases are genuinely written to assert functional behavior, contract adherence, boundary safety, and integration semantics.
- No test cases or mock fixtures contain hardcoded passes, forced true assertions, or facade implementations.
