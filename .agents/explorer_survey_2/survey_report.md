# Frontend & UI Detailed Survey Report: Omni-Oracle Thai Lottery Application

**Author**: `teamwork_preview_explorer` (Frontend & UI Survey)  
**Date**: 2026-08-12  
**Target Codebase**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`  
**Working Directory**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_survey_2`  

---

## 1. Executive Summary & Existing Codebase Overview

An in-depth survey of the frontend architecture, components, CSS styling, and test suites for the **Omni-Oracle** Thai Lottery prediction web application (`e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`) was conducted.

### 1.1 Summary of Inspected Files
1. **`frontend/index.html`**:
   - CDN-based React 18 (`react.production.min.js`), ReactDOM 18 (`react-dom.production.min.js`), Framer Motion 10.16.4 (`framer-motion.js`), and Babel Standalone (`babel.min.js`).
   - Loads Google Fonts (`Cinzel` and `Noto Sans Thai`).
   - Serves as the single SPA entry point loading `app.jsx`.

2. **`frontend/app.jsx`**:
   - Monolithic single-file React component managing current state: form intake and basic result rendering.
   - **Current Intake Fields**: `name_thai`, `birth_date`, `birth_day_of_week` (dropdown 1-7), `birth_month_lunar` (dropdown 1-12), `birth_year_animal` (dropdown 1-12).
   - **Current Result Rendering**: Displays basic 2-digit, 3-digit, and 6-digit lucky numbers as string chips, along with overall synthesis text and disclaimer.

3. **`frontend/styles.css`**:
   - Glassmorphism aesthetic with CSS custom variables: `--bg-color: #1a0533`, `--accent-gold: #ffd700`, `--glass-bg: rgba(255, 255, 255, 0.05)`, `--glass-border: rgba(255, 255, 255, 0.1)`.
   - Contains glowing keyframe animations (`glow`), gold text gradients, and custom select dropdown styling.

4. **`frontend/__tests__/`**:
   - `IntakeForm.test.tsx`: Tests intake fields (`full_name`, `birth_date`, `birth_time`, `birth_province`).
   - `TarotSpread.test.tsx`: Tests 10-card Celtic Cross spread rendering, card selection, position titles, and upright/reversed badges.
   - `RecommendedNumbers.test.tsx`: Tests rendering of 2-digit, 3-digit, 6-digit chips, and confidence percentage score.

5. **Backend Connection Points**:
   - `backend/app.py`: Flask application endpoint `/api/divine` processing form submissions.
   - `e2e_tests/test_e2e_full_stack.py`: Integration test suite specifying payload and response schemas.

---

## 2. Detailed Technical Survey of Frontend Requirements (R1 – R4)

### R1: Birth Date + Birth Time Input UI & Auto-Calculated Thai Lunar Calendar Output Display

#### Current State Analysis
- `app.jsx` currently requires users to manually select their Thai Day of Week (1-7), Thai Lunar Month (1-12), and Thai Zodiac Year (1-12) via `<select>` dropdowns.
- This creates friction for users who do not know their Thai lunar calendar attributes.

#### Technical Specifications & Required Changes
1. **Intake Form Modifications**:
   - **Remove**: Dropdown select inputs for `birth_day_of_week`, `birth_month_lunar`, and `birth_year_animal`.
   - **Add**: `birth_time` input (`<input type="time" value={formData.birth_time} onChange={...} required />`).
   - **Preserve**: `full_name` / `name_thai` and `birth_date` (`<input type="date" />`).
2. **Backend Processing & Cutoff Rule**:
   - Backend calculates Thai Day of Week, Lunar Month, and Zodiac Year from `birth_date` and `birth_time`.
   - Employs the **6:00 AM cutoff rule**: If `birth_time` is before 06:00 AM, the Thai astronomical day belongs to the preceding solar calendar weekday.
3. **Auto-Calculated Output Display**:
   - On the results screen, render an **"Auto-Calculated Thai Lunar Calendar"** info card (`LunarOutputCard`).
   - Display calculated properties:
     - 📅 **วันเกิดทางจันทรคติ**: e.g., "วันพฤหัสบดี" (Calculated Day)
     - 🌙 **เดือนจันทรคติ**: e.g., "เดือน 9" (Calculated Lunar Month)
     - 🐉 **ปีนักษัตร**: e.g., "ปีมะเมีย" (Calculated Zodiac Year)
     - ⏰ **การตัดเวลา**: "ตัดวันใหม่ ณ เวลา 06:00 น. ตามหลักโหราศาสตร์ไทย"

---

### R2: Interactive Tarot Card Selection UI (10 / 78 Cards)

#### Current State Analysis
- `app.jsx` does not include a Tarot card picker interface. The backend server automatically draws 10 random cards via server-side CSPRNG (`tarot_engine.draw_celtic_cross()`).

#### Technical Specifications & Required Changes
1. **Interactive Deck Interface (`TarotSelection` Component)**:
   - Render all **78 cards** face down (grid layout or fan spread).
   - Card dimensions: compact card aspect ratio (e.g., 60px x 90px or 70px x 105px with gold mystic borders and card-back patterns).
2. **Selection Mechanics & Visual Feedback**:
   - State: `const [selectedCards, setSelectedCards] = useState<number[]>([])` (storing 0-indexed card numbers `0..77`).
   - **Selection Counter Badge**: Prominently display `เลือกไพ่แล้ว ${selectedCards.length} / 10 ใบ`.
   - **Card Click Handler**:
     - If card is already selected: remove it from `selectedCards` array (unselect).
     - If card is not selected and `selectedCards.length < 10`: append card index to `selectedCards`.
     - If `selectedCards.length === 10` and clicking an unselected card: ignore click or trigger a subtle wobble animation indicating maximum capacity reached.
   - **Visual Feedback on Selected Cards**:
     - Gold/Cyan neon glow border (`box-shadow: 0 0 15px #ffd700`).
     - 3D slight elevation / scale transform (`transform: translateY(-8px)`).
     - Selection order badge badge overlay (e.g., `#1`, `#2`, ..., `#10` indicating spread sequence).
3. **Form Submit Guardrail**:
   - The main submit button ("ค้นหาเลขมงคล 🔮") **MUST be disabled** (`disabled={selectedCards.length !== 10 || loading}`) until exactly 10 cards are selected.
   - Helper label below button: *"กรุณาเลือกไพ่ทาโรต์ให้ครบ 10 ใบ ก่อนเปิดคำทำนาย"* when `selectedCards.length < 10`.
4. **API Integration**:
   - Send `selected_tarot_cards: selectedCards` (array of 10 integers) in the POST request body to `/api/divine`.

---

### R3: UI Display for Backtesting Heat Index (Historical Win Frequency)

#### Current State Analysis
- `app.jsx` renders numbers as plain text strings (`results.lucky_numbers.two_digit.join(" · ")`). There is no indicator of historical performance or win frequency.

#### Technical Specifications & Required Changes
1. **Data Contract**:
   - API response returns a `heat_index` dictionary for each recommended number (2-digit, 3-digit, 6-digit).
   - Structure:
     ```json
     "heat_index": {
       "52": { "win_count": 5, "heat_level": "High", "period": "1_year" },
       "85": { "win_count": 3, "heat_level": "Medium", "period": "1_year" },
       "142": { "win_count": 1, "heat_level": "Low", "period": "1_year" }
     }
     ```
2. **Visual UI Design (`HeatIndexBadge` & Heatmap Display)**:
   - For each recommended number, display a **Heat Index Badge**:
     - 🔥 **High Heat (≥ 4 wins)**: Red/Gold gradient badge with animated glow (`🔥 ออกแล้ว 5 ครั้ง ในรอบ 1 ปี (ความร้อนสูง)`).
     - ⚡ **Medium Heat (2-3 wins)**: Warm Amber badge (`⚡ ออกแล้ว 3 ครั้ง ในรอบ 1 ปี (ความร้อนปานกลาง)`).
     - ❄️ **Cool / Unique (0-1 win)**: Cyan/Purple badge (`❄️ ออกแล้ว 1 ครั้ง ในรอบ 1 ปี (เลขซุ่มงวดนี้)`).
   - **Progress Bar / Heat Scale**: Mini progress bar showing relative frequency (e.g., 5/10 scale).

---

### R4: UI Display for Divination Transparency (Origin & Source Breakdown)

#### Current State Analysis
- `app.jsx` provides an overall text paragraph synthesis, but lacks line-item transparency explaining how specific recommended numbers were generated.

#### Technical Specifications & Required Changes
1. **Data Contract**:
   - API response includes `number_origins` mapping each recommended number to its exact derivation source.
   - Structure:
     ```json
     "number_origins": {
       "52": "ถอดจากเลขฐาน 4 มหาภูติ ผสมไพ่ทาโรต์ใบที่ 3 (The High Priestess)",
       "85": "ถอดจากลัคนาราศีสิงห์ (ไทย) ร่วมกับสถิติหวยออกซ้ำ 5 ครั้ง",
       "142": "ถอดจากเรือนโภคา-ธนัง เลข 7 ตัว 9 ฐาน และไพ่ทาโรต์ใบที่ 10 (The Hermit)"
     }
     ```
2. **Visual UI Design (`TransparencyCard` & Origin Tags)**:
   - Position origin details directly underneath or beside each recommended number card.
   - UI Layout:
     ```
     +-----------------------------------------------------------+
     | 🎯 เลข 2 ตัว:  [ 52 ]                                      |
     |  🔥 Heat Index: ออกแล้ว 5 ครั้ง ในรอบ 1 ปี (ความร้อนสูง)       |
     |  📍 ที่มาคำทำนาย: ถอดจากเลขฐาน 4 มหาภูติ ผสมไพ่ทาโรต์ใบที่ 3    |
     +-----------------------------------------------------------+
     ```
   - Uses subtle glassmorphic container, location pin icon 📍, and muted accent text for readability.

---

## 3. Frontend Component Architecture & State Flow

```
[ App Container (app.jsx / app.tsx) ]
 ├── Intake View (State: !results)
 │    ├── IntakeForm Component
 │    │    ├── Full Name Input
 │    │    ├── Birth Date Picker
 │    │    └── Birth Time Picker
 │    └── TarotSelection Component
 │         ├── Card Counter Badge (Selected X / 10)
 │         ├── 78 Facedown Cards Grid (Click to toggle)
 │         └── Submit Button (Disabled until X === 10)
 └── Results View (State: results)
      ├── LunarOutputCard Component (Auto-calculated Day/Month/Year)
      ├── TarotSpreadResults Component (10-Card Celtic Cross View)
      ├── RecommendedNumbersCard Component
      │    ├── Number Chips (2-Digit, 3-Digit, 6-Digit)
      │    ├── HeatIndexBadge Component (Historical Win Frequency)
      │    └── TransparencyOrigin Component (Derivation Breakdown)
      ├── OracleSynthesisCard Component (Synthesis Paragraph)
      └── Reset Button ("วิเคราะห์ดวงชะตาใหม่")
```

---

## 4. API Contract & Integration Specifications

### 4.1 POST `/api/divine` Request Payload
```json
{
  "full_name": "สมชาย ดวงดี",
  "birth_date": "1995-08-15",
  "birth_time": "14:30",
  "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
}
```

### 4.2 POST `/api/divine` Response Schema
```json
{
  "thai_lunar_calendar": {
    "day_of_week_th": "วันอังคาร",
    "lunar_month_th": "เดือน 9",
    "zodiac_year_th": "ปีกุน",
    "cutoff_rule_applied": "06:00 น."
  },
  "tarot": {
    "spread": [
      {
        "position_index": 1,
        "position_name": "สถานการณ์ปัจจุบัน",
        "card_id": 0,
        "card_name": "The Fool",
        "is_reversed": false
      }
    ]
  },
  "recommended_numbers": {
    "two_digit": ["52", "85"],
    "three_digit": ["142", "525"],
    "six_digit": ["811852"]
  },
  "heat_index": {
    "52": { "win_count": 5, "level": "High" },
    "85": { "win_count": 3, "level": "Medium" },
    "142": { "win_count": 1, "level": "Low" }
  },
  "number_origins": {
    "52": "ถอดจากเลขฐาน 4 มหาภูติ ผสมไพ่ทาโรต์ใบที่ 3 (The High Priestess)",
    "85": "ถอดจากลัคนาราศีสิงห์ (ไทย) ร่วมกับสถิติหวยออกซ้ำ 5 ครั้ง",
    "142": "ถอดจากเรือนโภคา-ธนัง เลข 7 ตัว 9 ฐาน และไพ่ทาโรต์ใบที่ 10 (The Hermit)"
  },
  "synthesis": "ชะตาชีวิตของคุณอยู่ในเกณฑ์ดี มีดาวพฤหัสบดีส่งเสริม...",
  "disclaimer": "คำทำนายนี้เป็นเพียงความเชื่อส่วนบุคคล โปรดใช้วิจารณญาณ"
}
```

---

## 5. Verification Method & Test Plan

1. **Unit Testing (`vitest` + React Testing Library)**:
   - `IntakeForm.test.tsx`: Verify `birth_time` input presence, absence of manual lunar dropdowns, and button disabled state when card count < 10.
   - `TarotSpread.test.tsx`: Verify 78-card rendering, selection card counter `เลือกไพ่แล้ว X / 10 ใบ`, card toggle state, and selection cap at 10.
   - `RecommendedNumbers.test.tsx`: Verify rendering of 2-digit, 3-digit, 6-digit numbers, Heat Index badges (`win_count`), and Transparency origin breakdown text.
2. **End-to-End Testing (`pytest` + FastAPI `TestClient`)**:
   - Execute `pytest e2e_tests/test_e2e_full_stack.py` to confirm API schema compliance for `birth_time`, `selected_tarot_cards`, `heat_index`, and `number_origins`.
