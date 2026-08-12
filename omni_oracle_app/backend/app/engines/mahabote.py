"""
Burmese Mahabote Engine (มหาภูติพม่า)
Module: app.engines.mahabote
Layer 1 Core Calculation Engine for Omni-Oracle Thai Divination System.
"""

from datetime import date, datetime, time
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field


class DayOfWeek(int, Enum):
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY_DAY = 4
    JUPITER = 5  # Thursday
    VENUS = 6    # Friday
    SATURN = 7   # Saturday
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


class PositionDetail(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    position_key: str
    position_name_th: str
    position_name_en: str
    planet_digit: int = Field(..., ge=1, le=7)
    planet_name_th: str
    taksa_category: str
    is_kalayok_auspicious: bool = False
    is_kalayok_inauspicious: bool = False


class MahaboteChart(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cs_year: int
    cs_remainder: int = Field(..., ge=1, le=7)
    birth_day_digit: int = Field(..., ge=1, le=8)
    positions: Dict[str, PositionDetail]
    chart_matrix: List[List[int]]
    position_order: List[str] = [
        "thanang", "pita", "mata", "phoka", "matchima", "atta", "hina"
    ]


class TaksaPlanetDetail(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

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

    birth_date: str
    birth_time: Optional[str] = None
    is_wednesday_night: bool = False
    songkran_adjusted: bool = False
    cs_year: int
    cs_remainder: int = Field(..., ge=1, le=7)
    day_of_week: int = Field(..., ge=1, le=8)
    day_name_th: str
    chart: MahaboteChart
    taksa: TaksaInfo
    kalayok: KalayokInfo
    lucky_digits: LuckyDigitsResult


class MahaboteEngine:
    """Core calculation engine for Burmese Mahabote."""

    SONGKRAN_CUTOFF_MONTH: int = 4
    SONGKRAN_CUTOFF_DAY: int = 16

    # Position definitions and descriptions
    POSITIONS_INFO: List[Tuple[str, str, str]] = [
        ("thanang", "ธนัง", "Thanang"),
        ("pita", "ปิตา", "Pita"),
        ("mata", "มาตา", "Mata"),
        ("phoka", "โภคา", "Phoka"),
        ("matchima", "มัชฌิมา", "Majjhima"),
        ("atta", "อัตตะ", "Atta"),
        ("hina", "หินะ", "Hina"),
    ]

    PLANET_NAMES_TH: Dict[int, str] = {
        1: "อาทิตย์",
        2: "จันทร์",
        3: "อังคาร",
        4: "พุธ",
        5: "พฤหัสบดี",
        6: "ศุกร์",
        7: "เสาร์",
        8: "ราหู",
    }

    DAY_NAMES_TH: Dict[int, str] = {
        1: "อาทิตย์",
        2: "จันทร์",
        3: "อังคาร",
        4: "พุธ (กลางวัน)",
        5: "พฤหัสบดี",
        6: "ศุกร์",
        7: "เสาร์",
        8: "พุธ (กลางคืน - ราหู)",
    }

    TAKSA_ORDER: List[TaksaCategory] = [
        TaksaCategory.BRIVAR,
        TaksaCategory.AYU,
        TaksaCategory.DECH,
        TaksaCategory.SRI,
        TaksaCategory.MULA,
        TaksaCategory.INDUSTAH,
        TaksaCategory.MONTRII,
        TaksaCategory.KALAKINI,
    ]

    # Taksa 8-planet wheel order
    TAKSA_WHEEL: List[int] = [1, 2, 3, 4, 7, 5, 8, 6]

    # Kalayok lookup table by CS Remainder (1..7)
    # Format: cs_remainder -> (Thongchai, Athipati, Upabat, Lokawinat)
    KALAYOK_TABLE: Dict[int, Tuple[int, int, int, int]] = {
        1: (6, 5, 2, 3),
        2: (3, 2, 7, 1),
        3: (7, 6, 5, 4),
        4: (4, 3, 1, 7),
        5: (1, 7, 4, 2),
        6: (5, 4, 6, 5),
        7: (2, 1, 3, 6),
    }

    @classmethod
    def calculate_cs(cls, birth_date: date) -> Tuple[int, bool]:
        """Calculates CS year considering April 16 Songkran boundary."""
        be = birth_date.year + 543
        if (birth_date.month < cls.SONGKRAN_CUTOFF_MONTH) or (
            birth_date.month == cls.SONGKRAN_CUTOFF_MONTH
            and birth_date.day < cls.SONGKRAN_CUTOFF_DAY
        ):
            cs_year = be - 1182  # AD - 639
            songkran_adjusted = True
        else:
            cs_year = be - 1181  # AD - 638
            songkran_adjusted = False
        return cs_year, songkran_adjusted

    @classmethod
    def calculate_cs_remainder(cls, cs_year: int) -> int:
        """Calculates CS % 7, mapping remainder 0 to 7."""
        rem = cs_year % 7
        return 7 if rem == 0 else rem

    @classmethod
    def determine_day_of_week(
        cls,
        dt: date,
        birth_time: Optional[time] = None,
        is_wednesday_night: Optional[bool] = None,
    ) -> DayOfWeek:
        """Determines day digit 1..8 including Wednesday day/night logic."""
        # Python weekday: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
        weekday_map = {6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
        day_digit = weekday_map[dt.weekday()]

        if day_digit == 4:
            if is_wednesday_night is True:
                return DayOfWeek.WEDNESDAY_NIGHT
            elif is_wednesday_night is False:
                return DayOfWeek.WEDNESDAY_DAY
            elif birth_time is not None:
                if birth_time.hour >= 18 or birth_time.hour < 6:
                    return DayOfWeek.WEDNESDAY_NIGHT
                else:
                    return DayOfWeek.WEDNESDAY_DAY
            else:
                return DayOfWeek.WEDNESDAY_DAY

        return DayOfWeek(day_digit)

    @classmethod
    def calculate_taksa(cls, day_digit: int) -> TaksaInfo:
        """Calculates 8-planet Taksa alignment."""
        # Locate day_digit in TAKSA_WHEEL
        idx = cls.TAKSA_WHEEL.index(day_digit)
        taksa_map: Dict[int, str] = {}
        planets_detail: List[TaksaPlanetDetail] = []

        brivar_p = day_digit
        sri_p = 0
        kalakini_p = 0

        for i in range(8):
            planet = cls.TAKSA_WHEEL[(idx + i) % 8]
            cat = cls.TAKSA_ORDER[i]
            taksa_map[planet] = cat.value
            is_sri = cat == TaksaCategory.SRI
            is_kalakini = cat == TaksaCategory.KALAKINI

            if is_sri:
                sri_p = planet
            if is_kalakini:
                kalakini_p = planet

            planets_detail.append(
                TaksaPlanetDetail(
                    planet_digit=planet,
                    planet_name_th=cls.PLANET_NAMES_TH[planet],
                    category=cat.value,
                    is_kalakini=is_kalakini,
                    is_sri=is_sri,
                )
            )

        return TaksaInfo(
            birth_day_digit=day_digit,
            brivar_planet=brivar_p,
            sri_planet=sri_p,
            kalakini_planet=kalakini_p,
            taksa_map=taksa_map,
            planets=planets_detail,
        )

    @classmethod
    def calculate_kalayok(cls, cs_year: int) -> KalayokInfo:
        """Calculates annual Kalayok positions."""
        cs_rem = cls.calculate_cs_remainder(cs_year)
        tc, at, yb, lv = cls.KALAYOK_TABLE[cs_rem]
        return KalayokInfo(
            cs_year=cs_year,
            thongchai_digit=tc,
            atipati_digit=at,
            yamabat_digit=yb,
            lokavinas_digit=lv,
        )

    @classmethod
    def build_chart(
        cls,
        cs_remainder: int,
        day_digit: int,
        taksa: TaksaInfo,
        kalayok: KalayokInfo,
    ) -> MahaboteChart:
        """Constructs 7-position Mahabote chart."""
        positions: Dict[str, PositionDetail] = {}

        # 7-house assignment starts remainder at Thanang (index 0)
        pos_digits: List[int] = []
        for i in range(7):
            key, name_th, name_en = cls.POSITIONS_INFO[i]
            planet_d = ((cs_remainder - 1 + i) % 7) + 1
            pos_digits.append(planet_d)

            taksa_cat = taksa.taksa_map.get(planet_d, "บริวาร")
            is_kalayok_ausp = planet_d in (
                kalayok.thongchai_digit,
                kalayok.atipati_digit,
            )
            is_kalayok_inausp = planet_d in (
                kalayok.yamabat_digit,
                kalayok.lokavinas_digit,
            )

            positions[key] = PositionDetail(
                position_key=key,
                position_name_th=name_th,
                position_name_en=name_en,
                planet_digit=planet_d,
                planet_name_th=cls.PLANET_NAMES_TH[planet_d],
                taksa_category=taksa_cat,
                is_kalayok_auspicious=is_kalayok_ausp,
                is_kalayok_inauspicious=is_kalayok_inausp,
            )

        chart_matrix = [
            [pos_digits[0], pos_digits[1], pos_digits[2]],
            [pos_digits[3], pos_digits[4], pos_digits[5]],
            [pos_digits[6]],
        ]

        return MahaboteChart(
            cs_year=kalayok.cs_year,
            cs_remainder=cs_remainder,
            birth_day_digit=day_digit,
            positions=positions,
            chart_matrix=chart_matrix,
        )

    @classmethod
    def extract_lucky_digits(
        cls,
        chart: MahaboteChart,
        taksa: TaksaInfo,
        kalayok: KalayokInfo,
    ) -> LuckyDigitsResult:
        """Extracts primary, secondary, avoid digits, 2-digit pairs and power score."""

        pos_weights: Dict[str, float] = {
            "thanang": 3.0,
            "phoka": 2.5,
            "atta": 2.0,
            "pita": 2.0,
            "mata": 2.0,
            "matchima": 1.0,
            "hina": -3.0,
        }

        taksa_weights: Dict[str, float] = {
            TaksaCategory.SRI.value: 3.0,
            TaksaCategory.MULA.value: 2.5,
            TaksaCategory.MONTRII.value: 2.5,
            TaksaCategory.DECH.value: 2.0,
            TaksaCategory.AYU.value: 1.5,
            TaksaCategory.BRIVAR.value: 1.0,
            TaksaCategory.INDUSTAH.value: 1.0,
            TaksaCategory.KALAKINI.value: -3.0,
        }

        planet_scores: Dict[int, float] = {}
        avoid_set = set()

        # Add Taksa Kalakini and Kalayok bad digits to avoid
        avoid_set.add(taksa.kalakini_planet)
        avoid_set.add(kalayok.yamabat_digit)
        avoid_set.add(kalayok.lokavinas_digit)

        for key, pos in chart.positions.items():
            pw = pos_weights.get(key, 0.0)
            tw = taksa_weights.get(pos.taksa_category, 0.0)
            kw = 0.0
            if pos.planet_digit in (kalayok.thongchai_digit, kalayok.atipati_digit):
                kw = 2.5
            elif pos.planet_digit in (kalayok.yamabat_digit, kalayok.lokavinas_digit):
                kw = -2.5

            if key == "hina":
                avoid_set.add(pos.planet_digit)

            tot = pw + tw + kw
            planet_scores[pos.planet_digit] = tot
            if tot < 0:
                avoid_set.add(pos.planet_digit)

        # Build primary and secondary digits list
        scored_planets = [
            (d, planet_scores.get(d, 0.0))
            for d in range(1, 8)
            if d not in avoid_set
        ]
        scored_planets.sort(key=lambda x: x[1], reverse=True)

        primary_digits = [d for d, s in scored_planets if s >= 3.0]
        if not primary_digits and scored_planets:
            primary_digits = [scored_planets[0][0]]
            if len(scored_planets) > 1:
                primary_digits.append(scored_planets[1][0])

        secondary_digits = [
            d for d, s in scored_planets if d not in primary_digits and s >= 0.5
        ]

        avoid_digits = sorted(list(avoid_set))

        # Planetary Harmony Pairs (คู่มิตร, คู่สมพล, คู่ธาตุ, คู่ศัตรู)
        friendly_pairs = {(1, 5), (2, 4), (3, 6), (7, 8)}
        power_pairs = {(1, 6), (2, 8), (3, 5), (4, 7)}
        element_pairs = {(1, 7), (2, 5), (3, 8), (4, 6)}
        enemy_pairs = {(1, 3), (2, 5), (4, 8), (6, 7)}

        def get_bond(d1: int, d2: int) -> float:
            pair = (min(d1, d2), max(d1, d2))
            if pair in friendly_pairs:
                return 2.0
            if pair in power_pairs:
                return 1.5
            if pair in element_pairs:
                return 1.0
            if pair in enemy_pairs:
                return -2.0
            return 0.0

        # Candidate digits for pairs
        candidate_digits = primary_digits + secondary_digits
        if len(candidate_digits) < 2:
            candidate_digits = [d for d in range(1, 8) if d not in avoid_digits]

        pair_scores: List[Tuple[str, float]] = []
        for i in range(len(candidate_digits)):
            for j in range(len(candidate_digits)):
                d1 = candidate_digits[i]
                d2 = candidate_digits[j]
                if d1 in avoid_set or d2 in avoid_set:
                    continue
                pair_str = f"{d1}{d2}"
                base_s = planet_scores.get(d1, 1.0) + planet_scores.get(d2, 1.0)
                bond_s = get_bond(d1, d2)
                pair_scores.append((pair_str, base_s + bond_s))

        pair_scores.sort(key=lambda x: x[1], reverse=True)
        recommended_pairs: List[str] = []
        seen_pairs = set()
        for p_str, _ in pair_scores:
            if p_str not in seen_pairs:
                recommended_pairs.append(p_str)
                seen_pairs.add(p_str)
            if len(recommended_pairs) >= 6:
                break

        # Fallback pairs if candidate list produced few
        if len(recommended_pairs) < 3 and primary_digits:
            for p in primary_digits:
                for d in [3, 5, 2, 4, 7, 6, 1]:
                    if d not in avoid_set:
                        p_str = f"{p}{d}"
                        if p_str not in seen_pairs:
                            recommended_pairs.append(p_str)
                            seen_pairs.add(p_str)

        # Power score calculation (0.0 - 100.0)
        top_sum = sum(s for _, s in scored_planets[:3]) if scored_planets else 0.0
        power_score = round(min(100.0, max(10.0, (top_sum / 20.0) * 100.0)), 1)

        return LuckyDigitsResult(
            primary_digits=primary_digits,
            secondary_digits=secondary_digits,
            avoid_digits=avoid_digits,
            recommended_2digit_pairs=recommended_pairs,
            power_score=power_score,
        )

    def execute(
        self,
        birth_date: Union[str, date, datetime],
        birth_time: Optional[Union[str, time]] = None,
        is_wednesday_night: Optional[bool] = None,
    ) -> MahaboteResult:
        """Main execution seam."""
        # 1. Parse birth_date
        if isinstance(birth_date, str):
            try:
                b_date = date.fromisoformat(birth_date)
            except ValueError:
                raise ValueError(f"Invalid birth_date ISO format: {birth_date}")
        elif isinstance(birth_date, datetime):
            b_date = birth_date.date()
        elif isinstance(birth_date, date):
            b_date = birth_date
        else:
            raise TypeError(f"Unsupported birth_date type: {type(birth_date)}")

        # 2. Parse birth_time
        b_time: Optional[time] = None
        if isinstance(birth_time, str):
            if birth_time.strip():
                try:
                    parts = birth_time.split(":")
                    b_time = time(int(parts[0]), int(parts[1]))
                except Exception:
                    raise ValueError(f"Invalid birth_time format: {birth_time}")
        elif isinstance(birth_time, time):
            b_time = birth_time

        # 3. Calculate CS & Remainder
        cs_year, songkran_adjusted = cls.calculate_cs(b_date)
        cs_remainder = cls.calculate_cs_remainder(cs_year)

        # 4. Day of Week
        day_enum = cls.determine_day_of_week(
            b_date, birth_time=b_time, is_wednesday_night=is_wednesday_night
        )
        day_digit = day_enum.value
        is_wed_night = day_enum == DayOfWeek.WEDNESDAY_NIGHT

        # 5. Taksa & Kalayok
        taksa = cls.calculate_taksa(day_digit)
        kalayok = cls.calculate_kalayok(cs_year)

        # 6. Build Chart
        chart = cls.build_chart(cs_remainder, day_digit, taksa, kalayok)

        # 7. Extract Lucky Digits
        lucky_digits = cls.extract_lucky_digits(chart, taksa, kalayok)

        return MahaboteResult(
            birth_date=b_date.isoformat(),
            birth_time=b_time.strftime("%H:%M") if b_time else None,
            is_wednesday_night=is_wed_night,
            songkran_adjusted=songkran_adjusted,
            cs_year=cs_year,
            cs_remainder=cs_remainder,
            day_of_week=day_digit,
            day_name_th=cls.DAY_NAMES_TH[day_digit],
            chart=chart,
            taksa=taksa,
            kalayok=kalayok,
            lucky_digits=lucky_digits,
        )


def calculate_mahabote(
    birth_date: Union[str, date, datetime],
    birth_time: Optional[Union[str, time]] = None,
    is_wednesday_night: Optional[bool] = None,
) -> MahaboteResult:
    """Public seam entry point for pytest suite and FastAPI endpoints."""
    engine = MahaboteEngine()
    return engine.execute(
        birth_date=birth_date,
        birth_time=birth_time,
        is_wednesday_night=is_wednesday_night,
    )
