# Phase 4B — Production model integration

*11 November 2026. The verified methods from Phases 1–4A are now one
production pipeline, and its single authoritative output is
`results/revised/`. The manuscript, its tables and the figures are
unchanged.*

---

## 1. Authoritative methodology (as implemented)

| Component | Implementation |
|---|---|
| Wind data | `data/processed/wind_hub_105m.parquet`: ERA5 2014–2024, hourly, node 40.50° N 26.25° E (sha256 in `MANIFEST.json`) |
| Turbine | V164‑9.5 MW with the OEDB V164/9500 digitised curve (`config.turbine.POWER_CURVE_MS_KW`) |
| Energy estimator | Empirical hourly conversion: CF = ΣP / (P_r·N_h); AEP = CF·P_r·8 766 h |
| Weibull | Descriptive statistic and cross-check only (`weibull_crosscheck.json`) |
| Uncertainty | Sampling CI of the 11-year mean (t-interval; bootstrap and jackknife as checks). Observed interannual variability. Loss scenarios (`config.turbine.LOSS_SCENARIOS`). Wind-speed sensitivities. **All labelled separately; never combined** |
| Emissions | Primary: E × 0.6242 tCO₂/MWh (2023 combined margin, `config.emissions.GRID_EF_2023`). Context: operating margin, build margin, generation average. Secondary: life-cycle GHG in tCO₂‑eq (`LIFECYCLE_GHG_G_PER_KWH`), not subtracted |
| Scenarios | `config.turbine.ACTIVE_SCENARIOS` = S1 (247 MW), S2 (503.5 MW), S3 (997.5 MW; ~1 GW, conditional on allocation to Saros). S4 is retired (`RETIRED_SCENARIOS`) |
| Screening | Phase 4A geometry: Saros ÖÇK overlap, EMODnet bathymetry, ERA5 node position, packing and screening classes |

No value is hard-coded: every headline value is computed from the Parquet
file, the curve, the losses and the official factors. Tests compare the
values with the independent Phase 3A/3B outputs.

---

## 2. What changed

**Changed or new production code:**

| File | Change |
|---|---|
| `scripts/04_fit_weibull_aep.py` | **Rewritten.** Writes wind resource, empirical energy, Weibull cross-check, interannual and sampling results, loss scenarios and wind-speed sensitivity to `results/revised/`. `power_from_speed` and `fit_weibull` keep their names and behaviour, because other scripts and tests import them |
| `scripts/06_emissions_and_scenarios.py` | **New.** Avoided operational CO₂, context methods, life-cycle GHG, S1–S3. Reads only `results/revised/energy_yield.json` and `interannual_and_sampling.json` |
| `scripts/07_site_screening.py` | **New.** Bathymetry, ÖÇK overlap, ERA5 node, packing, screening classes, S1–S3 densities |
| `scripts/run_revised_pipeline.py` | **New.** Runs 04 → 06 → 07 and writes `MANIFEST.json` (descriptions, SHA-256, input hash, code commit) |
| `scripts/phase4a_site_checks.py` | `main()` split into `compute(scenarios)` plus writing. Output verified byte-identical |
| `config/turbine.py` | Added `ACTIVE_SCENARIOS` (neutral labels), `RETIRED_SCENARIOS`, `LOSS_SCENARIOS` and `TURBINE_SPACING_ASSUMPTION`. The historical `SCENARIOS` list is kept, clearly marked, for archive reproducibility |
| `config/emissions.py` | **Rewritten.** Verified 2023 factors with units and sources; fuel factors in both CO₂ and CO₂‑eq; verified life-cycle values; context references with verification status. The legacy `GRID_CO2` and `OFFSHORE_WIND_CO2` are kept only for the archive, relabelled as mixed or legacy. "IPCC 2025", "8–14" and "no recycling credit" are removed |
| `config/site.py` | Date 13 May 2026, candidate status, nearest coast Thrace (was Gelibolu) |
| `docs/review/verify_numbers.py`, `phase1_checks.py` | Now read the archived baseline paths (outputs unchanged) |
| `README.md`, `requirements.txt` (+rasterio, pytest), `docs/DECISION_LOG.md` (superseded notice), `results/README.md`, `scripts/legacy/README.md` | Documentation |

**Retired and archived:**

| Item | New location |
|---|---|
| Original 04 (total ÷ 11, S4, `results/weibull_aep_results.json`) | `scripts/legacy/04_fit_weibull_aep.py` |
| Seven-variable Weibull Monte Carlo, triangular grid mixture, life-cycle subtraction | `scripts/legacy/06_run_monte_carlo.py` |
| National comparison built on the MC samples (incl. S4) | `scripts/legacy/07_compare_with_grid.py` |
| MC figures; workflow, comparison and equivalents figures (hard-coded old values, unsourced fossil shares, CO₂‑eq fuel factors) | `scripts/legacy/08_*.py`, `09_*.py` |
| `results/{weibull_aep_results, monte_carlo_results, comparison_results}.json`, `monte_carlo_samples.npz` | Removed from `results/`. Byte-identical copies remain in `results/archive/baseline_original_curve/` (checksums tested) |

Legacy scripts keep their original code apart from a docstring note, the
import path and a run guard. They exit unless `SAROS_ALLOW_LEGACY=1` is set.
The archived Monte Carlo can still be reproduced bit-for-bit through
`scripts/phase2a_power_curve_rerun.py`.

---

## 3. Reproducing from a clean clone

```bash
git clone https://github.com/SerdarKizil0/saros-offshore-wind.git
cd saros-offshore-wind && git checkout claude/nifty-sagan-uql5y0
pip install -r requirements.txt
python scripts/run_revised_pipeline.py    # about 20 s; no download
python -m pytest -q tests/                # 55 passed
```

This was verified in a fresh clone (§6). The regenerated output files were
byte-identical to the committed ones. Only `MANIFEST.json` differs, in its
`code_commit_at_generation` field.

---

## 4. `results/revised/`: the interface future tables and figures must use

| # | File | Contents |
|---|---|---|
| 1 | `wind_resource.json` | Mean, median, percentiles, power density (ρ = 1.225), shear from ERA5 levels, monthly and annual means, CoV, direction shares (hours and energy) |
| 2 | `energy_yield.json` | **Central estimate:** gross/net CF, GWh per turbine, GWh/MW, full-load hours, normalisation check |
| 3 | `weibull_crosscheck.json` | Weibull MLE, Justus formula, goodness of fit, Weibull AEP, contributions by speed bin |
| 4 | `interannual_and_sampling.json`, `annual_energy.csv` | Observed variability (labelled `OBSERVED`); sampling CI (labelled `SAMPLING`) |
| 5 | `wind_speed_sensitivity.json` | ±5 %, ±10 % and the GWA-scaled case (labelled `SENSITIVITY`) |
| 6 | `loss_scenarios.json` | Low / nominal / high (labelled `LOSS SCENARIOS`) |
| 7 | `emissions.json` | Primary avoided CO₂ with a sampling-only CI; context methods; life-cycle GHG |
| 8 | `scenarios.json` | S1–S3 only (energy, CO₂, context, life-cycle, shares) plus a retirement note for S4 |
| 9 | `site_screening.json` | Bathymetry, ÖÇK overlap, ERA5 node, packing limit, screening classes, densities, unscreened topics |
| — | `MANIFEST.json` | Index with SHA-256 checksums |

Every file carries `"status": "PRE-SUBMISSION MODEL ESTIMATE — not a
validated project forecast"`. Future figure scripts must read only these
files, not `results/archive/` or `results/provisional/`.

---

## 5. Old versus revised headline results

| Quantity | Original (archived) | Revised (`results/revised/`) |
|---|---|---|
| Energy estimator | Weibull MC P50; deterministic total ÷ 11 | Empirical hourly, CF × 8 766 h |
| Net CF | 29.9 % (MC P50); 31.0 % (deterministic) | **27.69 %** |
| Net yield (GWh MW⁻¹ yr⁻¹) | 2.62 (P10–P90 2.41–2.83); 2.71 | **2.427** (90 % sampling CI 2.334–2.520) |
| Gross AEP per turbine | 30.4 GWh | **27.20 GWh** |
| Energy variability | "Inter-annual CoV 3.2 %" (wind speed, ddof 0) | Speed CoV 3.35 % (ddof 1); **energy CoV 7.0 %**; 2014 at 1.99, 2020 at 2.65 |
| Avoided CO₂ per MW | 1 525 t (P10–P90 1 277–1 754; mixed methods) | **1 515.2 tCO₂** (sampling-only CI 1 457–1 573; combined margin) |
| Life-cycle GHG per MW | Subtracted (11 g) | Separate: **29.1 tCO₂‑eq** (AR5 median; range 19.4–85.0) |
| S1 / S2 / S3 energy (GWh yr⁻¹) | 648 / 1 320 / 2 615 | **600 / 1 222 / 2 421** |
| S1 / S2 / S3 avoided CO₂ (kt yr⁻¹) | 377 / 768 / 1 521 | **374 / 763 / 1 511** |
| S4 | 4.56 TWh, 2.65 Mt | **Retired** |
| S3 share of 2024 consumption | 0.75 % | 0.70 % |
| Losses | Triangular samples | Low 2.586 / nominal 2.427 / high 2.225 GWh MW⁻¹ |
| Wind-speed ±10 % | Not reported | −20.4 % / +19.7 % AEP (sensitivity) |

---

## 6. Tests and verification

`python -m pytest -q tests/` gives **55 passed**: 39 earlier tests plus 16
new ones in `tests/test_revised_pipeline.py`.

The new tests check:

- **Headlines** equal Phase 3A (CF, yield, t-interval, bootstrap, CoV) and
  Phase 3B (avoided CO₂, its CI, life-cycle) to relative 10⁻¹².
- **Same energy throughout:** `emissions.json` uses the energy value in
  `energy_yield.json`, and each S1–S3 row equals E × MW (and × 0.6242).
- **S4 absent:** no S4 row and no 1738.5 anywhere in `results/revised/`.
  S4 appears only in the retirement note.
- **Normalisation and units:** leap years 2016/2020/2024 with 8 784 h;
  96 432 h in total; normalisation factor (96 432/11)/8 766; energy
  conservation in `annual_energy.csv`; GWh/MW = CF × 8.766.
- **Units by method:** CO₂ against CO₂‑eq is labelled per method, and the
  combined margin reproduces from the Tool 07 weights.
- **Labels:** distinct `OBSERVED`, `SAMPLING`, `SENSITIVITY` and
  `LOSS SCENARIOS` labels; every file has a status.
- **Phase 2B sensitivities** reproduced, and the GWA factor is 1.1014.
- **Screening** equals Phase 4A: ÖÇK 24.75 km², 25 positions; depths
  1.0 / 27.8 / 61.6 m; node 3.68 km outside the polygon; 62.6 % share.
- **No stale inputs:** production scripts reference no retired file, legacy
  factor, retired curve or historical `SCENARIOS`; no JSON or NPZ files
  remain in `results/`.
- **Checksums** match the manifest, and a fresh computation equals the
  committed outputs.

`tests/test_power_curve.py` was adapted: script 06 is loaded from `legacy/`,
and the archive test now asserts that the root copies are retired.

**Verification in a clean clone:** the full pipeline was rerun and the
outputs were compared against the committed ones (see the commit message).

**Problems fixed during integration:**

- My first legacy header broke `from __future__` ordering. It was fixed by
  merging the note into the original docstring.
- Two over-broad test patterns, a substring and then a regex, flagged the
  name `LOSS_SCENARIOS` and the label "LOSS SCENARIOS". The check was
  replaced by an AST-based identifier test.

---

## 7. Remaining inconsistencies and limitations

1. **Figures** in `figures/` and `figures_final/`, and **manuscript tables**,
   still show the original results. `scripts/05` (wind figure) was not
   re-run; the old figure scripts are in `legacy/`.
2. **Mean power density:** the manuscript's 422 W m⁻² is the
   Weibull-derived value. The empirical value in `wind_resource.json` is
   **416.8 W m⁻²**. The manuscript should use the empirical value.
3. **External references** with unverified primary sources are flagged in
   the outputs: the 347.9 TWh consumption figure, and the household and car
   equivalents. The equivalents were not carried forward.
4. **Scientific limitations** are unchanged from Phases 2B–4A: a single
   ERA5 node, a digitised curve, losses as assumptions, one wake value for
   every density, static 2023 factors, unscreened environmental topics, and
   draft tender rules.
5. **Inputs held under `docs/review/`:** `07_site_screening.py` and the
   GWA case in script 04 read data stored there (the KML, the EMODnet crop
   and the GWA crop). These are documented inputs with checksums, but
   moving them to `data/external/` would be cleaner.

---

## 8. What future figure and table scripts must use

| Manuscript element | Source |
|---|---|
| Resource table and figure (mean, power density, monthly, annual, wind rose) | `wind_resource.json`, `annual_energy.csv` (the wind rose may use the Parquet directly) |
| Energy table (Table 3) | `energy_yield.json`, `weibull_crosscheck.json`, `interannual_and_sampling.json` |
| Uncertainty figure (replaces old Fig. 5a–c) | `annual_energy.csv` (annual values), `interannual_and_sampling.json` (CI), `loss_scenarios.json`, `wind_speed_sensitivity.json`. **Separate panels; no histogram of MC samples** |
| Scenario table (Table 4) and figure | `scenarios.json` (S1–S3 only) |
| Emissions table (Table 5) and comparison figure | `emissions.json` |
| Site and constraints table or figure | `site_screening.json` |
