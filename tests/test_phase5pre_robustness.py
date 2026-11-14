"""Phase 5-PRE: ERA5 temporal and spatial robustness (inputs, calibration, invariants)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
IN_DIR = ROOT / "data/external/phase5pre"
OUT = ROOT / "results/provisional/phase5pre"
HIST = ROOT / "results/archive/baseline_2014_2024_cds"      # former results/revised/ (Phase 5-PRE-B)
pytestmark = pytest.mark.skipif(not (IN_DIR / "MANIFEST.json").exists(),
                                reason="Phase 5-PRE inputs not fetched")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def mod():
    return _load("p5pre", "scripts/phase5pre_era5_robustness.py")


@pytest.fixture(scope="module")
def fresh(mod):
    return mod.compute()


def _json(name):
    return json.loads((OUT / name).read_text())


# ------------------------------------------------------------------ inputs
def test_input_checksums_match_manifest():
    man = json.loads((IN_DIR / "MANIFEST.json").read_text())
    for name, sha in man["files"].items():
        assert hashlib.sha256((IN_DIR / name).read_bytes()).hexdigest() == sha, name


def test_openmeteo_returned_the_requested_grid_points():
    man = json.loads((IN_DIR / "MANIFEST.json").read_text())
    req = man["openmeteo_requests"]
    assert len(req) == 3 * 2
    assert sum(r["rows"] for r in req) == 3 * (46 * 8760 + 12 * 24)
    want = {"W": 26.00, "C": 26.25, "E": 26.50}
    for r in req:
        assert r["grid_lat"] == pytest.approx(40.50, abs=1e-9)
        assert r["grid_lon"] == pytest.approx(want[r["node"]], abs=1e-9)


@pytest.mark.parametrize("lon", [26.00, 26.25, 26.50])
def test_node_series_complete_and_hourly(mod, lon):
    d = mod.load_node(lon)
    n = 46 * 8760 + 12 * 24                      # 1979-2024, 12 leap years
    assert len(d) == n
    assert d.index[0] == pd.Timestamp("1979-01-01 00:00") and d.index[-1] == pd.Timestamp("2024-12-31 23:00")
    assert (np.diff(d.index.values).astype("timedelta64[h]").astype(int) == 1).all()
    assert not d.isna().any().any()
    assert d.min().min() >= 0 and d.max().max() < 40


# ------------------------------------------------------------- calibration
def test_baseline_reproduced_exactly(fresh):
    b = fresh["calibration.json"]["baseline_check"]
    assert b["net_gwh_per_mw_recomputed"] == pytest.approx(b["net_gwh_per_mw_archived_2014_2024_baseline"], rel=1e-12)


def test_openmeteo_passes_the_declared_calibration_criteria(fresh):
    c = fresh["calibration.json"]
    assert c["n_hours_matched"] == c["n_hours_baseline"] == 96432
    assert c["fit_for_ratio_analysis"] is True
    assert c["U100"]["pearson_r"] >= c["criteria"]["hourly_U100_correlation_min"]


def test_anchoring_returns_the_cds_baseline_for_the_baseline_period(fresh):
    p = fresh["temporal.json"]["periods"]["2014-2024"]
    rev = json.loads((HIST / "energy_yield.json").read_text())
    assert p["ratio_energy_vs_2014_2024"] == pytest.approx(1.0, rel=1e-12)
    assert p["anchored_net_gwh_per_mw"] == pytest.approx(rev["net"]["gwh_per_mw"], rel=1e-12)


# ------------------------------------------------------------------ temporal
def test_rolling_windows_consistent_with_period_table(fresh):
    roll = fresh["rolling_11yr.csv"]
    assert list(roll.start) == list(range(1979, 2015))
    b = roll.loc[roll.start == 2014].iloc[0]
    p = fresh["temporal.json"]["periods"]["2014-2024"]
    assert b.net_gwh_per_mw_openmeteo == pytest.approx(p["net_gwh_per_mw_openmeteo"], rel=1e-12)


def test_baseline_sampling_ci_matches_archived_baseline(fresh):
    ci = fresh["temporal.json"]["baseline_90pct_sampling_ci_net_gwh_per_mw"]
    rev = json.loads((HIST / "interannual_and_sampling.json").read_text())
    assert ci == pytest.approx(rev["sampling_ci_of_11yr_mean"]["primary_t_interval_90"]["net_gwh_per_mw"], rel=1e-12)


def test_annual_table_conserves_energy(fresh):
    t = fresh["annual_energy_1979_2024.csv"]
    assert t.hours.sum() == 46 * 8760 + 12 * 24
    pooled = t.gross_kwh.sum() / (9500.0 * t.hours.sum())
    p = fresh["temporal.json"]["periods"]["1979-2024"]["gross_cf_openmeteo"]
    assert pooled == pytest.approx(p, rel=1e-12)


# ------------------------------------------------------------------- spatial
def test_polygon_shares_and_node_geometry(fresh):
    g = fresh["node_geography.json"]
    assert sum(g[k]["polygon_share_nearest_to_node_pct"] for k in "WCE") == pytest.approx(100.0)
    # Phase 4A/4B value for the baseline node: 3.68 km outside, ~62.6% share
    assert g["C"]["inside_polygon"] is False
    assert g["C"]["distance_to_polygon_boundary_km"] == pytest.approx(3.678, abs=0.02)
    assert g["C"]["polygon_share_nearest_to_node_pct"] == pytest.approx(62.6, abs=0.5)
    for k in "WCE":
        assert 0.0 <= g[k]["era5_land_sea_mask_fraction"] <= 1.0


def test_interpolation_is_labelled_and_not_primary(fresh):
    i = fresh["spatial.json"]["interpolation_polygon_share_weighted"]
    assert "not adopted" in i["label"] and "not validation" in i["label"]
    assert sum(i["weights"].values()) == pytest.approx(1.0)


def test_node_c_spatial_entry_matches_temporal_baseline_period(fresh):
    # node C uses the documented alpha from its own 2014-2024 Open-Meteo series;
    # the temporal table uses the CDS baseline alpha. They must agree to < 0.05 %.
    s = fresh["spatial.json"]["nodes"]["C"]["net_gwh_per_mw"]
    t = fresh["temporal.json"]["periods"]["2014-2024"]["net_gwh_per_mw_openmeteo"]
    assert s == pytest.approx(t, rel=5e-4)


# --------------------------------------------------------- reproducibility
def test_committed_outputs_equal_fresh_computation(mod, fresh, tmp_path):
    mod.write(fresh, tmp_path)
    for name in fresh:
        assert (tmp_path / name).read_bytes() == (OUT / name).read_bytes(), name


def test_results_revised_consistent_with_its_manifest():
    man = json.loads((ROOT / "results/revised/MANIFEST.json").read_text())
    for name, meta in man["files"].items():
        assert hashlib.sha256((ROOT / "results/revised" / name).read_bytes()).hexdigest() == meta["sha256"], name
