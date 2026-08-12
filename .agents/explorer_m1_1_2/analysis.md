# Technical Analysis Report: Thai Astrology Engine (Sub-milestone M1.1)

**Author:** Explorer 2  
**Date:** 2026-08-06  
**Target Module:** `omni_oracle_app/backend/app/engines/thai_astrology.py`  
**Target Test Suite:** `omni_oracle_app/backend/tests/test_thai_astrology.py`  
**Working Directory:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_1_2`

---

## 1. Executive Summary

This report establishes the complete mathematical, astronomical, and architectural specification for the **Thai Astrology Engine** (`thai_astrology.py`), which forms the astronomical core of Layer 1 in the Omni-Oracle Divination System. 

The Thai Astrology Engine converts user birth metadata (date, time, latitude, longitude, UTC offset) into a deterministic **Nirayana (Sidereal) Natal Chart (ราศีจักร - D1)** adjusted by **Lahiri Ayanamsa**, accompanied by **D9 Navamsa Chart (นวางค์จักร)**, **D3 Drekkana Chart (ตรียางค์จักร)**, 12 Astrological Houses (ภพทั้ง 12), planetary dignities (เกษตร, อุจจ์, นิจ, ประ), Vimshottari Mahadasha planetary cycle, and extracts personal auspicious lucky digits (2-digit and 3-digit sets) for lottery recommendation.

---

## 2. Mathematical Rules & Astronomical Foundation

### 2.1 Tropical vs. Sidereal & Lahiri Ayanamsa Adjustment
- **Tropical Zodiac ($\lambda_{\text{trop}}$)**: Based on Vernal Equinox ($0^\circ$ Aries). Used in Western astrology.
- **Sidereal Zodiac ($\lambda_{\text{sid}}$)**: Based on fixed stellar background. Used in Thai (นิรายนะ) and Vedic astrology.
- **Lahiri Ayanamsa ($\text{Ayanamsa}_{\text{Lahiri}}$)**: The official standard displacement angle between Tropical zero and Sidereal zero.

#### Conversion Formula
$$\lambda_{\text{sid}} = (\lambda_{\text{trop}} - \text{Ayanamsa}_{\text{Lahiri}}) \pmod{360^\circ}$$

#### Swiss Ephemeris Integration (`pysweph` / `swisseph`)
When Swiss Ephemeris C-extension is available:
```python
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
ayanamsa_val = swe.get_ayanamsa_ut(julian_day_ut)
sidereal_longitude = (tropical_longitude - ayanamsa_val) % 360.0
```

#### Pure Python Fallback Mathematical Formula
When `swisseph` library is unavailable or in light test environments, Lahiri Ayanamsa is calculated using N.C. Lahiri's polynomial approximation relative to epoch J2000.0 ($JD = 2451545.0$):

Let $T = \frac{JD - 2451545.0}{36525.0}$ (Julian centuries from J2000.0):
$$\text{Ayanamsa}_{\text{Lahiri}}(T) = 23.85305556 + 1.39697128 \times T + 0.00030878 \times T^2 \quad (\text{in degrees})$$

At J2000.0 ($T=0$), Lahiri Ayanamsa is $23^\circ 51' 11" \approx 23.85306^\circ$.  
In 2026 ($T \approx 0.266$), Lahiri Ayanamsa is approximately $24.2278^\circ$ ($24^\circ 13' 40"$).

#### Zodiac Sign Partitioning (30° per sign)
For any sidereal longitude $\lambda_{\text{sid}} \in [0^\circ, 360^\circ)$:
- Sign Index $S = \lfloor \frac{\lambda_{\text{sid}}}{30} \rfloor \in \{0, 1, 2, ..., 11\}$
- Degree in Sign $\theta = \lambda_{\text{sid}} \pmod{30.0}$

| Index $S$ | Thai Sign Name | English Sign Name | Symbol / Element |
|---|---|---|---|
| 0 | เมษ | Aries | ♈ Fire (ไฟ) |
| 1 | พฤษภ | Taurus | ♉ Earth (ดิน) |
| 2 | เมถุน | Gemini | ♊ Air (ลม) |
| 3 | กรกฎ | Cancer | ♋ Water (น้ำ) |
| 4 | สิงห์ | Leo | ♌ Fire (ไฟ) |
| 5 | กันย์ | Virgo | ♍ Earth (ดิน) |
| 6 | ตุลย์ | Libra | ♎ Air (ลม) |
| 7 | พิจิก | Scorpio | ♏ Water (น้ำ) |
| 8 | ธนู | Sagittarius | ♐ Fire (ไฟ) |
| 9 | มังกร | Capricorn | ♑ Earth (ดิน) |
| 10 | กุมภ์ | Aquarius | ♒ Air (ลม) |
| 11 | มีน | Pisces | ♓ Water (น้ำ) |

---

### 2.2 Lagna (Ascendant) & House Calculation

#### Default Geographic Inputs for Thailand
- Timezone: ICT Standard UTC+7 (`Asia/Bangkok`).
- Default Latitude: $13.7563^\circ\text{ N}$ (Bangkok).
- Default Longitude: $100.5018^\circ\text{ E}$ (Bangkok).

#### Time Normalization to Universal Time (UT)
Given local date $Y, M, D$ and time $h, m, s$ with $UTC_{\text{offset}} = +7.0$:
$$UT_{\text{hours}} = h + \frac{m}{60} + \frac{s}{3600} - UTC_{\text{offset}}$$

#### Sidereal Ascendant Calculation Formula
1. Calculate Greenwich Mean Sidereal Time (GMST) in degrees:
   $$T_0 = \frac{JD_0 - 2451545.0}{36525.0}$$
   $$GMST = 100.46061837 + 36000.770053608 \times T_0 + 360.98564736629 \times \frac{UT}{24.0} \pmod{360^\circ}$$
2. Calculate Local Sidereal Time (LST):
   $$LST = (GMST + \text{longitude}) \pmod{360^\circ}$$
3. Calculate Obliquity of Ecliptic ($\varepsilon$):
   $$\varepsilon = 23.439291 - 0.0130042 \times T_0 \quad (\text{in degrees})$$
4. Compute Tropical Ascendant ($\text{Asc}_{\text{trop}}$):
   $$y = -\cos(LST)$$
   $$x = \sin(LST)\cos(\varepsilon) + \tan(\text{latitude})\sin(\varepsilon)$$
   $$\text{Asc}_{\text{trop}} = \text{atan2}(y, x) \pmod{360^\circ}$$
5. Convert to Sidereal Ascendant ($\text{Lagna}_{\text{sid}}$):
   $$\text{Lagna}_{\text{sid}} = (\text{Asc}_{\text{trop}} - \text{Ayanamsa}_{\text{Lahiri}}) \pmod{360^\circ}$$

#### House Mapping (Equal House / Whole Sign System)
In traditional Thai Rasi Chakra astrology, houses are mapped relative to the Lagna sign $S_{\text{Lagna}} = \lfloor \frac{\text{Lagna}_{\text{sid}}}{30} \rfloor$:

$$\text{HouseSign}(H) = (S_{\text{Lagna}} + H - 1) \pmod{12} \quad \text{for } H \in \{1, 2, ..., 12\}$$

| House $H$ | Thai House Name | Domain / Meaning |
|---|---|---|
| 1 | ตนุ (Tanu) | Self, physical body, core destiny, Lagna |
| 2 | กดุมภะ (Kadumba) | Financial earnings, portable assets |
| 3 | สหัชชะ (Sahajja) | Siblings, close friends, communication |
| 4 | พันธุ (Bhandhu) | Family, home, real estate, roots |
| 5 | ปุตตะ (Putta) | Children, subordinates, risk, creativity |
| 6 | อริ (Ari) | Debt, obstacles, health challenges, enemies |
| 7 | ปัตนิ (Patni) | Spouse, romantic/business partner |
| 8 | มรณะ (Marana) | Loss, transformation, overseas, inheritance |
| 9 | ศุภะ (Supha) | Virtue, prosperity, wisdom, guidance |
| 10 | กัมมะ (Kamma) | Career, public action, profession |
| 11 | ลาภะ (Lapha) | Gains, windfalls, secondary wealth, luck |
| 12 | วินาศ (Vinasa) | Secret loss, behind-the-scenes, isolation |

---

## 3. Divisional Charts (ดวงวรรคย่อย) Rules

### 3.1 Exact D9 Navamsa Chart Rules (นวางค์จักร)

#### Arc Division
Each $30^\circ$ Rasi sign is partitioned into 9 equal Navamsas of $3^\circ 20' = 3.33333333^\circ = \frac{10}{3}^\circ = 200'$ (arcminutes).

Total Navamsas in the 360° zodiac = $12 \times 9 = 108$ Navamsas.

#### Unified Mathematical Formula for Navamsa Sign ($S_{\text{D9}}$)
For any absolute Sidereal longitude $\lambda_{\text{sid}} \in [0^\circ, 360^\circ)$:

$$N_{\text{abs}} = \lfloor \frac{\lambda_{\text{sid}} \times 60}{200} \rfloor = \lfloor \frac{\lambda_{\text{sid}}}{3.33333333^\circ} \rfloor \in \{0, 1, ..., 107\}$$

$$S_{\text{D9}} = N_{\text{abs}} \pmod{12}$$

#### Proof of Equivalence to Elemental Triplicity Rules
Traditional Thai rules partition Rasi signs into 4 elemental triplicities:
1. **Fire Signs (เมษ 0, สิงห์ 4, ธนู 8)**: Navamsa sequence starts from **Aries (0)** ($N_{\text{abs}} \pmod{12} \in \{0..8\}$).
2. **Earth Signs (พฤษภ 1, กันย์ 5, มังกร 9)**: Navamsa sequence starts from **Capricorn (9)** ($N_{\text{abs}} \pmod{12} \in \{9, 10, 11, 0, 1, 2, 3, 4, 5\}$).
3. **Air Signs (เมถุน 2, ตุลย์ 6, กุมภ์ 10)**: Navamsa sequence starts from **Libra (6)** ($N_{\text{abs}} \pmod{12} \in \{6, 7, 8, 9, 10, 11, 0, 1, 2\}$).
4. **Water Signs (กรกฎ 3, พิจิก 7, มีน 11)**: Navamsa sequence starts from **Cancer (3)** ($N_{\text{abs}} \pmod{12} \in \{3, 4, 5, 6, 7, 8, 9, 10, 11\}$).

Because $108 = 9 \times 12$, the 108 Navamsas form 9 continuous 12-sign cycles around the zodiac starting at $0^\circ$ Aries. Thus $S_{\text{D9}} = \lfloor \frac{\lambda_{\text{sid}}}{3.33333333^\circ} \rfloor \pmod{12}$ is exact and universally valid for all 12 signs.

---

### 3.2 Exact D3 Drekkana Chart Rules (ตรียางค์จักร)

#### Arc Division
Each $30^\circ$ Rasi sign is partitioned into 3 equal Decanates (Drekkana) of $10^\circ$ each:
- **1st Decan ($d=0$)**: $0^\circ \le \theta < 10^\circ$
- **2nd Decan ($d=1$)**: $10^\circ \le \theta < 20^\circ$
- **3rd Decan ($d=2$)**: $20^\circ \le \theta < 30^\circ$

#### Decan Mapping Rules
1. **1st Decan ($d=0$)**: Occupies the **same sign** as Rasi ($S$).
2. **2nd Decan ($d=1$)**: Occupies the **5th sign** from Rasi sign ($S + 4 \pmod{12}$).
3. **3rd Decan ($d=2$)**: Occupies the **9th sign** from Rasi sign ($S + 8 \pmod{12}$).

#### Unified Mathematical Formula for Drekkana Sign ($S_{\text{D3}}$)
Given Rasi sign $S \in \{0..11\}$ and degree in sign $\theta = \lambda_{\text{sid}} \pmod{30.0}$:

$$d = \lfloor \frac{\theta}{10.0} \rfloor \in \{0, 1, 2\}$$

$$S_{\text{D3}} = (S + 4 \times d) \pmod{12}$$

---

## 4. Planetary Dignity, Mahadasha & Lucky Digit Extraction

### 4.1 Sign Rulers (ดาวเจ้าเกษตร) & Key House Lords
Sign Rulers array `SIGN_RULERS = [3, 6, 4, 2, 1, 4, 6, 3, 5, 7, 8, 5]` corresponding to signs 0 to 11 (Aries to Pisces).

- **Lagna Lord (ดาวตนุเกษตร)**: Ruler of Lagna sign $S_{\text{Lagna}}$:
  $$\text{LagnaLord} = \text{SIGN\_RULERS}[S_{\text{Lagna}}]$$
- **Kamma Lord (ดาวกัมมะเกษตร)**: Ruler of 10th House sign $S_{10} = (S_{\text{Lagna}} + 9) \pmod{12}$:
  $$\text{KammaLord} = \text{SIGN\_RULERS}[S_{10}]$$
- **Lapha Lord (ดาวลาภะเกษตร)**: Ruler of 11th House sign $S_{11} = (S_{\text{Lagna}} + 10) \pmod{12}$:
  $$\text{LaphaLord} = \text{SIGN\_RULERS}[S_{11}]$$

### 4.2 Planetary Dignities (ตำแหน่งมาตรฐานดาว)
1. **เกษตร (Home Kaset)**: Planet in its own sign.
2. **อุจจ์ (Exalted Ucha)**: Peak strength.
   - Sun (1) in Aries (0)
   - Moon (2) in Taurus (1)
   - Mars (3) in Capricorn (9)
   - Mercury (4) in Virgo (5)
   - Jupiter (5) in Cancer (3)
   - Venus (6) in Pisces (11)
   - Saturn (7) in Libra (6)
   - Rahu (8) in Taurus (1) / Gemini (2)
3. **นิจ (Debilitated Nicha)**: Opposite Exalted sign.
4. **ประ (Detriment Pra)**: Opposite own Kaset sign.

### 4.3 Vimshottari Mahadasha (มหาทักษา / เสวยอายุ)
Calculated from Moon's Sidereal Longitude $\lambda_{\text{Moon, sid}}$:
$$\text{NakshatraIndex } N_{\text{nak}} = \lfloor \frac{\lambda_{\text{Moon, sid}}}{13.33333333^\circ} \rfloor \in \{0, 1, ..., 26\}$$

Vimshottari Sequence array (9 planets):  
`MAHADASHA_SEQUENCE = [9, 6, 1, 2, 3, 8, 5, 7, 4]` (Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury).

$$\text{MahadashaPlanet} = \text{MAHADASHA\_SEQUENCE}[N_{\text{nak}} \pmod 9]$$

### 4.4 Lucky Digit Extraction Algorithm
1. **Primary Lucky Digit**: `LagnaLord`
2. **Secondary Lucky Digits**: `LaphaLord`, `KammaLord`, `MahadashaPlanet`
3. **Exalted / Kaset Digits**: Any planet with "เกษตร" or "อุจจ์" dignity in D1 or D9.
4. **Auspicious 2-Digit Sets**:
   - `f"{LagnaLord}{LaphaLord}"`
   - `f"{LagnaLord}{KammaLord}"`
   - `f"{MahadashaPlanet}{LagnaLord}"`
5. **Auspicious 3-Digit Sets**:
   - `f"{LagnaLord}{LaphaLord}{KammaLord}"`

---

## 5. Public Seam & Pydantic Schemas

The engine exposes a clean, typed public interface in `omni_oracle_app/backend/app/engines/thai_astrology.py`:

```python
from datetime import date, time
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class AyanamsaMode(str, Enum):
    LAHIRI = "LAHIRI"
    FAGAN_BRADLEY = "FAGAN_BRADLEY"
    RAMAN = "RAMAN"

class ThaiAstrologyInput(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    birth_date: date = Field(..., description="Birth date YYYY-MM-DD")
    birth_time: time = Field(..., description="Birth time HH:MM:SS")
    utc_offset_hours: float = Field(default=7.0, description="Timezone UTC offset (+7.0 for Thailand ICT)")
    latitude: float = Field(default=13.7563, description="Latitude in degrees (default: Bangkok)")
    longitude: float = Field(default=100.5018, description="Longitude in degrees (default: Bangkok)")
    ayanamsa_mode: AyanamsaMode = Field(default=AyanamsaMode.LAHIRI, description="Ayanamsa adjustment mode")

class PlanetPosition(BaseModel):
    planet_id: int = Field(..., description="Planet ID (1=Sun, 2=Moon, 3=Mars, 4=Mercury, 5=Jupiter, 6=Venus, 7=Saturn, 8=Rahu, 9=Ketu, 0=Uranus)")
    planet_name_th: str
    planet_name_en: str
    longitude_tropical: float
    longitude_sidereal: float
    sign_id: int = Field(..., ge=0, le=11)
    sign_name_th: str
    sign_name_en: str
    degree_in_sign: float
    house_num: int = Field(..., ge=1, le=12)
    house_name_th: str
    dignity: str = Field(..., description="เกษตร, อุจจ์, นิจ, ประ, ปกติ")
    d9_navamsa_sign_id: int = Field(..., ge=0, le=11)
    d9_navamsa_sign_th: str
    d3_drekkana_sign_id: int = Field(..., ge=0, le=11)
    d3_drekkana_sign_th: str

class AstrologyHouse(BaseModel):
    house_num: int = Field(..., ge=1, le=12)
    house_name_th: str
    sign_id: int = Field(..., ge=0, le=11)
    sign_name_th: str
    house_lord_planet_id: int

class ThaiAstrologyResult(BaseModel):
    ayanamsa_mode: str
    ayanamsa_value: float
    lagna_longitude_sidereal: float
    lagna_sign_id: int
    lagna_sign_th: str
    lagna_degree_in_sign: float
    lagna_d9_navamsa_sign_id: int
    lagna_d3_drekkana_sign_id: int
    planets: List[PlanetPosition]
    houses: List[AstrologyHouse]
    lagna_lord: int
    kamma_lord: int
    lapha_lord: int
    mahadasha_planet: int
    nakshatra_id: int
    nakshatra_name_th: str
    auspicious_digits: List[int]
    lucky_pairs_2d: List[str]
    lucky_trios_3d: List[str]

class ThaiAstrologyEngine:
    """Thai Astrology Calculation Engine (Lahiri Ayanamsa, D1 Rasi, D9 Navamsa, D3 Drekkana)."""
    
    def calculate(self, payload: ThaiAstrologyInput) -> ThaiAstrologyResult:
        """Executes full natal chart calculation and returns structured ThaiAstrologyResult."""
        ...
```

---

## 6. Pytest Unit Test Suite Plan (`test_thai_astrology.py`)

The test suite in `omni_oracle_app/backend/tests/test_thai_astrology.py` will validate:

1. **Test Ayanamsa Adjustment**:
   - Given a known Tropical longitude (e.g. 150.0°), verify Sidereal longitude equals `(150.0 - Ayanamsa) % 360.0`.
   - Verify Lahiri Ayanamsa value for 2026 is approximately $24.22^\circ \pm 0.1^\circ$.

2. **Test Lagna Calculation & House Mapping**:
   - Verify Lagna sign and degree for standard birth inputs (e.g. 1995-08-15 14:30 Bangkok).
   - Confirm House 1 is assigned to Lagna sign and House 2..12 follow sequentially `(Lagna + H - 1) mod 12`.

3. **Test D9 Navamsa Chart Boundaries**:
   - Test degree 0.0° Aries -> Navamsa 0 (Aries).
   - Test degree 3.3° Aries -> Navamsa 0 (Aries).
   - Test degree 3.4° Aries -> Navamsa 1 (Taurus).
   - Test degree 29.9° Aries -> Navamsa 8 (Sagittarius).
   - Test degree 0.0° Taurus -> Navamsa 9 (Capricorn).
   - Test degree 0.0° Gemini -> Navamsa 6 (Libra).
   - Test degree 0.0° Cancer -> Navamsa 3 (Cancer).

4. **Test D3 Drekkana Chart Boundaries**:
   - Test degree 5.0° Aries -> Drekkana 0 (Aries).
   - Test degree 15.0° Aries -> Drekkana 4 (Leo).
   - Test degree 25.0° Aries -> Drekkana 8 (Sagittarius).

5. **Test Planetary Dignities & Mahadasha**:
   - Test Sun in Aries -> Exalted ("อุจจ์").
   - Test Moon Nakshatra mapping and Mahadasha planet calculation.

6. **Test Lucky Digits Extraction**:
   - Verify `auspicious_digits` includes `lagna_lord`, `lapha_lord`, `kamma_lord`, `mahadasha_planet`.
   - Verify `lucky_pairs_2d` and `lucky_trios_3d` formatting.

---

## 7. Next Steps

With this complete specification, Implementer agents can construct `omni_oracle_app/backend/tests/test_thai_astrology.py` (Red test suite) and `omni_oracle_app/backend/app/engines/thai_astrology.py` (Green implementation) adhering strictly to TDD.
