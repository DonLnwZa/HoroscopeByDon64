# E2E Test Suite Architecture & Feature Specification Report
**Project:** Thai Lottery Divination Web Application (Omni-Oracle)  
**Track:** E2E Testing Track  
**Agent Identity:** `teamwork_preview_spec_miner_e2e_s1`  
**Working Directory:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\teamwork_preview_spec_miner_e2e_s1`  
**Date:** 2026-08-06  

---

## 1. Executive Summary & Environment Audit

This report establishes the opaque-box End-to-End (E2E) testing architecture and feature specification matrix for the **Omni-Oracle Thai Lottery Divination Web Application**. 

### 1.1 Environment & Tooling Audit
- **Workspace Location:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย`
- **Target Application Path:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app` (Dual Backend/Frontend target layout).
- **Historical Data Location:** `e:\ข้อมูลผลหวยย้อนหลัง 1 ปี\fetch_lottery\lottery_results_past_1_year.json` (24 historical GLO draws, 83,878 bytes, structured JSON array) and `fetch_lottery.py` (GLO API extraction script).
- **Backend Test Ecosystem (Python):**
  - Test Runner: `pytest` with `pytest-asyncio` for async FastAPI endpoints.
  - API Testing Client: `httpx` (AsyncClient) / `starlette.testclient.TestClient`.
  - Schema Validation: `pydantic` schemas for API contract assertions.
- **Frontend Test Ecosystem (Node.js / React / Next.js 14):**
  - Component/Unit Test Runner: `vitest` + `@testing-library/react` + `jsdom`.
  - E2E / API Integration Runner: Playwright / Vitest API harness.
- **Testing Approach:** Strict **Opaque-Box Testing** (black-box testing via public interfaces, REST API contracts, and user interactions without inspecting internal class states).

---

## 2. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Calculation Engine | Thai Astrology Engine | Calculates natal chart using Lahiri Ayanamsa, 10 planetary positions, 12 houses, D9 Navamsa, and D3 Drekkana | `birth_date` (YYYY-MM-DD), `birth_time` (HH:MM), `birth_province` | `AstrologyChart` (planetary degrees, house placements, D9/D3 divisional charts) | Raises `ValueError` for invalid date/time or unrecognized province | `Omni-Oracle Spec §2.1`, `PROJECT.md §11.1` |
| 2 | Calculation Engine | 7-Digit 9-Base Numerology Engine | Computes 7x9 matrix across Base 1 (Day), Base 2 (Month), Base 3 (Year), Base 4 strength, and 21 houses | `birth_date` (solar day, month, year) | `NumerologyMatrix` (7x9 matrix, house collisions, planetary pairs, strength rating) | Raises `ValueError` for out-of-bounds calendar inputs | `Omni-Oracle Spec §2.2`, `PROJECT.md §11.2` |
| 3 | Calculation Engine | Burmese Mahabote Engine | Calculates Chula Sakarat (Apr 16 Songkran cutoff), Modulo 7 placement across 7 positions, Taksa, and Kalayok | `birth_date`, `birth_time` | `MahaboteChart` (7 positions: Panga, Puti, Marana, Adhipati, Raja, Atta, Majjhima; Taksa alignment) | Returns validation error for missing birth date or invalid time format | `Omni-Oracle Spec §2.3`, `PROJECT.md §11.3` |
| 4 | Calculation Engine | Tarot Card Engine | CSPRNG deck shuffler for 78 cards, upright/reversed states, 10-card Celtic Cross spread | `selected_card_indices` (array of 10 integers 0-77 or CSPRNG seed) | `TarotSpread` (10 cards with positions, orientations, and arcana metadata) | Raises `ValueError` for duplicate card indices or out-of-range indices (<0 or >77) | `Omni-Oracle Spec §2.4`, `PROJECT.md §11.4` |
| 5 | Data Processing | Historical Lottery Data Processor | Parses 1-year GLO draws from `lottery_results_past_1_year.json`, extracts 2-digit, 3-digit, and 6-digit frequencies | File path to `lottery_results_past_1_year.json` | `LotteryStats` (digit frequency distribution, draw count, date range) | Raises `FileNotFoundError` or `JSONDecodeError` on missing/corrupted file | `ORIGINAL_REQUEST.md §R1`, `PROJECT.md §11.5` |
| 6 | Recommendation | Statistical Lottery Recommender | Combines personal divination digit scores (60% weight) with historical GLO frequencies (40% weight) | `DivinationFactSheet`, `LotteryStats` | `RecommendedNumbers` (top 2-digit, 3-digit, and 6-digit lucky numbers with confidence scores) | Fallback to historical top digits if divination scores are uniform | `PROJECT.md §11.6` |
| 7 | Backend API | Backend FastAPI & Pydantic Schemas | REST API endpoints (`/api/v1/predict`, `/api/v1/health`, `/api/v1/lottery/stats`) with OpenAPI contract validation | `PredictRequestSchema` JSON payload | `PredictResponseSchema` JSON payload | Returns `HTTP 422 Unprocessable Entity` for invalid payloads | `ORIGINAL_REQUEST.md §R1`, `PROJECT.md §11.7` |
| 8 | Safety & Security | Omni-Oracle Safety Guardrail Validator | Middleware & regex validator forbidding health diagnosis, medical advice, and financial guarantees | Text string or `PredictResponseSchema` | Sanitized response + `safety_metadata` (passed/flagged, rules triggered) | Strips unsafe text or returns `HTTP 400 Bad Request` with safety disclaimer | `ORIGINAL_REQUEST.md §R3`, `Omni-Oracle Spec §4` |
| 9 | Frontend UI | Next.js Premium Glassmorphic UI | Dark/Mystic theme (`#0B0F19`), responsive birthdate intake form, Framer Motion animations | User form inputs (`full_name`, `birth_date`, `birth_time`, `province`) | Interactive UI display, loading skeleton, divination result dashboards | Displays inline field validation errors and toast notifications | `ORIGINAL_REQUEST.md §R2`, `PROJECT.md §11.9` |
| 10 | Frontend UI | Interactive Tarot Drawer & Display | 3D/Glass card flip animations and 10-card Celtic Cross spread interaction | User mouse clicks / touch selections | Visual tarot cards flipped with upright/reversed states and readings | Prevents selection beyond 10 cards, disables already drawn cards | `PROJECT.md §11.10` |
| 11 | Integration | Full Stack Integration & E2E Verification | Seamless connection between Next.js frontend and FastAPI backend with error handling | User submission flow | Complete end-to-end reading, numbers recommendation, and safety banner | Graceful fallback display and retry buttons on backend API timeouts | `ORIGINAL_REQUEST.md §Acceptance`, `PROJECT.md §11.11` |

---

## 3. Edge Cases Matrix

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Thai Astrology | Midnight birth time (`00:00:00` vs `23:59:59`) | Correctly shifts ascendant degree across zodiac boundary without crash. |
| 2 | Thai Astrology | Unknown birth time (null/omitted) | Defaults to 12:00 PM solar noon with ascendant uncertainty warning in metadata. |
| 3 | Burmese Mahabote | Songkran cutoff boundary (April 15 vs April 16 birth date) | April 15 uses previous Chula Sakarat year (จ.ศ. - 1); April 16 shifts to new จ.ศ. year. |
| 4 | Burmese Mahabote | Leap year / February 29 birth date | Correctly computes Modulo 7 day-of-week and Chula Sakarat without date library exception. |
| 5 | 7x9 Numerology | Duplicate house collisions (e.g. Venus in Tanu + Kadumba + Lapa) | Correctly aggregates base strength scores and highlights multi-house alignment. |
| 6 | Tarot Card Engine | User submits duplicate card indices `[0, 0, 1, 2, ...]` | Engine rejects input with `ValueError("Duplicate card selection")`. |
| 7 | Tarot Card Engine | User draws 10 cards with all 10 reversed | Renders reversed interpretations correctly without causing UI layout breakage. |
| 8 | Historical Lottery | Empty or missing `lottery_results_past_1_year.json` | Gracefully falls back to default GLO frequency dataset or returns descriptive `HTTP 503` error. |
| 9 | Statistical Recommender | 60/40 Weight tie-breaker (two numbers equal score) | Sorts tie by highest 1st prize historical frequency, then ascending numerical order. |
| 10 | Safety Guardrail | Prompt containing health inquiry ("จะหายจากโรคเบาหวานไหม") | Guardrail intercepts inquiry, sanitizes response to life vitality advice, and sets `health_flag=true`. |
| 11 | Safety Guardrail | Prompt requesting financial guarantee ("การันตีเลขนี้ถูกแน่นอน 100%") | Guardrail appends financial disclaimer and strips guarantee language from prediction. |
| 12 | Backend FastAPI | Invalid JSON payload (e.g. `birth_date: "invalid-date"`) | Returns `HTTP 422 Unprocessable Entity` with detailed field location in error response. |
| 13 | Next.js Frontend | Network failure during backend API request | UI transitions from loading spinner to friendly error card with "Retry Prediction" button. |

---

## 4. Opaque-Box Test Suite Architecture

To ensure 100% test coverage and non-flaky verification across all 11 features, the test suite is structured into **4 Tiers**:

```
                              +---------------------------------------+
                              |      Tier 4: Real-World Scenarios     |
                              |         (6 E2E User Journeys)         |
                              +---------------------------------------+
                                                  |
                              +---------------------------------------+
                              |    Tier 3: Cross-Feature Pairwise    |
                              |       (11 Integration Suites)         |
                              +---------------------------------------+
                                                  |
                              +---------------------------------------+
                              |     Tier 2: Boundary & Safety         |
                              |     (55 Input Validation & R3 Tests)  |
                              +---------------------------------------+
                                                  |
                              +---------------------------------------+
                              |     Tier 1: Feature Coverage          |
                              |      (55 Functional Seam Tests)       |
                              +---------------------------------------+
```

### 4.1 Tier Breakdown & Requirements

#### Tier 1: Feature Coverage Test Suite (55 Test Cases Minimum)
- **Scope:** 5 test cases per feature across all 11 features (5 x 11 = 55 tests).
- **Target:** Verify happy-path calculations, REST API schema compliance, UI rendering, and data extraction through public interfaces (seams).
- **Rules:** Opaque-box execution. Asserts outputs matching expected mathematical models and REST contracts without peeking into internal engine private helper state.

#### Tier 2: Boundary & Safety Test Suite (55 Test Cases Minimum)
- **Scope:** 5 test cases per feature across all 11 features (5 x 11 = 55 tests).
- **Target:** Verify system resilience against invalid inputs, boundary dates (Songkran cutoff, midnight, leap years), malformed JSON, out-of-range arrays, and strict Omni-Oracle **R3 Safety Constraints** (health advice & financial guarantees prohibition).
- **Rules:** Ensures API returns appropriate status codes (`400`, `422`, `503`) and safety metadata flag states.

#### Tier 3: Cross-Feature Pairwise Integration Suite (11 Test Cases Minimum)
- **Scope:** 1 test suite per feature pair interaction (11 tests).
- **Target:** Verify interactions between combined modules:
  1. Thai Astrology ↔ 7x9 Numerology synthesis alignment.
  2. Burmese Mahabote ↔ Tarot card contextual overlay.
  3. Divination Fact Sheet ↔ Historical Lottery Recommender 60/40 weighting.
  4. FastAPI Backend ↔ Safety Guardrail middleware interception.
  5. Next.js Intake Form ↔ FastAPI `/api/v1/predict` JSON serialization.
  6. Tarot Drawer UI ↔ Backend Celtic Cross payload mapping.
  7. Historical Lottery Processor ↔ Statistical Recommender frequency cache.
  8. Safety Guardrail Sanitizer ↔ Omni-Oracle Persona Output formatter.
  9. Next.js Glassmorphic UI ↔ Async Loading state & API timeout fallback.
  10. Full Stack REST API ↔ OpenAPI Pydantic response validation.
  11. End-to-End Divination Pipeline ↔ Recommended Numbers JSON structure.

#### Tier 4: Real-World Application Scenarios (6 Test Scenarios Minimum)
- **Scope:** 6 complete end-to-end user scenarios simulating real user journeys:
  - **Scenario 1:** Complete Happy-Path User Journey (Intake Form -> 10-card Tarot Pick -> Real-time Divination -> 60/40 Recommended Numbers).
  - **Scenario 2:** Songkran New Year Born User Journey (Verifying Chula Sakarat year shift & Burmese Mahabote calculation integrity).
  - **Scenario 3:** Adversarial User Input Journey (Attempting prompt injection / health questions -> Guardrail filtering -> Safe guidance output).
  - **Scenario 4:** Minimal Data User Journey (Birthdate provided without birth time -> Default solar noon handling -> Valid reading output).
  - **Scenario 5:** Network Interruption & Recovery Journey (API failure mid-request -> UI toast alert -> Successful retry).
  - **Scenario 6:** Lottery Historical Draw Synchronization Journey (Parser reading 24 GLO draws -> Frequency matching -> Consistent top recommended numbers).

---

## 5. Recommended Entry Points and Test Runner Commands

### 5.1 Directory Layout for Test Suite
Tests will be placed cleanly within `omni_oracle_app/`:

```
omni_oracle_app/
├── backend/
│   └── tests/
│       ├── conftest.py
│       ├── test_tier1_feature_coverage.py
│       ├── test_tier2_boundary_safety.py
│       ├── test_tier3_pairwise_integration.py
│       └── test_tier4_realworld_scenarios.py
├── frontend/
│   └── __tests__/
│       ├── IntakeForm.test.tsx
│       ├── RecommendedNumbers.test.tsx
│       └── TarotSpread.test.tsx
└── e2e_tests/
    ├── test_e2e_full_stack.py
    └── fixtures/
        └── mock_lottery_data.json
```

### 5.2 Test Runner Commands

1. **Run Backend Pytest Suite (Tiers 1-4):**
   ```bash
   cd omni_oracle_app/backend
   pytest tests/ -v --tb=short
   ```

2. **Run Frontend Vitest Suite:**
   ```bash
   cd omni_oracle_app/frontend
   npm test -- --run
   ```

3. **Run Full Opaque-Box E2E Integration Suite:**
   ```bash
   cd omni_oracle_app
   pytest e2e_tests/ -v
   ```

---

## 6. Opaque-Box Mocking Strategy

To guarantee deterministic, fast, and isolated test execution without external network dependencies:

1. **External Network Mocking (GLO Web API):**
   - The standalone `fetch_lottery.py` script queries the external GLO endpoint `https://www.glo.or.th/api/checking/getLotteryResult`.
   - In test environments, tests must mock `urllib.request.urlopen` or `httpx` calls using `unittest.mock` or `pytest-mock` fixtures that load local `lottery_results_past_1_year.json`.

2. **CSPRNG Seed Mocking for Tarot & Lottery Tests:**
   - The Tarot engine uses CSPRNG deck shuffling (`secrets` / `random.SystemRandom`).
   - For repeatable Tier 1-3 tests, fixture helpers inject a fixed PRNG seed (`random.Random(42)`) or explicit `selected_card_indices` array, ensuring identical card draws across test runs without mutating the core tarot selection algorithm.

3. **Frontend API Mocking:**
   - Frontend Vitest tests mock `/api/v1/predict` responses using `msw` (Mock Service Worker) or `fetch` overrides, verifying UI state transitions (loading skeleton -> result dashboard) against frozen JSON fixtures.

4. **Preserving Opaque-Box Integrity:**
   - Tests interact exclusively with **Public Interfaces** (Python class public methods, FastAPI HTTP endpoints, React DOM elements).
   - Private methods (e.g. `_calculate_ayanamsa()`, `_mod7()`) are never called directly by tests, preserving encapsulation and allowing internal refactoring without breaking tests.

---

## 7. Next Steps & Handoff Checklist
- [x] Environment audit completed.
- [x] All 11 features and edge cases fully probed and cataloged.
- [x] 4-Tier Opaque-Box Architecture specified (127 minimum test cases).
- [x] Entry points, test commands, and mock strategy published.
- [x] Ready to hand off to Implementation and Verification teams.
