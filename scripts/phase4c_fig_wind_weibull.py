"""
Phase 4C — Figure: hub-height wind-speed distribution and Weibull fit
=====================================================================
  (a) Empirical distribution of every hourly hub-height wind speed (ERA5,
      2014-2024, 105 m), as a probability-density histogram with 0.5 m/s bins,
      and the fitted Weibull density (maximum likelihood, location fixed at 0).
  (b) Empirical density minus Weibull density in each bin: where the
      two-parameter approximation over- or under-states the observed hours.

The Weibull fit is descriptive only. The primary energy estimate converts each
hourly speed through the power curve (scripts/04_fit_weibull_aep.py); the
Weibull-integrated capacity factor is a cross-check (weibull_crosscheck.json).

Inputs (no value is typed in):
  data/processed/wind_hub_105m.parquet        U_hub, every hour, as committed
  results/revised/weibull_crosscheck.json     k, c, fit statistics, Weibull CF
  results/revised/wind_resource.json          empirical mean, hub height
  results/revised/energy_yield.json           empirical gross CF
  config/turbine.py                           cut-in, rated, cut-out speeds

Writes figures/revised/wind_weibull.{pdf,svg,png} and _caption.md (180 mm).
Run from the repository root:  python scripts/phase4c_fig_wind_weibull.py
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import figure_style as fs
from config.figure_style import (AXIS, FS_AXIS, FS_NOTE, GRID, GUIDE, INK, MUTED,
                                 PLATE)
from config.turbine import TURBINE

SERIES = ROOT / "data" / "processed" / "wind_hub_105m.parquet"
RESULTS = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "wind_weibull"

W_MM, H_MM = fs.FULL_WIDTH_MM, 112.0
LEFT_MM, RIGHT_MM, TOP_MM, BOTTOM_MM = 17.0, 5.0, 9.0, 12.5
PANEL_B_MM, GAP_MM = 24.0, 12.0
BIN_MS = 0.5                           # ERA5 speeds are continuous; 0.5 m/s resolves the mode
XMAX = 26.0                            # last bin edge above the maximum hourly speed (25.5 m/s)
C_EMP = fs.PRIMARY
C_FIT = fs.EMPHASIS
UNIT_SPEED = r"m s$^{-1}$"
UNIT_DENS = r"s m$^{-1}$"


def _tint(colour, t):
    from matplotlib.colors import to_hex, to_rgb
    a, b = np.array(to_rgb(colour)), np.array(to_rgb(fs.SURFACE))
    return to_hex(t * a + (1 - t) * b)


C_BAR = _tint(C_EMP, 0.32)


def _signed(v: float, nd: int = 1) -> str:
    """Signed number with a typographic minus."""
    return f"{v:+.{nd}f}".replace("-", "−")


@dataclass(frozen=True)
class WindData:
    u: np.ndarray                       # hourly hub-height speed, m/s
    edges: np.ndarray
    density: np.ndarray                 # empirical probability density per bin, s/m
    k: float
    c: float
    mean_emp: float
    mean_weibull: float
    ks: float
    r2_cdf: float
    gross_cf_emp: float
    gross_cf_weibull: float
    cf_rel_diff_pct: float
    hub_height_m: float
    period: str

    @property
    def centres(self) -> np.ndarray:
        return 0.5 * (self.edges[:-1] + self.edges[1:])

    @property
    def weibull_bin_density(self) -> np.ndarray:
        """Weibull probability of each bin divided by its width (comparable with the histogram)."""
        cdf = stats.weibull_min.cdf(self.edges, self.k, 0, self.c)
        return np.diff(cdf) / np.diff(self.edges)

    def weibull_pdf(self, x):
        return stats.weibull_min.pdf(x, self.k, 0, self.c)


def load_data() -> WindData:
    df = pd.read_parquet(SERIES)
    u = df["U_hub"].to_numpy(dtype=float)
    if np.isnan(u).any():
        raise ValueError("hourly series contains missing values; none are filled here")
    w = json.loads((RESULTS / "weibull_crosscheck.json").read_text(encoding="utf-8"))
    res = json.loads((RESULTS / "wind_resource.json").read_text(encoding="utf-8"))
    ey = json.loads((RESULTS / "energy_yield.json").read_text(encoding="utf-8"))
    fit = w["weibull_fit_U_hub"]
    if fit["n_hours"] != len(u) or res["data"]["n_hours"] != len(u):
        raise ValueError("series length disagrees with results/revised")
    if abs(w["gross_cf_empirical"] - ey["gross_cf"]) > 1e-12:
        raise ValueError("weibull_crosscheck.json and energy_yield.json disagree on the gross CF")
    if abs(u.mean() - res["U_hub"]["mean_ms"]) > 1e-6:
        raise ValueError("series mean disagrees with wind_resource.json")
    if u.max() >= XMAX or u.min() < 0:
        raise ValueError("speeds fall outside the histogram range")
    edges = np.arange(0.0, XMAX + BIN_MS / 2, BIN_MS)
    density, _ = np.histogram(u, bins=edges, density=True)
    return WindData(u, edges, density, float(fit["k_mle"]), float(fit["c_mle_ms"]),
                    float(res["U_hub"]["mean_ms"]), float(fit["weibull_mean_ms"]),
                    float(fit["ks_statistic"]), float(fit["r2_cdf"]),
                    float(w["gross_cf_empirical"]), float(w["gross_cf_weibull"]),
                    float(w["relative_difference_pct"]), float(res["hub_height_m"]),
                    str(res["data"]["period"]))


def build_figure(d: WindData):
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(W_MM, H_MM))
        width = W_MM - LEFT_MM - RIGHT_MM
        panel_a = H_MM - TOP_MM - BOTTOM_MM - PANEL_B_MM - GAP_MM
        ax_b = fig.add_axes([LEFT_MM / W_MM, BOTTOM_MM / H_MM, width / W_MM, PANEL_B_MM / H_MM],
                            label="panel_b")
        ax_a = fig.add_axes([LEFT_MM / W_MM, (BOTTOM_MM + PANEL_B_MM + GAP_MM) / H_MM,
                             width / W_MM, panel_a / H_MM], label="panel_a", sharex=ax_b)
        for ax in (ax_a, ax_b):
            ax.set_xlim(0, XMAX)
            ax.xaxis.set_major_locator(MultipleLocator(2))
            ax.xaxis.set_minor_locator(MultipleLocator(BIN_MS * 2))
            ax.grid(axis="y", color=GRID, linewidth=fs.LW_GRID, zorder=0)
            ax.set_axisbelow(True)
            ax.tick_params(axis="both", which="major", length=fs.TICK_MAJOR, width=fs.LW_AXIS,
                           color=AXIS, labelsize=FS_AXIS, labelcolor=INK, pad=fs.TICK_PAD)
            ax.tick_params(axis="both", which="minor", length=fs.TICK_MINOR, width=fs.LW_MIN, color=AXIS)
            ax.spines["left"].set_color(AXIS)
            ax.spines["bottom"].set_color(AXIS)

        # ---- (a) histogram and fitted density --------------------------------
        ax_a.bar(d.edges[:-1], d.density, width=BIN_MS, align="edge", color=C_BAR,
                 edgecolor=fs.SURFACE, linewidth=0.3, zorder=1, gid="empirical_histogram")
        x = np.linspace(0, XMAX, 1041)
        ax_a.plot(x, d.weibull_pdf(x), color=C_FIT, linewidth=fs.LW_DATA + 0.3, zorder=3,
                  gid="weibull_pdf")
        ymax = 0.13
        ax_a.set_ylim(0, ymax)
        ax_a.yaxis.set_major_locator(MultipleLocator(0.02))
        ax_a.tick_params(axis="x", which="both", labelbottom=False)
        ax_a.set_ylabel(f"Probability density ({UNIT_DENS})", fontsize=FS_AXIS)
        for v, name in ((TURBINE.cut_in_ms, "cut-in"), (TURBINE.rated_ms, "rated"),
                        (TURBINE.cut_out_ms, "cut-out")):
            for ax in (ax_a, ax_b):
                ax.axvline(v, color=GUIDE, linewidth=fs.LW_GUIDE, linestyle=fs.DOT_GUIDE,
                           dash_capstyle="butt", zorder=0.5, gid=f"guide_{name.replace('-', '')}")
            ax_a.text(v, ymax * 0.985, f"{name} {v:g}", ha="center", va="top", fontsize=FS_NOTE,
                      color=MUTED, bbox=PLATE, zorder=4)

        leg = ax_a.legend(
            [Patch(facecolor=C_BAR, edgecolor="none"), Line2D([], [], color=C_FIT, linewidth=fs.LW_DATA + 0.3)],
            [f"Hourly ERA5 speeds at {d.hub_height_m:g} m (n = {len(d.u):,} h), {BIN_MS:g} {UNIT_SPEED} bins",
             f"Weibull fit (MLE): k = {d.k:.2f}, c = {d.c:.2f} {UNIT_SPEED}"],
            loc="upper right", bbox_to_anchor=(1.0, 0.86), frameon=False, fontsize=FS_NOTE,
            handlelength=1.8, borderaxespad=0.2)
        leg.set_zorder(5)
        ax_a.text(0.995, 0.50,
                  f"Mean speed: hourly {d.mean_emp:.2f}, Weibull {d.mean_weibull:.2f} {UNIT_SPEED}\n"
                  f"Gross capacity factor: hourly conversion {d.gross_cf_emp * 100:.1f}%,\n"
                  f"Weibull integration {d.gross_cf_weibull * 100:.1f}% ({_signed(d.cf_rel_diff_pct)}%)",
                  transform=ax_a.transAxes, ha="right", va="top", fontsize=FS_NOTE, color=MUTED,
                  linespacing=1.45)

        # ---- (b) difference ---------------------------------------------------
        diff = d.density - d.weibull_bin_density
        lim = 0.02
        if np.abs(diff).max() >= lim:
            raise ValueError("difference panel range too small for the data")
        ax_b.bar(d.edges[:-1], diff, width=BIN_MS, align="edge", color=C_EMP, edgecolor=fs.SURFACE,
                 linewidth=0.3, zorder=2, gid="difference_bars")
        ax_b.axhline(0, color=INK, linewidth=fs.LW_AXIS, zorder=3)
        ax_b.set_ylim(-lim, lim)
        ax_b.yaxis.set_major_locator(MultipleLocator(0.01))
        ax_b.yaxis.set_minor_locator(MultipleLocator(0.005))
        ax_b.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: "0" if abs(v) < 1e-12 else f"{v:+.2f}".replace("-", "−")))
        ax_b.set_ylabel(f"Δ ({UNIT_DENS})", fontsize=FS_AXIS)
        ax_b.set_xlabel(f"Hourly wind speed at {d.hub_height_m:g} m hub height ({UNIT_SPEED})",
                        fontsize=FS_AXIS)
        ax_b.text(0.995, 0.93, "above zero: more hours than the Weibull fit", transform=ax_b.transAxes,
                  ha="right", va="top", fontsize=FS_NOTE, color=MUTED)
        ax_b.text(0.995, 0.07, "below zero: fewer hours than the Weibull fit", transform=ax_b.transAxes,
                  ha="right", va="bottom", fontsize=FS_NOTE, color=MUTED)
        fig.align_ylabels([ax_a, ax_b])

        fig.canvas.draw()
        fs.panel_heading(fig, ax_a, "(a)", "Hub-height wind-speed distribution",
                         f"Hourly ERA5, {d.period[:4]}–{d.period[-14:-10]}, with fitted Weibull density")
        fs.panel_heading(fig, ax_b, "(b)", "Δ = empirical minus Weibull density", "per bin")
    return fig


def layout_problems(fig) -> list[str]:
    return fs.layout_problems(fig) + fs.print_problems(fig)


def caption(d: WindData) -> str:
    y0, y1 = d.period[:4], d.period[-14:-10]
    return (
        f"**Figure 3.** Distribution of hourly hub-height wind speed at the ERA5 grid node used "
        f"for the Gulf of Saros site, {y0}–{y1}. (a) Probability-density histogram of all "
        f"{len(d.u):,} hourly speeds at {d.hub_height_m:g} m ({BIN_MS:g} m s⁻¹ bins; bar areas sum "
        f"to one) and the two-parameter Weibull density fitted by maximum likelihood with the "
        f"location fixed at zero (k = {d.k:.3f}, c = {d.c:.3f} m s⁻¹). Every hour of the committed "
        f"series is used; no values are filled or interpolated. Dotted lines mark the cut-in "
        f"({TURBINE.cut_in_ms:g} m s⁻¹), rated ({TURBINE.rated_ms:g} m s⁻¹) and cut-out "
        f"({TURBINE.cut_out_ms:g} m s⁻¹) speeds of the reference turbine. (b) Empirical density "
        f"minus the Weibull probability of the same bin divided by the bin width. The fit "
        f"reproduces the mean speed ({d.mean_emp:.2f} versus {d.mean_weibull:.2f} m s⁻¹) and the "
        f"cumulative distribution closely (R² = {d.r2_cdf:.3f}; Kolmogorov–Smirnov D = "
        f"{d.ks:.3f}; because hourly speeds are autocorrelated, no p-value is interpreted). "
        f"Close agreement in distribution does not establish agreement in energy: the "
        f"deviations in (b) fall partly in the steep part of the power curve, and the "
        f"Weibull-integrated gross capacity factor ({d.gross_cf_weibull * 100:.2f}%) differs by "
        f"{_signed(d.cf_rel_diff_pct)}% from the direct hourly conversion "
        f"({d.gross_cf_emp * 100:.2f}%). The Weibull fit is therefore reported as a descriptive "
        f"summary and cross-check only; the energy estimates in this study convert each hourly "
        f"speed through the power curve. ERA5 is reanalysis model output, not measured wind.\n"
    )


def main(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    d = load_data()
    fig = build_figure(d)
    problems = layout_problems(fig)
    if problems:
        raise RuntimeError("figure layout check failed: " + "; ".join(problems))
    paths = fs.save_figure(fig, out_dir, STEM)
    plt.close(fig)
    paths["caption"] = Path(out_dir) / f"{STEM}_caption.md"
    paths["caption"].write_text(caption(d), encoding="utf-8")
    print(f"Weibull k {d.k:.4f}, c {d.c:.4f}; CF hourly {d.gross_cf_emp:.4f} vs Weibull {d.gross_cf_weibull:.4f}")
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
