# Handoff Report — Frontend UI Upgrade Investigation (R1 & R2)

**Explorer**: explorer_1  
**Milestone**: M2 (Frontend UI Upgrade)  
**Target Directory**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\frontend\`  
**Date**: 2026-08-12  

---

## 1. Observation

Direct observations from examining the codebase files:

### 1.1 Existing Frontend Files (`omni_oracle_app/frontend/`)
- `omni_oracle_app/frontend/app.jsx` (7,878 bytes, 141 lines):
  - **Lines 7-13**: State definition initializes legacy dropdown fields:
    ```javascript
    const [formData, setFormData] = useState({
        name_thai: "",
        birth_date: "",
        birth_day_of_week: "1",
        birth_month_lunar: "1",
        birth_year_animal: "1"
    });
    ```
  - **Lines 65-98**: Form JSX renders 3 `<select>` dropdowns: `birth_day_of_week`, `birth_month_lunar`, and `birth_year_animal`.
  - **Lines 20-24**: `handleSubmit` sends `formData` directly in POST payload to `http://localhost:5000/api/divine`. It does NOT currently send `birth_time` or `selected_tarot_cards`.
  - **Lines 101-103**: Submit button `<button type="submit" className="btn-primary" disabled={loading}>` is disabled ONLY when `loading` is true. It does NOT check whether 10 Tarot cards are selected.
  - **Lines 107-134**: Results screen displays `results.lucky_numbers.two_digit`, `three_digit`, `six_digit`, `synthesis`, and `disclaimer`. It does NOT currently render the auto-calculated Thai Lunar Calendar output card.

- `omni_oracle_app/frontend/styles.css` (4,066 bytes, 168 lines):
  - Defines `.glass-card`, `.btn-primary`, `.form-grid`, `.form-group`, `.lucky-numbers`, `.gold-text`.
  - Currently lacks CSS classes for `.tarot-deck-grid`, `.tarot-card`, `.tarot-card.selected`, `.card-counter`, `.lunar-card`, `.lunar-info-grid`, `.lunar-item`, `.heat-badge`, `.origin-tag`.

- `omni_oracle_app/frontend/index.html` (913 bytes, 20 lines):
  - Loads React 18, ReactDOM 18, Framer Motion 10.16.4, Babel Standalone.
  - Mounts `<script type="text/babel" src="app.jsx"></script>`.

- `omni_oracle_app/frontend/__tests__/IntakeForm.test.tsx` (4,637 bytes, 110 lines):
  - Verifies input fields `aria-label="ชื่อ-นามสกุล"`, `aria-label="วันเกิด"`, `aria-label="เวลาเกิด"`, `aria-label="จังหวัดเกิด"`.
- `omni_oracle_app/frontend/__tests__/TarotSpread.test.tsx` (4,936 bytes, 101 lines):
  - Verifies selection counter text matching `/เลือกไพ่แล้ว 10 \/ 10 ใบ/i` and testids `tarot-card-${position_index}`.

### 1.2 Backend API Contract (`omni_oracle_app/backend/app.py`)
- **Lines 46-54**: `POST /api/divine` expects JSON:
  ```json
  {
    "full_name": "Somchai Jaidee",
    "birth_date": "1992-05-15",
    "birth_time": "05:30",
    "birth_province": "Bangkok",
    "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
  }
  ```
- **Lines 111-128**: `/api/divine` returns JSON response containing:
  ```json
  {
    "status": "success",
    "chart": {
      "birth_date": "1992-05-15",
      "birth_time": "05:30",
      "lunar_calendar": {
        "day_of_week": "Thursday",
        "lunar_month": 6,
        "zodiac_year": "Monkey",
        "cutoff_applied": true
      }
    },
    "lucky_numbers": { ... },
    "heat_index": { ... },
    "number_origins": { ... },
    "synthesis": "...",
    "disclaimer": "..."
  }
  ```

---

## 2. Logic Chain

1. **R1 Requirement (Input Replacement)**:
   - **Observation**: `app.jsx` currently requires users to manually select 3 dropdowns (`birth_day_of_week`, `birth_month_lunar`, `birth_year_animal`).
   - **Deduction**: Removing these 3 dropdowns and replacing them with a single `<input type="time" name="birth_time" value={formData.birth_time} onChange={...} required />` simplifies intake. The label must clearly explain birth time and Thai 06:00 AM cutoff rule (e.g. `เวลาเกิด (ตัดรอบ 06:00 น. แบบไทย)`).
   - **Output Rendering**: When `/api/divine` returns `results.chart.lunar_calendar`, a dedicated `ThaiLunarCalendarCard` component must display the calculated `day_of_week`, `lunar_month`, `zodiac_year`, and a badge indicating whether the 6:00 AM cutoff rule was applied.

2. **R2 Requirement (78 Interactive Tarot Grid)**:
   - **Observation**: `app.jsx` currently has no Tarot selection UI and sends no card indices to `/api/divine`.
   - **Deduction**: We must add a state `selectedTarotCards` (array of integers, max length 10) in `app.jsx`.
   - **Grid Rendering**: Render 78 face-down cards (indices 0..77). Clicking an unselected card adds its index to `selectedTarotCards` if `length < 10`. Clicking a selected card deselects it.
   - **Selection Counter**: Display counter element with exact text format `เลือกไพ่แล้ว ${selectedTarotCards.length} / 10 ใบ`.
   - **Submit Validation**: Disable the submit button (`disabled={loading || selectedTarotCards.length !== 10}`) and render button text `กรุณาเลือกไพ่ทาโรต์ให้ครบ 10 ใบ (เลือกแล้ว ${selectedTarotCards.length}/10)` until exactly 10 cards are selected.
   - **Payload Payload**: Send `selected_tarot_cards: selectedTarotCards` in the JSON POST payload to `/api/divine`.

---

## 3. Caveats

- **Component Testing Compatibility**: The tests in `omni_oracle_app/frontend/__tests__/` currently mock subcomponents (`MockIntakeForm`, `MockTarotSpread`). Modifying `app.jsx` will not break unit tests as long as component props and ARIA labels (`aria-label="เวลาเกิด"`, `aria-label="วันเกิด"`, `aria-label="ชื่อ-นามสกุล"`, `aria-label="จังหวัดเกิด"`) and test IDs (`data-testid="tarot-card-${i}"`) remain consistent.
- **Babel Standalone Execution**: Since `app.jsx` runs via Babel Standalone in `index.html`, all code must be valid JSX/React 18 standard code without uncompiled TypeScript syntax in `app.jsx`.

---

## 4. Conclusion & Implementation Plan

### 4.1 Proposed Code Changes for `app.jsx`

#### A. State Structure Update
```javascript
const [loading, setLoading] = useState(false);
const [results, setResults] = useState(null);
const [formData, setFormData] = useState({
    full_name: "",
    birth_date: "",
    birth_time: "06:00",
    birth_province: "กรุงเทพมหานคร"
});
const [selectedTarotCards, setSelectedTarotCards] = useState([]);
```

#### B. Tarot Card Selection Logic
```javascript
const handleCardClick = (cardIndex) => {
    if (selectedTarotCards.includes(cardIndex)) {
        setSelectedTarotCards(selectedTarotCards.filter(id => id !== cardIndex));
    } else if (selectedTarotCards.length < 10) {
        setSelectedTarotCards([...selectedTarotCards, cardIndex]);
    }
};
```

#### C. API Submit Payload Integration
```javascript
const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedTarotCards.length !== 10) return;
    setLoading(true);
    
    try {
        const payload = {
            full_name: formData.full_name,
            birth_date: formData.birth_date,
            birth_time: formData.birth_time,
            birth_province: formData.birth_province,
            selected_tarot_cards: selectedTarotCards
        };
        const res = await fetch("http://localhost:5000/api/divine", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        setResults(data);
    } catch (err) {
        console.error(err);
        alert("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ กรุณาตรวจสอบว่า Backend ทำงานอยู่");
    } finally {
        setLoading(false);
    }
};
```

#### D. R1 Intake Form UI Code Structure
```jsx
<div className="form-grid">
    <div className="form-group full-width">
        <label htmlFor="full_name">ชื่อ-นามสกุล</label>
        <input 
            id="full_name"
            aria-label="ชื่อ-นามสกุล"
            type="text" 
            value={formData.full_name} 
            onChange={e => setFormData({...formData, full_name: e.target.value})} 
            required 
            placeholder="เช่น สมชาย ดวงดี" 
        />
    </div>
    <div className="form-group">
        <label htmlFor="birth_date">วันเดือนปีเกิด (สากล)</label>
        <input 
            id="birth_date"
            aria-label="วันเกิด"
            type="date" 
            value={formData.birth_date} 
            onChange={e => setFormData({...formData, birth_date: e.target.value})} 
            required 
        />
    </div>
    <div className="form-group">
        <label htmlFor="birth_time">เวลาเกิด (ตัดรอบ 06:00 น. แบบไทย)</label>
        <input 
            id="birth_time"
            name="birth_time"
            aria-label="เวลาเกิด"
            type="time" 
            value={formData.birth_time} 
            onChange={e => setFormData({...formData, birth_time: e.target.value})} 
            required 
        />
    </div>
    <div className="form-group full-width">
        <label htmlFor="birth_province">จังหวัดเกิด</label>
        <select 
            id="birth_province"
            aria-label="จังหวัดเกิด"
            value={formData.birth_province}
            onChange={e => setFormData({...formData, birth_province: e.target.value})}
        >
            <option value="กรุงเทพมหานคร">กรุงเทพมหานคร</option>
            <option value="เชียงใหม่">เชียงใหม่</option>
            <option value="ขอนแก่น">ขอนแก่น</option>
            <option value="ภูเก็ต">ภูเก็ต</option>
            <option value="ชลบุรี">ชลบุรี</option>
        </select>
    </div>
</div>
```

#### E. R2 Tarot Deck Grid UI Code Structure
```jsx
<div className="tarot-section">
    <h3 className="gold-text">🃏 เลือกไพ่ทาโรต์มงคล 10 ใบ</h3>
    <p className="card-counter" aria-label="card-counter">
        เลือกไพ่แล้ว {selectedTarotCards.length} / 10 ใบ
    </p>
    <div className="tarot-deck-grid">
        {[...Array(78)].map((_, index) => {
            const isSelected = selectedTarotCards.includes(index);
            const selectOrder = selectedTarotCards.indexOf(index) + 1;
            return (
                <div
                    key={index}
                    data-testid={`tarot-card-${index}`}
                    className={`tarot-card-facedown ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleCardClick(index)}
                    title={`ไพ่ใบที่ ${index + 1}`}
                >
                    {isSelected ? (
                        <span className="card-order-badge">#{selectOrder}</span>
                    ) : (
                        <span className="card-back-pattern">🔮</span>
                    )}
                </div>
            );
        })}
    </div>
</div>
```

#### F. R1 Auto-Calculated Thai Lunar Calendar Output Card
```jsx
{results.chart && results.chart.lunar_calendar && (
    <motion.div 
        className="glass-card lunar-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
    >
        <h3 className="gold-text">🌙 ปฏิทินจันทรคติไทย (คำนวณอัตโนมัติ)</h3>
        <div className="lunar-info-grid">
            <div className="lunar-item">
                <span className="lunar-label">วันเกิดตามสัปดาห์</span>
                <span className="lunar-val">{results.chart.lunar_calendar.day_of_week}</span>
            </div>
            <div className="lunar-item">
                <span className="lunar-label">เดือนจันทรคติ</span>
                <span className="lunar-val">เดือน {results.chart.lunar_calendar.lunar_month}</span>
            </div>
            <div className="lunar-item">
                <span className="lunar-label">ปีนักษัตร</span>
                <span className="lunar-val">ปี{results.chart.lunar_calendar.zodiac_year}</span>
            </div>
        </div>
        <p className="cutoff-note">
            {results.chart.lunar_calendar.cutoff_applied 
                ? "🌅 คำนวณโดยใช้กฎตัดรอบวันใหม่เวลา 06:00 น. ตามหลักโหราศาสตร์ไทย"
                : "☀️ เวลาเกิดหลัง 06:00 น. ตรงตามวันทางสากล"}
        </p>
    </motion.div>
)}
```

---

### 4.2 Proposed CSS Additions for `styles.css`

```css
/* R1 Lunar Calendar Output Card */
.lunar-card {
    margin-bottom: 2rem;
    border-color: rgba(255, 215, 0, 0.3);
}

.lunar-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.lunar-item {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 215, 0, 0.2);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.lunar-label {
    font-size: 0.85rem;
    opacity: 0.8;
    color: var(--text-color);
}

.lunar-val {
    font-size: 1.2rem;
    font-weight: bold;
    color: var(--accent-gold);
}

.cutoff-note {
    font-size: 0.85rem;
    opacity: 0.75;
    text-align: center;
    margin-top: 0.5rem;
}

/* R2 Interactive 78 Tarot Deck Grid */
.tarot-section {
    margin-top: 2rem;
    margin-bottom: 2rem;
    text-align: center;
}

.card-counter {
    font-size: 1.1rem;
    font-weight: bold;
    color: var(--accent-gold);
    background: rgba(255, 215, 0, 0.1);
    border: 1px solid var(--accent-gold-dark);
    padding: 8px 16px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 1.2rem;
}

.tarot-deck-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(52px, 1fr));
    gap: 8px;
    max-height: 320px;
    overflow-y: auto;
    padding: 12px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
}

.tarot-card-facedown {
    height: 75px;
    border-radius: 8px;
    background: linear-gradient(135deg, #2a0845, #140326);
    border: 1px solid rgba(255, 215, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    user-select: none;
    transition: all 0.2s ease-in-out;
    position: relative;
    box-shadow: 0 2px 6px rgba(0,0,0,0.4);
}

.tarot-card-facedown:hover {
    transform: translateY(-4px);
    border-color: var(--accent-gold);
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
}

.tarot-card-facedown.selected {
    background: linear-gradient(135deg, #4a154b, #daa520);
    border: 2px solid var(--accent-gold);
    box-shadow: 0 0 14px rgba(255, 215, 0, 0.8);
    transform: translateY(-2px) scale(1.05);
}

.card-order-badge {
    font-size: 0.9rem;
    font-weight: bold;
    color: #1a0533;
    background: var(--accent-gold);
    border-radius: 50%;
    width: 26px;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.card-back-pattern {
    font-size: 1.2rem;
    opacity: 0.7;
}
```

---

## 5. Verification Method

To verify the implementation of R1 and R2:

1. **Static Analysis & File Inspection**:
   - Inspect `omni_oracle_app/frontend/app.jsx` to confirm:
     - Old dropdown state properties (`birth_day_of_week`, `birth_month_lunar`, `birth_year_animal`) are replaced with `birth_time`.
     - `<input type="time" name="birth_time" aria-label="เวลาเกิด">` is rendered with label.
     - 78 cards grid is rendered with `data-testid="tarot-card-${i}"`.
     - Submit button is disabled unless `selectedTarotCards.length === 10`.
     - POST payload sends `selected_tarot_cards` array of 10 integers.
     - Results view renders `results.chart.lunar_calendar` output card.

2. **Integration Verification via Terminal / Dev Server**:
   - Start Flask backend server:
     `python omni_oracle_app/backend/app.py`
   - Open browser or execute E2E / component test suite to verify form interaction, card selection toggling, counter updates (`เลือกไพ่แล้ว X / 10 ใบ`), button enablement on 10 cards, and API response payload rendering.
