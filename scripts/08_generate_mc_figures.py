"""
08 — Monte Carlo & scenario figures (Saros Bay)
================================================
Generates figures/F_monte_carlo.png — a 4-panel publication figure:
  (a) specific yield (GWh/yr/MW) distribution with P10/P50/P90
  (b) net capacity factor distribution
  (c) avoided CO2 (tCO2/yr/MW) distribution
  (d) farm AEP by scenario with P10–P90 error bars + avoided-CO2 labels

Inputs : results/monte_carlo_samples.npz, results/monte_carlo_results.json,
         results/comparison_results.json
Output : figures/F_monte_carlo.png

Run after 06_run_monte_carlo.py and 07_compare_with_grid.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config.site import RESULTS_DIR, FIGURES_DIR


def _annotate_pctls(ax, data, fmt, mid_color="red"):
    p10, p50, p90 = np.percentile(data, [10, 50, 90])
    for v, lab, col, mid in [(p10, "P10", "#888", False),
                             (p50, "P50", mid_color, True),
                             (p90, "P90", "#888", False)]:
        ax.axvline(v, color=col, linestyle="-" if mid else "--",
                   linewidth=1.8 if mid else 1.2)
        ax.text(v, ax.get_ylim()[1] * 0.92, f"{lab}\n{v:{fmt}}",
                ha="center", fontsize=9, color=col,
                fontweight="bold" if mid else "normal")


def main() -> int:
    npz = RESULTS_DIR / "monte_carlo_samples.npz"
    if not npz.exists():
        print(f"✗ {npz} not found. Run 06_run_monte_carlo.py first.")
        return 1
    s = np.load(npz)
    aep_mw = s["aep_per_mw"]
    cf = s["cf_net"] * 100
    avoid_mw = s["avoided_per_mw"]
    comp = json.loads((RESULTS_DIR / "comparison_results.json").read_text())

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax = axes[0, 0]
    ax.hist(aep_mw, bins=60, color="#5B9BD5", edgecolor="white", linewidth=0.3, alpha=0.85)
    _annotate_pctls(ax, aep_mw, ".2f")
    ax.set_xlabel("Net AEP per MW (GWh/yr/MW)"); ax.set_ylabel("Frequency")
    ax.set_title("(a) Specific yield distribution (10,000 MC runs)", fontweight="bold")

    ax = axes[0, 1]
    ax.hist(cf, bins=60, color="#70AD47", edgecolor="white", linewidth=0.3, alpha=0.85)
    _annotate_pctls(ax, cf, ".1f")
    ax.set_xlabel("Net capacity factor (%)"); ax.set_ylabel("Frequency")
    ax.set_title("(b) Capacity factor distribution", fontweight="bold")

    ax = axes[1, 0]
    ax.hist(avoid_mw, bins=60, color="#C55A11", edgecolor="white", linewidth=0.3, alpha=0.85)
    _annotate_pctls(ax, avoid_mw, ".0f", mid_color="darkred")
    ax.set_xlabel("Avoided CO$_2$ (tCO$_2$/yr/MW)"); ax.set_ylabel("Frequency")
    ax.set_title("(c) Avoided CO$_2$ distribution", fontweight="bold")

    ax = axes[1, 1]
    scen = comp["scenarios"]
    names = [f"{r['name'].replace('_',' ')}\n{r['installed_mw']:.0f} MW" for r in scen]
    aep_p50 = [r["farm_aep_twh"]["p50"] for r in scen]
    lo = [r["farm_aep_twh"]["p50"] - r["farm_aep_twh"]["p10"] for r in scen]
    hi = [r["farm_aep_twh"]["p90"] - r["farm_aep_twh"]["p50"] for r in scen]
    x = np.arange(len(scen))
    ax.bar(x, aep_p50, yerr=[lo, hi], capsize=5, color="#5B9BD5",
           edgecolor="#1f4e79", linewidth=1, error_kw={"linewidth": 1.5})
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=9)
    ax.set_ylabel("Annual energy production (TWh/yr)")
    ax.set_title("(d) Farm AEP by scenario (P10–P50–P90)", fontweight="bold")
    for i, r in enumerate(scen):
        ax.text(i, r["farm_aep_twh"]["p90"] + 0.1,
                f"{r['avoided_co2_mt']['p50']:.2f}\nMt CO$_2$",
                ha="center", fontsize=8, color="#C55A11", fontweight="bold")
    ax.set_ylim(0, max(aep_p50) * 1.25)

    plt.suptitle("Saros Bay OWF — Energy Production & Avoided Emissions under Uncertainty",
                 fontsize=14, fontweight="bold", y=1.00)
    plt.tight_layout()
    out = FIGURES_DIR / "F_monte_carlo.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"✓ Saved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
