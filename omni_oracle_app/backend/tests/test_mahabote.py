"""
Pytest Test Suite for Burmese Mahabote Divination Engine (มหาภูติพม่า)
Module: backend.tests.test_mahabote
Target Module: app.engines.mahabote
"""

from datetime import date, datetime, time
import pytest
from pydantic import ValidationError

from app.engines.mahabote import (
    DayOfWeek,
    KalayokCategory,
    KalayokInfo,
    LuckyDigitsResult,
    MahaboteChart,
    MahaboteEngine,
    MahabotePositionEnum,
    MahaboteResult,
    PositionDetail,
    TaksaCategory,
    TaksaInfo,
    TaksaPlanetDetail,
    calculate_mahabote,
)


def test_data_models_and_enums():
    """Verify all Enums and Pydantic Data Models validate attributes correctly."""
    assert DayOfWeek.SUNDAY == 1
    assert DayOfWeek.MONDAY == 2
    assert DayOfWeek.WEDNESDAY_DAY == 4
    assert DayOfWeek.WEDNESDAY_NIGHT == 8

    assert MahabotePositionEnum.ATTA == "atta"
    assert MahabotePositionEnum.THANANG == "thanang"
    assert MahabotePositionEnum.HINA == "hina"

    assert TaksaCategory.SRI == "ศรี"
    assert TaksaCategory.KALAKINI == "กาลกิณี"

    assert KalayokCategory.THONGCHAI == "ธงชัย"
    assert KalayokCategory.LOKAVINAS == "โลกาวินาศ"

    # Test PositionDetail
    pos = PositionDetail(
        position_key="thanang",
        position_name_th="ธนัง",
        position_name_en="Thanang",
        planet_digit=4,
        planet_name_th="พุธ",
        taksa_category="ศรี",
        is_kalayok_auspicious=True,
        is_kalayok_inauspicious=False,
    )
    assert pos.planet_digit == 4
    assert pos.position_key == "thanang"
    assert pos.is_kalayok_auspicious is True

    # Test Validation Bounds
    with pytest.raises(ValidationError):
        PositionDetail(
            position_key="invalid",
            position_name_th="ผิด",
            position_name_en="Bad",
            planet_digit=9,  # Out of range 1..7
            planet_name_th="ผิด",
            taksa_category="ศรี",
            is_kalayok_auspicious=False,
            is_kalayok_inauspicious=False,
        )


def test_calculate_mahabote_valid_input():
    """Verify calculate_mahabote returns a valid MahaboteResult structure."""
    result = calculate_mahabote("1995-08-15")
    assert isinstance(result, MahaboteResult)
    assert result.birth_date == "1995-08-15"
    assert result.cs_year == 1357
    assert result.cs_remainder == 6
    assert result.day_of_week == 3  # Aug 15, 1995 was Tuesday (3)
    assert result.day_name_th == "อังคาร"
    assert isinstance(result.chart, MahaboteChart)
    assert isinstance(result.taksa, TaksaInfo)
    assert isinstance(result.kalayok, KalayokInfo)
    assert isinstance(result.lucky_digits, LuckyDigitsResult)
    assert len(result.lucky_digits.primary_digits) > 0
    assert len(result.lucky_digits.recommended_2digit_pairs) > 0


@pytest.mark.parametrize(
    "input_date, expected_cs, expected_adjusted",
    [
        ("1990-01-01", 1351, True),
        ("1990-04-15", 1351, True),
        ("1990-04-16", 1352, False),
        ("1990-12-31", 1352, False),
        ("2024-04-15", 1385, True),
        ("2024-04-16", 1386, False),
        ("2000-04-15", 1361, True),
        ("2000-04-16", 1362, False),
    ],
)
def test_songkran_boundary_cutoff(input_date, expected_cs, expected_adjusted):
    """Verify April 15 vs April 16 Songkran cutoff adjusts CS year correctly."""
    result = calculate_mahabote(input_date)
    assert result.cs_year == expected_cs
    assert result.songkran_adjusted == expected_adjusted


def test_cs_remainder_zero_mapping():
    """Verify CS remainder equal to 0 is mapped to 7."""
    # CS 1386 % 7 == 0 -> should map cs_remainder to 7
    result = calculate_mahabote("2024-04-16")
    assert result.cs_year == 1386
    assert result.cs_year % 7 == 0
    assert result.cs_remainder == 7


@pytest.mark.parametrize(
    "birth_time, is_night_flag, expected_day_digit",
    [
        ("10:00", None, 4),
        ("17:59", None, 4),
        ("18:00", None, 8),
        ("22:30", None, 8),
        ("02:00", None, 8),
        (None, True, 8),
        (None, False, 4),
    ],
)
def test_wednesday_day_night_distinction(birth_time, is_night_flag, expected_day_digit):
    """Verify Wednesday birth time or flag assigns day digit 4 vs 8."""
    # 2024-05-15 is Wednesday
    result = calculate_mahabote(
        birth_date="2024-05-15",
        birth_time=birth_time,
        is_wednesday_night=is_night_flag,
    )
    assert result.day_of_week == expected_day_digit
    if expected_day_digit == 8:
        assert result.is_wednesday_night is True
        assert "พุธกลางคืน" in result.day_name_th
    else:
        assert result.is_wednesday_night is False


def test_mahabote_7_positions_matrix_assignment():
    """Verify placement of planet digits in 7 body positions starting from remainder."""
    # Date with CS remainder = 4, Day of week = 2 (Monday)
    result = calculate_mahabote("1994-05-10")
    cs_rem = result.cs_remainder
    # Thanang position should hold digit cs_rem
    thanang_pos = result.chart.positions["thanang"]
    assert thanang_pos.planet_digit == cs_rem

    # Verify positions follow sequential rotation
    pos_order = ["thanang", "pita", "mata", "phoka", "matchima", "atta", "hina"]
    digits = [result.chart.positions[p].planet_digit for p in pos_order]
    for i in range(7):
        expected_digit = ((cs_rem - 1 + i) % 7) + 1
        assert digits[i] == expected_digit


def test_taksa_mapping_rules():
    """Verify Taksa planet categories based on day of week."""
    # Sunday (1) birth -> Sri is 4 (Wed), Kalakini is 6 (Fri)
    result_sun = calculate_mahabote("2024-05-12")  # Sunday
    assert result_sun.taksa.brivar_planet == 1
    assert result_sun.taksa.sri_planet == 4
    assert result_sun.taksa.kalakini_planet == 6

    # Monday (2) birth -> Sri is 7 (Sat), Kalakini is 1 (Sun)
    result_mon = calculate_mahabote("2024-05-13")  # Monday
    assert result_mon.taksa.brivar_planet == 2
    assert result_mon.taksa.sri_planet == 7
    assert result_mon.taksa.kalakini_planet == 1


def test_kalayok_annual_mapping():
    """Verify Kalayok calculation for a known CS year."""
    # CS 1388 (2026 post-Songkran) % 7 = 2
    # For remainder 2: Thongchai=3, Athipati=2, Upabat=7, Lokawinat=1
    result = calculate_mahabote("2026-05-01")
    assert result.cs_year == 1388
    assert result.kalayok.thongchai_digit == 3
    assert result.kalayok.atipati_digit == 2
    assert result.kalayok.yamabat_digit == 7
    assert result.kalayok.lokavinas_digit == 1


def test_lucky_digits_extraction():
    """Verify primary, secondary, avoid digits and 2-digit pairs generation."""
    result = calculate_mahabote("1995-08-15")
    ld = result.lucky_digits

    # Avoid digits should include Kalakini planet
    kalakini = result.taksa.kalakini_planet
    assert kalakini in ld.avoid_digits

    # Primary digits should come from auspicious houses and positive taksa
    assert len(ld.primary_digits) >= 1
    assert all(d in range(0, 10) for d in ld.primary_digits)

    # 2-digit lottery pairs should be formatted as two-digit strings
    assert len(ld.recommended_2digit_pairs) >= 3
    for pair in ld.recommended_2digit_pairs:
        assert len(pair) == 2
        assert pair.isdigit()
        # Pair digits shouldn't be made solely of avoid digits
        d1, d2 = int(pair[0]), int(pair[1])
        assert not (d1 in ld.avoid_digits and d2 in ld.avoid_digits)


@pytest.mark.parametrize(
    "invalid_date",
    [
        "invalid-date",
        "15-08-1995",
        "2023-02-29",
        "2024-04-31",
        "",
        None,
    ],
)
def test_invalid_inputs_raise_errors(invalid_date):
    """Verify malformed date strings or invalid inputs raise ValueError or TypeError."""
    with pytest.raises((ValueError, TypeError)):
        calculate_mahabote(invalid_date)


def test_date_and_datetime_input_types():
    """Verify calculate_mahabote accepts date and datetime objects."""
    d_obj = date(1995, 8, 15)
    dt_obj = datetime(1995, 8, 15, 14, 30, 0)

    res_d = calculate_mahabote(d_obj)
    res_dt = calculate_mahabote(dt_obj)

    assert res_d.cs_year == res_dt.cs_year == 1357
    assert res_d.birth_date == res_dt.birth_date == "1995-08-15"


def test_mahabote_engine_classmethods():
    """Verify individual classmethods of MahaboteEngine function independently."""
    cs_year, adjusted = MahaboteEngine.calculate_cs(date(2024, 4, 15))
    assert cs_year == 1385
    assert adjusted is True

    rem = MahaboteEngine.calculate_cs_remainder(1386)
    assert rem == 7

    day = MahaboteEngine.determine_day_of_week(date(2024, 5, 15), time(19, 0))
    assert day == DayOfWeek.WEDNESDAY_NIGHT
