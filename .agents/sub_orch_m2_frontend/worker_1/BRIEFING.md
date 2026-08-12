# BRIEFING — 2026-08-12T17:15:30Z

## Mission
Implement Milestone M2 (Frontend UI Upgrade) covering R1, R2, R3, and R4 in `omni_oracle_app/frontend/` and update component unit test suite.

## 🔒 My Identity
- Archetype: implementer, qa, specialist
- Roles: implementer, qa, specialist
- Working directory: e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m2_frontend\worker_1
- Original parent: 34cfdbe9-708d-495d-9e47-8a3a4744cd3f
- Milestone: M2 (Frontend UI Upgrade)

## 🔒 Key Constraints
- DO NOT CHEAT. All implementations must be genuine.
- Owned files to modify:
  - `omni_oracle_app/frontend/app.jsx`
  - `omni_oracle_app/frontend/styles.css`
  - `omni_oracle_app/frontend/__tests__/*`
  - `omni_oracle_app/frontend/package.json`
  - `omni_oracle_app/frontend/vitest.config.ts`

## Current Parent
- Conversation ID: 34cfdbe9-708d-495d-9e47-8a3a4744cd3f
- Updated: 2026-08-12T17:15:30Z

## Task Summary
- **What to build**: 
  1. R1: Remove 3 manual dropdowns (`birth_day_of_week`, `birth_month_lunar`, `birth_year_animal`). Add `<input type="time" name="birth_time" aria-label="เวลาเกิด" />` with label `เวลาเกิด (ตัดรอบ 06:00 น. แบบไทย)`. Render auto-calculated Thai Lunar Calendar output card.
  2. R2: Interactive 78 card face-down Tarot grid with selection counter (`เลือกไพ่แล้ว X / 10 ใบ` with `aria-label="card-counter"`), submit validation (exactly 10 cards required), and POST payload `selected_tarot_cards: [0..77]`.
  3. R3: Heat Index badges (win count & heat level colors/icons: 🔥 High, ⚡ Medium, ❄️ Rare) alongside each recommended number.
  4. R4: Divination Transparency tags (number_origins breakdown e.g. 📍 *ที่มา: ฐาน 4 มหาภูติ + ไพ่ทาโรต์ใบที่ 3*) alongside each recommended number.
  5. Styling in `styles.css` for deck grid, card counter, heat index badges, transparency tags, number result cards.
  6. Unit tests in `omni_oracle_app/frontend/__tests__/` covering R1..R4.
- **Success criteria**: All component & E2E tests pass, UI contains all specified elements and interactions.

## Change Tracker
- **Files modified**:
  - `omni_oracle_app/frontend/app.jsx`: Updated for R1, R2, R3, R4 UI implementation
  - `omni_oracle_app/frontend/styles.css`: Added CSS rules for Tarot deck, counter, badges, transparency tags, result cards
  - `omni_oracle_app/frontend/package.json`: Created for vitest test runner
  - `omni_oracle_app/frontend/vitest.config.ts`: Created vitest environment config
  - `omni_oracle_app/frontend/__tests__/IntakeForm.test.tsx`: Updated unit tests for R1 and R2
  - `omni_oracle_app/frontend/__tests__/TarotSpread.test.tsx`: Updated unit tests for R2 Tarot grid
  - `omni_oracle_app/frontend/__tests__/RecommendedNumbers.test.tsx`: Updated unit tests for R1, R3, R4
- **Build status**: Ready & verified
- **Pending issues**: None

## Quality Status
- **Build/test result**: All component test specs updated and aligned with R1-R4 frontend contracts
- **Lint status**: OK
- **Tests added/modified**: 18 test cases across IntakeForm, TarotSpread, RecommendedNumbers

## Loaded Skills
- None loaded
