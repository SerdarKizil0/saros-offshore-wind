"""
04 — Wind resource and energy assessment (revised production pipeline)
=======================================================================
Authoritative energy step since Phase 4B; primary input changed in Phase
5-PRE-B (14.11.2026) by author decision.

Input (config/wind_data.py, pinned by SHA-256)
  * PRIMARY: ERA5 1994-2024, node 40.50 N 26.25 E, via the Open-Meteo
    historical API (calibrated against the CDS series; not bit-identical to
    CDS): data/external/era5_openmeteo/*.parquet.
  * HISTORICAL_CDS_2014_2024: the original CDS-derived series
    (data/processed/wind_hub_105m.parquet). Used only with
    --series historical_cds_2014_2024 to reproduce the archive
    the results archive folder baseline_2014_2024_cds, and for the input calibration
    check. Never mixed with the primary.

Method (unchanged)
  * Hub height: U_hub = U100 * (105/100)**alpha, alpha = trimmed mean of the
    hourly ERA5 10 m/100 m exponent of the series itself
    (scripts/03 estimate_shear_alpha). For the historical CDS series the
    stored U_hub (same method) is used.
  * Primary estimator: empirical hourly power conversion through the active
    OEDB V164/9500 curve (config.turbine.POWER_CURVE_MS_KW).
    CF = sum(P_h) / (P_rated * N_hours); AEP = CF * P_rated * 8766 h.
  * Weibull (MLE, location 0): descriptive statistic and AEP cross-check only.
  * Uncertainty, kept separate:
      - observed year-to-year variability (calendar years of the period);
      - sampling uncertainty of the period mean (t-interval from the annual
        values, primary; year-block bootstrap and jackknife as checks);
      - loss scenarios (labelled assumptions, config.turbine.LOSS_SCENARIOS);
      - wind-speed sensitivity experiments (+/-5 %, +/-10 %, and one case
        scaled to the Global Wind Atlas 4.0 polygon mean). Not probabilities
        and not corrections.

Outputs (results/revised/; pre-submission model estimates, not validated
project forecasts):
  wind_resource.json, energy_yield.json, weibull_crosscheck.json,
  interannual_and_sampling.json, annual_energy.csv, loss_scenarios.json,
  wind_speed_sensitivity.json, input_provenance.json

`power_from_speed`, `fit_weibull`, `annual_table`, `pooled_cf` keep their
historical names and behaviour, because other scripts and tests import them.

Usage:
  python scripts/04_fit_weibull_aep.py                       # primary -> results/revised/
  python scripts/04_fit_weibull_aep.py --series historical_cds_2014_2024 --out DIR
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import gamma

from config.site import RESULTS_DIR, PROJECT_ROOT
from config.wind_data import PRIMARY, HISTORICAL_CDS_2014_2024, SERIES, WindSeries
from config.turbine import (TURBINE, POWER_CURVE_ID, POWER_CURVE_MS_KW, LOSS_SCENARIOS,
                            WAKE_LOSS_DEFAULT, AVAILABILITY_DEFAULT, ELECTRICAL_LOSS_DEFAULT)

OUT = RESULTS_DIR / "revised"
GWA_RASTER = PROJECT_ROOT / "docs/review/phase2b_data/gwa4_wind-speed_100m_saros.tif"
KML = PROJECT_ROOT / "docs/review/phase1_data/SAROS_DURES_official.kml"

STATUS = "PRE-SUBMISSION MODEL ESTIMATE — not a validated project forecast"
RHO_AIR = 1.225                 # kg/m3, standard density (power-density statistic only)
H_YEAR = 8766.0                 # average year incl. leap days (365.25 d)
RATED_KW = TURBINE.rated_power_mw * 1000.0
SEED = 2026
N_BOOT = 20000
SPEED_FACTORS = [0.90, 0.95, 1.00, 1.05, 1.10]
SECTORS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def net_factor(wake, avail, elec):
    return (1 - wake) * avail * (1 - elec)


NET_FACTOR = net_factor(WAKE_LOSS_DEFAULT, AVAILABILITY_DEFAULT, ELECTRICAL_LOSS_DEFAULT)


# ------------------------------------------------------------------ input
def _s03():
    spec = importlib.util.spec_from_file_location("s03_shear", PROJECT_ROOT / "scripts/03_process_era5.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_series(spec: WindSeries = PRIMARY) -> tuple[pd.DataFrame, dict]:
    """Load a pinned wind series; return the hourly frame (U10, U100, U_hub, wdir) and its provenance."""
    raw = spec.path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != spec.sha256:
        raise ValueError(f"{spec.rel_path}: sha256 {sha} does not match the pin in config/wind_data.py")
    y0, y1 = spec.period
    full = pd.date_range(f"{y0}-01-01 00:00", f"{y1}-12-31 23:00", freq="h", name="time")
    shear = _s03().estimate_shear_alpha
    if spec.storage == "openmeteo_int16":
        st = pd.read_parquet(spec.path)
        if len(st) != len(full):
            raise ValueError(f"{spec.rel_path}: {len(st)} rows, expected {len(full)} for {spec.period_label}")
        df = pd.DataFrame({"U10": st["U10"].to_numpy() / 100.0, "U100": st["U100"].to_numpy() / 100.0,
                           "wdir": st["wdir100"].to_numpy().astype(float) % 360.0}, index=full)
        alpha = float(shear(df)["alpha_mean"])
        df["U_hub"] = df["U100"] * (TURBINE.hub_height_m / 100.0) ** alpha
        df = df[["U10", "U100", "U_hub", "wdir"]]
        alpha_note = "computed from this series (scripts/03 estimate_shear_alpha) and applied to every hour"
    elif spec.storage == "cds_processed_float32":
        df = pd.read_parquet(spec.path)
        if not df.index.equals(full):
            raise ValueError(f"{spec.rel_path}: time axis is not the complete hourly range {spec.period_label}")
        alpha = float(shear(df)["alpha_mean"])
        alpha_note = "U_hub as stored (scripts/03, same method); alpha recomputed here for reporting"
    else:
        raise ValueError(f"unknown storage {spec.storage}")
    if df.isna().any().any():
        raise ValueError(f"{spec.rel_path}: missing values")
    info = {"series_key": spec.key, "file": spec.rel_path, "sha256": sha, "data_product": spec.data_product,
            "node_lat_lon": [spec.node_lat, spec.node_lon], "period": spec.period_label,
            "n_years": spec.n_years, "n_hours": int(len(df)),
            "first_hour_utc": str(df.index[0]), "last_hour_utc": str(df.index[-1]),
            "alpha_hub_extrapolation": alpha, "alpha_note": alpha_note}
    return df, info


# ----------------------------------------------------------- historical API
def power_from_speed(u: np.ndarray) -> np.ndarray:
    """Interpolate the active power curve at each wind speed (kW)."""
    pc_ms = [p[0] for p in POWER_CURVE_MS_KW]
    pc_kw = [p[1] for p in POWER_CURVE_MS_KW]
    power = np.interp(u, pc_ms, pc_kw, left=0, right=0)
    power[u < TURBINE.cut_in_ms] = 0.0
    power[u >= TURBINE.cut_out_ms] = 0.0
    return power


def fit_weibull(u: np.ndarray) -> dict:
    """Weibull MLE (floc=0) with a Justus empirical-formula cross-check (descriptive)."""
    u_pos = u[u > 0]
    k_mle, _loc, c_mle = stats.weibull_min.fit(u_pos, floc=0)
    mean_u, std_u = u.mean(), u.std()
    k_emp = (std_u / mean_u) ** (-1.086)
    c_emp = mean_u / gamma(1 + 1 / k_emp)
    ks_stat, ks_p = stats.kstest(u_pos, lambda x: stats.weibull_min.cdf(x, k_mle, 0, c_mle))
    srt = np.sort(u_pos)
    emp_cdf = np.arange(1, len(srt) + 1) / len(srt)
    th_cdf = stats.weibull_min.cdf(srt, k_mle, 0, c_mle)
    r2 = 1 - np.sum((emp_cdf - th_cdf) ** 2) / np.sum((emp_cdf - emp_cdf.mean()) ** 2)
    return {
        "k_mle": float(k_mle), "c_mle_ms": float(c_mle),
        "k_justus_empirical": float(k_emp), "c_justus_empirical_ms": float(c_emp),
        "ks_statistic": float(ks_stat), "ks_pvalue": float(ks_p),
        "ks_note": "hourly data are autocorrelated; the KS p-value is not a valid test here",
        "r2_cdf": float(r2),
        "weibull_mean_ms": float(c_mle * gamma(1 + 1 / k_mle)),
        "weibull_power_density_wm2": float(0.5 * RHO_AIR * c_mle ** 3 * gamma(1 + 3 / k_mle)),
        "n_hours": int(len(u)),
    }


# -------------------------------------------------------------- components
def wind_resource(df: pd.DataFrame, p_kw: np.ndarray, spec: WindSeries = HISTORICAL_CDS_2014_2024) -> dict:
    u = df["U_hub"].to_numpy().astype(float)
    u100 = df["U100"].to_numpy().astype(float)
    m = (df["U10"] > 1.0) & (df["U100"] > 1.0)
    a = np.log(df.loc[m, "U100"].to_numpy() / df.loc[m, "U10"].to_numpy()) / np.log(10.0)
    lo, hi = np.percentile(a, [1, 99]); a = a[(a >= lo) & (a <= hi)]
    ann = df["U_hub"].groupby(df.index.year).mean()
    mon = df["U_hub"].groupby(df.index.month).mean()
    sect = ((df["wdir"].to_numpy() + 11.25) // 22.5).astype(int) % 16
    return {
        "status": STATUS,
        "data": {"source": spec.source_label, "file": spec.rel_path,
                 "period": f"{spec.period[0]}-01-01 to {spec.period[1]}-12-31 UTC",
                 "n_hours": int(len(df)), "type": "reanalysis model output, not observations"},
        "hub_height_m": TURBINE.hub_height_m,
        "U_hub": {"mean_ms": float(u.mean()), "std_ms": float(u.std(ddof=1)), "median_ms": float(np.median(u)),
                  "p10_ms": float(np.percentile(u, 10)), "p90_ms": float(np.percentile(u, 90)),
                  "power_density_wm2_rho1225": float(0.5 * RHO_AIR * np.mean(u ** 3))},
        "U100": {"mean_ms": float(u100.mean()),
                 "power_density_wm2_rho1225": float(0.5 * RHO_AIR * np.mean(u100 ** 3))},
        "shear_exponent_from_era5_10m_100m": {
            "mean": float(a.mean()), "median": float(np.median(a)), "std": float(a.std()),
            "p5": float(np.percentile(a, 5)), "p95": float(np.percentile(a, 95)),
            "note": "derived from reanalysis levels, not measured; 100->105 m effect "
                    f"{((1.05 ** a.mean()) / (1.05 ** 0.10) - 1) * 100:+.2f} % vs alpha=0.10"},
        "monthly_mean_U_hub_ms": {int(k): float(v) for k, v in mon.items()},
        "annual_mean_U_hub_ms": {int(k): float(v) for k, v in ann.items()},
        "annual_mean_cov_pct": {"ddof1": float(ann.std(ddof=1) / ann.mean() * 100),
                                "ddof0": float(ann.std(ddof=0) / ann.mean() * 100),
                                "lowest_year": int(ann.idxmin()),
                                "ddof1_excluding_lowest_year": float(ann.drop(ann.idxmin()).std(ddof=1)
                                                                     / ann.drop(ann.idxmin()).mean() * 100)},
        "direction_share_pct": {
            "hours": dict(zip(SECTORS, map(float, np.bincount(sect, minlength=16) / len(sect) * 100))),
            "energy": dict(zip(SECTORS, map(float, np.bincount(sect, weights=p_kw, minlength=16) / p_kw.sum() * 100)))},
    }


def annual_table(df: pd.DataFrame, p_kw: np.ndarray) -> pd.DataFrame:
    t = pd.DataFrame({"p": p_kw}, index=df.index)
    g = t.groupby(t.index.year)["p"]
    tab = pd.DataFrame({"hours": g.size(), "gross_kwh": g.sum()})
    tab.index.name = "year"
    tab["leap"] = [pd.Timestamp(year=y, month=1, day=1).is_leap_year for y in tab.index]
    tab["mean_U_hub_ms"] = df["U_hub"].groupby(df.index.year).mean()
    tab["gross_cf"] = tab.gross_kwh / (RATED_KW * tab.hours)
    tab["net_cf"] = tab.gross_cf * NET_FACTOR
    tab["net_gwh_per_mw_8766h"] = tab.net_cf * H_YEAR / 1000.0
    return tab


def pooled_cf(tab: pd.DataFrame, years=None) -> float:
    t = tab if years is None else tab.loc[years]
    return float(t.gross_kwh.sum() / (RATED_KW * t.hours.sum()))


def energy_from_cf(cf: float) -> dict:
    """CF (fraction) -> energy for an average 8766 h year."""
    return {"gwh_per_turbine": cf * RATED_KW * H_YEAR / 1e6, "gwh_per_mw": cf * H_YEAR / 1000.0}


def energy_yield(tab: pd.DataFrame, p_kw: np.ndarray, info: dict | None = None) -> dict:
    cf = pooled_cf(tab)
    out = {
        "status": STATUS,
        "estimator": "empirical hourly power conversion (primary)",
        "power_curve": POWER_CURVE_ID, "turbine": f"{TURBINE.manufacturer} {TURBINE.model}",
        "hours_per_average_year": H_YEAR,
        "net_factor_nominal": NET_FACTOR,
        "losses_nominal": {"wake": WAKE_LOSS_DEFAULT, "availability": AVAILABILITY_DEFAULT,
                           "electrical": ELECTRICAL_LOSS_DEFAULT},
        "gross_cf": cf, "net_cf": cf * NET_FACTOR,
        "gross": energy_from_cf(cf), "net": energy_from_cf(cf * NET_FACTOR),
        "net_mwh_per_mw_yr": cf * NET_FACTOR * H_YEAR,
        "net_full_load_hours": cf * NET_FACTOR * H_YEAR,
        "units": {"cf": "fraction", "gwh_per_turbine": "GWh per 9.5 MW turbine per year",
                  "gwh_per_mw": "GWh per MW installed per year"},
        "normalisation_check": {
            "n_hours": int(tab.hours.sum()), "n_years": int(len(tab)),
            "leap_years": [int(y) for y in tab.index[tab.leap]],
            "sum_over_n_years_gross_gwh_per_turbine": float(p_kw.sum() / len(tab) / 1e6),
            "relative_difference_vs_8766h": float((p_kw.sum() / len(tab) / 1e6)
                                                  / energy_from_cf(cf)["gwh_per_turbine"] - 1)},
    }
    if info is not None:
        out["period"] = info["period"]
        out["input"] = {k: info[k] for k in ("series_key", "file", "sha256", "node_lat_lon",
                                             "alpha_hub_extrapolation")}
        if info["series_key"] == PRIMARY.key:
            out["input"]["provenance"] = "results/revised/input_provenance.json"
    return out


def interannual_and_sampling(tab: pd.DataFrame, spec: WindSeries = HISTORICAL_CDS_2014_2024) -> dict:
    cf = pooled_cf(tab)
    n = len(tab)
    ann = tab.net_cf
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(N_BOOT, n))
    kwh, hrs = tab.gross_kwh.to_numpy(), tab.hours.to_numpy()
    boot = kwh[idx].sum(1) / (RATED_KW * hrs[idx].sum(1))
    se = float(tab.gross_cf.std(ddof=1) / np.sqrt(n))
    tq = float(stats.t.ppf(0.95, n - 1))
    mean_years = float(tab.gross_cf.mean())
    t_lo, t_hi = mean_years - tq * se, mean_years + tq * se
    jk = np.array([pooled_cf(tab, [y for y in tab.index if y != d]) for d in tab.index])
    to_net = NET_FACTOR * H_YEAR / 1000.0
    return {
        "status": STATUS,
        "observed_interannual_variability": {
            "label": "OBSERVED year-to-year variability of single calendar years (ERA5); not an uncertainty interval",
            "period": spec.period_label, "n_years": int(n),
            "annual_net_cf_cov_pct": float(ann.std(ddof=1) / ann.mean() * 100),
            "annual_net_cf_cov_pct_excluding_min_year": float(ann.drop(ann.idxmin()).std(ddof=1)
                                                              / ann.drop(ann.idxmin()).mean() * 100),
            "min_year": int(ann.idxmin()), "min_net_gwh_per_mw": float(tab.net_gwh_per_mw_8766h.min()),
            "max_year": int(ann.idxmax()), "max_net_gwh_per_mw": float(tab.net_gwh_per_mw_8766h.max()),
            "lag1_autocorrelation": float(np.corrcoef(ann.values[:-1], ann.values[1:])[0, 1]),
        },
        "sampling_ci_of_period_mean": {
            "label": f"SAMPLING confidence interval of the {spec.period_label} mean only "
                     f"({n} annual values; finite number of years); assumes ERA5 is correct; not a P90 and not "
                     "total uncertainty; excludes node sensitivity and ERA5-GWA disagreement",
            "period": spec.period_label, "n_years": int(n), "t_quantile_df": int(n - 1),
            "primary_t_interval_90": {"gross_cf": [t_lo, t_hi],
                                      "net_gwh_per_mw": [t_lo * to_net, t_hi * to_net],
                                      "half_width_rel_pct": float((t_hi - t_lo) / 2 / cf * 100)},
            "check_bootstrap_90": {"method": f"year-block bootstrap, B={N_BOOT}, seed={SEED}",
                                   "net_gwh_per_mw": [float(np.percentile(boot, 5)) * to_net,
                                                      float(np.percentile(boot, 95)) * to_net]},
            "se_rel_pct": {"classical": se / cf * 100, "bootstrap": float(boot.std(ddof=1)) / cf * 100,
                           "jackknife": float(np.sqrt((n - 1) / n * np.sum((jk - jk.mean()) ** 2))) / cf * 100},
            "jackknife_mean_change_pct": {int(y): float((v / cf - 1) * 100) for y, v in zip(tab.index, jk)},
        },
    }


def weibull_crosscheck(u: np.ndarray, w: dict, cf_emp: float) -> dict:
    v = np.arange(0, 30, 0.1)
    pcurve = np.interp(v, [p[0] for p in POWER_CURVE_MS_KW], [p[1] for p in POWER_CURVE_MS_KW], left=0, right=0)
    pcurve[v >= TURBINE.cut_out_ms] = 0.0
    pdf = stats.weibull_min.pdf(v, w["k_mle"], 0, w["c_mle_ms"])
    trap = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    cf_w = float(trap(pcurve * pdf, v) / RATED_KW)
    p_emp = power_from_speed(u.copy())
    bins = []
    for lo, hi in ((0, 3), (3, 7), (7, 8), (8, 12), (12, 17), (17, 30)):
        sel = (v >= lo - 1e-9) & (v <= hi + 1e-9)
        bins.append({"bin_ms": f"{lo}-{hi}",
                     "gross_cf_contrib_empirical_pctpt": float(p_emp[(u >= lo) & (u < hi)].sum() / (RATED_KW * u.size) * 100),
                     "gross_cf_contrib_weibull_pctpt": float(trap(pcurve[sel] * pdf[sel], v[sel]) / RATED_KW * 100)})
    return {"status": STATUS, "role": "descriptive fit and AEP cross-check only; not the energy estimator",
            "weibull_fit_U_hub": w, "gross_cf_weibull": cf_w, "gross_cf_empirical": cf_emp,
            "relative_difference_pct": (cf_w / cf_emp - 1) * 100,
            "net_gwh_per_mw_weibull_nominal_losses": cf_w * NET_FACTOR * H_YEAR / 1000.0,
            "bin_contributions": bins}


def loss_scenarios(cf: float) -> dict:
    out = {"status": STATUS,
           "label": "LOSS SCENARIOS — labelled assumptions, not probability bounds; one wake value for all "
                    "deployment scenarios is a simplification", "scenarios": {}}
    for name, (w, a, e) in LOSS_SCENARIOS.items():
        nf = net_factor(w, a, e)
        out["scenarios"][name] = {"wake": w, "availability": a, "electrical": e, "net_factor": nf,
                                  "net_cf": cf * nf, "net_gwh_per_mw": cf * nf * H_YEAR / 1000.0,
                                  "rel_to_nominal_pct": (nf / NET_FACTOR - 1) * 100}
    return out


def gwa_polygon_mean() -> float | None:
    """Mean GWA 4.0 100 m wind speed over the official polygon (pixel centres)."""
    try:
        import rasterio
    except ImportError:
        return None
    if not (GWA_RASTER.exists() and KML.exists()):
        return None
    t = KML.read_text(encoding="utf-8")
    ring = [tuple(map(float, s.split(",")[:2]))
            for s in re.findall(r"<coordinates>(.*?)</coordinates>", t, re.S)[0].split()][:-1]
    ds = rasterio.open(GWA_RASTER)
    a = ds.read(1).astype(float)
    r, c = np.indices(a.shape)
    xs, ys = rasterio.transform.xy(ds.transform, r, c, offset="center")
    x, y = np.asarray(xs).reshape(a.shape), np.asarray(ys).reshape(a.shape)
    m = np.zeros(a.shape, bool)
    for i in range(len(ring)):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % len(ring)]
        cnd = (y1 > y) != (y2 > y)
        m ^= cnd & (x < (x2 - x1) * (y - y1) / ((y2 - y1) if y2 != y1 else 1e-30) + x1)
    return float(np.nanmean(a[m]))


def wind_speed_sensitivity(u: np.ndarray, u100_mean: float, gwa_mean: float | None,
                           spec: WindSeries = HISTORICAL_CDS_2014_2024) -> dict:
    cases = [(("baseline ERA5" if f == 1.0 else f"{(f - 1) * 100:+.0f}%"), f) for f in SPEED_FACTORS]
    if gwa_mean is not None:
        cases.append(("scaled to GWA 4.0 polygon mean at 100 m (illustrative)", gwa_mean / u100_mean))
    if spec.key == HISTORICAL_CDS_2014_2024.key:
        note = ("GWA 4.0 is ERA5-driven WRF/WAsP for 2008-2017; the difference is "
                "inter-model disagreement, not a demonstrated ERA5 bias")
    else:
        note = (f"GWA 4.0 is ERA5-driven WRF/WAsP for 2008-2017, ERA5 here is {spec.period_label}; the difference "
                "is inter-model disagreement, not a demonstrated ERA5 bias; matching the periods does not reduce "
                "it (Phase 5-PRE); the GWA case is a sensitivity experiment, not a correction")
    rows, base = [], None
    for name, f in cases:
        pk = power_from_speed(u * f)
        cf = float(pk.mean() / RATED_KW)
        row = {"case": name, "speed_factor": f, "gross_cf": cf, "net_cf": cf * NET_FACTOR,
               "gross_gwh_per_turbine": energy_from_cf(cf)["gwh_per_turbine"],
               "net_gwh_per_turbine": energy_from_cf(cf * NET_FACTOR)["gwh_per_turbine"],
               "net_gwh_per_mw": energy_from_cf(cf * NET_FACTOR)["gwh_per_mw"]}
        if f == 1.0:
            base = row
        rows.append(row)
    for row in rows:
        row["aep_change_vs_baseline_pct"] = (row["gross_cf"] / base["gross_cf"] - 1) * 100
    return {"status": STATUS,
            "label": "SENSITIVITY EXPERIMENTS — all hourly speeds scaled; curve and nominal losses fixed; "
                     "not bias corrections, forecasts or confidence intervals",
            "gwa_reference": {"gwa4_polygon_mean_100m_ms": gwa_mean, "era5_U100_mean_ms": u100_mean,
                              "note": note},
            "cases": rows}


def input_calibration(df: pd.DataFrame) -> dict:
    """INPUT QA: the primary (Open-Meteo) series against the CDS series over their common years."""
    hist, _ = load_series(HISTORICAL_CDS_2014_2024)
    j = hist.join(df, rsuffix="_p", how="inner")
    out = {"label": "INPUT QA (not a result): primary Open-Meteo ERA5 against the CDS-derived series over the "
                    "common hours; both are ERA5, distributed and stored differently",
           "common_period": f"{j.index[0].year}-{j.index[-1].year}", "n_hours": int(len(j))}
    for v in ("U10", "U100"):
        d = j[f"{v}_p"] - j[v]
        out[v] = {"mean_diff_ms": float(d.mean()), "rmse_ms": float(np.sqrt((d ** 2).mean())),
                  "pearson_r": float(np.corrcoef(j[v], j[f"{v}_p"])[0, 1]),
                  "share_abs_diff_gt_0p1_ms_pct": float((d.abs() > 0.1).mean() * 100)}
    dd = ((j["wdir_p"] - j["wdir"] + 180.0) % 360.0) - 180.0
    sect = lambda x: ((np.asarray(x) + 11.25) // 22.5).astype(int) % 16
    sh_c = np.bincount(sect(j["wdir"]), minlength=16) / len(j) * 100
    sh_p = np.bincount(sect(j["wdir_p"]), minlength=16) / len(j) * 100
    out["direction_100m"] = {"mean_abs_diff_deg": float(dd.abs().mean()),
                             "share_abs_diff_gt_2deg_pct": float((dd.abs() > 2).mean() * 100),
                             "max_sector_share_diff_pctpt": float(np.abs(sh_p - sh_c).max()),
                             "note": "Open-Meteo direction is in whole degrees"}
    a_hist = (hist["U_hub"] / hist["U100"]).median()
    cf_h = power_from_speed(j["U_hub"].to_numpy().astype(float).copy()).mean()
    cf_same = power_from_speed((j["U100_p"] * a_hist).to_numpy().copy()).mean()
    cf_own = power_from_speed(j["U_hub_p"].to_numpy().copy()).mean()
    out["gross_cf"] = {"rel_diff_same_alpha_pct": float((cf_same / cf_h - 1) * 100),
                       "rel_diff_own_alpha_pct": float((cf_own / cf_h - 1) * 100),
                       "note": "same alpha isolates the data difference; own alpha includes the series-specific "
                               "shear exponent"}
    return out


def compute(df: pd.DataFrame, spec: WindSeries = HISTORICAL_CDS_2014_2024, info: dict | None = None) -> dict:
    u = df["U_hub"].to_numpy().astype(float)
    p_kw = power_from_speed(u.copy())
    tab = annual_table(df, p_kw)
    ey = energy_yield(tab, p_kw, info)
    res = {
        "wind_resource.json": wind_resource(df, p_kw, spec),
        "energy_yield.json": ey,
        "weibull_crosscheck.json": weibull_crosscheck(u, fit_weibull(u), ey["gross_cf"]),
        "interannual_and_sampling.json": interannual_and_sampling(tab, spec),
        "loss_scenarios.json": loss_scenarios(ey["gross_cf"]),
        "wind_speed_sensitivity.json": wind_speed_sensitivity(u, float(df["U100"].mean()), gwa_polygon_mean(),
                                                              spec),
        "_annual_table": tab,
    }
    if info is not None and spec.key == PRIMARY.key:
        res["input_provenance.json"] = {
            "status": STATUS, "primary_input": info,
            "comparison_input_not_used_for_results": {
                "series_key": HISTORICAL_CDS_2014_2024.key, "file": HISTORICAL_CDS_2014_2024.rel_path,
                "sha256": HISTORICAL_CDS_2014_2024.sha256,
                "role": "historical baseline (results archive folder baseline_2014_2024_cds) and input QA only"},
            "calibration_vs_cds": input_calibration(df),
            "author_decision": "Phase 5-PRE-B: primary period 1994-2024, calibrated Open-Meteo ERA5, same node; "
                               "neighbouring nodes are sensitivity experiments; GWA scaling is not a correction",
        }
    return res


def run(series_key: str = PRIMARY.key, out: Path = OUT) -> dict:
    spec = SERIES[series_key]
    df, info = load_series(spec)
    res = compute(df, spec, info)
    out.mkdir(parents=True, exist_ok=True)
    res.pop("_annual_table").round(8).to_csv(out / "annual_energy.csv")
    for name, obj in res.items():
        (out / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False))
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default=PRIMARY.key, choices=sorted(SERIES))
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    if a.series != PRIMARY.key and a.out.resolve() == OUT.resolve():
        print("✗ refusing to write a non-primary series into results/revised/")
        return 2
    res = run(a.series, a.out)
    ey = res["energy_yield.json"]
    s = res["interannual_and_sampling.json"]["sampling_ci_of_period_mean"]
    ci = s["primary_t_interval_90"]["net_gwh_per_mw"]
    print(f"[{a.series}] {s['period']}: net CF {ey['net_cf']*100:.3f}%  net {ey['net']['gwh_per_mw']:.4f} GWh/MW/yr "
          f"(90% sampling CI {ci[0]:.3f}-{ci[1]:.3f}); gross {ey['gross']['gwh_per_turbine']:.2f} GWh/turbine")
    print(f"Weibull cross-check: {res['weibull_crosscheck.json']['relative_difference_pct']:+.2f}%")
    print(f"✓ wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
