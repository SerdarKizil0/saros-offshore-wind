"""
Tests for the Phase 3B carbon accounting.
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "results" / "provisional" / "phase3b" / "carbon_accounting.json"


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("p3b", ROOT / "scripts/phase3b_carbon_accounting.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def res(m):
    return m.compute()


def test_official_factors_and_units(m):
    g = m.GRID
    assert g["combined_margin_wind_solar"]["value"] == 0.6242
    assert g["operating_margin"]["value"] == 0.7134
    assert g["build_margin"]["value"] == 0.3567
    assert g["generation_average_co2"]["value"] == 0.430
    assert g["generation_average_co2eq"]["value"] == 0.434
    assert g["generation_average_co2eq"]["unit"] == "tCO2-eq/MWh"
    for k in ("combined_margin_wind_solar", "operating_margin", "build_margin", "generation_average_co2"):
        assert g[k]["unit"] == "tCO2/MWh" and g[k]["gas"] == "CO2"


def test_combined_margin_reproduced_from_tool07_weights(res):
    c = res["consistency_checks"]
    assert c["cm_from_om_bm_tool07_weights"] == pytest.approx(c["cm_published"], abs=5e-5)


def test_energy_input_is_phase3a_central(res):
    p3a = json.loads((ROOT / "results/provisional/phase3a/energy_uncertainty.json").read_text())
    assert res["energy"]["net_mwh_per_mw_yr"] == pytest.approx(p3a["central_estimate"]["net"]["gwh_per_mw"] * 1000)
    assert res["energy"]["net_mwh_per_mw_yr"] == pytest.approx(2427.37, abs=0.01)


def test_primary_is_energy_times_cm_and_not_net_of_lifecycle(res):
    E = res["energy"]["net_mwh_per_mw_yr"]
    p = res["primary_avoided_co2"]
    assert p["value"] == pytest.approx(E * 0.6242, rel=1e-12)          # MWh * t/MWh
    assert p["value"] == pytest.approx(1515.2, abs=0.1)
    assert p["unit"] == "tCO2 per MW per year"
    lo, hi = p["ci90_energy_sampling_only"]
    assert lo < p["value"] < hi
    assert "not total carbon uncertainty" in p["ci_label"]


def test_lifecycle_units_and_separation(res):
    E = res["energy"]["net_mwh_per_mw_yr"]
    lc = res["secondary_lifecycle_ghg"]
    assert lc["unit"].startswith("tCO2-eq")
    assert lc["cases"]["ipcc_ar5_median"]["t_co2eq_per_mw_yr"] == pytest.approx(E * 12 / 1000, rel=1e-12)  # g/kWh = kg/MWh
    assert [lc["cases"][k]["g_co2eq_per_kwh"] for k in ("ipcc_ar5_min", "ipcc_ar5_median", "ipcc_ar5_max")] == [8.0, 12.0, 35.0]


def test_context_methods_labelled_with_own_units(res):
    c = res["context_grid_methods"]
    assert c["generation_average_co2eq"]["unit_result"] == "tCO2-eq/MW/yr"
    assert c["operating_margin"]["unit_result"] == "tCO2/MW/yr"
    assert c["build_margin"]["per_mw_yr"] < c["generation_average_co2"]["per_mw_yr"] \
        < c["combined_margin_wind_solar"]["per_mw_yr"] < c["operating_margin"]["per_mw_yr"]


def test_scenarios_scale_linearly_with_capacity(res):
    E = res["energy"]["net_mwh_per_mw_yr"]
    s3 = next(s for s in res["scenarios"] if s["name"] == "S3_phase2")
    assert s3["installed_mw"] == 997.5
    assert s3["net_energy_gwh_yr"] == pytest.approx(E * 997.5 / 1000, rel=1e-12)
    assert s3["avoided_co2_cm_kt_yr"] == pytest.approx(E * 997.5 * 0.6242 / 1000, rel=1e-12)
    assert len(res["scenarios"]) == 4


def test_legacy_decomposition(res):
    lg = res["legacy_comparison"]
    assert lg["original_reported_p50_t_per_mw"] == pytest.approx(1524.81, abs=0.01)
    assert lg["original_effective_factor_g_per_kwh"] == pytest.approx(581.6, abs=0.1)
    # product of the two changes equals the total change
    assert (1 + lg["energy_change_pct"] / 100) * (1 + lg["factor_change_pct"] / 100) - 1 == \
        pytest.approx(lg["new_vs_original_pct"] / 100, abs=1e-12)


def test_committed_output_matches_fresh_run(res):
    assert json.loads(OUT.read_text()) == json.loads(json.dumps(res, ensure_ascii=False))
