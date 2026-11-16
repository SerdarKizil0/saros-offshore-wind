"""
Phase 5D-1: locks for the corrected scientific statements (final revision).

These tests pin the corrections made in response to the review, as decided in
docs/review/PHASE5D0_REVIEW_RESPONSE_MATRIX.md:
- reference-period interpretation (Z1);
- ERA5 resolution and output nodes (Z2);
- GWA 4.0 period source (M5);
- terminology, limitations and rounding (P1).
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manuscript"
REV = ROOT / "results" / "revised"
TEXT = ["00_abstract.md", "01_introduction.md", "02_study_area.md", "03_methodology.md", "04_results.md",
        "05_discussion.md", "06_conclusion.md", "07_declarations.md", "09_figures.md", "tables.md",
        "supplementary_tables.md"]


def flat(name: str) -> str:
    return " ".join((MAN / name).read_text(encoding="utf-8").split())


ALL = {n: flat(n) for n in TEXT}


# ---------------------------------------------------------------- Z1 reference period
def test_unsupported_period_wording_is_gone():
    for n, t in ALL.items():
        assert not re.search(r"biased high|is systematic\b|show that this is systematic", t), n
        assert "not a neutral choice of reference period" not in t, n
        assert "What is demonstrated is the pattern" not in t, n


def test_period_difference_is_set_against_the_11_year_sampling_interval():
    roll = pd.read_csv(REV / "rolling_11yr_windows.csv")
    last = roll.sort_values("start_year").iloc[-1]
    assert (int(last.start_year), int(last.end_year)) == (2014, 2024)
    hw = f"±{last.t90_half_width_rel_pct:.1f} %"
    assert hw == "±3.8 %"
    for n in ("00_abstract.md", "04_results.md", "05_discussion.md"):
        assert hw in ALL[n], n
    assert "does not by itself establish a lasting change" in ALL["00_abstract.md"]
    assert "It is not, on its own, evidence of a lasting change in the wind resource" in ALL["04_results.md"]
    assert "What is observed is a difference, not a demonstrated shift" in ALL["05_discussion.md"]
    assert "a difference of the same size as the sampling uncertainty of an 11-year mean" in ALL["06_conclusion.md"]
    # the per-window intervals come from the existing result column, shown in Table S6
    assert "90 % sampling half-width of the window mean (%)" in ALL["supplementary_tables.md"]


def test_no_exploratory_statistics_enter_the_manuscript():
    for n, t in ALL.items():
        assert not re.search(r"permutation|Kendall|Mann[–-]Whitney|Welch|Theil|Sen's slope|p = 0\.\d|p ≈", t), n
        assert not re.search(r"\btrend test\b|per decade", t), n


# ---------------------------------------------------------------- Z2 ERA5 resolution
def test_era5_resolution_and_output_nodes_are_described_correctly():
    m = ALL["03_methodology.md"]
    assert "horizontal resolution of about 31 km (Hersbach et al., 2020)" in m
    assert "regular 0.25° latitude–longitude grid interpolated from the model grid" in m
    s = ALL["02_study_area.md"]
    assert "interpolated from a model grid of about 31 km" in s and "about 21 km apart" in s
    assert "consistent with smoothing on the coarser model grid" in s
    for n, t in ALL.items():
        for bad in ("0.25° cell", "land fraction of the cell", "land fraction of each cell", "mixed land–sea cell",
                    "grid cell or pixels", "neighbouring cell", "model cells", "the three cells", "primary cell",
                    "western cell", "eastern cell", "the grid cell"):
            assert bad not in t, (n, bad)


def test_genuine_gradient_is_offered_as_an_explanation():
    assert "genuine east–west gradient in the wind" in ALL["04_results.md"]
    assert "A genuine east–west gradient" in ALL["05_discussion.md"]
    assert "not independent cells" in ALL["09_figures.md"]


def test_figure_labels_use_output_node_wording():
    fig1 = (ROOT / "scripts" / "fig1_site_map.py").read_text(encoding="utf-8")
    fig3 = (ROOT / "scripts" / "fig3_nodes_and_products.py").read_text(encoding="utf-8")
    assert '"Area nearest to each ERA5 node"' in fig1 and "land–sea mask {node" in fig1
    assert "0.25° cell of each node" not in fig1
    assert '"Boundary between nearest-node areas"' in fig3 and "land–sea mask\\n" in fig3
    assert "0.25° ERA5 cells" not in fig3 and "node's 0.25° cell" not in fig3


# ---------------------------------------------------------------- M5 GWA period
def test_gwa_period_is_sourced_to_the_gwa4_documentation():
    for n in ("03_methodology.md", "04_results.md", "09_figures.md"):
        assert re.search(r"2008–2017.{0,80}Hansen et al\.,? ?\(?2025|mesoscale simulation period", ALL[n]), n
    assert "Hansen et al., 2025" in ALL["03_methodology.md"]
    refs = flat("08_references.md")
    assert "Hansen, B.O., Floors, R., Badger, J. (2025). *Global Wind Atlas 4 – Validation" in refs
    rows = {r["key"]: r for r in csv.DictReader((ROOT / "docs/review/phase5b2_reference_register.csv")
                                                 .open(encoding="utf-8"))}
    assert rows["hansen2025"]["status"] == "V-FT" and "2008-2017" in rows["hansen2025"]["note"]
    assert "reference period of the wind atlas" not in " ".join(ALL.values())


# ---------------------------------------------------------------- Yildirim limitation retained
def test_yildirim_limitation_is_explicit():
    i = ALL["01_introduction.md"]
    assert "the full text was not available to us" in i
    assert "the results of the two studies are not compared here" in i
    assert "According to Yildirim (2023), an earlier tender process was opened in 2018" in i


# ---------------------------------------------------------------- P1 corrections
def test_p1_corrections_are_present():
    t = " ".join(ALL.values())
    assert "sampling interval" not in t                                              # terminology
    assert "sampling confidence interval" in ALL["03_methodology.md"]
    m = ALL["03_methodology.md"]
    assert "illustrative assumptions chosen by the authors" in m                     # losses
    assert "It covers the 2014–2024 common period only; the years 1994–2013 were not compared with a CDS download" in m
    assert "it starts in 1994 to give 31 years" in m                                 # baseline rationale
    assert "independent draws from a distribution that does not change over the period" in m   # stationarity
    assert "The uncertainty of the digitised curve and the effect of the choice of turbine were not quantified" in m
    assert re.search(r"specific rating of about \d{3} W m⁻²", m)
    assert "which was not quantified, comes in addition" in ALL["06_conclusion.md"]
    assert "The study makes four limited contributions" in ALL["01_introduction.md"]
    assert "three practices, none of them new" in ALL["06_conclusion.md"]
    assert "raises a question for the competent authorities" in ALL["06_conclusion.md"]


def test_headline_values_are_rounded_only_in_abstract_and_conclusions():
    ey = json.loads((REV / "energy_yield.json").read_text())
    for n in ("00_abstract.md", "06_conclusion.md"):
        assert f"about {ey['net']['gwh_per_mw']:.2f} GWh MW⁻¹ yr⁻¹" in ALL[n], n
        assert f"{ey['net']['gwh_per_mw']:.3f} GWh" not in ALL[n], n
    assert f"{ey['net']['gwh_per_mw']:.3f}" in ALL["tables.md"]


def test_reference_details_corrected_from_registries():
    refs = flat("08_references.md")
    for s in ("Çağatay, M.N., Yavuzoğlu, A.Z., Önder, Ş., Ülgen, U.B.", "Davis, N.N., Badger, J., Hahmann, A.N., Hansen, B.O.",
              "Kalverla, P.C., Holtslag, A.A.M., Ronda, R.J., Steeneveld, G.-J.", "Doblas-Reyes, F.J.", "Hasager, C.B.",
              "*Wind Energy Science*, 9(8), 1727–1745", "Zippenfenig, P. (2024). Open-Meteo.com Weather API (version 1.4.0)",
              "20(5), 5571–5584"):
        assert s in refs, s
    assert "Zippenfenig, 2024" in ALL["03_methodology.md"] and "Zippenfenig, 2024" in ALL["07_declarations.md"]
