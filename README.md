# Saros Offshore Wind — Energy & Avoided-Emissions Assessment

Reproducible analysis pipeline for the **Gulf of Saros offshore wind candidate
zone** (one of the four DÜRES zones designated by Türkiye's Ministry of Energy
and Natural Resources on 14 May 2026).

The pipeline characterises the wind resource from 11 years of ERA5 reanalysis,
estimates annual energy production with a Vestas V164-9.5 MW reference turbine,
and quantifies avoided CO₂ emissions relative to the official Turkish grid
emission factor — all with 10,000-iteration Monte Carlo uncertainty propagation.

> **Headline result:** A ~1 GW deployment generates ≈2.62 TWh yr⁻¹ and avoids
> ≈1.52 Mt CO₂ yr⁻¹ (P10–P90: 1.27–1.75) — equivalent to ~0.76 million cars
> removed from the road, at a carbon burden ≈69× lower than the equivalent
> fossil-thermal generation.

---

## Pipeline

Scripts are numbered to run in order:

| Script | Purpose |
|---|---|
| `01_test_cds_setup.py` | Verify Copernicus CDS API credentials |
| `02_download_era5_saros.py` | Download 2014–2024 hourly ERA5 winds (monthly chunks) |
| `03_process_era5.py` | Concatenate, extrapolate to 105 m hub, measure shear |
| `04_fit_weibull_aep.py` | Weibull fit + AEP (power-curve convolution) |
| `05_generate_wind_figures.py` | Wind-resource figures (static + interactive) |
| `06_run_monte_carlo.py` | 10,000-iteration uncertainty quantification |
| `07_compare_with_grid.py` | Avoided emissions + national context |
| `08_generate_mc_figures.py` | Monte Carlo & scenario figures |
| `09_generate_extra_figures.py` | Workflow, wind rose, comparison, equivalents |
| `10_build_docx.py` | Assemble the manuscript .docx |

## Repository layout

```
config/        single source of truth (site, turbine, emission factors)
scripts/       numbered analysis pipeline (01–10)
data/          inputs/intermediates (large files gitignored)
results/       JSON/NPZ analysis outputs
figures/       publication + interactive figures
manuscript/    paper sections (markdown), tables, verified references
docs/          setup notes and decision log
```

## Quick start

```bash
git clone https://github.com/<your-username>/saros-offshore-wind.git
cd saros-offshore-wind

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure CDS API (see docs/CDS_API_SETUP.md), then:
python scripts/01_test_cds_setup.py
python scripts/02_download_era5_saros.py   # 30 min – a few hours
python scripts/03_process_era5.py
python scripts/04_fit_weibull_aep.py
python scripts/06_run_monte_carlo.py
python scripts/07_compare_with_grid.py
```

## Data availability

The raw ERA5 NetCDF files (~80 MB) are **not** committed — they are freely
re-downloadable from the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/)
via `02_download_era5_saros.py`. The processed hourly series
(`data/processed/wind_hub_105m.parquet`) and all analysis outputs in
`results/` are included so the figures and tables can be reproduced without
re-downloading.

## Key methodological choices

- **11-year window (2014–2024)** to capture inter-annual variability (CoV 3.2%).
- **Measured shear exponent** (α = 0.149) instead of the assumed open-sea 0.10.
- **Per-MW reporting** (capacity-normalised), robust to the unfinalised
  installed capacity; four scenarios (S1–S4) provided for context.
- **Official combined-margin grid factor** (624.2 gCO₂-eq kWh⁻¹, ETKB/EVÇED
  2023) as the primary avoided-emission basis.

See `docs/DECISION_LOG.md` for the full rationale behind each choice.

## Citation

If you use this code or its results, please cite the associated manuscript
(under review). A `CITATION.cff` will be added on acceptance.

## License

Code released under the MIT License (see `LICENSE`). ERA5 data © ECMWF/Copernicus,
used under the Copernicus licence.
