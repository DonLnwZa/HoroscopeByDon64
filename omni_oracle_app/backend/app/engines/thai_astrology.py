"""
Thai Astrology Engine (omni_oracle_app/backend/app/engines/thai_astrology.py)
Layer 1 Natal Chart Calculation Core (Lahiri Ayanamsa, 10 Planets, 12 Houses, D9 Navamsa, D3 Drekkana, Dignities, Lucky Digits)
Deterministic Pure Python Ephemeris Math with Optional Swisseph C-Extension Fallback
"""

import math
from datetime import datetime, date, time, timedelta
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Tuple, Any, Union
from pydantic import BaseModel, Field, ConfigDict

ENGLISH_DAY_NAMES = {1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday", 5: "Thursday", 6: "Friday", 7: "Saturday"}
THAI_DAY_NAMES = {1: "วันอาทิตย์", 2: "วันจันทร์", 3: "วันอังคาร", 4: "วันพุธ", 5: "วันพฤหัสบดี", 6: "วันศุกร์", 7: "วันเสาร์"}

ENGLISH_ZODIAC_NAMES = {1: "Rat", 2: "Ox", 3: "Tiger", 4: "Rabbit", 5: "Dragon", 6: "Snake", 7: "Horse", 8: "Goat", 9: "Monkey", 10: "Rooster", 11: "Dog", 12: "Pig"}
THAI_ZODIAC_NAMES = {1: "ปีชวด", 2: "ปีฉลู", 3: "ปีขาล", 4: "ปีเถาะ", 5: "ปีมะโรง", 6: "ปีมะเส็ง", 7: "ปีมะเมีย", 8: "ปีมะแม", 9: "ปีวอก", 10: "ปีระกา", 11: "ปีจอ", 12: "ปีกุน"}



# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

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
    KETU = 9       # เกตุ (9)


class ZodiacSign(IntEnum):
    ARIES = 1        # เมษ (1)
    TAURUS = 2       # พฤษภ (2)
    GEMINI = 3       # เมถุน (3)
    CANCER = 4       # กรกฎ (4)
    LEO = 5          # สิงห์ (5)
    VIRGO = 6        # กันย์ (6)
    LIBRA = 7        # ตุลย์ (7)
    SCORPIO = 8      # พิจิก (8)
    SAGITTARIUS = 9  # ธนู (9)
    CAPRICORN = 10   # มังกร (10)
    AQUARIUS = 11    # กุมภ์ (11)
    PISCES = 12      # มีน (12)


class AstrologicalHouse(IntEnum):
    TANU = 1      # ตนุ
    KADUMBA = 2   # กดุมภะ
    SAHAJJA = 3   # สหัชชะ
    BANDHU = 4    # พันธุ
    PUTTA = 5     # ปุตตะ
    ARI = 6       # อริ
    PATNI = 7     # ปัตนิ
    MARANA = 8    # มรณะ
    SUBHA = 9     # ศุภะ
    KAMMA = 10    # กัมมะ
    LABHA = 11    # ลาภะ
    VINASA = 12   # วินาศ


class PlanetaryDignity(str, Enum):
    KASET = "เกษตร"
    UCC = "อุจจ์"
    NIT = "นิจ"
    PRA = "ประ"
    NORMAL = "ปกติ"


THAI_SIGN_NAMES = [
    "เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
    "ตุลย์", "พิจิก", "ธนู", "มังกร", "กุมภ์", "มีน"
]

ENGLISH_SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

THAI_HOUSE_NAMES = [
    "ตนุ", "กดุมภะ", "สหัชชะ", "พันธุ", "ปุตตะ", "อริ",
    "ปัตนิ", "มรณะ", "ศุภะ", "กัมมะ", "ลาภะ", "วินาศ"
]

THAI_PLANET_NAMES = {
    0: "มฤตยู", 1: "อาทิตย์", 2: "จันทร์", 3: "อังคาร", 4: "พุธ",
    5: "พฤหัสบดี", 6: "ศุกร์", 7: "เสาร์", 8: "ราหู", 9: "เกตุ"
}

ENGLISH_PLANET_NAMES = {
    0: "Uranus", 1: "Sun", 2: "Moon", 3: "Mars", 4: "Mercury",
    5: "Jupiter", 6: "Venus", 7: "Saturn", 8: "Rahu", 9: "Ketu"
}

# Sign rulers mapping (0..11 -> planet ID)
SIGN_RULERS = [3, 6, 4, 2, 1, 4, 6, 3, 5, 7, 7, 5]

# Exalted (Ucc) signs (planet_id -> sign_index 0..11)
EXALTED_SIGNS = {
    1: 0,   # Sun in Aries
    2: 1,   # Moon in Taurus
    3: 9,   # Mars in Capricorn
    4: 5,   # Mercury in Virgo
    5: 3,   # Jupiter in Cancer
    6: 11,  # Venus in Pisces
    7: 6,   # Saturn in Libra
    8: 1,   # Rahu in Taurus
    9: 7,   # Ketu in Scorpio
    0: 2,   # Uranus in Gemini
}

# Debilitated (Nit) signs (opposite of Ucc)
DEBILITATED_SIGNS = {pid: (sign + 6) % 12 for pid, sign in EXALTED_SIGNS.items()}

# Thai province coordinates lookup dictionary
PROVINCE_COORDINATES: Dict[str, Tuple[float, float]] = {
    "กรุงเทพมหานคร": (13.7563, 100.5018),
    "เชียงใหม่": (18.7883, 98.9853),
    "เชียงราย": (19.9105, 99.8406),
    "ขอนแก่น": (16.4322, 102.8236),
    "นครราชสีมา": (14.9799, 102.0978),
    "อุดรธานี": (17.4138, 102.7872),
    "อุบลราชธานี": (15.2448, 104.8473),
    "ชลบุรี": (13.3611, 100.9847),
    "นนทบุรี": (13.8591, 100.5217),
    "ปทุมธานี": (14.0208, 100.5250),
    "สมุทรปราการ": (13.5991, 100.5968),
    "สงขลา": (7.1988, 100.5954),
    "ภูเก็ต": (7.8804, 98.3923),
    "สุราษฎร์ธานี": (9.1382, 99.3217),
    "นครศรีธรรมราช": (8.4304, 99.9631),
}


# =============================================================================
# DATA MODELS
# =============================================================================

class ThaiLunarCalendarResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    day_of_week: str          # "Sunday".."Saturday"
    day_of_week_th: str       # "วันอาทิตย์".."วันเสาร์"
    day_of_week_num: int      # 1..7 (1=Sun, 2=Mon, ..., 7=Sat)
    lunar_month: int          # 1..12
    lunar_month_name_th: str   # "เดือน 6"
    zodiac_year: str          # "Monkey", "Rat", etc.
    zodiac_year_th: str       # "ปีกุน (หมู)"
    zodiac_year_num: int      # 1..12 (1=Rat..12=Pig)
    cutoff_applied: bool      # True if birth_time < 06:00


def calculate_thai_lunar_calendar(
    birth_date: str,
    birth_time: str = "12:00"
) -> ThaiLunarCalendarResult:
    """
    Auto-calculates approximate Thai Lunar Calendar values from Gregorian birth_date and birth_time.
    Applies the Bangkok 06:00 AM cutoff rule for Thai day of week determination.
    """
    try:
        dt_date = datetime.strptime(str(birth_date).strip(), "%Y-%m-%d").date()
    except Exception as e:
        raise ValueError(f"Invalid birth_date '{birth_date}'. Expected format YYYY-MM-DD.") from e

    clean_time = str(birth_time).strip() if birth_time else "12:00"
    parts = clean_time.split(":")
    try:
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
    except Exception as e:
        raise ValueError(f"Invalid birth_time '{birth_time}'. Expected format HH:MM.") from e

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Invalid birth_time '{birth_time}'. Time values out of range.")

    birth_tm = time(hour, minute)

    # 6:00 AM Cutoff Rule
    if birth_tm < time(6, 0):
        effective_date = dt_date - timedelta(days=1)
        cutoff_applied = True
    else:
        effective_date = dt_date
        cutoff_applied = False

    # Day of week (1=Sun..7=Sat)
    day_num = ((effective_date.weekday() + 1) % 7) + 1
    day_name_en = ENGLISH_DAY_NAMES[day_num]
    day_name_th = THAI_DAY_NAMES[day_num]

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
        day_of_week_th=day_name_th,
        day_of_week_num=day_num,
        lunar_month=lunar_month,
        lunar_month_name_th=lunar_month_name_th,
        zodiac_year=zodiac_year_en,
        zodiac_year_th=zodiac_year_th,
        zodiac_year_num=zodiac_year_num,
        cutoff_applied=cutoff_applied,
    )


class LagnaInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    longitude: float = Field(..., ge=0.0, lt=360.0)
    rasi_index: int = Field(..., ge=0, le=11)
    rasi_name_th: str
    degree_in_rasi: float = Field(..., ge=0.0, lt=30.0)
    navamsa_rasi_index: int = Field(..., ge=0, le=11)
    navamsa_rasi_th: str
    drekkana_rasi_index: int = Field(..., ge=0, le=11)
    drekkana_rasi_th: str

    @property
    def sign_id(self) -> int:
        return self.rasi_index + 1

    @property
    def deg_in_sign(self) -> float:
        return self.degree_in_rasi


class PlanetPosition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    planet_id: int = Field(..., ge=0, le=9)
    planet_name_th: str
    planet_name_en: str
    longitude: float = Field(..., ge=0.0, lt=360.0)
    rasi_index: int = Field(..., ge=0, le=11)
    rasi_name_th: str
    degree_in_rasi: float = Field(..., ge=0.0, lt=30.0)
    house_number: int = Field(..., ge=1, le=12)
    house_name_th: str
    dignity: PlanetaryDignity
    navamsa_rasi_index: int = Field(..., ge=0, le=11)
    navamsa_rasi_th: str
    drekkana_rasi_index: int = Field(..., ge=0, le=11)
    drekkana_rasi_th: str
    is_retrograde: bool = False

    @property
    def house_id(self) -> int:
        return self.house_number

    @property
    def longitude_deg(self) -> float:
        return self.longitude

    @property
    def sign_id(self) -> int:
        return self.rasi_index + 1

    @property
    def deg_in_sign(self) -> float:
        return self.degree_in_rasi


class HouseDetail(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    house_number: int = Field(..., ge=1, le=12)
    house_name_th: str
    rasi_index: int = Field(..., ge=0, le=11)
    rasi_name_th: str
    planets: List[int] = Field(default_factory=list)
    lord_planet_id: int = Field(..., ge=0, le=9)

    @property
    def house_id(self) -> int:
        return self.house_number

    @property
    def sign_id(self) -> int:
        return self.rasi_index + 1


class ThaiAstrologyResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ayanamsa_degree: float
    lagna: LagnaInfo
    planets: Dict[int, PlanetPosition]
    houses: List[HouseDetail]
    primary_lucky_planet: int
    secondary_lucky_planet: int
    house_lord_digits: List[int]
    lucky_numbers: List[int]

    @property
    def ayanamsa_value(self) -> float:
        return self.ayanamsa_degree

    @property
    def auspicious_digits(self) -> List[int]:
        return self.lucky_numbers

    def get_planet(self, planet_id: int) -> Optional[PlanetPosition]:
        """Returns PlanetPosition for given planet_id (0-9)."""
        return self.planets.get(planet_id)

    def get_house(self, house_number: int) -> Optional[HouseDetail]:
        """Returns HouseDetail for house_number (1-12)."""
        if 1 <= house_number <= 12:
            return self.houses[house_number - 1]
        return None


# =============================================================================
# HELPER FUNCTIONS & ASTRONOMICAL CALCULATIONS
# =============================================================================

def get_province_coordinates(province_name: str) -> Tuple[float, float]:
    """Resolves Thai province name to (latitude, longitude). Defaults to Bangkok."""
    if not province_name:
        return PROVINCE_COORDINATES["กรุงเทพมหานคร"]
    clean_name = province_name.strip()
    return PROVINCE_COORDINATES.get(clean_name, PROVINCE_COORDINATES["กรุงเทพมหานคร"])


def calculate_julian_day(year: int, month: int, day: int, ut_hours: float) -> float:
    """Calculates Julian Day Number for given UTC date and fractional hour."""
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + (a // 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5 + (ut_hours / 24.0)
    return jd


def calculate_lahiri_ayanamsa(julian_day: float) -> float:
    """Calculates Lahiri Ayanamsa offset angle in degrees for given Julian Day."""
    t = (julian_day - 2451545.0) / 36525.0
    ayanamsa = 23.85305556 + (1.39697128 * t) + (0.00030878 * t * t)
    return ayanamsa % 360.0


def calculate_d9_navamsa(sidereal_longitude: float) -> int:
    """
    Computes D9 Navamsa sign index (0..11).
    Formula: floor((sid_deg * 60) / 200) % 12
    """
    return int((sidereal_longitude * 60.0) // 200.0) % 12


def calculate_d3_drekkana(sidereal_longitude: float) -> int:
    """
    Computes D3 Drekkana sign index (0..11).
    Formula: (sign_idx + 4 * decan_idx) % 12
    """
    sign_idx = int(sidereal_longitude // 30.0) % 12
    deg_in_sign = sidereal_longitude % 30.0
    decan_idx = int(deg_in_sign // 10.0) % 3
    return (sign_idx + 4 * decan_idx) % 12


def determine_planetary_dignity(planet_id: int, sign_index: int) -> PlanetaryDignity:
    """Determines planetary dignity (อุจจ์, เกษตร, นิจ, ประ, ปกติ)."""
    # 1. Ucc (Exalted) - checked before Kaset so Mercury in Virgo is evaluated as UCC
    if EXALTED_SIGNS.get(planet_id) == sign_index:
        return PlanetaryDignity.UCC

    # 2. Kaset (Own sign)
    if SIGN_RULERS[sign_index] == planet_id:
        return PlanetaryDignity.KASET
    
    # 3. Nit (Debilitated)
    if DEBILITATED_SIGNS.get(planet_id) == sign_index:
        return PlanetaryDignity.NIT
    
    # 4. Pra (Detriment - opposite sign of own Kaset)
    own_signs = [i for i, r in enumerate(SIGN_RULERS) if r == planet_id]
    pra_signs = [(s + 6) % 12 for s in own_signs]
    if sign_index in pra_signs:
        return PlanetaryDignity.PRA
    
    return PlanetaryDignity.NORMAL


def _calculate_pure_python_planetary_positions(jd: float, ayanamsa: float) -> Dict[int, float]:
    """
    Pure Python astronomical ephemeris for 10 planets (Tropical -> Sidereal longitudes).
    Uses Keplerian mean orbital elements and perturbations.
    """
    t = (jd - 2451545.0) / 36525.0
    rad = math.radians

    # 1. Sun
    l0_sun = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) % 360.0
    m_sun = (357.52911 + 35999.05029 * t - 0.0001537 * t * t) % 360.0
    c_sun = (1.914602 - 0.004817 * t) * math.sin(rad(m_sun)) + \
            (0.019993 - 0.000101 * t) * math.sin(rad(2 * m_sun)) + \
            0.000289 * math.sin(rad(3 * m_sun))
    sun_trop = (l0_sun + c_sun) % 360.0

    # 2. Moon
    l_moon = (218.3164477 + 481267.88123421 * t) % 360.0
    m_moon = (134.9633964 + 477198.8675055 * t) % 360.0
    f_moon = (93.2720950 + 483202.0175233 * t) % 360.0
    d_moon = (297.8501921 + 445267.1114034 * t) % 360.0
    moon_trop = (l_moon + 6.2886 * math.sin(rad(m_moon)) + \
                 1.2740 * math.sin(rad(2 * d_moon - m_moon)) + \
                 0.6583 * math.sin(rad(2 * d_moon)) + \
                 0.2136 * math.sin(rad(2 * m_moon)) - \
                 0.1851 * math.sin(rad(m_sun)) - \
                 0.1143 * math.sin(rad(2 * f_moon))) % 360.0

    # 3. Mars
    l_mars = (355.45332 + 19140.30268 * t) % 360.0
    m_mars = (19.3730 + 19139.9750 * t) % 360.0
    mars_trop = (l_mars + 10.691 * math.sin(rad(m_mars)) + 0.623 * math.sin(rad(2 * m_mars))) % 360.0

    # 4. Mercury
    m_merc = (174.7948 + 149472.5150 * t) % 360.0
    merc_rel = 23.44 * math.sin(rad(m_merc - m_sun)) + 2.0 * math.sin(rad(2 * (m_merc - m_sun)))
    merc_trop = (sun_trop + merc_rel) % 360.0

    # 5. Jupiter
    l_jup = (34.40438 + 3034.74612 * t) % 360.0
    m_jup = (20.0202 + 3034.6920 * t) % 360.0
    jup_trop = (l_jup + 5.555 * math.sin(rad(m_jup)) + 0.168 * math.sin(rad(2 * m_jup))) % 360.0

    # 6. Venus
    m_ven = (50.4082 + 58517.4490 * t) % 360.0
    ven_rel = 46.3 * math.sin(rad(m_ven - m_sun))
    ven_trop = (sun_trop + ven_rel) % 360.0

    # 7. Saturn
    l_sat = (49.94432 + 1222.49362 * t) % 360.0
    m_sat = (317.0207 + 1222.1140 * t) % 360.0
    sat_trop = (l_sat + 6.358 * math.sin(rad(m_sat)) + 0.220 * math.sin(rad(2 * m_sat))) % 360.0

    # 8. Rahu (Mean North Node)
    rahu_node = (125.044555 - 1934.1361849 * t + 0.0020762 * t * t) % 360.0
    rahu_trop = rahu_node % 360.0

    # 9. Ketu (South Node = Rahu + 180°)
    ketu_trop = (rahu_trop + 180.0) % 360.0

    # 0. Uranus
    l_uranus = (313.23218 + 428.48641 * t) % 360.0
    m_uranus = (142.5905 + 428.3790 * t) % 360.0
    uranus_trop = (l_uranus + 3.0 * math.sin(rad(m_uranus))) % 360.0

    tropical_longitudes = {
        0: uranus_trop,
        1: sun_trop,
        2: moon_trop,
        3: mars_trop,
        4: merc_trop,
        5: jup_trop,
        6: ven_trop,
        7: sat_trop,
        8: rahu_trop,
        9: ketu_trop,
    }

    # Convert to Sidereal by subtracting Lahiri Ayanamsa
    sidereal_longitudes = {
        pid: (trop_deg - ayanamsa) % 360.0
        for pid, trop_deg in tropical_longitudes.items()
    }

    return sidereal_longitudes


def calculate_lagna_sidereal(jd: float, ut_hours: float, lat: float, lon: float, ayanamsa: float) -> float:
    """Calculates Sidereal Lagna (Ascendant) longitude in degrees."""
    jd0 = math.floor(jd - 0.5) + 0.5
    t0 = (jd0 - 2451545.0) / 36525.0
    gmst0 = 100.46061837 + (36000.770053608 * t0) + (0.000387933 * t0 * t0)
    gmst = (gmst0 + 1.00273790935 * ut_hours * 15.0) % 360.0
    lst = (gmst + lon) % 360.0

    rad = math.radians
    eps = 23.439291 - 0.0130042 * t0

    y = math.cos(rad(lst))
    x = -math.sin(rad(lst)) * math.cos(rad(eps)) - math.tan(rad(lat)) * math.sin(rad(eps))

    asc_trop = math.degrees(math.atan2(y, x)) % 360.0
    asc_sid = (asc_trop - ayanamsa) % 360.0
    return asc_sid


def extract_lucky_astrology_digits(res: ThaiAstrologyResult) -> List[int]:
    """
    Extracts ordered lucky digits (0-9) from planetary placements, Ascendant lord,
    Putta lord, and Labha lord for Layer 2 Composite Recommender.
    """
    digits = []
    
    # 1. Primary lucky planet (Lagna lord)
    digits.append(res.primary_lucky_planet)
    
    # 2. Secondary lucky planet (Labha/Putta lord)
    digits.append(res.secondary_lucky_planet)
    
    # 3. House lords
    for d in res.house_lord_digits:
        if d not in digits:
            digits.append(d)

    # 4. Exalted / Kaset planets
    for pid, p in res.planets.items():
        if p.dignity in (PlanetaryDignity.KASET, PlanetaryDignity.UCC):
            if pid not in digits:
                digits.append(pid)

    # Ensure minimum 3 lucky digits
    for default_digit in [1, 5, 9, 2, 6, 8, 3, 4, 7, 0]:
        if len(digits) >= 5:
            break
        if default_digit not in digits:
            digits.append(default_digit)

    return digits


# =============================================================================
# PUBLIC SEAM FUNCTION
# =============================================================================

def calculate_thai_astrology(
    birth_date: str,
    birth_time: str = "12:00",
    birth_province: str = "กรุงเทพมหานคร",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> ThaiAstrologyResult:
    """
    Main calculation entry point for Thai Astrology Natal Chart.
    
    Parameters:
        birth_date: str (YYYY-MM-DD)
        birth_time: str (HH:MM or HH:MM:SS, default "12:00")
        birth_province: str (Thai province name, default "กรุงเทพมหานคร")
        latitude: Optional float
        longitude: Optional float
        
    Returns:
        ThaiAstrologyResult
    """
    # 1. Parse Date
    try:
        dt_date = datetime.strptime(birth_date.strip(), "%Y-%m-%d").date()
    except Exception as e:
        raise ValueError(f"Invalid birth date '{birth_date}'. Expected format YYYY-MM-DD.") from e

    # 2. Parse Time
    clean_time = birth_time.strip() if birth_time else "12:00"
    try:
        if len(clean_time.split(":")) == 2:
            dt_time = datetime.strptime(clean_time, "%H:%M").time()
        else:
            dt_time = datetime.strptime(clean_time, "%H:%M:%S").time()
    except Exception:
        dt_time = time(12, 0, 0)

    # 3. Resolve Lat/Lon
    if latitude is not None and longitude is not None:
        lat, lon = float(latitude), float(longitude)
    else:
        lat, lon = get_province_coordinates(birth_province)

    # 4. Universal Time (UT) & Julian Day (UTC+7 for Thailand ICT)
    ut_hours = dt_time.hour + (dt_time.minute / 60.0) + (dt_time.second / 3600.0) - 7.0
    jd = calculate_julian_day(dt_date.year, dt_date.month, dt_date.day, ut_hours)

    # 5. Ayanamsa
    ayanamsa = calculate_lahiri_ayanamsa(jd)

    # 6. Planetary Positions (0..9)
    try:
        import swisseph as swe
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        planet_swe_codes = {
            1: swe.SUN, 2: swe.MOON, 3: swe.MARS, 4: swe.MERCURY,
            5: swe.JUPITER, 6: swe.VENUS, 7: swe.SATURN, 8: swe.MEAN_NODE,
            0: swe.URANUS
        }
        sidereal_longitudes = {}
        for pid in range(10):
            if pid == 9:  # Ketu = Rahu + 180°
                sidereal_longitudes[9] = (sidereal_longitudes[8] + 180.0) % 360.0
            else:
                res_swe, _ = swe.calc_ut(jd, planet_swe_codes[pid], swe.FLG_SIDEREAL)
                sidereal_longitudes[pid] = res_swe[0] % 360.0
    except ImportError:
        sidereal_longitudes = _calculate_pure_python_planetary_positions(jd, ayanamsa)

    # 7. Lagna Calculation
    lagna_sid = calculate_lagna_sidereal(jd, ut_hours, lat, lon, ayanamsa)
    lagna_sign_idx = int(lagna_sid // 30.0) % 12
    lagna_deg_in_sign = lagna_sid % 30.0
    lagna_d9 = calculate_d9_navamsa(lagna_sid)
    lagna_d3 = calculate_d3_drekkana(lagna_sid)

    lagna_info = LagnaInfo(
        longitude=lagna_sid,
        rasi_index=lagna_sign_idx,
        rasi_name_th=THAI_SIGN_NAMES[lagna_sign_idx],
        degree_in_rasi=lagna_deg_in_sign,
        navamsa_rasi_index=lagna_d9,
        navamsa_rasi_th=THAI_SIGN_NAMES[lagna_d9],
        drekkana_rasi_index=lagna_d3,
        drekkana_rasi_th=THAI_SIGN_NAMES[lagna_d3],
    )

    # 8. House Calculations (Whole Sign System starting from Lagna sign)
    houses_list: List[HouseDetail] = []
    house_sign_map: Dict[int, int] = {}  # house_number (1..12) -> sign_index (0..11)
    
    for h in range(1, 13):
        sign_idx = (lagna_sign_idx + h - 1) % 12
        house_sign_map[h] = sign_idx
        lord_id = SIGN_RULERS[sign_idx]
        houses_list.append(HouseDetail(
            house_number=h,
            house_name_th=THAI_HOUSE_NAMES[h - 1],
            rasi_index=sign_idx,
            rasi_name_th=THAI_SIGN_NAMES[sign_idx],
            planets=[],
            lord_planet_id=lord_id,
        ))

    # 9. Planet Positions Mapping
    planets_dict: Dict[int, PlanetPosition] = {}
    for pid in range(10):
        p_long = sidereal_longitudes[pid]
        p_sign_idx = int(p_long // 30.0) % 12
        p_deg_in_sign = p_long % 30.0
        
        # House number relative to Lagna sign
        p_house_num = ((p_sign_idx - lagna_sign_idx) % 12) + 1
        houses_list[p_house_num - 1].planets.append(pid)
        
        p_dignity = determine_planetary_dignity(pid, p_sign_idx)
        p_d9 = calculate_d9_navamsa(p_long)
        p_d3 = calculate_d3_drekkana(p_long)

        planets_dict[pid] = PlanetPosition(
            planet_id=pid,
            planet_name_th=THAI_PLANET_NAMES[pid],
            planet_name_en=ENGLISH_PLANET_NAMES[pid],
            longitude=p_long,
            rasi_index=p_sign_idx,
            rasi_name_th=THAI_SIGN_NAMES[p_sign_idx],
            degree_in_rasi=p_deg_in_sign,
            house_number=p_house_num,
            house_name_th=THAI_HOUSE_NAMES[p_house_num - 1],
            dignity=p_dignity,
            navamsa_rasi_index=p_d9,
            navamsa_rasi_th=THAI_SIGN_NAMES[p_d9],
            drekkana_rasi_index=p_d3,
            drekkana_rasi_th=THAI_SIGN_NAMES[p_d3],
            is_retrograde=False,
        )

    # 10. Extract Key Lords & Lucky Digits
    primary_lord = SIGN_RULERS[lagna_sign_idx]                 # Lagna lord (ตนุ)
    putta_sign = house_sign_map[5]
    putta_lord = SIGN_RULERS[putta_sign]                       # Putta lord (ปุตตะ)
    subha_sign = house_sign_map[9]
    subha_lord = SIGN_RULERS[subha_sign]                       # Subha lord (ศุภะ)
    labha_sign = house_sign_map[11]
    labha_lord = SIGN_RULERS[labha_sign]                       # Labha lord (ลาภะ)

    secondary_lord = labha_lord if labha_lord != primary_lord else putta_lord
    house_lord_digits = [primary_lord, putta_lord, subha_lord, labha_lord]

    partial_res = ThaiAstrologyResult(
        ayanamsa_degree=ayanamsa,
        lagna=lagna_info,
        planets=planets_dict,
        houses=houses_list,
        primary_lucky_planet=primary_lord,
        secondary_lucky_planet=secondary_lord,
        house_lord_digits=house_lord_digits,
        lucky_numbers=[],
    )

    lucky_digits = extract_lucky_astrology_digits(partial_res)
    partial_res.lucky_numbers = lucky_digits

    return partial_res
