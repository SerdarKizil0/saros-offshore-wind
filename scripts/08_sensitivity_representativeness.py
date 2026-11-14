"""
08 — Sensitivity and representativeness experiments (revised production pipeline)
==================================================================================
Added in Phase 5B-0. Promotes the Phase 5-PRE evidence into the authoritative
results, recomputed against the PRIMARY baseline (ERA5 1994-2024, node
40.50 N 26.25 E, Open-Meteo-delivered, calibrated; scripts/04).

Runs after scripts/04 and reads results/revised/{energy_yield,
interannual_and_sampling, loss_scenarios, wind_speed_sensitivity}.json for
the reference values, which it verifies against its own recomputation.

Writes (results/revised/):
  period_sensitivity.json        PERIOD-SELECTION sensitivity: other reference periods and
                                 rolling 11-year windows at the primary node
  rolling_11yr_windows.csv       every 11-year window 1979-2024 (full series, ranks)
  node_sensitivity.json          GRID-NODE sensitivity: the three ERA5 nodes on the 40.50 N row,
                                 1994-2024, identical method; coordinates, land-sea mask, data period
  wind_product_discrepancy.json  ERA5 vs Global Wind Atlas 4.0 with the actual periods of each
                                 product; inter-model disagreement, not validation, not a correction
  sensitivity_index.json         the six categories, their type and files; NOT combinable

The six categories are kept separate and are NOT components of one calibrated
probabilistic uncertainty interval:
  1 sampling uncertainty of the period mean (the only probabilistic interval);
  2 observed interannual variability;
  3 period-selection sensitivity;
  4 grid-node sensitivity;
  5 wind-product discrepancy;
  6 loss-assumption sensitivity.

Nothing here changes, rescales or averages the primary estimate. Neighbouring
nodes are model output, not measurements, and are neither averaged nor used
as bounds. GWA is not ground truth.

Method (identical to scripts/04): U_hub = U100 * (105/100)**alpha, alpha =
trimmed mean of the hourly ERA5 10 m/100 m exponent (scripts/03); empirical
hourly conversion with the active OEDB V164/9500 curve; nominal losses;
CF = sum P / (P_r * hours); net GWh/MW/yr = CF_net * 8.766.
  * Period experiments at the primary node use the PRIMARY alpha for all
    years, so that only the wind changes.
  * Node experiments use each node's own alpha from its 1994-2024 series (the
    documented method); the primary-alpha variant is also reported.

Usage:  python scripts/08_sensitivity_representativeness.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from scipy import stats

from config.site import RESULTS_DIR
from config.wind_data import (PRIMARY, NODE_SERIES, PRIMARY_NODE, ERA5_LAND_SEA_MASK, GWA4_WIND_SPEED_100M,
                              EMODNET_NODE_BOX, WindSeries)

REV = RESULTS_DIR / "revised"
STATUS = "PRE-SUBMISSION MODEL ESTIMATE — not a validated project forecast"
WINDOW_YEARS = 11
COMPARISON_PERIODS = [
    ("1994-2024", "reference: primary period of the authoritative estimate"),
    ("1979-2024", "longest record retrieved for this node"),
    ("2014-2024", "period of the historical baseline (comparison only)"),
    ("2015-2024", "most recent ten years (comparison only)"),
    ("2008-2017", "reference period of the Global Wind Atlas 4.0 climatology (comparison only)"),
]
GWA_PERIOD = (2008, 2017)
LSM_RULE = "ERA5 land-sea mask < 0.2 offshore; 0.2-0.5 coastal/mixed; >= 0.5 land"
NOT_COMBINABLE = ("The categories are different kinds of quantity. They are NOT components of a single calibrated "
                  "probabilistic uncertainty interval and must not be added, root-sum-squared or merged.")


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


S04 = _load("s04_for_08", "scripts/04_fit_weibull_aep.py")
P4A = _load("p4a_for_08", "scripts/phase4a_site_checks.py")
NET, H_YEAR, RATED_KW = S04.NET_FACTOR, S04.H_YEAR, S04.RATED_KW
TO_NET = NET * H_YEAR / 1000.0                 # gross CF -> net GWh/MW/yr


# ------------------------------------------------------------------ inputs
def _verified(path: Path, sha: str) -> Path:
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != sha:
        raise ValueError(f"{path}: sha256 {got} does not match the pin in config/wind_data.py")
    return path


def load_node(spec: WindSeries) -> pd.DataFrame:
    """Hourly U10, U100 (m/s) of one sensitivity node, complete hourly axis verified."""
    st = pd.read_parquet(_verified(spec.path, spec.sha256))
    y0, y1 = spec.period
    full = pd.date_range(f"{y0}-01-01 00:00", f"{y1}-12-31 23:00", freq="h", name="time")
    if len(st) != len(full) or list(st.columns) != ["U10", "U100"] or st.isna().any().any():
        raise ValueError(f"{spec.rel_path}: unexpected shape or missing values")
    return pd.DataFrame({"U10": st["U10"].to_numpy() / 100.0, "U100": st["U100"].to_numpy() / 100.0}, index=full)


def alpha_of(df: pd.DataFrame) -> float:
    return float(S04._s03().estimate_shear_alpha(df)["alpha_mean"])


def with_hub(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    out = df.copy()
    out["U_hub"] = out["U100"] * (S04.TURBINE.hub_height_m / 100.0) ** alpha
    return out


def annual(df: pd.DataFrame) -> pd.DataFrame:
    return S04.annual_table(df, S04.power_from_speed(df["U_hub"].to_numpy().astype(float).copy()))


def cf(tab: pd.DataFrame, y0: int, y1: int) -> float:
    return S04.pooled_cf(tab, list(range(y0, y1 + 1)))


def t90_half_width_rel_pct(tab: pd.DataFrame, y0: int, y1: int) -> float:
    t = tab.loc[y0:y1]
    n = len(t)
    return float(stats.t.ppf(0.95, n - 1) * t.gross_cf.std(ddof=1) / np.sqrt(n) / cf(tab, y0, y1) * 100)


def _span(label: str) -> tuple[int, int]:
    a, b = label.split("-")
    return int(a), int(b)


# ------------------------------------------------------------ reference
def reference() -> dict:
    """Primary values as written by scripts/04, cross-checked against a recomputation here."""
    ey = json.loads((REV / "energy_yield.json").read_text())
    s = json.loads((REV / "interannual_and_sampling.json").read_text())["sampling_ci_of_period_mean"]
    df, info = S04.load_series(PRIMARY)
    tab = annual(df)
    cfp = S04.pooled_cf(tab)
    if ey["input"]["series_key"] != PRIMARY.key or abs(cfp / ey["gross_cf"] - 1) > 1e-12:
        raise ValueError("results/revised/energy_yield.json is not the current primary estimate; run scripts/04")
    if s["period"] != PRIMARY.period_label:
        raise ValueError("sampling interval period differs from the primary period")
    return {"df": df, "tab": tab, "alpha": info["alpha_hub_extrapolation"], "gross_cf": cfp,
            "net_gwh_per_mw": cfp * TO_NET, "U100_mean": float(df["U100"].mean()),
            "ci_half_width_rel_pct": s["primary_t_interval_90"]["half_width_rel_pct"],
            "ci_net_gwh_per_mw": s["primary_t_interval_90"]["net_gwh_per_mw"],
            "meta": {"series_key": PRIMARY.key, "file": PRIMARY.rel_path, "sha256": PRIMARY.sha256,
                     "period": PRIMARY.period_label, "node_lat_lon": [PRIMARY.node_lat, PRIMARY.node_lon],
                     "net_gwh_per_mw": ey["net"]["gwh_per_mw"], "net_cf": ey["net_cf"], "gross_cf": ey["gross_cf"],
                     "source_file": "results/revised/energy_yield.json"}}


def _scale_note() -> str:
    return ("|change| divided by the half-width of the 90 % sampling interval of the reference mean; given for scale "
            "only. It is not a significance test and does not turn this sensitivity into a confidence bound.")


# ------------------------------------------------------- 3 period selection
def period_sensitivity(ref: dict, node_c: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    y0p, y1p = PRIMARY.period
    same = (np.array_equal(node_c.loc[str(y0p):str(y1p), "U100"].to_numpy(), ref["df"]["U100"].to_numpy())
            and np.array_equal(node_c.loc[str(y0p):str(y1p), "U10"].to_numpy(), ref["df"]["U10"].to_numpy()))
    if not same:
        raise ValueError("sensitivity node C series differs from the primary series over the primary period")
    spec = NODE_SERIES[PRIMARY_NODE]
    df = with_hub(node_c, ref["alpha"])
    tab = annual(df)
    periods = {}
    for label, role in COMPARISON_PERIODS:
        a, b = _span(label)
        c = cf(tab, a, b)
        u100 = float(df.loc[str(a):str(b), "U100"].mean())
        d_e = (c / ref["gross_cf"] - 1) * 100
        periods[label] = {"role": role, "n_years": b - a + 1, "mean_U100_ms": u100,
                          "mean_U_hub_ms": float(df.loc[str(a):str(b), "U_hub"].mean()),
                          "gross_cf": c, "net_cf": c * NET, "net_gwh_per_mw": c * TO_NET,
                          "energy_change_vs_reference_pct": d_e,
                          "U100_change_vs_reference_pct": (u100 / ref["U100_mean"] - 1) * 100,
                          "abs_change_over_reference_ci_half_width": abs(d_e) / ref["ci_half_width_rel_pct"]}
    if abs(periods[PRIMARY.period_label]["energy_change_vs_reference_pct"]) > 1e-9:
        raise ValueError("reference period does not reproduce the primary estimate")

    first, last = spec.period[0], spec.period[1] - WINDOW_YEARS + 1
    rows = []
    for s in range(first, last + 1):
        e = s + WINDOW_YEARS - 1
        c = cf(tab, s, e)
        rows.append({"start_year": s, "end_year": e, "n_years": WINDOW_YEARS, "gross_cf": c,
                     "net_gwh_per_mw": c * TO_NET,
                     "rel_to_primary_mean_pct": (c / ref["gross_cf"] - 1) * 100,
                     "t90_half_width_rel_pct": t90_half_width_rel_pct(tab, s, e),
                     "within_primary_period": bool(s >= y0p and e <= y1p)})
    roll = pd.DataFrame(rows)
    inp = roll.within_primary_period
    roll["rank_from_lowest_within_primary_period"] = roll.net_gwh_per_mw.where(inp).rank(method="min").astype("Int64")
    roll["rank_from_lowest_all_windows"] = roll.net_gwh_per_mw.rank(method="min").astype("Int64")

    def summary(sub: pd.DataFrame, rank_col: str, span: str) -> dict:
        lo, hi = sub.loc[sub.net_gwh_per_mw.idxmin()], sub.loc[sub.net_gwh_per_mw.idxmax()]
        base = sub.loc[sub.start_year == 2014].iloc[0]
        return {"window_start_years": span, "n_windows": int(len(sub)),
                "lowest_window": f"{int(lo.start_year)}-{int(lo.end_year)}",
                "lowest_window_rel_to_primary_mean_pct": float(lo.rel_to_primary_mean_pct),
                "highest_window": f"{int(hi.start_year)}-{int(hi.end_year)}",
                "highest_window_rel_to_primary_mean_pct": float(hi.rel_to_primary_mean_pct),
                "window_2014_2024_rank_from_lowest": int(base[rank_col]),
                "window_2014_2024_is_highest": bool(int(base[rank_col]) == len(sub)),
                "window_2014_2024_rel_to_primary_mean_pct": float(base.rel_to_primary_mean_pct),
                "t90_half_width_rel_pct_range": [float(sub.t90_half_width_rel_pct.min()),
                                                 float(sub.t90_half_width_rel_pct.max())]}

    out = {
        "status": STATUS,
        "label": "PERIOD-SELECTION SENSITIVITY — same node, same method, other reference periods; a sensitivity "
                 "experiment, not an uncertainty interval. Further years are further reanalysis years, not "
                 "independent observations.",
        "category": "period_selection_sensitivity",
        "reference_baseline": ref["meta"],
        "assumptions": {
            "node_lat_lon": [spec.node_lat, spec.node_lon],
            "series": {"file": spec.rel_path, "sha256": spec.sha256, "data_period": spec.period_label,
                       "data_product": spec.data_product,
                       "identical_to_primary_series_over_primary_period": True},
            "alpha": ref["alpha"], "alpha_note": "primary-series alpha applied to every year, so only the wind changes",
            "estimator": "empirical hourly conversion, OEDB V164/9500, nominal losses, CF x 8766 h (scripts/04)",
            "window_length_years": WINDOW_YEARS},
        "periods": periods,
        "rolling_windows": {
            "file": "results/revised/rolling_11yr_windows.csv",
            "within_primary_period": summary(roll[inp], "rank_from_lowest_within_primary_period",
                                             f"{y0p}-{y1p - WINDOW_YEARS + 1}"),
            "all_windows": summary(roll, "rank_from_lowest_all_windows", f"{first}-{last}"),
            "note": "overlapping windows share years and are not independent samples; t90 half-widths are the "
                    "sampling intervals of each window's own mean (category 1 applied per window)"},
        "scale_note": _scale_note(),
        "homogeneity_note": "differences between periods may partly reflect changes in the observing system "
                            "assimilated by ERA5; they are not evidence of a climatic trend",
    }
    return out, roll


# ------------------------------------------------------------- 4 grid node
def _lsm() -> dict:
    return json.loads(_verified(*ERA5_LAND_SEA_MASK).read_text())


def lsm_fraction(lsm: dict, lat: float, lon: float) -> float:
    la, lo = np.array(lsm["latitude"]), np.array(lsm["longitude"])
    i, k = int(np.argmin(np.abs(la - lat))), int(np.argmin(np.abs(lo - lon)))
    if abs(la[i] - lat) > 1e-6 or abs(lo[k] - lon) > 1e-6:
        raise ValueError("node is not on the land-sea mask grid")
    return float(np.array(lsm["land_sea_mask"])[i, k])


def classify(f: float) -> str:
    return ("offshore (predominantly sea in ERA5)" if f < 0.2 else
            "coastal / mixed land-sea in ERA5" if f < 0.5 else "land in ERA5")


def node_geometry() -> dict:
    """Geographical relation of each node to the official polygon (descriptive; never used as weights)."""
    gx, gy = np.meshgrid(np.arange(26.03, 26.47, 0.001), np.arange(40.50, 40.60, 0.001))
    m = P4A.inside(gx, gy, P4A.P)
    out = {}
    for k, s in NODE_SERIES.items():
        x, y = P4A.to_xy([s.node_lon], [s.node_lat])
        near = (np.round(gx[m] * 4) / 4 == s.node_lon) & (np.round(gy[m] * 4) / 4 == s.node_lat)
        out[k] = {"inside_polygon": bool(P4A.inside(np.array([s.node_lon]), np.array([s.node_lat]), P4A.P)[0]),
                  "distance_to_polygon_boundary_km": float(P4A.dist_to_edges(x, y, P4A.PXY)[0]),
                  "polygon_share_nearest_to_node_pct": float(near.mean() * 100)}
    return out


def node_sensitivity(ref: dict, nodes: dict[str, pd.DataFrame]) -> dict:
    y0, y1 = PRIMARY.period
    lsm, geo = _lsm(), node_geometry()
    rows, tabs = {}, {}
    for k, spec in NODE_SERIES.items():
        d = nodes[k].loc[str(y0):str(y1)]
        a = alpha_of(d)
        h = with_hub(d, a)
        tab = annual(h)
        tabs[k] = tab
        c = S04.pooled_cf(tab)
        u = h["U_hub"].to_numpy()
        f = lsm_fraction(lsm, spec.node_lat, spec.node_lon)
        rows[k] = {
            "lat": spec.node_lat, "lon": spec.node_lon, "is_primary_node": k == PRIMARY_NODE,
            "file": spec.rel_path, "sha256": spec.sha256, "data_product": spec.data_product,
            "data_period_in_file": spec.period_label, "data_period_used": f"{y0}-01-01 00:00 to {y1}-12-31 23:00 UTC",
            "n_hours_used": int(len(d)),
            "era5_land_sea_mask_fraction": f, "classification_from_era5_land_sea_mask": classify(f),
            **geo[k],
            "alpha_node": a, "mean_U10_ms": float(d["U10"].mean()), "mean_U100_ms": float(d["U100"].mean()),
            "mean_U_hub_ms": float(u.mean()),
            "U_hub_hourly_speed_percentiles_ms": {"10th": float(np.percentile(u, 10)), "50th": float(np.median(u)),
                                                  "90th": float(np.percentile(u, 90))},
            "power_density_U_hub_wm2_rho1225": float(0.5 * S04.RHO_AIR * np.mean(u ** 3)),
            "gross_cf": c, "net_cf": c * NET, "net_gwh_per_mw": c * TO_NET,
            "net_gwh_per_mw_with_primary_alpha": S04.pooled_cf(annual(with_hub(d, ref["alpha"]))) * TO_NET,
            "annual_net_cov_pct": float(tab.net_cf.std(ddof=1) / tab.net_cf.mean() * 100),
        }
    if abs(rows[PRIMARY_NODE]["gross_cf"] / ref["gross_cf"] - 1) > 1e-12:
        raise ValueError("node C does not reproduce the primary estimate")
    base = rows[PRIMARY_NODE]
    for k, r in rows.items():
        d_e = (r["gross_cf"] / base["gross_cf"] - 1) * 100
        paired = (tabs[k].net_gwh_per_mw_8766h / tabs[PRIMARY_NODE].net_gwh_per_mw_8766h - 1) * 100
        r.update({
            "energy_rel_to_primary_node_pct": d_e,
            "U100_rel_to_primary_node_pct": (r["mean_U100_ms"] / base["mean_U100_ms"] - 1) * 100,
            "abs_diff_over_reference_ci_half_width": abs(d_e) / ref["ci_half_width_rel_pct"],
            "paired_annual_rel_diff_vs_primary_node_pct": {
                "n_years": int(len(paired)), "mean": float(paired.mean()),
                "sd": float(paired.std(ddof=1)) if k != PRIMARY_NODE else 0.0,
                "min": float(paired.min()), "max": float(paired.max())},
            "annual_correlation_with_primary_node": float(np.corrcoef(tabs[k].net_gwh_per_mw_8766h,
                                                                      tabs[PRIMARY_NODE].net_gwh_per_mw_8766h)[0, 1])})
    others = [r["energy_rel_to_primary_node_pct"] for k, r in rows.items() if k != PRIMARY_NODE]
    return {
        "status": STATUS,
        "label": "GRID-NODE SENSITIVITY EXPERIMENT — reanalysis output at the primary node and its two neighbours "
                 "on the 40.50 N row, identical method and period. Model output, not measurements; the nodes are "
                 "not averaged and their differences are not confidence bounds.",
        "category": "grid_node_sensitivity",
        "reference_baseline": ref["meta"],
        "assumptions": {
            "period": PRIMARY.period_label,
            "alpha": "each node's own trimmed-mean exponent from its 1994-2024 series (documented method); the "
                     "primary-alpha variant is reported per node",
            "estimator": "empirical hourly conversion, OEDB V164/9500, nominal losses, CF x 8766 h (scripts/04)",
            "land_sea_mask": {"file": str(ERA5_LAND_SEA_MASK[0].relative_to(ROOT)), "sha256": ERA5_LAND_SEA_MASK[1],
                              "source": lsm["source"], "classification_rule": LSM_RULE},
            "polygon_share_note": "share of the official polygon nearest to each node: a geometric descriptor, "
                                  "never used as a weight"},
        "nodes": rows,
        "neighbour_difference_range_pct": {"lowest": min(others), "highest": max(others)},
        "interpretation_limits": [
            "no node lies inside the polygon",
            "the three values are not combined into an average or an interpolated estimate",
            "the range is the result of two specific neighbouring cells, not a bound on the true resource",
            "node differences persist every year (see the paired annual statistics), so they are systematic "
            "model differences and are not reduced by a longer record"],
        "scale_note": _scale_note(),
    }


# ---------------------------------------------------- 5 wind-product discrepancy
def _raster(path_sha) -> tuple:
    import rasterio
    with rasterio.open(_verified(*path_sha)) as r:
        a = r.read(1).astype(float)
        rr, cc = np.indices(a.shape)
        xs, ys = rasterio.transform.xy(r.transform, rr, cc, offset="center")
        return a, np.asarray(xs).reshape(a.shape), np.asarray(ys).reshape(a.shape), r.transform


def gwa_node_statistics() -> dict:
    """GWA 4.0 100 m mean speed at each node pixel and over the 0.25 deg box centred on the node."""
    import rasterio
    g, gx, gy, gt = _raster(GWA4_WIND_SPEED_100M)
    z, _zx, _zy, zt = _raster(EMODNET_NODE_BOX)
    out = {}
    for k, s in NODE_SERIES.items():
        m = (np.abs(gx - s.node_lon) <= 0.125) & (np.abs(gy - s.node_lat) <= 0.125)
        rows, cols = rasterio.transform.rowcol(zt, gx[m], gy[m])
        sea = z[np.asarray(rows), np.asarray(cols)] < 0
        r0, c0 = rasterio.transform.rowcol(gt, s.node_lon, s.node_lat)
        out[k] = {"node_pixel_ms": float(g[r0, c0]), "box_0p25deg_mean_ms": float(np.nanmean(g[m])),
                  "box_0p25deg_sea_pixels_mean_ms": float(np.nanmean(g[m][sea])),
                  "box_sea_pixel_share_pct": float(sea.mean() * 100)}
    return out


def wind_product_discrepancy(ref: dict, nodes: dict[str, pd.DataFrame]) -> dict:
    gwa_poly = S04.gwa_polygon_mean()
    if gwa_poly is None:
        raise RuntimeError("GWA raster or polygon not available")
    y0, y1 = PRIMARY.period
    g0, g1 = GWA_PERIOD
    gstat = gwa_node_statistics()
    u = ref["df"]["U_hub"].to_numpy().astype(float)

    def aep_if_scaled(f: float) -> float:
        return float(S04.power_from_speed(u * f).mean() / RATED_KW / ref["gross_cf"] - 1) * 100

    per_node = {}
    for k, s in NODE_SERIES.items():
        u_prim = float(nodes[k].loc[str(y0):str(y1), "U100"].mean())
        u_gwa = float(nodes[k].loc[str(g0):str(g1), "U100"].mean())
        per_node[k] = {
            "lat": s.node_lat, "lon": s.node_lon,
            "era5_U100_ms": {PRIMARY.period_label: u_prim, f"{g0}-{g1}": u_gwa},
            "gwa4_100m_ms": gstat[k],
            "ratio_gwa_box_to_era5": {
                "era5_" + PRIMARY.period_label: gstat[k]["box_0p25deg_mean_ms"] / u_prim,
                f"era5_{g0}-{g1}_period_matched": gstat[k]["box_0p25deg_mean_ms"] / u_gwa},
            "ratio_gwa_box_sea_pixels_to_era5_period_matched": gstat[k]["box_0p25deg_sea_pixels_mean_ms"] / u_gwa}
    c = per_node[PRIMARY_NODE]["era5_U100_ms"]
    r_prim, r_match = gwa_poly / c[PRIMARY.period_label], gwa_poly / c[f"{g0}-{g1}"]
    ws = json.loads((REV / "wind_speed_sensitivity.json").read_text())
    gwa_case = next(x for x in ws["cases"] if "GWA" in x["case"])
    if abs(gwa_case["speed_factor"] / r_prim - 1) > 1e-12:
        raise ValueError("GWA ratio differs from results/revised/wind_speed_sensitivity.json")
    order = lambda key: [k for k, _ in sorted(((k, key(k)) for k in NODE_SERIES), key=lambda t: -t[1])]
    return {
        "status": STATUS,
        "label": "WIND-PRODUCT DISCREPANCY (ERA5 vs Global Wind Atlas 4.0) — disagreement between two models. "
                 "Neither is validated against offshore measurements here, GWA is not ground truth, and the ratio "
                 "is not a bias estimate, a correction or a confidence interval. The primary estimate is not "
                 "rescaled.",
        "category": "wind_product_discrepancy",
        "reference_baseline": ref["meta"],
        "products": {
            "era5": {"description": "ERA5 hourly 100 m wind speed, Open-Meteo-delivered (calibrated; not "
                                    "bit-identical to CDS); provenance in results/revised/input_provenance.json",
                     "node_lat_lon": [PRIMARY.node_lat, PRIMARY.node_lon],
                     "height_m": 100, "quantity": "mean of hourly 100 m wind speed",
                     "periods_used": [PRIMARY.period_label, f"{g0}-{g1}"]},
            "gwa4": {"description": "Global Wind Atlas 4.0, mean wind speed at 100 m: ERA5-forced WRF (3 km) with "
                                    "WAsP microscale downscaling, about 250 m grid; not independent of ERA5",
                     "period": f"{g0}-{g1}", "height_m": 100,
                     "file": str(GWA4_WIND_SPEED_100M[0].relative_to(ROOT)), "sha256": GWA4_WIND_SPEED_100M[1],
                     "polygon_mean_ms": gwa_poly,
                     "polygon_mean_definition": "mean of the pixel centres inside the official candidate polygon"}},
        "polygon_vs_primary_node": {
            "gwa4_polygon_mean_100m_ms": gwa_poly,
            "era5_node_U100_ms": c,
            "ratio_gwa_to_era5": {
                "era5_" + PRIMARY.period_label: r_prim,
                f"era5_{g0}-{g1}_period_matched": r_match},
            "era5_period_ratio_gwa_period_over_primary": c[f"{g0}-{g1}"] / c[PRIMARY.period_label],
            "period_matching_effect": "widens the ratio" if r_match > r_prim else "narrows the ratio",
            "note": f"the unmatched ratio compares a {g0}-{g1} climatology with the {PRIMARY.period_label} ERA5 "
                    "mean; the period-matched ratio removes the period difference but not the difference in "
                    "spatial support (polygon mean vs one 0.25 deg cell)"},
        "per_node_gwa_box_vs_era5": per_node,
        "spatial_pattern": {
            "era5_order_by_U100": order(lambda k: per_node[k]["era5_U100_ms"][PRIMARY.period_label]),
            "gwa4_order_by_box_mean": order(lambda k: gstat[k]["box_0p25deg_mean_ms"]),
            "note": "the two products do not agree on the spatial ordering of the three cells"},
        "energy_sensitivity_if_primary_hours_were_scaled": {
            "label": "SENSITIVITY EXPERIMENT, illustrative: every primary hourly speed multiplied by the ratio; "
                     "power curve and nominal losses fixed. Not adopted and not a correction.",
            "by_ratio_era5_" + PRIMARY.period_label: {"speed_factor": r_prim,
                                                       "aep_change_vs_primary_pct": aep_if_scaled(r_prim)},
            f"by_ratio_era5_{g0}-{g1}_period_matched": {"speed_factor": r_match,
                                                        "aep_change_vs_primary_pct": aep_if_scaled(r_match)},
            "generic_speed_factors_file": "results/revised/wind_speed_sensitivity.json"},
    }


# --------------------------------------------------------------- index
def sensitivity_index(ref: dict, per: dict, node: dict, wpd: dict) -> dict:
    s = json.loads((REV / "interannual_and_sampling.json").read_text())
    ls = json.loads((REV / "loss_scenarios.json").read_text())["scenarios"]
    v, ci = s["observed_interannual_variability"], s["sampling_ci_of_period_mean"]
    rw = per["rolling_windows"]["within_primary_period"]
    pvn = wpd["polygon_vs_primary_node"]["ratio_gwa_to_era5"]
    esc = wpd["energy_sensitivity_if_primary_hours_were_scaled"]
    key_p, key_m = "era5_" + PRIMARY.period_label, f"era5_{GWA_PERIOD[0]}-{GWA_PERIOD[1]}_period_matched"
    nb = {k: r["energy_rel_to_primary_node_pct"] for k, r in node["nodes"].items() if not r["is_primary_node"]}
    cats = [
        {"n": 1, "category": "sampling_uncertainty_of_period_mean", "kind": "probabilistic interval",
         "is_probabilistic_interval": True, "file": "results/revised/interannual_and_sampling.json",
         "headline": {"t90_net_gwh_per_mw": ci["primary_t_interval_90"]["net_gwh_per_mw"],
                      "half_width_rel_pct": ci["primary_t_interval_90"]["half_width_rel_pct"],
                      "n_annual_values": ci["n_years"]},
         "meaning": "finite-sample uncertainty of the 1994-2024 mean, conditional on ERA5 at this node being correct"},
        {"n": 2, "category": "interannual_variability", "kind": "observed spread of single years",
         "is_probabilistic_interval": False, "file": "results/revised/interannual_and_sampling.json",
         "headline": {"annual_net_cov_pct": v["annual_net_cf_cov_pct"],
                      "lowest_year": [v["min_year"], v["min_net_gwh_per_mw"]],
                      "highest_year": [v["max_year"], v["max_net_gwh_per_mw"]]},
         "meaning": "year-to-year variation of the model years; not an uncertainty of the mean"},
        {"n": 3, "category": "period_selection_sensitivity", "kind": "sensitivity experiment",
         "is_probabilistic_interval": False, "file": "results/revised/period_sensitivity.json",
         "headline": {"energy_change_vs_reference_pct": {k: p["energy_change_vs_reference_pct"]
                                                         for k, p in per["periods"].items()
                                                         if k != PRIMARY.period_label},
                      "rolling_11yr_within_primary_period_rel_pct": [rw["lowest_window_rel_to_primary_mean_pct"],
                                                                     rw["highest_window_rel_to_primary_mean_pct"]],
                      "window_2014_2024_rank_from_lowest": [rw["window_2014_2024_rank_from_lowest"],
                                                            rw["n_windows"]]},
         "meaning": "effect of choosing another reference period at the same node"},
        {"n": 4, "category": "grid_node_sensitivity", "kind": "sensitivity experiment",
         "is_probabilistic_interval": False, "file": "results/revised/node_sensitivity.json",
         "headline": {"energy_rel_to_primary_node_pct": nb,
                      "era5_land_sea_mask_fraction": {k: r["era5_land_sea_mask_fraction"]
                                                      for k, r in node["nodes"].items()}},
         "meaning": "effect of using a neighbouring reanalysis cell; not averaged, not a bound"},
        {"n": 5, "category": "wind_product_discrepancy", "kind": "inter-model disagreement",
         "is_probabilistic_interval": False, "file": "results/revised/wind_product_discrepancy.json",
         "supporting_file": "results/revised/wind_speed_sensitivity.json",
         "headline": {"ratio_gwa_polygon_to_era5_node": {key_p: pvn[key_p], key_m: pvn[key_m]},
                      "aep_change_if_scaled_pct_illustrative": {
                          key_p: esc["by_ratio_" + key_p]["aep_change_vs_primary_pct"],
                          key_m: esc["by_ratio_" + key_m]["aep_change_vs_primary_pct"]}},
         "meaning": "disagreement between ERA5 and GWA 4.0; not validation and not a correction"},
        {"n": 6, "category": "loss_assumption_sensitivity", "kind": "labelled assumption scenarios",
         "is_probabilistic_interval": False, "file": "results/revised/loss_scenarios.json",
         "headline": {"rel_to_nominal_pct": {k: x["rel_to_nominal_pct"] for k, x in ls.items()},
                      "net_gwh_per_mw": {k: x["net_gwh_per_mw"] for k, x in ls.items()}},
         "meaning": "effect of the assumed wake, availability and electrical losses; no site evidence"},
    ]
    return {"status": STATUS,
            "label": "INDEX of uncertainty and sensitivity categories of the primary estimate. " + NOT_COMBINABLE,
            "combinable_into_one_interval": False,
            "reference_baseline": ref["meta"],
            "categories": cats,
            "not_quantified": ["absolute accuracy of ERA5 at this site (no offshore measurements)",
                               "wind gradient inside the polygon", "power-curve digitisation and air density",
                               "hourly versus 10-minute averaging", "layout-specific wake losses",
                               "representativeness of 1994-2024 for future operation"]}


# ----------------------------------------------------------------- driver
def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    return o


def compute() -> dict:
    ref = reference()
    nodes = {k: load_node(s) for k, s in NODE_SERIES.items()}
    per, roll = period_sensitivity(ref, nodes[PRIMARY_NODE])
    node = node_sensitivity(ref, nodes)
    wpd = wind_product_discrepancy(ref, nodes)
    return {"period_sensitivity.json": per, "rolling_11yr_windows.csv": roll, "node_sensitivity.json": node,
            "wind_product_discrepancy.json": wpd,
            "sensitivity_index.json": sensitivity_index(ref, per, node, wpd)}


def write(res: dict, out: Path = REV) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, obj in res.items():
        if name.endswith(".csv"):
            obj.to_csv(out / name, index=False, float_format="%.10g")
        else:
            (out / name).write_text(json.dumps(_clean(obj), indent=2, ensure_ascii=False, allow_nan=False))


def main() -> int:
    if not (REV / "energy_yield.json").exists():
        print("✗ results/revised/energy_yield.json missing — run scripts/04_fit_weibull_aep.py first")
        return 1
    res = compute()
    write(res)
    per, node, wpd = (res[k] for k in ("period_sensitivity.json", "node_sensitivity.json",
                                       "wind_product_discrepancy.json"))
    for k, p in per["periods"].items():
        print(f"  period {k}: {p['net_gwh_per_mw']:.4f} GWh/MW/yr ({p['energy_change_vs_reference_pct']:+.2f}%)")
    rw = per["rolling_windows"]["within_primary_period"]
    print(f"  2014-2024 window rank {rw['window_2014_2024_rank_from_lowest']} of {rw['n_windows']} (1994-2024)")
    for k, r in node["nodes"].items():
        print(f"  node {k} ({r['lon']:.2f}E, lsm {r['era5_land_sea_mask_fraction']:.2f}): "
              f"{r['net_gwh_per_mw']:.4f} GWh/MW/yr ({r['energy_rel_to_primary_node_pct']:+.2f}%)")
    r = wpd["polygon_vs_primary_node"]["ratio_gwa_to_era5"]
    print("  GWA/ERA5: " + ", ".join(f"{k} {v:.4f}" for k, v in r.items()))
    print(f"✓ wrote sensitivity outputs to {REV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
