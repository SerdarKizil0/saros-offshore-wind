"""
Phase 2B — wind-resource representativeness and sensitivity (provisional)
==========================================================================
Offline analysis of committed inputs only:
  data/processed/wind_hub_105m.parquet            ERA5 series (baseline, unchanged)
  docs/review/phase1_data/SAROS_DURES_official.kml official polygon
  docs/review/phase1_data/emodnet_dtm2024_saros_crop.tif
  docs/review/phase2b_data/*                       GWA 4.0, EMODnet, GSOD extracts
                                                   (from scripts/phase2b_fetch_inputs.py)

Writes (provisional; nothing else is modified):
  results/provisional/phase2b/wind_validation.json
  results/provisional/phase2b/wind_speed_sensitivity.json

The sensitivity cases scale ERA5 hub-height speed by fixed factors. They
are sensitivity experiments, not bias corrections, forecasts or
uncertainty percentiles, and do not replace the baseline.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import rasterio
from scipy import stats
from scipy.special import gamma

from config.site import SITE
from config.turbine import (TURBINE, POWER_CURVE_ID, POWER_CURVE_MS_KW,
                            WAKE_LOSS_DEFAULT, AVAILABILITY_DEFAULT,
                            ELECTRICAL_LOSS_DEFAULT)

P1 = ROOT / "docs" / "review" / "phase1_data"
P2 = ROOT / "docs" / "review" / "phase2b_data"
OUT = ROOT / "results" / "provisional" / "phase2b"
PARQUET = ROOT / "data" / "processed" / "wind_hub_105m.parquet"

ERA5_PT = (40.50, 26.25)            # (lat, lon) nearest 0.25 deg node to the centroid
HALF = 0.125                        # half-width of the 0.25 deg box around the node
RHO = 1.225
R_E = 6371.0
NET_FACTOR = ((1 - WAKE_LOSS_DEFAULT) * AVAILABILITY_DEFAULT
              * (1 - ELECTRICAL_LOSS_DEFAULT))
RATED_KW = TURBINE.rated_power_mw * 1000
FACTORS = [0.90, 0.95, 1.00, 1.05, 1.10]


# ------------------------------------------------------------------ helpers
def km(lat1, lon1, lat2, lon2):
    x = np.radians(np.asarray(lon2) - lon1) * np.cos(np.radians(0.5 * (lat1 + np.asarray(lat2))))
    y = np.radians(np.asarray(lat2) - lat1)
    return R_E * np.hypot(x, y)


def read_kml_ring(path):
    import re
    t = path.read_text(encoding="utf-8")
    pts = [tuple(map(float, s.split(",")[:2]))
           for s in re.findall(r"<coordinates>(.*?)</coordinates>", t, re.S)[0].split()]
    return pts[:-1] if pts[0] == pts[-1] else pts            # (lon, lat)


def inside(lon, lat, ring):
    x, y = np.asarray(lon), np.asarray(lat)
    m = np.zeros(x.shape, bool)
    for i in range(len(ring)):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % len(ring)]
        c = (y1 > y) != (y2 > y)
        xi = (x2 - x1) * (y - y1) / ((y2 - y1) if y2 != y1 else 1e-30) + x1
        m ^= c & (x < xi)
    return m


def raster_centres(path, transform=None):
    ds = rasterio.open(path)
    a = ds.read(1).astype(float)
    tr = transform or ds.transform
    r, c = np.indices(a.shape)
    xs, ys = rasterio.transform.xy(tr, r, c, offset="center")
    return a, np.asarray(xs).reshape(a.shape), np.asarray(ys).reshape(a.shape), tr


def power_from_speed(u):
    """Identical to scripts/04 power_from_speed (active curve)."""
    pc_ms = [p[0] for p in POWER_CURVE_MS_KW]
    pc_kw = [p[1] for p in POWER_CURVE_MS_KW]
    p = np.interp(u, pc_ms, pc_kw, left=0, right=0)
    p[u < TURBINE.cut_in_ms] = 0.0
    p[u >= TURBINE.cut_out_ms] = 0.0
    return p


def r(x, n=4):
    return None if x is None else float(round(float(x), n))


# --------------------------------------------------------------- sections
def series_checks(df):
    """Task 2.4 — completeness and internal consistency of the 11-year series."""
    idx = df.index
    yr = idx.year
    full = pd.date_range("2014-01-01 00:00", "2024-12-31 23:00", freq="h")
    run = (df["U100"].diff() != 0).cumsum()
    longest_const = int(df.groupby(run).size().max())
    ratio = (df["U_hub"] / df["U100"]).to_numpy()
    by_year = {}
    for y, g in df.groupby(yr):
        m = (g.U10 > 1) & (g.U100 > 1)
        a = np.log(g.U100[m] / g.U10[m]) / np.log(10)
        lo, hi = np.percentile(a, [1, 99])
        by_year[int(y)] = {
            "hours": int(len(g)),
            "mean_U10": r(g.U10.mean()), "mean_U100": r(g.U100.mean()),
            "mean_U_hub": r(g.U_hub.mean()),
            "alpha_trimmed_mean": r(a[(a >= lo) & (a <= hi)].mean()),
            "share_U10_gt_U100_pct": r((g.U10 > g.U100).mean() * 100, 2),
            "share_NE_quadrant_pct": r(((g.wdir >= 0) & (g.wdir < 90)).mean() * 100, 2),
            "share_hours_lt_3ms_pct": r((g.U_hub < 3).mean() * 100, 2),
        }
    return {
        "n_hours": int(len(df)), "expected_hours": int(len(full)),
        "index_equals_full_hourly_range": bool(idx.equals(full)),
        "duplicates": int(idx.duplicated().sum()), "nan_values": int(df.isna().sum().sum()),
        "min_max": {c: [r(df[c].min()), r(df[c].max())] for c in df.columns},
        "U_hub_over_U100_min_max": [float(ratio.min()), float(ratio.max())],
        "longest_run_identical_U100_hours": longest_const,
        "by_year": by_year,
    }


def anomaly_2014(df, gsod):
    """Task 2.3 — is 2014 low in the ERA5 series and in station records?"""
    out = {}
    ann = df.groupby(df.index.year)[["U10", "U100", "U_hub"]].mean()
    rest = ann.loc[2015:2024]
    for c in ann.columns:
        out[f"ERA5_{c}_2014_vs_2015_2024_pct"] = r((ann.loc[2014, c] / rest[c].mean() - 1) * 100, 2)
        out[f"ERA5_{c}_2014_z_vs_2015_2024"] = r((ann.loc[2014, c] - rest[c].mean()) / rest[c].std(ddof=1), 2)
    mon = df["U100"].groupby([df.index.year, df.index.month]).mean().unstack()
    clim = mon.loc[2015:2024].mean()
    out["ERA5_U100_2014_monthly_anomaly_pct"] = {int(m): r((mon.loc[2014, m] / clim[m] - 1) * 100, 1)
                                                for m in range(1, 13)}
    st = {}
    for sid, g in gsod.groupby("station"):
        yr = g.groupby("year").apply(lambda x: pd.Series({
            "days": x.n_days.sum(),
            "mean": np.average(x.mean_wdsp_ms, weights=x.n_days)}), include_groups=False)
        good = yr[yr.days >= 330]
        rest_ = good.loc[good.index >= 2015, "mean"]
        rec = {"name": g.name.iloc[0], "lat": r(g.lat.iloc[0]), "lon": r(g.lon.iloc[0]),
               "distance_to_ERA5_point_km": r(km(*ERA5_PT, g.lat.iloc[0], g.lon.iloc[0]), 1),
               "days_per_year": {int(k): int(v) for k, v in yr.days.items()},
               "annual_mean_ms": {int(k): r(v, 3) for k, v in yr["mean"].items()}}
        if 2014 in good.index and len(rest_) >= 5:
            rec["2014_vs_2015_2024_pct"] = r((good.loc[2014, "mean"] / rest_.mean() - 1) * 100, 2)
            rec["2014_z"] = r((good.loc[2014, "mean"] - rest_.mean()) / rest_.std(ddof=1), 2)
        # month-to-month co-variability with ERA5 10 m speed (same months, >= 25 days)
        e10 = df["U10"].groupby([df.index.year, df.index.month]).mean()
        gg = g[g.n_days >= 25].set_index(["year", "month"])["mean_wdsp_ms"]
        j = pd.concat([e10.rename("era5"), gg.rename("st")], axis=1, join="inner").dropna()
        an = j.groupby(level=1).transform(lambda s: s - s.mean())      # remove seasonal cycle
        rec["monthly_anomaly_corr_with_ERA5_U10"] = r(an.era5.corr(an.st), 3)
        rec["n_months_compared"] = int(len(j))
        # 2014 month by month: % anomaly vs the station's own 2015-2024 monthly climatology
        clim_st = j.loc[j.index.get_level_values(0) >= 2015].groupby(level=1).mean()
        if 2014 in j.index.get_level_values(0):
            j14 = j.loc[2014]
            a_st = (j14.st / clim_st.st.reindex(j14.index) - 1) * 100
            a_e = (j14.era5 / clim_st.era5.reindex(j14.index) - 1) * 100
            rec["2014_monthly_anomaly_pct"] = {int(m): r(v, 1) for m, v in a_st.items()}
            rec["2014_ERA5_U10_monthly_anomaly_pct_same_months"] = {int(m): r(v, 1) for m, v in a_e.items()}
            rec["2014_monthly_anomaly_corr"] = r(np.corrcoef(a_st, a_e)[0, 1], 3) if len(a_st) > 3 else None
        st[sid] = rec
    out["GSOD_stations"] = st
    return out


def era5_point_stats(df):
    u = df["U100"].to_numpy().astype(float)
    k, _, c = stats.weibull_min.fit(u[u > 0], floc=0)
    sub = df.loc["2014":"2017", "U100"]
    return {
        "location": {"lat": ERA5_PT[0], "lon": ERA5_PT[1],
                     "basis": "0.25 deg ERA5 node nearest the polygon centroid "
                              f"({SITE.centroid_lat}, {SITE.centroid_lon}); coordinates are not stored "
                              "in the parquet, selection reproduced from scripts/03 logic"},
        "period": "2014-01-01 to 2024-12-31 (hourly, instantaneous at the top of each hour, UTC)",
        "mean_U100_2014_2024": r(u.mean()),
        "mean_U100_2015_2024": r(df.loc["2015":"2024", "U100"].mean()),
        "mean_U100_2014_2017_overlap_with_GWA_period": r(sub.mean()),
        "weibull_k_U100": r(k), "weibull_c_U100": r(c),
        "power_density_U100_Wm2_rho1225": r(0.5 * RHO * np.mean(u ** 3), 1),
    }


def gwa_compare(ring, era5):
    ws, X, Y, tr = raster_centres(P2 / "gwa4_wind-speed_100m_saros.tif")
    pdn, *_ = raster_centres(P2 / "gwa4_power-density_100m_saros.tif", tr)
    A, *_ = raster_centres(P2 / "gwa4_combined-Weibull-A_100m_saros.tif", tr)
    K, *_ = raster_centres(P2 / "gwa4_combined-Weibull-k_100m_saros.tif", tr)
    # land/sea at GWA pixel centres from the EMODnet DTM (downsampled)
    dem = rasterio.open(P2 / "emodnet_dtm2024_era5cell_x0.25.tif")
    inb = ((X > dem.bounds.left) & (X < dem.bounds.right) &
           (Y > dem.bounds.bottom) & (Y < dem.bounds.top))
    z = np.full(ws.shape, np.nan)
    z[inb] = np.array([v[0] for v in dem.sample(zip(X[inb], Y[inb]))])
    sea = z < 0

    def agg(mask, name):
        return {"region": name, "n_pixels": int(mask.sum()),
                "mean_ws": r(np.nanmean(ws[mask])), "min_ws": r(np.nanmin(ws[mask])),
                "max_ws": r(np.nanmax(ws[mask])), "std_ws": r(np.nanstd(ws[mask])),
                "mean_k": r(np.nanmean(K[mask])), "mean_pd_Wm2": r(np.nanmean(pdn[mask]), 1)}

    i, j = map(int, ~tr @ (ERA5_PT[1], ERA5_PT[0]))          # col, row of the node pixel
    poly = inside(X, Y, ring)
    box = (np.abs(Y - ERA5_PT[0]) <= HALF) & (np.abs(X - ERA5_PT[1]) <= HALF)
    node = {"region": "GWA pixel containing the ERA5 node", "pixel_centre": [r(Y[j, i]), r(X[j, i])],
            "ws": r(ws[j, i]), "k": r(K[j, i]), "A": r(A[j, i]), "pd_Wm2": r(pdn[j, i], 1),
            "A_gamma_mean": r(A[j, i] * gamma(1 + 1 / K[j, i]))}
    regions = [agg(poly, "official polygon"),
               agg(box, "0.25 deg box centred on ERA5 node, all pixels"),
               agg(box & sea, "0.25 deg box centred on ERA5 node, sea pixels"),
               agg(box & ~sea & inb, "0.25 deg box centred on ERA5 node, land pixels")]
    e = era5["mean_U100_2014_2024"]
    ratios = {"node_pixel": r(node["ws"] / e)}
    for g in regions:
        ratios[g["region"]] = r(g["mean_ws"] / e)
    # within-polygon N-S gradient (modelled spatial variability)
    lat_bands = {}
    for a, b in ((40.50, 40.53), (40.53, 40.56), (40.56, 40.58), (40.58, 40.60)):
        m = poly & (Y >= a) & (Y < b)
        lat_bands[f"{a:.2f}-{b:.2f}"] = r(np.nanmean(ws[m]))
    return {"dataset": "Global Wind Atlas 4.0 (DTU / World Bank ESMAP), country raster TUR, 100 m a.g.l., "
                       "0.0025 deg grid; WRF 3 km forced by ERA5 2008-2017, generalised and WAsP/PyWAsP "
                       "microscale (DTU Wind Energy Report E-0256)",
            "node_pixel": node, "regions": regions,
            "ratio_GWA_mean_to_ERA5_U100_mean_2014_2024": ratios,
            "polygon_gwa_ws_by_latitude_band": lat_bands}


def geometry(ring):
    lon = np.array([p[0] for p in ring]); lat = np.array([p[1] for p in ring])
    # dense sampling of polygon interior
    gx, gy = np.meshgrid(np.arange(26.03, 26.47, 0.001), np.arange(40.50, 40.60, 0.001))
    m = inside(gx, gy, ring)
    inbox = (np.abs(gy - ERA5_PT[0]) <= HALF) & (np.abs(gx - ERA5_PT[1]) <= HALF)
    # nearest 0.25 deg node for each interior sample
    nlat = np.round(gy[m] * 4) / 4; nlon = np.round(gx[m] * 4) / 4
    share = pd.Series(list(zip(nlat, nlon))).value_counts(normalize=True)
    # distance node -> polygon boundary (densified edges)
    seg = []
    for a in range(len(ring)):
        (x1, y1), (x2, y2) = ring[a], ring[(a + 1) % len(ring)]
        t = np.linspace(0, 1, 200)
        seg.append(np.c_[x1 + t * (x2 - x1), y1 + t * (y2 - y1)])
    seg = np.vstack(seg)
    d = km(ERA5_PT[0], ERA5_PT[1], seg[:, 1], seg[:, 0])
    # land fraction and depth around the node from EMODnet (downsampled)
    zz, ex, ey, _ = raster_centres(P2 / "emodnet_dtm2024_era5cell_x0.25.tif")
    b = (np.abs(ey - ERA5_PT[0]) <= HALF) & (np.abs(ex - ERA5_PT[1]) <= HALF)
    b2 = (np.abs(ey - ERA5_PT[0]) <= 2 * HALF) & (np.abs(ex - ERA5_PT[1]) <= 2 * HALF)
    land = zz >= 0
    jn = np.unravel_index(np.argmin(km(*ERA5_PT, ey, ex)), zz.shape)
    north = land & (ey > ERA5_PT[0] + 0.05)
    south = land & (ey < ERA5_PT[0] - 0.05)
    return {
        "era5_node_inside_polygon": bool(inside(np.array([ERA5_PT[1]]), np.array([ERA5_PT[0]]), ring)[0]),
        "era5_node_to_polygon_boundary_min_km": r(d.min(), 2),
        "era5_node_to_centroid_km": r(km(*ERA5_PT, SITE.centroid_lat, SITE.centroid_lon), 2),
        "polygon_share_in_0p25deg_box_of_node_pct": r(inbox[m].mean() * 100, 1),
        "polygon_share_by_nearest_0p25deg_node_pct": {f"{k[0]:.2f}N {k[1]:.2f}E": r(v * 100, 1)
                                                     for k, v in share.items()},
        "depth_at_node_m": r(-zz[jn], 0),
        "land_fraction_0p25deg_box_pct": r(land[b].mean() * 100, 1),
        "land_fraction_0p5deg_box_pct": r(land[b2].mean() * 100, 1),
        "node_to_northern_coast_km": r(km(*ERA5_PT, ey[north], ex[north]).min(), 1),
        "node_to_southern_coast_km": r(km(*ERA5_PT, ey[south], ex[south]).min(), 1),
        "note": "Land fraction is the geometric share of EMODnet DTM cells >= 0 m inside the box. "
                "It approximates, but is not, the ERA5 land-sea mask, which was not available.",
    }


def sensitivity(df, gwa):
    u0 = df["U_hub"].to_numpy().astype(float)
    e100 = float(df["U100"].mean())
    f_gwa = gwa["regions"][0]["mean_ws"] / e100
    cases = [(f"{(f - 1) * 100:+.0f}%" if f != 1 else "baseline ERA5", f) for f in FACTORS]
    cases.append(("scaled to GWA 4.0 polygon mean at 100 m (illustrative)", f_gwa))
    rows = []
    base = None
    for name, f in cases:
        u = u0 * f
        pk = power_from_speed(u)
        gross = pk.sum() / SITE.era5_n_years / 1e6           # GWh/yr per turbine
        row = {"case": name, "speed_factor": r(f, 5), "mean_U_hub": r(u.mean()),
               "gross_aep_gwh_per_turbine": r(gross), "gross_cf_pct": r(pk.mean() / RATED_KW * 100),
               "net_aep_gwh_per_turbine": r(gross * NET_FACTOR),
               "net_cf_pct": r(pk.mean() / RATED_KW * NET_FACTOR * 100),
               "net_aep_gwh_per_mw": r(gross * NET_FACTOR / TURBINE.rated_power_mw)}
        if f == 1.0:
            base = row
        rows.append(row)
    for row in rows:
        row["aep_change_vs_baseline_pct"] = r((row["gross_aep_gwh_per_turbine"]
                                               / base["gross_aep_gwh_per_turbine"] - 1) * 100, 2)
    return {
        "status": "PROVISIONAL SENSITIVITY EXPERIMENT — not a bias correction, forecast, "
                  "uncertainty percentile or replacement for the baseline",
        "method": "empirical hourly AEP (scripts/04 method), all hourly U_hub values multiplied "
                  "by the factor; turbine curve and nominal losses fixed",
        "power_curve": POWER_CURVE_ID, "net_factor": NET_FACTOR,
        "gwa_scaling_basis": {"gwa_polygon_mean_100m": gwa["regions"][0]["mean_ws"],
                              "era5_U100_mean_2014_2024": r(e100),
                              "caveat": "different periods (GWA 2008-2017 vs ERA5 2014-2024), "
                                        "different spatial support (polygon mean of 250 m pixels vs "
                                        "one 0.25 deg node), uniform scaling keeps the ERA5 shape"},
        "cases": rows,
    }


def main() -> int:
    df = pd.read_parquet(PARQUET)
    ring = read_kml_ring(P1 / "SAROS_DURES_official.kml")
    gsod = pd.read_csv(P2 / "gsod_monthly_2014_2024.csv", dtype={"station": str})
    era5 = era5_point_stats(df)
    gwa = gwa_compare(ring, era5)
    val = {
        "status": "PROVISIONAL — Phase 2B review analysis; baseline data and results unchanged",
        "era5_point": era5,
        "gwa4": gwa,
        "geometry_and_land_sea": geometry(ring),
        "series_checks": series_checks(df),
        "anomaly_2014": anomaly_2014(df, gsod),
        "neighbouring_era5_cells": "NOT AVAILABLE — no neighbouring-cell series in the repository; "
                                   "CDS credentials absent; Open-Meteo archive API timed out from this "
                                   "environment (11.11.2026). No substitute generated.",
    }
    sens = sensitivity(df, gwa)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "wind_validation.json").write_text(json.dumps(val, indent=2, ensure_ascii=False))
    (OUT / "wind_speed_sensitivity.json").write_text(json.dumps(sens, indent=2, ensure_ascii=False))
    print(json.dumps({"era5_point": era5, "gwa_ratios": gwa["ratio_GWA_mean_to_ERA5_U100_mean_2014_2024"]},
                     indent=1))
    for row in sens["cases"]:
        print(f"{row['case']:<58s} f={row['speed_factor']:.4f} gross {row['gross_aep_gwh_per_turbine']:6.2f} "
              f"GWh  CFg {row['gross_cf_pct']:5.2f}%  net {row['net_aep_gwh_per_turbine']:6.2f}  "
              f"CFn {row['net_cf_pct']:5.2f}%  {row['aep_change_vs_baseline_pct']:+6.2f}%")
    print(f"✓ wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
