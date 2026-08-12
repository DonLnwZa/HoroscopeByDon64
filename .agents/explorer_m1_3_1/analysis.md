# Technical Analysis Report: Burmese Mahabote Engine (มหาภูติพม่า)

**Sub-milestone:** M1.3 (Burmese Mahabote Engine)  
**Author:** Explorer 1 (`explorer_m1_3_1`)  
**Target Module:** `omni_oracle_app/backend/app/engines/mahabote.py`  
**Test Suite:** `omni_oracle_app/backend/tests/test_mahabote.py`  
**Date:** 2026-08-06  

---

## 1. Executive Summary

This report provides the full mathematical specification, algorithm design, matrix population rules, and Pydantic schemas for the **Burmese Mahabote Engine (ระบบมหาภูติพม่า)** in the Omni-Oracle lottery divination system.

The Mahabote engine is a deterministic Layer 1 calculation engine that computes:
1. **Chula Sakarat (จุลศักราช: CS)** conversion from Christian Era (AD) / Buddhist Era (BE) with Songkran (April 16) cutoff logic.
2. **Modulo 7 Remainder (CS % 7)** with 0 mapped to 7, plus symbolic Burmese remainder classification.
3. **Day of Week Mapping** (1=Sunday .. 7=Saturday).
4. **7 Body/House Positions (อัฏฐเคราะห์ / 7 ตำแหน่ง)**: อัตตะ (Atta), หินะ (Hina), ธนัง (Thanang), ปิตา (Pita), มาตา (Mata), โภคา (Phoka), มัชฌิมา (Majjhima) and anatomical 7 Phumi mapping (ตุ๊กตาไขนาม).
5. **7 Positions Matrix Population Algorithm**: Placement of planet numbers 1..7 into houses based on remainder and birth day, identification of birth house, and extraction of primary/secondary lucky lottery digits.

---

## 2. Mathematical Rules & Algorithm Requirements

### 2.1 Chula Sakarat (CS) Conversion Logic

- **Calendar Epoch Relationship**:
  - `BE (พุทธศักราช)` = `AD (คริสต์ศักราช) + 543`
  - `CS (จุลศักราช)` base formula = `BE - 1181` (or `AD - 638` for dates on or after Burmese Solar New Year).

- **Songkran Cutoff Rule (วันเถลิงศก / เมษายน 16)**:
  - In ancient Burmese and Thai solar calendars, the year turns on **April 16** (00:00:00 local time).
  - **Before April 16 (Jan 1 – Apr 15 inclusive)**: The birth date belongs to the *previous* CS year.
    $$\text{CS} = \text{BE} - 1182 = \text{AD} - 639$$
  - **On or after April 16 (Apr 16 – Dec 31 inclusive)**: The birth date belongs to the *current* CS year.
    $$\text{CS} = \text{BE} - 1181 = \text{AD} - 638$$

#### Boundary Examples & Verification Vectors:
| Date (ISO) | BE | Cutoff Condition | CS Formula | CS Result |
|------------|----|------------------|------------|-----------|
| `1990-01-01` | 2533 | Jan 1 < Apr 16 | 2533 - 1182 | 1351 |
| `1990-04-15` | 2533 | Apr 15 < Apr 16 | 2533 - 1182 | 1351 |
| `1990-04-16` | 2533 | Apr 16 >= Apr 16 | 2533 - 1181 | 1352 |
| `1990-12-31` | 2533 | Dec 31 >= Apr 16 | 2533 - 1181 | 1352 |
| `2000-04-15` | 2543 | Apr 15 < Apr 16 | 2543 - 1182 | 1361 |
| `2000-04-16` | 2543 | Apr 16 >= Apr 16 | 2543 - 1181 | 1362 |

---

### 2.2 Modulo 7 Remainder Calculation

- **Formula**:
  $$\text{raw\_remainder} = \text{CS} \bmod 7$$
  $$\text{remainder} = \begin{cases} 7 & \text{if } \text{raw\_remainder} = 0 \\ \text{raw\_remainder} & \text{otherwise} \end{cases}$$
- **Output Domain**: Integer set $\{1, 2, 3, 4, 5, 6, 7\}$.

#### Symbolic Remainder Names in Burmese Mahabote:
1. **เศษ 1**: อังคาสะ (Aka)
2. **เศษ 2**: อพยยะ (Abhaya)
3. **เศษ 3**: ยันตะ (Yanta)
4. **เศษ 4**: มังคละ (Mangala)
5. **เศษ 5**: อธิบดี (Adhipati)
6. **เศษ 6**: ราชา (Raja)
7. **เศษ 7 (0)**: มรณะ / กุมภะ (Marana / Kumbha)

---

### 2.3 Day of Week Mapping

- **Standard Thai/Burmese Planetary Day Mapping**:
  - Sunday (วันอาทิตย์) = **1** (☀️ อาทิตย์)
  - Monday (วันจันทร์) = **2** (🌙 จันทร์)
  - Tuesday (วันอังคาร) = **3** (🔴 อังคาร)
  - Wednesday (วันพุธ) = **4** (🟢 พุธ)
  - Thursday (วันพฤหัสบดี) = **5** (🟠 พฤหัสบดี)
  - Friday (วันศุกร์) = **6** (🔵 ศุกร์)
  - Saturday (วันเสาร์) = **7** (🟣 เสาร์)

- **Python Implementation**:
  Python `date.weekday()` returns `0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun`.
  Mapping algorithm:
  ```python
  DAY_OF_WEEK_MAP = {
      0: 2,  # Mon -> 2
      1: 3,  # Tue -> 3
      2: 4,  # Wed -> 4
      3: 5,  # Thu -> 5
      4: 6,  # Fri -> 6
      5: 7,  # Sat -> 7
      6: 1,  # Sun -> 1
  }
  day_of_week = DAY_OF_WEEK_MAP[dt.weekday()]
  ```

---

### 2.4 7 Body Positions (อัฏฐเคราะห์ / 7 ตำแหน่ง)

The Mahabote Engine models the 7 primary life houses (เรือนมหาภูติพม่า 7 ตำแหน่ง):

| # | House Name (TH) | House Name (EN) | Astrological Aspect & Meaning | Classification |
|---|-----------------|-----------------|--------------------------------|----------------|
| 1 | **อัตตะ** | Atta | Self, Mind, Character, Identity (ตัวตน, วาสนา, สรีระ) | Auspicious (เรือนดี) |
| 2 | **หินะ** | Hina | Flaw, Weakness, Obstacle, Loss (ความบกพร่อง, อุปสรรค, หายนะ) | Inauspicious (เรือนเสีย) |
| 3 | **ธนัง** | Thanang | Wealth, Cash Flow, Earnings, Income (ทรัพย์สิน, รายได้, เงินทอง) | Auspicious (เรือนดี) |
| 4 | **ปิตา** | Pita | Father, Senior Male, Authority, Boss (บิดา, ผู้ใหญ่ชาย, ผู้บังคับบัญชา) | Auspicious (เรือนดี) |
| 5 | **มาตา** | Mata | Mother, Female Patron, Caregiver (มารดา, ผู้ใหญ่หญิง, ผู้ให้อุปถัมภ์) | Auspicious (เรือนดี) |
| 6 | **โภคา** | Phoka | Property, Real Estate, Land, Assets (อสังหาริมทรัพย์, ที่ดิน, ความอุดมสมบูรณ์) | Auspicious (เรือนดี) |
| 7 | **มัชฌิมา** | Majjhima | Moderation, Neutrality, Balance, Stability (ทางสายกลาง, ความสม่ำเสมอ, เป็นกลาง) | Neutral/Auspicious |

#### Anatomical 7 Phumi Mapping (ตุ๊กตาไขนาม):
1. **ภังคะ (Bhangkha)** — Right Leg (ขาขวา)
2. **ปูติ (Puti)** — Left Leg (ขาซ้าย)
3. **มรณะ (Marana)** — Left Waist (เอวซ้าย)
4. **อธิบดี (Adhipati)** — Left Arm (แขนซ้าย)
5. **ราชา (Raja)** — Head (ศีรษะ)
6. **อัตตะ (Atta)** — Right Arm (แขนขวา)
7. **มัชฌิมา (Majjhima)** — Right Waist (เอวขวา)

---

### 2.5 Matrix Population & House Mapping Algorithm

The 7 house positions in Mahabote are arranged in fixed order:
$$\text{HOUSES} = [\text{"ธนัง"}, \text{"ปิตา"}, \text{"มาตา"}, \text{"โภคา"}, \text{"มัชฌิมา"}, \text{"อัตตะ"}, \text{"หินะ"}]$$

#### Matrix Population Steps:
1. **Compute CS & Remainder $R$** ($R \in \{1..7\}$).
2. **Sequential Planet Digit Assignment**:
   Starting with remainder $R$ at house 1 ($\text{ธนัง}$), each house $i$ ($0 \le i < 7$) is populated with planet digit:
   $$\text{digit}_i = ((R - 1 + i) \bmod 7) + 1$$

   *Example*: If $R = 4$:
   - $\text{ธนัง (Thanang)} = 4$
   - $\text{ปิตา (Pita)} = 5$
   - $\text{มาตา (Mata)} = 6$
   - $\text{โภคา (Phoka)} = 7$
   - $\text{มัชฌิมา (Majjhima)} = 1$
   - $\text{อัตตะ (Atta)} = 2$
   - $\text{หินะ (Hina)} = 3$

3. **Identify Birth House**:
   Given user's birth day $D \in \{1..7\}$ (1=Sun .. 7=Sat), locate the house $H$ where $\text{digit}_H = D$.
   That house $H$ is marked as `is_birth_house = True`.

4. **Lottery Digits Extraction Logic**:
   - **Primary Lucky Digits**: Digits placed in financial powerhouses $\text{ธนัง (Thanang)}$ and $\text{โภคา (Phoka)}$.
   - **Secondary Lucky Digits**: Digits placed in $\text{อัตตะ (Atta)}$, $\text{ปิตา (Pita)}$, $\text{มาตา (Mata)}$, and $\text{มัชฌิมา (Majjhima)}$.
   - **Avoid Digits (Unlucky/Risk)**: Digit placed in $\text{หินะ (Hina)}$.

---

## 3. Codebase Inspection Findings

An audit of `omni_oracle_app/backend` revealed:
- `omni_oracle_app/backend/app/engines/thai_astrology.py` — Complete (Lahiri Ayanamsa natal chart).
- `omni_oracle_app/backend/app/engines/numerology_7x9.py` — Complete (7-digit 9-base matrix engine).
- `omni_oracle_app/backend/app/engines/mahabote.py` — **Not yet implemented** (Target for M1.3 implementation).
- `omni_oracle_app/backend/tests/test_mahabote.py` — **Not yet created** (Target Pytest seam test suite).

The design of `mahabote.py` must follow Pydantic v2 schemas (`BaseModel`, `Field`, `ConfigDict`) matching the architecture established in `numerology_7x9.py`.

---

## 4. Proposed Pydantic Data Models & Interface Specification

```python
"""
Burmese Mahabote Engine (มหาภูติพม่า)
Module: app.engines.mahabote
Layer 1 Core Calculation Engine for Omni-Oracle Thai Divination System.
"""

from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class MahaboteHouseType(str, Enum):
    AUSPICIOUS = "auspicious"
    INAUSPICIUS = "inauspicious"
    NEUTRAL = "neutral"


class MahaboteHouseDetail(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    house_name_th: str
    house_name_en: str
    position_index: int = Field(..., ge=0, le=6)
    digit_value: int = Field(..., ge=1, le=7)
    house_type: MahaboteHouseType
    description_th: str
    is_birth_house: bool = False

    @property
    def is_auspicious(self) -> bool:
        return self.house_type == MahaboteHouseType.AUSPICIOUS

    @property
    def is_inauspicious(self) -> bool:
        return self.house_type == MahaboteHouseType.INAUSPICIUS


class MahaboteMatrix(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cs_year: int
    cs_remainder: int = Field(..., ge=1, le=7)
    day_of_week: int = Field(..., ge=1, le=7)
    houses: Dict[str, MahaboteHouseDetail]
    house_order: List[str] = Field(..., min_length=7, max_length=7)
    grid_matrix: List[List[int]] = Field(..., min_length=3, max_length=3)


class MahaboteResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    birth_date: str
    is_before_songkran: bool
    buddhist_era: int
    chula_sakarat: int
    cs_remainder: int = Field(..., ge=1, le=7)
    remainder_name_th: str
    day_of_week: int = Field(..., ge=1, le=7)
    day_name_th: str
    birth_house_name: str

    matrix: MahaboteMatrix
    primary_lucky_digits: List[int]
    secondary_lucky_digits: List[int]
    avoid_digits: List[int]
    recommended_lottery_digits: List[int]
```

### Engine Seam Function Signature
```python
def calculate_mahabote(
    birth_date: Union[str, date, datetime],
    day_of_week_override: Optional[int] = None,
) -> MahaboteResult:
    """
    Computes Burmese Mahabote calculation for a given birth date.
    
    Args:
        birth_date: ISO date string ("YYYY-MM-DD"), date, or datetime object.
        day_of_week_override: Optional explicit day of week (1=Sun .. 7=Sat).
        
    Returns:
        MahaboteResult: Structured calculation result.
    """
```

---

## 5. Verification & Test Plan

1. **Unit Test Suite (`test_mahabote.py`)**:
   - `test_data_models_and_enums()`: Validate Pydantic fields, defaults, properties.
   - `test_chula_sakarat_songkran_cutoff()`: Verify Apr 15 vs Apr 16 cutoff across multiple years (e.g. 1990, 2000, 2026).
   - `test_modulo_7_remainder_zero_handling()`: Verify remainder 0 becomes 7.
   - `test_day_of_week_mapping()`: Verify Sun=1 .. Sat=7.
   - `test_7_positions_matrix_population()`: Verify fixed house order and digit rotation.
   - `test_lucky_digits_extraction()`: Verify primary/secondary/avoid digit lists.
   - `test_invalid_inputs()`: Verify error handling for invalid date strings.

2. **Pytest Run Command**:
   ```powershell
   pytest omni_oracle_app/backend/tests/test_mahabote.py -v
   ```
