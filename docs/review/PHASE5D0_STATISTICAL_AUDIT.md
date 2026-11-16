# Phase 5D-0 — Statistical and technical audit of the reviewer's central criticisms

*16 November 2026. Read-only audit at commit `4a46a0a`. No manuscript text, figure,
model, result file or build script was changed, and no file under `results/` was written.
All calculations use the committed inputs and the production functions of
`scripts/04_fit_weibull_aep.py` and `scripts/08_sensitivity_representativeness.py`. The
audit script is reproduced in the Appendix; it was run from a scratch directory and
prints to the console only. Numbers are given to the precision needed for a decision.
They are audit values, not authoritative results.*

The review audited here is the "independent-style" review in this conversation, which
returned MAJOR REVISION. That review was produced in the same working session that
prepared the manuscript. It is therefore not a fully independent review (see the plan,
§6).

---

## A. Reference-period statistics (review weakness Z1)

### A1. Verification of the reviewer's numbers

| Reviewer claim | Audit value | Verdict |
|---|---|---|
| 31-year mean, 90 % t-interval ±2.3 % | ±2.27 % (n = 31, df 30); equals `interannual_and_sampling.json` | **Verified** |
| 2014–2024 window: +3.1 % above the 31-year mean | +3.11 % (mean of annual values) and +3.12 % (pooled CF, as published) | **Verified** |
| 2014–2024 window has its own 90 % interval of about ±3.8 % | ±3.83 %; already stored as `t90_half_width_rel_pct` in `results/revised/rolling_11yr_windows.csv` | **Verified** (no new calculation is needed to report it) |
| Random-year permutation: P(at least one of the 21 windows ≥ +3.1 %) ≈ 0.34 | 0.337 (B = 200 000) | **Numerically verified; wrong null for the question** (A4) |
| OLS trend +2.7 % per decade, p = 0.065 | +2.75 % per decade, p = 0.065; 90 % CI +0.3 to +5.2 % per decade | **Verified** |
| Kendall trend p = 0.052 | τ = 0.247, p = 0.052; Theil–Sen +2.8 % per decade | **Verified** |
| "6 windows above, 15 below" arises from the overlap | Permutation P(≤ 1 sign change among the 21 window anomalies) = 0.23 | **Verified**: the pattern is unremarkable |

### A2. Additional checks (not in the review)

| Check | Value | Meaning |
|---|---|---|
| Non-overlapping comparison: 2014–2024 vs 1994–2013 | difference +4.8 % of the reference; Welch p = 0.089 (two-sided); 90 % CI +0.2 to +9.4 %; Mann–Whitney p = 0.037 | The recent decade is higher than the preceding twenty years. The evidence is moderate, not decisive |
| 2015–2024 (10 years) | +4.96 %, own 90 % half-width ±2.23 % (these years have low scatter) | This difference **exceeds** its own sampling interval. The reviewer's argument "inside its own interval" holds for 2014–2024 but not for 2015–2024 |
| Trend over the longer record 1979–2024 (same node, primary α) | +1.0 % per decade, OLS p = 0.20; Kendall p = 0.14 | Weaker. The 1994–2024 trend depends on the start year |
| 2014–2024 window, permutation null within 1979–2024 | P(last window ≥ observed) = 0.032; P(any of 36 windows ≥ observed maximum) = 0.42 | Same contrast as in A4 |
| Serial correlation of annual yields | lag-1 = −0.08 (raw), −0.22 (detrended); −0.06 over 1979–2024 | No positive persistence |
| Normality of annual yields (Shapiro–Wilk) | p = 0.54 | The t-interval is not contradicted |
| Overlap of adjacent 11-year windows | 10 of 11 years shared; theoretical correlation 0.91 | About 2.8 independent windows in 31 years |
| 1979–2024 annual series reproduces the primary series over 1994–2024 | maximum difference 5 × 10⁻⁹ GWh MW⁻¹ yr⁻¹ | The audit uses the published series |

### A3. Four things that must not be conflated

1. **An observed difference between reference periods** (fact). The 2014–2024 mean is
   3.1 % above the 1994–2024 mean, and 2015–2024 is 5.0 % above it. The manuscript states
   this correctly.
2. **Sampling uncertainty of an estimated mean** (statistics). An 11-year mean has a 90 %
   half-width of about ±3.8–4.1 %, a 31-year mean ±2.3 %.
   - Under stationarity, the 2014–2024 deviation is compatible with the sampling
     variability of an 11-year mean.
   - Hence, under stationarity, "period selection" is to a large extent the same
     phenomenon as category 1 applied to a shorter record, not a separate source of
     uncertainty.
   - The manuscript's comparison of the +3.1 % with the 31-year half-width (Abstract;
     §4.6; §6, first finding) contrasts quantities of different sample sizes. It is not
     wrong as a statement of magnitude, but it suggests a contrast that the data do not
     establish.
3. **Evidence for a temporal trend** (inference). The evidence is weak to moderate:
   - p ≈ 0.05–0.09 over 1994–2024 depending on the test;
   - p ≈ 0.14–0.20 over 1979–2024.
   - It cannot be separated from changes in the assimilated observations, which §5.2
     already states.
4. **Evidence for systematic bias** (claim). None.
   - Under stationarity, a recent 11-year estimate is an unbiased estimator of the
     long-term mean; one realisation being high is not bias.
   - With a trend, "bias" relative to a past mean would be the wrong word as well, since
     the recent level would then be the more relevant one.
   - **Unsupported wording:** "The rolling windows show that this is systematic" (§4.3);
     "a recent decade is not a neutral choice … biased high relative to the long-term mean
     of the same series" (§6, third finding). These must be corrected.

### A4. Is the random-year permutation an appropriate null model?

- **What it tests.** Permuting the 31 annual values tests exchangeability: no trend, no
  persistence, no regime shift. That is a reasonable null for "the window pattern is what
  one random arrangement of these years would produce". Lag-1 autocorrelation is near
  zero, so permutation does not destroy a meaningful dependence structure.
- **The reviewer's statistic.** The probability that *any* of the 21 windows exceeds the
  observed maximum is a scan statistic. It corrects for searching across windows.
- **The 2014–2024 window was not found by searching.** It was the original analysis
  period, used throughout Phases 1–4C before the long record was obtained, and the
  manuscript says so (§3.7). The look-elsewhere correction therefore does not apply to the
  question "is the pre-specified recent window high?".
- **The pre-specified probability** is P(last window ≥ +3.12 %) = 0.041, one-sided, and
  0.032 within 1979–2024.
- **"Highest of all windows"** (§4.3; Fig. 2 caption): P(last window is the maximum) =
  0.10. This is not unusual.
- **Conclusion.** The reviewer used a statistic that understates the evidence for the
  pre-specified window. The correct statistic gives moderate evidence that the recent
  window is high under exchangeability. Neither statistic supports "systematic" or
  "biased". **The permutation test should not be added to the manuscript.** It answers a
  question the manuscript need not ask; the reported per-window intervals and careful
  wording suffice.

### A5. Assumptions behind the confidence interval (Eq. 6)

The t-interval assumes that the 31 annual values are independent draws from one
stationary distribution, and that ERA5 at this node is correct; the second assumption is
already stated.

- Independence is supported (lag-1 ≈ −0.08) and normality is not rejected (p = 0.54).
- Stationarity is not tested, and the 1994–2024 series has a borderline positive trend.
- If a trend exists, the interval still describes the precision of the 1994–2024 mean as
  a summary of those years. It does not describe the precision of a forecast of the next
  25 years.
- §3.6 should add one sentence stating the stationarity assumption. §5.1 already says
  that representativeness for future operation is untested.

### A6. Verdict on A

| Element | Decision | Action |
|---|---|---|
| Wrong comparison basis and wording ("systematic", "biased high") | **Accept** | Manuscript wording; report the 11-year window's own half-width, which already exists in the results |
| Trend not considered | **Partially accept** | One stationarity sentence (§3.6). Optionally a descriptive trend sentence; not required |
| Permutation p ≈ 0.34 as evidence | **Reject** | Wrong null for a pre-specified window |
| Pattern 6 above / 15 below is expected | **Accept** | Remove it as evidence (§5.2) |
| New statistical tests in the manuscript | **Not needed** | Response letter only |

---

## B. ERA5 spatial representation (review weakness Z2)

### B1. Facts

| Quantity | Value | Source and status |
|---|---|---|
| Native ERA5 HRES resolution | TL639 spectral, reduced Gaussian grid, ≈ 31 km | Hersbach et al. (2020); already used in `PHASE5PRE_ERA5_ROBUSTNESS.md` §4.1. The register lists Hersbach (2020) as V-MD (metadata only). **The sentence must be checked against the paper before citation** (low risk) |
| Output grid used | regular 0.25° latitude–longitude, interpolated by ECMWF from the native grid | ARCO-ERA5 0.25° store; Open-Meteo `models=era5` |
| Spacing of the sampled nodes at 40.5° N | 0.25° longitude = 21.2 km (east–west); 0.25° latitude = 27.8 km | Computed |
| Land–sea mask at the primary node | 0.44 (W 0.12, E 0.46) | `era5_land_sea_mask_saros.json` (ARCO-ERA5, 0.25°) |
| True land share inside the 0.25° box around each node (EMODnet DTM) | W 2.0 %, **C 12.8 %**, E 39.6 % | `PHASE5PRE_ERA5_ROBUSTNESS.md` §4.1 |
| Land share of a 0.5° box around C | 41.7 % | Phase 2B |

### B2. Assessment

- **The reviewer's central point is correct.** The 0.25° values are interpolated from a
  coarser native grid, and the sampled nodes (21 km apart) are closer together than the
  native spacing (about 31 km). Adjacent output nodes therefore share native grid points.
  They are neither independent samples nor values for disjoint 0.25° cells.
- **The repository's own evidence confirms it.** The mask value at the primary node (0.44)
  is far above the actual land share of its 0.25° box (12.8 %). It is close to the land
  share of a 0.5° box (41.7 %), which is what interpolation from an approximately 31 km
  native field would produce.
- **The manuscript's reading of 0.44 as "the land fraction of the cell" is therefore
  wrong**, even though the mask value itself is correct. The value describes the model's
  smoothed land influence at the output point, which is the more useful interpretation.
- **Node differences are neither purely error nor purely gradient.** They combine:
  (i) a real east–west exposure gradient (the western node lies further into the open
  gulf); (ii) different land influence in the model's smoothed representation; and
  (iii) shear differences (α 0.10 / 0.15 / 0.14).
- The manuscript already calls land influence an unestablished hypothesis (§5.3) and notes
  that land fraction alone does not order the nodes. It does not mention a genuine
  gradient as a co-explanation, and it should.
- **What stands.** The quantitative node results are unaffected: the paired differences are
  +6.7 % ± 0.3 % and −8.5 % ± 0.3 % (90 % half-widths), so they are not sampling noise. So
  is the conclusion that the choice of node matters more than the sampling interval.
- **The nearest-node shares** (27.7 / 62.6 / 9.7 %) are still valid as a geometric
  descriptor. They must be described as "nearest output node", not as "the cell each node
  represents".

### B3. Exact text that must change

| Location | Current text (abridged) | Problem |
|---|---|---|
| Abstract | "the node used is a mixed land–sea cell outside the polygon" | "cell" |
| §1 ¶4 | "Its grid spacing is 0.25°. In a gulf … one grid cell can contain both land and sea" | Output spacing presented as model resolution |
| §2.6 ¶1 | "The grid node nearest the polygon centroid …" and the nearest-node shares | Acceptable; keep |
| §2.6 ¶2 | "A reanalysis value represents a grid cell, not a point. In the static ERA5 land–sea mask the cell of the primary node has a land fraction of 0.44, so the model treats it as a mixed land–sea cell" | Cell interpretation; must mention native resolution and interpolation |
| §3.2 | "provides hourly fields on a 0.25° grid" | Add that the native resolution is about 31 km and that 0.25° is the output grid |
| §3.7, Grid node | "The land fraction of each cell … the three cells differ in their land fraction" | "cell" |
| §4.4 ¶2–3 | "systematic differences between model cells"; "The three cells differ …"; "mixed land–sea cells" | "cell"; no gradient alternative |
| §4.5 | "The size of the disagreement depends on the cell" | Minor; rephrase as "on the node" |
| §5.3 | Heading "Why the grid cell matters …"; "The candidate polygon is about 11 km wide, less than the spacing of the reanalysis grid"; "a statement about a cell that only partly covers the area" | Spacing and cell framing; add gradient alternative |
| §5.4 ¶2 | "smallest at the cell that ERA5 treats as predominantly marine" | Rephrase as "at the node where ERA5's land influence is smallest" |
| §5.6 | "the wind series represents a cell that is partly land" | Rephrase |
| §6, second finding | "the nearest node belongs to a cell that the model treats as partly land" | Rephrase |
| Table 2, row 1 | "ERA5 land–sea mask (land fraction of the cell)" | Becomes "ERA5 land–sea mask at the node (0.25° output grid)" |
| Table 4, row 4 | "neighbouring 0.25° cells" | Becomes "neighbouring 0.25° output nodes" |
| Fig. 1 legend | "ERA5 0.25° cell of each node" | Becomes "Area nearest to each 0.25° output node" |
| Fig. 1 labels | "land fraction 0.12 / 0.44 / 0.46" | Keep, but caption must define it as the land–sea-mask value at the node |
| Fig. 1 caption | "Dash-dotted lines outline the 0.25° cell that each node represents … land fraction of each cell" | Rephrase; add native-resolution note |
| Fig. 3 legend | "Boundary between 0.25° ERA5 cells"; "sea pixels of the node's 0.25° cell" | Rephrase ("box"/"nearest-node boundary") |
| Fig. 3 caption | "the same 0.25° cell"; "boundaries between the three 0.25° cells" | Rephrase |
| Table S11 header | "GWA 0.25° box" | Acceptable; keep |

No result changes. Figures 1 and 3 need regeneration for label text only.

---

## C. Turbine power-curve sensitivity (review weakness Z3)

### C1. What the Phase 2A record contains

`docs/review/PHASE2A_POWER_CURVE.md` §1, §3 and §4 record a **controlled** comparison:

| Element | Original run | Phase 2A run |
|---|---|---|
| Wind data | CDS ERA5, 2014–2024 (`wind_hub_105m.parquet`, sha `0cfc4742…`) | identical file, verified bit for bit |
| Period | 2014–2024 | 2014–2024 |
| Losses | nominal (η = 0.848) | nominal |
| Method | empirical hourly conversion (script 04) | identical |
| **Power curve** | undocumented original curve; rated at 13 m/s; peak electrical Cp 0.564 | OEDB V164/9500; rated at 14 m/s; peak Cp 0.476 |
| Gross AEP per turbine | 30.41 GWh | 27.20 GWh (**−10.55 %**) |
| Net yield (empirical) | 2.714 GWh MW⁻¹ yr⁻¹ | 2.428 GWh MW⁻¹ yr⁻¹ |

The reviewer's figures "2.62 → 2.37" are the farm-level Monte Carlo P50 for scenario S3,
in TWh yr⁻¹ (§4c), from a retired method. The controlled empirical change is −10.55 %
(−9.78 % on the Weibull basis).

### C2. Assessment

- **The −10.5 % is a controlled curve change.** Wind, period, losses and method were
  identical.
- **It is not a measure of uncertainty in the adopted curve.** It compares the adopted
  curve with a retired one that was rejected because it is physically implausible for this
  machine:
  - peak electrical Cp 0.564, against 0.476 for the OEDB digitisation;
  - rated power 1 m/s earlier;
  - undocumented source.
- Using it to bound the digitisation uncertainty of the OEDB curve would treat a known
  error as a plausible alternative. **The reviewer's inference is rejected.**
- **The underlying concern is nonetheless valid.** The adopted curve's uncertainty is not
  quantified anywhere. Exploratory read-only checks on the primary 1994–2024 series
  (gross energy; not authoritative):

| Perturbation of the OEDB curve | Change in gross energy |
|---|---|
| Curve shifted by −0.2 / +0.2 m/s along the speed axis | +4.9 % / −4.8 % |
| Curve shifted by −0.3 / +0.3 m/s | +7.4 % / −7.1 % |
| Power scaled by 0.97 / 1.03 (capped at rated power) | −3.0 % / +2.5 % |

- A plausible digitisation tolerance (a few tenths of m/s or a few per cent of power)
  moves the yield by about 3–5 %. That is comparable to or larger than the sampling
  half-width, smaller than the node differences, and well below the 10 % the reviewer
  implied.
- **The specific rated power is verified:** 9.5 MW over a 164 m rotor gives 450 W m⁻².
- The claim that turbine choice could matter more than the three examined choices is
  plausible but unverified. It lies outside the paper's stated question, period, node and
  product, and §5.6 already warns against comparing capacity factors across machines.

### C3. Decision

- **No new sensitivity calculation is scientifically necessary** for the paper's existing
  claims. The categories are explicitly limited to those examined.
- Two corrections are needed so that the conclusions do not read as exhaustive:
  - §5.6 and §6 must state that power-curve and turbine-choice uncertainty was not
    quantified;
  - the first finding of §6 ("the sampling interval is the smallest of the categories
    examined") must keep the word "examined" and add that turbine-related uncertainty is
    not among them.
- **Optional (P2).** A one-line curve-shift sensitivity (±0.2 m/s) through the pipeline.
  It would let the text give a number instead of a qualitative statement. If added, it
  must be produced by `scripts/08` and written to `results/revised/`, not taken from this
  audit.

---

## Appendix — audit script (read-only)

Full script as run. It imports the production functions, reads committed inputs only and
prints JSON; it writes no file. To reproduce, save it outside the repository and run it
with Python, giving the repository root as its argument. It has a fixed seed, so the permutation p-values reproduce to about ±0.002.

```python
"""Phase 5D-0 read-only statistical audit. Writes nothing to the repository."""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()   # repository root
sys.path.insert(0, str(ROOT))
def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m
S08 = load("s08", "scripts/08_sensitivity_representativeness.py"); S04 = S08.S04
from config.wind_data import NODE_SERIES
REV = ROOT / "results/revised"
ann = pd.read_csv(REV / "annual_energy.csv").set_index("year")["net_gwh_per_mw_8766h"]
ps = json.load(open(REV / "period_sensitivity.json")); alpha = ps["assumptions"]["alpha"]
ey = json.load(open(REV / "energy_yield.json")); Yref = ey["net"]["gwh_per_mw"]
out = {}

# ---- annual yields 1979-2024 at the primary node (same series, primary alpha) ------------
node = NODE_SERIES["C"] if isinstance(NODE_SERIES, dict) else [s for s in NODE_SERIES if "26.25" in s.rel_path][0]
df = S08.with_hub(S08.load_node(node), alpha)
tab = S08.annual(df); y_all = tab["net_gwh_per_mw_8766h"]
out["check_1994_2024_identical_to_results"] = float(np.max(np.abs(y_all.loc[1994:2024].to_numpy() - ann.to_numpy())))

def ci90(v):
    v = np.asarray(v); n = len(v); hw = stats.t.ppf(0.95, n - 1) * v.std(ddof=1) / np.sqrt(n)
    return v.mean(), hw / v.mean() * 100
y = ann.to_numpy(); yrs = ann.index.to_numpy()
m31, hw31 = ci90(y)
out["mean_1994_2024_annual_values"] = m31; out["Yref_pooled"] = Yref
out["t90_halfwidth_31yr_pct"] = hw31
for a, b in ((2014, 2024), (2015, 2024), (1994, 2013), (2008, 2017)):
    m, hw = ci90(ann.loc[a:b]); out[f"mean_{a}_{b}_rel_to_Yref_pct"] = (m / Yref - 1) * 100; out[f"t90_halfwidth_{a}_{b}_pct"] = hw
# pooled CF of 2014-2024 differs slightly from mean of annual values; report both
out["period_sensitivity_2014_2024_pct"] = ps["periods"]["2014-2024"]["energy_change_vs_reference_pct"]

# ---- difference between the recent window and the rest (non-overlapping comparison) ----
r, rest = ann.loc[2014:2024].to_numpy(), ann.loc[1994:2013].to_numpy()
w = stats.ttest_ind(r, rest, equal_var=False)
d = r.mean() - rest.mean(); se = np.sqrt(r.var(ddof=1) / len(r) + rest.var(ddof=1) / len(rest))
out["diff_2014_2024_minus_1994_2013_pct_of_Yref"] = d / Yref * 100
out["welch_p_two_sided"] = w.pvalue; out["diff_90ci_pct"] = [(d - 1.70 * se) / Yref * 100, (d + 1.70 * se) / Yref * 100]
mw = stats.mannwhitneyu(r, rest, alternative="two-sided"); out["mannwhitney_p_two_sided"] = mw.pvalue

# ---- trend --------------------------------------------------------------------------
def trend(series):
    x, v = series.index.to_numpy(), series.to_numpy()
    lr = stats.linregress(x, v); kt = stats.kendalltau(x, v); ts = stats.theilslopes(v, x)
    return {"ols_pct_per_decade": lr.slope * 10 / v.mean() * 100, "ols_p": lr.pvalue,
            "ols_90ci_pct_per_decade": [(lr.slope - stats.t.ppf(0.95, len(v) - 2) * lr.stderr) * 10 / v.mean() * 100,
                                        (lr.slope + stats.t.ppf(0.95, len(v) - 2) * lr.stderr) * 10 / v.mean() * 100],
            "kendall_tau": kt.statistic, "kendall_p": kt.pvalue, "sen_pct_per_decade": ts.slope * 10 / v.mean() * 100}
out["trend_1994_2024"] = trend(ann); out["trend_1979_2024"] = trend(y_all)
resid = y - np.polyval(np.polyfit(yrs, y, 1), yrs)
out["lag1_raw"] = float(np.corrcoef(y[:-1], y[1:])[0, 1]); out["lag1_detrended"] = float(np.corrcoef(resid[:-1], resid[1:])[0, 1])
out["shapiro_p_1994_2024"] = stats.shapiro(y).pvalue
out["lag1_1979_2024"] = float(np.corrcoef(y_all.to_numpy()[:-1], y_all.to_numpy()[1:])[0, 1])

# ---- rolling windows and permutation nulls -------------------------------------------
def wins(v, L=11):
    c = np.concatenate([[0], np.cumsum(v)]); return (c[L:] - c[:-L]) / L
obs = (wins(y) / m31 - 1) * 100
def sign_changes(rel): s = np.sign(rel); return int(np.sum(s[1:] != s[:-1]))
out["windows_obs_min_max_pct"] = [obs.min(), obs.max()]; out["windows_obs_sign_changes"] = sign_changes(obs)
out["adjacent_window_overlap_corr_theory"] = 10 / 11
rng = np.random.default_rng(2026); B = 200_000
c = dict(max_ge=0, last_ge=0, last_is_max=0, range_ge=0, sc_le=0)
for _ in range(B):
    p = rng.permutation(y); rel = (wins(p) / m31 - 1) * 100
    c["max_ge"] += rel.max() >= obs.max() - 1e-12; c["last_ge"] += rel[-1] >= obs[-1] - 1e-12
    c["last_is_max"] += rel.argmax() == len(rel) - 1; c["range_ge"] += rel.max() - rel.min() >= obs.max() - obs.min() - 1e-12
    c["sc_le"] += sign_changes(rel) <= sign_changes(obs)
out["perm_B"] = B
out["perm_p_any_window_ge_obs_max"] = c["max_ge"] / B
out["perm_p_last_window_ge_obs"] = c["last_ge"] / B
out["perm_p_last_window_is_max"] = c["last_is_max"] / B
out["perm_p_range_ge_obs"] = c["range_ge"] / B
out["perm_p_sign_changes_le_obs"] = c["sc_le"] / B
# 1979-2024: same tests on 36 windows
ya = y_all.to_numpy(); ma = ya.mean(); obs_a = (wins(ya) / ma - 1) * 100
ca = dict(last_ge=0, max_ge=0)
for _ in range(50_000):
    p = rng.permutation(ya); rel = (wins(p) / ma - 1) * 100
    ca["last_ge"] += rel[-1] >= obs_a[-1] - 1e-12; ca["max_ge"] += rel.max() >= obs_a.max() - 1e-12
out["perm_1979_2024_p_last_window_ge_obs"] = ca["last_ge"] / 50_000
out["perm_1979_2024_p_any_window_ge_obs_max"] = ca["max_ge"] / 50_000
out["window_2014_2024_rel_to_1979_2024_mean_pct"] = obs_a[-1]

# ---- node differences versus sampling ------------------------------------------------
ns = json.load(open(REV / "node_sensitivity.json"))["nodes"]
for k in ("W", "E"):
    pr = ns[k]["paired_annual_rel_diff_vs_primary_node_pct"]
    out[f"node_{k}_paired_mean_pct"] = pr["mean"]
    out[f"node_{k}_paired_90ci_halfwidth_pct"] = stats.t.ppf(0.95, 30) * pr["sd"] / np.sqrt(31)

# ---- exploratory power-curve sensitivity (NOT a result; not for the manuscript as is) -
u = df.loc["1994":"2024", "U_hub"].to_numpy().astype(float)
base = S04.power_from_speed(u.copy()).mean()
for du in (-0.3, -0.2, 0.2, 0.3):          # curve shifted along the speed axis (digitisation offset)
    out[f"curve_shift_{du:+.1f}ms_gross_change_pct"] = (S04.power_from_speed((u - du).copy()).mean() / base - 1) * 100
for f in (0.97, 1.03):                      # power scaled, capped at rated
    p = np.minimum(S04.power_from_speed(u.copy()) * f, S04.TURBINE.rated_power_mw * 1000)
    out[f"curve_power_x{f}_gross_change_pct"] = (p.mean() / base - 1) * 100
out["specific_rated_power_w_per_m2"] = S04.TURBINE.rated_power_mw * 1e6 / (np.pi * (S04.TURBINE.rotor_diameter_m / 2) ** 2)
print(json.dumps(out, indent=1, default=float))
```
