# Scope: Milestone M2 — Frontend UI Upgrade

## Objectives
Implement and verify all frontend UI features for R1, R2, R3, R4 in `omni_oracle_app/frontend/`.

## Scope Checklist
- [x] R1 Frontend: Remove 3 manual dropdowns (`birth_day_of_week`, `birth_month_lunar`, `birth_year_animal`) from `app.jsx`. Add `<input type="time" name="birth_time" />` (with label for birth time). Render auto-calculated Thai Lunar Calendar info card on the results screen.
- [x] R2 Frontend: Implement interactive 78 face-down Tarot card grid in `app.jsx`. Add selection counter `เลือกไพ่แล้ว X / 10 ใบ`, toggle/select card indices (`0..77`), disable submit button unless exactly 10 cards are selected, and send `selected_tarot_cards` array in POST payload to `/api/divine`.
- [x] R3 Frontend: Render Heat Index badges (win count & heat level badges: 🔥 High, ⚡ Medium, ❄️ Rare) alongside each recommended number in the results display.
- [x] R4 Frontend: Render Divination Transparency tags (provenance / source breakdown e.g. 📍 *ที่มา: ฐาน 4 มหาภูติ + ไพ่ทาโรต์ใบที่ 3*) alongside each recommended number.
- [x] Update frontend styles in `omni_oracle_app/frontend/styles.css` for tarot deck grid, card counter, heat index badges, and transparency tags.
- [x] Update frontend component tests in `omni_oracle_app/frontend/__tests__/` (IntakeForm, TarotSpread, RecommendedNumbers).

## File Boundaries
- Primary owned files: `omni_oracle_app/frontend/app.jsx`, `omni_oracle_app/frontend/styles.css`, `omni_oracle_app/frontend/index.html`, `omni_oracle_app/frontend/__tests__/*`.
- Must NOT break backend API integrations.

## Reference Specification
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md`
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md`
