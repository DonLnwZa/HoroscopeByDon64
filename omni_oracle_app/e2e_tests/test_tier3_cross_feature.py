"""
Tier 3 Cross-Feature Pairwise Integration Test Suite (11 Test Cases).
Target: omni_oracle_app/e2e_tests/test_tier3_cross_feature.py
Methodology: Pairwise and multi-feature integration across R1, R2, R3, R4.
Full JSON request/response schema validation and subsystem isolation.
"""

import pytest


def test_t3_pairwise_01_r1_r2_lunar_cutoff_with_tarot_selection(app_client):
    """Pairwise 1: R1 (Lunar Cutoff) ↔ R2 (Interactive Tarot Selection)."""
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
    assert data["chart"]["lunar_calendar"]["cutoff_applied"] is True
    assert len(data["tarot_reading"]["spread"]) == 10


def test_t3_pairwise_02_r1_r3_lunar_lucky_digits_to_heat_index(app_client):
    """Pairwise 2: R1 (Lunar/Astrology) ↔ R3 (Backtesting Heat Index)."""
    payload = {
        "full_name": "Kanya",
        "birth_date": "1990-01-01",
        "birth_time": "06:30",
        "selected_tarot_cards": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    lucky = data["lucky_numbers"]
    heat = data["heat_index"]
    for category in ["two_digit", "three_digit", "six_digit"]:
        assert category in heat
        assert len(heat[category]) == len(lucky.get(category, []))


def test_t3_pairwise_03_r1_r4_lunar_astrology_to_number_origins(app_client):
    """Pairwise 3: R1 (Lunar/Astrology) ↔ R4 (Divination Transparency Origins)."""
    payload = {
        "full_name": "Anan",
        "birth_date": "1988-11-12",
        "birth_time": "05:15",
        "selected_tarot_cards": [0, 10, 20, 30, 40, 50, 60, 70, 71, 72]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    origins = data["number_origins"]
    assert isinstance(origins, dict)
    assert len(origins) > 0


def test_t3_pairwise_04_r2_r3_tarot_cards_to_heat_index(app_client):
    """Pairwise 4: R2 (Interactive Tarot Selection) ↔ R3 (Backtesting Heat Index)."""
    payload = {
        "full_name": "Malai",
        "birth_date": "1995-03-20",
        "birth_time": "12:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    heat = data["heat_index"]
    for cat in ["two_digit", "three_digit", "six_digit"]:
        for item in heat[cat]:
            assert "win_count" in item
            assert "level" in item


def test_t3_pairwise_05_r2_r4_tarot_cards_to_number_origins(app_client):
    """Pairwise 5: R2 (Interactive Tarot Selection) ↔ R4 (Divination Transparency Origins)."""
    payload = {
        "full_name": "Tarot User",
        "birth_date": "1995-03-20",
        "birth_time": "12:00",
        "selected_tarot_cards": [3, 12, 25, 31, 44, 50, 61, 72, 5, 18]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    origins = data["number_origins"]
    assert len(origins) > 0


def test_t3_pairwise_06_r3_r4_heat_index_origins_structural_parity(app_client, valid_divine_payload):
    """Pairwise 6: R3 (Heat Index) ↔ R4 (Divination Transparency Origins) Structural Parity."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    heat = data["heat_index"]
    origins = data["number_origins"]
    heat_numbers = set()
    for cat in ["two_digit", "three_digit", "six_digit"]:
        for item in heat[cat]:
            heat_numbers.add(str(item["number"]))
    assert heat_numbers.issubset(set(origins.keys()))


def test_t3_pairwise_07_full_single_request_integration(app_client, valid_divine_payload):
    """Pairwise 7: Full 4-Feature Combined Pipeline (R1 + R2 + R3 + R4)."""
    res = app_client.post("/api/divine", json=valid_divine_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == "success" or "chart" in data
    assert "chart" in data
    assert "tarot_reading" in data
    assert "lucky_numbers" in data
    assert "heat_index" in data
    assert "number_origins" in data
    assert "synthesis" in data
    assert "disclaimer" in data


def test_t3_pairwise_08_multi_request_sequential_isolation(app_client):
    """Pairwise 8: Sequential requests with different birth times (05:30 vs 06:30) maintain isolation."""
    payload_a = {
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    payload_b = {
        "birth_date": "1992-05-15",
        "birth_time": "06:30",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res_a = app_client.post("/api/divine", json=payload_a)
    res_b = app_client.post("/api/divine", json=payload_b)
    
    assert res_a.status_code == 200
    assert res_b.status_code == 200
    assert res_a.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is True
    assert res_b.get_json()["chart"]["lunar_calendar"]["cutoff_applied"] is False


def test_t3_pairwise_09_multi_request_tarot_variation(app_client):
    """Pairwise 9: Sequential requests with different Tarot selections alter tarot_reading."""
    payload_a = {
        "birth_date": "1992-05-15",
        "birth_time": "12:00",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    payload_b = {
        "birth_date": "1992-05-15",
        "birth_time": "12:00",
        "selected_tarot_cards": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    }
    res_a = app_client.post("/api/divine", json=payload_a)
    res_b = app_client.post("/api/divine", json=payload_b)
    
    assert res_a.status_code == 200
    assert res_b.status_code == 200
    spread_a = res_a.get_json()["tarot_reading"]["spread"]
    spread_b = res_b.get_json()["tarot_reading"]["spread"]
    assert spread_a != spread_b


def test_t3_pairwise_10_error_boundary_invalid_r2_valid_r1(app_client):
    """Pairwise 10: Invalid R2 (3 cards) fails fast before R1 engine processing."""
    payload = {
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "selected_tarot_cards": [0, 1, 2]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code in [400, 422]


def test_t3_pairwise_11_error_boundary_invalid_r1_valid_r2(app_client):
    """Pairwise 11: Invalid R1 birth_date returns validation error."""
    payload = {
        "birth_date": "invalid-date",
        "birth_time": "05:30",
        "selected_tarot_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    res = app_client.post("/api/divine", json=payload)
    assert res.status_code in [400, 422]
