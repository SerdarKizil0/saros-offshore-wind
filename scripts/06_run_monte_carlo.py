"""
06 — Monte Carlo uncertainty quantification (Saros Bay)
========================================================
Propagates uncertainty in seven inputs through the AEP and avoided-CO2
calculation, producing P10/P50/P90 bands.

Sampled inputs (per iteration):
  k    Weibull shape      ~ Normal(k0, 0.04)
  c    Weibull scale      ~ Normal(c0, σ_interannual)   ← from 11 annual fits
  wake array wake loss    ~ Triangular(0.05, 0.08, 0.12)
  avail availability       ~ Triangular(0.92, 0.95, 0.97)
  elec electrical loss     ~ Triangular(0.02, 0.03, 0.04)
  grid Türkiye grid CO2    ~ Triangular(434, 624.2, 713.4)  [official EVÇED 2023]
  lca  offshore wind LCA   ~ Triangular(8, 11, 14)          [Bonou/IPCC]

Each iteration computes per-turbine gross AEP analytically by convolving
the V164-9.5 MW power curve with the sampled Weibull pdf, applies losses,
then converts wind generation into avoided CO2 using the sampled net
grid factor (grid − lca).

Inputs : data/processed/wind_hub_105m.parquet
Outputs: results/monte_carlo_results.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from scipy import stats

from config.site import SITE, DATA_DIR, RESULTS_DIR
from config.turbine import (TURBINE, POWER_CURVE_MS_KW, SCENARIOS,
                            WAKE_LOSS_DEFAULT, AVAILABILITY_DEFAULT,
                            ELECTRICAL_LOSS_DEFAULT)
from config.emissions import GRID_CO2, OFFSHORE_WIND_CO2

INPUT = DATA_DIR / "processed" / "wind_hub_105m.parquet"
OUTPUT = RESULTS_DIR / "monte_carlo_results.json"

N_ITER = 10000
SEED = 2026

# numpy 2.x renamed trapz -> trapezoid
_trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz


def base_weibull_and_iav(df: pd.DataFrame) -> tuple[float, float, float]:
    """Return (k0, c0, sigma_c) where sigma_c is the std of annual c fits."""
    u = df["U_hub"].values
    k0, _, c0 = stats.weibull_min.fit(u[u > 0], floc=0)
    annual_c = []
    for _yr, g in df.groupby(df.index.year):
        uu = g["U_hub"].values
        _k, _l, cc = stats.weibull_min.fit(uu[uu > 0], floc=0)
        annual_c.append(cc)
    return float(k0), float(c0), float(np.std(annual_c))


def make_power_grid():
    pc_ms = [p[0] for p in POWER_CURVE_MS_KW]
    pc_kw = [p[1] for p in POWER_CURVE_MS_KW]
    v = np.arange(0, 30, 0.1)
    p = np.interp(v, pc_ms, pc_kw, left=0, right=0)
    p[v >= TURBINE.cut_out_ms] = 0.0
    return v, p


def aep_from_weibull(k, c, v_grid, p_grid):
    """Analytical gross AEP (kWh/yr) and gross CF from power-curve × pdf."""
    pdf = stats.weibull_min.pdf(v_grid, k, 0, c)
    mean_kw = _trapz(p_grid * pdf, v_grid)
    rated_kw = TURBINE.rated_power_mw * 1000
    return mean_kw * 8766, mean_kw / rated_kw


def pctl(a):
    p = np.percentile(a, [10, 50, 90])
    return {"p10": float(p[0]), "p50": float(p[1]), "p90": float(p[2]),
            "mean": float(np.mean(a)), "std": float(np.std(a))}


def main() -> int:
    print("=" * 72)
    print(" Monte Carlo uncertainty — Saros Bay")
    print("=" * 72)
    if not INPUT.exists():
        print(f"✗ Input not found: {INPUT}. Run 03_process_era5.py first.")
        return 1

    df = pd.read_parquet(INPUT)
    k0, c0, sigma_c = base_weibull_and_iav(df)
    print(f"Base Weibull: k={k0:.4f}, c={c0:.4f}")
    print(f"Inter-annual σ(c) = {sigma_c:.4f} "
          f"(CoV {sigma_c/c0*100:.1f}%)")

    v_grid, p_grid = make_power_grid()
    rng = np.random.default_rng(SEED)

    # --- sample inputs ---
    k_s = rng.normal(k0, 0.04, N_ITER)
    c_s = rng.normal(c0, sigma_c, N_ITER)
    wake_s = rng.triangular(0.05, WAKE_LOSS_DEFAULT, 0.12, N_ITER)
    avail_s = rng.triangular(0.92, AVAILABILITY_DEFAULT, 0.97, N_ITER)
    elec_s = rng.triangular(0.02, ELECTRICAL_LOSS_DEFAULT, 0.04, N_ITER)
    grid_s = rng.triangular(GRID_CO2.low, GRID_CO2.best, GRID_CO2.high, N_ITER)
    lca_s = rng.triangular(OFFSHORE_WIND_CO2.low, OFFSHORE_WIND_CO2.best,
                           OFFSHORE_WIND_CO2.high, N_ITER)

    # --- iterate ---
    print(f"\nRunning {N_ITER:,} iterations …")
    net_aep_turb = np.zeros(N_ITER)   # GWh/yr per turbine
    cf_net = np.zeros(N_ITER)
    for i in range(N_ITER):
        gross_kwh, gross_cf = aep_from_weibull(k_s[i], c_s[i], v_grid, p_grid)
        nf = (1 - wake_s[i]) * avail_s[i] * (1 - elec_s[i])
        net_aep_turb[i] = gross_kwh * nf / 1e6
        cf_net[i] = gross_cf * nf

    aep_per_mw = net_aep_turb / TURBINE.rated_power_mw          # GWh/yr/MW
    avoided_kwh = grid_s - lca_s                                # gCO2/kWh
    avoided_per_mw = aep_per_mw * 1e6 * avoided_kwh / 1e6       # tCO2/yr/MW

    # --- report ---
    print("\n=== Per-MW results ===")
    r_aep = pctl(aep_per_mw)
    r_cf = pctl(cf_net * 100)
    r_av = pctl(avoided_per_mw)
    print(f"Net AEP/MW (GWh/yr/MW): P10={r_aep['p10']:.3f} "
          f"P50={r_aep['p50']:.3f} P90={r_aep['p90']:.3f}")
    print(f"Net CF (%):             P10={r_cf['p10']:.1f} "
          f"P50={r_cf['p50']:.1f} P90={r_cf['p90']:.1f}")
    print(f"Avoided CO2 (t/yr/MW):  P10={r_av['p10']:.0f} "
          f"P50={r_av['p50']:.0f} P90={r_av['p90']:.0f}")
    print(f"AEP CoV: {r_aep['std']/r_aep['mean']*100:.1f}%")

    # --- scenarios ---
    scen_out = []
    print("\n=== Scenario farm totals ===")
    for s in SCENARIOS:
        farm_aep = net_aep_turb * s.n_turbines / 1000.0       # TWh/yr
        farm_co2 = avoided_per_mw * s.installed_mw / 1e6      # Mt/yr
        ra, rc = pctl(farm_aep), pctl(farm_co2)
        scen_out.append({
            "name": s.name, "installed_mw": s.installed_mw,
            "n_turbines": s.n_turbines,
            "farm_aep_twh": ra, "avoided_co2_mt": rc,
        })
        print(f"  {s.name:10s} ({s.installed_mw:6.1f} MW): "
              f"AEP P50={ra['p50']:.2f} TWh/yr | "
              f"CO2 P50={rc['p50']:.2f} Mt/yr")

    results = {
        "site": SITE.full_name,
        "n_iterations": N_ITER, "seed": SEED,
        "base_weibull": {"k": k0, "c": c0, "sigma_c_interannual": sigma_c},
        "sampling": {
            "k": "Normal(k0, 0.04)",
            "c": f"Normal(c0, {sigma_c:.4f})",
            "wake": "Triangular(0.05, 0.08, 0.12)",
            "availability": "Triangular(0.92, 0.95, 0.97)",
            "electrical": "Triangular(0.02, 0.03, 0.04)",
            "grid_co2": f"Triangular({GRID_CO2.low}, {GRID_CO2.best}, {GRID_CO2.high})",
            "lca_co2": f"Triangular({OFFSHORE_WIND_CO2.low}, {OFFSHORE_WIND_CO2.best}, {OFFSHORE_WIND_CO2.high})",
        },
        "per_mw": {
            "net_aep_gwh_per_mw": r_aep,
            "net_cf_pct": r_cf,
            "avoided_co2_t_per_mw": r_av,
        },
        "scenarios": scen_out,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    # store the raw per-MW arrays compactly for figure generation
    np.savez_compressed(RESULTS_DIR / "monte_carlo_samples.npz",
                        aep_per_mw=aep_per_mw, cf_net=cf_net,
                        avoided_per_mw=avoided_per_mw)
    OUTPUT.write_text(json.dumps(results, indent=2))
    print(f"\n✓ Saved: {OUTPUT}")
    print(f"✓ Samples: {RESULTS_DIR / 'monte_carlo_samples.npz'}")
    print("\nNext step: python scripts/07_compare_with_grid.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
