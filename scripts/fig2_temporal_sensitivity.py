"""
Figure 2: annual net energy yield 1994-2024 and rolling 11-year windows
=======================================================================
Two panels on one calendar-year axis.

  (a) Net energy yield of every calendar year 1994-2024 at the primary ERA5
      node, with the 1994-2024 mean (the primary estimate). One point per
      year; nothing in this panel is an interval. The years of the
      2014-2024 comparison period are shaded.
  (b) Mean net yield of every 11-year window of the 1979-2024 record,
      relative to the primary estimate and plotted at the final year of the
      window. Windows inside 1994-2024 are filled; windows that start before
      1994 are open. The 2014-2024 window is emphasised. Overlapping windows
      share years; they are not independent samples and the spread of the
      dots is not an interval.

Every plotted number is read from results/revised/; nothing is recomputed
except the relative change of the annual values, (year / mean - 1) x 100,
which is the definition used in the manuscript text.

  annual_energy.csv            year, net_gwh_per_mw_8766h
  energy_yield.json            net.gwh_per_mw (primary estimate), period
  rolling_11yr_windows.csv     start_year, end_year, net_gwh_per_mw,
                               rel_to_primary_mean_pct, within_primary_period
  period_sensitivity.json      rolling_windows summary (cross-check)

Run from the repository root:  python scripts/fig2_temporal_sensitivity.py
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
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FormatStrFormatter, MultipleLocator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import figure_style as fs
from config.figure_style import (AXIS, BAND, EMPHASIS, FS_NOTE, GRID, INK, MUTED, PLATE,
                                 PRIMARY, SURFACE, UNIT_YIELD)

RESULTS = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "fig2_temporal_sensitivity"

W_MM, H_MM = fs.FULL_WIDTH_MM, 120.0
LEFT_MM, RIGHT_MM, TOP_MM, BOTTOM_MM = 15.0, 4.0, 8.0, 11.0
GAP_MM = 17.0
PANEL_A_MM = 52.0
XLIM = (1987.8, 2025.2)
YLIM_A = (1.85, 2.75)
YLIM_B = (-4.5, 5.5)
COMPARISON = (2014, 2024)


@dataclass(frozen=True)
class FigureData:
    years: tuple[int, ...]
    values: tuple[float, ...]                 # net GWh MW-1 per 8766 h year
    mean: float                               # primary estimate (1994-2024)
    period: str
    win_start: tuple[int, ...]
    win_end: tuple[int, ...]
    win_rel_pct: tuple[float, ...]            # relative to the primary estimate
    win_inside: tuple[bool, ...]              # inside 1994-2024

    def rel_pct(self, year: int) -> float:
        return (self.values[self.years.index(year)] / self.mean - 1) * 100

    @property
    def lowest_year(self) -> int:
        return self.years[self.values.index(min(self.values))]

    @property
    def highest_year(self) -> int:
        return self.years[self.values.index(max(self.values))]

    def window(self, start: int) -> int:
        return self.win_start.index(start)


def load_data(results: Path = RESULTS) -> FigureData:
    ann = pd.read_csv(results / "annual_energy.csv")
    ey = json.loads((results / "energy_yield.json").read_text(encoding="utf-8"))
    ps = json.loads((results / "period_sensitivity.json").read_text(encoding="utf-8"))
    roll = pd.read_csv(results / "rolling_11yr_windows.csv").sort_values("start_year")
    d = FigureData(
        years=tuple(int(v) for v in ann["year"]),
        values=tuple(float(v) for v in ann["net_gwh_per_mw_8766h"]),
        mean=float(ey["net"]["gwh_per_mw"]),
        period=f"{int(ann['year'].min())}–{int(ann['year'].max())}",
        win_start=tuple(int(v) for v in roll["start_year"]),
        win_end=tuple(int(v) for v in roll["end_year"]),
        win_rel_pct=tuple(float(v) for v in roll["rel_to_primary_mean_pct"]),
        win_inside=tuple(bool(v) for v in roll["within_primary_period"]),
    )
    problems = verify(d, ey, ps)
    if problems:
        raise ValueError("Figure 2 data check failed: " + "; ".join(problems))
    return d


def verify(d: FigureData, ey: dict, ps: dict) -> list[str]:
    out = []
    if d.years != tuple(range(1994, 2025)):
        out.append(f"annual series is not 1994-2024: {d.years[0]}-{d.years[-1]}")
    if ey["period"] != d.period.replace("–", "-"):
        out.append(f"energy_yield.json period {ey['period']} is not the plotted {d.period}")
    summary = ps["rolling_windows"]
    if len(d.win_start) != summary["all_windows"]["n_windows"]:
        out.append("number of windows disagrees with period_sensitivity.json")
    if sum(d.win_inside) != summary["within_primary_period"]["n_windows"]:
        out.append("number of windows inside 1994-2024 disagrees with period_sensitivity.json")
    if any(e - s != 10 for s, e in zip(d.win_start, d.win_end)):
        out.append("a window is not 11 years long")
    top = d.win_rel_pct.index(max(d.win_rel_pct))
    if f"{d.win_start[top]}-{d.win_end[top]}" != summary["all_windows"]["highest_window"]:
        out.append("highest window disagrees with period_sensitivity.json")
    if abs(max(d.win_rel_pct) - summary["all_windows"]["highest_window_rel_to_primary_mean_pct"]) > 1e-9:
        out.append("highest window value disagrees with period_sensitivity.json")
    return out


def _minus(s: str) -> str:
    return s.replace("-", "−")


def build_figure(d: FigureData):
    plot_w = W_MM - LEFT_MM - RIGHT_MM
    panel_b = H_MM - TOP_MM - BOTTOM_MM - GAP_MM - PANEL_A_MM
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(W_MM, H_MM))
        ax_b = fig.add_axes([LEFT_MM / W_MM, BOTTOM_MM / H_MM, plot_w / W_MM, panel_b / H_MM],
                            label="panel_b")
        ax_a = fig.add_axes([LEFT_MM / W_MM, (BOTTOM_MM + panel_b + GAP_MM) / H_MM, plot_w / W_MM,
                             PANEL_A_MM / H_MM], label="panel_a")
        for ax in (ax_a, ax_b):
            ax.set_xlim(*XLIM)
            ax.xaxis.set_major_locator(MultipleLocator(5))
            ax.xaxis.set_minor_locator(MultipleLocator(1))
            ax.grid(True, axis="y", color=GRID, linewidth=fs.LW_GRID)

        # ---- (a) annual values -------------------------------------------------
        ax_a.set_ylim(*YLIM_A)
        ax_a.yaxis.set_major_locator(MultipleLocator(0.2))
        ax_a.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        ax_a.axvspan(COMPARISON[0] - 0.5, COMPARISON[1] + 0.5, facecolor=BAND, edgecolor="none",
                     zorder=0, gid="comparison_period")
        ax_a.axhline(d.mean, color=INK, linewidth=fs.LW_REF, linestyle=fs.DASH_REF, zorder=2,
                     gid="primary_mean")
        ax_a.plot(d.years, d.values, linestyle="none", marker="o", markersize=fs.MS_POINT,
                  color=PRIMARY, markeredgecolor=SURFACE, markeredgewidth=fs.MEW, zorder=3,
                  gid="annual_values")
        ax_a.set_ylabel(f"Net yield ({UNIT_YIELD})")
        ax_a.text(XLIM[0] + 0.4, d.mean + 0.03, f"{d.period} mean\n{d.mean:.3f}", ha="left",
                  va="bottom", fontsize=FS_NOTE, color=INK, linespacing=1.15)
        ax_a.text((COMPARISON[0] + COMPARISON[1]) / 2, YLIM_A[1] - 0.03,
                  f"{COMPARISON[0]}–{COMPARISON[1]} comparison period", ha="center", va="top",
                  fontsize=FS_NOTE, color=MUTED)
        second = sorted(zip(d.values, d.years))[1][1]
        for yr, dx, ha in ((d.lowest_year, 6, "left"), (d.highest_year, -6, "right"), (second, -6, "right")):
            ax_a.annotate(f"{yr}  {_minus(f'{d.rel_pct(yr):+.1f}')} %", (yr, d.values[d.years.index(yr)]),
                          xytext=(dx, 0), textcoords="offset points", ha=ha, va="center",
                          fontsize=FS_NOTE, color=MUTED, gid=f"label_{yr}")
        ax_a.set_xticks(list(range(1990, 2026, 5)))
        ax_a.tick_params(axis="x", labelbottom=True)

        # ---- (b) rolling 11-year windows -----------------------------------------
        ax_b.set_ylim(*YLIM_B)
        ax_b.yaxis.set_major_locator(MultipleLocator(2))
        ax_b.yaxis.set_major_formatter(lambda v, _: _minus(f"{v:+.0f}") if v else "0")
        ax_b.axhline(0, color=INK, linewidth=fs.LW_REF, linestyle=fs.DASH_REF, zorder=2,
                     gid="primary_reference")
        inside = [i for i, f in enumerate(d.win_inside) if f]
        before = [i for i, f in enumerate(d.win_inside) if not f]
        ax_b.plot([d.win_end[i] for i in before], [d.win_rel_pct[i] for i in before],
                  linestyle="none", marker="o", markersize=fs.MS_POINT - 0.6, markerfacecolor=SURFACE,
                  markeredgecolor=PRIMARY, markeredgewidth=fs.LW_DATA, zorder=3,
                  gid="windows_before_1994")
        rest = [i for i in inside if d.win_start[i] != COMPARISON[0]]
        ax_b.plot([d.win_end[i] for i in rest], [d.win_rel_pct[i] for i in rest],
                  linestyle="none", marker="o", markersize=fs.MS_POINT, color=PRIMARY,
                  markeredgecolor=SURFACE, markeredgewidth=fs.MEW, zorder=3, gid="windows_inside")
        k = d.window(COMPARISON[0])
        ax_b.plot([d.win_end[k]], [d.win_rel_pct[k]], linestyle="none", marker="o",
                  markersize=fs.MS_EMPHASIS, color=EMPHASIS, markeredgecolor=SURFACE,
                  markeredgewidth=fs.MEW, zorder=4, gid="window_2014_2024")
        ax_b.annotate(f"window {COMPARISON[0]}–{COMPARISON[1]}: {_minus(f'{d.win_rel_pct[k]:+.1f}')} %",
                      (d.win_end[k], d.win_rel_pct[k]), xytext=(d.win_end[k] - 3.2, 4.4),
                      textcoords="data", ha="right", va="center", fontsize=FS_NOTE, color=INK,
                      arrowprops=dict(arrowstyle="-", color=INK, linewidth=fs.LW_GUIDE,
                                      shrinkA=1.5, shrinkB=3.5), gid="label_2014_2024")
        lo = d.win_rel_pct.index(min(d.win_rel_pct))
        ax_b.annotate(f"{d.win_start[lo]}–{d.win_end[lo]}\n{_minus(f'{d.win_rel_pct[lo]:+.1f}')} %",
                      (d.win_end[lo], d.win_rel_pct[lo]), xytext=(6, 0), textcoords="offset points",
                      ha="left", va="center", fontsize=FS_NOTE, color=MUTED, linespacing=1.15)
        ax_b.text(XLIM[0] + 0.4, 0.25, f"{d.period} estimate", ha="left", va="bottom",
                  fontsize=FS_NOTE, color=INK)
        ax_b.set_ylabel("Change (%)")
        ax_b.set_xlabel("Year; in (b), final year of the 11-year window")
        ax_b.set_xticks(list(range(1990, 2026, 5)))

        handles = [Line2D([], [], linestyle="none", marker="o", markersize=fs.MS_POINT, color=PRIMARY,
                          markeredgecolor=SURFACE, markeredgewidth=fs.MEW),
                   Line2D([], [], linestyle="none", marker="o", markersize=fs.MS_POINT - 0.6,
                          markerfacecolor=SURFACE, markeredgecolor=PRIMARY,
                          markeredgewidth=fs.LW_DATA)]
        ax_b.legend(handles, [f"window inside {d.period}", "window starting before 1994"],
                    loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=FS_NOTE,
                    handletextpad=0.3, borderaxespad=0.3, labelspacing=0.35)

        fs.panel_heading(fig, ax_a, "(a)", f"Annual net yield, {d.period}",
                         "single calendar years at the primary ERA5 node")
        fs.panel_heading(fig, ax_b, "(b)", "Rolling 11-year windows, 1979–2024",
                         f"mean of each window relative to the {d.period} estimate")
    return fig


def layout_problems(fig) -> list[str]:
    return fs.layout_problems(fig) + fs.print_problems(fig)


def main(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    d = load_data()
    fig = build_figure(d)
    problems = layout_problems(fig)
    if problems:
        raise RuntimeError("Figure 2 layout check failed: " + "; ".join(problems))
    paths = fs.save_figure(fig, out_dir, STEM)
    plt.close(fig)
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
