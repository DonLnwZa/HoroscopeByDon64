# Architecture & TDD Specification Report
**Project:** Omni-Oracle Thai Lottery Horoscope App (`omni_oracle_app`)  
**Specification Miner:** Architecture & TDD Spec Miner (`spec_miner_arch_s0`)  
**Date:** 2026-08-06  
**Status:** Completed & Verified  

---

## 1. Executive Summary & Architectural Overview

The **Omni-Oracle Thai Lottery Horoscope App** is a high-precision, multidimensional astrological and numerological platform. It synthesizes 4 core divination systems (**Thai & Western Astrology**, **7-Number 9-Base Numerology**, **Burmese Mahabote**, and **Tarot & Synchronicity**) and correlates their lucky output patterns with **1-year historical Thai Government Lottery (GLO) statistics** (`lottery_results_past_1_year.json`) to recommend personalized lottery numbers.

The system is strictly governed by the **Omni-Oracle Persona** (deep philosophical insight, non-superstitious life path guidance) and **Safety Guardrails** (zero medical advice, zero financial/investment guarantees). The entire application is designed using **Test-Driven Development (TDD)** principles, establishing clean seams (public interfaces) before writing implementation code.

---

## 2. System Architecture (3-Layer Backend Model)

To eliminate LLM calculation hallucinations and guarantee 100% mathematical accuracy, the backend is split into three decoupled operational layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      1. Data & Calculation Layer                        │
│   (Swiss Ephemeris, 7x9 Matrix Engine, Mahabote CS%7, Tarot CSPRNG)     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ Deterministic JSON Data
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  2. Fact Extraction & Lottery Matcher                   │
│ (Planetary Dignities, 7x9 Collisions, 1-Year GLO Stat Correlation)      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ Fact Map + Matched Numbers
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  3. AI Interpretation & Safety Layer                    │
│   (Omni-Oracle Synthesis LLM + Regex/Semantic Safety Guardrail Filter)  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Backend API Specification (Python - FastAPI)

### 3.1 Directory Structure (`omni_oracle_app/backend`)

```text
omni_oracle_app/
└── backend/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py                     # FastAPI app initialization & OpenAPI config
    │   ├── config.py                   # Pydantic BaseSettings (ENV configuration)
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── routes.py               # API Endpoints (/predict, /lottery/history, /health)
    │   │   └── middleware.py           # Safety Guardrail & Exception Handler Middleware
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   ├── request.py              # Birthdate & Request Pydantic v2 Models
    │   │   └── response.py             # Horoscopes & Lottery Pydantic v2 Models
    │   ├── engines/
    │   │   ├── __init__.py
    │   │   ├── astrology.py            # Natal Chart & Planetary Positions Engine
    │   │   ├── numerology_7x9.py       # 7x9 Matrix & House Collision Engine
    │   │   ├── mahabote.py             # Burmese Mahabote & 7-Position Matrix Engine
    │   │   └── tarot.py                # CSPRNG Tarot Deck & Celtic Cross Engine
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── lottery_matcher.py      # 1-Year Historical GLO Lottery Matcher Engine
    │   │   ├── omni_oracle.py          # Omni-Oracle LLM Interpretation Service
    │   │   └── safety_guardrail.py     # Safety Constraint Filter & Validator
    │   └── data/
    │       └── lottery_results_past_1_year.json # Historical GLO Lottery Data (24 draws)
    └── tests/
        ├── conftest.py                 # Pytest fixtures, test client, mock LLM setup
        ├── test_astrology.py
        ├── test_numerology.py
        ├── test_mahabote.py
        ├── test_tarot.py
        ├── test_lottery_matcher.py
        ├── test_safety_guardrails.py
        └── test_api_routes.py
```

---

### 3.2 Request & Response JSON Schemas (Pydantic v2)

#### Request Schema: `PredictRequestSchema`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PredictRequestSchema",
  "type": "object",
  "properties": {
    "birthdate": {
      "type": "string",
      "format": "date",
      "description": "User birthdate in ISO YYYY-MM-DD format",
      "example": "1995-08-15"
    },
    "birth_time": {
      "type": "string",
      "pattern": "^([0-1][0-9]|2[0-3]):[0-5][0-9]$",
      "description": "User birth time in HH:MM format (24-hour)",
      "default": "12:00",
      "example": "08:30"
    },
    "name": {
      "type": "string",
      "description": "User full name for Tukata Kai Nam letter analysis",
      "example": "สมชาย ใจดี"
    },
    "card_selection_seed": {
      "type": ["integer", "null"],
      "description": "Optional integer seed for deterministic Tarot card generation during testing",
      "default": null,
      "example": 42
    },
    "branches": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["astrology", "numerology_7x9", "mahabote", "tarot"]
      },
      "default": ["astrology", "numerology_7x9", "mahabote", "tarot"],
      "description": "Divination systems to include in reading"
    }
  },
  "required": ["birthdate"]
}
```

#### Response Schema: `PredictResponseSchema`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PredictResponseSchema",
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "request_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "user_profile": {
      "type": "object",
      "properties": {
        "birthdate": { "type": "string" },
        "day_of_week": { "type": "string", "example": "Tuesday" },
        "thai_zodiac_year": { "type": "string", "example": "Pig" },
        "chula_sakarat": { "type": "integer", "example": 1357 }
      },
      "required": ["birthdate", "day_of_week", "thai_zodiac_year", "chula_sakarat"]
    },
    "divination_summary": {
      "type": "object",
      "properties": {
        "astrology": { "type": "object" },
        "numerology_7x9": { "type": "object" },
        "mahabote": { "type": "object" },
        "tarot": { "type": "object" }
      }
    },
    "omni_oracle_reading": {
      "type": "object",
      "properties": {
        "persona": { "type": "string", "default": "Omni-Oracle (Master Astrologer & Divination AI)" },
        "life_path_guidance": { "type": "string", "description": "Markdown text with deep philosophical insight" },
        "strengths_and_talents": { "type": "array", "items": { "type": "string" } },
        "challenges_and_remedies": { "type": "array", "items": { "type": "string" } }
      },
      "required": ["persona", "life_path_guidance", "strengths_and_talents", "challenges_and_remedies"]
    },
    "lottery_recommendations": {
      "type": "object",
      "properties": {
        "primary_6digit": { "type": "string", "pattern": "^[0-9]{6}$", "example": "835492" },
        "top_3digit": { "type": "array", "items": { "type": "string", "pattern": "^[0-9]{3}$" }, "example": ["492", "549", "354"] },
        "bottom_2digit": { "type": "array", "items": { "type": "string", "pattern": "^[0-9]{2}$" }, "example": ["92", "49", "54"] },
        "lucky_single_digits": { "type": "array", "items": { "type": "integer" }, "example": [2, 4, 9, 5] },
        "confidence_score": { "type": "number", "minimum": 0.0, "maximum": 1.0, "example": 0.88 },
        "matching_logic_explanation": { "type": "string" }
      },
      "required": ["primary_6digit", "top_3digit", "bottom_2digit", "lucky_single_digits", "confidence_score", "matching_logic_explanation"]
    },
    "safety_meta": {
      "type": "object",
      "properties": {
        "passed_safety_check": { "type": "boolean" },
        "sanitized": { "type": "boolean" },
        "disclaimer": { "type": "string" }
      },
      "required": ["passed_safety_check", "sanitized", "disclaimer"]
    }
  },
  "required": ["success", "request_id", "timestamp", "user_profile", "omni_oracle_reading", "lottery_recommendations", "safety_meta"]
}
```

---

### 3.3 Backend Seams (Public Python Interfaces)

| Interface Seam | Module File | Signature | Description |
|----------------|-------------|-----------|-------------|
| `calculate_natal_chart` | `app/engines/astrology.py` | `calculate_natal_chart(birthdate: date, birth_time: time, lat: float = 13.75, lon: float = 100.50) -> NatalChartData` | Calculates Sidereal planet coordinates, Ascendant, and D9 Navamsa dignities. |
| `build_7x9_matrix` | `app/engines/numerology_7x9.py` | `build_7x9_matrix(day_num: int, lunar_month: int, zodiac_year: int) -> Matrix7x9Data` | Generates 7x9 matrix, computes Base 4 planet strength, and finds house collision points (การชนฐาน). |
| `calculate_mahabote` | `app/engines/mahabote.py` | `calculate_mahabote(birthdate: date, name: str = "") -> MahaboteData` | Calculates Chula Sakarat % 7, populates 7 positions (ภังคะ..มัชฌิมา), Taksa, and Tukata Kai Nam scores. |
| `draw_celtic_cross` | `app/engines/tarot.py` | `draw_celtic_cross(seed: Optional[int] = None) -> CelticCrossData` | Draws 10 cards using CSPRNG (`secrets` module or seeded RNG), resolving upright/reversed status. |
| `match_lottery` | `app/services/lottery_matcher.py` | `match_lottery(astro: NatalChartData, num7x9: Matrix7x9Data, mahabote: MahaboteData, tarot: CelticCrossData, history: List[LotteryDraw]) -> LotteryMatchResult` | Synthesizes lucky digits across 4 systems and matches with 1-year GLO lottery frequency statistics. |
| `validate_and_sanitize` | `app/services/safety_guardrail.py` | `validate_and_sanitize(reading_text: str) -> SafetyResult` | Scans prediction text against medical/financial violation regex patterns; redacts or re-prompts if needed. |
| `synthesize_reading` | `app/services/omni_oracle.py` | `synthesize_reading(divination_bundle: DivinationBundle, matched_lottery: LotteryMatchResult) -> OmniOracleOutput` | Formats prompt with Omni-Oracle persona rules, invokes LLM, and formats Markdown response. |

---

## 4. Historical Lottery Matcher Architecture & Algorithm

### 4.1 Data Input (`lottery_results_past_1_year.json`)
The GLO historical dataset contains 24 bi-monthly lottery draws over 1 year (e.g. 1st of month and 16th of month). Each record contains:
- `draw_date`: string (ISO Date)
- `first_prize`: string (6 digits, e.g. `"123456"`)
- `three_digit_front`: array of 2 strings (3 digits each)
- `three_digit_back`: array of 2 strings (3 digits each)
- `two_digit_bottom`: string (2 digits, e.g. `"89"`)

### 4.2 Mathematical Matching Algorithm

1. **Astrological Lucky Digit Extraction ($W_{\text{astro}}(d)$):**
   - **Astrology:** Ascendant lord planet digit ($d_{\text{asc}}$), D9 exalted planet digits (+3 weight).
   - **7x9 Numerology:** Planet digits colliding across **กดุมภะ (Wealth)** + **ลาภะ (Windfall)** + **โภคา (Property)** (+4 weight). Base 4 planet digits (+2 weight).
   - **Burmese Mahabote:** Planet digits in **ราชา (King)** and **อธิบดี (Chief)** positions (+3 weight). Taksa **ศรี** and **มูละ** digits (+2 weight).
   - **Tarot:** Major Arcana card numbers reduced to single digits (modulo 10 or numerology reduction) (+1 weight).
   - Aggregate normalized weight vector: $W_{\text{astro}}(d)$ for $d \in \{0..9\}$.

2. **1-Year GLO Historical Frequency Analysis ($W_{\text{hist}}(d)$):**
   - Compute digit frequency distribution across all 1st prizes, 3-digit front/back, and 2-digit bottom over 24 draws.
   - Position-specific digit probability $P_{\text{pos}}(d, k)$ for digit position $k \in \{1..6\}$.
   - 2-digit ending frequency matrix $F_{2D}(ij)$ for $ij \in 00..99$.
   - 3-digit ending frequency matrix $F_{3D}(ijk)$ for $ijk \in 000..999$.

3. **Composite Scoring & Combination Generation:**
   - Single digit score: $S(d) = 0.6 \cdot W_{\text{astro}}(d) + 0.4 \cdot W_{\text{hist}}(d)$. Top 4 single digits selected.
   - 2-digit pair score: $S_{2D}(ij) = S(i) \cdot S(j) \cdot (1 + \log(1 + F_{2D}(ij)))$. Top 3 2-digit combinations selected.
   - 3-digit set score: $S_{3D}(ijk) = S(i) \cdot S(j) \cdot S(k) \cdot (1 + \log(1 + F_{3D}(ijk)))$. Top 3 3-digit combinations selected.
   - 6-digit primary prize assembly: Position-wise greedy assignment maximizing $P_{\text{pos}}(d, k) \cdot S(d)$ constrained by selected top 3-digit and 2-digit components.

---

## 5. Frontend Architecture & Design Specifications (Next.js/React)

### 5.1 Technology Stack & Dependencies
- **Framework:** Next.js 14+ (App Router, TypeScript)
- **UI Components & Styling:** Tailwind CSS v3/v4, Framer Motion (for smooth cosmic card flips, glowing aura animations, floating wheel rotation), Lucide React Icons
- **State Management:** React Context API + `useReducer`
- **Testing Setup:** Vitest + React Testing Library (`@testing-library/react`, `@testing-library/jest-dom`), Mock Service Worker (`msw`)

---

### 5.2 Aesthetics & Theme Guidelines
- **Theme Name:** *Mystic Obsidian & Celestial Gold*
- **Color Palette:**
  - Background Base: `#0B0F19` (Deep Space Dark)
  - Card Glassmorphism: `rgba(19, 14, 38, 0.6)` (`backdrop-blur-xl`, `border border-amber-500/20`)
  - Accent Gold (Lucky Highlight): `#F59E0B` / `#FBBF24` (Celestial Gold Gradient)
  - Accent Teal (Astrology Glow): `#06B6D4` (Astral Cyan)
  - Text Primary: `#F8FAFC` (Slate 50), Text Secondary: `#94A3B8` (Slate 400)
- **Visual Style:**
  - Glassmorphic translucent cards with subtle gold-glowing borders (`hover:shadow-[0_0_25px_rgba(245,158,11,0.25)]`).
  - Animated birthdate entry card with pulsing starlight background particles.
  - Interactive Tarot Card Flip Component (3D perspective transform with Framer Motion).

---

### 5.3 Frontend Component Breakdown

```text
src/
├── app/
│   ├── layout.tsx                      # Root layout with Dark/Mystic background
│   ├── page.tsx                        # Main landing & prediction page
│   └── globals.css                     # Custom Tailwind glassmorphism styles
├── components/
│   ├── Navbar.tsx                      # Header with logo & system status badge
│   ├── BirthdateForm.tsx               # Birthdate, time, name input & submit form
│   ├── BranchSelector.tsx              # Divination branch chips (Astrology, 7x9, Mahabote, Tarot)
│   ├── LoadingOracle.tsx               # Mystical particle loading animation
│   ├── PredictionDisplay.tsx           # Main results view wrapper
│   ├── OmniOracleReadingCard.tsx       # Markdown rendered life-path guidance
│   ├── DivinationGrid.tsx              # Collapsible 4-branch summary cards
│   ├── LotteryTicketCard.tsx           # Premium glowing Thai GLO lottery ticket display
│   ├── TarotPicker.tsx                 # Interactive 3D card flip Tarot spread viewer
│   └── DisclaimerFooter.tsx            # Mandatory Omni-Oracle safety disclaimer
├── services/
│   └── api.ts                          # Fetch client for /api/v1/horoscope/predict
└── tests/
    ├── BirthdateForm.test.tsx          # Form validation & input tests
    ├── LotteryTicketCard.test.tsx      # Lottery display component unit tests
    └── PredictionFlow.test.tsx         # Full user flow integration test with MSW
```

---

## 6. Safety Guardrails Specification (Omni-Oracle Constraints)

### 6.1 Requirements & Rules
Per requirement **R3** and **Acceptance Criteria (Safety Constraints)**:
1. **No Medical Advice:** System MUST NOT issue disease diagnosis, medical treatment recommendations, mortality/death predictions, or pregnancy timing promises. Medical/health queries must be sanitized into general vitality, lifestyle balance, or stress management advice.
2. **No Financial Guarantees:** System MUST NOT promise 100% lottery win guarantees ("ถูกหวย 100%", "การันตีรางวัลที่ 1"), financial windfall assurances, or encourage reckless gambling.

---

### 6.2 Implementation Architecture (`SafetyGuardrailMiddleware` & `SafetyValidator`)

```python
# Regex filter patterns for safety validator
FORBIDDEN_HEALTH_PATTERNS = [
    r"รักษาโรค", r"วินิจฉัย", r"โรคร้าย", r"มะเร็ง", r"ผ่าตัด", 
    r"การตั้งครรภ์", r"เสียชีวิต", r"ความตาย", r"ติดเชื้อ", r"ยารักษา"
]

FORBIDDEN_FINANCIAL_PATTERNS = [
    r"ถูกหวย 100%", r"การันตี", r"รับประกัน", r"รวยแน่นอน", 
    r"รางวัลที่ 1 100%", r"ไม่มีทางพลาด", r"คืนเงิน"
]
```

#### Sanitization Logic:
1. If LLM-generated interpretation output triggers any health or financial pattern, the `SafetyValidator` replaces the violative sentence with a compliant Omni-Oracle life-path guidance phrasing.
2. Every API response automatically appends a mandatory `safety_meta` payload:
   ```json
   {
     "passed_safety_check": true,
     "sanitized": false,
     "disclaimer": "คำเตือน: Omni-Oracle ให้แนวทางชีวิตเชิงปรัชญาและสถิติ ไม่ใช่คำแนะนำทางการแพทย์หรือการประกันผลตอบแทนทางการเงิน โปรดใช้พิจารณญาณ"
   }
   ```

---

## 7. Test-Driven Development (TDD) Strategy

### 7.1 Red -> Green -> Refactor Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          1. RED STAGE                                   │
│  Write failing pytest/vitest assertions against Public Interface Seams  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ Run test -> FAIL (Interface defined)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         2. GREEN STAGE                                  │
│ Write minimal engine/component code required to make tests PASS          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ Run test -> PASS
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        3. REFACTOR STAGE                                │
│ Optimize algorithms, improve typing, format code, clean architecture    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 7.2 Public Seams & TDD Test File Mapping

| Seam Component | Test File Location | Primary Assertions | Test Runner Command |
|----------------|-------------------|--------------------|---------------------|
| Astrology Engine | `backend/tests/test_astrology.py` | Ascendant degree precision, Sidereal planetary signs, D9 Navamsa dignities | `pytest backend/tests/test_astrology.py` |
| 7x9 Numerology Engine | `backend/tests/test_numerology.py` | Matrix dimensions (7x9), Base 4 planetary strength sum, house collisions | `pytest backend/tests/test_numerology.py` |
| Mahabote Engine | `backend/tests/test_mahabote.py` | Chula Sakarat algorithm (`พ.ศ. - 1181/1182`), 7 position mapping, Taksa overlay | `pytest backend/tests/test_mahabote.py` |
| Tarot Engine | `backend/tests/test_tarot.py` | 10-card Celtic Cross spread, zero duplicate card selection, seed determinism | `pytest backend/tests/test_tarot.py` |
| Historical Lottery Matcher | `backend/tests/test_lottery_matcher.py` | 6-digit primary output format (`^[0-9]{6}$`), score calculation, JSON integration | `pytest backend/tests/test_lottery_matcher.py` |
| Safety Guardrails | `backend/tests/test_safety_guardrails.py` | Rejection of forbidden medical & financial guarantee phrases, disclaimer inclusion | `pytest backend/tests/test_safety_guardrails.py` |
| REST API Routes | `backend/tests/test_api_routes.py` | HTTP 200 JSON schema validation for `/predict`, HTTP 422 for invalid date | `pytest backend/tests/test_api_routes.py` |
| Frontend Form | `frontend/tests/BirthdateForm.test.tsx` | Date input validation, submit event handling, loading state triggers | `npx vitest run frontend/tests/BirthdateForm.test.tsx` |
| Frontend Ticket Card | `frontend/tests/LotteryTicketCard.test.tsx` | Rendering 6-digit primary number, 3-digit top, 2-digit bottom, styling | `npx vitest run frontend/tests/LotteryTicketCard.test.tsx` |

---

## 8. Discovered Features & Edge Cases

### 8.1 Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Backend Core | Multi-Branch Horoscopic Synthesis | Computes natal chart, 7x9 numerology, Mahabote, and Tarot spreads simultaneously for a single user birthdate. | `birthdate` (YYYY-MM-DD), `birth_time` (HH:MM), `name` (string) | Aggregate `DivinationSummary` JSON | Returns HTTP 422 Unprocessable Entity if birthdate is invalid or in future. | `ORIGINAL_REQUEST.md` & `รายงาน...txt` |
| 2 | Backend Divination | Chula Sakarat Boundary Adjustment | Automatically adjusts Chula Sakarat calculation (`พ.ศ. - 1181` vs `พ.ศ. - 1182`) based on Songkran boundary (April 16). | `birthdate` date object | `chula_sakarat` integer | Fallback to default `พ.ศ. - 1181` if month/day is ambiguous. | `รายงาน...txt` Section 3.1 |
| 3 | Backend Divination | Tukata Kai Nam Name Scoring | Converts Thai name characters into planetary numeric values to score harmony with birth chart. | `name` string (Thai characters) | Name score & harmony indicator | Ignores non-Thai letters / spaces without throwing error. | `รายงาน...txt` Section 3.2 |
| 4 | Backend Divination | 7x9 Matrix House Collision | Identifies planetary numbers appearing in multiple key houses (e.g. กดุมภะ + ลาภะ + โภคา). | 3 base rows (Day, Month, Year) | Array of collision planet numbers & house names | Returns empty collision array if no planets collide across key houses. | `รายงาน...txt` Section 2.3 |
| 5 | Backend Engine | Seeded Tarot Spread Generator | Allows passing optional RNG seed to produce deterministic Celtic Cross 10-card Tarot spreads for TDD testing. | `card_selection_seed` (int or null) | 10-card `CelticCrossData` array | Standard CSPRNG (`secrets` module) used if seed is null. | `รายงาน...txt` Section 1 |
| 6 | Backend Service | Historical GLO 1-Year Lottery Matcher | Correlates astrological lucky digits with 24 past GLO draws to recommend 6-digit, 3-digit, and 2-digit numbers. | `DivinationSummary`, `lottery_results_past_1_year.json` | `LotteryRecommendations` JSON | Fallback to astrological-only scoring if historical JSON file is missing or corrupted. | `ORIGINAL_REQUEST.md` R1 & `New Text Document.txt` |
| 7 | Backend Safety | Omni-Oracle Guardrail Filter | Validates LLM output text to block health/medical advice and financial guarantees. | `omni_oracle_reading` text | Cleaned text + `safety_meta` boolean flag | Redacts offending sentences and appends standard disclaimer if violations detected. | `ORIGINAL_REQUEST.md` R3 & `Omni-Oracle...md` |
| 8 | Frontend UI | Glassmorphism Mystic Dark Theme | Interactive UI with cosmic dark palette (`#0B0F19`), translucent blur cards, and celestial gold accents. | User interaction & prediction state | Animated React UI layout | Falls back to solid dark background if backdrop-filter is unsupported by browser. | `ORIGINAL_REQUEST.md` R2 |
| 9 | Frontend UI | 3D Tarot Card Flip Viewer | Interactive card-flipping interface displaying 10 Tarot cards in Celtic Cross arrangement with Framer Motion. | Card selection state | 3D animated card rotation & detail view | Simple flat card render if motion animations are reduced (`prefers-reduced-motion`). | `รายงาน...txt` Section 1 |
| 10 | Frontend Component | Glowing GLO Lottery Ticket Display | Visual representation of recommended lottery numbers rendered like an official Thai GLO ticket. | `lottery_recommendations` object | Rendered lottery ticket card component | Gracefully renders hyphenated placeholder (`------`) if numbers are unavailable. | `ORIGINAL_REQUEST.md` R2 |

---

### 8.2 Edge Cases
| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Chula Sakarat Engine | Birthdate on April 15 vs April 16 (Songkran Boundary) | Dates up to April 15 use `พ.ศ. - 1182` (pre-Songkran year); April 16 onwards use `พ.ศ. - 1181`. Correct year boundary guaranteed. |
| 2 | 7x9 Numerology Engine | Lunar Month 8 to 12 (Month > 7) | System subtracts 7 from month value (e.g. Month 8 becomes Month 1; Month 12 becomes Month 5) ensuring row 2 values never exceed 7. |
| 3 | Burmese Mahabote Engine | Modulo 7 calculation resulting in remainder 0 | Remainder 0 is automatically re-mapped to 7 (Saturday / Planet 7) to maintain valid 1-7 planetary indexing. |
| 4 | Tarot CSPRNG Engine | Rapid consecutive card draws | Cryptographically secure random generator prevents duplicate cards across a single 10-card Celtic Cross spread. |
| 5 | Historical Lottery Matcher | Historical lottery JSON has missing draw date or empty array | Matcher logs warning, falls back to pure astrological weight scoring, and returns confidence score 0.5 with explanation. |
| 6 | Safety Guardrail | User prompts directly asking "ฉีดวัคซีนดีไหม" or "การันตีถูกรางวัลที่ 1 ใช่ไหม" | Safety filter detects health/financial triggers, strips medical recommendations, replaces guarantee claims with probabilistic life guidance, and attaches disclaimer. |
| 7 | Frontend Form | User enters birthdate in the future (e.g. 2030-01-01) | Frontend validation prevents form submission; backend API returns HTTP 422 Unprocessable Entity with error message "Birthdate cannot be in the future". |
| 8 | Frontend Form | User omits birth time (defaults to missing/empty) | System automatically defaults birth time to `"12:00"` (Noon chart) and flags Ascendant calculation precision as estimated. |

---

## 9. Verification & Acceptance Criteria Matrix

| Requirement | Acceptance Criteria | Verification Method | Status |
|-------------|---------------------|---------------------|--------|
| **R1. Backend API** | FastAPI backend with `/api/v1/horoscope/predict` returning JSON containing 4-branch divination & lottery recommendations. | Execute `pytest backend/tests/test_api_routes.py` and inspect Pydantic JSON response. | Verified Spec |
| **R1. Lottery Matcher** | Correlate 4-branch outputs with 1-year historical GLO data (`lottery_results_past_1_year.json`). | Execute `pytest backend/tests/test_lottery_matcher.py` validating scoring & number generation. | Verified Spec |
| **R2. Frontend Design** | Next.js/React premium UI with Glassmorphism, Dark Theme, birthdate form, real-time prediction, and lottery card. | Run Vitest suite (`npx vitest run`) and visual layout check. | Verified Spec |
| **R3. Omni-Oracle Safety** | Zero medical advice, zero financial guarantees. Sanitization filter + safety metadata. | Execute `pytest backend/tests/test_safety_guardrails.py` with test payloads containing forbidden terms. | Verified Spec |
| **R4. TDD Strategy** | Red -> Green -> Refactor workflow. Tests for public seams created before implementation code. | Run full backend & frontend test suites with zero failures. | Verified Spec |
