## 2026-08-06T01:06:43Z
<USER_REQUEST>
You are Worker 1 for Sub-milestone M1.1: Thai Astrology Engine.

Your working directory: e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\worker_m1_1

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Context & Reference Files:
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md`
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md`
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_divination\SCOPE.md`
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_1_1\analysis.md`
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_1_2\analysis.md`
- `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_1_3\analysis.md`

Your Task:
Implement the Thai Astrology Engine (`omni_oracle_app/backend/app/engines/thai_astrology.py`) and its Pytest suite (`omni_oracle_app/backend/tests/test_thai_astrology.py`) using STRICT TDD (Red -> Green -> Refactor).

Detailed TDD Workflow Requirements:
1. **Directory Setup**: Create package structure under `omni_oracle_app/backend/app/engines/` and `omni_oracle_app/backend/tests/` with `__init__.py` files.
2. **RED Step (Write Tests First)**:
   - Create `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\tests\test_thai_astrology.py`.
   - Test public seam: `calculate_thai_astrology(birth_date: str, birth_time: str = "12:00", birth_province: str = "กรุงเทพมหานคร") -> ThaiAstrologyResult`.
   - Test Data Models: `ThaiAstrologyResult`, `PlanetPosition`, `HouseDetail`, `LagnaInfo`, `ThaiPlanet`, `ZodiacSign`, `AstrologicalHouse`, `PlanetaryDignity`.
   - Test Features:
     a) 10 planets (Sun=1, Moon=2, Mars=3, Mercury=4, Jupiter=5, Venus=6, Saturn=7, Rahu=8, Ketu=9, Uranus=0) with degree, sign, house, dignity.
     b) Lagna calculation (Ascendant) & 12 houses (ตนุ to วินาศ).
     c) Harmonic charts: D9 Navamsa (`floor((sid_deg * 60) / 200) % 12`) and D3 Drekkana (`(sign_idx + 4 * decan_idx) % 12`).
     d) Lahiri Ayanamsa subtraction `(tropical_deg - ayanamsa) % 360`.
     e) Edge cases: missing birth time (default "12:00"), unknown province (default Bangkok), invalid date formats.
     f) Lucky digits extraction (`primary_lucky_planet`, `secondary_lucky_planet`, `house_lord_digits`, `lucky_numbers`).
   - Execute pytest to verify tests FAIL (Red state).
3. **GREEN Step (Write Implementation)**:
   - Write pure Python math calculation engine in `e:\เว็บดูดวงเพื่อซื้อหวยไทย\omni_oracle_app\backend\app\engines\thai_astrology.py`. (Use swisseph if available, with robust pure Python astronomical fallback for Lahiri Ayanamsa & planetary longitudes so it runs everywhere without external C library dependencies).
   - Execute pytest to verify ALL tests PASS (Green state).
4. **REFACTOR & Document**:
   - Ensure clean code, docstrings, type annotations.
5. **Handoff**:
   - Write handoff report to `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\worker_m1_1\handoff.md` and `changes.md`. Include exact pytest output and proof of test-first execution.
   - Communicate via `send_message` when finished.
</USER_REQUEST>
