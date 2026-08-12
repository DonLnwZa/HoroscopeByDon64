import random

class NumberRecommender:
    def __init__(self, stats_engine):
        self.stats_engine = stats_engine

    def generate_recommendations(self, numerology_data, mahabote_data, astrology_data, tarot_data):
        """
        Generates 2-digit, 3-digit, and 6-digit lucky numbers along with origin provenance.
        Returns tuple: (lucky_numbers_dict, number_origins_dict)
        """
        # Safely extract Mahabote digits
        mah_positions = mahabote_data.get('positions', {}) if isinstance(mahabote_data, dict) else {}
        thanang_digit = mah_positions.get('thanang', {}).get('planet_digit', 1) if isinstance(mah_positions.get('thanang'), dict) else 1
        phoka_digit = mah_positions.get('phoka', {}).get('planet_digit', 5) if isinstance(mah_positions.get('phoka'), dict) else 5

        # Safely extract Astrology digits
        ast_primary = astrology_data.get('primary_lucky_planet', 1) if isinstance(astrology_data, dict) else 1
        ast_secondary = astrology_data.get('secondary_lucky_planet', 5) if isinstance(astrology_data, dict) else 5

        # Safely extract Numerology digits
        num_primary = numerology_data.get('primary_lucky_digits', [4, 8]) if isinstance(numerology_data, dict) else [4, 8]
        base_num = num_primary[0] if num_primary else 4

        # Safely extract Tarot cards
        tarot_cards = tarot_data if isinstance(tarot_data, list) else tarot_data.get('spread', []) if isinstance(tarot_data, dict) else []
        card1_name = tarot_cards[0].get('name', 'The Magician') if len(tarot_cards) > 0 else 'The Magician'
        card1_idx = tarot_cards[0].get('card_index', 1) if len(tarot_cards) > 0 else 1
        card3_name = tarot_cards[2].get('name', 'The Empress') if len(tarot_cards) > 2 else 'The Empress'
        card3_idx = tarot_cards[2].get('card_index', 3) if len(tarot_cards) > 2 else 3

        # 2-digit numbers
        two_digit_1 = f"{thanang_digit}{phoka_digit}"
        card3_digit = (card3_idx % 10)
        two_digit_2 = f"{card3_digit}{base_num}"
        if two_digit_2 == two_digit_1:
            two_digit_2 = f"{(card3_digit + 1) % 10}{base_num}"

        # 3-digit numbers
        three_digit_1 = f"{ast_primary}{two_digit_1}"
        num_d2 = num_primary[1] if len(num_primary) > 1 else 9
        three_digit_2 = f"{base_num}{num_d2}{ast_secondary}"
        if three_digit_2 == three_digit_1:
            three_digit_2 = f"{(base_num + 1) % 10}{num_d2}{ast_secondary}"

        # 6-digit number
        six_digit_1 = f"{three_digit_1}{three_digit_2}"

        lucky_numbers = {
            "two_digit": [two_digit_1, two_digit_2],
            "three_digit": [three_digit_1, three_digit_2],
            "six_digit": [six_digit_1]
        }

        number_origins = self.generate_origins(lucky_numbers, numerology_data, mahabote_data, astrology_data, tarot_data)

        return lucky_numbers, number_origins

    def generate_origins(self, lucky_numbers, numerology_data, mahabote_data, astrology_data, tarot_data):
        origins = {}
        
        mah_positions = mahabote_data.get('positions', {}) if isinstance(mahabote_data, dict) else {}
        thanang_digit = mah_positions.get('thanang', {}).get('planet_digit', 1) if isinstance(mah_positions.get('thanang'), dict) else 1
        phoka_digit = mah_positions.get('phoka', {}).get('planet_digit', 5) if isinstance(mah_positions.get('phoka'), dict) else 5
        
        ast_primary = astrology_data.get('primary_lucky_planet', 1) if isinstance(astrology_data, dict) else 1

        num_primary = numerology_data.get('primary_lucky_digits', [4, 8]) if isinstance(numerology_data, dict) else [4, 8]
        base_num = num_primary[0] if num_primary else 4

        tarot_cards = tarot_data if isinstance(tarot_data, list) else tarot_data.get('spread', []) if isinstance(tarot_data, dict) else []
        card1_name = tarot_cards[0].get('name', 'The Magician') if len(tarot_cards) > 0 else 'The Magician'
        card1_idx = tarot_cards[0].get('card_index', 1) if len(tarot_cards) > 0 else 1
        card3_name = tarot_cards[2].get('name', 'The Empress') if len(tarot_cards) > 2 else 'The Empress'
        card3_idx = tarot_cards[2].get('card_index', 3) if len(tarot_cards) > 2 else 3

        for cat in ["two_digit", "three_digit", "six_digit"]:
            for idx, num in enumerate(lucky_numbers.get(cat, [])):
                num_str = str(num)
                if cat == "two_digit":
                    if idx == 0:
                        origins[num_str] = [
                            f"ตำราพรมชาติมหาภูติ: ฐานัง ({thanang_digit}) + โภคา ({phoka_digit})",
                            f"โหราศาสตร์ไทย: ดาวเจ้าเรือนตนุ ({ast_primary})"
                        ]
                    else:
                        origins[num_str] = [
                            f"ไพ่ทาโรต์ใบที่ {card3_idx}: {card3_name}",
                            f"คัมภีร์เลขศาสตร์ 7x9: ฐานเลข {base_num}"
                        ]
                elif cat == "three_digit":
                    if idx == 0:
                        origins[num_str] = [f"สูตรถอดรหัส: ดาวตนุ ({ast_primary}) + มหาภูติ ({thanang_digit}{phoka_digit})"]
                    else:
                        origins[num_str] = [f"ไพ่ทาโรต์ใบที่ {card1_idx}: {card1_name} + เลขศาสตร์ {num_str}"]
                else:
                    origins[num_str] = ["สังเคราะห์การคำนวณรวมจากทั้ง 4 ศาสตร์"]

        return origins

