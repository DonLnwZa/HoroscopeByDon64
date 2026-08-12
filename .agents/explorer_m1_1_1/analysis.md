# Technical Analysis: Sub-milestone M1.1 — Thai Astrology Engine

## 1. Overview & Objectives

The Thai Astrology Engine (`omni_oracle_app/backend/app/engines/thai_astrology.py`) is Layer 1's core astronomical and natal chart calculation module. It is responsible for calculating deterministically:
1. **Lahiri Ayanamsa Sidereal Zodiac Offset** for a given birth date, birth time, and geographic location in Thailand.
2. **Positions of 10 Planets (0–9)**: Sun (1), Moon (2), Mars (3), Mercury (4), Jupiter (5), Venus (6), Saturn (7), Rahu (8), Ketu (9), Uranus (0).
3. **12 Houses (Rasi Chart)**: Whole-sign house placement relative to Lagna (Ascendant), mapping houses Tanu (1) to Vinasa (12).
4. **Harmonic / Divisional Charts**:
   - **D9 Navamsa** (1/9th division = $3^\circ 20'$ per segment)
   - **D3 Drekkana** (1/3rd division = $10^\circ 00'$ per segment)
5. **Public Interface / Pytest Seam**: Clean Pydantic data structures (`ThaiAstrologyResult`, `PlanetPosition`, `LagnaInfo`, `HouseDetail`) and entry function `calculate_thai_astrology(...)`.

---

## 2. Astronomical & Astrological Logic

### 2.1 Sidereal Zodiac & Lahiri Ayanamsa Formula
Thai astrology uses the **Sidereal (นิรายนะ)** zodiac fixed star frame of reference. The difference between Tropical (Western) longitude ($\lambda_{\text{trop}}$) and Sidereal longitude ($\lambda_{\text{sid}}$) is the **Ayanamsa** ($A$):
$$\lambda_{\text{sid}} = (\lambda_{\text{trop}} - A) \pmod{360^\circ}$$

- **Standard Ayanamsa**: **Lahiri Ayanamsa** (Chitra Paksha).
- In year 2026, Lahiri Ayanamsa is approximately $24.23^\circ$ ($24^\circ 13' 48''$).
- **Ayanamsa Formula Approximation** (Pure Python implementation):
  $$A(JD) = 23.85 + 0.013708 \times \frac{JD - 2451545.0}{365.25}$$
  where $JD$ is the Julian Day Number for the UTC birth timestamp.

### 2.2 Geographic Coordinates for Thai Provinces
Location default: Bangkok (13.7563° N, 100.5018° E).
Province coordinate dictionary handles common Thai provinces (e.g. Bangkok, Chiang Mai, Nakhon Ratchasima, Songkhla, Khon Kaen, Chonburi, etc.), falling back to Bangkok coordinates when province is unlisted or custom lat/lon are provided.

### 2.3 10 Planets Mapping (Digits 0–9)
Thai Astrology uses single-digit planetary codes:
| Planet ID | Thai Name | English Name | Symbol / Role |
|---|---|---|---|
| `1` | อาทิตย์ | Sun | Solar energy, vitality, honor |
| `2` | จันทร์ | Moon | Lunar energy, emotions, mind |
| `3` | อังคาร | Mars | Action, courage, energy |
| `4` | พุธ | Mercury | Intellect, speech, trade |
| `5` | พฤหัสบดี | Jupiter | Wisdom, virtue, luck |
| `6` | ศุกร์ | Venus | Beauty, wealth, art |
| `7` | เสาร์ | Saturn | Discipline, obstacle, endurance |
| `8` | ราหู | Rahu (North Node) | Ambition, eclipse, illusion |
| `9` | เกตุ | Ketu (South Node) | Spirituality, intuition |
| `0` | มฤตยู | Uranus | Innovation, transformation, unexpected change |

### 2.4 12 Houses (Whole Sign House System: Tanu to Vinasa)
Lagna sign ($S_{\text{lagna}} \in \{0 \dots 11\}$) defines House 1 (ตนุ).
For any sign $S \in \{0 \dots 11\}$, house number $H$ is:
$$H = ((S - S_{\text{lagna}}) \pmod{12}) + 1$$

12 Houses Mapping:
1. **ตนุ (Tanu)**: Self, vitality, persona
2. **กดุมภะ (Kadumba)**: Wealth, income, assets
3. **สหัชชะ (Sahajja)**: Siblings, communication, short trips
4. **พันธุ (Bandhu)**: Family, property, roots
5. **ปุตตะ (Putta)**: Children, speculation, luck
6. **อริ (Ari)**: Enemies, obstacles, debts
7. **ปัตนิ (Patni)**: Spouse, partner, relationships
8. **มรณะ (Marana)**: Transformation, loss, foreign land
9. **ศุภะ (Supha)**: Fortune, wisdom, morality
10. **กัมมะ (Kamma)**: Career, public status, duty
11. **ลาภะ (Lapha)**: Gains, profits, realization of goals
12. **วินาศ (Vinasa)**: Hidden expenditure, secret, solitude

### 2.5 Harmonic Charts Calculation Rules

#### 1) D9 Navamsa (นวางค์จักร) — $1/9^{\text{th}}$ Division ($3.3333^\circ$ per segment)
- Each sign ($30^\circ$) is divided into 9 segments $k \in \{0, 1, \dots, 8\}$ where $k = \lfloor D / 3.3333333333333335 \rfloor$.
- **Starting Sign ($S_{\text{start}}$)** based on element of sign $S$:
  - Fiery ($S \pmod 4 == 0$: Aries, Leo, Sagittarius): $S_{\text{start}} = 0$ (Aries)
  - Earthy ($S \pmod 4 == 1$: Taurus, Virgo, Capricorn): $S_{\text{start}} = 9$ (Capricorn)
  - Airy ($S \pmod 4 == 2$: Gemini, Libra, Aquarius): $S_{\text{start}} = 6$ (Libra)
  - Watery ($S \pmod 4 == 3$: Cancer, Scorpio, Pisces): $S_{\text{start}} = 3$ (Cancer)
- **Navamsa Sign Index**:
  $$S_{\text{navamsa}} = (S_{\text{start}} + k) \pmod{12}$$

#### 2) D3 Drekkana (ตรียางค์จักร) — $1/3^{\text{rd}}$ Division ($10^\circ$ per segment)
- Each sign ($30^\circ$) is divided into 3 segments $k \in \{0, 1, 2\}$ where $k = \lfloor D / 10.0 \rfloor$.
- **Drekkana Sign Index**:
  - $k=0$ (1st Drekkana): Same sign $S$
  - $k=1$ (2nd Drekkana): 5th sign $(S + 4) \pmod{12}$
  - $k=2$ (3rd Drekkana): 9th sign $(S + 8) \pmod{12}$

---

## 3. Public Interface & Seam Design

### Pydantic Schemas (`omni_oracle_app/backend/app/schemas/` or in `thai_astrology.py`)

```python
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class PlanetPosition(BaseModel):
    planet_id: int = Field(..., ge=0, le=9, description="Planet digit (0-9)")
    planet_name_th: str
    planet_name_en: str
    longitude: float = Field(..., ge=0.0, lt=360.0)
    rasi_index: int = Field(..., ge=0, le=11)
    rasi_name_th: str
    degree_in_rasi: float = Field(..., ge=0.0, lt=30.0)
    house_number: int = Field(..., ge=1, le=12)
    house_name_th: str
    navamsa_rasi_index: int = Field(..., ge=0, le=11)
    navamsa_rasi_th: str
    drekkana_rasi_index: int = Field(..., ge=0, le=11)
    drekkana_rasi_th: str
    is_retrograde: bool = False

class LagnaInfo(BaseModel):
    longitude: float = Field(..., ge=0.0, lt=360.0)
    rasi_index: int = Field(..., ge=0, le=11)
    rasi_name_th: str
    degree_in_rasi: float = Field(..., ge=0.0, lt=30.0)
    navamsa_rasi_index: int = Field(..., ge=0, le=11)
    navamsa_rasi_th: str
    drekkana_rasi_index: int = Field(..., ge=0, le=11)
    drekkana_rasi_th: str

class HouseDetail(BaseModel):
    house_number: int = Field(..., ge=1, le=12)
    house_name_th: str
    rasi_index: int = Field(..., ge=0, le=11)
    rasi_name_th: str
    planets: List[int] = Field(default_factory=list, description="List of planet IDs in this house")

class ThaiAstrologyResult(BaseModel):
    ayanamsa_degree: float
    lagna: LagnaInfo
    planets: Dict[int, PlanetPosition]
    houses: List[HouseDetail]
    lucky_digits: List[int] = Field(..., description="Extracted key planetary digits for lottery engine")
```

### Seam Function Entrypoint
```python
def calculate_thai_astrology(
    birth_date: str,
    birth_time: str = "12:00",
    birth_province: str = "กรุงเทพมหานคร",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> ThaiAstrologyResult:
    ...
```

---

## 4. Dependencies & Architecture Strategy

- **Dual Engine Architecture**:
  1. Primary: Use `swisseph` (`pyswisseph`) if installed (`swe.set_sid_mode(swe.SIDM_LAHIRI)`).
  2. Fallback: Self-contained pure Python Meeus/Keplerian ephemeris math engine with Lahiri Ayanamsa formula.
- This guarantees zero external runtime failure, smooth installation on any OS, and fast execution for Pytest unit testing suite.

---

## 5. Pytest Seam Specification (`test_thai_astrology.py`)

Test cases to verify:
1. `test_calculate_thai_astrology_valid_input`: Verifies output data structures, 10 planet IDs present (0-9), 12 houses (1-12), and valid degree ranges.
2. `test_lagna_and_house_mapping`: Ensures Lagna is assigned House 1 (ตนุ) and subsequent houses follow zodiac order.
3. `test_harmonic_charts_d9_d3`: Validates D9 Navamsa and D3 Drekkana formulas for known degree positions.
4. `test_lahiri_ayanamsa_range`: Verifies Lahiri Ayanamsa falls within expected astronomical range (~23.5°–24.5°).
5. `test_lucky_digits_extraction`: Validates extraction of lucky digits array for Layer 2 recommender integration.
