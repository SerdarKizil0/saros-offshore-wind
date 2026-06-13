# Data

- `processed/wind_hub_105m.parquet` — 96,432 hourly hub-height (105 m) wind
  speed & direction records (2014–2024). Committed so results are reproducible
  without re-downloading.
- `era5/` (gitignored) — raw ERA5 NetCDF, regenerable via
  `scripts/02_download_era5_saros.py`.
