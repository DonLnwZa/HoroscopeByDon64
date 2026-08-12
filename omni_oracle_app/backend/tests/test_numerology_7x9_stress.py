"""
Pytest Property-Based Stress & Edge Case Test Suite for 7-Digit 9-Base Numerology Engine
Target Module: app.engines.numerology_7x9
"""

import datetime
import pytest
from app.engines.numerology_7x9 import (
    calculate_numerology_7x9,
    Numerology7x9Result,
    HouseType,
    HouseDetail7x9,
    BaseCollisionInfo,
    PLANETARY_STRENGTH,
)


def _assert_result_invariants(res: Numerology7x9Result):
    """Helper assertion function for verifying core mathematical invariants."""
    # 1. 9x7 Matrix Dimensions
    assert len(res.matrix.matrix_grid) == 9
    for r in range(9):
        assert len(res.matrix.matrix_grid[r]) == 7

    # 2. Rows 1..3 Permutation Invariant
    for r_idx in range(3):
        row_vals = res.matrix.matrix_grid[r_idx]
        assert set(row_vals) == {1, 2, 3, 4, 5, 6, 7}

    # 3. Base 4..9 Math Formulas per Column
    for c in range(7):
        b1 = res.base_1_row[c]
        b2 = res.base_2_row[c]
        b3 = res.base_3_row[c]
        b4 = res.base_4_row[c]
        b5 = res.base_5_row[c]
        b6 = res.base_6_row[c]
        b7 = res.base_7_row[c]
        b8 = res.base_8_row[c]
        b9 = res.base_9_row[c]

        assert b4 == b1 + b2 + b3
        assert b5 == b1 + b2
        assert b6 == b1 + b3
        assert b7 == b2 + b3
        assert b8 == b1 + b4
        assert b9 == PLANETARY_STRENGTH[b1]

    # 4. Digits 1..7 Collision Count Invariant (Exactly 3 per digit)
    for digit in range(1, 8):
        coll = res.collisions[digit]
        assert coll.count == 3
        assert len(coll.houses) == 3
        assert len(coll.base4_powers) == 3

    # 5. House Mapping & Cell Access
    for r in range(1, 4):
        for c in range(1, 8):
            h_name = res.get_house_name(r, c)
            cell_val = res.get_cell(r, c)
            assert cell_val == res.matrix.matrix_grid[r - 1][c - 1]
            h_detail = res.get_house(h_name)
            assert h_detail is not None
            assert h_detail.digit_value == cell_val
            assert h_detail.row_index == r - 1
            assert h_detail.col_index == c - 1
            assert h_detail.base4_power == res.base_4_row[c - 1]

    # 6. Lucky Digits & Numbers Bounds
    assert len(res.primary_lucky_digits) > 0
    for d in res.primary_lucky_digits:
        assert 1 <= d <= 7
    for d in res.secondary_lucky_digits:
        assert 1 <= d <= 7
    for num in res.lucky_numbers:
        assert 0 <= num <= 99


@pytest.mark.parametrize("d", list(range(1, 8)))
@pytest.mark.parametrize("m", list(range(1, 8)))
@pytest.mark.parametrize("y", list(range(1, 8)))
def test_all_343_matrix_override_combinations(d: int, m: int, y: int):
    """Test all 7x7x7 = 343 base override combinations for day(1..7) x month(1..7) x year(1..7)."""
    res = calculate_numerology_7x9(
        "2026-01-01",
        day_of_week=d,
        thai_lunar_month=m,
        thai_lunar_year=y,
    )
    _assert_result_invariants(res)


@pytest.mark.parametrize("d", list(range(1, 8)))
@pytest.mark.parametrize("m", list(range(1, 13)))
@pytest.mark.parametrize("y", list(range(1, 13)))
def test_all_1008_lunar_month_year_combinations(d: int, m: int, y: int):
    """Test all 7x12x12 = 1008 lunar override combinations for day(1..7) x month(1..12) x year(1..12)."""
    res = calculate_numerology_7x9(
        "2026-01-01",
        day_of_week=d,
        thai_lunar_month=m,
        thai_lunar_year=y,
    )
    _assert_result_invariants(res)


@pytest.mark.parametrize("d_str", [
    "0001-01-01",
    "1500-02-28",
    "1900-02-28",  # 1900 non-leap
    "2000-02-29",  # 2000 century leap year
    "2004-02-29",  # 2004 leap year
    "2020-02-29",  # 2020 leap year
    "2024-02-29",  # 2024 leap year
    "2026-08-06",  # Present date
    "2099-12-31",
    "9999-12-31",
])
def test_leap_years_and_historical_dates(d_str: str):
    """Verify leap year calculations and historical date boundaries."""
    res = calculate_numerology_7x9(d_str)
    dt = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
    expected_dow = ((dt.weekday() + 1) % 7) + 1
    assert res.day_of_week == expected_dow
    _assert_result_invariants(res)


def test_parameter_alias_strict_equivalence():
    """Verify primary and alias parameter names yield identical Pydantic models."""
    res1 = calculate_numerology_7x9(
        "2020-05-15",
        day_of_week=3,
        thai_lunar_month=8,
        thai_lunar_year=12,
    )
    res2 = calculate_numerology_7x9(
        "2020-05-15",
        birth_day_override=3,
        lunar_month_override=8,
        zodiac_year_override=12,
    )
    assert res1.model_dump() == res2.model_dump()


def test_cell_and_house_getter_boundary_errors():
    """Verify get_cell and get_house_name raise ValueError for invalid indices."""
    res = calculate_numerology_7x9("2026-01-01")

    # Invalid get_cell rows/cols
    with pytest.raises(ValueError, match="Row must be between 1..9"):
        res.get_cell(0, 1)
    with pytest.raises(ValueError, match="Row must be between 1..9"):
        res.get_cell(10, 1)
    with pytest.raises(ValueError, match="Col must be between 1..7"):
        res.get_cell(1, 0)
    with pytest.raises(ValueError, match="Col must be between 1..7"):
        res.get_cell(1, 8)

    # Invalid get_house_name rows/cols
    with pytest.raises(ValueError, match="Row must be between 1..3"):
        res.get_house_name(0, 1)
    with pytest.raises(ValueError, match="Row must be between 1..3"):
        res.get_house_name(4, 1)
    with pytest.raises(ValueError, match="Col must be between 1..7"):
        res.get_house_name(1, 0)
    with pytest.raises(ValueError, match="Col must be between 1..7"):
        res.get_house_name(1, 8)
