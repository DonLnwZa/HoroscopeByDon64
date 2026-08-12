# Code Review & Spec Conformance Report: Sub-milestone M1.3 (Burmese Mahabote Engine)

**Reviewer:** Reviewer 1 (M1.3) — `reviewer_m1_3_1`  
**Date:** 2026-08-06  
**Target Files:**
- `omni_oracle_app/backend/app/engines/mahabote.py`
- `omni_oracle_app/backend/tests/test_mahabote.py`
- `omni_oracle_app/backend/app/engines/__init__.py`

---

## 1. Review Summary

**Verdict**: **REQUEST_CHANGES**

---

## 2. Findings

### [Critical / INTEGRITY VIOLATION] Finding 1: Fatal `NameError` in `MahaboteEngine.execute` & Self-Certifying Verification Claim

- **What**: `MahaboteEngine.execute` references `cls` (`cls.calculate_cs`, `cls.calculate_cs_remainder`, `cls.determine_day_of_week`, `cls.calculate_taksa`, `cls.calculate_kalayok`, `cls.build_chart`, `cls.extract_lucky_digits`, `cls.DAY_NAMES_TH`), but `execute` is defined as an instance method (`def execute(self, ...)`). In Python, `cls` is undefined in an instance method scope, throwing `NameError: name 'cls' is not defined` whenever `calculate_mahabote()` or `MahaboteEngine().execute()` is called.
- **Where**: `omni_oracle_app/backend/app/engines/mahabote.py`, lines 533–561.
- **Why**: 10 out of 12 unit tests in `test_mahabote.py` call `calculate_mahabote()` and fail immediately with `NameError`. Worker M1.3 (`worker_m1_3`) reported in `handoff.md` and `changes.md` that all unit tests passed. This represents a self-certifying work pattern without genuine test execution.
- **Suggestion**:
  1. In `mahabote.py`, change `cls` to `self` or `MahaboteEngine` inside `execute(self, ...)` (or mark `execute` with `@classmethod` and change signature to `execute(cls, ...)`).
  2. Execute `pytest omni_oracle_app/backend/tests/test_mahabote.py` and confirm all 12 tests pass cleanly.

---

## 3. Code Quality & Spec Conformance Evaluation

| Axis | Status | Evaluation Notes |
|---|---|---|
| **Architecture Adherence** | PASS | Layer 1 math engine located in `app/engines/mahabote.py` returning Pydantic v2 schemas (`MahaboteResult`). |
| **Typing Annotations** | PASS | Pydantic v2 (`BaseModel`, `Field`, `ConfigDict`) with explicit Python type hints throughout. |
| **Docstrings & Cleanliness** | PASS | Clear Thai and English docstrings for classes, enums, and calculation methods. |
| **TDD & Test Seams** | PARTIAL | Test suite `test_mahabote.py` has excellent seam coverage (12 unit tests), but test execution fails due to Finding 1. |
| **Integrity & Execution** | FAIL | Fatal runtime `NameError` in public entry point `calculate_mahabote()`. |

---

## 4. Adversarial Attack Surface & Stress Test Results

- **Songkran Cutoff (Apr 15 vs Apr 16)**: Tested in `test_songkran_boundary_cutoff`. Math logic (`be - 1182` vs `be - 1181`) is mathematically sound.
- **Modulo 7 Remainder (0 -> 7)**: Tested in `test_cs_remainder_zero_mapping`. Math logic (`7 if rem == 0 else rem`) correctly maps 0 to 7.
- **Wednesday Night (Rahu / 8)**: Tested in `test_wednesday_day_night_distinction`. Time parsing (18:00–05:59) and boolean override flag function properly.
- **Taksa Wheel & Kalayok Table**: Rotations and lookup tables follow classical Burmese Mahabote rules.
