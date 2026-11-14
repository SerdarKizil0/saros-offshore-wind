"""
Historical 2014-2024 CDS baseline (results/archive/baseline_2014_2024_cds/).

Until Phase 5-PRE-B these files were results/revised/. The checks below are the
former Phase 4B consistency tests, now aimed at the archive. They also verify
that the current production code, run on the historical series, still
reproduces every archived number.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ARCH = ROOT / "results" / "archive" / "baseline_2014_2024_cds"
P3A = ROOT / "results/provisional/phase3a/energy_uncertainty.json"
P3B = ROOT / "results/provisional/phase3b/carbon_accounting.json"
P2B = ROOT / "results/provisional/phase2b/wind_speed_sensitivity.json"
P4A = ROOT / "results/provisional/phase4a/site_checks.json"
HIST_KEY = "historical_cds_2014_2024"
# key renames made in Phase 5-PRE-B (period-neutral names); values are unchanged
RENAMED = {"sampling_ci_of_11yr_mean": "sampling_ci_of_period_mean",
           "annual_net_cf_cov_pct_excluding_2014": "annual_net_cf_cov_pct_excluding_min_year",
           "ddof1_excluding_2014": "ddof1_excluding_lowest_year"}


def A(name):
    return json.loads((ARCH / name).read_text())


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def _leaves(d, path=()):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from _leaves(v, path + (RENAMED.get(k, k),))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            yield from _leaves(v, path + (i,))
    else:
        yield path, d


def assert_reproduces(archived: dict, fresh: dict, name: str):
    """Every archived leaf exists in the fresh output with the same value (labels excepted)."""
    new = dict(_leaves(json.loads(json.dumps(fresh, ensure_ascii=False))))
    for path, v in _leaves(archived):
        assert path in new, f"{name}: {path} missing"
        if path[-1] == "label" or path[-1] == "status" and isinstance(v, str):
            continue
        assert new[path] == v, f"{name}: {path} {new[path]!r} != {v!r}"


@pytest.fixture(scope="module")
def hist_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("hist")
    s04 = _load("s04_hist", "scripts/04_fit_weibull_aep.py")
    s04.run(HIST_KEY, out)
    s06 = _load("s06_hist", "scripts/06_emissions_and_scenarios.py")
    em, sc = s06.compute(out)
    s07 = _load("s07_hist", "scripts/07_site_screening.py")
    return out, em, sc, s07.compute(HIST_KEY)


# ------------------------------------------------------------ archive integrity
def test_archive_checksums():
    lines = (ARCH / "SHA256SUMS").read_text().split("\n")
    sums = dict(reversed(ln.split()) for ln in lines if ln.strip())
    assert len(sums) == 11
    for name, sha in sums.items():
        assert hashlib.sha256((ARCH / name).read_bytes()).hexdigest() == sha, name
    m = A("MANIFEST.json")
    for f, meta in m["files"].items():
        assert hashlib.sha256((ARCH / f).read_bytes()).hexdigest() == meta["sha256"], f
    assert m["inputs"]["wind_series_sha256"] == hashlib.sha256(
        (ROOT / "data/processed/wind_hub_105m.parquet").read_bytes()).hexdigest()


# ------------------------------------------- archive vs the review-phase evidence
def test_energy_matches_phase3a():
    ey, p3 = A("energy_yield.json"), json.loads(P3A.read_text())
    assert ey["net_cf"] == pytest.approx(p3["central_estimate"]["net_cf"], rel=1e-12)
    assert ey["net"]["gwh_per_mw"] == pytest.approx(p3["central_estimate"]["net"]["gwh_per_mw"], rel=1e-12)
    assert ey["net"]["gwh_per_mw"] == pytest.approx(2.4274, abs=1e-4)


def test_sampling_ci_and_variability_match_phase3a():
    s, p3 = A("interannual_and_sampling.json"), json.loads(P3A.read_text())
    t = s["sampling_ci_of_11yr_mean"]["primary_t_interval_90"]["gross_cf"]
    assert t == pytest.approx(p3["sampling_uncertainty_of_mean"]["t_interval_90_gross_cf"], rel=1e-12)
    b = s["sampling_ci_of_11yr_mean"]["check_bootstrap_90"]["net_gwh_per_mw"]
    assert b == pytest.approx(p3["sampling_uncertainty_of_mean"]["net_gwh_per_mw_ci90"], rel=1e-12)
    v = s["observed_interannual_variability"]
    assert v["annual_net_cf_cov_pct"] == pytest.approx(p3["interannual_variability"]["annual_cov_pct"], rel=1e-12)


def test_emissions_match_phase3b():
    em, p3b = A("emissions.json"), json.loads(P3B.read_text())
    p = em["primary_avoided_operational_co2"]
    assert p["t_co2_per_mw_yr"] == pytest.approx(p3b["primary_avoided_co2"]["value"], rel=1e-12)
    assert p["ci90_t_co2_per_mw_yr"] == pytest.approx(p3b["primary_avoided_co2"]["ci90_energy_sampling_only"],
                                                      rel=1e-12)
    s3 = next(r for r in A("scenarios.json")["scenarios"] if r["name"] == "S3")
    ref = next(r for r in p3b["scenarios"] if r["name"] == "S3_phase2")
    assert s3["avoided_co2_cm_kt_yr"] == pytest.approx(ref["avoided_co2_cm_kt_yr"], rel=1e-12)


def test_wind_speed_sensitivity_matches_phase2b():
    new = {round(c["speed_factor"], 4): c for c in A("wind_speed_sensitivity.json")["cases"]}
    old = {round(c["speed_factor"], 4): c for c in json.loads(P2B.read_text())["cases"]}
    for f in (0.9, 0.95, 1.0, 1.05, 1.1):
        assert new[f]["aep_change_vs_baseline_pct"] == pytest.approx(old[f]["aep_change_vs_baseline_pct"], abs=0.006)


def test_screening_matches_phase4a():
    s, p4 = A("site_screening.json"), json.loads(P4A.read_text())
    assert s["protected_area_overlap"]["saros_ock_2010"]["overlap_km2"] == pytest.approx(p4["ock_overlap_km2"],
                                                                                         rel=1e-12)
    assert s["screening_classes_best_fit_layout"]["inside_saros_ock_2010"] == 25


# ------------------------------- current code reproduces the archive (no drift)
@pytest.mark.parametrize("name", ["wind_resource.json", "energy_yield.json", "weibull_crosscheck.json",
                                  "interannual_and_sampling.json", "loss_scenarios.json",
                                  "wind_speed_sensitivity.json"])
def test_script04_reproduces_archive(hist_run, name):
    out, *_ = hist_run
    assert_reproduces(A(name), json.loads((out / name).read_text()), name)


def test_annual_table_byte_identical(hist_run):
    out, *_ = hist_run
    assert (out / "annual_energy.csv").read_bytes() == (ARCH / "annual_energy.csv").read_bytes()


def test_script06_reproduces_archive(hist_run):
    _, em, sc, _ = hist_run
    assert_reproduces(A("emissions.json"), em, "emissions.json")
    assert_reproduces(A("scenarios.json"), sc, "scenarios.json")


def test_script07_reproduces_archive(hist_run):
    *_, ss = hist_run
    assert_reproduces(A("site_screening.json"), ss, "site_screening.json")


def test_historical_mode_cannot_overwrite_revised():
    import subprocess
    r = subprocess.run([sys.executable, "scripts/04_fit_weibull_aep.py", "--series", HIST_KEY], cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 2 and "refusing" in r.stdout
