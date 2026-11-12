"""
Tests for the shared publication figure style (config/figure_style.py).
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import figure_style as fs  # noqa: E402


def _luminance(hex_colour: str) -> float:
    rgb = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast_on_white(hex_colour: str) -> float:
    return 1.05 / (_luminance(hex_colour) + 0.05)


# ---- rcParams and the generated style file --------------------------------
def test_rc_is_accepted_by_matplotlib():
    with fs.style():
        for key, value in fs.RC.items():
            assert key in matplotlib.rcParams
            assert matplotlib.rcParams[key] == matplotlib.rcParams.validate[key](value)


def test_mplstyle_file_is_in_sync_with_rc():
    assert fs.MPLSTYLE.read_text(encoding="utf-8") == fs.mplstyle_text(), \
        "run `python -m config.figure_style` to regenerate config/publication.mplstyle"
    with matplotlib.rc_context():
        matplotlib.rcdefaults()
        with fs.style():
            from_module = {k: matplotlib.rcParams[k] for k in fs.RC}
        matplotlib.rcdefaults()
        with plt.style.context(str(fs.MPLSTYLE)):
            from_file = {k: matplotlib.rcParams[k] for k in fs.RC}
    assert from_file == from_module


def test_export_settings_keep_text_and_page_size():
    assert fs.RC["pdf.fonttype"] == 42            # embedded TrueType, not Type 3
    assert fs.RC["svg.fonttype"] == "none"        # editable SVG text
    assert fs.RC["savefig.bbox"] is None          # never "tight": exact page size
    assert fs.RC["savefig.dpi"] == fs.PNG_DPI == 600


def test_font_ships_with_matplotlib():
    path = font_manager.findfont(font_manager.FontProperties(family=fs.FONT_FAMILY),
                                 fallback_to_default=False)
    assert Path(path).name == "DejaVuSans.ttf"
    assert "mpl-data" in Path(path).parts         # bundled, no external font file


# ---- tokens -----------------------------------------------------------------
def test_typography_and_stroke_floors():
    assert min(fs.FS_HEAD, fs.FS_AXIS, fs.FS_NOTE) == fs.MIN_FONT_PT >= 7.0
    weights = [fs.LW_GUIDE, fs.LW_GRID, fs.LW_AXIS, fs.LW_DATA, fs.LW_REF, fs.MEW]
    assert min(weights) >= fs.LW_MIN >= 0.5


def test_palette_is_fixed_and_legible_on_white():
    data = [*fs.CATEGORICAL, *fs.CATEGORICAL_EXTRA]
    assert all(re.fullmatch(r"#[0-9A-F]{6}", c) for c in data)
    assert len(set(data)) == len(data)
    assert (fs.PRIMARY, fs.EMPHASIS) == fs.CATEGORICAL[:2]
    assert list(matplotlib.rcParams.validate["axes.prop_cycle"](
        fs.RC["axes.prop_cycle"]).by_key()["color"]) == list(fs.CATEGORICAL)
    assert all(_contrast_on_white(c) >= 3.0 for c in fs.CATEGORICAL)   # graphical objects
    assert _contrast_on_white(fs.INK) >= 7.0 and _contrast_on_white(fs.MUTED) >= 4.5   # text
    assert _contrast_on_white(fs.AXIS) >= 3.0


def test_units_render_with_mathtext():
    assert fs.UNIT_YIELD == r"GWh MW$^{-1}$ yr$^{-1}$"
    assert fs.UNIT_YIELD_PLAIN == "GWh MW⁻¹ yr⁻¹"


# ---- helpers ----------------------------------------------------------------
@pytest.fixture
def small_fig():
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(88, 60))
        ax = fig.add_axes([0.15, 0.2, 0.8, 0.6])
        ax.plot([0, 1], [0, 1])
        ax.set_xlabel(f"Yield ({fs.UNIT_YIELD})")
    yield fig, ax
    plt.close(fig)


def test_save_figure_exact_size_and_reproducible(small_fig, tmp_path):
    fig, _ = small_fig
    first = fs.save_figure(fig, tmp_path / "a", "probe")
    second = fs.save_figure(fig, tmp_path / "b", "probe")
    for ext in fs.EXPORT_FORMATS:
        assert first[ext].read_bytes() == second[ext].read_bytes(), ext

    w_pt, h_pt = 88 / 25.4 * 72, 60 / 25.4 * 72
    pdf = first["pdf"].read_bytes()
    box = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
    assert [float(v) for v in box.groups()] == pytest.approx([0, 0, w_pt, h_pt], abs=0.01)
    assert b"/FontFile2" in pdf and b"/Subtype /Image" not in pdf
    svg = first["svg"].read_text(encoding="utf-8")
    assert f'width="{w_pt:.5f}'[:12] in svg and "<text" in svg and "<image" not in svg
    px_w, px_h = struct.unpack(">II", first["png"].read_bytes()[16:24])
    # Matplotlib truncates to whole pixels: at 600 dpi that is < 0.05 mm
    assert px_w / 600 * 25.4 == pytest.approx(88, abs=0.05)
    assert px_h / 600 * 25.4 == pytest.approx(60, abs=0.05)


def test_layout_checks_catch_real_problems(small_fig):
    fig, ax = small_fig
    assert fs.layout_problems(fig) == [] and fs.print_problems(fig) == []

    fig.text(0.5, 0.5, "overlapping label", fontsize=fs.FS_NOTE)
    fig.text(0.5, 0.5, "overlapping label", fontsize=fs.FS_NOTE)
    fig.text(0.99, 0.5, "runs off the page", fontsize=fs.FS_NOTE)
    ax.axvline(0.5, gid="ref_line")
    ax.text(0.5, 0.3, "crossed", ha="center")
    problems = " | ".join(fs.layout_problems(fig, line_gids=("ref_line",)))
    assert "overlap" in problems and "clipped by the page" in problems
    assert "crossed by ref_line: 'crossed'" in problems

    fig.text(0.1, 0.05, "too small", fontsize=6)
    ax.plot([0, 1], [1, 0], linewidth=0.3)
    small = fs.print_problems(fig)
    assert len(small) == 2 and "too small" in small[0] and "0.3 pt" in small[1]


def test_panel_heading_sits_on_one_baseline_above_the_axes(small_fig):
    fig, ax = small_fig
    before = len(fig.texts)
    fs.panel_heading(fig, ax, "(a)", "Title", "qualifier")
    tag, title, note = fig.texts[before:]
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    boxes = [t.get_window_extent(r) for t in (tag, title, note)]
    assert {t.get_position()[1] for t in (tag, title, note)} == {tag.get_position()[1]}
    assert boxes[0].x1 < boxes[1].x0 and boxes[1].x1 < boxes[2].x0
    assert min(b.y0 for b in boxes) > ax.get_window_extent(r).y1
    assert tag.get_fontweight() == "bold" and note.get_color() == fs.MUTED
