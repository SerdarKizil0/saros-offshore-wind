"""
03 — ERA5 processing: 11-year wind speed time series at hub height
====================================================================
Reads the monthly NetCDFs from data/era5/ (era5_saros_YYYY_MM.nc),
concatenates them by time, extracts the grid cell nearest the polygon
centroid, computes wind speed at 10 m and 100 m, measures the log-law
shear exponent from the data, extrapolates to the 105 m hub height,
and writes a processed hourly series + a JSON diagnostics summary.

NO dask required: the full record (~96 000 hours × a few cells) fits
comfortably in memory, so files are opened eagerly and concatenated.

Output:
  data/processed/wind_hub_105m.parquet
  data/processed/wind_processing_summary.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import xarray as xr

from config.site import SITE, ERA5_DIR, DATA_DIR


PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_TIMESERIES = PROCESSED_DIR / "wind_hub_105m.parquet"
OUTPUT_SUMMARY    = PROCESSED_DIR / "wind_processing_summary.json"

H1_REF = 10.0     # m, ERA5 "10m" winds
H2_REF = 100.0    # m, ERA5 "100m" winds
H_HUB  = 105.0    # m, Vestas V164-9.5 MW hub height


def open_all_files() -> xr.Dataset:
    """Open every monthly NetCDF eagerly and concatenate by time.

    No dask: each file is tiny. We load, harmonize, concat in memory.
    """
    files = sorted(ERA5_DIR.glob("era5_saros_*.nc"))
    if not files:
        raise FileNotFoundError(
            f"No ERA5 files in {ERA5_DIR}. "
            f"Run scripts/02_download_era5_saros.py first."
        )
    print(f"Opening {len(files)} NetCDF files (eager, no dask) …")

    datasets = []
    for f in files:
        # engine defaults to netcdf4; no chunks => eager numpy-backed
        ds = xr.open_dataset(f)
        ds = harmonize_variable_names(ds)
        datasets.append(ds.load())   # force into memory, then close handle
        ds.close()

    # Determine the time dimension name
    time_dim = "valid_time" if "valid_time" in datasets[0].dims else "time"
    combined = xr.concat(datasets, dim=time_dim)
    combined = combined.sortby(time_dim)
    return combined


def harmonize_variable_names(ds: xr.Dataset) -> xr.Dataset:
    """ERA5 may use either u10/v10/u100/v100 or 10u/10v/100u/100v."""
    candidates = {
        "u10":  ["u10",  "10u"],
        "v10":  ["v10",  "10v"],
        "u100": ["u100", "100u"],
        "v100": ["v100", "100v"],
    }
    rename = {}
    for canonical, options in candidates.items():
        for name in options:
            if name in ds.data_vars and name != canonical:
                rename[name] = canonical
                break
    if rename:
        ds = ds.rename(rename)
    return ds


def select_centroid_cell(ds: xr.Dataset) -> xr.Dataset:
    sel = ds.sel(
        latitude=SITE.centroid_lat,
        longitude=SITE.centroid_lon,
        method="nearest",
    )
    print(f"Nearest ERA5 cell to centroid "
          f"({SITE.centroid_lat:.3f}N, {SITE.centroid_lon:.3f}E):")
    print(f"  cell: {float(sel.latitude):.3f}N, {float(sel.longitude):.3f}E")
    return sel


def compute_wind_speeds(ds: xr.Dataset) -> pd.DataFrame:
    for v in ("u10", "v10", "u100", "v100"):
        if v not in ds.data_vars:
            raise KeyError(f"Variable '{v}' missing after harmonization. "
                           f"Found: {list(ds.data_vars)}")
    u10, v10 = ds["u10"].values, ds["v10"].values
    u100, v100 = ds["u100"].values, ds["v100"].values

    speed10  = np.sqrt(u10**2  + v10**2)
    speed100 = np.sqrt(u100**2 + v100**2)
    direction100 = np.degrees(np.arctan2(-u100, -v100)) % 360

    time_dim = "valid_time" if "valid_time" in ds.coords else "time"
    time = pd.to_datetime(ds[time_dim].values)

    df = pd.DataFrame(
        {"U10": speed10, "U100": speed100, "wdir": direction100},
        index=time,
    )
    df.index.name = "time"
    df = df[~df.index.duplicated(keep="first")].sort_index()
    return df


def estimate_shear_alpha(df: pd.DataFrame) -> dict:
    mask = (df["U10"] > 1.0) & (df["U100"] > 1.0)
    u1 = df.loc[mask, "U10"].values
    u2 = df.loc[mask, "U100"].values
    alpha = np.log(u2 / u1) / np.log(H2_REF / H1_REF)
    lo, hi = np.percentile(alpha, [1, 99])
    trimmed = alpha[(alpha >= lo) & (alpha <= hi)]
    return {
        "alpha_mean":   float(np.mean(trimmed)),
        "alpha_median": float(np.median(trimmed)),
        "alpha_std":    float(np.std(trimmed)),
        "alpha_p5":     float(np.percentile(trimmed, 5)),
        "alpha_p95":    float(np.percentile(trimmed, 95)),
        "n_hours_used":  int(mask.sum()),
        "n_hours_total": int(len(df)),
        "literature_default": 0.10,
        "method": "hour-by-hour log-law ratio, 1-99 percentile trimmed",
    }


def extrapolate_to_hub(df: pd.DataFrame, alpha: float) -> pd.Series:
    return df["U100"] * (H_HUB / H2_REF) ** alpha


def summary_stats(s: pd.Series) -> dict:
    return {
        "mean": float(s.mean()), "std": float(s.std()),
        "min": float(s.min()),
        "p10": float(s.quantile(0.10)), "p50": float(s.quantile(0.50)),
        "p90": float(s.quantile(0.90)), "max": float(s.max()),
        "n_hours": int(s.size),
    }


def main() -> int:
    print("=" * 72)
    print(" ERA5 processing — Saros Bay")
    print("=" * 72)

    ds = open_all_files()
    time_dim = "valid_time" if "valid_time" in ds.coords else "time"
    t0 = pd.to_datetime(ds[time_dim].min().values)
    t1 = pd.to_datetime(ds[time_dim].max().values)
    print(f"Time range: {t0} → {t1}")
    print(f"Dims: {dict(ds.sizes)}")

    point = select_centroid_cell(ds)
    df = compute_wind_speeds(point)
    print(f"Hourly observations: {len(df):,}")
    print(f"Missing/NaN hours: {int(df['U100'].isna().sum())}")

    shear = estimate_shear_alpha(df)
    print(f"\nLog-law shear α (measured):")
    print(f"  mean={shear['alpha_mean']:.4f}  "
          f"median={shear['alpha_median']:.4f}  σ={shear['alpha_std']:.4f}")
    print(f"  90% range: [{shear['alpha_p5']:.3f}, {shear['alpha_p95']:.3f}]")

    u_hub = extrapolate_to_hub(df, shear["alpha_mean"])
    df["U_hub"] = u_hub

    print(f"\nWind speed at hub ({H_HUB} m):")
    stats = summary_stats(u_hub)
    for k, v in stats.items():
        print(f"  {k:<8s} = {v}")

    annual = {int(y): float(v)
              for y, v in u_hub.groupby(u_hub.index.year).mean().items()}
    print(f"\nAnnual mean @ hub:")
    for yr, val in annual.items():
        print(f"  {yr}: {val:.3f} m/s")
    iav_cv = float(np.std(list(annual.values())) / np.mean(list(annual.values())))
    print(f"  Inter-annual CoV: {iav_cv*100:.1f}%")

    monthly = {int(m): float(v)
               for m, v in u_hub.groupby(u_hub.index.month).mean().items()}
    months = ["J","F","M","A","M","J","J","A","S","O","N","D"]
    print(f"\nMonthly climatology (mean m/s):")
    for m, val in monthly.items():
        print(f"  {months[m-1]} ({m:02d}): {val:.2f}")

    df[["U10", "U100", "U_hub", "wdir"]].to_parquet(OUTPUT_TIMESERIES)
    print(f"\n✓ Saved time series: {OUTPUT_TIMESERIES}")

    summary = {
        "site": {"name": SITE.full_name,
                 "centroid_lat": SITE.centroid_lat,
                 "centroid_lon": SITE.centroid_lon},
        "period": {"start": str(df.index.min()), "end": str(df.index.max()),
                   "n_hours": int(len(df)), "n_years": SITE.era5_n_years},
        "shear_analysis": shear,
        "hub_height_m": H_HUB,
        "summary_stats_hub": stats,
        "annual_means": annual,
        "inter_annual_cv": iav_cv,
        "monthly_climatology": monthly,
    }
    OUTPUT_SUMMARY.write_text(json.dumps(summary, indent=2))
    print(f"✓ Saved summary:     {OUTPUT_SUMMARY}")
    print("\nNext step: python scripts/04_fit_weibull_aep.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
