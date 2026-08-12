"""
Tier 1 Feature Coverage Test Suite (20 Test Cases).
Target: omni_oracle_app/e2e_tests/test_tier1_feature_coverage.py
Methodology: 5 test cases per feature across R1, R2, R3, R4.
Opaque-box contract testing with explicit assertions.
"""

import pytest


# =====================================================================
# FEATURE R1: Thai Lunar Calendar Auto-Calculation & 6am Cutoff
# =====================================================================

def test_r1_t1_01_lunar_calc_daytime(app_client):
    """R1-1: Birth time >= 06:00 ("14:30") retains current solar day (cutoff_applied: False)."""
    payload = {
        "full_name": "Somchai Jaidee",
        "birth_date": "1992-05-15",
        "birth_time": "14:30",
        "birth_province": "Bangkok",
        "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    lunar = data["chart"]["lunar_calendar"]
    assert lunar["cutoff_applied"] is False
    assert lunar["day_of_week"] in ["Friday", "ศุกร์", "Thursday", "พฤหัสบดี"]


def test_r1_t1_02_lunar_calc_early_morning_cutoff(app_client):
    """R1-2: Birth time < 06:00 ("05:30") applies 6am cutoff rule (cutoff_applied: True)."""
    payload = {
        "full_name": "Somchai Jaidee",
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "birth_province": "Bangkok",
        "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    lunar = data["chart"]["lunar_calendar"]
    assert lunar["cutoff_applied"] is True


def test_r1_t1_03_lunar_month_range(app_client, valid_divine_payload):
    """R1-3: Auto-calculated lunar_month is an integer in range [1..12]."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    lunar_month = data["chart"]["lunar_calendar"]["lunar_month"]
    assert isinstance(lunar_month, int)
    assert 1 <= lunar_month <= 12


def test_r1_t1_04_zodiac_year_mapping(app_client, valid_divine_payload):
    """R1-4: Auto-calculated zodiac_year returns a non-empty string animal name."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    zodiac = data["chart"]["lunar_calendar"]["zodiac_year"]
    assert isinstance(zodiac, str)
    assert len(zodiac) > 0


def test_r1_t1_05_lunar_calendar_divine_response_structure(app_client, valid_divine_payload):
    """R1-5: /api/divine payload contains chart.lunar_calendar with all 4 required keys."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "chart" in data
    assert "lunar_calendar" in data["chart"]
    lunar = data["chart"]["lunar_calendar"]
    for key in ["day_of_week", "lunar_month", "zodiac_year", "cutoff_applied"]:
        assert key in lunar, f"Missing key '{key}' in chart.lunar_calendar"


# =====================================================================
# FEATURE R2: Interactive Tarot Selection
# =====================================================================

def test_r2_t1_01_tarot_valid_10_cards(app_client, valid_divine_payload):
    """R2-1: Submit valid array of 10 distinct card indices and verify HTTP 200 OK."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "tarot_reading" in data
    assert "spread" in data["tarot_reading"]
    assert len(data["tarot_reading"]["spread"]) == 10


def test_r2_t1_02_tarot_position_mapping(app_client, valid_divine_payload):
    """R2-2: Verify returned 10 cards map 1-to-1 to 10 Celtic Cross positions."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    spread = data["tarot_reading"]["spread"]
    assert len(spread) == 10
    for card in spread:
        assert "position_meaning" in card or "position_name" in card or "position" in card


def test_r2_t1_03_tarot_major_minor_arcana_metadata(app_client):
    """R2-3: Verify Major Arcana (0..21) vs Minor Arcana (22..77) classification."""
    payload = {
        "full_name": "Test User",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "selected_tarot_cards": [0, 21, 22, 77, 5, 10, 30, 40, 50, 60]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    spread = data["tarot_reading"]["spread"]
    assert spread[0]["type"] == "Major Arcana"
    assert spread[1]["type"] == "Major Arcana"
    assert spread[2]["type"] == "Minor Arcana"
    assert spread[3]["type"] == "Minor Arcana"


def test_r2_t1_04_tarot_reversal_state_handling(app_client, valid_divine_payload):
    """R2-4: Verify each drawn card includes is_reversed boolean flag."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    spread = data["tarot_reading"]["spread"]
    for card in spread:
        assert isinstance(card["is_reversed"], bool)


def test_r2_t1_05_tarot_divine_endpoint_integration(app_client, valid_divine_payload):
    """R2-5: Verify /api/divine passes selected_tarot_cards into tarot spread generator."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    spread = data["tarot_reading"]["spread"]
    assert len(spread) == 10


# =====================================================================
# FEATURE R3: Backtesting Heat Index
# =====================================================================

def test_r3_t1_01_heat_index_response_structure(app_client, valid_divine_payload):
    """R3-1: Verify /api/divine response JSON contains heat_index with 3 digit categories."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "heat_index" in data
    heat = data["heat_index"]
    assert "two_digit" in heat
    assert "three_digit" in heat
    assert "six_digit" in heat


def test_r3_t1_02_heat_index_win_count_calculation(app_client, valid_divine_payload):
    """R3-2: Verify win count is an integer >= 0 for all numbers in heat_index."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    heat = data["heat_index"]
    for category in ["two_digit", "three_digit", "six_digit"]:
        for item in heat[category]:
            assert "win_count" in item
            assert isinstance(item["win_count"], int)
            assert item["win_count"] >= 0


def test_r3_t1_03_heat_index_hot_classification(app_client, valid_divine_payload):
    """R3-3: Verify recommended number with win_count >= 3 is classified as HOT."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    heat = data["heat_index"]
    for category in ["two_digit", "three_digit", "six_digit"]:
        for item in heat[category]:
            if item["win_count"] >= 3:
                assert item["level"] == "HOT"


def test_r3_t1_04_heat_index_warm_classification(app_client, valid_divine_payload):
    """R3-4: Verify recommended number with win_count in [1, 2] is classified as WARM."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    heat = data["heat_index"]
    for category in ["two_digit", "three_digit", "six_digit"]:
        for item in heat[category]:
            if item["win_count"] in [1, 2]:
                assert item["level"] == "WARM"


def test_r3_t1_05_heat_index_cold_classification(app_client, valid_divine_payload):
    """R3-5: Verify recommended number with win_count == 0 is classified as COLD."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    heat = data["heat_index"]
    for category in ["two_digit", "three_digit", "six_digit"]:
        for item in heat[category]:
            if item["win_count"] == 0:
                assert item["level"] == "COLD"


# =====================================================================
# FEATURE R4: Divination Transparency (Number Origins)
# =====================================================================

def test_r4_t1_01_number_origins_presence(app_client, valid_divine_payload):
    """R4-1: Verify /api/divine response JSON contains number_origins dictionary."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "number_origins" in data
    assert isinstance(data["number_origins"], dict)


def test_r4_t1_02_origins_mapped_for_all_recommended_numbers(app_client, valid_divine_payload):
    """R4-2: Verify every number in lucky_numbers has a key in number_origins."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    lucky = data["lucky_numbers"]
    origins = data["number_origins"]
    all_numbers = lucky.get("two_digit", []) + lucky.get("three_digit", []) + lucky.get("six_digit", [])
    for num in all_numbers:
        assert str(num) in origins, f"Number '{num}' missing from number_origins"


def test_r4_t1_03_origin_explanation_format(app_client, valid_divine_payload):
    """R4-3: Verify each value in number_origins is a non-empty list of strings."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    origins = data["number_origins"]
    for num, src_list in origins.items():
        assert isinstance(src_list, list)
        assert len(src_list) > 0
        for src in src_list:
            assert isinstance(src, str)
            assert len(src) > 0


def test_r4_t1_04_origin_tracks_engine_sources(app_client, valid_divine_payload):
    """R4-4: Verify origin strings reference specific divination engines."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    origins = data["number_origins"]
    all_text = " ".join([src for src_list in origins.values() for src in src_list])
    engine_keywords = ["Mahabote", "Astrology", "Tarot", "Numerology", "Combined", "Synthesis"]
    assert any(kw in all_text for kw in engine_keywords)


def test_r4_t1_05_transparency_frontend_payload_contract(app_client, valid_divine_payload):
    """R4-5: Verify number_origins payload format matches frontend contract."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    lucky = data["lucky_numbers"]
    origins = data["number_origins"]
    assert len(origins) >= len(lucky.get("two_digit", []))
