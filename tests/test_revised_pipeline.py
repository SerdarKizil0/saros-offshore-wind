"""
Phase 4B — consistency tests for the revised production pipeline (results/revised/).
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REV = ROOT / "results" / "revised"
P3A = ROOT / "results/provisional/phase3a/energy_uncertainty.json"
P3B = ROOT / "results/provisional/phase3b/carbon_accounting.json"
P2B = ROOT / "results/provisional/phase2b/wind_speed_sensitivity.json"
P4A = ROOT / "results/provisional/phase4a/site_checks.json"
PRODUCTION = ["scripts/04_fit_weibull_aep.py", "scripts/06_emissions_and_scenarios.py",
              "scripts/07_site_screening.py", "scripts/run_revised_pipeline.py"]
PARQUET = ROOT / "data/processed/wind_hub_105m.parquet"
pytestmark = pytest.mark.skipif(not PARQUET.exists(), reason="parquet not available")


def J(name):
    return json.loads((REV / name).read_text())


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------ headline values vs Phase 3A/3B
def test_energy_matches_phase3a():
    ey, p3 = J("energy_yield.json"), json.loads(P3A.read_text())
    assert ey["estimator"].startswith("empirical hourly")
    assert ey["net_cf"] == pytest.approx(p3["central_estimate"]["net_cf"], rel=1e-12)
    assert ey["net"]["gwh_per_mw"] == pytest.approx(p3["central_estimate"]["net"]["gwh_per_mw"], rel=1e-12)
    assert ey["net"]["gwh_per_mw"] == pytest.approx(2.4274, abs=1e-4)
    assert ey["net_cf"] == pytest.approx(0.2769, abs=1e-4)


def test_sampling_ci_and_variability_match_phase3a():
    s, p3 = J("interannual_and_sampling.json"), json.loads(P3A.read_text())
    t = s["sampling_ci_of_11yr_mean"]["primary_t_interval_90"]["gross_cf"]
    assert t == pytest.approx(p3["sampling_uncertainty_of_mean"]["t_interval_90_gross_cf"], rel=1e-12)
    b = s["sampling_ci_of_11yr_mean"]["check_bootstrap_90"]["net_gwh_per_mw"]
    assert b == pytest.approx(p3["sampling_uncertainty_of_mean"]["net_gwh_per_mw_ci90"], rel=1e-12)
    v = s["observed_interannual_variability"]
    assert v["annual_net_cf_cov_pct"] == pytest.approx(p3["interannual_variability"]["annual_cov_pct"], rel=1e-12)


def test_emissions_match_phase3b_and_use_same_energy():
    em, ey, p3b = J("emissions.json"), J("energy_yield.json"), json.loads(P3B.read_text())
    assert em["energy_input"]["net_mwh_per_mw_yr"] == pytest.approx(ey["net_mwh_per_mw_yr"], rel=1e-15)
    p = em["primary_avoided_operational_co2"]
    assert p["factor_value"] == 0.6242 and p["factor_unit"] == "tCO2/MWh"
    assert p["t_co2_per_mw_yr"] == pytest.approx(ey["net_mwh_per_mw_yr"] * 0.6242, rel=1e-12)
    assert p["t_co2_per_mw_yr"] == pytest.approx(p3b["primary_avoided_co2"]["value"], rel=1e-12)
    assert p["t_co2_per_mw_yr"] == pytest.approx(1515.2, abs=0.1)
    assert p["ci90_t_co2_per_mw_yr"] == pytest.approx(p3b["primary_avoided_co2"]["ci90_energy_sampling_only"], rel=1e-12)
    lc = em["secondary_lifecycle_ghg"]
    assert lc["unit"].startswith("tCO2-eq")
    assert lc["cases"]["ipcc_ar5_median"]["t_co2eq_per_mw_yr"] == pytest.approx(
        p3b["secondary_lifecycle_ghg"]["cases"]["ipcc_ar5_median"]["t_co2eq_per_mw_yr"], rel=1e-12)


def test_context_methods_units():
    c = J("emissions.json")["context_grid_methods"]
    assert c["generation_average_co2eq"]["result_unit"] == "tCO2-eq/MW/yr"
    for k in ("operating_margin", "build_margin", "generation_average_co2"):
        assert c[k]["result_unit"] == "tCO2/MW/yr"
    assert "combined_margin_wind_solar" not in c


def test_cm_reproduced_from_tool07_weights():
    from config.emissions import GRID_EF_2023 as G, CM_TOOL07_WEIGHTS_WIND_SOLAR as W
    assert W[0] * G["operating_margin"].value + W[1] * G["build_margin"].value == pytest.approx(
        G["combined_margin_wind_solar"].value, abs=5e-5)


# ---------------------------------------------------------------- scenarios
def test_active_scenarios_only_and_s4_absent_everywhere():
    sc = J("scenarios.json")
    assert [r["name"] for r in sc["scenarios"]] == ["S1", "S2", "S3"]
    E = J("energy_yield.json")["net_mwh_per_mw_yr"]
    for r in sc["scenarios"]:
        assert r["net_energy_gwh_yr"] == pytest.approx(E * r["installed_mw"] / 1000, rel=1e-12)
        assert r["avoided_co2_cm_kt_yr"] == pytest.approx(E * r["installed_mw"] * 0.6242 / 1000, rel=1e-12)
    # S4 only appears as a retirement note, never as a result row
    for f in REV.glob("*.json"):
        d = json.loads(f.read_text())
        rows = d.get("scenarios") if isinstance(d.get("scenarios"), list) else []
        rows += d.get("active_scenarios_density", [])
        assert not any("S4" in r.get("name", "") for r in rows), f
        assert "1738.5" not in f.read_text(), f
    assert "S4_max" in sc["retired"]


def test_s3_matches_phase3b_historical_s3():
    s3 = next(r for r in J("scenarios.json")["scenarios"] if r["name"] == "S3")
    ref = next(r for r in json.loads(P3B.read_text())["scenarios"] if r["name"] == "S3_phase2")
    assert s3["installed_mw"] == ref["installed_mw"] == 997.5
    assert s3["avoided_co2_cm_kt_yr"] == pytest.approx(ref["avoided_co2_cm_kt_yr"], rel=1e-12)


# -------------------------------------------------------- normalisation, units
def test_leap_year_normalisation_and_energy_conservation():
    ey = J("energy_yield.json")
    n = ey["normalisation_check"]
    assert n["n_hours"] == 96432 and n["n_years"] == 11 and n["leap_years"] == [2016, 2020, 2024]
    assert n["relative_difference_vs_8766h"] == pytest.approx((96432 / 11) / 8766 - 1, abs=1e-12)
    tab = pd.read_csv(REV / "annual_energy.csv")
    assert list(tab.hours) == [8784 if y in (2016, 2020, 2024) else 8760 for y in tab.year]
    assert tab.gross_kwh.sum() / (9500 * tab.hours.sum()) == pytest.approx(ey["gross_cf"], rel=1e-9)
    assert ey["gross"]["gwh_per_turbine"] == pytest.approx(ey["gross_cf"] * 9.5 * 8766 / 1000, rel=1e-12)
    assert ey["net"]["gwh_per_mw"] == pytest.approx(ey["net_cf"] * 8.766, rel=1e-12)


def test_weibull_is_crosscheck_only():
    w = J("weibull_crosscheck.json")
    assert "cross-check" in w["role"] and "not the energy estimator" in w["role"]
    assert w["relative_difference_pct"] == pytest.approx(-1.85, abs=0.01)
    assert w["gross_cf_empirical"] == J("energy_yield.json")["gross_cf"]


# ------------------------------------------------------- labelling of intervals
def test_interval_types_distinctly_labelled():
    s = J("interannual_and_sampling.json")
    assert s["observed_interannual_variability"]["label"].startswith("OBSERVED")
    assert s["sampling_ci_of_11yr_mean"]["label"].startswith("SAMPLING")
    assert J("wind_speed_sensitivity.json")["label"].startswith("SENSITIVITY")
    assert J("loss_scenarios.json")["label"].startswith("LOSS SCENARIOS")
    assert "not total carbon uncertainty" in J("emissions.json")["primary_avoided_operational_co2"]["ci_label"]
    for f in REV.glob("*.json"):
        if f.name != "MANIFEST.json":
            assert json.loads(f.read_text())["status"].startswith("PRE-SUBMISSION"), f


def test_wind_speed_sensitivity_matches_phase2b():
    new = {round(c["speed_factor"], 4): c for c in J("wind_speed_sensitivity.json")["cases"]}
    old = {round(c["speed_factor"], 4): c for c in json.loads(P2B.read_text())["cases"]}
    for f in (0.9, 0.95, 1.0, 1.05, 1.1):
        assert new[f]["aep_change_vs_baseline_pct"] == pytest.approx(old[f]["aep_change_vs_baseline_pct"], abs=0.006)
    gwa = [c for c in new.values() if "GWA" in c["case"]]
    assert len(gwa) == 1 and gwa[0]["speed_factor"] == pytest.approx(1.1014, abs=1e-4)


# --------------------------------------------------------------- screening
def test_screening_matches_documented_geometry():
    s, p4 = J("site_screening.json"), json.loads(P4A.read_text())
    assert s["protected_area_overlap"]["saros_ock_2010"]["overlap_km2"] == pytest.approx(p4["ock_overlap_km2"], rel=1e-12)
    assert s["screening_classes_best_fit_layout"]["inside_saros_ock_2010"] == \
        p4["screening_of_best_prevailing_axis_layout"]["inside_saros_ock_2010"] == 25
    b = s["bathymetry"]["depth_m"]
    assert (round(b["min"], 1), round(b["median"], 1), round(b["max"], 1)) == (1.0, 27.8, 61.6)   # Phase 1
    assert s["bathymetry"]["inside_polygon_deeper_than_200m_cells"] == 0
    n = s["era5_node_representativeness"]
    assert n["inside_polygon"] is False
    assert n["distance_to_polygon_boundary_km"] == pytest.approx(3.68, abs=0.05)
    assert n["polygon_share_nearest_to_this_node_pct"] == pytest.approx(62.6, abs=0.5)
    assert [r["name"] for r in s["active_scenarios_density"]] == ["S1", "S2", "S3"]


# ------------------------------------------------- no stale inputs in active code
def test_production_code_reads_no_outdated_results():
    banned = ["monte_carlo_samples", "monte_carlo_results", "comparison_results",
              "weibull_aep_results", "results/archive", "results/provisional", "GRID_CO2",
              "OFFSHORE_WIND_CO2", "POWER_CURVE_ORIGINAL", "S4_max\""]
    for rel in PRODUCTION:
        src = (ROOT / rel).read_text()
        for b in banned:
            assert b not in src, f"{rel} references {b}"
        # the historical SCENARIOS list (with S4) must not be used as an identifier
        tree = ast.parse(src)
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        names |= {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
        assert "SCENARIOS" not in names and "DEFAULT_SCENARIO" not in names, f"{rel} uses historical SCENARIOS"
    assert not list((ROOT / "results").glob("*.json")) and not list((ROOT / "results").glob("*.npz"))


def test_manifest_checksums():
    m = J("MANIFEST.json")
    assert len(m["files"]) == 10
    for f, meta in m["files"].items():
        assert hashlib.sha256((REV / f).read_bytes()).hexdigest() == meta["sha256"], f
    assert m["inputs"]["wind_series_sha256"] == hashlib.sha256(PARQUET.read_bytes()).hexdigest()


def test_revised_outputs_reproduce_from_fresh_computation():
    s04 = _load("s04", "scripts/04_fit_weibull_aep.py")
    res = s04.compute(pd.read_parquet(PARQUET))
    res.pop("_annual_table")
    for name, obj in res.items():
        assert json.loads(json.dumps(obj, ensure_ascii=False)) == J(name), name
    s06 = _load("s06n", "scripts/06_emissions_and_scenarios.py")
    em, sc = s06.compute()
    assert json.loads(json.dumps(em, ensure_ascii=False)) == J("emissions.json")
    assert json.loads(json.dumps(sc, ensure_ascii=False)) == J("scenarios.json")


def test_config_has_no_unsupported_claims():
    src = (ROOT / "config/emissions.py").read_text() + (ROOT / "config/turbine.py").read_text()
    assert "IPCC 2025" not in src and "IPCC AR6/2025" not in src
    assert not re.search(r"no recycling credit.*conservative", src, re.I)
