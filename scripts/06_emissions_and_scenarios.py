"""
06 — Avoided operational CO2, life-cycle GHG and active scenarios (revised)
============================================================================
Replaces the retired Monte Carlo emissions step (scripts/legacy/06_run_monte_carlo.py)
and national-context step (scripts/legacy/07_compare_with_grid.py).

Reads ONLY results/revised/energy_yield.json and
results/revised/interannual_and_sampling.json (written by script 04), plus
config.emissions and config.turbine.ACTIVE_SCENARIOS.

  PRIMARY    avoided operational grid CO2 = E_net x 0.6242 tCO2/MWh (2023
             wind/solar combined margin, CO2 only).
  CONTEXT    operating margin, build margin, generation average (CO2 and CO2-eq):
             labelled accounting conventions, not statistical bounds.
  SECONDARY  life-cycle GHG of the wind generation, tCO2-eq, reported
             separately (never subtracted from the CO2-only grid factor).
  Intervals  only the energy sampling CI of the period mean (t-interval from
             the annual values of the primary period) propagated through a
             fixed 2023 factor; not total carbon uncertainty.

Outputs: results/revised/emissions.json, results/revised/scenarios.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.site import RESULTS_DIR
from config.turbine import ACTIVE_SCENARIOS, RETIRED_SCENARIOS, TURBINE_SPACING_ASSUMPTION
from config.emissions import (GRID_EF_2023, PRIMARY_GRID_FACTOR, LIFECYCLE_GHG_G_PER_KWH,
                              LIFECYCLE_REFERENCE, TR_OFFSHORE_TARGET_2035_GW,
                              TR_TOTAL_CONSUMPTION_TWH_2024)

REV = RESULTS_DIR / "revised"
STATUS = "PRE-SUBMISSION MODEL ESTIMATE — not a validated project forecast"


def ci_label(period: str) -> str:
    return (f"energy SAMPLING uncertainty of the {period} mean only, through a fixed 2023 factor; "
            "not total carbon uncertainty")


def load_energy(rev: Path = REV) -> dict:
    ey = json.loads((rev / "energy_yield.json").read_text())
    s = json.loads((rev / "interannual_and_sampling.json").read_text())["sampling_ci_of_period_mean"]
    if ey.get("period") != s["period"]:
        raise ValueError(f"period mismatch: energy {ey.get('period')} vs sampling CI {s['period']}")
    lo, hi = s["primary_t_interval_90"]["net_gwh_per_mw"]
    return {"net_mwh_per_mw_yr": ey["net_mwh_per_mw_yr"],
            "net_mwh_per_mw_yr_ci90_sampling": [lo * 1000.0, hi * 1000.0],
            "net_cf": ey["net_cf"], "power_curve": ey["power_curve"], "estimator": ey["estimator"],
            "period": ey["period"], "input_series": ey["input"]["series_key"],
            "source": "results/revised/energy_yield.json; interannual_and_sampling.json (t-interval)"}


def compute(rev: Path = REV) -> tuple[dict, dict]:
    e = load_energy(rev)
    CI_LABEL = ci_label(e["period"])
    E = e["net_mwh_per_mw_yr"]
    lo, hi = e["net_mwh_per_mw_yr_ci90_sampling"]
    pf = GRID_EF_2023[PRIMARY_GRID_FACTOR]
    cm = pf.value

    emissions = {
        "status": STATUS,
        "energy_input": e,
        "primary_avoided_operational_co2": {
            "factor": PRIMARY_GRID_FACTOR, "factor_value": cm, "factor_unit": pf.unit, "source": pf.source,
            "t_co2_per_mw_yr": E * cm,
            "ci90_t_co2_per_mw_yr": [lo * cm, hi * cm], "ci_label": CI_LABEL,
            "unit": "tCO2 per MW installed per year (MWh x tCO2/MWh)",
            "note": "static 2023 factor; not a forecast of future grid displacement",
        },
        "context_grid_methods": {
            k: {"factor_value": f.value, "factor_unit": f.unit, "role": f.role, "source": f.source,
                "result_per_mw_yr": E * f.value,
                "result_unit": "tCO2-eq/MW/yr" if f.unit.startswith("tCO2-eq") else "tCO2/MW/yr",
                "rel_to_primary_pct": (f.value / cm - 1) * 100}
            for k, f in GRID_EF_2023.items() if k != PRIMARY_GRID_FACTOR},
        "secondary_lifecycle_ghg": {
            "unit": "tCO2-eq per MW installed per year (MWh x gCO2-eq/kWh / 1000)",
            "reference_case": LIFECYCLE_REFERENCE,
            "cases": {k: {"g_co2eq_per_kwh": g, "t_co2eq_per_mw_yr": E * g / 1000.0}
                      for k, g in LIFECYCLE_GHG_G_PER_KWH.items()},
            "not_subtracted_from_primary": "different gases (CO2-eq vs CO2) and system boundaries "
                                           "(cradle-to-grave wind vs combustion-only grid factor)",
            "note": "literature intensities for other (windier) sites; not Saros-specific",
        },
    }

    lc_ref = LIFECYCLE_GHG_G_PER_KWH[LIFECYCLE_REFERENCE] / 1000.0
    rows = []
    for s in ACTIVE_SCENARIOS:
        mw = s.installed_mw
        rows.append({
            "name": s.name, "description": s.description, "n_turbines": s.n_turbines, "installed_mw": mw,
            "net_energy_gwh_yr": E * mw / 1000.0,
            "net_energy_gwh_yr_ci90_sampling": [lo * mw / 1000.0, hi * mw / 1000.0],
            "avoided_co2_cm_kt_yr": E * mw * cm / 1000.0,
            "avoided_co2_cm_kt_yr_ci90_sampling": [lo * mw * cm / 1000.0, hi * mw * cm / 1000.0],
            "context_operating_margin_kt_co2_yr": E * mw * GRID_EF_2023["operating_margin"].value / 1000.0,
            "context_generation_average_kt_co2_yr": E * mw * GRID_EF_2023["generation_average_co2"].value / 1000.0,
            "lifecycle_ghg_kt_co2eq_yr_reference": E * mw * lc_ref / 1000.0,
            "lifecycle_ghg_kt_co2eq_yr_ipcc_range": [E * mw * LIFECYCLE_GHG_G_PER_KWH["ipcc_ar5_min"] / 1e6,
                                                     E * mw * LIFECYCLE_GHG_G_PER_KWH["ipcc_ar5_max"] / 1e6],
            "share_of_2035_offshore_target_capacity_pct": mw / (TR_OFFSHORE_TARGET_2035_GW * 1000.0) * 100,
            "share_of_2024_consumption_pct": E * mw / 1e6 / TR_TOTAL_CONSUMPTION_TWH_2024 * 100,
        })
    scenarios = {
        "status": STATUS,
        "label": "ILLUSTRATIVE capacities; same per-MW estimator and nominal losses for all; "
                 "one wake value for all densities is a simplification",
        "spacing_assumption": TURBINE_SPACING_ASSUMPTION,
        "consumption_reference": {"twh": TR_TOTAL_CONSUMPTION_TWH_2024,
                                  "note": "manuscript value; primary TEİAŞ document not verified in the review"},
        "retired": RETIRED_SCENARIOS,
        "scenarios": rows,
    }
    return emissions, scenarios


def main() -> int:
    if not (REV / "energy_yield.json").exists():
        print("✗ results/revised/energy_yield.json missing — run scripts/04_fit_weibull_aep.py first")
        return 1
    emissions, scenarios = compute()
    (REV / "emissions.json").write_text(json.dumps(emissions, indent=2, ensure_ascii=False))
    (REV / "scenarios.json").write_text(json.dumps(scenarios, indent=2, ensure_ascii=False))
    p = emissions["primary_avoided_operational_co2"]
    print(f"Avoided CO2 (CM): {p['t_co2_per_mw_yr']:.1f} tCO2/MW/yr "
          f"[{p['ci90_t_co2_per_mw_yr'][0]:.0f}-{p['ci90_t_co2_per_mw_yr'][1]:.0f}, sampling only]")
    for r in scenarios["scenarios"]:
        print(f"  {r['name']}: {r['installed_mw']:.1f} MW  {r['net_energy_gwh_yr']:.1f} GWh/yr  "
              f"{r['avoided_co2_cm_kt_yr']:.1f} kt CO2/yr")
    print(f"✓ wrote {REV / 'emissions.json'}, {REV / 'scenarios.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
