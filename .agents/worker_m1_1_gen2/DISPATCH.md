## 2026-08-05T18:12:39Z
You are Worker 2 (Gen 2) for Sub-milestone M1.1: Thai Astrology Engine Fixes.

Your working directory: e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\worker_m1_1_gen2

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Context & Issue Reports:
- `GATE_STATUS.md`: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_divination\GATE_STATUS.md`
- Reviewer 2 Report: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\reviewer_m1_1_2\handoff.md`
- Challenger 1 Report: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\challenger_m1_1_1\handoff.md`
- Target Code: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\app\engines\thai_astrology.py`
- Target Test: `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\tests\test_thai_astrology.py`

Your Task:
Remediate the mathematical issues in `thai_astrology.py` and update `test_thai_astrology.py`:

1. **Fix 180° Lagna Inversion**:
   In `calculate_lagna_sidereal()`, correct trigonometric component signs:
   `y = math.cos(rad(lst))`
   `x = -math.sin(rad(lst)) * math.cos(rad(eps)) - math.tan(rad(lat)) * math.sin(rad(eps))`

2. **Fix GMST Double-Counting**:
   In `calculate_lagna_sidereal()`, calculate `jd0 = math.floor(jd - 0.5) + 0.5` (Julian Date at 0h UT on that day) to compute base GMST at 0h UT (`GMST0`), then add `1.00273790935 * ut_hours * 15.0` degrees for the UT time component.

3. **Fix Planetary Dignity Precedence**:
   In `determine_planetary_dignity()`, check `EXALTED_SIGNS` (Ucc) before `SIGN_RULERS` (Kaset). This ensures Mercury in Virgo is evaluated as `UCC` (Exalted status takes precedence).

4. **Add Ground-Truth Test Assertions**:
   In `test_thai_astrology.py`, add explicit assertions comparing Lagna and planetary positions against known benchmark outputs (e.g. verifying Lagna for 1990-01-01 12:00 in Bangkok is in Pisces/Aries, not Virgo 180° opposite).

5. **Run Pytest & Verify**:
   Run `pytest omni_oracle_app/backend/tests/test_thai_astrology.py -v` and verify ALL unit tests PASS cleanly.

6. **Write Handoff**:
   Write handoff report to `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\worker_m1_1_gen2\handoff.md` and `changes.md`. Include exact pytest output. Communicate via `send_message` when done.
