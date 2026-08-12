# Requirements & TDD Seam Analysis Report: Thai Astrology Engine (M1.1)

**Target Module:** `omni_oracle_app/backend/app/engines/thai_astrology.py`  
**Target Test Suite:** `omni_oracle_app/backend/tests/test_thai_astrology.py`  
**Author:** Explorer 3 (Sub-milestone M1.1)  
**Date:** 2026-08-06  

---

## 1. Executive Summary

The Thai Astrology Engine (`thai_astrology.py`) forms a core deterministic calculation module in Layer 1 of the Omni-Oracle Architecture. It computes natal planetary positions using the **Sidereal Zodiac (Lahiri Ayanamsa)**, 12 Astrological Houses (ภพทั้ง 12), Divisional Charts (D9 Navamsa นวางค์จักร & D3 Drekkana ตรียางค์จักร), planetary dignities (เกษตร, อุจจ์, นิจ, ประ), and extracts key planetary digits (0–9) for downstream consumption by the Layer 2 Composite Lottery Recommender.

This report establishes the **Strict TDD Seam Specifications**, edge case handling policies, benchmark verification test cases, and Layer 2 integration schema required to write test cases in `test_thai_astrology.py` before source code implementation begins.

---

## 2. Public Interface & TDD Seam Design

To enforce strict Red-Green-Refactor TDD, the public interface of `thai_astrology.py` must expose strongly-typed dataclasses, enumerations, and pure calculation functions.

### 2.1 Enumerations & Type Definitions

```python
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import date, time

class ThaiPlanet(IntEnum):
    URANUS = 0     # มฤตยู (0)
    SUN = 1        # อาทิตย์ (1)
    MOON = 2       # จันทร์ (2)
    MARS = 3       # อังคาร (3)
    MERCURY = 4    # พุธ (4)
    JUPITER = 5    # พฤหัสบดี (5)
    VENUS = 6      # ศุกร์ (6)
    SATURN = 7     # เสาร์ (7)
    RAHU = 8       # ราหู (8)
    KETU = 9       # เกตุไทย (9)

class ZodiacSign(IntEnum):
    ARIES = 1        # ราศีเมษ (0° - 30°)
    TAURUS = 2       # ราศีพฤษภ (30° - 60°)
    GEMINI = 3       # ราศีเมถุน (60° - 90°)
    CANCER = 4       # ราศีกรกฎ (90° - 120°)
    LEO = 5          # ราศีสิงห์ (120° - 150°)
    VIRGO = 6        # ราศีกันย์ (150° - 180°)
    LIBRA = 7        # ราศีตุลย์ (180° - 210°)
    SCORPIO = 8      # ราศีพิจิก (210° - 240°)
    SAGITTARIUS = 9  # ราศีธนู (240° - 270°)
    CAPRICORN = 10   # ราศีมังกร (270° - 300°)
    AQUARIUS = 11    # ราศีกุมภ์ (300° - 330°)
    PISCES = 12      # ราศีมีน (330° - 360°)

class AstrologicalHouse(IntEnum):
    TANU = 1      # ตนุ (ตนเอง/ดวงชะตา)
    KADUMBA = 2   # กดุมภะ (การเงิน/รายได้)
    SAHAJJA = 3   # สหัชชะ (เพื่อน/สังคม)
    BANDHU = 4    # พันธุ (ญาติ/ครอบครัว)
    PUTTA = 5     # ปุตตะ (บุตร/บริวาร/การเสี่ยงโชค)
    ARI = 6       # อริ (อุปสรรค/ศัตรู/หนี้สิน)
    PATNI = 7     # ปัตนิ (คู่ครอง/หุ้นส่วน)
    MARANA = 8    # มรณะ (ความสูญเสีย/ต่างชาติ)
    SUBHA = 9     # ศุภะ (ความเจริญ/ผู้ใหญ่)
    KAMMA = 10    # กัมมะ (การงาน/อาชีพ)
    LABHA = 11    # ลาภะ (โชคลาภ/ลาภลอย/ความสำเร็จ)
    VINASA = 12   # วินาศ (ความสูญเสีย/ความลับ)

class PlanetaryDignity(str, Enum):
    KASET = "เกษตร"    # เจ้าเรือน มั่นคง
    UCC = "อุจจ์"      # สูงส่ง ทรงพลัง
    NIT = "นิจ"       # ต่ำต้อย อ่อนแอ
    PRA = "ประ"       # ตรงข้ามเกษตร เสื่อม
    NORMAL = "ปกติ"    # สภาวะปกติ
```

### 2.2 Dataclasses

#### Input Schema (`ThaiAstrologyInput`)
```python
@dataclass
class ThaiAstrologyInput:
    birth_date: date                       # วันเกิด (YYYY-MM-DD)
    birth_time: Optional[time] = None      # เวลาเกิด (HH:MM:SS), ถ้าไม่มีจะ default ตามนโยบาย
    birth_province: Optional[str] = "กรุงเทพมหานคร" # จังหวัดเกิด
    latitude: Optional[float] = None       # ละติจูด (ถ้าไม่ระบุจะค้นหาจากชื่อจังหวัด)
    longitude: Optional[float] = None      # ลองจิจูด (ถ้าไม่ระบุจะค้นหาจากชื่อจังหวัด)
    ayanamsa: str = "lahiri"               # ระบบอายนางศะ (default: Lahiri Sidereal)
```

#### Output Schemas (`PlanetPosition`, `HousePosition`, `ThaiAstrologyChart`)
```python
@dataclass
class PlanetPosition:
    planet_id: int               # 0-9
    planet_name_th: str          # เช่น "อาทิตย์", "จันทร์", ..., "มฤตยู"
    planet_name_en: str          # เช่น "Sun", "Moon", ..., "Uranus"
    longitude_deg: float         # 0.0 - 360.0° (Sidereal)
    sign_id: int                 # 1-12 (ZodiacSign)
    sign_name_th: str            # เช่น "เมษ", "พฤษภ", ...
    deg_in_sign: float           # 0.0 - 30.0°
    house_id: int                # 1-12 (AstrologicalHouse Relative to Ascendant)
    house_name_th: str           # เช่น "ตนุ", "กดุมภะ", ...
    is_retrograde: bool          # โคจรพักร์ (ถอยหลัง)
    dignity: PlanetaryDignity    # มาตรฐานดาว
    navamsa_sign_id: int         # 1-12 (D9 Navamsa sign)
    drekkana_sign_id: int        # 1-12 (D3 Drekkana sign)

@dataclass
class HousePosition:
    house_id: int                # 1-12
    house_name_th: str           # เช่น "ตนุ", "กดุมภะ", ...
    sign_id: int                 # 1-12 (ZodiacSign occupying house cusp)
    lord_planet_id: int          # 0-9 (เจ้าเรือนประจำราศี)

@dataclass
class ThaiAstrologyChart:
    ascendant_longitude: float             # ลองจิจูดลัคนา (0.0 - 360.0°)
    ascendant_sign_id: int                 # 1-12 (ลัคนาราศี)
    ascendant_deg_in_sign: float           # 0.0 - 30.0°
    ascendant_lord_planet_id: int          # 0-9 (ดาวเจ้าเรือนตนุ)
    planets: Dict[int, PlanetPosition]     # keyed by planet_id (0-9)
    houses: Dict[int, HousePosition]       # keyed by house_id (1-12)
    primary_lucky_planet: int              # ดาวโชคลาภหลัก (0-9)
    secondary_lucky_planet: int            # ดาวโชคลาภรอง (0-9)
    lucky_digits: List[int]                # ตัวเลขเด็ดสกัดจากโหราศาสตร์ไทย [ primary, secondary, ... ]
    calculation_metadata: Dict[str, Any]   # Metadata เช่น ayanamsa, lat/lon, is_time_estimated
```

### 2.3 Exposed Public Functions

```python
def calculate_thai_astrology(input_data: ThaiAstrologyInput) -> ThaiAstrologyChart:
    """
    Main calculation entry point for Thai Astrology Natal Chart.
    Computes Lahiri Ayanamsa Sidereal positions, Ascendant, 12 Houses,
    Navamsa D9, Drekkana D3, planetary dignities, and lucky digits.
    """
    ...

def get_province_coordinates(province_name: str) -> Tuple[float, float]:
    """
    Resolves Thai province name to (latitude, longitude).
    Defaults to Bangkok (13.7563 N, 100.5018 E) if province is unknown or empty.
    """
    ...

def calculate_lahiri_ayanamsa(julian_day: float) -> float:
    """
    Calculates the Lahiri Ayanamsa offset angle (approx 23°-24°) for a given Julian Day.
    """
    ...

def extract_lucky_astrology_digits(chart: ThaiAstrologyChart) -> List[int]:
    """
    Extracts ordered lucky digits (0-9) from planetary placements, Ascendant lord,
    Putta lord, and Labha lord for Layer 2 Composite Recommender.
    """
    ...
```

---

## 3. Edge Cases & Error Handling Specification

| Scenario / Input | Expected Behavior | Handling Strategy |
|---|---|---|
| **Missing `birth_time` (`None`)** | Default to `12:00:00` (Noon) standard midpoint. | Set `calculation_metadata["is_time_estimated"] = True`, log warning in metadata. |
| **Invalid date format or out-of-range date** | Raise `ValueError("Invalid birth date")`. | Input validation before ephemeris call. |
| **Unknown / Invalid `birth_province`** | Fallback to Bangkok (Lat: `13.7563`, Lon: `100.5018`). | Set `calculation_metadata["province_used"] = "กรุงเทพมหานคร (Default)"`. |
| **Out-of-bounds Latitude/Longitude** | Raise `ValueError("Latitude must be between -90 and 90, Longitude between -180 and 180")`. | Validate explicit lat/lon inputs if provided. |
| **Swiss Ephemeris fallback mode** | If `swisseph` library is unavailable in runtime environment, fall back to pure-python Keplerian/astronomical algorithm. | Ensure fallback engine produces exact or near-exact (< 0.1° discrepancy) Sidereal positions. |
| **360° Angle Wrap Around** | Wrap all degree calculations using `deg % 360.0`. | Prevent degree range errors (e.g. -5° -> 355°). |

---

## 4. Verification Strategies & Benchmark Test Cases

To verify accuracy in `test_thai_astrology.py`, tests will utilize known astronomical benchmark horoscopes and deterministic mathematical identities.

### Benchmark 1: Known Natal Chart Verification
- **Input:** Date: `1990-01-01`, Time: `12:00:00` (UTC+7), Province: `"กรุงเทพมหานคร"` (13.7563 N, 100.5018 E).
- **Ayanamsa:** Lahiri Sidereal (~23.72°).
- **Expected Placements:**
  - Sun (๑ / `ThaiPlanet.SUN`): In Sagittarius (ราศีธนู, `ZodiacSign.SAGITTARIUS`), degree ~16°-17°.
  - Jupiter (๕ / `ThaiPlanet.JUPITER`): In Gemini (ราศีเมถุน, `ZodiacSign.GEMINI`).
  - Saturn (๗ / `ThaiPlanet.SATURN`): In Sagittarius (ราศีธนู, `ZodiacSign.SAGITTARIUS`).
  - Rahu (๘ / `ThaiPlanet.RAHU`): In Capricorn (ราศีมังกร, `ZodiacSign.CAPRICORN`).
  - Ketu (๙ / `ThaiPlanet.KETU`): In Cancer (ราศีกรกฎ, `ZodiacSign.CANCER`).

### Benchmark 2: Navamsa (D9) Division Rules
- **Rule:**
  - Movable Signs (1, 4, 7, 10): 1st Navamsa starts at the sign itself.
  - Fixed Signs (2, 5, 8, 11): 1st Navamsa starts at the 9th sign from itself.
  - Dual Signs (3, 6, 9, 12): 1st Navamsa starts at the 5th sign from itself.
- **Test Assertion:** For a planet at `1.0°` Aries (Movable sign, 1st Navamsa slice `0.0° - 3°20'`), `navamsa_sign_id` MUST be `1` (Aries).

### Benchmark 3: Sign Lordship & House Mapping
- **Sign Lords:**
  - Aries (1) -> Mars (3), Taurus (2) -> Venus (6), Gemini (3) -> Mercury (4), Cancer (4) -> Moon (2), Leo (5) -> Sun (1), Virgo (6) -> Mercury (4), Libra (7) -> Venus (6), Scorpio (8) -> Mars (3), Sagittarius (9) -> Jupiter (5), Capricorn (10) -> Saturn (7), Aquarius (11) -> Saturn (7), Pisces (12) -> Jupiter (5).
- **Test Assertion:** `houses[1].lord_planet_id` matches `houses[1].sign_id`'s corresponding ruler.

---

## 5. Integration Interface with Layer 2 Recommender Engine

The Layer 2 Composite Lottery Recommender blends scores from 4 divination engines (60% weight) and 1-year historical GLO lottery frequencies (40% weight).

### 5.1 Lucky Digits Extraction Algorithm

1. **Primary Lucky Planet (`primary_lucky_planet`)**:
   - The planet ruling the Ascendant sign (เจ้าเรือนตนุ).
   - E.g., Ascendant in Cancer (4) -> Lord is Moon (2) -> Primary Digit = `2`.
2. **Secondary Lucky Planet (`secondary_lucky_planet`)**:
   - The planet ruling the 11th House (เจ้าเรือนลาภะ - House of Fortunes & Lottery Gains) OR 5th House (เจ้าเรือนปุตตะ - House of Speculation).
   - E.g., House 11 in Taurus (2) -> Lord is Venus (6) -> Secondary Digit = `6`.
3. **Auspicious House Lords & Resident Benefics**:
   - Collect planet IDs located in or ruling Houses 1 (ตนุ), 5 (ปุตตะ), 9 (ศุกระ/ศุภะ), and 11 (ลาภะ).
4. **Digit Array Standard**:
   - Output `lucky_digits: List[int]` contains 3 to 5 unique digits in order of strength, e.g., `[primary, secondary, putta_lord, labha_lord]`.

---

## 6. Pytest Test Suite Architecture (`test_thai_astrology.py`)

The test suite will contain the following test modules:

1. `test_input_validation_and_defaults()`: Tests missing time, unknown province, invalid dates, and metadata flags.
2. `test_lahiri_ayanamsa_calculation()`: Verifies Ayanamsa degree formula against reference Julian Days.
3. `test_natal_chart_planetary_positions()`: Verifies benchmark planet longitudes and sign IDs.
4. `test_navamsa_and_drekkana_divisions()`: Verifies D9 and D3 mathematical sign assignments.
5. `test_sign_lords_and_house_custs()`: Verifies house lord mapping and Ascendant calculations.
6. `test_lucky_digits_extraction()`: Verifies lucky digit output format and correctness for Layer 2 Recommender.

---
