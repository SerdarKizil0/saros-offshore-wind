"""
09 — Additional figures: workflow, wind rose, comparison, equivalents
======================================================================
Generates the remaining publication figures:
  F2_workflow.png    — methodological workflow diagram
  F3_windrose.png    — wind rose at 105 m
  F7_comparison.png  — offshore vs conventional (fuel-resolved) + avoided
  F8_equivalents.png — household and car equivalents by scenario

Inputs : data/processed/wind_hub_105m.parquet,
         results/monte_carlo_samples.npz
Output : figures/F2..F8 PNGs

Constants for tangible equivalents:
  Household: 3036 kWh/yr (TEİAŞ, 4-person family)
  Car:       2.0 tCO2/yr (avg passenger vehicle)

Fuel-resolved conventional scenario uses official ETKB/EVÇED 2023
fuel emission factors (g/kWh): natural gas 405, imported coal 803,
lignite 1133, weighted by an approximate fossil-thermal generation mix.
The fuel-displacement total is reported alongside the official
combined-margin avoided emission for transparency.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch

from config.site import DATA_DIR, RESULTS_DIR, FIGURES_DIR
from config.turbine import SCENARIOS

# Constants
HOUSEHOLD_KWH = 3036
CAR_CO2_TON = 2.0
EF_FUEL = {"Natural gas": 405, "Imported coal": 803, "Lignite": 1133}
FOSSIL_SHARE = {"Natural gas": 0.368, "Imported coal": 0.333, "Lignite": 0.299}
LCA_CO2 = 11.0
S3_MW = 997.5


def fig_workflow():
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_xlim(0, 10); ax.set_ylim(0, 16); ax.axis("off")
    c_data, c_proc, c_model, c_out = "#cfe2f3", "#d9ead3", "#fff2cc", "#f4cccc"

    def box(x, y, w, h, text, color, fs=10):
        ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                     boxstyle="round,pad=0.1", facecolor=color,
                     edgecolor="#333", linewidth=1.3))
        ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight="bold")

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                     mutation_scale=18, color="#444", linewidth=1.5))

    box(5,15,5,1.0,"ERA5 Reanalysis\n11 yr hourly, 10 m & 100 m winds\n(2014–2024, 96 432 h)",c_data)
    arrow(5,14.5,5,13.9)
    box(5,13.4,5,1.0,"Wind speed @ 100 m\n$U=\\sqrt{u^2+v^2}$  •  centroid grid cell",c_proc)
    arrow(5,12.9,5,12.3)
    box(5,11.8,5,1.0,"Hub-height extrapolation → 105 m\nPower law, measured α = 0.149",c_proc)
    arrow(5,11.3,5,10.7)
    box(5,10.2,5,1.0,"Weibull fit (MLE)\nk = 2.04, c = 8.08 m/s  •  R² = 0.998",c_model)
    arrow(5,9.7,5,9.1)
    box(5,8.6,5,1.0,"AEP — power-curve convolution\nVestas V164-9.5 MW  •  + losses",c_model)
    arrow(5,8.1,5,7.5)
    box(5,7.0,5,1.0,"Net AEP\n2.62 GWh/yr/MW  •  CF 29.9%",c_out)
    arrow(5,6.5,3,5.9); arrow(5,6.5,7,5.9)
    box(3,5.4,3.4,1.1,"Türkiye grid EF\n624 g/kWh\n(combined margin)",c_data,9)
    box(7,5.4,3.4,1.1,"Offshore wind LCA\n11 g/kWh\n(Bonou 2016)",c_data,9)
    arrow(3,4.85,5,4.2); arrow(7,4.85,5,4.2)
    box(5,3.7,5,1.0,"Avoided CO$_2$\n1525 tCO$_2$/yr/MW",c_out)
    arrow(5,3.2,5,2.6)
    box(5,2.1,5.5,1.0,"Monte Carlo (10 000 iter, 7 inputs)\nP10 / P50 / P90 distributions",c_model)
    arrow(5,1.6,5,1.0)
    box(5,0.5,5.5,0.8,"Scenarios S1–S4  +  national context",c_out)

    leg = [Patch(facecolor=c, edgecolor="#333", label=l) for c, l in
           [(c_data,"Input data"),(c_proc,"Processing"),(c_model,"Modelling"),(c_out,"Output")]]
    ax.legend(handles=leg, loc="upper left", fontsize=9, framealpha=0.9)
    ax.set_title("Methodological Workflow — Saros Bay OWF Assessment",
                 fontsize=14, fontweight="bold", pad=10)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR/"F2_workflow.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def fig_windrose(df):
    ws, wd = df["U_hub"].values, df["wdir"].values
    from windrose import WindroseAxes
    fig = plt.figure(figsize=(8, 8))
    ax = WindroseAxes.from_ax(fig=fig)
    ax.bar(wd, ws, normed=True, opening=0.85, edgecolor="white",
           bins=[0,3.5,7,10.5,14,18,25], cmap=plt.cm.viridis)
    ax.set_legend(title="Wind speed (m/s)", loc="lower left",
                  bbox_to_anchor=(-0.1,-0.05), fontsize=9)
    ax.set_title("Wind rose at 105 m hub height — Saros Bay (2014–2024)",
                 fontsize=13, fontweight="bold", pad=20)
    plt.savefig(FIGURES_DIR/"F3_windrose.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def fig_comparison(aep_mw, avoid_mw):
    s3_aep_twh = np.median(aep_mw)*S3_MW/1000
    s3_kwh = s3_aep_twh*1e9
    conv = {f: s3_kwh*FOSSIL_SHARE[f]*EF_FUEL[f]/1e6 for f in EF_FUEL}
    conv_total = sum(conv.values())
    wind_co2 = s3_kwh*LCA_CO2/1e6
    avoided_cm = np.median(avoid_mw)*S3_MW/1e6
    avoided_fossil = (conv_total - wind_co2)/1e6

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    ax = axes[0]
    colors = {"Natural gas":"#f4a259","Imported coal":"#5d4037","Lignite":"#8d6e63"}
    bottom = 0
    for fuel in ["Natural gas","Imported coal","Lignite"]:
        v = conv[fuel]/1e6
        ax.bar(0, v, bottom=bottom, color=colors[fuel], width=0.55,
               edgecolor="white", linewidth=1, label=fuel)
        ax.text(0, bottom+v/2, f"{fuel}\n{v:.2f} Mt", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")
        bottom += v
    ax.bar(1, wind_co2/1e6, color="#2E7D32", width=0.55, edgecolor="white",
           linewidth=1, label="Offshore wind (LCA)")
    ax.text(1, wind_co2/1e6+0.05, f"Offshore wind\n{wind_co2/1e6:.3f} Mt",
            ha="center", va="bottom", fontsize=9, color="#2E7D32", fontweight="bold")
    ax.set_xticks([0,1]); ax.set_xticklabels(["Conventional\n(fossil-thermal mix)","Offshore wind"], fontsize=11)
    ax.set_ylabel("Annual CO$_2$ emissions (Mt CO$_2$/yr)", fontsize=11)
    ax.set_title("(a) Carbon burden of producing 2.62 TWh/yr", fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(0, conv_total/1e6*1.15)

    ax = axes[1]
    methods = ["Combined margin\n(official, 624 g/kWh)","Fossil-thermal\ndisplacement"]
    vals = [avoided_cm, avoided_fossil]
    errs = [[avoided_cm-np.percentile(avoid_mw,10)*S3_MW/1e6],
            [np.percentile(avoid_mw,90)*S3_MW/1e6-avoided_cm]]
    ax.bar(methods, vals, color=["#C55A11","#8d6e63"], width=0.5,
           edgecolor="black", linewidth=1)
    ax.errorbar(0, avoided_cm, yerr=errs, fmt="none", ecolor="black", capsize=6, lw=1.5)
    for i, v in enumerate(vals):
        ax.text(i, v+0.03, f"{v:.2f} Mt/yr", ha="center", fontsize=11, fontweight="bold")
    ax.set_ylabel("Avoided CO$_2$ (Mt CO$_2$/yr)", fontsize=11)
    ax.set_title("(b) Avoided emissions: official vs fossil-displacement", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(vals)*1.25)

    plt.suptitle("Saros Bay OWF (~1 GW) — Offshore Wind versus Conventional Generation",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR/"F7_comparison.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def fig_equivalents(aep_mw, avoid_mw):
    scen = [(s.name.replace("_"," "), s.installed_mw) for s in SCENARIOS]
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax = axes[0]
    households = [np.median(aep_mw)*mw/1000*1e9/HOUSEHOLD_KWH/1e6 for _, mw in scen]
    ax.bar([n for n,_ in scen], households, color="#5B9BD5",
           edgecolor="#1f4e79", linewidth=1, width=0.6)
    for i, v in enumerate(households):
        ax.text(i, v+0.02, f"{v:.2f}M\nhouseholds", ha="center", fontsize=9, fontweight="bold")
    ax.set_ylabel("Households powered (millions)", fontsize=11)
    ax.set_title("(a) Equivalent households supplied", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(households)*1.2)
    ax.text(0.02,0.97,f"Basis: {HOUSEHOLD_KWH:,} kWh/household/yr\n(TEİAŞ, 4-person family)",
            transform=ax.transAxes, fontsize=8, va="top", style="italic",
            bbox=dict(facecolor="#f0f0f0", edgecolor="none"))

    ax = axes[1]
    cars = [np.median(avoid_mw)*mw/CAR_CO2_TON/1e6 for _, mw in scen]
    ax.bar([n for n,_ in scen], cars, color="#C55A11",
           edgecolor="#8B3A0F", linewidth=1, width=0.6)
    for i, v in enumerate(cars):
        ax.text(i, v+0.01, f"{v:.2f}M\ncars", ha="center", fontsize=9, fontweight="bold")
    ax.set_ylabel("Cars removed equivalent (millions)", fontsize=11)
    ax.set_title("(b) Avoided CO$_2$ in car-equivalents", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(cars)*1.2)
    ax.text(0.02,0.97,f"Basis: {CAR_CO2_TON} tCO$_2$/car/yr\n(avg passenger vehicle)\nCombined-margin EF",
            transform=ax.transAxes, fontsize=8, va="top", style="italic",
            bbox=dict(facecolor="#f0f0f0", edgecolor="none"))

    plt.suptitle("Saros Bay OWF — Tangible Equivalents by Deployment Scenario",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR/"F8_equivalents.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def main() -> int:
    df = pd.read_parquet(DATA_DIR/"processed"/"wind_hub_105m.parquet")
    s = np.load(RESULTS_DIR/"monte_carlo_samples.npz")
    aep_mw, avoid_mw = s["aep_per_mw"], s["avoided_per_mw"]

    fig_workflow();      print("✓ F2_workflow.png")
    fig_windrose(df);    print("✓ F3_windrose.png")
    fig_comparison(aep_mw, avoid_mw);  print("✓ F7_comparison.png")
    fig_equivalents(aep_mw, avoid_mw); print("✓ F8_equivalents.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
