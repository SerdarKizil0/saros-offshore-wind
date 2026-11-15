"""
Phase 5C-1: publication figure set, provenance, semantics and manuscript integration.

Figure 1 (the map) has its own detailed tests in tests/test_fig1_site_map.py; this
file covers Figures 2-4 in detail and all four figures at set level. The committed
figures are compared with the generators by content (SVG markup without metadata,
decoded PNG pixels, PDF page facts), never by compressed bytes.
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import struct
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.lines import Line2D
from matplotlib.text import Text
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REV = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
MAN = ROOT / "manuscript"
W_PT = 180 / 25.4 * 72


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def J(name):
    return json.loads((REV / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def b12():
    return _load("build12_t", "scripts/12_build_figures.py")


@pytest.fixture(scope="module")
def mods(b12):
    return {stem: b12.load(gen) for _, stem, gen in b12.FIGURES}


@pytest.fixture(scope="module")
def built(mods):
    out = {}
    for stem, m in mods.items():
        d = m.load_data()
        out[stem] = (m, d, m.build_figure(d))
    yield out
    for _, _, fig in out.values():
        plt.close(fig)


@pytest.fixture(scope="module")
def fresh(b12, tmp_path_factory):
    tmp = tmp_path_factory.mktemp("figures")
    b12.build(tmp)
    return tmp


def texts(fig):
    return [t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]


def ax(fig, label):
    return next(a for a in fig.axes if a.get_label() == label)


def drawn_lines(axis):
    return [ln for ln in axis.lines if ln.get_linestyle() not in ("None", "none", "")]


def markers(axis, gid):
    return [ln for ln in axis.lines if ln.get_gid() == gid]


STEMS = ["fig1_site_map", "fig2_temporal_sensitivity", "fig3_nodes_and_products", "fig4_sensitivity_categories"]


# ===================================================================== set level
def test_the_figure_set_is_the_planned_compact_set(b12):
    assert [(n, s) for n, s, _ in b12.FIGURES] == list(enumerate(STEMS, start=1))
    committed = sorted(p.name for p in FIG_DIR.iterdir())
    assert committed == sorted(f"{s}.{e}" for s in STEMS for e in ("pdf", "svg", "png"))   # nothing stale
    for _, _, gen in b12.FIGURES:
        assert (ROOT / "scripts" / gen).exists()
    assert not list((ROOT / "scripts").glob("phase4c_*.py"))                              # retired generators


def test_committed_figures_match_the_generators_by_content(b12, fresh):
    problems = [p for s in STEMS for p in b12.compare(FIG_DIR, fresh, s)]
    assert problems == []


def test_content_comparison_detects_a_real_change(b12, fresh, tmp_path):
    for ext in ("pdf", "svg", "png"):
        shutil.copy(fresh / f"fig2_temporal_sensitivity.{ext}", tmp_path)
    png = tmp_path / "fig2_temporal_sensitivity.png"
    with Image.open(png) as im:
        arr = np.asarray(im.convert("RGBA")).copy()
    arr[100:110, 100:110] = (255, 0, 0, 255)
    Image.fromarray(arr).save(png)
    svg = tmp_path / "fig2_temporal_sensitivity.svg"
    svg.write_text(svg.read_text(encoding="utf-8").replace("2.354", "2.427", 1), encoding="utf-8")
    problems = " | ".join(b12.compare(tmp_path, fresh, "fig2_temporal_sensitivity"))
    assert "png pixels differ" in problems and "svg differs" in problems
    # recompressing the same pixels is not a change
    for ext in ("svg", "png"):
        shutil.copy(fresh / f"fig2_temporal_sensitivity.{ext}", tmp_path)
    with Image.open(png) as im:
        im.save(png, compress_level=1)
    assert b12.compare(tmp_path, fresh, "fig2_temporal_sensitivity") == []


@pytest.mark.parametrize("stem", STEMS)
def test_generators_read_only_authoritative_inputs(stem, b12):
    gen = dict((s, g) for _, s, g in b12.FIGURES)[stem]
    src = (ROOT / "scripts" / gen).read_text(encoding="utf-8")
    assert "from config import figure_style as fs" in src
    assert not re.findall(r"#[0-9A-Fa-f]{6}\b", src)                     # colours from the shared style
    assert "rc_context(" not in src and "savefig(" not in src
    assert "results/archive" not in src and "2014_2024_cds" not in src and '"archive"' not in src
    assert 'ROOT / "results" / "revised"' in src
    assert not re.search(r"monte|random|np\.random", src, re.I)
    assert not re.findall(r"requests|urllib|http[s]?://", src)


@pytest.mark.parametrize("stem", STEMS)
def test_layout_typography_and_strokes(stem, built):
    m, _, fig = built[stem]
    assert m.layout_problems(fig) == []
    found = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    assert {t.get_fontname() for t in found} == {"DejaVu Sans"}
    assert {t.get_fontsize() for t in found} <= {7.0, 8.0, 8.5}
    widths = [ln.get_linewidth() for ln in fig.findobj(Line2D) if ln.get_visible()
              and ln.get_linestyle() not in ("None", "none")]
    assert widths and min(widths) >= 0.5


@pytest.mark.parametrize("stem", STEMS)
def test_exports_are_180_mm_vector_with_editable_text(stem, fresh):
    pdf = (fresh / f"{stem}.pdf").read_bytes()
    box = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
    assert float(box.group(3)) == pytest.approx(W_PT, abs=0.01)
    assert b"/FontFile2" in pdf and b"/Type3" not in pdf
    images = len(re.findall(rb"/Subtype\s*/Image", pdf))
    assert images <= (2 if stem == "fig1_site_map" else 0)             # only the map's bathymetry raster
    svg = (fresh / f"{stem}.svg").read_text(encoding="utf-8")
    assert "<text" in svg
    w = float(re.search(r'<svg[^>]*\bwidth="([\d.]+)pt"', svg, re.S).group(1))
    assert w == pytest.approx(W_PT, abs=0.01)
    px_w, _ = struct.unpack(">II", (fresh / f"{stem}.png").read_bytes()[16:24])
    assert px_w / 600 * 25.4 == pytest.approx(180, abs=0.05)


def _svg_words(path: Path) -> str:
    svg = path.read_text(encoding="utf-8")
    return " ".join(re.sub(r"<[^>]+>", "", t) for t in re.findall(r"<text\b.*?</text>", svg, re.S))


@pytest.mark.parametrize("stem", STEMS)
def test_no_retired_values_or_probability_language_in_figures(stem, fresh, built):
    words = " ".join(texts(built[stem][2])) + " " + _svg_words(fresh / f"{stem}.svg")
    assert words.strip()
    for bad in (r"\bS4\b", r"\bP\d0\b", r"Monte", r"2\.427", r"1,515|1 515|1515", r"confidence", r"±",
                r"\btotal\b", r"\bcombined\b", r"\bbounds?\b", r"Weibull", r"CO", r"validat", r"uncertainty range"):
        assert not re.search(bad, words), (stem, bad)
    assert "interval" not in words or stem == "fig4_sensitivity_categories"


# ===================================================================== Figure 2
def test_fig2_annual_values_and_mean_come_from_the_results(built):
    m, d, fig = built["fig2_temporal_sensitivity"]
    ann = pd.read_csv(REV / "annual_energy.csv")
    a = ax(fig, "panel_a")
    (pts,) = markers(a, "annual_values")
    assert list(pts.get_xdata()) == list(ann["year"]) == list(range(1994, 2025))
    assert np.array_equal(pts.get_ydata(), ann["net_gwh_per_mw_8766h"].to_numpy())
    (mean,) = markers(a, "primary_mean")
    assert mean.get_ydata()[0] == J("energy_yield.json")["net"]["gwh_per_mw"]
    assert J("energy_yield.json")["period"] == "1994-2024"
    assert [ln.get_gid() for ln in drawn_lines(a)] == ["primary_mean"]          # no stems or whiskers
    t = " ".join(texts(fig))
    for token in ("Annual net yield, 1994–2024", "1994–2024 mean", "2014–2024 comparison period",
                  "Rolling 11-year windows, 1979–2024", "GWh MW$^{-1}$ yr$^{-1}$"):
        assert token in t, token
    for yr in (2001, 2002, 2014):                                           # labelled years use (v/mean-1)
        assert f"{yr}  " in t and f"{d.rel_pct(yr):+.1f}".replace("-", "−") in t


def test_fig2_windows_are_the_stored_windows_and_2014_2024_is_emphasised(built):
    m, d, fig = built["fig2_temporal_sensitivity"]
    roll = pd.read_csv(REV / "rolling_11yr_windows.csv").sort_values("start_year")
    b = ax(fig, "panel_b")
    pts = {g: markers(b, g)[0] for g in ("windows_inside", "windows_before_1994", "window_2014_2024")}
    xs = np.concatenate([p.get_xdata() for p in pts.values()])
    ys = np.concatenate([p.get_ydata() for p in pts.values()])
    got = sorted(zip(xs, ys))
    want = sorted(zip(roll["end_year"], roll["rel_to_primary_mean_pct"]))
    assert len(got) == 36 and np.allclose(got, want, rtol=0, atol=0)
    inside = roll[roll.within_primary_period]
    assert len(pts["windows_inside"].get_xdata()) + 1 == len(inside) == 21
    assert set(pts["windows_before_1994"].get_xdata()) == set(roll[~roll.within_primary_period]["end_year"])
    assert pts["window_2014_2024"].get_xdata()[0] == 2024
    assert pts["window_2014_2024"].get_ydata()[0] == roll["rel_to_primary_mean_pct"].max()
    assert [ln.get_gid() for ln in drawn_lines(b)] == ["primary_reference"]


# ===================================================================== Figure 3
def test_fig3_node_values_come_from_the_results_and_are_not_joined(built):
    m, d, fig = built["fig3_nodes_and_products"]
    nodes = J("node_sensitivity.json")["nodes"]
    a = ax(fig, "panel_a")
    for k in ("W", "C", "E"):
        (p,) = markers(a, f"node_{k}")
        assert (p.get_xdata()[0], p.get_ydata()[0]) == (nodes[k]["lon"], nodes[k]["net_gwh_per_mw"])
    assert {ln.get_gid() for ln in drawn_lines(a)} == {"cell_boundary"}           # nothing joins the nodes
    t = " ".join(texts(fig))
    for k in ("W", "C", "E"):
        assert f"land fraction\n{nodes[k]['era5_land_sea_mask_fraction']:.2f}" in t
        assert f"{nodes[k]['net_gwh_per_mw']:.3f}" in t
    for k in ("W", "E"):
        assert f"{nodes[k]['energy_rel_to_primary_node_pct']:+.1f}".replace("-", "−") + " %" in t
    assert "ERA5, 1994–2024" in t


def test_fig3_products_use_the_matched_gwa_period(built):
    m, d, fig = built["fig3_nodes_and_products"]
    wp = J("wind_product_discrepancy.json")
    assert wp["products"]["gwa4"]["period"] == "2008-2017"
    b = ax(fig, "panel_b")
    box = wp["per_node_gwa_box_vs_era5"]
    (era5,) = markers(b, "era5_u100")
    (gwa,) = markers(b, "gwa_cell_sea")
    assert list(era5.get_ydata()) == [box[k]["era5_U100_ms"]["2008-2017"] for k in ("W", "C", "E")]
    assert list(gwa.get_ydata()) == [box[k]["gwa4_100m_ms"]["box_0p25deg_sea_pixels_mean_ms"]
                                     for k in ("W", "C", "E")]
    (poly,) = markers(b, "gwa_polygon_mean")
    assert set(poly.get_ydata()) == {wp["products"]["gwa4"]["polygon_mean_ms"]}
    from config.site import SAROS_POLYGON_LONLAT
    lons = [p[0] for p in SAROS_POLYGON_LONLAT]
    assert tuple(poly.get_xdata()) == (min(lons), max(lons))
    t = " ".join(texts(fig))
    for k in ("W", "C", "E"):
        assert f"×{box[k]['ratio_gwa_box_sea_pixels_to_era5_period_matched']:.2f}" in t
    ratio = wp["polygon_vs_primary_node"]["ratio_gwa_to_era5"]["era5_2008-2017_period_matched"]
    assert f"polygon mean ×{ratio:.2f}" in t
    assert t.count("2008–2017") >= 3 and "GWA 4.0" in t and "m s$^{-1}$" in t
    assert {ln.get_gid() for ln in drawn_lines(b)} == {"cell_boundary", "gwa_polygon_mean"}
    edges = sorted(ln.get_xdata()[0] for ln in markers(b, "cell_boundary"))
    assert edges == [26.125, 26.375]


# ===================================================================== Figure 4
def test_fig4_rows_follow_the_index_and_are_never_combined(built):
    m, d, fig = built["fig4_sensitivity_categories"]
    idx = J("sensitivity_index.json")
    assert idx["combinable_into_one_interval"] is False
    assert d.order == tuple(c["category"] for c in idx["categories"])
    a = ax(fig, "categories")
    # every data mark sits within exactly one row; only the reference and separators span rows.
    # Rows 2 and 3 stack dots that would overlap (vertical offsets < 0.4 row), x is never moved.
    for ln in a.lines:
        if ln.get_gid() in ("primary_reference", "row_separator"):
            continue
        ys = np.asarray(ln.get_ydata(), float)
        centre = np.round(ys)
        assert len(set(centre)) == 1 and np.all(np.abs(ys - centre) < 0.4), ln.get_gid()
        if ln.get_gid() not in ("annual_values", "windows", "window_2014_2024"):
            assert np.all(ys == centre), ln.get_gid()
    rows = {ln.get_gid(): int(np.round(ln.get_ydata()[0])) for ln in a.lines
            if ln.get_gid() not in ("primary_reference", "row_separator")}
    assert rows["sampling_interval"] == 0 and rows["annual_values"] == 1 and rows["windows"] == 2
    assert rows["node"] == 3 and rows["product_scaled"] == 4 and rows["loss"] == 5
    kinds = [t.get_text() for t in fig.texts if (t.get_gid() or "").startswith("kind_")]
    assert len(kinds) == 6 and [k for k in kinds if "probabilistic" in k] == ["the only probabilistic interval"]
    assert kinds[0] == "the only probabilistic interval"
    t = " ".join(texts(fig))
    assert not re.search(r"\b(total|sum|combined|envelope|overall|RSS)\b", t, re.I)


def test_fig4_stacked_dots_do_not_overlap(built):
    m, d, fig = built["fig4_sensitivity_categories"]
    a = ax(fig, "categories")
    for gids in (("annual_values",), ("windows", "window_2014_2024")):
        pts = np.concatenate([np.c_[ln.get_xdata(), ln.get_ydata()] for ln in a.lines if ln.get_gid() in gids])
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                dx, dy = abs(pts[i, 0] - pts[j, 0]), abs(pts[i, 1] - pts[j, 1])
                assert dx >= m.DOT_GAP_PCT - 1e-9 or dy >= m.DODGE_STEP - 1e-9, (gids, pts[i], pts[j])
    caption = (MAN / "09_figures.md").read_text(encoding="utf-8")
    assert "vertical position within a row has no meaning" in " ".join(caption.split())


def test_fig4_values_come_from_the_results(built):
    m, d, fig = built["fig4_sensitivity_categories"]
    a = ax(fig, "categories")
    ey, ias = J("energy_yield.json"), J("interannual_and_sampling.json")
    p = ey["net"]["gwh_per_mw"]
    lo, hi = ias["sampling_ci_of_period_mean"]["primary_t_interval_90"]["net_gwh_per_mw"]
    (ci,) = markers(a, "sampling_interval")
    assert np.allclose(ci.get_xdata(), [(lo / p - 1) * 100, (hi / p - 1) * 100], rtol=0, atol=1e-12)
    hw = ias["sampling_ci_of_period_mean"]["primary_t_interval_90"]["half_width_rel_pct"]
    assert np.diff(ci.get_xdata())[0] / 2 == pytest.approx(hw, abs=1e-9)
    (ann,) = markers(a, "annual_values")
    want = (pd.read_csv(REV / "annual_energy.csv")["net_gwh_per_mw_8766h"] / p - 1) * 100
    assert np.allclose(sorted(ann.get_xdata()), sorted(want), rtol=0, atol=1e-12)
    roll = pd.read_csv(REV / "rolling_11yr_windows.csv")
    inside = roll[roll.within_primary_period]["rel_to_primary_mean_pct"]
    wins = list(markers(a, "windows")[0].get_xdata()) + list(markers(a, "window_2014_2024")[0].get_xdata())
    assert sorted(wins) == sorted(inside) and markers(a, "window_2014_2024")[0].get_xdata()[0] == inside.max()
    nodes = J("node_sensitivity.json")["nodes"]
    assert sorted(ln.get_xdata()[0] for ln in markers(a, "node")) == sorted(
        nodes[k]["energy_rel_to_primary_node_pct"] for k in ("W", "E"))
    scaled = J("wind_product_discrepancy.json")["energy_sensitivity_if_primary_hours_were_scaled"][
        "by_ratio_era5_2008-2017_period_matched"]
    (prod,) = markers(a, "product_scaled")
    assert prod.get_xdata()[0] == scaled["aep_change_vs_primary_pct"]
    assert prod.get_markerfacecolor() != prod.get_markeredgecolor()                  # open: not adopted
    ls = J("loss_scenarios.json")["scenarios"]
    assert sorted(ln.get_xdata()[0] for ln in markers(a, "loss")) == sorted(
        [ls["low_loss"]["rel_to_nominal_pct"], ls["high_loss"]["rel_to_nominal_pct"]])
    t = " ".join(texts(fig))
    assert "1994–2024" in t and "2008–2017" in t and "(%)" in a.get_xlabel()
    assert "not adopted" in t and f"{p:.3f}" in t


# ===================================================================== manuscript integration
CAPS = MAN / "09_figures.md"


def _captions() -> dict[int, str]:
    text = CAPS.read_text(encoding="utf-8")
    parts = re.split(r"\*\*Figure (\d)\.\*\*", text)
    return {int(n): " ".join(body.split("![Figure")[0].split()) for n, body in zip(parts[1::2], parts[2::2])}


def test_every_figure_has_one_caption_and_the_right_file():
    caps = _captions()
    assert sorted(caps) == [1, 2, 3, 4]
    links = re.findall(r"!\[Figure (\d)\]\(\.\./figures/revised/([\w]+)\.png\)", CAPS.read_text(encoding="utf-8"))
    assert [(int(n), s) for n, s in links] == list(enumerate(STEMS, start=1))
    src = (MAN / "src" / "09_figures.md").read_text(encoding="utf-8")
    assert "{{" in src                                                     # captions take numbers from results


def test_captions_state_period_units_and_limits():
    c = _captions()
    for n in (2, 3, 4):
        assert "1994–2024" in c[n], n
    assert "2008–2017" in c[3] and "GWA reference period" in c[3]
    assert "GWh MW⁻¹ yr⁻¹" in c[2] and "GWh MW⁻¹ yr⁻¹" in c[3]
    assert "not independent samples" in c[2] and "not observed production" in c[2]
    assert "not averaged" in c[3] and "not limits on the resource" in c[3]
    assert "not an observation or ground truth" in c[3] and "not used to correct the primary estimate" in c[3]
    assert "the only probabilistic interval" in c[4] and "not combined" in c[4]
    assert "not samples of one distribution" in c[4] and "not adopted" in c[4]
    assert "not an official verified boundary" in c[1] and "not an approved project" in c[1]
    assert "no turbine layout" in c[1]
    ey = J("energy_yield.json")
    assert f"{ey['net']['gwh_per_mw']:.3f} GWh MW⁻¹ yr⁻¹" in c[2]


def test_figures_are_called_out_in_order_and_all_are_cited():
    order = ["02_study_area.md", "03_methodology.md", "04_results.md", "05_discussion.md"]
    text = " ".join(" ".join((MAN / n).read_text(encoding="utf-8").split()) for n in order)
    calls = [int(n) for n in re.findall(r"\bFigs?\. (\d)[a-z]?", text)]
    assert set(calls) == {1, 2, 3, 4}
    first = list(dict.fromkeys(calls))
    assert first == [1, 2, 3, 4]                                           # first call-outs in numerical order
    for n in ("00_abstract.md", "01_introduction.md", "06_conclusion.md", "07_declarations.md"):
        assert not re.search(r"\bFigs?\. \d", (MAN / n).read_text(encoding="utf-8")), n
    assert not re.search(r"\bFigs?\. [5-9]", text)
    # panel call-outs exist for the two-panel figures
    for panel in ("Fig. 2a", "Fig. 2b", "Fig. 3a", "Fig. 3b"):
        assert panel in text, panel


def test_figure_style_docstring_no_longer_points_to_retired_scripts():
    src = (ROOT / "config" / "figure_style.py").read_text(encoding="utf-8")
    assert "phase4c_fig" not in src
