"""
Tests for the Phase 4C figure set: methodology, wind/Weibull, power curve,
energy sensitivity, avoided CO2, and the contact sheet.
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import importlib.util
import json
import re
import struct
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.text import Text

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIG_DIR = ROOT / "figures" / "revised"
RES = ROOT / "results" / "revised"
W_PT = 180 / 25.4 * 72
NEW = ("methodology", "wind_weibull", "power_curve", "energy_sensitivity", "avoided_co2")


def _load(name):
    spec = importlib.util.spec_from_file_location(f"p4c_{name}", SCRIPTS / f"phase4c_fig_{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mods():
    return {n: _load(n) for n in NEW}


@pytest.fixture(scope="module")
def built(mods):
    out = {}
    for n, m in mods.items():
        d = m.load_data()
        res = m.build_figure(d)
        fig, extra = (res if isinstance(res, tuple) else (res, None))
        out[n] = (m, d, fig, extra)
    yield out
    for _, _, fig, _ in out.values():
        plt.close(fig)


@pytest.fixture(scope="module")
def outputs(mods, tmp_path_factory):
    tmp = tmp_path_factory.mktemp("figs")
    return {n: m.main(tmp) for n, m in mods.items()}


def _json(name):
    return json.loads((RES / name).read_text(encoding="utf-8"))


def _texts(fig):
    return [t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]


# ---- headline values and model identity ----------------------------------------
def test_headline_values_are_the_revised_ones():
    ey, em = _json("energy_yield.json"), _json("emissions.json")
    assert ey["net"]["gwh_per_mw"] == pytest.approx(2.4274, abs=5e-5)
    assert em["primary_avoided_operational_co2"]["t_co2_per_mw_yr"] == pytest.approx(1515.2, abs=0.05)
    assert ey["power_curve"] == "OEDB_V164_9500"
    assert ey["estimator"].startswith("empirical hourly power conversion")


def test_sensitivity_figure_uses_the_central_estimate(built):
    _, d, fig, _ = built["energy_sensitivity"]
    assert d.central == pytest.approx(2.4274, abs=5e-5)
    assert any("central estimate 2.427" in t for t in _texts(fig))


def test_co2_figure_primary_value(built):
    _, d, fig, _ = built["avoided_co2"]
    primary = [r for r in d.grid if r.primary]
    assert len(primary) == 1 and primary[0].value == pytest.approx(1515.2, abs=0.05)
    assert primary[0].label.startswith("Combined margin")


# ---- layout and export --------------------------------------------------------------
@pytest.mark.parametrize("name", NEW)
def test_layout_is_clean(built, name):
    m, _, fig, extra = built[name]
    problems = m.layout_problems(fig, extra) if extra is not None else m.layout_problems(fig)
    assert problems == []
    fonts = {t.get_fontname() for t in fig.findobj(Text) if t.get_text().strip()}
    assert fonts == {"DejaVu Sans"}
    sizes = {t.get_fontsize() for t in fig.findobj(Text) if t.get_text().strip()}
    assert min(sizes) >= 7.0 and sizes <= {7.0, 8.0, 8.5}


@pytest.mark.parametrize("name", NEW)
def test_exports_are_180_mm_vector_and_editable(outputs, name):
    paths = outputs[name]
    pdf = paths["pdf"].read_bytes()
    box = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
    assert float(box.group(3)) == pytest.approx(W_PT, abs=0.01)
    assert b"/FontFile2" in pdf and b"/Type3" not in pdf
    assert not re.findall(rb"/Subtype\s*/Image", pdf)                 # fully vector
    svg = paths["svg"].read_text(encoding="utf-8")
    assert "<text" in svg and "<image" not in svg
    w = float(re.search(r'<svg[^>]*\bwidth="([\d.]+)pt"', svg, re.S).group(1))
    assert w == pytest.approx(W_PT, abs=0.01)
    px_w, _ = struct.unpack(">II", paths["png"].read_bytes()[16:24])
    assert px_w / 600 * 25.4 == pytest.approx(180, abs=0.05)


@pytest.mark.parametrize("name", NEW)
def test_committed_outputs_match_the_generator(outputs, name):
    for ext in ("pdf", "svg", "png", "caption"):
        new = outputs[name][ext]
        committed = FIG_DIR / new.name
        assert committed.exists(), committed
        assert committed.read_bytes() == new.read_bytes(), f"{new.name} is stale"


@pytest.mark.parametrize("name", NEW)
def test_generators_take_style_and_data_from_shared_sources(name):
    src = (SCRIPTS / f"phase4c_fig_{name}.py").read_text(encoding="utf-8")
    assert "from config import figure_style as fs" in src
    assert not re.findall(r"#[0-9A-Fa-f]{6}\b", src)
    assert "rc_context(" not in src and "savefig(" not in src
    assert "results/archive" not in src and "provisional" not in src
    assert "monte_carlo" not in src.lower()


# ---- retired items never appear ---------------------------------------------------------
@pytest.mark.parametrize("name", NEW)
def test_no_retired_scenario_or_values(outputs, name):
    svg = outputs[name]["svg"].read_text(encoding="utf-8")
    svg_text = " ".join(re.sub(r"<[^>]+>", "", t) for t in re.findall(r"<text\b.*?</text>", svg, re.S))
    assert svg_text.strip()
    cap = outputs[name]["caption"].read_text(encoding="utf-8")
    for s in (svg_text, cap):          # rendered words only, not SVG path coordinates
        assert not re.search(r"\bS4\b|1738\.5|1,738|1 738|4\.56 TWh", s)
        assert "P10–P90" not in s and "2.62" not in s


# ---- Weibull figure ---------------------------------------------------------------------
def test_weibull_figure_uses_every_hour_and_the_committed_fit(built):
    m, d, fig, _ = built["wind_weibull"]
    assert len(d.u) == 96432 and not np.isnan(d.u).any()
    assert np.sum(d.density * np.diff(d.edges)) == pytest.approx(1.0, abs=1e-12)
    counts, _ = np.histogram(d.u, bins=d.edges)
    assert counts.sum() == len(d.u)                         # nothing dropped or added
    w = _json("weibull_crosscheck.json")["weibull_fit_U_hub"]
    assert (d.k, d.c) == (w["k_mle"], w["c_mle_ms"])
    spec = importlib.util.spec_from_file_location("e04", SCRIPTS / "04_fit_weibull_aep.py")
    e04 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(e04)
    refit = e04.fit_weibull(d.u)
    assert (refit["k_mle"], refit["c_mle_ms"]) == pytest.approx((d.k, d.c), rel=1e-6)
    from scipy import stats
    tail = stats.weibull_min.sf(d.edges[-1], d.k, 0, d.c)        # Weibull mass above the last edge
    assert d.weibull_bin_density.sum() * 0.5 == pytest.approx(1.0 - tail, abs=1e-12)


def test_weibull_caption_does_not_claim_energy_accuracy(mods, built):
    _, d, _, _ = built["wind_weibull"]
    c = mods["wind_weibull"].caption(d)
    assert "does not establish agreement in energy" in c and "cross-check only" in c
    assert "no p-value is interpreted" in c


# ---- power curve ---------------------------------------------------------------------------
def test_power_curve_is_the_active_production_interpolation(built):
    from config import turbine as tcfg
    m, d, fig, _ = built["power_curve"]
    pts = np.asarray(tcfg.POWER_CURVE_OEDB_V164_9500_MS_KW, float)
    assert np.allclose(np.r_[d.oedb, d.boundary], np.c_[pts[:, 0], pts[:, 1] / 1000])
    e04 = m._energy_module()
    assert np.allclose(d.p_line, e04.power_from_speed(d.u_line.copy()) / 1000)
    ax = fig.axes[0]
    drawn = [ln for ln in ax.lines if ln.get_gid() == "production_interpolation"]
    xs = np.concatenate([ln.get_xdata() for ln in drawn])
    ys = np.concatenate([ln.get_ydata() for ln in drawn])
    assert np.allclose(ys, e04.power_from_speed(xs.copy()) / 1000)
    assert ys[xs < tcfg.TURBINE.cut_in_ms].max() == 0 and ys[xs >= tcfg.TURBINE.cut_out_ms].max() == 0
    assert d.oedb[np.argmax(d.oedb[:, 1] >= 9.5), 0] == tcfg.TURBINE.rated_ms


def test_retired_curve_is_marked_superseded(built, mods):
    _, d, fig, _ = built["power_curve"]
    leg = fig.axes[0].get_legend()
    assert any("superseded" in t.get_text() for t in leg.get_texts())
    cap = mods["power_curve"].caption(d)
    assert "not a manufacturer-certified table" in cap and "superseded" in cap


# ---- sensitivity ---------------------------------------------------------------------------
def test_sensitivity_cases_match_results_and_stay_separate(built, mods):
    _, d, fig, _ = built["energy_sensitivity"]
    ws = {c["case"]: c for c in _json("wind_speed_sensitivity.json")["cases"]}
    assert [round(c.pct, 6) for c in d.speed] == [round(ws[k]["aep_change_vs_baseline_pct"], 6)
                                                   for k in ("-10%", "-5%", "+5%", "+10%")]
    ls = _json("loss_scenarios.json")["scenarios"]
    assert [round(c.pct, 6) for c in d.loss] == [round(ls[k]["rel_to_nominal_pct"], 6)
                                                  for k in ("low_loss", "high_loss")]
    labels = {a.get_label() for a in fig.axes}
    assert labels == {"panel_a", "panel_b"}
    bars = {ax.get_label(): [p for p in ax.patches if p.get_gid()] for ax in fig.axes}
    assert len(bars["panel_a"]) == 4 and len(bars["panel_b"]) == 2
    assert not any("GWA" in t for t in _texts(fig))
    cap = mods["energy_sensitivity"].caption(d)
    assert "not combined" in cap and "confidence interval" in cap and "P50/P90" in cap


# ---- avoided CO2 ---------------------------------------------------------------------------
def test_co2_conventions_are_bars_not_bounds_and_lifecycle_is_separate(built, mods):
    _, d, fig, _ = built["avoided_co2"]
    em = _json("emissions.json")
    ctx = em["context_grid_methods"]
    vals = {r.label: r.value for r in d.grid}
    assert vals["Operating margin"] == ctx["operating_margin"]["result_per_mw_yr"]
    assert vals["Build margin"] == ctx["build_margin"]["result_per_mw_yr"]
    assert vals["Generation average"] == ctx["generation_average_co2"]["result_per_mw_yr"]
    ax_a = next(a for a in fig.axes if a.get_label() == "panel_a")
    ax_b = next(a for a in fig.axes if a.get_label() == "panel_b")
    assert not [ln for ln in ax_a.lines if ln.get_linestyle() != "None"]   # no interval drawn in (a)
    assert "CO$_2$-eq" in ax_b.get_xlabel() and "-eq" not in ax_a.get_xlabel()
    lc = em["secondary_lifecycle_ghg"]["cases"]["ipcc_ar5_median"]["t_co2eq_per_mw_yr"]
    assert d.lifecycle == lc
    # nothing subtracted: no plotted value equals primary minus life cycle
    net = [r.value for r in d.grid if r.primary][0] - lc
    assert not any(f"{net:,.0f}" in t for t in _texts(fig))
    assert not any(re.search(r"\bS[1-4]\b", t) for t in _texts(fig))
    cap = mods["avoided_co2"].caption(d)
    assert "not uncertainty bounds" in cap and "not subtracted" in cap


# ---- methodology diagram ---------------------------------------------------------------------
def test_methodology_has_no_results_and_weibull_does_not_feed_energy(built, mods):
    m, d, fig, bx = built["methodology"]
    texts = " ".join(_texts(fig))
    ey, em = _json("energy_yield.json"), _json("emissions.json")
    for v in (f"{ey['net']['gwh_per_mw']:.3f}", f"{ey['net']['gwh_per_mw']:.2f}",
              f"{ey['net_cf'] * 100:.1f}", f"{em['primary_avoided_operational_co2']['t_co2_per_mw_yr']:,.0f}",
              f"{em['primary_avoided_operational_co2']['t_co2_per_mw_yr']:.0f}", "1,515", "27.7"):
        assert v not in texts, v
    assert "Monte Carlo" not in texts
    main = ["era5", "hub", "curve", "energy", "losses", "net", "co2"]
    assert all(not bx[k].side for k in main)
    assert all(bx[k].side for k in ("weibull", "sens", "unc"))
    ax = fig.axes[0]
    # the Weibull-to-energy connector carries no arrow head
    heads = [p for p in ax.patches if p.get_gid() == "comparison_line"]
    assert heads == []
    assert [ln for ln in ax.lines if ln.get_gid() == "comparison_line"]
    cap = mods["methodology"].caption(d)
    assert "not used as an input" in cap and "No step uses Monte Carlo" in cap


# ---- contact sheet ---------------------------------------------------------------------------
def test_contact_sheet_lists_every_publication_figure():
    spec = importlib.util.spec_from_file_location("sheet", SCRIPTS / "phase4c_contact_sheet.py")
    sheet = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sheet)
    stems = [s for _, s, _, _ in sheet.FIGURES]
    assert set(NEW) | {"annual_energy_uncertainty", "saros_study_area"} == set(stems)
    assert [n for n, *_ in sheet.FIGURES] == list(range(1, 8))
    for _, s, gen, _ in sheet.FIGURES:
        assert (FIG_DIR / f"{s}.png").exists() and (SCRIPTS / gen).exists()
    assert (FIG_DIR / "contact_sheet.png").exists() and (FIG_DIR / "contact_sheet.pdf").exists()
