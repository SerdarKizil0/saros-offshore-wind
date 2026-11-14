"""
11 — Build the manuscript sections and tables from results/revised/ (Phase 5B-1)
================================================================================
Single source of truth for every number in the Study Area, Methods and
Results sections and in the tables.

  manuscript/src/02_study_area.md   ->  manuscript/02_study_area.md
  manuscript/src/03_methodology.md  ->  manuscript/03_methodology.md
  manuscript/src/04_results.md      ->  manuscript/04_results.md
  (generated)                       ->  manuscript/tables.md
  (generated)                       ->  manuscript/supplementary_tables.md

The prose lives in manuscript/src/. Numbers are written there as placeholders

    {{file:key.path|format}}        e.g. {{energy_yield:net.gwh_per_mw|.4f}}

`file` is a JSON file of results/revised/ (without .json) or `d` for the small
set of derived values computed in `derived()` below (each derived value is a
documented transformation of result or input files; none is typed by hand).
`format` is a Python format spec with optional prefixes: `pct` (x100), `abs`
(absolute value), `sp` (space as thousands separator). A leading `+` gives a
signed number. Negative signs are written as the Unicode minus.

Edit the files in manuscript/src/, never the generated files, then run:

    python scripts/11_build_manuscript_sections.py          # write
    python scripts/11_build_manuscript_sections.py --check  # verify up to date

This script reads results only; it never changes results/revised/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from config.site import SITE, SAROS_POLYGON_LONLAT
from config.turbine import TURBINE, POWER_CURVE_MS_KW, POWER_CURVE_ID
from config.wind_data import PRIMARY

REV = ROOT / "results" / "revised"
MAN = ROOT / "manuscript"
SRC = MAN / "src"
SECTIONS = ["02_study_area.md", "03_methodology.md", "04_results.md"]
GENERATED_NOTE = ("<!-- GENERATED FILE - do not edit. Source: manuscript/src/{name}. Numbers come from "
                  "results/revised/. Rebuild with: python scripts/11_build_manuscript_sections.py -->\n\n")
TOKEN = re.compile(r"\{\{\s*([A-Za-z0-9_]+):([^{}|]+?)\s*(?:\|\s*([^{}]+?)\s*)?\}\}")
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


# ------------------------------------------------------------------ loading
def load_results() -> dict:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(REV.glob("*.json"))}


def polygon_area_utm_km2() -> float:
    """Area of the official polygon in WGS 84 / UTM zone 35N (EPSG:32635), shoelace formula."""
    from pyproj import Transformer
    tr = Transformer.from_crs("EPSG:4326", "EPSG:32635", always_xy=True)
    xs, ys = tr.transform([p[0] for p in SAROS_POLYGON_LONLAT], [p[1] for p in SAROS_POLYGON_LONLAT])
    n = len(xs)
    return abs(sum(xs[i] * ys[(i + 1) % n] - xs[(i + 1) % n] * ys[i] for i in range(n))) / 2.0 / 1e6


def derived(R: dict) -> dict:
    """Derived values: documented transformations of result and input files (nothing typed by hand)."""
    ann = pd.read_csv(REV / "annual_energy.csv").set_index("year")
    y = ann["net_gwh_per_mw_8766h"]
    mean = R["energy_yield"]["net"]["gwh_per_mw"]
    wr, ey, ss = R["wind_resource"], R["energy_yield"], R["site_screening"]
    mon = {int(k): v for k, v in wr["monthly_mean_U_hub_ms"].items()}
    au = {int(k): v for k, v in wr["annual_mean_U_hub_ms"].items()}
    alpha = wr["shear_exponent_from_era5_10m_100m"]["mean"]
    cases = R["wind_speed_sensitivity"]["cases"]
    key = {0.90: "m10", 0.95: "m5", 1.00: "ref", 1.05: "p5", 1.10: "p10"}
    speed = {key[round(c["speed_factor"], 2)]: c for c in cases if "GWA" not in c["case"]}
    s3 = next(s for s in R["scenarios"]["scenarios"] if s["name"] == "S3")
    s3d = next(s for s in ss["active_scenarios_density"] if s["name"] == "S3")
    deep = ss["bathymetry"]["share_deeper_than_pct"]
    rank = y.rank(method="min").astype(int)
    man = json.loads((PRIMARY.path.parent / "MANIFEST.json").read_text())
    retrieved = dt.datetime.fromisoformat(man["retrieved_utc"])
    nodes = R["node_sensitivity"]["nodes"]
    months_sorted = sorted(mon, key=mon.get)
    return {
        "polygon_area_km2": polygon_area_utm_km2(),
        "n_vertices": SITE.n_vertices, "centroid_lat": SITE.centroid_lat, "centroid_lon": SITE.centroid_lon,
        "share_shallower_10m_pct": 100.0 - deep["10"], "share_shallower_50m_pct": 100.0 - deep["50"],
        "alpha_effect_vs_0p10_pct": ((1.05 ** alpha) / (1.05 ** 0.10) - 1) * 100,
        "n_years": int(len(ann)), "n_leap_years": int(ann["leap"].sum()),
        "min_year_rel_pct": (y.min() / mean - 1) * 100, "max_year_rel_pct": (y.max() / mean - 1) * 100,
        "second_lowest_year": int(y.sort_values().index[1]),
        "second_lowest_net": float(y.sort_values().iloc[1]),
        "second_lowest_rel_pct": (float(y.sort_values().iloc[1]) / mean - 1) * 100,
        "y2014_net": float(y[2014]), "y2014_rel_pct": (float(y[2014]) / mean - 1) * 100,
        "y2014_rank_from_lowest": int(rank[2014]),
        "annual_U_min_year": min(au, key=au.get), "annual_U_min": min(au.values()),
        "annual_U_max_year": max(au, key=au.get), "annual_U_max": max(au.values()),
        "month_max_name": MONTHS[months_sorted[-1] - 1], "month_max": mon[months_sorted[-1]],
        "month_min_name": MONTHS[months_sorted[0] - 1], "month_min": mon[months_sorted[0]],
        "speed": speed,
        "elasticity_plus5": speed["p5"]["aep_change_vs_baseline_pct"] / 5.0,
        "s3": s3, "s3_density": s3d,
        "s3_turbines_times_rating_mw": s3["n_turbines"] * TURBINE.rated_power_mw,
        "retrieval_date": f"{retrieved.day} {MONTHS[retrieved.month - 1]} {retrieved.year}",
        "curve_n_points_oedb": sum(1 for v, _ in POWER_CURVE_MS_KW if v <= 24.5),
        "curve_max_speed_oedb": max(v for v, _ in POWER_CURVE_MS_KW if v <= 24.5),
        "node_share_sum_pct": sum(n["polygon_share_nearest_to_node_pct"] for n in nodes.values()),
        "turbine": {"rated_mw": TURBINE.rated_power_mw, "rotor_m": TURBINE.rotor_diameter_m,
                    "hub_m": TURBINE.hub_height_m, "cut_in": TURBINE.cut_in_ms, "rated_ms": TURBINE.rated_ms,
                    "cut_out": TURBINE.cut_out_ms, "curve_id": POWER_CURVE_ID},
    }


# --------------------------------------------------------------- formatting
def fmt(value, spec: str | None) -> str:
    if spec is None:
        return str(value)
    if spec == "en":                               # text label with an en dash, e.g. a period "1999-2009"
        return str(value).replace("-", "–")
    flags = set()
    while True:
        for f in ("abs", "pct", "sp"):
            if spec.startswith(f):
                flags.add(f)
                spec = spec[len(f):]
                break
        else:
            break
    v = float(value)
    if "pct" in flags:
        v *= 100.0
    if "abs" in flags:
        v = abs(v)
    if spec.endswith("d"):
        v = int(round(v))
    if "sp" in flags:
        sign = "+" if spec.startswith("+") else ""
        s = format(v, sign + "," + spec.lstrip("+")).replace(",", " ")
    else:
        s = format(v, spec)
    return s.replace("-", "−")


def lookup(R: dict, D: dict, src: str, path: str):
    node = D if src == "d" else R[src]
    for part in path.strip().split("."):
        if isinstance(node, list):
            node = node[int(part)]
        else:
            node = node[part]
    return node


def render(text: str, R: dict, D: dict) -> str:
    def sub(m: re.Match) -> str:
        try:
            return fmt(lookup(R, D, m.group(1), m.group(2)), m.group(3))
        except (KeyError, IndexError, ValueError, TypeError) as e:
            raise KeyError(f"cannot resolve placeholder {m.group(0)}: {e!r}") from e
    out = TOKEN.sub(sub, text)
    left = re.search(r"\{\{\s*[A-Za-z0-9_]+\s*:", out)        # LaTeX may legitimately contain '}}'
    if left:
        raise ValueError(f"unresolved placeholder left in the text near: {out[left.start():left.start() + 60]!r}")
    return out


def reflow(text: str, width: int = 78) -> str:
    """Re-wrap prose paragraphs and list items after substitution. Headings, equations, tables and
    comments are left as they are."""
    import textwrap
    keep = "\u2060"                                  # marks a space that must not become a line break

    def wrap(t: str, **kw) -> str:
        t = re.sub(r"(\d) %", r"\1" + keep + "%", " ".join(t.split()))
        return textwrap.fill(t, width=width, break_long_words=False, break_on_hyphens=False, **kw).replace(keep, " ")
    blocks = []
    for block in text.split("\n\n"):
        first = block.lstrip()
        if not first or first.startswith(("#", "$$", "|", "<!--")):
            blocks.append(block)
        elif first.startswith("- "):
            items = re.split(r"\n(?=- )", block.strip("\n"))
            blocks.append("\n".join(wrap(i[2:], initial_indent="- ", subsequent_indent="  ") for i in items))
        else:
            blocks.append(wrap(block))
    return "\n\n".join(blocks).rstrip("\n") + "\n"


# ------------------------------------------------------------------- tables
def table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def f(v, spec):
    return fmt(v, spec)


def rng(lo, hi, spec):
    return f"{fmt(lo, spec)}–{fmt(hi, spec)}"


def main_tables(R: dict, D: dict) -> str:
    ey, wr, s = R["energy_yield"], R["wind_resource"], R["interannual_and_sampling"]
    ci, var = s["sampling_ci_of_period_mean"], s["observed_interannual_variability"]
    t90 = ci["primary_t_interval_90"]
    a = wr["shear_exponent_from_era5_10m_100m"]
    parts = ["# Tables\n",
             "*Generated by `scripts/11_build_manuscript_sections.py` from `results/revised/`. Do not edit by "
             "hand. Supplementary tables are in `supplementary_tables.md`.*\n"]

    # ---- Table 1
    rows = [
        ["Record", f"{ey['period'].replace('-', '–')}; {D['n_years']} calendar years; "
                   f"{f(ey['normalisation_check']['n_hours'], 'spd')} hourly values", "Reanalysis output"],
        ["Mean wind speed at 100 m (m s⁻¹)", f(wr["U100"]["mean_ms"], ".2f"), "Reanalysis output"],
        ["Shear exponent α from the 10 m and 100 m levels", f(a["mean"], ".3f"), "Derived from reanalysis levels"],
        ["Mean / standard deviation / median wind speed at 105 m (m s⁻¹)",
         f"{f(wr['U_hub']['mean_ms'], '.2f')} / {f(wr['U_hub']['std_ms'], '.2f')} / "
         f"{f(wr['U_hub']['median_ms'], '.2f')}", "Reanalysis output, extrapolated"],
        ["Mean wind power density at 105 m (W m⁻², ρ = 1.225 kg m⁻³)",
         f(wr["U_hub"]["power_density_wm2_rho1225"], ".0f"), "Reanalysis output, extrapolated"],
        ["Gross capacity factor (%)", f(ey["gross_cf"], "pct.2f"), "Model result (power curve)"],
        ["Net capacity factor (%)", f(ey["net_cf"], "pct.2f"), "Model result (power curve, assumed losses)"],
        ["Gross / net energy per 9.5 MW turbine (GWh yr⁻¹)",
         f"{f(ey['gross']['gwh_per_turbine'], '.2f')} / {f(ey['net']['gwh_per_turbine'], '.2f')}",
         "Model result"],
        ["**Net specific yield (GWh MW⁻¹ yr⁻¹)**", f"**{f(ey['net']['gwh_per_mw'], '.3f')}**",
         "Model result (power curve, assumed losses)"],
        ["Net full-load hours (h yr⁻¹)", f(ey["net_full_load_hours"], "sp.0f"), "Model result"],
        ["90 % sampling interval of the mean net yield (GWh MW⁻¹ yr⁻¹)",
         f"{rng(*t90['net_gwh_per_mw'], '.3f')} (±{f(t90['half_width_rel_pct'], '.1f')} %)",
         f"Sampling statistic (t, {ci['n_years']} annual values)"],
        ["Coefficient of variation of annual net yield (%)", f(var["annual_net_cf_cov_pct"], ".1f"),
         "Interannual variability of reanalysis years"],
        ["Lowest / highest annual net yield (GWh MW⁻¹ yr⁻¹)",
         f"{f(var['min_net_gwh_per_mw'], '.3f')} ({var['min_year']}) / "
         f"{f(var['max_net_gwh_per_mw'], '.3f')} ({var['max_year']})",
         "Interannual variability of reanalysis years"],
    ]
    parts.append("## Table 1. Long-term wind resource and energy yield at the primary ERA5 node "
                 f"({PRIMARY.node_lat:.2f}° N, {PRIMARY.node_lon:.2f}° E), {ey['period'].replace('-', '–')}.\n\n"
                 + table(["Quantity", "Value", "Type of quantity"], rows)
                 + "\n\n*Reference turbine V164-9.5 MW with the third-party digitised OEDB V164/9500 power "
                   "curve (not manufacturer-certified). Nominal losses: wake "
                   f"{f(ey['losses_nominal']['wake'], 'pct.0f')} %, availability "
                   f"{f(ey['losses_nominal']['availability'], 'pct.0f')} %, electrical "
                   f"{f(ey['losses_nominal']['electrical'], 'pct.0f')} % (assumptions, not layout-validated). "
                   "The sampling interval is conditional on the reanalysis at this node; it is not a P90 "
                   "value and not a total uncertainty. No value is validated against offshore "
                   "measurements.*\n")

    # ---- Table 2
    idx = {c["category"]: c for c in R["sensitivity_index"]["categories"]}
    per, node, wpd = R["period_sensitivity"], R["node_sensitivity"], R["wind_product_discrepancy"]
    rw = per["rolling_windows"]["within_primary_period"]
    pvn = wpd["polygon_vs_primary_node"]["ratio_gwa_to_era5"]
    ls = R["loss_scenarios"]["scenarios"]
    p14 = per["periods"]["2014-2024"]
    rows = [
        ["1", "Sampling uncertainty of the 1994–2024 mean", "Probabilistic interval (the only one)",
         f"{rng(*t90['net_gwh_per_mw'], '.3f')} GWh MW⁻¹ yr⁻¹ (90 %); ±{f(t90['half_width_rel_pct'], '.1f')} %",
         "Conditional on ERA5 at the primary node"],
        ["2", "Interannual variability", "Observed spread of single reanalysis years",
         f"CoV {f(var['annual_net_cf_cov_pct'], '.1f')} %; {f(var['min_net_gwh_per_mw'], '.3f')} "
         f"({var['min_year']}) to {f(var['max_net_gwh_per_mw'], '.3f')} ({var['max_year']})",
         "Not an uncertainty of the mean"],
        ["3", "Period-selection sensitivity", "Sensitivity experiment",
         f"2014–2024 comparison period: {f(p14['energy_change_vs_reference_pct'], '+.1f')} %; rolling 11-year "
         f"windows within 1994–2024: {f(rw['lowest_window_rel_to_primary_mean_pct'], '+.1f')} % to "
         f"{f(rw['highest_window_rel_to_primary_mean_pct'], '+.1f')} %",
         "Same node and method; other reference periods"],
        ["4", "Grid-node sensitivity", "Sensitivity experiment",
         f"Western neighbour {f(node['nodes']['W']['energy_rel_to_primary_node_pct'], '+.1f')} %; eastern "
         f"neighbour {f(node['nodes']['E']['energy_rel_to_primary_node_pct'], '+.1f')} %",
         "Same period and method; neighbouring 0.25° cells; not averaged, not a bound"],
        ["5", "Wind-product discrepancy (ERA5 vs GWA 4.0)", "Inter-model disagreement",
         f"GWA/ERA5 mean-speed ratio {f(pvn['era5_1994-2024'], '.3f')} (ERA5 1994–2024) and "
         f"{f(pvn['era5_2008-2017_period_matched'], '.3f')} (ERA5 2008–2017, period-matched)",
         "Neither product validated offshore here; not a correction"],
        ["6", "Loss-assumption sensitivity", "Labelled assumption scenarios",
         f"Low losses {f(ls['low_loss']['rel_to_nominal_pct'], '+.1f')} %; high losses "
         f"{f(ls['high_loss']['rel_to_nominal_pct'], '+.1f')} %", "No site or layout evidence"],
    ]
    assert [c["category"] for c in R["sensitivity_index"]["categories"]] == list(idx)
    parts.append("## Table 2. Uncertainty and sensitivity categories of the primary estimate "
                 f"({f(ey['net']['gwh_per_mw'], '.3f')} GWh MW⁻¹ yr⁻¹). The categories are different kinds of "
                 "quantity and are not combined.\n\n"
                 + table(["No.", "Category", "Kind of quantity", "Headline result",
                          "Condition or meaning"], rows)
                 + "\n\n*Only category 1 is a probabilistic interval. Categories 3 to 6 are sensitivity "
                   "experiments, an inter-model comparison and assumption scenarios; they are not confidence "
                   "intervals, and the six categories must not be added or merged into a single interval.*\n")

    # ---- Table 3
    N = node["nodes"]
    order = ["W", "C", "E"]
    head = ["Quantity"] + [f"{N[k]['lat']:.2f}° N, {N[k]['lon']:.2f}° E" + (" (primary)" if N[k]["is_primary_node"]
                                                                          else "") for k in order]

    def row(label, fn):
        return [label] + [fn(N[k]) for k in order]

    def paired(n):
        if n["is_primary_node"]:
            return "—"
        p = n["paired_annual_rel_diff_vs_primary_node_pct"]
        return f"{f(p['mean'], '+.1f')} (sd {f(p['sd'], '.1f')}; {f(p['min'], '+.1f')} to {f(p['max'], '+.1f')})"

    rows = [
        row("ERA5 land–sea mask (land fraction of the cell)", lambda n: f(n["era5_land_sea_mask_fraction"], ".2f")),
        row("Class from the land–sea mask", lambda n: n["classification_from_era5_land_sea_mask"].split(" (")[0]
            .replace(" in ERA5", "")),
        row("Inside the candidate polygon", lambda n: "yes" if n["inside_polygon"] else "no"),
        row("Distance to the polygon boundary (km)", lambda n: f(n["distance_to_polygon_boundary_km"], ".1f")),
        row("Share of the polygon nearest to this node (%)",
            lambda n: f(n["polygon_share_nearest_to_node_pct"], ".1f")),
        row("Shear exponent α", lambda n: f(n["alpha_node"], ".3f")),
        row("Mean wind speed at 100 m (m s⁻¹)", lambda n: f(n["mean_U100_ms"], ".2f")),
        row("Mean wind speed at 105 m (m s⁻¹)", lambda n: f(n["mean_U_hub_ms"], ".2f")),
        row("Gross / net capacity factor (%)",
            lambda n: f"{f(n['gross_cf'], 'pct.2f')} / {f(n['net_cf'], 'pct.2f')}"),
        row("Net specific yield (GWh MW⁻¹ yr⁻¹)", lambda n: f(n["net_gwh_per_mw"], ".3f")),
        row("Difference from the primary node (%)",
            lambda n: "—" if n["is_primary_node"] else f(n["energy_rel_to_primary_node_pct"], "+.1f")),
        row("Paired annual difference, mean (sd; range) (%)", paired),
    ]
    parts.append(f"## Table 3. Grid-node sensitivity experiment: the three ERA5 nodes on the 40.50° N row, "
                 f"{node['assumptions']['period'].replace('-', '–')}, identical method.\n\n" + table(head, rows)
                 + "\n\n*Reanalysis output at grid nodes, not measurements. The nodes are not averaged and the "
                   "differences are not confidence bounds. The polygon shares are geometric descriptors and "
                   "are not used as weights.*\n")

    # ---- Table 4
    P = wpd["per_node_gwa_box_vs_era5"]
    pv = wpd["polygon_vs_primary_node"]
    g = pv["gwa4_polygon_mean_100m_ms"]
    rows = [
        ["Candidate polygon (GWA) vs primary node (ERA5)", f(g, ".2f"),
         f"{f(pv['era5_node_U100_ms']['1994-2024'], '.2f')} (1994–2024)", f(pvn["era5_1994-2024"], ".3f")],
        ["Candidate polygon (GWA) vs primary node (ERA5), period-matched", f(g, ".2f"),
         f"{f(pv['era5_node_U100_ms']['2008-2017'], '.2f')} (2008–2017)",
         f(pvn["era5_2008-2017_period_matched"], ".3f")],
    ]
    for k in order:
        rows.append([f"0.25° box around {N[k]['lat']:.2f}° N, {N[k]['lon']:.2f}° E, sea pixels (GWA) vs that "
                     "node (ERA5), period-matched",
                     f(P[k]["gwa4_100m_ms"]["box_0p25deg_sea_pixels_mean_ms"], ".2f"),
                     f"{f(P[k]['era5_U100_ms']['2008-2017'], '.2f')} (2008–2017)",
                     f(P[k]["ratio_gwa_box_sea_pixels_to_era5_period_matched"], ".3f")])
    parts.append("## Table 4. Mean wind speed at 100 m in ERA5 and in the Global Wind Atlas 4.0 (GWA; "
                 "climatology for 2008–2017), with the reference period of each value.\n\n"
                 + table(["Comparison", "GWA 4.0, 2008–2017 (m s⁻¹)", "ERA5 (m s⁻¹; period)", "Ratio GWA / ERA5"],
                         rows)
                 + "\n\n*Disagreement between two models. GWA is itself driven by ERA5, neither product is "
                   "validated against offshore measurements here, and the ratio is not a bias estimate or a "
                   "correction. The primary estimate is not rescaled.*\n")

    # ---- Table 5
    ss = R["site_screening"]
    b, ock = ss["bathymetry"], ss["protected_area_overlap"]["saros_ock_2010"]
    en = ss["era5_node_representativeness"]
    rows = [
        ["Polygon area (WGS 84 / UTM zone 35N)", f"{f(D['polygon_area_km2'], '.1f')} km²"],
        ["Extent along / across the principal axis",
         f"{f(ss['polygon']['length_along_axis_km'], '.1f')} km / {f(ss['polygon']['width_across_axis_km'], '.1f')} "
         f"km (axis bearing {f(ss['polygon']['principal_axis_bearing_deg'], '.0f')}°)"],
        ["Water depth, minimum / median / maximum (m below LAT)",
         f"{f(b['depth_m']['min'], '.1f')} / {f(b['depth_m']['median'], '.1f')} / {f(b['depth_m']['max'], '.1f')}"],
        ["Water depth, 5th–95th percentile (m)", rng(b["depth_m"]["p5"], b["depth_m"]["p95"], ".1f")],
        ["Share of the area shallower than 10 m", f"{f(D['share_shallower_10m_pct'], '.1f')} %"],
        ["Share of the area deeper than 50 m", f"{f(b['share_deeper_than_pct']['50'], '.1f')} %"],
        ["Area deeper than 200 m", "none" if b["inside_polygon_deeper_than_200m_cells"] == 0 else "present"],
        ["Overlap with the Saros Körfezi Special Environmental Protection Area (boundary reconstructed from "
         "the 2010 decree coordinates; approximate)",
         f"≈{f(ock['overlap_km2'], '.0f')} km² (≈{f(ock['overlap_share_pct'], '.0f')} % of the polygon)"],
        ["Overlap with the Gelibolu Peninsula strictly protected sensitive area (2019)",
         "none" if not ss["protected_area_overlap"]["gelibolu_kkha_2019"]["overlap"] else "present"],
        ["Primary ERA5 node relative to the polygon",
         f"outside; {f(en['distance_to_polygon_boundary_km'], '.1f')} km from the boundary; nearest node for "
         f"{f(en['polygon_share_nearest_to_this_node_pct'], '.1f')} % of the area"],
    ]
    parts.append("## Table 5. First-order screening of the candidate polygon.\n\n"
                 + table(["Item", "Result"], rows)
                 + "\n\n*Bathymetry: EMODnet Digital Bathymetry DTM 2024, cell centres inside the polygon. The "
                   "protected-area boundary is a reconstruction from the coordinates of Decision 2010/1089 "
                   "(no geodetic datum stated); later amendments could not be ruled out. The table is a "
                   "screening result. It is not a permitting, layout or environmental-impact assessment.*\n")

    # ---- Table 6
    em = R["emissions"]
    p, ctx, s3 = em["primary_avoided_operational_co2"], em["context_grid_methods"], D["s3"]
    rows = [
        ["**Combined margin, wind and solar (primary convention)**", f(p["factor_value"], ".4f"),
         f"**{f(p['t_co2_per_mw_yr'], 'sp.0f')}** ({rng(*p['ci90_t_co2_per_mw_yr'], 'sp.0f')})",
         f"{f(s3['avoided_co2_cm_kt_yr'], 'sp.0f')} ({rng(*s3['avoided_co2_cm_kt_yr_ci90_sampling'], 'sp.0f')})"],
        ["Operating margin (context)", f(ctx["operating_margin"]["factor_value"], ".4f"),
         f(ctx["operating_margin"]["result_per_mw_yr"], "sp.0f"),
         f(s3["context_operating_margin_kt_co2_yr"], "sp.0f")],
        ["Build margin (context)", f(ctx["build_margin"]["factor_value"], ".4f"),
         f(ctx["build_margin"]["result_per_mw_yr"], "sp.0f"),
         f(s3["installed_mw"] * ctx["build_margin"]["result_per_mw_yr"] / 1000.0, "sp.0f")],
        ["Generation average, CO₂ (context)", f(ctx["generation_average_co2"]["factor_value"], ".3f"),
         f(ctx["generation_average_co2"]["result_per_mw_yr"], "sp.0f"),
         f(s3["context_generation_average_kt_co2_yr"], "sp.0f")],
    ]
    parts.append("## Table 6. Operational grid-CO₂ accounting equivalent of the net yield under the official 2023 "
                 "emission-factor conventions for Türkiye.\n\n"
                 + table(["Accounting convention (2023)", "Factor (tCO₂ MWh⁻¹)",
                          "Accounting equivalent (tCO₂ MW⁻¹ yr⁻¹)",
                          f"Illustrative {f(s3['installed_mw'], '.1f')} MW case, conditional (kt CO₂ yr⁻¹)"], rows)
                 + f"\n\n*Net energy of the illustrative case: {f(s3['net_energy_gwh_yr'], 'sp.0f')} GWh yr⁻¹ "
                   f"({rng(*s3['net_energy_gwh_yr_ci90_sampling'], 'sp.0f')}). Values in parentheses propagate "
                   "only the sampling interval of the mean energy through a fixed 2023 factor. The conventions "
                   "are alternative accounting conventions, not bounds, and none is a forecast of the "
                   "generation that would physically be displaced. The illustrative case "
                   f"({s3['n_turbines']} × {f(TURBINE.rated_power_mw, '.1f')} MW) is conditional on a future "
                   "allocation of the draft tender capacity to Saros, which has not been made. Life-cycle "
                   "greenhouse-gas values are reported separately in the supplementary tables.*\n")
    return "\n".join(parts)


def supplementary_tables(R: dict, D: dict) -> str:
    ey, wr = R["energy_yield"], R["wind_resource"]
    parts = ["# Supplementary tables\n",
             "*Generated by `scripts/11_build_manuscript_sections.py` from `results/revised/`. Do not edit by "
             "hand.*\n"]

    # S1 inputs and assumptions
    ip = R["input_provenance"]["primary_input"]
    ln = ey["losses_nominal"]
    ls = R["loss_scenarios"]["scenarios"]
    t = D["turbine"]
    rows = [
        ["Wind data", f"ERA5 hourly 10 m and 100 m wind speed and 100 m direction, delivered through the "
                      f"Open-Meteo historical-weather API; node {ip['node_lat_lon'][0]:.2f}° N, "
                      f"{ip['node_lat_lon'][1]:.2f}° E; {ip['period'].replace('-', '–')}; "
                      f"{f(ip['n_hours'], 'spd')} hours; retrieved {D['retrieval_date']}"],
        ["Input file checksum (SHA-256)", f"`{ip['sha256']}`"],
        ["Reference turbine", f"Vestas V164-9.5 MW; rotor {f(t['rotor_m'], '.0f')} m; rated {f(t['rated_mw'], '.1f')} "
                              f"MW; hub height {f(t['hub_m'], '.0f')} m (assumed)"],
        ["Power curve", f"OEDB turbine library row V164/9500 (identifier `{t['curve_id']}`): third-party "
                        f"digitisation of a published graph, {D['curve_n_points_oedb']} points from 0 to "
                        f"{f(D['curve_max_speed_oedb'], '.1f')} m s⁻¹; not manufacturer-certified; air-density "
                        "basis undocumented (1.225 kg m⁻³ assumed)"],
        ["Cut-in / rated / cut-out wind speed", f"{f(t['cut_in'], '.1f')} / {f(t['rated_ms'], '.0f')} / "
                                                f"{f(t['cut_out'], '.0f')} m s⁻¹"],
        ["Shear exponent α", f"{f(ip['alpha_hub_extrapolation'], '.4f')} (trimmed mean of the hourly "
                             "10 m/100 m exponent; reanalysis-derived)"],
        ["Nominal losses (assumptions)", f"wake {f(ln['wake'], 'pct.0f')} %, availability "
                                         f"{f(ln['availability'], 'pct.0f')} %, electrical "
                                         f"{f(ln['electrical'], 'pct.0f')} %; net factor "
                                         f"{f(ey['net_factor_nominal'], '.5f')}"],
        ["Low-loss / high-loss scenarios (assumptions)",
         "; ".join(f"{k.replace('_', ' ')}: wake {f(v['wake'], 'pct.0f')} %, availability "
                   f"{f(v['availability'], 'pct.0f')} %, electrical {f(v['electrical'], 'pct.0f')} %"
                   for k, v in ls.items() if k != "nominal")],
        ["Hours per average year", f(ey["hours_per_average_year"], "sp.0f")],
    ]
    parts.append("## Table S1. Data, reference turbine and assumptions.\n\n" + table(["Item", "Value"], rows) + "\n")

    # S2 calibration
    c = R["input_provenance"]["calibration_vs_cds"]
    rows = [
        ["Common period and hours", f"{c['common_period'].replace('-', '–')}; {f(c['n_hours'], 'spd')} hours"],
        ["100 m speed: mean difference / RMSE (m s⁻¹)", f"{f(c['U100']['mean_diff_ms'], '+.5f')} / "
                                                        f"{f(c['U100']['rmse_ms'], '.3f')}"],
        ["100 m speed: correlation", f(c["U100"]["pearson_r"], ".5f")],
        ["100 m speed: share of hours differing by more than 0.1 m s⁻¹ (%)",
         f(c["U100"]["share_abs_diff_gt_0p1_ms_pct"], ".2f")],
        ["10 m speed: mean difference / RMSE (m s⁻¹)", f"{f(c['U10']['mean_diff_ms'], '+.5f')} / "
                                                       f"{f(c['U10']['rmse_ms'], '.3f')}"],
        ["100 m direction: mean absolute difference (°)", f(c["direction_100m"]["mean_abs_diff_deg"], ".2f")],
        ["Gross capacity factor, same α (relative difference, %)",
         f(c["gross_cf"]["rel_diff_same_alpha_pct"], "+.3f")],
    ]
    parts.append("## Table S2. Input check: the Open-Meteo-delivered ERA5 series against the series derived "
                 "from the Copernicus Climate Data Store (CDS) at the same node over their common years.\n\n"
                 + table(["Check", "Result"], rows)
                 + "\n\n*Both series are ERA5. They are distributed and stored differently, so they are close "
                   "but not bit-identical. This is an input check, not a validation of the wind resource.*\n")

    # S3 annual values
    ann = pd.read_csv(REV / "annual_energy.csv")
    rows = [[int(r.year), int(r.hours), f(r.mean_U_hub_ms, ".2f"), f(r.gross_cf, "pct.2f"), f(r.net_cf, "pct.2f"),
             f(r.net_gwh_per_mw_8766h, ".3f")] for r in ann.itertuples()]
    parts.append("## Table S3. Annual values at the primary node (reanalysis years).\n\n"
                 + table(["Year", "Hours", "Mean wind speed at 105 m (m s⁻¹)", "Gross CF (%)", "Net CF (%)",
                          "Net yield (GWh MW⁻¹ yr⁻¹)"], rows) + "\n")

    # S4 sampling checks
    ci = R["interannual_and_sampling"]["sampling_ci_of_period_mean"]
    var = R["interannual_and_sampling"]["observed_interannual_variability"]
    rows = [
        ["90 % t-interval (primary)", rng(*ci["primary_t_interval_90"]["net_gwh_per_mw"], ".3f")],
        ["90 % year-block bootstrap interval (check)", rng(*ci["check_bootstrap_90"]["net_gwh_per_mw"], ".3f")],
        ["Standard error of the mean: classical / bootstrap / jackknife (%)",
         " / ".join(f(ci["se_rel_pct"][k], ".2f") for k in ("classical", "bootstrap", "jackknife"))],
        ["Annual net-yield CoV; without the lowest year (%)",
         f"{f(var['annual_net_cf_cov_pct'], '.2f')}; {f(var['annual_net_cf_cov_pct_excluding_min_year'], '.2f')}"],
        ["Annual mean-speed CoV (%)", f(wr["annual_mean_cov_pct"]["ddof1"], ".2f")],
        ["Lag-1 autocorrelation of annual capacity factors", f(var["lag1_autocorrelation"], "+.2f")],
    ]
    parts.append("## Table S4. Sampling interval of the 1994–2024 mean net yield (GWh MW⁻¹ yr⁻¹) and "
                 "interannual statistics.\n\n" + table(["Statistic", "Value"], rows) + "\n")

    # S5 periods
    per = R["period_sensitivity"]
    rows = [[k.replace("-", "–"), p["role"], p["n_years"], f(p["mean_U100_ms"], ".2f"),
             f(p["net_gwh_per_mw"], ".3f"),
             "—" if k == per["reference_baseline"]["period"] else f(p["energy_change_vs_reference_pct"], "+.2f")]
            for k, p in per["periods"].items()]
    parts.append("## Table S5. Period-selection sensitivity experiment at the primary node (same method, "
                 "primary-series α).\n\n"
                 + table(["Period", "Role", "Years", "Mean wind speed at 100 m (m s⁻¹)",
                          "Net yield (GWh MW⁻¹ yr⁻¹)", "Change vs 1994–2024 (%)"], rows) + "\n")

    # S6 rolling windows
    roll = pd.read_csv(REV / "rolling_11yr_windows.csv")
    rows = [[f"{int(r.start_year)}–{int(r.end_year)}", f(r.net_gwh_per_mw, ".3f"),
             f(r.rel_to_primary_mean_pct, "+.2f"), "yes" if r.within_primary_period else "no",
             "—" if pd.isna(r.rank_from_lowest_within_primary_period) else int(r.rank_from_lowest_within_primary_period),
             int(r.rank_from_lowest_all_windows)] for r in roll.itertuples()]
    parts.append("## Table S6. All rolling 11-year windows at the primary node, 1979–2024.\n\n"
                 + table(["Window", "Net yield (GWh MW⁻¹ yr⁻¹)", "Relative to the 1994–2024 mean (%)",
                          "Inside 1994–2024", "Rank from lowest, windows inside 1994–2024",
                          "Rank from lowest, all windows"], rows)
                 + "\n\n*Overlapping windows share years and are not independent samples.*\n")

    # S7 Weibull
    w = R["weibull_crosscheck"]
    wf = w["weibull_fit_U_hub"]
    rows = [
        ["Shape k / scale c (maximum likelihood)", f"{f(wf['k_mle'], '.3f')} / {f(wf['c_mle_ms'], '.3f')} m s⁻¹"],
        ["Shape k / scale c (Justus empirical formula)",
         f"{f(wf['k_justus_empirical'], '.3f')} / {f(wf['c_justus_empirical_ms'], '.3f')} m s⁻¹"],
        ["R² of the cumulative distribution / Kolmogorov–Smirnov D",
         f"{f(wf['r2_cdf'], '.4f')} / {f(wf['ks_statistic'], '.3f')}"],
        ["Weibull-implied mean speed / power density",
         f"{f(wf['weibull_mean_ms'], '.2f')} m s⁻¹ / {f(wf['weibull_power_density_wm2'], '.0f')} W m⁻²"],
        ["Gross capacity factor: Weibull integration vs hourly conversion (%)",
         f"{f(w['gross_cf_weibull'], 'pct.2f')} vs {f(w['gross_cf_empirical'], 'pct.2f')} "
         f"({f(w['relative_difference_pct'], '+.2f')} %)"],
    ]
    parts.append("## Table S7. Weibull description of the hourly 105 m wind speed (descriptive only; not the "
                 "energy estimator).\n\n" + table(["Statistic", "Value"], rows)
                 + "\n\n*Hourly values are autocorrelated, so no significance level is attached to the "
                   "Kolmogorov–Smirnov statistic.*\n")

    # S8 monthly and direction
    mon = wr["monthly_mean_U_hub_ms"]
    parts.append("## Table S8. Monthly mean wind speed at 105 m (m s⁻¹), 1994–2024.\n\n"
                 + table([m[:3] for m in MONTHS], [[f(mon[str(i)], ".2f") for i in range(1, 13)]]) + "\n")
    dh, de = wr["direction_share_pct"]["hours"], wr["direction_share_pct"]["energy"]
    parts.append("## Table S9. Distribution of the 100 m wind direction by 16 sectors: share of hours and "
                 "share of gross energy (%).\n\n"
                 + table(["Sector"] + list(dh), [["Hours"] + [f(v, ".1f") for v in dh.values()],
                                                 ["Energy"] + [f(de[k], ".1f") for k in dh]])
                 + f"\n\n*Energy-weighted prevailing axis: "
                   f"{f(R['site_screening']['wind_direction']['energy_weighted_prevailing_axis_deg'], '.0f')}°. "
                   "Direction from the reanalysis, in whole degrees.*\n")

    # S10 speed scaling and GWA node statistics
    ws = R["wind_speed_sensitivity"]["cases"]
    rows = [[("Reference (no scaling)" if c["speed_factor"] == 1.0 else c["case"].replace("-", "−")),
             f(c["speed_factor"], ".3f"), f(c["net_gwh_per_mw"], ".3f"),
             "—" if c["speed_factor"] == 1.0 else f(c["aep_change_vs_baseline_pct"], "+.1f")]
            for c in ws]
    esc = R["wind_product_discrepancy"]["energy_sensitivity_if_primary_hours_were_scaled"]
    pm = esc["by_ratio_era5_2008-2017_period_matched"]
    rows.append(["scaled by the period-matched GWA/ERA5 ratio (illustrative)", f(pm["speed_factor"], ".3f"), "—",
                 f(pm["aep_change_vs_primary_pct"], "+.1f")])
    parts.append("## Table S10. Wind-speed scaling experiments: every hourly speed multiplied by one factor, "
                 "power curve and nominal losses fixed.\n\n"
                 + table(["Case", "Speed factor", "Net yield (GWh MW⁻¹ yr⁻¹)", "Change in energy (%)"], rows)
                 + "\n\n*Sensitivity experiments only. They are not corrections, forecasts or confidence "
                   "intervals, and no scaled value is adopted.*\n")
    P = R["wind_product_discrepancy"]["per_node_gwa_box_vs_era5"]
    rows = [[f"{v['lat']:.2f}° N, {v['lon']:.2f}° E", f(v["gwa4_100m_ms"]["node_pixel_ms"], ".2f"),
             f(v["gwa4_100m_ms"]["box_0p25deg_mean_ms"], ".2f"),
             f(v["gwa4_100m_ms"]["box_0p25deg_sea_pixels_mean_ms"], ".2f"),
             f(v["era5_U100_ms"]["1994-2024"], ".2f"), f(v["era5_U100_ms"]["2008-2017"], ".2f"),
             f(v["ratio_gwa_box_to_era5"]["era5_2008-2017_period_matched"], ".3f"),
             f(v["ratio_gwa_box_sea_pixels_to_era5_period_matched"], ".3f")] for v in P.values()]
    parts.append("## Table S11. Global Wind Atlas 4.0 (2008–2017) and ERA5 mean wind speed at 100 m around "
                 "each node (m s⁻¹).\n\n"
                 + table(["Node", "GWA node pixel", "GWA 0.25° box, all pixels", "GWA 0.25° box, sea pixels",
                          "ERA5 1994–2024", "ERA5 2008–2017", "Ratio box / ERA5 2008–2017",
                          "Ratio sea pixels / ERA5 2008–2017"], rows)
                 + "\n\n*Inter-model comparison, not validation.*\n")

    # S12 illustrative capacities
    dens = {d["name"]: d for d in R["site_screening"]["active_scenarios_density"]}
    cons = R["scenarios"]["consumption_reference"]
    rows = [[f"{s['n_turbines']} × {f(TURBINE.rated_power_mw, '.1f')} MW", f(s["installed_mw"], ".1f"),
             f(dens[s["name"]]["density_mw_per_km2_full_polygon"], ".1f"),
             f"{f(s['net_energy_gwh_yr'], 'sp.0f')} ({rng(*s['net_energy_gwh_yr_ci90_sampling'], 'sp.0f')})",
             f"{f(s['avoided_co2_cm_kt_yr'], 'sp.0f')} ({rng(*s['avoided_co2_cm_kt_yr_ci90_sampling'], 'sp.0f')})",
             f"{f(s['lifecycle_ghg_kt_co2eq_yr_reference'], '.1f')} "
             f"({rng(*s['lifecycle_ghg_kt_co2eq_yr_ipcc_range'], '.1f')})",
             f(s["share_of_2035_offshore_target_capacity_pct"], ".1f"),
             f(s["share_of_2024_gross_consumption_pct"], ".2f")] for s in R["scenarios"]["scenarios"]]
    parts.append("## Table S12. Illustrative capacities (linear scaling of the per-MW results; no layout, "
                 "one wake value for all densities).\n\n"
                 + table(["Illustrative capacity", "MW", "Density (MW km⁻², full polygon)",
                          "Net energy (GWh yr⁻¹; sampling interval)",
                          "Combined-margin CO₂ accounting equivalent (kt yr⁻¹; sampling interval)",
                          "Life-cycle GHG (kt CO₂-eq yr⁻¹; literature range)",
                          "Share of the 5 GW national 2035 offshore projection (%)",
                          f"Share of {cons['year']} national gross consumption (%)"], rows)
                 + f"\n\n*Illustrative capacities without an official basis; the spacing used for the density "
                   f"context ({R['scenarios']['spacing_assumption'].split(' (')[0]}) is an assumption. Gross "
                   f"consumption {f(cons['gwh'], 'sp.1f')} GWh ({cons['year']}; gross generation plus imports "
                   "minus exports). Life-cycle values are literature intensities for other sites, reported "
                   "separately and not subtracted from the CO₂-only grid factor.*\n")

    # S13 emission conventions and life cycle
    em = R["emissions"]
    ctx = em["context_grid_methods"]
    rows = [["Combined margin, wind and solar (primary)", f(em["primary_avoided_operational_co2"]["factor_value"], ".4f"),
             "tCO₂ MWh⁻¹", f(em["primary_avoided_operational_co2"]["t_co2_per_mw_yr"], "sp.1f"), "tCO₂ MW⁻¹ yr⁻¹"]]
    names = {"operating_margin": "Operating margin", "build_margin": "Build margin",
             "generation_average_co2": "Generation average (CO₂)",
             "generation_average_co2eq": "Generation average (all greenhouse gases)"}
    for k, label in names.items():
        eq = ctx[k]["factor_unit"].startswith("tCO2-eq")
        rows.append([label, f(ctx[k]["factor_value"], ".4f" if k != "generation_average_co2" and not eq else ".3f"),
                     "tCO₂-eq MWh⁻¹" if eq else "tCO₂ MWh⁻¹", f(ctx[k]["result_per_mw_yr"], "sp.1f"),
                     "tCO₂-eq MW⁻¹ yr⁻¹" if eq else "tCO₂ MW⁻¹ yr⁻¹"])
    parts.append("## Table S13. Official 2023 grid emission factors for Türkiye and the corresponding "
                 "accounting equivalents of the net yield.\n\n"
                 + table(["Convention", "Factor", "Unit", "Accounting equivalent", "Unit"], rows)
                 + "\n\n*Alternative accounting conventions, not statistical bounds. The all-gas generation "
                   "average is in a different unit and is not comparable with the CO₂-only rows.*\n")
    lc = em["secondary_lifecycle_ghg"]["cases"]
    lab = {"ipcc_ar5_min": "IPCC AR5 Annex III, minimum", "ipcc_ar5_median": "IPCC AR5 Annex III, median",
           "ipcc_ar5_max": "IPCC AR5 Annex III, maximum", "bonou2016_6MW": "Bonou et al. (2016), 6 MW plant",
           "bonou2016_4MW": "Bonou et al. (2016), 4 MW plant"}
    rows = [[lab[k], f(v["g_co2eq_per_kwh"], ".1f"), f(v["t_co2eq_per_mw_yr"], ".1f")] for k, v in lc.items()]
    parts.append("## Table S14. Life-cycle greenhouse-gas intensity of offshore wind from the literature and "
                 "the corresponding amount for the net yield.\n\n"
                 + table(["Source", "Intensity (g CO₂-eq kWh⁻¹)", "Amount (tCO₂-eq MW⁻¹ yr⁻¹)"], rows)
                 + "\n\n*Literature values for other sites, not specific to Saros. They are in CO₂-eq with a "
                   "cradle-to-grave boundary and are therefore reported separately from, and not subtracted "
                   "from, the CO₂-only operational grid factor.*\n")

    # S15 screening classes
    sc = R["site_screening"]["screening_classes_best_fit_layout"]
    sp = R["site_screening"]["spacing_and_packing"]
    rows = [["Grid positions fitted (illustrative)", sc["n_positions"]],
            ["Water depth shallower than 10 m", sc["depth_lt_10m"]],
            ["Water depth 50 m to 62 m", sc["depth_50_to_62m"]],
            ["Within 1 km of the shore", sc["within_1km_of_shore"]],
            ["Inside the reconstructed protected-area boundary", sc["inside_saros_ock_2010"]],
            ["In none of these classes", sc["outside_all_classes"]]]
    parts.append("## Table S15. Screening classes of one illustrative regular grid fitted to the polygon "
                 f"({sp['assumption'].split(' (')[0]} spacing, an assumption).\n\n"
                 + table(["Class", "Number of grid positions"], rows)
                 + "\n\n*Illustrative only. The counts belong to one arbitrary grid fit and are not robust: a "
                   "change of 0.3° in the fitted axis moved them by up to four positions. They are screening "
                   "classes, not exclusion zones, and the grid is not a layout.*\n")
    return "\n".join(parts)


# ------------------------------------------------------------------- driver
def build() -> dict[str, str]:
    R = load_results()
    D = derived(R)
    out = {}
    for name in SECTIONS:
        out[name] = GENERATED_NOTE.format(name=name) + reflow(render((SRC / name).read_text(encoding="utf-8"), R, D))
    out["tables.md"] = main_tables(R, D)
    out["supplementary_tables.md"] = supplementary_tables(R, D)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify that the generated files are up to date")
    a = ap.parse_args()
    out = build()
    stale = [n for n, t in out.items() if not (MAN / n).exists() or (MAN / n).read_text(encoding="utf-8") != t]
    if a.check:
        print("up to date" if not stale else "STALE: " + ", ".join(stale))
        return 1 if stale else 0
    for n, t in out.items():
        (MAN / n).write_text(t, encoding="utf-8")
    print(f"wrote {len(out)} files to {MAN} ({len(stale)} changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
