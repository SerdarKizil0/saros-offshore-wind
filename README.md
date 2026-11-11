# Saros Offshore Wind — Energy & Avoided-Emissions Assessment

Reproducible analysis pipeline for the **Gulf of Saros offshore-wind candidate
area** (candidate YEKA announced by Türkiye's Ministry of Energy and Natural
Resources on 13 May 2026; KML file "SAROS DÜRES"). Candidate status only: no
approved project.

The revised pipeline (Phase 4B) converts 11 years of hourly ERA5 reanalysis
(2014–2024) directly into energy with the Vestas V164-9.5 MW reference turbine
(OEDB digitised power curve), and reports avoided operational grid CO₂ with the
official 2023 combined-margin factor. Uncertainty is reported as separate,
labelled components (sampling CI of the 11-year mean, observed interannual
variability, loss scenarios, wind-speed sensitivities). No Monte Carlo is used
for the headline values.

> **Pre-submission model estimates** (`results/revised/`, not validated project
> forecasts): net capacity factor 27.7 %, net yield 2.43 GWh MW⁻¹ yr⁻¹ (90 %
> sampling CI of the 11-year mean 2.33–2.52), avoided operational CO₂
> 1 515 tCO₂ MW⁻¹ yr⁻¹. For the illustrative ~1 GW scenario (S3, conditional on
> allocation to Saros): 2.42 TWh yr⁻¹ and 1.51 Mt CO₂ yr⁻¹. A ±10 % change in
> wind speed changes energy by about ±20 % (sensitivity, not a probability).

---

## Pipeline

```bash
python scripts/run_revised_pipeline.py   # 04 -> 06 -> 07, writes results/revised/ + MANIFEST.json
python -m pytest -q tests/
```

| Script | Purpose | Status |
|---|---|---|
| `01_test_cds_setup.py` | Verify Copernicus CDS API credentials | active (only to regenerate the Parquet) |
| `02_download_era5_saros.py` | Download 2014–2024 hourly ERA5 winds | active (only to regenerate the Parquet) |
| `03_process_era5.py` | Extract node, compute speeds, extrapolate to 105 m | active (only to regenerate the Parquet) |
| `04_fit_weibull_aep.py` | Wind resource, empirical AEP, Weibull cross-check, sampling CI, losses, sensitivities | **revised** |
| `05_generate_wind_figures.py` | Wind-resource figure (not re-run; figures pending redesign) | unchanged |
| `06_emissions_and_scenarios.py` | Avoided operational CO₂, life-cycle GHG, scenarios S1–S3 | **new** |
| `07_site_screening.py` | Bathymetry, protected-area overlap, packing, screening classes | **new** |
| `10_build_docx.py` | Assemble the manuscript .docx | unchanged |
| `legacy/` | Retired Weibull Monte Carlo, grid comparison, old figure scripts | archived (guarded) |
| `phase*_*.py` | Review analyses (Phases 2A–4A), provisional outputs | review record |

## Repository layout

```
config/        single source of truth (site, turbine, emission factors)
scripts/       pipeline (01–07, run_revised_pipeline.py), legacy/, phase review scripts
data/          inputs/intermediates (large files gitignored)
results/       revised/ (authoritative), provisional/ (review phases), archive/ (historical)
figures/       publication + interactive figures
manuscript/    paper sections (markdown), tables, verified references
docs/          setup notes, decision log, review reports (docs/review/)
```

## Quick start

```bash
git clone https://github.com/SerdarKizil0/saros-offshore-wind.git
cd saros-offshore-wind
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# The hourly series is committed, so no download is needed:
python scripts/run_revised_pipeline.py
python -m pytest -q tests/
```

To regenerate the hourly series from ERA5 (optional; needs a CDS account, see
`docs/CDS_API_SETUP.md` and `data/README.md`): run scripts 01–03.

## Data availability

The raw ERA5 NetCDF files are **not** committed — they are freely
re-downloadable from the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/)
via `02_download_era5_saros.py`. The processed hourly series
(`data/processed/wind_hub_105m.parquet`, SHA-256 in
`data/processed/wind_hub_105m.parquet.sha256`) and all analysis outputs in
`results/` are included so the figures and tables can be reproduced without
re-downloading. Source, licence, columns and reproduction steps:
`data/README.md`.

## Key methodological choices

- **ERA5 2014–2024**, nearest 0.25° node (40.50° N, 26.25° E). The node lies
  3.7 km outside the polygon; reanalysis output, not measurements.
- **Empirical hourly power conversion** is the energy estimator; Weibull is
  descriptive only (−1.85 % AEP cross-check difference).
- **Shear exponent** α = 0.149 derived from the ERA5 10 m / 100 m levels
  (not measured); its effect on the 100→105 m step is +0.24 %.
- **Uncertainty kept separate:** sampling CI of the 11-year mean (t-interval);
  observed interannual variability (energy CoV 7.0 %, 2014 −18 %); loss
  scenarios; wind-speed sensitivities (±5/±10 %; GWA 4.0 is ~10 % higher,
  reported as inter-model disagreement).
- **Primary emissions metric:** avoided operational grid CO₂ with the official
  2023 wind/solar combined margin, 0.6242 tCO₂/MWh (CO₂ only). Life-cycle GHG
  is reported separately in tCO₂-eq; other grid conventions are labelled context.
- **Scenarios:** per-MW results are primary; S1–S3 are illustrative; S4 is
  retired. About 25 km² (14 %) of the zone overlaps the Saros Special
  Environmental Protection Area (2010).

See `docs/review/` (Phases 1–4B) for the evidence; `docs/DECISION_LOG.md` is a
historical record.

## Citation

If you use this code or its results, please cite the associated manuscript
(under review). A `CITATION.cff` will be added on acceptance.

## License

Code released under the MIT License (see `LICENSE`). ERA5 data: contains modified
Copernicus Climate Change Service information [2026], distributed under
CC BY 4.0 (see `data/README.md`).
