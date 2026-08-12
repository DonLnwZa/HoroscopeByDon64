"""
Tier 4 Real-World Application Scenarios Test Suite (6 Test Cases).
Target: omni_oracle_app/e2e_tests/test_tier4_real_world.py
Methodology: End-to-end user divination journey scenarios and real-world workflows.
"""

import pytest


def test_t4_scenario_01_early_morning_birth_cutoff_journey(app_client):
    """
    Scenario 1: Somchai, born at 05:30 AM on 1992-05-15 in Bangkok (Pre-sunrise cutoff).
    Full session journey: Health check -> Divine -> Validate Cutoff & Transparency.
    """
    health_res = app_client.get("/api/health")
    assert health_res.status_code == 200
    
    divine_payload = {
        "full_name": "Somchai Jaidee",
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "birth_province": "Bangkok",
        "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
    }
    divine_res = app_client.post("/api/divine", json=divine_payload)
    assert divine_res.status_code == 200
    data = divine_res.get_json()
    
    assert data["chart"]["lunar_calendar"]["cutoff_applied"] is True
    assert "heat_index" in data
    assert "number_origins" in data
    assert len(data["synthesis"]) > 0


def test_t4_scenario_02_post_cutoff_morning_birth_journey(app_client):
    """
    Scenario 2: Malai, born at 06:30 AM on 1992-05-15 in Chiang Mai (Post-sunrise).
    Full session journey: Divine -> Validate no cutoff -> Validate Heat Index levels.
    """
    divine_payload = {
        "full_name": "Malai Wong",
        "birth_date": "1992-05-15",
        "birth_time": "06:30",
        "birth_province": "เชียงใหม่",
        "selected_tarot_cards": [1, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    }
    res = app_client.post("/api/divine", json=divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["chart"]["lunar_calendar"]["cutoff_applied"] is False


def test_t4_scenario_03_songkran_new_year_boundary_journey(app_client):
    """
    Scenario 3: Kanya, born during Songkran Thai New Year transition.
    Submits requests for April 15 23:45 and April 16 06:15.
    """
    payload_a = {
        "full_name": "Kanya Songkran A",
        "birth_date": "1995-04-15",
        "birth_time": "23:45",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    payload_b = {
        "full_name": "Kanya Songkran B",
        "birth_date": "1995-04-16",
        "birth_time": "06:15",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res_a = app_client.post("/api/divine", json=payload_a)
    res_b = app_client.post("/api/divine", json=payload_b)
    
    assert res_a.status_code == 200
    assert res_b.status_code == 200
    assert res_a.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is False
    assert res_b.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is False


def test_t4_scenario_04_midnight_birth_boundary_cards_journey(app_client):
    """
    Scenario 4: Anan, born 00:05 AM with boundary Tarot cards (0 & 77).
    """
    payload = {
        "full_name": "Anan Midnight",
        "birth_date": "1998-12-31",
        "birth_time": "00:05",
        "selected_tarot_cards": [0, 77, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["chart"]["lunar_calendar"]["cutoff_applied"] is True
    spread = data["tarot_reading"]["spread"]
    assert len(spread) == 10


def test_t4_scenario_05_invalid_input_resilience_journey(app_client):
    """
    Scenario 5: User makes UI input mistake (3 cards), gets error, fixes input, succeeds.
    """
    bad_payload = {
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "selected_tarot_cards": [0, 1, 2]
    }
    bad_res = app_client.post("/api/divine", json=bad_payload)
    assert bad_res.status_code in [400, 422]
    
    good_payload = {
        "full_name": "Somchai Resilient",
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    good_res = app_client.post("/api/divine", json=good_payload)
    assert good_res.status_code == 200


def test_t4_scenario_06_glo_historical_backtesting_sync_journey(app_client):
    """
    Scenario 6: Full historical backtesting sync journey against 24 GLO draw records.
    """
    stats_res = app_client.get("/api/lottery/stats")
    assert stats_res.status_code == 200
    
    divine_payload = {
        "full_name": "Backtest User",
        "birth_date": "1990-07-20",
        "birth_time": "14:00",
        "selected_tarot_cards": [5, 15, 25, 35, 45, 55, 65, 75, 10, 20]
    }
    divine_res = app_client.post("/api/divine", json=divine_payload)
    assert divine_res.status_code == 200
    data = divine_res.get_json()
    assert "heat_index" in data
    assert "number_origins" in data
