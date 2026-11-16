"""
Figure 3: three ERA5 grid nodes and the ERA5-GWA wind-product discrepancy
==========================================================================
Two panels on one longitude axis (the three nodes lie on 40.50 N).

  (a) Long-term net energy yield (1994-2024) at the primary node and its two
      neighbours, with each node's ERA5 land-sea-mask value and the difference
      from the primary node. The nodes are not averaged; nothing joins them,
      and their differences are not drawn as an interval.
  (b) Mean 100 m wind speed for the period of the Global Wind Atlas,
      2008-2017: ERA5 at each node, the GWA 4.0 mean over the sea pixels of
      the same 0.25 deg cell, and the GWA 4.0 mean over the candidate
      polygon. GWA is a downscaling of ERA5, not an observation; the ratios
      describe the disagreement between two models.

Both panels show the longitude range of the candidate polygon and the
boundaries between the three 0.25 deg cells (26.125 E and 26.375 E). The
polygon range comes from config/site.py (the vertices of the official KML);
every plotted value comes from results/revised/:

  node_sensitivity.json            nodes.{W,C,E}: lon, net_gwh_per_mw,
                                   energy_rel_to_primary_node_pct,
                                   era5_land_sea_mask_fraction, period
  wind_product_discrepancy.json    per_node_gwa_box_vs_era5.{W,C,E}:
                                   era5_U100_ms.2008-2017,
                                   gwa4_100m_ms.box_0p25deg_sea_pixels_mean_ms,
                                   ratio_gwa_box_sea_pixels_to_era5_period_matched;
                                   products.gwa4.period, polygon_mean_ms

Run from the repository root:  python scripts/fig3_nodes_and_products.py
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
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FormatStrFormatter, MultipleLocator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import figure_style as fs
from config.figure_style import (BAND, EMPHASIS, FS_NOTE, GRID, INK, MUTED, PRIMARY,
                                 SURFACE, UNIT_YIELD)
from config.site import SAROS_POLYGON_LONLAT

RESULTS = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "fig3_nodes_and_products"

W_MM, H_MM = fs.FULL_WIDTH_MM, 87.5
LEFT_MM, RIGHT_MM, TOP_MM, BOTTOM_MM = 15.0, 3.0, 8.0, 22.5
GAP_MM = 15.0
XLIM = (25.90, 26.60)
YLIM_A = (1.95, 2.75)
YLIM_B = (6.3, 8.5)
NODES = ("W", "C", "E")
CELL_HALF_DEG = 0.125                  # ERA5 0.25 deg grid: a node represents its cell
C_ERA5, C_GWA = PRIMARY, EMPHASIS      # one colour per wind product


@dataclass(frozen=True)
class FigureData:
    lon: dict                          # node -> longitude (deg E)
    lat: float
    primary: str
    period_energy: str                 # 1994-2024
    net: dict                          # node -> net GWh MW-1 yr-1
    rel_pct: dict                      # node -> % relative to the primary node
    land_fraction: dict
    gwa_period: str                    # 2008-2017
    era5_u100_gwa_period: dict         # node -> m/s
    gwa_cell_sea: dict                 # node -> m/s
    ratio_cell_sea: dict
    gwa_polygon: float
    era5_primary_u100_gwa_period: float
    polygon_lon: tuple[float, float]

    @property
    def cell_edges(self) -> tuple[float, ...]:
        lons = sorted(self.lon.values())
        return tuple((a + b) / 2 for a, b in zip(lons, lons[1:]))

    @property
    def ratio_polygon(self) -> float:
        return self.gwa_polygon / self.era5_primary_u100_gwa_period


def load_data(results: Path = RESULTS) -> FigureData:
    ns = json.loads((results / "node_sensitivity.json").read_text(encoding="utf-8"))
    wp = json.loads((results / "wind_product_discrepancy.json").read_text(encoding="utf-8"))
    nodes, box = ns["nodes"], wp["per_node_gwa_box_vs_era5"]
    gwa_period = wp["products"]["gwa4"]["period"]
    lons = [p[0] for p in SAROS_POLYGON_LONLAT]
    d = FigureData(
        lon={k: float(nodes[k]["lon"]) for k in NODES},
        lat=float(nodes["C"]["lat"]),
        primary=next(k for k in NODES if nodes[k]["is_primary_node"]),
        period_energy=ns["assumptions"]["period"].replace("-", "–"),
        net={k: float(nodes[k]["net_gwh_per_mw"]) for k in NODES},
        rel_pct={k: float(nodes[k]["energy_rel_to_primary_node_pct"]) for k in NODES},
        land_fraction={k: float(nodes[k]["era5_land_sea_mask_fraction"]) for k in NODES},
        gwa_period=gwa_period.replace("-", "–"),
        era5_u100_gwa_period={k: float(box[k]["era5_U100_ms"][gwa_period]) for k in NODES},
        gwa_cell_sea={k: float(box[k]["gwa4_100m_ms"]["box_0p25deg_sea_pixels_mean_ms"]) for k in NODES},
        ratio_cell_sea={k: float(box[k]["ratio_gwa_box_sea_pixels_to_era5_period_matched"]) for k in NODES},
        gwa_polygon=float(wp["products"]["gwa4"]["polygon_mean_ms"]),
        era5_primary_u100_gwa_period=float(wp["polygon_vs_primary_node"]["era5_node_U100_ms"][gwa_period]),
        polygon_lon=(min(lons), max(lons)),
    )
    problems = verify(d, ns, wp)
    if problems:
        raise ValueError("Figure 3 data check failed: " + "; ".join(problems))
    return d


def verify(d: FigureData, ns: dict, wp: dict) -> list[str]:
    out = []
    if d.primary != "C" or d.rel_pct["C"] != 0.0:
        out.append("primary node is not C")
    if ns["reference_baseline"]["period"] != "1994-2024" or d.period_energy != "1994–2024":
        out.append("node comparison is not for 1994-2024")
    if d.gwa_period != "2008–2017":
        out.append(f"unexpected GWA period {d.gwa_period}")
    for k in NODES:
        if abs(wp["per_node_gwa_box_vs_era5"][k]["lon"] - d.lon[k]) > 1e-9:
            out.append(f"node {k} longitude differs between the two result files")
        if abs(d.gwa_cell_sea[k] / d.era5_u100_gwa_period[k] - d.ratio_cell_sea[k]) > 1e-9:
            out.append(f"node {k}: stored ratio is not GWA/ERA5")
    if abs(d.ratio_polygon - wp["polygon_vs_primary_node"]["ratio_gwa_to_era5"]
           ["era5_2008-2017_period_matched"]) > 1e-9:
        out.append("polygon ratio disagrees with wind_product_discrepancy.json")
    if any(abs(e - c) > 1e-9 for e, c in zip(d.cell_edges, (26.125, 26.375))):
        out.append("cell boundaries are not 26.125 E and 26.375 E")
    if not (d.lon["W"] < d.polygon_lon[0] and d.polygon_lon[1] < d.lon["E"]):
        out.append("polygon longitude range is not between the outer nodes")
    return out


def _minus(s: str) -> str:
    return s.replace("-", "−")


def _context(ax, d: FigureData):
    ax.axvspan(*d.polygon_lon, facecolor=BAND, edgecolor="none", zorder=0, gid="polygon_lon_range")
    for e in d.cell_edges:
        ax.axvline(e, color=MUTED, linewidth=fs.LW_GUIDE, linestyle=fs.DOT_GUIDE, zorder=1,
                   gid="cell_boundary")
    ax.set_xlim(*XLIM)
    ax.set_xticks([d.lon[k] for k in NODES], [f"{d.lon[k]:.2f}° E" for k in NODES])
    ax.tick_params(axis="x", which="minor", bottom=False)
    ax.grid(True, axis="y", color=GRID, linewidth=fs.LW_GRID)


def build_figure(d: FigureData):
    panel_w = (W_MM - LEFT_MM - RIGHT_MM - GAP_MM) / 2
    panel_h = H_MM - TOP_MM - BOTTOM_MM
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(W_MM, H_MM))
        ax_a = fig.add_axes([LEFT_MM / W_MM, BOTTOM_MM / H_MM, panel_w / W_MM, panel_h / H_MM],
                            label="panel_a")
        ax_b = fig.add_axes([(LEFT_MM + panel_w + GAP_MM) / W_MM, BOTTOM_MM / H_MM, panel_w / W_MM,
                             panel_h / H_MM], label="panel_b")
        for ax in (ax_a, ax_b):
            _context(ax, d)

        # ---- (a) net yield per node --------------------------------------------
        ax_a.set_ylim(*YLIM_A)
        ax_a.yaxis.set_major_locator(MultipleLocator(0.2))
        ax_a.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        for k in NODES:
            primary = k == d.primary
            ax_a.plot([d.lon[k]], [d.net[k]], linestyle="none", marker="s",
                      markersize=fs.MS_EMPHASIS if primary else fs.MS_POINT, color=C_ERA5,
                      markeredgecolor=SURFACE, markeredgewidth=fs.MEW, zorder=3, gid=f"node_{k}")
            change = "primary node" if primary else f"{_minus(f'{d.rel_pct[k]:+.1f}')} %"
            ax_a.annotate(f"{d.net[k]:.3f}\n{change}", (d.lon[k], d.net[k]), xytext=(0, 7),
                          textcoords="offset points", ha="center", va="bottom", fontsize=FS_NOTE,
                          color=INK, linespacing=1.15)
            ax_a.annotate(f"land–sea mask\n{d.land_fraction[k]:.2f}", (d.lon[k], YLIM_A[0]),
                          xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                          fontsize=FS_NOTE, color=MUTED, linespacing=1.15)
        ax_a.set_ylabel(f"Net yield ({UNIT_YIELD})")

        # ---- (b) mean 100 m wind speed, GWA period ----------------------------------
        ax_b.set_ylim(*YLIM_B)
        ax_b.yaxis.set_major_locator(MultipleLocator(0.5))
        ax_b.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        ax_b.plot(list(d.polygon_lon), [d.gwa_polygon] * 2, color=C_GWA, linewidth=fs.LW_DATA,
                  linestyle=fs.DASH_REF, solid_capstyle="butt", zorder=2, gid="gwa_polygon_mean")
        ax_b.plot([d.lon[k] for k in NODES], [d.era5_u100_gwa_period[k] for k in NODES],
                  linestyle="none", marker="s", markersize=fs.MS_POINT, color=C_ERA5,
                  markeredgecolor=SURFACE, markeredgewidth=fs.MEW, zorder=3, gid="era5_u100")
        ax_b.plot([d.lon[k] for k in NODES], [d.gwa_cell_sea[k] for k in NODES],
                  linestyle="none", marker="D", markersize=fs.MS_POINT - 0.6, color=C_GWA,
                  markeredgecolor=SURFACE, markeredgewidth=fs.MEW, zorder=3, gid="gwa_cell_sea")
        for k in NODES:
            ax_b.annotate(f"×{d.ratio_cell_sea[k]:.2f}",
                          (d.lon[k], (d.era5_u100_gwa_period[k] + d.gwa_cell_sea[k]) / 2),
                          xytext=(5, 0), textcoords="offset points", ha="left", va="center",
                          fontsize=FS_NOTE, color=MUTED, gid=f"ratio_{k}")
        ax_b.annotate(f"polygon mean ×{d.ratio_polygon:.2f}", (d.polygon_lon[0], d.gwa_polygon),
                      xytext=(3, 3), textcoords="offset points", ha="left", va="bottom",
                      fontsize=FS_NOTE, color=MUTED, gid="ratio_polygon")
        ax_b.set_ylabel("Mean wind speed at 100 m (m s$^{-1}$)")

        # ---- key and headings ----------------------------------------------------------
        handles = [
            Line2D([], [], linestyle="none", marker="s", markersize=fs.MS_POINT, color=C_ERA5,
                   markeredgecolor=SURFACE, markeredgewidth=fs.MEW),
            Line2D([], [], linestyle="none", marker="D", markersize=fs.MS_POINT - 0.6, color=C_GWA,
                   markeredgecolor=SURFACE, markeredgewidth=fs.MEW),
            Line2D([], [], color=C_GWA, linewidth=fs.LW_DATA, linestyle=fs.DASH_REF),
            Patch(facecolor=BAND, edgecolor="none"),
            Line2D([], [], color=MUTED, linewidth=fs.LW_GUIDE, linestyle=fs.DOT_GUIDE),
        ]
        labels = [
            f"ERA5 at the node, {d.gwa_period}",
            f"GWA 4.0, sea pixels, 0.25° box at node, {d.gwa_period}",
            f"GWA 4.0, mean over the candidate polygon, {d.gwa_period}",
            "Longitude range of the candidate polygon",
            "Boundary between nearest-node areas",
        ]
        fig.legend(handles[:3], labels[:3], loc="upper left", frameon=False, fontsize=FS_NOTE,
                   bbox_to_anchor=((LEFT_MM + panel_w + GAP_MM) / W_MM, (BOTTOM_MM - 8.0) / H_MM),
                   borderaxespad=0, borderpad=0, handlelength=1.8, handletextpad=0.6,
                   labelspacing=0.4)
        fig.legend(handles[3:], labels[3:], loc="upper left", frameon=False, fontsize=FS_NOTE,
                   bbox_to_anchor=(LEFT_MM / W_MM, (BOTTOM_MM - 8.0) / H_MM),
                   borderaxespad=0, borderpad=0, handlelength=1.8, handletextpad=0.6,
                   labelspacing=0.4)
        fs.panel_heading(fig, ax_a, "(a)", "Net yield by grid node", f"ERA5, {d.period_energy}")
        fs.panel_heading(fig, ax_b, "(b)", "ERA5 and Global Wind Atlas", f"100 m, {d.gwa_period}",
                         x_mm=LEFT_MM + panel_w + GAP_MM - 13.0)
    return fig


def layout_problems(fig) -> list[str]:
    return fs.layout_problems(fig) + fs.print_problems(fig)


def main(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    d = load_data()
    fig = build_figure(d)
    problems = layout_problems(fig)
    if problems:
        raise RuntimeError("Figure 3 layout check failed: " + "; ".join(problems))
    paths = fs.save_figure(fig, out_dir, STEM)
    plt.close(fig)
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
