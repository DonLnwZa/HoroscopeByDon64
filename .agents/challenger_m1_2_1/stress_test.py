"""
Empirical Stress Test & Property-Based Verification Harness for 7-Digit 9-Base Numerology Engine
Module: app.engines.numerology_7x9
"""

import sys
import os
import datetime
from typing import List, Dict, Tuple

# Add backend directory to sys.path
backend_dir = r"e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.engines.numerology_7x9 import (
    calculate_numerology_7x9,
    Numerology7x9Result,
    HouseType,
    HouseDetail7x9,
    BaseCollisionInfo,
    PLANETARY_STRENGTH,
    DAY_NAMES_TH,
    LUNAR_MONTH_NAMES_TH,
    ZODIAC_YEAR_NAMES_TH,
)


def verify_result_invariants(res: Numerology7x9Result, d_in: int, m_in: int, y_in: int):
    """Rigorous property-based invariant check on a single Numerology7x9Result."""
    # 1. Matrix shape check
    assert len(res.matrix.matrix_grid) == 9, "Matrix must have 9 rows"
    for r in range(9):
        assert len(res.matrix.matrix_grid[r]) == 7, f"Row {r+1} must have 7 columns"

    # 2. Base 1..3 properties
    # Each row 1..3 must be a permutation of 1..7
    for r_idx, r_name in [(0, "base_1_row"), (1, "base_2_row"), (2, "base_3_row")]:
        row_vals = res.matrix.matrix_grid[r_idx]
        assert set(row_vals) == {1, 2, 3, 4, 5, 6, 7}, f"{r_name} must contain all digits 1..7"
        assert len(row_vals) == 7

    # 3. Base 4..9 Math formulas check per column
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

        assert b4 == b1 + b2 + b3, f"Col {c}: Base 4 ({b4}) != B1+B2+B3 ({b1}+{b2}+{b3})"
        assert b5 == b1 + b2, f"Col {c}: Base 5 ({b5}) != B1+B2"
        assert b6 == b1 + b3, f"Col {c}: Base 6 ({b6}) != B1+B3"
        assert b7 == b2 + b3, f"Col {c}: Base 7 ({b7}) != B2+B3"
        assert b8 == b1 + b4, f"Col {c}: Base 8 ({b8}) != B1+B4"
        expected_b9 = PLANETARY_STRENGTH[b1]
        assert b9 == expected_b9, f"Col {c}: Base 9 ({b9}) != Planetary Strength for {b1} ({expected_b9})"

    # 4. Digits 1..7 Collision count invariant
    for digit in range(1, 8):
        coll = res.collisions[digit]
        assert coll.count == 3, f"Digit {digit} count must be exactly 3 in 3x7 grid, got {coll.count}"
        assert len(coll.houses) == 3, f"Digit {digit} houses list length must be 3"
        assert len(coll.base4_powers) == 3, f"Digit {digit} base4_powers length must be 3"

    # 5. House mapping & cell access check
    for r in range(1, 4):
        for c in range(1, 8):
            h_name = res.get_house_name(r, c)
            cell_val = res.get_cell(r, c)
            assert cell_val == res.matrix.matrix_grid[r - 1][c - 1]
            h_detail = res.get_house(h_name)
            assert h_detail is not None, f"House '{h_name}' missing from houses dictionary"
            assert h_detail.digit_value == cell_val
            assert h_detail.row_index == r - 1
            assert h_detail.col_index == c - 1
            assert h_detail.base4_power == res.base_4_row[c - 1]

    # 6. Lucky digits & numbers checks
    assert len(res.primary_lucky_digits) > 0, "Primary lucky digits must not be empty"
    for d in res.primary_lucky_digits:
        assert 1 <= d <= 7, f"Primary lucky digit {d} out of range 1..7"
    for d in res.secondary_lucky_digits:
        assert 1 <= d <= 7, f"Secondary lucky digit {d} out of range 1..7"
    for num in res.lucky_numbers:
        assert 0 <= num <= 99, f"Lucky number {num} out of 0..99 range"

    # 7. Helper properties check
    assert res.primary_lucky_digit == res.primary_lucky_digits[0]
    assert res.secondary_lucky_digit == res.secondary_lucky_digits[0]
    assert res.lunar_month == res.thai_lunar_month
    assert res.zodiac_year == res.thai_lunar_year


def test_matrix_combination_grid():
    """Test all 7x7x7 = 343 base override combinations for day(1..7) x month(1..7) x year(1..7)."""
    print("--- Running Matrix Combination Grid (343 combinations) ---")
    count = 0
    for d in range(1, 8):
        for m in range(1, 8):
            for y in range(1, 8):
                res = calculate_numerology_7x9(
                    "2026-01-01",
                    day_of_week=d,
                    thai_lunar_month=m,
                    thai_lunar_year=y,
                )
                verify_result_invariants(res, d, m, y)
                count += 1
    print(f"PASS: Verified all {count} 7x7x7 matrix combinations.")


def test_full_lunar_month_year_grid():
    """Test all 7x12x12 = 1008 combinations for day(1..7) x month(1..12) x year(1..12)."""
    print("--- Running Full Lunar Grid (1008 combinations) ---")
    count = 0
    for d in range(1, 8):
        for m in range(1, 13):
            for y in range(1, 13):
                res = calculate_numerology_7x9(
                    "2026-01-01",
                    day_of_week=d,
                    thai_lunar_month=m,
                    thai_lunar_year=y,
                )
                verify_result_invariants(res, d, m, y)
                count += 1
    print(f"PASS: Verified all {count} 7x12x12 lunar combinations.")


def test_parameter_alias_equivalence():
    """Verify primary and alias parameter names produce bit-for-bit identical results."""
    print("--- Running Parameter Alias Equivalence Tests ---")
    for d in range(1, 8):
        for m in (1, 6, 12):
            for y in (1, 6, 12):
                res1 = calculate_numerology_7x9(
                    "2020-05-15",
                    day_of_week=d,
                    thai_lunar_month=m,
                    thai_lunar_year=y,
                )
                res2 = calculate_numerology_7x9(
                    "2020-05-15",
                    birth_day_override=d,
                    lunar_month_override=m,
                    zodiac_year_override=y,
                )
                assert res1.model_dump() == res2.model_dump(), "Primary and alias parameter results differ!"
    print("PASS: Parameter alias equivalence verified.")


def test_leap_years_and_historical_dates():
    """Test leap years and historical date boundaries."""
    print("--- Running Leap Years and Historical Dates Tests ---")
    dates = [
        "0001-01-01",  # Minimum Python date
        "1500-02-28",
        "1900-02-28",  # 1900 was not a leap year
        "2000-02-29",  # 2000 was a century leap year
        "2004-02-29",  # 2004 regular leap year
        "2020-02-29",  # 2020 leap year
        "2024-02-29",  # 2024 leap year
        "2026-08-06",  # Today
        "2099-12-31",
        "9999-12-31",  # Maximum Python date
    ]
    for d_str in dates:
        res = calculate_numerology_7x9(d_str)
        dt = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
        # Verify day of week matches dt.weekday()
        expected_dow = ((dt.weekday() + 1) % 7) + 1
        assert res.day_of_week == expected_dow, f"Date {d_str}: day_of_week {res.day_of_week} != expected {expected_dow}"
        verify_result_invariants(res, expected_dow, dt.month, ((dt.year - 4) % 12) + 1)
    print(f"PASS: Verified {len(dates)} historical dates & leap years.")


def test_edge_cases_and_exceptions():
    """Verify robust error handling for invalid input formats and bounds."""
    print("--- Running Edge Cases & Exception Tests ---")
    invalid_dates = [
        "",
        "2024-02-30",  # Invalid Feb day
        "1900-02-29",  # 1900 is not a leap year
        "2026/08/06",  # Wrong separator
        "06-08-2026",  # DD-MM-YYYY format
        "invalid",
        "2026-13-01",  # Invalid month
        "2026-00-01",
    ]
    for d_str in invalid_dates:
        try:
            calculate_numerology_7x9(d_str)
            assert False, f"Expected ValueError for date '{d_str}' but calculation succeeded!"
        except ValueError as e:
            assert "Invalid birth date" in str(e)

    out_of_bounds_params = [
        {"day_of_week": 0},
        {"day_of_week": 8},
        {"day_of_week": -1},
        {"thai_lunar_month": 0},
        {"thai_lunar_month": 13},
        {"thai_lunar_year": 0},
        {"thai_lunar_year": 13},
    ]
    for p in out_of_bounds_params:
        try:
            calculate_numerology_7x9("2026-01-01", **p)
            assert False, f"Expected ValueError for param {p} but calculation succeeded!"
        except ValueError as e:
            assert any(k in str(e) for k in ("day_of_week", "thai_lunar_month", "thai_lunar_year"))

    print("PASS: Edge cases and exception handling verified.")


def main():
    print("==================================================")
    print("  7-Digit 9-Base Engine Empirical Stress Suite    ")
    print("==================================================")
    test_matrix_combination_grid()
    test_full_lunar_month_year_grid()
    test_parameter_alias_equivalence()
    test_leap_years_and_historical_dates()
    test_edge_cases_and_exceptions()
    print("==================================================")
    print("  ALL EMPIRICAL STRESS TESTS PASSED SUCCESSFULLY! ")
    print("==================================================")


if __name__ == "__main__":
    main()
