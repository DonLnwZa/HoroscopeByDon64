# Scope: Milestone M1 — Backend Engines & API Upgrade

## Objectives
Implement and verify all backend features for R1, R2, R3, R4 in `omni_oracle_app/backend/`.

## Scope Checklist
- [x] R1: Implement auto Thai Lunar Calendar calculation from `birth_date` (YYYY-MM-DD) and `birth_time` (HH:MM) applying the 6:00 AM Bangkok cutoff rule (deriving Thai Day of week, Lunar Month 1-12, and Zodiac Year 1-12).
- [x] R2: Update `tarot.py` `draw_celtic_cross(selected_cards)` to accept an array of 10 card indices (`0..77`) from `selected_tarot_cards` in request payload and map them to Celtic Cross positions.
- [x] R3: Update `lottery_stats.py` to evaluate recommended numbers against 24 historical draw records in `lottery_results_past_1_year.json` and output `heat_index` levels (`HOT`, `WARM`, `COLD`) with win counts.
- [x] R4: Update `number_recommender.py` to track provenance across the 4 engines (Astrology, Numerology 7x9, Mahabote, Tarot, Lottery Hot Pool) and return `number_origins` mapping.
- [x] Update `/api/divine` endpoint in `omni_oracle_app/backend/app.py` to accept the new request payload (`birth_time`, `selected_tarot_cards`) and return `heat_index` and `number_origins`.
- [x] Write/update unit and integration tests in `omni_oracle_app/backend/tests/` to verify all backend changes.

## File Boundaries
- Primary owned files: `omni_oracle_app/backend/app.py`, `omni_oracle_app/backend/app/engines/*.py`, `omni_oracle_app/backend/tests/*.py`.
- Must NOT modify frontend files (`omni_oracle_app/frontend/*`).

## Reference Specification
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md`
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md`
