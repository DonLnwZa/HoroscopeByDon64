"""
7-Digit 9-Base Numerology Engine (วิชาเลข 7 ตัว 9 ฐาน)
Module: app.engines.numerology_7x9
Layer 1 Core Calculation Engine for Omni-Oracle Thai Divination System.
"""

from datetime import datetime
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
    thai_lunar_month: int = Field(..., ge=1, le=12)
    lunar_month_name_th: str
    thai_lunar_year: int = Field(..., ge=1, le=12)
    zodiac_year_name_th: str

    matrix: NumerologyMatrix
    base_1_row: List[int]
    base_2_row: List[int]
    base_3_row: List[int]
    base_4_row: List[int]
    base_5_row: List[int]
    base_6_row: List[int]
    base_7_row: List[int]
    base_8_row: List[int]
    base_9_row: List[int]

    house_names: List[List[str]]
    houses: Dict[str, HouseDetail7x9]
    house_collisions: Dict[int, List[str]]
    collisions: Dict[int, BaseCollisionInfo]
    auspicious_houses: List[str]
    inauspicious_houses: List[str]
    primary_lucky_digits: List[int]
    secondary_lucky_digits: List[int]
    lucky_numbers: List[int]

    @property
    def lunar_month(self) -> int:
        return self.thai_lunar_month

    @property
    def zodiac_year(self) -> int:
        return self.thai_lunar_year

    @property
    def primary_lucky_digit(self) -> int:
        return self.primary_lucky_digits[0] if self.primary_lucky_digits else 1

    @property
    def secondary_lucky_digit(self) -> int:
        return self.secondary_lucky_digits[0] if self.secondary_lucky_digits else 2

    def get_cell(self, row: int, col: int) -> int:
        """Returns cell value at 1-indexed row (1..9) and col (1..7)."""
        if not (1 <= row <= 9 and 1 <= col <= 7):
            raise ValueError("Row must be between 1..9 and Col must be between 1..7")
        return self.matrix.matrix_grid[row - 1][col - 1]

    def get_house_name(self, row: int, col: int) -> str:
        """Returns house name at 1-indexed row (1..3) and col (1..7)."""
        if not (1 <= row <= 3 and 1 <= col <= 7):
            raise ValueError("Row must be between 1..3 and Col must be between 1..7")
        return self.house_names[row - 1][col - 1]

    def get_house(self, house_name_th: str) -> Optional[HouseDetail7x9]:
        return self.houses.get(house_name_th)

    def get_digit_collision(self, digit: int) -> Optional[BaseCollisionInfo]:
        return self.collisions.get(digit)


# Domain constants
DAY_NAMES_TH = {
    1: "วันอาทิตย์",
    2: "วันจันทร์",
    3: "วันอังคาร",
    4: "วันพุธ",
    5: "วันพฤหัสบดี",
    6: "วันศุกร์",
    7: "วันเสาร์",
}

LUNAR_MONTH_NAMES_TH = {
    1: "เดือน 1 (อ้าย)",
    2: "เดือน 2 (ยี่)",
    3: "เดือน 3",
    4: "เดือน 4",
    5: "เดือน 5",
    6: "เดือน 6",
    7: "เดือน 7",
    8: "เดือน 8",
    9: "เดือน 9",
    10: "เดือน 10",
    11: "เดือน 11",
    12: "เดือน 12",
}

ZODIAC_YEAR_NAMES_TH = {
    1: "ปีชวด",
    2: "ปีฉลู",
    3: "ปีขาล",
    4: "ปีเถาะ",
    5: "ปีมะโรง",
    6: "ปีมะเส็ง",
    7: "ปีมะเมีย",
    8: "ปีมะแม",
    9: "ปีวอก",
    10: "ปีระกา",
    11: "ปีจอ",
    12: "ปีกุน",
}

# 21 Astrological House Matrix Layout across Rows 1-3
HOUSE_MATRIX_TAXONOMY = [
    # Row 1 (Day Base): 0..6
    [
        ("อัตตะ", "Atta", HouseType.NEUTRAL),
        ("หินะ", "Hina", HouseType.INAUSPICIUS),
        ("ธนัง", "Thanang", HouseType.AUSPICIOUS),
        ("ปิตา", "Pita", HouseType.NEUTRAL),
        ("มาตา", "Mata", HouseType.NEUTRAL),
        ("โภคา", "Phokha", HouseType.AUSPICIOUS),
        ("มัชฌิมา", "Majjhima", HouseType.NEUTRAL),
    ],
    # Row 2 (Month Base): 0..6
    [
        ("ตะนุ", "Tanu", HouseType.NEUTRAL),
        ("กดุมภะ", "Kadumba", HouseType.AUSPICIOUS),
        ("สหัชชะ", "Sahajja", HouseType.NEUTRAL),
        ("พันธุ", "Bandhu", HouseType.AUSPICIOUS),
        ("ปุตตะ", "Putta", HouseType.AUSPICIOUS),
        ("ปัตนิ", "Patni", HouseType.AUSPICIOUS),
        ("มรณะ", "Marana", HouseType.INAUSPICIUS),
    ],
    # Row 3 (Year Base): 0..6
    [
        ("สุภะ", "Subha", HouseType.AUSPICIOUS),
        ("กัมมะ", "Kamma", HouseType.AUSPICIOUS),
        ("ลาภะ", "Labha", HouseType.AUSPICIOUS),
        ("พยายะ", "Phayaya", HouseType.INAUSPICIUS),
        ("ทาสา", "Thasa", HouseType.NEUTRAL),
        ("ทาสี", "Thasi", HouseType.NEUTRAL),
        ("ภวังค์", "Bhavanga", HouseType.NEUTRAL),
    ],
]

INAUSPICIOUS_HOUSE_NAMES = {"หินะ", "มรณะ", "พยายะ", "อริ"}
TOP_AUSPICIOUS_HOUSE_NAMES = {"ลาภะ", "สุภะ", "กัมมะ", "โภคา", "ธนัง"}
SECONDARY_AUSPICIOUS_HOUSE_NAMES = {"กดุมภะ", "ปุตตะ", "ปัตนิ", "พันธุ"}

# Planetary Strength Lookup Table for Base 9 (กำลังพระเคราะห์)
PLANETARY_STRENGTH = {
    1: 6,   # อาทิตย์
    2: 15,  # จันทร์
    3: 8,   # อังคาร
    4: 17,  # พุธ
    5: 19,  # พฤหัสบดี
    6: 21,  # ศุกร์
    7: 10,  # เสาร์
    8: 12,  # ราหู
    9: 9,   # เกตุ
}

# Friendly Planetary Pairs (คู่มิตร)
FRIENDLY_PAIRS = {
    1: 5, 5: 1,
    2: 4, 4: 2,
    3: 6, 6: 3,
    7: 8, 8: 7,
}


def calculate_numerology_7x9(
    birth_date: str,
    day_of_week: Optional[int] = None,
    thai_lunar_month: Optional[int] = None,
    thai_lunar_year: Optional[int] = None,
    birth_day_override: Optional[int] = None,
    lunar_month_override: Optional[int] = None,
    zodiac_year_override: Optional[int] = None,
) -> Numerology7x9Result:
    """
    Main entry point for 7-Digit 9-Base Numerology Engine calculation.

    Parameters:
        birth_date: str (YYYY-MM-DD)
        day_of_week / birth_day_override: Optional[int] (1..7, 1=Sun..7=Sat)
        thai_lunar_month / lunar_month_override: Optional[int] (1..12)
        thai_lunar_year / zodiac_year_override: Optional[int] (1..12, 1=Rat..12=Pig)

    Returns:
        Numerology7x9Result Pydantic model
    """
    # Parameter alias handling
    effective_day = day_of_week if day_of_week is not None else birth_day_override
    effective_month = thai_lunar_month if thai_lunar_month is not None else lunar_month_override
    effective_year = thai_lunar_year if thai_lunar_year is not None else zodiac_year_override

    # Date parsing & validation
    try:
        dt = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError(f"Invalid birth date format '{birth_date}'. Expected YYYY-MM-DD.")

    # Day of week (1..7)
    if effective_day is not None:
        if not (1 <= effective_day <= 7):
            raise ValueError("day_of_week must be between 1 and 7")
        day_num = effective_day
    else:
        # Python weekday: Mon=0..Sun=6 -> Thai day of week: Sun=1..Sat=7
        day_num = ((dt.weekday() + 1) % 7) + 1

    # Thai lunar month (1..12)
    if effective_month is not None:
        if not (1 <= effective_month <= 12):
            raise ValueError("thai_lunar_month must be between 1 and 12")
        month_num = effective_month
    else:
        month_num = dt.month

    # Thai zodiac year (1..12)
    if effective_year is not None:
        if not (1 <= effective_year <= 12):
            raise ValueError("thai_lunar_year must be between 1 and 12")
        year_num = effective_year
    else:
        year_num = ((dt.year - 4) % 12) + 1

    # 1..7 Scale Normalization for month and year bases
    D = day_num
    M = ((month_num - 1) % 7) + 1
    Y = ((year_num - 1) % 7) + 1

    # Compute Rows 1 to 9 (7 columns each)
    r1 = [((D - 1 + c) % 7) + 1 for c in range(7)]
    r2 = [((M - 1 + c) % 7) + 1 for c in range(7)]
    r3 = [((Y - 1 + c) % 7) + 1 for c in range(7)]

    r4 = [r1[c] + r2[c] + r3[c] for c in range(7)]
    r5 = [r1[c] + r2[c] for c in range(7)]
    r6 = [r1[c] + r3[c] for c in range(7)]
    r7 = [r2[c] + r3[c] for c in range(7)]
    r8 = [r1[c] + r4[c] for c in range(7)]
    r9 = [PLANETARY_STRENGTH.get(r1[c], r1[c]) for c in range(7)]

    matrix_grid = [r1, r2, r3, r4, r5, r6, r7, r8, r9]
    matrix = NumerologyMatrix(
        base1_day=r1,
        base2_month=r2,
        base3_year=r3,
        base4_sum=r4,
        base5=r5,
        base6=r6,
        base7=r7,
        base8=r8,
        base9=r9,
        matrix_grid=matrix_grid,
    )

    # 21 Astrological House Detail mapping & House Names matrix
    house_names: List[List[str]] = []
    houses: Dict[str, HouseDetail7x9] = {}

    for row_idx in range(3):
        row_names: List[str] = []
        for col_idx in range(7):
            name_th, name_en, house_type = HOUSE_MATRIX_TAXONOMY[row_idx][col_idx]
            digit_val = matrix_grid[row_idx][col_idx]
            b4_pow = r4[col_idx]

            detail = HouseDetail7x9(
                house_name_th=name_th,
                house_name_en=name_en,
                row_index=row_idx,
                col_index=col_idx,
                digit_value=digit_val,
                house_type=house_type,
                base4_power=b4_pow,
            )
            houses[name_th] = detail
            row_names.append(name_th)
        house_names.append(row_names)

    # Collision detection for digits 1..7
    collisions: Dict[int, BaseCollisionInfo] = {}
    house_collisions: Dict[int, List[str]] = {}

    for digit in range(1, 8):
        digit_houses: List[str] = []
        digit_b4_powers: List[int] = []
        has_bad = False
        has_good = False
        score = 0.0

        for r_idx in range(3):
            for c_idx in range(7):
                if matrix_grid[r_idx][c_idx] == digit:
                    name_th = house_names[r_idx][c_idx]
                    b4_pow = r4[c_idx]
                    digit_houses.append(name_th)
                    digit_b4_powers.append(b4_pow)

                    if name_th in INAUSPICIOUS_HOUSE_NAMES:
                        has_bad = True
                        score -= 2.5
                    elif name_th in TOP_AUSPICIOUS_HOUSE_NAMES:
                        has_good = True
                        score += 3.0
                    elif name_th in SECONDARY_AUSPICIOUS_HOUSE_NAMES:
                        has_good = True
                        score += 1.5

        if digit_b4_powers:
            avg_b4 = sum(digit_b4_powers) / float(len(digit_b4_powers))
            score += 0.5 * avg_b4

        info = BaseCollisionInfo(
            digit=digit,
            count=len(digit_houses),
            houses=digit_houses,
            has_inauspicious_collision=has_bad,
            has_auspicious_collision=has_good,
            base4_powers=digit_b4_powers,
            collision_score=round(score, 2),
        )
        collisions[digit] = info
        house_collisions[digit] = digit_houses

    auspicious_houses_list = [h for h in TOP_AUSPICIOUS_HOUSE_NAMES | SECONDARY_AUSPICIOUS_HOUSE_NAMES if h in houses]
    inauspicious_houses_list = [h for h in INAUSPICIOUS_HOUSE_NAMES if h in houses]

    # Extract Primary & Secondary Lucky Digits
    # Sort digits by collision score descending
    sorted_digits = sorted(range(1, 8), key=lambda d: collisions[d].collision_score, reverse=True)

    pure_auspicious_digits = [
        d for d in sorted_digits
        if collisions[d].has_auspicious_collision and not collisions[d].has_inauspicious_collision
    ]

    if pure_auspicious_digits:
        primary_lucky_digits = pure_auspicious_digits[:3]
    else:
        non_bad = [d for d in sorted_digits if not collisions[d].has_inauspicious_collision]
        primary_lucky_digits = non_bad[:3] if non_bad else sorted_digits[:3]

    secondary_lucky_digits = [d for d in sorted_digits if d not in primary_lucky_digits][:3]

    # Generate Composite Lucky Numbers (2-digit pairs and primary digits)
    lucky_numbers: List[int] = []
    for pd in primary_lucky_digits:
        if pd not in lucky_numbers:
            lucky_numbers.append(pd)

    # Combine pairs from primary lucky digits
    for i in range(len(primary_lucky_digits)):
        for j in range(len(primary_lucky_digits)):
            if i != j:
                pair = primary_lucky_digits[i] * 10 + primary_lucky_digits[j]
                if pair not in lucky_numbers:
                    lucky_numbers.append(pair)

    # Combine primary with friendly pair
    for pd in primary_lucky_digits:
        friend = FRIENDLY_PAIRS.get(pd)
        if friend:
            pair1 = pd * 10 + friend
            pair2 = friend * 10 + pd
            if pair1 not in lucky_numbers:
                lucky_numbers.append(pair1)
            if pair2 not in lucky_numbers:
                lucky_numbers.append(pair2)

    return Numerology7x9Result(
        birth_date=birth_date,
        day_of_week=day_num,
        day_name_th=DAY_NAMES_TH.get(day_num, ""),
        thai_lunar_month=month_num,
        lunar_month_name_th=LUNAR_MONTH_NAMES_TH.get(month_num, f"เดือน {month_num}"),
        thai_lunar_year=year_num,
        zodiac_year_name_th=ZODIAC_YEAR_NAMES_TH.get(year_num, f"ปี {year_num}"),
        matrix=matrix,
        base_1_row=r1,
        base_2_row=r2,
        base_3_row=r3,
        base_4_row=r4,
        base_5_row=r5,
        base_6_row=r6,
        base_7_row=r7,
        base_8_row=r8,
        base_9_row=r9,
        house_names=house_names,
        houses=houses,
        house_collisions=house_collisions,
        collisions=collisions,
        auspicious_houses=auspicious_houses_list,
        inauspicious_houses=inauspicious_houses_list,
        primary_lucky_digits=primary_lucky_digits,
        secondary_lucky_digits=secondary_lucky_digits,
        lucky_numbers=lucky_numbers,
    )
