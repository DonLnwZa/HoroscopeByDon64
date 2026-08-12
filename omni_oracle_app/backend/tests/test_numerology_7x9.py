"""
Pytest Unit Test Suite for 7-Digit 9-Base Numerology Engine (M1.2)
Target Module: app.engines.numerology_7x9
Strict TDD: RED -> GREEN -> REFACTOR
"""

import pytest
from app.engines.numerology_7x9 import (
    calculate_numerology_7x9,
    HouseType,
    HouseDetail7x9,
    BaseCollisionInfo,
    NumerologyMatrix,
    Numerology7x9Result,
)


def test_data_models_and_enums():
    """Verify Enums and Data Models are defined correctly with Pydantic validations."""
    assert HouseType.AUSPICIOUS == "auspicious"
    assert HouseType.INAUSPICIUS == "inauspicious"
    assert HouseType.NEUTRAL == "neutral"

    house = HouseDetail7x9(
        house_name_th="ลาภะ",
        house_name_en="Labha",
        row_index=2,
        col_index=2,
        digit_value=3,
        house_type=HouseType.AUSPICIOUS,
        base4_power=15,
    )
    assert house.is_auspicious is True
    assert house.is_inauspicious is False

    collision = BaseCollisionInfo(
        digit=7,
        count=3,
        houses=["กัมมะ", "มาตา", "ปัตนิ"],
        has_inauspicious_collision=False,
        has_auspicious_collision=True,
        base4_powers=[14, 14, 10],
        collision_score=8.5,
    )
    assert collision.digit == 7
    assert collision.has_inauspicious_collision is False
    assert collision.has_auspicious_collision is True


def test_calculate_numerology_7x9_valid_input():
    """Test standard calculation with a valid birth date."""
    res = calculate_numerology_7x9("1995-08-15")
    assert isinstance(res, Numerology7x9Result)
    assert res.birth_date == "1995-08-15"
    assert 1 <= res.day_of_week <= 7
    assert 1 <= res.thai_lunar_month <= 12
    assert 1 <= res.thai_lunar_year <= 12

    # Check 9x7 Matrix dimensions
    assert len(res.matrix.matrix_grid) == 9
    for row in res.matrix.matrix_grid:
        assert len(row) == 7

    # Check convenience row attributes
    assert len(res.base_1_row) == 7
    assert len(res.base_2_row) == 7
    assert len(res.base_3_row) == 7
    assert len(res.base_4_row) == 7
    assert len(res.base_5_row) == 7
    assert len(res.base_6_row) == 7
    assert len(res.base_7_row) == 7
    assert len(res.base_8_row) == 7
    assert len(res.base_9_row) == 7


def test_matrix_generation_rules_and_formulas():
    """
    Verify 7x9 Matrix generation math formulas:
    - Base 1..3: Elements in range 1..7 wrapping sequentially
    - Base 4: Sum of Base 1 + Base 2 + Base 3 per column (values 3..21)
    - Base 5: Base 1 + Base 2
    - Base 6: Base 1 + Base 3
    - Base 7: Base 2 + Base 3
    - Base 8: Base 1 + Base 4
    - Base 9: Planetary Strength lookup (1=6, 2=15, 3=8, 4=17, 5=19, 6=21, 7=10, 8=12, 9=9)
    """
    # Force Sunday (1), Month 1, Year 1 override for deterministic checking
    res = calculate_numerology_7x9(
        "2000-01-01",
        day_of_week=1,
        thai_lunar_month=1,
        thai_lunar_year=1,
    )

    # Base 1, 2, 3 should all be [1, 2, 3, 4, 5, 6, 7]
    expected_base123 = [1, 2, 3, 4, 5, 6, 7]
    assert res.base_1_row == expected_base123
    assert res.base_2_row == expected_base123
    assert res.base_3_row == expected_base123

    # Base 4 = Base 1 + Base 2 + Base 3 = [3, 6, 9, 12, 15, 18, 21]
    expected_base4 = [3, 6, 9, 12, 15, 18, 21]
    assert res.base_4_row == expected_base4

    # Base 5 = Base 1 + Base 2 = [2, 4, 6, 8, 10, 12, 14]
    expected_base5 = [2, 4, 6, 8, 10, 12, 14]
    assert res.base_5_row == expected_base5

    # Base 6 = Base 1 + Base 3 = [2, 4, 6, 8, 10, 12, 14]
    assert res.base_6_row == expected_base5

    # Base 7 = Base 2 + Base 3 = [2, 4, 6, 8, 10, 12, 14]
    assert res.base_7_row == expected_base5

    # Base 8 = Base 1 + Base 4 = [4, 8, 12, 16, 20, 24, 28]
    expected_base8 = [4, 8, 12, 16, 20, 24, 28]
    assert res.base_8_row == expected_base8

    # Base 9 = Planetary Strength lookup of Base 1 column digits (1=6, 2=15, 3=8, 4=17, 5=19, 6=21, 7=10)
    expected_base9 = [6, 15, 8, 17, 19, 21, 10]
    assert res.base_9_row == expected_base9


def test_21_houses_mapping():
    """
    Verify 21 Astrological Houses mapping across Rows 1-3:
    Row 1: อัตตะ, หินะ, ธนัง, ปิตา, มาตา, โภคา, มัชฌิมา
    Row 2: ตะนุ, กดุมภะ, สหัชชะ, พันธุ, ปุตตะ, ปัตนิ, มรณะ
    Row 3: สุภะ, กัมมะ, ลาภะ, พยายะ, ทาสา, ทาสี, ภวังค์
    """
    res = calculate_numerology_7x9("1995-08-15")

    expected_row1 = ["อัตตะ", "หินะ", "ธนัง", "ปิตา", "มาตา", "โภคา", "มัชฌิมา"]
    expected_row2 = ["ตะนุ", "กดุมภะ", "สหัชชะ", "พันธุ", "ปุตตะ", "ปัตนิ", "มรณะ"]
    expected_row3 = ["สุภะ", "กัมมะ", "ลาภะ", "พยายะ", "ทาสา", "ทาสี", "ภวังค์"]

    assert res.house_names[0] == expected_row1
    assert res.house_names[1] == expected_row2
    assert res.house_names[2] == expected_row3

    # Check cell access methods
    assert res.get_house_name(1, 1) == "อัตตะ"
    assert res.get_house_name(1, 3) == "ธนัง"
    assert res.get_house_name(2, 2) == "กดุมภะ"
    assert res.get_house_name(3, 3) == "ลาภะ"


def test_house_collisions_and_dignities():
    """
    Verify House Collisions for digits 1..7:
    - Each digit 1..7 appears 3 times in Rows 1-3.
    - Check auspicious and inauspicious house classifications.
    - Check inauspicious houses include: หินะ, มรณะ, พยายะ
    - Check auspicious houses include: สุภะ, กัมมะ, ลาภะ, โภคา, ธนัง, กดุมภะ
    """
    res = calculate_numerology_7x9("1995-08-15")

    assert "หินะ" in res.inauspicious_houses
    assert "มรณะ" in res.inauspicious_houses
    assert "พยายะ" in res.inauspicious_houses

    assert "สุภะ" in res.auspicious_houses
    assert "ลาภะ" in res.auspicious_houses
    assert "ธนัง" in res.auspicious_houses

    # Every digit 1..7 must have collision info populated
    for digit in range(1, 8):
        collision = res.get_digit_collision(digit)
        assert collision is not None
        assert collision.digit == digit
        assert collision.count == 3
        assert len(collision.houses) == 3


def test_lucky_digits_extraction():
    """
    Verify Lucky Digits extraction:
    - primary_lucky_digits: non-empty list of single digits (1..7)
    - secondary_lucky_digits: list of single digits (1..7)
    - lucky_numbers: list of numbers for lottery recommendation (single or 2-digit)
    - primary_lucky_digit / secondary_lucky_digit properties
    """
    res = calculate_numerology_7x9("1995-08-15")

    assert isinstance(res.primary_lucky_digits, list)
    assert len(res.primary_lucky_digits) > 0
    for d in res.primary_lucky_digits:
        assert 1 <= d <= 7

    assert isinstance(res.secondary_lucky_digits, list)
    for d in res.secondary_lucky_digits:
        assert 1 <= d <= 7

    assert isinstance(res.lucky_numbers, list)
    assert len(res.lucky_numbers) >= 3
    for num in res.lucky_numbers:
        assert 0 <= num <= 99

    assert 1 <= res.primary_lucky_digit <= 7
    assert 1 <= res.secondary_lucky_digit <= 7


def test_explicit_overrides_and_alias_parameters():
    """Test parameter overrides both with primary names and alias names."""
    res_primary = calculate_numerology_7x9(
        "1995-08-15",
        day_of_week=3,
        thai_lunar_month=8,
        thai_lunar_year=12,
    )
    assert res_primary.day_of_week == 3
    assert res_primary.thai_lunar_month == 8
    assert res_primary.thai_lunar_year == 12

    res_alias = calculate_numerology_7x9(
        "1995-08-15",
        birth_day_override=3,
        lunar_month_override=8,
        zodiac_year_override=12,
    )
    assert res_alias.day_of_week == 3
    assert res_alias.thai_lunar_month == 8
    assert res_alias.thai_lunar_year == 12


def test_edge_cases_and_error_handling():
    """Verify invalid birth dates and out-of-bounds parameters raise ValueError."""
    # Invalid birth date format
    with pytest.raises(ValueError, match="Invalid birth date"):
        calculate_numerology_7x9("15-08-1995")

    with pytest.raises(ValueError, match="Invalid birth date"):
        calculate_numerology_7x9("invalid-date")

    # Out-of-bounds day_of_week
    with pytest.raises(ValueError, match="day_of_week"):
        calculate_numerology_7x9("1995-08-15", day_of_week=0)

    with pytest.raises(ValueError, match="day_of_week"):
        calculate_numerology_7x9("1995-08-15", day_of_week=8)

    # Out-of-bounds thai_lunar_month
    with pytest.raises(ValueError, match="thai_lunar_month"):
        calculate_numerology_7x9("1995-08-15", thai_lunar_month=13)

    # Out-of-bounds thai_lunar_year
    with pytest.raises(ValueError, match="thai_lunar_year"):
        calculate_numerology_7x9("1995-08-15", thai_lunar_year=0)
