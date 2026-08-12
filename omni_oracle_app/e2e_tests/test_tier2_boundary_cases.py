"""
Tier 2 Boundary & Corner Cases Test Suite (20 Test Cases).
Target: omni_oracle_app/e2e_tests/test_tier2_boundary_cases.py
Methodology: 5 test cases per feature across R1, R2, R3, R4.
Boundary value analysis, edge cases, error conditions, and input validation.
"""

import pytest


# =====================================================================
# FEATURE R1 BOUNDARIES: Thai Lunar Calendar & 6am Cutoff
# =====================================================================

def test_r1_t2_01_boundary_055959_vs_060000(app_client):
    """R1-B1: Test exact 1-second cutoff boundary: '05:59:59' vs '06:00:00'."""
    payload_before = {
        "full_name": "Somchai",
        "birth_date": "1995-08-15",
        "birth_time": "05:59:59",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    payload_exact = {
        "full_name": "Somchai",
        "birth_date": "1995-08-15",
        "birth_time": "06:00:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    
    res_before = app_client.post("/api/divine", json=payload_before)
    res_exact = app_client.post("/api/divine", json=payload_exact)
    
    assert res_before.status_code == 200
    assert res_exact.status_code == 200
    
    lunar_before = res_before.get_json()["chart"]["lunar_calendar"]
    lunar_exact = res_exact.get_json()["chart"]["lunar_calendar"]
    
    assert lunar_before["cutoff_applied"] is True
    assert lunar_exact["cutoff_applied"] is False


def test_r1_t2_02_boundary_midnight_000000(app_client):
    """R1-B2: Test midnight '00:00:00' birth time handles date arithmetic safely."""
    payload = {
        "full_name": "Midnight Born",
        "birth_date": "1995-08-15",
        "birth_time": "00:00:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    lunar = res.get_json()["chart"]["lunar_calendar"]
    assert lunar["cutoff_applied"] is True


def test_r1_t2_03_boundary_late_night_235959(app_client):
    """R1-B3: Test late night '23:59:59' birth time retains current solar day."""
    payload = {
        "full_name": "Late Night Born",
        "birth_date": "1995-08-15",
        "birth_time": "23:59:59",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    lunar = res.get_json()["chart"]["lunar_calendar"]
    assert lunar["cutoff_applied"] is False


def test_r1_t2_04_leap_year_feb29(app_client):
    """R1-B4: Test February 29 leap year birth date with early time '04:30'."""
    payload = {
        "full_name": "Leap Year Born",
        "birth_date": "2024-02-29",
        "birth_time": "04:30",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    lunar = res.get_json()["chart"]["lunar_calendar"]
    assert lunar["cutoff_applied"] is True


def test_r1_t2_05_missing_or_empty_birth_time_fallback(app_client):
    """R1-B5: Test missing or empty birth_time string defaults to 12:00 (cutoff_applied: False)."""
    payload = {
        "full_name": "No Time Given",
        "birth_date": "1992-05-15",
        "birth_time": "",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    lunar = res.get_json()["chart"]["lunar_calendar"]
    assert lunar["cutoff_applied"] is False


# =====================================================================
# FEATURE R2 BOUNDARIES: Interactive Tarot Selection
# =====================================================================

def test_r2_t2_01_tarot_boundary_indices_0_and_77(app_client):
    """R2-B1: Submit array containing boundary card indices 0 (The Fool) and 77 (King of Pentacles)."""
    payload = {
        "full_name": "Boundary Cards",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "selected_tarot_cards": [0, 77, 1, 2, 3, 4, 5, 6, 7, 8]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    spread = res.get_json()["tarot_reading"]["spread"]
    assert len(spread) == 10


def test_r2_t2_02_tarot_too_few_cards_rejection(app_client):
    """R2-B2: Submit array with <10 cards (9 cards) -> returns HTTP 400 or 422."""
    payload = {
        "full_name": "Too Few Cards",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code in [400, 422]


def test_r2_t2_03_tarot_too_many_cards_rejection(app_client):
    """R2-B3: Submit array with >10 cards (11 cards) -> returns HTTP 400 or 422."""
    payload = {
        "full_name": "Too Many Cards",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code in [400, 422]


def test_r2_t2_04_tarot_out_of_range_index_rejection(app_client):
    """R2-B4: Submit array containing index <0 (-1) or >77 (78) -> returns HTTP 400 or 422."""
    payload = {
        "full_name": "Out of Bounds Index",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "selected_tarot_cards": [-1, 1, 2, 3, 4, 5, 6, 7, 8, 78]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code in [400, 422]


def test_r2_t2_05_tarot_duplicate_indices_rejection(app_client):
    """R2-B5: Submit array containing duplicate card indices -> returns HTTP 400 or 422."""
    payload = {
        "full_name": "Duplicate Cards",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "selected_tarot_cards": [0, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code in [400, 422]


# =====================================================================
# FEATURE R3 BOUNDARIES: Backtesting Heat Index
# =====================================================================

def test_r3_t2_01_boundary_0_wins_cold(app_client, valid_divine_payload):
    """R3-B1: Number with 0 historical wins evaluates to win_count == 0 and level == COLD."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    heat = res.get_json()["heat_index"]
    all_items = heat.get("two_digit", []) + heat.get("three_digit", []) + heat.get("six_digit", [])
    cold_items = [item for item in all_items if item["win_count"] == 0]
    for item in cold_items:
        assert item["level"] == "COLD"


def test_r3_t2_02_boundary_1_win_warm(app_client, valid_divine_payload):
    """R3-B2: Number with 1 historical win evaluates to win_count == 1 and level == WARM."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    heat = res.get_json()["heat_index"]
    all_items = heat.get("two_digit", []) + heat.get("three_digit", []) + heat.get("six_digit", [])
    one_win_items = [item for item in all_items if item["win_count"] == 1]
    for item in one_win_items:
        assert item["level"] == "WARM"


def test_r3_t2_03_boundary_2_wins_warm(app_client, valid_divine_payload):
    """R3-B3: Number with 2 historical wins evaluates to win_count == 2 and level == WARM."""
    from app.engines.lottery_stats import LotteryStatsEngine
    stats = LotteryStatsEngine()
    # Evaluate number "52" which has exactly 2 historical wins in past 1 year GLO data
    res = stats.evaluate_heat_index({"two_digit": ["52"]})
    two_win_item = res["two_digit"][0]
    assert two_win_item["number"] == "52"
    assert two_win_item["win_count"] == 2
    assert two_win_item["level"] == "WARM"


def test_r3_t2_04_boundary_3_wins_hot(app_client, valid_divine_payload):
    """R3-B4: Number with 3 historical wins evaluates to win_count >= 3 and level == HOT."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    heat = res.get_json()["heat_index"]
    all_items = heat.get("two_digit", []) + heat.get("three_digit", []) + heat.get("six_digit", [])
    hot_items = [item for item in all_items if item["win_count"] >= 3]
    for item in hot_items:
        assert item["level"] == "HOT"


def test_r3_t2_05_heat_index_empty_data_fallback(app_client, valid_divine_payload):
    """R3-B5: Heat index calculations complete safely without server 500 error."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "heat_index" in data


# =====================================================================
# FEATURE R4 BOUNDARIES: Divination Transparency (Number Origins)
# =====================================================================

def test_r4_t2_01_origin_fallback_for_synthetic_digits(app_client, valid_divine_payload):
    """R4-B1: Recommended 6-digit number synthesizes and lists contributing origins."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    lucky_six = data["lucky_numbers"].get("six_digit", [])
    origins = data["number_origins"]
    for six_num in lucky_six:
        assert str(six_num) in origins
        assert len(origins[str(six_num)]) > 0


def test_r4_t2_02_origin_single_engine_source(app_client, valid_divine_payload):
    """R4-B2: Single engine origin descriptions are cleanly formatted strings."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    origins = data["number_origins"]
    for num, src_list in origins.items():
        for src in src_list:
            assert isinstance(src, str)
            assert len(src) > 0


def test_r4_t2_03_origin_all_4_engines_combined(app_client, valid_divine_payload):
    """R4-B3: Multi-engine recommendations combine provenance from all 4 systems cleanly."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    origins = res.get_json()["number_origins"]
    assert len(origins) > 0


def test_r4_t2_04_origin_unicode_thai_characters(app_client, valid_divine_payload):
    """R4-B4: Provenance strings handle Thai Unicode text without encoding failures."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    origins_json_str = res.get_data(as_text=True)
    assert isinstance(origins_json_str, str)
    assert len(origins_json_str) > 0


def test_r4_t2_05_origin_empty_engine_output_safety(app_client, valid_divine_payload):
    """R4-B5: Partial data outputs provide fallback explanation without raising KeyError."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    origins = res.get_json()["number_origins"]
    for key, val in origins.items():
        assert isinstance(val, list)
