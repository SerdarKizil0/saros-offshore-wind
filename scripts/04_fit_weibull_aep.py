"""
04 — Weibull fit + AEP calculation (Saros Bay)
===============================================
Reads the processed hub-height wind series, fits a Weibull distribution
(MLE, with method-of-moments cross-check), assesses goodness of fit,
then computes Annual Energy Production with the Vestas V164-9.5 MW
power curve — reported per-MW and across capacity scenarios.

Inputs : data/processed/wind_hub_105m.parquet
Outputs: results/weibull_aep_results.json

Run after 03_process_era5.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import gamma

from config.site import SITE, DATA_DIR, RESULTS_DIR
from config.turbine import (TURBINE, POWER_CURVE_MS_KW, SCENARIOS,
                            WAKE_LOSS_DEFAULT, AVAILABILITY_DEFAULT,
                            ELECTRICAL_LOSS_DEFAULT)

INPUT = DATA_DIR / "processed" / "wind_hub_105m.parquet"
OUTPUT = RESULTS_DIR / "weibull_aep_results.json"

RHO_AIR = 1.225   # kg/m³, standard sea-level air density


# ----------------------------------------------------------------
def fit_weibull(u: np.ndarray) -> dict:
    """Fit Weibull by MLE (floc=0) plus method-of-moments cross-check."""
    u_pos = u[u > 0]

    # MLE — location fixed at 0 (standard for wind)
    k_mle, _loc, c_mle = stats.weibull_min.fit(u_pos, floc=0)

    # Method of moments
    mean_u, std_u = u.mean(), u.std()
    k_mom = (std_u / mean_u) ** (-1.086)
    c_mom = mean_u / gamma(1 + 1 / k_mom)

    # Goodness of fit
    ks_stat, ks_p = stats.kstest(
        u_pos, lambda x: stats.weibull_min.cdf(x, k_mle, 0, c_mle)
    )
    sorted_u = np.sort(u_pos)
    emp_cdf = np.arange(1, len(sorted_u) + 1) / len(sorted_u)
    theo_cdf = stats.weibull_min.cdf(sorted_u, k_mle, 0, c_mle)
    r2 = 1 - np.sum((emp_cdf - theo_cdf) ** 2) / \
             np.sum((emp_cdf - emp_cdf.mean()) ** 2)

    weib_mean = c_mle * gamma(1 + 1 / k_mle)
    emp_pd  = 0.5 * RHO_AIR * np.mean(u ** 3)
    weib_pd = 0.5 * RHO_AIR * c_mle ** 3 * gamma(1 + 3 / k_mle)

    return {
        "k_mle": float(k_mle), "c_mle": float(c_mle),
        "k_mom": float(k_mom), "c_mom": float(c_mom),
        "ks_statistic": float(ks_stat), "ks_pvalue": float(ks_p),
        "r2_cdf": float(r2),
        "weibull_mean_ms": float(weib_mean),
        "empirical_mean_ms": float(mean_u),
        "empirical_power_density_wm2": float(emp_pd),
        "weibull_power_density_wm2": float(weib_pd),
        "n_hours": int(len(u)),
        "n_hours_positive": int(len(u_pos)),
    }


def power_from_speed(u: np.ndarray) -> np.ndarray:
    """Interpolate the V164-9.5 MW power curve at each wind speed (kW)."""
    pc_ms = [p[0] for p in POWER_CURVE_MS_KW]
    pc_kw = [p[1] for p in POWER_CURVE_MS_KW]
    power = np.interp(u, pc_ms, pc_kw, left=0, right=0)
    power[u < TURBINE.cut_in_ms] = 0.0
    power[u >= TURBINE.cut_out_ms] = 0.0
    return power


def compute_aep(u: np.ndarray, n_years: int) -> dict:
    """Gross & net AEP per turbine, capacity factors, per-MW yield."""
    power_kw = power_from_speed(u)
    rated_kw = TURBINE.rated_power_mw * 1000

    # Each row is one hour; summing kW over hours gives kWh.
    gross_energy_kwh = power_kw.sum()                    # over the whole record
    gross_aep_turbine = gross_energy_kwh / n_years       # kWh/yr
    cf_gross = power_kw.mean() / rated_kw

    net_factor = (
        (1 - WAKE_LOSS_DEFAULT)
        * AVAILABILITY_DEFAULT
        * (1 - ELECTRICAL_LOSS_DEFAULT)
    )
    net_aep_turbine = gross_aep_turbine * net_factor
    cf_net = cf_gross * net_factor

    net_aep_per_mw = net_aep_turbine / TURBINE.rated_power_mw
    full_load_hours = net_aep_turbine / rated_kw

    return {
        "gross_aep_per_turbine_gwh": gross_aep_turbine / 1e6,
        "net_aep_per_turbine_gwh":   net_aep_turbine / 1e6,
        "cf_gross_pct": cf_gross * 100,
        "cf_net_pct":   cf_net * 100,
        "net_aep_per_mw_gwh": net_aep_per_mw / 1e6,
        "net_full_load_hours": full_load_hours,
        "loss_assumptions": {
            "wake": WAKE_LOSS_DEFAULT,
            "availability": AVAILABILITY_DEFAULT,
            "electrical": ELECTRICAL_LOSS_DEFAULT,
            "net_factor": net_factor,
        },
    }


def scenario_table(net_aep_turbine_gwh: float) -> list[dict]:
    rows = []
    for s in SCENARIOS:
        rows.append({
            "name": s.name,
            "description": s.description,
            "n_turbines": s.n_turbines,
            "installed_mw": s.installed_mw,
            "farm_net_aep_gwh": net_aep_turbine_gwh * s.n_turbines,
            "farm_net_aep_twh": net_aep_turbine_gwh * s.n_turbines / 1000,
        })
    return rows


# ----------------------------------------------------------------
def main() -> int:
    print("=" * 72)
    print(" Weibull fit + AEP — Saros Bay")
    print("=" * 72)

    if not INPUT.exists():
        print(f"✗ Input not found: {INPUT}")
        print("  Run scripts/03_process_era5.py first.")
        return 1

    df = pd.read_parquet(INPUT)
    u = df["U_hub"].values
    n_years = SITE.era5_n_years
    print(f"Loaded {len(u):,} hourly wind speeds ({n_years} years)")

    # --- Weibull ---
    w = fit_weibull(u)
    print(f"\nWeibull (MLE):  k = {w['k_mle']:.4f},  c = {w['c_mle']:.4f} m/s")
    print(f"Weibull (MoM):  k = {w['k_mom']:.4f},  c = {w['c_mom']:.4f} m/s")
    print(f"Goodness of fit: R²(CDF) = {w['r2_cdf']:.5f}, "
          f"KS D = {w['ks_statistic']:.4f}")
    print(f"Mean: Weibull {w['weibull_mean_ms']:.3f} vs "
          f"empirical {w['empirical_mean_ms']:.3f} m/s")
    print(f"Power density: {w['weibull_power_density_wm2']:.0f} W/m² "
          f"(empirical {w['empirical_power_density_wm2']:.0f})")

    # --- AEP ---
    aep = compute_aep(u, n_years)
    print(f"\nPer turbine (Vestas V164-9.5 MW):")
    print(f"  Gross AEP: {aep['gross_aep_per_turbine_gwh']:.2f} GWh/yr  "
          f"(CF {aep['cf_gross_pct']:.1f}%)")
    print(f"  Net AEP:   {aep['net_aep_per_turbine_gwh']:.2f} GWh/yr  "
          f"(CF {aep['cf_net_pct']:.1f}%)")
    print(f"  Net per MW: {aep['net_aep_per_mw_gwh']:.3f} GWh/yr/MW")
    print(f"  Full-load hours: {aep['net_full_load_hours']:.0f} h/yr")

    # --- Scenarios ---
    scenarios = scenario_table(aep["net_aep_per_turbine_gwh"])
    print(f"\nCapacity scenarios (net farm AEP):")
    for r in scenarios:
        print(f"  {r['name']:12s}: {r['n_turbines']:3d} turb "
              f"= {r['installed_mw']:6.1f} MW → {r['farm_net_aep_twh']:.3f} TWh/yr")

    # --- Save ---
    results = {
        "site": SITE.full_name,
        "turbine": f"{TURBINE.manufacturer} {TURBINE.model}",
        "hub_height_m": TURBINE.hub_height_m,
        "weibull": w,
        "aep": aep,
        "scenarios": scenarios,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=2))
    print(f"\n✓ Saved: {OUTPUT}")
    print("\nNext step: python scripts/05_run_monte_carlo.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
