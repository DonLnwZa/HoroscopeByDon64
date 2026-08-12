# Handoff Report — Frontend & UI Survey

**Agent**: `teamwork_preview_explorer`  
**Working Directory**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_survey_2`  
**Target Application**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`  
**Date**: 2026-08-12  

---

## 1. Observation

- **Observed File**: `omni_oracle_app/frontend/index.html` (Lines 1-20)
  - Loads React 18, ReactDOM 18, Framer Motion 10.16.4, and Babel standalone via CDN script tags (`<script src="https://unpkg.com/react@18/..."></script>`).
- **Observed File**: `omni_oracle_app/frontend/app.jsx` (Lines 1-141)
  - Lines 7-13: `formData` state includes `birth_day_of_week`, `birth_month_lunar`, `birth_year_animal` as manual string inputs.
  - Lines 65-98: Form contains manual dropdown `<select>` controls for Day of Week, Lunar Month, and Zodiac Year.
  - Line 20: POST request to `http://localhost:5000/api/divine` sending `formData`.
  - Lines 118-124: Results display basic string join for numbers (`{results.lucky_numbers.two_digit.join(" · ")}`) without Heat Index or Divination Transparency origins.
- **Observed File**: `omni_oracle_app/frontend/styles.css` (Lines 1-168)
  - Configures dark glassmorphism styling (`--bg-color: #1a0533`, `--accent-gold: #ffd700`, `.glass-card`).
- **Observed File**: `omni_oracle_app/frontend/__tests__/IntakeForm.test.tsx` (Lines 6-58)
  - Mocks `MockIntakeForm` containing `birth_date`, `birth_time` (`<input type="time" />`), `birth_province`, `full_name`.
- **Observed File**: `omni_oracle_app/frontend/__tests__/TarotSpread.test.tsx` (Lines 33-49)
  - Mocks `MockTarotSpread` containing card counter `เลือกไพ่แล้ว {selected.length} / 10 ใบ` and Celtic Cross positions.
- **Observed File**: `omni_oracle_app/frontend/__tests__/RecommendedNumbers.test.tsx` (Lines 5-42)
  - Mocks `MockRecommendedNumbers` rendering 2-digit, 3-digit, 6-digit chips, and confidence percentage.
- **Observed File**: `omni_oracle_app/backend/app.py` (Lines 46-92)
  - `/api/divine` accepts `birth_date`, `birth_day_of_week`, `birth_month_lunar`, `birth_year_animal`, runs `tarot_engine.draw_celtic_cross()` on server side, and returns `lucky_numbers`, `synthesis`, `disclaimer`.
- **Observed File**: `e2e_tests/test_e2e_full_stack.py` (Lines 63-70)
  - Expects `full_intake_payload` with `birth_date`, `birth_time`, `birth_province`, `full_name`, and `selected_cards: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`.

---

## 2. Logic Chain

1. **Observation 1 & 2**: `app.jsx` currently renders manual select dropdowns for Day of Week, Lunar Month, and Zodiac Year, while `IntakeForm.test.tsx` and `test_e2e_full_stack.py` use `birth_time`.
   - *Inference*: Requirement R1 (Auto-Approximate Thai Lunar Calendar) requires removing the 3 manual dropdowns from `app.jsx`, adding `<input type="time" />`, passing `birth_time` to backend, and displaying an auto-calculated lunar calendar result card on the results screen.
2. **Observation 2, 5, & 6**: `app.jsx` has no card selection UI, and backend `app.py` currently draws random cards on the server. `test_e2e_full_stack.py` expects `selected_cards` array of 10 integers.
   - *Inference*: Requirement R2 (Interactive Tarot Selection) requires adding a 78-card interactive deck grid to the frontend form, tracking selected card indices (`0..77`), displaying `เลือกไพ่แล้ว X / 10 ใบ`, disabling submit until `selected_cards.length === 10`, and posting `selected_tarot_cards` to `/api/divine`.
3. **Observation 2 & 7**: `app.jsx` displays numbers as plain joined text without historical win frequency or origin sources.
   - *Inference*: Requirement R3 (Heat Index) and R4 (Divination Transparency) require enhancing the results view to display Heat Index badges (win frequency, heat level colors) and origin derivation tags (e.g. 📍 *มาจากฐาน 4 มหาภูติ + ไพ่ทาโรต์ใบที่ 3*) alongside each recommended number.

---

## 3. Caveats

- **Network / CDN dependencies**: `index.html` loads React and Framer Motion from unpkg CDNs. In offline environments, local script bundling or fallback script tags may be needed.
- **Backend API Synchronization**: The backend endpoint `/api/divine` (Flask) and `/api/v1/predict` (FastAPI spec) must both update to handle `birth_time` and `selected_tarot_cards` and return `heat_index` and `number_origins`.

---

## 4. Conclusion

The existing frontend structure in `omni_oracle_app/frontend` is clean, modular, and ready for feature upgrades R1–R4. Detailed blueprints and specifications have been recorded in `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_survey_2\survey_report.md`.

---

## 5. Verification Method

1. **Inspect Survey Artifacts**:
   - Check `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_survey_2\survey_report.md` for complete survey details covering R1, R2, R3, R4.
2. **Component Tests**:
   - Run Vitest / RTL tests for frontend components:
     ```bash
     cd e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\frontend
     npx vitest run
     ```
3. **E2E Full Stack Tests**:
   - Run pytest for full stack integration:
     ```bash
     cd e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app
     pytest e2e_tests/test_e2e_full_stack.py
     ```
