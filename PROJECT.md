# Project: Omni-Oracle Thai Lottery Prediction Web Application Upgrade

## Architecture
- **Backend**: Flask Web Application located at `omni_oracle_app/backend/app.py`
  - Routes: `GET /`, `GET /api/health`, `GET /api/lottery/stats`, `POST /api/divine`
  - Engines (`omni_oracle_app/backend/app/engines/`):
    - `thai_astrology.py`: Computes planetary positions, Lagna, Labha lords.
    - `numerology_7x9.py`: Computes 7x9 Base grid and house collisions.
    - `mahabote.py`: Computes Mahabote Thanang, Phoka, Sri positions.
    - `tarot.py`: Maps 78 Tarot cards, draws Celtic Cross spread.
    - `lottery_stats.py`: Evaluates 24 historical draw records for win frequencies and Heat Index.
    - `number_recommender.py`: Combines engine outputs and tracks provenance / origins of recommended numbers.
    - `oracle_synthesis.py`: Synthesizes holistic divination reading.
  - Data: `omni_oracle_app/backend/data/lottery_results_past_1_year.json` (24 GLO draw records).
- **Frontend**: Single Page Application at `omni_oracle_app/frontend/index.html` + `app.jsx` + `styles.css`
  - Tech stack: React 18 + Babel Standalone + Framer Motion (glassmorphism UI theme).

## Feature Inventory
Every feature from user request is assigned to a milestone:

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | R1-Backend | Auto Thai Lunar Calendar calculation from `birth_date` + `birth_time` with Bangkok 6:00 AM cutoff rule (calculating day of week, lunar month 1-12, zodiac year 1-12) | M1 | ORIGINAL_REQUEST |
| 2 | R1-Frontend | Replace 3 manual select dropdowns in `app.jsx` with `<input type="time">` for `birth_time` and render auto-calculated lunar calendar output card | M2 | ORIGINAL_REQUEST |
| 3 | R2-Backend | `/api/divine` accepts `selected_tarot_cards` array of 10 integers (`0..77`) and passes them to `tarot_engine.draw_celtic_cross(selected_cards)` | M1 | ORIGINAL_REQUEST |
| 4 | R2-Frontend | Interactive 78 face-down Tarot card grid in `app.jsx` with visual selection states, card counter `เลือกไพ่แล้ว X / 10 ใบ`, submit validation (exactly 10 cards required), and sending `selected_tarot_cards` in POST request body | M2 | ORIGINAL_REQUEST |
| 5 | R3-Backend | Backtesting Heat Index algorithm in `lottery_stats.py` comparing recommended numbers against 24 historical GLO draw records and returning `heat_index` breakdown (`HOT`, `WARM`, `COLD`) in `/api/divine` payload | M1 | ORIGINAL_REQUEST |
| 6 | R3-Frontend | Heat Index badges display (win count & heat level color: 🔥 High, ⚡ Medium, ❄️ Rare) alongside recommended numbers in `app.jsx` | M2 | ORIGINAL_REQUEST |
| 7 | R4-Backend | Divination Transparency provenance tracking in `number_recommender.py` recording engine origins across 4 engines and returning `number_origins` in `/api/divine` payload | M1 | ORIGINAL_REQUEST |
| 8 | R4-Frontend | Divination Transparency tags display (e.g. 📍 *ที่มา: ฐาน 4 มหาภูติ + ไพ่ทาโรต์ใบที่ 3*) alongside recommended numbers in `app.jsx` | M2 | ORIGINAL_REQUEST |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Backend Engines & API Upgrade | Implement R1 auto Thai lunar calendar + 6am cutoff in backend, R2 Tarot index mapping in `tarot.py`, R3 Heat Index backtesting in `lottery_stats.py`, R4 Divination Transparency origin tracking in `number_recommender.py`, and update Flask `/api/divine` route contracts | none | DONE |
| M2 | Frontend UI Upgrade | Update `app.jsx` & `styles.css` for R1 `birth_time` input + lunar card, R2 78-card interactive deck grid + 10 card selection counter + submit validation, R3 Heat Index badges, R4 Divination Transparency origin tags | M1 | DONE |
| M3 | Final Milestone: E2E Integration & Coverage Hardening | Phase 1: Pass 100% of E2E test suite (Tiers 1-4). Phase 2: Tier 5 Adversarial Coverage Hardening with Challenger & Forensic Auditor | M1, M2 | DONE |

## Interface Contracts

### `POST /api/divine`

**Request Payload JSON**:
```json
{
  "full_name": "Somchai Jaidee",
  "birth_date": "1992-05-15",
  "birth_time": "05:30",
  "birth_province": "Bangkok",
  "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
}
```

**Response Payload JSON**:
```json
{
  "status": "success",
  "chart": {
    "birth_date": "1992-05-15",
    "birth_time": "05:30",
    "lunar_calendar": {
      "day_of_week": "Thursday",
      "lunar_month": 6,
      "zodiac_year": "Monkey",
      "cutoff_applied": true
    }
  },
  "tarot_reading": { ... },
  "lucky_numbers": {
    "two_digit": ["15", "84"],
    "three_digit": ["485", "792"],
    "six_digit": ["485792"]
  },
  "heat_index": {
    "two_digit": [
      {"number": "15", "win_count": 3, "level": "HOT"},
      {"number": "84", "win_count": 1, "level": "WARM"}
    ],
    "three_digit": [
      {"number": "485", "win_count": 0, "level": "COLD"},
      {"number": "792", "win_count": 2, "level": "HOT"}
    ],
    "six_digit": [
      {"number": "485792", "win_count": 0, "level": "COLD"}
    ]
  },
  "number_origins": {
    "15": ["Mahabote: Thanang + Phoka", "Thai Astrology: Lagna Lord 1"],
    "84": ["Tarot Card #3: The Empress", "Numerology 7x9: Base 4"],
    "485": ["Combined: Lagna 4 + Mahabote 85"],
    "792": ["Tarot Card #1: The Magician + Numerology 792"],
    "485792": ["Synthesis of Top Engine Predictions"]
  },
  "synthesis": "...",
  "disclaimer": "..."
}
```

## Code Layout
- Backend: `omni_oracle_app/backend/`
  - Server entry: `app.py`
  - Engines: `app/engines/` (`thai_astrology.py`, `numerology_7x9.py`, `mahabote.py`, `tarot.py`, `lottery_stats.py`, `number_recommender.py`, `oracle_synthesis.py`)
  - Data: `data/lottery_results_past_1_year.json`
  - Tests: `tests/`
- Frontend: `omni_oracle_app/frontend/`
  - HTML entry: `index.html`
  - Main app script: `app.jsx`
  - Stylesheet: `styles.css`
  - Component tests: `__tests__/`
- E2E Tests: `omni_oracle_app/e2e_tests/`
