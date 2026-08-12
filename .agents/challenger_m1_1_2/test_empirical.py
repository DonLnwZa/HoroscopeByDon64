"""
Empirical Verification & Stress Test Suite for Thai Astrology Engine (M1.1)
Challenger 2 (.agents/challenger_m1_1_2/test_empirical.py)

Tests:
1. D9 Navamsa boundary transitions (0°, 3°20', 6°40', 9°59'59", 10°, 30°, 359°59'59", 360°, floating point precision around boundaries).
2. D3 Drekkana boundary transitions (0°, 9°59'59", 10°, 19°59'59", 20°, 29°59'59", 30°, etc.).
3. Stress test extract_lucky_astrology_digits for range 0-9, non-empty, deduplication, synthetic inputs.
4. Comprehensive range scanning over 0.0° to 360.0° in fine steps (0.01°).
"""

import sys
import os
import math

# Add backend directory to sys.path to allow direct import
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "omni_oracle_app", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.engines.thai_astrology import (
    calculate_d9_navamsa,
    calculate_d3_drekkana,
    extract_lucky_astrology_digits,
    calculate_thai_astrology,
    calculate_lahiri_ayanamsa,
    calculate_julian_day,
    get_province_coordinates,
    ThaiAstrologyResult,
    LagnaInfo,
    PlanetPosition,
    HouseDetail,
    PlanetaryDignity,
    ThaiPlanet,
    ZodiacSign,
    AstrologicalHouse,
)


def verify_d9_navamsa_boundaries():
    """Verify D9 Navamsa segment boundary transitions."""
    results = []

    # 1. Micro-boundary tests around 3°20' (200 arcmin = 3.333333... degrees)
    # Just before 3°20' -> should be 0 (Aries Navamsa in Aries Rasi)
    # Exactly at 3°20' -> should be 1 (Taurus Navamsa in Aries Rasi)
    test_cases_d9 = [
        (0.0, 0, "0°00'00\" (Aries Rasi, 1st Navamsa)"),
        (0.000001, 0, "0°00'00.0036\""),
        (3.333333, 0, "3°19'59.999\" (Just before 3°20')"),
        (3.3333333333333335, 1, "3°20'00\" (Exact 3°20' -> 2nd Navamsa)"),
        (3.333334, 1, "3°20'00.0036\""),
        (6.666666, 1, "6°39'59.999\" (Just before 6°40')"),
        (6.666666666666667, 2, "6°40'00\" (Exact 6°40' -> 3rd Navamsa)"),
        (9.999722222222223, 2, "9°59'59\" (Just before 10°00')"),
        (10.0, 3, "10°00'00\" (Exact 10°00' -> 4th Navamsa)"),
        (13.333333333333334, 4, "13°20'00\" (Exact 13°20' -> 5th Navamsa)"),
        (16.666666666666668, 5, "16°40'00\" (Exact 16°40' -> 6th Navamsa)"),
        (20.0, 6, "20°00'00\" (Exact 20°00' -> 7th Navamsa)"),
        (23.333333333333336, 7, "23°20'00\" (Exact 23°20' -> 8th Navamsa)"),
        (26.666666666666668, 8, "26°40'00\" (Exact 26°40' -> 9th Navamsa)"),
        (29.999999, 8, "29°59'59.996\" (End of Aries Rasi)"),
        (30.0, 9, "30°00'00\" (Start of Taurus Rasi -> 1st Navamsa of Taurus = Capricorn)"),
        (33.333333333333336, 10, "33°20'00\" (2nd Navamsa of Taurus = Aquarius)"),
        (359.999999, 11, "359°59'59.996\" (End of Pisces Rasi -> 9th Navamsa of Pisces = Pisces)"),
        (360.0, 0, "360°00'00\" (Wrap around to 0° Aries)"),
    ]

    passed = 0
    failed = 0
    for long_deg, expected_nav, desc in test_cases_d9:
        actual_nav = calculate_d9_navamsa(long_deg)
        if actual_nav == expected_nav:
            passed += 1
            results.append(f"[PASS] D9 long={long_deg:18.12f} deg | expected={expected_nav:2d} | actual={actual_nav:2d} | {desc}")
        else:
            failed += 1
            results.append(f"[FAIL] D9 long={long_deg:18.12f} deg | expected={expected_nav:2d} | actual={actual_nav:2d} | {desc}")

    # Exhaustive continuous scanning across all 108 navamsa segments (0° to 360°, step 0.01°)
    scan_passed = 0
    scan_total = 36000
    for i in range(scan_total):
        deg = i * 0.01
        nav = calculate_d9_navamsa(deg)
        expected = int((deg * 60.0) // 200.0) % 12
        if nav == expected and 0 <= nav <= 11:
            scan_passed += 1

    return passed, failed, scan_passed, scan_total, results


def verify_d3_drekkana_boundaries():
    """Verify D3 Drekkana segment boundary transitions."""
    results = []

    # Decans: 0° to <10° (decan 0), 10° to <20° (decan 1), 20° to <30° (decan 2)
    test_cases_d3 = [
        (0.0, 0, "0°00'00\" Aries (Decan 1 -> Aries)"),
        (9.999999, 0, "9°59'59.996\" Aries (Decan 1 -> Aries)"),
        (10.0, 4, "10°00'00\" Aries (Decan 2 -> Leo)"),
        (19.999999, 4, "19°59'59.996\" Aries (Decan 2 -> Leo)"),
        (20.0, 8, "20°00'00\" Aries (Decan 3 -> Sagittarius)"),
        (29.999999, 8, "29°59'59.996\" Aries (Decan 3 -> Sagittarius)"),
        (30.0, 1, "30°00'00\" Taurus (Decan 1 -> Taurus)"),
        (40.0, 5, "40°00'00\" Taurus (Decan 2 -> Virgo)"),
        (50.0, 9, "50°00'00\" Taurus (Decan 3 -> Capricorn)"),
        (60.0, 2, "60°00'00\" Gemini (Decan 1 -> Gemini)"),
        (70.0, 6, "70°00'00\" Gemini (Decan 2 -> Libra)"),
        (80.0, 10, "80°00'00\" Gemini (Decan 3 -> Aquarius)"),
        (359.999999, 11, "359°59'59.996\" Pisces (Decan 3 -> Pisces)"),
        (360.0, 0, "360°00'00\" Wrap around to 0° Aries"),
    ]

    passed = 0
    failed = 0
    for long_deg, expected_d3, desc in test_cases_d3:
        actual_d3 = calculate_d3_drekkana(long_deg)
        if actual_d3 == expected_d3:
            passed += 1
            results.append(f"[PASS] D3 long={long_deg:18.12f} deg | expected={expected_d3:2d} | actual={actual_d3:2d} | {desc}")
        else:
            failed += 1
            results.append(f"[FAIL] D3 long={long_deg:18.12f} deg | expected={expected_d3:2d} | actual={actual_d3:2d} | {desc}")

    # Exhaustive continuous scanning across 36 drekkana segments (0° to 360°, step 0.01°)
    scan_passed = 0
    scan_total = 36000
    for i in range(scan_total):
        deg = i * 0.01
        d3 = calculate_d3_drekkana(deg)
        sign_idx = int(deg // 30.0) % 12
        decan_idx = int((deg % 30.0) // 10.0) % 3
        expected = (sign_idx + 4 * decan_idx) % 12
        if d3 == expected and 0 <= d3 <= 11:
            scan_passed += 1

    return passed, failed, scan_passed, scan_total, results


def stress_test_lucky_digits():
    """Stress test extract_lucky_astrology_digits under normal and extreme synthetic charts."""
    results = []
    passed = 0
    failed = 0

    # 1. Real birth charts across 12 months & various times
    sample_dates = [
        ("1980-01-01", "00:00"),
        ("1985-04-15", "06:30"),
        ("1990-07-20", "12:00"),
        ("1995-10-31", "18:45"),
        ("2000-02-29", "23:59"),
        ("2012-12-12", "12:12"),
        ("2026-08-06", "08:00"),
    ]

    for bdate, btime in sample_dates:
        res = calculate_thai_astrology(bdate, btime)
        digits = extract_lucky_astrology_digits(res)
        
        # Check non-empty
        cond_nonempty = len(digits) > 0
        # Check all integers 0-9
        cond_valid_range = all(isinstance(d, int) and 0 <= d <= 9 for d in digits)
        # Check at least 5 digits (per implementation guarantee)
        cond_min_len = len(digits) >= 5

        if cond_nonempty and cond_valid_range and cond_min_len:
            passed += 1
            results.append(f"[PASS] Real Chart ({bdate} {btime}) -> lucky_digits={digits}")
        else:
            failed += 1
            results.append(f"[FAIL] Real Chart ({bdate} {btime}) -> lucky_digits={digits}")

    # 2. Synthetic Charts with extreme/edge configurations
    # Synthetic 1: Minimal dummy result
    dummy_lagna = LagnaInfo(
        longitude=0.0, rasi_index=0, rasi_name_th="เมษ", degree_in_rasi=0.0,
        navamsa_rasi_index=0, navamsa_rasi_th="เมษ", drekkana_rasi_index=0, drekkana_rasi_th="เมษ"
    )

    # Construct 10 planets
    dummy_planets = {}
    for pid in range(10):
        dummy_planets[pid] = PlanetPosition(
            planet_id=pid, planet_name_th="P", planet_name_en="P", longitude=0.0,
            rasi_index=0, rasi_name_th="เมษ", degree_in_rasi=0.0, house_number=1,
            house_name_th="ตนุ", dignity=PlanetaryDignity.NORMAL, navamsa_rasi_index=0,
            navamsa_rasi_th="เมษ", drekkana_rasi_index=0, drekkana_rasi_th="เมษ"
        )

    dummy_houses = [
        HouseDetail(house_number=h, house_name_th="H", rasi_index=(h-1)%12, rasi_name_th="S", lord_planet_id=1)
        for h in range(1, 13)
    ]

    # Synthetic chart A: Duplicate lords & no exalted planets
    synth_res_a = ThaiAstrologyResult(
        ayanamsa_degree=24.0, lagna=dummy_lagna, planets=dummy_planets, houses=dummy_houses,
        primary_lucky_planet=3, secondary_lucky_planet=3, house_lord_digits=[3, 3, 3, 3], lucky_numbers=[]
    )
    digits_a = extract_lucky_astrology_digits(synth_res_a)
    cond_a_valid = len(digits_a) >= 5 and all(0 <= d <= 9 for d in digits_a)
    if cond_a_valid:
        passed += 1
        results.append(f"[PASS] Synthetic Chart A (all lords=3) -> lucky_digits={digits_a}")
    else:
        failed += 1
        results.append(f"[FAIL] Synthetic Chart A -> lucky_digits={digits_a}")

    # Synthetic chart B: All planets KASET or UCC
    for pid in range(10):
        dummy_planets[pid].dignity = PlanetaryDignity.UCC
    synth_res_b = ThaiAstrologyResult(
        ayanamsa_degree=24.0, lagna=dummy_lagna, planets=dummy_planets, houses=dummy_houses,
        primary_lucky_planet=1, secondary_lucky_planet=5, house_lord_digits=[1, 4, 6, 5], lucky_numbers=[]
    )
    digits_b = extract_lucky_astrology_digits(synth_res_b)
    cond_b_valid = len(digits_b) >= 5 and all(0 <= d <= 9 for d in digits_b)
    if cond_b_valid:
        passed += 1
        results.append(f"[PASS] Synthetic Chart B (all UCC planets) -> lucky_digits={digits_b}")
    else:
        failed += 1
        results.append(f"[FAIL] Synthetic Chart B -> lucky_digits={digits_b}")

    return passed, failed, results


def run_all_empirical_tests():
    print("=" * 70)
    print("EMPIRICAL VERIFICATION SUITE - THAI ASTROLOGY ENGINE (M1.1)")
    print("=" * 70)

    # 1. D9 Navamsa
    d9_p, d9_f, d9_sp, d9_st, d9_res = verify_d9_navamsa_boundaries()
    print(f"\n--- 1. D9 Navamsa Boundary Verification ---")
    for line in d9_res:
        print(line)
    print(f"Discrete boundary test result: {d9_p} PASSED, {d9_f} FAILED.")
    print(f"Continuous scan test result: {d9_sp}/{d9_st} PASSED.")

    # 2. D3 Drekkana
    d3_p, d3_f, d3_sp, d3_st, d3_res = verify_d3_drekkana_boundaries()
    print(f"\n--- 2. D3 Drekkana Boundary Verification ---")
    for line in d3_res:
        print(line)
    print(f"Discrete boundary test result: {d3_p} PASSED, {d3_f} FAILED.")
    print(f"Continuous scan test result: {d3_sp}/{d3_st} PASSED.")

    # 3. Lucky Digits Extraction
    ld_p, ld_f, ld_res = stress_test_lucky_digits()
    print(f"\n--- 3. Lucky Digits Extraction Stress Test ---")
    for line in ld_res:
        print(line)
    print(f"Lucky Digits stress test result: {ld_p} PASSED, {ld_f} FAILED.")

    print("\n" + "=" * 70)
    total_failures = d9_f + (d9_st - d9_sp) + d3_f + (d3_st - d3_sp) + ld_f
    if total_failures == 0:
        print("OVERALL VERDICT: ALL EMPIRICAL TESTS PASSED SUCCESSFULLY.")
    else:
        print(f"OVERALL VERDICT: {total_failures} EMPIRICAL TEST FAILURES DETECTED.")
    print("=" * 70)

    return total_failures


if __name__ == "__main__":
    failures = run_all_empirical_tests()
    sys.exit(0 if failures == 0 else 1)
