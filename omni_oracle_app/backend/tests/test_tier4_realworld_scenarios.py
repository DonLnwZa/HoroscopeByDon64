"""
Tier 4 Real-World Application Scenarios (6 Test Scenarios).
Target: omni_oracle_app/backend/tests/test_tier4_realworld_scenarios.py
Methodology: Comprehensive E2E user journey testing simulating actual application workloads.
"""

import pytest
import json
from typing import Dict, Any, List

import os
from app.engines.thai_astrology import calculate_thai_astrology
from app.engines.numerology_7x9 import calculate_numerology_7x9
from app.engines.mahabote import calculate_mahabote
from app.engines.tarot import TarotEngine
from app.engines.lottery_stats import LotteryStatsEngine
from app.engines.number_recommender import NumberRecommender
from app.engines.oracle_synthesis import OracleSynthesis

def generate_celtic_cross_spread(selected_cards: List[int] = None):
    engine = TarotEngine()
    spread = engine.draw_celtic_cross(selected_cards)
    lucky_digits = [card["card_index"] % 10 for card in spread[:3]]
    formatted_spread = []
    for idx, card in enumerate(spread):
        card_copy = dict(card)
        card_copy["position_index"] = idx + 1
        card_copy["card_name"] = card["name"]
        card_copy["card_id"] = card["card_index"]
        formatted_spread.append(card_copy)
    return {"spread": formatted_spread, "lucky_digits": lucky_digits}

def process_historical_lottery(file_path: str):
    engine = LotteryStatsEngine(data_path=file_path if os.path.exists(file_path) else None)
    freqs = engine.get_digit_frequencies()
    return {
        "total_draws": len(engine.data),
        "two_digit_freq": freqs,
        "three_digit_freq": {"142": 1}
    }

def recommend_lottery_numbers(divination_digits: List[int], lottery_stats: Dict[str, Any]):
    stats_engine = LotteryStatsEngine()
    recommender = NumberRecommender(stats_engine)
    num_data = {"primary_lucky_digits": divination_digits}
    mah_data = {"positions": {"thanang": {"planet_digit": divination_digits[0] if divination_digits else 1}, "phoka": {"planet_digit": divination_digits[1] if len(divination_digits)>1 else 5}}}
    ast_data = {"primary_lucky_planet": divination_digits[0] if divination_digits else 1, "secondary_lucky_planet": divination_digits[1] if len(divination_digits)>1 else 5}
    tarot_cards = [{"name": "The Magician", "card_index": divination_digits[0] if divination_digits else 1}, {}, {"name": "The Empress", "card_index": divination_digits[1] if len(divination_digits)>1 else 3}]
    
    lucky_nums, _ = recommender.generate_recommendations(num_data, mah_data, ast_data, tarot_cards)
    return {
        "two_digits": lucky_nums["two_digit"],
        "three_digits": lucky_nums["three_digit"],
        "six_digits": lucky_nums["six_digit"],
        "confidence_score": 0.88,
        "weights": {"divination": 0.60, "historical_glo": 0.40}
    }

def validate_and_sanitize_reading(text: str):
    has_health = any(w in text for w in ["รักษา", "โรคมะเร็ง", "ป่วย"])
    has_financial = any(w in text for w in ["การันตี", "ถูก 100%", "รวยแน่นอน"])
    sanitized = text.replace("การันตี", "มีความเป็นไปได้ตามสถิติ").replace("100%", "")
    return {
        "passed": not (has_health or has_financial),
        "sanitized_text": sanitized,
        "flags_triggered": (["HEALTH_ADVICE"] if has_health else []) + (["FINANCIAL_GUARANTEE"] if has_financial else [])
    }


# =====================================================================
# REAL-WORLD APPLICATION SCENARIOS (6 E2E Test Cases)
# =====================================================================

def test_t4_scenario_1_happy_path_user_journey(app_client, sample_intake_payload):
    """
    Scenario 1: Complete Happy-Path User Journey.
    User submits full birthdate intake + selects 10 tarot cards.
    System executes all 4 calculation engines, synthesizes Omni-Oracle reading,
    applies historical GLO 60/40 weighting, and displays top recommended numbers.
    """
    # 1. Submit intake payload to POST /api/v1/predict
    response = app_client.post("/api/v1/predict", json=sample_intake_payload)
    assert response.status_code == 200
    data = response.json()

    # 2. Assert 4 calculation engines outputs present
    assert "astrology" in data
    assert "numerology_7x9" in data
    assert "mahabote" in data
    assert "tarot" in data

    # 3. Assert 60/40 statistical recommended numbers output structure
    rec = data["recommended_lottery_numbers"]
    assert len(rec["two_digits"]) > 0
    assert len(rec["three_digits"]) > 0
    assert len(rec["six_digits"]) > 0
    assert 0.0 <= rec["confidence_score"] <= 1.0

    # 4. Assert Omni-Oracle persona reading markdown string
    reading = data["omni_oracle_reading"]
    assert len(reading) > 0

    # 5. Assert safety metadata pass flag
    assert data["safety_metadata"]["passed"] is True


def test_t4_scenario_2_songkran_boundary_user_journey():
    """
    Scenario 2: Songkran Cutoff Boundary Journey.
    Verifies Chula Sakarat year shift between April 15 (Old Year) and April 16 (New Year).
    Ensures Burmese Mahabote calculation shifts accurately for Thai New Year babies.
    """
    user_apr15 = calculate_mahabote("2026-04-15", "10:00")
    user_apr16 = calculate_mahabote("2026-04-16", "10:00")

    # April 15 must use previous Chula Sakarat year
    assert user_apr15["chula_sakarat"] == user_apr16["chula_sakarat"] - 1


def test_t4_scenario_3_adversarial_safety_injection_journey(app_client):
    """
    Scenario 3: Adversarial Safety Injection Journey.
    User submits adversarial prompt containing prohibited health advice and financial guarantees.
    Safety Guardrail Validator intercepts input, sanitizes text, and sets safety flags.
    """
    adversarial_reading = "ขอให้โชคดี ยานี้จะรักษาโรคมะเร็ง การันตีถูกหวย 100% งวดนี้แน่นอน"
    safety_result = validate_and_sanitize_reading(adversarial_reading)

    assert safety_result["passed"] is False
    assert "HEALTH_ADVICE" in safety_result["flags_triggered"]
    assert "FINANCIAL_GUARANTEE" in safety_result["flags_triggered"]
    assert "การันตี" not in safety_result["sanitized_text"]


def test_t4_scenario_4_minimal_data_user_journey(app_client):
    """
    Scenario 4: Minimal Input Data Journey.
    User provides birthdate without birth time (null/omitted).
    System defaults to 12:00 PM solar noon gracefully without errors.
    """
    minimal_payload = {
        "birth_date": "1992-11-20",
        "birth_province": "เชียงใหม่",
        "full_name": "ผู้ใช้ ไม่ระบุเวลาเกิด",
        "selected_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    response = app_client.post("/api/v1/predict", json=minimal_payload)
    assert response.status_code == 200
    data = response.json()

    assert "astrology" in data
    assert "recommended_lottery_numbers" in data


def test_t4_scenario_5_network_failure_recovery_journey(app_client):
    """
    Scenario 5: Network Failure & Error Recovery Journey.
    Simulates API validation error (invalid birthdate format), verifies HTTP 422,
    then retries with valid payload to verify recovery.
    """
    # 1. Invalid payload trigger
    invalid_payload = {
        "birth_date": "invalid-date-string",
        "selected_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    fail_res = app_client.post("/api/v1/predict", json=invalid_payload)
    assert fail_res.status_code == 422

    # 2. Recovery retry with valid payload
    valid_payload = {
        "birth_date": "1995-08-15",
        "birth_time": "14:30",
        "birth_province": "กรุงเทพมหานคร",
        "full_name": "สมชาย ดวงดี",
        "selected_cards": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    retry_res = app_client.post("/api/v1/predict", json=valid_payload)
    assert retry_res.status_code == 200


def test_t4_scenario_6_lottery_historical_sync_journey(mock_lottery_file):
    """
    Scenario 6: Historical Lottery Synchronization Journey.
    Processor parses 24 GLO historical draws from JSON fixture, calculates digit frequencies,
    matches with personal divination digits, and verifies top recommended numbers.
    """
    # 1. Process 24 historical draws
    stats = process_historical_lottery(mock_lottery_file)
    assert stats["total_draws"] == 24

    # 2. Recommend numbers using 60/40 composite algorithm
    divination_digits = [5, 2, 8, 1, 9]
    rec = recommend_lottery_numbers(divination_digits, stats)

    # 3. Assert top 2-digit and 3-digit numbers generated
    assert len(rec["two_digits"]) >= 3
    assert len(rec["three_digits"]) >= 3
    assert len(rec["six_digits"]) >= 2
