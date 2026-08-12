## 2026-08-12T05:38:45Z
<USER_REQUEST>
You are Explorer 1 for Milestone M1 (Backend Engines & API Upgrade).
Working directory: e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_backend\explorer_1

YOUR TASK:
Investigate existing backend files in e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\ for Requirements R1 (Thai Lunar Calendar & 6am Cutoff) and R2 (Tarot selected cards mapping).

MANDATORY DOCUMENTS TO READ:
1. e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md
2. e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md
3. e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_backend\SCOPE.md

FOCUS AREAS:
1. R1 Thai Lunar Calendar:
   - Check how `birth_date` and `birth_time` are currently handled in `thai_astrology.py` or other engines.
   - Design the exact logic for 6:00 AM Bangkok cutoff (if time < 06:00, subtract 1 day for Thai astrological day of week determination).
   - Design approximate Thai Lunar Month (1..12) and Thai Zodiac Year calculation from Gregorian birth_date.
   - Define exact JSON structure for `chart.lunar_calendar`: `day_of_week`, `lunar_month`, `zodiac_year`, `cutoff_applied`.
2. R2 Tarot Selection Mapping:
   - Examine `tarot.py` and `draw_celtic_cross` function.
   - Design updates so `draw_celtic_cross(selected_cards)` accepts an array of 10 card indices (0..77) from `selected_tarot_cards` payload, maps them to the 10 Celtic Cross positions, and handles validation/errors.

OUTPUT REQUIREMENT:
Write a detailed investigation report at e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_backend\explorer_1\analysis.md with findings, existing code analysis, precise proposed code changes / function signatures, and unit test strategy.
Include handoff.md in your working directory and send a message back to parent. Do NOT modify source code files.
</USER_REQUEST>
