# Analysis Report: Public Seam & TDD Pytest Architecture for Burmese Mahabote Engine (Sub-milestone M1.3)

**Author:** Explorer 3 (`explorer_m1_3_3`)  
**Target Module:** `omni_oracle_app/backend/app/engines/mahabote.py`  
**Target Test File:** `omni_oracle_app/backend/tests/test_mahabote.py`  
**Date:** 2026-08-06  

---

## 1. Executive Summary

This report defines the public seam interface and Test-Driven Development (TDD) architecture for the **Burmese Mahabote Divination Engine (มหาภูติพม่า)** in `omni_oracle_app/backend/app/engines/mahabote.py`.

The design ensures 100% architectural consistency with the existing Layer 1 divination engines (`numerology_7x9.py` and `thai_astrology.py`), using Pydantic `BaseModel` schemas for strict validation and JSON serialization. The seam supports both class-based execution via `MahaboteEngine` and functional entry via `calculate_mahabote()`.

---

## 2. Architecture & File Seams

### 2.1 File Placement
- **Engine Implementation:** `omni_oracle_app/backend/app/engines/mahabote.py`
- **Pytest Suite:** `omni_oracle_app/backend/tests/test_mahabote.py`

### 2.2 Integration Seam
```
                          [ Input Intake ]
                 (birth_date, birth_time, is_wednesday_night)
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │  calculate_mahabote   │ (Public Function Seam)
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │    MahaboteEngine     │ (Core Engine Class)
                     └───────────┬───────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
[Chula Sakarat]          [7 Body Positions]         [Taksa & Kalayok]
(CS % 7 -> Remainder)    (Atta, Hina, Thanang...)    (Sri, Kalakini, Thongchai)
     │                           │                           │
     └───────────────────────────┼───────────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │     MahaboteResult      │ (Pydantic Output Schema)
                    └─────────────────────────┘
```

---

## 3. Class & Function Contracts

### 3.1 Pydantic Data Models & Enums

#### Enums
```python
from enum import Enum

class DayOfWeek(int, Enum):
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY_DAY = 4
    JUPITER = 5
    VENUS = 6
    SATURN = 7
    WEDNESDAY_NIGHT = 8  # Rahu (พุธกลางคืน 18:00 - 05:59)

class MahabotePositionEnum(str, Enum):
    ATTA = "atta"          # อัตตะ (Self / Character)
    HINA = "hina"          # หินะ (Obstacle / Flaw)
    THANANG = "thanang"    # ธนัง (Wealth / Asset)
    PITA = "pita"          # ปิตา (Father / Patron)
    MATA = "mata"          # มาตา (Mother / Nurture)
    PHOKA = "phoka"        # โภคา (Property / Estate)
    MATCHIMA = "matchima"  # มัชฌิมา (Middle / Balance)

class TaksaCategory(str, Enum):
    BRIVAR = "บริวาร"
    AYU = "อายุ"
    DECH = "เดช"
    SRI = "ศรี"
    MULA = "มูละ"
    INDUSTAH = "อุตสาหะ"
    MONTRII = "มนตรี"
    KALAKINI = "กาลกิณี"

class KalayokCategory(str, Enum):
    THONGCHAI = "ธงชัย"
    ATIPATI = "อธิบดี"
    YAMABAT = "อุบาทว์"
    LOKAVINAS = "โลกาวินาศ"
```

#### Output Schemas
```python
from typing import Dict, List, Optional, Union
from datetime import date, time, datetime
from pydantic import BaseModel, Field, ConfigDict

class PositionDetail(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    position_key: str  # e.g., "atta", "hina"
    position_name_th: str  # e.g., "อัตตะ"
    position_name_en: str  # e.g., "Atta"
    planet_digit: int = Field(..., ge=1, le=7)
    planet_name_th: str  # e.g., "อาทิตย์"
    taksa_category: str  # e.g., "ศรี", "กาลกิณี"
    is_kalayok_auspicious: bool
    is_kalayok_inauspicious: bool

class MahaboteChart(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cs_year: int
    cs_remainder: int = Field(..., ge=1, le=7)
    birth_day_digit: int = Field(..., ge=1, le=8)
    positions: Dict[str, PositionDetail]
    chart_matrix: List[List[int]]  # 3-row traditional layout grid
    position_order: List[str] = [
        "atta", "hina", "thanang", "pita", "mata", "phoka", "matchima"
    ]

class TaksaPlanetDetail(BaseModel):
    planet_digit: int = Field(..., ge=1, le=8)
    planet_name_th: str
    category: str
    is_kalakini: bool
    is_sri: bool

class TaksaInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    birth_day_digit: int = Field(..., ge=1, le=8)
    brivar_planet: int
    sri_planet: int
    kalakini_planet: int
    taksa_map: Dict[int, str]
    planets: List[TaksaPlanetDetail]

class KalayokInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cs_year: int
    thongchai_digit: int = Field(..., ge=1, le=7)
    atipati_digit: int = Field(..., ge=1, le=7)
    yamabat_digit: int = Field(..., ge=1, le=7)
    lokavinas_digit: int = Field(..., ge=1, le=7)

class LuckyDigitsResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    primary_digits: List[int]
    secondary_digits: List[int]
    avoid_digits: List[int]
    recommended_2digit_pairs: List[str]
    power_score: float = Field(..., ge=0.0, le=100.0)

class MahaboteResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    birth_date: str  # "YYYY-MM-DD"
    birth_time: Optional[str] = None  # "HH:MM"
    is_wednesday_night: bool = False
    songkran_adjusted: bool = False
    cs_year: int
    cs_remainder: int
    day_of_week: int
    day_name_th: str
    chart: MahaboteChart
    taksa: TaksaInfo
    kalayok: KalayokInfo
    lucky_digits: LuckyDigitsResult
```

---

### 3.2 Public Function & Class Seams

#### Core Class Contract: `MahaboteEngine`
```python
class MahaboteEngine:
    """Core calculation engine for Burmese Mahabote."""

    SONGKRAN_CUTOFF_MONTH: int = 4
    SONGKRAN_CUTOFF_DAY: int = 16
    CS_OFFSET: int = 638

    @classmethod
    def calculate_cs(cls, birth_date: date) -> Tuple[int, bool]:
        """Calculates CS year considering April 16 Songkran boundary."""
        ...

    @classmethod
    def calculate_cs_remainder(cls, cs_year: int) -> int:
        """Calculates CS % 7, mapping remainder 0 to 7."""
        ...

    @classmethod
    def determine_day_of_week(
        cls,
        dt: date,
        birth_time: Optional[time] = None,
        is_wednesday_night: Optional[bool] = None
    ) -> DayOfWeek:
        """Determines day digit 1..8 including Wednesday day/night logic."""
        ...

    @classmethod
    def build_chart(cls, cs_remainder: int, day_digit: int) -> MahaboteChart:
        """Constructs 7-position Mahabote chart."""
        ...

    @classmethod
    def calculate_taksa(cls, day_digit: int) -> TaksaInfo:
        """Calculates 8-planet Taksa alignment."""
        ...

    @classmethod
    def calculate_kalayok(cls, cs_year: int) -> KalayokInfo:
        """Calculates annual Kalayok positions."""
        ...

    @classmethod
    def extract_lucky_digits(
        cls,
        chart: MahaboteChart,
        taksa: TaksaInfo,
        kalayok: KalayokInfo
    ) -> LuckyDigitsResult:
        """Extracts primary, secondary, avoid digits, 2-digit pairs and power score."""
        ...

    def execute(
        self,
        birth_date: Union[str, date],
        birth_time: Optional[Union[str, time]] = None,
        is_wednesday_night: Optional[bool] = None
    ) -> MahaboteResult:
        """Main execution seam."""
        ...
```

#### Standalone Seam Contract: `calculate_mahabote`
```python
def calculate_mahabote(
    birth_date: Union[str, date],
    birth_time: Optional[Union[str, time]] = None,
    is_wednesday_night: Optional[bool] = None
) -> MahaboteResult:
    """Public seam entry point for pytest suite and FastAPI endpoints."""
    engine = MahaboteEngine()
    return engine.execute(
        birth_date=birth_date,
        birth_time=birth_time,
        is_wednesday_night=is_wednesday_night
    )
```

---

## 4. Input Processing & Type Flexibility

1. **`birth_date` Flexibility:**
   - Accepts `"YYYY-MM-DD"`, `datetime.date`, or `datetime.datetime`.
   - String inputs are parsed using standard `date.fromisoformat()` or `datetime.strptime(val, "%Y-%m-%d")`.
   - Invalid formats (e.g. `"15/08/1995"`, `"2024-02-30"`, `""`, `None`) raise `ValueError` with explicit message.

2. **`birth_time` Processing:**
   - Accepts `None`, `"HH:MM"`, `"HH:MM:SS"`, or `datetime.time`.
   - If `birth_date` is Wednesday (`day_of_week == 4`):
     - `06:00` to `17:59` -> Wednesday Day (`DayOfWeek.WEDNESDAY_DAY = 4`).
     - `18:00` to `05:59` -> Wednesday Night (`DayOfWeek.WEDNESDAY_NIGHT = 8`).
   - If `birth_time` is `None` for Wednesday, defaults to `is_wednesday_night` parameter (or `False` if not provided).

3. **`is_wednesday_night` Explicit Flag:**
   - Boolean override flag. When set to `True` for a Wednesday birth date, forces `day_digit = 8` (Rahu).

---

## 5. Key Edge Cases & Boundary Conditions

| # | Edge Case Category | Condition | Required Engine Behavior |
|---|-------------------|-----------|--------------------------|
| 1 | **Songkran Cutoff (April 15)** | Birth on April 15, 2024 | Belongs to PREVIOUS CS year: `CS = 2024 - 639 = 1385`. `songkran_adjusted = True`. |
| 2 | **Songkran Cutoff (April 16)** | Birth on April 16, 2024 | Belongs to CURRENT CS year: `CS = 2024 - 638 = 1386`. `songkran_adjusted = False`. |
| 3 | **CS Modulo 7 Remainder 0** | CS year where `CS % 7 == 0` (e.g. CS 1386) | Remainder `0` MUST be mapped to **`7`** (Saturn root). Remainder cannot be `0`. |
| 4 | **Leap Year Handling** | Birth on `2024-02-29` | Valid leap day. Parsed correctly. |
| 5 | **Invalid Leap Day** | Birth on `2023-02-29` | Non-leap year. Raises `ValueError`. |
| 6 | **Century Boundaries** | Birth on `1900-01-01` vs `2000-01-01` | CS calculated correctly across century transitions. |
| 7 | **Wednesday Boundary (17:59 vs 18:00)** | Wednesday 17:59 vs 18:00 | 17:59 -> Day (`4`); 18:00 -> Night (`8`). |
| 8 | **Malformed Input** | `birth_date = "invalid"` or `None` | Raises `ValueError` / `TypeError`. |

---

## 6. Strict TDD Pytest Architecture for Worker

The worker implementer will implement `omni_oracle_app/backend/tests/test_mahabote.py` containing 7 test tiers:

```python
"""
Pytest Unit Test Suite for Burmese Mahabote Engine (M1.3)
Target Module: app.engines.mahabote
Strict TDD: RED -> GREEN -> REFACTOR
"""

import pytest
from datetime import date, time
from app.engines.mahabote import (
    calculate_mahabote,
    MahaboteEngine,
    MahaboteResult,
    MahaboteChart,
    TaksaInfo,
    KalayokInfo,
    LuckyDigitsResult,
    PositionDetail,
    DayOfWeek,
    MahabotePositionEnum,
    TaksaCategory,
    KalayokCategory,
)

# Tier 1: Enums & Data Models
def test_data_models_and_enums():
    """Verify all Enums and Pydantic Data Models validate attributes and bounds correctly."""
    ...

# Tier 2: Standard Public Seam
def test_calculate_mahabote_valid_input():
    """Verify calculate_mahabote returns a valid MahaboteResult structure."""
    ...

# Tier 3: Songkran Boundary Cutoff
@pytest.mark.parametrize("input_date, expected_cs, expected_adjusted", [
    ("2024-04-15", 1385, True),
    ("2024-04-16", 1386, False),
    ("1995-04-15", 1356, True),
    ("1995-04-16", 1357, False),
])
def test_songkran_boundary_cutoff(input_date, expected_cs, expected_adjusted):
    """Verify April 15 vs April 16 Songkran cutoff adjusts CS year correctly."""
    ...

# Tier 4: CS Remainder 0 -> 7 Mapping
def test_cs_remainder_zero_mapping():
    """Verify CS remainder equal to 0 is mapped to 7."""
    ...

# Tier 5: Wednesday Day vs Night Distinction
@pytest.mark.parametrize("birth_time, is_night_flag, expected_day_digit", [
    ("10:00", None, 4),
    ("17:59", None, 4),
    ("18:00", None, 8),
    ("22:00", None, 8),
    (None, True, 8),
    (None, False, 4),
])
def test_wednesday_day_night_distinction(birth_time, is_night_flag, expected_day_digit):
    """Verify Wednesday birth time or flag assigns day digit 4 vs 8."""
    ...

# Tier 6: Invalid Inputs & Error Handling
@pytest.mark.parametrize("invalid_date", [
    "invalid-date",
    "15-08-1995",
    "2023-02-29",
    "2024-04-31",
    "",
    None,
])
def test_invalid_inputs_raise_errors(invalid_date):
    """Verify malformed date strings raise ValueError or TypeError."""
    ...

# Tier 7: Internal Engine Class Methods
def test_engine_class_methods():
    """Verify individual classmethods of MahaboteEngine function independently."""
    ...
```

---

## 7. Verification & Sign-off

- Code structure adheres to 3-Layer architecture and `PROJECT.md`.
- Seam contracts match `numerology_7x9.py` and `thai_astrology.py` design patterns.
- Ready for Worker to implement TDD Red tests and Green engine implementation.
