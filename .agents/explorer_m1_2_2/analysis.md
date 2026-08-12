# Analysis Report: 7-Digit 9-Base Numerology Engine (Sub-milestone M1.2)

**Author:** Explorer 2 (`explorer_m1_2_2`)  
**Target Engine File:** `omni_oracle_app/backend/app/engines/numerology_7x9.py`  
**Target Pytest Seam File:** `omni_oracle_app/backend/tests/test_numerology_7x9.py`  
**Date:** 2026-08-06  

---

## 1. Executive Summary & System Architecture

The **7-Digit 9-Base Numerology Engine** (`numerology_7x9.py`) is a core Layer 1 calculation engine in the Omni-Oracle Thai Lottery Divination web application. As specified in `PROJECT.md` and `SCOPE.md`, it computes a deterministic 7-column by 9-row mathematical matrix derived from the user's birthdate parameters (day of week, Thai lunar month, and Thai zodiac year).

This engine serves as a vital input for Layer 2's **Composite Lottery Recommender** (`lottery_recommender.py`), providing:
1. **21 Astrological Houses (เรือนชะตา 21 เรือน)** mapping across Rows 1–3.
2. **House Collision & Strength Detection (การชนเรือน)** identifying overlaps between auspicious and inauspicious houses.
3. **Planetary Pair Dynamics (คู่มิตร, คู่ศัตรู, คู่สมพล, คู่ธาตุ)** evaluating planetary strength and sum powers (กำลังดาว).
4. **Lucky Digits Extraction Algorithm** generating `primary_lucky_digits`, `secondary_lucky_digits`, and `lucky_numbers` for lottery recommendation weighting (60% Divination / 40% GLO Frequency).

---

## 2. Key Focus Area 1: 21 House Mapping (เรือนชะตา 21 เรือน)

In traditional Thai 7-Digit numerology (เลข 7 ตัว 3 ฐาน / 9 ฐาน), the first 3 rows form the core matrix of 21 astrological houses across 7 columns (index 0 to 6). Each column corresponds to a position in the 7-day cycle.

### 2.1 The 3x7 House Matrix Structure

```
Column Index:    Col 0       Col 1       Col 2       Col 3       Col 4       Col 5       Col 6
Row 1 (ฐานวัน):  อัตตะ       หินะ        ธนัง        ปิตา        มาตา        โภคา        มัชฌิมา
Row 2 (ฐานเดือน): ตะนุ        กดุมภะ      สหัชชะ      พันธุ        ปุตตะ       ปัตนิ       มรณะ
Row 3 (ฐานปี):   สุภะ        กัมมะ       ลาภะ        พยายะ       ทาสา        ทาสี        ภวังค์
```

### 2.2 21 House Taxonomy & Astrological Meanings

| Row | Col | House Name (TH) | House Name (EN) | Category | Astrological Meaning |
|---|---|---|---|---|---|
| **Row 1** | 0 | **อัตตะ** | Atta | Neutral | Self, Personality, Ego, Physical identity |
| | 1 | **หินะ** | Hina | Inauspicious | Flaw, Degradation, Loss, Vulnerability, Downfall |
| | 2 | **ธนัง** | Thanang | Auspicious | Liquid Wealth, Cash flow, Financial resources |
| | 3 | **ปิตา** | Pita | Neutral | Father, Male elders, Senior male figures, Mentors |
| | 4 | **มาตา** | Mata | Neutral | Mother, Female elders, Caregivers, Senior females |
| | 5 | **โภคา** | Bhoga | Auspicious | Property, Real Estate, Land, Possessions, Assets |
| | 6 | **มัชฌิมา** | Majjhima | Neutral | Moderation, Neutrality, Balance, Middle path |
| **Row 2** | 0 | **ตะนุ** | Tanu | Neutral | Core Identity, Physical Body, Mindset |
| | 1 | **กดุมภะ** | Kadumba | Auspicious | Income, Earning capacity, Personal revenue |
| | 2 | **สหัชชะ** | Sahajja | Neutral | Siblings, Close friends, Social network |
| | 3 | **พันธุ** | Bandhu | Auspicious | Family, Household stability, Lineage, Relatives |
| | 4 | **ปุตตะ** | Putta | Auspicious | Offspring, Children, Speculation, New ventures |
| | 5 | **ปัตนิ** | Patni | Auspicious | Spouse, Life partner, Business partners |
| | 6 | **มรณะ** | Marana | Inauspicious | Loss, Endings, Distant travel, Transformation |
| **Row 3** | 0 | **สุภะ** | Subha | Auspicious | Fortune, Prosperity, Virtue, Spiritual grace |
| | 1 | **กัมมะ** | Kamma | Auspicious | Action, Career, Duty, Profession, Work |
| | 2 | **ลาภะ** | Labha | Auspicious | Windfalls, Sudden gains, Lottery luck, Treasures |
| | 3 | **พยายะ** | Phayaya | Inauspicious | Secret troubles, Hidden enemies, Illness, Obstacles |
| | 4 | **ทาสา** | Dasa | Neutral | Male subordinates, Employees, Followers |
| | 5 | **ทาสี** | Dasi | Neutral | Female subordinates, Employees, Service workers |
| | 6 | **ภวังค์** | Bhavanga | Neutral | Subconscious, Undercurrents, Latent destiny |

---

## 3. Key Focus Area 2: House Collision & Strength Detection (ชนเรือน)

### 3.1 Classification of House Dignities
- **Top Auspicious Houses (ภพดีมาก/ภพโชคลาภหลัก)**:
  - `ลาภะ` (Row 3, Col 2): Direct lottery gains and windfall fortune.
  - `สุภะ` (Row 3, Col 0): High prosperity, grace, and luck.
  - `กัมมะ` (Row 3, Col 1): Career success and constructive effort.
  - `โภคา` (Row 1, Col 5): Property, asset wealth, and stability.
  - `ธนัง` (Row 1, Col 2): Liquid wealth and cash resources.
  - Secondary Auspicious: `กดุมภะ` (Row 2, Col 1), `ปุตตะ` (Row 2, Col 4), `ปัตนิ` (Row 2, Col 5).

- **Inauspicious / Bad Houses (ภพเสีย/ภพเสื่อม)**:
  - `หินะ` (Row 1, Col 1): Flaws, destruction, financial loss.
  - `มรณะ` (Row 2, Col 6): Loss, death/endings, drastic disruption.
  - `พยายะ` (Row 3, Col 3): Hidden obstacles, illness, secret leaks.

### 3.2 House Collision Types (ประเภทการชนเรือน)
Each digit $d \in \{1 \dots 7\}$ appears in exactly 3 positions across Rows 1, 2, and 3. The combination of houses linked by digit $d$ determines its collision classification:

1. **Pure Auspicious Collision (ชนเรือนดีบริสุทธิ์)**:
   - Digit $d$ appears ONLY in auspicious houses (e.g. `ลาภะ` + `โภคา` + `ธนัง`).
   - Result: Highest possible lucky score. Digit $d$ is added to `primary_lucky_digits`.

2. **Good-Bad Collision / Cross Collision (ชนเรือนดี-เสีย)**:
   - Digit $d$ appears in BOTH an auspicious house (e.g. `ลาภะ` or `สุภะ`) AND an inauspicious house (e.g. `มรณะ` or `หินะ`).
   - Result: Represents **ทุกขลาภ** (Gain accompanied by trouble or loss). Digit $d$ is flagged with `has_collision = True`. It is demoted from primary lucky digits to `secondary_lucky_digits` with a warning flag for Omni-Oracle synthesis.

3. **Pure Inauspicious Collision (ชนเรือนเสีย)**:
   - Digit $d$ appears in multiple inauspicious houses (e.g. `หินะ` + `มรณะ`).
   - Result: Avoided for primary lottery selection.

### 3.3 Digit Strength Scoring Formula
For each digit $d \in \{1 \dots 7\}$:
$$\text{Score}(d) = \sum_{h \in \text{Houses}(d)} \text{Weight}(h) + 0.5 \times \text{Base4\_Power}(\text{col}(h)) - \text{Penalty}(\text{BadHouses}(d))$$

Where:
- $\text{Weight}(\text{Top Auspicious}) = +3.0$
- $\text{Weight}(\text{Secondary Auspicious}) = +1.5$
- $\text{Weight}(\text{Neutral}) = 0.0$
- $\text{Penalty}(\text{Inauspicious}) = -2.5$

---

## 4. Key Focus Area 3: Planetary Pair Dynamics (คู่ดาว)

Planetary relationship dynamics govern the interaction between numbers in both single digits (1..7) and Base 4 column sums (กำลังดาว: 3..21).

### 4.1 Planetary Pair Categories (คู่ดาว 4 ประเภท)

1. **คู่มิตร (Friendly Pairs - Support & Mutual Aid)**:
   - **1 - 5** (Sun - Jupiter): Honor, wisdom, authority.
   - **2 - 4** (Moon - Mercury): Soft charm, speech, negotiation.
   - **3 - 6** (Mars - Venus): Passion, attraction, energetic drive.
   - **7 - 8** (Saturn - Rahu): Endurance, stealth, large scale power.

2. **คู่ศัตรู (Enemy Pairs - Obstacles & Friction)**:
   - **1 - 3** (Sun - Mars): Conflict, short temper, violent friction.
   - **2 - 5** (Moon - Jupiter): Emotional clash with rigid principles.
   - **4 - 7 / 4 - 8** (Mercury - Saturn / Mercury - Rahu): Miscommunication, deceit.
   - **6 - 7** (Venus - Saturn): Sorrow in desire, financial strain ("เสาร์ศุกร์เสาร์วาย").

3. **คู่สมพล (Power Pairs - Achievement through Drive)**:
   - **1 - 6** (Sun - Venus): Sum = 7 (Radiance, prestige, prosperity).
   - **2 - 8** (Moon - Rahu): Sum = 10 (Popular influence, magnetism).
   - **3 - 5** (Mars - Jupiter): Sum = 8 (Courageous wisdom, tactical success).
   - **4 - 7** (Mercury - Saturn): Sum = 11 (Analytical persistence).

4. **คู่ธาตุ (Elemental Pairs - Power Amplification)**:
   - **1 - 7** (Sun - Saturn): **Fire Element (ธาตุไฟ)** - Intensity, high ambition.
   - **2 - 5** (Moon - Jupiter): **Earth Element (ธาตุดิน)** - Solid wealth, foundation.
   - **3 - 8** (Mars - Rahu): **Wind Element (ธาตุลม)** - Rapid change, dynamic motion.
   - **4 - 6** (Mercury - Venus): **Water Element (ธาตุน้ำ)** - Liquidity, trade, money flow.

### 4.2 Base 4 Sum Powers (กำลังดาว ฐาน 4)
Base 4 represents the sum of Base 1 + Base 2 + Base 3 for each column (values 3 to 21). Specific sums map directly to Thai planetary powers (กำลังดาว):

| Base 4 Sum | Planetary Power (กำลังดาว) | Quality |
|---|---|---|
| **6** | อาทิตย์ (1) | Moderate status |
| **15** | จันทร์ (2) | High charm & liquidity (Very Auspicious) |
| **8** | อังคาร (3) | High energy, fast movement |
| **17** | พุธ (4) | Communication & intelligence |
| **19** | พฤหัสบดี (5) | Great wisdom & virtue (Extremely Auspicious) |
| **21** | ศุกร์ (6) | Peak wealth & luxury (Extremely Auspicious) |
| **10** | เสาร์ (7) | Heavy duty, endurance |
| **12** | ราหู (8) | Fortune through speculation / shadow luck |
| **9** | เกตุ (9) | Spiritual luck & unexpected intuition |
| **13** | มฤตยู (0) | Sudden change, transformation |

---

## 5. Key Focus Area 4: Lucky Digits Extraction Algorithm

The engine exports three structured lucky number lists for Layer 2 Recommender integration:

### 5.1 Extraction Procedure
1. **Primary Lucky Digits (`primary_lucky_digits: List[int]`)**:
   - Select digits $d \in \{1 \dots 7\}$ that appear in top auspicious houses (`สุภะ`, `ลาภะ`, `กัมมะ`, `โภคา`, `ธนัง`).
   - Condition: Must have `has_inauspicious_collision == False`.
   - Sorted descending by `collision_score` and Base 4 column power.
   - Returns top 2–3 single digits.

2. **Secondary Lucky Digits (`secondary_lucky_digits: List[int]`)**:
   - Select digits $d$ that appear in secondary auspicious houses (`กดุมภะ`, `ปุตตะ`, `ปัตนิ`) OR auspicious digits that have a mild cross-collision with inauspicious houses.
   - Returns 2–3 supporting digits.

3. **Lucky Numbers (`lucky_numbers: List[int]`)**:
   - Synthesize 2-digit pairs by pairing `primary_lucky_digits` with each other, with high-power Base 4 column single digits, or with planetary pair partners (e.g. if Primary includes 6, pair with 3 or 4 -> [63, 64, 36, 46]).
   - Returns a list of 4–6 2-digit numbers for lottery ticket matching.

---

## 6. Matrix Computation Rules (Bases 1 to 9)

Given inputs:
- `day_num` (1=Sun .. 7=Sat)
- `lunar_month_num` (1..12)
- `zodiac_year_num` (1..12)

### Formulas:
- Normalization:
  - $D = \text{day\_num} \in \{1..7\}$
  - $M = ((\text{lunar\_month\_num} - 1) \bmod 7) + 1 \in \{1..7\}$
  - $Y = ((\text{zodiac\_year\_num} - 1) \bmod 7) + 1 \in \{1..7\}$

- Rows (for column $c \in \{0 \dots 6\}$):
  1. **Base 1 (Day)**: $R_{1, c} = ((D - 1 + c) \bmod 7) + 1$
  2. **Base 2 (Month)**: $R_{2, c} = ((M - 1 + c) \bmod 7) + 1$
  3. **Base 3 (Year)**: $R_{3, c} = ((Y - 1 + c) \bmod 7) + 1$
  4. **Base 4 (Sum)**: $R_{4, c} = R_{1, c} + R_{2, c} + R_{3, c}$
  5. **Base 5 (Derived 1)**: $R_{5, c} = ((R_{1, c} + R_{2, c} - 1) \bmod 7) + 1$
  6. **Base 6 (Derived 2)**: $R_{6, c} = ((R_{2, c} + R_{3, c} - 1) \bmod 7) + 1$
  7. **Base 7 (Derived 3)**: $R_{7, c} = ((R_{6, c} \times 2 - 1) \bmod 7) + 1$
  8. **Base 8 (Derived 4)**: $R_{8, c} = ((R_{4, c} - 1) \bmod 7) + 1$
  9. **Base 9 (Derived 5)**: $R_{9, c} = ((R_{8, c} + R_{1, c} - 1) \bmod 7) + 1$

---

## 7. Seam & Public Interface Specification (`numerology_7x9.py`)

### Pydantic Data Schemas

```python
"""
7-Digit 9-Base Numerology Engine Data Schemas
Location: omni_oracle_app/backend/app/engines/numerology_7x9.py
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class HouseType(str, Enum):
    AUSPICIOUS = "auspicious"
    INAUSPICIUS = "inauspicious"
    NEUTRAL = "neutral"


class HouseDetail7x9(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    house_name_th: str
    house_name_en: str
    row_index: int = Field(..., ge=0, le=8)
    col_index: int = Field(..., ge=0, le=6)
    digit_value: int = Field(..., ge=1, le=7)
    house_type: HouseType
    base4_power: int = Field(..., ge=3, le=21)

    @property
    def is_auspicious(self) -> bool:
        return self.house_type == HouseType.AUSPICIOUS

    @property
    def is_inauspicious(self) -> bool:
        return self.house_type == HouseType.INAUSPICIUS


class BaseCollisionInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    digit: int = Field(..., ge=1, le=7)
    count: int = Field(..., ge=1, le=9)
    houses: List[str]
    has_inauspicious_collision: bool
    has_auspicious_collision: bool
    base4_powers: List[int]
    collision_score: float


class NumerologyMatrix(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    base1_day: List[int] = Field(..., min_length=7, max_length=7)
    base2_month: List[int] = Field(..., min_length=7, max_length=7)
    base3_year: List[int] = Field(..., min_length=7, max_length=7)
    base4_sum: List[int] = Field(..., min_length=7, max_length=7)
    base5: List[int] = Field(..., min_length=7, max_length=7)
    base6: List[int] = Field(..., min_length=7, max_length=7)
    base7: List[int] = Field(..., min_length=7, max_length=7)
    base8: List[int] = Field(..., min_length=7, max_length=7)
    base9: List[int] = Field(..., min_length=7, max_length=7)
    matrix_grid: List[List[int]] = Field(..., min_length=9, max_length=9)


class Numerology7x9Result(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    birth_date: str
    day_of_week: int = Field(..., ge=1, le=7)
    day_name_th: str
    lunar_month: int = Field(..., ge=1, le=12)
    zodiac_year: int = Field(..., ge=1, le=12)
    zodiac_year_name_th: str
    matrix: NumerologyMatrix
    houses: Dict[str, HouseDetail7x9]
    collisions: Dict[int, BaseCollisionInfo]
    auspicious_houses: List[str]
    inauspicious_houses: List[str]
    primary_lucky_digits: List[int]
    secondary_lucky_digits: List[int]
    lucky_numbers: List[int]

    def get_house(self, house_name_th: str) -> Optional[HouseDetail7x9]:
        return self.houses.get(house_name_th)

    def get_digit_collision(self, digit: int) -> Optional[BaseCollisionInfo]:
        return self.collisions.get(digit)


def calculate_numerology_7x9(
    birth_date: str,
    birth_day_override: Optional[int] = None,
    lunar_month_override: Optional[int] = None,
    zodiac_year_override: Optional[int] = None,
) -> Numerology7x9Result:
    """
    Main calculation entry point for 7-Digit 9-Base Numerology Engine.
    """
    ...
```

---

## 8. Pytest Test Suite Seam Specification (`test_numerology_7x9.py`)

The Pytest suite must cover the public interface seam with tests for:
1. **`test_matrix_generation_symmetric`**: Validates Base 1 to 9 row calculation for Sunday (1), Month 1, Year 1.
2. **`test_21_house_mapping_correctness`**: Asserts that all 21 house names exist in `result.houses` and match Row 1, 2, 3 assignments.
3. **`test_house_collision_detection`**: Verifies good-bad collision detection and score flags.
4. **`test_planetary_pair_dynamics`**: Checks Base 4 column sum powers (กำลังดาว).
5. **`test_lucky_digits_extraction`**: Verifies non-empty `primary_lucky_digits`, `secondary_lucky_digits`, and `lucky_numbers`.
6. **`test_date_parsing_and_overrides`**: Verifies `birth_day_override`, `lunar_month_override`, and `zodiac_year_override`.
7. **`test_invalid_inputs`**: Verifies `ValueError` raising on malformed dates or invalid overrides out of 1..7 / 1..12.

---

## 9. Conclusion & Actionable Recommendations

- **Architecture Compliance**: The 21 House taxonomy, house collision rules, planetary pair dynamics, and lucky digit extraction algorithms are fully defined and ready for implementer execution.
- **TDD Readiness**: `test_numerology_7x9.py` interface seam contract is fully specified with strict Pydantic schemas and assertion points.
