"""
07 — Comparison with conventional supply + context (Saros Bay)
===============================================================
Combines the Monte Carlo AEP / avoided-CO2 distributions with national
context figures to express results in policy-legible terms.

Context references (energy basis):
  • Türkiye total electricity consumption 2024: 347.9 TWh  [TEİAŞ/TEDAŞ]
  • Türkiye 2035 offshore wind target: 5 GW  [ETKB roadmap; World Bank 2024]
  • Istanbul annual consumption: optional (set ISTANBUL_TWH below once
    an official figure is confirmed). Left None → that line is skipped.

Inputs : results/monte_carlo_results.json, results/monte_carlo_samples.npz
Outputs: results/comparison_results.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from config.site import SITE, RESULTS_DIR
from config.turbine import SCENARIOS, DEFAULT_SCENARIO
from config.emissions import GRID_CO2, OFFSHORE_WIND_CO2, TR_OFFSHORE_TARGET_2035_GW

MC_JSON = RESULTS_DIR / "monte_carlo_results.json"
MC_NPZ  = RESULTS_DIR / "monte_carlo_samples.npz"
OUTPUT  = RESULTS_DIR / "comparison_results.json"

# --- National context (verified) ---
TR_TOTAL_CONSUMPTION_TWH_2024 = 347.9    # TEİAŞ/TEDAŞ 2024
# Istanbul: official city-level TWh not readily published; leave None
# until confirmed, or set an explicit verified value.
ISTANBUL_TWH = None    # e.g. 70.0 (≈20% of national) — VERIFY before use

# A 5 GW offshore fleet at the Saros-class net capacity factor would
# generate roughly this much (using P50 per-MW yield, computed below).


def pctl(a):
    p = np.percentile(a, [10, 50, 90])
    return {"p10": float(p[0]), "p50": float(p[1]), "p90": float(p[2])}


def main() -> int:
    print("=" * 72)
    print(" Comparison with conventional supply — Saros Bay")
    print("=" * 72)
    if not MC_NPZ.exists():
        print(f"✗ {MC_NPZ} not found. Run 06_run_monte_carlo.py first.")
        return 1

    s = np.load(MC_NPZ)
    aep_per_mw = s["aep_per_mw"]              # GWh/yr/MW
    avoided_per_mw = s["avoided_per_mw"]      # tCO2/yr/MW

    p_aep = pctl(aep_per_mw)
    print(f"\nNet AEP per MW (GWh/yr/MW): "
          f"P10={p_aep['p10']:.3f} P50={p_aep['p50']:.3f} P90={p_aep['p90']:.3f}")

    # --- 5 GW national-target equivalent (energy a Saros-class 5 GW fleet makes) ---
    target_mw = TR_OFFSHORE_TARGET_2035_GW * 1000
    target_energy_twh = aep_per_mw * target_mw / 1000.0   # GWh→TWh
    p_te = pctl(target_energy_twh)
    print(f"\nIf the 5 GW 2035 target had Saros-class yield:")
    print(f"  {p_te['p50']:.1f} TWh/yr (P50)  "
          f"= {p_te['p50']/TR_TOTAL_CONSUMPTION_TWH_2024*100:.1f}% of national demand")

    # --- per-scenario context ---
    scen_rows = []
    print(f"\n=== Scenario context (vs {TR_TOTAL_CONSUMPTION_TWH_2024} TWh national) ===")
    for sc in SCENARIOS:
        farm_aep_twh = aep_per_mw * sc.installed_mw / 1000.0      # TWh/yr dist
        farm_co2_mt  = avoided_per_mw * sc.installed_mw / 1e6     # Mt/yr dist
        pct_national = farm_aep_twh / TR_TOTAL_CONSUMPTION_TWH_2024 * 100
        pct_target_cap = sc.installed_mw / target_mw * 100

        pa, pc, pn = pctl(farm_aep_twh), pctl(farm_co2_mt), pctl(pct_national)
        row = {
            "name": sc.name, "installed_mw": sc.installed_mw,
            "n_turbines": sc.n_turbines,
            "farm_aep_twh": pa, "avoided_co2_mt": pc,
            "pct_of_national_demand": pn,
            "pct_of_2035_target_capacity": pct_target_cap,
        }
        if ISTANBUL_TWH:
            row["pct_of_istanbul_demand"] = pctl(farm_aep_twh / ISTANBUL_TWH * 100)
        scen_rows.append(row)

        line = (f"  {sc.name:10s} ({sc.installed_mw:6.1f} MW): "
                f"AEP P50={pa['p50']:.2f} TWh/yr "
                f"({pn['p50']:.1f}% national) | "
                f"CO2 P50={pc['p50']:.2f} Mt/yr | "
                f"{pct_target_cap:.0f}% of 5 GW target")
        print(line)

    # --- headline for default scenario (S3 ~1 GW) ---
    d = next(r for r in scen_rows if r["name"] == DEFAULT_SCENARIO.name)
    print(f"\n=== HEADLINE ({DEFAULT_SCENARIO.name}, "
          f"{DEFAULT_SCENARIO.installed_mw:.0f} MW) ===")
    print(f"  Annual generation : {d['farm_aep_twh']['p50']:.2f} TWh/yr "
          f"[{d['farm_aep_twh']['p10']:.2f}–{d['farm_aep_twh']['p90']:.2f}]")
    print(f"  Avoided CO2       : {d['avoided_co2_mt']['p50']:.2f} Mt/yr "
          f"[{d['avoided_co2_mt']['p10']:.2f}–{d['avoided_co2_mt']['p90']:.2f}]")
    print(f"  Share of national : {d['pct_of_national_demand']['p50']:.1f}%")

    results = {
        "site": SITE.full_name,
        "context": {
            "tr_total_consumption_twh_2024": TR_TOTAL_CONSUMPTION_TWH_2024,
            "tr_offshore_target_2035_gw": TR_OFFSHORE_TARGET_2035_GW,
            "istanbul_twh": ISTANBUL_TWH,
            "grid_co2_primary": GRID_CO2.best,
            "offshore_lca_co2": OFFSHORE_WIND_CO2.best,
        },
        "five_gw_target_energy_twh": p_te,
        "scenarios": scen_rows,
        "headline_scenario": DEFAULT_SCENARIO.name,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=2))
    print(f"\n✓ Saved: {OUTPUT}")
    if ISTANBUL_TWH is None:
        print("\nNote: Istanbul context skipped (ISTANBUL_TWH not set). "
              "Set it once an official figure is confirmed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
