import sys
import os
import random
from datetime import date, timedelta
import math

# Add backend directory to sys.path
backend_dir = r"e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.engines.mahabote import (
    MahaboteEngine,
    calculate_mahabote,
    DayOfWeek,
    TaksaCategory,
    KalayokCategory,
    MahabotePositionEnum,
)

def run_49_combinations_test():
    print("=== TEST 1: All 49 combinations of (7 weekdays x 7 CS remainders) ===")
    errors = []
    
    # 7 CS remainders: 1 to 7
    # For CS remainder rem, we can find a year CS_year such that CS_year % 7 == rem (if rem != 7 else 0)
    # E.g. CS 1380 to 1386 cover remainders 1, 2, 3, 4, 5, 6, 7 (1386 % 7 == 0 -> rem 7).
    # Birth dates for weekdays 1 to 7 (Sun to Sat):
    # 2024-05-12 is Sunday (1)
    # 2024-05-13 is Monday (2)
    # 2024-05-14 is Tuesday (3)
    # 2024-05-15 is Wednesday (4)
    # 2024-05-16 is Thursday (5)
    # 2024-05-17 is Friday (6)
    # 2024-05-18 is Saturday (7)
    
    base_dates_by_weekday = {
        1: date(2024, 5, 12),
        2: date(2024, 5, 13),
        3: date(2024, 5, 14),
        4: date(2024, 5, 15),
        5: date(2024, 5, 16),
        6: date(2024, 5, 17),
        7: date(2024, 5, 18),
    }

    # CS year formula for post-Songkran date (May): CS = AD - 638
    # We want CS % 7 == rem (with rem=7 for 0).
    # CS = 1386 is 0 mod 7 -> rem 7. AD = 1386 + 638 = 2024.
    # CS = 1380..1386 -> AD = 2018..2024.
    cs_rem_to_ad_year = {
        1: 2019, # CS 1381 % 7 = 1
        2: 2020, # CS 1382 % 7 = 2
        3: 2021, # CS 1383 % 7 = 3
        4: 2022, # CS 1384 % 7 = 4
        5: 2023, # CS 1385 % 7 = 5
        6: 2018, # CS 1380 % 7 = 6
        7: 2024, # CS 1386 % 7 = 0 -> 7
    }

    count = 0
    for day_digit, base_d in base_dates_by_weekday.items():
        for target_rem, ad_year in cs_rem_to_ad_year.items():
            count += 1
            # Adjust year while preserving weekday (same month/day offset by 7-day multiples or target year)
            # Find a date in target ad_year with the same day of week (day_digit)
            # We can start at date(ad_year, 5, 1) and find the matching weekday
            test_d = date(ad_year, 5, 1)
            # Python weekday: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
            target_py_wkday = {1: 6, 2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5}[day_digit]
            while test_d.weekday() != target_py_wkday:
                test_d += timedelta(days=1)
                
            try:
                res = calculate_mahabote(test_d)
                
                # Check CS remainder
                if res.cs_remainder != target_rem:
                    errors.append(f"Combo #{count} (Day {day_digit}, Target Rem {target_rem}): got cs_remainder {res.cs_remainder}")
                
                # Check day of week
                if res.day_of_week != day_digit:
                    errors.append(f"Combo #{count} (Day {day_digit}, Target Rem {target_rem}): got day_of_week {res.day_of_week}")
                
                # Verify chart 7 houses
                chart = res.chart
                if len(chart.positions) != 7:
                    errors.append(f"Combo #{count}: positions count {len(chart.positions)} != 7")
                
                expected_positions = ["thanang", "pita", "mata", "phoka", "matchima", "atta", "hina"]
                for i, pos_key in enumerate(expected_positions):
                    if pos_key not in chart.positions:
                        errors.append(f"Combo #{count}: missing position {pos_key}")
                    else:
                        pos_detail = chart.positions[pos_key]
                        expected_planet = ((target_rem - 1 + i) % 7) + 1
                        if pos_detail.planet_digit != expected_planet:
                            errors.append(f"Combo #{count} {pos_key}: expected planet {expected_planet}, got {pos_detail.planet_digit}")
                        if not (1 <= pos_detail.planet_digit <= 7):
                            errors.append(f"Combo #{count} {pos_key}: planet digit {pos_detail.planet_digit} out of bounds [1..7]")

                # Check matrix structure
                if len(chart.chart_matrix) != 3:
                    errors.append(f"Combo #{count}: chart_matrix length {len(chart.chart_matrix)} != 3")
                elif len(chart.chart_matrix[0]) != 3 or len(chart.chart_matrix[1]) != 3 or len(chart.chart_matrix[2]) != 1:
                    errors.append(f"Combo #{count}: chart_matrix shape is invalid: {[len(r) for r in chart.chart_matrix]}")

            except Exception as e:
                errors.append(f"Combo #{count} (Day {day_digit}, Target Rem {target_rem}) raised exception: {e}")

    print(f"Tested {count} combinations. Errors found: {len(errors)}")
    for err in errors:
        print("  -", err)
    return len(errors) == 0


def run_taksa_wheel_test():
    print("\n=== TEST 2: Taksa Planetary Wheel across all 8 planets / weekdays ===")
    errors = []
    
    # Check all 8 day_digits (1..8)
    expected_wheels = {
        1: [1, 2, 3, 4, 7, 5, 8, 6],
        2: [2, 3, 4, 7, 5, 8, 6, 1],
        3: [3, 4, 7, 5, 8, 6, 1, 2],
        4: [4, 7, 5, 8, 6, 1, 2, 3],
        5: [5, 8, 6, 1, 2, 3, 4, 7],
        6: [6, 1, 2, 3, 4, 7, 5, 8],
        7: [7, 5, 8, 6, 1, 2, 3, 4],
        8: [8, 6, 1, 2, 3, 4, 7, 5],
    }
    
    expected_categories = [
        "บริวาร", "อายุ", "เดช", "ศรี", "มูละ", "อุตสาหะ", "มนตรี", "กาลกิณี"
    ]

    for day_digit in range(1, 9):
        taksa = MahaboteEngine.calculate_taksa(day_digit)
        
        if taksa.birth_day_digit != day_digit:
            errors.append(f"Day {day_digit}: taksa.birth_day_digit is {taksa.birth_day_digit}")
        
        planets_order = [p.planet_digit for p in taksa.planets]
        cats_order = [p.category for p in taksa.planets]
        
        if planets_order != expected_wheels[day_digit]:
            errors.append(f"Day {day_digit}: expected planets {expected_wheels[day_digit]}, got {planets_order}")
            
        if cats_order != expected_categories:
            errors.append(f"Day {day_digit}: expected categories {expected_categories}, got {cats_order}")
            
        # Check brivar, sri, kalakini
        if taksa.brivar_planet != expected_wheels[day_digit][0]:
            errors.append(f"Day {day_digit}: brivar {taksa.brivar_planet} != {expected_wheels[day_digit][0]}")
        if taksa.sri_planet != expected_wheels[day_digit][3]:
            errors.append(f"Day {day_digit}: sri {taksa.sri_planet} != {expected_wheels[day_digit][3]}")
        if taksa.kalakini_planet != expected_wheels[day_digit][7]:
            errors.append(f"Day {day_digit}: kalakini {taksa.kalakini_planet} != {expected_wheels[day_digit][7]}")

    print(f"Tested all 8 Taksa weekdays. Errors found: {len(errors)}")
    for err in errors:
        print("  -", err)
    return len(errors) == 0


def run_random_1000_birthdates_test():
    print("\n=== TEST 3: Stress test 1,000 random birthdates (Lucky digits & lottery pairs) ===")
    errors = []
    
    random.seed(42)
    start_date = date(1940, 1, 1)
    end_date = date(2030, 12, 31)
    delta_days = (end_date - start_date).days
    
    count = 1000
    for i in range(count):
        r_days = random.randint(0, delta_days)
        b_date = start_date + timedelta(days=r_days)
        
        # Also test random times and wednesday night flags
        r_hour = random.randint(0, 23)
        r_min = random.randint(0, 59)
        b_time_str = f"{r_hour:02d}:{r_min:02d}"
        is_wed_night_flag = None if b_date.weekday() != 2 else random.choice([True, False, None])
        
        try:
            res = calculate_mahabote(
                birth_date=b_date,
                birth_time=b_time_str,
                is_wednesday_night=is_wed_night_flag,
            )
            ld = res.lucky_digits
            
            # Check NaN, Null, or invalid types
            if ld.power_score is None or math.isnan(ld.power_score):
                errors.append(f"Iter #{i} ({b_date}): power_score is null/NaN ({ld.power_score})")
            elif not (0.0 <= ld.power_score <= 100.0):
                errors.append(f"Iter #{i} ({b_date}): power_score {ld.power_score} out of range [0..100]")
                
            # Check primary digits
            if ld.primary_digits is None:
                errors.append(f"Iter #{i} ({b_date}): primary_digits is None")
            else:
                for d in ld.primary_digits:
                    if not isinstance(d, int) or not (0 <= d <= 9):
                        errors.append(f"Iter #{i} ({b_date}): invalid primary digit {d}")

            # Check secondary digits
            if ld.secondary_digits is None:
                errors.append(f"Iter #{i} ({b_date}): secondary_digits is None")
            else:
                for d in ld.secondary_digits:
                    if not isinstance(d, int) or not (0 <= d <= 9):
                        errors.append(f"Iter #{i} ({b_date}): invalid secondary digit {d}")

            # Check avoid digits
            if ld.avoid_digits is None:
                errors.append(f"Iter #{i} ({b_date}): avoid_digits is None")
            else:
                for d in ld.avoid_digits:
                    if not isinstance(d, int) or not (0 <= d <= 9):
                        errors.append(f"Iter #{i} ({b_date}): invalid avoid digit {d}")

            # Check recommended 2-digit lottery pairs
            if ld.recommended_2digit_pairs is None:
                errors.append(f"Iter #{i} ({b_date}): recommended_2digit_pairs is None")
            elif len(ld.recommended_2digit_pairs) == 0:
                errors.append(f"Iter #{i} ({b_date}): recommended_2digit_pairs is EMPTY")
            else:
                for pair in ld.recommended_2digit_pairs:
                    if not isinstance(pair, str):
                        errors.append(f"Iter #{i} ({b_date}): pair {pair} is not str")
                    elif len(pair) != 2:
                        errors.append(f"Iter #{i} ({b_date}): pair '{pair}' length != 2")
                    elif not pair.isdigit():
                        errors.append(f"Iter #{i} ({b_date}): pair '{pair}' is not digit format '00'-'99'")
                    else:
                        val = int(pair)
                        if not (0 <= val <= 99):
                            errors.append(f"Iter #{i} ({b_date}): pair value {val} out of range 0..99")

        except Exception as e:
            errors.append(f"Iter #{i} ({b_date}) raised exception: {e}")

    print(f"Tested {count} random birthdates. Errors found: {len(errors)}")
    for err in errors[:10]: # Print first 10
        print("  -", err)
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more errors")
    return len(errors) == 0


if __name__ == "__main__":
    t1 = run_49_combinations_test()
    t2 = run_taksa_wheel_test()
    t3 = run_random_1000_birthdates_test()
    
    if t1 and t2 and t3:
        print("\n>>> ALL STRESS TESTS PASSED SUCCESSFULLY! <<<")
        sys.exit(0)
    else:
        print("\n>>> STRESS TESTS FAILED! <<<")
        sys.exit(1)
