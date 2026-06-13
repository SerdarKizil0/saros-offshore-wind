"""
Wind resource figures (static + interactive)
=============================================
Generates two deliverables from data/processed/wind_hub_105m.parquet:

  figures/F_wind_resource.png            — 4-panel static figure (publication)
  figures/wind_resource_interactive.html — interactive Plotly explorer

Static panels: (a) histogram + Weibull PDF + power curve overlay,
(b) Q-Q plot, (c) monthly climatology, (d) inter-annual variability.

Run after 04_fit_weibull_aep.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

from config.site import SITE, DATA_DIR, FIGURES_DIR
from config.turbine import POWER_CURVE_MS_KW

INPUT = DATA_DIR / "processed" / "wind_hub_105m.parquet"


def make_static(df: pd.DataFrame, k: float, c: float) -> Path:
    u = df["U_hub"].values
    u_pos = u[u > 0]
    pc_ms = [p[0] for p in POWER_CURVE_MS_KW]
    pc_kw = [p[1] for p in POWER_CURVE_MS_KW]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # (a) hist + weibull + power curve
    ax = axes[0, 0]
    bins = np.arange(0, 28, 0.5)
    ax.hist(u, bins=bins, density=True, alpha=0.55, color="#5B9BD5",
            edgecolor="white", linewidth=0.4,
            label=f"ERA5 data ({len(u):,} h)")
    x = np.linspace(0.01, 27, 400)
    ax.plot(x, stats.weibull_min.pdf(x, k, 0, c), "r-", linewidth=2.4,
            label=f"Weibull (k={k:.2f}, c={c:.2f})")
    ax.set_xlabel("Wind speed @ 105 m (m/s)")
    ax.set_ylabel("Probability density")
    ax.set_title("(a) Wind speed distribution & Weibull fit", fontweight="bold")
    ax2 = ax.twinx()
    ax2.plot(pc_ms, np.array(pc_kw) / 1000, color="#2E7D32", linewidth=2,
             linestyle="--", alpha=0.8, label="Power curve")
    ax2.set_ylabel("Turbine power (MW)", color="#2E7D32")
    ax2.tick_params(axis="y", labelcolor="#2E7D32")
    ax2.set_ylim(0, 10.5)
    ax.set_xlim(0, 27)
    l1, lb1 = ax.get_legend_handles_labels()
    l2, lb2 = ax2.get_legend_handles_labels()
    ax.legend(l1 + l2, lb1 + lb2, loc="upper right", fontsize=9)

    # (b) Q-Q
    ax = axes[0, 1]
    sorted_u = np.sort(u_pos)
    theo_q = stats.weibull_min.ppf(np.linspace(0.001, 0.999, len(sorted_u)), k, 0, c)
    idx = np.linspace(0, len(sorted_u) - 1, 2000).astype(int)
    ax.scatter(theo_q[idx], sorted_u[idx], s=6, alpha=0.4, color="#5B9BD5")
    ax.plot([0, 26], [0, 26], "r-", linewidth=1.5, label="1:1 line")
    ax.set_xlabel("Weibull theoretical quantile (m/s)")
    ax.set_ylabel("Empirical quantile (m/s)")
    ax.set_title("(b) Q–Q plot (goodness of fit)", fontweight="bold")
    ax.legend(fontsize=9); ax.set_xlim(0, 26); ax.set_ylim(0, 26)

    # (c) monthly
    ax = axes[1, 0]
    monthly = df["U_hub"].groupby(df.index.month).mean()
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    colors = ["#1f4e79" if v >= 7.5 else "#5B9BD5" if v >= 6.5 else "#a9cce3"
              for v in monthly.values]
    ax.bar(range(1, 13), monthly.values, color=colors, edgecolor="white")
    ax.axhline(u.mean(), color="red", linestyle="--", linewidth=1.3,
               label=f"Annual mean ({u.mean():.2f} m/s)")
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(months, fontsize=9)
    ax.set_ylabel("Mean wind speed (m/s)")
    ax.set_title("(c) Monthly climatology (2014–2024)", fontweight="bold")
    ax.legend(fontsize=9)

    # (d) inter-annual
    ax = axes[1, 1]
    annual = df["U_hub"].groupby(df.index.year).mean()
    ax.plot(annual.index, annual.values, "o-", color="#1f4e79",
            linewidth=2, markersize=7)
    ax.axhline(annual.mean(), color="red", linestyle="--", linewidth=1.3,
               label=f"11-yr mean ({annual.mean():.2f} m/s)")
    cov = annual.std() / annual.mean() * 100
    ax.fill_between(annual.index, annual.mean() - annual.std(),
                    annual.mean() + annual.std(), alpha=0.15, color="red",
                    label=f"±1σ (CoV {cov:.1f}%)")
    ax.set_xlabel("Year"); ax.set_ylabel("Annual mean wind speed (m/s)")
    ax.set_title("(d) Inter-annual variability", fontweight="bold")
    ax.legend(fontsize=9); ax.set_ylim(6, 8)

    plt.suptitle("Saros Bay — Wind Resource Characterization at 105 m Hub Height",
                 fontsize=14, fontweight="bold", y=1.00)
    plt.tight_layout()
    out = FIGURES_DIR / "F_wind_resource.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    return out


def make_interactive(df: pd.DataFrame, k: float, c: float) -> Path:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    u = df["U_hub"].values
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Distribution + Weibull fit", "Monthly box plot",
                        "Full 11-year time series (daily mean)", None),
        specs=[[{}, {}], [{"colspan": 2}, None]],
        vertical_spacing=0.12, horizontal_spacing=0.10)

    hist, edges = np.histogram(u, bins=np.arange(0, 28, 0.5), density=True)
    centers = (edges[:-1] + edges[1:]) / 2
    fig.add_trace(go.Bar(x=centers, y=hist, name="ERA5 data",
        marker_color="#5B9BD5", opacity=0.6), row=1, col=1)
    xx = np.linspace(0.01, 27, 300)
    fig.add_trace(go.Scatter(x=xx, y=stats.weibull_min.pdf(xx, k, 0, c),
        name=f"Weibull k={k:.2f} c={c:.2f}", line=dict(color="red", width=3)),
        row=1, col=1)

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for m in range(1, 13):
        vals = df.loc[df.index.month == m, "U_hub"].values[::4]
        fig.add_trace(go.Box(y=vals, name=months[m - 1],
            marker_color="#1f4e79", showlegend=False, boxpoints=False),
            row=1, col=2)

    daily = df["U_hub"].resample("D").mean()
    fig.add_trace(go.Scatter(x=daily.index, y=daily.values, name="Daily mean",
        line=dict(color="#2E7D32", width=0.6), showlegend=False),
        row=2, col=1)
    annual = df["U_hub"].groupby(df.index.year).mean()
    ann_x = pd.to_datetime([f"{y}-07-01" for y in annual.index])
    fig.add_trace(go.Scatter(x=ann_x, y=annual.values, name="Annual mean",
        mode="markers+lines", marker=dict(color="red", size=9),
        line=dict(color="red", width=2)), row=2, col=1)

    fig.update_xaxes(title_text="Wind speed (m/s)", row=1, col=1)
    fig.update_yaxes(title_text="Density", row=1, col=1)
    fig.update_yaxes(title_text="Wind speed (m/s)", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Wind speed (m/s)", row=2, col=1)
    fig.update_layout(height=800, width=1300, template="plotly_white",
        title_text="Saros Bay Wind Resource — Interactive Explorer (105 m hub)",
        title_font_size=18,
        legend=dict(orientation="h", yanchor="bottom", y=1.06,
                    xanchor="right", x=1))

    out = FIGURES_DIR / "wind_resource_interactive.html"
    fig.write_html(out, include_plotlyjs="cdn")
    return out


def main() -> int:
    if not INPUT.exists():
        print(f"✗ Input not found: {INPUT}. Run 03_process_era5.py first.")
        return 1
    df = pd.read_parquet(INPUT)
    u_pos = df["U_hub"].values[df["U_hub"].values > 0]
    k, _, c = stats.weibull_min.fit(u_pos, floc=0)
    print(f"Weibull k={k:.4f}, c={c:.4f}")

    p1 = make_static(df, k, c)
    print(f"✓ Static figure:      {p1}")
    p2 = make_interactive(df, k, c)
    print(f"✓ Interactive figure: {p2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
