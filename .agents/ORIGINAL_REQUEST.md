# Original User Request

## Initial Request — 2026-08-12T05:35:28Z

Upgrade the existing Omni-Oracle lottery prediction web application (`e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`) with four features: 1) Approximate Thai Lunar Calendar auto-calculation from birth date and time, 2) Interactive Tarot selection UI (user selects 10 out of 78 facedown cards), 3) Backtesting Heat Index showing how often recommended numbers won in the past year, and 4) Transparency in displaying the origin of each recommended number.

Working directory: e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app
Integrity mode: development

## Requirements

### R1. Auto-Approximate Thai Lunar Calendar
Remove the manual dropdowns for Day of Week, Lunar Month, and Zodiac Year from the frontend. Instead, add a `birth_time` input. The backend must approximate the Thai lunar values based on the Gregorian birth date and time (using the 6:00 AM cut-off rule for the Thai day of the week).

### R2. Interactive Tarot Selection
Replace the backend random Tarot drawing with a frontend interactive UI. Display 78 cards face down. The user must click to select exactly 10 cards. The selected card indices must be sent to the `/api/divine` endpoint.

### R3. Heat Index (Backtesting)
The backend must compare the generated lucky numbers against the historical lottery results (`e:\ข้อมูลผลหวยย้อนหลัง 1 ปี\fetch_lottery\lottery_results_past_1_year.json`) and compute a "Heat Index" (how many times the number has won in the past year).

### R4. Divination Transparency
The backend must track and return the origin/source of each recommended lucky number (e.g., "Derived from Mahabote base 4 and Tarot card #3"). The frontend must display this origin alongside the Heat Index.

## Acceptance Criteria

### API Contract
- [ ] `/api/divine` accepts `birth_time` (string) and `selected_tarot_cards` (array of 10 integers).
- [ ] `/api/divine` response JSON contains a `heat_index` section detailing the historical win count for the recommended numbers.
- [ ] `/api/divine` response JSON contains a `number_origins` section detailing the source of each recommended number.

### Frontend Integration
- [ ] The user cannot submit the divination form until exactly 10 Tarot cards are selected on the UI.
- [ ] The final results screen displays the Heat Index and the origin (Transparency) of the recommended numbers.
