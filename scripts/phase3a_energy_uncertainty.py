"""
Phase 3A — energy estimator and uncertainty framework (provisional)
====================================================================
Inputs (unchanged): data/processed/wind_hub_105m.parquet, the active
OEDB V164/9500 curve, nominal losses in config/turbine.py, and Phase 2A/2B
outputs (read only, for comparison).

Central estimator: empirical hourly power conversion of the committed ERA5
series (scripts/04 power_from_speed, imported directly), expressed as a
time-weighted capacity factor and converted to energy for an average year
of 8766 h (365.25 d).

Quantified:
  * year-to-year variability of annual CF (11 calendar years, observed in
    the reanalysis);
  * sampling uncertainty of the 11-year mean: year-block bootstrap (whole
    calendar years resampled with replacement), with jackknife and
    t-interval cross-checks.
Not given probability distributions (scenarios or sensitivities only):
  * loss assumptions (nominal baseline + low/high loss scenarios);
  * ERA5 representativeness / wind-speed level (Phase 2B sensitivities);
  * power curve, air density, unmodelled engineering effects.

Outputs (provisional; nothing else is written):
  results/provisional/phase3a/energy_uncertainty.json
  results/provisional/phase3a/annual_energy.csv
No avoided-emission quantities are computed here.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from scipy import stats

from config.turbine import (TURBINE, POWER_CURVE_ID, POWER_CURVE_MS_KW,
                            WAKE_LOSS_DEFAULT, AVAILABILITY_DEFAULT,
                            ELECTRICAL_LOSS_DEFAULT)

PARQUET = ROOT / "data" / "processed" / "wind_hub_105m.parquet"
OUT = ROOT / "results" / "provisional" / "phase3a"
BASELINE = ROOT / "results" / "archive" / "baseline_original_curve"
P2A = ROOT / "results" / "provisional" / "phase2a"
P2B = ROOT / "results" / "provisional" / "phase2b"

RATED_KW = TURBINE.rated_power_mw * 1000.0
H_YEAR = 8766.0                        # average year incl. leap days (365.25 d)
SEED = 2026
B = 20000                              # bootstrap replicates
BIN_EDGES = np.arange(0.0, 27.0, 1.0)

LOSS_SCENARIOS = {                     # (wake, availability, electrical)
    # Nominal = existing config values (baseline). Low/high = the bounds that
    # scripts/06 already uses as triangular endpoints. Labelled assumptions,
    # not probability bounds; no site-specific evidence supports them.
    "low_loss": (0.05, 0.97, 0.02),
    "nominal": (WAKE_LOSS_DEFAULT, AVAILABILITY_DEFAULT, ELECTRICAL_LOSS_DEFAULT),
    "high_loss": (0.12, 0.92, 0.04),
}


def _s04():
    spec = importlib.util.spec_from_file_location("s04", ROOT / "scripts/04_fit_weibull_aep.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def net_factor(w, a, e):
    return (1 - w) * a * (1 - e)


NF = net_factor(*LOSS_SCENARIOS["nominal"])


def cf_to_energy(cf):
    """CF (fraction) -> dict of per-turbine GWh/yr and per-MW GWh/yr for an 8766 h year."""
    return {"gwh_per_turbine": cf * RATED_KW * H_YEAR / 1e6,
            "gwh_per_mw": cf * H_YEAR / 1000.0}


def annual_table(df, power_kw):
    t = pd.DataFrame({"p": power_kw}, index=df.index)
    g = t.groupby(t.index.year)["p"]
    tab = pd.DataFrame({"hours": g.size(), "gross_kwh": g.sum()})
    tab.index.name = "year"
    tab["leap"] = [pd.Timestamp(year=y, month=1, day=1).is_leap_year for y in tab.index]
    tab["gross_cf"] = tab.gross_kwh / (RATED_KW * tab.hours)
    tab["net_cf"] = tab.gross_cf * NF
    # calendar-year energy (actual hours) and leap-normalised energy (8766 h)
    tab["gross_gwh_calendar"] = tab.gross_kwh / 1e6
    tab["net_gwh_per_mw_calendar"] = tab.gross_kwh * NF / 1e6 / TURBINE.rated_power_mw
    tab["net_gwh_per_mw_8766h"] = tab.net_cf * H_YEAR / 1000.0
    tab["mean_U_hub"] = df["U_hub"].groupby(df.index.year).mean()
    return tab


def pooled_cf(tab, years=None):
    t = tab if years is None else tab.loc[years]
    return float(t.gross_kwh.sum() / (RATED_KW * t.hours.sum()))


def bootstrap(tab):
    rng = np.random.default_rng(SEED)
    yrs = tab.index.to_numpy()
    kwh = tab.gross_kwh.to_numpy(); hrs = tab.hours.to_numpy()
    idx = rng.integers(0, len(yrs), size=(B, len(yrs)))
    cf = kwh[idx].sum(1) / (RATED_KW * hrs[idx].sum(1))
    return cf


def weibull_decomposition(u, k, c, s04):
    """Energy by 1 m/s bin: empirical hours vs Weibull probability, same curve."""
    v = np.arange(0, 30, 0.1)                                  # scripts/06 grid
    pcurve = np.interp(v, [p[0] for p in POWER_CURVE_MS_KW], [p[1] for p in POWER_CURVE_MS_KW],
                       left=0, right=0)
    pcurve[v >= TURBINE.cut_out_ms] = 0.0
    pdf = stats.weibull_min.pdf(v, k, 0, c)
    p_emp = s04.power_from_speed(u.copy())
    rows = []
    for lo, hi in zip(BIN_EDGES[:-1], BIN_EDGES[1:]):
        me = (u >= lo) & (u < hi)
        mv = (v >= lo) & (v < hi)
        # Weibull contribution evaluated with the same trapezoid as scripts/06,
        # restricted to the bin (piecewise; bins share endpoints exactly on the grid)
        vv = v[(v >= lo - 1e-9) & (v <= hi + 1e-9)]
        pp = pcurve[(v >= lo - 1e-9) & (v <= hi + 1e-9)]
        ff = pdf[(v >= lo - 1e-9) & (v <= hi + 1e-9)]
        w_cf = np.trapezoid(pp * ff, vv) / RATED_KW if len(vv) > 1 else 0.0
        rows.append({"bin_ms": f"{lo:.0f}-{hi:.0f}",
                     "hours_share_emp_pct": float(me.mean() * 100),
                     "prob_weibull_pct": float(stats.weibull_min.cdf(hi, k, 0, c)
                                               - stats.weibull_min.cdf(lo, k, 0, c)) * 100,
                     "gross_cf_contrib_emp_pct": float(p_emp[me].sum() / (RATED_KW * u.size) * 100),
                     "gross_cf_contrib_weibull_pct": float(w_cf * 100)})
    d = pd.DataFrame(rows)
    d["diff_weibull_minus_emp_pctpts"] = d.gross_cf_contrib_weibull_pct - d.gross_cf_contrib_emp_pct
    total_w = np.trapezoid(pcurve * pdf, v) / RATED_KW
    return d, float(total_w)


def main() -> int:
    s04 = _s04()
    df = pd.read_parquet(PARQUET)
    u = df["U_hub"].to_numpy().astype(float)
    p_kw = s04.power_from_speed(u.copy())                       # production function
    tab = annual_table(df, p_kw)

    # ---------------- central estimate ----------------
    cf_pooled = pooled_cf(tab)
    cf_mean_of_years = float(tab.gross_cf.mean())
    central = {"gross_cf": cf_pooled, "net_cf": cf_pooled * NF,
               "gross": cf_to_energy(cf_pooled), "net": cf_to_energy(cf_pooled * NF),
               "net_full_load_hours": cf_pooled * NF * H_YEAR}
    normalisation = {
        "hours_total": int(tab.hours.sum()), "years": int(len(tab)),
        "leap_years": [int(y) for y in tab.index[tab.leap]],
        "mean_hours_per_calendar_year_in_sample": float(tab.hours.sum() / len(tab)),
        "phase2a_sum_over_11_gross_gwh": float(p_kw.sum() / len(tab) / 1e6),
        "cf_x_8766h_gross_gwh": central["gross"]["gwh_per_turbine"],
        "relative_difference": float((p_kw.sum() / len(tab) / 1e6) / central["gross"]["gwh_per_turbine"] - 1),
        "pooled_cf_minus_mean_of_annual_cf": cf_pooled - cf_mean_of_years,
    }

    # ---------------- interannual variability (single years) ----------------
    ann = tab.net_cf
    variability = {
        "annual_net_cf_mean": float(ann.mean()), "annual_net_cf_sd_ddof1": float(ann.std(ddof=1)),
        "annual_cov_pct": float(ann.std(ddof=1) / ann.mean() * 100),
        "min_year": int(ann.idxmin()), "min_net_cf": float(ann.min()),
        "max_year": int(ann.idxmax()), "max_net_cf": float(ann.max()),
        "min_rel_to_pooled_pct": float((tab.gross_cf.min() / cf_pooled - 1) * 100),
        "max_rel_to_pooled_pct": float((tab.gross_cf.max() / cf_pooled - 1) * 100),
        "cov_without_2014_pct": float(ann.drop(2014).std(ddof=1) / ann.drop(2014).mean() * 100),
        "lag1_autocorr_annual_cf": float(np.corrcoef(ann.values[:-1], ann.values[1:])[0, 1]),
        "speed_cov_pct": float(tab.mean_U_hub.std(ddof=1) / tab.mean_U_hub.mean() * 100),
        "energy_to_speed_variability_ratio": float((ann.std(ddof=1) / ann.mean())
                                                   / (tab.mean_U_hub.std(ddof=1) / tab.mean_U_hub.mean())),
    }

    # ---------------- sampling uncertainty of the 11-year mean ----------------
    bcf = bootstrap(tab)
    n = len(tab)
    se_classic = float(tab.gross_cf.std(ddof=1) / np.sqrt(n))
    jk = np.array([pooled_cf(tab, [y for y in tab.index if y != d]) for d in tab.index])
    se_jack = float(np.sqrt((n - 1) / n * np.sum((jk - jk.mean()) ** 2)))
    tq90 = stats.t.ppf(0.95, n - 1)
    q = lambda a, p: float(np.percentile(a, p))
    sampling = {
        "method": "year-block bootstrap: 11 calendar years resampled with replacement, "
                  f"B={B}, seed={SEED}; statistic = time-weighted gross CF",
        "bootstrap_gross_cf_ci90": [q(bcf, 5), q(bcf, 95)],
        "bootstrap_gross_cf_ci95": [q(bcf, 2.5), q(bcf, 97.5)],
        "bootstrap_se": float(bcf.std(ddof=1)),
        "classical_se_sd_over_sqrt_n": se_classic,
        "jackknife_se": se_jack,
        "t_interval_90_gross_cf": [cf_mean_of_years - tq90 * se_classic, cf_mean_of_years + tq90 * se_classic],
        "jackknife_leave_one_year_out_gross_cf": {int(y): float(v) for y, v in zip(tab.index, jk)},
        "net_gwh_per_mw_ci90": [q(bcf, 5) * NF * H_YEAR / 1000, q(bcf, 95) * NF * H_YEAR / 1000],
        "ci90_half_width_rel_pct": float((q(bcf, 95) - q(bcf, 5)) / 2 / cf_pooled * 100),
        "interpretation": "uncertainty of the 2014-2024 mean due to the finite number of years, "
                          "assuming years are exchangeable and ERA5 is correct; not year-to-year "
                          "production variability and not long-term climate representativeness",
    }

    # ---------------- losses as scenarios ----------------
    losses = {}
    for name, (w, a, e) in LOSS_SCENARIOS.items():
        nf = net_factor(w, a, e)
        losses[name] = {"wake": w, "availability": a, "electrical": e, "net_factor": nf,
                        "net_cf": cf_pooled * nf, "net_gwh_per_mw": cf_pooled * nf * H_YEAR / 1000,
                        "rel_to_nominal_pct": (nf / NF - 1) * 100}

    # ---------------- Weibull cross-check ----------------
    base_w = json.loads((BASELINE / "monte_carlo_results.json").read_text())["base_weibull"]
    dec, cf_weib = weibull_decomposition(u, base_w["k"], base_w["c"], s04)
    p2a = json.loads((P2A / "power_curve_comparison.json").read_text())
    mc_new = json.loads((P2A / "monte_carlo_results.json").read_text())["per_mw"]
    loss_mean_ratio = (net_factor((0.05 + 0.08 + 0.12) / 3, (0.92 + 0.95 + 0.97) / 3,
                                  (0.02 + 0.03 + 0.04) / 3) / NF)
    weibull = {
        "weibull_k_c_archived": [base_w["k"], base_w["c"]],
        "gross_cf_weibull": cf_weib, "gross_cf_empirical": cf_pooled,
        "relative_difference_weibull_vs_empirical_pct": (cf_weib / cf_pooled - 1) * 100,
        "net_gwh_per_mw_weibull_nominal": cf_weib * NF * H_YEAR / 1000,
        "bin_decomposition": dec.round(4).to_dict(orient="records"),
        "mc_phase2a_p50_net_gwh_per_mw": mc_new["net_aep_gwh_per_mw"]["p50"],
        "mc_phase2a_cov_pct": mc_new["net_aep_gwh_per_mw"]["std"] / mc_new["net_aep_gwh_per_mw"]["mean"] * 100,
        "triangular_mean_to_mode_loss_ratio": loss_mean_ratio,
        "weibull_nominal_x_loss_ratio": cf_weib * NF * H_YEAR / 1000 * loss_mean_ratio,
    }

    # ---------------- structural sensitivities (reference, not probabilistic) ----------------
    sens = json.loads((P2B / "wind_speed_sensitivity.json").read_text())["cases"]
    structural = {
        "wind_speed_level_phase2b": {c["case"]: c["aep_change_vs_baseline_pct"] for c in sens},
        "power_curve_choice_original_vs_oedb_pct": (p2a["empirical_hourly"]["original"]["gross_aep_per_turbine_gwh"]
                                                    / p2a["empirical_hourly"]["oedb_v164_9500"]["gross_aep_per_turbine_gwh"] - 1) * 100,
        "not_quantified": ["air density at site", "hub-height extrapolation (alpha)",
                           "hourly instantaneous ERA5 vs 10-min power-curve basis",
                           "layout- and capacity-density-dependent wakes (S1-S4)",
                           "curtailment, degradation, icing/temperature derating",
                           "representativeness of 2014-2024 for the long-term climate"],
    }

    # ---------------- comparison of estimates ----------------
    orig = json.loads((BASELINE / "weibull_aep_results.json").read_text())["aep"]
    comparison = [
        {"estimate": "Original deterministic (retired curve, sum/11)", "net_gwh_per_mw": orig["net_aep_per_mw_gwh"],
         "net_cf_pct": orig["cf_net_pct"]},
        {"estimate": "Original MC P50 (retired curve, Weibull MC)",
         "net_gwh_per_mw": json.loads((BASELINE / "monte_carlo_results.json").read_text())["per_mw"]["net_aep_gwh_per_mw"]["p50"]},
        {"estimate": "Phase 2A empirical (OEDB, sum/11)", "net_gwh_per_mw": p2a["empirical_hourly"]["oedb_v164_9500"]["net_aep_per_mw_gwh"],
         "net_cf_pct": p2a["empirical_hourly"]["oedb_v164_9500"]["net_cf_pct"]},
        {"estimate": "Phase 2A Weibull, nominal losses (OEDB)", "net_gwh_per_mw": weibull["net_gwh_per_mw_weibull_nominal"],
         "net_cf_pct": cf_weib * NF * 100},
        {"estimate": "Phase 2A MC P50 (OEDB, Weibull MC)", "net_gwh_per_mw": weibull["mc_phase2a_p50_net_gwh_per_mw"]},
        {"estimate": "Phase 3A central (OEDB, empirical, CF x 8766 h)", "net_gwh_per_mw": central["net"]["gwh_per_mw"],
         "net_cf_pct": central["net_cf"] * 100},
    ]

    contributions = {
        "interannual_single_year_cov_pct": variability["annual_cov_pct"],
        "sampling_of_mean_bootstrap_se_rel_pct": sampling["bootstrap_se"] / cf_pooled * 100,
        "sampling_of_mean_ci90_half_width_rel_pct": sampling["ci90_half_width_rel_pct"],
        "loss_scenarios_rel_pct": [losses["high_loss"]["rel_to_nominal_pct"], losses["low_loss"]["rel_to_nominal_pct"]],
        "wind_speed_pm5_pct": [structural["wind_speed_level_phase2b"]["-5%"], structural["wind_speed_level_phase2b"]["+5%"]],
        "wind_speed_pm10_pct": [structural["wind_speed_level_phase2b"]["-10%"], structural["wind_speed_level_phase2b"]["+10%"]],
    }

    out = {
        "status": "PROVISIONAL — Phase 3A energy uncertainty framework; not a bankable P50/P90; "
                  "no avoided-emission quantities",
        "power_curve": POWER_CURVE_ID, "hours_per_average_year": H_YEAR,
        "central_estimate": central, "normalisation_checks": normalisation,
        "interannual_variability": variability, "sampling_uncertainty_of_mean": sampling,
        "loss_scenarios": losses, "weibull_cross_check": weibull,
        "structural_sensitivities": structural, "comparison": comparison,
        "relative_magnitudes": contributions,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "energy_uncertainty.json").write_text(json.dumps(out, indent=2))
    tab.round(8).to_csv(OUT / "annual_energy.csv")

    # ---------------- console ----------------
    print(f"Central: gross CF {cf_pooled*100:.3f}%  net CF {central['net_cf']*100:.3f}%  "
          f"net {central['net']['gwh_per_mw']:.4f} GWh/MW/yr  gross {central['gross']['gwh_per_turbine']:.3f} GWh/turbine")
    print(f"Normalisation: sum/11 vs CF*8766 = {normalisation['relative_difference']*100:+.4f}%; "
          f"pooled - mean(annual CF) = {normalisation['pooled_cf_minus_mean_of_annual_cf']*100:+.4f} pct-pts")
    print(tab[["hours", "leap", "mean_U_hub", "gross_cf", "net_cf", "net_gwh_per_mw_8766h"]].round(4).to_string())
    print(f"Interannual: CoV {variability['annual_cov_pct']:.2f}% (w/o 2014 {variability['cov_without_2014_pct']:.2f}%), "
          f"lag-1 r {variability['lag1_autocorr_annual_cf']:+.2f}, energy/speed CoV ratio "
          f"{variability['energy_to_speed_variability_ratio']:.2f}")
    print(f"Sampling: bootstrap 90% CI net {sampling['net_gwh_per_mw_ci90'][0]:.3f}-{sampling['net_gwh_per_mw_ci90'][1]:.3f} "
          f"GWh/MW (±{sampling['ci90_half_width_rel_pct']:.2f}%); SE boot {sampling['bootstrap_se']*100:.3f} / "
          f"classic {se_classic*100:.3f} / jack {se_jack*100:.3f} pct-pts CF")
    print("Losses:", {k: round(v["net_gwh_per_mw"], 3) for k, v in losses.items()})
    print(f"Weibull: CF {cf_weib*100:.3f}% vs emp {cf_pooled*100:.3f}% ({weibull['relative_difference_weibull_vs_empirical_pct']:+.2f}%); "
          f"Weibull nominal x loss-mean ratio {weibull['weibull_nominal_x_loss_ratio']:.4f} vs MC P50 "
          f"{weibull['mc_phase2a_p50_net_gwh_per_mw']:.4f}")
    print(dec.round(3).to_string(index=False))
    print(f"✓ wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
