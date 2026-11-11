"""
Phase 2B — fetch small external inputs for the wind-resource checks
====================================================================
Network script, run once. It writes only small extracts into
docs/review/phase2b_data/, plus a manifest with URLs, retrieval time and
SHA-256 checksums. Large downloads go to a temporary directory and are not
kept.

  * Global Wind Atlas 4.0, Türkiye country rasters at 100 m: mean wind
    speed, power density, combined Weibull A and k. Each is cropped to
    25.8–26.8 E, 40.2–40.9 N (native 0.0025 deg grid, unchanged).
  * EMODnet DTM 2024, 25.875–26.625 E x 40.125–40.875 N, downsampled
    x0.25 by the WCS server. Used only for land fraction around the ERA5
    grid point.
  * NOAA GSOD daily summaries 2014–2024 for the two ISD stations within
    80 km of the ERA5 point that cover the whole period: CANAKKALE
    17112099999 and DIMOKRITOS (Alexandroupoli) 16627099999. Reduced to
    station-year and station-month mean wind speed plus day counts.

Usage:  python scripts/phase2b_fetch_inputs.py
Needs:  numpy, pandas, rasterio, network access.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "review" / "phase2b_data"

GWA_LAYERS = ["wind-speed", "power-density", "combined-Weibull-A", "combined-Weibull-k"]
GWA_URL = "https://globalwindatlas.info/api/gis/country/TUR/{layer}/100"
GWA_BOX = (25.8, 40.2, 26.8, 40.9)                     # W, S, E, N
EMOD_URL = ("https://ows.emodnet-bathymetry.eu/wcs?service=WCS&version=2.0.1"
            "&request=GetCoverage&coverageId=emodnet__mean&format=image/tiff"
            "&subset=Lat(40.125,40.875)&subset=Long(25.875,26.625)&scalefactor=0.25")
GSOD_URL = "https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/{year}/{sid}.csv"
GSOD_STATIONS = {"17112099999": "CANAKKALE", "16627099999": "DIMOKRITOS"}
KNOT = 0.514444


def curl(url: str, dest: Path) -> None:
    subprocess.run(["curl", "-sS", "-L", "--fail", "-m", "600", "-A", "Mozilla/5.0",
                    "-o", str(dest), url], check=True)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    import rasterio
    from rasterio.windows import from_bounds

    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "files": {}}

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # ---- GWA 4.0 ----
        for layer in GWA_LAYERS:
            src = tmp / f"TUR_{layer}_100m.tif"
            url = GWA_URL.format(layer=layer)
            curl(url, src)
            with rasterio.open(src) as ds:
                win = from_bounds(*GWA_BOX, transform=ds.transform).round_offsets().round_lengths()
                arr = ds.read(1, window=win)
                prof = ds.profile.copy()
                prof.update(width=arr.shape[1], height=arr.shape[0],
                            transform=ds.window_transform(win), compress="deflate",
                            tiled=False)
                prof.pop("blockxsize", None); prof.pop("blockysize", None)
                dst = OUT / f"gwa4_{layer}_100m_saros.tif"
                with rasterio.open(dst, "w", **prof) as o:
                    o.write(arr, 1)
            manifest["files"][dst.name] = {
                "url": url, "source_file_sha256": sha(src),
                "source_bytes": src.stat().st_size, "sha256": sha(dst),
                "note": "crop of the GWA 4.0 country raster, native grid unchanged"}
            print("✓", dst.name)

        # ---- EMODnet DTM 2024 (downsampled) ----
        dst = OUT / "emodnet_dtm2024_era5cell_x0.25.tif"
        curl(EMOD_URL, dst)
        manifest["files"][dst.name] = {"url": EMOD_URL, "sha256": sha(dst),
                                       "note": "EMODnet DTM 2024 (doi:10.12770/cf51df64-56f9-4a99-b1aa-36b8d7b743a1), "
                                               "server-side scalefactor 0.25"}
        print("✓", dst.name)

    # ---- NOAA GSOD ----
    recs = []
    urls = []
    for sid, name in GSOD_STATIONS.items():
        for year in range(2014, 2025):
            url = GSOD_URL.format(year=year, sid=sid)
            urls.append(url)
            r = subprocess.run(["curl", "-sS", "-L", "--fail", "-m", "120", url],
                               check=True, capture_output=True)
            d = pd.read_csv(io.BytesIO(r.stdout), usecols=["STATION", "DATE", "LATITUDE",
                                                         "LONGITUDE", "ELEVATION", "NAME", "WDSP"])
            d = d[d["WDSP"] < 999.9]                       # 999.9 = missing
            d["DATE"] = pd.to_datetime(d["DATE"])
            for m, g in d.groupby(d["DATE"].dt.month):
                recs.append({"station": sid, "name": name, "year": year, "month": int(m),
                             "n_days": int(len(g)), "mean_wdsp_ms": float(g["WDSP"].mean() * KNOT),
                             "lat": float(g["LATITUDE"].iloc[0]), "lon": float(g["LONGITUDE"].iloc[0]),
                             "elev_m": float(g["ELEVATION"].iloc[0])})
    gs = pd.DataFrame(recs)
    dst = OUT / "gsod_monthly_2014_2024.csv"
    gs.to_csv(dst, index=False, float_format="%.4f")
    manifest["files"][dst.name] = {"url_pattern": GSOD_URL, "stations": GSOD_STATIONS,
                                   "sha256": sha(dst),
                                   "note": "monthly means of GSOD daily mean wind speed (WDSP, knots -> m/s); "
                                           "missing (999.9) excluded"}
    print("✓", dst.name)

    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print("✓ MANIFEST.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
