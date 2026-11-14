# Phase 5-PRE — ERA5 temporal and spatial robustness

*14 November 2026. This phase responds to the independent editorial review
(Phase 5B gate). It tests the existing estimate; it does not try to make
ERA5 agree with GWA. The manuscript, figures, tables, production pipeline
and `results/revised/` are unchanged. All outputs are **provisional**.*

**Labels**

- **[OBS]** — model output for given years. ERA5 is a reanalysis, so
  further years are more reanalysis years, *not* independent observations.
- **[SAMP]** — sampling interval.
- **[SENS]** — sensitivity experiment.
- **[DIS]** — inter-model disagreement.
- **[INT]** — interpolation.
- **[J]** — reviewer judgement.

No result here is a validation against measurements.

**Reproduce**

```bash
python scripts/phase5pre_fetch_inputs.py      # network, ~1 min; writes data/external/phase5pre/ (3.4 MB)
python scripts/phase5pre_era5_robustness.py   # offline, ~3 s; writes results/provisional/phase5pre/
python -m pytest -q tests/test_phase5pre_robustness.py   # 16 passed
```

---

## 0. Summary

| Question | Answer | Basis |
|---|---|---|
| 1. Is 2014–2024 materially different from a longer period? | **Yes, in a systematic sense.** At the same node, 2014–2024 is the **windiest of all 11-year windows**: 21 of 21 within 1994–2024 and 36 of 36 within 1979–2024. Its net yield is **3.0 % above** the 1994–2024 mean (3.2 % above 1979–2024). This lies inside the ±3.8 % sampling interval, but it is a one-sided selection effect, not noise. | `temporal.json`, `rolling_11yr.csv` |
| 2. Does node choice matter more than the 90 % sampling CI? | **Yes.** The neighbouring nodes differ by **+6.6 % (26.00° E)** and **−8.7 % (26.50° E)** in net yield: 1.7× and 2.3× the CI half-width. The offsets are systematic (paired annual difference sd ≈ 1.2 %). | `spatial.json` |
| 3. How much of the ERA5–GWA gap does the period mismatch explain? | **None.** ERA5 2008–2017 was *calmer* than 2014–2024 (U100 −1.8 %). Period matching therefore **widens** the gap from 10.1 % to 12.2 % in speed (share explained −19 %). | `gwa_period.json` |
| 4. Should the primary estimate change? | **Recommended [J]:** change the central estimate to the 1994–2024 long-term ERA5 mean at the same node: **2.354 GWh MW⁻¹ yr⁻¹, net CF 26.85 %** (−3.0 %). Keep node 26.25° E, and report the node spread as a separate spatial-representativeness term. This needs a decision (§7). | §3, §6 |
| 5. What remains unresolved? | The absolute ERA5 level (GWA/ERA5 1.07–1.15 by node, period-matched); the wind gradient inside the polygon (the two models disagree in sign); offshore measurement; power curve; losses; reanalysis homogeneity. | §6.5 |

---

## 1. Step 1 — Data inventory

| Item | Finding |
|---|---|
| Raw CDS NetCDF (`data/era5/era5_saros_YYYY_MM.nc`) | **Absent.** Gitignored and not present anywhere in this environment (a filesystem search for ERA5 NetCDF files found none) |
| Processed baseline (`data/processed/wind_hub_105m.parquet`) | Present, sha256 `0cfc4742…`. **One node only:** 40.50° N 26.25° E (`scripts/03` selects the nearest cell). 96 432 hours, 2014‑01‑01 00:00 to 2024‑12‑31 23:00 UTC; columns U10, U100, U_hub, wdir (float32) |
| Original request box (`config/site.py`) | 40.454–40.649° N, 25.989–26.511° E. On the 0.25° grid this contains the 40.50° N row at **26.00, 26.25 and 26.50° E**. Whether the raw files actually held all three **cannot be verified** without them |
| CDS credentials | **None** (no `~/.cdsapirc`, no CDS environment variables). A CDS retrieval was not possible |
| Neighbouring nodes in the archive | **Not extractable** from repository data |

**Substitute obtained (no synthetic data):**

- **Open-Meteo** historical API, `models=era5`, `cell_selection=nearest`.
  ERA5 at the three nodes, 1979–2024, U10 and U100. Each response reported
  exactly the requested grid point.
- **ARCO-ERA5** (Google public Zarr): the ERA5 static land–sea mask.

Provenance, checksums and the CDS-equivalent request are in
`data/external/phase5pre/README.md` and `MANIFEST.json`.

---

## 2. Is the Open-Meteo series usable? Calibration against the CDS baseline

Open-Meteo stores ERA5 with lossy compression, so it is not bit-identical
to a CDS download. Acceptance criteria were fixed in the script before use:

- hourly U100 r ≥ 0.99;
- pooled gross CF within ±1 %;
- every annual net yield within ±1 %.

Node 26.25° E, 2014–2024, 96 432 matched hours:

| Check | Result |
|---|---|
| U100 mean difference / RMSE / r | −0.00009 m/s / 0.041 m/s / 0.99994 |
| U10 mean difference / RMSE / r | −0.00009 m/s / 0.035 m/s / 0.99991 |
| Hours with \|ΔU100\| > 0.1 m/s | 0.21 % (largest 2.6 m/s; isolated hours) |
| Pooled gross CF (same α, same curve) | 32.661 % against 32.663 %: **−0.004 %** |
| Annual net yields | Largest difference 0.018 %; r = 0.9999995 |
| Rounding the CDS series to 0.01 m/s | +0.0003 % (two-decimal storage is irrelevant) |

**Verdict: fit for ratio analysis** (`fit_for_ratio_analysis: true`).

- Period and node results are reported both raw and **anchored**: CDS
  2014–2024 × (Open-Meteo X / Open-Meteo node C 2014–2024).
- Anchored and raw values differ by 0.004 %.
- The baseline is reproduced exactly: 2.42736680 GWh MW⁻¹ yr⁻¹, equal to
  `results/revised/energy_yield.json` (test).

**Method.** Unchanged from production:

- empirical hourly conversion with the OEDB V164/9500 curve and nominal
  losses;
- CF × 8 766 h;
- hub height from the ERA5 10/100 m trimmed-mean α.

The temporal analysis uses the baseline α = 0.14923 for all years.
Recomputing α over 1994–2024 gives 0.14914 and changes energy by −0.001 %.

---

## 3. Temporal robustness (node 40.50° N 26.25° E) [OBS]

### 3.1 Period means

| Period | Years | U100 (m/s, anchored) | ΔU100 | Gross CF | Net CF | Net yield (GWh MW⁻¹ yr⁻¹, anchored) | ΔE | Inside baseline 90 % CI (2.334–2.520)? |
|---|---|---|---|---|---|---|---|---|
| **2014–2024** (baseline) | 11 | 7.120 | — | 32.66 % | 27.69 % | **2.427** | — | — |
| 2015–2024 | 10 | 7.181 | +0.86 % | 33.25 % | 28.19 % | 2.471 | +1.79 % | yes |
| 2008–2017 (GWA period) | 10 | 6.989 | −1.83 % | 31.35 % | 26.58 % | 2.330 | −4.01 % | **no** |
| **1994–2024** | 31 | 7.007 | −1.58 % | 31.67 % | **26.85 %** | **2.354** | **−3.02 %** | yes (near lower edge) |
| 1979–2024 | 46 | 6.992 | −1.80 % | 31.62 % | 26.81 % | 2.350 | −3.18 % | yes |

1979–2024 and 1994–2024 agree to 0.2 %. The long-term level is therefore
not sensitive to where the long record starts.

### 3.2 Rolling 11-year windows (`rolling_11yr.csv`)

| | Within 1994–2024 (21 windows) | Within 1979–2024 (36 windows) |
|---|---|---|
| Range relative to the long-term mean | −3.4 % (1999–2009) to **+3.1 % (2014–2024)** | −3.2 % to **+3.3 % (2014–2024)** |
| Rank of 2014–2024 | **21 of 21 (highest)** | **36 of 36 (highest)** |
| 90 % t-interval half-width across windows | 2.5–5.0 % | 2.4–5.0 % |
| Windows whose 90 % CI contains the long-term mean | 21 / 21 | 36 / 36 |

- The five most recent windows (2010–2020 to 2014–2024) are all 1.8–3.1 %
  above the 1994–2024 mean.
- Linear trend in annual yield: +2.7 % per decade over 1994–2024
  (p = 0.065) and +1.0 % per decade over 1979–2024 (p = 0.20). This is
  descriptive only: reanalysis trends partly reflect changes in the
  assimilated observing system.
- The windows overlap and share years, so the coverage figure is
  descriptive, not a calibration test of the interval.

### 3.3 The 2014 low-wind year

| | Within 2014–2024 (Phase 3A) | Within 1994–2024 | Within 1979–2024 |
|---|---|---|---|
| Rank (1 = calmest) | 1 of 11 | **2 of 31** (only 2002 lower: 1.944 vs 1.992) | **2 of 46** |
| Relative to the period mean | −17.9 % | −15.4 % | −15.2 % |
| z against the other years | −5.0 | **−2.3** | −2.4 |
| Empirical return period (Weibull plotting position) | — | ≈16 years | ≈24 years |

- **2014 is a rare but not unprecedented calm year:** 2002 (1.944) and
  1999 (2.037) are comparable.
- Its extreme z-score within 2014–2024 is largely an artefact of the short,
  windy reference period.
- Phase 2B's station evidence (Çanakkale) already showed 2014 to be a
  genuine calm year. **It stays in the record.**

### 3.4 Interannual variability and the sampling CI

- **Annual net CoV:** 7.4 % (1994–2024) and 6.9 % (1979–2024), against
  7.0 % for 2014–2024. Lag-1 autocorrelation is −0.08 and −0.06, so
  treating years as exchangeable remains reasonable for this purpose.
- **The ±3.8 % interval depends on the window.** For the same window
  length, the 90 % t-interval half-width ranges from 2.4 % to 5.0 %.
- **The interval is conditional on the window.** It contained the 31-year
  mean here, but the window it was built on is the most extreme of all.
  [SAMP] It describes the finite-sample uncertainty of one window's mean;
  it does not describe selection of the window.
- **A 31-year mean** has a 90 % t-interval of 2.300–2.407 GWh MW⁻¹ yr⁻¹
  (±2.3 %). This is still conditional on ERA5 being correct, and still not
  a P90.

---

## 4. Spatial robustness (2014–2024, identical assumptions) [OBS]

### 4.1 Node geography

| | **W** 40.50° N 26.00° E | **C** 40.50° N 26.25° E (baseline) | **E** 40.50° N 26.50° E |
|---|---|---|---|
| ERA5 land–sea mask (cell land fraction) | **0.12** | **0.44** | **0.46** |
| Classification (rule: lsm < 0.2 offshore; 0.2–0.5 coastal/mixed; ≥ 0.5 land) | offshore | coastal / mixed | coastal / mixed |
| EMODnet elevation at the node | −66 m (sea) | −172 m (sea) | −175 m (sea) |
| EMODnet land share, 0.25° box | 2.0 % | 12.8 % | 39.6 % |
| Nearest land (within the EMODnet crop) | 14.0 km | 10.6 km | 4.2 km |
| Inside polygon? / distance to boundary | no / 4.97 km | no / 3.68 km | no / 9.14 km |
| Distance to polygon centroid | 17.9 km | 7.7 km | 26.3 km |
| Share of polygon nearest to the node | 27.7 % | 62.7 % | 9.6 % |

**What the land–sea mask shows.** All three nodes are *located* in the
sea. But in ERA5's own land–sea mask the baseline node is a **mixed
land–sea cell (44 % land)**. That is close to the 41.7 % geometric land
share of a 0.5° box (Phase 2B), consistent with ERA5's ≈31 km native grid
smearing the Thrace and Gelibolu coasts onto the point. Only the western
node is a marine cell in the model.

### 4.2 Wind and energy

| | W | **C** | E |
|---|---|---|---|
| α (own 2014–2024 series, documented method) | 0.100 | 0.149 | 0.140 |
| Mean U100 / U_hub (m/s) | 7.32 / 7.36 | 7.12 / 7.17 | 6.85 / 6.90 |
| U_hub P10 / P50 / P90 (m/s) | 2.34 / 7.06 / 12.56 | 2.52 / 6.96 / 11.87 | 2.54 / 6.69 / 11.32 |
| Power density at hub (W m⁻², ρ = 1.225) | 481 | 417 | 363 |
| Gross CF / net CF | 34.80 % / 29.51 % | 32.66 % / 27.69 % | 29.82 % / 25.28 % |
| **Net yield (GWh MW⁻¹ yr⁻¹, anchored)** | **2.587** | **2.427** | **2.216** |
| Relative to C | **+6.56 %** | — | **−8.70 %** |
| \|difference\| / CI half-width (3.83 %) | **1.7×** | — | **2.3×** |
| Paired annual difference vs C: mean ± sd (range) | +6.6 ± 1.2 % (5.0 to 8.5) | — | −8.7 ± 1.2 % (−10.3 to −7.2) |
| Annual correlation with C | 0.986 | 1 | 0.987 |
| 1994–2024 / 2014–2024 energy ratio | 0.971 | 0.970 | 0.972 |

- With the baseline α instead of each node's own α, W is 2.598 and
  E is 2.218; the difference is < 0.5 %.
- **The period effect is spatially coherent.** All three nodes are
  2.8–3.0 % lower over 1994–2024.
- **The node differences are systematic.** They persist every year with
  sd ≈ 1.2 %, so they are not reduced by adding years.
- The marine node W has the lowest shear (α = 0.100), close to the
  open-sea literature value. This is consistent with a less land-affected
  model profile at W [INT].

### 4.3 Interpolation (reported, not adopted) [INT]

Weighting the three nodes by the share of the polygon nearest to each
(0.277 / 0.627 / 0.096) gives 2.451 GWh MW⁻¹ yr⁻¹ (+1.0 % against C).

- This is interpolation of model output, **not validation**. It mixes
  cells with ERA5 land fractions from 0.12 to 0.46.
- It is not used as an estimate. Its small net effect comes from W and E
  offsetting each other; it is not evidence that C is representative.

---

## 5. ERA5 period versus the GWA reference period [DIS]

GWA 4.0 is ERA5-forced WRF/WAsP for 2008–2017. It is **not** ground truth,
and neither product has been validated offshore here.

| Quantity | Value |
|---|---|
| GWA 4.0 polygon mean at 100 m | 7.842 m/s |
| ERA5 node C U100, 2014–2024 (CDS) | 7.120 m/s → GWA / ERA5 = **1.101** |
| ERA5 node C U100, 2008–2017 (period-matched, anchored) | 6.989 m/s (−1.8 %) → GWA / ERA5 = **1.122** |
| Share of the (log) disagreement explained by the period | **−19 %** (the period mismatch *widens* the gap) |
| AEP change if the hours are scaled to GWA, unmatched / period-matched [SENS] | +20.0 % / +23.8 % |

**Per node: GWA 0.25° box (sea pixels only) against ERA5 2008–2017**

| | W (lsm 0.12) | C (lsm 0.44) | E (lsm 0.46) |
|---|---|---|---|
| GWA box, sea pixels only (m/s) | 7.69 | 8.06 (= Phase 2B) | 7.39 |
| ERA5 U100 2008–2017 (m/s) | 7.21 | 6.99 | 6.71 |
| Ratio, period-matched | **1.067** | **1.153** | **1.102** |

Interpretation:

- **The period mismatch is not the explanation.** The disagreement grows
  when periods are matched.
- **The disagreement is smallest at the most marine ERA5 cell (W)** and
  largest at the baseline cell. This is *consistent with* ERA5 land
  influence at C contributing to the gap [INT]. It does not prove it,
  because GWA's own coastal and microscale treatment differs.
- **The models disagree on the spatial pattern.** ERA5 ranks W > C > E;
  GWA ranks C > W > E. Neither the intra-polygon gradient nor its sign can
  be established from these products.

---

## 6. Scientific interpretation

1. **The 2014–2024 estimate is materially different from the longer
   record [J].** The difference is small in magnitude (−3.0 %, inside the
   ±3.8 % sampling interval) but systematic in direction: the baseline
   window is the windiest of all 21 or 36 windows. Keeping it as the
   central estimate builds in an upward selection bias of about 3 %. The
   bias is not visible from the 11 years alone.

2. **Node choice outweighs the sampling CI.** The plausible neighbouring
   nodes move net yield by +6.6 % and −8.7 %, i.e. 1.7–2.3× the CI
   half-width. The ±3.8 % interval therefore understates
   reanalysis-representation uncertainty by at least a factor of two. Node
   spread must be reported separately and never combined with the CI.

3. **The period mismatch explains none of the ERA5–GWA disagreement.**
   Period-matched, the polygon-level gap is 12.2 % in speed (≈ +24 % AEP
   sensitivity). Across nodes it ranges from 6.7 % (marine W) to 15.3 %
   (C).

4. **Recommended change of primary estimate [J]: from the 2014–2024 mean
   to the 1994–2024 mean at the same node.**

   | Option | Value | Why |
   |---|---|---|
   | **A (recommended)** 1994–2024 at node C | **2.354 GWh MW⁻¹ yr⁻¹ (net CF 26.85 %; gross 31.67 %)** | Standard long-term practice; removes the window-selection effect; 31 years; 1979–2024 confirms it (2.350) |
   | B: keep 2014–2024 | 2.427 | Requires an explicit statement that it is the windiest 11-year window, 3.0 % above the long-term mean |
   | Not recommended: switch to node W or to the interpolated value | 2.587 / 2.451 | No observational basis to prefer either. Switching would select the answer closest to GWA |

   Implication for CO₂ if A is adopted (arithmetic only; not computed in
   `results/`): 2.354 × 0.6242 = 1 469 tCO₂ MW⁻¹ yr⁻¹, instead of 1 515.

   Implementation caveat: the long series comes from Open-Meteo, calibrated
   to the CDS within 0.004 %. For final publication, either accept and cite
   this calibrated source, or re-download 1994–2024 from the CDS (§7).

5. **Unresolved after this phase:**
   - the absolute ERA5 level (GWA/ERA5 1.07–1.15 by node; no
     measurement);
   - the wind gradient across the polygon (models disagree in sign; the
     baseline node sits outside the zone in a mixed land–sea cell);
   - the digitised power curve, air density, losses and single wake value;
   - the hourly vs 10-minute basis;
   - reanalysis homogeneity (recent windows are windier; the trend cannot
     be separated from observing-system change);
   - representativeness of 1994–2024 for operation in the 2030s;
   - the Open-Meteo vs CDS distribution (calibrated, not identical).

---

## 7. Decision required before Phase 5B

1. **Primary period.** Adopt option A (1994–2024 at node 26.25° E; 2.354
   GWh MW⁻¹ yr⁻¹) or keep option B with explicit disclosure.
2. **Data source for the long period.** Accept the calibrated Open-Meteo
   ERA5 series with citation, or provide CDS credentials for a
   1994–2024 re-download (request spec in
   `data/external/phase5pre/README.md`).
3. **How to report spatial representativeness.** Recommended: node spread
   of −8.7 % / +6.6 % as its own labelled sensitivity, plus the ERA5
   land–sea-mask finding. Never averaged into the central estimate, never
   merged with the CI.

If A is chosen, `results/revised/` must be regenerated by an explicit
production change (a separate step, with tests). This phase did not change
it.

---

## 8. Files and tests

| File | Content |
|---|---|
| `scripts/phase5pre_fetch_inputs.py` | Network fetch (Open-Meteo ERA5 at 3 nodes, 1979–2024; ERA5 land–sea mask), manifest |
| `scripts/phase5pre_era5_robustness.py` | Offline analysis; reuses `scripts/03` (α) and `scripts/04` (power curve, annual table, pooled CF) |
| `data/external/phase5pre/` | Inputs, `README.md` (provenance, licences, CDS spec), `MANIFEST.json` |
| `results/provisional/phase5pre/` | `calibration.json`, `temporal.json`, `rolling_11yr.csv`, `annual_energy_1979_2024.csv`, `spatial.json`, `node_geography.json`, `gwa_period.json`, `MANIFEST.json` |
| `tests/test_phase5pre_robustness.py` | 16 tests |

**What the 16 tests check:**

- input checksums;
- the returned grid points;
- complete hourly series;
- exact baseline reproduction;
- the calibration criteria;
- anchoring identity;
- the baseline CI equal to `results/revised`;
- energy conservation;
- rolling-window consistency;
- polygon shares and the 3.68 km distance;
- interpolation labelled "not adopted";
- committed outputs equal a fresh run;
- `results/revised/` checksums unchanged.

**Full suite:** 156 passed, 5 failed. The 5 failures are pre-existing and
unrelated to this phase: `test_phase4c_final_figures.py::test_committed_outputs_match_the_generator`
for five figures. Regenerated PDF and PNG files differ from the committed
ones in compressed bytes, while the SVGs are byte-identical. This points to
an environment (zlib/libpng) dependence, not a content change. They fail
identically on the unmodified branch.
