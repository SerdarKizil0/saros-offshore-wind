# Phase 5B-0 — Addendum to the Phase 5A manuscript revision plan

*14 November 2026. This addendum synchronises
`PHASE5A_MANUSCRIPT_REVISION_PLAN.md` with the decisions and results that
came after it: Phase 5-PRE (ERA5 robustness), Phase 5-PRE-B (1994–2024
baseline), Phase 5-PRE-C (novelty and source audit) and the final scope
decision (CONDITIONAL GO). The manuscript, publication figures and figure
generators are unchanged. Phase 5B-1 has not started.*

**How to use the two documents**

- The 5A plan remains valid for everything that does not depend on the
  wind period, the scope or the sources: its issue list (C01–C18, M01–M34,
  m01–m22), the claims to remove, the equation changes, the workflow fixes.
- Wherever 5A states a numerical value from the 2014–2024 results, or an
  instruction built on them, **this addendum takes precedence**.
- Every number must be read from `results/revised/` by script. The values
  quoted below are for orientation and are checked against the result files
  by `tests/test_phase5b0_sensitivity.py`.

---

## 1. Authoritative baseline

| Item | Value | File → key |
|---|---|---|
| Period | 1994–2024 (31 calendar years, 271 752 hours) | `energy_yield.json` → `period`, `normalisation_check` |
| Source | ERA5 delivered through the Open-Meteo historical API; calibrated against the historical CDS series (gross CF −0.004 % over the common years); **not bit-identical to CDS** | `input_provenance.json` |
| Node | 40.50° N, 26.25° E (outside the polygon, 3.68 km; ERA5 land–sea mask 0.44) | `site_screening.json`, `node_sensitivity.json` |
| Net specific yield | **2.3539 GWh MW⁻¹ yr⁻¹** | `energy_yield.json` → `net.gwh_per_mw` |
| Net capacity factor | **26.85 %** (gross 31.67 %) | `energy_yield.json` → `net_cf`, `gross_cf` |
| Sampling-only 90 % interval of the mean | **2.300–2.407 GWh MW⁻¹ yr⁻¹** (t, 31 annual values, df 30) | `interannual_and_sampling.json` → `sampling_ci_of_period_mean` |
| Operational avoided-grid-CO₂ accounting equivalent | **1 469.3 tCO₂ MW⁻¹ yr⁻¹** (2023 combined margin, CO₂ only) | `emissions.json` → `primary_avoided_operational_co2` |

The 2014–2024 CDS results are historical. They are archived in
`results/archive/baseline_2014_2024_cds/` and must not be mixed with the
values above.

---

## 2. Superseded 5A values

"5A value" is the value 5A gives as *New* (its §2, §4, Appendix A) or as
*remains valid* (its §1.2–§1.8). All of them came from the 2014–2024
results.

### 2.1 Data and wind resource

| Quantity | 5A value (superseded) | Current value | File → key |
|---|---|---|---|
| Record | 2014–2024; 96 432 h; 11 years | 1994–2024; 271 752 h; 31 years | `energy_yield.json` |
| Data source wording | "committed ERA5 series" (CDS) | Open-Meteo-delivered ERA5, calibrated, not bit-identical to CDS | `input_provenance.json` |
| Mean / SD / median U_hub | 7.17 / 3.66 / 6.96 m s⁻¹ | 7.06 / 3.69 / 6.80 m s⁻¹ | `wind_resource.json` → `U_hub` |
| Mean U100 | 7.12 m s⁻¹ | 7.007 m s⁻¹ | `wind_resource.json` → `U100` |
| Power density at hub | 417 W m⁻² (Weibull 422) | 408.6 W m⁻² (Weibull 413.6) | `wind_resource.json`; `weibull_crosscheck.json` |
| Weibull k, c (MLE) | 2.035, 8.080 | 1.980, 7.950 m s⁻¹ | `weibull_crosscheck.json` → `weibull_fit_U_hub` |
| Justus k, c | 2.08, 8.10 | 2.02, 7.97 | same |
| R² (CDF), KS D | 0.998, 0.022 | 0.998, 0.021 | same |
| Weibull vs empirical gross CF | 32.06 % vs 32.66 % (−1.85 %) | 31.18 % vs 31.67 % (−1.56 %) | `weibull_crosscheck.json` |
| α statistics (mean / median / SD / P5–P95) | 0.149 / 0.142 / 0.054 / 0.074–0.252 | 0.149 / 0.141 / 0.055 / 0.072–0.254 | `wind_resource.json` → `shear_exponent_from_era5_10m_100m` |
| Annual mean-speed CoV | 3.35 % (1.83 % without 2014) | 3.64 % (3.31 % without the lowest year, 2002) | `wind_resource.json` → `annual_mean_cov_pct` |
| Annual mean-speed range | 6.55 (2014) – 7.41 (2016) m s⁻¹ | 6.44 (2002) – 7.52 (2001) m s⁻¹ | `wind_resource.json` → `annual_mean_U_hub_ms` |
| Monthly means | Feb 8.42, Jan 8.24, Jun 5.62, Aug 7.55 m s⁻¹ | Dec 8.30, Feb 8.14, Jan 8.04, Jun 5.51, Aug 6.95 m s⁻¹ | `wind_resource.json` → `monthly_mean_U_hub_ms` |
| Direction, hours | NE 25.8 %, ENE 18.4 % | NE 25.5 %, ENE 17.8 % | `wind_resource.json` → `direction_share_pct` |
| Direction, energy | NE 33.0, NNE 17.8, ENE 17.3, SSW 13.5 %; axis 41° | NE 33.1, NNE 17.2, ENE 16.5, SSW 13.6 %; axis 40.7° | same; `site_screening.json` → `wind_direction` |

### 2.2 Energy and its uncertainty categories

| Quantity | 5A value (superseded) | Current value | File → key |
|---|---|---|---|
| Gross AEP per turbine / gross CF | 27.20 GWh / 32.66 % | 26.38 GWh / 31.67 % | `energy_yield.json` |
| Net AEP per turbine / net CF | 23.06 GWh / 27.69 % | 22.36 GWh / 26.85 % | same |
| Net yield | 2.427 (2.4274) GWh MW⁻¹ yr⁻¹ | 2.3539 GWh MW⁻¹ yr⁻¹ | same |
| Full-load hours | 2 427 h | 2 354 h | same |
| 90 % sampling interval | 2.334–2.520 (t, df 10; ±3.8 %) | 2.300–2.407 (t, df 30; ±2.27 %) | `interannual_and_sampling.json` |
| Bootstrap check | 2.340–2.500 | 2.302–2.403 | same |
| SE of the mean | 2.11 % | 1.34 % | same |
| Annual energy CoV | 7.0 % (3.8 % without 2014) | 7.44 % (6.77 % without the lowest year) | same |
| Single-year range | 1.99 (2014) – 2.65 (2020) | 1.944 (2002) – 2.674 (2001) | same; `annual_energy.csv` |
| Calm year | 2014: −17.9 % | 2002 is lowest (−17.4 %); 2014 is second lowest (1.992; −15.4 %) | `annual_energy.csv` |
| Loss scenarios (low / nominal / high) | 2.586 / 2.427 / 2.225 | 2.507 / 2.354 / 2.158 (+6.5 / 0 / −8.3 %, unchanged in relative terms) | `loss_scenarios.json` |
| Speed −10 / −5 / +5 / +10 % | 1.931 / 2.180 / 2.670 / 2.905 (−20.4 / −10.2 / +10.0 / +19.7 %) | 1.876 / 2.115 / 2.588 / 2.816 (−20.3 / −10.1 / +10.0 / +19.6 %) | `wind_speed_sensitivity.json` |
| ERA5 vs GWA at 100 m | 7.12 vs 7.84 m s⁻¹ (×1.10); scaled case 2.912 (+20.0 %) | 7.007 vs 7.842 m s⁻¹ (×1.119 against 1994–2024; ×1.122 period-matched); scaled case 2.901 (+23.2 %), illustrative only | `wind_product_discrepancy.json`; `wind_speed_sensitivity.json` |

### 2.3 Emissions, scenarios, screening

| Quantity | 5A value (superseded) | Current value | File → key |
|---|---|---|---|
| Avoided CO₂ per MW (combined margin) | 1 515.2 (1 457–1 573) tCO₂ | 1 469.3 (1 436–1 503) tCO₂ | `emissions.json` |
| Context: OM / BM / generation average (CO₂) | 1 731.7 / 865.8 / 1 043.8 | 1 679.3 / 839.6 / 1 012.2 tCO₂ MW⁻¹ yr⁻¹ | `emissions.json` → `context_grid_methods` |
| Context: generation average, CO₂-eq | 1 053.5 | 1 021.6 tCO₂-eq MW⁻¹ yr⁻¹ | same |
| Life-cycle GHG (AR5 median; range) | 29.1 (19.4–85.0) | 28.2 (18.8–82.4) tCO₂-eq MW⁻¹ yr⁻¹ | `emissions.json` → `secondary_lifecycle_ghg` |
| Life-cycle, Bonou plants | 18.9–26.5 | 18.4–25.7 | same |
| S1 (247 MW) | 600 GWh (577–623); 374 kt (360–389) | 581 GWh (568–595); 363 kt (355–371) | `scenarios.json` |
| S2 (503.5 MW) | 1 222 GWh (1 175–1 269); 763 kt (734–792) | 1 185 GWh (1 158–1 212); 740 kt (723–757) | same |
| S3 (997.5 MW) | 2 421 GWh (2 328–2 514); 1 511 kt (1 453–1 569); life cycle 29.1 (19.4–84.7) | 2 348 GWh (2 295–2 401); 1 466 kt (1 432–1 499); life cycle 28.2 (18.8–82.2) kt CO₂-eq | same |
| S3 share of national consumption | 0.70 % of 347.9 TWh (unverified) | 0.664 % of 353 579.8 GWh gross consumption (§5) | `scenarios.json` → `share_of_2024_gross_consumption_pct` |
| Screening classes of the best-fit grid (<10 m / 50–62 m / <1 km / ÖÇK / none) | 14 / 19 / 5 / 25 / 123 | 15 / 23 / 8 / 25 / 117 | `site_screening.json` → `screening_classes_best_fit_layout` |

**Unchanged** (input-only quantities): polygon geometry and area;
bathymetry (1.0–61.6 m, median 27.8 m); ÖÇK overlap (≈25 km², ≈14.4 %);
node position (3.68 km, 62.6 %); packing (182 positions); scenario
densities; emission factors; loss assumptions; S3 share of the 5 GW target
(19.95 %).

---

## 3. Superseded and changed 5A instructions

| 5A item | Change |
|---|---|
| §1.2–§1.8 "Remains valid" lists | The wind statistics listed there as valid (period, mean, SD, median, α statistics, Weibull k and c, monthly values, annual range, direction shares) are **not** valid any more. Use §2.1. Everything non-numerical in those lists stays |
| §1.2 Abstract rewrite target | Rebuild from §1 and §4 of this addendum and the scope in §6: long-term yield first, then the period, node and wind-product sensitivities, one sentence each for the protected-area overlap and for CO₂ accounting |
| C01, Eq. 5 | N is the number of hours of the primary series (§2.1). The data sentence must name the Open-Meteo-delivered ERA5 series and its calibration |
| C03 | Replace values using §2 here, not 5A §2 |
| C04, 5A Table 6 | "Four separate components" becomes **six separate categories** (§4): sampling uncertainty; interannual variability; period-selection sensitivity; grid-node sensitivity; wind-product discrepancy; loss-assumption sensitivity. Source: `sensitivity_index.json`. They are never combined |
| new Eq. 9 | t-interval from the 31 annual yields: Ȳ ± t₀.₉₅,₃₀ · s_Y/√31 |
| C13 | Add: the node is a mixed land–sea ERA5 cell (land–sea mask 0.44); the western neighbour is the only marine cell (0.12). Source: `node_sensitivity.json` |
| C17 | Report both ratios with their periods (§4.3). Period matching does not reduce the disagreement. Keep "inter-model disagreement, not a demonstrated ERA5 bias"; the scaled case is illustrative and is not applied |
| C18 | Use the variability values of §2.2. The calm-year statement changes: the lowest year is 2002, and 2014 is the second lowest |
| C15, M24 | Still remove the demand-alignment claim. Describe seasonality with the 1994–2024 monthly values: winter maximum December–February, June minimum, and a weaker late-summer secondary maximum than in 2014–2024 |
| C12, M25 | Wording from Phase 5-PRE-C: "boundary of Decision 2010/1089, reconstructed from the decree coordinates (no datum stated); no later amendment found as of 14 November 2026". Give "≈14 % (≈25 km²)" |
| Screening-class counts (5A §2.1, Table 1) | Supplementary only, labelled illustrative: a 0.3° change of the fitted axis moved the counts by up to four positions (5-PRE-B §3) |
| M06, M07, M08 | No "first" claim of any kind (§6). An earlier study of a Saros region exists (Yildirim 2023). 2018 and 2023 candidate sets existed |
| M10 | Resolved: §5. Editorial recommendation: keep the share out of the main text; it stays available in `scenarios.json` |
| M13 | Title and framing from §6 |
| M14, 5A §1.9 | Item 3 ("eleven years of record … long-term representativeness is unknown") is replaced by the period-selection result (§4.1). Item 1 gains the node-sensitivity numbers (§4.2). Item 2 uses the ratios of §4.3. Add: the primary data are an Open-Meteo redistribution of ERA5 (calibrated, not bit-identical); reanalysis homogeneity over 31 years; 1994–2024 assumed representative of future operation |
| M16 | Resolved: the 5 GW (2035) figure is in the *Türkiye Ulusal Enerji Planı 2022* (24.6 GW onshore + 5 GW offshore). Cite it, not the World Bank |
| M19 | Use the SE of §2.2 |
| M34, 5A §5 (figures) | All figures in `figures/revised/` were generated from the 2014–2024 results and are stale. Phase 5C must regenerate them from `results/revised/`, add figures for the rolling windows and the node comparison, and remove the temporary `FIGURE_RESULTS` pin in the figure tests. No caption file may be used verbatim before regeneration |
| 5A §4 Table 3 | Regenerate with §2 values; one column |
| 5A §4 Table 4 | Main text: one illustrative ≈1 GW case (S3), conditional on the draft tender. S1 and S2 move to supplementary material |
| m04, m20 | Data description and data-availability statement name both inputs: the primary Open-Meteo series (`data/external/era5_openmeteo/`, SHA-256 pinned) and the historical CDS series |
| m19 (future work) | The neighbouring-node extraction and the period-matched ERA5–GWA comparison are **done**. Future work is now: offshore measurement; a CDS re-download of 1994–2024; a third wind product (NEWA or CERRA); a reference turbine with a public tabulated curve |
| 5A §6.3 | Resolved: consumption (§5), 5 GW source (M16), tender status (draft; no final notice up to 14 November 2026). Still secondary only: the 2023 candidate-area notice |
| 5A §6.4 (new references) | Add: Yildirim 2023; Cali et al. 2018; *Türkiye Ulusal Enerji Planı 2022*; TEDAŞ 2025 sector report; World Bank 2024 roadmap; Open-Meteo (Zippenfenig 2023); Global Wind Atlas (Davis et al. 2023); Gandoin & Garza 2024. The inventory with DOIs is `phase5pre_c_reference_inventory.csv` |
| 5A §6.1 Duzcan & Kara | Crossref gives 20(5), 5571–5584, which conflicts with the pages in 5A. Confirm on the publisher page |
| 5A §8 risks 1 and 4 | Risk 1 (resource level): now quantified as three separate sensitivities (§4). Risk 4 (novelty): see §6 |
| 5A §9 sequence | 5B-1 builds the tables from `results/revised/` including `sensitivity_index.json`. Results follow the architecture in §6. 5B-7 uses the retired-value list of §7 |
| 5A Appendix A | Replaced by §1 |
| 5A Appendix B | Replaced by §7 |

---

## 4. Promoted sensitivity evidence (now in `results/revised/`)

Produced by `scripts/08_sensitivity_representativeness.py` in the production
pipeline. Reference for every experiment: the primary estimate of §1.

**The six categories are different kinds of quantity. They are not
components of one calibrated probabilistic uncertainty interval and must
not be added, root-sum-squared or merged** (`sensitivity_index.json`,
`combinable_into_one_interval: false`).

| # | Category | Kind | Headline | File |
|---|---|---|---|---|
| 1 | Sampling uncertainty of the 1994–2024 mean | Probabilistic interval (the only one) | 2.300–2.407; ±2.27 % | `interannual_and_sampling.json` |
| 2 | Interannual variability | Observed spread of single years | CoV 7.44 %; 1.944 (2002) to 2.674 (2001) | same; `annual_energy.csv` |
| 3 | Period-selection sensitivity | Sensitivity experiment | §4.1 | `period_sensitivity.json`, `rolling_11yr_windows.csv` |
| 4 | Grid-node sensitivity | Sensitivity experiment | §4.2 | `node_sensitivity.json` |
| 5 | Wind-product discrepancy | Inter-model disagreement | §4.3 | `wind_product_discrepancy.json`, `wind_speed_sensitivity.json` |
| 6 | Loss-assumption sensitivity | Labelled assumption scenarios | +6.5 % / −8.3 % | `loss_scenarios.json` |

### 4.1 Period selection (same node, same method, primary α)

| Period | Net yield (GWh MW⁻¹ yr⁻¹) | Change vs 1994–2024 |
|---|---|---|
| 1994–2024 (reference) | 2.3539 | — |
| 1979–2024 | 2.3501 | −0.16 % |
| 2008–2017 (GWA period) | 2.3300 | −1.01 % |
| Recent 11 years (2014 to 2024) | 2.4272 | **+3.12 %** |
| 2015–2024 | 2.4707 | +4.97 % |

- **Rolling 11-year windows:** 21 windows inside 1994–2024 range from
  −3.39 % (1999–2009) to +3.12 %. The most recent window is the
  **highest of all 21**, and the highest of all 36 windows of 1979–2024.
  The full series with ranks is in `rolling_11yr_windows.csv`.
- "+3.12 % above the reference" and "the reference is 3.03 % below the
  recent window" are the same fact expressed on two bases.
- The Open-Meteo value for the recent window differs from the archived CDS
  value by −0.005 % (input calibration).

### 4.2 Grid node (1994–2024, identical method, each node's own α)

| Node | ERA5 land–sea mask | α | Net yield | vs primary node | Paired annual difference (mean ± sd; range) |
|---|---|---|---|---|---|
| 40.50° N 26.00° E | 0.12 (offshore) | 0.100 | 2.5117 | **+6.70 %** | +6.7 ± 1.0 % (5.0 to 8.6) |
| **40.50° N 26.25° E (primary)** | 0.44 (coastal/mixed) | 0.149 | 2.3539 | — | — |
| 40.50° N 26.50° E | 0.46 (coastal/mixed) | 0.138 | 2.1536 | **−8.51 %** | −8.5 ± 1.0 % (−10.4 to −6.4) |

- These replace the 2014–2024 node differences quoted in Phase 5-PRE
  (+6.56 % and −8.70 %).
- No node lies inside the polygon. The values are model output, not
  measurements. They are **not averaged** and **not confidence bounds**.
- The differences persist in every year, so they are systematic and are not
  reduced by a longer record.

### 4.3 Wind product (ERA5 vs Global Wind Atlas 4.0)

| Comparison | GWA 4.0 (2008–2017) | ERA5 U100 | Ratio |
|---|---|---|---|
| Polygon mean vs primary node, ERA5 1994–2024 | 7.842 m s⁻¹ | 7.007 m s⁻¹ | 1.119 |
| Polygon mean vs primary node, ERA5 2008–2017 (period-matched) | 7.842 | 6.989 | 1.122 |
| 0.25° box, sea pixels, at 26.00° E, period-matched | 7.689 | 7.208 | 1.067 |
| Same at 26.25° E | 8.061 | 6.989 | 1.153 |
| Same at 26.50° E | 7.395 | 6.708 | 1.102 |

- This is disagreement between two models. GWA is ERA5-driven and is not
  ground truth; neither product is validated offshore here.
- Period matching widens the ratio slightly. It does not explain it.
- The products disagree on the spatial ordering of the three cells
  (ERA5: west > centre > east; GWA: centre > west > east).
- If every primary hour were scaled by the ratio, AEP would change by
  +23.2 % (unmatched) or +23.8 % (period-matched). This is an illustrative
  sensitivity. **The primary estimate is not rescaled.**

---

## 5. Superseded national-consumption denominator

- **Superseded:** 347.9 TWh (2024). It appears only in secondary sources
  (Phase 5-PRE-C).
- **Adopted:** **353 579.8 GWh**, the official 2024 **gross** consumption
  ("Türkiye tüketimi" = gross generation 354 570.2 + imports 2 681.6 −
  exports 3 671.9 GWh). It includes plant internal use and network losses.
  - Source: TEDAŞ, *2025 Yılı Türkiye Elektrik Dağıtımı Sektör Raporu*,
    Table 5 (data: TEİAŞ); document SHA-256 `72f02193…`.
  - Net consumption (308 673.9 GWh) is recorded but not used.
- **Effect:** only the optional share metric changes. S3 is 0.664 % of
  gross consumption. The key is renamed
  `share_of_2024_gross_consumption_pct`, and
  `scenarios.json → consumption_reference` carries the source and
  definition.
- **Nothing else changed.** All ten other result files that existed before
  this phase are byte-identical (test).

---

## 6. Scope decisions carried into Phase 5B

These are editorial decisions (final scope memo), not new findings.

- **Central contribution:** sensitivity and spatial/temporal
  representativeness of a reanalysis-based estimate, anchored by the
  preliminary long-term energy yield.
- **Research question:** for the Gulf of Saros candidate area announced on
  13 May 2026, what long-term net specific yield does ERA5 (1994–2024) give
  for a reference 9.5 MW turbine, and how sensitive is it to the reference
  period, the grid node, the wind data source and the loss assumptions?
- **Working title:** *Long-term reanalysis-based energy yield of the Gulf
  of Saros offshore wind candidate area, Türkiye: sensitivity to reference
  period, grid node and wind data source.*
- **Results architecture:** long-term yield → sampling interval and
  interannual variability → period selection → grid node → wind product →
  losses → site screening (bathymetry, ≈14 % ÖÇK overlap) → CO₂ accounting
  (short).
- **Yildirim (2023), while its full text is unavailable.** State only what
  the abstract and data statement support: it analysed three candidate
  regions of the 2018 tender process with Global Wind Atlas data and
  reported its best results for a Saros region. Do not quote its capacity
  factor, energy or area, do not compare numbers, and state that the
  spatial relation between its area and the 2026 polygon could not be
  established.
- **No "first" claim.** Describe the object factually (the polygon
  announced on 13 May 2026).
- **Wording to avoid:** "site-specific", "validated", "bankable",
  "designated zone", "uncertainty quantified/propagated", "ERA5
  underestimates", any statement that treats the GWA ratio or the node
  range as a confidence interval or bound, unconditional "avoids X Mt CO₂".
- **Main text vs supplementary:** as listed in the final scope memo;
  Weibull, direction, calibration detail, bootstrap/jackknife, S1/S2,
  life-cycle table, screening-class counts and the historical 2014–2024
  results are supplementary.

---

## 7. Retired-value list (replaces 5A Appendix B)

No pattern below may appear in `manuscript/*.md`, `tables.md` or the built
document as a current result. This list **adds** the 2014–2024 values to
the patterns of 5A Appendix B, which stay retired.

- **Energy:** `2.427`, `2.4274`, `27.69`, `27.7 %`, `32.66`, `27.20`,
  `23.06`, `2 427 h`, `2.334`, `2.520`, `2.340–2.500`, `±3.8 %`,
  `2.586`, `2.225`, `1.931`, `2.180`, `2.670`, `2.905`, `2.912`.
- **Variability:** `7.0 %` (energy CoV), `3.35 %`, `1.83 %`, `−17.9 %`,
  "2014 is the lowest year", `1.99–2.65`.
- **Wind:** `7.17`, `3.66`, `6.96`, `417 W`, `422 W`, `2.035`, `8.080`,
  `−1.85 %`, `8.42`, `8.24`, `5.62`, `7.55`, `×1.10`, `+20.0 %`.
- **Emissions and scenarios:** `1 515`, `1515.2`, `1 457–1 573`,
  `1 731.7`, `865.8`, `1 043.8`, `1 053.5`, `29.1`, `19.4–85.0`,
  `600 GWh`, `1 222`, `2 421`, `374 kt`, `763 kt`, `1 511`, `347.9`,
  `0.70 %`.
- **Record:** `96 432`, "11-year mean", "eleven years", `df = 10`.
- **Phrases:** "first peer-reviewed", "first site-specific", "first
  assessment", "no peer-reviewed assessment exists".

The period label for 2014 to 2024 may appear only where it is explicitly a
comparison period (period-selection sensitivity, historical baseline).

---

## 8. Status for Phase 5B-1

- **Closed by this phase:** the 5A plan is synchronised; the sensitivity
  evidence is in the authoritative results with tests; the consumption
  denominator is corrected.
- **Open, not blocking the start of 5B-1** (tables, Methods, Study area,
  Results): none.
- **Open, blocking the final Introduction and Discussion:** the full text
  of Yildirim (2023) and a database literature sweep (Scopus or Web of
  Science). Until then the rules of §6 apply.
- **Deferred to Phase 5C:** figure regeneration and removal of the
  figure-test pin; reference list.
