# Data

| Path | In Git | Content |
|---|---|---|
| `processed/wind_hub_105m.parquet` | **yes** | Hourly 10 m, 100 m and 105 m wind speed and 100 m direction at the ERA5 grid cell nearest the Saros zone centroid, 2014–2024 |
| `processed/wind_hub_105m.parquet.sha256` | yes | Checksum of the file above |
| `processed/wind_processing_summary.json` | no | Diagnostics written by `scripts/03`; regenerable |
| `era5/era5_saros_YYYY_MM.nc` | no | Raw ERA5 NetCDF downloads (gitignored); regenerable with `scripts/02` |

## `processed/wind_hub_105m.parquet`

### Integrity

- SHA-256: `0cfc4742010acbc8cbdac4090527589393ab8b2858aaaa5d92cfc9fbfc1916a5`
- Size: 3 213 759 bytes
- Format: Parquet, single row group, written by `parquet-cpp-arrow` 24.0.0
  through pandas 3.0.2
- Verify with:

  ```bash
  cd data/processed && sha256sum -c wind_hub_105m.parquet.sha256
  ```

### Source and attribution

- **Dataset:** ERA5 hourly data on single levels from 1940 to present
  (`reanalysis-era5-single-levels`, product type `reanalysis`), retrieved
  from the Copernicus Climate Data Store (CDS).
- **Citation:** Hersbach, H., Bell, B., Berrisford, P., et al. (2023). ERA5
  hourly data on single levels from 1940 to present. Copernicus Climate
  Change Service (C3S) Climate Data Store (CDS).
  doi:10.24381/cds.adbb2d47. For the method reference, see Hersbach et al.
  (2020), *Q. J. R. Meteorol. Soc.* 146, 1999–2049, doi:10.1002/qj.3803.
- **Variables requested:** `10m_u_component_of_wind`,
  `10m_v_component_of_wind`, `100m_u_component_of_wind`,
  `100m_v_component_of_wind`.
- **Retrieval:** all 24 hours of every month, 2014–2024. The request box
  (N, W, S, E) is 40.6486, 25.9885, 40.454, 26.5109, i.e. the polygon
  bounds plus 0.05°, taken from `config/site.py`.
- **Retrieval date:** not recorded in the file. The writer versions point to
  2026, so the 2024 data are the final ERA5 release, not preliminary ERA5T
  (this is an inference).
- **Licence:** CDS datasets, ERA5 included, are distributed under
  **Creative Commons Attribution 4.0 (CC BY 4.0)** since 2 July 2025,
  replacing the earlier Licence to use Copernicus Products. Redistributing
  and adapting the data, including derived products such as this file, is
  permitted with attribution and a notice of modification. The earlier
  licence also allowed redistribution of derived products with attribution.
- **Required notice:** Contains modified Copernicus Climate Change Service
  information [2026]. Neither the European Commission nor ECMWF is
  responsible for any use that may be made of the Copernicus information or
  data it contains.
- **Modifications:**
  - one grid cell extracted;
  - vector magnitudes and direction computed from the u and v components;
  - 100 m speed extrapolated to 105 m;
  - values stored as float32.

### Columns, units and time

| Column | Unit | Definition |
|---|---|---|
| `time` (index) | — | `datetime64[ns]`, timezone-naive, **UTC** (the ERA5 `valid_time`). 96 432 hourly stamps, 2014‑01‑01 00:00 to 2024‑12‑31 23:00, complete, no gaps, no NaN |
| `U10` | m s⁻¹ | √(u10² + v10²), instantaneous at the timestamp |
| `U100` | m s⁻¹ | √(u100² + v100²) |
| `U_hub` | m s⁻¹ | `U100` × (105/100)^α, with α = 0.1492303 (see processing) |
| `wdir` | degrees | Meteorological direction (the direction the wind blows *from*, clockwise from north), computed from the 100 m components: `atan2(-u, -v) mod 360` |

All columns are float32. Each value comes from the ERA5 grid cell nearest
the polygon centroid (40.5571° N, 26.1978° E), selected with
`method="nearest"` in `scripts/03`. The value represents a ~0.25° cell, not
a point measurement.

### Processing pipeline

1. **`scripts/02_download_era5_saros.py`** downloads monthly NetCDF files
   (`era5_saros_YYYY_MM.nc`) through `cdsapi`.
2. **`scripts/03_process_era5.py`**:
   - concatenates the files and selects the cell nearest the centroid;
   - computes `U10`, `U100` and `wdir`;
   - estimates the shear exponent hour by hour as
     α = ln(U100/U10) / ln(10), using hours with both speeds above
     1 m s⁻¹ (93 434 h), trimmed to the 1st–99th percentile; the mean of
     the trimmed values is used;
   - computes `U_hub` and writes this file.

Checks recomputed from this file on 11.11.2026:

- α mean, median and standard deviation: 0.14923 / 0.14166 / 0.05393;
- `U_hub / U100` is constant at 1.0073074, i.e. 1.05^α;
- inter-annual coefficient of variation of `U_hub`: 3.20%;
- mean `U_hub`: 7.171635 m s⁻¹;
- gross AEP with the archived original power curve:
  30.411791370569144 GWh yr⁻¹. This and the mean match
  `results/archive/baseline_original_curve/` bit-for-bit.

### Reproducing the file

```bash
pip install -r requirements.txt   # includes cdsapi and xarray
python scripts/01_test_cds_setup.py
python scripts/02_download_era5_saros.py
python scripts/03_process_era5.py
```

- `scripts/01` checks your CDS credentials. You need a CDS account and
  `~/.cdsapirc`, and you must accept the CC BY 4.0 licence on the dataset
  page. See `docs/CDS_API_SETUP.md`.
- `scripts/02` downloads 132 monthly files into `data/era5/`.
- `scripts/03` writes `data/processed/wind_hub_105m.parquet`.

A fresh download may not be byte-identical, for three reasons:

- ECMWF can revise ERA5 data;
- library versions change the Parquet encoding;
- the Weibull MLE in later scripts differs at about 10⁻⁸ relative between
  scipy versions.

Compare a fresh file's values with the committed one, not its checksum.
Running `scripts/03` overwrites the committed file; restore it with:

```bash
git checkout -- data/processed/wind_hub_105m.parquet
```
