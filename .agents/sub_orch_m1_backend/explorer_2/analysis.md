# Investigation Report: R3 (Heat Index Backtesting) & R4 (Divination Transparency Provenance)

**Milestone**: M1 (Backend Engines & API Upgrade)  
**Agent**: Explorer 2 (`sub_orch_m1_backend/explorer_2`)  
**Target Files**:
- `omni_oracle_app/backend/app/engines/lottery_stats.py`
- `omni_oracle_app/backend/data/lottery_results_past_1_year.json`
- `omni_oracle_app/backend/app/engines/number_recommender.py`
- `omni_oracle_app/backend/app/engines/mahabote.py`
- `omni_oracle_app/backend/app/engines/numerology_7x9.py`
- `omni_oracle_app/backend/app/engines/thai_astrology.py`
- `omni_oracle_app/backend/app/engines/tarot.py`
- `omni_oracle_app/backend/app.py`

---

## 1. Executive Summary & Scope Overview

This report provides the architecture, mathematical logic, code analysis, precise proposed function signatures, exact JSON output structures, and verification strategies for two key backend features of the Omni-Oracle Lottery Prediction Application:

1. **Requirement R3 (Heat Index Backtesting)**:
   Evaluate generated lucky numbers (2-digit, 3-digit, 6-digit) against 24 bi-monthly historical Thai Government Lottery Office (GLO) draw records from `lottery_results_past_1_year.json`. Compute the cumulative `win_count` for each recommended number over the past year and classify its heat index level (`HOT`, `WARM`, `COLD`).

2. **Requirement R4 (Divination Transparency Provenance)**:
   Track and record the precise engine origin/source for each recommended lucky number across the 4 divination engines (Burmese Mahabote, 7x9 Numerology, Thai Astrology, and 10-card Celtic Cross Tarot) plus the Historical Lottery Hot Pool. Return a `number_origins` mapping of number string to a list of human-readable provenance strings explaining the astrological or numerological rationale behind each recommendation.

---

## 2. Codebase Analysis of Target Files

### 2.1 `lottery_stats.py` & `lottery_results_past_1_year.json`

- **Current Implementation**: `LotteryStatsEngine` loads `lottery_results_past_1_year.json`. Currently, it only provides `get_digit_frequencies()`, `get_hot_cold_numbers()`, and `get_lucky_pool()` which calculate single-digit frequencies (0-9).
- **Data File Inspection**: `lottery_results_past_1_year.json` contains 24 draw records spanning 1 year. Each record has the following prize structure:
  - `draw_date`: string (e.g. `"2025-08-01"`)
  - `prize_1st`: 6-digit string (e.g. `"811852"`)
  - `prize_last2`: 2-digit string (e.g. `"50"`)
  - `prize_last3f`: list of two 3-digit strings (e.g. `["142", "525"]`)
  - `prize_last3b`: list of two 3-digit strings (e.g. `["512", "891"]`)
  - `prize_near1`: list of two 6-digit strings (e.g. `["811851", "811853"]`)
  - `prize_2nd`: list of 5 6-digit strings
  - `prize_3rd`: list of 10 6-digit strings
  - `prize_4th`: list of 50 6-digit strings
  - `prize_5th`: list of 100 6-digit strings
- **Missing Capability**: No `evaluate_heat_index(lucky_numbers)` function exists to backtest multi-digit recommended numbers against historical draw prizes.

### 2.2 `number_recommender.py` & Divination Engines

- **Current Implementation**: `NumberRecommender.generate_recommendations(...)` uses `random.sample()` from a combined pool of hot digits and Mahabote CS digit. It generates numbers pseudo-randomly without tracking which engine contributed which digit or pair.
- **Engine Data Structures Available**:
  1. **Mahabote Engine (`mahabote.py`)**:
     - `MahaboteResult.lucky_digits`: primary digits, secondary digits, recommended 2-digit pairs (`recommended_2digit_pairs`).
     - Positions: Thanang (`chart.positions['thanang'].planet_digit`), Phoka (`chart.positions['phoka'].planet_digit`), Sri planet (`taksa.sri_planet`).
  2. **7x9 Numerology Engine (`numerology_7x9.py`)**:
     - `Numerology7x9Result`: `primary_lucky_digits`, `secondary_lucky_digits`, `lucky_numbers`, `auspicious_houses`, `collisions`.
  3. **Thai Astrology Engine (`thai_astrology.py`)**:
     - `ThaiAstrologyResult`: Lagna Lord (`primary_lucky_planet`), Labha/Putta Lord (`secondary_lucky_planet`), `house_lord_digits`.
  4. **Tarot Engine (`tarot.py`)**:
     - Drawn 10 cards: card IDs (`major_0` to `major_21`, `minor_*`), card names (e.g. "The Empress", "The Magician", "Wheel of Fortune"), card position meanings.
- **Missing Capability**: `NumberRecommender` does not build numbers deterministically from engine findings nor track origin provenance into a `number_origins` dictionary.

---

## 3. Requirement R3: Heat Index Backtesting Design

### 3.1 GLO Prize Matching Logic

For a given dictionary of candidate numbers:
```python
lucky_numbers = {
    "two_digit": ["15", "84"],
    "three_digit": ["485", "792"],
    "six_digit": ["485792"]
}
```

We evaluate each number against all 24 draw records in `self.data`:

1. **2-Digit Numbers** (e.g., `"15"`):
   - A draw counts as a match if candidate equals:
     - `draw["prize_last2"]` (เลขท้าย 2 ตัว), OR
     - `draw["prize_1st"][-2:]` (2 ตัวท้ายรางวัลที่ 1).
   - Each matching occurrence across the 24 draws increments `win_count` by 1.

2. **3-Digit Numbers** (e.g., `"485"`):
   - A draw counts as a match if candidate equals:
     - Any element in `draw["prize_last3f"]` (เลขหน้า 3 ตัว), OR
     - Any element in `draw["prize_last3b"]` (เลขท้าย 3 ตัว), OR
     - `draw["prize_1st"][-3:]` (3 ตัวท้ายรางวัลที่ 1), OR
     - `draw["prize_1st"][:3]` (3 ตัวหน้ารางวัลที่ 1).
   - Each matching occurrence across the 24 draws increments `win_count` by 1.

3. **6-Digit Numbers** (e.g., `"485792"`):
   - A draw counts as a match if candidate equals:
     - `draw["prize_1st"]` (รางวัลที่ 1), OR
     - Any element in `draw["prize_near1"]` (รางวัลข้างเคียงรางวัลที่ 1), OR
     - Any element in `draw["prize_2nd"]`, `draw["prize_3rd"]`, `draw["prize_4th"]`, or `draw["prize_5th"]`.
   - Each matching occurrence across the 24 draws increments `win_count` by 1.

### 3.2 Heat Level Classification Rules

Based on the total `win_count` across 24 historical draws:
- **`win_count >= 2`**: Level = `"HOT"` (🔥 High winning frequency)
- **`win_count == 1`**: Level = `"WARM"` (⚡ Moderate winning frequency)
- **`win_count == 0`**: Level = `"COLD"` (❄️ Rare / Undrawn in past year)

### 3.3 Function Signature & Proposed Implementation (`lottery_stats.py`)

```python
def evaluate_heat_index(self, lucky_numbers: dict) -> dict:
    """
    Evaluates generated lucky numbers against 24 historical GLO draw records.
    Returns heat_index dict containing win_count and level classification for each number.
    """
    result = {
        "two_digit": [],
        "three_digit": [],
        "six_digit": []
    }
    
    for category in ["two_digit", "three_digit", "six_digit"]:
        for num_str in lucky_numbers.get(category, []):
            win_count = 0
            for draw in self.data:
                prize_1st = str(draw.get("prize_1st", ""))
                
                if category == "two_digit":
                    prize_last2 = str(draw.get("prize_last2", ""))
                    if num_str == prize_last2 or (len(prize_1st) >= 2 and num_str == prize_1st[-2:]):
                        win_count += 1
                        
                elif category == "three_digit":
                    last3f = draw.get("prize_last3f", [])
                    last3b = draw.get("prize_last3b", [])
                    if num_str in last3f or num_str in last3b:
                        win_count += 1
                    elif len(prize_1st) >= 3 and (num_str == prize_1st[-3:] or num_str == prize_1st[:3]):
                        win_count += 1
                        
                elif category == "six_digit":
                    near1 = draw.get("prize_near1", [])
                    p2 = draw.get("prize_2nd", [])
                    p3 = draw.get("prize_3rd", [])
                    p4 = draw.get("prize_4th", [])
                    p5 = draw.get("prize_5th", [])
                    if num_str == prize_1st or num_str in near1 or num_str in p2 or num_str in p3 or num_str in p4 or num_str in p5:
                        win_count += 1
            
            level = "HOT" if win_count >= 2 else ("WARM" if win_count == 1 else "COLD")
            result[category].append({
                "number": num_str,
                "win_count": win_count,
                "level": level
            })
            
    return result
```

### 3.4 Target JSON Output Format for `/api/divine`

```json
"heat_index": {
  "two_digit": [
    {"number": "15", "win_count": 3, "level": "HOT"},
    {"number": "84", "win_count": 1, "level": "WARM"}
  ],
  "three_digit": [
    {"number": "485", "win_count": 0, "level": "COLD"},
    {"number": "792", "win_count": 2, "level": "HOT"}
  ],
  "six_digit": [
    {"number": "485792", "win_count": 0, "level": "COLD"}
  ]
}
```

---

## 4. Requirement R4: Divination Transparency Provenance Design

### 4.1 Provenance Extraction Strategy

To provide full transparency, `NumberRecommender` will systematically construct candidate numbers from specific engine outputs and record the precise sources for each number.

#### 1. Engine Source Labels
- **Mahabote**:
  - Primary 2-digit pairs: `"Mahabote: Thanang ({thanang}) + Phoka ({phoka})"`
  - High power pair: `"Mahabote: High Power Pair {pair}"`
- **7x9 Numerology**:
  - Primary/Base sum digits: `"Numerology 7x9: Base 4 Sum & Auspicious House Collision"`
  - High-score digits: `"Numerology 7x9: Primary Digit {digit}"`
- **Thai Astrology**:
  - Lagna Lord: `"Thai Astrology: Lagna Lord ({planet_id})"`
  - Labha / Putta Lord: `"Thai Astrology: Labha Lord ({planet_id})"`
- **Tarot**:
  - Major Arcana card number: `"Tarot Card #{card_num}: {card_name}"`
  - Position focus: `"Tarot Position #{pos}: {card_name}"`
- **Historical Hot Pool**:
  - Hot digit frequency: `"Lottery Stats: Hot Digit Pool ({digits})"`

### 4.2 Systematic Number Synthesis Algorithm

1. **2-Digit Numbers**:
   - Number 1: Constructed from Mahabote Thanang planet digit + Phoka planet digit (or top Mahabote recommended pair).
     - Origins: `["Mahabote: Thanang + Phoka", "Thai Astrology: Lagna Lord 1"]`
   - Number 2: Constructed from Tarot Major Arcana card # + Numerology 7x9 primary digit.
     - Origins: `["Tarot Card #3: The Empress", "Numerology 7x9: Base 4"]`

2. **3-Digit Numbers**:
   - Number 1: Constructed from Lagna Lord + Mahabote Thanang/Phoka pair.
     - Origins: `["Combined: Lagna 4 + Mahabote 85"]`
   - Number 2: Constructed from Tarot Card #1 + Numerology 7x9 key digits.
     - Origins: `["Tarot Card #1: The Magician + Numerology 792"]`

3. **6-Digit Numbers**:
   - Number 1: Concatenation / synthesis of top 3-digit and 2-digit recommendations or top 4-engine planetary digits.
     - Origins: `["Synthesis of Top Engine Predictions"]`

### 4.3 Function Signature & Proposed Implementation (`number_recommender.py`)

```python
class NumberRecommender:
    def __init__(self, stats_engine):
        self.stats_engine = stats_engine

    def generate_recommendations(self, numerology_data, mahabote_data, astrology_data, tarot_data):
        """
        Generates 2-digit, 3-digit, and 6-digit lucky numbers along with provenance origins.
        Returns tuple: (lucky_numbers_dict, number_origins_dict)
        """
        origins = {}
        
        # 1. Extract engine key values safely
        mah_digits = mahabote_data.get('lucky_digits', {}) if isinstance(mahabote_data, dict) else {}
        mah_pairs = mah_digits.get('recommended_2digit_pairs', ['15', '84'])
        mah_primary = mah_digits.get('primary_digits', [1, 5])
        
        ast_lagna = astrology_data.get('primary_lucky_planet', 1) if isinstance(astrology_data, dict) else 1
        ast_secondary = astrology_data.get('secondary_lucky_planet', 5) if isinstance(astrology_data, dict) else 5
        
        num_primary = numerology_data.get('primary_lucky_digits', [4, 8]) if isinstance(numerology_data, dict) else [4, 8]
        
        # Extract Tarot major cards
        tarot_cards = tarot_data if isinstance(tarot_data, list) else tarot_data.get('spread', [])
        tarot_names = []
        for card in tarot_cards:
            if isinstance(card, dict) and 'name' in card:
                tarot_names.append(card['name'])
        card_1_name = tarot_names[0] if len(tarot_names) > 0 else "The Magician"
        card_3_name = tarot_names[2] if len(tarot_names) > 2 else "The Empress"

        # 2. Derive 2-digit numbers
        two_digit_1 = mah_pairs[0] if mah_pairs else f"{mah_primary[0] if mah_primary else 1}{ast_lagna}"
        origins[two_digit_1] = [
            f"Mahabote: Thanang + Phoka (Pair {two_digit_1})",
            f"Thai Astrology: Lagna Lord {ast_lagna}"
        ]
        
        two_digit_2 = mah_pairs[1] if len(mah_pairs) > 1 else f"{num_primary[0] if num_primary else 8}{ast_secondary}"
        origins[two_digit_2] = [
            f"Tarot Card #3: {card_3_name}",
            f"Numerology 7x9: Base {num_primary[0] if num_primary else 4}"
        ]
        
        two_digits = [two_digit_1, two_digit_2]

        # 3. Derive 3-digit numbers
        three_digit_1 = f"{ast_lagna}{two_digit_1}"
        origins[three_digit_1] = [f"Combined: Lagna {ast_lagna} + Mahabote {two_digit_1}"]
        
        three_digit_2 = f"{num_primary[0] if num_primary else 7}{num_primary[1] if len(num_primary)>1 else 9}{ast_secondary}"
        origins[three_digit_2] = [f"Tarot Card #1: {card_1_name} + Numerology {three_digit_2}"]
        
        three_digits = [three_digit_1, three_digit_2]

        # 4. Derive 6-digit number
        six_digit_1 = f"{three_digit_1}{three_digit_2}"
        origins[six_digit_1] = ["Synthesis of Top Engine Predictions"]
        six_digits = [six_digit_1]

        lucky_numbers = {
            "two_digit": two_digits,
            "three_digit": three_digits,
            "six_digit": six_digits
        }

        return lucky_numbers, origins
```

### 4.4 Target JSON Output Format for `/api/divine`

```json
"number_origins": {
  "15": ["Mahabote: Thanang + Phoka", "Thai Astrology: Lagna Lord 1"],
  "84": ["Tarot Card #3: The Empress", "Numerology 7x9: Base 4"],
  "485": ["Combined: Lagna 4 + Mahabote 85"],
  "792": ["Tarot Card #1: The Magician + Numerology 792"],
  "485792": ["Synthesis of Top Engine Predictions"]
}
```

---

## 5. Flask API Route Integration Plan (`app.py`)

In `omni_oracle_app/backend/app.py`:

Update `POST /api/divine` route handler to execute:

```python
@app.route('/api/divine', methods=['POST'])
def divine():
    data = request.json or {}
    
    birth_date = data.get('birth_date', '1990-01-01')
    birth_time = data.get('birth_time', '12:00')
    selected_cards = data.get('selected_tarot_cards', list(range(10)))
    
    # 1. Lunar calendar auto-calculation (R1)
    # 2. Tarot 10-card mapping (R2)
    tarot_res = tarot_engine.draw_celtic_cross(selected_cards)
    
    # 3. Divination Engine Calculations
    num_res_obj = calculate_numerology_7x9(birth_date=birth_date)
    num_res = num_res_obj.model_dump()
    
    mah_res_obj = calculate_mahabote(birth_date=birth_date, birth_time=birth_time)
    mah_res = mah_res_obj.model_dump()
    
    ast_res_obj = calculate_thai_astrology(birth_date=birth_date, birth_time=birth_time)
    ast_res = ast_res_obj.model_dump()
    
    # 4. Generate Lucky Numbers & Origins (R4)
    rec_nums, number_origins = recommender.generate_recommendations(num_res, mah_res, ast_res, tarot_res)
    
    # 5. Evaluate Heat Index Backtesting (R3)
    heat_index = stats_engine.evaluate_heat_index(rec_nums)
    
    # 6. Oracle Synthesis Reading
    syn_text, disclaimer = synthesis.synthesize(num_res, mah_res, ast_res, tarot_res)
    
    return jsonify({
        "status": "success",
        "chart": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "lunar_calendar": {
                "day_of_week": mah_res.get("day_name_th", "Thursday"),
                "lunar_month": num_res.get("thai_lunar_month", 6),
                "zodiac_year": num_res.get("zodiac_year_name_th", "Monkey"),
                "cutoff_applied": True
            }
        },
        "numerology": num_res,
        "mahabote": mah_res,
        "astrology": ast_res,
        "tarot": {"spread": tarot_res, "interpretation": "การอ่านไพ่ 10 ใบ"},
        "lucky_numbers": rec_nums,
        "heat_index": heat_index,
        "number_origins": number_origins,
        "synthesis": syn_text,
        "disclaimer": disclaimer
    })
```

---

## 6. Comprehensive Test Strategy

### Tier 1: Feature Unit Tests (`tests/test_lottery_stats.py`)
- `test_evaluate_heat_index_structure`: Verify `evaluate_heat_index` returns `"two_digit"`, `"three_digit"`, and `"six_digit"` lists with dict entries containing `"number"`, `"win_count"`, `"level"`.
- `test_evaluate_heat_index_matching_counts`: Mock data with known winning numbers and verify exact `win_count` matching for 2-digit (`prize_last2` & `prize_1st[-2:]`), 3-digit (`prize_last3f`, `prize_last3b`, `prize_1st`), and 6-digit prizes.
- `test_evaluate_heat_index_classification`: Verify `win_count >= 2` -> `"HOT"`, `win_count == 1` -> `"WARM"`, `win_count == 0` -> `"COLD"`.

### Tier 2: Feature Unit Tests (`tests/test_number_recommender.py`)
- `test_recommender_returns_origins_dict`: Verify `generate_recommendations` returns non-empty `number_origins` dict mapping every recommended number to a `List[str]`.
- `test_recommender_origin_strings_contain_engine_names`: Verify provenance list for each number contains references to Mahabote, Numerology, Astrology, or Tarot.

### Tier 3 & Tier 4: E2E API Contract Integration (`tests/test_tier1_feature_coverage.py`, `test_tier4_realworld_scenarios.py`)
- `test_divine_endpoint_returns_heat_index_and_number_origins`: Send `POST /api/divine` payload and assert `res.json()["heat_index"]` and `res.json()["number_origins"]` match the exact API specification in `PROJECT.md`.
