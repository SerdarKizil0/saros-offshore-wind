"""
Phase 5B-0 — sensitivity outputs in results/revised/, the corrected national-consumption
denominator, and the synchronised revision plan.
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config.wind_data import PRIMARY, NODE_SERIES, ERA5_LAND_SEA_MASK  # noqa: E402
from config.emissions import TR_GROSS_CONSUMPTION_2024  # noqa: E402

REV = ROOT / "results" / "revised"
ARCH = ROOT / "results" / "archive" / "baseline_2014_2024_cds"
ADDENDUM = ROOT / "docs/review/PHASE5B0_REVISION_PLAN_ADDENDUM.md"
PLAN_5A = ROOT / "docs/review/PHASE5A_MANUSCRIPT_REVISION_PLAN.md"
PRE_5B0_COMMIT = "2646477"                     # last commit before Phase 5B-0
NEW_FILES = ["period_sensitivity.json", "rolling_11yr_windows.csv", "node_sensitivity.json",
             "wind_product_discrepancy.json", "sensitivity_index.json"]
# SHA-256 of the result files as committed before Phase 5B-0 (results/revised/MANIFEST.json at 2646477).
# Every primary energy and emissions file must be byte-identical; only scenarios.json may differ.
PRE_5B0_SHA256 = {
    "wind_resource.json": "82558d7bfb2acd1f02b914277064791258d7472e0feed5d0800016283c46d704",
    "energy_yield.json": "b047e0371dee1f618a1f9f6c880628eee865caff28ab736d6ce39585fb58f26e",
    "weibull_crosscheck.json": "0ca112e810bcd0a1602df457f668602d07a412fa1eb4f2ff0704326e58078928",
    "interannual_and_sampling.json": "a2daaf26eea3a45a2fb55c4d9b343e940d0aba2fcc1094591e2e679329fbf764",
    "annual_energy.csv": "fe438c18f5de622c71825ba8a1e9eb9e6fa046f6b48b6d48265df9ee6e977790",
    "wind_speed_sensitivity.json": "b042dad665cb8992893ac5272934669ce9bc3eddec8060cb058693a6b74e2df8",
    "loss_scenarios.json": "c0f7cf2dfb34ad815a544761a1cb98e7b6e78091824a2011ebbc986da0ed0e8d",
    "emissions.json": "238734ce3b5bedb786912a76250425b1009c5cc70a8733d9098c2e07299ad44c",
    "site_screening.json": "b191405ffdff431efc5c7e0834cd316e98ea1992cfeb691c0e7cd1654ba6657b",
    "input_provenance.json": "2384ac9c1ec8f27bab08edfabe5e3b385a04ec2b138b34ea32c12f6e21b5845a",
}
ARCHIVE_SHA256SUMS = "44877f79edd43fa8d6e729c60830c5ac5fa3de430aaf3fabe64dd2f4fbe8ac22"
ETA = 0.92 * 0.95 * 0.97
CATEGORIES = ["sampling_uncertainty_of_period_mean", "interannual_variability", "period_selection_sensitivity",
              "grid_node_sensitivity", "wind_product_discrepancy", "loss_assumption_sensitivity"]


def J(name):
    return json.loads((REV / name).read_text())


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def _leaves(d, path=()):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from _leaves(v, path + (k,))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            yield from _leaves(v, path + (i,))
    else:
        yield path, d


def _keys(d):
    if isinstance(d, dict):
        for k, v in d.items():
            yield k
            yield from _keys(v)
    elif isinstance(d, list):
        for v in d:
            yield from _keys(v)


# ---------------------------------------------- independent recomputation (numpy only)
def _independent(lon: float, y0: int, y1: int, alpha: float | None = None) -> dict:
    st = pd.read_parquet(ROOT / f"data/external/phase5pre/era5_openmeteo_40.50N_{lon:.2f}E_1979_2024.parquet")
    t = pd.date_range("1979-01-01", periods=len(st), freq="h")
    sel = (t.year >= y0) & (t.year <= y1)
    u10, u100 = st.U10.to_numpy()[sel] / 100.0, st.U100.to_numpy()[sel] / 100.0
    if alpha is None:
        m = (u10 > 1.0) & (u100 > 1.0)
        a = np.log(u100[m] / u10[m]) / np.log(10.0)
        lo, hi = np.percentile(a, [1, 99])
        alpha = a[(a >= lo) & (a <= hi)].mean()
    u = u100 * 1.05 ** alpha
    from config.turbine import POWER_CURVE_MS_KW
    v, p = np.array(POWER_CURVE_MS_KW).T
    pw = np.interp(u, v, p, left=0, right=0)
    pw[(u < 3.5) | (u >= 25.0)] = 0.0
    return {"alpha": alpha, "gross_cf": pw.sum() / (9500.0 * len(pw)), "n": int(sel.sum()),
            "u100": u100.mean()}


# ------------------------------------------- 1. primary values unchanged by this phase
@pytest.mark.parametrize("name", sorted(PRE_5B0_SHA256))
def test_primary_result_files_are_byte_identical_to_pre_5b0(name):
    assert sha(REV / name) == PRE_5B0_SHA256[name], f"{name} changed in Phase 5B-0"


def test_scenarios_changed_only_in_the_consumption_share():
    r = subprocess.run(["git", "show", f"{PRE_5B0_COMMIT}:results/revised/scenarios.json"], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("git history not available")
    old, new = dict(_leaves(json.loads(r.stdout))), dict(_leaves(J("scenarios.json")))
    allowed = lambda p: p[0] == "consumption_reference" or "consumption_pct" in str(p[-1])
    assert {p for p in old if not allowed(p)} == {p for p in new if not allowed(p)}
    for p, v in old.items():
        if not allowed(p):
            assert new[p] == v, p


# ------------------------------------------------------- 2. consumption denominator
OLD_DENOMINATOR = r"(?<![\d.])347\.9(?!\d)"      # as a number of its own, not inside e.g. 2347.98...


def test_consumption_denominator_is_the_official_gross_value():
    c = J("scenarios.json")["consumption_reference"]
    assert c["gwh"] == 353579.8 == TR_GROSS_CONSUMPTION_2024["gwh"] and c["year"] == 2024
    assert "gross" in c["definition"] and "TEDAŞ" in c["source"] and c["document_sha256"].startswith("72f02193")
    k = c["components_gwh"]
    assert k["gross_generation"] + k["imports"] - k["exports"] == pytest.approx(c["gwh"], abs=0.15)
    for r in J("scenarios.json")["scenarios"]:
        assert "share_of_2024_consumption_pct" not in r
        assert r["share_of_2024_gross_consumption_pct"] == pytest.approx(r["net_energy_gwh_yr"] / 353579.8 * 100,
                                                                        rel=1e-12)


def test_superseded_denominator_is_not_a_current_value():
    for f in REV.iterdir():
        if f.name == "scenarios.json":
            c = json.loads(f.read_text())
            assert "347.9" in c["consumption_reference"]["note"]          # named only as superseded
            c["consumption_reference"].pop("note")
            assert not re.search(OLD_DENOMINATOR, json.dumps(c))
        else:
            assert not re.search(OLD_DENOMINATOR, f.read_text()), f.name
    src = (ROOT / "config/emissions.py").read_text()
    assert "TR_TOTAL_CONSUMPTION_TWH_2024" not in src.split("# LEGACY")[0]


# ---------------------------------------------- 3. node comparison, 1994-2024
@pytest.mark.parametrize("key", ["W", "C", "E"])
def test_node_comparison_reproduced_independently(key):
    spec, node = NODE_SERIES[key], J("node_sensitivity.json")["nodes"][key]
    ind = _independent(spec.node_lon, 1994, 2024)
    assert (node["lat"], node["lon"]) == (40.5, spec.node_lon)
    assert node["n_hours_used"] == ind["n"] == 31 * 8760 + 8 * 24
    assert node["data_period_used"] == "1994-01-01 00:00 to 2024-12-31 23:00 UTC"
    assert node["sha256"] == spec.sha256 == sha(spec.path)
    assert node["alpha_node"] == pytest.approx(ind["alpha"], rel=1e-12)
    assert node["gross_cf"] == pytest.approx(ind["gross_cf"], rel=1e-12)
    assert node["net_gwh_per_mw"] == pytest.approx(ind["gross_cf"] * ETA * 8.766, rel=1e-12)
    assert node["mean_U100_ms"] == pytest.approx(ind["u100"], rel=1e-12)
    base = _independent(26.25, 1994, 2024)
    assert node["energy_rel_to_primary_node_pct"] == pytest.approx((ind["gross_cf"] / base["gross_cf"] - 1) * 100,
                                                                  abs=1e-9)


def test_primary_node_equals_the_primary_estimate_and_land_sea_mask_is_reported():
    n = J("node_sensitivity.json")
    c = n["nodes"]["C"]
    assert c["is_primary_node"] and c["net_gwh_per_mw"] == pytest.approx(J("energy_yield.json")["net"]["gwh_per_mw"],
                                                                         rel=1e-12)
    assert n["assumptions"]["period"] == "1994-2024" and n["reference_baseline"]["period"] == "1994-2024"
    lsm = json.loads(ERA5_LAND_SEA_MASK[0].read_text())
    grid = np.array(lsm["land_sea_mask"])
    for k, r in n["nodes"].items():
        i, j = lsm["latitude"].index(40.5), lsm["longitude"].index(r["lon"])
        assert r["era5_land_sea_mask_fraction"] == pytest.approx(float(grid[i, j]), abs=1e-12)
        assert r["inside_polygon"] is False
    assert n["nodes"]["W"]["classification_from_era5_land_sea_mask"].startswith("offshore")
    assert n["nodes"]["C"]["classification_from_era5_land_sea_mask"].startswith("coastal")
    assert sum(r["polygon_share_nearest_to_node_pct"] for r in n["nodes"].values()) == pytest.approx(100.0)
    # regression anchors of the 1994-2024 comparison (not the older 2014-2024 differences)
    assert n["nodes"]["W"]["energy_rel_to_primary_node_pct"] == pytest.approx(6.70, abs=0.005)
    assert n["nodes"]["E"]["energy_rel_to_primary_node_pct"] == pytest.approx(-8.51, abs=0.005)


def test_nodes_are_neither_averaged_nor_turned_into_bounds():
    n = J("node_sensitivity.json")
    assert "not averaged" in n["label"] and "not confidence bounds" in n["label"] and "not measurements" in n["label"]
    bad = {"average", "averaged", "weighted", "interpolated", "interpolation", "combined", "bound", "bounds",
           "ci90", "p10", "p50", "p90", "confidence", "uncertainty"}
    for k in _keys(n):
        assert not (set(k.lower().split("_")) & bad), k
    assert "never used as a weight" in n["assumptions"]["polygon_share_note"]


# ---------------------------------------------------- 4. period selection, rolling
def test_period_sensitivity_and_rolling_windows():
    per, roll = J("period_sensitivity.json"), pd.read_csv(REV / "rolling_11yr_windows.csv")
    ey = J("energy_yield.json")
    assert per["periods"]["1994-2024"]["net_gwh_per_mw"] == pytest.approx(ey["net"]["gwh_per_mw"], rel=1e-12)
    assert per["assumptions"]["series"]["identical_to_primary_series_over_primary_period"] is True
    alpha = ey["input"]["alpha_hub_extrapolation"]
    for label in ("1979-2024", "2014-2024", "2008-2017"):
        y0, y1 = map(int, label.split("-"))
        ind = _independent(26.25, y0, y1, alpha)
        assert per["periods"][label]["gross_cf"] == pytest.approx(ind["gross_cf"], rel=1e-12)
        assert per["periods"][label]["energy_change_vs_reference_pct"] == pytest.approx(
            (ind["gross_cf"] / ey["gross_cf"] - 1) * 100, abs=1e-9)
    assert list(roll.start_year) == list(range(1979, 2015)) and (roll.end_year - roll.start_year == 10).all()
    assert int(roll.within_primary_period.sum()) == 21
    last = roll[roll.start_year == 2014].iloc[0]
    assert last.net_gwh_per_mw == pytest.approx(per["periods"]["2014-2024"]["net_gwh_per_mw"], rel=1e-9)
    assert int(last.rank_from_lowest_within_primary_period) == 21 and int(last.rank_from_lowest_all_windows) == 36
    assert last.net_gwh_per_mw == roll.net_gwh_per_mw.max()
    w = _independent(26.25, 1999, 2009, alpha)
    assert roll[roll.start_year == 1999].iloc[0].gross_cf == pytest.approx(w["gross_cf"], rel=1e-9)
    rw = per["rolling_windows"]
    assert rw["within_primary_period"]["window_2014_2024_rank_from_lowest"] == 21
    assert rw["within_primary_period"]["n_windows"] == 21 and rw["all_windows"]["n_windows"] == 36
    assert rw["all_windows"]["window_2014_2024_is_highest"] is True
    assert "not independent" in rw["note"]


# ------------------------------------------------------------ 5. wind product
def test_wind_product_discrepancy_keeps_periods_and_does_not_rescale():
    w = J("wind_product_discrepancy.json")
    assert w["products"]["gwa4"]["period"] == "2008-2017"
    assert w["products"]["era5"]["periods_used"] == ["1994-2024", "2008-2017"]
    for phrase in ("not ground truth", "not a bias estimate", "not rescaled", "disagreement between two models"):
        assert phrase in w["label"], phrase
    pv = w["polygon_vs_primary_node"]
    g = pv["gwa4_polygon_mean_100m_ms"]
    assert pv["era5_node_U100_ms"]["1994-2024"] == pytest.approx(J("wind_resource.json")["U100"]["mean_ms"], rel=1e-12)
    assert pv["era5_node_U100_ms"]["2008-2017"] == pytest.approx(_independent(26.25, 2008, 2017)["u100"], rel=1e-12)
    assert pv["ratio_gwa_to_era5"]["era5_1994-2024"] == pytest.approx(g / pv["era5_node_U100_ms"]["1994-2024"])
    assert pv["ratio_gwa_to_era5"]["era5_2008-2017_period_matched"] == pytest.approx(
        g / pv["era5_node_U100_ms"]["2008-2017"])
    case = next(c for c in J("wind_speed_sensitivity.json")["cases"] if "GWA" in c["case"])
    esc = w["energy_sensitivity_if_primary_hours_were_scaled"]
    assert esc["by_ratio_era5_1994-2024"]["speed_factor"] == pytest.approx(case["speed_factor"], rel=1e-12)
    assert esc["by_ratio_era5_1994-2024"]["aep_change_vs_primary_pct"] == pytest.approx(
        case["aep_change_vs_baseline_pct"], abs=1e-9)
    assert "Not adopted and not a correction" in esc["label"]
    # the primary estimate itself is untouched (sha pin above) and equals the reference baseline here
    assert w["reference_baseline"]["net_gwh_per_mw"] == J("energy_yield.json")["net"]["gwh_per_mw"]


# ------------------------------------------- 6. categories are not conflated
def test_six_categories_are_distinct_and_not_combinable():
    idx = J("sensitivity_index.json")
    assert [c["category"] for c in idx["categories"]] == CATEGORIES
    assert idx["combinable_into_one_interval"] is False and "NOT components" in idx["label"]
    assert [c["category"] for c in idx["categories"] if c["is_probabilistic_interval"]] == [CATEGORIES[0]]
    for c in idx["categories"]:
        assert (REV / Path(c["file"]).name).exists(), c["file"]
    prefix = {"period_sensitivity.json": "PERIOD-SELECTION SENSITIVITY", "node_sensitivity.json":
              "GRID-NODE SENSITIVITY EXPERIMENT", "wind_product_discrepancy.json": "WIND-PRODUCT DISCREPANCY",
              "loss_scenarios.json": "LOSS SCENARIOS", "wind_speed_sensitivity.json": "SENSITIVITY EXPERIMENTS"}
    for f, p in prefix.items():
        assert J(f)["label"].startswith(p), f
    s = J("interannual_and_sampling.json")
    assert s["sampling_ci_of_period_mean"]["label"].startswith("SAMPLING")
    assert s["observed_interannual_variability"]["label"].startswith("OBSERVED")
    # no percentile or interval vocabulary in the sensitivity files
    for f in ("period_sensitivity.json", "node_sensitivity.json", "wind_product_discrepancy.json"):
        d = J(f)
        assert d["category"] in CATEGORIES[2:5]
        for k in _keys(d):
            kl = k.lower()
            assert not re.search(r"(^|_)(p10|p50|p90|ci90|uncertainty|confidence_interval)(_|$)", kl), (f, k)


def test_index_headlines_equal_the_source_files():
    idx = {c["category"]: c["headline"] for c in J("sensitivity_index.json")["categories"]}
    s = J("interannual_and_sampling.json")
    assert idx[CATEGORIES[0]]["t90_net_gwh_per_mw"] == s["sampling_ci_of_period_mean"]["primary_t_interval_90"][
        "net_gwh_per_mw"]
    assert idx[CATEGORIES[1]]["annual_net_cov_pct"] == s["observed_interannual_variability"]["annual_net_cf_cov_pct"]
    per = J("period_sensitivity.json")["periods"]
    assert idx[CATEGORIES[2]]["energy_change_vs_reference_pct"]["2014-2024"] == \
        per["2014-2024"]["energy_change_vs_reference_pct"]
    nodes = J("node_sensitivity.json")["nodes"]
    assert idx[CATEGORIES[3]]["energy_rel_to_primary_node_pct"] == {
        k: nodes[k]["energy_rel_to_primary_node_pct"] for k in ("W", "E")}
    w = J("wind_product_discrepancy.json")["polygon_vs_primary_node"]["ratio_gwa_to_era5"]
    assert idx[CATEGORIES[4]]["ratio_gwa_polygon_to_era5_node"] == w
    ls = J("loss_scenarios.json")["scenarios"]
    assert idx[CATEGORIES[5]]["rel_to_nominal_pct"] == {k: v["rel_to_nominal_pct"] for k, v in ls.items()}


# ------------------------------------------------- 7. generated by the pipeline
def test_sensitivity_outputs_are_pipeline_products():
    src = (ROOT / "scripts/run_revised_pipeline.py").read_text()
    assert '"scripts/08_sensitivity_representativeness.py"' in src
    m = J("MANIFEST.json")
    for f in NEW_FILES:
        assert m["files"][f]["sha256"] == sha(REV / f), f
    sens = m["inputs"]["sensitivity_only"]
    assert {k: v["sha256"] for k, v in sens["node_series"].items()} == {k: s.sha256 for k, s in NODE_SERIES.items()}
    assert m["inputs"]["wind_series_sha256"] == PRIMARY.sha256                  # primary input unchanged


def test_fresh_computation_equals_committed_sensitivity_outputs(tmp_path):
    s08 = _load("s08_fresh", "scripts/08_sensitivity_representativeness.py")
    s08.write(s08.compute(), tmp_path)
    for f in NEW_FILES:
        assert (tmp_path / f).read_bytes() == (REV / f).read_bytes(), f


def test_sensitivity_inputs_are_pinned(tmp_path):
    s08 = _load("s08_pin", "scripts/08_sensitivity_representativeness.py")
    bad = tmp_path / "x.json"
    bad.write_bytes(ERA5_LAND_SEA_MASK[0].read_bytes() + b" ")
    with pytest.raises(ValueError, match="sha256"):
        s08._verified(bad, ERA5_LAND_SEA_MASK[1])


# --------------------------------------------------------- 8. archive untouched
def test_historical_archive_untouched():
    assert sha(ARCH / "SHA256SUMS") == ARCHIVE_SHA256SUMS
    for line in (ARCH / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        assert sha(ARCH / name) == digest, name
    assert json.loads((ARCH / "scenarios.json").read_text())["consumption_reference"]["twh"] == 347.9
    r = subprocess.run(["git", "status", "--porcelain", "--", str(ARCH.relative_to(ROOT))], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode == 0:
        assert r.stdout.strip() == ""


# ------------------------------------------- 9. revision plan is synchronised
OBSOLETE = [r"2\.4274", r"2\.427(?!\d)", r"27\.69", r"1[  ]?515", r"2\.334", r"2\.520", r"347\.9", r"2\.912",
            r"23\.06", r"27\.20", r"32\.66", r"17\.9", r"96[  ]?432"]


def _sections(text: str) -> dict:
    parts = re.split(r"(?m)^## ", text)
    return {p.split("\n", 1)[0].strip(): p for p in parts[1:]}


def test_addendum_states_the_current_baseline_from_the_result_files():
    sec = _sections(ADDENDUM.read_text())
    base = sec["1. Authoritative baseline"]
    ey, s, em = J("energy_yield.json"), J("interannual_and_sampling.json"), J("emissions.json")
    lo, hi = s["sampling_ci_of_period_mean"]["primary_t_interval_90"]["net_gwh_per_mw"]
    co2 = em["primary_avoided_operational_co2"]["t_co2_per_mw_yr"]
    for token in (f"{ey['net']['gwh_per_mw']:.4f}", f"{ey['net_cf'] * 100:.2f} %", f"{lo:.3f}–{hi:.3f}",
                  f"{co2:,.1f}".replace(",", " "), "1994–2024", "40.50° N, 26.25° E",
                  "not bit-identical to CDS"):
        assert token in base, token
    sens = sec["4. Promoted sensitivity evidence (now in `results/revised/`)"]
    n, per = J("node_sensitivity.json")["nodes"], J("period_sensitivity.json")["periods"]
    w = J("wind_product_discrepancy.json")["polygon_vs_primary_node"]["ratio_gwa_to_era5"]
    fmt = lambda v: f"{v:+.2f}".replace("-", "−")
    for token in (fmt(n["W"]["energy_rel_to_primary_node_pct"]), fmt(n["E"]["energy_rel_to_primary_node_pct"]),
                  fmt(per["2014-2024"]["energy_change_vs_reference_pct"]),
                  f"{w['era5_1994-2024']:.3f}", f"{w['era5_2008-2017_period_matched']:.3f}",
                  f"{n['W']['net_gwh_per_mw']:.4f}", f"{n['E']['net_gwh_per_mw']:.4f}",
                  "not averaged", "not confidence bounds", "not rescaled"):
        assert token in sens, token
    cons = sec["5. Superseded national-consumption denominator"]
    share = J("scenarios.json")["scenarios"][2]["share_of_2024_gross_consumption_pct"]
    assert "353 579.8 GWh" in cons and f"{share:.3f} %" in cons


def test_no_obsolete_5a_value_is_presented_as_current():
    text = ADDENDUM.read_text()
    for title, body in _sections(text).items():
        allowed = "Superseded" in title or "Retired" in title
        for pat in OBSOLETE:
            if re.search(pat, body):
                assert allowed, f"obsolete value /{pat}/ in section '{title}'"
    head = text.split("\n## ", 1)[0]
    assert not any(re.search(p, head) for p in OBSOLETE)
    # the 5A plan itself points to the addendum before any of its values
    plan = PLAN_5A.read_text()
    banner = plan.split("\n*14 November 2026.", 1)[0]
    assert "Superseded in part (Phase 5B-0" in banner and "PHASE5B0_REVISION_PLAN_ADDENDUM.md" in banner
    # the archive values named as superseded really are the archived ones
    arch = json.loads((ARCH / "energy_yield.json").read_text())
    assert f"{arch['net']['gwh_per_mw']:.4f}" == "2.4274" and "2.4274" in _sections(text)["2. Superseded 5A values"]
