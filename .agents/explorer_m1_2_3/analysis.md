# Technical Analysis: Sub-milestone M1.2 — 7-Digit 9-Base Numerology Engine

## 1. Overview & Core Objectives

The 7-Digit 9-Base Numerology Engine (`omni_oracle_app/backend/app/engines/numerology_7x9.py`) is Layer 1's core deterministic numerology calculation module. It is responsible for calculating:

1. **7 Columns x 9 Rows Matrix Generation (`NumerologyMatrix`)**:
   - **Base 1 (Day Base / ฐานวัน)**: 7-column sequence starting from day of week (1=Sun .. 7=Sat), wrapping 1..7.
   - **Base 2 (Month Base / ฐานเดือน)**: 7-column sequence starting from Thai lunar month (1..12 mapped to 1..7), wrapping 1..7.
   - **Base 3 (Year Base / ฐานปี)**: 7-column sequence starting from Thai zodiac year (1=Rat .. 12=Pig mapped to 1..7), wrapping 1..7.
   - **Base 4 (Sum Base / ฐานรวม)**: Vertical column sum of Base 1 + Base 2 + Base 3 (range 3..21, representing planetary power / กำลังดาว).
   - **Bases 5 to 9 (Derived Bases / ฐานที่ 5-9)**: Deterministic secondary and tertiary mathematical expansions.

2. **21 Astrological Houses Mapping (`HouseDetail7x9`)**:
   - Row 1 (Day Base): 7 houses (**อัตตะ, หินะ, ธนัง, ปิตา, มาตา, โภคา, มัชฌิมา**)
   - Row 2 (Month Base): 7 houses (**ตะนุ, กดุมภะ, สหัชชะ, พันธุ, ปุตตะ, อริ, ปัตนิ**)
   - Row 3 (Year Base): 7 houses (**มรณะ, ศุภะ, กัมมะ, ลาภะ, พยายะ, ทาสา, ทาสี**)
   - Expanded Base 8/9: 7 extra houses (**อาตมะ, ทาสา/ทาสี, สิทธิโชค, โจร, อุบาทว์, อุปถัมภ์, เคหัง**)

3. **Collision & Dignity Analysis (`BaseCollisionInfo`)**:
   - Detect digit collisions (การชนฐาน) across rows 1-3.
   - Flag auspicious collisions (multi-house overlap in กดุมภะ, ลาภะ, ธนัง, ศุภะ) vs inauspicious collisions (overlap in หินะ, อริ, มรณะ, พยายะ, โจร, อุบาทว์).

4. **Public Interface & Pytest Seam**:
   - High-trust Pydantic data schemas (`Numerology7x9Result`, `NumerologyMatrix`, `HouseDetail7x9`, `BaseCollisionInfo`, `HouseType`).
   - Single calculation entry point: `calculate_numerology_7x9(...)`.

---

## 2. Mathematical & Astrological Specifications

### 2.1 Matrix Generation Formulas

Given inputs:
- `day_num`: Day of week (1 = Sunday, 2 = Monday, ..., 7 = Saturday).
- `lunar_month_num`: Thai lunar month (1..12).
- `zodiac_year_num`: Thai zodiac year (1..12).

#### Row Normalization (1..7 Scale):
- Day value $D = \text{day\_num} \in \{1 \dots 7\}$
- Month value $M = ((\text{lunar\_month\_num} - 1) \bmod 7) + 1 \in \{1 \dots 7\}$
- Year value $Y = ((\text{zodiac\_year\_num} - 1) \bmod 7) + 1 \in \{1 \dots 7\}$

#### Row 1 to 9 Generation (Column $c \in \{0 \dots 6\}$):
1. **Base 1 (Day)**: $R_{1, c} = ((D - 1 + c) \bmod 7) + 1$
2. **Base 2 (Month)**: $R_{2, c} = ((M - 1 + c) \bmod 7) + 1$
3. **Base 3 (Year)**: $R_{3, c} = ((Y - 1 + c) \bmod 7) + 1$
4. **Base 4 (Sum / กำลังดาว)**: $R_{4, c} = R_{1, c} + R_{2, c} + R_{3, c} \in \{3 \dots 21\}$
5. **Base 5 (Derived 1)**: $R_{5, c} = ((R_{1, c} + R_{2, c} - 1) \bmod 7) + 1$
6. **Base 6 (Derived 2)**: $R_{6, c} = ((R_{2, c} + R_{3, c} - 1) \bmod 7) + 1$
7. **Base 7 (Derived 3)**: $R_{7, c} = ((R_{6, c} \times 2 - 1) \bmod 7) + 1$
8. **Base 8 (Derived 4 - Base 4 mod 7)**: $R_{8, c} = ((R_{4, c} - 1) \bmod 7) + 1$
9. **Base 9 (Derived 5 - Base 8 + Base 1)**: $R_{9, c} = ((R_{8, c} + R_{1, c} - 1) \bmod 7) + 1$

---

### 2.2 The 21 Astrological Houses Taxonomy

| Row Index | Column (0 to 6) | House Name (TH) | House Name (EN) | Category | Description |
|---|---|---|---|---|---|
| **Row 1** | 0 | อัตตะ | Atta | Neutral | Self, Personality, Outward Ego |
| | 1 | หินะ | Hina | Inauspicious | Degradation, Flaw, Sudden Downfall |
| | 2 | ธนัง | Thanang | Auspicious | Accumulated Wealth, Liquid Assets |
| | 3 | ปิตา | Pita | Neutral | Father, Senior Male Figures |
| | 4 | มาตา | Mata | Neutral | Mother, Senior Female Figures |
| | 5 | โภคา | Bhoga | Auspicious | Real Estate, Fixed Assets, Property |
| | 6 | มัชฌิมา | Majjhima | Neutral | Moderation, Neutral Ground |
| **Row 2** | 0 | ตะนุ | Tanu | Neutral | Physical Body, Core Mind |
| | 1 | กดุมภะ | Kadumba | Auspicious | Income, Earning Capacity, Money |
| | 2 | สหัชชะ | Sahajja | Neutral | Friends, Companions, Networking |
| | 3 | พันธุ | Bandhu | Auspicious | Family, Household Stability |
| | 4 | ปุตตะ | Putta | Auspicious | Children, Speculation, New Risk |
| | 5 | อริ | Ari | Inauspicious | Enemies, Debt, Obstacles |
| | 6 | ปัตนิ | Patni | Auspicious | Spouse, Business Partner |
| **Row 3** | 0 | มรณะ | Marana | Inauspicious | Loss, Overseas, Transformation |
| | 1 | ศุภะ | Subha | Auspicious | Prosperity, Virtue, High Favor |
| | 2 | กัมมะ | Kamma | Auspicious | Career, Public Duty, Action |
| | 3 | ลาภะ | Lapha | Auspicious | Sudden Gain, Fortune, Windfall |
| | 4 | พยายะ | Phayaya | Inauspicious | Secret Enemies, Hidden Illness |
| | 5 | ทาสา | Thasa | Neutral | Male Servants, Subordinates |
| | 6 | ทาสี | Thasi | Neutral | Female Servants, Subordinates |

---

## 3. Seam & Public Interface Design

### Data Models (`omni_oracle_app/backend/app/engines/numerology_7x9.py`)

```python
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class HouseType(str, Enum):
    AUSPICIOUS = "auspicious"      # ภพดี
    INAUSPICIUS = "inauspicious"    # ภพเสีย / ภพเสื่อม
    NEUTRAL = "neutral"            # ภพกลาง

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
```

### Public Seam Entry Point

```python
def calculate_numerology_7x9(
    birth_date: str,
    birth_day_override: Optional[int] = None,
    lunar_month_override: Optional[int] = None,
    zodiac_year_override: Optional[int] = None,
) -> Numerology7x9Result:
    ...
```

---

## 4. Edge Cases & Input Validation Matrix

| Edge Case / Input | Validation / Derivation Rule | Exception / Fallback Behavior |
|---|---|---|
| `birth_date` format | Must match `YYYY-MM-DD` | Raise `ValueError("Invalid birth date format. Expected YYYY-MM-DD.")` |
| `birth_date` range | Year between 1900 and 2100 | Raise `ValueError("Birth date out of valid range (1900-2100).")` |
| Day of Week derivation | ISO `dt.weekday()` (Mon=0..Sun=6) -> Thai (Sun=1..Sat=7) | Formula: `(dt.weekday() + 1) % 7 + 1` |
| `birth_day_override` | Must be integer 1..7 | Raise `ValueError("birth_day_override must be between 1 and 7")` |
| `lunar_month_override` | Must be integer 1..12 | Raise `ValueError("lunar_month_override must be between 1 and 12")` |
| Lunar Month fallback | No override provided | Auto-fallback to solar month: `lunar_month = dt.month` |
| `zodiac_year_override` | Must be integer 1..12 | Raise `ValueError("zodiac_year_override must be between 1 and 12")` |
| Zodiac Year fallback | No override provided | Auto-fallback formula: `zodiac_year = ((dt.year - 4) % 12) + 1` |

---

## 5. Unit Test Benchmark Scenarios

### Benchmark 1: Sunday / Month 1 / Year 1 Override (Symmetric Test Case)
- **Inputs**: `birth_date="2000-01-01"`, `birth_day_override=1` (Sunday), `lunar_month_override=1` (Month 1), `zodiac_year_override=1` (Rat / 1).
- **Expected Base 1**: `[1, 2, 3, 4, 5, 6, 7]`
- **Expected Base 2**: `[1, 2, 3, 4, 5, 6, 7]`
- **Expected Base 3**: `[1, 2, 3, 4, 5, 6, 7]`
- **Expected Base 4 (Sum)**: `[3, 6, 9, 12, 15, 18, 21]`
- **Verifications**:
  - `res.matrix.base4_sum == [3, 6, 9, 12, 15, 18, 21]`
  - Collisions for digit 1: Appears in Col 0 in all 3 rows (Houses: อัตตะ, ตะนุ, มรณะ).
  - Since digit 1 touches มรณะ, `has_inauspicious_collision == True`.

### Benchmark 2: Realistic Sample Date Verification (`1995-08-15`)
- **Inputs**: `birth_date="1995-08-15"`, `lunar_month_override=8`, `zodiac_year_override=12` (กุน - Pig).
- **Derived Day**: Tuesday (Day 3).
- **Normalized Values**: Day 3, Month `(8-1)%7+1 = 1`, Year `(12-1)%7+1 = 5`.
- **Base 1**: `[3, 4, 5, 6, 7, 1, 2]`
- **Base 2**: `[1, 2, 3, 4, 5, 6, 7]`
- **Base 3**: `[5, 6, 7, 1, 2, 3, 4]`
- **Base 4 (Sum)**: `[9, 12, 15, 11, 14, 10, 13]`
- **Verifications**:
  - Digit 7 appears in Col 4 (Base 1: มาตา), Col 6 (Base 2: ปัตนิ), Col 2 (Base 3: กัมมะ).
  - All 3 collided houses for digit 7 are non-inauspicious -> `has_auspicious_collision == True`, `has_inauspicious_collision == False`.
  - Digit 7 ranks high in `lucky_numbers`.

---

## 6. Summary for Downstream Implementation (M1.2 Seam)

The TDD Pytest suite `test_numerology_7x9.py` should be authored first to assert:
1. Enum values (`HouseType`).
2. Pydantic schema structure and property getters.
3. Seam calculation results for Benchmark 1 and Benchmark 2.
4. Exception raising on invalid dates and out-of-bounds overrides.
5. Extraction of clean, ordered `lucky_numbers` for Layer 2 Composite Recommender.
