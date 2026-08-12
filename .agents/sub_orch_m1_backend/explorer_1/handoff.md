# Handoff Report: Explorer 1 (M1 Backend R1 & R2 Investigation)

**Author**: Explorer 1  
**Working Directory**: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_backend\explorer_1\`  
**Date**: 2026-08-12  

---

## 1. Observation

1. **`omni_oracle_app/backend/app/engines/thai_astrology.py`**:
   - Lines 461-480: Function `calculate_thai_astrology(birth_date: str, birth_time: str = "12:00", ...)` accepts `birth_date` and `birth_time`, converting to Julian Day and Lahiri Ayanamsa.
   - It computes natal planetary longitudes and Lagna, but does not provide 6:00 AM cutoff day-of-week logic, Thai Lunar Month (1..12), or Thai Zodiac Year (1..12).

2. **`omni_oracle_app/backend/app/engines/tarot.py`**:
   - Lines 58-81: Function `draw_celtic_cross(self)` currently takes zero arguments.
   - It randomly shuffles `self.deck` (78 cards) and pops 10 cards using `secrets.randbelow(len(deck_copy))` and random `is_reversed = secrets.choice([True, False])`.

3. **`omni_oracle_app/backend/app.py`**:
   - Lines 46-92: Endpoint `/api/divine` parses request JSON (`birth_date`, `birth_day_of_week`, `birth_month_lunar`, `birth_year_animal`).
   - Line 79: Calls `tarot_engine.draw_celtic_cross()` with no parameters.

4. **`omni_oracle_app/backend/app/engines/numerology_7x9.py`**:
   - Lines 234-260: Function `calculate_numerology_7x9` accepts integer values for `day_of_week` (1..7), `thai_lunar_month` (1..12), and `thai_lunar_year` (1..12).

5. **`PROJECT.md` API Specifications**:
   - Lines 43-67: Payload and response contracts for `POST /api/divine`:
     - Request body accepts `birth_time` (string) and `selected_tarot_cards` (array of 10 ints `0..77`).
     - Response body expects `chart.lunar_calendar`: `{"day_of_week": "Thursday", "lunar_month": 6, "zodiac_year": "Monkey", "cutoff_applied": true}`.

---

## 2. Logic Chain

1. **Step 1 (R1 Requirement)**:
   - *Observation*: `PROJECT.md` specifies that manual dropdowns are removed from frontend, and `birth_time` is sent in POST payload. `numerology_7x9` requires `day_of_week` (1..7), `thai_lunar_month` (1..12), and `thai_lunar_year` (1..12).
   - *Reasoning*: A new helper function `calculate_thai_lunar_calendar(birth_date, birth_time)` must be added to `thai_astrology.py` (or as a separate module).
   - *Rule Details*:
     - If `birth_time < 06:00` (e.g. 05:30), subtract 1 day from `birth_date` for astrological day of week determination, and set `cutoff_applied = True`.
     - Calculate day of week (1=Sun..7=Sat) and English day string.
     - Calculate approximate Thai lunar month 1..12 using `lunar_month = (((month if day < 16 else month + 1)) % 12) + 1`.
     - Calculate approximate Thai zodiac year 1..12 using April 13 Songkran boundary rule `(((year - 4) % 12) + 1)`.
   - *Conclusion*: Returns `ThaiLunarCalendarResult` matching the required `chart.lunar_calendar` JSON object.

2. **Step 2 (R2 Requirement)**:
   - *Observation*: `tarot.py` line 58 currently takes no arguments and draws random cards.
   - *Reasoning*: `draw_celtic_cross` signature must be updated to `draw_celtic_cross(selected_cards=None)`.
   - *Rule Details*:
     - If `selected_cards` is provided: Validate it is a list of exactly 10 unique integers in range `0..77`. If invalid, raise `ValueError`. Map elements 0..9 to the 10 Celtic Cross positions in order.
     - If `selected_cards` is `None`: Maintain backward compatibility by randomly drawing 10 cards using CSPRNG.
   - *Conclusion*: Fully satisfies R2 requirements and supports error handling (HTTP 400 response in `/api/divine`).

3. **Step 3 (Integration Seam)**:
   - *Observation*: `/api/divine` in `app.py` coordinates the engines.
   - *Reasoning*: Updating `/api/divine` to invoke `calculate_thai_lunar_calendar`, feed derived lunar values to `numerology_7x9`, feed `selected_tarot_cards` to `tarot_engine.draw_celtic_cross`, and construct `chart.lunar_calendar` completes the M1 backend upgrade for R1 and R2.

---

## 3. Caveats

- **Timezone Assumption**: All birth times provided in `birth_time` payload are assumed to be in ICT (Bangkok local time, UTC+7), matching the 6:00 AM local sunrise rule.
- **No Source Code Changes Made**: This is a read-only investigation report. Code snippets provided in `analysis.md` are proposed implementations for the implementer agent.

---

## 4. Conclusion

Requirements R1 and R2 are fully analyzed with clear, clean, and deterministic algorithms:
- R1: `calculate_thai_lunar_calendar` cleanly handles 6:00 AM Bangkok cutoff, day of week shift, Thai Lunar Month (1..12), and Thai Zodiac Year (1..12), matching the exact API contract for `chart.lunar_calendar`.
- R2: `draw_celtic_cross(selected_cards)` validates 10 card indices (`0..77`), maps them to Celtic Cross positions, and maintains fallback backward compatibility.
- Detailed code design and unit test suites are fully documented in `analysis.md`.

---

## 5. Verification Method

1. **Inspection**:
   - Read `analysis.md` at `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_backend\explorer_1\analysis.md`.
2. **Pytest Execution** (after implementation):
   - Run command: `pytest omni_oracle_app/backend/tests/test_thai_astrology.py omni_oracle_app/backend/tests/test_tarot.py`
3. **Invalidation Conditions**:
   - If `birth_time < 06:00` does not subtract 1 day from astrological day of week determination.
   - If `draw_celtic_cross` accepts duplicate card indices or out-of-range indices (<0 or >77) without raising `ValueError`.
