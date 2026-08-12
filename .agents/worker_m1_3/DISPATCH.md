## 2026-08-05T18:29:57Z

<USER_REQUEST>
You are Worker for Sub-milestone M1.3 (Burmese Mahabote Engine).
Your working directory is e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\worker_m1_3.

Read these context files first:
- e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md
- e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md
- e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\sub_orch_m1_divination\SCOPE.md
- e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_3_1\analysis.md
- e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_3_2\analysis.md
- e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_3_3\analysis.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

STRICT TDD REQUIREMENT:
1. Write the Pytest test suite FIRST in `omni_oracle_app/backend/tests/test_mahabote.py` covering all public seams, data models, calculations, and edge cases.
2. Run `pytest omni_oracle_app/backend/tests/test_mahabote.py` (or python -m pytest ...) to confirm RED status (tests fail/error because engine does not exist yet).
3. Implement `omni_oracle_app/backend/app/engines/mahabote.py` cleanly to satisfy all public seams and math rules.
4. Run `pytest omni_oracle_app/backend/tests/test_mahabote.py` and ensure GREEN status (100% tests pass).

Scope & Specifications to implement:
- Module: `omni_oracle_app/backend/app/engines/mahabote.py`
- Test: `omni_oracle_app/backend/tests/test_mahabote.py`
- Math rules:
  1. Chula Sakarat (CS): `CS = BE - 1181`. Songkran cutoff: Jan 1 to Apr 15 uses `CS = BE - 1182` (`CE - 639`).
  2. Base Modulo 7: `cs_mod = CS % 7`. Map `0` to `7`.
  3. Day of Week: Sunday=1, Monday=2, Tuesday=3, Wednesday=4 (Wednesday night option support if passed, else standard 1-7), Thursday=5, Friday=6, Saturday=7.
  4. 7 Body Positions: Atta (อัตตะ), Hina (หินะ), Thanang (ธนัง), Pita (ปิตา), Mata (มาตา), Phoka (โภคา), Majjhima (มัชฌิมา). Matrix assignment starting from remainder.
  5. Taksa (ตักษา): Bariwan, Ayu, Dech, Sri, Mula, Utsaha, Montri, Kalakini based on birth weekday.
  6. Kalayok (กาลโยค): Thongchai, Athipati, Upabat, Lokawinat.
  7. Lucky Digits Extraction: 0-9 single digits and 2-digit lottery pairs derived from favorable positions (Thanang, Phoka, Sri, Dech, Montri) avoiding Kalakini/Hina/Upabat/Lokawinat.

Write your changes report to `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\worker_m1_3\changes.md` and deliver `handoff.md`.
Send a message back to parent when done.
</USER_REQUEST>
