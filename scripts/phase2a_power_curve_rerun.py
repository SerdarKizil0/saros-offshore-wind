"""
Phase 2A — power-curve correction: rerun and old-vs-new comparison
===================================================================
Changes ONLY the turbine power curve (POWER_CURVE_ORIGINAL_MS_KW ->
POWER_CURVE_OEDB_V164_9500_MS_KW). Wind statistics, losses, emission
factors, uncertainty distributions, seed and scenarios are unchanged.

What it does
  1. Weibull-integrated gross/net AEP for both curves (same Weibull k0, c0,
     same 0.1 m/s grid and interpolation as scripts/06_run_monte_carlo.py).
  2. Empirical hourly AEP for both curves (same method as
     scripts/04_fit_weibull_aep.py) — ONLY if
     data/processed/wind_hub_105m.parquet exists. Otherwise it is reported
     as NOT COMPUTED; nothing is estimated.
  3. Monte Carlo, seed 2026, identical sampling to scripts/06. The base
     Weibull parameters (k0, c0, sigma_c) are read from the archived
     baseline results, where scripts/06 stored them at full float64
     precision from the parquet run. The original-curve run must reproduce
     the archived samples bit-for-bit, otherwise the script aborts.

Outputs (provisional; the archived baseline and results/*.json are not touched)
  results/provisional/phase2a/monte_carlo_results.json
  results/provisional/phase2a/monte_carlo_samples.npz
  results/provisional/phase2a/power_curve_comparison.json

The avoided-CO2 outputs reuse the existing, NOT yet validated, emissions
treatment of scripts/06 and are provisional.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from scipy import stats

from config.site import DATA_DIR, RESULTS_DIR, SITE
from config.turbine import (TURBINE, SCENARIOS, POWER_CURVE_ORIGINAL_MS_KW,
                            POWER_CURVE_OEDB_V164_9500_MS_KW,
                            WAKE_LOSS_DEFAULT, AVAILABILITY_DEFAULT,
                            ELECTRICAL_LOSS_DEFAULT)
from config.emissions import GRID_CO2, OFFSHORE_WIND_CO2

BASELINE_DIR = RESULTS_DIR / "archive" / "baseline_original_curve"
OUT_DIR = RESULTS_DIR / "provisional" / "phase2a"
PARQUET = DATA_DIR / "processed" / "wind_hub_105m.parquet"

CURVES = {"original": POWER_CURVE_ORIGINAL_MS_KW,
          "oedb_v164_9500": POWER_CURVE_OEDB_V164_9500_MS_KW}

_trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
NET_FACTOR = ((1 - WAKE_LOSS_DEFAULT) * AVAILABILITY_DEFAULT
              * (1 - ELECTRICAL_LOSS_DEFAULT))
RATED_KW = TURBINE.rated_power_mw * 1000


# ---- curve evaluation: exact copies of the production conventions --------
def power_grid(curve):
    """== scripts/06 make_power_grid(), for an explicit curve."""
    pc_ms = [p[0] for p in curve]
    pc_kw = [p[1] for p in curve]
    v = np.arange(0, 30, 0.1)
    p = np.interp(v, pc_ms, pc_kw, left=0, right=0)
    p[v >= TURBINE.cut_out_ms] = 0.0
    return v, p


def power_from_speed(u, curve):
    """== scripts/04 power_from_speed(), for an explicit curve."""
    pc_ms = [p[0] for p in curve]
    pc_kw = [p[1] for p in curve]
    power = np.interp(u, pc_ms, pc_kw, left=0, right=0)
    power[u < TURBINE.cut_in_ms] = 0.0
    power[u >= TURBINE.cut_out_ms] = 0.0
    return power


def weibull_gross_cf(k, c, v, p):
    """== scripts/06 aep_from_weibull() (returns gross CF)."""
    pdf = stats.weibull_min.pdf(v, k, 0, c)
    return _trapz(p * pdf, v) / RATED_KW


def pctl(a):
    p = np.percentile(a, [10, 50, 90])
    return {"p10": float(p[0]), "p50": float(p[1]), "p90": float(p[2]),
            "mean": float(np.mean(a)), "std": float(np.std(a))}


# ---- Monte Carlo: identical sampling order and formulas to scripts/06 ----
def run_mc(curve, k0, c0, sigma_c, n_iter, seed):
    v_grid, p_grid = power_grid(curve)
    rng = np.random.default_rng(seed)
    k_s = rng.normal(k0, 0.04, n_iter)
    c_s = rng.normal(c0, sigma_c, n_iter)
    wake_s = rng.triangular(0.05, WAKE_LOSS_DEFAULT, 0.12, n_iter)
    avail_s = rng.triangular(0.92, AVAILABILITY_DEFAULT, 0.97, n_iter)
    elec_s = rng.triangular(0.02, ELECTRICAL_LOSS_DEFAULT, 0.04, n_iter)
    grid_s = rng.triangular(GRID_CO2.low, GRID_CO2.best, GRID_CO2.high, n_iter)
    lca_s = rng.triangular(OFFSHORE_WIND_CO2.low, OFFSHORE_WIND_CO2.best,
                           OFFSHORE_WIND_CO2.high, n_iter)
    net_aep_turb = np.zeros(n_iter)
    cf_net = np.zeros(n_iter)
    for i in range(n_iter):
        pdf = stats.weibull_min.pdf(v_grid, k_s[i], 0, c_s[i])
        mean_kw = _trapz(p_grid * pdf, v_grid)
        gross_kwh, gross_cf = mean_kw * 8766, mean_kw / RATED_KW
        nf = (1 - wake_s[i]) * avail_s[i] * (1 - elec_s[i])
        net_aep_turb[i] = gross_kwh * nf / 1e6
        cf_net[i] = gross_cf * nf
    aep_per_mw = net_aep_turb / TURBINE.rated_power_mw
    avoided_kwh = grid_s - lca_s
    avoided_per_mw = aep_per_mw * 1e6 * avoided_kwh / 1e6
    scen = []
    for s in SCENARIOS:
        scen.append({
            "name": s.name, "installed_mw": s.installed_mw,
            "n_turbines": s.n_turbines,
            "farm_aep_twh": pctl(net_aep_turb * s.n_turbines / 1000.0),
            "avoided_co2_mt": pctl(avoided_per_mw * s.installed_mw / 1e6),
        })
    return {"aep_per_mw": aep_per_mw, "cf_net": cf_net,
            "avoided_per_mw": avoided_per_mw, "scenarios": scen}


def main() -> int:
    base = json.loads((BASELINE_DIR / "monte_carlo_results.json").read_text())
    base_npz = np.load(BASELINE_DIR / "monte_carlo_samples.npz")
    k0 = base["base_weibull"]["k"]
    c0 = base["base_weibull"]["c"]
    sigma_c = base["base_weibull"]["sigma_c_interannual"]
    n_iter, seed = base["n_iterations"], base["seed"]
    print(f"Base Weibull (archived, from parquet run): k0={k0!r} c0={c0!r} "
          f"sigma_c={sigma_c!r}; N={n_iter}, seed={seed}")

    # --- 1. Weibull-integrated AEP ---
    weib = {}
    for name, curve in CURVES.items():
        v, p = power_grid(curve)
        g = weibull_gross_cf(k0, c0, v, p)
        weib[name] = {
            "gross_cf_pct": g * 100,
            "gross_aep_per_turbine_gwh": g * RATED_KW * 8766 / 1e6,
            "net_cf_pct": g * NET_FACTOR * 100,
            "net_aep_per_turbine_gwh": g * NET_FACTOR * RATED_KW * 8766 / 1e6,
            "net_aep_per_mw_gwh": g * NET_FACTOR * 8.766,
            "net_full_load_hours": g * NET_FACTOR * 8766,
        }
    # boundary-convention sensitivities on the corrected curve (Weibull basis)
    v, p = power_grid(CURVES["oedb_v164_9500"])
    g_ref = weibull_gross_cf(k0, c0, v, p)
    p_cutin = p.copy(); p_cutin[v < TURBINE.cut_in_ms] = 0.0
    p_tail = p.copy(); p_tail[(v > 24.5) & (v < 25.0)] = 0.0
    sens = {
        "zero_below_cut_in_as_script04_rel_change": weibull_gross_cf(k0, c0, v, p_cutin) / g_ref - 1,
        "zero_24p5_to_25_instead_of_plateau_rel_change": weibull_gross_cf(k0, c0, v, p_tail) / g_ref - 1,
    }

    # --- 2. Empirical hourly AEP (only with the real input) ---
    if PARQUET.exists():
        import pandas as pd
        u = pd.read_parquet(PARQUET)["U_hub"].values
        emp = {"status": "computed", "n_hours": int(u.size)}
        for name, curve in CURVES.items():
            pk = power_from_speed(u, curve)
            gross = pk.sum() / SITE.era5_n_years
            emp[name] = {
                "gross_aep_per_turbine_gwh": gross / 1e6,
                "gross_cf_pct": pk.mean() / RATED_KW * 100,
                "net_aep_per_turbine_gwh": gross * NET_FACTOR / 1e6,
                "net_cf_pct": pk.mean() / RATED_KW * NET_FACTOR * 100,
                "net_aep_per_mw_gwh": gross * NET_FACTOR / TURBINE.rated_power_mw / 1e6,
            }
    else:
        emp = {"status": "NOT COMPUTED",
               "reason": f"required input {PARQUET.relative_to(PARQUET.parents[2])} "
                         "is not in the repository and no ERA5 credentials are "
                         "available to regenerate it; no estimate substituted"}
        print(f"\n! Empirical hourly AEP NOT COMPUTED: {PARQUET} missing.")

    # --- 3. Monte Carlo ---
    mc = {name: run_mc(curve, k0, c0, sigma_c, n_iter, seed)
          for name, curve in CURVES.items()}
    for key in ("aep_per_mw", "cf_net", "avoided_per_mw"):
        if not np.array_equal(mc["original"][key], base_npz[key]):
            print(f"✗ original-curve rerun does not reproduce archived '{key}'")
            return 2
    print("✓ Original-curve Monte Carlo reproduces archived samples bit-for-bit")

    new = mc["oedb_v164_9500"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT_DIR / "monte_carlo_samples.npz",
                        aep_per_mw=new["aep_per_mw"], cf_net=new["cf_net"],
                        avoided_per_mw=new["avoided_per_mw"])
    status = ("PROVISIONAL — Phase 2A power-curve correction only; avoided-CO2 "
              "values use the existing, unvalidated emissions sampling")
    mc_json = {
        "status": status,
        "power_curve": "OEDB_V164_9500 (config.turbine.POWER_CURVE_OEDB_V164_9500_MS_KW)",
        "site": base["site"], "n_iterations": n_iter, "seed": seed,
        "base_weibull": base["base_weibull"], "sampling": base["sampling"],
        "per_mw": {"net_aep_gwh_per_mw": pctl(new["aep_per_mw"]),
                   "net_cf_pct": pctl(new["cf_net"] * 100),
                   "avoided_co2_t_per_mw": pctl(new["avoided_per_mw"])},
        "scenarios": new["scenarios"],
    }
    (OUT_DIR / "monte_carlo_results.json").write_text(json.dumps(mc_json, indent=2))

    def mcsum(r):
        return {"net_aep_gwh_per_mw": pctl(r["aep_per_mw"]),
                "net_cf_pct": pctl(r["cf_net"] * 100),
                "avoided_co2_t_per_mw_PROVISIONAL": pctl(r["avoided_per_mw"]),
                "S3_farm_aep_twh": r["scenarios"][2]["farm_aep_twh"],
                "S3_avoided_co2_mt_PROVISIONAL": r["scenarios"][2]["avoided_co2_mt"]}

    comp = {
        "status": status,
        "inputs_unchanged": ["Weibull k0, c0, sigma_c", "loss factors",
                             "emission factors", "MC distributions and seed",
                             "capacity scenarios"],
        "weibull_integrated_nominal_losses": weib,
        "weibull_relative_change": weib["oedb_v164_9500"]["gross_cf_pct"]
        / weib["original"]["gross_cf_pct"] - 1,
        "boundary_convention_sensitivity_weibull": sens,
        "empirical_hourly": emp,
        "monte_carlo": {name: mcsum(r) for name, r in mc.items()},
    }
    (OUT_DIR / "power_curve_comparison.json").write_text(json.dumps(comp, indent=2))

    # --- console summary ---
    o, n = weib["original"], weib["oedb_v164_9500"]
    print("\nWeibull-integrated (nominal losses)      original    OEDB")
    for k, f in (("gross_aep_per_turbine_gwh", "{:9.2f}"), ("gross_cf_pct", "{:9.2f}"),
                 ("net_aep_per_turbine_gwh", "{:9.2f}"), ("net_cf_pct", "{:9.2f}"),
                 ("net_aep_per_mw_gwh", "{:9.3f}")):
        print(f"  {k:<36s}" + f.format(o[k]) + f.format(n[k]))
    print(f"  relative change: {comp['weibull_relative_change']*100:+.2f}%")
    print(f"  sensitivity (corrected curve): {sens}")
    for name, r in comp["monte_carlo"].items():
        a, c, av = (r["net_aep_gwh_per_mw"], r["net_cf_pct"],
                    r["avoided_co2_t_per_mw_PROVISIONAL"])
        print(f"MC {name:15s} AEP/MW {a['p10']:.3f}/{a['p50']:.3f}/{a['p90']:.3f}  "
              f"CF {c['p10']:.2f}/{c['p50']:.2f}/{c['p90']:.2f}  "
              f"CO2 {av['p10']:.0f}/{av['p50']:.0f}/{av['p90']:.0f}  "
              f"S3 {r['S3_farm_aep_twh']['p50']:.3f} TWh "
              f"{r['S3_avoided_co2_mt_PROVISIONAL']['p50']:.3f} Mt")
    print(f"\n✓ Wrote {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
