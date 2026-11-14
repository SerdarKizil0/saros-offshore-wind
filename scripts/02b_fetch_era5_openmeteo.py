"""
02b — Primary wind input (since Phase 5-PRE-B): ERA5 1994-2024 via Open-Meteo
==============================================================================
Network script, run once. Writes the PRIMARY production wind input:

  data/external/era5_openmeteo/era5_openmeteo_40.50N_26.25E_1994_2024.parquet
  data/external/era5_openmeteo/MANIFEST.json

Content: hourly ERA5 at the 0.25 deg node 40.50 N 26.25 E (the node of the
historical CDS series, data/processed/wind_hub_105m.parquet), 1994-01-01 00:00
to 2024-12-31 23:00 UTC:
  U10, U100   wind speed at 10 m and 100 m, int16 centi-m/s (API: two decimals)
  wdir100     meteorological direction at 100 m, int16 degrees (API: whole degrees)
Row i = 1994-01-01 00:00 UTC + i hours. The time axis is verified complete and
regular before the timestamp column is dropped.

Source: Open-Meteo historical-weather API, models=era5, cell_selection=nearest.
Open-Meteo redistributes ECMWF ERA5 on the native 0.25 deg grid with lossy
internal storage. The values are NOT bit-identical to a CDS download. Phase
5-PRE calibrated this source against the CDS series over 2014-2024 (pooled
gross CF -0.004 %); scripts/04 re-checks the calibration on every run.

The production pipeline pins the file by SHA-256 (config/wind_data.py). If a
re-fetch returns different bytes (e.g. Open-Meteo reprocessing), the pipeline
stops instead of silently changing the primary input.

Usage:  python scripts/02b_fetch_era5_openmeteo.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config.wind_data import PRIMARY  # noqa: E402

LAT, LON = PRIMARY.node_lat, PRIMARY.node_lon
Y0, Y1 = PRIMARY.period
CHUNKS = [(1994, 2008), (2009, 2024)]
URL = ("https://archive-api.open-meteo.com/v1/archive?latitude={lat:.2f}&longitude={lon:.2f}"
       "&start_date={y0}-01-01&end_date={y1}-12-31"
       "&hourly=wind_speed_10m,wind_speed_100m,wind_direction_100m"
       "&models=era5&wind_speed_unit=ms&timezone=GMT&cell_selection=nearest")


def get(url: str, tries: int = 6) -> bytes:
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-script"})
            return urllib.request.urlopen(req, timeout=180).read()
        except (urllib.error.URLError, TimeoutError) as e:
            wait = 30 * (k + 1) if getattr(e, "code", None) == 429 else 5 * (k + 1)
            print(f"  retry {k + 1}/{tries} after {wait}s: {e}")
            time.sleep(wait)
    raise RuntimeError(f"failed: {url}")


def main() -> int:
    assert (CHUNKS[0][0], CHUNKS[-1][1]) == (Y0, Y1)
    out_dir = PRIMARY.path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    log, parts = [], []
    for y0, y1 in CHUNKS:
        url = URL.format(lat=LAT, lon=LON, y0=y0, y1=y1)
        body = get(url)
        j = json.loads(body)
        if abs(j["latitude"] - LAT) > 1e-6 or abs(j["longitude"] - LON) > 1e-6:
            raise RuntimeError(f"grid point mismatch: got {j['latitude']}, {j['longitude']}")
        h = j["hourly"]
        df = pd.DataFrame({"U10": h["wind_speed_10m"], "U100": h["wind_speed_100m"],
                           "wdir100": h["wind_direction_100m"]}, index=pd.to_datetime(h["time"]))
        if df.isna().any().any():
            raise RuntimeError(f"{y0}-{y1}: missing values")
        parts.append(df)
        log.append({"years": [y0, y1], "url": url, "sha256": hashlib.sha256(body).hexdigest(),
                    "grid_lat": j["latitude"], "grid_lon": j["longitude"], "rows": len(df)})
        print(f"  {y0}-{y1}: {len(df)} h")
        time.sleep(3)
    d = pd.concat(parts)
    full = pd.date_range(f"{Y0}-01-01 00:00", f"{Y1}-12-31 23:00", freq="h")
    if not d.index.equals(full):
        raise RuntimeError("time axis is not the complete hourly range")
    store = pd.DataFrame({"U10": (d.U10 * 100).round().astype("int16"),
                          "U100": (d.U100 * 100).round().astype("int16"),
                          "wdir100": d.wdir100.round().astype("int16")}).reset_index(drop=True)
    store.to_parquet(PRIMARY.path, compression="zstd", compression_level=19)
    sha = hashlib.sha256(PRIMARY.path.read_bytes()).hexdigest()
    manifest = {
        "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "file": PRIMARY.path.name, "sha256": sha, "rows": int(len(store)),
        "node": {"lat": LAT, "lon": LON}, "period_utc": [str(full[0]), str(full[-1])],
        "columns": {"U10": "int16 centi-m/s", "U100": "int16 centi-m/s", "wdir100": "int16 degrees (from)"},
        "time_axis": f"row i = {Y0}-01-01 00:00 UTC + i hours",
        "data_product": PRIMARY.data_product,
        "requests": log,
        "licences": {"ERA5": "Contains modified Copernicus Climate Change Service information; CC BY 4.0",
                     "Open-Meteo": "CC BY 4.0; Zippenfenig, P. (2023) Open-Meteo.com Weather API, "
                                   "doi:10.5281/zenodo.7970649"},
    }
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"wrote {PRIMARY.path} sha256 {sha}")
    if sha != PRIMARY.sha256:
        print("NOTE: sha256 differs from the pin in config/wind_data.py; review before updating the pin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
