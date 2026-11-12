"""
Phase 4C — Figure: turbine power curve used by the production model
===================================================================
One panel: electrical power of the Vestas V164-9.5 MW reference turbine
against hub-height wind speed.

  * markers: every point of the active OEDB "V164/9500" digitised curve
    (config.turbine.POWER_CURVE_OEDB_V164_9500_MS_KW, 0-24.5 m/s);
  * open markers: the three boundary points added in config (rated plateau
    to 25 m/s and the cut-out drop), which are not OEDB data;
  * solid line: the production interpolation itself, evaluated with
    power_from_speed() from scripts/04_fit_weibull_aep.py (linear between
    points, zero below cut-in and at or above cut-out);
  * dashed grey line: the retired, undocumented curve used before Phase 2A,
    marked as superseded.

Writes figures/revised/power_curve.{pdf,svg,png} and _caption.md (180 mm).
Run from the repository root:  python scripts/phase4c_fig_power_curve.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import figure_style as fs
from config.figure_style import AXIS, FS_AXIS, FS_NOTE, GRID, GUIDE, INK, MUTED, PLATE
from config import turbine as tcfg

RESULTS = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "power_curve"
ENERGY_SCRIPT = ROOT / "scripts" / "04_fit_weibull_aep.py"

W_MM, H_MM = fs.FULL_WIDTH_MM, 92.0
LEFT_MM, RIGHT_MM, TOP_MM, BOTTOM_MM = 17.0, 5.0, 9.0, 12.5
OEDB_LAST_MS = 24.5                     # last OEDB row; the points after it are boundary points
C_CURVE = fs.PRIMARY
C_RETIRED = MUTED
UNIT_SPEED = r"m s$^{-1}$"


def _energy_module():
    spec = importlib.util.spec_from_file_location("energy04", ENERGY_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@dataclass(frozen=True)
class CurveData:
    oedb: np.ndarray                    # (n, 2) m/s, MW
    boundary: np.ndarray
    retired: np.ndarray
    u_line: np.ndarray                  # dense speeds for the production line
    p_line: np.ndarray                  # MW from power_from_speed()
    cut_in: float
    rated_speed: float
    cut_out: float
    rated_mw: float
    curve_id: str
    turbine: str
    rho_note: str


def load_data() -> CurveData:
    if tcfg.POWER_CURVE_ID != "OEDB_V164_9500" or tcfg.POWER_CURVE_MS_KW is not tcfg.POWER_CURVE_OEDB_V164_9500_MS_KW:
        raise ValueError("production curve is not the OEDB V164/9500 curve")
    ey = json.loads((RESULTS / "energy_yield.json").read_text(encoding="utf-8"))
    if ey["power_curve"] != tcfg.POWER_CURVE_ID:
        raise ValueError("results/revised were produced with a different curve")
    pts = np.asarray(tcfg.POWER_CURVE_MS_KW, dtype=float)
    pts[:, 1] /= 1000.0
    n_oedb = int(np.flatnonzero(pts[:, 0] == OEDB_LAST_MS)[0]) + 1
    oedb, boundary = pts[:n_oedb], pts[n_oedb:]
    if not (oedb[-1, 0] == 24.5 and boundary[:, 0].tolist() == [25.0, 25.01, 30.0]):
        raise ValueError("unexpected split between OEDB and boundary points")
    retired = np.asarray(tcfg.POWER_CURVE_ORIGINAL_MS_KW, dtype=float)
    retired[:, 1] /= 1000.0
    # the production interpolation, exactly as the energy model evaluates it
    e04 = _energy_module()
    u = np.unique(np.r_[np.linspace(0, 30, 3001), pts[:, 0],
                        tcfg.TURBINE.cut_in_ms - 1e-9, tcfg.TURBINE.cut_out_ms - 1e-9])
    p = e04.power_from_speed(u.copy()) / 1000.0
    return CurveData(oedb, boundary, retired, u, p, tcfg.TURBINE.cut_in_ms, tcfg.TURBINE.rated_ms,
                     tcfg.TURBINE.cut_out_ms, tcfg.TURBINE.rated_power_mw, tcfg.POWER_CURVE_ID,
                     f"{tcfg.TURBINE.manufacturer} {tcfg.TURBINE.model}", "1.225 kg m⁻³ assumed")


def _plot_line(ax, u, p, **kw):
    """Draw a piecewise curve, breaking it at vertical jumps (cut-in, cut-out)."""
    jumps = np.where(np.abs(np.diff(p)) > 0.05)[0]
    jumps = [j for j in jumps if u[j + 1] - u[j] <= 0.011]      # cut-in / cut-out steps
    starts = [0] + [j + 1 for j in jumps]
    ends = [j + 1 for j in jumps] + [len(u)]
    lines = []
    for a, b in zip(starts, ends):
        lines += ax.plot(u[a:b], p[a:b], **kw)
        kw.pop("label", None)
    return lines


def build_figure(d: CurveData):
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(W_MM, H_MM))
        ax = fig.add_axes([LEFT_MM / W_MM, BOTTOM_MM / H_MM, (W_MM - LEFT_MM - RIGHT_MM) / W_MM,
                           (H_MM - TOP_MM - BOTTOM_MM) / H_MM], label="panel")
        ax.set_xlim(0, 30.6)
        ax.set_ylim(0, 11)
        ax.xaxis.set_major_locator(MultipleLocator(2))
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        ax.yaxis.set_major_locator(MultipleLocator(2))
        ax.yaxis.set_minor_locator(MultipleLocator(1))
        ax.grid(axis="y", which="major", color=GRID, linewidth=fs.LW_GRID, zorder=0)
        ax.set_axisbelow(True)
        ax.spines["left"].set_color(AXIS)
        ax.spines["bottom"].set_color(AXIS)
        ax.tick_params(axis="both", which="major", length=fs.TICK_MAJOR, width=fs.LW_AXIS, color=AXIS,
                       labelsize=FS_AXIS, labelcolor=INK, pad=fs.TICK_PAD)
        ax.tick_params(axis="both", which="minor", length=fs.TICK_MINOR, width=fs.LW_MIN, color=AXIS)
        ax.set_xlabel(f"Hub-height wind speed ({UNIT_SPEED})", fontsize=FS_AXIS)
        ax.set_ylabel("Electrical power (MW)", fontsize=FS_AXIS)

        # thresholds
        for v, name in ((d.cut_in, "cut-in"), (d.rated_speed, "rated"), (d.cut_out, "cut-out")):
            ax.axvline(v, color=GUIDE, linewidth=fs.LW_GUIDE, linestyle=fs.DOT_GUIDE, dash_capstyle="butt",
                       zorder=0.5, gid=f"guide_{name.replace('-', '')}")
            ax.text(v, 10.85, f"{name}\n{v:g} {UNIT_SPEED}", ha="center", va="top", fontsize=FS_NOTE,
                    color=MUTED, linespacing=1.3, bbox=PLATE, zorder=4)
        ax.axhline(d.rated_mw, xmin=0, xmax=1, color=GUIDE, linewidth=fs.LW_GUIDE,
                   linestyle=fs.DOT_GUIDE, dash_capstyle="butt", zorder=0.5, gid="guide_rated_power")
        ax.text(15.0, d.rated_mw - 0.25, f"rated power {d.rated_mw:g} MW", ha="left", va="top",
                fontsize=FS_NOTE, color=MUTED, zorder=4)

        # retired curve (superseded), production line, OEDB and boundary points
        _plot_line(ax, d.retired[:, 0], d.retired[:, 1], color=C_RETIRED, linewidth=fs.LW_DATA,
                   linestyle=fs.DASH_REF, zorder=1.5, gid="retired_curve")
        _plot_line(ax, d.u_line, d.p_line, color=C_CURVE, linewidth=fs.LW_DATA + 0.4,
                   solid_joinstyle="round", zorder=2, gid="production_interpolation")
        ax.plot(d.oedb[:, 0], d.oedb[:, 1], linestyle="none", marker="o", markersize=3.4,
                color=C_CURVE, markeredgecolor=fs.SURFACE, markeredgewidth=fs.MEW * 0.8, zorder=3,
                gid="oedb_points")
        ax.plot(d.boundary[:, 0], d.boundary[:, 1], linestyle="none", marker="o", markersize=3.6,
                markerfacecolor=fs.SURFACE, markeredgecolor=C_CURVE, markeredgewidth=fs.LW_DATA,
                zorder=3, gid="boundary_points")

        handles = [
            (Line2D([], [], color=C_CURVE, linewidth=fs.LW_DATA + 0.4),
             Line2D([], [], linestyle="none", marker="o", markersize=3.4, color=C_CURVE,
                    markeredgecolor=fs.SURFACE, markeredgewidth=fs.MEW * 0.8)),
            Line2D([], [], linestyle="none", marker="o", markersize=3.6, markerfacecolor=fs.SURFACE,
                   markeredgecolor=C_CURVE, markeredgewidth=fs.LW_DATA),
            Line2D([], [], color=C_RETIRED, linewidth=fs.LW_DATA, linestyle=fs.DASH_REF),
        ]
        labels = [
            "Active OEDB V164/9500 curve: digitised points\nand the interpolation used by the energy model",
            "Boundary points closing the curve (not OEDB data)",
            "Retired original curve (undocumented; superseded)",
        ]
        from matplotlib.legend_handler import HandlerTuple
        ax.legend(handles, labels, loc="lower right", bbox_to_anchor=(0.995, 0.12), frameon=False,
                  fontsize=FS_NOTE, handlelength=2.4, labelspacing=0.75,
                  handler_map={tuple: HandlerTuple(ndivide=1, pad=0)})

        fig.canvas.draw()
        fs.panel_heading(fig, ax, "", f"{d.turbine} power curve",
                         "Electrical output at standard air density")
    return fig


def layout_problems(fig) -> list[str]:
    return fs.layout_problems(fig) + fs.print_problems(fig)


def caption(d: CurveData) -> str:
    i14 = int(np.argmax(d.oedb[:, 1] >= d.rated_mw))
    p_cutin = d.oedb[np.isclose(d.oedb[:, 0], d.cut_in), 1][0]
    r_full = d.retired[np.argmax(d.retired[:, 1] >= d.rated_mw), 0]
    return (
        f"**Figure 4.** Power curve of the {d.turbine} reference turbine used in this study. "
        f"Filled markers are the {len(d.oedb)} points (0–{d.oedb[-1, 0]:g} m s⁻¹) "
        f"of the 'V164/9500' entry of the Open Energy Database turbine library, a third-party "
        f"digitisation of the power-curve graph published by the manufacturer; it is not a "
        f"manufacturer-certified table, and its air density is not documented "
        f"({d.rho_note}). The solid line is the interpolation applied to every hourly wind "
        f"speed in the energy model: linear between points, zero below the {d.cut_in:g} m s⁻¹ "
        f"cut-in (where the curve starts at {p_cutin * 1000:.0f} kW) and zero at and above the "
        f"{d.cut_out:g} m s⁻¹ cut-out. Rated power ({d.rated_mw:g} MW) is first reached at "
        f"{d.oedb[i14, 0]:g} m s⁻¹. The OEDB table ends at {d.oedb[-1, 0]:g} m s⁻¹; the open "
        f"markers hold the rated plateau to the stated cut-out speed and close the curve, and "
        f"are model assumptions rather than OEDB data. No cut-out hysteresis or high-wind "
        f"ride-through is modelled. The dashed grey line is the curve used in the original "
        f"analysis, whose source is undocumented; it reaches rated power at {r_full:g} m s⁻¹ and "
        f"lies above the active curve between cut-in and rated speed. It is shown for comparison "
        f"only and is superseded: no result in this study uses it.\n"
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
    print(f"curve {d.curve_id}: {len(d.oedb)} OEDB points + {len(d.boundary)} boundary points")
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
