import secrets
import json
from typing import List, Optional

class TarotEngine:
    def __init__(self):
        # We define a basic deck representation.
        self.deck = self._generate_deck()
        self.celtic_cross_positions = [
            "สถานการณ์ปัจจุบัน",
            "สิ่งที่เข้ามาขัดขวางหรือส่งเสริม",
            "รากฐานของปัญหาหรืออดีตที่ผ่านมา",
            "อดีตที่เพิ่งผ่านพ้นไป",
            "เป้าหมายหรือสิ่งที่มุ่งหวัง",
            "อนาคตอันใกล้",
            "ตัวตนของผู้ถามในสถานการณ์นั้น",
            "สภาพแวดล้อมและบุคคลรอบข้าง",
            "ความหวังและความกลัว",
            "บทสรุปของสถานการณ์"
        ]

    def _generate_deck(self):
        deck = []
        
        # Major Arcana
        major_names = [
            "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", 
            "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", 
            "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", 
            "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
        ]
        
        for i, name in enumerate(major_names):
            deck.append({
                "id": f"major_{i}",
                "name": name,
                "type": "Major Arcana",
                "meaning_upright": f"ความหมายเชิงบวกของ {name}",
                "meaning_reversed": f"ความหมายเชิงลบหรือถูกปิดกั้นของ {name}"
            })
            
        # Minor Arcana
        suits = ["Wands", "Cups", "Swords", "Pentacles"]
        ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]
        
        for suit in suits:
            for rank in ranks:
                name = f"{rank} of {suit}"
                deck.append({
                    "id": f"minor_{suit}_{rank}",
                    "name": name,
                    "type": "Minor Arcana",
                    "meaning_upright": f"พลังงาน {suit} ในระดับ {rank}",
                    "meaning_reversed": f"ปัญหาที่เกี่ยวข้องกับพลังงาน {suit} ระดับ {rank}"
                })
                
        return deck

    def draw_celtic_cross(self, selected_cards: Optional[List[int]] = None) -> List[dict]:
        """
        Draws a 10-card Celtic Cross spread.
        
        Parameters:
            selected_cards: Optional list of 10 card indices (0..77) chosen by user.
                            If None, randomly shuffles and draws 10 cards using CSPRNG.
                            
        Returns:
            List of 10 drawn card dictionaries.
            
        Raises:
            ValueError if selected_cards is invalid.
        """
        drawn_cards = []
        
        if selected_cards is not None:
            if not isinstance(selected_cards, (list, tuple)):
                raise ValueError("selected_tarot_cards must be a list of 10 card indices.")
            if len(selected_cards) != 10:
                raise ValueError(f"selected_tarot_cards must contain exactly 10 card indices, got {len(selected_cards)}.")
            
            seen_indices = set()
            for idx in selected_cards:
                if not isinstance(idx, int) or isinstance(idx, bool):
                    raise ValueError(f"Invalid card index '{idx}'. Card index must be an integer.")
                if not (0 <= idx <= 77):
                    raise ValueError(f"Card index {idx} out of valid range (0..77).")
                if idx in seen_indices:
                    raise ValueError(f"Duplicate card index {idx} in selected_tarot_cards.")
                seen_indices.add(idx)

            for i, card_idx in enumerate(selected_cards):
                card = self.deck[card_idx]
                is_reversed = secrets.choice([True, False])
                drawn_cards.append({
                    "id": card["id"],
                    "card_index": card_idx,
                    "name": card["name"],
                    "type": card["type"],
                    "is_reversed": is_reversed,
                    "position_meaning": self.celtic_cross_positions[i],
                    "meaning": card["meaning_reversed"] if is_reversed else card["meaning_upright"]
                })
        else:
            deck_copy = self.deck.copy()
            for i in range(10):
                idx = secrets.randbelow(len(deck_copy))
                card = deck_copy.pop(idx)
                is_reversed = secrets.choice([True, False])
                card_orig_idx = next(j for j, c in enumerate(self.deck) if c["id"] == card["id"])
                drawn_cards.append({
                    "id": card["id"],
                    "card_index": card_orig_idx,
                    "name": card["name"],
                    "type": card["type"],
                    "is_reversed": is_reversed,
                    "position_meaning": self.celtic_cross_positions[i],
                    "meaning": card["meaning_reversed"] if is_reversed else card["meaning_upright"]
                })
                
        return drawn_cards
