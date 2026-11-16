# Phase 5D-0 — Review response matrix

*16 November 2026. Assessment of every comment in the "independent-style" peer review
(verdict MAJOR REVISION) given in this conversation, against the manuscript and
supplement at commit `4a46a0a`, `results/revised/`, the scripts and the methodology
documents. Nothing was changed. The quantitative checks are in
`PHASE5D0_STATISTICAL_AUDIT.md`, and the resulting work plan is in
`PHASE5D0_MINIMAL_REVISION_PLAN.md`.*

**Decision legend**
- **A** = accept: scientifically justified.
- **PA** = partially accept: valid concern, but the proposed remedy is excessive or
  incomplete.
- **R** = reject: unsupported, incorrect or outside the justified scope.

**Priority legend**
- **P0** = scientifically necessary before submission.
- **P1** = important for publication quality.
- **P2** = optional.

**Kind of work required**
- **T** = manuscript text only.
- **F** = figure label (regeneration, no value change).
- **S** = external source must be obtained or verified.
- **C** = new calculation through the pipeline.

**Totals: 36 items.** 10 A, 19 PA, 7 R. Seven reviewer claims could not be independently
verified (§3).

---

## 1. Decision matrix

| ID | Reviewer claim | Decision | Evidence | Minimum action | Priority | Submission blocker |
|---|---|---|---|---|---|---|
| **Z1a** | The +3.1 % of 2014–2024 is wrongly contrasted with the 31-year ±2.3 %; the right basis is the 11-year mean's own interval (±3.8 %) (Abstract; §4.3; §4.6; §6) | **PA** | Audit A1: ±3.83 % verified; already stored as `t90_half_width_rel_pct` in `rolling_11yr_windows.csv`. But 2015–2024 (+5.0 %) exceeds its own ±2.2 %, and 2014–2024 vs 1994–2013 differs by +4.8 % (Welch p = 0.09; Mann–Whitney p = 0.04) | **T.** Reword the Abstract, §4.3, §4.6 last paragraph and §6 first finding. Say that the recent decade is higher, but by an amount comparable to the sampling uncertainty of an 11-year mean (quote the stored half-width). Drop the implication that period selection is a source separate from and larger than sampling | **P0** | **Yes** (misleading central statement; text only) |
| **Z1b** | Random-year permutation gives p ≈ 0.34, so the window result is unremarkable | **R** | Audit A4: 0.337 verified numerically, but it is a scan statistic over all 21 windows. 2014–2024 was pre-specified (the original period; §3.7). The pre-specified probability is p = 0.041 (0.032 in 1979–2024) | None in the manuscript. Explain in the response letter. Do not add a permutation test | — | No |
| **Z1c** | "6 windows above, 15 below" is an artefact of overlapping windows (§5.2) | **A** | Audit A2: P(≤ 1 sign change) = 0.23 under permutation; adjacent windows share 10 of 11 years (r = 0.91) | **T.** Remove "What is demonstrated is the pattern …" as evidence. Keep the fact that 9 of the 10 years 2015–2024 are above the mean, stated as description | **P0** | Yes (with Z1a) |
| **Z1d** | A borderline trend (OLS p = 0.065, Kendall p = 0.052) is not tested; it would violate the i.i.d. assumption of Eq. 6 | **PA** | Audit A1/A5: verified for 1994–2024. Over 1979–2024 the trend is weaker (+1.0 % per decade, p = 0.20). Lag-1 −0.08; Shapiro p = 0.54 | **T.** One sentence in §3.6 stating the stationarity assumption and what the interval does not cover. Optional (P2, **C**): a descriptive trend sentence produced by the pipeline. No formal test is required | **P1** | No |
| **Z1e** | "Systematic" (§4.3) and "biased high" (§6) are unsupported | **A** | Audit A3: one high realisation is not estimator bias, and the trend evidence is weak to moderate | **T.** Replace with "higher in this record" and similar wording | **P0** | **Yes** (text only) |
| **Z2a** | ERA5's native resolution is about 31 km; the 0.25° values are interpolated; nodes 21 km apart are not independent cells; "the 0.25° cell each node represents" is wrong (§2.6; §3.7; Fig. 1) | **A** | Audit B1: node spacing 21.2 km. Mask 0.44 at C, but the true land share of C's 0.25° box is 12.8 % and of the 0.5° box 41.7 % (`PHASE5PRE_ERA5_ROBUSTNESS.md` §4.1). The repository's own documents already state "≈31 km native grid" | **T + F + S.** Correct the sentences and labels listed in audit B3 (§1, §2.6, §3.2, §3.7, §4.4, §4.5, §5.3, §5.4, §5.6, §6, Tables 2 and 4, Figs 1 and 3). Confirm the native-resolution statement in Hersbach et al. (2020) before citing it | **P0** | **Yes** (factual error) |
| **Z2b** | The western node lies nearer the open sea; part of the node difference may be a real gradient | **A** | Fig. 1 geometry; §5.3 discusses only land influence. Paired differences ±0.3 % (audit A2), so they are systematic, not noise | **T.** One sentence in §4.4 and §5.3: the differences combine a possible real east–west gradient, the model's smoothed land influence and shear. The data cannot apportion them | **P0** | Yes (part of Z2a) |
| **Z2c** | §5.6 "direction of error unknown" ignores the cited ERA5 evaluations, which point to underestimation offshore | **PA** | Register: Olauson, Ramon, Kalverla, Gualtieri and Rubio are "cited for scope only" (V-MD, metadata). Only the title of Gandoin & Garza (2024) supports underestimation, and only of *strong* winds offshore. A general negative bias is **not verified** | **S + T.** Either read two or three of the cited evaluations and add one evidence-based sentence on reported bias, or soften to "not established at this site". No new data | **P1** | No |
| **Z2d** | The paper shows inter-model divergence, not measured representativeness; its answer is qualitative | **PA** | Without observations representativeness cannot be quantified, and the paper already says so (§5.1, §5.4). The title promises sensitivity, not representativeness | **T.** In §1 (objective) and §6, describe the contribution as a quantified sensitivity to representation choices, not a measurement of representativeness. No new analysis | **P1** | No |
| **Z3a** | Phase 2A shows the power curve moves yield by about 10 % (2.62 → 2.37), more than any node effect | **R** | Audit C1: the −10.55 % is a controlled change (same wind, period, losses), but against a retired curve rejected as physically implausible (peak Cp 0.564; rated 1 m/s early). "2.62 → 2.37" is the retired Monte Carlo farm P50 in TWh. It is no measure of the adopted curve's uncertainty | None (response letter) | — | No |
| **Z3b** | Uncertainty of the digitised curve is not quantified | **PA** | Audit C2 (exploratory): ±0.2 m/s shift gives ∓4.8 %; ±3 % power gives about ±3 %. Nothing in the manuscript quantifies it | **T.** In §5.6 and the first finding of §6, state that power-curve and turbine-related uncertainty were not quantified and are not among the categories compared. Optional (P2, **C**): ±0.2 m/s curve-shift case in `scripts/08` | **P1** | No |
| **Z3c** | Specific rated power is about 450 W m⁻²; turbine choice may dominate the three examined choices | **PA** | 450 W m⁻² verified. "May dominate" is not verified, and turbine choice is outside the stated question. §5.6 already warns against comparing CFs across machines | **T.** One clause noting the high specific rating of the reference machine (§3.4 or §5.6). No new turbine | **P2** | No |
| **Z3d** | Loss values are unsourced; the "loss sensitivity" is only the ratio of assumed factors | **PA** | §3.5 calls them illustrative assumptions without a source. The ±6.5 % / −8.3 % follow from η alone | **S + T.** Cite one or two sources for typical offshore loss ranges, or state that the values are the authors' illustrative choices. Call row 6 "effect of alternative loss assumptions (arithmetic)" | **P1** | No |
| **Z3e** | False precision ("26.85 %", "2.354") | **PA** | Precision is appropriate in tables (reproducibility) but not in the Abstract and Conclusions | **T.** Round in the Abstract and §6 (about 2.35 GWh MW⁻¹ yr⁻¹; about 27 %); keep the tables | **P1** | No |
| **M1a** | Yildirim (2023), the closest prior study, was not read | **A** | Register A1: full text not accessed. My own attempt also failed | **S.** Obtain and read the full text; revise the §1 paragraph. Add a quantitative comparison only if its area and method allow | **P0** | **Yes** (external) |
| **M1b** | The 2018 tender process is cited through Yildirim, not a primary source | **PA** | §1 ¶1; the archived 2018 MENR notice could not be opened (checklist A2) | **S/T.** Cite the primary notice if it can be obtained; otherwise write "according to Yildirim (2023)" | **P1** | No |
| **M4** | The CDS cross-check covers only 2014–2024 (20 of 31 years unchecked) | **PA** | Verified (§3.2; Table S2). The same ERA5 archive was redistributed; agreement over 96 432 h is r = 0.99994 and the CF difference −0.004 %. The risk is low but not zero | **T.** One explicit sentence in §3.2 and §5.6. Optional (P2): re-download 1994–2013 from CDS (needs credentials) | **P1** | No |
| **M5** | The GWA 4.0 period 2008–2017 has no citable source | **A** | Register: the period comes from a Phase 2B review of DTU material; Davis et al. (2023) describes the method in general. The period-matching effect is only 0.26 % | **S.** Cite GWA 4.0 documentation (release note, technical report or the GWA site with access date). If none is found, state the period as provider information with that caveat | **P0** | **Yes** (sourcing) |
| **M7** | Missing literature on reference-period choice, long-term correction and recent wind recovery (for example Zeng et al. 2019); the §6 "practices" are standard industry knowledge | **PA** | Not in the reference list. Zeng et al. 2019 is **unverified** | **S + T.** Add one or two verified sources in §1/§5.2. Rephrase §6 as "confirms, for this case, established practice" | **P1** | No |
| **M8a** | CO₂ accounting and the 997.5 MW case are off-topic; Table 6 gives spurious precision | **PA** | CO₂ is the fourth stated contribution (scope decision of Phase 5-PRE-C). §5.8 already says it adds no information. "1 466 (1 432–1 499) kt" is over-precise for a conditional case | **T.** Keep, but shorten §4.8 and §5.8 slightly and round Table 6's conditional column. Do not remove | **P2** | No |
| **M8b** | Remove the seismotectonic paragraph (§2.5) | **R** | Three sentences of context. They state that the fault distance was not computed and hazard not assessed, which a regional reviewer would expect to see | None | — | No |
| **m1** | "Sampling interval" is ambiguous (in wind data it means time resolution) | **A** | The term is used throughout | **T.** Global rename to "sampling confidence interval" (first use: "confidence interval of the mean, sampling uncertainty only") | **P1** | No |
| **m2** | The Abstract mixes yield % with a speed % (12 %) | **R** | The Abstract already says "a mean wind speed about 12 % higher" | None | — | No |
| **m3** | No rationale for starting in 1994 | **A** | §3.2 gives none; 1979–2024 differs by −0.2 % (Table S5) | **T.** One sentence: a recent 31-year period ending in the last complete year; the extended record is in §4.3 | **P1** | No |
| **m4** | Report the polygon-share-weighted node value (2.378, +1.0 %); "no physical meaning" is too strong | **PA** | 2.378 verified. A weighted value would look like a refined estimate that the data cannot justify | **T.** Soften "an average would have no physical meaning" to "would not be better supported than any single node". Do not add the weighted value | **P2** | No |
| **m5** | Fig. 3a repeats Table 2; Fig. 4 row 5 (+23.8 %) compresses the axis | **PA** | Fig. 3a adds the polygon longitude range and the shared axis with 3b. Row 5 is part of the message (scale of product disagreement) | Keep Fig. 3a. Optional (**F**): axis break or annotated off-scale marker for row 5 | **P2** | No |
| **m6** | Captions are too long (Fig. 1 about 200 words) | **PA** | Journal-dependent; caption limits vary | **T.** Move method detail from the Fig. 1 and Fig. 2 captions to the text once the journal is chosen | **P2** | No |
| **m7** | Eqs. 7 and 8 are trivial | **R** | They define Δ and C used in tables and text; harmless | None | — | No |
| **m8** | Supplementary tables carry surplus content (S7, two rows of S12, S14, S15) | **PA** | S15 is self-declared "not robust and not used further". S7 (Weibull) is commonly requested. S12 and S14 support §3.9 | **T.** Remove S15 and the §4.7 sentence citing it. Keep S7, S12 and S14 | **P2** | No |
| **m9** | Bound the ÖÇK datum effect by a shift calculation | **PA** | The overlap is already labelled approximate with reasons (§2.4) | Optional (P2, **C**): ±100–200 m shift test | **P2** | No |
| **m10** | "Requires clarification by the competent authorities" (§6) reads as advice | **A** | Wording in §6 | **T.** Change to "raises a question for the competent authorities" | **P2** | No |
| **X1** | Persistence of node differences is expected for series correlated at 0.99 and adds no evidence | **R** | High correlation is exactly why the paired difference is systematic, not sampling noise: paired 90 % half-width ±0.31 % (audit A2). The manuscript's inference ("a longer record does not reduce them") is correct | None | — | No |
| **X2** | Bootstrap and jackknife are redundant | **R** | Reported only in Table S4 as checks; harmless | None | — | No |
| **X3** | Lag-1 near zero does not exclude a trend | **A** | True; see Z1d | Covered by Z1d | (P1) | No |
| **X4** | "Can only be settled by observation" ignores satellite and coastal data | **PA** | §5.9. Satellite winds (SAR, scatterometer) are observations, but with their own limits near coasts | **T.** Add "for example in-situ or satellite-derived winds" | **P2** | No |
| **X5** | Contribution is modest; a database sweep (including Turkish sources and theses) is needed for a defensible claim | **PA** | No novelty claim is made (§1). The sweep has not been done (checklist A3) | **S.** Run the sweep. Revise §1 only if relevant work is found | **P1** | No (recommended before submission) |

---

## 2. Count of decisions

| Decision | Count | IDs |
|---|---|---|
| ACCEPT | 10 | Z1c, Z1e, Z2a, Z2b, M1a, M5, m1, m3, m10, X3 |
| PARTIALLY ACCEPT | 19 | Z1a, Z1d, Z2c, Z2d, Z3b, Z3c, Z3d, Z3e, M1b, M4, M7, M8a, m4, m5, m6, m8, m9, X4, X5 |
| REJECT | 7 | Z1b, Z3a, M8b, m2, m7, X1, X2 |

## 3. Claims that cannot be independently verified here

| Claim | Why not verifiable | Consequence |
|---|---|---|
| Yildirim (2023) used GWA and is directly comparable with this study's GWA comparison | Full text not accessible | Resolve with M1a |
| The cited ERA5 evaluations show a negative offshore bias | The papers were verified at metadata level only; only one title points that way (strong winds) | Read before writing (Z2c) |
| A recent global reversal of wind stilling (Zeng et al., 2019) explains the higher recent decade | Source not in the register; not verified | Verify before citing (M7) |
| Turbine choice "may dominate" the examined sensitivities | No alternative-turbine calculation exists | Treat as a limitation, not a finding (Z3c) |
| GWA 4.0 covers 2008–2017 | Provider documentation not in hand | M5 |
| ERA5 native grid about 31 km (TL639) | Well established, but Hersbach et al. (2020) is register status V-MD | Confirm in the paper before citing (Z2a) |
| The 1994–2013 Open-Meteo data match CDS | No CDS file for those years in the repository | Disclose (M4) |

## 4. Verified reviewer numbers

All verified:
- the 31-year interval (±2.27 %);
- the 2014–2024 deviation (+3.1 %) and its own interval (±3.83 %);
- the permutation value (0.337, but see Z1b);
- the OLS (+2.75 % per decade, p = 0.065) and Kendall (p = 0.052) trends for 1994–2024;
- the window-pattern artefact;
- the node spacing (21.2 km);
- the specific power (450 W m⁻²);
- the GWA period effect (0.26 %);
- the weighted node value (2.378);
- the controlled −10.55 % curve change (misinterpreted, Z3a);
- the CDS cross-check coverage (2014–2024 only).
