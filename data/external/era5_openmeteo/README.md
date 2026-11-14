# Primary wind input — ERA5 1994–2024 via Open-Meteo (since Phase 5-PRE-B)

This is the **primary production wind input** of the revised pipeline
(author decision, 14 November 2026). It is pinned by SHA-256 in
`config/wind_data.py`; `scripts/04_fit_weibull_aep.py` refuses any file whose
checksum differs.

| File | Content |
|---|---|
| `era5_openmeteo_40.50N_26.25E_1994_2024.parquet` | Hourly ERA5 at 40.50° N 26.25° E, 1994-01-01 00:00 to 2024-12-31 23:00 UTC (271 752 rows) |
| `MANIFEST.json` | Request URLs, per-response SHA-256, returned grid point, retrieval time, file SHA-256 |

## Columns

| Column | Type | Meaning |
|---|---|---|
| `U10` | int16, centi-m/s | 10 m wind speed. Divide by 100; the API returns two decimals, so storage is lossless |
| `U100` | int16, centi-m/s | 100 m wind speed |
| `wdir100` | int16, degrees | 100 m direction the wind blows *from*. The API returns whole degrees; 360 ≡ 0 |

- There is no timestamp column. Row *i* is 1994-01-01 00:00 UTC + *i*
  hours.
- `scripts/02b` verifies that the time axis is complete and regular before
  dropping it. `scripts/04` re-checks the row count against the period.

## Processing in the pipeline (`scripts/04`, `load_series`)

1. `U_hub = U100 × (105/100)^α`. α = 0.149139 is the trimmed-mean hourly
   10/100 m exponent of this series (`scripts/03` `estimate_shear_alpha`,
   unchanged method).
2. Empirical hourly conversion with the OEDB V164/9500 curve and nominal
   losses (unchanged).

## Source and its limits

- **Source:** Open-Meteo historical-weather API, `models=era5`,
  `cell_selection=nearest`, `wind_speed_unit=ms`, `timezone=GMT`. Two
  requests: 1994–2008 and 2009–2024.
- **Not bit-identical to the CDS:** Open-Meteo redistributes ECMWF ERA5 on
  the native 0.25° grid with lossy internal storage.
- **Calibration against the CDS-derived series** (2014–2024, same node,
  96 432 hours), re-computed on every pipeline run
  (`results/revised/input_provenance.json`):
  - U100 mean difference −0.00009 m/s; r = 0.99994;
  - pooled gross CF −0.004 % (same α);
  - direction mean absolute difference 0.42°, from whole-degree rounding;
    the largest 16-sector share difference is 0.56 percentage points.
- **Stability:** the speeds are bit-identical to the independent Phase 5-PRE
  download of the same node and years
  (`data/external/phase5pre/`).

## Re-fetching

```bash
python scripts/02b_fetch_era5_openmeteo.py
```

If Open-Meteo has reprocessed its archive, the new file will have a
different checksum. The script then prints a note instead of changing the
pin, and the pipeline keeps refusing the file until the pin is reviewed and
updated deliberately.

## Licences and notices

- **ERA5:** contains modified Copernicus Climate Change Service information
  [2026]. Neither the European Commission nor ECMWF is responsible for any
  use of this information.
- **Open-Meteo:** CC BY 4.0. Cite Zippenfenig, P. (2023), *Open-Meteo.com
  Weather API*, doi:10.5281/zenodo.7970649.
