# Analysis Report: 7-Digit 9-Base Numerology Engine (Sub-milestone M1.2)

**Author:** Explorer 1 (`.agents/explorer_m1_2_1`)  
**Target Engine File:** `omni_oracle_app/backend/app/engines/numerology_7x9.py`  
**Target Test Suite Seam:** `omni_oracle_app/backend/tests/test_numerology_7x9.py`  
**Date:** 2026-08-06  

---

## 1. Executive Summary

This report establishes the complete mathematical specification, domain logic, public API seam, and Pytest verification plan for the **7-Digit 9-Base Numerology Engine** (`numerology_7x9.py`) in accordance with Sub-milestone M1.2 of the Omni-Oracle project architecture.

The 7-Digit 9-Base system (วิชาเลข 7 ตัว 9 ฐาน) is a deterministic ancient Thai numerological system that maps birth parameters—Day of Week (1..7), Thai Lunar Month (1..12), and Thai Zodiac Year (1..12)—into a 9x7 matrix of planetary digits and house positions. The engine converts Gregorian birthdates to Thai calendar parameters, constructs the 9-base matrix, evaluates 21 astrological house collisions, calculates planetary strength values, and extracts auspicious digits for Layer 2 Composite Recommender.

---

## 2. Matrix Layout Architecture (7 Columns x 9 Bases)

The core data structure is a 9x7 integer matrix (`matrix[0..8][0..6]`) where columns $k \in \{0..6\}$ correspond to positions 1 through 7.

### 2.1 Base 1 to Base 3 Setup (Rows 1–3)

#### Base 1 (ฐานวันเกิด / Day of Week Base)
- **Input:** $D \in \{1..7\}$ (1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri, 7=Sat).
- **Column Formula ($k=0..6$):**
  $$v_{1, k} = ((D - 1 + k) \bmod 7) + 1$$
- **Values:** Sequence of 7 numbers starting from $D$, wrapping 1..7.
- **7 Houses (Row 1):**
  1. `อัตตะ` (Atta - Self/Identity)
  2. `หินะ` (Hina - Flaw/Misfortune)
  3. `ธนัง` (Thanang - Accumulated Wealth)
  4. `ปิตา` (Pita - Father/Male Patron)
  5. `มาตา` (Mata - Mother/Female Patron)
  6. `โภคา` (Phokha - Assets/Real Estate)
  7. `มัชฌิมา` (Majjhima - Middle Path/Neutral Status)

#### Base 2 (ฐานเดือนเกิด / Lunar Month Base)
- **Input:** $M \in \{1..12\}$ (Thai Lunar Month: 1=เดือน 1/อ้าย, 2=เดือน 2/ยี่, ..., 12=เดือน 12).
- **Reduction Formula:** $M' = ((M - 1) \bmod 7) + 1$ (Wraps months >7 into range 1..7).
- **Column Formula ($k=0..6$):**
  $$v_{2, k} = ((M' - 1 + k) \bmod 7) + 1$$
- **7 Houses (Row 2):**
  1. `ตะนุ` (Tanu - Personality/Appearance)
  2. `กดุมภะ` (Kadumba - Cash Flow/Income)
  3. `สหัชชะ` (Sahajja - Friends/Social Circle)
  4. `พันธุ` (Bandhu - Family/Relativity)
  5. `ปุตตะ` (Putta - Children/Speculation/Subordinates)
  6. `อริ` (Ari - Enemies/Obstacles/Debts)
  7. `ปัตนิ` (Patni - Spouse/Partner)

#### Base 3 (ฐานปีเกิด / Zodiac Year Base)
- **Input:** $Y \in \{1..12\}$ (Thai Zodiac Year: 1=ชวด/Rat, 2=ฉลู/Ox, ..., 12=กุน/Pig).
- **Reduction Formula:** $Y' = ((Y - 1) \bmod 7) + 1$ (Wraps year >7 into range 1..7).
- **Column Formula ($k=0..6$):**
  $$v_{3, k} = ((Y' - 1 + k) \bmod 7) + 1$$
- **7 Houses (Row 3):**
  1. `มรณะ` (Marana - Loss/Transmutation/Foreign Lands)
  2. `ศุภะ` (Subha - Prosperity/Elders/Growth)
  3. `กัมมะ` (Kamma - Career/Actions)
  4. `ลาภะ` (Labha - Fortune/Gains/Windfall)
  5. `พยายะ` (Phayaye - Hidden Issues/Illness/Secrets)
  6. `ทาสา` (Thasa - Male Subordinates)
  7. `ทาสี` (Thasi - Female Subordinates)

---

### 2.2 Base 4 to Base 9 Advanced Calculation Rules

| Base Index | Name (ชื่อฐาน) | Formula per Column $k \in \{0..6\}$ | Value Range | Interpretation / Significance |
|---|---|---|---|---|
| **Base 4** | ฐานรวมวัน-เดือน-ปี | $v_{4, k} = v_{1, k} + v_{2, k} + v_{3, k}$ | 3 to 21 | Column total power / Planetary strength basis |
| **Base 5** | ฐานวัน + เดือน | $v_{5, k} = v_{1, k} + v_{2, k}$ | 2 to 14 | Personality & Resource interaction |
| **Base 6** | ฐานวัน + ปี | $v_{6, k} = v_{1, k} + v_{3, k}$ | 2 to 14 | Karmic background & Life direction |
| **Base 7** | ฐานเดือน + ปี | $v_{7, k} = v_{2, k} + v_{3, k}$ | 2 to 14 | Subconscious ambition & Fortune foundation |
| **Base 8** | ฐานวัน + ฐานรวม | $v_{8, k} = v_{1, k} + v_{4, k}$ | 4 to 28 | Expansion & Secondary support base |
| **Base 9** | ฐานกำลังพระเคราะห์ | Planetary Strength of Col Digit / Base 4 | 6 to 21 | Astronomical / Numerological planetary power |

#### Base 9 Planetary Strength Lookup (กำลังพระเคราะห์)
In Thai numerology, primary numbers 1..7 (and special sums) map to planetary powers:
- **Digit 1 (อาทิตย์ / Sun):** Power = 6
- **Digit 2 (จันทร์ / Moon):** Power = 15
- **Digit 3 (อังคาร / Mars):** Power = 8
- **Digit 4 (พุธ / Mercury):** Power = 17
- **Digit 5 (พฤหัสบดี / Jupiter):** Power = 19
- **Digit 6 (ศุกร์ / Venus):** Power = 21
- **Digit 7 (เสาร์ / Saturn):** Power = 10
- **Digit 8 (ราหู / Rahu):** Power = 12
- **Digit 9 (เกตุ / Ketu):** Power = 9

---

### 2.3 Astrological House Mapping & Collision Logic (การชนฐาน / ชนภพ)

The 21 houses across Rows 1–3 are categorized into:

1. **Auspicious Houses (ภพมงคล / ภพโชคลาภ):**
   - `ลาภะ` (Windfall / Luck)
   - `กดุมภะ` (Financial Liquidity)
   - `ศุภะ` (Prosperity & Advancement)
   - `โภคา` (Property / Wealth)
   - `ธนัง` (Savings & Assets)

2. **Malefic / Afflicted Houses (ภพเสื่อม / ภพเสีย):**
   - `หินะ` (Flaw / Ruin)
   - `อริ` (Obstacles / Debts)
   - `มรณะ` (Loss / Endings)
   - `พยายะ` (Illness / Secrets)

#### House Collision Algorithm
For each digit $d \in \{1..7\}$, collect all house names across Rows 1–3 where $v_{row, col} == d$:
- If a digit appears in multiple Auspicious Houses (e.g. `กดุมภะ` + `ลาภะ` + `โภคา`) without malefic interference, it is selected as a **Primary Lucky Digit**.
- If a digit appears in Malefic Houses (e.g. `อริ` or `มรณะ`), its score is penalized.

#### Planetary Relationships (คู่ดาว)
- **Friendly Pairs (คู่มิตร):** 1-5, 2-4, 3-6, 7-8 (Enhance fortune score)
- **Enemy Pairs (คู่ศัตรู):** 4-8, 6-7, 2-5, 1-3 (Introduce conflict)
- **Power Pairs (คู่สมพล):** 1-6, 2-8, 3-5, 4-7 (Increase momentum)

---

## 3. Automatic Gregorian to Thai Date Conversion Formulas

The engine must support both automatic date parsing and explicit parameter overrides.

### 3.1 Thai Day of Week (1..7)
Given Gregorian `birth_date` parsed as `datetime.date`:
$$\text{day\_of\_week} = (\text{dt.weekday()} + 1) \bmod 7 + 1$$
- Sunday (`weekday() == 6`) $\rightarrow 1$
- Monday (`weekday() == 0`) $\rightarrow 2$
- Tuesday (`weekday() == 1`) $\rightarrow 3$
- Wednesday (`weekday() == 2`) $\rightarrow 4$
- Thursday (`weekday() == 3`) $\rightarrow 5$
- Friday (`weekday() == 4`) $\rightarrow 6$
- Saturday (`weekday() == 5`) $\rightarrow 7$

### 3.2 Thai Lunar Month (1..12)
- **Astronomical / Lunar Phase Calculation:**
  Elongation $E = (\lambda_{\text{moon}} - \lambda_{\text{sun}}) \bmod 360^\circ$.
  The Sun's tropical sign index $S_{\text{NM}}$ at the preceding New Moon determines the Thai Lunar Month:
  $$\text{thai\_lunar\_month} = ((S_{\text{NM}} - 7) \bmod 12) + 1$$
- **Fallback Deterministic Calendar Formula:**
  If astronomical ephemeris is not queried, Month 1 (เดือนอ้าย) begins in mid-November:
  $$\text{lunar\_month\_approx} = ((\text{dt.month} + 1) \bmod 12) + 1$$
- **Explicit Override:** If `thai_lunar_month` is provided in $[1..12]$, use it directly.

### 3.3 Thai Lunar Year / Zodiac (1..12)
- **Base Zodiac Formula:**
  $$Z_{\text{raw}} = ((\text{dt.year} - 4) \bmod 12) + 1$$
  - $1 = \text{ชวด (Rat)}$, $2 = \text{ฉลู (Ox)}$, ..., $12 = \text{กุน (Pig)}$.
- **Songkran / Thai New Year Cutoff Rule:**
  In Thai astrology, the Zodiac Year changes on **1st Waxing Day of Month 5 (ขึ้น 1 ค่ำ เดือน 5)**, which falls between late March and April 13-16.
  If birth date is before the Lunar New Year cutoff (e.g. Month 1..4 or before April 13), use previous Gregorian year's zodiac:
  $$Z_{\text{effective}} = ((\text{dt.year} - 5) \bmod 12) + 1$$
- **Explicit Override:** If `thai_lunar_year` is provided in $[1..12]$, use it directly.

---

## 4. Public Seam & Pytest Interface Design

### 4.1 Module Paths
- **Implementation File:** `omni_oracle_app/backend/app/engines/numerology_7x9.py`
- **Pytest Suite File:** `omni_oracle_app/backend/tests/test_numerology_7x9.py`

### 4.2 Signature
```python
def calculate_numerology_7x9(
    birth_date: str,
    day_of_week: Optional[int] = None,
    thai_lunar_month: Optional[int] = None,
    thai_lunar_year: Optional[int] = None,
) -> Numerology7x9Result:
    """
    Main entry point for 7-Digit 9-Base Numerology calculation.
    
    Parameters:
        birth_date: str (YYYY-MM-DD format)
        day_of_week: Optional[int] (1..7, 1=Sun..7=Sat)
        thai_lunar_month: Optional[int] (1..12)
        thai_lunar_year: Optional[int] (1..12, 1=Rat..12=Pig)
        
    Returns:
        Numerology7x9Result Pydantic model containing full 9x7 matrix,
        21 house mappings, house collisions, and extracted lucky digits.
    """
```

### 4.3 Pydantic Data Models

```python
class Numerology7x9Result(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    birth_date: str
    day_of_week: int = Field(..., ge=1, le=7)
    day_name_th: str
    thai_lunar_month: int = Field(..., ge=1, le=12)
    lunar_month_name_th: str
    thai_lunar_year: int = Field(..., ge=1, le=12)
    zodiac_year_name_th: str
    
    # 9x7 Matrix & Individual Base Rows
    matrix: List[List[int]]  # 9 rows, 7 columns
    base_1_row: List[int]
    base_2_row: List[int]
    base_3_row: List[int]
    base_4_row: List[int]
    base_5_row: List[int]
    base_6_row: List[int]
    base_7_row: List[int]
    base_8_row: List[int]
    base_9_row: List[int]

    # House Mappings & Collisions
    house_names: List[List[str]]  # 3 rows, 7 columns
    house_collisions: Dict[int, List[str]]
    auspicious_houses: List[str]
    afflicted_houses: List[str]

    # Lucky Digits output for Layer 2 Recommender
    primary_lucky_digit: int = Field(..., ge=1, le=7)
    secondary_lucky_digit: int = Field(..., ge=1, le=7)
    lucky_numbers: List[int]

    def get_cell(self, row: int, col: int) -> int:
        """Returns cell value at 1-indexed row (1..9) and col (1..7)."""
        return self.matrix[row - 1][col - 1]

    def get_house_name(self, row: int, col: int) -> str:
        """Returns house name at 1-indexed row (1..3) and col (1..7)."""
        return self.house_names[row - 1][col - 1]

    @property
    def auspicious_digits(self) -> List[int]:
        return self.lucky_numbers
```

---

## 5. Pytest Suite Design (`test_numerology_7x9.py`)

The test suite must validate all requirements under strict TDD principles:

1. **`test_data_models_and_enums`**:
   - Validates ranges, house names, and Pydantic constraints.
2. **`test_calculate_numerology_7x9_valid_input`**:
   - Verifies default run with `"1995-08-15"`.
   - Confirms matrix dimensions are exactly 9x7.
3. **`test_explicit_overrides`**:
   - Tests `day_of_week=3`, `thai_lunar_month=9`, `thai_lunar_year=12` overrides.
4. **`test_matrix_base_4_sum_and_wrapping`**:
   - Asserts `base_4_row[k] == base_1_row[k] + base_2_row[k] + base_3_row[k]`.
   - Asserts all elements in `base_1_row`, `base_2_row`, `base_3_row` are in range 1..7.
5. **`test_21_houses_and_collisions`**:
   - Confirms 21 house names are mapped correctly.
   - Confirms `house_collisions` maps digits 1..7 to lists of house names.
6. **`test_gregorian_to_thai_date_conversions`**:
   - Benchmarks known dates (e.g. 1995-08-15 -> Tuesday=3, Pig=12; 2026-08-05 -> Wednesday=4, Horse=7).
7. **`test_edge_cases_and_exceptions`**:
   - Asserts invalid date string raises `ValueError`.
   - Asserts out-of-bound `day_of_week` (e.g. 0 or 8) or `thai_lunar_month` (13) raises `ValueError`.
8. **`test_lucky_numbers_output`**:
   - Asserts `primary_lucky_digit` and `secondary_lucky_digit` are single digits in 1..7.
   - Asserts `lucky_numbers` contains single digits in 0..9 for composite recommender.

---

## 6. Conclusion & Implementation Readiness

The analysis confirms that the 7-Digit 9-Base Numerology Engine design is fully specified, mathematically sound, and ready for TDD implementation by the Implementer agent. All interfaces align seamlessly with project standards.
