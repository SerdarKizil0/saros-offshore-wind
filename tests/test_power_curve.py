"""
Regression tests for the Phase 2A power-curve correction.

Run from the repository root:  python -m pytest -q tests/
Needs only committed files (no ERA5 parquet).
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config.turbine import (TURBINE, POWER_CURVE_ID, POWER_CURVE_MS_KW,   # noqa: E402
                            POWER_CURVE_OEDB_V164_9500_MS_KW,
                            POWER_CURVE_ORIGINAL_MS_KW)

RHO, BETZ = 1.225, 16 / 27
AREA = np.pi * (TURBINE.rotor_diameter_m / 2) ** 2
RATED_KW = TURBINE.rated_power_mw * 1000
BASELINE = ROOT / "results" / "archive" / "baseline_original_curve"
PROVISIONAL = ROOT / "results" / "provisional" / "phase2a"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def s04():
    return _load("s04", "scripts/04_fit_weibull_aep.py")


@pytest.fixture(scope="module")
def s06():
    return _load("s06", "scripts/legacy/06_run_monte_carlo.py")   # retired; grid convention kept


@pytest.fixture(scope="module")
def p2a():
    return _load("p2a", "scripts/phase2a_power_curve_rerun.py")


# ---------------------------------------------------------------- source/units
def test_active_curve_is_oedb():
    assert POWER_CURVE_ID == "OEDB_V164_9500"
    assert POWER_CURVE_MS_KW is POWER_CURVE_OEDB_V164_9500_MS_KW


def test_active_curve_matches_oedb_source_watts_to_kw():
    src = [(float(r["wind_speed_ms"]), float(r["power_W"]) / 1000.0)
           for r in csv.DictReader(open(ROOT / "docs/review/phase1_data/oedb_V164_power_curves.csv"))
           if r["turbine_type"] == "V164/9500"]
    assert len(src) == 49
    assert POWER_CURVE_MS_KW[:49] == src
    # only the three documented boundary points are added
    assert POWER_CURVE_MS_KW[49:] == [(25.0, 9500.0), (25.01, 0.0), (30.0, 0.0)]


def test_rated_power_units():
    assert max(p for _, p in POWER_CURVE_MS_KW) == RATED_KW == 9500.0


def test_original_curve_retained_unchanged():
    d = dict(POWER_CURVE_ORIGINAL_MS_KW)
    assert len(POWER_CURVE_ORIGINAL_MS_KW) == 27
    assert (d[8.0], d[9.0], d[12.5], d[13.0], d[25.01]) == (3690, 5320, 9450, 9500, 0)


# ------------------------------------------------------------- physical limits
@pytest.mark.parametrize("curve", [POWER_CURVE_MS_KW])
def test_speeds_strictly_increasing(curve):
    v = [c[0] for c in curve]
    assert all(b > a for a, b in zip(v, v[1:]))


def test_monotonic_non_decreasing_below_cut_out():
    p = [pk for v, pk in POWER_CURVE_MS_KW if v <= TURBINE.cut_out_ms]
    assert all(b >= a for a, b in zip(p, p[1:]))


def test_cp_below_betz_and_documented_peak():
    v = np.array([c[0] for c in POWER_CURVE_MS_KW])
    p = np.array([c[1] for c in POWER_CURVE_MS_KW])
    m = (v > 0) & (p > 0)
    cp = p[m] * 1000 / (0.5 * RHO * AREA * v[m] ** 3)
    assert cp.max() < BETZ
    assert cp.max() == pytest.approx(0.4762, abs=2e-4)
    assert v[m][np.argmax(cp)] == 8.5


def test_original_curve_cp_flags_implausible():
    v = np.array([c[0] for c in POWER_CURVE_ORIGINAL_MS_KW])
    p = np.array([c[1] for c in POWER_CURVE_ORIGINAL_MS_KW], float)
    m = (v > 0) & (p > 0)
    assert (p[m] * 1000 / (0.5 * RHO * AREA * v[m] ** 3)).max() > 0.56


# ------------------------------------------ cut-in / rated / cut-out behaviour
def test_cut_in_rated_cut_out_points():
    d = dict(POWER_CURVE_MS_KW)
    assert d[3.0] == 0.0 and d[3.5] == 115.0
    first_rated = min(v for v, p in POWER_CURVE_MS_KW if p >= RATED_KW)
    assert first_rated == TURBINE.rated_ms == 14.0
    assert TURBINE.cut_in_ms == 3.5 and TURBINE.cut_out_ms == 25.0


def test_script06_grid_behaviour(s06):
    v, p = s06.make_power_grid()
    assert p.min() >= 0 and p.max() <= RATED_KW
    assert np.all(p[v >= 25.0 - 1e-9] == 0.0)
    assert np.all(p[(v >= 14.0 - 1e-9) & (v < 25.0 - 1e-9)] == RATED_KW)
    assert np.all(p[v <= 3.0 + 1e-9] == 0.0)


def test_script04_speed_behaviour(s04):
    u = np.array([0.0, 2.9, 3.2, 3.49, 3.5, 8.25, 14.0, 24.6, 24.99, 25.0, 26.0, 40.0])
    p = s04.power_from_speed(u.copy())
    assert np.all(p[:4] == 0.0)          # below cut-in zeroed (script 04 convention)
    assert p[4] == 115.0
    assert p[5] == pytest.approx((3123.0 + 3784.0) / 2)   # linear interpolation
    assert p[6] == RATED_KW and p[7] == RATED_KW and p[8] == RATED_KW
    assert np.all(p[9:] == 0.0)           # at/above cut-out


def test_linear_interpolation_midpoints(s04):
    pts = POWER_CURVE_MS_KW[7:28]         # 3.5 .. 13.5 m/s
    mids = np.array([(a[0] + b[0]) / 2 for a, b in zip(pts, pts[1:])])
    exp = np.array([(a[1] + b[1]) / 2 for a, b in zip(pts, pts[1:])])
    assert np.allclose(s04.power_from_speed(mids), exp, rtol=0, atol=1e-9)


def test_production_scripts_use_active_curve(s04, s06, p2a):
    v6, g6 = s06.make_power_grid()
    v2, g2 = p2a.power_grid(POWER_CURVE_MS_KW)
    assert np.array_equal(v6, v2) and np.array_equal(g6, g2)
    u = np.linspace(0, 30, 3001)
    assert np.array_equal(s04.power_from_speed(u.copy()),
                          p2a.power_from_speed(u.copy(), POWER_CURVE_MS_KW))


# ------------------------------------------------------------ reproducibility
def test_baseline_archive_intact_and_root_copies_retired():
    for line in (BASELINE / "SHA256SUMS").read_text().split("\n"):
        if not line.strip():
            continue
        digest, name = line.split()
        assert hashlib.sha256((BASELINE / name).read_bytes()).hexdigest() == digest
        # Phase 4B: the pre-2A outputs no longer sit in the active results/ root
        assert not (ROOT / "results" / name).exists()


def _base_params():
    b = json.loads((BASELINE / "monte_carlo_results.json").read_text())
    w = b["base_weibull"]
    return w["k"], w["c"], w["sigma_c_interannual"], b["n_iterations"], b["seed"]


def test_mc_original_curve_reproduces_archive_bit_for_bit(p2a):
    k0, c0, sc, n, seed = _base_params()
    r = p2a.run_mc(POWER_CURVE_ORIGINAL_MS_KW, k0, c0, sc, n, seed)
    z = np.load(BASELINE / "monte_carlo_samples.npz")
    for key in ("aep_per_mw", "cf_net", "avoided_per_mw"):
        assert np.array_equal(r[key], z[key])


def test_mc_corrected_curve_reproduces_provisional_bit_for_bit(p2a):
    k0, c0, sc, n, seed = _base_params()
    r = p2a.run_mc(POWER_CURVE_MS_KW, k0, c0, sc, n, seed)
    z = np.load(PROVISIONAL / "monte_carlo_samples.npz")
    for key in ("aep_per_mw", "cf_net", "avoided_per_mw"):
        assert np.array_equal(r[key], z[key])
    assert np.median(r["aep_per_mw"]) == pytest.approx(2.366, abs=5e-4)


def test_weibull_relative_change(p2a):
    k0, c0, *_ = _base_params()
    g = {}
    for name, curve in (("o", POWER_CURVE_ORIGINAL_MS_KW), ("n", POWER_CURVE_MS_KW)):
        v, p = p2a.power_grid(curve)
        g[name] = p2a.weibull_gross_cf(k0, c0, v, p)
    assert g["o"] * 100 == pytest.approx(35.54, abs=0.01)
    assert g["n"] * 100 == pytest.approx(32.06, abs=0.01)
    assert g["n"] / g["o"] - 1 == pytest.approx(-0.0978, abs=5e-4)


# ------------------------------------------------- empirical (needs parquet)
PARQUET = ROOT / "data" / "processed" / "wind_hub_105m.parquet"


@pytest.mark.skipif(not PARQUET.exists(), reason="wind_hub_105m.parquet not available")
def test_empirical_aep_original_exact_and_corrected_regression(p2a):
    import pandas as pd
    u = pd.read_parquet(PARQUET)["U_hub"].values
    assert u.size == 96432
    base = json.loads((BASELINE / "weibull_aep_results.json").read_text())
    g_old = p2a.power_from_speed(u, POWER_CURVE_ORIGINAL_MS_KW).sum() / 11 / 1e6
    assert g_old == base["aep"]["gross_aep_per_turbine_gwh"]       # bit-for-bit
    g_new = p2a.power_from_speed(u, POWER_CURVE_MS_KW).sum() / 11 / 1e6
    assert g_new == pytest.approx(27.2021, abs=1e-4)
    assert g_new / g_old - 1 == pytest.approx(-0.10554, abs=1e-5)
