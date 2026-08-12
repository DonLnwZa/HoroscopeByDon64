# Handoff Report — Explorer 2 (Milestone M2: R3, R4 UI Features & CSS Styling)

## 1. Observation

### Mandatory Documents Read
1. `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md`
2. `e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md`
3. `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m2_frontend\SCOPE.md`

### Source Files & Line Numbers Inspected
- `omni_oracle_app/frontend/app.jsx` (Lines 1–141):
  - Line 119–123: Currently renders recommended lucky numbers as plain dot-separated strings:
    ```jsx
    <div className="number-display gold-text">
        {results.lucky_numbers.two_digit.join(" · ")}
    </div>
    <h3>เลข 3 ตัว: {results.lucky_numbers.three_digit.join(" · ")}</h3>
    <h3>เลข 6 ตัว: {results.lucky_numbers.six_digit.join(" · ")}</h3>
    ```
  - Currently does NOT display Heat Index badges (R3) or Divination Transparency provenance tags (R4).
- `omni_oracle_app/frontend/styles.css` (Lines 1–168):
  - Contains basic glassmorphism card styling (`.glass-card`), gold text (`.gold-text`), button styling (`.btn-primary`), and simple form grid (`.form-grid`).
  - Lacks CSS rules for the 78-card Tarot grid (`.tarot-grid`), card selection counter (`.card-counter`), Heat Index badges (`.heat-badge`), origin tags (`.origin-tag`), and structured number result rows (`.number-card-row`).
- `omni_oracle_app/backend/app.py` (Lines 111–128):
  - Returns `/api/divine` payload containing `heat_index` and `number_origins`:
    ```json
    {
      "status": "success",
      "chart": { ... },
      "lucky_numbers": {
        "two_digit": ["15", "84"],
        "three_digit": ["485", "792"],
        "six_digit": ["485792"]
      },
      "heat_index": {
        "two_digit": [{"number": "15", "win_count": 3, "level": "HOT"}, {"number": "84", "win_count": 1, "level": "WARM"}],
        "three_digit": [{"number": "485", "win_count": 0, "level": "COLD"}, {"number": "792", "win_count": 2, "level": "HOT"}],
        "six_digit": [{"number": "485792", "win_count": 0, "level": "COLD"}]
      },
      "number_origins": {
        "15": ["Mahabote: Thanang (1) + Phoka (5)", "Thai Astrology: Lagna Lord 1"],
        "84": ["Tarot Card #3: The Empress", "Numerology 7x9: Base 4"],
        "485": ["Combined: Lagna 4 + Mahabote 85"],
        "792": ["Tarot Card #1: The Magician + Numerology 792"],
        "485792": ["Synthesis of Top Engine Predictions"]
      }
    }
    ```
- `omni_oracle_app/backend/app/engines/lottery_stats.py` (Lines 58–108):
  - Computes `win_count` across 24 historical draws and maps:
    - `win_count >= 2`: `HOT`
    - `win_count == 1`: `WARM`
    - `win_count == 0`: `COLD`
- `omni_oracle_app/backend/app/engines/number_recommender.py` (Lines 59–99):
  - Generates list of strings describing provenance for each recommended number string.

---

## 2. Logic Chain

### Step 1: Mapping R3 (Heat Index Badges) to Backend Response Contract
Backend `/api/divine` payload provides `results.heat_index[category]` where `category` is `"two_digit"`, `"three_digit"`, or `"six_digit"`.
Each item contains `{ "number": "...", "win_count": N, "level": "HOT" | "WARM" | "COLD" }`.

Level mapping specification:
1. **HOT**: Icon `🔥`, Text `🔥 ร้อนแรง (ชนะ ${win_count} ครั้งใน 1 ปี)`, Badge Class `heat-badge hot`
2. **WARM**: Icon `⚡`, Text `⚡ ปานกลาง (ชนะ ${win_count} ครั้งใน 1 ปี)`, Badge Class `heat-badge warm`
3. **COLD**: Icon `❄️`, Text `❄️ หายาก (ชนะ ${win_count} ครั้งใน 1 ปี)`, Badge Class `heat-badge cold`

### Step 2: Mapping R4 (Divination Transparency Tags) to Backend Response Contract
Backend `/api/divine` payload provides `results.number_origins[numStr]` mapping number string to list of origin descriptions.

Rendering specification:
- Prefix label: `📍 ที่มา:`
- For each string description in `origins` array, render a translucent chip tag (`.origin-tag`).
- Example output: `📍 ที่มา: [Mahabote: Thanang (1) + Phoka (5)] [Thai Astrology: Lagna Lord 1]`

### Step 3: Redesigning Number Results Display in `app.jsx`
Instead of plain text `.join(" · ")`, lucky numbers are displayed inside structured sub-cards (`.number-card-row`):
- Category Header (e.g. `🎯 เลข 2 ตัว (เลขเด็ดหลัก)`, `✨ เลข 3 ตัว`, `👑 เลข 6 ตัว (รางวัลที่ 1)`)
- Card for each number containing:
  1. Prominent number value (`.number-value`, 2rem+ gold font).
  2. Heat Index Badge (`.heat-badge`, R3).
  3. Divination Transparency Tags (`.origin-tags-group`, R4).

### Step 4: CSS Styling Specification for `styles.css`
1. **78 Tarot Grid (`.tarot-grid`)**:
   - `display: grid; grid-template-columns: repeat(auto-fill, minmax(55px, 1fr)); gap: 8px;`
   - Scrollable container with `max-height: 360px; overflow-y: auto;` and custom webkit scrollbar.
   - Facedown cards: aspect ratio `2/3`, gradient background `#2a0845` to `#6441A5`, golden border.
   - Hover state: `transform: translateY(-4px) scale(1.05); border-color: #ffd700; shadow`.
   - Selected state (`.selected`): gradient `#daa520` to `#ffd700`, text color `#1a0533`, bright white/gold border, box shadow glow `0 0 15px rgba(255, 215, 0, 0.8)`.
   - Disabled state (`.disabled`): opacity `0.4`, `filter: grayscale(60%)`, `cursor: not-allowed`.
2. **Card Counter (`.card-counter`)**:
   - Translucent glassmorphism pill showing `เลือกไพ่แล้ว X / 10 ใบ`.
   - Highlight state when `X === 10`: border color `#40c057`, background `rgba(64, 192, 87, 0.15)`, text `✓ เลือกครบ 10 ใบแล้ว`.
3. **Heat Index Badges (`.heat-badge`)**:
   - Translucent pill badges (`border-radius: 20px`, `padding: 4px 10px`, `font-size: 0.82rem`).
   - `.heat-badge.hot`: background `rgba(255, 75, 43, 0.2)`, border `1px solid rgba(255, 75, 43, 0.6)`, text `#ff6b4a`, glow shadow.
   - `.heat-badge.warm`: background `rgba(255, 215, 0, 0.2)`, border `1px solid rgba(255, 215, 0, 0.6)`, text `#ffd700`, glow shadow.
   - `.heat-badge.cold`: background `rgba(0, 191, 255, 0.15)`, border `1px solid rgba(0, 191, 255, 0.5)`, text `#70d6ff`, glow shadow.
4. **Transparency Tags (`.origin-tag`)**:
   - Sub-card pill chips with italicized font (`font-size: 0.8rem`), background `rgba(255, 255, 255, 0.06)`, border `1px solid rgba(255, 215, 0, 0.25)`.
5. **Number Display Cards (`.number-card-row`)**:
   - Flex container with glassmorphism background `rgba(255, 255, 255, 0.04)`, border `1px solid rgba(255, 215, 0, 0.2)`, border-radius `12px`, padding `1rem`.

---

## 3. Caveats

- **API Fallback Safety**: Frontend JSX must safely handle missing or empty `heat_index` or `number_origins` fields (using optional chaining `results?.heat_index?.[category]`) so old API responses or incomplete payloads do not break rendering.
- **Vitest Prop Contract**: Frontend unit tests in `__tests__/RecommendedNumbers.test.tsx` pass props named `two_digits`, `three_digits`, `six_digits` rather than `two_digit`, `three_digit`, `six_digit`. Components in `app.jsx` should accept both property names for seamless compatibility.

---

## 4. Conclusion & Implementation Plan

### Step-by-Step Implementation Plan for M2 Frontend Upgrade (R3, R4, CSS)

#### Step 1: Add Helper Functions for R3 & R4 in `app.jsx`
```jsx
// R3 Heat Index Badge Helper
const renderHeatBadge = (category, numStr) => {
    if (!results?.heat_index?.[category]) return null;
    const item = results.heat_index[category].find(h => String(h.number) === String(numStr));
    if (!item) return null;

    let badgeClass = "heat-badge cold";
    let text = `❄️ หายาก (ชนะ ${item.win_count} ครั้ง)`;
    if (item.level === "HOT") {
        badgeClass = "heat-badge hot";
        text = `🔥 ร้อนแรง (ชนะ ${item.win_count} ครั้ง)`;
    } else if (item.level === "WARM") {
        badgeClass = "heat-badge warm";
        text = `⚡ ปานกลาง (ชนะ ${item.win_count} ครั้ง)`;
    }

    return (
        <span className={badgeClass} title={`สถิติผลหวยย้อนหลัง 1 ปี: ชนะ ${item.win_count} ครั้ง`}>
            {text}
        </span>
    );
};

// R4 Divination Transparency Tags Helper
const renderOrigins = (numStr) => {
    const origins = results?.number_origins?.[numStr];
    if (!origins || origins.length === 0) return null;
    return (
        <div className="origin-tags-group">
            <span className="origin-label">📍 ที่มา:</span>
            {origins.map((org, i) => (
                <span key={i} className="origin-tag">
                    {org}
                </span>
            ))}
        </div>
    );
};
```

#### Step 2: Update Results Markup in `app.jsx`
Replace lines 118–124 of `app.jsx` with structured number display rows:
```jsx
<h2 className="gold-text">🎯 เลขเด็ดมงคลของคุณงวดนี้</h2>

{/* 2-Digit Numbers */}
<div className="number-section">
    <h3 className="section-title">เลข 2 ตัว (เลขเด็ดหลัก)</h3>
    <div className="number-cards-grid">
        {(results.lucky_numbers?.two_digit || results.lucky_numbers?.two_digits || []).map((num, idx) => (
            <div key={idx} className="number-card-row">
                <div className="number-card-header">
                    <span className="number-value gold-text">{num}</span>
                    {renderHeatBadge("two_digit", num)}
                </div>
                {renderOrigins(num)}
            </div>
        ))}
    </div>
</div>

{/* 3-Digit Numbers */}
<div className="number-section" style={{marginTop: '1.5rem'}}>
    <h3 className="section-title">เลข 3 ตัว</h3>
    <div className="number-cards-grid">
        {(results.lucky_numbers?.three_digit || results.lucky_numbers?.three_digits || []).map((num, idx) => (
            <div key={idx} className="number-card-row">
                <div className="number-card-header">
                    <span className="number-value gold-text">{num}</span>
                    {renderHeatBadge("three_digit", num)}
                </div>
                {renderOrigins(num)}
            </div>
        ))}
    </div>
</div>

{/* 6-Digit Numbers */}
<div className="number-section" style={{marginTop: '1.5rem'}}>
    <h3 className="section-title">เลข 6 ตัว (รางวัลที่ 1)</h3>
    <div className="number-cards-grid">
        {(results.lucky_numbers?.six_digit || results.lucky_numbers?.six_digits || []).map((num, idx) => (
            <div key={idx} className="number-card-row">
                <div className="number-card-header">
                    <span className="number-value gold-text" style={{fontSize: '2rem'}}>{num}</span>
                    {renderHeatBadge("six_digit", num)}
                </div>
                {renderOrigins(num)}
            </div>
        ))}
    </div>
</div>
```

#### Step 3: Append CSS Rules to `omni_oracle_app/frontend/styles.css`
Append the following stylesheet rules to `styles.css`:

```css
/* ----------------------------------------------------
   Tarot 78 Card Grid & Selection Counter (R2)
   ---------------------------------------------------- */
.tarot-section {
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
}

.tarot-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.card-counter {
    font-size: 0.95rem;
    font-weight: bold;
    padding: 6px 14px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid var(--glass-border);
    color: var(--accent-gold);
    transition: all 0.3s ease;
}

.card-counter.complete {
    background: rgba(64, 192, 87, 0.15);
    border-color: rgba(64, 192, 87, 0.6);
    color: #40c057;
}

.tarot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(55px, 1fr));
    gap: 8px;
    max-height: 320px;
    overflow-y: auto;
    padding: 12px;
    background: rgba(0, 0, 0, 0.25);
    border-radius: 12px;
    border: 1px solid var(--glass-border);
}

/* Custom Scrollbar for Tarot Grid */
.tarot-grid::-webkit-scrollbar {
    width: 6px;
}
.tarot-grid::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 10px;
}
.tarot-grid::-webkit-scrollbar-thumb {
    background: var(--accent-gold-dark);
    border-radius: 10px;
}

.tarot-card-item {
    aspect-ratio: 2 / 3;
    background: linear-gradient(135deg, #2a0845, #6441A5);
    border: 1px solid rgba(255, 215, 0, 0.3);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: bold;
    color: white;
    cursor: pointer;
    user-select: none;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    position: relative;
}

.tarot-card-item:hover:not(.disabled) {
    transform: translateY(-4px) scale(1.05);
    border-color: var(--accent-gold);
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.35);
}

.tarot-card-item.selected {
    background: linear-gradient(135deg, #daa520, #ffd700);
    color: #1a0533;
    border: 2px solid #ffffff;
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.8);
    transform: translateY(-2px) scale(1.08);
}

.tarot-card-item.disabled:not(.selected) {
    opacity: 0.4;
    filter: grayscale(60%);
    cursor: not-allowed;
}

/* ----------------------------------------------------
   Number Result Display Cards, R3 Heat Index & R4 Transparency
   ---------------------------------------------------- */
.number-section {
    text-align: left;
}

.section-title {
    font-size: 1.1rem;
    color: var(--accent-gold);
    margin-bottom: 0.75rem;
    border-bottom: 1px solid rgba(255, 215, 0, 0.2);
    padding-bottom: 0.4rem;
}

.number-cards-grid {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.number-card-row {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 215, 0, 0.2);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: background 0.3s ease;
}

.number-card-row:hover {
    background: rgba(255, 255, 255, 0.07);
    border-color: rgba(255, 215, 0, 0.4);
}

.number-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}

.number-value {
    font-size: 2.4rem;
    font-weight: bold;
    letter-spacing: 3px;
    line-height: 1;
}

/* R3 Heat Index Badges */
.heat-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    backdrop-filter: blur(4px);
    transition: all 0.2s ease;
}

.heat-badge.hot {
    background: rgba(255, 75, 43, 0.2);
    border: 1px solid rgba(255, 75, 43, 0.6);
    color: #ff6b4a;
    box-shadow: 0 0 10px rgba(255, 75, 43, 0.25);
}

.heat-badge.warm {
    background: rgba(255, 215, 0, 0.2);
    border: 1px solid rgba(255, 215, 0, 0.6);
    color: #ffd700;
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.25);
}

.heat-badge.cold {
    background: rgba(0, 191, 255, 0.15);
    border: 1px solid rgba(0, 191, 255, 0.5);
    color: #70d6ff;
    box-shadow: 0 0 10px rgba(0, 191, 255, 0.2);
}

/* R4 Divination Transparency Tags */
.origin-tags-group {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    margin-top: 4px;
}

.origin-label {
    font-size: 0.82rem;
    color: rgba(255, 255, 255, 0.7);
    font-weight: bold;
}

.origin-tag {
    display: inline-flex;
    align-items: center;
    padding: 3px 8px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 215, 0, 0.25);
    border-radius: 6px;
    font-size: 0.8rem;
    color: #e0e0e0;
    font-style: italic;
}
```

---

## 5. Verification Method

### 1. Static Verification
- Inspect `omni_oracle_app/frontend/app.jsx` to verify presence of `renderHeatBadge` and `renderOrigins` helpers and structured `.number-card-row` output.
- Inspect `omni_oracle_app/frontend/styles.css` to verify presence of `.tarot-grid`, `.card-counter`, `.heat-badge`, `.origin-tag`, `.number-card-row` selectors.

### 2. Frontend Unit Tests
Execute Vitest test suite for frontend components:
```bash
npx vitest run omni_oracle_app/frontend/__tests__/RecommendedNumbers.test.tsx
```

### 3. E2E Integration Inspection
Start backend server:
```bash
python omni_oracle_app/backend/app.py
```
Submit form with 10 Tarot cards selected, inspect results UI, and confirm:
1. Heat Index badges display with 🔥, ⚡, or ❄️ and exact win count.
2. Transparency tags display with 📍 and origin breakdown.
3. Tarot grid supports 78 card selection with counter tracking `X / 10`.
