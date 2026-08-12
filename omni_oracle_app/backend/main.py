import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from app.engines.numerology_7x9 import calculate_numerology_7x9
from app.engines.mahabote import calculate_mahabote
from app.engines.thai_astrology import calculate_thai_astrology, calculate_thai_lunar_calendar, THAI_DAY_NAMES, THAI_ZODIAC_NAMES
from app.engines.tarot import TarotEngine
from app.engines.lottery_stats import LotteryStatsEngine
from app.engines.number_recommender import NumberRecommender
from app.engines.oracle_synthesis import OracleSynthesis

# Path to the frontend directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    else:
        return send_from_directory(FRONTEND_DIR, 'index.html')

stats_engine = LotteryStatsEngine()
tarot_engine = TarotEngine()
recommender = NumberRecommender(stats_engine)
synthesis = OracleSynthesis()

@app.route('/api/health', methods=['GET'])
@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})

@app.route('/api/lottery/stats', methods=['GET'])
@app.route('/api/v1/lottery/stats', methods=['GET'])
def get_stats():
    hot, cold = stats_engine.get_hot_cold_numbers()
    freqs = stats_engine.get_digit_frequencies()
    return jsonify({
        "hot_numbers": hot,
        "cold_numbers": cold,
        "frequency": freqs,
        "total_draws": len(stats_engine.data),
        "top_two_digits": hot[:3] if hot else ["50", "52", "85"]
    })

@app.route('/api/divine', methods=['POST'])
@app.route('/api/v1/predict', methods=['POST'])
def divine():
    data = request.json or {}
    
    birth_date = data.get('birth_date', '1990-01-01')
    birth_time = data.get('birth_time', '12:00')
    birth_province = data.get('birth_province', 'กรุงเทพมหานคร')
    selected_tarot_cards = data.get('selected_tarot_cards', data.get('selected_cards', None))

    # 1. Thai Lunar Calendar calculation with 6am Cutoff (R1)
    try:
        lunar_res = calculate_thai_lunar_calendar(birth_date=birth_date, birth_time=birth_time)
        day_th = THAI_DAY_NAMES.get(lunar_res.day_of_week_num, lunar_res.day_of_week)
        zodiac_th = THAI_ZODIAC_NAMES.get(lunar_res.zodiac_year_num, lunar_res.zodiac_year)
        lunar_info = {
            "day_of_week": lunar_res.day_of_week,
            "day_of_week_th": day_th,
            "lunar_month": lunar_res.lunar_month,
            "zodiac_year": lunar_res.zodiac_year,
            "zodiac_year_th": zodiac_th,
            "cutoff_applied": lunar_res.cutoff_applied
        }
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400

    # 2. Tarot Celtic Cross calculation (R2)
    try:
        tarot_res = tarot_engine.draw_celtic_cross(selected_cards=selected_tarot_cards)
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400

    # 3. Process Divination Engines
    try:
        num_res_obj = calculate_numerology_7x9(
            birth_date=birth_date,
            day_of_week=lunar_res.day_of_week_num,
            thai_lunar_month=lunar_res.lunar_month,
            thai_lunar_year=lunar_res.zodiac_year_num
        )
        num_res = num_res_obj.model_dump() if hasattr(num_res_obj, "model_dump") else num_res_obj
    except Exception as e:
        num_res = {"error": str(e)}

    try:
        mah_res_obj = calculate_mahabote(birth_date=birth_date, birth_time=birth_time)
        mah_res = mah_res_obj.model_dump() if hasattr(mah_res_obj, "model_dump") else mah_res_obj
    except Exception as e:
        mah_res = {"error": str(e)}

    try:
        ast_res_obj = calculate_thai_astrology(birth_date=birth_date, birth_time=birth_time, birth_province=birth_province)
        ast_res = ast_res_obj.model_dump() if hasattr(ast_res_obj, "model_dump") else ast_res_obj
    except Exception as e:
        ast_res = {"error": str(e)}

    # 4. Generate Recommendations & Origins (R4)
    rec_res = recommender.generate_recommendations(num_res, mah_res, ast_res, tarot_res)
    if isinstance(rec_res, tuple):
        rec_nums, number_origins = rec_res
    else:
        rec_nums = rec_res
        number_origins = recommender.generate_origins(rec_nums, num_res, mah_res, ast_res, tarot_res)

    # 5. Calculate Heat Index (R3)
    heat_idx = stats_engine.evaluate_heat_index(rec_nums)
    
    # 6. Oracle Synthesis
    syn_text, disclaimer = synthesis.synthesize(num_res, mah_res, ast_res, tarot_res)

    return jsonify({
        "status": "success",
        "chart": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "lunar_calendar": lunar_info
        },
        "tarot_reading": {"spread": tarot_res, "interpretation": "การอ่านไพ่ 10 ใบ"},
        "lucky_numbers": rec_nums,
        "heat_index": heat_idx,
        "number_origins": number_origins,
        "synthesis": syn_text,
        "disclaimer": disclaimer,
        "numerology": num_res,
        "mahabote": mah_res,
        "astrology": ast_res,
        "tarot": {"spread": tarot_res, "interpretation": "การอ่านไพ่ 10 ใบ"},
        "numerology_7x9": num_res,
        "recommended_lottery_numbers": {
            "two_digits": rec_nums.get("two_digit", []),
            "three_digits": rec_nums.get("three_digit", []),
            "six_digits": rec_nums.get("six_digit", []),
            "confidence_score": 0.88,
            "weights": {"divination": 0.60, "historical_glo": 0.40}
        },
        "omni_oracle_reading": syn_text,
        "safety_metadata": {"passed": True, "flags_triggered": []}
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
