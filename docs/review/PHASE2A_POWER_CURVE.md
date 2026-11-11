# Phase 2A — Power-curve correction: implementation and verification

*11 November 2026. Scope: the turbine power curve only. Wind statistics,
losses, emission factors, Monte Carlo (MC) distributions, seed, spacing and
scenarios are unchanged. Manuscript, figures and tables are untouched. All
corrected outputs are **provisional**.*

## 1. What changed

| Item | Change |
|---|---|
| `config/turbine.py` | Active curve `POWER_CURVE_MS_KW` = `POWER_CURVE_OEDB_V164_9500_MS_KW`; the retired curve is kept as `POWER_CURVE_ORIGINAL_MS_KW`; added `POWER_CURVE_ID = "OEDB_V164_9500"`. Provenance and limitations are in the code comment |
| `results/archive/baseline_original_curve/` | Byte-identical copy of the pre-2A `results/*` files, plus `SHA256SUMS` and a README. `results/*.json` and `results/*.npz` are **not modified** |
| `scripts/phase2a_power_curve_rerun.py` | Old-versus-new rerun. It writes only to `results/provisional/phase2a/` |
| `results/provisional/phase2a/` | `monte_carlo_results.json`, `monte_carlo_samples.npz` and `power_curve_comparison.json`, each labelled `PROVISIONAL` |
| `tests/test_power_curve.py` | 18 regression tests |
| `docs/review/phase1_checks.py`, `verify_numbers.py` | Now import the original curve explicitly, so their pre-2A analysis output is unchanged |

The production scripts (`04`, `05`, `06`) now read the new curve through
`config`. They were **not run**, because running them would overwrite
`results/*.json`. The rerun script uses exact copies of their curve
functions, and tests check that the copies match the scripts output for
output.

## 2. Curve provenance and boundary behaviour

**Source:** the OEDB turbine library row `V164/9500`
(windpowerlib `dev` @191d8ca, `oedb/power_curves.csv`). It is a third-party
digitisation ("engauge digitizer") of the graph MHI Vestas published. It is
**not manufacturer-certified**, and its air-density basis is undocumented
(1.225 kg m⁻³ assumed). All 49 OEDB points (0–24.5 m/s) were used
unchanged, converted from W to kW.

| Check | Result |
|---|---|
| Cut-in | 0 kW at ≤3.0 m/s; 115 kW at 3.5 m/s (`cut_in_ms = 3.5`) |
| Rated | 9500 kW first reached at **14.0 m/s** (= `rated_ms`); the old curve reached it at 13.0 |
| Cut-out | The OEDB table ends at 24.5 m/s. Three added boundary points, documented as not being OEDB data: `(25.0, 9500)` holds the plateau to the Vestas-stated 25 m/s cut-out; `(25.01, 0)` and `(30, 0)` follow the old curve's convention |
| Peak electrical Cp | 0.476 at 8.5 m/s (old curve: 0.564); below Betz everywhere |
| Interpolation | Linear, unchanged. Script 04 zeroes power below 3.5 m/s; script 06 interpolates 3.0→3.5 m/s. This existing inconsistency was kept. Its effect is −0.064% (Weibull basis); 3 735 hours fall in 3.0–3.5 m/s |
| Tail sensitivity | Zeroing 24.5–25 m/s instead of holding the plateau changes the result by −0.006%. Only 2 of 96 432 hours fall in that range |

## 3. Input verification (`wind_hub_105m.parquet`, provided 11.11.2026)

- **File:** sha256 `0cfc4742…916a5`, 3.2 MB. It covers 96 432 hours from
  2014‑01‑01 to 2024‑12‑31 23:00 with no missing values.
- **Empirical checks:** the mean is 7.171635150909424 m/s and the
  original-curve gross AEP is 30.411791370569144 GWh. Both match the
  archived baseline **bit-for-bit**.
- **Weibull refit:** scipy 1.18 gives k and c within 2.5×10⁻⁸ of the
  archived values (an optimiser-version difference). The MC therefore uses
  the archived k0, c0 and σ_c, so that only the curve changes. Using refitted
  parameters instead changes the samples by at most 2×10⁻⁷ relative.
- **Now committed** (follow-up to Phase 2A), through a narrow `.gitignore`
  exception. Provenance, licence and checksum are in `data/README.md`.

## 4. Old versus corrected results

### 4a. Empirical hourly AEP (method of script 04, exact)

| | Original | Corrected | Change |
|---|---|---|---|
| Gross AEP per turbine (GWh/yr) | 30.41 | **27.20** | −10.55% |
| Gross CF | 36.52% | **32.66%** | |
| Net AEP per turbine (GWh/yr) | 25.78 | **23.06** | |
| Net CF | 30.96% | **27.69%** | |
| Net yield (GWh yr⁻¹ MW⁻¹) | 2.714 | **2.428** | |
| Full-load hours | 2714 | **2428** | |

Phase 1 estimated 27.4 GWh and 27.9% by scaling. The exact values are
slightly lower, because 50% of hours fall in the 6–12 m/s band, where the
two curves differ most.

### 4b. Weibull-integrated AEP (method of script 06, same curve)

| | Original | Corrected | Change |
|---|---|---|---|
| Gross AEP per turbine (GWh/yr) | 29.59 | **26.70** | −9.78% |
| Gross CF | 35.54% | **32.06%** | |
| Net CF (nominal losses) | 30.13% | **27.18%** | |
| Net yield (GWh yr⁻¹ MW⁻¹) | 2.641 | **2.383** | |

The gap between the empirical and Weibull methods narrows from −2.7% to
−1.8% (32.06% against 32.66% gross CF). *[Erratum, Phase 3A: an earlier
version of this sentence wrongly said "widens to −3.4%"; see
PHASE3A_ENERGY_UNCERTAINTY.md §1.]* This is the Weibull-fit issue K4 from
the review.

### 4c. Monte Carlo (N = 10 000, seed 2026, only the curve changed)

| Per MW | Original P10 / P50 / P90 | Corrected P10 / P50 / P90 |
|---|---|---|
| Net yield (GWh yr⁻¹ MW⁻¹) | 2.410 / 2.622 / 2.833 | **2.166 / 2.366 / 2.565** |
| Net CF (%) | 27.5 / 29.9 / 32.3 | **24.7 / 27.0 / 29.3** |
| Coefficient of variation of yield | 6.33% | 6.62% |
| Avoided CO₂ (t yr⁻¹ MW⁻¹) ⚠ | 1277 / 1525 / 1754 | **1150 / 1375 / 1586** ⚠ |

Farm-level P50, with P10–P90 in brackets:

| Scenario | Energy, original (TWh/yr) | Energy, corrected (TWh/yr) | CO₂, original (Mt/yr) ⚠ | CO₂, corrected (Mt/yr) ⚠ |
|---|---|---|---|---|
| S1, 247 MW | 0.65 | 0.58 (0.53–0.63) | 0.38 | 0.34 |
| S2, 503.5 MW | 1.32 | 1.19 (1.09–1.29) | 0.77 | 0.69 |
| S3, 997.5 MW | 2.62 | **2.36** (2.16–2.56) | 1.52 | **1.37** (1.15–1.58) |
| S4, 1738.5 MW | 4.56 | 4.11 (3.77–4.46) | 2.65 | 2.39 |

⚠ **CO₂ values are provisional.** They reuse the unvalidated emissions
sampling in scripts/06. The review (K3) found that the triangular
grid-factor distribution does not represent the official combined margin.

## 5. Tests

`python -m pytest -q tests/` gives **18 passed** (2.6 s). The tests cover:

- **Source and units:** OEDB W → kW and the three boundary points;
  maximum 9500 kW = rated power.
- **Physical limits:** monotonic increase; Cp below Betz with a peak of
  0.4762; the retired curve is flagged by its Cp above 0.56.
- **Cut-in, rated and cut-out:** behaviour of both production scripts'
  curve functions.
- **Interpolation:** linear midpoints.
- **Code identity:** the rerun functions equal the script 04 and 06
  functions.
- **Archive integrity:** baseline checksums match, and `results/*` equals
  the archive.
- **MC reproducibility:** bit-for-bit for both curves.
- **Weibull regression:** −9.78%.
- **Empirical regression:** the original curve matches the archive exactly
  and the corrected curve gives 27.2021 GWh. This test is skipped when the
  parquet file is absent.

One failure occurred during development: the expected peak Cp was entered
as 0.4757, while the true value is 0.4762. That was an error in the test,
not the model, and it was corrected. No tests fail now.

## 6. Still provisional or open

1. **Curve certification.** The curve is a digitisation of a published
   graph, not a certified table. The ±3% curve uncertainty suggested in
   Phase 1 is **not** added to the MC; the distributions are unchanged in
   this phase.
2. **Avoided CO₂.** Every CO₂ figure depends on the unvalidated emissions
   methodology (K3).
3. **Production files not regenerated.** `results/*.json`, figures, tables
   and the manuscript still show the original-curve numbers.
   `scripts/04`–`09` would overwrite them. Do this only after the remaining
   Phase 2 decisions.
4. **Not addressed in Phase 2A:**
   - ERA5 bias against Global Wind Atlas (K1)
   - Weibull-based MC versus empirical AEP (K4)
   - Uncertainty design (K5)
   - Site air density
   - The script 04/06 cut-in inconsistency (−0.06%)
