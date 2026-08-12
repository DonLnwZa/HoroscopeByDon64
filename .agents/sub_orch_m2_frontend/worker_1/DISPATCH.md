## 2026-08-12T17:12:13Z
You are worker_1 for Milestone M2 (Frontend UI Upgrade).
Your working directory is: e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m2_frontend\worker_1

MANDATORY DOCUMENTS TO READ:
1. e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md
2. e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md
3. e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m2_frontend\SCOPE.md
4. Explorer handoffs:
   - e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m2_frontend\explorer_1_v2\handoff.md
   - e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m2_frontend\explorer_2_v2\handoff.md
   - e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m2_frontend\explorer_3_v2\handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

OWNED FILES TO MODIFY:
- `omni_oracle_app/frontend/app.jsx`
- `omni_oracle_app/frontend/styles.css`
- `omni_oracle_app/frontend/__tests__/*`
- `omni_oracle_app/frontend/package.json` (create if needed for test runner)
- `omni_oracle_app/frontend/vitest.config.ts` (create if needed for test runner)

ASSIGNMENT:
1. R1 Frontend: Replace manual dropdowns (`birth_day_of_week`, `birth_month_lunar`, `birth_year_animal`) in `app.jsx` with `<input type="time" name="birth_time" aria-label="เวลาเกิด" />` with label `เวลาเกิด (ตัดรอบ 06:00 น. แบบไทย)`. Render auto-calculated Thai Lunar Calendar output card on the results screen when `results.chart.lunar_calendar` is returned.
2. R2 Frontend: Implement 78 face-down interactive Tarot card grid in `app.jsx` with selection counter (`เลือกไพ่แล้ว X / 10 ใบ` with `aria-label="card-counter"`), submit button state validation (disabled unless exactly 10 cards are selected), and sending `selected_tarot_cards: [0..77]` array in POST payload to `/api/divine`.
3. R3 Frontend: Render Heat Index badges (win count & heat level colors/icons: 🔥 High, ⚡ Medium, ❄️ Rare) alongside each recommended number in the results view.
4. R4 Frontend: Render Divination Transparency tags (number_origins breakdown e.g. 📍 *ที่มา: ฐาน 4 มหาภูติ + ไพ่ทาโรต์ใบที่ 3*) alongside each recommended number in the results view.
5. Update `styles.css` with CSS rules for the Tarot deck grid, card counter, heat index badges, transparency tags, and number result cards.
6. Create/update component unit tests in `omni_oracle_app/frontend/__tests__/` to cover R1, R2, R3, and R4 requirements.
7. Run the tests using `npx vitest run` or pytest/e2e runner, verify build/tests pass, and record test commands & outputs in your report.

Write your report to: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m2_frontend\worker_1\handoff.md` and notify parent when done.
