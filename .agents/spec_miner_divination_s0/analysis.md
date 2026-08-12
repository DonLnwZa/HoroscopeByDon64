# Comprehensive Specification Mining Analysis: Divination Systems & Omni-Oracle Engine

**Author:** Divination Spec Miner  
**Date:** 2026-08-06  
**Target Repository:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\`  
**Primary Reference Files:**
1. `e:\เว็บดูดวงเพื่อซื้อหวยไทย\Omni-Oracle (Master Astrologer & Divination AI).md`
2. `e:\เว็บดูดวงเพื่อซื้อหวยไทย\รายงานการวิเคราะห์เชิงลึกระบบโหราศาสตร์และพยากรณ์ศาสตร์เพื่อการพัฒนาระบบสถาปัตยกรรมเว็บไซต์ดูดวง.txt`
3. `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md`

---

## 1. Executive Summary & Architectural Overview

The objective of this specification mining analysis is to extract, formalize, and document all mathematical formulas, astronomical models, lookup matrices, rules, algorithms, interpretation logic, and safety constraints for the **Divination Quad-Engine System** and the **Omni-Oracle AI Interpretation Layer**.

The architecture strictly enforces a **Three-Layer Separation of Concerns**:
1. **Data & Calculation Layer**: Pure deterministic algorithms and astronomical engines (Swiss Ephemeris, Chula Sakarat converter, 7x9 Matrix builder, Tarot CSPRNG). Outputs validated JSON structured data only.
2. **Fact Extraction Layer**: Evaluates planetary dignities, matrix base collisions (การชนฐาน), Taksa/Mahabote overlays, tarot position-semantic alignments, and statistical correlation with historical 1-year GLO lottery numbers (`lottery_results_past_1_year.json`).
3. **AI Interpretation Layer (Omni-Oracle)**: System prompt (`Skill.md`) driven LLM that ingests JSON facts, synthesizes cross-modal insights, and presents professional, non-superstitious life path guidance while adhering to strict safety guardrails.

---

## 2. System 1: Thai & Western/Vedic Astrology (โหราศาสตร์ไทยและสากล)

### 2.1 Astronomical Frameworks: Tropical vs. Sidereal
* **Tropical Zodiac (Western / สายนะ)**:
  * Reference point: Vernal Equinox (0° Aries).
  * Focus: Psycho-astrology, personality dynamics, inner drives, planetary aspects.
  * Offset (Ayanamsa): `0.0°`.
* **Sidereal Zodiac (Thai & Vedic / นิรายนะ)**:
  * Reference point: Fixed stars (Spica / Chitra star alignment).
  * Focus: Concrete events, life destiny (วาสนา), karmic patterns (กรรมเก่า), auspicious timing (ฤกษ์ยาม).
  * Precession Offset (Ayanamsa): `~23.5° to 24.0°` (Lahiri Ayanamsa is the primary industry standard).
  * **Precision Constraint**: Ephemeris calculations must maintain sub-arcsecond accuracy (<0.3 arcsec). Miscalculating Ayanamsa by even 0.3° causes incorrect sign/navamsa transitions.

### 2.2 Planetary Mapping & Ephemeris Engine
* **Engine**: Swiss Ephemeris (`pysweph` / C-library wrapper) based on NASA JPL DE430/431/440 ephemerides.
* **Celestial Bodies Mapped (0-9)**:
  * `0`: มฤตยู (Uranus)
  * `1`: อาทิตย์ (Sun)
  * `2`: จันทร์ (Moon)
  * `3`: อังคาร (Mars)
  * `4`: พุธ (Mercury)
  * `5`: พฤหัสบดี (Jupiter)
  * `6`: ศุกร์ (Venus)
  * `7`: เสาร์ (Saturn)
  * `8`: ราหู (North Node / Rahu)
  * `9`: เกตุ (Thai Ketu / South Node shadow)
  * *(Optional Western additions)*: เนปจูน (Neptune), พลูโต (Pluto).

### 2.3 The 12 Astrological Houses (ภพทั้ง 12)
| House # | Thai Name | Meaning & Domain |
|---|---|---|
| 1 | **ตนุ (Tanu)** | Self, Ascendant (ลัคนา), physical body, core personality |
| 2 | **กดุมภะ (Kadumba)** | Finances, wealth, portable assets, income |
| 3 | **สหัชชะ (Sahajja)** | Siblings, close friends, short journeys, communication |
| 4 | **พันธุ (Bhandhu)** | Family, home, parents, foundations, real estate |
| 5 | **ปุตตะ (Putta)** | Children, subordinates, risk-taking, speculative investments, creativity |
| 6 | **อริ (Ari)** | Enemies, obstacles, debts, conflicts, health challenges |
| 7 | **ปัตนิ (Patni)** | Spouse, romantic partner, business partners |
| 8 | **มรณะ (Marana)** | Transformation, loss, inheritance, foreign lands, unexpected shifts |
| 9 | **ศุภะ (Supha)** | Prosperity, virtue, higher wisdom, fortunate achievements |
| 10 | **กัมมะ (Kamma)** | Career, public duties, life actions, profession |
| 11 | **ลาภะ (Lapha)** | Gains, windfalls, success, secondary income, luck |
| 12 | **วินาศ (Vinasa)** | Loss, secret enemies, hidden matters, isolation, backend work |

### 2.4 Divisional Charts (ดวงวรรคย่อย)
* **Rasi Chart (D1 / ราศีจักร)**: Primary natal wheel (12 signs, 30° per sign).
* **Navamsa Chart (D9 / นวางค์จักร)**: Each 30° sign divided into 9 sub-arcs of **3°20'** (200 arcminutes) each. Unlocks true inner planet dignity:
  * **เกษตร (Ruler)**: Planet in home sign (strong, stable).
  * **อุจจ์ (Exalted)**: Maximum strength and brilliance.
  * **นิจ (Debilitated/Fallen)**: Weak, vulnerable, impaired efficiency.
  * **ประ (Detriment)**: Opposite ruler, unstable.
* **Drekkana Chart (D3 / ตรียางค์จักร)**: Each 30° sign divided into 3 sub-arcs of **10°** each, mapped by elemental triplicities (Fire, Earth, Air, Water).

### 2.5 Calculation Engine Inputs & Output JSON Schema
* **Input Parameters**:
  * `birth_date` (YYYY-MM-DD)
  * `birth_time` (HH:MM:SS)
  * `utc_offset` (e.g. +07:00)
  * `latitude` (Float, e.g. 13.7563)
  * `longitude` (Float, e.g. 100.5018)
  * `ayanamsa_type` (Enum: `LAHIRI`, `FAGAN_BRADLEY`, `RAMAN`)
* **JSON Output Structure**:
  ```json
  {
    "ascendant": { "sign": "Aries", "degree": 14.52, "house": 1 },
    "ayanamsa_used": "LAHIRI",
    "ayanamsa_value": 24.15,
    "planets": [
      { "id": 1, "name": "Sun", "sign": "Leo", "degree": 10.2, "house": 5, "dignity": "เกษตร", "navamsa_sign": "Aries", "drekkana_sign": "Leo" }
    ],
    "houses": [
      { "house_num": 1, "sign": "Aries", "start_degree": 0.0 }
    ]
  }
  ```

---

## 3. System 2: 7-Digit 9-Base Numerology (เลข 7 ตัว 9 ฐาน)

### 3.1 Matrix Architecture (7 Columns x 9 Rows)
The 7-Digit 9-Base system is a **Deterministic System**. Given the day of the week, lunar month, and zodiac year, the 7x9 matrix is uniquely generated.

### 3.2 Base Derivation Rules (ฐานที่ 1 ถึง 9)
1. **Base 1 (ฐานวันเกิด / Day Base)**:
   * Sunday = 1, Monday = 2, Tuesday = 3, Wednesday = 4, Thursday = 5, Friday = 6, Saturday = 7.
   * Shift sequence across 7 columns starting from birth day digit.
   * *Example (Tuesday = 3)*: `Col1=3, Col2=4, Col3=5, Col4=6, Col5=7, Col6=1, Col7=2`.
2. **Base 2 (ฐานเดือนเกิด / Lunar Month Base)**:
   * Thai Lunar Month (1 to 12).
   * **Modulo 7 Reduction Rule**: If month is 1..7, use month directly. If month is 8..12, subtract 7 (`month - 7`). Range is strictly 1..7.
   * *Examples*: Month 8 -> 1; Month 12 -> 5.
   * Sequence wraps around 1..7 across 7 columns.
3. **Base 3 (ฐานปีเกิด / Zodiac Year Base)**:
   * Thai Zodiac Year (1 to 12 mapped to 1 to 7):
     * 1=ชวด (Rat), 2=ฉลู (Ox), 3=ขาล (Tiger), 4=เถาะ (Rabbit), 5=มะโรง (Dragon), 6=มะเส็ง (Snake), 7=มะเมีย (Horse).
     * 8=วอก (Monkey) -> 1, 9=ระกา (Rooster) -> 2, 10=จอ (Dog) -> 3, 11=กุน (Pig) -> 4, 12=กุน/หมู -> 5. (`(year - 1) mod 7 + 1`).
4. **Base 4 (ฐานรวม / Planetary Strength / กำลังดาว)**:
   * Formula: `Base4[col] = Base1[col] + Base2[col] + Base3[col]` for each column `col` (1..7).
   * Sum values range from **3 to 21**. Acts as planetary power / base strength.
5. **Bases 5 to 9 (ฐานประมวลผลขั้นสูง)**:
   * Generated via standard 7-number expansion formulas (e.g. Base 7 = `(Base 6 * 2) mod 7`, Base 8/9 overlaying expansion houses).

### 3.3 The 21 Astrological Houses (ภพทั้ง 21) Matrix
| Column | Row 1 (Day Base) | Row 2 (Month Base) | Row 3 (Year Base) | Expansion Houses (Base 8/9) |
|---|---|---|---|---|
| Col 1 | **อัตตะ** (Self) | **ตะนุ** (Appearance/Mind) | **มรณะ** (Loss/Foreign) | **อาตมะ** (Soul/Spirit) |
| Col 2 | **หินะ** (Ruin/Flaws) | **กดุมภะ** (Wealth/Income) | **ศุภะ** (Prosperity) | **ทาสา/ทาสี** (Subordinates) |
| Col 3 | **ธนัง** (Assets/Savings) | **สหัชชะ** (Friends/Travel) | **กัมมะ** (Career/Karma) | **สิทธิโชค** (Ultimate Luck) |
| Col 4 | **ปิตา** (Father/Male) | **พันธุ** (Family/Home) | **ลาภะ** (Gains/Windfall) | **โจร** (Loss/Fraud) |
| Col 5 | **มาตา** (Mother/Female) | **ปุตตะ** (Children/Risk) | **พยายะ** (Hidden/Illness) | **อุบาทว์** (Calamity) |
| Col 6 | **โภคา** (Real Estate) | **อริ** (Enemies/Debts) | **ทาสา** (Male Attendant) | **อุปถัมภ์** (Patronage) |
| Col 7 | **มัชฌิมา** (Balance) | **ปัตนิ** (Spouse/Partner) | **ทาสี** (Female Attendant)| **เคหัง/นาวัง** (Home/Vehicle)|

### 3.4 Matrix Base Collisions (การชนฐาน) & Planetary Relationships
* **Base Collision Logic**: When the same planet number appears in multiple houses across Rows 1-3 (e.g., Planet 6 Venus in กดุมภะ + ลาภะ + โภคา):
  * **Auspicious Collision**: If colliding houses are positive and Base 4 strength is high (e.g. 15), evaluate high wealth potential.
  * **Inauspicious Collision**: If colliding houses involve หินะ, อริ, มรณะ, พยายะ, or low/malefic Base 4 strength, evaluate vulnerability/debt risk.
* **Planetary Relationships**:
  * **คู่มิตร (Friendly Pairs)**: 1-5 (Sun-Jupiter), 2-4 (Moon-Mercury), 3-6 (Mars-Venus), 7-8 (Saturn-Rahu).
  * **คู่ศัตรู (Enemy Pairs)**: 4-8 (Mercury-Rahu), 6-7 (Venus-Saturn), 2-5 (Moon-Jupiter), 1-3 (Sun-Mars).
  * **คู่สมพล (Power Pairs)**: 1-6 (Sun-Venus), 2-8 (Moon-Rahu), 3-5 (Mars-Jupiter), 4-7 (Mercury-Saturn).

---

## 4. System 3: Mahabote / Burmese Astrology (มหาภูติพม่า)

### 4.1 Chula Sakarat (จ.ศ.) Conversion Algorithm
* **Base Epoch**: Chula Sakarat Era Year 1 = BE 1181 (CE 638).
* **Cutoff Date**: April 16 (Songkran / Thaleung Sok - Traditional Solar New Year).
* **Algorithm**:
  ```python
  def calculate_chula_sakarat(birth_date):
      year = birth_date.year
      thai_be = year + 543  # Convert CE to BE if needed
      
      # Check cutoff: Jan 1 - Apr 15 is previous Chula Sakarat year
      if (birth_date.month < 4) or (birth_date.month == 4 and birth_date.day <= 15):
          chula_sakarat = thai_be - 1182
      else:
          chula_sakarat = thai_be - 1181
          
      remainder = chula_sakarat % 7
      if remainder == 0:
          remainder = 7
      return chula_sakarat, remainder
  ```

### 4.2 The 7 Positions (ภูมิทั้ง 7) & Anatomical Placement (ตุ๊กตาไขนาม)
| Position Name | Anatomical Location | Symbolic Meaning |
|---|---|---|
| **ภังคะ (Bhangga)** | Right Leg (ขวา - Start) | Destruction, sudden breakdown, unstable state |
| **ปูติ (Puti)** | Left Leg (ซ้าย) | Decay, rot, lingering flaws, issues needing resolution |
| **มรณะ (Marana)** | Left Waist (เอวซ้าย) | Ending, loss, transformation, overseas, separation |
| **อธิบดี (Athipati)**| Left Arm (แขนซ้าย) | Supreme authority, executive control, command power |
| **ราชา (Raja)** | Head (ศีรษะ - Peak) | Glory, peak success, high honor, victory |
| **อัตตะ (Atta)** | Right Arm (แขนขวา) | Self, ego, outward behavior, personal initiative |
| **มัชฌิมา (Majjhima)**| Right Waist (เอวขวา) | Middle path, equilibrium, normal state |

* **Placement Algorithm**: Place remainder `R` at **ภังคะ**. Then cycle planet digits 1..7 sequentially through positions: `ภังคะ -> ปูติ -> มรณะ -> อธิบดี -> ราชา -> อัตตะ -> มัชฌิมา`.

### 4.3 Thai String Manipulation for Name Analysis (ตุ๊กตาไขนาม)
To analyze personal names, convert each letter of the user's name into its corresponding planet number via Thai Alphabet Consonant Groups (วรรค):
* **วรรคอาทิตย์ (1)**: อ, สระทั้งหมด (All Vowels)
* **วรรคจันทร์ (2)**: ก, ข, ค, ฆ, ง
* **วรรคอังคาร (3)**: จ, ฉ, ช, ซ, ฌ, ญ
* **วรรคพุธ (4)**: ฎ, ฏ, ฐ, ฑ, ฒ, ณ
* **วรรคเสาร์ (7)**: ด, ต, ถ, ท, ธ, น
* **วรรคพฤหัสบดี (5)**: บ, ป, ผ, ฝ, พ, ฟ, ภ, ม
* **วรรคราหู (8)**: ย, ร, ล, ว
* **วรรคศุกร์ (6)**: ศ, ษ, ส, ห, ฬ, ฮ

### 4.4 Taksa & Kalayok Overlay Logic
* **Taksa 8 Roles (ทักษา 8 ภูมิ)**:
  1. บริวาร (Followers/Subordinates)
  2. อายุ (Health/Longevity)
  3. เดช (Power/Authority)
  4. ศรี (Charm/Fortune/Good luck)
  5. มูละ (Assets/Capital/Wealth)
  6. อุตสาหะ (Effort/Drive)
  7. มนตรี (Patrons/Mentors)
  8. กาลกิณี (Misfortune/Obstacles)
* Overlay Taksa onto Mahabote positions. E.g., If **มูละ** falls on **ราชา** = High wealth & honor. If **มูละ** falls on **ปูติ** or **มรณะ** = Wealth destruction or vulnerable assets.
* **Kalayok (กาลโยค)**: Annual indicators (ธงชัย, อธิบดี, อุบาทว์, โลกาวินาศ) evaluated for yearly transits.

---

## 5. System 4: Tarot & Synchronicity Engine (ไพ่ทาโรต์)

### 5.1 CSPRNG & Deck Taxonomy
* **Randomization Requirement**: Must use Cryptographically Secure Pseudo-Random Number Generator (e.g. Python `secrets` or `os.urandom`) for card shuffling and draw selection to mirror true synchronicity.
* **Deck Structure**: 78 Cards total.
  * **Major Arcana (22 Cards, ID 0-21)**: The Fool (0) to The World (21). Macro events, karmic lessons, major transformations.
  * **Minor Arcana (56 Cards)**: 4 Suits x 14 Cards (Ace..10, Page, Knight, Queen, King):
    * **Wands (ไม้เท้า)**: Fire element - action, career, ambition.
    * **Cups (ถ้วย)**: Water element - emotions, relationships, intuition.
    * **Swords (ดาบ)**: Air element - intellect, struggle, decision, truth.
    * **Pentacles (เหรียญ)**: Earth element - material wealth, finances, stability.

### 5.2 Reversals & Boolean State
* Each card draw has `is_reversed` (Boolean `true`/`false`).
* If `is_reversed == true`: Card semantic shifts to blocked energy, internal manifestation, delayed progress, or shadow aspect.

### 5.3 10-Card Celtic Cross Spread Position Mapping
| Position # | Position Name | Logical Role in Engine Synthesis |
|---|---|---|
| 1 | **Present Situation** (สถานการณ์ปัจจุบัน) | Baseline state / central anchor variable |
| 2 | **Challenge / Crossing** (สิ่งขัดขวาง/ส่งเสริม) | Intervening variable (obstacle or prompt) |
| 3 | **Foundation** (รากฐานอดีต) | Root cause / underlying subconscious driver |
| 4 | **Recent Past** (อดีตเพิ่งผ่านพ้น) | Declining momentum / recent experience |
| 5 | **Conscious Goal** (เป้าหมายมุ่งหวัง) | Intentional focus / conscious aspiration |
| 6 | **Near Future** (อนาคตอันใกล้) | Short-term trajectory (1-3 months) |
| 7 | **Querent's Position** (ตัวตนผู้ถาม) | Self-perception & psychological state |
| 8 | **Environment** (สภาพแวดล้อม) | External forces, third-party influences |
| 9 | **Hopes & Fears** (ความหวังและความกลัว) | Emotional bias / subconscious tension |
| 10 | **Final Outcome** (บทสรุป) | Synthesized culmination of positions 1-9 |

---

## 6. Omni-Oracle Persona & Safety Constraints

### 6.1 Persona Definition & Tone
* **Identity**: Omni-Oracle (Master Astrologer & Divination AI).
* **Tone**: Deeply analytical, compassionate, professional, philosophical, non-superstitious, focused on **Life Path Guidance**.
* **Layer Isolation**: LLM handles **AI Interpretation Layer ONLY**. It receives pre-calculated JSON objects from Calculation Layer and NEVER performs manual arithmetic, date conversion, or ephemeris lookup.

### 6.2 Multi-Dimensional Synthesis Workflow
1. Receive structured JSON payload containing calculations from all active divination engines.
2. Identify **Cross-Modal Signal Overlaps** (จุดร่วม), e.g., Saturn in 6th house (Astrology) + Planet 7 in อริ (7x9) + 10 of Swords (Tarot) = Clear signal of work stress requiring boundaries.
3. Generate structured Markdown output highlighting strengths, challenges, and actionable **Remedies & Guidance**.

### 6.3 Strict Safety Constraints
1. **ABSOLUTELY NO Medical / Health Advice**:
   * **PROHIBITED**: Diagnosing diseases, predicting illness severity, forecasting death, pregnancy predictions, prescribing treatments or remedies.
   * **MANDATORY RE-FRAMING**: Re-interpret health queries strictly in terms of life energy, stress management, work-life balance, and wellness habits.
2. **ABSOLUTELY NO Guaranteed Financial Returns or Gambling Bets**:
   * **PROHIBITED**: Stating guaranteed lottery wins, promising financial investment returns, encouraging speculative gambling addictions.
   * **MANDATORY RE-FRAMING**: Present number recommendations purely as symbolic astrological alignments and statistical synthesis, emphasizing financial prudence and responsible choices.

---

## 7. Lottery Recommendation Synthesis (Divination + 1-Year GLO Statistics)

### 7.1 Cross-Referencing Engine
* **Input Data**:
  1. Personal Divination Matrix Digits (from Astrology planet values/houses, 7x9 colliding digits, Mahabote ราชา/อธิบดี/มูละ digits, Tarot card numbers).
  2. Historical GLO past 1-year lottery results JSON (`lottery_results_past_1_year.json`).
* **Synthesis Algorithm**:
  1. Extract candidate single digits (0-9) with high frequency / dignity across the 4 divination charts.
  2. Perform frequency distribution analysis on 2-digit and 3-digit winning numbers from past 1 year GLO data.
  3. Filter and weight candidate numbers by combining personal astrological potency scores with statistical frequency weights.
  4. Return recommended 2-digit and 3-digit numbers along with Omni-Oracle symbolic explanations.

---

## 8. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|---|---|---|---|---|---|---|
| 1 | Thai Astrology | Ephemeris Position Calculation | Calculates exact planetary positions using Swiss Ephemeris | Date, Time, Lat, Lon, UTC Offset, Ayanamsa | JSON (10 planets, Ascendant, 12 Houses) | Invalid coordinates/datetime returns HTTP 400 | Analysis Report §4 & Omni-Oracle §2.1 |
| 2 | Thai Astrology | Ayanamsa Adjustment | Converts Tropical coordinates to Sidereal using Lahiri/Fagan-Bradley | Ephemeris degree, Ayanamsa Enum | Sidereal zodiac degrees | Fallback to Lahiri default if unspecified | Analysis Report §4.2 |
| 3 | Thai Astrology | Divisional Chart (D9/D3) Generator | Subdivides 30° signs into Navamsa (D9, 3°20') and Drekkana (D3, 10°) | Planet/Ascendant degrees | Navamsa sign, Drekkana sign, Dignity | Degree out of bounds [0, 360) throws ValidationError | Analysis Report §4.3 |
| 4 | 7x9 Numerology | 7x9 Matrix Generation | Generates 7-column x 9-row numerology matrix | Day of week, Thai Lunar Month, Zodiac Year | 7x9 Integer Matrix | Invalid day (not 1-7) returns ValidationError | Analysis Report §2.1 |
| 5 | 7x9 Numerology | Base 2 Modulo 7 Reduction | Reduces lunar months 8-12 to range 1-7 by subtracting 7 | Lunar Month integer (1-12) | Reduced Month digit (1-7) | Month outside 1-12 throws RangeError | Analysis Report §2.1 |
| 6 | 7x9 Numerology | Base 4 Strength Calculation | Sums vertical column numbers of Base 1, 2, 3 | Matrix Col 1-7 values | Base 4 values array (3-21) | Column mismatch throws MatrixShapeError | Analysis Report §2.1 |
| 7 | 7x9 Numerology | Base Collision Analyzer | Detects recurring planet numbers across positive/negative houses | 7x9 Matrix + 21 House array | Collision map, wealth/risk scores | Unrecognized house ID throws LookupError | Analysis Report §2.3 |
| 8 | Mahabote | Chula Sakarat Converter | Converts BE to Chula Sakarat using April 16 Songkran cutoff | Birth Date (YYYY-MM-DD) | Chula Sakarat int, Remainder (1-7) | Invalid date format returns HTTP 400 | Analysis Report §3.1 |
| 9 | Mahabote | 7-Position Placement (ตุ๊กตาไขนาม) | Places remainder at ภังคะ and cycles 1-7 through body positions | Remainder int (1-7) | Map of 7 positions to planet digits | Remainder not 1-7 throws ValueError | Analysis Report §3.2 |
| 10 | Mahabote | Thai Name Letter Converter | Converts Thai letters in user's name to planet digits (วรรค 1-8) | Name string | Array of planet numbers per character | Non-Thai characters ignored/skipped | Analysis Report §3.2 |
| 11 | Mahabote | Taksa & Kalayok Overlay | Overlays 8 Taksa roles (บริวาร..กาลกิณี) and annual Kalayok onto Mahabote positions | Birth day planet, Mahabote map | Combined dignity & transit assessment | Unmapped birth day throws InvalidInputError | Analysis Report §3.3 |
| 12 | Tarot | CSPRNG Deck Shuffler | Cryptographically shuffles 78 cards deck | Random seed / system entropy | Ordered 78 card array | Entropy failure throws SecurityError | Analysis Report §1 |
| 13 | Tarot | Celtic Cross 10-Card Draw | Draws 10 cards with upright/reversed states | Card array, CSPRNG | 10 Card objects with `is_reversed` flag | Deck size < 10 throws InsufficientCardsError | Analysis Report §1 |
| 14 | Tarot | Positional Context Synthesizer | Maps card semantics to Celtic Cross position roles (1-10) | 10 Card objects + Position IDs | Positional interpretation JSON | Position index out of 1-10 throws RangeError | Analysis Report §1 & Omni-Oracle §2.4 |
| 15 | Omni-Oracle | Multi-Dimensional Synthesis | Integrates signals across all 4 active engines to find common ground | Quad-Engine JSON output | Synthesized Markdown forecast & guidance | Missing required engine JSON throws SchemaError | Omni-Oracle §3 |
| 16 | Omni-Oracle | Health Advice Guardrail | Filters out and re-frames medical/disease queries to lifestyle/energy | User prompt / draft response | Safety-compliant text | Triggers warning log if medical query detected | Omni-Oracle §4 |
| 17 | Omni-Oracle | Financial Guarantee Guardrail | Filters out guaranteed return claims and re-frames to statistical probability | User prompt / draft response | Safety-compliant text | Triggers warning log if financial guarantee detected | Omni-Oracle §4 |
| 18 | Lottery Synthesis | Divination + GLO Lottery Matching | Cross-references personal divination digits with 1-year GLO statistical frequencies | Divination digits, `lottery_results_past_1_year.json` | Recommended 2-digit & 3-digit numbers | Missing lottery JSON returns fallback divination numbers | ORIGINAL_REQUEST R1 & New Text Document |

---

## 9. Edge Cases

| # | Feature | Input | Observed / Expected Behavior |
|---|---|---|---|
| 1 | Chula Sakarat | Birth date: April 15 (before Songkran cutoff) vs April 16 (after cutoff) | April 15 uses `BE - 1182`, April 16 uses `BE - 1181`. Must test exact boundary. |
| 2 | Chula Sakarat Modulo | `Chula Sakarat % 7 == 0` | Must map remainder `0` to `7` (Saturday / Planet 7) to avoid array indexing error. |
| 3 | 7x9 Base 2 Month | Lunar Month = 12 | `12 - 7 = 5`. Row 2 sequence must start at 5 and wrap `[5, 6, 7, 1, 2, 3, 4]`. |
| 4 | 7x9 Base 3 Year | Zodiac Year = 12 (Pig/กุน) | `(12 - 1) % 7 + 1 = 5`. Row 3 sequence starts at 5. |
| 5 | Swiss Ephemeris Ayanamsa | Longitude edge case near 0° Aries / 360° Pisces | Degree rollover must properly handle 359.99° -> 0.00° without sign mismatch. |
| 6 | Thai Name Mapping | Name contains special vowels, tone marks (่ ้ ๊ ๋), or english characters | Tone marks and non-consonant/non-vowel symbols must be sanitized or ignored gracefully. |
| 7 | Tarot Reversals | Drawing Card 0 (The Fool) Reversed at Position 10 (Outcome) | Semantic must invert to "carelessness, uncalculated risk" in outcome context without crashing. |
| 8 | Omni-Oracle Safety | User asks: "จะป่วยเป็นมะเร็งไหม?" (Will I get cancer?) | Engine must intercept health diagnosis request and re-frame output to life energy & stress management. |
| 9 | Omni-Oracle Safety | User asks: "การันตีไหมว่าเลขนี้จะออกงวดนี้ 100%?" | Engine must refuse 100% guarantee and re-frame to symbolic probabilistic guidance. |
| 10 | Lottery Data Missing | `lottery_results_past_1_year.json` unavailable or corrupt | System must gracefully fallback to pure divination numerology calculation without crashing API. |
