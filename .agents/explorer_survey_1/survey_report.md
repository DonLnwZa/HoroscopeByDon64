# Omni-Oracle Backend & API Detailed Survey Report

**Date**: 2026-08-12  
**Target Repository**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`  
**Historical Data Location**: `e:\ข้อมูลผลหวยย้อนหลัง 1 ปี\fetch_lottery\lottery_results_past_1_year.json`  
**Author**: Backend & API Survey Explorer (`explorer_survey_1`)

---

## 1. Executive Summary

This survey report provides a comprehensive technical analysis of the `omni_oracle_app` backend and historical lottery data, laying the foundation for upgrading the Omni-Oracle lottery prediction system with four major features:
1. **R1: Auto-Approximate Thai Lunar Calendar** (Removing manual dropdowns; auto-calculating Day of Week with a **6:00 AM cutoff rule** in Bangkok UTC+7, Thai Lunar Month, and Zodiac Year from Gregorian birth date and time).
2. **R2: Interactive Tarot Selection API** (Accepting 10 user-selected card indices out of 78 total cards via `/api/divine`).
3. **R3: Backtesting Heat Index** (Comparing recommended numbers against 1-year historical GLO lottery results to compute win frequency).
4. **R4: Divination Transparency** (Tracking and returning the origin/source breakdown of each recommended lucky number across the four divination engines).

---

## 2. Codebase & Engine Architecture Survey

### 2.1 File Map of `omni_oracle_app/backend`
```
omni_oracle_app/backend/
├── app.py                            # Flask application entry point & API route definitions
├── app/
│   ├── __init__.py
│   └── engines/
│       ├── __init__.py
│       ├── thai_astrology.py          # Lahiri Ayanamsa, 10 Planets, 12 Houses, D9/D3 divisional charts
│       ├── mahabote.py                # Burmese Mahabote 7-position chart, Taksa 8-planet wheel, Kalayok
│       ├── numerology_7x9.py          # 7-Digit 9-Base Numerology matrix, Base 1-4 power, 21 house collisions
│       ├── tarot.py                   # 78 Tarot cards deck (22 Major Arcana + 56 Minor Arcana) & Celtic Cross spread
│       ├── lottery_stats.py           # Historical GLO lottery statistics analyzer
│       ├── number_recommender.py      # Cross-engine composite lucky number generator
│       └── oracle_synthesis.py        # Multi-engine synthesis & ethical safety disclaimer text generator
├── data/
│   └── lottery_results_past_1_year.json # Copy of 1-year historical lottery results (24 draws)
├── tests/
│   ├── test_tarot.py
│   ├── test_mahabote.py
│   ├── test_numerology_7x9.py
│   ├── test_thai_astrology.py
│   ├── test_lottery_stats.py
│   ├── test_tier1_feature_coverage.py
│   ├── test_tier2_boundary_safety.py
│   ├── test_tier3_pairwise_integration.py
│   └── test_tier4_realworld_scenarios.py
└── requirements.txt
```

### 2.2 Analysis of Core Backend Engines

| Engine | File Path | Current Status & Capabilities | Required Upgrades |
|---|---|---|---|
| **Thai Astrology** | `app/engines/thai_astrology.py` | Full planetary ephemeris, 12 houses, Lahiri ayanamsa, Lagna calculation from date/time/province. | Integrated into `/api/divine` with `birth_date` & `birth_time`. |
| **Mahabote Engine** | `app/engines/mahabote.py` | Calculates Chula Sakarat, 7 positions, Taksa wheel, Kalayok, Wednesday day/night logic. | Ensure day-of-week calculation respects 6:00 AM cutoff. |
| **Numerology 7x9** | `app/engines/numerology_7x9.py` | Calculates 7-column x 9-row matrix, house collisions across 21 astrological houses. | Auto-derive `day_of_week`, `lunar_month`, and `zodiac_year` from date & time instead of requiring raw inputs. |
| **Tarot Engine** | `app/engines/tarot.py` | 78-card deck representation. Currently draws 10 cards randomly via `secrets.randbelow`. | Upgrade `draw_celtic_cross()` to accept `selected_cards: List[int]` (10 indices out of 78). |
| **Lottery Stats Engine** | `app/engines/lottery_stats.py` | Reads 1-year GLO JSON file. Calculates digit frequencies and hot/cold digits. | Add Backtesting Heat Index comparison function for 2-digit, 3-digit, and 6-digit numbers. |
| **Number Recommender** | `app/engines/number_recommender.py` | Generates 2-digit, 3-digit, 6-digit numbers from simple pool. | Add provenance tracking (`number_origins`) detailing which engine/position produced each digit. |
| **Flask API Server** | `app.py` | Accepts POST `/api/divine` with manual day/month/year dropdowns. | Update route signature, payload parser, and response JSON contract for R1-R4. |

---

## 3. Historical Lottery Dataset Audit

### 3.1 Data File Location & Structure
- **Primary Path**: `e:\ข้อมูลผลหวยย้อนหลัง 1 ปี\fetch_lottery\lottery_results_past_1_year.json`
- **Backend Mirror**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\data\lottery_results_past_1_year.json`
- **Record Count**: 24 draw objects representing 1 full year of Thai Government Lottery (GLO) draws (bi-monthly: 1st and 16th of each month from August 2024 to August 2025).

### 3.2 Key Fields per Draw Object
```json
{
  "draw_date": "2025-08-01",
  "prize_1st": "811852",
  "prize_last2": "50",
  "prize_last3f": ["142", "525"],
  "prize_last3b": ["512", "891"],
  "prize_near1": ["811851", "811853"],
  "prize_2nd": ["329930", "519877", "588144", "809975", "810260"],
  "prize_3rd": [...10 numbers...],
  "prize_4th": [...50 numbers...],
  "prize_5th": [...100 numbers...]
}
```

---

## 4. Deep Technical Analysis & Feature Solution Designs

### 4.1 Requirement R1: Auto-Approximate Thai Lunar Calendar

#### Problem Statement
Currently, `app.py` expects manual inputs from the request body:
```python
day_of_week = int(data.get('birth_day_of_week', 1))
lunar_month = int(data.get('birth_month_lunar', 1))
year_animal = int(data.get('birth_year_animal', 1))
```
This forces the user to manually calculate or guess their Thai day of week, lunar month, and zodiac year.

#### Proposed Solution & Algorithm Logic
1. **Input Payload**: `birth_date` (string `YYYY-MM-DD`), `birth_time` (string `HH:MM`, default `"12:00"`).
2. **6:00 AM Cutoff Rule for Day of Week (Bangkok UTC+7)**:
   - In Thai traditional calendar system, a day starts at 06:00 AM (sunrise).
   - Parse `birth_date` and `birth_time`.
   - If `birth_time < "06:00"`, the birth day of week is calculated for `birth_date - 1 day`.
   - Otherwise, day of week is calculated for `birth_date`.
   - Formula for Day of Week (1=Sunday, 2=Monday, ..., 7=Saturday):
     ```python
     effective_date = dt_date - timedelta(days=1) if dt_time.hour < 6 else dt_date
     # Python weekday: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
     day_of_week = ((effective_date.weekday() + 1) % 7) + 1
     ```
3. **Thai Lunar Month Approximation**:
   - In Thai lunar calendar (เดือนจันทรคติไทย):
     - Month 1 (เดือน 1 / เดือนอ้าย) starts around Dec / Jan.
     - Month 5 (เดือน 5 / สงกรานต์) is around April.
     - Month 12 (เดือน 12 / ลอยกระทง) is around November.
   - Approximation Formula:
     ```python
     # Approximation based on Gregorian month
     lunar_month = ((dt_date.month) % 12) + 1  # Or standard offset table
     ```
4. **Thai Zodiac Year (ปีนักษัตร) Approximation**:
   - 12 Zodiac animals (1=ชวด/Rat, 2=ฉลู/Ox, 3=ขาล/Tiger, 4=เถาะ/Rabbit, 5=มะโรง/Dragon, 6=มะเส็ง/Snake, 7=มะเมีย/Horse, 8=มะแม/Goat, 9=วอก/Monkey, 10=ระกา/Rooster, 11=จอ/Dog, 12=กุน/Pig).
   - Cutoff boundary: April 13 (Songkran).
   - Formula:
     ```python
     if (dt_date.month < 4) or (dt_date.month == 4 and dt_date.day < 13):
         zodiac_year = ((dt_date.year - 5) % 12) + 1
     else:
         zodiac_year = ((dt_date.year - 4) % 12) + 1
     ```

---

### 4.2 Requirement R2: Interactive Tarot Selection API Endpoint

#### Problem Statement
Currently, `TarotEngine.draw_celtic_cross()` generates a spread of 10 random cards using `secrets.randbelow(len(deck_copy))`.

#### Proposed Solution & Algorithm Logic
1. **API Endpoint Signature**:
   - `/api/divine` request body expects:
     ```json
     {
       "birth_date": "1995-08-15",
       "birth_time": "08:30",
       "selected_tarot_cards": [0, 5, 12, 19, 24, 31, 40, 52, 60, 77]
     }
     ```
2. **Validation Rules**:
   - `selected_tarot_cards` must be a list of exactly 10 integers.
   - Every integer $i$ must satisfy $0 \le i \le 77$.
   - If invalid or missing (fallback), generate or raise a clear error.
3. **Card Lookup & Spread Construction**:
   - Card mapping in `TarotEngine`:
     - Indices 0..21: Major Arcana (22 cards: 0="The Fool", 1="The Magician", ..., 21="The World").
     - Indices 22..77: Minor Arcana (56 cards across 4 suits: Wands, Cups, Swords, Pentacles).
   - For each card index $c$ in `selected_tarot_cards` at index $i \in \{0..9\}$:
     - Position Meaning = `celtic_cross_positions[i]` (e.g. Position 0 = "สถานการณ์ปัจจุบัน").
     - Orientation (`is_reversed`) deterministically derived (e.g. `c % 2 == 1` or hash-based).
     - Construct position card record.

---

### 4.3 Requirement R3: Backtesting Heat Index Algorithm

#### Problem Statement
The user needs to know how "hot" or frequent each recommended lucky number was in historical Thai lottery draws over the past year.

#### Proposed Solution & Algorithm Logic
1. **Matching Rules for Recommended Numbers against 24 Historical Draws**:
   - **2-digit numbers** (e.g., `"50"`):
     - Check direct match against `prize_last2` (เลขท้าย 2 ตัว).
     - Check match against last 2 digits of `prize_1st` (2 ตัวท้ายของรางวัลที่ 1).
   - **3-digit numbers** (e.g., `"142"`):
     - Check match against `prize_last3f` (เลขหน้า 3 ตัว) and `prize_last3b` (เลขท้าย 3 ตัว).
     - Check match against last 3 digits of `prize_1st`.
   - **6-digit numbers** (e.g., `"811852"`):
     - Check exact match against `prize_1st`, `prize_near1`, `prize_2nd`, `prize_3rd`, `prize_4th`, `prize_5th`.
2. **Heat Score Classification**:
   - `win_count`: Total draws where the number appeared as a prize.
   - `heat_level`:
     - `win_count >= 3`: `"HOT"` (ความร้อนแรงสูง)
     - `win_count == 1 or 2`: `"WARM"` (ความร้อนแรงปานกลาง)
     - `win_count == 0`: `"COLD"` (ยังไม่เคยออกในรอบ 1 ปี)
3. **JSON Output Structure**:
   ```json
   "heat_index": {
     "total_draws_analyzed": 24,
     "two_digit": {
       "50": { "win_count": 3, "heat_level": "HOT", "matched_prizes": ["prize_last2 (2025-08-01)", "prize_last2 (2024-11-16)"] },
       "52": { "win_count": 1, "heat_level": "WARM", "matched_prizes": ["prize_1st_last2 (2025-08-01)"] }
     },
     "three_digit": {
       "142": { "win_count": 1, "heat_level": "WARM", "matched_prizes": ["prize_last3f (2025-08-01)"] }
     },
     "six_digit": {
       "811852": { "win_count": 1, "heat_level": "HOT", "matched_prizes": ["prize_1st (2025-08-01)"] }
     }
   }
   ```

---

### 4.4 Requirement R4: Divination Transparency (Origin/Source Tracking Breakdown)

#### Problem Statement
Currently, `NumberRecommender.generate_recommendations()` randomly picks digits from a pool without storing where each number came from.

#### Proposed Solution & Algorithm Logic
1. **Origin Attribution Engine**:
   - Each recommended number is composed from specific roots across the 4 divination engines:
     - **Astrology Root**: Lagna lord, Labha lord, Putta lord, exalted planet digits.
     - **Numerology 7x9 Root**: Base 4 total power, Base 1-3 matrix collisions, top auspicious houses (ลาภะ, สุภะ, โภคา, ธนัง).
     - **Mahabote Root**: Thanang digit (ธนัง), Phoka digit (โภคา), Taksa Sri digit (ศรี), Kalayok Thongchai digit (ธงชัย).
     - **Tarot Root**: Selected Tarot card numbers (e.g. Card #0 The Fool, Card #10 Wheel of Fortune).
     - **Lottery Stats Root**: Hot digits from historical GLO frequency counts.
2. **JSON Output Structure (`number_origins`)**:
   ```json
   "number_origins": {
     "two_digit": [
       {
         "number": "52",
         "sources": [
           "มหาภูติพม่า: ตำแหน่งโภคา (ดาวพฤหัสบดี 5)",
           "โหราศาสตร์ไทย: ดาวเจ้าเรือนลาภะ (ดาวจันทร์ 2)",
           "ไพ่ทาโรต์: ไพ่ใบที่ 2 (The High Priestess)"
         ],
         "primary_engine": "Mahabote + ThaiAstrology",
         "provenance_summary": "ถอดจากดาวพฤหัสบดีเรือนโภคา ผสานดาวจันทร์เรือนลาภะ"
       }
     ],
     "three_digit": [
       {
         "number": "142",
         "sources": [
           "เลข 7 ตัว 9 ฐาน: ขุมพลังฐาน 4 รวม 14 (1, 4)",
           "โหราศาสตร์ไทย: ดาวเจ้าเรือนลาภะ (2)",
           "ไพ่ทาโรต์: ไพ่ใบที่ 1 (The Magician)"
         ],
         "primary_engine": "Numerology7x9 + Tarot",
         "provenance_summary": "ฐานรวม 4 และไพ่ The Magician"
       }
     ],
     "six_digit": [
       {
         "number": "811852",
         "sources": [
           "การสังเคราะห์รวม 4 ศาสตร์ (มหาภูติ + โหราศาสตร์ + เลข 7 ตัว + ทาโรต์)",
           "สถิติหวย: ตรงกับรางวัลที่ 1 ประจำงวด 1 ส.ค. 2025"
         ],
         "primary_engine": "Omni-Synthesis Core",
         "provenance_summary": "ชุดตัวเลขมงคลสมบูรณ์แบบถอดจากลัคนาและไพ่สรุป"
       }
     ]
   }
   ```

---

## 5. Unified API Specification for `/api/divine`

### 5.1 POST `/api/divine` Request JSON Schema
```json
{
  "birth_date": "1995-08-15",
  "birth_time": "08:30",
  "selected_tarot_cards": [0, 5, 12, 19, 24, 31, 40, 52, 60, 77]
}
```

### 5.2 POST `/api/divine` Response JSON Schema
```json
{
  "calculated_lunar_calendar": {
    "day_of_week": 3,
    "day_name_th": "วันอังคาร",
    "thai_lunar_month": 9,
    "lunar_month_name_th": "เดือน 9",
    "thai_lunar_year": 8,
    "zodiac_year_name_th": "ปีกุน",
    "is_before_6am_cutoff": false
  },
  "numerology": { ... },
  "mahabote": { ... },
  "astrology": { ... },
  "tarot": {
    "spread": [
      {
        "card_index": 0,
        "id": "major_0",
        "name": "The Fool",
        "type": "Major Arcana",
        "is_reversed": false,
        "position_meaning": "สถานการณ์ปัจจุบัน",
        "meaning": "ความหมายเชิงบวกของ The Fool"
      },
      ... 10 cards ...
    ],
    "interpretation": "การอ่านไพ่ 10 ใบ"
  },
  "lucky_numbers": {
    "two_digit": ["50", "52"],
    "three_digit": ["142", "525"],
    "six_digit": ["811852"]
  },
  "heat_index": {
    "total_draws_analyzed": 24,
    "two_digit": {
      "50": { "win_count": 3, "heat_level": "HOT" },
      "52": { "win_count": 1, "heat_level": "WARM" }
    },
    "three_digit": {
      "142": { "win_count": 1, "heat_level": "WARM" }
    },
    "six_digit": {
      "811852": { "win_count": 1, "heat_level": "HOT" }
    }
  },
  "number_origins": {
    "two_digit": [
      {
        "number": "50",
        "sources": ["มหาภูติพม่า: ฐานโภคา (5)", "สถิติหวยฮิต"],
        "provenance_summary": "ถอดจากดาวพฤหัสบดี (5) และเลขศูนย์ดวงดาว"
      }
    ],
    "three_digit": [ ... ],
    "six_digit": [ ... ]
  },
  "synthesis": "Omni-Oracle วิเคราะห์ดวงชะตาของคุณจากการผสาน 4 ศาสตร์...",
  "disclaimer": "คำทำนายและตัวเลขแนะนำเป็นเพียงสถิติและแนวทางตามศาสตร์พยากรณ์เท่านั้น..."
}
```

---

## 6. Implementation Roadmap & Concrete Patch Guidance

### Step 1: Add Thai Lunar Approximation Helper (`app/engines/lunar_calculator.py` or within `app.py`)
- Implement `calculate_thai_lunar_params(birth_date_str, birth_time_str)`:
  - Parse date and time.
  - Apply 6:00 AM cutoff rule for `day_of_week`.
  - Calculate `thai_lunar_month` and `thai_lunar_year`.

### Step 2: Update `TarotEngine` (`app/engines/tarot.py`)
- Modify `draw_celtic_cross(selected_card_indices: Optional[List[int]] = None)`:
  - If `selected_card_indices` provided, pick cards by indices `[0..77]`.
  - Attach `card_index` to each card object in the spread.

### Step 3: Upgrade `LotteryStatsEngine` (`app/engines/lottery_stats.py`)
- Add `compute_heat_index(recommended_numbers_dict)`:
  - Search 24 historical draw objects.
  - Count matching prize occurrences for 2-digit, 3-digit, and 6-digit numbers.
  - Return formatted `heat_index` dict.

### Step 4: Upgrade `NumberRecommender` (`app/engines/number_recommender.py`)
- Update `generate_recommendations(...)` to track sources/lineage for each generated number.
- Return both `lucky_numbers` and `number_origins`.

### Step 5: Update `/api/divine` Route in `app.py`
- Parse `birth_date`, `birth_time`, and `selected_tarot_cards`.
- Execute auto-lunar approximation.
- Call updated engines and assemble unified JSON response.

---

## 7. Verification & Testing Plan

1. **Unit Test Cases (`tests/test_lunar_calculator.py`)**:
   - Verify birth time `"05:30"` shifts birth date to previous day for day-of-week calculation.
   - Verify birth time `"06:01"` uses current birth date for day-of-week calculation.
2. **Tarot API Test Cases (`tests/test_tarot.py`)**:
   - Verify passing array of 10 card indices returns exact corresponding 10 cards.
   - Verify rejection when array length $\ne 10$ or index out of range $[0, 77]$.
3. **Heat Index Test Cases (`tests/test_lottery_stats.py`)**:
   - Test number `"50"` matches `prize_last2` in historical dataset and returns `win_count >= 1`.
   - Test non-matching number `"00"` returns `win_count == 0` and `heat_level == "COLD"`.
4. **Transparency Test Cases (`tests/test_number_recommender.py`)**:
   - Verify every recommended number in `lucky_numbers` has a matching key and source breakdown in `number_origins`.
