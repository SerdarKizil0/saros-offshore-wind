"""
Phase 5B-2 — manuscript-wide consistency of the complete text (title, abstract, Sections 1 to 6,
declarations, references) with results/revised/ and with the scope decisions.
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MAN = ROOT / "manuscript"
SRC = MAN / "src"
REV = ROOT / "results" / "revised"
REGISTER = ROOT / "docs/review/phase5b2_reference_register.csv"
PROSE = ["00_abstract.md", "01_introduction.md", "02_study_area.md", "03_methodology.md", "04_results.md",
         "05_discussion.md", "06_conclusion.md", "07_declarations.md",
         "09_figures.md"]                 # figure captions, added in Phase 5C-1
REFS = "08_references.md"
TABLES = ["tables.md", "supplementary_tables.md"]
NARRATIVE = ["00_abstract.md", "01_introduction.md", "05_discussion.md", "06_conclusion.md"]   # written in 5B-2
TITLE = ("Long-term reanalysis-based energy yield of the Gulf of Saros offshore wind candidate area, Türkiye: "
         "sensitivity to reference period, grid node and wind data source")
PHASE_5B1_COMMIT = "5da6d44"


def J(name):
    return json.loads((REV / name).read_text())


def read(name: str) -> str:
    return (MAN / name).read_text(encoding="utf-8")


def flat(name: str) -> str:
    return " ".join(read(name).split())


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def builder():
    return _load("build11_b2", "scripts/11_build_manuscript_sections.py")


def strip_math(t: str) -> str:
    t = re.sub(r"\$\$.*?\$\$", " ", t, flags=re.S)
    return re.sub(r"\$[^$\n]*\$", " X ", t)


def units(name: str) -> list[str]:
    text = re.sub(r"<!--.*?-->", "", strip_math(read(name)), flags=re.S)
    out = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("|"):
            out += [ln for ln in block.split("\n") if not re.fullmatch(r"\|[-| ]+\|", ln)]
            continue
        one = " ".join(block.split())
        out += [s for s in re.split(r"(?<=[.!?])[*\]]?\s+(?=[*\"“(\[A-ZÖÇ])", one) if s]
    return out


PROSE_UNITS = [(n, u) for n in PROSE for u in units(n)]
TABLE_UNITS = [(n, u) for n in TABLES for u in units(n)]
SUP_PROSE = [(n, u) for n, u in TABLE_UNITS if n == "supplementary_tables.md" and not u.startswith("|")]
TEXT_UNITS = PROSE_UNITS + [(n, u) for n, u in TABLE_UNITS if n == "tables.md"] + SUP_PROSE
ALL_UNITS = PROSE_UNITS + TABLE_UNITS
YEAR_ROW = re.compile(r"^\| (19|20)\d\d(–(19|20)\d\d)? \|")
NEG = re.compile(r"\b(not|no|none|neither|nor|never|without|cannot|nothing)\b", re.I)
CITED = re.compile(r"\((?:[^()]*\b)?(19|20)\d\d[a-z]?\)|\b(19|20)\d\d[a-z]?\)")


def offenders(pattern: str, where=None, flags=re.I):
    rx = re.compile(pattern, flags)
    return [(n, u) for n, u in (ALL_UNITS if where is None else where) if rx.search(u)]


# ------------------------------------------------------------- 1. reproducible build
def test_whole_manuscript_is_generated_and_up_to_date(builder):
    out = builder.build()
    assert set(out) == set(PROSE + [REFS] + TABLES)
    for name, text in out.items():
        assert read(name) == text, f"{name} is stale; run scripts/11_build_manuscript_sections.py"
        assert (SRC / name).exists() or name in TABLES
    r = subprocess.run([sys.executable, "scripts/11_build_manuscript_sections.py", "--check"], cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 0 and "up to date" in r.stdout
    for n in PROSE + [REFS]:
        assert read(n).startswith("<!-- GENERATED FILE") and not re.search(r"\{\{\s*\w+\s*:", read(n)), n


DECIMALS_OK = {"40.50", "26.25", "26.00", "26.50", "0.25", "9.5", "3.5", "1.225", "0.10", "0.90", "0.95", "1.05",
               "1.10", "0.75", "4.0",
               "29.6",
               "367.62"}                    # Yildirim (2023), Table 3: area of its Saros study region (km²)                      # National Energy Plan 2022: wind capacity projected for 2035 (GW)
INTEGERS_OK = {"1 000", "20 000", "100", "105", "164", "250", "200", "2872", "29852", "27793", "30791", "1133",
               "1089", "9500", "256",
               "32635"}                     # EPSG code of WGS 84 / UTM zone 35N (figure caption)


@pytest.mark.parametrize("name", PROSE)
def test_no_result_number_is_typed_by_hand(name):
    t = (SRC / name).read_text(encoding="utf-8")
    t = re.sub(r"\{\{.*?\}\}", " ", t, flags=re.S)
    t = re.sub(r"<!--.*?-->|!\[[^]]*\]\([^)]*\)", " ", t, flags=re.S)    # comments and image links
    t = strip_math(t)
    t = re.sub(r"doi:\S+", " ", t)
    t = re.sub(r"(?m)^#+ [\d.]+", "#", t)
    t = re.sub(r"Sections? \d+(\.\d+)?((,| to| and) \d+(\.\d+)?)*", "Section", t)
    t = re.sub(r"V164[-/]9\.5|V164/9500", "V164", t)
    decimals = set(re.findall(r"(?<![\d.])\d+\.\d+(?![\d.]*\d)", t))
    assert decimals <= DECIMALS_OK, f"hand-typed decimals {sorted(decimals - DECIMALS_OK)}"
    ints = set(re.findall(r"(?<![\d.,])\d{1,3}(?: \d{3})+(?!\d)|(?<![\d.,])\d{3,}(?![\d.]*\d)", t))
    ints = {i for i in ints if not (len(i) == 4 and 1900 <= int(i) <= 2100)}
    assert ints <= INTEGERS_OK, f"hand-typed integers {sorted(ints - INTEGERS_OK)}"


# --------------------------------------- 2. period, source, units, numbers across sections
def test_title_is_the_approved_one():
    assert read("00_abstract.md").split("\n# ", 1)[1].split("\n", 1)[0] == TITLE
    assert "**Keywords:**" in read("00_abstract.md")


def test_period_and_source_are_consistent_across_the_manuscript():
    for n in ("00_abstract.md", "01_introduction.md", "04_results.md", "05_discussion.md", "06_conclusion.md"):
        assert "1994–2024" in flat(n), n
    assert "Open-Meteo" in flat("03_methodology.md") and "Open-Meteo" in flat("07_declarations.md")
    assert "not bit-identical" in flat("03_methodology.md") and "not bit-identical" in flat("07_declarations.md")
    assert "31-year mean" in flat("00_abstract.md") and "31 years of hourly ERA5" in flat("01_introduction.md")
    for n, u in ALL_UNITS:
        if YEAR_ROW.match(u):
            continue
        if "2014–2024" in u:
            assert re.search(r"comparison|window|common|input check|historical", u, re.I), (n, u)
    for bad in ("eleven years of hourly", "2014–2024 mean", "ERA5 reanalysis (2014–2024)"):
        assert not offenders(re.escape(bad)), bad
    for n, u in offenders(re.escape("11-year mean")):          # Phase 5D-1: only as sampling uncertainty of a window
        assert re.search(r"sampling", u, re.I), (n, u)


def test_headline_numbers_agree_in_every_section(builder):
    f = builder.fmt
    ey, s = J("energy_yield.json"), J("interannual_and_sampling.json")
    node = J("node_sensitivity.json")["nodes"]
    lo, hi = s["sampling_ci_of_period_mean"]["primary_t_interval_90"]["net_gwh_per_mw"]
    # Phase 5D-1: headline values are rounded in the Abstract and Conclusions ("about"), exact elsewhere
    y = f"{f(ey['net']['gwh_per_mw'], '.3f')} GWh MW⁻¹ yr⁻¹"
    for n in ("04_results.md", "05_discussion.md"):
        assert y in flat(n), n
    y2 = f"about {f(ey['net']['gwh_per_mw'], '.2f')} GWh MW⁻¹ yr⁻¹"
    for n in ("00_abstract.md", "06_conclusion.md"):
        assert y2 in flat(n), n
    cf = f"{f(ey['net_cf'], 'pct.2f')} %"
    for n in ("04_results.md", "05_discussion.md"):
        assert cf in flat(n), n
    assert f"about {f(ey['net_cf'], 'pct.0f')} %" in flat("00_abstract.md")
    ci = f"{f(lo, '.3f')}–{f(hi, '.3f')} GWh MW⁻¹ yr⁻¹"
    assert ci in flat("04_results.md")
    hw = s["sampling_ci_of_period_mean"]["primary_t_interval_90"]["half_width_rel_pct"]
    assert f"±{f(hw, '.1f')} %" in flat("00_abstract.md")
    w, e = (f(node[k]["energy_rel_to_primary_node_pct"], "+.1f") + " %" for k in ("W", "E"))
    for n in ("00_abstract.md", "04_results.md", "05_discussion.md"):
        assert w in flat(n) and e in flat(n), n
    p14 = f(J("period_sensitivity.json")["periods"]["2014-2024"]["energy_change_vs_reference_pct"], "abs.1f") + " %"
    assert p14 in flat("00_abstract.md") and p14 in flat("04_results.md")


def test_every_yield_value_in_the_text_exists_in_the_results(builder):
    """Any number carrying the yield unit must be a formatted value of the result files."""
    known = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, float):
            known.add(builder.fmt(o, ".3f"))
    for p in REV.glob("*.json"):
        walk(json.loads(p.read_text()))
    known |= {builder.fmt(v, ".3f") for v in builder.derived(builder.load_results()).values()
              if isinstance(v, float)}
    found = set()
    for n in PROSE:
        found |= set(re.findall(r"(\d\.\d{3})(?:–\d\.\d{3})? GWh MW⁻¹ yr⁻¹", flat(n)))
        found |= set(re.findall(r"\d\.\d{3}–(\d\.\d{3}) GWh MW⁻¹ yr⁻¹", flat(n)))
    assert found and found <= known, sorted(found - known)


def test_units_across_the_manuscript():
    text = " ".join(read(n) for n in PROSE + TABLES)
    for bad in ("gCO₂", "TWh", "Mt CO₂", "MtCO₂", "kWh⁻¹ MW"):
        assert bad not in text.replace("g CO₂-eq kWh", ""), bad
    for n, u in TEXT_UNITS:
        if "CO₂-eq" in u or "CO₂-equivalent" in u:
            assert re.search(r"life-cycle|greenhouse|all-gas|different unit|literature|cradle-to-grave", u, re.I), (n, u)


def test_discussion_statements_derived_from_results_hold(builder):
    d = builder.derived(builder.load_results())
    w = d["windows"]
    assert w["n_above"] == w["n_recent_consecutive_above"] and w["n_above"] + w["n_below"] == w["n"]
    assert d["second_lowest_year"] == 2014
    n = J("node_sensitivity.json")["nodes"]
    half = J("interannual_and_sampling.json")["sampling_ci_of_period_mean"]["primary_t_interval_90"]["half_width_rel_pct"]
    for k in ("W", "E"):
        assert abs(n[k]["energy_rel_to_primary_node_pct"]) > half          # "larger than the sampling interval"
    # "land fraction alone does not order the three cells"
    assert abs(n["E"]["era5_land_sea_mask_fraction"] - n["C"]["era5_land_sea_mask_fraction"]) < 0.05
    assert n["E"]["net_gwh_per_mw"] < n["C"]["net_gwh_per_mw"] < n["W"]["net_gwh_per_mw"]
    ls = J("loss_scenarios.json")["scenarios"]
    p14 = J("period_sensitivity.json")["periods"]["2014-2024"]["energy_change_vs_reference_pct"]
    assert min(p14, abs(ls["low_loss"]["rel_to_nominal_pct"]), abs(ls["high_loss"]["rel_to_nominal_pct"])) > half
    assert J("site_screening.json")["polygon"]["width_across_axis_km"] < 0.25 * 111.0 * 0.76   # narrower than a cell


# --------------------------------------------- 3. obsolete methodology and claims
OBSOLETE = [r"\bMonte Carlo\b", r"10 ?000[- ]iteration", r"\bP10\b", r"\bP50\b", r"triangular", r"fuel-resolved",
            r"\bhouseholds?\b", r"passenger car", r"theoretical maximum", r"\bpilot\b", r"Phase-2",
            r"measured (wind-)?shear exponent\b(?! )", r"manufacturer power curve", r"life-cycle factor of",
            r"net of an offshore wind", r"seventy-fold", r"69×"]
CLAIMS = [r"\bbankable\b", r"\bdesignated\b", r"site-specific", r"\bthe first\b",
          r"first (assessment|peer|study|published|site|quantif)", r"\bnovel\b", r"\bunprecedented\b",
          r"to (the best of )?our knowledge", r"no (peer-reviewed|published) (assessment|study)",
          r"ERA5 underestimates", r"uncertainty (quantif|propagat)", r"propagat\w+ uncertaint",
          r"combined uncertainty", r"economically viable", r"winter peak in .*demand", r"low inter-annual variability",
          r"\breliable\b", r"\bproves?\b", r"\bconfirms? that\b"]


@pytest.mark.parametrize("pattern", OBSOLETE + CLAIMS)
def test_obsolete_methods_and_unsupported_claims_are_absent(pattern):
    assert not offenders(pattern), offenders(pattern)[:2]


def test_weibull_is_never_the_energy_estimator():
    for n in PROSE:
        if n != "03_methodology.md":
            assert "Weibull" not in read(n), n
    meth = read("03_methodology.md")
    block = meth.split("## 3.10.")[1]
    assert "Weibull" not in meth.split("## 3.10.")[0]              # mentioned only in the supplementary subsection
    assert "descriptive statistic" in " ".join(block.split())
    assert "is not used to estimate energy" in " ".join(block.split())
    assert "Weibull" not in read("tables.md")
    assert "converted hour by hour" in flat("00_abstract.md")
    assert "converting 31 years of hourly ERA5 wind speeds" in flat("01_introduction.md")


def test_negated_only_vocabulary():
    for word in (r"validat", r"\bP90\b", r"total uncertainty", r"\bmeasured\b", r"\bviab", r"approved project",
                 r"\bprediction\b", r"\bbounds?\b"):
        for n, u in offenders(word, PROSE_UNITS + TABLE_UNITS):
            assert NEG.search(u), (word, n, u)
    for n, u in offenders(r"\bfeasib", PROSE_UNITS + TABLE_UNITS):
        assert NEG.search(u) or re.search(r"\((19|20)\d\d\)", u), (n, u)       # only as another study's title/type


# ---------------------------------- 4. sampling interval vs sensitivities; no bounds
def test_interval_language_is_reserved_for_the_sampling_interval():
    for n, u in offenders(r"±"):
        assert re.search(r"sampling", u, re.I), (n, u)
    for n, u in offenders(r"confidence"):
        assert re.search(r"sampling", u, re.I) or NEG.search(u), (n, u)
    lo, hi = J("interannual_and_sampling.json")["sampling_ci_of_period_mean"]["primary_t_interval_90"]["net_gwh_per_mw"]
    for n, u in offenders(re.escape(f"{lo:.3f}–{hi:.3f}"), TEXT_UNITS):
        assert re.search(r"sampling", u, re.I), (n, u)
    # node, product and period results are never given interval or probability vocabulary
    pat = (r"(grid[- ]node|neighbour\w*|grid cell|\bcells?\b|GWA|atlas|wind product|period-selection)[^.;]*"
           r"\b(confidence interval|probabilit|probabilistic|error bars?|standard error|percentile|P90)")
    for n, u in offenders(pat, TEXT_UNITS):
        assert NEG.search(u) or "only probabilistic" in u or "Probabilistic interval (the only one)" in u, (n, u)


def test_categories_are_kept_apart_everywhere():
    assert "they are not combined into one uncertainty interval" in flat("00_abstract.md")
    assert "merged into one interval" in flat("01_introduction.md")
    assert "They are not combined into a single interval" in flat("04_results.md")
    disc = flat("05_discussion.md")
    assert "## 5.5. Why the six categories are not combined" in read("05_discussion.md")
    for phrase in ("Only the sampling confidence interval has a probabilistic meaning", "they are not independent",
                   "would count the same deficiency twice", "not exhaustive",
                   "The period result partly overlaps category 1"):
        assert phrase in disc, phrase
    assert "instead of merging them into one interval" in flat("06_conclusion.md")
    assert "sampling confidence interval of the 31-year mean is smaller than the node, product and loss effects" \
        in disc


def test_discussion_separates_findings_from_hypotheses():
    disc = flat("05_discussion.md")
    heads = re.findall(r"(?m)^## 5\.(\d)\.", read("05_discussion.md"))
    assert heads == [str(i) for i in range(1, 10)]
    for phrase in ("What is observed is a difference, not a demonstrated shift",
                   "Whether the recent years reflect more than sampling variability is not demonstrated",
                   "This study has no means of separating the two", "It is a plausible hypothesis",
                   "Neither is established here", "A genuine east–west gradient", "One observation is suggestive",
                   "It does not show which product is closer to the truth",
                   "Nor is the 1994–2024 mean a prediction", "is an assumption that this study cannot test",
                   "It does not show that the overlapping part is unavailable",
                   "not as a forecast of emissions", "None of these steps would remove the need for measurements"):
        assert phrase in disc, phrase


# ------------------------------------------- 5. status, capacity and CO2 wording
def test_candidate_status_and_conditional_capacity_everywhere():
    assert "candidate areas" in flat("00_abstract.md") and "candidate area" in flat("01_introduction.md")
    assert "It is not an approved project, and no capacity has been assigned to it" in flat("01_introduction.md")
    for n, u in offenders(r"(allocat|assign)\w* [^.]*\bSaros|capacity has been assigned", TEXT_UNITS):
        assert re.search(r"\b(not|no|if|were|future|conditional)\b", u, re.I), (n, u)
    for n, u in offenders(r"1 000 MWe|997\.5|≈ ?1 GW|105 turbines", TEXT_UNITS):
        assert re.search(r"draft|conditional|illustrative|\bif\b|any one", u, re.I), (n, u)
    for n in NARRATIVE:
        assert not re.search(r"997\.5|247|503\.5|\bS[1234]\b(?! )", re.sub(r"Tables? S\d+", "", flat(n))), n
    for pat in (r"\b(is|are|be) (prohibited|forbidden|permitted|allowed)\b", r"cannot be built", r"can be built"):
        assert not offenders(pat), offenders(pat)[:1]


def test_co2_is_an_accounting_equivalent_everywhere():
    for n, u in offenders(r"\bavoid"):
        assert re.search(r"accounting|convention", u, re.I), (n, u)
    for pat in (r"\bavoids\b", r"\b(will|would|could) avoid\b", r"\bdisplaces\b", r"\bwill displace\b",
                r"emission-free", r"\boffsets?\b", r"carbon[- ]positive", r"\bsaves?\b", r"decarbonis"):
        assert not offenders(pat), offenders(pat)[:1]
    for n, u in offenders(r"displac"):
        assert NEG.search(u), (n, u)
    assert "CO₂" not in read("00_abstract.md") and "carbon" not in read("00_abstract.md").lower()
    assert "accounting equivalent" in flat("01_introduction.md")
    assert "## 5.8. Why the CO₂ values are accounting equivalents" in read("05_discussion.md")
    assert "factor for 2023 cannot stand for them" in flat("05_discussion.md")


def test_abstract_scope_and_length():
    a = read("00_abstract.md").split("## Abstract", 1)[1].split("**Keywords:**")[0]
    words = len(a.split())
    assert 200 <= words <= 320, words
    for phrase in ("candidate areas", "ERA5", "1994–2024", "hour by hour", "sampling confidence interval", "11-year",
                   "neighbouring ERA5 output nodes", "Global Wind Atlas", "No result is validated", "should be reported"):
        assert phrase in " ".join(a.split()), phrase
    assert not re.search(r"MWe|tender|scenario", a)


# ------------------------------------------------------------ 6. Yildirim (2023)
def test_yildirim_is_discussed_within_the_verified_limits():
    """Post-freeze literature correction (16 November 2026): the full text was obtained and read by the
    author. The study is described, distinguished from this paper and not compared numerically."""
    hits = [(n, u) for n, u in PROSE_UNITS if "Yildirim" in u]
    assert hits and {n for n, _ in hits} == {"01_introduction.md", "05_discussion.md"}
    intro = flat("01_introduction.md")
    for phrase in ("techno-economic feasibility assessment of three candidate regions identified in the 2018 tender process",
                   "two in the Aegean Sea and one in the Black Sea", "including a Saros region",
                   "Wind data were taken from the Global Wind Atlas", "a turbine layout, the annual energy production",
                   "capital and operating expenditure, the levelised cost of energy and the net present value",
                   "The present study does not repeat such an assessment",
                   "is given as 367.62 km² (its Table 3)",
                   "whether the two areas overlap could not be established",
                   "the yields and capacity factors of the two studies are not compared here"):
        assert phrase in intro, phrase
    for bad in ("not available to us", "full text was not", "published abstract does not define", "the first"):
        assert bad not in intro, bad
    block = intro.split("The Gulf of Saros itself has been examined before.")[1].split("These studies share")[0]
    nums = re.findall(r"\d[\d.]*", re.sub(r"\b(19|20)\d\d\b|ERA5", "", block))
    assert set(nums) <= {"367.62", "3", "31", "172.6"}, nums          # area from its Table 3, our polygon, record length
    for bad in (r"capacity factor of", r"GWh", r"MW\b", r"higher than|lower than", r"\bdo not overlap\b"):
        assert not re.search(bad, block), bad
    disc = flat("05_discussion.md")
    assert "such as the feasibility assessment of a Saros region by Yildirim (2023), inherit this unresolved difference" in disc
    row = next(r for r in csv.DictReader(REGISTER.open(encoding="utf-8")) if r["key"] == "yildirim2023")
    assert row["status"] == "V-FT" and "367.62" in row["note"] and "FULL TEXT NOT ACCESSED" not in row["note"]


# --------------------------------------------------------------- 7. references
def _reference_entries():
    out = {}
    for line in read(REFS).split("\n- ")[1:]:
        entry = " ".join(line.split("\n\n")[0].split())
        m = re.match(r"(Official Gazette \d+)", entry)
        if m:
            out[m.group(1)] = entry
            continue
        m = re.match(r"(.+?) \((\d{4}[a-z]?)\)\.", entry)
        assert m, entry
        first = re.split(r",| \(", m.group(1))[0].strip()
        out[f"{first} {m.group(2)}"] = entry
    return out


def _citations():
    cites = set()
    name = r"[A-ZÖÇŞİÜ][\w\-ğüşıöçéİÖÜŞÇĞ]+"
    for n in PROSE + TABLES:
        t = " ".join(strip_math(read(n)).split())
        for inner in re.findall(r"\(([^()]*(?:19|20)\d\d[a-z]?[^()]*)\)", t):
            for part in re.split(r";", inner):
                m = re.fullmatch(rf"\s*((?:{name})(?: {name})*)(?: et al\.| and {name})?,? ((?:19|20)\d\d[a-z]?)\s*",
                                 part)
                if m and not m.group(1).startswith(("Official", "Section", "Table", "Eq")):
                    cites.add(f"{m.group(1)} {m.group(2)}")
        for m in re.finditer(rf"({name})(?: et al\.| and {name})? \(((?:19|20)\d\d[a-z]?)\)", t):
            cites.add(f"{m.group(1)} {m.group(2)}")
        for m in re.finditer(r"Official Gazette (\d{5})", t):
            cites.add(f"Official Gazette {m.group(1)}")
    return cites


def test_every_citation_has_a_reference_and_every_reference_is_cited():
    refs, cites = _reference_entries(), _citations()
    assert len(cites) >= 30
    missing = sorted(c for c in cites if c not in refs)
    assert not missing, f"cited but not in the reference list: {missing}"
    unused = sorted(r for r in refs if r not in cites)
    assert not unused, f"in the reference list but never cited: {unused}"


def test_every_reference_has_an_identifiable_record():
    refs = _reference_entries()
    rows = list(csv.DictReader(REGISTER.open(encoding="utf-8")))
    assert len(rows) == len(refs) == len({r["key"] for r in rows})
    for r in rows:
        assert r["status"] in {"V-FT", "V-AB", "V-MD"} and r["identifier"].strip() and r["verified_how"].strip(), r
    reg_ids = {r["identifier"] for r in rows}
    for key, entry in refs.items():
        doi = re.search(r"doi:(\S+)", entry)
        url = re.search(r"https?://\S+", entry)
        if doi:
            assert f"doi:{doi.group(1).rstrip('.')}" in reg_ids, key
        elif url:
            assert url.group(0) in reg_ids, key
        else:
            assert key == "Official Gazette 29852", key                 # named in two official documents; no URL yet
    # DOIs that were checked against a registry in an earlier phase are still the ones cited
    inv = {r["doi_or_url"] for r in csv.DictReader((ROOT / "docs/review/phase5pre_c_reference_inventory.csv")
                                                    .open(encoding="utf-8"))}
    cited_dois = {re.search(r"doi:(\S+)", e).group(1).rstrip(".") for e in refs.values() if "doi:" in e}
    new = {"10.1093/gji/ggab462", "10.1016/j.apenergy.2016.07.058", "10.12770/cf51df64-56f9-4a99-b1aa-36b8d7b743a1",
           "10.1029/2001TC901037", "10.1016/S0025-3227(02)00354-7", "10.5281/zenodo.7970649"}   # verified in 5B-2
    assert cited_dois <= inv | new, sorted(cited_dois - inv - new)


# ------------------------------------------------------------- 8. declarations
def test_author_dependent_declarations_are_marked_not_invented():
    d = read("07_declarations.md")
    sections = {h: b for h, b in re.findall(r"(?m)^## (.+?)\n(.*?)(?=^## |\Z)", d, flags=re.S)}
    for h in ("Data availability", "Code availability", "Funding", "Conflicts of interest", "Author contributions",
              "Use of generative artificial intelligence", "Acknowledgements"):
        assert h in sections, h
        assert "[AUTHOR TO CONFIRM" in sections[h], h
    for h in ("Funding", "Conflicts of interest", "Author contributions", "Acknowledgements"):
        body = " ".join(sections[h].split())
        assert body.startswith("[AUTHOR TO CONFIRM") and body.endswith("]"), h       # nothing asserted
    for pat in (r"declare[s]? no", r"no (competing|conflict)", r"received no", r"funded by", r"\bgrant\b",
                r"\bTÜBİTAK\b", r"University"):
        assert not re.search(pat, d, re.I), pat
    da = " ".join(sections["Data availability"].split())
    for phrase in ("doi:10.24381/cds.adbb2d47", "Open-Meteo", "not bit-identical", "SHA-256",
                   "modified Copernicus Climate Change Service information"):
        assert phrase in da, phrase
    assert "byte for byte" in " ".join(sections["Code availability"].split())


# --------------------------- 9. Sections 2-4, tables and results unchanged in substance
def _git_show(path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{PHASE_5B1_COMMIT}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


# Phase 5C-1 added figure call-outs; Phase 5C-2 renumbered the main tables in the order of first
# citation (5B-1 numbers 1, 3, 4, 2, 5, 6 became 1-6) and cited Supplementary Tables S1, S12 and S13
# in Methods. These are the only permitted changes to the text of Sections 2 to 4.
CALLOUT = re.compile(r" \((?:see also )?Fig\. \d[a-z]?\)|; Fig\. \d[a-z]?(?=\))|(?<=\()Fig\. \d[a-z]?; ")
SUPP_CALLOUT = re.compile(r" \(Supplementary Table S(?:1|12|13)\)|; Supplementary Table S(?:1|12|13)(?=\))")
TABLE_5B1_NUMBER = {1: 1, 2: 3, 3: 4, 4: 2, 5: 5, 6: 6}        # current number -> Phase 5B-1 number


LCA_CITATION = " (Schlömer et al., 2014; Bonou et al., 2016)"   # Phase 5C-2: cited in the main text too


def strip_callouts(text: str) -> str:
    text = SUPP_CALLOUT.sub("", CALLOUT.sub("", text)).replace(LCA_CITATION, "")
    return re.sub(r"\bTable ([1-6])\b", lambda m: f"Table {TABLE_5B1_NUMBER[int(m.group(1))]}", text)


def tables_in_5b1_order(text: str, remap: bool = True) -> str:
    head, *blocks = re.split(r"(?m)^(?=## Table \d\.)", text)
    if remap:
        blocks = [re.sub(r"^## Table (\d)\.", lambda m: f"## Table {TABLE_5B1_NUMBER[int(m.group(1))]}.", b)
                  for b in blocks]
    blocks = [b if b.endswith("\n") else b + "\n" for b in blocks]
    return head + "".join(sorted(blocks, key=lambda b: int(b[9])))


def _numbers(text: str) -> list[str]:
    body = re.sub(r"(?m)^## Table [S\d]+\..*$", "", text)                 # table titles carry labels only
    return sorted(t.strip() for t in re.findall(r"[−+-]?\d[\d  ]*(?:\.\d+)?", body))


def test_table_numbers_are_unchanged_since_phase_5b1():
    """Phase 5D-1 changed wording, labels and citations, never a tabulated value.
    Main tables: the multiset of numbers equals that of Phase 5B-1 (the tables were renumbered
    in Phase 5C-2 and labels reworded in 5D-1). Supplementary tables: equal apart from the added
    column of window half-widths in Table S6, which comes from rolling_11yr_windows.csv."""
    old_main = _git_show("manuscript/tables.md")
    old_sup = _git_show("manuscript/supplementary_tables.md")
    if old_main is None or old_sup is None:
        pytest.skip("git history not available")
    strip_num = lambda t: re.sub(r"\bTable [S]?\d+\b", "", t)            # noqa: E731
    new_main = re.sub(r"Category 3 partly overlaps category 1.*?uncertainty\.", "", read("tables.md"))
    new_main = re.sub(r"the 90 % sampling half-width of the mean of the 2014–2024 window is ±\d\.\d %", "", new_main)
    new_main = new_main.replace("(0.25° output grid)", "").replace("Hansen et al., 2025", "")   # labels
    assert _numbers(strip_num(new_main)) == _numbers(strip_num(old_main))
    roll = pd.read_csv(REV / "rolling_11yr_windows.csv")
    extra = [f"{v:.1f}" for v in roll["t90_half_width_rel_pct"]]
    new_sup = read("supplementary_tables.md").replace(" (Schlömer et al., 2014)", "").replace("; TEDAŞ, 2025", "")  # 5B-2 citations
    got = _numbers(strip_num(new_sup))
    for e in extra + ["90", "11"]:
        got.remove(e)
    want = _numbers(strip_num(old_sup.replace("(2008–2017)", "(mesoscale period 2008–2017)")))
    assert got == want


def test_numerical_results_are_untouched():
    t = _load("t5b1", "tests/test_manuscript_5b1.py")
    for name, digest in t.RESULTS_SHA256.items():
        assert hashlib.sha256((REV / name).read_bytes()).hexdigest() == digest, name
    arch = ROOT / "results/archive/baseline_2014_2024_cds/SHA256SUMS"
    assert hashlib.sha256(arch.read_bytes()).hexdigest() == t.ARCHIVE_SHA256SUMS
