"""
Phase 4C — Figure: annual net energy yield and sampling uncertainty of the mean
===============================================================================
Reproduces the approved two-panel design as a publication figure.

  (a) Net annual energy yield of every calendar year: one point estimate per
      year on a dot plot. No stems, bars or whiskers are drawn, so nothing in
      this panel can be read as an interval.
  (b) Central estimate and 90 % confidence interval of the multi-year mean
      (sampling uncertainty only), on the same horizontal scale as (a).

Every plotted number is read from results/revised/ (see PHASE4B_INTEGRATION.md
section 8); nothing is hard-coded and nothing is recomputed:

  annual_energy.csv              net_gwh_per_mw_8766h        annual values
  energy_yield.json              net.gwh_per_mw              central estimate
  interannual_and_sampling.json  sampling_ci_of_11yr_mean
                                 .primary_t_interval_90      90 % sampling CI

Writes, at exactly 180 x 125 mm:

  figures/revised/annual_energy_uncertainty.pdf   vector, embedded TrueType text
  figures/revised/annual_energy_uncertainty.svg   vector, text kept as text
  figures/revised/annual_energy_uncertainty.png   600 dpi
  figures/revised/annual_energy_uncertainty_caption.md

Fonts: DejaVu Sans, which ships inside Matplotlib (no external font files).
Run from the repository root:  python scripts/phase4c_fig_annual_energy_uncertainty.py
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import ConnectionPatch, Rectangle
from matplotlib.text import Text
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
from matplotlib.transforms import Affine2D

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "annual_energy_uncertainty"

# ---- geometry (mm) ---------------------------------------------------------
W_MM, H_MM = 180.0, 125.0
LEFT_MM, RIGHT_MM = 13.0, 5.0
TOP_MM, BOTTOM_MM = 9.0, 12.5
PANEL_B_MM, GAP_MM = 20.0, 12.0
HEAD_GAP_MM = 2.6                      # panel heading baseline above its axes
XLIM = (1.8, 2.8)                      # GWh MW-1 yr-1, shared by both panels
PNG_DPI = 600

# ---- typography (pt at printed size) and ink -------------------------------
FS_HEAD, FS_AXIS, FS_NOTE = 8.5, 8.0, 7.0
INK, MUTED = "#1F2328", "#555B63"
GRID, AXIS = "#E3E5E8", "#8A9099"
GUIDE = "#C9CED4"                      # dotted row guides in (a)
BAND = "#D9DEE5"
# White plate behind in-plot labels so guide lines never strike through digits.
PLATE = dict(boxstyle="square,pad=0.3", facecolor="white", edgecolor="none")
# Okabe-Ito blue / vermillion: separable under protan, deutan and tritan vision.
C_YEAR, C_LOW = "#0072B2", "#D55E00"

UNIT = r"GWh MW$^{-1}$ yr$^{-1}$"
UNIT_PLAIN = "GWh MW⁻¹ yr⁻¹"

RC = {
    "font.family": "DejaVu Sans",
    "mathtext.fontset": "dejavusans",
    "mathtext.default": "regular",
    "font.size": FS_AXIS,
    "axes.unicode_minus": True,
    "pdf.fonttype": 42,                # embedded TrueType: text stays text
    "svg.fonttype": "none",            # SVG text stays editable
    "svg.hashsalt": STEM,              # reproducible SVG ids
    "figure.dpi": 100,
    "savefig.facecolor": "white",
}


@dataclass(frozen=True)
class FigureData:
    years: tuple[int, ...]
    values: tuple[float, ...]          # net GWh/MW per 8766 h year
    mean: float                        # central estimate
    ci_lo: float
    ci_hi: float
    low_year: int
    high_year: int
    turbine: str
    power_curve: str
    net_factor: float
    hours_per_year: float
    hub_height_m: float

    @property
    def n(self) -> int:
        return len(self.years)

    def value(self, year: int) -> float:
        return self.values[self.years.index(year)]

    @property
    def low_pct_below_mean(self) -> float:
        return (1.0 - self.value(self.low_year) / self.mean) * 100.0


def load_data(results: Path = RESULTS) -> FigureData:
    """Read the plotted numbers from results/revised and cross-check the files."""
    tab = pd.read_csv(results / "annual_energy.csv").sort_values("year")
    energy = json.loads((results / "energy_yield.json").read_text(encoding="utf-8"))
    samp = json.loads((results / "interannual_and_sampling.json").read_text(encoding="utf-8"))
    wind = json.loads((results / "wind_resource.json").read_text(encoding="utf-8"))

    years = tuple(int(y) for y in tab["year"])
    values = tuple(float(v) for v in tab["net_gwh_per_mw_8766h"])
    mean = float(energy["net"]["gwh_per_mw"])
    ci_lo, ci_hi = (float(v) for v in
                    samp["sampling_ci_of_11yr_mean"]["primary_t_interval_90"]["net_gwh_per_mw"])
    obs = samp["observed_interannual_variability"]
    low_year = years[values.index(min(values))]
    high_year = years[values.index(max(values))]

    # The three files must describe the same estimate.
    def close(a, b, rel):
        return abs(a - b) <= rel * abs(b)

    problems = []
    if list(years) != list(range(years[0], years[0] + len(years))):
        problems.append("years are not unique and consecutive")
    if not ci_lo < mean < ci_hi:
        problems.append("central estimate is outside its confidence interval")
    if not close(sum(values) / len(values), mean, 1e-3):
        problems.append("mean of annual values disagrees with the central estimate")
    if (low_year, high_year) != (int(obs["min_year"]), int(obs["max_year"])):
        problems.append("extreme years disagree between CSV and JSON")
    if not (close(min(values), obs["min_net_gwh_per_mw"], 1e-6)
            and close(max(values), obs["max_net_gwh_per_mw"], 1e-6)):
        problems.append("extreme values disagree between CSV and JSON")
    if not all(XLIM[0] < v < XLIM[1] for v in (*values, ci_lo, ci_hi)):
        problems.append(f"a plotted value falls outside the fixed axis range {XLIM}")
    if problems:
        raise ValueError("results/revised is inconsistent: " + "; ".join(problems))

    return FigureData(years, values, mean, ci_lo, ci_hi, low_year, high_year,
                      turbine=str(energy["turbine"]), power_curve=str(energy["power_curve"]),
                      net_factor=float(energy["net_factor_nominal"]),
                      hours_per_year=float(energy["hours_per_average_year"]),
                      hub_height_m=float(wind["hub_height_m"]))


def _heading(fig, mm, ax, tag, title, note):
    """Panel heading on one baseline: bold tag, title, muted qualifier."""
    y = ax.get_position().y1 * H_MM + HEAD_GAP_MM
    renderer = fig.canvas.get_renderer()
    x = 2.0
    for text, weight, colour, gap in ((tag, "bold", INK, 1.6), (title, "normal", INK, 2.6),
                                      (note, "normal", MUTED, 0.0)):
        t = fig.text(x, y, text, transform=mm, fontsize=FS_HEAD, fontweight=weight,
                     color=colour, ha="left", va="baseline")
        x = t.get_window_extent(renderer).x1 / fig.dpi * 25.4 + gap


def build_figure(d: FigureData):
    """Return the Matplotlib figure (panel axes are labelled 'panel_a' / 'panel_b')."""
    with matplotlib.rc_context(RC):
        fig = plt.figure(figsize=(W_MM / 25.4, H_MM / 25.4))
        mm = Affine2D().scale(1 / 25.4) + fig.dpi_scale_trans
        width = W_MM - LEFT_MM - RIGHT_MM
        panel_a_mm = H_MM - TOP_MM - BOTTOM_MM - PANEL_B_MM - GAP_MM
        ax_b = fig.add_axes([LEFT_MM / W_MM, BOTTOM_MM / H_MM, width / W_MM, PANEL_B_MM / H_MM],
                            label="panel_b")
        ax_a = fig.add_axes([LEFT_MM / W_MM, (BOTTOM_MM + PANEL_B_MM + GAP_MM) / H_MM,
                             width / W_MM, panel_a_mm / H_MM], label="panel_a", sharex=ax_b)

        for ax in (ax_a, ax_b):
            ax.set_facecolor("none")
            ax.set_xlim(*XLIM)
            ax.xaxis.set_major_locator(MultipleLocator(0.2))
            ax.xaxis.set_minor_locator(MultipleLocator(0.1))
            ax.grid(axis="x", which="major", color=GRID, linewidth=0.6, zorder=0)
            ax.set_axisbelow(True)
            for side in ("top", "right", "left"):
                ax.spines[side].set_visible(False)

        # ---- (a) one point estimate per calendar year ----------------------
        rows = list(range(d.n))
        ax_a.set_ylim(d.n - 0.45, -1.55)           # first year on top, one row of headroom
        ax_a.spines["bottom"].set_visible(False)
        ax_a.tick_params(axis="x", which="both", length=0, labelbottom=False)
        ax_a.tick_params(axis="y", length=0, pad=5, labelsize=FS_AXIS, labelcolor=INK)
        ax_a.set_yticks(rows, [str(y) for y in d.years])
        # Row guides: thin, pale and dotted, so a guide interrupted by a label can
        # never read as a solid whisker or interval.
        ax_a.grid(axis="y", color=GUIDE, linewidth=0.5, linestyle=(0, (1.0, 2.0)),
                  dash_capstyle="butt", zorder=0)
        i_low = d.years.index(d.low_year)
        ax_a.get_yticklabels()[i_low].set_fontweight("bold")

        others = [i for i in rows if i != i_low]
        ax_a.plot([d.values[i] for i in others], others, linestyle="none", marker="o",
                  markersize=5.6, color=C_YEAR, markeredgecolor="white", markeredgewidth=0.6,
                  zorder=3, gid="annual_points", clip_on=False)
        ax_a.plot([d.values[i_low]], [i_low], linestyle="none", marker="o", markersize=6.6,
                  color=C_LOW, markeredgecolor="white", markeredgewidth=0.6, zorder=3,
                  gid="low_year_point", clip_on=False)

        # Precise values only for the two extreme years, both to the right of the
        # point, so a row guide is never interrupted on both sides of a marker.
        renderer = fig.canvas.get_renderer()
        i_high = d.years.index(d.high_year)
        value_low = ax_a.annotate(f"{d.values[i_low]:.3f}", (d.values[i_low], i_low),
                                  xytext=(6.5, 0), textcoords="offset points", ha="left",
                                  va="center_baseline", fontsize=FS_NOTE, color=MUTED, bbox=PLATE)
        value_w = value_low.get_window_extent(renderer).width * 72 / fig.dpi
        ax_a.annotate(f"Low-wind year ({d.low_pct_below_mean:.1f}% below mean)",
                      (d.values[i_low], i_low), xytext=(6.5 + value_w + 3.5, 0),
                      textcoords="offset points", ha="left", va="center_baseline",
                      fontsize=FS_NOTE, color=INK, bbox=PLATE)
        ax_a.annotate(f"{d.values[i_high]:.3f}", (d.values[i_high], i_high), xytext=(6, 0),
                      textcoords="offset points", ha="left", va="center_baseline",
                      fontsize=FS_NOTE, color=MUTED, bbox=PLATE)
        ax_a.annotate(f"{d.n}-year mean, {d.mean:.3f}", (d.mean, -1.0), xytext=(4, 0),
                      textcoords="offset points", ha="left", va="center_baseline",
                      fontsize=FS_NOTE, color=INK)          # headroom row: nothing to mask

        # ---- (b) sampling confidence interval of the mean -------------------
        y0, half = 0.62, 0.14
        ax_b.set_ylim(0, 1)
        ax_b.set_yticks([])
        ax_b.spines["bottom"].set_color(AXIS)
        ax_b.spines["bottom"].set_linewidth(0.6)
        ax_b.tick_params(axis="x", which="major", length=3, width=0.6, color=AXIS,
                         labelsize=FS_AXIS, labelcolor=INK, pad=2.5)
        ax_b.tick_params(axis="x", which="minor", length=1.8, width=0.5, color=AXIS)
        ax_b.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        ax_b.set_xlabel(f"Estimated net annual energy yield ({UNIT})", fontsize=FS_AXIS,
                        color=INK, labelpad=3.5)

        ax_b.add_patch(Rectangle((d.ci_lo, y0 - half), d.ci_hi - d.ci_lo, 2 * half,
                                 facecolor=BAND, edgecolor="none", zorder=1))
        ax_b.plot([d.ci_lo, d.ci_hi], [y0, y0], color=INK, linewidth=0.8, zorder=2,
                  solid_capstyle="butt", gid="ci_interval")
        for x in (d.ci_lo, d.ci_hi):
            ax_b.plot([x, x], [y0 - half, y0 + half], color=INK, linewidth=0.8, zorder=2,
                      solid_capstyle="butt")
        ax_b.plot([d.mean], [y0], linestyle="none", marker="D", markersize=5.0, color=INK,
                  markeredgecolor="white", markeredgewidth=0.6, zorder=4, gid="mean_marker")
        for x, dx, ha in ((d.ci_lo, -5, "right"), (d.ci_hi, 5, "left")):
            ax_b.annotate(f"{x:.3f}", (x, y0), xytext=(dx, 0), textcoords="offset points",
                          ha=ha, va="center_baseline", fontsize=FS_AXIS, color=INK)
        ax_b.annotate(f"{d.mean:.3f}", (d.mean, y0 - half), xytext=(0, -3.5),
                      textcoords="offset points", ha="center", va="top", fontsize=FS_AXIS,
                      fontweight="bold", color=INK)
        ax_b.text(0.012, y0, f"Finite-sample uncertainty of the mean only (n = {d.n} years).\n"
                             "Not total wind-resource or project uncertainty.",
                  transform=ax_b.get_yaxis_transform(), ha="left", va="center",
                  fontsize=FS_NOTE, color=MUTED, linespacing=1.45)

        # ---- the mean, one dashed line through both panels ------------------
        fig.add_artist(ConnectionPatch(
            xyA=(d.mean, 1.0), coordsA=ax_a.get_xaxis_transform(),
            xyB=(d.mean, y0), coordsB=ax_b.transData,
            color=INK, linewidth=0.8, linestyle=(0, (4, 2.6)), zorder=2, gid="mean_line"))

        fig.canvas.draw()
        _heading(fig, mm, ax_a, "(a)", f"Annual net energy yield, {d.years[0]}–{d.years[-1]}",
                 "Point estimates, one per calendar year")
        _heading(fig, mm, ax_b, "(b)", f"Sampling uncertainty of the {d.n}-year mean",
                 "90% confidence interval")
    return fig


def layout_problems(fig) -> list[str]:
    """Text that overlaps other text, crosses the mean line or leaves the canvas."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas = fig.bbox
    undrawn = set()                    # labels of ticks outside the view are never drawn
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            lo, hi = sorted(axis.get_view_interval())
            for tick in (*axis.get_major_ticks(), *axis.get_minor_ticks()):
                if not lo - 1e-9 <= tick.get_loc() <= hi + 1e-9:
                    undrawn.update((id(tick.label1), id(tick.label2)))
    boxes = []
    for t in fig.findobj(Text):
        if id(t) in undrawn or not (t.get_visible() and t.get_text().strip()):
            continue
        bb = t.get_window_extent(renderer)
        if bb.width == 0 or bb.height == 0:
            continue
        boxes.append((t.get_text().replace("\n", " "), bb))
    problems = []
    for name, bb in boxes:
        if bb.x0 < canvas.x0 or bb.y0 < canvas.y0 or bb.x1 > canvas.x1 or bb.y1 > canvas.y1:
            problems.append(f"clipped by the page: {name!r}")
    for line in fig.findobj(lambda a: a.get_gid() == "mean_line"):
        lb = line.get_window_extent(renderer)
        for name, bb in boxes:
            if bb.x0 - 2 < lb.x1 and bb.x1 + 2 > lb.x0 and bb.y0 < lb.y1 and bb.y1 > lb.y0:
                problems.append(f"crossed by the mean line: {name!r}")
    for i, (na, a) in enumerate(boxes):
        for nb, b in boxes[i + 1:]:
            if min(a.x1, b.x1) - max(a.x0, b.x0) > 0.5 and min(a.y1, b.y1) - max(a.y0, b.y0) > 0.5:
                problems.append(f"overlap: {na!r} / {nb!r}")
    return problems


def caption(d: FigureData) -> str:
    lo, hi = d.value(d.low_year), d.value(d.high_year)
    source, *row = d.power_curve.split("_")        # e.g. OEDB_V164_9500
    return (
        f"**Figure 1.** Model-derived net annual energy yield per installed megawatt at the "
        f"Gulf of Saros site, {d.years[0]}–{d.years[-1]}. "
        f"(a) Net energy yield of each calendar year, obtained by converting hourly ERA5 "
        f"reanalysis wind speeds at {d.hub_height_m:g} m hub height with the {d.turbine} power "
        f"curve ({source} turbine-library curve {'/'.join(row)}), applying a nominal net loss "
        f"factor of {d.net_factor:g} and normalising every year to {d.hours_per_year:g} h. "
        f"Each marker is a single-year point estimate; no uncertainty interval is shown for "
        f"individual years. The dashed line marks the {d.n}-year mean "
        f"({d.mean:.3f} {UNIT_PLAIN}). The lowest year, {d.low_year} ({lo:.3f} {UNIT_PLAIN}), "
        f"lies {d.low_pct_below_mean:.1f}% below the mean; the highest, {d.high_year}, reaches "
        f"{hi:.3f} {UNIT_PLAIN}. "
        f"(b) Central estimate and 90% confidence interval of the {d.n}-year mean "
        f"({d.ci_lo:.3f}–{d.ci_hi:.3f} {UNIT_PLAIN}; Student's t-interval, n = {d.n} years) on "
        f"the same scale as (a). The interval expresses only the sampling uncertainty that "
        f"arises from the finite number of years and treats the ERA5 wind speeds as correct; "
        f"it is not a P90 value and excludes wind-resource bias, power-curve, loss and "
        f"project-design uncertainty. All values are model estimates, not observed turbine "
        f"production.\n"
    )


def main(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    d = load_data()
    fig = build_figure(d)
    problems = layout_problems(fig)
    if problems:
        raise RuntimeError("figure layout check failed: " + "; ".join(problems))
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {ext: out_dir / f"{STEM}.{ext}" for ext in ("pdf", "svg", "png")}
    with matplotlib.rc_context(RC):
        # No bbox_inches="tight": the page must stay exactly 180 x 125 mm.
        fig.savefig(paths["pdf"], metadata={"CreationDate": None, "Title": STEM})
        fig.savefig(paths["svg"], metadata={"Date": None, "Title": STEM})
        fig.savefig(paths["png"], dpi=PNG_DPI)
    plt.close(fig)
    paths["caption"] = out_dir / f"{STEM}_caption.md"
    paths["caption"].write_text(caption(d), encoding="utf-8")

    print(f"Central estimate {d.mean:.4f}; 90% sampling CI {d.ci_lo:.3f}-{d.ci_hi:.3f} GWh/MW/yr")
    print(f"Lowest {d.low_year}: {d.value(d.low_year):.3f} ({d.low_pct_below_mean:.1f}% below mean); "
          f"highest {d.high_year}: {d.value(d.high_year):.3f}")
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
