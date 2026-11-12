"""
Publication figure style — single source of truth
=================================================
Typography, colour palette, line weights and export settings for every
manuscript figure, extracted from the approved Figure 1
(scripts/phase4c_fig_annual_energy_uncertainty.py).

Use it from a figure script:

    from config import figure_style as fs

    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(fs.FULL_WIDTH_MM, 125))
        ...                                   # use fs.INK, fs.FS_NOTE, fs.LW_DATA ...
        fs.panel_heading(fig, ax, "(a)", "Title", "qualifier")
    assert not fs.layout_problems(fig) and not fs.print_problems(fig)
    fs.save_figure(fig, ROOT / "figures/revised", "my_figure")

or, for quick exploratory plots, load only the rcParams:

    plt.style.use("config/publication.mplstyle")

publication.mplstyle is generated from RC below; regenerate it after any change:

    python -m config.figure_style

Rules the tokens encode
-----------------------
* Sizes are in points at the printed size. Figures are drawn at their final
  width (FULL_WIDTH_MM) and never rescaled, so 7 pt stays 7 pt on paper.
  Three sizes only: heading 8.5, axis 8, note 7 (MIN_FONT_PT).
* DejaVu Sans ships inside Matplotlib, so there is no external font file.
  PDF embeds TrueType (fonttype 42); SVG keeps text as editable <text>.
* Ink is near-black and two greys; data colour is reserved for data.
* CATEGORICAL is Okabe-Ito blue, vermillion, bluish green, in that fixed
  order. All pairs pass the CVD (deutan ΔE >= 11), normal-vision and 3:1
  contrast checks on white. CATEGORICAL_EXTRA (reddish purple) is a fourth
  slot that is only ΔE 7.6 from bluish green for deuteranopes and 2.98:1 on
  white: use it only with direct labels. Never let a 5th series take a
  generated colour; fold it into "other" or use small multiples.
  Single-series figures use BLUE; one emphasised item uses VERMILLION.
* Strokes: nothing thinner than LW_MIN = 0.5 pt (0.18 mm). Reference lines are
  dashed INK; row/column guides are dotted GUIDE so that an interrupted guide
  never reads as an uncertainty bar. Uncertainty intervals use LW_DATA with
  solid_capstyle="butt", so the stroke ends exactly on the interval endpoint.
* Export: exact page size (never bbox_inches="tight"), vector PDF and SVG,
  600 dpi PNG, and no timestamps, so a rerun reproduces identical bytes.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
from cycler import cycler
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.transforms import Affine2D

MPLSTYLE = Path(__file__).with_name("publication.mplstyle")

# ---- page ------------------------------------------------------------------
MM_PER_INCH = 25.4
FULL_WIDTH_MM = 180.0                  # two-column width used by Figure 1
PNG_DPI = 600
EXPORT_FORMATS = ("pdf", "svg", "png")

# ---- typography (pt at printed size) ----------------------------------------
FONT_FAMILY = "DejaVu Sans"
FS_HEAD, FS_AXIS, FS_NOTE = 8.5, 8.0, 7.0
MIN_FONT_PT = FS_NOTE
HEAD_GAP_MM = 2.6                      # panel heading baseline above its axes

# Units: mathtext for figures, Unicode for captions and plain text.
UNIT_YIELD = r"GWh MW$^{-1}$ yr$^{-1}$"
UNIT_YIELD_PLAIN = "GWh MW⁻¹ yr⁻¹"

# ---- ink and neutral fills --------------------------------------------------
INK = "#1F2328"                        # text, reference lines, interval strokes
MUTED = "#555B63"                      # secondary text: values, qualifiers, notes
AXIS = "#8A9099"                       # axis spine and ticks
GRID = "#E3E5E8"                       # solid value grid
GUIDE = "#C9CED4"                      # dotted row/column guides
BAND = "#D9DEE5"                       # interval band fill
SURFACE = "white"

# ---- data colours (Okabe & Ito 2008) ----------------------------------------
BLUE, VERMILLION, BLUISH_GREEN, REDDISH_PURPLE = "#0072B2", "#D55E00", "#009E73", "#CC79A7"
CATEGORICAL = (BLUE, VERMILLION, BLUISH_GREEN)
CATEGORICAL_EXTRA = (REDDISH_PURPLE,)  # direct labels required, see module docstring
PRIMARY, EMPHASIS = BLUE, VERMILLION

# ---- line weights (pt) and marks --------------------------------------------
LW_MIN = 0.5                           # thinnest stroke allowed anywhere
LW_GUIDE = 0.5
LW_GRID = 0.6
LW_AXIS = 0.6
LW_DATA = 0.8                          # interval strokes, data lines
LW_REF = 0.8                           # dashed reference line (e.g. a mean)
DASH_REF = (0, (4.0, 2.6))
DOT_GUIDE = (0, (1.0, 2.0))
MS_POINT, MS_EMPHASIS, MS_SUMMARY = 5.6, 6.6, 5.0   # dot, emphasised dot, summary diamond
MEW = 0.6                              # white marker edge separating overlaps
TICK_MAJOR, TICK_MINOR, TICK_PAD = 3.0, 1.8, 2.5

# White plate behind in-plot labels that sit on a guide or grid line.
PLATE = dict(boxstyle="square,pad=0.3", facecolor=SURFACE, edgecolor="none")

RC: dict = {
    # typography
    "font.family": FONT_FAMILY,
    "font.size": FS_AXIS,
    "mathtext.fontset": "dejavusans",
    "mathtext.default": "regular",
    "axes.unicode_minus": True,
    "axes.titlesize": FS_HEAD,
    "axes.titleweight": "normal",
    "axes.titlelocation": "left",
    "axes.labelsize": FS_AXIS,
    "xtick.labelsize": FS_AXIS,
    "ytick.labelsize": FS_AXIS,
    "legend.fontsize": FS_NOTE,
    "legend.title_fontsize": FS_NOTE,
    # ink and colour
    "text.color": INK,
    "axes.labelcolor": INK,
    "axes.edgecolor": AXIS,
    "xtick.color": AXIS,
    "ytick.color": AXIS,
    "xtick.labelcolor": INK,
    "ytick.labelcolor": INK,
    "axes.prop_cycle": cycler(color=list(CATEGORICAL)),
    "figure.facecolor": SURFACE,
    "axes.facecolor": "none",
    "grid.color": GRID,
    "grid.linewidth": LW_GRID,
    "grid.linestyle": "-",
    # structure and line weights
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "axes.axisbelow": True,
    "axes.linewidth": LW_AXIS,
    "axes.labelpad": 3.5,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": TICK_MAJOR,
    "ytick.major.size": TICK_MAJOR,
    "xtick.minor.size": TICK_MINOR,
    "ytick.minor.size": TICK_MINOR,
    "xtick.major.width": LW_AXIS,
    "ytick.major.width": LW_AXIS,
    "xtick.minor.width": LW_MIN,
    "ytick.minor.width": LW_MIN,
    "xtick.major.pad": TICK_PAD,
    "ytick.major.pad": TICK_PAD,
    "lines.linewidth": LW_DATA,
    "lines.markersize": MS_POINT,
    "lines.markeredgewidth": MEW,
    "lines.solid_capstyle": "projecting",  # Matplotlib default; interval strokes pass "butt"
    "lines.dash_capstyle": "butt",
    "patch.linewidth": LW_AXIS,
    "hatch.linewidth": LW_MIN,
    "legend.frameon": False,
    "legend.handlelength": 1.6,
    # export
    "figure.dpi": 100,
    "savefig.dpi": PNG_DPI,
    "savefig.format": "pdf",
    "savefig.bbox": None,              # "standard": keep the exact page size
    "savefig.pad_inches": 0.0,
    "savefig.facecolor": SURFACE,
    "savefig.edgecolor": SURFACE,
    "savefig.transparent": False,
    "pdf.fonttype": 42,                # embedded TrueType: text stays text
    # ps.fonttype is left at its default: EPS is not an export target, and in
    # Matplotlib 3.11 setting it also regroups mathtext glyphs in the PDF.
    "svg.fonttype": "none",            # SVG text stays editable
    "svg.hashsalt": "saros-publication",   # reproducible SVG ids (save_figure uses the stem)
}


# ---- helpers ----------------------------------------------------------------
def style():
    """Context manager applying RC; wrap both figure construction and saving."""
    return matplotlib.rc_context(RC)


def figsize_mm(width_mm: float, height_mm: float) -> tuple[float, float]:
    return width_mm / MM_PER_INCH, height_mm / MM_PER_INCH


def mm_transform(fig):
    """Transform for figure coordinates in millimetres from the lower-left corner."""
    return Affine2D().scale(1 / MM_PER_INCH) + fig.dpi_scale_trans


def text_width_pt(fig, text: Text) -> float:
    return text.get_window_extent(fig.canvas.get_renderer()).width * 72 / fig.dpi


def panel_heading(fig, ax, tag: str, title: str, note: str | None = None,
                  x_mm: float = 2.0, gap_mm: float = HEAD_GAP_MM) -> None:
    """Panel heading on one baseline above `ax`: bold tag, title, muted qualifier."""
    mm = mm_transform(fig)
    y = ax.get_position().y1 * fig.get_figheight() * MM_PER_INCH + gap_mm
    renderer = fig.canvas.get_renderer()
    x = x_mm
    parts = [(tag, "bold", INK, 1.6), (title, "normal", INK, 2.6)]
    if note:
        parts.append((note, "normal", MUTED, 0.0))
    for text, weight, colour, gap in parts:
        t = fig.text(x, y, text, transform=mm, fontsize=FS_HEAD, fontweight=weight,
                     color=colour, ha="left", va="baseline")
        x = t.get_window_extent(renderer).x1 / fig.dpi * MM_PER_INCH + gap


def _drawn_texts(fig):
    """Visible, non-empty text artists, excluding labels of ticks outside the view."""
    undrawn = set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            lo, hi = sorted(axis.get_view_interval())
            for tick in (*axis.get_major_ticks(), *axis.get_minor_ticks()):
                if not lo - 1e-9 <= tick.get_loc() <= hi + 1e-9:
                    undrawn.update((id(tick.label1), id(tick.label2)))
    return [t for t in fig.findobj(Text)
            if id(t) not in undrawn and t.get_visible() and t.get_text().strip()]


def layout_problems(fig, line_gids=()) -> list[str]:
    """Text that overlaps other text, leaves the page or is crossed by a named line."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas = fig.bbox
    boxes = []
    for t in _drawn_texts(fig):
        bb = t.get_window_extent(renderer)
        if bb.width and bb.height:
            boxes.append((t.get_text().replace("\n", " "), bb))
    problems = []
    for name, bb in boxes:
        if bb.x0 < canvas.x0 or bb.y0 < canvas.y0 or bb.x1 > canvas.x1 or bb.y1 > canvas.y1:
            problems.append(f"clipped by the page: {name!r}")
    for line in fig.findobj(lambda a: a.get_gid() in line_gids):
        lb = line.get_window_extent(renderer)
        for name, bb in boxes:
            if bb.x0 - 2 < lb.x1 and bb.x1 + 2 > lb.x0 and bb.y0 < lb.y1 and bb.y1 > lb.y0:
                problems.append(f"crossed by {line.get_gid()}: {name!r}")
    for i, (na, a) in enumerate(boxes):
        for nb, b in boxes[i + 1:]:
            if min(a.x1, b.x1) - max(a.x0, b.x0) > 0.5 and min(a.y1, b.y1) - max(a.y0, b.y0) > 0.5:
                problems.append(f"overlap: {na!r} / {nb!r}")
    return problems


def print_problems(fig, min_font_pt: float = MIN_FONT_PT, min_stroke_pt: float = LW_MIN) -> list[str]:
    """Text smaller than min_font_pt or strokes thinner than min_stroke_pt at printed size."""
    problems = [f"text below {min_font_pt} pt: {t.get_text()!r} ({t.get_fontsize()} pt)"
                for t in _drawn_texts(fig) if t.get_fontsize() < min_font_pt - 1e-9]
    for ln in fig.findobj(Line2D):
        if ln.get_visible() and ln.get_linestyle() != "None" and ln.get_linewidth() < min_stroke_pt - 1e-9:
            problems.append(f"stroke below {min_stroke_pt} pt: {ln} ({ln.get_linewidth()} pt)")
    return problems


def save_figure(fig, out_dir: Path, stem: str, formats=EXPORT_FORMATS) -> dict[str, Path]:
    """Write stem.pdf/.svg/.png at the figure's exact size, without timestamps."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"pdf": {"CreationDate": None, "Title": stem},
            "svg": {"Date": None, "Title": stem},
            "png": None}
    paths = {}
    with matplotlib.rc_context({**RC, "svg.hashsalt": stem}):
        for ext in formats:
            paths[ext] = out_dir / f"{stem}.{ext}"
            fig.savefig(paths[ext], format=ext, dpi=PNG_DPI if ext == "png" else "figure",
                        metadata=meta[ext])
    return paths


def mplstyle_text() -> str:
    """RC rendered as a Matplotlib style file (hex colours without '#')."""
    def fmt(v):
        if v is None:
            return "standard"
        if isinstance(v, str):
            return v[1:] if v.startswith("#") and len(v) in (7, 9) else v
        if isinstance(v, type(cycler(color=["k"]))):
            return "cycler('color', [" + ", ".join(f"'{c[1:]}'" for c in v.by_key()["color"]) + "])"
        return str(v)

    lines = ["## Saros publication figure style. GENERATED from config/figure_style.py;",
             "## edit RC there and run `python -m config.figure_style`."]
    lines += [f"{k}: {fmt(v)}" for k, v in RC.items()]
    return "\n".join(lines) + "\n"


def write_mplstyle(path: Path = MPLSTYLE) -> Path:
    path.write_text(mplstyle_text(), encoding="utf-8")
    return path


if __name__ == "__main__":
    print("wrote", write_mplstyle())
