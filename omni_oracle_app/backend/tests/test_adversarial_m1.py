"""
Adversarial Stress-Test Suite for Milestone M1 (R1 & R2 Backend Requirements)
File: omni_oracle_app/backend/tests/test_adversarial_m1.py
"""

import pytest
from main import app
from app.engines.thai_astrology import calculate_thai_lunar_calendar, ThaiLunarCalendarResult
from app.engines.tarot import TarotEngine


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# =====================================================================
# R1 ADVERSARIAL BOUNDARY TESTS: THAI LUNAR CALENDAR & 6AM CUTOFF
# =====================================================================

def test_r1_boundary_05_59_59_triggers_cutoff():
    """Birth time 05:59:59 must trigger 6am cutoff (effective date rolls back 1 day)."""
    res = calculate_thai_lunar_calendar(birth_date="2026-08-12", birth_time="05:59:59")
    assert isinstance(res, ThaiLunarCalendarResult)
    assert res.cutoff_applied is True
    # 2026-08-12 is Wednesday. With cutoff (2026-08-11), it becomes Tuesday.
    assert res.day_of_week == "Tuesday"


def test_r1_boundary_06_00_00_no_cutoff():
    """Birth time 06:00:00 exact boundary must NOT trigger cutoff."""
    res = calculate_thai_lunar_calendar(birth_date="2026-08-12", birth_time="06:00:00")
    assert res.cutoff_applied is False
    assert res.day_of_week == "Wednesday"


def test_r1_boundary_00_00_triggers_cutoff():
    """Birth time 00:00 (midnight) must trigger cutoff."""
    res = calculate_thai_lunar_calendar(birth_date="2026-08-12", birth_time="00:00")
    assert res.cutoff_applied is True
    assert res.day_of_week == "Tuesday"


def test_r1_boundary_23_59_no_cutoff():
    """Birth time 23:59 (late night) must NOT trigger cutoff."""
    res = calculate_thai_lunar_calendar(birth_date="2026-08-12", birth_time="23:59")
    assert res.cutoff_applied is False
    assert res.day_of_week == "Wednesday"


def test_r1_boundary_05_59_triggers_cutoff():
    """Birth time 05:59 (1 min before 6am) must trigger cutoff."""
    res = calculate_thai_lunar_calendar(birth_date="2026-08-12", birth_time="05:59")
    assert res.cutoff_applied is True
    assert res.day_of_week == "Tuesday"


def test_r1_boundary_06_00_no_cutoff():
    """Birth time 06:00 (exact 6am) must NOT trigger cutoff."""
    res = calculate_thai_lunar_calendar(birth_date="2026-08-12", birth_time="06:00")
    assert res.cutoff_applied is False
    assert res.day_of_week == "Wednesday"


def test_r1_invalid_time_formats():
    """Test out-of-bounds and malformed time inputs."""
    with pytest.raises(ValueError, match="Time values out of range"):
        calculate_thai_lunar_calendar("2026-08-12", "25:00")

    with pytest.raises(ValueError, match="Time values out of range"):
        calculate_thai_lunar_calendar("2026-08-12", "12:60")

    with pytest.raises(ValueError, match="Time values out of range"):
        calculate_thai_lunar_calendar("2026-08-12", "-01:00")

    with pytest.raises(ValueError, match="Expected format HH:MM"):
        calculate_thai_lunar_calendar("2026-08-12", "abc:def")


# =====================================================================
# R2 ADVERSARIAL BOUNDARY TESTS: TAROT SELECTION MAPPING & VALIDATION
# =====================================================================

def test_r2_valid_card_indices_0_and_77():
    """Verify lowest (0) and highest (77) valid card indices work correctly."""
    engine = TarotEngine()
    selection = [0, 77, 1, 2, 3, 4, 5, 6, 7, 8]
    spread = engine.draw_celtic_cross(selected_cards=selection)
    assert len(spread) == 10
    assert spread[0]['card_index'] == 0
    assert spread[0]['id'] == "major_0"
    assert spread[1]['card_index'] == 77
    assert spread[1]['id'] == "minor_Pentacles_King"


def test_r2_invalid_card_count_9_cards():
    """Passing 9 cards must raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="exactly 10 card indices, got 9"):
        engine.draw_celtic_cross(selected_cards=[0, 1, 2, 3, 4, 5, 6, 7, 8])


def test_r2_invalid_card_count_11_cards():
    """Passing 11 cards must raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="exactly 10 card indices, got 11"):
        engine.draw_celtic_cross(selected_cards=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


def test_r2_duplicate_indices():
    """Passing duplicate card indices (e.g. [0, 0, 1...]) must raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="Duplicate card index 0"):
        engine.draw_celtic_cross(selected_cards=[0, 0, 1, 2, 3, 4, 5, 6, 7, 8])


def test_r2_out_of_range_negative():
    """Negative card index (-1) must raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="out of valid range"):
        engine.draw_celtic_cross(selected_cards=[-1, 0, 1, 2, 3, 4, 5, 6, 7, 8])


def test_r2_out_of_range_upper_bound_78():
    """Card index 78 (out of 0..77 range) must raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="out of valid range"):
        engine.draw_celtic_cross(selected_cards=[78, 0, 1, 2, 3, 4, 5, 6, 7, 8])


def test_r2_out_of_range_100():
    """Card index 100 must raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="out of valid range"):
        engine.draw_celtic_cross(selected_cards=[100, 0, 1, 2, 3, 4, 5, 6, 7, 8])


def test_r2_non_integer_floats():
    """Float card indices must raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="must be an integer"):
        engine.draw_celtic_cross(selected_cards=[0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_r2_non_integer_strings():
    """String card indices must raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="must be an integer"):
        engine.draw_celtic_cross(selected_cards=["0", 1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_r2_boolean_indices_rejected():
    """Boolean card index (True/False) must raise ValueError despite Python bool subclass of int."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="must be an integer"):
        engine.draw_celtic_cross(selected_cards=[True, 1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_r2_non_list_input():
    """Non-list input (e.g. dict or string) must raise ValueError."""
    engine = TarotEngine()
    with pytest.raises(ValueError, match="must be a list of 10 card indices"):
        engine.draw_celtic_cross(selected_cards="invalid")


# =====================================================================
# API ROUTE ADVERSARIAL INTEGRATION TESTS
# =====================================================================

def test_api_divine_rejects_duplicate_tarot(client):
    payload = {
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "selected_tarot_cards": [0, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    }
    res = client.post('/api/divine', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "Duplicate card index" in data["message"]


def test_api_divine_rejects_out_of_range_tarot(client):
    payload = {
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 78]
    }
    res = client.post('/api/divine', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "out of valid range" in data["message"]


def test_api_divine_handles_05_59_59(client):
    payload = {
        "birth_date": "2026-08-12",
        "birth_time": "05:59:59",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = client.post('/api/divine', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["chart"]["lunar_calendar"]["cutoff_applied"] is True
    assert data["chart"]["lunar_calendar"]["day_of_week"] == "Tuesday"


def test_api_divine_handles_06_00_00(client):
    payload = {
        "birth_date": "2026-08-12",
        "birth_time": "06:00:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = client.post('/api/divine', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["chart"]["lunar_calendar"]["cutoff_applied"] is False
    assert data["chart"]["lunar_calendar"]["day_of_week"] == "Wednesday"
