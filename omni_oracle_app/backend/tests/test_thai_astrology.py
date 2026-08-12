"""
Pytest Unit Test Suite for Thai Astrology Engine (M1.1)
Target Module: app.engines.thai_astrology
Strict TDD: RED -> GREEN -> REFACTOR
"""

import pytest
from datetime import date, time
from app.engines.thai_astrology import (
    calculate_thai_astrology,
    ThaiAstrologyResult,
    PlanetPosition,
    HouseDetail,
    LagnaInfo,
    ThaiPlanet,
    ZodiacSign,
    AstrologicalHouse,
    PlanetaryDignity,
    calculate_lahiri_ayanamsa,
    get_province_coordinates,
    extract_lucky_astrology_digits,
    determine_planetary_dignity,
    calculate_lagna_sidereal,
)


def test_data_models_and_enums():
    """Verify Enums and Data Models are defined correctly."""
    assert ThaiPlanet.SUN == 1
    assert ThaiPlanet.MOON == 2
    assert ThaiPlanet.MARS == 3
    assert ThaiPlanet.MERCURY == 4
    assert ThaiPlanet.JUPITER == 5
    assert ThaiPlanet.VENUS == 6
    assert ThaiPlanet.SATURN == 7
    assert ThaiPlanet.RAHU == 8
    assert ThaiPlanet.KETU == 9
    assert ThaiPlanet.URANUS == 0

    assert AstrologicalHouse.TANU == 1
    assert AstrologicalHouse.LABHA == 11
    assert AstrologicalHouse.VINASA == 12

    assert PlanetaryDignity.KASET == "เกษตร"
    assert PlanetaryDignity.UCC == "อุจจ์"
    assert PlanetaryDignity.NIT == "นิจ"
    assert PlanetaryDignity.PRA == "ประ"
    assert PlanetaryDignity.NORMAL == "ปกติ"


def test_calculate_thai_astrology_valid_input():
    """Test standard public seam calculation with valid date, time, province."""
    res = calculate_thai_astrology("1995-08-15", "14:30", "กรุงเทพมหานคร")
    assert isinstance(res, ThaiAstrologyResult)

    # Check Lagna Info
    assert isinstance(res.lagna, LagnaInfo)
    assert 0.0 <= res.lagna.longitude < 360.0
    assert 0 <= res.lagna.rasi_index <= 11
    assert 0.0 <= res.lagna.degree_in_rasi < 30.0

    # Check 10 Planets (0 to 9)
    assert len(res.planets) == 10
    expected_planet_ids = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
    planet_keys = set(res.planets.keys()) if isinstance(res.planets, dict) else {p.planet_id for p in res.planets}
    assert planet_keys == expected_planet_ids

    # Check 12 Houses
    assert len(res.houses) == 12
    house_numbers = [h.house_number for h in res.houses]
    assert house_numbers == list(range(1, 13))
    assert res.houses[0].house_name_th == "ตนุ"
    assert res.houses[11].house_name_th == "วินาศ"

    # Check Lahiri Ayanamsa degree range (in year 1995 it's ~23.8°)
    assert 23.0 <= res.ayanamsa_degree <= 25.0


def test_lagna_and_house_mapping():
    """Test that House 1 (ตนุ) is mapped to Lagna's zodiac sign, and subsequent houses follow in order."""
    res = calculate_thai_astrology("2026-08-05", "08:00", "กรุงเทพมหานคร")
    lagna_sign = res.lagna.rasi_index
    assert res.houses[0].rasi_index == lagna_sign

    for i in range(12):
        expected_sign = (lagna_sign + i) % 12
        assert res.houses[i].rasi_index == expected_sign
        assert res.houses[i].house_number == i + 1


def test_harmonic_charts_d9_d3_math():
    """
    Test Harmonic charts mathematical formulas:
    - D9 Navamsa: floor((sid_deg * 60) / 200) % 12
    - D3 Drekkana: (sign_idx + 4 * decan_idx) % 12
    """
    res = calculate_thai_astrology("2000-01-01", "12:00", "กรุงเทพมหานคร")

    for pid, p in res.planets.items() if isinstance(res.planets, dict) else [(p.planet_id, p) for p in res.planets]:
        sid_deg = p.longitude
        sign_idx = int(sid_deg // 30) % 12
        deg_in_sign = sid_deg % 30.0

        # Navamsa test formula: floor((sid_deg * 60) / 200) % 12
        expected_navamsa = int((sid_deg * 60) // 200) % 12
        assert p.navamsa_rasi_index == expected_navamsa, f"Planet {pid} D9 Navamsa mismatch"

        # Drekkana test formula: (sign_idx + 4 * decan_idx) % 12
        decan_idx = int(deg_in_sign // 10.0)
        expected_drekkana = (sign_idx + 4 * decan_idx) % 12
        assert p.drekkana_rasi_index == expected_drekkana, f"Planet {pid} D3 Drekkana mismatch"


def test_lahiri_ayanamsa_subtraction():
    """Test Lahiri Ayanamsa subtraction formula: (tropical_deg - ayanamsa) % 360."""
    jd_j2000 = 2451545.0  # Jan 1, 2000 12:00 UT
    ayanamsa = calculate_lahiri_ayanamsa(jd_j2000)
    assert 23.8 <= ayanamsa <= 23.9

    tropical_deg = 100.0
    sidereal_deg = (tropical_deg - ayanamsa) % 360.0
    assert abs(sidereal_deg - (100.0 - ayanamsa)) < 1e-5


def test_edge_cases_and_defaults():
    """Test edge cases: missing birth time, unknown province, invalid dates."""
    # Default time "12:00"
    res_default_time = calculate_thai_astrology("1990-05-20")
    assert isinstance(res_default_time, ThaiAstrologyResult)

    # Unknown province -> Fallback to Bangkok
    lat_bkk, lon_bkk = get_province_coordinates("กรุงเทพมหานคร")
    lat_unknown, lon_unknown = get_province_coordinates("จังหวัดสมมติที่ไม่เคยมียู๋จริง")
    assert (lat_bkk, lon_bkk) == (lat_unknown, lon_unknown)

    # Invalid date string -> raises ValueError
    with pytest.raises(ValueError, match="Invalid birth date"):
        calculate_thai_astrology("invalid-date-format")


def test_lucky_digits_extraction():
    """Test lucky digits extraction fields and structure."""
    res = calculate_thai_astrology("1998-12-31", "18:45", "เชียงใหม่")
    
    assert res.primary_lucky_planet in range(10)
    assert res.secondary_lucky_planet in range(10)
    assert isinstance(res.house_lord_digits, list)
    assert isinstance(res.lucky_numbers, list)
    assert len(res.lucky_numbers) >= 3

    # All extracted lucky numbers must be single digits 0-9
    for num in res.lucky_numbers:
        assert 0 <= num <= 9

    # Verify extract_lucky_astrology_digits pure function output
    extracted = extract_lucky_astrology_digits(res)
    assert isinstance(extracted, list)
    assert len(extracted) > 0
    for num in extracted:
        assert 0 <= num <= 9


def test_ground_truth_lagna_and_planetary_benchmark():
    """
    Ground-truth benchmark test:
    Verifies Lagna calculations against known astronomical positions:
    1. 1990-01-01 12:00 in Bangkok -> Lagna must be in Pisces (มีน, rasi_index=11), NOT Virgo 180° opposite.
    2. 2026-08-05 06:00 (Sunrise in Bangkok) -> Lagna must be in Cancer (กรกฎ, rasi_index=3), matching Sun's sign at sunrise.
    """
    # 1. 1990-01-01 12:00 Bangkok
    res_1990 = calculate_thai_astrology("1990-01-01", "12:00", "กรุงเทพมหานคร")
    assert res_1990.lagna.rasi_index == 11, f"Expected Pisces (11), got {res_1990.lagna.rasi_index} ({res_1990.lagna.rasi_name_th})"
    assert res_1990.lagna.rasi_name_th == "มีน"
    assert 330.0 <= res_1990.lagna.longitude < 360.0

    # 2. 2026-08-05 06:00 Bangkok (Sunrise)
    res_sunrise = calculate_thai_astrology("2026-08-05", "06:00", "กรุงเทพมหานคร")
    sun_sign = res_sunrise.planets[1].rasi_index
    lagna_sign = res_sunrise.lagna.rasi_index
    assert sun_sign == 3, f"Expected Sun in Cancer (3), got {sun_sign}"
    assert lagna_sign == sun_sign, f"At sunrise, Lagna ({lagna_sign}) must equal Sun sign ({sun_sign})"


def test_mercury_in_virgo_dignity_precedence():
    """
    Verify planetary dignity precedence:
    Mercury in Virgo (sign_index 5) is both Exalted (Ucc) and Own sign (Kaset).
    Exalted status (Ucc) MUST take precedence over Kaset.
    """
    mercury_id = 4
    virgo_index = 5
    gemini_index = 2

    # Mercury in Virgo -> UCC
    dignity_virgo = determine_planetary_dignity(mercury_id, virgo_index)
    assert dignity_virgo == PlanetaryDignity.UCC, f"Expected UCC for Mercury in Virgo, got {dignity_virgo}"

    # Mercury in Gemini -> KASET
    dignity_gemini = determine_planetary_dignity(mercury_id, gemini_index)
    assert dignity_gemini == PlanetaryDignity.KASET, f"Expected KASET for Mercury in Gemini, got {dignity_gemini}"

    # Sun in Aries -> UCC
    assert determine_planetary_dignity(1, 0) == PlanetaryDignity.UCC


def test_gmst_no_double_counting():
    """
    Verify GMST sidereal time calculation does not double-count UT hours drift:
    LST rate of change per 1 UT hour must equal ~15.041068 degrees (1.00273790935 * 15°).
    """
    jd_base = 2451545.5  # Jan 1, 2000 0h UT
    ayanamsa = 23.85305556
    lat = 13.7563
    lon = 100.5018

    # Lagna at 0h UT
    lagna_0h = calculate_lagna_sidereal(jd_base, 0.0, lat, lon, ayanamsa)
    # Lagna at 1h UT
    lagna_1h = calculate_lagna_sidereal(jd_base + (1.0 / 24.0), 1.0, lat, lon, ayanamsa)

    # Shift over 1 hour in longitude
    diff = (lagna_1h - lagna_0h) % 360.0
    # Expected ascendant shift is around 14° to 16° depending on obliquity and latitude,
    # but exact GMST shift component used internally is 1.00273790935 * 15 = 15.041068°
    assert 13.0 <= diff <= 17.0

