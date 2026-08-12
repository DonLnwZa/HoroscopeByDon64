# Scope: E2E Testing Track

## Objectives
Design and implement a complete opaque-box E2E test suite (Tiers 1-4) for Omni-Oracle Thai Lottery Web Application according to `PROJECT.md` specifications and `ORIGINAL_REQUEST.md`.

## Test Requirements (Tiers 1-4)
- **Tier 1 - Feature Coverage (>=5 tests per feature)**:
  - R1: Thai Lunar Calendar auto-calculation & 6:00 AM cutoff rule.
  - R2: Interactive Tarot 10 card array input validation and mapping.
  - R3: Backtesting Heat Index win count & heat level calculations.
  - R4: Divination Transparency origin breakdown format.
- **Tier 2 - Boundary & Corner Cases (>=5 tests per feature)**:
  - Birth time boundary tests: 05:59:59 (cutoff applied) vs 06:00:00 (no cutoff), 00:00, 23:59.
  - Tarot selection boundary tests: <10 cards, >10 cards, out-of-range indices (<0 or >77), duplicate indices.
  - Heat Index data boundary tests: numbers with 0 wins (COLD), 1-2 wins (WARM), >=3 wins (HOT).
  - Divination Transparency boundary tests: missing engine origins, empty inputs.
- **Tier 3 - Cross-Feature Pairwise Integration**:
  - Combined R1 + R2 + R3 + R4 full request/response payload validation.
- **Tier 4 - Real-World Application Scenarios**:
  - Complete user divination session workflows.

## Deliverables
- `TEST_INFRA.md` at project root (`e:\เว็บดูดวงเพื่อซื้อหวยไทย\TEST_INFRA.md`).
- E2E Test files in `omni_oracle_app/e2e_tests/` and `omni_oracle_app/backend/tests/`.
- `TEST_READY.md` at project root (`e:\เว็บดูดวงเพื่อซื้อหวยไทย\TEST_READY.md`) summarizing test counts and execution command when all E2E tests are designed and passing.

## Reference Specification
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md`
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md`
