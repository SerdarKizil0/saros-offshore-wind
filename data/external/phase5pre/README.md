# Phase 5-PRE inputs — ERA5 at three 0.25° nodes, 1979–2024

Written by `scripts/phase5pre_fetch_inputs.py` (network, run once on
14 November 2026). Request URLs, per-response SHA-256, the grid point each
request returned and the SHA-256 of every file are in `MANIFEST.json`.
Used only by `scripts/phase5pre_era5_robustness.py`. The production pipeline
and `results/revised/` do not read these files.

| File | Content |
|---|---|
| `era5_openmeteo_40.50N_26.00E_1979_2024.parquet` | Hourly ERA5 `U10`, `U100` (wind speed, m/s) at 40.50° N 26.00° E |
| `era5_openmeteo_40.50N_26.25E_1979_2024.parquet` | Same, 40.50° N 26.25° E (the baseline node of `data/processed/wind_hub_105m.parquet`) |
| `era5_openmeteo_40.50N_26.50E_1979_2024.parquet` | Same, 40.50° N 26.50° E |
| `era5_land_sea_mask_saros.json` | ERA5 static land–sea mask (fraction 0–1), 0.25° grid, 25.50–27.00° E × 40.00–41.00° N |
| `MANIFEST.json` | Provenance and checksums |

## Format

- Each Parquet file has two `int16` columns in centi-m/s; divide by 100.
  The API returns two decimals, so this storage is lossless.
- There is no timestamp column. Row *i* is 1979-01-01 00:00 UTC + *i* hours
  (403 248 rows, through 2024-12-31 23:00). The fetch script checks that the
  returned time axis is exactly this complete hourly range before it drops
  the column.
- Values are instantaneous ERA5 fields at the hour (UTC), as in the CDS
  baseline.

## Source

- **Wind:** Open-Meteo historical-weather API
  (`archive-api.open-meteo.com/v1/archive`), `models=era5`,
  `cell_selection=nearest`, `wind_speed_unit=ms`, `timezone=GMT`, two
  23-year requests per node. Every response reported exactly the requested
  grid point.
  - Open-Meteo redistributes ECMWF ERA5 on the native 0.25° grid. Its
    internal storage is lossy, so values are **not bit-identical** to a CDS
    download.
  - Calibration against the committed CDS-derived baseline (node 26.25° E,
    2014–2024, 96 432 matched hours):
    - mean U100 difference −0.00009 m/s; RMSE 0.041 m/s; r = 0.99994;
    - pooled gross capacity factor −0.004 %;
    - largest annual net-yield difference 0.018 %.

    Details in `results/provisional/phase5pre/calibration.json`.
- **Land–sea mask:** ARCO-ERA5 public Zarr store on Google Cloud
  (`gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`,
  variable `land_sea_mask`). One chunk was read anonymously over HTTPS; its
  SHA-256 is in the manifest.

## Why not the CDS

- No CDS credentials exist in the environment (no `~/.cdsapirc`).
- The raw CDS NetCDF files behind the 2014–2024 baseline are gitignored
  and absent (`data/README.md`). The committed parquet holds only the
  26.25° E node.
- The original request box (40.454–40.649° N, 25.989–26.511° E) spans
  exactly the 40.50° N row of 26.00/26.25/26.50° E. Whether the raw files
  actually contained all three nodes cannot be checked without them.

## CDS equivalent (to replace this source)

| Setting | Value |
|---|---|
| Dataset | `reanalysis-era5-single-levels`, `product_type` `reanalysis` |
| Variables | `10m_u_component_of_wind`, `10m_v_component_of_wind`, `100m_u_component_of_wind`, `100m_v_component_of_wind` |
| Time | years 1979–2024, all months and days, 00:00–23:00 |
| Area | `[40.55, 25.95, 40.45, 26.55]` (N, W, S, E) |

Use the monthly chunking of `scripts/02_download_era5_saros.py`. Then form
`U = sqrt(u² + v²)` per node and re-run
`scripts/phase5pre_era5_robustness.py` with those series.

## Licences and notices

- **ERA5:** contains modified Copernicus Climate Change Service information
  [2026]. Neither the European Commission nor ECMWF is responsible for any
  use of this information.
- **Open-Meteo:** data under CC BY 4.0. Cite Zippenfenig, P. (2023),
  *Open-Meteo.com Weather API*, doi:10.5281/zenodo.7970649.
- **ARCO-ERA5:** Google Cloud public dataset.
