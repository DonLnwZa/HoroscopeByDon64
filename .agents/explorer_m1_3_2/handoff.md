# Handoff Report: Mahabote Taksa & Kalayok Analysis (Explorer 2 - M1.3)

**Author:** Explorer 2  
**Target Sub-milestone:** M1.3 (Burmese Mahabote Engine)  
**Working Directory:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_3_2`  
**Report Output File:** `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_3_2\analysis.md`

---

## 1. Observation

- **Project Context & Mandate:**
  - `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\ORIGINAL_REQUEST.md` line 6: "สร้างเว็บแอปพลิเคชันที่นำศาสตร์พยากรณ์ 4 แขนง (โหราศาสตร์, เลข 7 ตัว 9 ฐาน, มหาภูติพม่า, ไพ่ทาโรต์) มาวิเคราะห์ร่วมกับสถิติหวยย้อนหลัง 1 ปี...".
  - `e:\เว็บดูดวงเพื่อซื้อหวยไทย\PROJECT.md` lines 15, 70: Feature #3 Burmese Mahabote Engine in `omni_oracle_app/backend/app/engines/mahabote.py` with Pytest suite `omni_oracle_app/backend/tests/test_mahabote.py`.
  - `e:\เว็บดูดวงเพื่อซื้อหวยไทย\รายงานการวิเคราะห์เชิงลึกระบบโหราศาสตร์และพยากรณ์ศาสตร์เพื่อการพัฒนาระบบสถาปัตยกรรมเว็บไซต์ดูดวง.txt` lines 112-154: Detailed technical specifications for Chula Sakarat conversion, 7 positions (ตุ๊กตาไขนาม), and Taksa/Kalayok overlays.

- **Current Implementation State:**
  - `omni_oracle_app/backend/tests/test_tier1_feature_coverage.py` lines 64-77: Provides TDD seam for `calculate_mahabote(birth_date, birth_time)` expecting outputs including `chula_sakarat`, `day_of_week`, `positions` (`panga`, `puti`, `marana`, `adhipati`, `raja`, `atta`, `majjhima`), `taksa_day`, `kalayok`, and `lucky_digits`.
  - `omni_oracle_app/backend/tests/test_tier4_realworld_scenarios.py` lines 26-34: Validates Songkran cutoff (April 15 old CS year vs April 16 new CS year).
  - Production code `omni_oracle_app/backend/app/engines/mahabote.py` and unit test `omni_oracle_app/backend/tests/test_mahabote.py` are not yet created (pending M1.3 TDD implementation).

---

## 2. Logic Chain

1. **Observation 1 & Document Specs:** The Burmese Mahabote engine calculates the Chula Sakarat ($CS$) year, computes $CS \pmod 7$, places planets 1-7 in 7 body positions starting at Panga, and overlays Taksa and Kalayok.
2. **Observation 2 & Taksa Rules:** Taksa cycles through 8 categories (Bariwan, Ayu, Dech, Sri, Mula, Utsaha, Montri, Kalakini) starting from the birth day planet. Sri (+3.0), Dech (+2.0), Montri (+2.5), Mula (+2.5) provide positive weightings; Kalakini (-3.0) provides malefic penalty.
3. **Observation 3 & Kalayok Rules:** For a given $CS$ year, $CS \pmod 7$ yields annual indicators: Thongchai (+3.0), Athipati (+2.5), Upabat (-2.5), Lokawinat (-3.0).
4. **Observation 4 & Interaction Matrix:** Body position weights (Raja +3.0, Athipati +2.5, Atta +2.0, Majjhima +1.0, Panga -2.0, Puti -2.5, Marana -3.0) combine additively with Taksa and Kalayok weights. Favorable overlay (e.g. Sri in Raja, Dech in Athipati) yields top scores (+7.5 to +9.0). Unfavorable overlay (Kalakini in Marana/Puti/Panga) yields strong negative scores (-6.0 to -9.0) and disqualifies the digit.
5. **Observation 5 & Lucky Digits Algorithm:** Single digits are ranked by net composite score $S(d)$. Top 3-4 single digits form candidate pairs $d_i d_j$. Pairs are scored by $S(d_i) + S(d_j)$ plus Planetary Harmony Bonds (คู่มิตร +2.0, คู่สมพล +1.5, คู่ธาตุ +1.0, คู่ศัตรู -2.0) and House Synergy. This yields robust, astrologically sound 2-digit lottery pair recommendations.

---

## 3. Caveats

- **Wednesday Night (8 / Rahu) in 7-Position Mahabote:** Traditional Mahabote uses 7 positions with numbers 1 to 7. When extracting single lucky digits for lottery recommendation, Rahu (8) and Ketu (9) are extended derived digits. Implementers must ensure that digits 0, 8, 9 are computed via derivation rules without breaking the 7-position matrix.
- **Songkran Cutoff Date Standard:** The code uses April 16 as the Songkran cutoff boundary for CS year decrementing (April 1-15 uses $CS = พ.ศ. - 1182$). This is aligned across `test_tier4_realworld_scenarios.py` and the technical document.

---

## 4. Conclusion

- A complete, deterministic model for Taksa, Kalayok, House-Taksa interaction, and Lucky Digits Extraction has been specified in `analysis.md`.
- The scoring formulas, Taksa lookup matrix, Kalayok lookup table, and 2-digit lottery pair ranking logic provide a direct blueprint for implementers writing `omni_oracle_app/backend/app/engines/mahabote.py` and its pytest suite `omni_oracle_app/backend/tests/test_mahabote.py`.

---

## 5. Verification Method

- **Analysis File Inspection:**
  - View `e:\เว็บดูดวงเพื่อซื้อหวยไทย\.agents\explorer_m1_3_2\analysis.md` to verify all 4 required sections (Taksa table, Kalayok lookup, interaction matrix, lucky digits algorithm).
- **Test Seam Verification:**
  - Run pytest on tier 1 & 4 test files once implemented: `pytest omni_oracle_app/backend/tests/test_tier1_feature_coverage.py omni_oracle_app/backend/tests/test_mahabote.py`
