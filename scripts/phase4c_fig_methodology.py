"""
Phase 4C — Figure: methodology workflow
=======================================
A vector flow diagram of the revised (Phase 4B) production model.

Primary chain (solid boxes, solid arrows), as implemented in
scripts/03_process_era5.py, 04_fit_weibull_aep.py and 06_emissions_and_scenarios.py:

  ERA5 hourly wind -> hub-height speed -> active OEDB power curve
  -> empirical hourly energy -> nominal losses -> net energy yield
  -> avoided grid CO2

Supporting analyses (dashed boxes, dashed connectors), which never feed the
primary estimate:
  * Weibull fit: descriptive statistic and AEP cross-check (comparison only);
  * interannual variability and sampling uncertainty of the 11-year mean;
  * wind-speed scaling and loss-scenario experiments.

No result values are drawn. The only numbers are inputs and design choices
(grid node, period, hub height, scaling factors, reference year of the grid
factors). The retired Weibull Monte Carlo is not part of the model and is not
drawn.

Writes figures/revised/methodology.{pdf,svg,png} and _caption.md (180 mm).
Run from the repository root:  python scripts/phase4c_fig_methodology.py
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import figure_style as fs
from config.figure_style import FS_AXIS, FS_NOTE, INK, MUTED
from config import turbine as tcfg

RESULTS = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "methodology"

W_MM, H_MM = fs.FULL_WIDTH_MM, 115.0
MAIN_X, MAIN_W = 58.0, 66.0
LEFT_X, LEFT_W = 3.0, 47.0
RIGHT_X, RIGHT_W = 132.0, 45.0
BOX_H, PITCH, TOP_Y = 10.5, 14.5, 104.0
LW_BOX = fs.LW_DATA
DASH_SIDE = (0, (3.0, 2.0))
C_MAIN = INK
C_SIDE = MUTED
C_ARROW = fs.PRIMARY


@dataclass
class Box:
    key: str
    title: str
    detail: str
    x: float
    y: float                            # centre
    w: float
    h: float = BOX_H
    side: bool = False
    artists: list = field(default_factory=list)

    @property
    def left(self): return self.x
    @property
    def right(self): return self.x + self.w
    @property
    def top(self): return self.y + self.h / 2
    @property
    def bottom(self): return self.y - self.h / 2
    @property
    def cx(self): return self.x + self.w / 2


@dataclass(frozen=True)
class FlowData:
    node: tuple[float, float]
    period: tuple[str, str]
    hub_height_m: float
    curve_id: str
    speed_factors: tuple[float, ...]
    primary_factor: str
    loss_keys: tuple[str, ...]


def load_data() -> FlowData:
    """Design inputs only; no result value is read for display."""
    wr = json.loads((RESULTS / "wind_resource.json").read_text(encoding="utf-8"))
    ey = json.loads((RESULTS / "energy_yield.json").read_text(encoding="utf-8"))
    ws = json.loads((RESULTS / "wind_speed_sensitivity.json").read_text(encoding="utf-8"))
    em = json.loads((RESULTS / "emissions.json").read_text(encoding="utf-8"))
    ss = json.loads((RESULTS / "site_screening.json").read_text(encoding="utf-8"))
    if ey["estimator"] != "empirical hourly power conversion (primary)":
        raise ValueError("the primary estimator is no longer the empirical hourly conversion")
    if ey["power_curve"] != tcfg.POWER_CURVE_ID:
        raise ValueError("results/revised use a different power curve")
    lon, lat = ss["era5_node_representativeness"]["node_lon_lat"]
    period = wr["data"]["period"]
    factors = tuple(c["speed_factor"] for c in ws["cases"]
                    if c["case"] in ("-10%", "-5%", "+5%", "+10%"))
    return FlowData((float(lat), float(lon)), (period[:4], period[14:18]), float(wr["hub_height_m"]),
                    str(ey["power_curve"]), factors,
                    str(em["primary_avoided_operational_co2"]["factor"]),
                    tuple(k for k in tcfg.LOSS_SCENARIOS if k != "nominal"))


def boxes(d: FlowData) -> dict[str, Box]:
    lat, lon = d.node
    curve = d.curve_id.split("_", 1)[1].replace("_", "/")       # V164/9500
    rows = [
        ("era5", "ERA5 hourly reanalysis",
         f"grid node {lat:.2f}° N, {lon:.2f}° E; {d.period[0]}–{d.period[1]}"),
        ("hub", f"Hub-height wind speed ({d.hub_height_m:g} m)",
         "100 m wind, ERA5 10–100 m shear exponent"),
        ("curve", "Turbine power curve",
         f"active OEDB {curve}, piecewise linear"),
        ("energy", "Empirical hourly energy",
         "every hour converted; no distribution model"),
        ("losses", "Nominal losses",
         "wake, availability, electrical (assumed)"),
        ("net", "Net energy yield per MW",
         "capacity factor × 8 766 h average year"),
        ("co2", "Avoided operational grid CO₂",
         "2023 combined margin; life cycle separate"),
    ]
    out = {}
    for i, (k, t, det) in enumerate(rows):
        out[k] = Box(k, t, det, MAIN_X, TOP_Y - i * PITCH, MAIN_W)
    lo, hi = min(d.speed_factors), max(d.speed_factors)
    out["weibull"] = Box("weibull", "Weibull distribution fit",
                         "descriptive statistic and\ncapacity-factor cross-check",
                         LEFT_X, out["hub"].y, LEFT_W, h=BOX_H + 3.0, side=True)
    out["sens"] = Box("sens", "Sensitivity experiments",
                      f"hourly speeds × {lo:.2f}–{hi:.2f};\nlow- and high-loss scenarios",
                      RIGHT_X, (out["curve"].y + out["energy"].y) / 2, RIGHT_W, h=BOX_H + 3.0, side=True)
    out["unc"] = Box("unc", "Year-to-year variability",
                     "annual yields and sampling\ninterval of the 11-year mean",
                     RIGHT_X, out["net"].y, RIGHT_W, h=BOX_H + 3.0, side=True)
    return out


def _draw_box(ax, b: Box):
    rect = Rectangle((b.left, b.bottom), b.w, b.h, facecolor=fs.SURFACE,
                     edgecolor=C_SIDE if b.side else C_MAIN, linewidth=LW_BOX,
                     linestyle=DASH_SIDE if b.side else "-", zorder=2, gid=f"box_{b.key}")
    ax.add_patch(rect)
    n_detail = b.detail.count("\n") + 1
    title_y = b.y + 1.0 + 1.6 * (n_detail - 1)          # stack centred on the box (mm)
    t1 = ax.text(b.cx, title_y, b.title, ha="center", va="baseline", fontsize=FS_AXIS,
                 color=INK, zorder=3)
    t2 = ax.text(b.cx, title_y - 1.6, b.detail, ha="center", va="top", fontsize=FS_NOTE,
                 color=MUTED, linespacing=1.3, zorder=3)
    b.artists = [rect, t1, t2]


def _arrow(ax, path, gid, dashed=False, head=True, colour=None):
    """Polyline in mm; the last segment carries the arrow head."""
    colour = colour or (C_SIDE if dashed else C_ARROW)
    kw = dict(color=colour, linewidth=fs.LW_DATA, zorder=1.5,
              linestyle=DASH_SIDE if dashed else "-")
    for (x0, y0), (x1, y1) in zip(path[:-2], path[1:-1]):
        ax.plot([x0, x1], [y0, y1], solid_capstyle="butt", dash_capstyle="butt", gid=gid, **kw)
    (x0, y0), (x1, y1) = path[-2], path[-1]
    if head:
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=7,
                                     shrinkA=0, shrinkB=0, gid=gid, capstyle="butt",
                                     joinstyle="miter", **kw))
    else:
        ax.plot([x0, x1], [y0, y1], solid_capstyle="butt", dash_capstyle="butt", gid=gid, **kw)


def build_figure(d: FlowData):
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(W_MM, H_MM))
        ax = fig.add_axes([0, 0, 1, 1], label="diagram")
        ax.set_xlim(0, W_MM)
        ax.set_ylim(0, H_MM)
        ax.set_axis_off()
        bx = boxes(d)
        for b in bx.values():
            _draw_box(ax, b)

        chain = ["era5", "hub", "curve", "energy", "losses", "net", "co2"]
        for a, b in zip(chain[:-1], chain[1:]):
            _arrow(ax, [(bx[a].cx, bx[a].bottom), (bx[b].cx, bx[b].top)], gid="main_arrow")

        # Weibull: fed by the hourly speeds; compared with, never feeding, the hourly energy
        w = bx["weibull"]
        _arrow(ax, [(bx["hub"].left, bx["hub"].y), (w.right, w.y)], gid="side_arrow", dashed=True)
        xm = w.cx
        _arrow(ax, [(xm, w.bottom), (xm, bx["energy"].y), (bx["energy"].left, bx["energy"].y)],
               gid="comparison_line", dashed=True, head=False)
        ax.text(xm + 1.6, (w.bottom + bx["energy"].y) / 2, "compared only;\nnot an input",
                ha="left", va="center", fontsize=FS_NOTE, color=MUTED, linespacing=1.3)

        # Sensitivity: reruns with scaled speeds and alternative losses
        s = bx["sens"]
        xs = s.cx
        _arrow(ax, [(bx["hub"].right, bx["hub"].y), (xs, bx["hub"].y), (xs, s.top)],
               gid="side_arrow", dashed=True)
        _arrow(ax, [(bx["losses"].right, bx["losses"].y), (xs, bx["losses"].y), (xs, s.bottom)],
               gid="side_arrow", dashed=True)
        # Interannual variability and sampling uncertainty from the annual yields
        u = bx["unc"]
        _arrow(ax, [(bx["net"].right, bx["net"].y), (u.left, u.y)], gid="side_arrow", dashed=True)

        # key
        ky = 5.2
        ax.add_patch(Rectangle((MAIN_X - 56, ky - 1.6), 7, 3.2, facecolor=fs.SURFACE, edgecolor=C_MAIN,
                               linewidth=LW_BOX, zorder=2))
        ax.text(MAIN_X - 47, ky, "Primary estimation chain", ha="left", va="center_baseline",
                fontsize=FS_NOTE, color=INK)
        ax.add_patch(Rectangle((MAIN_X + 2, ky - 1.6), 7, 3.2, facecolor=fs.SURFACE, edgecolor=C_SIDE,
                               linewidth=LW_BOX, linestyle=DASH_SIDE, zorder=2))
        ax.text(MAIN_X + 11, ky, "Supporting analysis; does not produce the primary estimate",
                ha="left", va="center_baseline", fontsize=FS_NOTE, color=INK)
    return fig, bx


def box_problems(bx: dict[str, Box], fig) -> list[str]:
    """Text that does not fit inside its own box (1 mm inner margin)."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    out = []
    for b in bx.values():
        rect = b.artists[0].get_window_extent(r)
        m = 1.0 / 25.4 * fig.dpi
        for t in b.artists[1:]:
            bb = t.get_window_extent(r)
            if bb.x0 < rect.x0 + m or bb.x1 > rect.x1 - m or bb.y0 < rect.y0 + m or bb.y1 > rect.y1 - m:
                out.append(f"text does not fit its box: {t.get_text()!r}")
    return out


def layout_problems(fig, bx) -> list[str]:
    return fs.layout_problems(fig) + fs.print_problems(fig) + box_problems(bx, fig)


def caption(d: FlowData) -> str:
    lat, lon = d.node
    lo, hi = min(d.speed_factors), max(d.speed_factors)
    return (
        f"**Figure 2.** Workflow of the energy and avoided-emission model. Solid boxes and arrows "
        f"form the primary estimation chain: hourly ERA5 reanalysis wind at the grid node "
        f"{lat:.2f}° N, {lon:.2f}° E ({d.period[0]}–{d.period[1]}) is extrapolated from 100 m to the "
        f"{d.hub_height_m:g} m hub height with a power-law shear exponent derived from the ERA5 10 m "
        f"and 100 m levels; every hourly speed is converted to electrical power with the active "
        f"OEDB V164/9500 power curve; the resulting empirical capacity factor is reduced by "
        f"nominal wake, availability and electrical losses and expressed as net energy yield per "
        f"installed megawatt for an average year of 8 766 h; avoided operational grid CO₂ follows "
        f"from the 2023 combined-margin emission factor, with life-cycle greenhouse-gas emissions "
        f"reported separately in CO₂-equivalent. Dashed boxes are supporting analyses that do not "
        f"produce the primary estimate: a Weibull fit to the hourly speeds, used as a descriptive "
        f"statistic and as a cross-check of the capacity factor (compared with, not used as an "
        f"input to, the empirical energy); the observed interannual variability of the annual "
        f"yields and the sampling confidence interval of the 11-year mean; and sensitivity "
        f"experiments that rerun the chain with all hourly speeds scaled by {lo:.2f}–{hi:.2f} or "
        f"with alternative loss assumptions. No step uses Monte Carlo sampling.\n"
    )


def main(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    d = load_data()
    fig, bx = build_figure(d)
    problems = layout_problems(fig, bx)
    if problems:
        raise RuntimeError("figure layout check failed: " + "; ".join(problems))
    paths = fs.save_figure(fig, out_dir, STEM)
    plt.close(fig)
    paths["caption"] = Path(out_dir) / f"{STEM}_caption.md"
    paths["caption"].write_text(caption(d), encoding="utf-8")
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
