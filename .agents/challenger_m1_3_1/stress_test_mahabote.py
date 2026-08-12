"""
Empirical Stress Test Suite for Burmese Mahabote Engine (M1.3)
Location: .agents/challenger_m1_3_1/stress_test_mahabote.py
Target Module: omni_oracle_app.backend.app.engines.mahabote
"""

import sys
from pathlib import Path
from datetime import date, datetime, time, timedelta

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parents[2] / "omni_oracle_app" / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.engines.mahabote import (
    MahaboteEngine,
    calculate_mahabote,
    DayOfWeek,
    MahaboteResult,
    MahaboteChart,
    TaksaInfo,
    KalayokInfo,
    LuckyDigitsResult,
)


def run_all_stress_tests():
    print("=========================================================")
    print("STARTING EMPIRICAL STRESS TESTS FOR BURMESE MAHABOTE ENGINE")
    print("=========================================================")

    test_songkran_cutoff_boundaries()
    test_cs_remainder_100_year_cycle_continuity()
    test_wednesday_day_night_handling_all_cases()
    test_chart_matrix_permutation_properties()
    test_lucky_digits_and_avoid_digits_invariants()
    test_invalid_inputs_and_type_robustness()

    print("=========================================================")
    print("ALL EMPIRICAL STRESS TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("=========================================================")


def test_songkran_cutoff_boundaries():
    print("\n[STRESS TEST 1] Songkran Cutoff Boundaries & Leap Years...")

    # Test cases: (birth_date_str, expected_cs_year, expected_adjusted)
    cases = [
        # Normal Year 1995
        ("1995-04-15", 1356, True),
        ("1995-04-16", 1357, False),
        # Leap Year 2000 (divisible by 400)
        ("2000-02-29", 1361, True),
        ("2000-04-15", 1361, True),
        ("2000-04-16", 1362, False),
        # Leap Year 2024
        ("2024-02-29", 1385, True),
        ("2024-04-15", 1385, True),
        ("2024-04-16", 1386, False),
        # Non-Leap Century Year 1900 (divisible by 100, not 400)
        ("1900-02-28", 1261, True),
        ("1900-04-15", 1261, True),
        ("1900-04-16", 1262, False),
        # Non-Leap Century Year 2100
        ("2100-04-15", 1461, True),
        ("2100-04-16", 1462, False),
    ]

    for d_str, exp_cs, exp_adj in cases:
        res = calculate_mahabote(d_str)
        assert res.cs_year == exp_cs, f"Failed CS year for {d_str}: expected {exp_cs}, got {res.cs_year}"
        assert res.songkran_adjusted == exp_adj, f"Failed adjusted flag for {d_str}: expected {exp_adj}, got {res.songkran_adjusted}"

    # Test datetime boundary: April 15 23:59:59 vs April 16 00:00:00
    dt_before = datetime(2024, 4, 15, 23, 59, 59)
    dt_after = datetime(2024, 4, 16, 0, 0, 0)

    res_before = calculate_mahabote(dt_before)
    res_after = calculate_mahabote(dt_after)

    assert res_before.cs_year == 1385
    assert res_before.songkran_adjusted is True
    assert res_after.cs_year == 1386
    assert res_after.songkran_adjusted is False

    print("  -> Passed Songkran Cutoff & Leap Year boundary checks!")


def test_cs_remainder_100_year_cycle_continuity():
    print("\n[STRESS TEST 2] CS Remainder Mod 7 Cycle Continuity (1920-2030)...")

    start_date = date(1920, 1, 1)
    end_date = date(2030, 12, 31)

    curr = start_date
    prev_cs = None
    prev_rem = None

    total_days = 0

    while curr <= end_date:
        res = calculate_mahabote(curr)
        total_days += 1

        # Check invariants
        assert 1 <= res.cs_remainder <= 7, f"Invalid cs_remainder {res.cs_remainder} on {curr}"
        assert res.cs_remainder == (res.cs_year % 7 if res.cs_year % 7 != 0 else 7)

        if prev_cs is not None:
            if curr.month == 4 and curr.day == 16:
                # Songkran transition: CS year MUST increase by exactly 1
                assert res.cs_year == prev_cs + 1, f"CS year non-monotonic on {curr}: prev={prev_cs}, curr={res.cs_year}"
                # Remainder MUST transition cyclically (1->2->3->4->5->6->7->1)
                expected_rem = (prev_rem % 7) + 1
                assert res.cs_remainder == expected_rem, f"CS remainder cycle broken on {curr}: prev={prev_rem}, expected={expected_rem}, got={res.cs_remainder}"
            else:
                # On non-Songkran transition days, CS year and remainder MUST remain identical to previous day
                if curr.month != 4 or curr.day != 16:
                    assert res.cs_year == prev_cs, f"CS year changed unexpectedly on {curr}: prev={prev_cs}, curr={res.cs_year}"
                    assert res.cs_remainder == prev_rem, f"CS remainder changed unexpectedly on {curr}: prev={prev_rem}, curr={res.cs_remainder}"

        prev_cs = res.cs_year
        prev_rem = res.cs_remainder
        curr += timedelta(days=1)

    print(f"  -> Successfully verified continuity across all {total_days} consecutive days from 1920 to 2030!")


def test_wednesday_day_night_handling_all_cases():
    print("\n[STRESS TEST 3] Wednesday Day vs Night Flag & Time Handling...")

    # Wednesday Date: 2024-05-15
    wed_date = "2024-05-15"

    # 1. Explicit Flag True -> Wednesday Night (8)
    res1 = calculate_mahabote(wed_date, is_wednesday_night=True)
    assert res1.day_of_week == 8
    assert res1.is_wednesday_night is True
    assert res1.day_name_th == "พุธ (กลางคืน - ราหู)"

    # 2. Explicit Flag False -> Wednesday Day (4)
    res2 = calculate_mahabote(wed_date, is_wednesday_night=False)
    assert res2.day_of_week == 4
    assert res2.is_wednesday_night is False
    assert res2.day_name_th == "พุธ (กลางวัน)"

    # 3. Birth Time 18:00 -> Night (8)
    res3 = calculate_mahabote(wed_date, birth_time="18:00")
    assert res3.day_of_week == 8
    assert res3.is_wednesday_night is True

    # 4. Birth Time 05:59 -> Night (8)
    res4 = calculate_mahabote(wed_date, birth_time="05:59")
    assert res4.day_of_week == 8
    assert res4.is_wednesday_night is True

    # 5. Birth Time 06:00 -> Day (4)
    res5 = calculate_mahabote(wed_date, birth_time="06:00")
    assert res5.day_of_week == 4
    assert res5.is_wednesday_night is False

    # 6. Birth Time 17:59 -> Day (4)
    res6 = calculate_mahabote(wed_date, birth_time="17:59")
    assert res6.day_of_week == 4
    assert res6.is_wednesday_night is False

    # 7. Non-Wednesday Date (Sunday: 2024-05-12) with is_wednesday_night=True
    # Should ignore flag because birth date is Sunday
    res_sun = calculate_mahabote("2024-05-12", is_wednesday_night=True)
    assert res_sun.day_of_week == 1
    assert res_sun.is_wednesday_night is False
    assert res_sun.day_name_th == "อาทิตย์"

    print("  -> Passed Wednesday Day vs Night handling across all flag & time combinations!")


def test_chart_matrix_permutation_properties():
    print("\n[STRESS TEST 4] Chart Matrix Permutation & Seam Properties...")

    for year in range(1990, 2000):
        for month in (1, 5, 9):
            d_str = f"{year}-{month:02d}-15"
            res = calculate_mahabote(d_str)

            # Check positions dict keys
            pos_keys = list(res.chart.positions.keys())
            expected_keys = ["thanang", "pita", "mata", "phoka", "matchima", "atta", "hina"]
            assert sorted(pos_keys) == sorted(expected_keys)

            # Check that 7 positions contain digits 1..7 exactly once
            digits = [res.chart.positions[k].planet_digit for k in expected_keys]
            assert sorted(digits) == [1, 2, 3, 4, 5, 6, 7], f"Positions do not form a 1..7 permutation on {d_str}: {digits}"

            # Check thanang holds remainder
            assert res.chart.positions["thanang"].planet_digit == res.cs_remainder

            # Check chart matrix structure (3x3 grid with 7 elements total)
            matrix = res.chart.chart_matrix
            assert len(matrix) == 3
            assert len(matrix[0]) == 3
            assert len(matrix[1]) == 3
            assert len(matrix[2]) == 1

            matrix_flat = [d for row in matrix for d in row]
            assert matrix_flat == digits

    print("  -> Passed Chart Matrix permutation & structure properties!")


def test_lucky_digits_and_avoid_digits_invariants():
    print("\n[STRESS TEST 5] Lucky Digits & Avoid Digits Invariants...")

    for day in range(1, 29):
        d_str = f"2024-06-{day:02d}"
        res = calculate_mahabote(d_str)
        ld = res.lucky_digits

        # Invariant 1: Kalakini planet MUST be in avoid_digits
        assert res.taksa.kalakini_planet in ld.avoid_digits

        # Invariant 2: Yamabat and Lokavinas MUST be in avoid_digits
        assert res.kalayok.yamabat_digit in ld.avoid_digits
        assert res.kalayok.lokavinas_digit in ld.avoid_digits

        # Invariant 3: Hina planet MUST be in avoid_digits
        hina_digit = res.chart.positions["hina"].planet_digit
        assert hina_digit in ld.avoid_digits

        # Invariant 4: Primary digits and avoid digits must be disjoint
        for p in ld.primary_digits:
            assert p not in ld.avoid_digits, f"Primary digit {p} found in avoid_digits on {d_str}"

        # Invariant 5: Power score is bounded between 10.0 and 100.0
        assert 10.0 <= ld.power_score <= 100.0

        # Invariant 6: 2-digit pairs are valid 2-digit strings
        for pair in ld.recommended_2digit_pairs:
            assert len(pair) == 2
            assert pair.isdigit()

    print("  -> Passed Lucky Digits & Avoid Digits invariant checks!")


def test_invalid_inputs_and_type_robustness():
    print("\n[STRESS TEST 6] Invalid Inputs & Type Robustness...")

    invalid_dates = [
        "not-a-date",
        "2024-02-30",
        "2023-04-31",
        "15/04/2024",
        "2024-13-01",
        "",
        12345,
    ]

    for inv in invalid_dates:
        try:
            calculate_mahabote(inv)
            assert False, f"Expected exception for invalid date '{inv}', but call succeeded!"
        except (ValueError, TypeError):
            pass  # Expected

    # Valid input types (str, date, datetime)
    res_str = calculate_mahabote("2024-05-15")
    res_date = calculate_mahabote(date(2024, 5, 15))
    res_dt = calculate_mahabote(datetime(2024, 5, 15, 12, 0))

    assert res_str.cs_year == res_date.cs_year == res_dt.cs_year
    assert res_str.cs_remainder == res_date.cs_remainder == res_dt.cs_remainder

    print("  -> Passed Invalid Inputs & Type Robustness checks!")


if __name__ == "__main__":
    run_all_stress_tests()
