## 2026-08-06T01:07:01Z

You are a Test Writer for the E2E Testing Track of the Thai Lottery Divination Web Application (Omni-Oracle).

Your identity: teamwork_preview_test_writer_e2e_s1
Your working directory: e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\teamwork_preview_test_writer_e2e_s1

Input Documents:
- Original Request: e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md
- Project Document: e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md
- Test Infra Spec: e:\เว็บดูดวงเพื่อซื้อหวยไทย\TEST_INFRA.md
- Spec Miner Analysis: e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\teamwork_preview_spec_miner_e2e_s1\analysis.md

Scope & Tasks:
Write the complete opaque-box 4-tier requirement-driven E2E test suite in `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\`:

1. `omni_oracle_app/backend/tests/conftest.py`:
   - Pytest fixtures for `TestClient`, mock GLO historical lottery JSON data (24 draw results), tarot card deck fixtures, and sample birthdate intake payloads.

2. `omni_oracle_app/backend/tests/test_tier1_feature_coverage.py`:
   - 55 Tier 1 functional test cases (5 per feature across 11 features: Thai Astrology, 7x9 Numerology, Burmese Mahabote, Tarot Celtic Cross, Historical Lottery Processor, Statistical Recommender, FastAPI endpoints, Omni-Oracle Safety Filter, Glassmorphic UI API contract, Interactive Tarot Drawer API, Full Stack Integration).

3. `omni_oracle_app/backend/tests/test_tier2_boundary_safety.py`:
   - 55 Tier 2 boundary & safety test cases (5 per feature across 11 features: midnight birth time, null birth time, Songkran cutoff April 15 vs 16, leap year Feb 29, duplicate tarot card indices, empty lottery JSON, 60/40 score ties, prompt injection health inquiries, financial guarantee prompts, malformed JSON 422 errors, network timeout fallbacks).

4. `omni_oracle_app/backend/tests/test_tier3_pairwise_integration.py`:
   - 11 Tier 3 pairwise integration test cases testing interactions between features (e.g. Astrology ↔ Numerology, Mahabote ↔ Tarot, FactSheet ↔ Recommender 60/40 weighting, FastAPI ↔ Guardrails).

5. `omni_oracle_app/backend/tests/test_tier4_realworld_scenarios.py`:
   - 6 Tier 4 real-world user journey E2E test scenarios (Happy path, Songkran birthday, Adversarial prompt safety check, Minimal input data, API failure recovery, GLO historical draw sync).

6. `omni_oracle_app/frontend/__tests__/IntakeForm.test.tsx`, `RecommendedNumbers.test.tsx`, `TarotSpread.test.tsx`:
   - Vitest component & UI validation test files for Next.js frontend interfaces.

7. `omni_oracle_app/e2e_tests/test_e2e_full_stack.py`:
   - Full stack E2E integration test suite validating opaque-box endpoints.

Ensure every test has explicit assertions, descriptive docstrings, and clean imports.
Deliver your handoff report to `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\teamwork_preview_test_writer_e2e_s1\handoff.md` and message your parent when complete.
