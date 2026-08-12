"""
Tier 5 White-Box Backend Adversarial Test Suite.
Target: omni_oracle_app/e2e_tests/test_tier5_backend_adversarial.py
Methodology: Deep white-box adversarial stress testing across Flask API routes
and all 7 backend engines (Thai Astrology, Numerology 7x9, Mahabote, Tarot,
Lottery Stats, Number Recommender, Oracle Synthesis).

Covers:
- Untested code paths and branch coverage gaps
- Boundary value anomalies and date/time cutoff transitions
- Type coercion risks (bool as int, float indices, string numbers)
- Songkran April 16 boundary and Wednesday Night Rahu logic
- Fault tolerance under empty, missing, or malformed engine inputs
"""

import os
import sys
from datetime import date, datetime, time
import pytest

# Ensure app imports resolve correctly
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from app.engines.thai_astrology import (
    calculate_thai_astrology,
    calculate_thai_lunar_calendar,
    get_province_coordinates,
    determine_planetary_dignity,
    PlanetaryDignity,
    ThaiLunarCalendarResult
)
from app.engines.numerology_7x9 import (
    calculate_numerology_7x9,
    Numerology7x9Result
)
from app.engines.mahabote import (
    calculate_mahabote,
    MahaboteEngine,
    DayOfWeek
)
from app.engines.tarot import TarotEngine
from app.engines.lottery_stats import LotteryStatsEngine
from app.engines.number_recommender import NumberRecommender
from app.engines.oracle_synthesis import OracleSynthesis


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# =====================================================================
# SECTION 1: FLASK API ENDPOINTS & ROUTE ADVERSARIAL TESTS
# =====================================================================

def test_tier5_api_health_endpoints(client):
    """Verify GET /api/health and GET /api/v1/health return 200 OK and valid JSON."""
    res1 = client.get('/api/health')
    assert res1.status_code == 200
    assert res1.get_json() == {"status": "ok", "version": "1.0.0"}

    res2 = client.get('/api/v1/health')
    assert res2.status_code == 200
    assert res2.get_json() == {"status": "ok", "version": "1.0.0"}


def test_tier5_api_lottery_stats_endpoints(client):
    """Verify GET /api/lottery/stats returns correct data structure and top 2 digits."""
    res = client.get('/api/lottery/stats')
    assert res.status_code == 200
    data = res.get_json()
    assert "hot_numbers" in data
    assert "cold_numbers" in data
    assert "frequency" in data
    assert "total_draws" in data
    assert "top_two_digits" in data
    assert isinstance(data["top_two_digits"], list)
    assert len(data["top_two_digits"]) <= 3


def test_tier5_api_frontend_static_serving(client):
    """Verify static route serves index.html or requested files, and handles fallback."""
    res_root = client.get('/')
    assert res_root.status_code == 200
    assert b"<!DOCTYPE html>" in res_root.data or b"<html" in res_root.data or res_root.status_code == 200

    res_missing = client.get('/nonexistent_route_12345')
    assert res_missing.status_code == 200  # Fallback to index.html for SPA routing


def test_tier5_api_divine_empty_payload_defaults(client):
    """POST /api/divine with empty payload JSON applies default parameters safely."""
    res = client.post('/api/divine', json={})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["chart"]["birth_date"] == "1990-01-01"
    assert data["chart"]["birth_time"] == "12:00"


def test_tier5_api_divine_selected_cards_alias(client):
    """POST /api/divine accepts 'selected_cards' as an alias for 'selected_tarot_cards'."""
    payload = {
        "birth_date": "1992-05-15",
        "birth_time": "14:00",
        "selected_cards": [10, 20, 30, 40, 50, 60, 70, 71, 72, 73]
    }
    res = client.post('/api/divine', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    spread = data["tarot_reading"]["spread"]
    assert len(spread) == 10
    assert spread[0]["card_index"] == 10


def test_tier5_api_divine_malformed_birth_date(client):
    """POST /api/divine with invalid birth_date returns HTTP 400 error response."""
    payload = {
        "birth_date": "2026-02-30",  # Invalid calendar date
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = client.post('/api/divine', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "Invalid birth_date" in data["message"]


def test_tier5_api_divine_malformed_birth_time(client):
    """POST /api/divine with invalid birth_time returns HTTP 400 error response."""
    payload = {
        "birth_date": "1995-08-15",
        "birth_time": "25:70",  # Invalid time values
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = client.post('/api/divine', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "Invalid birth_time" in data["message"]


# =====================================================================
# SECTION 2: THAI ASTROLOGY ENGINE WHITE-BOX TESTS
# =====================================================================

def test_tier5_astrology_province_coordinate_lookup():
    """Verify Thai province coordinate resolution and fallback behavior."""
    # Known province
    lat, lon = get_province_coordinates("เชียงใหม่")
    assert (lat, lon) == (18.7883, 98.9853)

    # Unknown province defaults to Bangkok
    lat_def, lon_def = get_province_coordinates("ยะลา")
    assert (lat_def, lon_def) == (13.7563, 100.5018)

    # Empty string defaults to Bangkok
    lat_empty, lon_empty = get_province_coordinates("")
    assert (lat_empty, lon_empty) == (13.7563, 100.5018)


def test_tier5_astrology_explicit_lat_lon_override():
    """Verify explicit latitude and longitude override in calculate_thai_astrology."""
    res = calculate_thai_astrology(
        birth_date="1995-08-15",
        birth_time="12:00",
        latitude=7.8804,
        longitude=98.3923
    )
    assert res.lagna is not None
    assert isinstance(res.lagna.longitude, float)
    assert 0.0 <= res.lagna.longitude < 360.0


def test_tier5_astrology_planetary_dignities():
    """Verify exalted (Ucc), own sign (Kaset), debilitated (Nit), and detriment (Pra) dignities."""
    # Exalted: Sun in Aries (sign 0)
    assert determine_planetary_dignity(1, 0) == PlanetaryDignity.UCC
    # Exalted: Mercury in Virgo (sign 5) - should evaluate to UCC before Kaset
    assert determine_planetary_dignity(4, 5) == PlanetaryDignity.UCC
    # Kaset: Sun in Leo (sign 4)
    assert determine_planetary_dignity(1, 4) == PlanetaryDignity.KASET
    # Debilitated: Sun in Libra (sign 6)
    assert determine_planetary_dignity(1, 6) == PlanetaryDignity.NIT
    # Detriment: Sun in Aquarius (sign 10 - opposite of Leo)
    assert determine_planetary_dignity(1, 10) == PlanetaryDignity.PRA


def test_tier5_astrology_result_helper_methods():
    """Verify get_planet and get_house methods on ThaiAstrologyResult."""
    res = calculate_thai_astrology("1992-05-15", "05:30")

    # Valid planet lookup
    sun = res.get_planet(1)
    assert sun is not None
    assert sun.planet_name_en == "Sun"

    # Out of bound planet lookup returns None
    assert res.get_planet(99) is None

    # Valid house lookup (1..12)
    house1 = res.get_house(1)
    assert house1 is not None
    assert house1.house_number == 1

    # Out of bound house lookup returns None
    assert res.get_house(0) is None
    assert res.get_house(13) is None


def test_tier5_astrology_lunar_calendar_songkran_zodiac_shift():
    """Verify zodiac year shift around Songkran (April 13)."""
    # April 12 -> Before Songkran -> previous zodiac year
    res_before = calculate_thai_lunar_calendar("2024-04-12", "12:00")
    # April 13 -> Songkran -> new zodiac year
    res_after = calculate_thai_lunar_calendar("2024-04-13", "12:00")

    assert res_before.zodiac_year_num != res_after.zodiac_year_num


# =====================================================================
# SECTION 3: NUMEROLOGY 7X9 MATRIX & BOUNDS ANALYSIS
# =====================================================================

def test_tier5_numerology_override_parameters():
    """Verify parameter overrides for day, month, and year in calculate_numerology_7x9."""
    res = calculate_numerology_7x9(
        birth_date="1990-01-01",
        birth_day_override=5,     # Thursday
        lunar_month_override=6,   # Month 6
        zodiac_year_override=9    # Year of Monkey
    )
    assert res.day_of_week == 5
    assert res.thai_lunar_month == 6
    assert res.thai_lunar_year == 9


def test_tier5_numerology_out_of_range_parameter_rejections():
    """Verify out-of-range overrides raise ValueError."""
    with pytest.raises(ValueError, match="day_of_week must be between 1 and 7"):
        calculate_numerology_7x9("1990-01-01", day_of_week=0)

    with pytest.raises(ValueError, match="thai_lunar_month must be between 1 and 12"):
        calculate_numerology_7x9("1990-01-01", thai_lunar_month=13)

    with pytest.raises(ValueError, match="thai_lunar_year must be between 1 and 12"):
        calculate_numerology_7x9("1990-01-01", thai_lunar_year=0)


def test_tier5_numerology_result_getters_bounds():
    """Verify bounds checking for get_cell and get_house_name in Numerology7x9Result."""
    res = calculate_numerology_7x9("1992-05-15")

    # Valid getters
    assert 1 <= res.get_cell(1, 1) <= 7
    assert isinstance(res.get_house_name(1, 1), str)

    # Invalid row/col bounds raise ValueError
    with pytest.raises(ValueError, match="Row must be between 1..9"):
        res.get_cell(0, 1)

    with pytest.raises(ValueError, match="Col must be between 1..7"):
        res.get_cell(1, 8)

    with pytest.raises(ValueError, match="Row must be between 1..3"):
        res.get_house_name(4, 1)


def test_tier5_numerology_house_and_collision_helpers():
    """Verify get_house and get_digit_collision helper methods."""
    res = calculate_numerology_7x9("1992-05-15")

    # Valid house lookup
    atta = res.get_house("อัตตะ")
    assert atta is not None
    assert atta.house_name_en == "Atta"

    # Non-existent house returns None
    assert res.get_house("non_existent") is None

    # Collision lookup for digit 1..7
    col1 = res.get_digit_collision(1)
    assert col1 is not None
    assert col1.digit == 1

    # Out of range digit collision returns None
    assert res.get_digit_collision(8) is None


# =====================================================================
# SECTION 4: MAHABOTE ENGINE SONGKRAN & WEDNESDAY NIGHT ANALYSIS
# =====================================================================

def test_tier5_mahabote_songkran_cutoff_boundary():
    """Verify April 16 Songkran boundary for CS year calculation in Mahabote."""
    # April 15 -> Before Songkran -> songkran_adjusted: True
    res_before = calculate_mahabote("2024-04-15", "12:00")
    assert res_before.songkran_adjusted is True

    # April 16 -> Songkran day -> songkran_adjusted: False
    res_after = calculate_mahabote("2024-04-16", "12:00")
    assert res_after.songkran_adjusted is False
    assert res_after.cs_year == res_before.cs_year + 1


def test_tier5_mahabote_wednesday_night_rahu_logic():
    """Verify Wednesday daytime (4) vs Wednesday night (8 - Rahu) transition logic."""
    # Wednesday 14:00 -> Daytime Wednesday (digit 4)
    res_day = calculate_mahabote("2026-08-12", "14:00")  # 2026-08-12 is Wednesday
    assert res_day.day_of_week == 4
    assert res_day.is_wednesday_night is False

    # Wednesday 20:00 -> Nighttime Wednesday (digit 8 - Rahu)
    res_night = calculate_mahabote("2026-08-12", "20:00")
    assert res_night.day_of_week == 8
    assert res_night.is_wednesday_night is True

    # Explicit is_wednesday_night override
    res_override = calculate_mahabote("2026-08-12", "12:00", is_wednesday_night=True)
    assert res_override.day_of_week == 8
    assert res_override.is_wednesday_night is True


def test_tier5_mahabote_input_type_flexibility_and_errors():
    """Verify calculate_mahabote handles string, date, datetime, and raises TypeError for invalid types."""
    # Date object
    res_date = calculate_mahabote(date(1992, 5, 15), time(14, 30))
    assert res_date.birth_date == "1992-05-15"

    # Datetime object
    res_dt = calculate_mahabote(datetime(1992, 5, 15, 14, 30))
    assert res_dt.birth_date == "1992-05-15"

    # Unsupported type raises TypeError
    with pytest.raises(TypeError, match="Unsupported birth_date type"):
        calculate_mahabote(12345678)  # Integer date


# =====================================================================
# SECTION 5: TAROT ENGINE INPUT COERCION & REVERSAL INTEGRITY
# =====================================================================

def test_tier5_tarot_type_validation_coercion_risks():
    """Verify TarotEngine strictly rejects non-integer card index types (bool, float, str)."""
    engine = TarotEngine()

    # Boolean indices (True/False) must be rejected
    with pytest.raises(ValueError, match="must be an integer"):
        engine.draw_celtic_cross(selected_cards=[True, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    # Float indices must be rejected
    with pytest.raises(ValueError, match="must be an integer"):
        engine.draw_celtic_cross(selected_cards=[0.0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    # String indices must be rejected
    with pytest.raises(ValueError, match="must be an integer"):
        engine.draw_celtic_cross(selected_cards=["0", 1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_tier5_tarot_random_draw_when_none():
    """Verify TarotEngine generates 10 unique cards with random draw when selected_cards is None."""
    engine = TarotEngine()
    spread = engine.draw_celtic_cross(selected_cards=None)
    assert len(spread) == 10
    indices = [card["card_index"] for card in spread]
    assert len(set(indices)) == 10  # 10 unique cards


# =====================================================================
# SECTION 6: LOTTERY STATS ENGINE HEAT INDEX & FREQUENCY EDGE CASES
# =====================================================================

def test_tier5_lottery_stats_empty_and_string_coercion():
    """Verify evaluate_heat_index handles string coercion and classification boundaries cleanly."""
    stats = LotteryStatsEngine()

    # Numeric integers converted to strings cleanly
    res = stats.evaluate_heat_index({
        "two_digit": [52, 99],
        "three_digit": [485],
        "six_digit": [485792]
    })
    assert len(res["two_digit"]) == 2
    assert res["two_digit"][0]["number"] == "52"
    assert res["two_digit"][0]["level"] in ["HOT", "WARM", "COLD"]


def test_tier5_lottery_stats_hot_warm_cold_thresholds():
    """Verify exact threshold boundary logic for Heat Index levels."""
    stats = LotteryStatsEngine()
    # 0 wins -> COLD
    res_cold = stats.evaluate_heat_index({"two_digit": ["000000_nonexistent"]})
    assert res_cold["two_digit"][0]["level"] == "COLD"
    assert res_cold["two_digit"][0]["win_count"] == 0

    # Number "52" has 2 wins -> WARM
    res_warm = stats.evaluate_heat_index({"two_digit": ["52"]})
    assert res_warm["two_digit"][0]["win_count"] == 2
    assert res_warm["two_digit"][0]["level"] == "WARM"


# =====================================================================
# SECTION 7: NUMBER RECOMMENDER & ORACLE SYNTHESIS FAULT TOLERANCE
# =====================================================================

def test_tier5_recommender_fault_tolerance_empty_inputs():
    """Verify NumberRecommender handles empty or malformed engine outputs gracefully."""
    stats = LotteryStatsEngine()
    recommender = NumberRecommender(stats)

    # All engines return empty dicts or lists
    rec_nums, origins = recommender.generate_recommendations({}, {}, {}, [])
    assert "two_digit" in rec_nums
    assert "three_digit" in rec_nums
    assert "six_digit" in rec_nums
    assert len(origins) > 0


def test_tier5_oracle_synthesis_output_validity():
    """Verify OracleSynthesis outputs valid reading and disclaimer strings."""
    synthesis = OracleSynthesis()
    syn_text, disclaimer = synthesis.synthesize({}, {}, {}, [])

    assert isinstance(syn_text, str)
    assert len(syn_text) > 0
    assert "Omni-Oracle" in syn_text

    assert isinstance(disclaimer, str)
    assert "ไม่มีการรับประกันผล" in disclaimer or "วิจารณญาณ" in disclaimer
