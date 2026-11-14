"""
Phase 5-PRE — fetch ERA5 inputs for the temporal and spatial robustness checks
==============================================================================
Network script, run once. Writes into data/external/phase5pre/:

  * era5_openmeteo_40.50N_<lon>E_1979_2024.parquet  (three nodes, 26.00/26.25/26.50 E)
      Hourly ERA5 10 m and 100 m wind speed (m/s) for 1979-01-01 00:00 to
      2024-12-31 23:00 UTC, from the Open-Meteo historical-weather API with
      models=era5 and cell_selection=nearest. Stored as int16 centi-m/s
      (the API returns two decimals, so the storage is lossless). The time axis
      is verified to be the complete hourly range and then dropped: row i is
      1979-01-01 00:00 UTC + i hours.
  * era5_land_sea_mask_saros.json
      ERA5 static land-sea mask (fraction 0-1) on the 0.25 deg grid,
      25.50-27.00 E x 40.00-41.00 N, read from one chunk of the public
      ARCO-ERA5 Zarr store (Google Cloud, anonymous HTTPS).
  * MANIFEST.json
      Every request URL, retrieval time, per-response SHA-256, grid point
      returned by the API, row counts and the SHA-256 of each written file.

Why Open-Meteo and not the CDS:
  The CDS needs credentials, and none are available in this environment
  (no ~/.cdsapirc). The raw CDS NetCDF files of the 2014-2024 baseline are
  not in the repository (gitignored, data/README.md). Open-Meteo redistributes
  ERA5 on the native 0.25 deg grid but stores it with lossy compression, so
  its values are not bit-identical to the CDS. The analysis script therefore
  calibrates the Open-Meteo series against the committed CDS-derived
  baseline (data/processed/wind_hub_105m.parquet) over 2014-2024 before
  using it, and uses Open-Meteo only for ratios anchored to that baseline.

CDS equivalent (for a user with credentials), per node or as a box:
  dataset  reanalysis-era5-single-levels, product_type reanalysis
  variable 10m_u_component_of_wind, 10m_v_component_of_wind,
           100m_u_component_of_wind, 100m_v_component_of_wind
  years    1979-2024, all months, days, 24 hours
  area     [40.55, 25.95, 40.45, 26.55]  (N, W, S, E) -> nodes 40.50 N x 26.00/26.25/26.50 E
  then:    python scripts/02_download_era5_saros.py (edit years/area) and
           re-run this phase with the CDS series in place of the Open-Meteo one.

Usage:  python scripts/phase5pre_fetch_inputs.py
Needs:  numpy, pandas, pyarrow, numcodecs (blosc), network access.
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

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "external" / "phase5pre"

NODES = {"W": (40.50, 26.00), "C": (40.50, 26.25), "E": (40.50, 26.50)}
YEAR0, YEAR1 = 1979, 2024
CHUNKS = [(1979, 2001), (2002, 2024)]            # two 23-year requests per node
OM_URL = ("https://archive-api.open-meteo.com/v1/archive?latitude={lat:.2f}&longitude={lon:.2f}"
          "&start_date={y0}-01-01&end_date={y1}-12-31&hourly=wind_speed_10m,wind_speed_100m"
          "&models=era5&wind_speed_unit=ms&timezone=GMT&cell_selection=nearest")
ARCO = "https://storage.googleapis.com/gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
LSM_BOX = (25.50, 40.00, 27.00, 41.00)          # W, S, E, N
PAUSE_S = 3.0


def node_file(lon: float) -> Path:
    return OUT / f"era5_openmeteo_40.50N_{lon:.2f}E_{YEAR0}_{YEAR1}.parquet"


def get(url: str, tries: int = 6) -> bytes:
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-script"})
            return urllib.request.urlopen(req, timeout=180).read()
        except (urllib.error.URLError, TimeoutError) as e:
            wait = 30 * (k + 1) if getattr(e, "code", None) == 429 else 5 * (k + 1)
            print(f"    retry {k + 1}/{tries} after {wait}s: {e}")
            time.sleep(wait)
    raise RuntimeError(f"failed: {url}")


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch_node(key: str, lat: float, lon: float, log: list) -> pd.DataFrame:
    parts = []
    for y0, y1 in CHUNKS:
        url = OM_URL.format(lat=lat, lon=lon, y0=y0, y1=y1)
        body = get(url)
        j = json.loads(body)
        if abs(j["latitude"] - lat) > 1e-6 or abs(j["longitude"] - lon) > 1e-6:
            raise RuntimeError(f"grid point mismatch: asked {lat},{lon}, got {j['latitude']},{j['longitude']}")
        h = j["hourly"]
        df = pd.DataFrame({"U10": h["wind_speed_10m"], "U100": h["wind_speed_100m"]},
                          index=pd.to_datetime(h["time"]))
        n_exp = sum(8784 if pd.Timestamp(year=y, month=1, day=1).is_leap_year else 8760
                    for y in range(y0, y1 + 1))
        if len(df) != n_exp or df.isna().any().any():
            raise RuntimeError(f"{key} {y0}-{y1}: {len(df)} rows, {int(df.isna().sum().sum())} NaN")
        parts.append(df)
        log.append({"node": key, "years": [y0, y1], "url": url, "sha256": sha_bytes(body),
                    "grid_lat": j["latitude"], "grid_lon": j["longitude"], "rows": len(df)})
        print(f"  {key} {lon:.2f}E {y0}-{y1}: {len(df)} h")
        time.sleep(PAUSE_S)
    out = pd.concat(parts)
    full = pd.date_range(f"{YEAR0}-01-01 00:00", f"{YEAR1}-12-31 23:00", freq="h")
    if not out.index.equals(full):
        raise RuntimeError(f"{key}: time axis is not the complete hourly range {YEAR0}-{YEAR1}")
    out.index.name = "time"
    return out


def fetch_lsm() -> tuple[dict, dict]:
    import numcodecs
    blosc = numcodecs.Blosc()
    lat = np.frombuffer(blosc.decode(get(f"{ARCO}/latitude/0")), "<f4")
    lon = np.frombuffer(blosc.decode(get(f"{ARCO}/longitude/0")), "<f4")
    t = int((dt.datetime(2014, 1, 1) - dt.datetime(1900, 1, 1)).total_seconds() // 3600)
    url = f"{ARCO}/land_sea_mask/{t}.0.0"
    raw = get(url)
    lsm = np.frombuffer(blosc.decode(raw), "<f4").reshape(len(lat), len(lon))
    w, s, e, n = LSM_BOX
    iy = np.where((lat >= s - 1e-6) & (lat <= n + 1e-6))[0]
    ix = np.where((lon >= w - 1e-6) & (lon <= e + 1e-6))[0]
    sub = {"latitude": [float(lat[i]) for i in iy], "longitude": [float(lon[i]) for i in ix],
           "land_sea_mask": [[round(float(lsm[i, k]), 6) for k in ix] for i in iy],
           "units": "fraction of land (0-1); ERA5 static field 'lsm'",
           "source": "ARCO-ERA5 (Google Cloud public dataset), store full_37-1h-0p25deg-chunk-1.zarr-v3, "
                     "variable land_sea_mask, time index 2014-01-01T00 (field is static)"}
    prov = {"url": url, "chunk_sha256": sha_bytes(raw), "time_index_hours_since_1900": t}
    return sub, prov


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "description": "Phase 5-PRE inputs; see scripts/phase5pre_fetch_inputs.py docstring",
                "licences": {"ERA5": "Copernicus Climate Change Service licence; contains modified "
                                     "Copernicus Climate Change Service information",
                             "Open-Meteo": "data served under CC BY 4.0 (open-meteo.com); "
                                           "Zippenfenig, P. (2023) Open-Meteo.com Weather API, "
                                           "doi:10.5281/zenodo.7970649",
                             "ARCO-ERA5": "Google Cloud public dataset; Carver & Merose (2023), ARCO-ERA5"},
                "openmeteo_requests": [], "files": {}}

    lsm, lsm_prov = fetch_lsm()
    p = OUT / "era5_land_sea_mask_saros.json"
    p.write_text(json.dumps(lsm, indent=1))
    manifest["land_sea_mask"] = lsm_prov
    manifest["files"][p.name] = sha_bytes(p.read_bytes())

    for key, (lat, lon) in NODES.items():
        df = fetch_node(key, lat, lon, manifest["openmeteo_requests"])
        store = (df * 100).round().astype("int16").reset_index(drop=True)
        f = node_file(lon)
        store.to_parquet(f, compression="zstd", compression_level=19)
        manifest["files"][f.name] = sha_bytes(f.read_bytes())
        manifest.setdefault("nodes", {})[key] = {
            "lat": lat, "lon": lon, "file": f.name, "rows": int(len(df)),
            "start": str(df.index[0]), "end": str(df.index[-1]),
            "storage": "int16 centi-m/s (divide by 100); API values have two decimals",
            "time_axis": f"row i = {YEAR0}-01-01 00:00 UTC + i hours (verified complete and regular "
                         f"before the timestamp column was dropped)"}

    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
