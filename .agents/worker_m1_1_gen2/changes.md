# Changes Summary — Worker 2 (Gen 2) M1.1

## Target Files
1. `omni_oracle_app/backend/app/engines/thai_astrology.py`
2. `omni_oracle_app/backend/tests/test_thai_astrology.py`

---

## 1. `omni_oracle_app/backend/app/engines/thai_astrology.py`

### Change 1.1: Fix 180° Lagna Inversion Trigonometric Signs & Fix GMST Double-Counting
- **Function**: `calculate_lagna_sidereal(jd: float, ut_hours: float, lat: float, lon: float, ayanamsa: float)`
- **Problem Fixed**: 
  1. Signs of trigonometric components $y$ and $x$ were negated, resulting in calculation of Descendant (7th house / western horizon) rather than Ascendant (1st house / eastern horizon).
  2. `gmst0` was computed using full `jd` (including fractional day `ut_hours/24`), and then `360.98564736629 * (ut_hours / 24.0)` was added, double-counting the daily sidereal drift rate ($0.985647^\circ/\text{day}$).
- **Modification**:
  ```python
  def calculate_lagna_sidereal(jd: float, ut_hours: float, lat: float, lon: float, ayanamsa: float) -> float:
      """Calculates Sidereal Lagna (Ascendant) longitude in degrees."""
      jd0 = math.floor(jd - 0.5) + 0.5
      t0 = (jd0 - 2451545.0) / 36525.0
      gmst0 = 100.46061837 + (36000.770053608 * t0) + (0.000387933 * t0 * t0)
      gmst = (gmst0 + 1.00273790935 * ut_hours * 15.0) % 360.0
      lst = (gmst + lon) % 360.0

      rad = math.radians
      eps = 23.439291 - 0.0130042 * t0

      y = math.cos(rad(lst))
      x = -math.sin(rad(lst)) * math.cos(rad(eps)) - math.tan(rad(lat)) * math.sin(rad(eps))

      asc_trop = math.degrees(math.atan2(y, x)) % 360.0
      asc_sid = (asc_trop - ayanamsa) % 360.0
      return asc_sid
  ```

### Change 1.2: Fix Planetary Dignity Precedence Order
- **Function**: `determine_planetary_dignity(planet_id: int, sign_index: int)`
- **Problem Fixed**: Kaset (`SIGN_RULERS`) check was performed before Exalted (`EXALTED_SIGNS`) check. For Mercury (`planet_id=4`) in Virgo (`sign_index=5`), Virgo is both own sign and exalted sign, causing Mercury in Virgo to return `KASET` instead of `UCC`.
- **Modification**:
  ```python
  def determine_planetary_dignity(planet_id: int, sign_index: int) -> PlanetaryDignity:
      """Determines planetary dignity (อุจจ์, เกษตร, นิจ, ประ, ปกติ)."""
      # 1. Ucc (Exalted) - checked before Kaset so Mercury in Virgo is evaluated as UCC
      if EXALTED_SIGNS.get(planet_id) == sign_index:
          return PlanetaryDignity.UCC

      # 2. Kaset (Own sign)
      if SIGN_RULERS[sign_index] == planet_id:
          return PlanetaryDignity.KASET
      
      # 3. Nit (Debilitated)
      if DEBILITATED_SIGNS.get(planet_id) == sign_index:
          return PlanetaryDignity.NIT
      
      # 4. Pra (Detriment - opposite sign of own Kaset)
      own_signs = [i for i, r in enumerate(SIGN_RULERS) if r == planet_id]
      pra_signs = [(s + 6) % 12 for s in own_signs]
      if sign_index in pra_signs:
          return PlanetaryDignity.PRA
      
      return PlanetaryDignity.NORMAL
  ```

---

## 2. `omni_oracle_app/backend/tests/test_thai_astrology.py`

### Change 2.1: Added Imports
- Imported `determine_planetary_dignity` and `calculate_lagna_sidereal`.

### Change 2.2: Added Ground-Truth & Remediation Unit Tests
1. `test_ground_truth_lagna_and_planetary_benchmark()`:
   - Verifies 1990-01-01 12:00 in Bangkok has Lagna in Pisces (มีน, `rasi_index=11`), NOT Virgo 180° opposite.
   - Verifies 2026-08-05 06:00 (sunrise in Bangkok) has Lagna in Cancer (`rasi_index=3`), matching Sun's sign at sunrise.
2. `test_mercury_in_virgo_dignity_precedence()`:
   - Verifies Mercury in Virgo evaluates to `PlanetaryDignity.UCC`.
   - Verifies Mercury in Gemini evaluates to `PlanetaryDignity.KASET`.
   - Verifies Sun in Aries evaluates to `PlanetaryDignity.UCC`.
3. `test_gmst_no_double_counting()`:
   - Verifies GMST rate addition across 1h interval matches expected sidereal shift (~15.04°/h) without daily rate double counting.
