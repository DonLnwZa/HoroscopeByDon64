import pytest
import os
import json
from app.engines.lottery_stats import LotteryStatsEngine

def setup_mock_data(tmp_path):
    mock_data = [
        {
            "draw_date": "2025-08-01",
            "prize_1st": "811852",
            "prize_last2": "50",
            "prize_last3f": ["142", "525"],
            "prize_last3b": ["512", "891"]
        },
        {
            "draw_date": "2025-08-16",
            "prize_1st": "994865",
            "prize_last2": "63",
            "prize_last3f": ["247", "602"],
            "prize_last3b": ["834", "989"]
        }
    ]
    
    data_file = tmp_path / "lottery_results.json"
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)
        
    return str(data_file)

def test_load_data(tmp_path):
    data_path = setup_mock_data(tmp_path)
    engine = LotteryStatsEngine(data_path=data_path)
    
    assert len(engine.data) == 2
    assert engine.data[0]['prize_1st'] == "811852"

def test_number_frequencies(tmp_path):
    data_path = setup_mock_data(tmp_path)
    engine = LotteryStatsEngine(data_path=data_path)
    
    freqs = engine.get_digit_frequencies()
    assert '0' in freqs
    assert '1' in freqs
    
    # In "50" and "63" (last 2), 5, 0, 6, 3 should be present
    assert freqs['5'] >= 1
    
def test_hot_cold_numbers(tmp_path):
    data_path = setup_mock_data(tmp_path)
    engine = LotteryStatsEngine(data_path=data_path)
    
    hot, cold = engine.get_hot_cold_numbers()
    assert isinstance(hot, list)
    assert isinstance(cold, list)
