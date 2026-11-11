"""
Phase 3B — corrected avoided-emissions accounting (provisional)
================================================================
Separates three quantities that the original model mixed:

  1. PRIMARY  — avoided operational grid CO2 (tCO2, CO2 only), from the
     official 2023 combined-margin factor for wind/solar (ETKB/EVÇED,
     UNFCCC CDM Tool 07 v07.0).
  2. SECONDARY — life-cycle GHG emissions attributable to the wind
     generation itself (tCO2-eq), from literature per-kWh intensities.
     Reported separately; NOT subtracted from (1), because the units
     (CO2 vs CO2-eq) and system boundaries (combustion-only grid factor vs
     cradle-to-grave wind) differ.
  3. CONTEXT  — alternative grid-accounting conventions (operating margin,
     build margin, generation average). These are different methods, not
     statistical bounds.

Energy input: Phase 3A central net yield (empirical hourly, OEDB curve,
nominal losses), plus its sampling-only 90 % t-interval.

All factors are static 2023 historical values, not forecasts.
Writes only results/provisional/phase3b/carbon_accounting.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.turbine import SCENARIOS

P3A = ROOT / "results" / "provisional" / "phase3a" / "energy_uncertainty.json"
BASELINE = ROOT / "results" / "archive" / "baseline_original_curve"
P2A = ROOT / "results" / "provisional" / "phase2a"
OUT = ROOT / "results" / "provisional" / "phase3b"

URL_GRID = ("https://enerji.gov.tr/Media/Dizin/EVCED/tr/%C3%87evreVe%C4%B0klim/"
            "%C4%B0klimDe%C4%9Fi%C5%9Fikli%C4%9Fi/TUESEmisyonFktr/Belgeler/Sebeke_EF_Bilgi_Formu_2023.pdf")
URL_GEN = ("https://enerji.gov.tr/Media/Dizin/EVCED/tr/%C3%87evreVe%C4%B0klim/"
           "%C4%B0klimDe%C4%9Fi%C5%9Fikli%C4%9Fi/EmisyonFaktorleri/"
           "2023_Turkiye_Elektrik_UretimiveElektrik_Tuketim_Noktasi_Emisyon_Faktorleri.pdf")

# ---- Grid factors, t/MWh, verified against the official 2023 forms ----------
GRID = {
    "combined_margin_wind_solar": {
        "value": 0.6242, "unit": "tCO2/MWh", "gas": "CO2",
        "role": "PRIMARY (official factor published for GHG-reduction calculations of wind/solar generation)",
        "source": "ETKB-EVÇED-FRM-039 Rev.03, calculation period 2023, published 26.12.2025, p.2",
        "url": URL_GRID, "sha256": "0b4d25584cbe63a386941b2815f792aaa79ea66a2f5d4125a170ef54c50e81c4"},
    "operating_margin": {
        "value": 0.7134, "unit": "tCO2/MWh", "gas": "CO2",
        "role": "context: short-run displacement of existing generation",
        "source": "ETKB-EVÇED-FRM-039 Rev.03 (2023), p.1", "url": URL_GRID,
        "sha256": "0b4d25584cbe63a386941b2815f792aaa79ea66a2f5d4125a170ef54c50e81c4"},
    "build_margin": {
        "value": 0.3567, "unit": "tCO2/MWh", "gas": "CO2",
        "role": "context: recent capacity additions (component of the combined margin)",
        "source": "ETKB-EVÇED-FRM-039 Rev.03 (2023), p.1", "url": URL_GRID,
        "sha256": "0b4d25584cbe63a386941b2815f792aaa79ea66a2f5d4125a170ef54c50e81c4"},
    "generation_average_co2": {
        "value": 0.430, "unit": "tCO2/MWh", "gas": "CO2",
        "role": "context: attributional average of all generation (IEA method)",
        "source": "ETKB-EVÇED-FRM-042 Rev.01, calculation period 2023, published 26.12.2025, p.1",
        "url": URL_GEN, "sha256": "9c88c77e97a8e03ef3e4e4d404f7e039fb6aba0ea6e27093da4858eaf7fff4a2"},
    "generation_average_co2eq": {
        "value": 0.434, "unit": "tCO2-eq/MWh", "gas": "CO2-eq (CO2+CH4+N2O)",
        "role": "context, different unit: same average including other GHGs",
        "source": "ETKB-EVÇED-FRM-042 Rev.01 (2023), p.1", "url": URL_GEN,
        "sha256": "9c88c77e97a8e03ef3e4e4d404f7e039fb6aba0ea6e27093da4858eaf7fff4a2"},
}
# CDM Tool 07 weights for wind/solar combined margin: 0.75 OM + 0.25 BM.
CM_WEIGHTS_WIND_SOLAR = (0.75, 0.25)

# ---- Life-cycle intensities of offshore wind, g CO2-eq/kWh (= kg/MWh) -------
LIFECYCLE = {
    "bonou2016_G4_4MW": {"value": 10.9, "note": "Bonou et al. 2016, Table 4; 4.0 MW-130 m, 9.5 m/s, "
                         "20 y, ~58.6 % CF to grid, EoL recycling credited", "energy_mwh_per_mw_yr": 20528 / 4.0},
    "bonou2016_D6_6MW": {"value": 7.8, "note": "Bonou et al. 2016, Table 4; 6.0 MW-154 m, 10 m/s, "
                         "25 y, ~59.1 % CF to grid, EoL recycling credited", "energy_mwh_per_mw_yr": 31045 / 6.0},
    "bonou2016_headline": {"value": 11.0, "note": "Bonou et al. 2016 abstract: offshore < 11 g CO2-eq/kWh"},
    "ipcc_ar5_min": {"value": 8.0, "note": "IPCC AR5 WGIII Annex III (Schlömer et al. 2014), Table A.III.2"},
    "ipcc_ar5_median": {"value": 12.0, "note": "IPCC AR5 WGIII Annex III, Table A.III.2 (reference value)"},
    "ipcc_ar5_max": {"value": 35.0, "note": "IPCC AR5 WGIII Annex III, Table A.III.2"},
}
LIFECYCLE_REFERENCE = "ipcc_ar5_median"


def load_energy():
    d = json.loads(P3A.read_text())
    nf = d["loss_scenarios"]["nominal"]["net_factor"]
    h = d["hours_per_average_year"]
    lo, hi = d["sampling_uncertainty_of_mean"]["t_interval_90_gross_cf"]
    return {
        "net_mwh_per_mw_yr": d["central_estimate"]["net"]["gwh_per_mw"] * 1000.0,
        "net_mwh_per_mw_yr_ci90_sampling": [lo * nf * h, hi * nf * h],
        "net_cf": d["central_estimate"]["net_cf"],
        "source": "results/provisional/phase3a/energy_uncertainty.json (central_estimate; t-interval)",
    }


def tonnes(mwh: float, factor_t_per_mwh: float) -> float:
    """MWh x t/MWh = t."""
    return mwh * factor_t_per_mwh


def compute():
    e = load_energy()
    E = e["net_mwh_per_mw_yr"]
    lo, hi = e["net_mwh_per_mw_yr_ci90_sampling"]

    cm = GRID["combined_margin_wind_solar"]["value"]
    primary = {
        "quantity": "avoided operational grid CO2 (combined margin, wind/solar, 2023)",
        "unit": "tCO2 per MW per year",
        "value": tonnes(E, cm),
        "ci90_energy_sampling_only": [tonnes(lo, cm), tonnes(hi, cm)],
        "ci_label": "propagates only the Phase 3A sampling uncertainty of the 2014-2024 mean "
                    "energy through a fixed 2023 factor; not total carbon uncertainty",
        "factor_t_per_mwh": cm,
    }

    lifecycle = {}
    for k, v in LIFECYCLE.items():
        lifecycle[k] = {"g_co2eq_per_kwh": v["value"], "note": v["note"],
                        "t_co2eq_per_mw_yr": tonnes(E, v["value"] / 1000.0),
                        "share_of_primary_pct_indicative": v["value"] / 1000.0 / cm * 100}
    # illustration: per-kWh intensity rescaled to Saros energy yield per MW
    # (assumes equal embodied emissions per MW and lifetime; not an estimate)
    cf_adjusted = {k: {"g_co2eq_per_kwh_scaled": LIFECYCLE[k]["value"] * LIFECYCLE[k]["energy_mwh_per_mw_yr"] / E,
                       "energy_ratio": LIFECYCLE[k]["energy_mwh_per_mw_yr"] / E}
                   for k in ("bonou2016_G4_4MW", "bonou2016_D6_6MW")}

    context = {}
    for k, v in GRID.items():
        context[k] = {"factor": v["value"], "unit_factor": v["unit"], "gas": v["gas"], "role": v["role"],
                      "per_mw_yr": tonnes(E, v["value"]),
                      "unit_result": "tCO2-eq/MW/yr" if "eq" in v["unit"] else "tCO2/MW/yr",
                      "rel_to_primary_pct": (v["value"] / cm - 1) * 100}

    scen = []
    for s in SCENARIOS:
        mwh = E * s.installed_mw
        scen.append({
            "name": s.name, "installed_mw": s.installed_mw, "n_turbines": s.n_turbines,
            "net_energy_gwh_yr": mwh / 1000.0,
            "net_energy_gwh_yr_ci90_sampling": [lo * s.installed_mw / 1000.0, hi * s.installed_mw / 1000.0],
            "avoided_co2_cm_kt_yr": tonnes(mwh, cm) / 1000.0,
            "avoided_co2_cm_kt_yr_ci90_sampling": [tonnes(lo * s.installed_mw, cm) / 1000.0,
                                                    tonnes(hi * s.installed_mw, cm) / 1000.0],
            "context_operating_margin_kt_co2_yr": tonnes(mwh, GRID["operating_margin"]["value"]) / 1000.0,
            "context_generation_average_kt_co2_yr": tonnes(mwh, GRID["generation_average_co2"]["value"]) / 1000.0,
            "lifecycle_ghg_kt_co2eq_yr_ipcc_median": tonnes(mwh, 0.012) / 1000.0,
            "lifecycle_ghg_kt_co2eq_yr_ipcc_range": [tonnes(mwh, 0.008) / 1000.0, tonnes(mwh, 0.035) / 1000.0],
        })

    # ---- relationship to previously reported values ----
    old = json.loads((BASELINE / "monte_carlo_results.json").read_text())["per_mw"]
    old_aep = old["net_aep_gwh_per_mw"]["p50"]; old_av = old["avoided_co2_t_per_mw"]
    p2a = json.loads((P2A / "monte_carlo_results.json").read_text())["per_mw"]["avoided_co2_t_per_mw"]
    legacy = {
        "original_reported_p50_t_per_mw": old_av["p50"],
        "original_reported_p10_p90": [old_av["p10"], old_av["p90"]],
        "original_energy_p50_gwh_per_mw": old_aep,
        "original_effective_factor_g_per_kwh": old_av["p50"] / old_aep,
        "original_grid_sampling": "Triangular(434 [gen. avg, CO2-eq], 624.2 [CM, CO2], 713.4 [OM, CO2]) "
                                  "minus Triangular(8, 11, 14) lifecycle CO2-eq",
        "phase2a_provisional_p50_t_per_mw": p2a["p50"],
        "new_primary_t_per_mw": primary["value"],
        "new_vs_original_pct": (primary["value"] / old_av["p50"] - 1) * 100,
        "energy_change_pct": (E / 1000.0 / old_aep - 1) * 100,
        "factor_change_pct": (cm * 1000.0 / (old_av["p50"] / old_aep) - 1) * 100,
        "interpretation": "near-equality is coincidental: energy fell ~7.4 % (power curve, estimator) "
                          "while the effective factor rose ~7.3 % (mixed-method median -> official CM)",
    }

    checks = {
        "cm_from_om_bm_tool07_weights": (CM_WEIGHTS_WIND_SOLAR[0] * GRID["operating_margin"]["value"]
                                         + CM_WEIGHTS_WIND_SOLAR[1] * GRID["build_margin"]["value"]),
        "cm_published": cm,
    }
    return {
        "status": "PROVISIONAL — Phase 3B accounting; static 2023 factors; energy from Phase 3A",
        "energy": e, "primary_avoided_co2": primary,
        "secondary_lifecycle_ghg": {"unit": "tCO2-eq per MW per year (g CO2-eq/kWh x MWh / 1000)",
                                    "reference_case": LIFECYCLE_REFERENCE, "cases": lifecycle,
                                    "illustrative_cf_adjusted_intensity": cf_adjusted,
                                    "not_subtracted_from_primary": "different gases (CO2-eq vs CO2) and "
                                    "boundaries (cradle-to-grave wind vs combustion-only grid factor)"},
        "context_grid_methods": context, "scenarios": scen,
        "legacy_comparison": legacy, "consistency_checks": checks,
    }


def main() -> int:
    out = compute()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "carbon_accounting.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    p = out["primary_avoided_co2"]
    print(f"Energy {out['energy']['net_mwh_per_mw_yr']:.2f} MWh/MW/yr; CI90 (sampling) "
          f"{out['energy']['net_mwh_per_mw_yr_ci90_sampling'][0]:.1f}-{out['energy']['net_mwh_per_mw_yr_ci90_sampling'][1]:.1f}")
    print(f"PRIMARY avoided CO2 (CM): {p['value']:.1f} tCO2/MW/yr  [sampling-only CI90 "
          f"{p['ci90_energy_sampling_only'][0]:.0f}-{p['ci90_energy_sampling_only'][1]:.0f}]")
    for k, v in out["context_grid_methods"].items():
        print(f"  context {k:<28s} {v['factor']:.4f} {v['unit_factor']:<12s} -> {v['per_mw_yr']:7.1f} "
              f"{v['unit_result']} ({v['rel_to_primary_pct']:+.1f}%)")
    for k, v in out["secondary_lifecycle_ghg"]["cases"].items():
        print(f"  lifecycle {k:<20s} {v['g_co2eq_per_kwh']:5.1f} g/kWh -> {v['t_co2eq_per_mw_yr']:6.1f} tCO2-eq/MW/yr "
              f"({v['share_of_primary_pct_indicative']:.1f}% of primary, indicative)")
    print("  CF-adjusted (illustrative):", {k: round(v["g_co2eq_per_kwh_scaled"], 1)
                                            for k, v in out["secondary_lifecycle_ghg"]["illustrative_cf_adjusted_intensity"].items()})
    for s in out["scenarios"]:
        print(f"  {s['name']:<10s} {s['installed_mw']:7.1f} MW  {s['net_energy_gwh_yr']:7.1f} GWh  "
              f"CM {s['avoided_co2_cm_kt_yr']:7.1f} kt CO2 [{s['avoided_co2_cm_kt_yr_ci90_sampling'][0]:.0f}-"
              f"{s['avoided_co2_cm_kt_yr_ci90_sampling'][1]:.0f}]  OM {s['context_operating_margin_kt_co2_yr']:7.1f}  "
              f"GA {s['context_generation_average_kt_co2_yr']:7.1f}  LCA {s['lifecycle_ghg_kt_co2eq_yr_ipcc_median']:5.1f} kt CO2-eq")
    lg = out["legacy_comparison"]
    print(f"Legacy: {lg['original_reported_p50_t_per_mw']:.0f} (eff. {lg['original_effective_factor_g_per_kwh']:.1f} g/kWh) "
          f"-> {lg['new_primary_t_per_mw']:.1f} ({lg['new_vs_original_pct']:+.2f}%); energy {lg['energy_change_pct']:+.2f}%, "
          f"factor {lg['factor_change_pct']:+.2f}%; Phase 2A {lg['phase2a_provisional_p50_t_per_mw']:.0f}")
    print("CM check:", out["consistency_checks"])
    print(f"✓ wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
