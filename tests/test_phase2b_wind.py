"""
Tests for the Phase 2B wind representativeness / sensitivity analysis.
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PARQUET = ROOT / "data" / "processed" / "wind_hub_105m.parquet"
OUT = ROOT / "results" / "provisional" / "phase2b"

pytestmark = pytest.mark.skipif(not PARQUET.exists(), reason="parquet not available")


@pytest.fixture(scope="module")
def p2b():
    spec = importlib.util.spec_from_file_location("p2b", ROOT / "scripts/phase2b_wind_validation.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def df():
    return pd.read_parquet(PARQUET)


@pytest.fixture(scope="module")
def ring(p2b):
    return p2b.read_kml_ring(p2b.P1 / "SAROS_DURES_official.kml")


def test_baseline_case_equals_phase2a_corrected_empirical(p2b, df, ring):
    sens = p2b.sensitivity(df, p2b.gwa_compare(ring, p2b.era5_point_stats(df)))
    base = next(c for c in sens["cases"] if c["speed_factor"] == 1.0)
    p2a = json.loads((ROOT / "results/provisional/phase2a/power_curve_comparison.json").read_text())
    ref = p2a["empirical_hourly"]["oedb_v164_9500"]
    assert base["gross_aep_gwh_per_turbine"] == pytest.approx(ref["gross_aep_per_turbine_gwh"], abs=1e-4)
    assert base["net_cf_pct"] == pytest.approx(ref["net_cf_pct"], abs=1e-4)


def test_sensitivity_monotonic_and_regression(p2b, df, ring):
    sens = p2b.sensitivity(df, p2b.gwa_compare(ring, p2b.era5_point_stats(df)))
    core = [c for c in sens["cases"] if c["speed_factor"] in p2b.FACTORS]
    g = [c["gross_aep_gwh_per_turbine"] for c in core]
    assert g == sorted(g)
    ch = {c["speed_factor"]: c["aep_change_vs_baseline_pct"] for c in core}
    assert ch[0.9] == pytest.approx(-20.45, abs=0.01) and ch[1.1] == pytest.approx(19.70, abs=0.01)
    assert ch[0.95] == pytest.approx(-10.20, abs=0.01) and ch[1.05] == pytest.approx(10.00, abs=0.01)
    # committed output equals a fresh computation
    assert json.loads((OUT / "wind_speed_sensitivity.json").read_text())["cases"] == sens["cases"]


def test_only_wind_speed_changes(p2b, df):
    u = df["U_hub"].to_numpy().astype(float)
    a = p2b.power_from_speed(u * 1.05)
    b = p2b.power_from_speed(u)
    assert a.max() <= 9500.0 and b.max() <= 9500.0
    assert p2b.NET_FACTOR == pytest.approx(0.84778)


def test_geometry_and_series_facts(p2b, df, ring):
    geo = p2b.geometry(ring)
    assert geo["era5_node_inside_polygon"] is False
    assert geo["era5_node_to_polygon_boundary_min_km"] == pytest.approx(3.68, abs=0.05)
    assert geo["polygon_share_in_0p25deg_box_of_node_pct"] == pytest.approx(62.6, abs=0.5)
    s = p2b.series_checks(df)
    assert s["index_equals_full_hourly_range"] and s["duplicates"] == 0 and s["nan_values"] == 0
    assert s["n_hours"] == 96432


def test_gwa_polygon_mean_matches_review_value(p2b, df, ring):
    gwa = p2b.gwa_compare(ring, p2b.era5_point_stats(df))
    assert gwa["regions"][0]["mean_ws"] == pytest.approx(7.83, abs=0.02)
    assert gwa["node_pixel"]["ws"] == pytest.approx(8.19, abs=0.01)
