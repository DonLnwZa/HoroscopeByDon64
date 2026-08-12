"""
Integration & Unit Tests for Milestone M1 Backend Requirements (R1, R2, R3, R4, POST /api/divine)
File: omni_oracle_app/backend/tests/test_api_divine.py
"""

import pytest
from main import app
from app.engines.thai_astrology import calculate_thai_lunar_calendar, ThaiLunarCalendarResult
from app.engines.tarot import TarotEngine
from app.engines.lottery_stats import LotteryStatsEngine
from app.engines.number_recommender import NumberRecommender


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# =====================================================================
# R1: THAI LUNAR CALENDAR TESTS
# =====================================================================

def test_r1_lunar_calendar_before_6am_cutoff():
    """Verify 06:00 AM cutoff shifts day of week back 1 day (1992-05-15 05:30 -> Thursday May 14)."""
    res = calculate_thai_lunar_calendar(birth_date="1992-05-15", birth_time="05:30")
    assert isinstance(res, ThaiLunarCalendarResult)
    assert res.cutoff_applied is True
    assert res.day_of_week == "Thursday"
    assert res.lunar_month == 6
    assert res.zodiac_year == "Monkey"


def test_r1_lunar_calendar_after_6am_no_cutoff():
    """Verify birth_time after 06:00 AM does not trigger cutoff (1992-05-15 08:30 -> Friday)."""
    res = calculate_thai_lunar_calendar(birth_date="1992-05-15", birth_time="08:30")
    assert res.cutoff_applied is False
    assert res.day_of_week == "Friday"
    assert res.lunar_month == 6
    assert res.zodiac_year == "Monkey"


def test_r1_lunar_calendar_exact_6am_boundary():
    """Verify 06:00 AM exact boundary does not apply cutoff."""
    res = calculate_thai_lunar_calendar(birth_date="1992-05-15", birth_time="06:00")
    assert res.cutoff_applied is False
    assert res.day_of_week == "Friday"


def test_r1_lunar_calendar_invalid_inputs():
    """Verify invalid date/time inputs raise ValueError."""
    with pytest.raises(ValueError, match="Invalid birth_date"):
        calculate_thai_lunar_calendar(birth_date="invalid-date", birth_time="12:00")

    with pytest.raises(ValueError, match="Invalid birth_time"):
        calculate_thai_lunar_calendar(birth_date="1990-01-01", birth_time="25:00")


# =====================================================================
# R2: INTERACTIVE TAROT SELECTION TESTS
# =====================================================================

def test_r2_tarot_valid_selection():
    """Verify passing 10 unique card indices maps to Celtic Cross positions."""
    engine = TarotEngine()
    selection = [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
    spread = engine.draw_celtic_cross(selected_cards=selection)
    
    assert len(spread) == 10
    drawn_indices = [card['card_index'] for card in spread]
    assert drawn_indices == selection
    assert spread[0]['position_meaning'] == "สถานการณ์ปัจจุบัน"
    assert spread[9]['position_meaning'] == "บทสรุปของสถานการณ์"


def test_r2_tarot_invalid_length():
    """Verify passing less than 10 cards raises ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="exactly 10 card indices"):
        engine.draw_celtic_cross(selected_cards=[0, 1, 2])


def test_r2_tarot_out_of_range():
    """Verify passing card index > 77 raises ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="out of valid range"):
        engine.draw_celtic_cross(selected_cards=[0, 1, 2, 3, 4, 5, 6, 7, 8, 88])


def test_r2_tarot_duplicate_selection():
    """Verify duplicate card indices raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="Duplicate card index"):
        engine.draw_celtic_cross(selected_cards=[5, 5, 12, 15, 20, 25, 30, 35, 40, 45])


def test_r2_tarot_default_fallback():
    """Verify selected_cards=None falls back to 10 random unique cards."""
    engine = TarotEngine()
    spread = engine.draw_celtic_cross(selected_cards=None)
    assert len(spread) == 10
    card_ids = [c['id'] for c in spread]
    assert len(set(card_ids)) == 10


# =====================================================================
# R3: HEAT INDEX BACKTESTING TESTS
# =====================================================================

def test_r3_heat_index_evaluation():
    """Verify evaluate_heat_index computes win counts and levels (HOT, WARM, COLD)."""
    stats = LotteryStatsEngine()
    rec_nums = {
        "two_digit": ["50", "99"],
        "three_digit": ["142", "999"],
        "six_digit": ["811852", "000000"]
    }
    heat_index = stats.evaluate_heat_index(rec_nums)
    
    assert "two_digit" in heat_index
    assert "three_digit" in heat_index
    assert "six_digit" in heat_index

    two_digit_entries = heat_index["two_digit"]
    assert len(two_digit_entries) == 2
    for entry in two_digit_entries:
        assert "number" in entry
        assert "win_count" in entry
        assert entry["level"] in ["HOT", "WARM", "COLD"]
        if entry["win_count"] >= 2:
            assert entry["level"] == "HOT"
        elif entry["win_count"] == 1:
            assert entry["level"] == "WARM"
        else:
            assert entry["level"] == "COLD"


# =====================================================================
# R4: DIVINATION TRANSPARENCY PROVENANCE TESTS
# =====================================================================

def test_r4_number_origins():
    """Verify number_origins mapping provides engine source details for every number."""
    stats = LotteryStatsEngine()
    rec = NumberRecommender(stats)
    
    num_res = {"primary_lucky_digits": [4, 8]}
    mah_res = {"positions": {"thanang": {"planet_digit": 1}, "phoka": {"planet_digit": 5}}}
    ast_res = {"primary_lucky_planet": 1, "secondary_lucky_planet": 5}
    tarot_res = [{"name": "The Magician", "card_index": 1}, {}, {"name": "The Empress", "card_index": 3}]

    lucky_numbers, origins = rec.generate_recommendations(num_res, mah_res, ast_res, tarot_res)
    
    all_nums = lucky_numbers["two_digit"] + lucky_numbers["three_digit"] + lucky_numbers["six_digit"]
    for num in all_nums:
        assert num in origins
        assert isinstance(origins[num], list)
        assert len(origins[num]) > 0


# =====================================================================
# FLASK API /api/divine CONTRACT INTEGRATION TESTS
# =====================================================================

def test_api_divine_full_contract_success(client):
    """Verify POST /api/divine responds matching exact PROJECT.md JSON interface contract."""
    payload = {
        "full_name": "Somchai Jaidee",
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "birth_province": "Bangkok",
        "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
    }
    
    res = client.post('/api/divine', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    
    assert data["status"] == "success"
    assert "chart" in data
    assert data["chart"]["birth_date"] == "1992-05-15"
    assert data["chart"]["birth_time"] == "05:30"
    
    lunar = data["chart"]["lunar_calendar"]
    assert lunar["day_of_week"] == "Thursday"
    assert lunar["lunar_month"] == 6
    assert lunar["zodiac_year"] == "Monkey"
    assert lunar["cutoff_applied"] is True

    assert "tarot_reading" in data
    assert len(data["tarot_reading"]["spread"]) == 10
    
    assert "lucky_numbers" in data
    assert "two_digit" in data["lucky_numbers"]
    assert "three_digit" in data["lucky_numbers"]
    assert "six_digit" in data["lucky_numbers"]

    assert "heat_index" in data
    assert "two_digit" in data["heat_index"]

    assert "number_origins" in data
    for num_category in data["lucky_numbers"].values():
        for num in num_category:
            assert num in data["number_origins"]

    assert "synthesis" in data
    assert "disclaimer" in data


def test_api_divine_invalid_tarot_selection(client):
    """Verify POST /api/divine rejects invalid tarot selection with 400 Bad Request."""
    payload = {
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "selected_tarot_cards": [0, 1, 2]
    }
    res = client.post('/api/divine', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"


def test_api_divine_backward_compatibility(client):
    """Verify POST /api/divine handles empty payload gracefully with default parameters."""
    res = client.post('/api/divine', json={})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "chart" in data
    assert "heat_index" in data
    assert "number_origins" in data
