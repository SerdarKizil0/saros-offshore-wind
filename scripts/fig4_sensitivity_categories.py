"""
Figure 4: the six reported categories side by side, never combined
==================================================================
One row per category of results/revised/sensitivity_index.json, in its
order, on a common axis of relative change in net yield with respect to the
primary estimate (1994-2024, primary node, nominal losses). Each row keeps
its own kind of mark, and nothing spans rows: no envelope, no total, no sum
or root-sum-square is drawn or printed. The common axis is a scale for
comparing magnitudes, not a shared probability distribution.

  1 sampling uncertainty     the 90 % t-interval of the 31-year mean (the
                             only probabilistic interval), as a bar
  2 interannual variability  the 31 single years 1994-2024, as dots (dots that would overlap
                             are stacked vertically; only the horizontal position has meaning)
  3 period selection         the 21 rolling 11-year windows inside
                             1994-2024, as dots; 2014-2024 emphasised
  4 grid node                the two neighbouring nodes, as two squares
  5 wind product             the illustrative case in which every primary
                             hourly speed is scaled by the period-matched
                             GWA/ERA5 ratio (not adopted), as an open diamond
  6 loss assumptions         the low- and high-loss scenarios, as triangles

Sources (results/revised/): sensitivity_index.json (order, kinds,
combinable_into_one_interval = false), energy_yield.json,
interannual_and_sampling.json, annual_energy.csv, rolling_11yr_windows.csv,
node_sensitivity.json, wind_product_discrepancy.json, loss_scenarios.json.
The only computation is the relative change (value / primary - 1) x 100 for
values stored in GWh MW-1 yr-1 (sampling interval, annual values).

Run from the repository root:  python scripts/fig4_sensitivity_categories.py
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
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import figure_style as fs
from config.figure_style import (EMPHASIS, FS_AXIS, FS_NOTE, GRID, GUIDE, INK, MUTED, PRIMARY,
                                 SURFACE, UNIT_YIELD)

RESULTS = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "fig4_sensitivity_categories"

W_MM, H_MM = fs.FULL_WIDTH_MM, 104.0
LABEL_MM = 50.0                        # row-label column
LEFT_MM, RIGHT_MM, TOP_MM, BOTTOM_MM = 4.0, 4.0, 4.0, 12.0
XLIM = (-21.0, 28.0)
CATEGORIES = ("sampling_uncertainty_of_period_mean", "interannual_variability",
              "period_selection_sensitivity", "grid_node_sensitivity", "wind_product_discrepancy",
              "loss_assumption_sensitivity")
TITLES = {   # title, what is plotted, kind of quantity
    "sampling_uncertainty_of_period_mean": ("Sampling uncertainty", "90 % interval of the 31-year mean",
                                            "the only probabilistic interval"),
    "interannual_variability": ("Interannual variability", "31 single years, 1994–2024",
                                "observed spread of single years"),
    "period_selection_sensitivity": ("Reference period", "21 rolling 11-year windows",
                                     "sensitivity experiment"),
    "grid_node_sensitivity": ("Grid node", "the two neighbouring ERA5 cells",
                              "sensitivity experiment"),
    "wind_product_discrepancy": ("Wind product", "ERA5 hours scaled to GWA 4.0",
                                 "illustrative case, not adopted"),
    "loss_assumption_sensitivity": ("Loss assumptions", "low- and high-loss sets",
                                    "assumption scenarios"),
}


@dataclass(frozen=True)
class FigureData:
    primary: float
    period: str
    order: tuple[str, ...]
    kinds: dict
    sampling: tuple[float, float]              # % relative to primary
    annual: dict                               # year -> %
    windows: dict                              # "start-end" -> %
    nodes: dict                                # lon label -> %
    product_scaled: float                      # % (illustrative, not adopted)
    product_ratio: float
    gwa_period: str
    losses: dict                               # scenario -> %
    combinable: bool


def _rel(v: float, ref: float) -> float:
    return (v / ref - 1) * 100


def load_data(results: Path = RESULTS) -> FigureData:
    J = lambda n: json.loads((results / n).read_text(encoding="utf-8"))   # noqa: E731
    idx, ey, ias = J("sensitivity_index.json"), J("energy_yield.json"), J("interannual_and_sampling.json")
    ns, wp, ls = J("node_sensitivity.json"), J("wind_product_discrepancy.json"), J("loss_scenarios.json")
    primary = float(ey["net"]["gwh_per_mw"])
    ci = ias["sampling_ci_of_period_mean"]["primary_t_interval_90"]["net_gwh_per_mw"]
    ann = pd.read_csv(results / "annual_energy.csv")
    roll = pd.read_csv(results / "rolling_11yr_windows.csv")
    roll = roll[roll.within_primary_period].sort_values("start_year")
    scaled = wp["energy_sensitivity_if_primary_hours_were_scaled"]["by_ratio_era5_2008-2017_period_matched"]
    d = FigureData(
        primary=primary,
        period=ey["period"].replace("-", "–"),
        order=tuple(c["category"] for c in idx["categories"]),
        kinds={c["category"]: c for c in idx["categories"]},
        sampling=(_rel(ci[0], primary), _rel(ci[1], primary)),
        annual={int(y): _rel(v, primary) for y, v in zip(ann["year"], ann["net_gwh_per_mw_8766h"])},
        windows={f"{s}–{e}": float(r) for s, e, r in zip(roll["start_year"], roll["end_year"],
                                                         roll["rel_to_primary_mean_pct"])},
        nodes={f"{ns['nodes'][k]['lon']:.2f}° E": float(ns["nodes"][k]["energy_rel_to_primary_node_pct"])
               for k in ("W", "E")},
        product_scaled=float(scaled["aep_change_vs_primary_pct"]),
        product_ratio=float(scaled["speed_factor"]),
        gwa_period=wp["products"]["gwa4"]["period"].replace("-", "–"),
        losses={"low loss": float(ls["scenarios"]["low_loss"]["rel_to_nominal_pct"]),
                "high loss": float(ls["scenarios"]["high_loss"]["rel_to_nominal_pct"])},
        combinable=bool(idx["combinable_into_one_interval"]),
    )
    problems = verify(d, idx, ias)
    if problems:
        raise ValueError("Figure 4 data check failed: " + "; ".join(problems))
    return d


def verify(d: FigureData, idx: dict, ias: dict) -> list[str]:
    out = []
    if d.order != CATEGORIES:
        out.append(f"category order differs from sensitivity_index.json: {d.order}")
    if d.combinable:
        out.append("sensitivity_index.json says the categories are combinable")
    prob = [c for c in d.order if d.kinds[c]["is_probabilistic_interval"]]
    if prob != ["sampling_uncertainty_of_period_mean"]:
        out.append(f"probabilistic categories are {prob}, expected the sampling interval only")
    hw = ias["sampling_ci_of_period_mean"]["primary_t_interval_90"]["half_width_rel_pct"]
    if abs((d.sampling[1] - d.sampling[0]) / 2 - hw) > 1e-9:
        out.append("sampling interval half-width disagrees with interannual_and_sampling.json")
    if len(d.annual) != 31 or len(d.windows) != 21:
        out.append("expected 31 annual values and 21 windows")
    head = d.kinds["period_selection_sensitivity"]["headline"]["rolling_11yr_within_primary_period_rel_pct"]
    if abs(min(d.windows.values()) - head[0]) > 1e-9 or abs(max(d.windows.values()) - head[1]) > 1e-9:
        out.append("window range disagrees with sensitivity_index.json")
    node_head = d.kinds["grid_node_sensitivity"]["headline"]["energy_rel_to_primary_node_pct"]
    if sorted(d.nodes.values()) != sorted(node_head.values()):
        out.append("node values disagree with sensitivity_index.json")
    if d.period != "1994–2024":
        out.append(f"primary period is {d.period}")
    return out


def _minus(s: str) -> str:
    return s.replace("-", "−")


DODGE_STEP = 0.12                      # vertical step between stacked dots, in row units (> one dot)
DOT_GAP_PCT = 0.7                      # dots closer than this along x (in %; about one dot) are stacked


def dodge(values: dict, gap: float = DOT_GAP_PCT, step: float = DODGE_STEP) -> dict:
    """Vertical offsets that keep dots of one row from overlapping (a deterministic beeswarm).
    Values are never moved along x; offsets alternate above and below the row line."""
    levels = [0, 1, -1, 2, -2, 3, -3]
    placed: list[tuple[float, int]] = []
    out = {}
    for key, x in sorted(values.items(), key=lambda kv: (kv[1], str(kv[0]))):
        for lv in levels:
            if all(abs(x - px) >= gap or plv != lv for px, plv in placed):
                break
        placed.append((x, lv))
        out[key] = lv * step
    return out


def _pct(v: float) -> str:
    return _minus(f"{v:+.1f}") + " %"


def build_figure(d: FigureData):
    plot_x = LEFT_MM + LABEL_MM
    plot_w = W_MM - plot_x - RIGHT_MM
    plot_h = H_MM - TOP_MM - BOTTOM_MM
    n = len(d.order)
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(W_MM, H_MM))
        ax = fig.add_axes([plot_x / W_MM, BOTTOM_MM / H_MM, plot_w / W_MM, plot_h / H_MM],
                          label="categories")
        ax.set_xlim(*XLIM)
        ax.set_ylim(n - 0.5, -0.6)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.xaxis.set_major_locator(MultipleLocator(5))
        ax.xaxis.set_major_formatter(lambda v, _: _minus(f"{v:+.0f}") if v else "0")
        ax.grid(True, axis="x", color=GRID, linewidth=fs.LW_GRID)
        ax.set_xlabel(f"Change in net yield relative to the primary estimate ({d.period}) (%)")
        ax.axvline(0, color=INK, linewidth=fs.LW_REF, linestyle=fs.DASH_REF, zorder=2,
                   gid="primary_reference")
        for i in range(1, n):
            ax.axhline(i - 0.5, color=GUIDE, linewidth=fs.LW_GUIDE, linestyle=fs.DOT_GUIDE, zorder=1,
                       gid="row_separator")

        mm = fs.mm_transform(fig)
        for row, cat in enumerate(d.order):
            # row label in the left column, vertically centred on the row
            y_fig = ax.transData.transform((0, row))[1] / fig.dpi * fs.MM_PER_INCH
            title, what, kind = TITLES[cat]
            fig.text(LEFT_MM, y_fig + 2.6, f"{row + 1}  {title}", transform=mm, fontsize=FS_AXIS,
                     color=INK, ha="left", va="baseline")
            fig.text(LEFT_MM + 4.2, y_fig - 0.9, what, transform=mm, fontsize=FS_NOTE, color=MUTED,
                     ha="left", va="baseline")
            fig.text(LEFT_MM + 4.2, y_fig - 4.1, kind, transform=mm, fontsize=FS_NOTE, color=MUTED,
                     ha="left", va="baseline", style="italic", gid=f"kind_{cat}")

        # 1 sampling interval: the only interval, drawn as a bar with butt ends
        r = d.order.index("sampling_uncertainty_of_period_mean")
        ax.plot(list(d.sampling), [r, r], color=PRIMARY, linewidth=2.4, solid_capstyle="butt", zorder=3,
                gid="sampling_interval")
        ax.text(d.sampling[1] + 0.6, r, f"{_minus(f'{d.sampling[0]:.1f}')} to {_pct(d.sampling[1])}",
                ha="left", va="center", fontsize=FS_NOTE, color=MUTED)

        # 2 interannual: every single year
        r = d.order.index("interannual_variability")
        off = dodge(d.annual)
        ax.plot(list(d.annual.values()), [r + off[y] for y in d.annual], linestyle="none", marker="o",
                markersize=fs.MS_POINT - 1.0, color=PRIMARY, markeredgecolor=SURFACE,
                markeredgewidth=fs.MEW * 0.85, zorder=3, gid="annual_values")
        lo_y = min(d.annual, key=d.annual.get)
        hi_y = max(d.annual, key=d.annual.get)
        ax.text(d.annual[lo_y], r + 0.36, f"{lo_y}", ha="center", va="top", fontsize=FS_NOTE, color=MUTED)
        ax.text(d.annual[hi_y], r + 0.36, f"{hi_y}", ha="center", va="top", fontsize=FS_NOTE, color=MUTED)

        # 3 period selection: the 21 windows; 2014-2024 emphasised
        r = d.order.index("period_selection_sensitivity")
        last = "2014–2024"
        off = dodge(d.windows)
        others = [k for k in d.windows if k != last]
        ax.plot([d.windows[k] for k in others], [r + off[k] for k in others], linestyle="none", marker="o",
                markersize=fs.MS_POINT - 1.0, color=PRIMARY, markeredgecolor=SURFACE,
                markeredgewidth=fs.MEW * 0.85, zorder=3, gid="windows")
        ax.plot([d.windows[last]], [r + off[last]], linestyle="none", marker="o", markersize=fs.MS_POINT,
                color=EMPHASIS, markeredgecolor=SURFACE, markeredgewidth=fs.MEW, zorder=4,
                gid="window_2014_2024")
        ax.text(d.windows[last] + 0.9, r + off[last], f"{last}: {_pct(d.windows[last])}", ha="left", va="center",
                fontsize=FS_NOTE, color=INK)

        # 4 grid node: two alternatives, not joined
        r = d.order.index("grid_node_sensitivity")
        for name, v in d.nodes.items():
            ax.plot([v], [r], linestyle="none", marker="s", markersize=fs.MS_POINT - 0.4, color=PRIMARY,
                    markeredgecolor=SURFACE, markeredgewidth=fs.MEW, zorder=3, gid="node")
            ax.text(v, r + 0.3, f"{name}: {_pct(v)}", ha="center", va="top", fontsize=FS_NOTE, color=MUTED)

        # 5 wind product: illustrative scaling, open marker
        r = d.order.index("wind_product_discrepancy")
        ax.plot([d.product_scaled], [r], linestyle="none", marker="D", markersize=fs.MS_POINT - 0.6,
                markerfacecolor=SURFACE, markeredgecolor=PRIMARY, markeredgewidth=fs.LW_DATA, zorder=3,
                gid="product_scaled")
        ax.text(d.product_scaled + 0.8, r + 0.3,
                f"speeds × {d.product_ratio:.3f} ({d.gwa_period} ratio): {_pct(d.product_scaled)}",
                ha="right", va="top", fontsize=FS_NOTE, color=MUTED)

        # 6 loss scenarios
        r = d.order.index("loss_assumption_sensitivity")
        for name, v in d.losses.items():
            ax.plot([v], [r], linestyle="none", marker="^" if v > 0 else "v", markersize=fs.MS_POINT - 0.4,
                    color=PRIMARY, markeredgecolor=SURFACE, markeredgewidth=fs.MEW, zorder=3, gid="loss")
            ax.text(v, r + 0.3, f"{name}: {_pct(v)}", ha="center", va="top", fontsize=FS_NOTE, color=MUTED)

        ax.text(0.3, -0.52, f"primary estimate, {d.primary:.3f} {UNIT_YIELD}", ha="left",
                va="center", fontsize=FS_NOTE, color=INK)
    return fig


def layout_problems(fig) -> list[str]:
    return fs.layout_problems(fig, line_gids=("primary_reference",)) + fs.print_problems(fig)


def main(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    d = load_data()
    fig = build_figure(d)
    problems = layout_problems(fig)
    if problems:
        raise RuntimeError("Figure 4 layout check failed: " + "; ".join(problems))
    paths = fs.save_figure(fig, out_dir, STEM)
    plt.close(fig)
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
