"""
Tests for the Phase 3A energy estimator and uncertainty framework.
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PARQUET = ROOT / "data" / "processed" / "wind_hub_105m.parquet"
OUT = ROOT / "results" / "provisional" / "phase3a"

pytestmark = pytest.mark.skipif(not PARQUET.exists(), reason="parquet not available")


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("p3a", ROOT / "scripts/phase3a_energy_uncertainty.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def data(m):
    df = pd.read_parquet(PARQUET)
    s04 = m._s04()
    p = s04.power_from_speed(df["U_hub"].to_numpy().astype(float))
    return df, p, m.annual_table(df, p)


def test_year_normalisation_and_leap_years(data):
    _, p, tab = data
    assert list(tab.index) == list(range(2014, 2025))
    assert set(tab.index[tab.leap]) == {2016, 2020, 2024}
    assert all(tab.hours == np.where(tab.leap, 8784, 8760))
    assert tab.hours.sum() == p.size == 96432


def test_energy_conservation_and_units(m, data):
    _, p, tab = data
    assert tab.gross_kwh.sum() == pytest.approx(p.sum(), rel=1e-12)
    cf = m.pooled_cf(tab)
    assert cf == pytest.approx(p.mean() / 9500.0, rel=1e-12)          # kW / kW
    assert 0 < tab.gross_cf.min() and tab.gross_cf.max() < 1
    e = m.cf_to_energy(cf)
    assert e["gwh_per_turbine"] == pytest.approx(cf * 9.5 * 8766 / 1000, rel=1e-12)   # MW*h -> GWh
    assert e["gwh_per_mw"] == pytest.approx(e["gwh_per_turbine"] / 9.5, rel=1e-12)
    assert m.NF == pytest.approx(0.92 * 0.95 * 0.97)


def test_central_estimate_vs_phase2a_only_differs_by_year_length(m, data):
    _, p, tab = data
    p2a = json.loads((ROOT / "results/provisional/phase2a/power_curve_comparison.json").read_text())
    ref = p2a["empirical_hourly"]["oedb_v164_9500"]["net_aep_per_mw_gwh"]          # sum / 11 years
    central = m.cf_to_energy(m.pooled_cf(tab) * m.NF)["gwh_per_mw"]                 # CF x 8766 h
    assert ref / central - 1 == pytest.approx((96432 / 11) / 8766 - 1, abs=1e-12)


def test_weibull_bins_sum_to_total(m, data):
    df, _, _ = data
    b = json.loads((ROOT / "results/archive/baseline_original_curve/monte_carlo_results.json").read_text())["base_weibull"]
    dec, total = m.weibull_decomposition(df["U_hub"].to_numpy().astype(float), b["k"], b["c"], m._s04())
    assert dec.gross_cf_contrib_weibull_pct.sum() / 100 == pytest.approx(total, rel=1e-9)
    assert dec.gross_cf_contrib_emp_pct.sum() / 100 == pytest.approx(m.pooled_cf(data[2]), rel=1e-9)
    assert total == pytest.approx(0.320591, abs=1e-6)          # Phase 2A Weibull gross CF


def test_bootstrap_reproducible_and_contains_mean(m, data):
    tab = data[2]
    a, b = m.bootstrap(tab), m.bootstrap(tab)
    assert np.array_equal(a, b)
    lo, hi = np.percentile(a, [5, 95])
    cf = m.pooled_cf(tab)
    assert lo < cf < hi
    assert hi - lo < tab.gross_cf.max() - tab.gross_cf.min()   # CI of mean narrower than year range


def test_loss_scenarios_ordered(m):
    nf = {k: m.net_factor(*v) for k, v in m.LOSS_SCENARIOS.items()}
    assert nf["high_loss"] < nf["nominal"] < nf["low_loss"] < 1


def test_committed_outputs_match_fresh_run(m, data, tmp_path, monkeypatch):
    monkeypatch.setattr(m, "OUT", tmp_path)
    assert m.main() == 0
    fresh = json.loads((tmp_path / "energy_uncertainty.json").read_text())
    committed = json.loads((OUT / "energy_uncertainty.json").read_text())
    assert fresh == committed
    assert (tmp_path / "annual_energy.csv").read_text() == (OUT / "annual_energy.csv").read_text()
