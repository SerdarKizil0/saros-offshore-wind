"""
Phase 4C — Figure: avoided grid CO2 under alternative accounting conventions
============================================================================
  (a) Avoided operational grid CO2 per installed MW: the net energy yield times
      each 2023 Turkish grid emission factor. The combined margin (wind/solar)
      is the primary convention; the operating margin, build margin and
      generation average are context conventions, drawn as separate bars, not
      as bounds or an interval around the primary value.
  (b) Offshore-wind life-cycle greenhouse-gas emissions per installed MW, in
      CO2-equivalent, reported separately and never subtracted from (a)
      (different gases and system boundaries).

Inputs: results/revised/emissions.json (all plotted values),
results/revised/energy_yield.json (cross-check of the energy input).
Capacity scenarios (scenarios.json, S1-S3) are E x MW scalings of the same
per-MW values and add no information to this comparison; they are not drawn.
The generation average in CO2-eq is a different unit and is not drawn in (a).

Writes figures/revised/avoided_co2.{pdf,svg,png} and _caption.md (180 mm).
Run from the repository root:  python scripts/phase4c_fig_avoided_co2.py
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
from config.figure_style import AXIS, FS_AXIS, FS_NOTE, GRID, GUIDE, INK, MUTED

RESULTS = ROOT / "results" / "revised"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "avoided_co2"

LEFT_MM, RIGHT_MM, TOP_MM, BOTTOM_MM = 52.0, 5.0, 9.0, 12.5
ROW_MM, GAP_MM, AXIS_GAP_MM = 7.6, 9.0, 10.5
N_A, N_B = 4, 1
W_MM = fs.FULL_WIDTH_MM
H_MM = TOP_MM + (N_A + N_B) * ROW_MM + AXIS_GAP_MM + GAP_MM + BOTTOM_MM
XMAX = 2000.0
C_PRIMARY = fs.PRIMARY
C_CONTEXT = GUIDE
C_LIFECYCLE = fs.BLUISH_GREEN
UNIT_CO2 = r"t CO$_2$ MW$^{-1}$ yr$^{-1}$"
UNIT_CO2EQ = r"t CO$_2$-eq MW$^{-1}$ yr$^{-1}$"
CONVENTIONS = (  # key in emissions.json, row label
    ("combined_margin_wind_solar", "Combined margin, wind/solar"),
    ("operating_margin", "Operating margin"),
    ("build_margin", "Build margin"),
    ("generation_average_co2", "Generation average"),
)


@dataclass(frozen=True)
class Row:
    label: str
    detail: str
    value: float
    primary: bool = False


@dataclass(frozen=True)
class Co2Data:
    energy_mwh_per_mw: float
    grid: tuple[Row, ...]
    primary_ci: tuple[float, float]
    lifecycle: float
    lifecycle_g: float
    lifecycle_range: tuple[float, float]
    lifecycle_g_range: tuple[float, float]
    gen_avg_co2eq: float
    primary_source: str


def _fmt_factor(v: float) -> str:
    return f"{v:g}"                    # as published: 0.6242, 0.7134, 0.3567, 0.43


def load_data() -> Co2Data:
    em = json.loads((RESULTS / "emissions.json").read_text(encoding="utf-8"))
    ey = json.loads((RESULTS / "energy_yield.json").read_text(encoding="utf-8"))
    energy = float(em["energy_input"]["net_mwh_per_mw_yr"])
    problems = []
    if abs(energy - ey["net_mwh_per_mw_yr"]) > 1e-9:
        problems.append("emissions.json uses a different energy value")
    prim = em["primary_avoided_operational_co2"]
    ctx = em["context_grid_methods"]
    rows = []
    for key, name in CONVENTIONS:
        if key == "combined_margin_wind_solar":
            f, val, unit = prim["factor_value"], prim["t_co2_per_mw_yr"], prim["factor_unit"]
            if prim["factor"] != key:
                problems.append("primary factor is not the combined margin")
            detail = f"primary · {_fmt_factor(f)} t CO$_2$ MWh$^{{-1}}$"
        else:
            c = ctx[key]
            f, val, unit = c["factor_value"], c["result_per_mw_yr"], c["factor_unit"]
            detail = f"context · {_fmt_factor(f)} t CO$_2$ MWh$^{{-1}}$"
        if unit != "tCO2/MWh":
            problems.append(f"{key}: unit {unit} is not CO2-only")
        if abs(energy * f - val) > 1e-6 * val:
            problems.append(f"{key}: value is not energy x factor")
        rows.append(Row(name, detail, float(val), primary=(key == "combined_margin_wind_solar")))
    lc = em["secondary_lifecycle_ghg"]
    ref = lc["cases"][lc["reference_case"]]
    lo, hi = lc["cases"]["ipcc_ar5_min"], lc["cases"]["ipcc_ar5_max"]
    if "CO2-eq" not in lc["unit"]:
        problems.append("life-cycle unit is not CO2-eq")
    if not all(0 < r.value < XMAX for r in rows) or hi["t_co2eq_per_mw_yr"] >= XMAX:
        problems.append("a value falls outside the fixed axis range")
    if problems:
        raise ValueError("results/revised is inconsistent: " + "; ".join(problems))
    return Co2Data(energy, tuple(rows), tuple(prim["ci90_t_co2_per_mw_yr"]),
                   float(ref["t_co2eq_per_mw_yr"]), float(ref["g_co2eq_per_kwh"]),
                   (float(lo["t_co2eq_per_mw_yr"]), float(hi["t_co2eq_per_mw_yr"])),
                   (float(lo["g_co2eq_per_kwh"]), float(hi["g_co2eq_per_kwh"])),
                   float(ctx["generation_average_co2eq"]["result_per_mw_yr"]), str(prim["source"]))


def _axes(fig, bottom_mm, n, label):
    ax = fig.add_axes([LEFT_MM / W_MM, bottom_mm / H_MM, (W_MM - LEFT_MM - RIGHT_MM) / W_MM,
                       n * ROW_MM / H_MM], label=label)
    ax.set_xlim(0, XMAX)
    ax.set_ylim(n - 0.5, -0.5)
    ax.xaxis.set_major_locator(MultipleLocator(250))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.grid(axis="x", which="major", color=GRID, linewidth=fs.LW_GRID, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", which="major", length=fs.TICK_MAJOR, width=fs.LW_AXIS, color=AXIS,
                   labelsize=FS_AXIS, labelcolor=INK, pad=fs.TICK_PAD)
    ax.set_yticks(range(n), [""] * n)
    return ax


def _row_label(ax, i, label, detail, bold=False):
    ax.annotate(label, (0, i), xycoords=("axes fraction", "data"), xytext=(-6, 2.2),
                textcoords="offset points", ha="right", va="bottom", fontsize=FS_AXIS, color=INK,
                fontweight="bold" if bold else "normal")
    ax.annotate(detail, (0, i), xycoords=("axes fraction", "data"), xytext=(-6, -1.6),
                textcoords="offset points", ha="right", va="top", fontsize=FS_NOTE, color=MUTED)


def build_figure(d: Co2Data):
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(W_MM, H_MM))
        ax_b = _axes(fig, BOTTOM_MM, N_B, "panel_b")
        ax_a = _axes(fig, BOTTOM_MM + N_B * ROW_MM + AXIS_GAP_MM + GAP_MM, N_A, "panel_a")

        # ---- (a) one bar per accounting convention -------------------------
        for i, r in enumerate(d.grid):
            ax_a.barh(i, r.value, height=0.56, color=C_PRIMARY if r.primary else C_CONTEXT,
                      edgecolor="none", zorder=2, gid="primary_bar" if r.primary else "context_bar")
            _row_label(ax_a, i, r.label, r.detail, bold=r.primary)
            ax_a.annotate(f"{r.value:,.0f}", (r.value, i), xytext=(4, 0), textcoords="offset points",
                          ha="left", va="center_baseline", fontsize=FS_NOTE,
                          color=INK, fontweight="bold" if r.primary else "normal")
        ax_a.set_xlabel(f"Avoided operational CO$_2$ ({UNIT_CO2})", fontsize=FS_AXIS)

        # ---- (b) life-cycle GHG, separate unit and panel ----------------------
        ax_b.barh(0, d.lifecycle, height=0.56, color=C_LIFECYCLE, edgecolor="none", zorder=2,
                  gid="lifecycle_bar")
        lo, hi = d.lifecycle_range
        ax_b.plot([lo, hi], [0, 0], color=INK, linewidth=fs.LW_DATA, solid_capstyle="butt", zorder=3,
                  gid="lifecycle_range")
        for x in (lo, hi):
            ax_b.plot([x, x], [-0.17, 0.17], color=INK, linewidth=fs.LW_DATA, solid_capstyle="butt", zorder=3)
        _row_label(ax_b, 0, "Offshore wind, life cycle",
                   f"IPCC AR5 median · {d.lifecycle_g:g} g CO$_2$-eq kWh$^{{-1}}$")
        ax_b.annotate(f"{d.lifecycle:.1f}   (literature min–max {lo:.1f}–{hi:.1f})", (hi, 0),
                      xytext=(5, 0), textcoords="offset points", ha="left", va="center_baseline",
                      fontsize=FS_NOTE, color=INK)
        ax_b.set_xlabel(f"Life-cycle greenhouse-gas emissions ({UNIT_CO2EQ})", fontsize=FS_AXIS)

        fig.canvas.draw()
        fs.panel_heading(fig, ax_a, "(a)", "Avoided operational grid CO₂",
                         "Net energy × 2023 grid factor; grey: context conventions, not bounds")
        fs.panel_heading(fig, ax_b, "(b)", "Offshore-wind life-cycle greenhouse gases",
                         "CO₂-equivalent; reported separately, not subtracted from (a)")
    return fig


def layout_problems(fig) -> list[str]:
    return fs.layout_problems(fig) + fs.print_problems(fig)


def caption(d: Co2Data) -> str:
    g = {r.label: r for r in d.grid}
    p = next(r for r in d.grid if r.primary)
    lo, hi = d.lifecycle_range
    glo, ghi = d.lifecycle_g_range
    return (
        f"**Figure 7.** Avoided operational grid CO₂ and life-cycle greenhouse-gas emissions per "
        f"installed megawatt for the Gulf of Saros estimate. (a) Net energy yield "
        f"({d.energy_mwh_per_mw:,.1f} MWh MW⁻¹ yr⁻¹) multiplied by each 2023 grid emission factor "
        f"published by the Ministry of Energy and Natural Resources. The primary convention is the "
        f"combined margin for wind and solar generation (UNFCCC CDM Tool 07; "
        f"{p.value:,.1f} t CO₂ MW⁻¹ yr⁻¹). The operating margin "
        f"({g['Operating margin'].value:,.0f}), build margin ({g['Build margin'].value:,.0f}) and "
        f"generation average ({g['Generation average'].value:,.0f} t CO₂ MW⁻¹ yr⁻¹) are alternative "
        f"accounting conventions that answer different questions about which generation is "
        f"displaced; they are shown for context and are not uncertainty bounds of the primary "
        f"value. All four are CO₂-only factors for a static 2023 grid, not forecasts of future "
        f"displacement. The 90% confidence interval of the primary value that follows from the "
        f"sampling uncertainty of the 11-year energy mean alone is "
        f"{d.primary_ci[0]:,.0f}–{d.primary_ci[1]:,.0f} t CO₂ MW⁻¹ yr⁻¹; it excludes factor, "
        f"wind-resource and loss uncertainty. The generation average in CO₂-equivalent "
        f"({d.gen_avg_co2eq:,.0f} t CO₂-eq MW⁻¹ yr⁻¹) is a different unit and is not plotted. "
        f"(b) Offshore-wind life-cycle greenhouse-gas emissions in CO₂-equivalent for the same "
        f"energy, using the IPCC AR5 median intensity ({d.lifecycle_g:g} g CO₂-eq kWh⁻¹; "
        f"{d.lifecycle:.1f} t CO₂-eq MW⁻¹ yr⁻¹). The line spans the minimum and maximum of the "
        f"literature values compiled in AR5 ({glo:g}–{ghi:g} g CO₂-eq kWh⁻¹; {lo:.1f}–{hi:.1f} "
        f"t CO₂-eq MW⁻¹ yr⁻¹), a range of published studies rather than a statistical interval. "
        f"These are literature values for other sites, not a Saros-specific life-cycle "
        f"assessment. Life-cycle emissions are reported separately and are not subtracted from "
        f"(a), because they cover other gases and a cradle-to-grave boundary, whereas the grid "
        f"factors cover combustion CO₂ only. Both panels share one numerical scale so that "
        f"magnitudes can be compared; the units differ.\n"
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
    print("; ".join(f"{r.label} {r.value:.1f}" for r in d.grid) + f"; life cycle {d.lifecycle:.1f}")
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
