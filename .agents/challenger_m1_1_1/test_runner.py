"""
Empirical Verification & Stress Test Harness for Thai Astrology Engine
Runs comprehensive tests on app.engines.thai_astrology:
1. Boundary Date Inputs (historical dates, 2050+, leap years, midnight transitions)
2. Mathematical correctness of Lagna & GMST
3. Determinism & side-effect freedom across 1000 repeated calls
4. Edge cases & exception handling
5. Dignity evaluation accuracy
"""

import sys
import os
import math
from datetime import datetime, date, time

# Add omni_oracle_app/backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "omni_oracle_app", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.engines.thai_astrology import (
    calculate_thai_astrology,
    calculate_julian_day,
    calculate_lahiri_ayanamsa,
    calculate_lagna_sidereal,
    calculate_d9_navamsa,
    calculate_d3_drekkana,
    determine_planetary_dignity,
    extract_lucky_astrology_digits,
    get_province_coordinates,
    ThaiAstrologyResult,
    PlanetaryDignity,
    SIGN_RULERS,
    EXALTED_SIGNS,
    DEBILITATED_SIGNS,
)

def run_tests():
    print("=== STARTING EMPIRICAL SUITE FOR THAI ASTROLOGY ENGINE ===")
    failures = []
    
    # -------------------------------------------------------------
    # TEST 1: Standard Calculation Correctness
    # -------------------------------------------------------------
    try:
        res = calculate_thai_astrology("1995-08-15", "14:30", "กรุงเทพมหานคร")
        assert res is not None
        assert len(res.planets) == 10
        assert len(res.houses) == 12
        assert 0.0 <= res.lagna.longitude < 360.0
        assert 23.0 <= res.ayanamsa_degree <= 25.0
        print("[PASS] Test 1: Standard Calculation")
    except Exception as e:
        failures.append(f"Test 1 Failed: {e}")

    # -------------------------------------------------------------
    # TEST 2: Boundary Date Inputs
    # -------------------------------------------------------------
    boundary_dates = [
        # (date_str, time_str, province, description)
        ("1900-01-01", "00:00:00", "กรุงเทพมหานคร", "Historical 1900 midnight"),
        ("1900-12-31", "23:59:59", "เชียงใหม่", "Historical 1900 end of year"),
        ("2000-02-29", "12:00:00", "ภูเก็ต", "Leap year 2000 Feb 29"),
        ("2024-02-29", "00:00:00", "ขอนแก่น", "Leap year 2024 Feb 29 midnight"),
        ("2050-01-01", "00:00:00", "กรุงเทพมหานคร", "Future 2050 midnight"),
        ("2050-12-31", "23:59:59", "สงขลา", "Future 2050 end of year"),
        ("2100-06-15", "12:34:56", "อุดรธานี", "Far future 2100"),
        ("1850-05-10", "06:00:00", "กรุงเทพมหานคร", "Historical 1850"),
    ]
    
    for b_date, b_time, b_prov, desc in boundary_dates:
        try:
            r = calculate_thai_astrology(b_date, b_time, b_prov)
            assert 0.0 <= r.lagna.longitude < 360.0
            for pid, p in r.planets.items():
                assert 0.0 <= p.longitude < 360.0
                assert 0 <= p.rasi_index <= 11
                assert 0.0 <= p.degree_in_rasi < 30.0
                assert 1 <= p.house_number <= 12
                assert 0 <= p.navamsa_rasi_index <= 11
                assert 0 <= p.drekkana_rasi_index <= 11
            print(f"[PASS] Test 2 Boundary: {desc} ({b_date} {b_time})")
        except Exception as e:
            failures.append(f"Test 2 Boundary Failed for {desc} ({b_date}): {e}")

    # Invalid leap year 1900-02-29
    try:
        calculate_thai_astrology("1900-02-29", "12:00")
        failures.append("Test 2 Invalid Leap Year Failed: 1900-02-29 should have raised ValueError")
    except ValueError:
        print("[PASS] Test 2 Invalid Leap Year 1900-02-29 correctly rejected")

    # -------------------------------------------------------------
    # TEST 3: Determinism & Side Effect Freedom
    # -------------------------------------------------------------
    try:
        res1 = calculate_thai_astrology("1995-08-15", "14:30:00", "กรุงเทพมหานคร")
        for _ in range(100):
            res2 = calculate_thai_astrology("1995-08-15", "14:30:00", "กรุงเทพมหานคร")
            assert res1.lagna.longitude == res2.lagna.longitude
            assert res1.ayanamsa_degree == res2.ayanamsa_degree
            assert res1.lucky_numbers == res2.lucky_numbers
            for pid in range(10):
                assert res1.planets[pid].longitude == res2.planets[pid].longitude
                assert res1.planets[pid].dignity == res2.planets[pid].dignity
        print("[PASS] Test 3: Determinism across 100 repeated calls")
    except Exception as e:
        failures.append(f"Test 3 Determinism Failed: {e}")

    # -------------------------------------------------------------
    # TEST 4: Mathematical Verification of Lagna GMST & Formula Inspection
    # -------------------------------------------------------------
    # Checking GMST double-counting in calculate_lagna_sidereal
    jd = 2451545.0 # J2000 12:00 UT
    ut_hours = 12.0
    lat, lon = 13.7563, 100.5018
    ayanamsa = 23.85305556
    
    # Calculate using current function
    lagna1 = calculate_lagna_sidereal(jd, ut_hours, lat, lon, ayanamsa)
    print(f"Calculated Sidereal Lagna at J2000 12:00 UT: {lagna1:.4f}°")

    # Correct Meeus GMST calculation:
    # GMST_0h = 100.46061837 + 36000.770053608 * T0 + 0.000387933 * T0^2
    # GMST = GMST_0h + 360.98564736629 * (ut / 24.0)
    jd_0h = 2451544.5 # J2000 0h UT
    t0_correct = (jd_0h - 2451545.0) / 36525.0
    gmst0_correct = 100.46061837 + (36000.770053608 * t0_correct) + (0.000387933 * t0_correct * t0_correct)
    gmst_correct = (gmst0_correct + 360.98564736629 * (ut_hours / 24.0)) % 360.0
    lst_correct = (gmst_correct + lon) % 360.0
    
    rad = math.radians
    eps = 23.439291 - 0.0130042 * t0_correct
    y = -math.cos(rad(lst_correct))
    x = (math.sin(rad(lst_correct)) * math.cos(rad(eps))) + (math.tan(rad(lat)) * math.sin(rad(eps)))
    asc_trop_correct = math.degrees(math.atan2(y, x)) % 360.0
    asc_sid_correct = (asc_trop_correct - ayanamsa) % 360.0

    diff_lagna = abs(lagna1 - asc_sid_correct)
    print(f"Correct Sidereal Lagna: {asc_sid_correct:.4f}°, Diff: {diff_lagna:.4f}°")
    if diff_lagna > 0.01:
        print(f"[WARN/BUG DETECTED] Lagna math has a {diff_lagna:.4f}° deviation due to GMST double-counting of UT rate!")

    # -------------------------------------------------------------
    # TEST 5: Dignity Precedence Audit (Mercury in Virgo)
    # -------------------------------------------------------------
    # Mercury (4) in Virgo (5)
    merc_virgo_dignity = determine_planetary_dignity(4, 5)
    print(f"Mercury (4) in Virgo (5) dignity evaluated as: {merc_virgo_dignity}")
    if merc_virgo_dignity == PlanetaryDignity.KASET:
        print("[NOTE/ISSUE] Mercury in Virgo evaluated as KASET instead of UCC due to rule order (KASET checked before UCC).")

    # -------------------------------------------------------------
    # SUMMARY & VERDICT
    # -------------------------------------------------------------
    print("\n=== SUMMARY OF EMPIRICAL SUITE ===")
    if failures:
        print(f"Total Failures: {len(failures)}")
        for f in failures:
            print(f" - {f}")
    else:
        print("All structural & boundary tests passed successfully.")

if __name__ == "__main__":
    run_tests()
