"""
Phase 4C — Figure: sensitivity of the net energy yield
======================================================
Two separate experiments, on one shared horizontal scale (% change in net
energy yield relative to the central estimate), in two panels:

  (a) wind-speed scaling: every hourly hub-height speed multiplied by 0.90,
      0.95, 1.05 and 1.10, with the power curve and nominal losses fixed
      (results/revised/wind_speed_sensitivity.json);
  (b) alternative loss assumptions: the low- and high-loss scenarios
      (wake, availability, electrical) applied to the same gross energy
      (results/revised/loss_scenarios.json).

Each bar is one deterministic model run. The cases are not drawn from a
distribution, are not combined, and are neither confidence intervals nor
P50/P90 values. The illustrative GWA-scaled case in the sensitivity file is
not shown (it is discussed in the text, not part of the ±5/±10 % design).

Central estimate: results/revised/energy_yield.json (net.gwh_per_mw).
Writes figures/revised/energy_sensitivity.{pdf,svg,png} and _caption.md.
Run from the repository root:  python scripts/phase4c_fig_energy_sensitivity.py
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
from matplotlib.ticker import FuncFormatter, MultipleLocator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import figure_style as fs
from config.figure_style import (AXIS, FS_AXIS, FS_NOTE, GRID, INK, MUTED, UNIT_YIELD as UNIT,
                                 UNIT_YIELD_PLAIN as UNIT_PLAIN)

RESULTS = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "energy_sensitivity"

LEFT_MM, RIGHT_MM, TOP_MM, BOTTOM_MM = 46.0, 5.0, 12.5, 12.5
ROW_MM, GAP_MM = 7.6, 14.0             # same row height in both panels
W_MM, H_MM = fs.FULL_WIDTH_MM, TOP_MM + 6 * ROW_MM + GAP_MM + BOTTOM_MM
XLIM = (-25.0, 25.0)                   # % change; symmetric so that signs compare directly
INSIDE_PCT = 12.0                      # bars at least this long carry their value inside
SPEED_CASES = ("-10%", "-5%", "+5%", "+10%")
LOSS_CASES = ("low_loss", "high_loss")
C_SPEED = fs.PRIMARY
C_LOSS = fs.BLUISH_GREEN


def _minus(s: str) -> str:
    return s.replace("-", "−")


@dataclass(frozen=True)
class Case:
    label: str
    detail: str
    pct: float
    gwh_per_mw: float


@dataclass(frozen=True)
class SensData:
    central: float
    speed: tuple[Case, ...]
    loss: tuple[Case, ...]
    nominal_net_factor: float
    nominal_losses: dict


def load_data() -> SensData:
    ey = json.loads((RESULTS / "energy_yield.json").read_text(encoding="utf-8"))
    ws = json.loads((RESULTS / "wind_speed_sensitivity.json").read_text(encoding="utf-8"))
    ls = json.loads((RESULTS / "loss_scenarios.json").read_text(encoding="utf-8"))
    central = float(ey["net"]["gwh_per_mw"])
    by_case = {c["case"]: c for c in ws["cases"]}
    base = by_case["baseline ERA5"]
    nominal = ls["scenarios"]["nominal"]
    problems = []
    if abs(base["net_gwh_per_mw"] - central) > 1e-9 or abs(nominal["net_gwh_per_mw"] - central) > 1e-9:
        problems.append("baseline cases differ from the central estimate")
    speed = []
    for name in SPEED_CASES:
        c = by_case[name]
        pct = (c["net_gwh_per_mw"] / central - 1) * 100
        if abs(pct - c["aep_change_vs_baseline_pct"]) > 1e-6:
            problems.append(f"{name}: stored % change disagrees with the yields")
        speed.append(Case(f"Wind speed {_minus(name)}", f"all hours × {c['speed_factor']:.2f}", pct,
                          float(c["net_gwh_per_mw"])))
    loss = []
    names = {"low_loss": "Low losses", "high_loss": "High losses"}
    for key in LOSS_CASES:
        s = ls["scenarios"][key]
        pct = (s["net_gwh_per_mw"] / central - 1) * 100
        if abs(pct - s["rel_to_nominal_pct"]) > 1e-6:
            problems.append(f"{key}: stored % change disagrees with the yields")
        detail = (f"wake {s['wake'] * 100:g}%, avail. {s['availability'] * 100:g}%, "
                  f"elec. {s['electrical'] * 100:g}%")
        loss.append(Case(names[key], detail, pct, float(s["net_gwh_per_mw"])))
    if not all(XLIM[0] < c.pct < XLIM[1] for c in (*speed, *loss)):
        problems.append("a case falls outside the fixed axis range")
    if problems:
        raise ValueError("results/revised is inconsistent: " + "; ".join(problems))
    if any(abs(ey["losses_nominal"][k] - nominal[k]) > 1e-12 for k in ("wake", "availability", "electrical")):
        raise ValueError("nominal losses differ between energy_yield.json and loss_scenarios.json")
    return SensData(central, tuple(speed), tuple(loss), float(nominal["net_factor"]),
                    dict(ey["losses_nominal"]))


def _panel(fig, bottom_mm, cases, colour, label):
    n = len(cases)
    h = n * ROW_MM
    ax = fig.add_axes([LEFT_MM / W_MM, bottom_mm / H_MM, (W_MM - LEFT_MM - RIGHT_MM) / W_MM, h / H_MM],
                      label=label)
    ax.set_xlim(*XLIM)
    ax.set_ylim(n - 0.5, -0.5)
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.grid(axis="x", which="major", color=GRID, linewidth=fs.LW_GRID, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(axis="y", length=0, pad=6)
    ax.tick_params(axis="x", which="major", length=fs.TICK_MAJOR, width=fs.LW_AXIS, color=AXIS,
                   labelsize=FS_AXIS, labelcolor=INK, pad=fs.TICK_PAD)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: "0" if abs(v) < 1e-9 else _minus(f"{v:+.0f}")))
    ax.set_yticks(range(n), [""] * n)
    for i, c in enumerate(cases):
        ax.barh(i, c.pct, height=0.56, color=colour, edgecolor="none", zorder=2, gid=f"{label}_bar")
        # two-line row label: case, then its definition (muted)
        ax.annotate(c.label, (0, i), xycoords=("axes fraction", "data"), xytext=(-6, 2.2),
                    textcoords="offset points", ha="right", va="bottom", fontsize=FS_AXIS, color=INK)
        ax.annotate(c.detail, (0, i), xycoords=("axes fraction", "data"), xytext=(-6, -1.6),
                    textcoords="offset points", ha="right", va="top", fontsize=FS_NOTE, color=MUTED)
        side = 1 if c.pct >= 0 else -1
        inside = abs(c.pct) >= INSIDE_PCT          # long bars: value inside, white on the bar
        ax.annotate(f"{_minus(f'{c.pct:+.1f}')}%  ({c.gwh_per_mw:.3f})", (c.pct, i),
                    xytext=(-side * 4 if inside else side * 4, 0), textcoords="offset points",
                    ha=("right" if side > 0 else "left") if inside else ("left" if side > 0 else "right"),
                    va="center_baseline", fontsize=FS_NOTE, color=fs.SURFACE if inside else INK,
                    zorder=4)
    ax.axvline(0, color=INK, linewidth=fs.LW_REF, zorder=3, gid=f"{label}_zero")
    return ax


def build_figure(d: SensData):
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(W_MM, H_MM))
        ax_b = _panel(fig, BOTTOM_MM, d.loss, C_LOSS, "panel_b")
        ax_a = _panel(fig, BOTTOM_MM + len(d.loss) * ROW_MM + GAP_MM, d.speed, C_SPEED, "panel_a")
        ax_a.tick_params(axis="x", labelbottom=True)
        ax_b.set_xlabel("Change in net energy yield relative to the central estimate (%)", fontsize=FS_AXIS)
        # Both panels label their own zero: the central estimate
        ax_a.annotate(f"central estimate {d.central:.3f} {UNIT}", (0, -0.5),
                      xycoords="data", xytext=(4, 3), textcoords="offset points", ha="left",
                      va="bottom", fontsize=FS_NOTE, color=INK, annotation_clip=False)
        # vertical room for panel a's annotation: headroom above the first row
        fig.canvas.draw()
        fs.panel_heading(fig, ax_a, "(a)", "Wind-speed scaling",
                         "Sensitivity runs; power curve and nominal losses fixed", gap_mm=7.0)
        fs.panel_heading(fig, ax_b, "(b)", "Alternative loss assumptions",
                         f"Labelled scenarios; nominal net factor {d.nominal_net_factor:.3f}", gap_mm=4.0)
    return fig


def layout_problems(fig) -> list[str]:
    return fs.layout_problems(fig, line_gids=("panel_a_zero", "panel_b_zero")) + fs.print_problems(fig)


def caption(d: SensData) -> str:
    m10, p10 = d.speed[0], d.speed[-1]
    lo, hi = d.loss
    nl = d.nominal_losses
    return (
        f"**Figure 6.** Sensitivity of the model-derived net energy yield at the Gulf of Saros "
        f"site to two separate sets of assumptions, shown as the change relative to the central "
        f"estimate ({d.central:.3f} {UNIT_PLAIN}; values in parentheses in {UNIT_PLAIN}). "
        f"(a) Wind-speed scaling: every hourly ERA5 hub-height speed is multiplied by a constant "
        f"factor (0.90, 0.95, 1.05, 1.10) while the power curve and the nominal losses stay fixed. "
        f"The yield changes by about twice the speed change, and not symmetrically "
        f"({_minus(f'{m10.pct:+.1f}')}% for a 10% reduction, {_minus(f'{p10.pct:+.1f}')}% for a "
        f"10% increase), because most operating hours fall on the steep part of the power curve. "
        f"These are sensitivity experiments, not bias corrections or forecasts. (b) Alternative "
        f"loss assumptions: the low- and high-loss scenarios change the wake, availability and "
        f"electrical losses applied to the same gross energy ({_minus(f'{lo.pct:+.1f}')}% and "
        f"{_minus(f'{hi.pct:+.1f}')}%; nominal: wake {nl['wake'] * 100:g}%, availability "
        f"{nl['availability'] * 100:g}%, electrical {nl['electrical'] * 100:g}%). The loss values are "
        f"labelled assumptions without site-specific evidence, and one wake value is applied to "
        f"every deployment scenario. Each bar is a single deterministic model run. The two "
        f"experiments are kept apart and are not combined; neither set of cases is a probability "
        f"distribution, a confidence interval or a P50/P90 estimate.\n"
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
    print(f"central {d.central:.4f}; " + ", ".join(f"{c.label} {c.pct:+.2f}%" for c in (*d.speed, *d.loss)))
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
