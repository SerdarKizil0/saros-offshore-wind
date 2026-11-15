"""
Phase 5B-1 — consistency of the rewritten Study Area, Methods and Results sections and of the
generated tables with results/revised/.
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MAN = ROOT / "manuscript"
SRC = MAN / "src"
REV = ROOT / "results" / "revised"
ARCH = ROOT / "results" / "archive" / "baseline_2014_2024_cds"
SECTIONS = ["02_study_area.md", "03_methodology.md", "04_results.md"]
TABLE_FILES = ["tables.md", "supplementary_tables.md"]

# results/revised/ as committed at the start of Phase 5B-1 (MANIFEST.json at c0b1732): this phase must not
# change any numerical result.
RESULTS_SHA256 = {
    "wind_resource.json": "82558d7bfb2acd1f02b914277064791258d7472e0feed5d0800016283c46d704",
    "energy_yield.json": "b047e0371dee1f618a1f9f6c880628eee865caff28ab736d6ce39585fb58f26e",
    "weibull_crosscheck.json": "0ca112e810bcd0a1602df457f668602d07a412fa1eb4f2ff0704326e58078928",
    "interannual_and_sampling.json": "a2daaf26eea3a45a2fb55c4d9b343e940d0aba2fcc1094591e2e679329fbf764",
    "annual_energy.csv": "fe438c18f5de622c71825ba8a1e9eb9e6fa046f6b48b6d48265df9ee6e977790",
    "wind_speed_sensitivity.json": "b042dad665cb8992893ac5272934669ce9bc3eddec8060cb058693a6b74e2df8",
    "loss_scenarios.json": "c0f7cf2dfb34ad815a544761a1cb98e7b6e78091824a2011ebbc986da0ed0e8d",
    "emissions.json": "238734ce3b5bedb786912a76250425b1009c5cc70a8733d9098c2e07299ad44c",
    "scenarios.json": "667bc98e4002bbc37b38a351f51a4e454e4616b70077bdcdb19ba8dca2d5aac7",
    "site_screening.json": "b191405ffdff431efc5c7e0834cd316e98ea1992cfeb691c0e7cd1654ba6657b",
    "input_provenance.json": "2384ac9c1ec8f27bab08edfabe5e3b385a04ec2b138b34ea32c12f6e21b5845a",
    "period_sensitivity.json": "974465f3f026a3c1b5dff90264a903c16bd1885a02b043f7c2600313825b1546",
    "rolling_11yr_windows.csv": "1ba3ab2c7cf294eb2cdaacd44b269d36d67f95046d8d030bdd317028fc04feaf",
    "node_sensitivity.json": "fa420bf8b845a6d80020ce04aee2ea11d0ecfadc7439d080439cba121ea7c1b5",
    "wind_product_discrepancy.json": "3d3333e15dc753a392e27ad479cd6401fc494f0662395198ee006ceb31fb4896",
    "sensitivity_index.json": "13f95d9f694c2f204daf62deb6664d212acf055fded432c2d9f9abebea3d4a72",
}
ARCHIVE_SHA256SUMS = "44877f79edd43fa8d6e729c60830c5ac5fa3de430aaf3fabe64dd2f4fbe8ac22"
# (The pins that kept Abstract, Introduction, Discussion and Conclusion untouched during Phase 5B-1 were
# removed in Phase 5B-2, which rewrote those sections; see tests/test_manuscript_5b2.py.)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def J(name):
    return json.loads((REV / name).read_text())


@pytest.fixture(scope="module")
def builder():
    spec = importlib.util.spec_from_file_location("build11", ROOT / "scripts/11_build_manuscript_sections.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["build11"] = m
    spec.loader.exec_module(m)
    return m


def read(name: str) -> str:
    return (MAN / name).read_text(encoding="utf-8")


def strip_math(t: str) -> str:
    t = re.sub(r"\$\$.*?\$\$", " ", t, flags=re.S)
    return re.sub(r"\$[^$\n]*\$", " X ", t)


def units(name: str) -> list[str]:
    """Checkable units of a generated file: sentences of prose, and table rows, captions and notes."""
    text = strip_math(read(name))
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("|"):
            out += [ln for ln in block.split("\n") if not re.fullmatch(r"\|[-| ]+\|", ln)]
            continue
        flat = " ".join(block.split())
        out += [s for s in re.split(r"(?<=[.!?])[*]?\s+(?=[*\"“(A-ZÖÇ])", flat) if s]
    return out


ALL_FILES = SECTIONS + TABLE_FILES
ALL_UNITS = [(n, u) for n in ALL_FILES for u in units(n)]
MAIN_UNITS = [(n, u) for n in SECTIONS + ["tables.md"] for u in units(n)]
# supplementary data rows are read with their caption; captions and notes are checked like prose
SUP_PROSE = [(n, u) for n, u in ALL_UNITS if n == "supplementary_tables.md" and not u.startswith("|")]
TEXT_UNITS = MAIN_UNITS + SUP_PROSE
YEAR_ROW = re.compile(r"^\| (19|20)\d\d(–(19|20)\d\d)? \|")       # annual and rolling-window listings
NEG = re.compile(r"\b(not|no|none|neither|nor|never|without|cannot)\b", re.I)


def offenders(pattern: str, where=ALL_UNITS, flags=re.I):
    rx = re.compile(pattern, flags)
    return [(n, u) for n, u in where if rx.search(u)]


# ----------------------------------------------------------------- 1. reproducibility
def test_generated_sections_and_tables_are_up_to_date(builder):
    out = builder.build()
    assert set(ALL_FILES) <= set(out)           # Phase 5B-2 added the remaining sections to the build
    for name in ALL_FILES:
        text = out[name]
        assert read(name) == text, f"{name} is stale; run scripts/11_build_manuscript_sections.py"


def test_no_unresolved_placeholder_and_sources_exist():
    for n in SECTIONS:
        assert (SRC / n).exists()
        assert not re.search(r"\{\{\s*\w+\s*:", read(n)), n
        assert read(n).startswith("<!-- GENERATED FILE")
    for n in TABLE_FILES:
        assert "{{" not in read(n) and "Generated by `scripts/11_build_manuscript_sections.py`" in read(n)


# Constants that may be typed in the prose sources: coordinates and grid, the reference machine, documented
# model constants, published policy numbers, legal document numbers and experiment settings.
DECIMALS_OK = {"40.50", "26.25", "26.00", "26.50", "0.25",          # node coordinates, grid spacing, Tool 07 weight
               "9.5", "3.5",                                        # turbine rating, cut-in
               "1.225", "0.10",                                     # air density, comparison shear exponent
               "0.90", "0.95", "1.05", "1.10",                      # speed-scaling factors
               "0.75",                                              # Tool 07 operating-margin weight
               "4.0"}                                               # Global Wind Atlas version
INTEGERS_OK = {"1 000", "20 000", "100", "105", "164", "250", "200", "2872", "29852", "27793", "30791", "1133",
               "1089", "9500"}


def test_no_result_number_is_typed_by_hand_in_the_sources():
    for n in SECTIONS:
        t = (SRC / n).read_text(encoding="utf-8")
        t = re.sub(r"\{\{.*?\}\}", " ", t, flags=re.S)
        t = strip_math(t)
        t = re.sub(r"(?m)^#+ [\d.]+", "#", t)                                   # heading numbers
        t = re.sub(r"Sections? \d+(\.\d+)?((,| to| and) \d+(\.\d+)?)*", "Section", t)
        t = re.sub(r"V164[-/]9\.5|V164/9500", "V164", t)
        decimals = set(re.findall(r"(?<![\d.])\d+\.\d+(?![\d.]*\d)", t))
        assert decimals <= DECIMALS_OK, f"{n}: hand-typed decimals {sorted(decimals - DECIMALS_OK)}"
        ints = set(re.findall(r"(?<![\d.,])\d{1,3}(?: \d{3})+(?!\d)|(?<![\d.,])\d{3,}(?![\d.]*\d)", t))
        ints = {i for i in ints if not (len(i) == 4 and 1900 <= int(i) <= 2100)}
        assert ints <= INTEGERS_OK, f"{n}: hand-typed integers {sorted(ints - INTEGERS_OK)}"


def test_tool07_weights_in_text_equal_config():
    from config.emissions import CM_TOOL07_WEIGHTS_WIND_SOLAR as W
    assert tuple(W) == (0.75, 0.25)
    assert "0.75 times the operating margin plus 0.25 times" in " ".join(read("03_methodology.md").split())


# ------------------------------------------------- 2. current numbers, periods, units
def test_headline_values_in_the_text_equal_the_result_files(builder):
    f = builder.fmt
    ey, s, em = J("energy_yield.json"), J("interannual_and_sampling.json"), J("emissions.json")
    node, per = J("node_sensitivity.json")["nodes"], J("period_sensitivity.json")
    w = J("wind_product_discrepancy.json")["polygon_vs_primary_node"]["ratio_gwa_to_era5"]
    ls = J("loss_scenarios.json")["scenarios"]
    lo, hi = s["sampling_ci_of_period_mean"]["primary_t_interval_90"]["net_gwh_per_mw"]
    res = " ".join(read("04_results.md").split())
    for token in (f"**{f(ey['net']['gwh_per_mw'], '.3f')} GWh MW⁻¹ yr⁻¹**", f"{f(ey['net_cf'], 'pct.2f')} %",
                  f"{f(ey['gross_cf'], 'pct.2f')} %", f"{f(lo, '.3f')}–{f(hi, '.3f')} GWh MW⁻¹ yr⁻¹",
                  f"({f(node['W']['energy_rel_to_primary_node_pct'], '+.1f')} % relative to the primary node)",
                  f"({f(node['E']['energy_rel_to_primary_node_pct'], '+.1f')} %)",
                  f(w["era5_1994-2024"], ".3f"), f(w["era5_2008-2017_period_matched"], ".3f"),
                  f"({f(ls['low_loss']['rel_to_nominal_pct'], '+.1f')} %)",
                  f"({f(ls['high_loss']['rel_to_nominal_pct'], '+.1f')} %)",
                  f"{f(em['primary_avoided_operational_co2']['t_co2_per_mw_yr'], 'sp.0f')} tCO₂ MW⁻¹ yr⁻¹",
                  f"higher than the primary estimate by "
                  f"{f(per['periods']['2014-2024']['energy_change_vs_reference_pct'], 'abs.1f')} %",
                  "highest of all 21", "36 windows"):
        assert token in res, token
    # regression anchors of the adopted baseline
    assert "2.354 GWh" in res and "26.85 %" in res and "2.300–2.407" in res and "1 469 tCO₂" in res


def test_period_node_and_source_are_the_adopted_baseline():
    meth, res, area = (" ".join(read(n).split()) for n in ("03_methodology.md", "04_results.md", "02_study_area.md"))
    assert "1 January 1994 to 31 December 2024" in meth and "31 calendar years" in meth
    assert "271 752 hourly values" in meth and "Open-Meteo" in meth
    assert "not bit-identical" in meth and "Copernicus Climate Data Store" in meth
    assert res.startswith("<!--") and "Over 1994–2024 the ERA5 series at the primary node" in res
    assert "40.50° N, 26.25° E" in area and "40.50° N, 26.25° E" in meth
    ey = J("energy_yield.json")
    assert ey["period"] == "1994-2024" and ey["normalisation_check"]["n_hours"] == 271752


def test_other_periods_appear_only_as_comparisons():
    for n, u in ALL_UNITS:
        if YEAR_ROW.match(u):
            continue                       # rows of the rolling-window listing (caption states what they are)
        if "2014–2024" in u:
            assert re.search(r"comparison|window|common|input check|historical", u, re.I), (n, u)
        if "2008–2017" in u and n in SECTIONS:
            assert re.search(r"wind atlas|GWA|matched|comparison|reference period", u, re.I), (n, u)


def test_units_are_consistent():
    text = " ".join(read(n) for n in ALL_FILES)
    assert "GWh MW⁻¹ yr⁻¹" in text and "tCO₂ MWh⁻¹" in text and "tCO₂ MW⁻¹ yr⁻¹" in text
    for bad in ("gCO₂", "g CO₂ kWh", "TWh", "Mt CO₂", "MtCO₂"):
        assert bad not in text.replace("g CO₂-eq kWh", ""), bad
    # CO2-equivalent appears only for life-cycle values and the all-gas generation average
    for n, u in TEXT_UNITS:
        if "CO₂-eq" in u or "CO₂-equivalent" in u:
            assert re.search(r"life-cycle|greenhouse|all-gas|different unit|literature|cradle-to-grave", u, re.I), (n, u)
    # the grid factor has four decimals and the right unit wherever it is quoted
    cm = J("emissions.json")["primary_avoided_operational_co2"]
    assert cm["factor_unit"] == "tCO2/MWh" and f"{cm['factor_value']:.4f} tCO₂ MWh⁻¹" in " ".join(
        read("03_methodology.md").split())


# -------------------------------------------------------------- 3. retired values
B = r"(?<![\d.])"
E = r"(?![\d])"
RETIRED = [  # 2014-2024 results (addendum section 7) and the earlier Monte Carlo values (5A appendix B)
    r"2\.427", r"27\.69", r"32\.66", r"27\.20", r"23\.06", r"2 427", r"2\.334", r"2\.520", r"±3\.8",
    r"2\.586", r"2\.225", r"1\.931", r"2\.180", r"2\.670", r"2\.905", r"2\.912", r"7\.17", r"3\.66", r"6\.96",
    r"417 W", r"422 W", r"2\.035", r"8\.080", r"1\.85 %", r"8\.42", r"8\.24", r"5\.62", r"7\.55",
    r"1 515", r"1515", r"1 457", r"1 573", r"1 731", r"865\.8", r"1 043", r"1 053", r"29\.1", r"85\.0",
    r"600 GWh", r"1 222", r"2 421", r"1 511", r"347\.9", r"0\.70 %", r"96 432", r"df = 10",
    r"2\.62", r"2\.71", r"29\.9", r"31\.0 %", r"30\.4", r"36\.5", r"25\.8", r"2 ?714", r"1 ?525", r"1 ?277",
    r"1 ?754", r"2\.41", r"2\.83", r"172\.5", r"4\.56", r"1 ?739", r"0\.029", r"69×", r"3 ?036", r"13\.1 TWh",
]


def test_no_retired_value_is_presented_as_a_current_finding():
    bad = []
    for n, u in ALL_UNITS:
        if YEAR_ROW.match(u):
            continue                       # year-by-year listings: values of single years, labelled by year
        for pat in RETIRED:
            if re.search(B + pat + E, u) and "2014–2024" not in u:
                bad.append((n, pat, u[:160]))
    assert not bad, bad
    for n, u in ALL_UNITS:
        assert not re.search(r"11-year mean|eleven-year mean", u, re.I), (n, u)


# ------------------------------------------- 4. uncertainty / sensitivity terminology
BANNED = [r"\bbankable\b", r"\bMonte Carlo\b", r"\bP10\b", r"\bP50\b", r"site-specific", r"\bdesignated\b",
          r"\bthe first\b", r"first (assessment|peer|study|published|site)", r"\bnovel", r"theoretical maximum",
          r"measured shear exponent\b(?! )", r"manufacturer power curve", r"ERA5 underestimates",
          r"uncertainty (quantif|propagat)", r"propagat\w+ uncertaint", r"combined uncertainty",
          r"\bpilot\b", r"Phase-2", r"\bhouseholds?\b", r"passenger car", r"\bfeasib", r"economically viable",
          r"winter peak in .*demand", r"low inter-annual variability", r"well represented by"]


@pytest.mark.parametrize("pattern", BANNED)
def test_banned_wording_is_absent(pattern):
    assert not offenders(pattern), offenders(pattern)[:2]


def test_validation_is_only_ever_denied():
    for n, u in offenders(r"validat"):
        assert NEG.search(u), (n, u)
    for n, u in offenders(r"\bP90\b"):
        assert NEG.search(u), (n, u)
    for n, u in offenders(r"total uncertainty"):
        assert NEG.search(u), (n, u)
    for n, u in offenders(r"\bmeasured\b"):
        assert NEG.search(u), (n, u)


def test_interval_vocabulary_belongs_to_the_sampling_interval_only():
    for n, u in offenders(r"±"):
        assert re.search(r"sampling", u, re.I), (n, u)
    for n, u in offenders(r"confidence"):
        assert re.search(r"sampling", u, re.I) or NEG.search(u), (n, u)
    for n, u in offenders(r"\bbounds?\b"):
        assert NEG.search(u), (n, u)
    # sensitivities are stated as experiments, never as intervals of the estimate
    for n, u in offenders(r"(grid[- ]node|neighbour|GWA|period-selection|loss)[^.]*\b(confidence|probab)", MAIN_UNITS):
        assert NEG.search(u) or "Probabilistic interval (the only one)" in u or "only probabilistic" in u, (n, u)
    res = " ".join(read("04_results.md").split())
    assert "They are not combined into a single interval" in res
    assert "This is the only probabilistic interval in the study" in res
    meth = " ".join(read("03_methodology.md").split())
    assert "Only one probabilistic interval is reported" in meth
    assert "not combined with the sampling interval or with each other" in meth
    for label in ("(sensitivity experiment;", "(inter-model comparison;", "(assumption scenarios)"):
        assert label in res, label
    assert "statistics of reanalysis output, not of measurements" in res


def test_table_2_lists_six_separate_categories():
    t = read("tables.md")
    block = t.split("## Table 2.")[1].split("## Table 3.")[0]
    rows = [r for r in block.split("\n") if re.match(r"\| \d \|", r)]
    assert [r.split("|")[1].strip() for r in rows] == ["1", "2", "3", "4", "5", "6"]
    idx = J("sensitivity_index.json")
    assert len(idx["categories"]) == 6 and idx["combinable_into_one_interval"] is False
    assert sum("Probabilistic interval" in r for r in rows) == 1 and "Probabilistic" in rows[0]
    assert "are not combined" in block and "must not be added or merged into a single interval" in block
    assert "not averaged, not a bound" in rows[3] and "not a correction" in rows[4]


def test_power_curve_losses_and_weibull_are_described_correctly():
    meth = " ".join(read("03_methodology.md").split())
    assert "third-party digitisation" in meth and "not a manufacturer-certified power curve" in meth
    assert "illustrative assumptions" in meth and "no wake model was run" in meth
    assert "is not used to estimate energy" in meth
    assert "Weibull" not in read("04_results.md") and "Weibull" not in read("tables.md")
    assert "descriptive only; not the energy estimator" in read("supplementary_tables.md")
    assert "It is not a measured shear" in meth


# ----------------------------------------------------- 5. legal status, protected area
def test_candidate_status_and_no_capacity_allocation():
    area = " ".join(read("02_study_area.md").split())
    for phrase in ("candidate YEKA", "It is not a declared YEKA and not an approved project",
                   "draft tender specification", "any one of the areas",
                   "does not assign that capacity, or any capacity, to Saros", "14 November 2026"):
        assert phrase in area, phrase
    for n, u in offenders(r"approved project"):
        assert NEG.search(u), (n, u)
    for n, u in offenders(r"(allocat|assign)\w* [^.]*\bSaros"):
        assert re.search(r"\b(not|if|were|future|conditional)\b", u, re.I), (n, u)
    for n, u in offenders(r"1 000 MWe|997\.5|≈ ?1 GW|105 turbines", TEXT_UNITS):
        assert re.search(r"draft|conditional|illustrative|\bif\b|any one", u, re.I), (n, u)


def test_only_one_illustrative_capacity_in_the_main_text():
    for n in SECTIONS + ["tables.md"]:
        t = read(n)
        assert not re.search(r"(?<![\d.])(247(\.0)? MW|503\.5|26 × 9\.5|53 × 9\.5)", t), n
        assert not re.search(r"\bS[124]\b", re.sub(r"Tables? S\d+( and S\d+)?", "", " ".join(t.split()))), n
    sup = read("supplementary_tables.md")
    assert "26 × 9.5 MW" in sup and "53 × 9.5 MW" in sup and "1738.5" not in sup and "183" not in sup


def test_protected_area_is_reported_as_an_approximate_screening_result():
    area = " ".join(read("02_study_area.md").split())
    for phrase in ("Decision 2010/1089", "does not state a geodetic datum", "reconstructed",
                   "could not be confirmed", "the absence of a discovered amendment does not show that none exists",
                   "makes no determination"):
        assert phrase in area, phrase
    ock = J("site_screening.json")["protected_area_overlap"]["saros_ock_2010"]
    assert f"about {ock['overlap_km2']:.0f} km²" in area and f"about {ock['overlap_share_pct']:.0f} %" in area
    assert not re.search(r"14\.4 ?%|14\.36|24\.7", " ".join(read(n) for n in SECTIONS + ["tables.md"]))
    for pat in (r"\b(is|are|be) (prohibited|forbidden|permitted|allowed)\b", r"cannot be built", r"can be built",
                r"\bexcluded from development\b", r"\blegal(ly)? (barrier|obstacle)"):
        assert not offenders(pat), offenders(pat)[:1]
    for topic in J("site_screening.json")["not_screened"]:
        key = topic.split(" (")[0].split(" and ")[0].lower()
        assert key.split()[0] in area.lower(), topic


def test_node_and_land_sea_mask_are_described():
    area = " ".join(read("02_study_area.md").split())
    n = J("node_sensitivity.json")["nodes"]
    for k in ("W", "C", "E"):
        assert f"{n[k]['era5_land_sea_mask_fraction']:.2f}" in area
    assert "This node lies outside the polygon" in area and "None of the three nodes lies inside the polygon" in area
    assert "node-level results" in area


# ----------------------------------------------------------------- 6. CO2 wording
def test_no_unconditional_co2_displacement_claim():
    for n, u in offenders(r"\bavoid"):
        assert re.search(r"accounting|convention", u, re.I), (n, u)
    for pat in (r"\bavoids\b", r"\b(will|would|could) avoid\b", r"\bdisplaces\b", r"\bwill displace\b",
                r"emission-free", r"\boffsets?\b", r"carbon[- ]positive", r"\bsaves?\b"):
        assert not offenders(pat), offenders(pat)[:1]
    for n, u in offenders(r"displac"):
        assert NEG.search(u), (n, u)
    res = " ".join(read("04_results.md").split())
    meth = " ".join(read("03_methodology.md").split())
    assert "not a forecast of the generation that would physically be displaced" in res
    assert "It is not a forecast of the generation that the plant would physically displace" in meth
    assert "are not subtracted from" in meth
    assert "accounting equivalent" in res and "combined-margin convention" in res


# --------------------------------------------------------------------- 7. tables
def test_tables_are_numbered_and_cited():
    main, sup = read("tables.md"), read("supplementary_tables.md")
    assert re.findall(r"(?m)^## Table (\d+)\.", main) == [str(i) for i in range(1, 7)]
    s_nums = [int(x) for x in re.findall(r"(?m)^## Table S(\d+)\.", sup)]
    assert s_nums == list(range(1, len(s_nums) + 1)) and len(s_nums) >= 12
    text = " ".join(read(n) for n in SECTIONS)
    assert {int(x) for x in re.findall(r"(?<!Supplementary )Table (\d+)", text)} == set(range(1, 7))
    cited_s = {int(x) for x in re.findall(r"Table S(\d+)", text)} | {
        int(x) for a, b in re.findall(r"Tables S(\d+) and S(\d+)", text) for x in (a, b)}
    assert cited_s and cited_s <= set(s_nums)
    # material that the scope decision moves out of the main text
    for moved in ("Weibull", "Life-cycle greenhouse-gas intensity", "Illustrative capacities", "16 sectors",
                  "Input check", "Screening classes of one illustrative regular grid"):
        assert moved in sup and moved not in main, moved


def test_table_values_equal_the_result_files(builder):
    f = builder.fmt
    main = read("tables.md")
    n = J("node_sensitivity.json")["nodes"]
    row = next(r for r in main.split("\n") if r.startswith("| Net specific yield"))
    assert [c.strip() for c in row.split("|")[2:5]] == [f(n[k]["net_gwh_per_mw"], ".3f") for k in ("W", "C", "E")]
    row = next(r for r in main.split("\n") if r.startswith("| ERA5 land–sea mask"))
    assert [c.strip() for c in row.split("|")[2:5]] == [f(n[k]["era5_land_sea_mask_fraction"], ".2f")
                                                        for k in ("W", "C", "E")]
    em = J("emissions.json")
    assert f"| {em['primary_avoided_operational_co2']['factor_value']:.4f} |" in main
    s3 = next(s for s in J("scenarios.json")["scenarios"] if s["name"] == "S3")
    assert f"Illustrative {s3['installed_mw']:.1f} MW case, conditional" in main
    assert "which has not been made" in main


# ------------------------------------------------------------------ 8. integrity
def test_numerical_results_and_archive_are_unchanged():
    assert set(RESULTS_SHA256) == {p.name for p in REV.iterdir() if p.name != "MANIFEST.json"}
    for name, digest in RESULTS_SHA256.items():
        assert sha(REV / name) == digest, f"{name} changed in Phase 5B-1"
    m = J("MANIFEST.json")
    assert {k: v["sha256"] for k, v in m["files"].items()} == RESULTS_SHA256
    assert sha(ARCH / "SHA256SUMS") == ARCHIVE_SHA256SUMS
    for line in (ARCH / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        assert sha(ARCH / name) == digest, name


def test_builder_only_reads_results():
    src = (ROOT / "scripts/11_build_manuscript_sections.py").read_text()
    assert "results/archive" not in src and "provisional" not in src
    assert not re.search(r"REV\s*/[^\n]*write_text|to_csv\(REV", src)
