# Phase 4C-FINAL — Publication figure set

*12 November 2026. Completes the revised figure set for the Saros offshore wind
manuscript. All figures read only the production outputs in `results/revised/`,
the committed hourly series and documented inputs (Phase 4B §8). The manuscript,
the scientific model, `results/` and the historical figures in `figures/` and
`figures_final/` are unchanged.*

---

## 1. Final figure inventory

Proposed manuscript order. Every figure is 180 mm wide (two-column), drawn at
print size with `config/figure_style.py`, and exported as vector PDF, editable SVG
and 600 dpi PNG under `figures/revised/`.

| No. | File stem | Content | Size (mm) | Status |
|---|---|---|---|---|
| 1 | `saros_study_area` | Study area, ÖÇK overlay, bathymetry, ERA5 node | 180 × 109 | Approved earlier (refined 12 Nov) |
| 2 | `methodology` | Workflow of the production model | 180 × 115 | **New** |
| 3 | `wind_weibull` | Hourly hub-height speed distribution, Weibull fit, difference | 180 × 112 | **New** |
| 4 | `power_curve` | Active OEDB V164/9500 curve and production interpolation | 180 × 92 | **New** |
| 5 | `annual_energy_uncertainty` | Annual net yield; sampling CI of the 11-year mean | 180 × 125 | Approved earlier |
| 6 | `energy_sensitivity` | Wind-speed scaling and loss scenarios | 180 × 85 | **New** |
| 7 | `avoided_co2` | Avoided grid CO₂ by accounting convention; life-cycle GHG | 180 × 79 | **New** |
| — | `contact_sheet` | All seven figures at true relative size (PNG 200 dpi, PDF) | 394 × 506 | QA only |

The two figures approved earlier keep the interim numbers in their caption files
(`saros_study_area` = "Figure 2", `annual_energy_uncertainty` = "Figure 1"). They
were not edited here; renumber them at manuscript integration to 1 and 5.

---

## 2. Original-to-revised mapping

Original numbering from `scripts/10_build_docx.py` (`figures_final/`) and the
manuscript's provisional IDs.

| Original | Content | Revised | Note |
|---|---|---|---|
| Fig. 1 (F1) | Study area, regional context | **Fig. 1** `saros_study_area` | Official polygon, ÖÇK, EMODnet; no regional inset (no local coastline data) |
| Fig. 2 (F2) | Workflow incl. Weibull AEP and Monte Carlo | **Fig. 2** `methodology` | Empirical hourly chain; Weibull, uncertainty and sensitivity as side branches; no Monte Carlo |
| Fig. 3 (F3) | Wind rose | not regenerated | Data unchanged (direction shares in `wind_resource.json`); candidate for supplementary material |
| Fig. 4a (F_wind_resource) | Distribution, Weibull fit, power curve | **Fig. 3** + **Fig. 4** | Split: distribution/fit and power curve are separate questions |
| Fig. 4b | Q–Q plot | **Fig. 3b** | Replaced by the empirical-minus-Weibull difference per bin |
| Fig. 4c, 4d | Monthly climatology; interannual wind speed | not regenerated | Monthly means in `wind_resource.json`; interannual variation now shown in energy terms in Fig. 5 |
| Fig. 5 (F_monte_carlo) | Monte Carlo distributions, P10–P90, S1–S4 | **Fig. 5** + **Fig. 6** | Monte Carlo retired; sampling CI, observed variability and sensitivity are separate |
| Fig. 6 (F7) | Fossil pathway vs wind, 2.62 TWh, "69×" | **Fig. 7** `avoided_co2` | Accounting conventions side by side; life cycle separate and not subtracted; the fuel-resolved 69× comparison is not carried forward |
| Fig. 7 (F8) | Households and cars equivalents, incl. S4 | retired | Equivalents rest on unverified external values (Phase 4B §7.3); S4 retired |

S1–S3 capacity scenarios are E × MW scalings of the per-MW values and add no
information to Figs. 6–7; they belong in Table 4 (`scenarios.json`). S4 appears in
no figure.

---

## 3. Source files

| Fig. | Generator | Inputs |
|---|---|---|
| 1 | `scripts/phase4c_fig_saros_study_area.py` | `docs/review/phase1_data/SAROS_DURES_official.kml`, `emodnet_dtm2024_saros_crop.tif`; ÖÇK annex in `scripts/phase4a_site_checks.py`; `results/revised/site_screening.json` |
| 2 | `scripts/phase4c_fig_methodology.py` | design inputs only: `wind_resource.json` (node, period, hub height), `energy_yield.json` (estimator, curve id), `wind_speed_sensitivity.json` (factors), `emissions.json` (primary factor id), `site_screening.json` (node), `config/turbine.py` |
| 3 | `scripts/phase4c_fig_wind_weibull.py` | `data/processed/wind_hub_105m.parquet` (U_hub); `weibull_crosscheck.json`; `wind_resource.json`; `energy_yield.json`; `config/turbine.py` |
| 4 | `scripts/phase4c_fig_power_curve.py` | `config/turbine.py` (active and retired curves); `power_from_speed()` from `scripts/04_fit_weibull_aep.py`; `energy_yield.json` (curve id check) |
| 5 | `scripts/phase4c_fig_annual_energy_uncertainty.py` | `annual_energy.csv`; `energy_yield.json`; `interannual_and_sampling.json`; `wind_resource.json` |
| 6 | `scripts/phase4c_fig_energy_sensitivity.py` | `energy_yield.json`; `wind_speed_sensitivity.json`; `loss_scenarios.json` |
| 7 | `scripts/phase4c_fig_avoided_co2.py` | `emissions.json`; `energy_yield.json` |
| sheet | `scripts/phase4c_contact_sheet.py` | the seven PNGs |

Shared style: `config/figure_style.py`. Tests: `tests/test_phase4c_figure.py`,
`tests/test_phase4c_study_area.py`, `tests/test_phase4c_final_figures.py`.

---

## 4. Data provenance

* **No typed numbers.** Every plotted value is read from the files above. Each
  generator cross-checks its files before drawing and stops on disagreement, for
  example: baseline sensitivity case = central estimate; stored % changes =
  recomputed from the yields; avoided CO₂ = energy × factor for each convention;
  Weibull `gross_cf_empirical` = `energy_yield.json`; curve id in the results =
  active curve.
* **Hourly series (Fig. 3).** All 96 432 hours of `U_hub` are binned (0.5 m s⁻¹,
  0–26 m s⁻¹); the script stops if any value is missing or out of range. Nothing
  is filled or interpolated. k and c are the committed MLE values; the test
  refits them with `fit_weibull()` and reproduces them to 10⁻⁶.
* **Power curve (Fig. 4).** The drawn line is `power_from_speed()` itself,
  evaluated on a dense grid, so the figure shows the production interpolation,
  including zero below cut-in and from cut-out. The OEDB table has 49 points
  (0–24.5 m s⁻¹; there is no 14.5 m s⁻¹ row). The three closing points are
  drawn as open markers and labelled as not OEDB data.
* **Archived results are not read.** No generator references `results/archive/`,
  `results/provisional/` or Monte Carlo output (tested).
* **Headline checks.** Net yield 2.4274 GWh MW⁻¹ yr⁻¹; primary avoided CO₂
  1 515.2 tCO₂ MW⁻¹ yr⁻¹; curve `OEDB_V164_9500`; estimator "empirical hourly
  power conversion (primary)" (tested).

---

## 5. Captions

Captions are generated with the figures (`figures/revised/<stem>_caption.md`) and
reproduced here. Numbers follow the proposed order; see §1 for the two interim
captions.

### Figure 1 — `saros_study_area` (caption file still reads "Figure 2")

**Figure 2.** Saros offshore-wind candidate zone and the environmental and bathymetric context used for screening (WGS 84 / UTM zone 35N (EPSG:32635)). The black outline is the official candidate-zone polygon published by the Ministry of Energy and Natural Resources in the candidate-YEKA notice of 13 May 2026 (file 'SAROS DÜRES'). It is a candidate area, not an approved project; no turbine layout, cable route or installation footprint is implied. The zone covers 172.6 km²; its geometric centroid (open circle) lies at 40.557° N, 26.198° E. The energy model uses the ERA5 reanalysis grid node at 40.50° N, 26.25° E (black square), which lies outside the zone, 3.7 km from its nearest boundary (dotted line). The dashed vermillion line is the boundary of the Saros Körfezi Special Environmental Protection Area (ÖÇK), reconstructed from the coordinates in the annex to Council of Ministers Decision 2010/1089 (Official Gazette 27793, 22 December 2010); the narrow tint marks its protected side. The annex does not state a geodetic datum; the coordinates were read as WGS 84, so the overlay is an approximate GIS reconstruction, not a legally certified boundary. The ÖÇK continues east and south beyond the map edge, which is not part of its boundary. The hatched eastern arm of the zone, about 24.7 km² (14.4%) in the raster screening (25.0 km², 14.5%, by exact polygon intersection), lies inside the ÖÇK. ÖÇK status means that activities require permission from the environment ministry; it is not an automatic prohibition of construction. Shading shows water depth below lowest astronomical tide (depth = −elevation) from the EMODnet Digital Bathymetry DTM 2024 (1/16 arc-minute grid). The colour scale is piecewise linear: 0–60 m, the depth range of the zone, spans 60% of the colour ramp and 60–700 m the remaining 40% (break marked on the colour bar), so shelf depths are resolved without losing the deep basin. Depth inside the zone ranges from 1 to 62 m (median 28 m). The 10 m and 50 m isobaths mark the depth screening classes used in the site checks (shallower than 10 m; 50 m and deeper); they are screening thresholds, not legal or technical exclusion zones. Land is shown where the DTM elevation is 0 m or higher; islets and enclosed water bodies smaller than about 0.1 km² are omitted for legibility. The map extent is that of the bathymetry grid: the land in the south-eastern corner belongs to the southern shore of the gulf (Gelibolu Peninsula), most of which lies south of the grid. The arrow points to true north; the scale bar is exact to within 0.1% across the map.

### Figure 2 — `methodology`

**Figure 2.** Workflow of the energy and avoided-emission model. Solid boxes and arrows form the primary estimation chain: hourly ERA5 reanalysis wind at the grid node 40.50° N, 26.25° E (2014–2024) is extrapolated from 100 m to the 105 m hub height with a power-law shear exponent derived from the ERA5 10 m and 100 m levels; every hourly speed is converted to electrical power with the active OEDB V164/9500 power curve; the resulting empirical capacity factor is reduced by nominal wake, availability and electrical losses and expressed as net energy yield per installed megawatt for an average year of 8 766 h; avoided operational grid CO₂ follows from the 2023 combined-margin emission factor, with life-cycle greenhouse-gas emissions reported separately in CO₂-equivalent. Dashed boxes are supporting analyses that do not produce the primary estimate: a Weibull fit to the hourly speeds, used as a descriptive statistic and as a cross-check of the capacity factor (compared with, not used as an input to, the empirical energy); the observed interannual variability of the annual yields and the sampling confidence interval of the 11-year mean; and sensitivity experiments that rerun the chain with all hourly speeds scaled by 0.90–1.10 or with alternative loss assumptions. No step uses Monte Carlo sampling.

### Figure 3 — `wind_weibull`

**Figure 3.** Distribution of hourly hub-height wind speed at the ERA5 grid node used for the Gulf of Saros site, 2014–2024. (a) Probability-density histogram of all 96,432 hourly speeds at 105 m (0.5 m s⁻¹ bins; bar areas sum to one) and the two-parameter Weibull density fitted by maximum likelihood with the location fixed at zero (k = 2.035, c = 8.080 m s⁻¹). Every hour of the committed series is used; no values are filled or interpolated. Dotted lines mark the cut-in (3.5 m s⁻¹), rated (14 m s⁻¹) and cut-out (25 m s⁻¹) speeds of the reference turbine. (b) Empirical density minus the Weibull probability of the same bin divided by the bin width. The fit reproduces the mean speed (7.17 versus 7.16 m s⁻¹) and the cumulative distribution closely (R² = 0.998; Kolmogorov–Smirnov D = 0.022; because hourly speeds are autocorrelated, no p-value is interpreted). Close agreement in distribution does not establish agreement in energy: the deviations in (b) fall partly in the steep part of the power curve, and the Weibull-integrated gross capacity factor (32.06%) differs by −1.8% from the direct hourly conversion (32.66%). The Weibull fit is therefore reported as a descriptive summary and cross-check only; the energy estimates in this study convert each hourly speed through the power curve. ERA5 is reanalysis model output, not measured wind.

### Figure 4 — `power_curve`

**Figure 4.** Power curve of the Vestas V164-9.5 MW reference turbine used in this study. Filled markers are the 49 points (0–24.5 m s⁻¹) of the 'V164/9500' entry of the Open Energy Database turbine library, a third-party digitisation of the power-curve graph published by the manufacturer; it is not a manufacturer-certified table, and its air density is not documented (1.225 kg m⁻³ assumed). The solid line is the interpolation applied to every hourly wind speed in the energy model: linear between points, zero below the 3.5 m s⁻¹ cut-in (where the curve starts at 115 kW) and zero at and above the 25 m s⁻¹ cut-out. Rated power (9.5 MW) is first reached at 14 m s⁻¹. The OEDB table ends at 24.5 m s⁻¹; the open markers hold the rated plateau to the stated cut-out speed and close the curve, and are model assumptions rather than OEDB data. No cut-out hysteresis or high-wind ride-through is modelled. The dashed grey line is the curve used in the original analysis, whose source is undocumented; it reaches rated power at 13 m s⁻¹ and lies above the active curve between cut-in and rated speed. It is shown for comparison only and is superseded: no result in this study uses it.

### Figure 5 — `annual_energy_uncertainty` (caption file still reads "Figure 1")

**Figure 1.** Model-derived net annual energy yield per installed megawatt at the Gulf of Saros site, 2014–2024. (a) Net energy yield of each calendar year, obtained by converting hourly ERA5 reanalysis wind speeds at 105 m hub height with the Vestas V164-9.5 MW power curve (OEDB turbine-library curve V164/9500), applying a nominal net loss factor of 0.84778 and normalising every year to 8766 h. Each marker is a single-year point estimate; no uncertainty interval is shown for individual years. The dashed line marks the 11-year mean (2.427 GWh MW⁻¹ yr⁻¹). The lowest year, 2014 (1.992 GWh MW⁻¹ yr⁻¹), lies 17.9% below the mean; the highest, 2020, reaches 2.648 GWh MW⁻¹ yr⁻¹. (b) Central estimate and 90% confidence interval of the 11-year mean (2.334–2.520 GWh MW⁻¹ yr⁻¹; Student's t-interval, n = 11 years) on the same scale as (a). The interval expresses only the sampling uncertainty that arises from the finite number of years and treats the ERA5 wind speeds as correct; it is not a P90 value and excludes wind-resource bias, power-curve, loss and project-design uncertainty. All values are model estimates, not observed turbine production.

### Figure 6 — `energy_sensitivity`

**Figure 6.** Sensitivity of the model-derived net energy yield at the Gulf of Saros site to two separate sets of assumptions, shown as the change relative to the central estimate (2.427 GWh MW⁻¹ yr⁻¹; values in parentheses in GWh MW⁻¹ yr⁻¹). (a) Wind-speed scaling: every hourly ERA5 hub-height speed is multiplied by a constant factor (0.90, 0.95, 1.05, 1.10) while the power curve and the nominal losses stay fixed. The yield changes by about twice the speed change, and not symmetrically (−20.4% for a 10% reduction, +19.7% for a 10% increase), because most operating hours fall on the steep part of the power curve. These are sensitivity experiments, not bias corrections or forecasts. (b) Alternative loss assumptions: the low- and high-loss scenarios change the wake, availability and electrical losses applied to the same gross energy (+6.5% and −8.3%; nominal: wake 8%, availability 95%, electrical 3%). The loss values are labelled assumptions without site-specific evidence, and one wake value is applied to every deployment scenario. Each bar is a single deterministic model run. The two experiments are kept apart and are not combined; neither set of cases is a probability distribution, a confidence interval or a P50/P90 estimate.

### Figure 7 — `avoided_co2`

**Figure 7.** Avoided operational grid CO₂ and life-cycle greenhouse-gas emissions per installed megawatt for the Gulf of Saros estimate. (a) Net energy yield (2,427.4 MWh MW⁻¹ yr⁻¹) multiplied by each 2023 grid emission factor published by the Ministry of Energy and Natural Resources. The primary convention is the combined margin for wind and solar generation (UNFCCC CDM Tool 07; 1,515.2 t CO₂ MW⁻¹ yr⁻¹). The operating margin (1,732), build margin (866) and generation average (1,044 t CO₂ MW⁻¹ yr⁻¹) are alternative accounting conventions that answer different questions about which generation is displaced; they are shown for context and are not uncertainty bounds of the primary value. All four are CO₂-only factors for a static 2023 grid, not forecasts of future displacement. The 90% confidence interval of the primary value that follows from the sampling uncertainty of the 11-year energy mean alone is 1,457–1,573 t CO₂ MW⁻¹ yr⁻¹; it excludes factor, wind-resource and loss uncertainty. The generation average in CO₂-equivalent (1,053 t CO₂-eq MW⁻¹ yr⁻¹) is a different unit and is not plotted. (b) Offshore-wind life-cycle greenhouse-gas emissions in CO₂-equivalent for the same energy, using the IPCC AR5 median intensity (12 g CO₂-eq kWh⁻¹; 29.1 t CO₂-eq MW⁻¹ yr⁻¹). The line spans the minimum and maximum of the literature values compiled in AR5 (8–35 g CO₂-eq kWh⁻¹; 19.4–85.0 t CO₂-eq MW⁻¹ yr⁻¹), a range of published studies rather than a statistical interval. These are literature values for other sites, not a Saros-specific life-cycle assessment. Life-cycle emissions are reported separately and are not subtracted from (a), because they cover other gases and a cradle-to-grave boundary, whereas the grid factors cover combustion CO₂ only. Both panels share one numerical scale so that magnitudes can be compared; the units differ.

---

## 6. Regeneration

From the repository root, with `requirements.txt` installed (no network access
needed):

```bash
python scripts/run_revised_pipeline.py                 # only if results/revised must be rebuilt
python scripts/phase4c_fig_saros_study_area.py
python scripts/phase4c_fig_methodology.py
python scripts/phase4c_fig_wind_weibull.py
python scripts/phase4c_fig_power_curve.py
python scripts/phase4c_fig_annual_energy_uncertainty.py
python scripts/phase4c_fig_energy_sensitivity.py
python scripts/phase4c_fig_avoided_co2.py
python scripts/phase4c_contact_sheet.py                # after all seven figures
python -m pytest -q tests/                             # 145 passed
```

Each generator runs its layout checks before saving and refuses to write a figure
with overlapping, clipped or undersized text or strokes. Outputs carry no
timestamps; reruns reproduce identical bytes, and the tests compare fresh outputs
with the committed files.

---

## 7. Visual QA findings and limitations

**Checks run on every new figure**

* Automated: no text overlaps or page clipping; minimum 7 pt text and 0.5 pt
  strokes; three font sizes only; DejaVu Sans embedded as TrueType in the PDF;
  SVG text kept as text; exact 180 mm width; fully vector PDF/SVG (no embedded
  images). In the methodology diagram, all box text fits inside its box with a
  1 mm margin.
* Visual: each exported PDF was rendered and inspected, and the contact sheet was
  inspected for consistency. Defects found and fixed during the work:
  * Fig. 3: a clipped two-line axis label and hyphen-minus signs.
  * Fig. 4: the legend over the curve; rated-power and cut-in labels touching; a
    retired-curve vertical at cut-out that read as part of the active curve.
  * Fig. 6: value labels clipped at ±20%; detail text running off the page.
  * Fig. 7: a note overlapping a value.
  * Fig. 2: box text overflowing.
* Consistency (contact sheet): same typography, colour roles (blue = primary
  data, vermillion = emphasis or fitted model, bluish green = second experiment
  or life cycle, grey = context), panel headings, grids and tick styling across
  all seven figures.

**Unresolved limitations**

1. **Interim caption numbers.** The two approved figures still say "Figure 2" and
   "Figure 1" (§1); renumber them at integration.
2. **Not regenerated.** The wind rose (old Fig. 3) and the monthly climatology
   (old Fig. 4c) are not part of this set. If the manuscript keeps them, they need
   revised generators.
3. **Manuscript references.** The manuscript text still cites the old IDs
   (F_wind_resource, F_monte_carlo, F7, F8). Mapping them is integration work and
   was not started.
4. **Margins.** Fig. 5 (approved) uses a 13 mm left margin; the new figures use
   17–52 mm to fit their row labels. Panel headings all start at 2 mm, so the
   headings align on a page, but plot areas do not.
5. **Raster layer.** Fig. 1 embeds its bathymetry as an image layer (300 ppi). All
   other figures are fully vector.
6. **Font.** DejaVu Sans is used throughout for reproducibility. If the journal
   requires Arial or Helvetica, change it once in `config/figure_style.py`.
7. **Scientific limitations.** These are unchanged and stated in the captions:
   * a single ERA5 node (reanalysis, not measurement);
   * a digitised, non-certified power curve with an undocumented air density;
   * assumed losses with one wake value for all densities;
   * static 2023 grid factors;
   * literature life-cycle intensities that are not Saros-specific.
8. **Omitted case.** The GWA-scaled case is not shown in Fig. 6, which shows only
   the ±5% and ±10% design. It remains in `wind_speed_sensitivity.json` for the
   text.
9. **Contact sheet.** It is a QA raster at 200 dpi (PNG and PDF), not a
   publication file.
