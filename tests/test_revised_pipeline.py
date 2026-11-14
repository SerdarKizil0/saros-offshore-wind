"""
Revised production pipeline (results/revised/), primary input since Phase 5-PRE-B:
ERA5 1994-2024 at 40.50 N 26.25 E via Open-Meteo (calibrated; not bit-identical to CDS).
The former 2014-2024 checks live in tests/test_historical_baseline_2014_2024.py.
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config.wind_data import PRIMARY, HISTORICAL_CDS_2014_2024  # noqa: E402

REV = ROOT / "results" / "revised"
ARCH = ROOT / "results" / "archive" / "baseline_2014_2024_cds"
PRODUCTION = ["scripts/04_fit_weibull_aep.py", "scripts/06_emissions_and_scenarios.py",
              "scripts/07_site_screening.py", "scripts/run_revised_pipeline.py", "config/wind_data.py"]
N_HOURS = 31 * 8760 + 8 * 24                    # 1994-2024, 8 leap years
LEAP = [1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]
OUTPUTS = ["wind_resource.json", "energy_yield.json", "weibull_crosscheck.json", "interannual_and_sampling.json",
           "annual_energy.csv", "wind_speed_sensitivity.json", "loss_scenarios.json", "emissions.json",
           "scenarios.json", "site_screening.json", "input_provenance.json"]


def J(name):
    return json.loads((REV / name).read_text())


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------ input provenance
def test_primary_input_is_pinned_and_documented():
    raw = PRIMARY.path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PRIMARY.sha256
    man = json.loads((PRIMARY.path.parent / "MANIFEST.json").read_text())
    assert man["sha256"] == PRIMARY.sha256 and man["rows"] == N_HOURS
    assert man["node"] == {"lat": 40.5, "lon": 26.25}
    assert man["period_utc"] == ["1994-01-01 00:00:00", "2024-12-31 23:00:00"]
    for r in man["requests"]:
        assert (r["grid_lat"], r["grid_lon"]) == (40.5, 26.25)
    assert sum(r["rows"] for r in man["requests"]) == N_HOURS
    assert "not bit-identical" in PRIMARY.data_product
    assert (PRIMARY.path.parent / "README.md").exists()


def test_primary_series_complete_hourly_1994_2024():
    st = pd.read_parquet(PRIMARY.path)
    assert list(st.columns) == ["U10", "U100", "wdir100"] and len(st) == N_HOURS
    assert (st.dtypes == "int16").all() and not st.isna().any().any()
    assert st.U100.min() >= 0 and st.U100.max() < 4000 and st.wdir100.between(0, 360).all()
    s04 = _load("s04_in", "scripts/04_fit_weibull_aep.py")
    df, info = s04.load_series(PRIMARY)
    assert df.index[0] == pd.Timestamp("1994-01-01 00:00") and df.index[-1] == pd.Timestamp("2024-12-31 23:00")
    assert (np.diff(df.index.values).astype("timedelta64[h]").astype(int) == 1).all()
    assert info["n_hours"] == N_HOURS and info["period"] == "1994-2024"


def test_loader_refuses_an_unpinned_file(tmp_path):
    s04 = _load("s04_pin", "scripts/04_fit_weibull_aep.py")
    bad = tmp_path / "x.parquet"
    shutil.copy(PRIMARY.path, bad)
    with open(bad, "ab") as fh:
        fh.write(b"\0")
    from dataclasses import replace
    with pytest.raises(ValueError, match="sha256"):
        s04.load_series(replace(PRIMARY, path=bad))


def test_input_calibration_against_cds_is_recorded_and_passes():
    ip = J("input_provenance.json")
    assert ip["primary_input"]["sha256"] == PRIMARY.sha256
    c = ip["calibration_vs_cds"]
    assert c["label"].startswith("INPUT QA") and c["common_period"] == "2014-2024" and c["n_hours"] == 96432
    assert c["U100"]["pearson_r"] > 0.9999 and abs(c["U100"]["mean_diff_ms"]) < 0.001
    assert abs(c["gross_cf"]["rel_diff_same_alpha_pct"]) < 0.05        # Phase 5-PRE: -0.004 %
    assert ip["comparison_input_not_used_for_results"]["sha256"] == HISTORICAL_CDS_2014_2024.sha256


# ------------------------------------------------------------------- period
def test_every_output_is_1994_2024():
    ey = J("energy_yield.json")
    assert ey["period"] == "1994-2024" and ey["input"]["series_key"] == PRIMARY.key
    n = ey["normalisation_check"]
    assert n["n_hours"] == N_HOURS and n["n_years"] == 31 and n["leap_years"] == LEAP
    tab = pd.read_csv(REV / "annual_energy.csv")
    assert list(tab.year) == list(range(1994, 2025))
    assert list(tab.hours) == [8784 if y in LEAP else 8760 for y in tab.year]
    s = J("interannual_and_sampling.json")
    assert s["sampling_ci_of_period_mean"]["period"] == "1994-2024"
    assert s["sampling_ci_of_period_mean"]["n_years"] == 31 and s["sampling_ci_of_period_mean"]["t_quantile_df"] == 30
    assert s["observed_interannual_variability"]["n_years"] == 31
    assert J("wind_resource.json")["data"]["period"] == "1994-01-01 to 2024-12-31 UTC"
    assert J("wind_resource.json")["data"]["n_hours"] == N_HOURS
    assert J("emissions.json")["energy_input"]["period"] == "1994-2024"
    assert J("site_screening.json")["wind_direction"]["period"] == "1994-2024"


# ------------------------------------- independent recomputation (no script code)
@pytest.fixture(scope="module")
def independent():
    st = pd.read_parquet(PRIMARY.path)
    u10, u100 = st.U10.to_numpy() / 100.0, st.U100.to_numpy() / 100.0
    m = (u10 > 1.0) & (u100 > 1.0)
    a = np.log(u100[m] / u10[m]) / np.log(10.0)
    lo, hi = np.percentile(a, [1, 99])
    alpha = a[(a >= lo) & (a <= hi)].mean()
    u = u100 * 1.05 ** alpha
    from config.turbine import POWER_CURVE_MS_KW
    v, p = np.array(POWER_CURVE_MS_KW).T
    pw = np.interp(u, v, p, left=0, right=0)
    pw[(u < 3.5) | (u >= 25.0)] = 0.0
    years = pd.date_range("1994-01-01", periods=len(st), freq="h").year
    ann = pd.DataFrame({"p": pw, "y": years}).groupby("y")["p"].agg(["sum", "size"])
    return {"alpha": alpha, "gross_cf": pw.sum() / (9500.0 * len(pw)),
            "annual_cf": (ann["sum"] / (9500.0 * ann["size"])).to_numpy(), "u_mean": u.mean()}


def test_central_yield_recomputed_independently(independent):
    ey = J("energy_yield.json")
    eta = 0.92 * 0.95 * 0.97
    assert ey["input"]["alpha_hub_extrapolation"] == pytest.approx(independent["alpha"], rel=1e-12)
    assert ey["gross_cf"] == pytest.approx(independent["gross_cf"], rel=1e-12)
    assert ey["net_cf"] == pytest.approx(independent["gross_cf"] * eta, rel=1e-12)
    assert ey["net"]["gwh_per_mw"] == pytest.approx(independent["gross_cf"] * eta * 8.766, rel=1e-12)
    assert ey["net"]["gwh_per_mw"] == pytest.approx(2.3539, abs=1e-4)          # regression anchor
    assert J("wind_resource.json")["U_hub"]["mean_ms"] == pytest.approx(independent["u_mean"], rel=1e-12)


def test_sampling_interval_recomputed_from_the_31_annual_values(independent):
    cf = independent["annual_cf"]
    assert len(cf) == 31
    se = cf.std(ddof=1) / np.sqrt(31)
    q = stats.t.ppf(0.95, 30)
    to_net = 0.92 * 0.95 * 0.97 * 8.766
    t = J("interannual_and_sampling.json")["sampling_ci_of_period_mean"]["primary_t_interval_90"]
    assert t["net_gwh_per_mw"] == pytest.approx([(cf.mean() - q * se) * to_net, (cf.mean() + q * se) * to_net],
                                                rel=1e-12)
    v = J("interannual_and_sampling.json")["observed_interannual_variability"]
    assert v["annual_net_cf_cov_pct"] == pytest.approx(cf.std(ddof=1) / cf.mean() * 100, rel=1e-12)


def test_uncertainty_components_are_separate_and_labelled():
    s = J("interannual_and_sampling.json")
    assert s["observed_interannual_variability"]["label"].startswith("OBSERVED")
    lab = s["sampling_ci_of_period_mean"]["label"]
    assert lab.startswith("SAMPLING") and "1994-2024" in lab and "not a P90" in lab
    assert "node sensitivity" in lab and "ERA5-GWA" in lab
    ws = J("wind_speed_sensitivity.json")
    assert ws["label"].startswith("SENSITIVITY")
    assert "not a correction" in ws["gwa_reference"]["note"]
    gwa = [c for c in ws["cases"] if "GWA" in c["case"]]
    assert len(gwa) == 1
    assert gwa[0]["speed_factor"] == pytest.approx(ws["gwa_reference"]["gwa4_polygon_mean_100m_ms"]
                                                   / J("wind_resource.json")["U100"]["mean_ms"], rel=1e-12)
    assert J("loss_scenarios.json")["label"].startswith("LOSS SCENARIOS")
    for f in REV.glob("*.json"):
        if f.name != "MANIFEST.json":
            assert json.loads(f.read_text())["status"].startswith("PRE-SUBMISSION"), f


def test_documented_turbine_and_loss_assumptions_unchanged():
    ey = J("energy_yield.json")
    assert ey["power_curve"] == "OEDB_V164_9500" and ey["estimator"].startswith("empirical hourly")
    assert ey["losses_nominal"] == {"wake": 0.08, "availability": 0.95, "electrical": 0.03}
    assert ey["hours_per_average_year"] == 8766.0
    ls = J("loss_scenarios.json")["scenarios"]
    old = json.loads((ARCH / "loss_scenarios.json").read_text())["scenarios"]
    assert list(ls) == list(old) == ["low_loss", "nominal", "high_loss"]
    for k in ls:                                                     # assumptions identical to the archive
        for f in ("wake", "availability", "electrical", "net_factor", "rel_to_nominal_pct"):
            assert ls[k][f] == old[k][f], (k, f)


def test_weibull_is_descriptive_crosscheck_for_the_primary_period():
    w = J("weibull_crosscheck.json")
    assert "cross-check" in w["role"] and "not the energy estimator" in w["role"]
    assert w["gross_cf_empirical"] == J("energy_yield.json")["gross_cf"]
    assert w["weibull_fit_U_hub"]["n_hours"] == N_HOURS


# ------------------------------------------------------------ emissions, units
def test_emissions_arithmetic_and_units():
    em, ey = J("emissions.json"), J("energy_yield.json")
    E = ey["net_mwh_per_mw_yr"]
    assert em["energy_input"]["net_mwh_per_mw_yr"] == E
    assert E == pytest.approx(ey["net"]["gwh_per_mw"] * 1000, rel=1e-12)
    p = em["primary_avoided_operational_co2"]
    assert p["factor_value"] == 0.6242 and p["factor_unit"] == "tCO2/MWh"
    assert p["t_co2_per_mw_yr"] == pytest.approx(E * 0.6242, rel=1e-12)       # nothing subtracted
    ci = J("interannual_and_sampling.json")["sampling_ci_of_period_mean"]["primary_t_interval_90"]["net_gwh_per_mw"]
    assert p["ci90_t_co2_per_mw_yr"] == pytest.approx([ci[0] * 1000 * 0.6242, ci[1] * 1000 * 0.6242], rel=1e-12)
    assert "1994-2024" in p["ci_label"] and "not total carbon uncertainty" in p["ci_label"]
    c = em["context_grid_methods"]
    assert c["generation_average_co2eq"]["result_unit"] == "tCO2-eq/MW/yr"
    for k in ("operating_margin", "build_margin", "generation_average_co2"):
        assert c[k]["result_unit"] == "tCO2/MW/yr"
        assert c[k]["result_per_mw_yr"] == pytest.approx(E * c[k]["factor_value"], rel=1e-12)
    lc = em["secondary_lifecycle_ghg"]
    assert lc["unit"].startswith("tCO2-eq") and "not_subtracted_from_primary" in lc
    for case in lc["cases"].values():
        assert case["t_co2eq_per_mw_yr"] == pytest.approx(E * case["g_co2eq_per_kwh"] / 1000, rel=1e-12)


def test_cm_reproduced_from_tool07_weights():
    from config.emissions import GRID_EF_2023 as G, CM_TOOL07_WEIGHTS_WIND_SOLAR as W
    assert W[0] * G["operating_margin"].value + W[1] * G["build_margin"].value == pytest.approx(
        G["combined_margin_wind_solar"].value, abs=5e-5)


# ---------------------------------------------------------------- scenarios
def test_scenarios_consistent_and_s4_retired():
    sc, ey = J("scenarios.json"), J("energy_yield.json")
    E = ey["net_mwh_per_mw_yr"]
    ci = J("emissions.json")["energy_input"]["net_mwh_per_mw_yr_ci90_sampling"]
    assert [r["name"] for r in sc["scenarios"]] == ["S1", "S2", "S3"]
    assert [r["installed_mw"] for r in sc["scenarios"]] == [247.0, 503.5, 997.5]
    for r in sc["scenarios"]:
        mw = r["installed_mw"]
        assert r["net_energy_gwh_yr"] == pytest.approx(E * mw / 1000, rel=1e-12)
        assert r["net_energy_gwh_yr_ci90_sampling"] == pytest.approx([ci[0] * mw / 1000, ci[1] * mw / 1000], rel=1e-12)
        assert r["avoided_co2_cm_kt_yr"] == pytest.approx(E * mw * 0.6242 / 1000, rel=1e-12)
        assert r["lifecycle_ghg_kt_co2eq_yr_reference"] == pytest.approx(E * mw * 12 / 1e6, rel=1e-12)
    assert "S4_max" in sc["retired"]
    for f in REV.glob("*.json"):
        d = json.loads(f.read_text())
        rows = (d.get("scenarios") if isinstance(d.get("scenarios"), list) else []) + d.get("active_scenarios_density", [])
        assert not any("S4" in r.get("name", "") for r in rows), f
        assert "1738.5" not in f.read_text(), f


# ---------------------------------------------------------------- screening
def test_screening_geometry_unchanged_and_direction_from_primary():
    s, a = J("site_screening.json"), json.loads((ARCH / "site_screening.json").read_text())
    for k in ("polygon", "bathymetry", "era5_node_representativeness", "protected_area_overlap",
              "spacing_and_packing", "retired", "not_screened"):
        assert s[k] == a[k], k                                       # input-only geometry: identical
    assert s["protected_area_overlap"]["saros_ock_2010"]["overlap_km2"] == pytest.approx(24.7475, abs=1e-4)
    assert s["wind_direction"]["series"] == PRIMARY.key
    c = s["screening_classes_best_fit_layout"]
    assert c["n_positions"] == 182 and c["inside_saros_ock_2010"] == 25
    assert [r["name"] for r in s["active_scenarios_density"]] == ["S1", "S2", "S3"]


# ---------------------------------------------------------- no stale values
INPUT_ONLY_KEYS = {"area_km2", "principal_axis_bearing_deg", "length_along_axis_km", "width_across_axis_km",
                   "p5", "median", "p95", "max", "10", "30", "50", "60", "distance_to_polygon_boundary_km",
                   "polygon_share_nearest_to_this_node_pct", "overlap_km2", "overlap_share_pct", "cell_km2",
                   "area_division_count", "density_mw_per_km2_full_polygon", "density_mw_per_km2_outside_ock",
                   "share_of_fitted_positions_pct", "gwa4_polygon_mean_100m_ms",
                   "share_of_2035_offshore_target_capacity_pct", "net_factor", "rel_to_nominal_pct",
                   "rel_to_primary_pct"}


def _leaves(d, path=()):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from _leaves(v, path + (k,))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            yield from _leaves(v, path + (i,))
    else:
        yield path, d


def test_no_stale_2014_2024_values_in_authoritative_outputs():
    text = {f.name: f.read_text() for f in REV.iterdir() if f.is_file()}
    for name, t in text.items():
        if name in ("input_provenance.json", "MANIFEST.json"):
            continue                                                 # QA / provenance may name the CDS period
        for banned in ("2014-2024", "2014–2024", "11yr", "11-year", "sampling_ci_of_11yr_mean"):
            assert banned not in t, f"{name} contains {banned!r}"
    # every computed (non-input) number of the archive must be absent from results/revised
    for f in ARCH.glob("*.json"):
        if f.name == "MANIFEST.json":
            continue
        for path, v in _leaves(json.loads(f.read_text())):
            if not isinstance(v, float) or path[-1] in INPUT_ONLY_KEYS:
                continue
            r = repr(v)
            if len(r.replace("-", "").replace("0.", "").lstrip("0")) < 12:
                continue
            for name, t in text.items():
                assert not re.search(r"(?<![\d.])" + re.escape(r) + r"(?!\d)", t), f"stale {f.name}:{path} in {name}"


def test_production_code_reads_no_outdated_results():
    banned = ["monte_carlo_samples", "monte_carlo_results", "comparison_results", "weibull_aep_results",
              "results/archive", "results/provisional", "GRID_CO2", "OFFSHORE_WIND_CO2", "POWER_CURVE_ORIGINAL",
              "S4_max\"", "sampling_ci_of_11yr_mean"]
    for rel in PRODUCTION:
        src = (ROOT / rel).read_text()
        for b in banned:
            assert b not in src, f"{rel} references {b}"
        tree = ast.parse(src)
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        names |= {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
        assert "SCENARIOS" not in names and "DEFAULT_SCENARIO" not in names, f"{rel} uses historical SCENARIOS"
    assert not list((ROOT / "results").glob("*.json")) and not list((ROOT / "results").glob("*.npz"))


def test_config_has_no_unsupported_claims():
    src = (ROOT / "config/emissions.py").read_text() + (ROOT / "config/turbine.py").read_text()
    assert "IPCC 2025" not in src and "IPCC AR6/2025" not in src
    assert not re.search(r"no recycling credit.*conservative", src, re.I)


# ----------------------------------------------------- manifest, reproduction
def test_manifest_checksums_and_inputs():
    m = J("MANIFEST.json")
    assert sorted(m["files"]) == sorted(OUTPUTS)
    for f, meta in m["files"].items():
        assert hashlib.sha256((REV / f).read_bytes()).hexdigest() == meta["sha256"], f
    assert m["inputs"]["wind_series"] == PRIMARY.rel_path
    assert m["inputs"]["wind_series_sha256"] == PRIMARY.sha256 and m["inputs"]["period"] == "1994-2024"
    assert m["inputs"]["comparison_only"]["sha256"] == HISTORICAL_CDS_2014_2024.sha256


def test_revised_outputs_reproduce_from_fresh_computation():
    s04 = _load("s04_fresh", "scripts/04_fit_weibull_aep.py")
    df, info = s04.load_series(PRIMARY)
    res = s04.compute(df, PRIMARY, info)
    res.pop("_annual_table")
    for name, obj in res.items():
        assert json.loads(json.dumps(obj, ensure_ascii=False)) == J(name), name
    em, sc = _load("s06_fresh", "scripts/06_emissions_and_scenarios.py").compute()
    assert json.loads(json.dumps(em, ensure_ascii=False)) == J("emissions.json")
    assert json.loads(json.dumps(sc, ensure_ascii=False)) == J("scenarios.json")
    ss = _load("s07_fresh", "scripts/07_site_screening.py").compute()
    assert json.loads(json.dumps(ss, ensure_ascii=False)) == J("site_screening.json")


def test_clean_checkout_reproduces_results_byte_identically(tmp_path):
    """Copy only version-controlled (and new, non-ignored) files, run the pipeline, compare bytes."""
    files = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split("\n")
    work = tmp_path / "clone"
    for rel in filter(None, files):
        src = ROOT / rel
        if src.is_file():
            (work / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, work / rel)
    for f in (work / "results/revised").iterdir():
        f.unlink()
    r = subprocess.run([sys.executable, "scripts/run_revised_pipeline.py"], cwd=work, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    for name in OUTPUTS:
        assert (work / "results/revised" / name).read_bytes() == (REV / name).read_bytes(), name
