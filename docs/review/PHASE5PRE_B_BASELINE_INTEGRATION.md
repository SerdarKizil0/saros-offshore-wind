# Phase 5-PRE-B — Controlled long-term baseline integration

*14 November 2026. Implements the author's decision that followed Phase 5-PRE
(`PHASE5PRE_ERA5_ROBUSTNESS.md`). Manuscript, publication figures and
figure generators are unchanged. Phase 5B/5C not started.*

**Author decisions implemented**

1. **Primary period:** 1994–2024, same node, 40.50° N 26.25° E.
2. **Primary data:** ERA5 via the Open-Meteo historical API, explicitly
   labelled as such. It is calibrated against the CDS series and **not
   bit-identical** to the CDS.
3. **Historical baseline kept:** the CDS-derived 2014–2024 series and its
   results are retained for comparison and reproducibility.
4. **Neighbouring nodes:** treated as sensitivity experiments, not
   confidence bounds. They are not part of `results/revised/`; the
   evidence stays in `results/provisional/phase5pre/`.
5. **GWA scaling:** not used as a correction. It remains a labelled
   sensitivity case.

**Reproduce from a clean clone**

```bash
pip install -r requirements.txt
python scripts/run_revised_pipeline.py     # ~25 s, no download
python -m pytest -q tests/                 # 177 passed, 5 failed (pre-existing; §6)
```

---

## 1. What was changed

| Item | Change |
|---|---|
| `results/archive/baseline_2014_2024_cds/` | **New.** Byte-identical copy of the former `results/revised/` (commit `2ab13c1`), with `SHA256SUMS` and `README.md`. Archived **before** any change |
| `data/external/era5_openmeteo/` | **New primary input:** `era5_openmeteo_40.50N_26.25E_1994_2024.parquet` (U10, U100, wdir100; 271 752 h; 1.05 MB), `MANIFEST.json`, `README.md` |
| `scripts/02b_fetch_era5_openmeteo.py` | **New.** Fetches the primary input. It never overwrites the pin: a changed checksum is reported, not adopted |
| `config/wind_data.py` | **New.** `PRIMARY` and `HISTORICAL_CDS_2014_2024` specs (path, SHA-256 pin, period, node, data-product label) |
| `scripts/04_fit_weibull_aep.py` | See below |
| `scripts/06_emissions_and_scenarios.py` | See below |
| `scripts/07_site_screening.py` | Wind direction and speeds now come from the primary series (via `scripts/04` `load_series`) |
| `scripts/phase4a_site_checks.py` | `compute(..., wind=None)` takes an optional series. The default behaviour, and so the Phase 4A output, is unchanged |
| `scripts/run_revised_pipeline.py` | Manifest records the primary input (path, SHA-256, period, data product) and the comparison-only input. Now 11 output files |
| `scripts/phase5pre_era5_robustness.py` | Reads its 2014–2024 reference from the archive instead of `results/revised/`. All Phase 5-PRE numbers are unchanged; only one key name and the status string changed |
| Tests | See §5 |
| Documentation | `data/README.md`, `results/README.md`, `docs/DECISION_LOG.md` (superseded note) |

**`scripts/04_fit_weibull_aep.py`**

- `load_series(spec)`: verifies the SHA-256 pin and the complete hourly
  coverage. For Open-Meteo it builds `U_hub` from the series' own α.
- `run(series, out)`; `--series` / `--out` options. A non-primary series
  can never be written into `results/revised/`.
- Labels and periods are derived from the spec. Period-neutral key names:
  - `sampling_ci_of_period_mean` (was `sampling_ci_of_11yr_mean`);
  - `…_excluding_min_year` / `…_excluding_lowest_year` (was `…_excluding_2014`).
- New output `input_provenance.json`: input QA, recomputed on every run.

**`scripts/06_emissions_and_scenarios.py`**

- Reads the period from the energy output and refuses a period mismatch
  between `energy_yield.json` and the sampling CI.
- The CI label names the period.

**Unchanged:**

- the method: empirical hourly conversion, CF × 8 766 h;
- the OEDB V164/9500 curve;
- the losses: wake 8 %, availability 95 %, electrical 3 %, and the
  low/high scenarios;
- the hub height (105 m) and the α method;
- the 2023 combined margin, 0.6242 tCO₂/MWh, and the context factors;
- the life-cycle intensities;
- the S1–S3 capacities and the 7D × 5D assumption; S4 stays retired.

**No parameter was tuned.** The only data-derived parameter that changed
is α: 0.14923 → 0.14914, recomputed by the documented method from the new
series. Its effect is −0.001 % in energy.

---

## 2. New primary results (`results/revised/`, 1994–2024)

| Quantity | Value |
|---|---|
| Mean U100 / U_hub (105 m) | 7.007 / 7.058 m s⁻¹ |
| Power density at hub (ρ = 1.225) | 408.6 W m⁻² |
| Gross CF / net CF | 31.67 % / **26.85 %** |
| Gross / net AEP per 9.5 MW turbine | 26.38 / 22.36 GWh yr⁻¹ |
| **Net specific yield** | **2.3539 GWh MW⁻¹ yr⁻¹** (2 354 full-load hours) |
| 90 % sampling CI of the 1994–2024 mean (t, 31 annual values, df 30) [SAMP] | **2.300–2.407** (±2.27 %) |
| Check: year-block bootstrap, 90 % | 2.302–2.403 |
| SE of the mean, classical / bootstrap / jackknife | 1.34 / 1.31 / 1.34 % |
| Annual net-energy CoV [OBS] | 7.44 % (6.77 % without the lowest year) |
| Lowest / highest year | 2002 (1.944) / 2001 (2.674). 2014 is second lowest (1.992) |
| Annual mean-speed CoV | 3.64 % (ddof 1) |
| Lag-1 autocorrelation of annual CF | −0.08 |
| Weibull (descriptive): k / c / R² (CDF) / KS D | 1.980 / 7.950 m s⁻¹ / 0.998 / 0.021 |
| Weibull AEP vs empirical | −1.56 % (cross-check only) |
| Loss scenarios: low / nominal / high [assumption] | 2.507 / 2.354 / 2.158 GWh MW⁻¹ yr⁻¹ (+6.5 / 0 / −8.3 %) |
| Wind-speed sensitivity: −10 / −5 / +5 / +10 % [SENS] | −20.3 / −10.1 / +10.0 / +19.6 % AEP |
| GWA-scaled case (factor 1.119) [SENS, not a correction] | +23.2 % AEP |
| **Avoided operational CO₂** (2023 combined margin, CO₂ only) | **1 469.3 tCO₂ MW⁻¹ yr⁻¹** (90 % CI, energy sampling only: 1 436–1 503) |
| Context: operating margin / build margin / generation average (CO₂) | 1 679.3 / 839.6 / 1 012.2 tCO₂ MW⁻¹ yr⁻¹ |
| Context: generation average, CO₂-eq (different unit) | 1 021.6 tCO₂-eq MW⁻¹ yr⁻¹ |
| Life-cycle GHG, AR5 median [range] | 28.2 [18.8–82.4] tCO₂-eq MW⁻¹ yr⁻¹, reported separately, not subtracted |
| S1 247 MW | 581 GWh yr⁻¹ (568–595); 363 kt CO₂ yr⁻¹ (355–371) |
| S2 503.5 MW | 1 185 GWh yr⁻¹ (1 158–1 212); 740 kt CO₂ yr⁻¹ (723–757) |
| S3 997.5 MW | 2 348 GWh yr⁻¹ (2 295–2 401); 1 466 kt CO₂ yr⁻¹ (1 432–1 499); 0.67 % of 2024 consumption (347.9 TWh, unverified primary source) |

**Independent consistency.** The production value 2.3539 agrees with the
Phase 5-PRE estimate for 1994–2024:

- raw Open-Meteo value 2.3539, identical up to the α difference
  (−0.001 %);
- CDS-anchored value 2.3540 (+0.004 %).

---

## 3. Differences from the historical 2014–2024 baseline

| Quantity | 2014–2024 (archive) | 1994–2024 (primary) | Change |
|---|---|---|---|
| Mean U100 | 7.120 m s⁻¹ | 7.007 m s⁻¹ | −1.58 % |
| Power density at hub | 416.8 W m⁻² | 408.6 W m⁻² | −1.99 % |
| Gross CF | 32.66 % | 31.67 % | −3.03 % |
| Net CF | 27.69 % | 26.85 % | −3.03 % |
| Net yield | 2.4274 | **2.3539** GWh MW⁻¹ yr⁻¹ | **−3.03 %** |
| 90 % sampling CI | 2.334–2.520 (±3.83 %, n = 11) | 2.300–2.407 (±2.27 %, n = 31) | narrower |
| Annual energy CoV | 7.01 % | 7.44 % | — |
| Lowest year | 2014 | 2002 (2014 second) | — |
| Weibull k / c | 2.035 / 8.080 | 1.980 / 7.950 | — |
| Avoided CO₂ (CM) | 1 515.2 | **1 469.3** tCO₂ MW⁻¹ yr⁻¹ | −3.03 % |
| S3 energy / CO₂ | 2 421 GWh / 1 511 kt | 2 348 GWh / 1 466 kt | −3.03 % |
| Monthly mean U_hub, August | 7.55 m s⁻¹ | 6.95 m s⁻¹ | the late-summer secondary maximum is weaker in the long record |
| Monthly mean U_hub, December | 7.94 m s⁻¹ | 8.30 m s⁻¹ | winter maximum Dec–Feb in both |

**Screening.** Bathymetry, ÖÇK overlap (24.75 km², 14.4 %), node geometry,
packing (182 positions) and densities are identical, because they depend on
inputs only. Two things changed:

- **Energy-weighted prevailing axis:** 40.98° → 40.71°. The cause is the
  period: Open-Meteo gives 40.976° over 2014–2024, the same as the CDS. It
  is not the whole-degree rounding.
- **Screening-class counts of the best-fit grid:** the grid fit re-snapped.

| Class | Archive | Primary |
|---|---|---|
| Depth < 10 m | 14 | 15 |
| Depth 50–62 m | 19 | 23 |
| < 1 km from shore | 5 | 8 |
| Inside ÖÇK | 25 | 25 |
| Outside all classes | 123 | 117 |

A 0.3° rotation moving these counts by up to four positions shows they are
properties of one arbitrary grid fit, not robust site characteristics. They
should be reported, if at all, as illustrative.

---

## 4. Uncertainty components (kept separate; never combined)

| Component | Primary value | Where |
|---|---|---|
| Sampling uncertainty of the 31-year mean | ±2.27 % (90 % t) | `interannual_and_sampling.json` |
| Observed interannual variability | CoV 7.44 %; range 1.944–2.674 | same file, `annual_energy.csv` |
| Loss assumptions | −8.3 % / +6.5 % | `loss_scenarios.json` |
| Wind-speed level ±5 / ±10 % | ±10 / ±20 % AEP | `wind_speed_sensitivity.json` |
| ERA5–GWA disagreement | GWA/ERA5 = 1.119 at 100 m (polygon mean vs 1994–2024 node mean) → +23 % AEP if scaled | `wind_speed_sensitivity.json` (sensitivity, not a correction) |
| Neighbouring-node sensitivity | +6.6 % (26.00° E) / −8.7 % (26.50° E), 2014–2024 | `results/provisional/phase5pre/spatial.json` (sensitivity experiment, not a bound) |
| Input distribution (Open-Meteo vs CDS) | −0.004 % gross CF over 2014–2024 | `input_provenance.json` |

Accounting conventions for CO₂ (OM, BM, generation average) are reported as
context values, not as uncertainty.

---

## 5. Verification

| Test file | Tests | What it checks |
|---|---|---|
| `tests/test_revised_pipeline.py` (rewritten) | 20 | See list below |
| `tests/test_historical_baseline_2014_2024.py` (new) | 16 | See list below |
| `tests/test_phase5pre_robustness.py` | 16 | Re-pointed to the archive; Phase 5-PRE outputs reproduce |
| `tests/test_phase4c_figure.py`, `tests/test_phase4c_final_figures.py` | — | Pinned to the archive; see note below |

**`tests/test_revised_pipeline.py` checks:**

- input pin, manifest and README;
- complete hourly 1994–2024 coverage (271 752 h, 8 leap years);
- the loader refuses an unpinned file;
- the calibration QA is recorded and passes;
- every output carries period 1994–2024 (31 years, df 30);
- **independent recomputation** of α, gross and net CF, net yield and mean
  U_hub from the raw file with plain numpy (rel. 10⁻¹²);
- the t-interval and CoV recomputed from the 31 annual values;
- labels and separation of the uncertainty components;
- turbine and loss assumptions identical to the archive;
- emissions arithmetic and units: CO₂ vs CO₂-eq; life cycle not
  subtracted; CI label names the period;
- Tool 07 weights;
- scenario consistency, S1–S3 only, S4 retired;
- screening geometry identical, direction from the primary series;
- **no stale values:** no "2014-2024", "11yr" or "11-year" in authoritative
  outputs (except provenance), and no computed archive number reappears;
  only input-only geometry and factor values may;
- production code reads no archive or provisional files;
- manifest checksums and inputs;
- fresh in-memory recomputation equals the committed outputs;
- **clean-checkout reproduction:** copies only version-controlled files to
  a temporary directory, runs the pipeline and compares all 11 outputs
  byte for byte.

**`tests/test_historical_baseline_2014_2024.py` checks:**

- archive checksums;
- the archive against Phase 3A / 3B / 2B / 4A (the former Phase 4B tests);
- **current code in historical mode reproduces every archived number**
  (04, 06, 07; `annual_energy.csv` byte-identical);
- historical mode cannot write into `results/revised/`.

**Figure tests pinned to the archive.** The publication figures were
generated from the 2014–2024 results and must not change before Phase 5C.
The two figure-test modules therefore verify the committed figures against
`results/archive/baseline_2014_2024_cds/` (constant `FIGURE_RESULTS`, with
an explanatory comment).

- **No generator was changed.** The guard test that generators never read
  `results/archive` still applies to the generator source.
- A new test asserts that this pin is the documented archive and that it
  differs from the current primary results. **Phase 5C must regenerate the
  figures and remove the pin.**
- Without the pin, about 60 figure tests error or fail, because the
  generators' consistency checks reject the new results. That is the
  expected stale state, not a defect.

**Full suite:** 177 passed, 5 failed (§6).

**Clean clone.** The clean-checkout test passes. A real `git clone` of the
pushed branch (`fe9fd15`) followed by `python scripts/run_revised_pipeline.py`
regenerated all 11 output files byte-identically. `MANIFEST.json` differed
only in `code_commit_at_generation`, which records the generating commit
(`fe9fd15` instead of `a456d71`; the code is identical).

---

## 6. The five figure byte-comparison failures (pre-existing; cause documented)

`test_phase4c_final_figures.py::test_committed_outputs_match_the_generator[methodology | wind_weibull | power_curve | energy_sensitivity | avoided_co2]`

Regenerating each figure from the same (archived) inputs in this
environment gives:

| Check | Result |
|---|---|
| SVG | byte-identical |
| PNG | decoded pixel arrays identical |
| PDF, decompressed stream contents | identical |
| PDF, raw zlib-compressed stream bytes | differ |

**Cause:** a different zlib build or version compressed the committed
PDF/PNG files. This environment has zlib 1.3, matplotlib 3.11.2 and
Pillow 12.3.0.

- **The figure content is unchanged.** The annual-energy figure shows the
  same PDF-byte effect, but its test does not compare bytes.
- **Not fixed here:** no figure work in this phase. Phase 5C should either
  regenerate the files or compare decoded content instead of compressed
  bytes.

---

## 7. Unresolved limitations

1. **Absolute ERA5 level unvalidated.** GWA/ERA5 at 100 m is 1.12 against
   the 1994–2024 node mean, and 1.07–1.15 by node when period-matched
   (Phase 5-PRE). There are no offshore measurements.
2. **Single node outside the polygon.** The node is a mixed land–sea ERA5
   cell (land fraction 0.44). The neighbouring-node spread (−8.7 %/+6.6 %)
   exceeds the new sampling CI (±2.3 %) three- to four-fold. The two models
   disagree on the intra-polygon gradient.
3. **Primary data not from the CDS.** The Open-Meteo calibration is
   excellent (−0.004 %) but the source is a redistribution, not
   bit-identical; this must be stated in the paper. A CDS re-download of
   1994–2024 (request spec in `data/external/phase5pre/README.md`) would
   remove the caveat.
4. **Reanalysis homogeneity.** Recent windows are windier. A trend cannot
   be separated from changes in the assimilated observing system. 1994–2024
   is assumed representative of operation in the 2030s, which is untested.
5. **Turbine and losses unchanged as assumptions.** These are the digitised
   OEDB curve with undocumented air-density basis, losses as assumptions,
   one wake value for all densities, and the hourly rather than 10-minute
   basis.
6. **Carbon.** The static 2023 factor is a crediting convention, not a
   forecast of displacement. The life-cycle intensities are not
   Saros-specific.
7. **Screening-class counts depend on one grid fit** (§3).
8. **Stale downstream material.** The publication figures, captions and
   manuscript still carry 2014–2024 values (2.427, 1 515, CI 2.334–2.520,
   August secondary peak) and must be regenerated or rewritten in
   Phase 5B/5C.
