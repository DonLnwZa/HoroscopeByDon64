import json
import os
from collections import Counter

class LotteryStatsEngine:
    def __init__(self, data_path=None):
        if data_path is None:
            # Default path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.data_path = os.path.join(base_dir, "data", "lottery_results_past_1_year.json")
        else:
            self.data_path = data_path
            
        self.data = self._load_data()
        
    def _load_data(self):
        if not os.path.exists(self.data_path):
            return []
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_digit_frequencies(self):
        """Analyze frequency of digits 0-9 across 1st prize and last 2 digits"""
        counter = Counter()
        for draw in self.data:
            # Count digits in 1st prize
            prize_1st = str(draw.get("prize_1st", ""))
            for digit in prize_1st:
                counter[digit] += 1
                
            # Count digits in last 2
            prize_last2 = str(draw.get("prize_last2", ""))
            for digit in prize_last2:
                counter[digit] += 1
                
        return dict(counter)

    def get_hot_cold_numbers(self):
        """Return hottest and coldest digits"""
        freqs = self.get_digit_frequencies()
        if not freqs:
            return [], []
            
        sorted_digits = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
        hot = [x[0] for x in sorted_digits[:3]]
        cold = [x[0] for x in sorted_digits[-3:]]
        
        return hot, cold
        
    def get_lucky_pool(self):
        """Return a pool of lucky numbers to use for recommendations"""
        hot, _ = self.get_hot_cold_numbers()
        if not hot:
            return ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        return hot

    def evaluate_heat_index(self, lucky_numbers: dict) -> dict:
        """
        Evaluates generated lucky numbers against 24 historical GLO draw records.
        Returns heat_index dict containing win_count and level classification for each number.
        """
        result = {
            "two_digit": [],
            "three_digit": [],
            "six_digit": []
        }
        
        for category in ["two_digit", "three_digit", "six_digit"]:
            for num in lucky_numbers.get(category, []):
                num_str = str(num)
                win_count = 0
                for draw in self.data:
                    prize_1st = str(draw.get("prize_1st", ""))
                    
                    if category == "two_digit":
                        prize_last2 = str(draw.get("prize_last2", ""))
                        if num_str == prize_last2 or (len(prize_1st) >= 2 and num_str == prize_1st[-2:]):
                            win_count += 1
                            
                    elif category == "three_digit":
                        last3f = draw.get("prize_last3f", []) if isinstance(draw.get("prize_last3f"), list) else []
                        last3b = draw.get("prize_last3b", []) if isinstance(draw.get("prize_last3b"), list) else []
                        matched = False
                        if num_str in last3f or num_str in last3b:
                            matched = True
                        elif len(prize_1st) >= 3 and (num_str == prize_1st[-3:] or num_str == prize_1st[:3]):
                            matched = True
                        if matched:
                            win_count += 1
                            
                    elif category == "six_digit":
                        near1 = draw.get("prize_near1", []) if isinstance(draw.get("prize_near1"), list) else []
                        p2 = draw.get("prize_2nd", []) if isinstance(draw.get("prize_2nd"), list) else []
                        p3 = draw.get("prize_3rd", []) if isinstance(draw.get("prize_3rd"), list) else []
                        p4 = draw.get("prize_4th", []) if isinstance(draw.get("prize_4th"), list) else []
                        p5 = draw.get("prize_5th", []) if isinstance(draw.get("prize_5th"), list) else []
                        if num_str == prize_1st or num_str in near1 or num_str in p2 or num_str in p3 or num_str in p4 or num_str in p5:
                            win_count += 1
                
                level = "HOT" if win_count >= 3 else ("WARM" if win_count >= 1 else "COLD")
                result[category].append({
                    "number": num_str,
                    "win_count": win_count,
                    "level": level
                })
                
        return result

    def calculate_heat_index(self, lucky_numbers: dict) -> dict:
        return self.evaluate_heat_index(lucky_numbers)

