"""
Phase 5-PRE — temporal and spatial robustness of the 2014-2024 ERA5 estimate
============================================================================
Offline. Reads the committed baseline (data/processed/wind_hub_105m.parquet,
CDS-derived, node 40.50 N 26.25 E) and the Phase 5-PRE inputs fetched by
scripts/phase5pre_fetch_inputs.py (data/external/phase5pre/: Open-Meteo ERA5
at 40.50 N x 26.00/26.25/26.50 E, 1979-2024; ERA5 land-sea mask).

Writes results/provisional/phase5pre/ only. results/revised/ is not touched.

Method (identical to the production estimator, scripts/04):
  * hub height: U_hub = U100 * (105/100)**alpha, alpha = trimmed mean of the
    hourly ERA5 10 m/100 m log-ratio exponent (scripts/03 estimate_shear_alpha).
    Temporal comparisons at the baseline node use the baseline alpha for all
    years so that only the wind changes; spatial comparisons use each node's
    own alpha from 2014-2024 (the documented method), with the
    baseline-alpha variant also reported.
  * power: OEDB V164/9500 curve (scripts/04 power_from_speed), nominal losses,
    CF = sum P / (P_r * hours), net GWh/MW/yr = CF_net * 8.766.
  * Open-Meteo is used only after calibration against the CDS baseline over
    2014-2024 (acceptance criteria in CRITERIA). Period and node results are
    reported both as raw Open-Meteo values and "anchored" to the CDS baseline:
    anchored = CDS_2014-2024 * (OpenMeteo_X / OpenMeteo_C_2014-2024).

Labels: OBSERVED (model years), SAMPLING (t-interval), SENSITIVITY, MODEL
DISAGREEMENT, INTERPOLATION. Nothing here is a validation against measurements.

Usage:  python scripts/phase5pre_era5_robustness.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

IN_DIR = ROOT / "data" / "external" / "phase5pre"
BASE_PARQUET = ROOT / "data" / "processed" / "wind_hub_105m.parquet"
REVISED = ROOT / "results" / "revised"
OUT = ROOT / "results" / "provisional" / "phase5pre"
KML = ROOT / "docs/review/phase1_data/SAROS_DURES_official.kml"
GWA_TIF = ROOT / "docs/review/phase2b_data/gwa4_wind-speed_100m_saros.tif"
DTM_FINE = ROOT / "docs/review/phase1_data/emodnet_dtm2024_saros_crop.tif"
DTM_BOX = ROOT / "docs/review/phase2b_data/emodnet_dtm2024_era5cell_x0.25.tif"

STATUS = "PROVISIONAL REVIEW ANALYSIS (Phase 5-PRE) — not a validated project forecast; results/revised/ unchanged"
NODES = {"W": 26.00, "C": 26.25, "E": 26.50}
LAT = 40.50
BASE_YEARS = list(range(2014, 2025))
PERIODS = {"2014-2024": (2014, 2024), "2015-2024": (2015, 2024), "2008-2017": (2008, 2017),
           "1994-2024": (1994, 2024), "1979-2024": (1979, 2024)}
CRITERIA = {"hourly_U100_correlation_min": 0.99,
            "pooled_gross_cf_abs_rel_diff_max_pct": 1.0,
            "annual_net_yield_abs_rel_diff_max_pct": 1.0}


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S04 = _load("s04", "scripts/04_fit_weibull_aep.py")
S03 = _load("s03", "scripts/03_process_era5.py")
NET, H_YEAR, RATED_KW = S04.NET_FACTOR, S04.H_YEAR, S04.RATED_KW
TO_NET_GWH = NET * H_YEAR / 1000.0           # gross CF -> net GWh/MW/yr


# ------------------------------------------------------------------ inputs
def node_path(lon: float) -> Path:
    return IN_DIR / f"era5_openmeteo_40.50N_{lon:.2f}E_1979_2024.parquet"


def load_node(lon: float) -> pd.DataFrame:
    d = pd.read_parquet(node_path(lon)).astype(float) / 100.0
    d.index = pd.date_range("1979-01-01 00:00", periods=len(d), freq="h", name="time")
    return d


def load_base() -> pd.DataFrame:
    return pd.read_parquet(BASE_PARQUET)


def alpha_of(df: pd.DataFrame) -> float:
    return float(S03.estimate_shear_alpha(df)["alpha_mean"])


def with_hub(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    out = df.copy()
    out["U_hub"] = out["U100"] * (105.0 / 100.0) ** alpha
    return out


def annual(df: pd.DataFrame) -> pd.DataFrame:
    """Production annual table (scripts/04 annual_table) plus mean U100."""
    p = S04.power_from_speed(df["U_hub"].to_numpy().astype(float).copy())
    tab = S04.annual_table(df, p)
    tab["mean_U100_ms"] = df["U100"].groupby(df.index.year).mean()
    return tab


def cf(tab: pd.DataFrame, y0: int, y1: int) -> float:
    return S04.pooled_cf(tab, list(range(y0, y1 + 1)))


def t_interval(tab: pd.DataFrame, years: list[int]) -> dict:
    """Same construction as production (scripts/04 interannual_and_sampling)."""
    t = tab.loc[years]
    n = len(t)
    se = float(t.gross_cf.std(ddof=1) / np.sqrt(n))
    q = float(stats.t.ppf(0.95, n - 1))
    m = float(t.gross_cf.mean())
    pooled = S04.pooled_cf(tab, years)
    return {"net_gwh_per_mw": [(m - q * se) * TO_NET_GWH, (m + q * se) * TO_NET_GWH],
            "half_width_rel_pct": q * se / pooled * 100}


def mean_u100(df: pd.DataFrame, y0: int, y1: int) -> float:
    return float(df.loc[str(y0):str(y1), "U100"].mean())


# -------------------------------------------------------------- calibration
def calibration(base: pd.DataFrame, om_c: pd.DataFrame, alpha_base: float) -> dict:
    om = with_hub(om_c.loc["2014":"2024"], alpha_base)
    j = base.join(om, rsuffix="_om", how="inner")
    out = {"label": "CALIBRATION of the Open-Meteo ERA5 series against the committed CDS-derived baseline, "
                    "node 40.50 N 26.25 E, 2014-2024 (same model, different distribution and storage)",
           "n_hours_matched": int(len(j)), "n_hours_baseline": int(len(base))}
    for v in ("U10", "U100"):
        d = j[f"{v}_om"] - j[v]
        out[v] = {"mean_cds_ms": float(j[v].mean()), "mean_openmeteo_ms": float(j[f"{v}_om"].mean()),
                  "mean_diff_ms": float(d.mean()), "rmse_ms": float(np.sqrt((d ** 2).mean())),
                  "max_abs_diff_ms": float(d.abs().max()),
                  "share_abs_diff_gt_0p1_ms_pct": float((d.abs() > 0.1).mean() * 100),
                  "pearson_r": float(np.corrcoef(j[v], j[f"{v}_om"])[0, 1])}
    t_cds, t_om = annual(base), annual(om)
    rnd = base.copy()
    rnd["U_hub"] = rnd["U100"].round(2) * (105.0 / 100.0) ** alpha_base
    t_rnd = annual(rnd)
    cf_cds, cf_om, cf_rnd = (S04.pooled_cf(t) for t in (t_cds, t_om, t_rnd))
    ann_diff = (t_om.net_gwh_per_mw_8766h / t_cds.net_gwh_per_mw_8766h - 1) * 100
    out["energy"] = {
        "gross_cf_cds": cf_cds, "gross_cf_openmeteo": cf_om,
        "pooled_gross_cf_rel_diff_pct": (cf_om / cf_cds - 1) * 100,
        "net_gwh_per_mw_cds": cf_cds * TO_NET_GWH, "net_gwh_per_mw_openmeteo": cf_om * TO_NET_GWH,
        "rounding_only_rel_diff_pct": (cf_rnd / cf_cds - 1) * 100,
        "rounding_note": "CDS U100 rounded to 0.01 m/s; isolates the effect of two-decimal storage",
        "annual_net_yield_rel_diff_pct": {int(k): float(v) for k, v in ann_diff.items()},
        "annual_net_yield_max_abs_rel_diff_pct": float(ann_diff.abs().max()),
        "annual_net_yield_pearson_r": float(np.corrcoef(t_cds.net_gwh_per_mw_8766h,
                                                        t_om.net_gwh_per_mw_8766h)[0, 1])}
    ok = (out["U100"]["pearson_r"] >= CRITERIA["hourly_U100_correlation_min"]
          and abs(out["energy"]["pooled_gross_cf_rel_diff_pct"]) <= CRITERIA["pooled_gross_cf_abs_rel_diff_max_pct"]
          and out["energy"]["annual_net_yield_max_abs_rel_diff_pct"] <= CRITERIA["annual_net_yield_abs_rel_diff_max_pct"])
    out["criteria"] = CRITERIA
    out["fit_for_ratio_analysis"] = bool(ok)
    out["anchor"] = {"cds_gross_cf_2014_2024": cf_cds, "openmeteo_gross_cf_2014_2024": cf_om,
                     "cds_U100_mean_2014_2024": float(base["U100"].mean()),
                     "openmeteo_U100_mean_2014_2024": float(om["U100"].mean()),
                     "rule": "anchored = CDS value * (Open-Meteo X / Open-Meteo node C 2014-2024)"}
    return out


# ------------------------------------------------------------------ temporal
def temporal(om_c: pd.DataFrame, alpha_base: float, cal: dict, base_tab: pd.DataFrame) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    df = with_hub(om_c, alpha_base)
    tab = annual(df)
    a = cal["anchor"]
    cf_b, u_b = a["openmeteo_gross_cf_2014_2024"], a["openmeteo_U100_mean_2014_2024"]
    ci_base = t_interval(base_tab, BASE_YEARS)["net_gwh_per_mw"]
    periods = {}
    for name, (y0, y1) in PERIODS.items():
        c = cf(tab, y0, y1)
        r_e, r_u = c / cf_b, mean_u100(df, y0, y1) / u_b
        anch = a["cds_gross_cf_2014_2024"] * r_e * TO_NET_GWH
        periods[name] = {"years": y1 - y0 + 1, "mean_U100_ms_openmeteo": mean_u100(df, y0, y1),
                         "mean_U_hub_ms_openmeteo": float(df.loc[str(y0):str(y1), "U_hub"].mean()),
                         "gross_cf_openmeteo": c, "net_cf_openmeteo": c * NET,
                         "net_gwh_per_mw_openmeteo": c * TO_NET_GWH,
                         "ratio_energy_vs_2014_2024": r_e, "ratio_U100_vs_2014_2024": r_u,
                         "energy_change_vs_2014_2024_pct": (r_e - 1) * 100,
                         "U100_change_vs_2014_2024_pct": (r_u - 1) * 100,
                         "anchored_net_gwh_per_mw": anch,
                         "anchored_U100_ms": a["cds_U100_mean_2014_2024"] * r_u,
                         "anchored_inside_baseline_90pct_sampling_ci": bool(ci_base[0] <= anch <= ci_base[1])}

    lt = {k: cf(tab, *PERIODS[k]) * TO_NET_GWH for k in ("1994-2024", "1979-2024")}
    rows = []
    for s in range(1979, 2015):
        yrs = list(range(s, s + 11))
        c = S04.pooled_cf(tab, yrs)
        ti = t_interval(tab, yrs)
        rows.append({"start": s, "end": s + 10, "net_gwh_per_mw_openmeteo": c * TO_NET_GWH,
                     "anchored_net_gwh_per_mw": a["cds_gross_cf_2014_2024"] * c / cf_b * TO_NET_GWH,
                     "rel_to_1994_2024_mean_pct": (c * TO_NET_GWH / lt["1994-2024"] - 1) * 100,
                     "rel_to_1979_2024_mean_pct": (c * TO_NET_GWH / lt["1979-2024"] - 1) * 100,
                     "t90_lo": ti["net_gwh_per_mw"][0], "t90_hi": ti["net_gwh_per_mw"][1],
                     "t90_half_width_rel_pct": ti["half_width_rel_pct"],
                     "ci_contains_1994_2024_mean": ti["net_gwh_per_mw"][0] <= lt["1994-2024"] <= ti["net_gwh_per_mw"][1],
                     "ci_contains_1979_2024_mean": ti["net_gwh_per_mw"][0] <= lt["1979-2024"] <= ti["net_gwh_per_mw"][1],
                     "contains_2014": s <= 2014 <= s + 10})
    roll = pd.DataFrame(rows)

    def roll_summary(sub: pd.DataFrame, ref: str) -> dict:
        b = sub.loc[sub.start == 2014].iloc[0]
        col = "rel_to_1994_2024_mean_pct" if ref == "1994-2024" else "rel_to_1979_2024_mean_pct"
        cic = "ci_contains_1994_2024_mean" if ref == "1994-2024" else "ci_contains_1979_2024_mean"
        return {"n_windows": int(len(sub)), "reference_mean": ref,
                "min_net_gwh_per_mw_openmeteo": float(sub.net_gwh_per_mw_openmeteo.min()),
                "max_net_gwh_per_mw_openmeteo": float(sub.net_gwh_per_mw_openmeteo.max()),
                "min_window": f"{int(sub.loc[sub.net_gwh_per_mw_openmeteo.idxmin(), 'start'])}-"
                              f"{int(sub.loc[sub.net_gwh_per_mw_openmeteo.idxmin(), 'end'])}",
                "max_window": f"{int(sub.loc[sub.net_gwh_per_mw_openmeteo.idxmax(), 'start'])}-"
                              f"{int(sub.loc[sub.net_gwh_per_mw_openmeteo.idxmax(), 'end'])}",
                "window_rel_pct_min": float(sub[col].min()), "window_rel_pct_max": float(sub[col].max()),
                "window_2014_2024_rel_pct": float(b[col]),
                "window_2014_2024_rank_from_lowest": int((sub.net_gwh_per_mw_openmeteo
                                                          <= b.net_gwh_per_mw_openmeteo).sum()),
                "share_windows_ci_contains_reference_mean_pct": float(sub[cic].mean() * 100),
                "t90_half_width_rel_pct_min": float(sub.t90_half_width_rel_pct.min()),
                "t90_half_width_rel_pct_max": float(sub.t90_half_width_rel_pct.max()),
                "note": "overlapping windows share years; they are not independent samples"}

    y = tab.net_gwh_per_mw_8766h

    def year_stats(y0: int, y1: int) -> dict:
        s = y.loc[y0:y1]
        rank = int((s <= s.loc[2014]).sum())
        ex = s.drop(2014)
        lo5 = s.nsmallest(5)
        slope, icpt, r, p, se = stats.linregress(s.index.values, s.values)
        return {"n_years": int(len(s)), "rank_of_2014_from_lowest": rank,
                "years_at_or_below_2014": [int(k) for k in s.index[s <= s.loc[2014]]],
                "empirical_return_period_yr_weibull_plotting": (len(s) + 1) / rank,
                "net_2014_rel_to_period_mean_pct": float((s.loc[2014] / s.mean() - 1) * 100),
                "z_2014_vs_other_years": float((s.loc[2014] - ex.mean()) / ex.std(ddof=1)),
                "five_lowest_years": {int(k): float(v) for k, v in lo5.items()},
                "annual_net_cov_pct": float(s.std(ddof=1) / s.mean() * 100),
                "lag1_autocorrelation": float(np.corrcoef(s.values[:-1], s.values[1:])[0, 1]),
                "linear_trend_pct_per_decade": float(slope * 10 / s.mean() * 100),
                "linear_trend_p_value": float(p),
                "trend_note": "descriptive only: reanalysis trends are affected by changes in the assimilated "
                              "observing system and are not evidence of a climatic trend",
                "t90_of_period_mean": t_interval(tab, list(range(y0, y1 + 1)))}

    res = {"status": STATUS,
           "label": "OBSERVED model years (ERA5 via Open-Meteo, node 40.50 N 26.25 E, baseline alpha); "
                    "additional years are further reanalysis years, not independent observations",
           "alpha_used": alpha_base,
           "alpha_recomputed_1994_2024": alpha_of(om_c.loc["1994":"2024"]),
           "periods": periods,
           "baseline_90pct_sampling_ci_net_gwh_per_mw": ci_base,
           "rolling_11yr": {"within_1994_2024": roll_summary(roll[roll.start >= 1994], "1994-2024"),
                            "within_1979_2024": roll_summary(roll, "1979-2024")},
           "year_2014": {"1994-2024": year_stats(1994, 2024), "1979-2024": year_stats(1979, 2024)}}
    # alpha sensitivity: recomputed long-period alpha instead of the baseline value
    t_alt = annual(with_hub(om_c, res["alpha_recomputed_1994_2024"]))
    res["alpha_sensitivity_1994_2024_energy_pct"] = (cf(t_alt, 1994, 2024) / cf(tab, 1994, 2024) - 1) * 100
    return res, tab, roll


# ----------------------------------------------------------------- geography
def polygon():
    t = KML.read_text(encoding="utf-8")
    p = [tuple(map(float, s.split(",")[:2]))
         for s in re.findall(r"<coordinates>(.*?)</coordinates>", t, re.S)[0].split()]
    return p[:-1] if p[0] == p[-1] else p


def _xy(lon, lat, lon0, lat0):
    kx = np.radians(1) * 6371.0 * np.cos(np.radians(lat0)); ky = np.radians(1) * 6371.0
    return (np.asarray(lon) - lon0) * kx, (np.asarray(lat) - lat0) * ky


def _inside(x, y, poly):
    m = np.zeros(np.shape(x), bool)
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        c = (y1 > y) != (y2 > y)
        m ^= c & (x < (x2 - x1) * (y - y1) / ((y2 - y1) if y2 != y1 else 1e-30) + x1)
    return m


def _dist_edges(x, y, poly):
    a = np.array(poly); b = np.roll(a, -1, axis=0)
    dx, dy = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
    t = np.clip(((x - a[:, 0]) * dx + (y - a[:, 1]) * dy) / (dx * dx + dy * dy), 0, 1)
    return float(np.min(np.hypot(x - (a[:, 0] + t * dx), y - (a[:, 1] + t * dy))))


def raster_at(path: Path, lon: float, lat: float) -> float:
    import rasterio
    with rasterio.open(path) as r:
        row, col = r.index(lon, lat)
        return float(r.read(1)[row, col])


def box_stats(path: Path, lon: float, lat: float, half: float) -> dict:
    import rasterio
    with rasterio.open(path) as r:
        a = r.read(1).astype(float)
        rows, cols = np.indices(a.shape)
        xs, ys = rasterio.transform.xy(r.transform, rows, cols, offset="center")
        x = np.asarray(xs).reshape(a.shape); y = np.asarray(ys).reshape(a.shape)
        b = r.bounds
    m = (np.abs(x - lon) <= half) & (np.abs(y - lat) <= half)
    complete = (lon - half >= b.left - 1e-9 and lon + half <= b.right + 1e-9
                and lat - half >= b.bottom - 1e-9 and lat + half <= b.top + 1e-9)
    return {"values": a[m], "x": x, "y": y, "a": a, "complete": complete}


def gwa_sea_box_mean(lon: float, lat: float, half: float) -> float:
    """GWA 4.0 mean over the 0.25 deg box, sea pixels only (EMODnet elevation < 0 at the pixel centre)."""
    import rasterio
    g = box_stats(GWA_TIF, lon, lat, half)
    m = (np.abs(g["x"] - lon) <= half) & (np.abs(g["y"] - lat) <= half)
    xs, ys, vals = g["x"][m], g["y"][m], g["a"][m]
    with rasterio.open(DTM_BOX) as r:
        z = r.read(1)
        rc = [r.index(x, y) for x, y in zip(xs, ys)]
    sea = np.array([z[i, j] < 0 for i, j in rc])
    return float(np.nanmean(vals[sea]))


def geography() -> dict:
    lsm = json.loads((IN_DIR / "era5_land_sea_mask_saros.json").read_text())
    la = np.array(lsm["latitude"]); lo = np.array(lsm["longitude"]); g = np.array(lsm["land_sea_mask"])
    P = polygon()
    lon0 = sum(p[0] for p in P) / len(P); lat0 = sum(p[1] for p in P) / len(P)
    px, py = _xy([p[0] for p in P], [p[1] for p in P], lon0, lat0)
    poly = list(zip(px, py))
    # dense sample of the polygon (~150 m) for nearest-node shares
    gx, gy = np.meshgrid(np.arange(px.min(), px.max(), 0.15), np.arange(py.min(), py.max(), 0.15))
    ins = _inside(gx, gy, poly)
    sx, sy = gx[ins], gy[ins]
    nxy = {k: _xy(v, LAT, lon0, lat0) for k, v in NODES.items()}
    d = np.stack([np.hypot(sx - nxy[k][0], sy - nxy[k][1]) for k in NODES])
    near = np.argmin(d, axis=0)
    cx, cy = _xy(26.198, 40.557, lon0, lat0)   # centroid used by scripts/03 (config.site)
    out = {}
    for i, (k, lon) in enumerate(NODES.items()):
        f = float(g[np.argmin(np.abs(la - LAT)), np.argmin(np.abs(lo - lon))])
        cls = ("offshore (predominantly sea in ERA5)" if f < 0.2 else
               "coastal / mixed land-sea in ERA5" if f < 0.5 else "land in ERA5")
        bx = box_stats(DTM_BOX, lon, LAT, 0.125)
        land = bx["a"] > 0
        dland = np.hypot(*_xy(bx["x"][land], bx["y"][land], lon, LAT)).min() if land.any() else np.nan
        x, y = nxy[k]
        out[k] = {"lat": LAT, "lon": lon,
                  "era5_land_sea_mask_fraction": f, "classification_from_era5_lsm": cls,
                  "classification_rule": "ERA5 lsm < 0.2 offshore; 0.2-0.5 coastal/mixed; >= 0.5 land",
                  "emodnet_elevation_at_node_m": raster_at(DTM_FINE, lon, LAT),
                  "node_location": "sea" if raster_at(DTM_FINE, lon, LAT) < 0 else "land",
                  "emodnet_land_share_in_0p25deg_box_pct": float((bx["values"] > 0).mean() * 100),
                  "box_complete_in_raster": bool(bx["complete"]),
                  "nearest_land_pixel_km_within_raster": float(dland),
                  "inside_polygon": bool(_inside(np.array([x]), np.array([y]), poly)[0]),
                  "distance_to_polygon_boundary_km": _dist_edges(x, y, poly),
                  "distance_to_polygon_centroid_km": float(np.hypot(x - cx, y - cy)),
                  "polygon_share_nearest_to_node_pct": float((near == i).mean() * 100),
                  "gwa4_100m_at_node_pixel_ms": raster_at(GWA_TIF, lon, LAT),
                  "gwa4_100m_mean_0p25deg_box_ms": float(np.nanmean(box_stats(GWA_TIF, lon, LAT, 0.125)["values"])),
                  "gwa4_100m_mean_0p25deg_box_sea_only_ms": gwa_sea_box_mean(lon, LAT, 0.125)}
    out["_note"] = ("ERA5 lsm is the model's fractional land cover of the grid cell; at ~31 km native resolution it "
                    "smears land over coastal sea points. EMODnet elevation describes the node location itself. "
                    "Nearest-land distance is searched only within the EMODnet crop (25.875-26.625 E, "
                    "40.125-40.875 N).")
    return out


# ------------------------------------------------------------------ spatial
def spatial(nodes: dict[str, pd.DataFrame], alpha_base: float, cal: dict, geo: dict, base_tab: pd.DataFrame) -> dict:
    ci = t_interval(base_tab, BASE_YEARS)
    half = ci["half_width_rel_pct"]
    rows, tabs = {}, {}
    for k, df in nodes.items():
        d = df.loc["2014":"2024"]
        a_node = alpha_of(d)
        h = with_hub(d, a_node)
        tab = annual(h)
        tab_b = annual(with_hub(d, alpha_base))
        tabs[k] = tab
        u = h["U_hub"].to_numpy()
        c = S04.pooled_cf(tab)
        rows[k] = {"lon": NODES[k], "alpha_node_2014_2024": a_node,
                   "mean_U10_ms": float(d.U10.mean()), "mean_U100_ms": float(d.U100.mean()),
                   "mean_U_hub_ms": float(u.mean()), "p10_U_hub_ms": float(np.percentile(u, 10)),
                   "median_U_hub_ms": float(np.median(u)), "p90_U_hub_ms": float(np.percentile(u, 90)),
                   "power_density_U_hub_wm2_rho1225": float(0.5 * 1.225 * np.mean(u ** 3)),
                   "gross_cf": c, "net_cf": c * NET, "net_gwh_per_mw": c * TO_NET_GWH,
                   "net_gwh_per_mw_with_baseline_alpha": S04.pooled_cf(tab_b) * TO_NET_GWH,
                   "annual_net_cov_pct": float(tab.net_cf.std(ddof=1) / tab.net_cf.mean() * 100),
                   "ratio_1994_2024_to_2014_2024_energy": cf(annual(with_hub(df, a_node)), 1994, 2024) / c}
    c0 = rows["C"]["gross_cf"]
    a = cal["anchor"]
    for k in rows:
        r = rows[k]["gross_cf"] / c0
        diff = (r - 1) * 100
        paired = (tabs[k].net_gwh_per_mw_8766h / tabs["C"].net_gwh_per_mw_8766h - 1) * 100
        rows[k].update({"energy_rel_to_node_C_pct": diff,
                        "abs_diff_over_baseline_ci_half_width": abs(diff) / half,
                        "U100_rel_to_node_C_pct": (rows[k]["mean_U100_ms"] / rows["C"]["mean_U100_ms"] - 1) * 100,
                        "anchored_net_gwh_per_mw": a["cds_gross_cf_2014_2024"] * rows[k]["gross_cf"]
                                                   / a["openmeteo_gross_cf_2014_2024"] * TO_NET_GWH,
                        "paired_annual_rel_diff_vs_C_pct": {"mean": float(paired.mean()), "sd": float(paired.std(ddof=1)),
                                                            "min": float(paired.min()), "max": float(paired.max())},
                        "annual_correlation_with_C": float(np.corrcoef(tabs[k].net_gwh_per_mw_8766h,
                                                                       tabs["C"].net_gwh_per_mw_8766h)[0, 1])})
    w = {k: geo[k]["polygon_share_nearest_to_node_pct"] / 100 for k in NODES}
    interp = sum(w[k] * rows[k]["gross_cf"] for k in NODES)
    return {"status": STATUS,
            "label": "OBSERVED model output at three ERA5 nodes, 2014-2024, identical assumptions "
                     "(each node with its own alpha by the documented method)",
            "baseline_90pct_sampling_ci_half_width_rel_pct": half,
            "nodes": rows,
            "node_spread_energy_pct": {"min": min(r["energy_rel_to_node_C_pct"] for r in rows.values()),
                                       "max": max(r["energy_rel_to_node_C_pct"] for r in rows.values())},
            "interpolation_polygon_share_weighted": {
                "label": "INTERPOLATION of model output (not validation, not adopted): nearest-node polygon shares as "
                         "weights; mixes cells with ERA5 land fraction 0.12-0.46",
                "weights": w, "net_gwh_per_mw_openmeteo": interp * TO_NET_GWH,
                "rel_to_node_C_pct": (interp / c0 - 1) * 100,
                "anchored_net_gwh_per_mw": a["cds_gross_cf_2014_2024"] * interp / a["openmeteo_gross_cf_2014_2024"] * TO_NET_GWH}}


# --------------------------------------------------------------- GWA period
def gwa_period(base: pd.DataFrame, temp: dict, sp: dict, geo: dict, nodes: dict[str, pd.DataFrame]) -> dict:
    sens = json.loads((REVISED / "wind_speed_sensitivity.json").read_text())
    gwa = sens["gwa_reference"]["gwa4_polygon_mean_100m_ms"]
    u_base = float(base["U100"].mean())
    r_total = gwa / u_base
    r_p = temp["periods"]["2008-2017"]["ratio_U100_vs_2014_2024"]
    u_pm = u_base * r_p
    r_after = gwa / u_pm
    # AEP effect of scaling the CDS baseline hours to the period-matched GWA ratio (sensitivity, as in scripts/04)
    u = base["U_hub"].to_numpy().astype(float)
    cf0 = S04.power_from_speed(u.copy()).mean() / RATED_KW

    def aep(f):
        return float(S04.power_from_speed(u * f).mean() / RATED_KW / cf0 - 1) * 100

    per_node = {}
    for k in NODES:
        u_now = mean_u100(nodes[k], 2014, 2024)
        u_gwa = mean_u100(nodes[k], 2008, 2017)
        box, sea = geo[k]["gwa4_100m_mean_0p25deg_box_ms"], geo[k]["gwa4_100m_mean_0p25deg_box_sea_only_ms"]
        per_node[k] = {"era5_lsm": geo[k]["era5_land_sea_mask_fraction"],
                       "era5_U100_2014_2024_openmeteo_ms": u_now,
                       "era5_U100_2008_2017_openmeteo_ms": u_gwa,
                       "era5_period_ratio_2008_2017_over_2014_2024": u_gwa / u_now,
                       "gwa4_node_pixel_ms": geo[k]["gwa4_100m_at_node_pixel_ms"],
                       "gwa4_0p25deg_box_mean_ms": box,
                       "gwa4_0p25deg_box_sea_only_mean_ms": sea,
                       "ratio_gwa_box_to_era5_2014_2024": box / u_now,
                       "ratio_gwa_box_to_era5_period_matched": box / u_gwa,
                       "ratio_gwa_box_sea_only_to_era5_period_matched": sea / u_gwa}
    return {"status": STATUS,
            "label": "MODEL DISAGREEMENT decomposition (GWA 4.0 is ERA5-driven WRF/WAsP, 2008-2017; neither is "
                     "validated offshore here; GWA is not ground truth)",
            "gwa4_polygon_mean_100m_ms": gwa, "era5_U100_2014_2024_cds_ms": u_base,
            "ratio_gwa_to_era5_2014_2024": r_total,
            "era5_period_ratio_2008_2017_over_2014_2024": r_p,
            "era5_U100_2008_2017_anchored_ms": u_pm,
            "ratio_gwa_to_era5_period_matched": r_after,
            "share_of_log_disagreement_explained_by_period_pct": float(np.log(r_p) / np.log(r_total) * 100),
            "aep_change_if_scaled_to_gwa_unmatched_pct": aep(r_total),
            "aep_change_if_scaled_to_gwa_period_matched_pct": aep(r_after),
            "per_node_gwa_box_vs_era5": per_node,
            "note": "Positive share means ERA5 2008-2017 was windier than 2014-2024 and so explains part of the gap; "
                    "a negative share means the period mismatch widens it. Per-node ratios use each node's own "
                    "Open-Meteo ERA5 means (calibrated at node C to -0.001 % in mean U100). A GWA/ERA5 ratio is "
                    "inter-model disagreement, not a bias estimate."}


# ----------------------------------------------------------------- driver
def compute() -> dict:
    base = load_base()
    alpha_base = alpha_of(base)
    nodes = {k: load_node(v) for k, v in NODES.items()}
    base_tab = annual(base)
    cal = calibration(base, nodes["C"], alpha_base)
    temp, tab_c, roll = temporal(nodes["C"], alpha_base, cal, base_tab)
    geo = geography()
    sp = spatial(nodes, alpha_base, cal, geo, base_tab)
    gp = gwa_period(base, temp, sp, geo, nodes)
    rev = json.loads((REVISED / "energy_yield.json").read_text())
    cal["baseline_check"] = {"net_gwh_per_mw_recomputed": S04.pooled_cf(base_tab) * TO_NET_GWH,
                             "net_gwh_per_mw_results_revised": rev["net"]["gwh_per_mw"],
                             "alpha_baseline": alpha_base}
    cal["status"] = STATUS
    tab_c = tab_c.copy()
    tab_c.insert(0, "node", "40.50N_26.25E_openmeteo")
    return {"calibration.json": cal, "temporal.json": temp, "spatial.json": sp,
            "node_geography.json": {"status": STATUS, **geo}, "gwa_period.json": gp,
            "annual_energy_1979_2024.csv": tab_c, "rolling_11yr.csv": roll}


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def write(res: dict, out: Path = OUT) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    man = {"status": STATUS, "generated_by": "scripts/phase5pre_era5_robustness.py",
           "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [BASE_PARQUET, *sorted(IN_DIR.glob("*.parquet")),
                                IN_DIR / "era5_land_sea_mask_saros.json"]},
           "files": {}}
    for name, obj in res.items():
        p = out / name
        if name.endswith(".csv"):
            obj.to_csv(p, index=name.startswith("annual"), float_format="%.10g")
        else:
            p.write_text(json.dumps(_clean(obj), indent=2, allow_nan=False) + "\n")
        man["files"][name] = hashlib.sha256(p.read_bytes()).hexdigest()
    (out / "MANIFEST.json").write_text(json.dumps(man, indent=2) + "\n")
    return man


def main() -> int:
    res = compute()
    write(res)
    c, t, s, g = (res[k] for k in ("calibration.json", "temporal.json", "spatial.json", "gwa_period.json"))
    print("calibration fit_for_ratio_analysis:", c["fit_for_ratio_analysis"],
          f"dCF={c['energy']['pooled_gross_cf_rel_diff_pct']:+.3f}%")
    for k, v in t["periods"].items():
        print(f"  {k}: anchored {v['anchored_net_gwh_per_mw']:.3f} GWh/MW ({v['energy_change_vs_2014_2024_pct']:+.2f}%)")
    for k, v in s["nodes"].items():
        print(f"  node {k}: {v['energy_rel_to_node_C_pct']:+.2f}% vs C")
    print(f"  GWA period share: {g['share_of_log_disagreement_explained_by_period_pct']:.1f}%")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
