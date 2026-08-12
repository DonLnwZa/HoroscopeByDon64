"""
Empirical Verification & Stress Test Harness for M1.2 Numerology Engine
Author: Challenger 2 (challenger_m1_2_2)
"""

import sys
import os
from datetime import date, datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../omni_oracle_app/backend")))

from app.engines.numerology_7x9 import (
    calculate_numerology_7x9,
    HouseType,
    HouseDetail7x9,
    BaseCollisionInfo,
    NumerologyMatrix,
    Numerology7x9Result,
    HOUSE_MATRIX_TAXONOMY,
    INAUSPICIOUS_HOUSE_NAMES,
    TOP_AUSPICIOUS_HOUSE_NAMES,
    SECONDARY_AUSPICIOUS_HOUSE_NAMES,
    PLANETARY_STRENGTH,
    FRIENDLY_PAIRS,
)

def run_empirical_verification():
    print("=== Starting M1.2 Empirical Verification Harness ===")
    
    passed_tests = 0
    failed_tests = 0
    failures = []

    def check(condition, msg):
        nonlocal passed_tests, failed_tests
        if condition:
            passed_tests += 1
        else:
            failed_tests += 1
            failures.append(msg)
            print(f"[FAIL] {msg}")

    # 1. Exhaustive test over all 7x7x7 = 343 combination triples of (D, M, Y)
    total_combinations = 0
    for d in range(1, 8):
        for m in range(1, 13):
            for y in range(1, 13):
                total_combinations += 1
                try:
                    res = calculate_numerology_7x9(
                        "2026-01-01",
                        day_of_week=d,
                        thai_lunar_month=m,
                        thai_lunar_year=y,
                    )
                    
                    # Verify matrix dimensions
                    check(len(res.matrix.matrix_grid) == 9, f"D={d},M={m},Y={y}: Matrix grid row count != 9")
                    for r_idx, row in enumerate(res.matrix.matrix_grid):
                        check(len(row) == 7, f"D={d},M={m},Y={y}: Row {r_idx} length != 7")
                    
                    # Verify Base 1, 2, 3 values are strictly 1..7
                    for val in res.base_1_row:
                        check(1 <= val <= 7, f"Base 1 val {val} out of bounds 1..7")
                    for val in res.base_2_row:
                        check(1 <= val <= 7, f"Base 2 val {val} out of bounds 1..7")
                    for val in res.base_3_row:
                        check(1 <= val <= 7, f"Base 3 val {val} out of bounds 1..7")
                        
                    # Verify Base 4 formula: Base 4 = Base 1 + Base 2 + Base 3
                    expected_b4 = [res.base_1_row[c] + res.base_2_row[c] + res.base_3_row[c] for c in range(7)]
                    check(res.base_4_row == expected_b4, f"D={d},M={m},Y={y}: Base 4 formula mismatch")

                    # Verify Base 5 = Base 1 + Base 2
                    expected_b5 = [res.base_1_row[c] + res.base_2_row[c] for c in range(7)]
                    check(res.base_5_row == expected_b5, f"D={d},M={m},Y={y}: Base 5 formula mismatch")

                    # Verify Base 6 = Base 1 + Base 3
                    expected_b6 = [res.base_1_row[c] + res.base_3_row[c] for c in range(7)]
                    check(res.base_6_row == expected_b6, f"D={d},M={m},Y={y}: Base 6 formula mismatch")

                    # Verify Base 7 = Base 2 + Base 3
                    expected_b7 = [res.base_2_row[c] + res.base_3_row[c] for c in range(7)]
                    check(res.base_7_row == expected_b7, f"D={d},M={m},Y={y}: Base 7 formula mismatch")

                    # Verify Base 8 = Base 1 + Base 4
                    expected_b8 = [res.base_1_row[c] + res.base_4_row[c] for c in range(7)]
                    check(res.base_8_row == expected_b8, f"D={d},M={m},Y={y}: Base 8 formula mismatch")

                    # Verify Base 9 = Planetary strength of Base 1
                    expected_b9 = [PLANETARY_STRENGTH.get(res.base_1_row[c], res.base_1_row[c]) for c in range(7)]
                    check(res.base_9_row == expected_b9, f"D={d},M={m},Y={y}: Base 9 formula mismatch")

                    # Verify 21 Houses mapping
                    check(len(res.houses) == 21, f"D={d},M={m},Y={y}: House count != 21 (got {len(res.houses)})")
                    for name_th, house in res.houses.items():
                        check(1 <= house.digit_value <= 7, f"House {name_th} digit value {house.digit_value} not in 1..7")
                        check(3 <= house.base4_power <= 21, f"House {name_th} base4 power {house.base4_power} not in 3..21")

                    # Verify digit collision scoring for digits 1..7
                    check(len(res.collisions) == 7, f"D={d},M={m},Y={y}: Collision count != 7")
                    for digit_k, coll in res.collisions.items():
                        check(coll.count == 3, f"Digit {digit_k} count != 3 (got {coll.count})")
                        check(len(coll.houses) == 3, f"Digit {digit_k} houses len != 3")
                        check(len(coll.base4_powers) == 3, f"Digit {digit_k} base4_powers len != 3")

                    # Verify extracted lucky digits are single-digit integers 1..7
                    check(1 <= len(res.primary_lucky_digits) <= 3, f"Primary lucky digits count invalid: {len(res.primary_lucky_digits)}")
                    for pd in res.primary_lucky_digits:
                        check(isinstance(pd, int) and 1 <= pd <= 7, f"Primary lucky digit {pd} not single-digit integer 1..7")

                    for sd in res.secondary_lucky_digits:
                        check(isinstance(sd, int) and 1 <= sd <= 7, f"Secondary lucky digit {sd} not single-digit integer 1..7")

                    # Check lucky_numbers list: contains single digits and 2-digit pairs
                    for num in res.lucky_numbers:
                        check(isinstance(num, int) and 0 <= num <= 99, f"Lucky number {num} out of 0..99 range")

                except Exception as e:
                    check(False, f"Exception for D={d},M={m},Y={y}: {str(e)}")

    print(f"Tested {total_combinations} D/M/Y combinations.")

    # 2. Test ISO date parsing across edge cases
    test_dates = [
        "2000-01-01",
        "1995-08-15",
        "2024-02-29", # Leap year
        "1900-01-01",
        "2099-12-31",
    ]
    for bd in test_dates:
        try:
            res = calculate_numerology_7x9(bd)
            check(res.birth_date == bd, f"Birth date mismatch for {bd}")
        except Exception as e:
            check(False, f"Date parsing failed for {bd}: {e}")

    # 3. Check invalid inputs and exception handling
    invalid_dates = ["invalid", "2023-13-01", "2023-02-30", "", "15-08-1995"]
    for inv in invalid_dates:
        try:
            calculate_numerology_7x9(inv)
            check(False, f"Expected ValueError for invalid date '{inv}' but none raised")
        except ValueError:
            passed_tests += 1
        except Exception as e:
            check(False, f"Unexpected exception for invalid date '{inv}': {e}")

    invalid_params = [
        ("2026-01-01", 0, 1, 1),
        ("2026-01-01", 8, 1, 1),
        ("2026-01-01", 1, 0, 1),
        ("2026-01-01", 1, 13, 1),
        ("2026-01-01", 1, 1, 0),
        ("2026-01-01", 1, 1, 13),
    ]
    for bd, d_val, m_val, y_val in invalid_params:
        try:
            calculate_numerology_7x9(bd, day_of_week=d_val, thai_lunar_month=m_val, thai_lunar_year=y_val)
            check(False, f"Expected ValueError for invalid params ({d_val},{m_val},{y_val})")
        except ValueError:
            passed_tests += 1

    print(f"=== Verification Complete: {passed_tests} PASSED, {failed_tests} FAILED ===")
    if failures:
        print("Failures detail:")
        for f in failures[:10]:
            print(f" - {f}")
    return failed_tests == 0

if __name__ == "__main__":
    success = run_empirical_verification()
    sys.exit(0 if success else 1)
