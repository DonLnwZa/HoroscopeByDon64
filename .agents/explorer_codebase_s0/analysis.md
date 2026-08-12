# Project Baseline Analysis & Codebase Exploration Report

**Agent Identity:** Codebase & Environment Explorer (`explorer_codebase_s0`)  
**Working Directory:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_codebase_s0`  
**Workspace Root:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย`  
**Date:** 2026-08-06  

---

## 1. Executive Summary

This report documents the baseline investigation of the workspace at `e:\เว็บดูดวงเพื่อซื้อหวยไทย`, the external lottery data source directory at `e:\ข้อมูลผลหวยย้อนหลัง 1 ปี\fetch_lottery`, and the domain specifications for the **Omni-Oracle Thai Lottery Divination Web Application**.

### Key Findings
1. **Workspace Baseline:** The project root `e:\เว็บดูดวงเพื่อซื้อหวยไทย` contains 3 key foundation documents (`New Text Document.txt`, `Omni-Oracle (Master Astrologer & Divination AI).md`, and `รายงานการวิเคราะห์เชิงลึกระบบโหราศาสตร์และพยากรณ์ศาสตร์...txt`) alongside `.agents` metadata. The target application directory `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app` is not yet created and must be scaffolded.
2. **Historical Lottery Dataset:** Located at `e:\ข้อมูลผลหวยย้อนหลัง 1 ปี\fetch_lottery\lottery_results_past_1_year.json` (alongside `fetch_lottery.py`, `lottery_results_past_1_year.csv`, and `README.md`). Contains 24 complete draws (4,802 lines of structured JSON) spanning 1 full year of Thai Government Lottery (GLO) results.
3. **Fetch Script Mechanics:** `fetch_lottery.py` is a zero-dependency Python script that queries GLO's official POST endpoint (`https://www.glo.or.th/api/checking/getLotteryResult`), automatically accounting for date shifts (holiday postponements) and outputting UTF-8 JSON and UTF-8-BOM CSV files.
4. **Core Divination & Persona Specification:** The application integrates 4 divination sciences (Astrology, 7-Number 9-Base Numerology, Burmese Mahabote, and Tarot) under the strict **Omni-Oracle** persona constraints (Life Path Guidance, No Medical Advice, No Financial/Gambling Guarantees).
5. **Development & TDD Baseline:** Development must adhere strictly to TDD (Red -> Green -> Refactor) using Pytest for Backend (Python) and modern testing tools for Frontend (Next.js / React).

---

## 2. Detailed Workspace & Directory Breakdown

### 2.1 Project Root (`e:\เว็บดูดวงเพื่อซื้อหวยไทย`)

| File / Folder | Size / Type | Description |
| --- | --- | --- |
| `.agents/` | Directory | System metadata directory holding agent briefings, dispatches, progress logs, and handoffs. |
| `New Text Document.txt` | 1,170 bytes | User prompt notes, slash commands reference, URI link to external data script, and key project goals. |
| `Omni-Oracle (Master Astrologer & Divination AI).md` | 8,717 bytes | System persona & analytical module logic specification for Omni-Oracle AI across all 4 divination branches. |
| `รายงานการวิเคราะห์เชิงลึกระบบโหราศาสตร์และพยากรณ์ศาสตร์เพื่อการพัฒนาระบบสถาปัตยกรรมเว็บไซต์ดูดวง.txt` | 46,263 bytes | Comprehensive research report detailing mathematical formulas, 21 houses, Burmese Chula Sakarat algorithm, ephemeris calculations, Tarot spreads, and AI interpretation architecture. |

### 2.2 Target App Directory (`e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app`)
- **Status:** **Not Yet Created** (Baseline state).
- **Action Required:** Will be scaffolded by subsequent implementation phase into a dual backend/frontend project structure.

### 2.3 Historical Lottery Data Directory (`e:\ข้อมูลผลหวยย้อนหลัง 1 ปี\fetch_lottery`)

| File | Size | Description |
| --- | --- | --- |
| `fetch_lottery.py` | 9,742 bytes | Standalone Python script that automatically fetches and parses 1 year of historical GLO lottery results. |
| `lottery_results_past_1_year.json` | 83,878 bytes | Clean structured JSON array containing 24 historical draws from the past year. |
| `lottery_results_past_1_year.csv` | 16,039 bytes | Tabular CSV export formatted with UTF-8-BOM (`utf-8-sig`) for Excel analysis. |
| `README.md` | 5,848 bytes | Technical documentation explaining GLO API specifications, data structures, and script usage. |

---

## 3. Data Schema: `lottery_results_past_1_year.json`

The JSON file contains an array of objects, where each object represents a single lottery draw.

### Schema Specification
```json
[
  {
    "draw_date": "YYYY-MM-DD",
    "youtube_url": "https://www.youtube.com/watch?v=...",
    "pdf_url": "https://api.glo.or.th/utility/file/download/...",
    "prize_1st": "XXXXXX",
    "prize_last2": "XX",
    "prize_last3f": ["XXX", "XXX"],
    "prize_last3b": ["XXX", "XXX"],
    "prize_near1": ["XXXXXX", "XXXXXX"],
    "prize_2nd": ["XXXXXX", "XXXXXX", "XXXXXX", "XXXXXX", "XXXXXX"],
    "prize_3rd": ["XXXXXX", ... 10 items],
    "prize_4th": ["XXXXXX", ... 50 items],
    "prize_5th": ["XXXXXX", ... 100 items]
  }
]
```

### Field Definitions
- **`draw_date`** (`string`, ISO 8601 `YYYY-MM-DD`): Draw date (e.g., `"2025-08-01"`).
- **`youtube_url`** (`string`, URL): Official YouTube broadcast link for the draw.
- **`pdf_url`** (`string`, URL): Official GLO PDF certificate download link.
- **`prize_1st`** (`string`, 6 digits): 1st prize winning number.
- **`prize_last2`** (`string`, 2 digits): 2-digit bottom prize winning number.
- **`prize_last3f`** (`array of string`, 3 digits each, 2 items): 3-digit front winning numbers.
- **`prize_last3b`** (`array of string`, 3 digits each, 2 items): 3-digit back winning numbers.
- **`prize_near1`** (`array of string`, 6 digits each, 2 items): Adjacent 1st prize winning numbers (`1st - 1` and `1st + 1`).
- **`prize_2nd`** (`array of string`, 6 digits each, 5 items): 2nd prize winning numbers.
- **`prize_3rd`** (`array of string`, 6 digits each, 10 items): 3rd prize winning numbers.
- **`prize_4th`** (`array of string`, 6 digits each, 50 items): 4th prize winning numbers.
- **`prize_5th`** (`array of string`, 6 digits each, 100 items): 5th prize winning numbers.

---

## 4. Fetch Script Mechanics (`fetch_lottery.py`)

1. **Endpoint & Protocol:**
   - URL: `https://www.glo.or.th/api/checking/getLotteryResult`
   - Method: `POST`
   - Payload: `{"date": "DD", "month": "MM", "year": "YYYY"}` (where year is Gregorian/ค.ศ. string e.g. `"2026"`).
2. **Date Scanner Logic:**
   - Scans 13 past calendar months from current execution date.
   - For each month, tests potential draw dates: `[1, 2, 3, 16, 17, 18]` (to capture holiday shifts e.g. May 2nd instead of May 1st).
   - Special handling for December: adds `[29, 30, 31]` (to capture New Year shift to Dec 30th).
3. **Data Parsing & Deduplication:**
   - Filters duplicate draw responses matching `draw_date`.
   - Sorts chronologically from oldest to newest.
4. **Dependencies:**
   - Zero third-party dependencies (`urllib.request`, `json`, `csv`, `datetime`, `time`).

---

## 5. Divination Sciences & Omni-Oracle Persona Architecture

### 5.1 The 4 Divination Sciences
1. **Thai & Western Astrology (โหราศาสตร์):**
   - Planetary positions (10 planets), Ascendant (ลัคนาราศี), 12 Houses (ภพตนุ ถึง วินาศ), Sidereal (Vedic/Thai) & Tropical (Western) zodiac, Navamsa (D9).
2. **7-Number 9-Base Numerology (เลข 7 ตัว 9 ฐาน):**
   - 7x9 Matrix generation based on Birth Day (Base 1), Birth Month (Base 2), Birth Year/Zodiac (Base 3).
   - Base 4 (Sum of Base 1+2+3), Bases 5-9 calculation.
   - Mapping across 21 Astrological Houses (อัตตะ, ตะนุ, กดุมภะ, ฯลฯ).
3. **Burmese Mahabote (มหาภูติพม่า):**
   - Chula Sakarat (จ.ศ.) calculation: `(B.E. - 1181) % 7` or `(A.D. - 638) % 7`.
   - 7 Positions (ภังคะ, ปูติ, มรณะ, อธิบดี, ราชา, อัตตะ, มัชฌิมา).
   - Taksa (ทักษา) and Kalayok (กาลโยค) overlays.
4. **Tarot Spreads (ไพ่ทาโรต์):**
   - 78 Cards (22 Major Arcana + 56 Minor Arcana), Upright/Reversed states.
   - Spreads: Celtic Cross (10 positions) for deep multi-dimensional analysis.

### 5.2 Strict Omni-Oracle Persona Rules
- **Tone:** Professional, profound, compassionate, philosophical, rational, life-path focused (non-superstitious).
- **Rule 1 (No Medical Advice):** Absolute prohibition on diagnosing illness, predicting death/pregnancy, or offering medical advice. Health questions must be reframed into general vitality/lifestyle context.
- **Rule 2 (No Financial Guarantees):** Absolute prohibition on guaranteeing lottery wins or financial investments. Recommendations are presented as symbolic alignment and statistically correlated numbers based on birth energy.

---

## 6. Development Environment & Tooling Audit

- **Operating System:** Windows OS (PowerShell environment).
- **Python Ecosystem:**
  - Python 3+ runtime.
  - Package Management: `uv` / `pip` / `venv`.
  - Testing Framework: `pytest` (for Backend TDD).
- **Node.js / Web Ecosystem:**
  - Node.js runtime (npm, pnpm, yarn available).
  - Framework: Next.js / React (TypeScript).
  - UI Styling: Tailwind CSS, Framer Motion animations, Glassmorphism aesthetic.

---

## 7. Next Steps & Recommendations for Implementation

1. **Scaffold `omni_oracle_app` Workspace:**
   - Create `omni_oracle_app/backend` (FastAPI + Pytest + Pydantic).
   - Create `omni_oracle_app/frontend` (Next.js + React + Tailwind CSS).
2. **Integrate Historical Data:**
   - Copy or link `lottery_results_past_1_year.json` into backend data directory for statistical matching algorithms.
3. **TDD Workflow Execution:**
   - Define backend interfaces and test cases (`test_divination.py`, `test_lottery_stats.py`, `test_omni_oracle.py`).
   - Implement calculation engines for 4 divination sciences and statistical matching logic.
   - Build Next.js UI with Glassmorphism aesthetic and integrate with API.
