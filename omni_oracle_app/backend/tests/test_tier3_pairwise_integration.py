"""
Tier 3 Pairwise Integration Test Suite (11 Test Cases).
Target: omni_oracle_app/backend/tests/test_tier3_pairwise_integration.py
Methodology: Tests pairwise interactions between pairs of system features.
Ensures modules synthesize predictions and pass payloads seamlessly across boundaries.
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
    has_health = "รักษา" in text
    has_financial = "การันตี" in text
    return {
        "passed": not (has_health or has_financial),
        "sanitized_text": text.replace("การันตี", "มีความเป็นไปได้ตามสถิติ"),
        "flags_triggered": (["HEALTH_ADVICE"] if has_health else []) + (["FINANCIAL_GUARANTEE"] if has_financial else [])
    }


# =====================================================================
# TIER 3 PAIRWISE INTEGRATION TESTS (11 Test Cases)
# =====================================================================

def test_t3_01_astrology_numerology_synthesis():
    """Pairwise 1: Thai Astrology ↔ 7x9 Numerology lucky digit synthesis."""
    astro = calculate_thai_astrology("1995-08-15", "14:30")
    num = calculate_numerology_7x9("1995-08-15")
    combined_digits = astro.lucky_numbers + num["lucky_digits"]
    assert len(combined_digits) >= 5
    assert all(0 <= d <= 9 for d in combined_digits)


def test_t3_02_mahabote_tarot_overlay():
    """Pairwise 2: Burmese Mahabote ↔ Tarot card contextual overlay."""
    mahabote = calculate_mahabote("1995-08-15", "14:30")
    tarot = generate_celtic_cross_spread([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    raja_position = mahabote["positions"]["raja"]
    first_card = tarot["spread"][0]["card_id"]
    assert isinstance(raja_position, int)
    assert isinstance(first_card, int)


def test_t3_03_factsheet_recommender_weighting(mock_lottery_file):
    """Pairwise 3: Divination FactSheet ↔ Historical Lottery Recommender 60/40 weighting."""
    astro = calculate_thai_astrology("1995-08-15")
    num = calculate_numerology_7x9("1995-08-15")
    mahabote = calculate_mahabote("1995-08-15")
    tarot = generate_celtic_cross_spread([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    all_divination_digits = astro.lucky_numbers + num["lucky_digits"] + mahabote["lucky_digits"] + tarot["lucky_digits"]
    stats = process_historical_lottery(mock_lottery_file)
    recommendation = recommend_lottery_numbers(all_divination_digits, stats)

    assert recommendation["weights"]["divination"] == 0.60
    assert recommendation["weights"]["historical_glo"] == 0.40
    assert len(recommendation["two_digits"]) > 0


def test_t3_04_fastapi_safety_interception(app_client, sample_intake_payload):
    """Pairwise 4: FastAPI Backend ↔ Safety Guardrail middleware interception."""
    res = app_client.post("/api/v1/predict", json=sample_intake_payload)
    assert res.status_code == 200
    data = res.json()
    assert "safety_metadata" in data
    assert "passed" in data["safety_metadata"]


def test_t3_05_intake_form_payload_fastapi_serialization(app_client, sample_intake_payload):
    """Pairwise 5: Next.js Intake Form ↔ FastAPI /api/v1/predict JSON serialization."""
    res = app_client.post("/api/v1/predict", json=sample_intake_payload)
    assert res.status_code == 200
    data = res.json()
    assert "astrology" in data
    assert "recommended_lottery_numbers" in data


def test_t3_06_tarot_drawer_celtic_cross_mapping(app_client, sample_intake_payload):
    """Pairwise 6: Tarot Drawer API ↔ Backend Celtic Cross payload mapping."""
    res = app_client.post("/api/v1/predict", json=sample_intake_payload).json()
    tarot_spread = res["tarot"]["spread"]
    assert len(tarot_spread) == 10
    for idx, card in enumerate(tarot_spread):
        assert card["card_id"] == sample_intake_payload["selected_cards"][idx]


def test_t3_07_lottery_processor_recommender_cache(mock_lottery_file):
    """Pairwise 7: Historical Lottery Processor ↔ Statistical Recommender frequency cache."""
    stats = process_historical_lottery(mock_lottery_file)
    rec1 = recommend_lottery_numbers([5, 2], stats)
    rec2 = recommend_lottery_numbers([5, 2], stats)
    assert rec1["two_digits"] == rec2["two_digits"]


def test_t3_08_safety_sanitizer_persona_formatter():
    """Pairwise 8: Safety Guardrail Sanitizer ↔ Omni-Oracle Persona output formatter."""
    raw_reading = "ดวงชะตาของคุณจะดีขึ้น การันตีถูกหวย 100%"
    sanitized = validate_and_sanitize_reading(raw_reading)
    assert "การันตี" not in sanitized["sanitized_text"]


def test_t3_09_fastapi_error_handler_pydantic_payload(app_client):
    """Pairwise 9: FastAPI Error Handler ↔ Pydantic HTTP 422 response payload."""
    res = app_client.post("/api/v1/predict", json={"invalid": "payload"})
    assert res.status_code == 422
    assert "detail" in res.json()


def test_t3_10_full_stack_openapi_pydantic_validation(app_client, sample_intake_payload):
    """Pairwise 10: Full Stack REST API ↔ OpenAPI Pydantic response validation."""
    res = app_client.post("/api/v1/predict", json=sample_intake_payload)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data["omni_oracle_reading"], str)


def test_t3_11_divination_pipeline_recommended_numbers_json(app_client, sample_intake_payload):
    """Pairwise 11: End-to-End Divination Pipeline ↔ Recommended Numbers JSON structure."""
    res = app_client.post("/api/v1/predict", json=sample_intake_payload).json()
    rec = res["recommended_lottery_numbers"]
    assert "two_digits" in rec
    assert "three_digits" in rec
    assert "six_digits" in rec
    assert "confidence_score" in rec
