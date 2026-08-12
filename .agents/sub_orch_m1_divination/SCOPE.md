# Scope: Milestone 1 — Backend Core Divination Engines

## Architecture
Target Application Directory: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`
Directory: `omni_oracle_app/backend/app/engines/` and `omni_oracle_app/backend/tests/`

Modules to implement:
1. `thai_astrology.py`: Natal chart calculation (Lahiri Ayanamsa, 10 planets, 12 houses, D9 Navamsa, D3 Drekkana).
2. `numerology_7x9.py`: 7-digit 9-base matrix engine (Base 1-3, Base 4 strength, house collisions, planetary pairs).
3. `mahabote.py`: Burmese Mahabote engine (Chula Sakarat, April 16 Songkran cutoff, Modulo 7, 7 body positions, Taksa/Kalayok).
4. `tarot.py`: CSPRNG deck shuffler (78 cards), reversal state handling, 10-card Celtic Cross spread.

TDD Requirement:
Strict Red -> Green -> Refactor cycle.
Write Pytest unit tests in `omni_oracle_app/backend/tests/` for public interfaces/seams BEFORE implementation.

## Milestones
| # | Name | Scope | Status |
|---|------|-------|--------|
| M1.1 | Thai Astrology Engine & Tests | Pytest seam + Lahiri Ayanamsa natal chart engine | DONE |
| M1.2 | 7x9 Numerology Engine & Tests | Pytest seam + 7-Digit 9-Base matrix engine | DONE |
| M1.3 | Burmese Mahabote Engine & Tests | Pytest seam + Chula Sakarat 7-position engine | PLANNED |
| M1.4 | Tarot Card Engine & Tests | Pytest seam + CSPRNG 78-card Celtic Cross engine | PLANNED |
