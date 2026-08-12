# Technical Analysis & Design Report: Requirements R1 & R2 (Backend Engines & API Upgrade)

**Target Milestone**: M1 (Backend Engines & API Upgrade)  
**Author**: Explorer 1  
**Working Directory**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_backend\explorer_1\`  
**Date**: 2026-08-12  

---

## 1. Executive Summary

This report presents the architectural investigation and precise implementation designs for Requirements **R1 (Auto-Approximate Thai Lunar Calendar & 6:00 AM Cutoff)** and **R2 (Interactive Tarot Selected Cards Mapping)** within the Omni-Oracle backend application (`omni_oracle_app/backend/`).

Key Findings:
1. **R1 (Thai Lunar Calendar)**:
   - Existing codebase in `thai_astrology.py` computes planetary positions and Lagna but lacks the 6:00 AM Bangkok cutoff day-of-week shift, approximate Thai Lunar Month (1..12), and Thai Zodiac Year (1..12) calculations.
   - `numerology_7x9.py` currently accepts `day_of_week`, `thai_lunar_month`, and `thai_lunar_year` as parameters.
   - We design `calculate_thai_lunar_calendar(birth_date, birth_time)` to auto-derive these parameters using the 6:00 AM cutoff rule and return the exact JSON payload contract required for `chart.lunar_calendar`: `day_of_week`, `lunar_month`, `zodiac_year`, and `cutoff_applied`.

2. **R2 (Tarot Selection Mapping)**:
   - Existing `TarotEngine.draw_celtic_cross()` in `tarot.py` generates 10 random cards using CSPRNG (`secrets.randbelow`).
   - We design `draw_celtic_cross(selected_cards=None)` to accept an array of 10 card indices (`0..77`), validate them against range/length/uniqueness criteria, map them deterministically to the 10 Celtic Cross positions, and maintain backward compatibility when `selected_cards` is `None`.

No source code files were modified during this read-only investigation.

---

## 2. Existing Codebase Analysis

### 2.1 `omni_oracle_app/backend/app/engines/thai_astrology.py`
- **Current Role**: Calculates planetary longitudes, Lagna (Ascendant), houses (Whole Sign system), and planetary dignities (Ucc, Kaset, Nit, Pra, Normal) based on Gregorian birth date, birth time, and location coordinates.
- **Seams**:
  - `calculate_thai_astrology(birth_date: str, birth_time: str, birth_province: str)` -> returns `ThaiAstrologyResult`.
  - Calculates UTC time by subtracting 7 hours from ICT local time.
- **Gaps**: Does not compute Thai Lunar Month, Thai Zodiac Year, or the 6:00 AM day-of-week cutoff.

### 2.2 `omni_oracle_app/backend/app/engines/tarot.py`
- **Current Role**: Stores 78 Tarot card definitions (22 Major Arcana, 56 Minor Arcana) and 10 Celtic Cross position meanings.
- **Seams**:
  - `TarotEngine.__init__()`: Generates `self.deck` (78 card dicts with `id`, `name`, `type`, `meaning_upright`, `meaning_reversed`).
  - `draw_celtic_cross()`: Takes zero arguments. Shuffles `self.deck.copy()` and pops 10 random cards.
- **Gaps**: Cannot accept user-selected card indices from frontend payload (`selected_tarot_cards`).

### 2.3 `omni_oracle_app/backend/app.py`
- **Current Role**: Flask API server exposing `/api/health`, `/api/lottery/stats`, and `/api/divine`.
- **Current `/api/divine` behavior**:
  - Expects `birth_day_of_week`, `birth_month_lunar`, and `birth_year_animal` from request JSON body (or defaults to `1`).
  - Calls `tarot_engine.draw_celtic_cross()` with no arguments.
- **Gaps**: Needs to accept `birth_time` and `selected_tarot_cards`, invoke the auto-lunar calculation, pass derived lunar values to `numerology_7x9`, pass selected tarot card indices to `tarot_engine`, and return `chart.lunar_calendar`.

---

## 3. Detailed Design for R1: Auto Thai Lunar Calendar & 6am Cutoff

### 3.1 Domain Logic & Rules

1. **6:00 AM Bangkok Cutoff Rule**:
   - In Thai astrology, the astrological day begins at sunrise (~6:00 AM).
   - If `birth_time` < `06:00` (e.g. `05:30`), the birth is considered to occur on the **previous astrological day**.
   - `effective_date = birth_date - 1 day` if `birth_time < 06:00`, else `birth_date`.
   - `cutoff_applied = True` if `birth_time < 06:00`, else `False`.

2. **Thai Astrological Day of Week (1..7)**:
   - Derived from `effective_date.weekday()`:
     - Sunday = 1, Monday = 2, Tuesday = 3, Wednesday = 4, Thursday = 5, Friday = 6, Saturday = 7.
   - String representation: `"Sunday"`, `"Monday"`, `"Tuesday"`, `"Wednesday"`, `"Thursday"`, `"Friday"`, `"Saturday"`.

3. **Approximate Thai Lunar Month (1..12)**:
   - Thai Lunar Month 1 (เดือน 1 / เดือนอ้าย) begins around mid-November/December.
   - Approximation algorithm based on day of Gregorian month:
     - If `day >= 16`: `base_m = month + 1`
     - Else: `base_m = month`
     - `lunar_month = ((base_m) % 12) + 1` (Yields integer `1..12`).
   - Example:
     - May 15 (`month=5, day=15`): `lunar_month = (5 % 12) + 1 = 6` (เดือน 6).
     - Nov 20 (`month=11, day=20`): `lunar_month = (12 % 12) + 1 = 1` (เดือน 1 / อ้าย).

4. **Approximate Thai Zodiac Year (1..12)**:
   - 12 Zodiac Animals:
     1=Rat (ชวด), 2=Ox (ฉลู), 3=Tiger (ขาล), 4=Rabbit (เถาะ), 5=Dragon (มะโรง), 6=Snake (มะเส็ง), 7=Horse (มะเมีย), 8=Goat (มะแม), 9=Monkey (วอก), 10=Rooster (ระกา), 11=Dog (จอ), 12=Pig (กุน).
   - Songkran Boundary Rule: Traditional Thai zodiac year shifts on Songkran (April 13).
     - If `(effective_date.month, effective_date.day) < (4, 13)`: `zodiac_year_num = (((effective_date.year - 1 - 4) % 12) + 1)`
     - Else: `zodiac_year_num = (((effective_date.year - 4) % 12) + 1)`
   - String representation (English): `"Rat"`, `"Ox"`, `"Tiger"`, `"Rabbit"`, `"Dragon"`, `"Snake"`, `"Horse"`, `"Goat"`, `"Monkey"`, `"Rooster"`, `"Dog"`, `"Pig"`.

### 3.2 Target Data Model & JSON Contract

`chart.lunar_calendar` JSON object in `/api/divine` response:
```json
{
  "day_of_week": "Thursday",
  "lunar_month": 6,
  "zodiac_year": "Monkey",
  "cutoff_applied": true
}
```

### 3.3 Proposed Function Signature & Implementation

Add to `omni_oracle_app/backend/app/engines/thai_astrology.py`:

```python
class ThaiLunarCalendarResult(BaseModel):
    day_of_week: str          # "Sunday".."Saturday"
    day_of_week_num: int      # 1..7 (1=Sun, 2=Mon, ..., 7=Sat)
    lunar_month: int          # 1..12
    lunar_month_name_th: str   # "เดือน 6"
    zodiac_year: str          # "Monkey", "Rat", etc.
    zodiac_year_th: str       # "ปีวอก", "ปีชวด", etc.
    zodiac_year_num: int      # 1..12 (1=Rat..12=Pig)
    cutoff_applied: bool      # True if birth_time < 06:00

ENGLISH_DAY_NAMES = {1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday", 5: "Thursday", 6: "Friday", 7: "Saturday"}
THAI_DAY_NAMES = {1: "วันอาทิตย์", 2: "วันจันทร์", 3: "วันอังคาร", 4: "วันพุธ", 5: "วันพฤหัสบดี", 6: "วันศุกร์", 7: "วันเสาร์"}

ENGLISH_ZODIAC_NAMES = {1: "Rat", 2: "Ox", 3: "Tiger", 4: "Rabbit", 5: "Dragon", 6: "Snake", 7: "Horse", 8: "Goat", 9: "Monkey", 10: "Rooster", 11: "Dog", 12: "Pig"}
THAI_ZODIAC_NAMES = {1: "ปีชวด", 2: "ปีฉลู", 3: "ปีขาล", 4: "ปีเถาะ", 5: "ปีมะโรง", 6: "ปีมะเส็ง", 7: "ปีมะเมีย", 8: "ปีมะแม", 9: "ปีวอก", 10: "ปีระกา", 11: "ปีจอ", 12: "ปีกุน"}

def calculate_thai_lunar_calendar(
    birth_date: str,
    birth_time: str = "12:00"
) -> ThaiLunarCalendarResult:
    """
    Auto-calculates approximate Thai Lunar Calendar values from Gregorian birth_date and birth_time.
    Applies the Bangkok 06:00 AM cutoff rule for Thai day of week determination.
    """
    try:
        dt_date = datetime.strptime(birth_date.strip(), "%Y-%m-%d").date()
    except Exception as e:
        raise ValueError(f"Invalid birth_date '{birth_date}'. Expected format YYYY-MM-DD.") from e

    clean_time = birth_time.strip() if birth_time else "12:00"
    parts = clean_time.split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0

    # 6:00 AM Cutoff Rule
    if (hour, minute) < (6, 0):
        effective_date = dt_date - timedelta(days=1)
        cutoff_applied = True
    else:
        effective_date = dt_date
        cutoff_applied = False

    # Day of week (1=Sun..7=Sat)
    day_num = ((effective_date.weekday() + 1) % 7) + 1
    day_name_en = ENGLISH_DAY_NAMES[day_num]

    # Thai Lunar Month (1..12)
    m = effective_date.month
    d = effective_date.day
    base_m = m + 1 if d >= 16 else m
    lunar_month = ((base_m) % 12) + 1
    lunar_month_name_th = f"เดือน {lunar_month}"

    # Thai Zodiac Year (1..12)
    if (effective_date.month, effective_date.day) < (4, 13):
        zodiac_year_num = (((effective_date.year - 1 - 4) % 12) + 1)
    else:
        zodiac_year_num = (((effective_date.year - 4) % 12) + 1)

    zodiac_year_en = ENGLISH_ZODIAC_NAMES[zodiac_year_num]
    zodiac_year_th = THAI_ZODIAC_NAMES[zodiac_year_num]

    return ThaiLunarCalendarResult(
        day_of_week=day_name_en,
        day_of_week_num=day_num,
        lunar_month=lunar_month,
        lunar_month_name_th=lunar_month_name_th,
        zodiac_year=zodiac_year_en,
        zodiac_year_th=zodiac_year_th,
        zodiac_year_num=zodiac_year_num,
        cutoff_applied=cutoff_applied,
    )
```

---

## 4. Detailed Design for R2: Tarot Selected Cards Mapping

### 4.1 Domain Logic & Requirements

1. **Input Payload**: `selected_tarot_cards` array of 10 card indices (`0..77`).
2. **Validation Matrix**:
   - `selected_cards` must be a list/tuple.
   - `len(selected_cards)` must equal `10`.
   - Every element must be an `int` in range `0 <= card_idx <= 77`.
   - All 10 elements must be unique (no duplicate cards drawn).
   - If any validation fails, raise `ValueError` with clear message so `/api/divine` can respond with HTTP 400.
3. **Position Mapping**:
   - Element `selected_cards[i]` (where `i` = 0..9) maps to Celtic Cross Position `i`:
     - 0: สถานการณ์ปัจจุบัน
     - 1: สิ่งที่เข้ามาขัดขวางหรือส่งเสริม
     - 2: รากฐานของปัญหาหรืออดีตที่ผ่านมา
     - 3: อดีตที่เพิ่งผ่านพ้นไป
     - 4: เป้าหมายหรือสิ่งที่มุ่งหวัง
     - 5: อนาคตอันใกล้
     - 6: ตัวตนของผู้ถามในสถานการณ์นั้น
     - 7: สภาพแวดล้อมและบุคคลรอบข้าง
     - 8: ความหวังและความกลัว
     - 9: บทสรุปของสถานการณ์
4. **Reversal & Metadata**:
   - Keep `is_reversed = secrets.choice([True, False])`.
   - Include `card_index` in output dict to facilitate R4 origin tracking (e.g. "Derived from Tarot card #3: The Empress").
5. **Fallback Behavior**:
   - If `selected_cards` is `None` (not provided), fall back to CSPRNG random drawing of 10 unique cards from `self.deck` for backward compatibility.

### 4.2 Proposed Code Implementation for `tarot.py`

Update `draw_celtic_cross` in `omni_oracle_app/backend/app/engines/tarot.py`:

```python
def draw_celtic_cross(self, selected_cards: Optional[List[int]] = None) -> List[dict]:
    """
    Draws a 10-card Celtic Cross spread.
    
    Parameters:
        selected_cards: Optional list of 10 card indices (0..77) chosen by user.
                        If None, randomly shuffles and draws 10 cards using CSPRNG.
                        
    Returns:
        List of 10 drawn card dictionaries.
        
    Raises:
        ValueError if selected_cards is invalid.
    """
    drawn_cards = []
    
    if selected_cards is not None:
        if not isinstance(selected_cards, (list, tuple)):
            raise ValueError("selected_tarot_cards must be a list of 10 card indices.")
        if len(selected_cards) != 10:
            raise ValueError(f"selected_tarot_cards must contain exactly 10 card indices, got {len(selected_cards)}.")
        
        seen_indices = set()
        for idx in selected_cards:
            if not isinstance(idx, int) or isinstance(idx, bool):
                raise ValueError(f"Invalid card index '{idx}'. Card index must be an integer.")
            if not (0 <= idx <= 77):
                raise ValueError(f"Card index {idx} out of valid range (0..77).")
            if idx in seen_indices:
                raise ValueError(f"Duplicate card index {idx} in selected_tarot_cards.")
            seen_indices.add(idx)

        for i, card_idx in enumerate(selected_cards):
            card = self.deck[card_idx]
            is_reversed = secrets.choice([True, False])
            drawn_cards.append({
                "id": card["id"],
                "name": card["name"],
                "type": card["type"],
                "is_reversed": is_reversed,
                "position_meaning": self.celtic_cross_positions[i],
                "meaning": card["meaning_reversed"] if is_reversed else card["meaning_upright"],
                "card_index": card_idx
            })
    else:
        deck_copy = self.deck.copy()
        for i in range(10):
            idx = secrets.randbelow(len(deck_copy))
            card = deck_copy.pop(idx)
            is_reversed = secrets.choice([True, False])
            card_orig_idx = next(j for j, c in enumerate(self.deck) if c["id"] == card["id"])
            drawn_cards.append({
                "id": card["id"],
                "name": card["name"],
                "type": card["type"],
                "is_reversed": is_reversed,
                "position_meaning": self.celtic_cross_positions[i],
                "meaning": card["meaning_reversed"] if is_reversed else card["meaning_upright"],
                "card_index": card_orig_idx
            })
            
    return drawn_cards
```

---

## 5. Integration Plan for `app.py` `/api/divine` Endpoint

In `omni_oracle_app/backend/app.py`:

```python
@app.route('/api/divine', methods=['POST'])
def divine():
    data = request.json or {}
    
    birth_date = data.get('birth_date', '1990-01-01')
    birth_time = data.get('birth_time', '12:00')
    birth_province = data.get('birth_province', 'กรุงเทพมหานคร')
    selected_tarot_cards = data.get('selected_tarot_cards', None)
    
    # 1. R1: Thai Lunar Calendar calculation with 6am Cutoff
    try:
        lunar_cal = calculate_thai_lunar_calendar(birth_date=birth_date, birth_time=birth_time)
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400

    # 2. Engines execution
    try:
        num_res_obj = calculate_numerology_7x9(
            birth_date=birth_date,
            day_of_week=lunar_cal.day_of_week_num,
            thai_lunar_month=lunar_cal.lunar_month,
            thai_lunar_year=lunar_cal.zodiac_year_num
        )
        num_res = num_res_obj.model_dump()
    except Exception as e:
        num_res = {"error": str(e)}

    try:
        mah_res_obj = calculate_mahabote(birth_date=birth_date, birth_time=birth_time)
        mah_res = mah_res_obj.model_dump()
    except Exception as e:
        mah_res = {"error": str(e)}

    try:
        ast_res_obj = calculate_thai_astrology(birth_date=birth_date, birth_time=birth_time, birth_province=birth_province)
        ast_res = ast_res_obj.model_dump()
    except Exception as e:
        ast_res = {"error": str(e)}

    # 3. R2: Tarot engine execution
    try:
        tarot_res = tarot_engine.draw_celtic_cross(selected_cards=selected_tarot_cards)
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400

    rec_nums = recommender.generate_recommendations(num_res, mah_res, ast_res, tarot_res)
    syn_text, disclaimer = synthesis.synthesize(num_res, mah_res, ast_res, tarot_res)

    return jsonify({
        "status": "success",
        "chart": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "lunar_calendar": {
                "day_of_week": lunar_cal.day_of_week,
                "lunar_month": lunar_cal.lunar_month,
                "zodiac_year": lunar_cal.zodiac_year,
                "cutoff_applied": lunar_cal.cutoff_applied
            }
        },
        "numerology": num_res,
        "mahabote": mah_res,
        "astrology": ast_res,
        "tarot": {"spread": tarot_res, "interpretation": "การอ่านไพ่ 10 ใบ"},
        "lucky_numbers": rec_nums,
        "synthesis": syn_text,
        "disclaimer": disclaimer
    })
```

---

## 6. Unit Test Strategy

### 6.1 R1 Unit Tests (`omni_oracle_app/backend/tests/test_thai_astrology.py`)

1. **`test_lunar_calendar_cutoff_before_6am`**:
   - Input: `birth_date="1992-05-15"`, `birth_time="05:30"`.
   - Assert `res.cutoff_applied is True`.
   - Assert `res.day_of_week == "Thursday"` (since 1992-05-15 05:30 subtracts 1 day to May 14 Thursday).

2. **`test_lunar_calendar_cutoff_after_6am`**:
   - Input: `birth_date="1992-05-15"`, `birth_time="07:00"`.
   - Assert `res.cutoff_applied is False`.
   - Assert `res.day_of_week == "Friday"`.

3. **`test_lunar_month_approximation`**:
   - Test dates before day 16 vs on/after day 16 across months.
   - Assert `lunar_month` returns integer in `1..12`.

4. **`test_zodiac_year_songkran_boundary`**:
   - Input: `1993-01-15` (before April 13) -> returns Previous Year (`"Monkey"` / `9`).
   - Input: `1993-05-15` (after April 13) -> returns Current Year (`"Rooster"` / `10`).

5. **`test_lunar_calendar_contract_fields`**:
   - Verify result object contains `day_of_week`, `lunar_month`, `zodiac_year`, `cutoff_applied`.

### 6.2 R2 Unit Tests (`omni_oracle_app/backend/tests/test_tarot.py`)

1. **`test_draw_celtic_cross_with_valid_selection`**:
   - Input: `[0, 12, 25, 31, 44, 50, 61, 72, 5, 18]`.
   - Assert `len(spread) == 10`.
   - Assert card indices in spread match `[0, 12, 25, 31, 44, 50, 61, 72, 5, 18]`.
   - Assert `spread[0]['position_meaning'] == "สถานการณ์ปัจจุบัน"`.
   - Assert `spread[9]['position_meaning'] == "บทสรุปของสถานการณ์"`.

2. **`test_draw_celtic_cross_out_of_range`**:
   - Input: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 88]`.
   - Assert `pytest.raises(ValueError, match="out of valid range")`.

3. **`test_draw_celtic_cross_duplicate_indices`**:
   - Input: `[5, 5, 12, 15, 20, 25, 30, 35, 40, 45]`.
   - Assert `pytest.raises(ValueError, match="Duplicate card index")`.

4. **`test_draw_celtic_cross_wrong_length`**:
   - Input: `[0, 1, 2, 3, 4]`.
   - Assert `pytest.raises(ValueError, match="exactly 10 card indices")`.

5. **`test_draw_celtic_cross_default_backward_compatibility`**:
   - Input: `selected_cards=None`.
   - Assert returns 10 unique random cards.

---

## 7. Summary of Seams & Dependencies

- **Seam 1**: `calculate_thai_lunar_calendar(birth_date, birth_time)` in `thai_astrology.py` (or `thai_lunar.py`).
- **Seam 2**: `TarotEngine.draw_celtic_cross(selected_cards=None)` in `tarot.py`.
- **Seam 3**: `POST /api/divine` controller integration in `app.py`.
- **Dependencies for Sub-Orchestrator**:
  - Implementer can apply the proposed code snippets directly to `thai_astrology.py`, `tarot.py`, and `app.py`.
  - Explorer 2/3 (R3 & R4) can consume `tarot_res` card indices and `lunar_cal` outputs for backtesting and origin tracking.
