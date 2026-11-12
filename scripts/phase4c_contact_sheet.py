"""
Phase 4C — contact sheet of all publication figures
===================================================
Places every current publication figure (figures/revised/<stem>.png) on one
page, in the proposed manuscript order, at true relative size (each figure at
its printed width of 180 mm and its own height), so typography, colours,
panel alignment and density can be compared side by side.

Pairs of figures share a row; each figure carries a thin frame showing its
page edge and a label with the proposed number, file stem and printed size.

The proposed numbering (FIGURES) is the inventory used in
docs/review/PHASE4C_FINAL_FIGURES.md. Captions of the two figures approved
earlier still carry their interim numbers and are not edited here.

Writes figures/revised/contact_sheet.{png,pdf}. Run after the figure scripts:
  python scripts/phase4c_contact_sheet.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import figure_style as fs

FIG_DIR = ROOT / "figures" / "revised"
STEM = "contact_sheet"
SHEET_DPI = 200                        # QA sheet; the figures themselves are 600 dpi

# Proposed manuscript order: (number, stem, generator, short title)
FIGURES = [
    (1, "saros_study_area", "phase4c_fig_saros_study_area.py", "Study area and constraints"),
    (2, "methodology", "phase4c_fig_methodology.py", "Methodology workflow"),
    (3, "wind_weibull", "phase4c_fig_wind_weibull.py", "Wind-speed distribution and Weibull fit"),
    (4, "power_curve", "phase4c_fig_power_curve.py", "Turbine power curve"),
    (5, "annual_energy_uncertainty", "phase4c_fig_annual_energy_uncertainty.py",
     "Annual yield and sampling uncertainty"),
    (6, "energy_sensitivity", "phase4c_fig_energy_sensitivity.py", "Energy sensitivity"),
    (7, "avoided_co2", "phase4c_fig_avoided_co2.py", "Avoided grid CO₂ accounting"),
]
MARGIN_MM, COL_GAP_MM, ROW_GAP_MM, LABEL_MM = 10.0, 14.0, 9.0, 7.0
FIG_W_MM = fs.FULL_WIDTH_MM


def _png_size_mm(path: Path) -> tuple[float, float]:
    import struct
    w, h = struct.unpack(">II", path.read_bytes()[16:24])
    return w / fs.PNG_DPI * 25.4, h / fs.PNG_DPI * 25.4


def layout():
    """(number, stem, title, x_mm, y_top_mm, w_mm, h_mm) for each figure, plus page size."""
    items = []
    for n, stem, _gen, title in FIGURES:
        w, h = _png_size_mm(FIG_DIR / f"{stem}.png")
        items.append((n, stem, title, w, h))
    rows = [items[i:i + 2] for i in range(0, len(items), 2)]
    page_w = 2 * MARGIN_MM + 2 * FIG_W_MM + COL_GAP_MM
    placed, y = [], MARGIN_MM
    for row in rows:
        row_h = max(h for *_, h in row)
        for j, (n, stem, title, w, h) in enumerate(row):
            x = MARGIN_MM + j * (FIG_W_MM + COL_GAP_MM)
            placed.append((n, stem, title, x, y + LABEL_MM, w, h))
        y += LABEL_MM + row_h + ROW_GAP_MM
    page_h = y - ROW_GAP_MM + MARGIN_MM
    return placed, page_w, page_h


def build_sheet():
    placed, pw, ph = layout()
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(pw, ph), dpi=SHEET_DPI)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, pw)
        ax.set_ylim(ph, 0)                 # y downwards in mm
        ax.set_axis_off()
        for n, stem, title, x, y, w, h in placed:
            img = imread(FIG_DIR / f"{stem}.png")
            # downsample 600 -> SHEET_DPI by striding (deterministic, no resampling library)
            step = max(1, int(round(fs.PNG_DPI / SHEET_DPI)))
            ax.imshow(img[::step, ::step], extent=(x, x + w, y + h, y), interpolation="antialiased",
                      zorder=1)
            ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor=fs.GUIDE,
                                   linewidth=fs.LW_GUIDE, zorder=2))
            ax.text(x, y - 2.2, f"Figure {n}", fontsize=fs.FS_HEAD, fontweight="bold", color=fs.INK,
                    ha="left", va="baseline")
            ax.text(x + 17.5, y - 2.2, f"{title}   ·   {stem}   ·   {w:.0f} × {h:.0f} mm",
                    fontsize=fs.FS_HEAD, color=fs.MUTED, ha="left", va="baseline")
    return fig


def main(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    missing = [s for _, s, _, _ in FIGURES if not (FIG_DIR / f"{s}.png").exists()]
    if missing:
        raise FileNotFoundError("run the figure scripts first; missing: " + ", ".join(missing))
    fig = build_sheet()
    out_dir = Path(out_dir)
    paths = {}
    with matplotlib.rc_context({**fs.RC, "svg.hashsalt": STEM}):
        for ext, meta in (("png", None), ("pdf", {"CreationDate": None, "Title": STEM})):
            paths[ext] = out_dir / f"{STEM}.{ext}"
            fig.savefig(paths[ext], format=ext, dpi=SHEET_DPI, metadata=meta)
    plt.close(fig)
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    main()
