import math
import sys
import os

# Add backend directory to sys.path
backend_path = r"e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.engines.thai_astrology import (
    calculate_lagna_sidereal,
    calculate_thai_astrology,
    determine_planetary_dignity,
    PlanetaryDignity,
    ThaiPlanet,
    ZodiacSign,
)

def run_verification():
    print("=== STARTING EMPIRICAL VERIFICATION HARNESS ===")
    
    # Test 1: GMST 0h UT formula verification
    # 2000-01-01 12:00 UT -> JD = 2451545.0
    # 2000-01-01 00:00 UT -> JD0 = 2451544.5, t0 = -0.5 / 36525
    jd_j2000 = 2451545.0
    lat_bkk, lon_bkk = 13.7563, 100.5018
    ayanamsa = 23.85305556

    print("\n[Test 1] GMST Sidereal Drift Rate Test:")
    lagnas_24h = []
    for h in range(25):
        ut_hours = float(h)
        # JD for given hour
        jd = 2451544.5 + (ut_hours / 24.0)
        lagna = calculate_lagna_sidereal(jd, ut_hours, lat_bkk, lon_bkk, ayanamsa)
        lagnas_24h.append(lagna)
        if h in [0, 6, 12, 18, 24]:
            print(f"  Hour {h:02d}:00 UT -> Lagna = {lagna:.4f}°")

    # Total net rotation in 24h
    net_rotation = (lagnas_24h[24] - lagnas_24h[0]) % 360.0
    print(f"  Net rotation over 24h: {net_rotation:.4f}° (Expect ~1.0027 * 360° mod 360 = ~0.9856°)")
    assert abs(net_rotation - 0.9856) < 0.1, f"Unexpected net rotation: {net_rotation}"

    # Test 2: 24-Hour High Resolution Time Sweep (1440 minutes)
    print("\n[Test 2] High Resolution 24-Hour Lagna Sweep (1-minute steps = 1440 steps):")
    prev_lagna = None
    total_unwrapped_rotation = 0.0
    min_step_change = 999.0
    max_step_change = -999.0
    nan_count = 0
    discontinuity_count = 0

    jd_base = 2451544.5 # 2000-01-01 00:00 UT
    for m in range(1440):
        ut_h = m / 60.0
        jd = jd_base + (ut_h / 24.0)
        lagna = calculate_lagna_sidereal(jd, ut_h, lat_bkk, lon_bkk, ayanamsa)

        if math.isnan(lagna) or math.isinf(lagna):
            nan_count += 1
            continue

        if prev_lagna is not None:
            diff = (lagna - prev_lagna) % 360.0
            # Step change per minute should be positive (~0.25° per minute)
            if diff > 180.0:
                diff -= 360.0 # Unwrap backwards if any negative jump
            
            total_unwrapped_rotation += diff

            if diff < min_step_change:
                min_step_change = diff
            if diff > max_step_change:
                max_step_change = diff

            # Check if there is any negative movement or non-monotonic jump
            if diff <= 0.0 or diff > 2.0:
                discontinuity_count += 1
                print(f"  DISCONTINUITY at minute {m} ({ut_h:.2f}h): prev={prev_lagna:.4f}, curr={lagna:.4f}, diff={diff:.4f}")

        prev_lagna = lagna

    print(f"  Total Unwrapped Rotation in 24h: {total_unwrapped_rotation:.4f}° (Expect ~360.9856°)")
    print(f"  Min step change/min: {min_step_change:.6f}°")
    print(f"  Max step change/min: {max_step_change:.6f}°")
    print(f"  NaN / Inf count: {nan_count}")
    print(f"  Discontinuity count: {discontinuity_count}")

    assert nan_count == 0, "Found NaN or Inf in Lagna sweep!"
    assert discontinuity_count == 0, f"Found {discontinuity_count} discontinuities in Lagna sweep!"
    assert abs(total_unwrapped_rotation - 360.9856) < 0.5, f"Unwrapped rotation out of bounds: {total_unwrapped_rotation}"

    # Test 3: Ground Truth Benchmarks & Precedence
    print("\n[Test 3] Benchmark & Dignity Precedence Verification:")
    res_1990 = calculate_thai_astrology("1990-01-01", "12:00", "กรุงเทพมหานคร")
    print(f"  1990-01-01 12:00 BKK Lagna: {res_1990.lagna.longitude:.4f}° ({res_1990.lagna.rasi_name_th}, Sign #{res_1990.lagna.rasi_index})")
    assert res_1990.lagna.rasi_index == 11, "1990-01-01 12:00 Lagna must be Pisces (11)"

    res_sunrise = calculate_thai_astrology("2026-08-05", "06:00", "กรุงเทพมหานคร")
    sun_sign = res_sunrise.planets[1].rasi_index
    lagna_sign = res_sunrise.lagna.rasi_index
    print(f"  2026-08-05 06:00 BKK Sunrise: Sun Sign #{sun_sign}, Lagna Sign #{lagna_sign}")
    assert sun_sign == lagna_sign, "At sunrise, Lagna must match Sun sign!"

    # Mercury in Virgo check
    dig_mercury_virgo = determine_planetary_dignity(4, 5)
    print(f"  Mercury (4) in Virgo (5) Dignity: {dig_mercury_virgo} (Expect UCC)")
    assert dig_mercury_virgo == PlanetaryDignity.UCC, "Mercury in Virgo must be UCC"

    print("\n=== ALL VERIFICATION CHECKS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_verification()
