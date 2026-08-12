"""
Tier 5 White-Box Frontend Integration & Adversarial Test Suite.
Target: omni_oracle_app/e2e_tests/test_tier5_frontend_integration_adversarial.py
Scope: Frontend state contracts, Tarot selection boundaries, birth_time formatting & 6am cutoff,
       Heat Index rendering parity, Transparency origin tracking, API payload alias edge cases,
       and cross-module failure isolation.
"""

import json
import pytest
from app import app as flask_app
from app.engines.thai_astrology import calculate_thai_lunar_calendar
from app.engines.tarot import TarotEngine
from app.engines.lottery_stats import LotteryStatsEngine
from app.engines.number_recommender import NumberRecommender


# =====================================================================
# SECTION 1: Tarot Card Deck & Selection State Adversarial Tests (R2)
# =====================================================================

def test_t5_tarot_selection_state_toggle_and_bounds(app_client):
    """T5-01: Verify Tarot card selection index boundaries and rejected out-of-range indices."""
    # Out of range index 78 (deck size is 78: indices 0..77)
    payload_high = {
        "full_name": "Test User",
        "birth_date": "1995-08-15",
        "birth_time": "06:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 78]
    }
    res = app_client.post("/api/divine", json=payload_high)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "out of valid range" in data["message"]

    # Negative index -1
    payload_neg = {
        "full_name": "Test User",
        "birth_date": "1995-08-15",
        "birth_time": "06:00",
        "selected_tarot_cards": [-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res_neg = app_client.post("/api/divine", json=payload_neg)
    assert res_neg.status_code == 400
    assert "out of valid range" in res_neg.get_json()["message"]


def test_t5_tarot_duplicate_indices_rejection(app_client):
    """T5-02: Duplicate card indices in selected_tarot_cards array are rejected with HTTP 400."""
    payload_dup = {
        "full_name": "Test User",
        "birth_date": "1995-08-15",
        "birth_time": "06:00",
        "selected_tarot_cards": [5, 5, 12, 18, 25, 30, 42, 50, 61, 75]
    }
    res = app_client.post("/api/divine", json=payload_dup)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"
    assert "Duplicate card index" in data["message"]


def test_t5_tarot_count_validation_boundaries(app_client):
    """T5-03: Selection array containing <10 or >10 items is rejected with HTTP 400."""
    # 9 cards (under min 10)
    payload_under = {
        "full_name": "Test User",
        "birth_date": "1995-08-15",
        "birth_time": "06:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8]
    }
    res = app_client.post("/api/divine", json=payload_under)
    assert res.status_code == 400
    assert "exactly 10 card indices" in res.get_json()["message"]

    # 11 cards (over max 10)
    payload_over = {
        "full_name": "Test User",
        "birth_date": "1995-08-15",
        "birth_time": "06:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    res_over = app_client.post("/api/divine", json=payload_over)
    assert res_over.status_code == 400
    assert "exactly 10 card indices" in res_over.get_json()["message"]


def test_t5_tarot_non_integer_type_rejection(app_client):
    """T5-04: Non-integer elements (floats, strings, booleans, None) in tarot cards array are rejected."""
    payload_float = {
        "full_name": "Test User",
        "birth_date": "1995-08-15",
        "birth_time": "06:00",
        "selected_tarot_cards": [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = app_client.post("/api/divine", json=payload_float)
    assert res.status_code == 400
    assert "must be an integer" in res.get_json()["message"]

    payload_bool = {
        "full_name": "Test User",
        "birth_date": "1995-08-15",
        "birth_time": "06:00",
        "selected_tarot_cards": [True, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res_bool = app_client.post("/api/divine", json=payload_bool)
    assert res_bool.status_code == 400
    assert "must be an integer" in res_bool.get_json()["message"]


# =====================================================================
# SECTION 2: birth_time Formatting & Thai Lunar Cutoff Rule (R1)
# =====================================================================

def test_t5_birth_time_exact_cutoff_boundaries(app_client):
    """T5-05: Test 05:59:59 (cutoff: True) vs 06:00:00 (cutoff: False) boundary transition."""
    # 05:59 -> Cutoff applied
    payload_before = {
        "full_name": "Test User",
        "birth_date": "1995-08-15",
        "birth_time": "05:59",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res_before = app_client.post("/api/divine", json=payload_before)
    assert res_before.status_code == 200
    assert res_before.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is True

    # 06:00 -> Cutoff NOT applied
    payload_at = {
        "full_name": "Test User",
        "birth_date": "1995-08-15",
        "birth_time": "06:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res_at = app_client.post("/api/divine", json=payload_at)
    assert res_at.status_code == 200
    assert res_at.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is False


def test_t5_birth_time_extreme_clock_boundaries(app_client):
    """T5-06: Midnight (00:00) vs Late Night (23:59) cutoff behavior."""
    # Midnight 00:00 -> cutoff applied
    res_midnight = app_client.post("/api/divine", json={
        "birth_date": "1995-08-15",
        "birth_time": "00:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    })
    assert res_midnight.status_code == 200
    assert res_midnight.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is True

    # 23:59 -> cutoff NOT applied
    res_late = app_client.post("/api/divine", json={
        "birth_date": "1995-08-15",
        "birth_time": "23:59",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    })
    assert res_late.status_code == 200
    assert res_late.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is False


def test_t5_birth_time_whitespace_and_seconds_formatting(app_client):
    """T5-07: birth_time with leading/trailing whitespace (" 05:30 ") or seconds ("05:30:00")."""
    res_space = app_client.post("/api/divine", json={
        "birth_date": "1995-08-15",
        "birth_time": "  05:30  ",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    })
    assert res_space.status_code == 200
    assert res_space.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is True

    res_sec = app_client.post("/api/divine", json={
        "birth_date": "1995-08-15",
        "birth_time": "05:30:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    })
    assert res_sec.status_code == 200
    assert res_sec.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is True


def test_t5_birth_time_invalid_format_rejection(app_client):
    """T5-08: Out-of-range or malformed birth_time strings are rejected with HTTP 400."""
    invalid_times = ["25:00", "-01:00", "12:60", "invalid_time", "99:99"]
    for t in invalid_times:
        res = app_client.post("/api/divine", json={
            "birth_date": "1995-08-15",
            "birth_time": t,
            "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        })
        assert res.status_code == 400, f"Expected 400 for birth_time '{t}', got {res.status_code}"
        assert res.get_json()["status"] == "error"


# =====================================================================
# SECTION 3: Heat Index Badge & Historical Backtesting Parity (R3)
# =====================================================================

def test_t5_heat_index_structure_and_level_parity(app_client, valid_divine_payload):
    """T5-09: Heat index returns two_digit, three_digit, and six_digit arrays with win_count & level."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "heat_index" in data
    heat = data["heat_index"]

    for category in ["two_digit", "three_digit", "six_digit"]:
        assert category in heat
        assert isinstance(heat[category], list)
        assert len(heat[category]) > 0
        for item in heat[category]:
            assert "number" in item
            assert "win_count" in item
            assert "level" in item
            assert item["level"] in ["HOT", "WARM", "COLD"]
            assert isinstance(item["win_count"], int)
            assert item["win_count"] >= 0


def test_t5_heat_index_classification_logic():
    """T5-10: Verify Heat Index threshold rules: win_count >= 3 -> HOT, 1..2 -> WARM, 0 -> COLD."""
    stats_engine = LotteryStatsEngine()
    
    test_lucky_numbers = {
        "two_digit": ["50", "85", "99"],  # 50 and 85 exist in past draws
        "three_digit": ["485", "000"],
        "six_digit": ["123456"]
    }
    heat_idx = stats_engine.evaluate_heat_index(test_lucky_numbers)

    for category in ["two_digit", "three_digit", "six_digit"]:
        for item in heat_idx[category]:
            win_count = item["win_count"]
            level = item["level"]
            if win_count >= 3:
                assert level == "HOT"
            elif win_count >= 1:
                assert level == "WARM"
            else:
                assert level == "COLD"


# =====================================================================
# SECTION 4: Divination Transparency Origin Tracking (R4)
# =====================================================================

def test_t5_transparency_origins_key_parity(app_client, valid_divine_payload):
    """T5-11: Every recommended lucky number across 2-digit, 3-digit, 6-digit has a number_origins entry."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    
    lucky_nums = data["lucky_numbers"]
    origins = data["number_origins"]

    all_nums = (
        lucky_nums.get("two_digit", []) +
        lucky_nums.get("three_digit", []) +
        lucky_nums.get("six_digit", [])
    )

    for num in all_nums:
        num_str = str(num)
        assert num_str in origins, f"Missing origin provenance for recommended number '{num_str}'"
        assert isinstance(origins[num_str], list)
        assert len(origins[num_str]) > 0
        for source_tag in origins[num_str]:
            assert isinstance(source_tag, str)
            assert len(source_tag) > 0


def test_t5_transparency_origin_engine_sources(app_client, valid_divine_payload):
    """T5-12: Provenance strings reference specific engine names (Mahabote, Thai Astrology, Tarot, Numerology)."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    origins = data["number_origins"]

    # Combine all origin strings into a single text block
    combined_origins = " ".join([tag for origin_list in origins.values() for tag in origin_list])
    
    # Verify core engine terms are represented
    assert "Mahabote" in combined_origins or "Lagna" in combined_origins
    assert "Tarot" in combined_origins or "Synthesis" in combined_origins


# =====================================================================
# SECTION 5: API Payload Edge Cases & Cross-Module Boundaries
# =====================================================================

def test_t5_api_payload_alias_fallback_support(app_client):
    """T5-13: Endpoint accepts selected_cards alias key as fallback for selected_tarot_cards."""
    payload_alias = {
        "full_name": "Somchai Jaidee",
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "selected_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
    }
    res = app_client.post("/api/divine", json=payload_alias)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["tarot_reading"]["spread"]) == 10


def test_t5_api_response_dual_key_contract_parity(app_client, valid_divine_payload):
    """T5-14: Response contains both primary and legacy key mappings (lucky_numbers vs recommended_lottery_numbers)."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()

    # Primary keys
    assert "lucky_numbers" in data
    assert "two_digit" in data["lucky_numbers"]
    assert "three_digit" in data["lucky_numbers"]
    assert "six_digit" in data["lucky_numbers"]

    # Alias / legacy compatibility keys
    assert "recommended_lottery_numbers" in data
    rec_legacy = data["recommended_lottery_numbers"]
    assert "two_digits" in rec_legacy
    assert "three_digits" in rec_legacy
    assert "six_digits" in rec_legacy

    # Parity check
    assert data["lucky_numbers"]["two_digit"] == rec_legacy["two_digits"]
    assert data["lucky_numbers"]["three_digit"] == rec_legacy["three_digits"]
    assert data["lucky_numbers"]["six_digit"] == rec_legacy["six_digits"]


def test_t5_sequential_isolation_and_idempotency(app_client, valid_divine_payload):
    """T5-15: Consecutive requests with identical payloads produce consistent deterministic core calculations."""
    res1 = app_client.post("/api/divine", json=valid_divine_payload)
    res2 = app_client.post("/api/divine", json=valid_divine_payload)

    assert res1.status_code == 200
    assert res2.status_code == 200

    data1 = res1.get_json()
    data2 = res2.get_json()

    # Lunar calendar calculations must be strictly identical
    assert data1["chart"]["lunar_calendar"] == data2["chart"]["lunar_calendar"]
    # Mahabote and astrology results must match
    assert data1["mahabote"] == data2["mahabote"]
    assert data1["astrology"] == data2["astrology"]


def test_t5_health_and_stats_endpoints(app_client):
    """T5-16: GET /api/health and GET /api/lottery/stats respond with valid contract JSON."""
    res_health = app_client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.get_json()["status"] == "ok"

    res_stats = app_client.get("/api/lottery/stats")
    assert res_stats.status_code == 200
    stats_data = res_stats.get_json()
    assert "hot_numbers" in stats_data
    assert "cold_numbers" in stats_data
    assert "total_draws" in stats_data
    assert stats_data["total_draws"] == 24
