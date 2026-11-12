"""
Tests for the Phase 4C figure (annual net energy yield and sampling CI of the mean).
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import csv
import importlib.util
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.text import Text

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase4c_fig_annual_energy_uncertainty.py"
RESULTS = ROOT / "results" / "revised"
W_PT, H_PT = 180 / 25.4 * 72, 125 / 25.4 * 72


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("p4c_fig", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod               # dataclasses resolve annotations via sys.modules
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def data(m):
    return m.load_data()


@pytest.fixture(scope="module")
def fig(m, data):
    f = m.build_figure(data)
    yield f
    plt.close(f)


@pytest.fixture(scope="module")
def outputs(m, tmp_path_factory):
    return m.main(tmp_path_factory.mktemp("fig"))


def _axes(fig):
    return {ax.get_label(): ax for ax in fig.axes}


def _gid(ax, gid):
    (line,) = [ln for ln in ax.lines if ln.get_gid() == gid]
    return line


def _csv_values():
    with open(RESULTS / "annual_energy.csv", newline="") as fh:
        return {int(r["year"]): float(r["net_gwh_per_mw_8766h"]) for r in csv.DictReader(fh)}


def test_data_come_from_results_revised(data):
    assert dict(zip(data.years, data.values)) == _csv_values()
    energy = json.loads((RESULTS / "energy_yield.json").read_text())
    samp = json.loads((RESULTS / "interannual_and_sampling.json").read_text())
    assert data.mean == energy["net"]["gwh_per_mw"]
    assert [data.ci_lo, data.ci_hi] == \
        samp["sampling_ci_of_11yr_mean"]["primary_t_interval_90"]["net_gwh_per_mw"]


def test_regression_values(data):
    assert data.years == tuple(range(2014, 2025))
    assert data.mean == pytest.approx(2.4274, abs=5e-5)
    assert (data.ci_lo, data.ci_hi) == pytest.approx((2.334, 2.520), abs=5e-4)
    assert data.value(2014) == pytest.approx(1.992, abs=5e-4)
    assert data.value(2020) == pytest.approx(2.648, abs=5e-4)
    assert (data.low_year, data.high_year) == (2014, 2020)
    assert f"{data.low_pct_below_mean:.1f}" == "17.9"


def test_no_data_literals_in_the_generator():
    # annual values, mean and CI have >= 3 decimals; none may appear in the source
    assert not re.findall(r"(?<![\w.])[12]\.\d{3,}", SCRIPT.read_text(encoding="utf-8"))


def test_figure_follows_the_data_files(m, tmp_path):
    work = tmp_path / "revised"
    shutil.copytree(RESULTS, work)
    rows = (work / "annual_energy.csv").read_text().splitlines()
    i = next(k for k, r in enumerate(rows) if r.startswith("2017,"))
    cells = rows[i].split(",")
    cells[-1] = str(float(cells[-1]) + 0.01)
    rows[i] = ",".join(cells)
    (work / "annual_energy.csv").write_text("\n".join(rows) + "\n")
    changed = m.load_data(work)
    f = m.build_figure(changed)
    try:
        ax = _axes(f)["panel_a"]
        plotted = dict(zip(_gid(ax, "annual_points").get_ydata(), _gid(ax, "annual_points").get_xdata()))
        assert plotted[changed.years.index(2017)] == pytest.approx(_csv_values()[2017] + 0.01)
    finally:
        plt.close(f)


def test_inconsistent_results_are_rejected(m, tmp_path):
    work = tmp_path / "revised"
    shutil.copytree(RESULTS, work)
    energy = json.loads((work / "energy_yield.json").read_text())
    energy["net"]["gwh_per_mw"] *= 1.1
    (work / "energy_yield.json").write_text(json.dumps(energy))
    with pytest.raises(ValueError):
        m.load_data(work)


def test_every_year_is_plotted_at_its_own_value(fig, data):
    ax = _axes(fig)["panel_a"]
    labels = {int(round(t)): lab.get_text() for t, lab in zip(ax.get_yticks(), ax.get_yticklabels())}
    plotted = {}
    for gid in ("annual_points", "low_year_point"):
        line = _gid(ax, gid)
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            plotted[int(labels[int(y)])] = float(x)
    assert plotted == _csv_values()
    assert int(labels[int(_gid(ax, "low_year_point").get_ydata()[0])]) == data.low_year
    # value labels printed beside the markers agree with the CSV too
    printed = sorted(t.get_text() for t in ax.texts if re.fullmatch(r"\d\.\d{3}", t.get_text()))
    assert printed == sorted(f"{v:.3f}" for v in _csv_values().values())


def test_panel_a_draws_point_estimates_only(fig):
    ax = _axes(fig)["panel_a"]
    assert ax.lines and all(ln.get_linestyle() == "None" for ln in ax.lines)   # markers, no segments
    assert not ax.patches and not ax.collections and not ax.containers


def test_panel_b_shows_the_authoritative_interval(fig, data):
    ax = _axes(fig)["panel_b"]
    assert list(_gid(ax, "ci_interval").get_xdata()) == [data.ci_lo, data.ci_hi]
    assert list(_gid(ax, "mean_marker").get_xdata()) == [data.mean]
    texts = {t.get_text() for t in ax.texts}
    assert {f"{data.ci_lo:.3f}", f"{data.ci_hi:.3f}", f"{data.mean:.3f}"} <= texts


def test_shared_scale_and_unit_label(fig):
    axes = _axes(fig)
    assert set(axes) == {"panel_a", "panel_b"}
    assert axes["panel_a"].get_xlim() == axes["panel_b"].get_xlim() == (1.8, 2.8)
    assert axes["panel_b"].get_xlabel().endswith(r"(GWh MW$^{-1}$ yr$^{-1}$)")
    assert axes["panel_a"].get_xlabel() == ""                      # one x-axis label only
    assert axes["panel_a"].get_position().height > 3 * axes["panel_b"].get_position().height


def test_layout_is_clean_and_fonts_are_bundled(m, fig):
    assert m.layout_problems(fig) == []
    used = {t.get_fontname() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()}
    assert used == {"DejaVu Sans"}
    sizes = {t.get_fontsize() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()}
    assert min(sizes) >= 7.0 and len(sizes) <= 3


def test_exact_180_by_125_mm_outputs(outputs):
    pdf = outputs["pdf"].read_bytes()
    box = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
    assert [float(v) for v in box.groups()] == pytest.approx([0, 0, W_PT, H_PT], abs=0.01)
    assert len(re.findall(rb"/Type\s*/Page\b", pdf)) == 1
    assert b"/Subtype /Image" not in pdf                             # vector only
    assert b"/FontFile2" in pdf and b"/Type3" not in pdf             # embedded TrueType text

    svg = outputs["svg"].read_text(encoding="utf-8")
    w, h = (float(re.search(rf'<svg[^>]*\b{k}="([\d.]+)pt"', svg, re.S).group(1)) for k in ("width", "height"))
    assert (w, h) == pytest.approx((W_PT, H_PT), abs=0.01)
    assert "<text" in svg and "<image" not in svg                    # editable text, no raster

    png = outputs["png"].read_bytes()
    px_w, px_h = struct.unpack(">II", png[16:24])
    assert px_w / 600 * 25.4 == pytest.approx(180, abs=0.05)
    assert px_h / 600 * 25.4 == pytest.approx(125, abs=0.05)


@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="poppler not installed")
def test_pdf_text_has_no_orphaned_unit_symbols(outputs, data):
    text = subprocess.run(["pdftotext", "-layout", str(outputs["pdf"]), "-"],
                          capture_output=True, text=True, check=True).stdout
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    assert "Estimated net annual energy yield (GWh MW−1 yr−1)" in lines
    assert text.count("GWh") == 1
    assert not [ln for ln in lines if re.fullmatch(r"(yr|MW|GWh|[−-]1\)?|\))", ln)]
    for year, value in zip(data.years, data.values):                 # each year shares a line with its value
        (row,) = [ln for ln in lines if ln.startswith(str(year))]
        assert f"{value:.3f}" in row


def test_committed_caption_matches_the_data(m, data):
    committed = ROOT / "figures" / "revised" / "annual_energy_uncertainty_caption.md"
    assert committed.read_text(encoding="utf-8") == m.caption(data)
    for token in (f"{data.mean:.3f}", f"{data.ci_lo:.3f}–{data.ci_hi:.3f}", "sampling uncertainty"):
        assert token in m.caption(data)
