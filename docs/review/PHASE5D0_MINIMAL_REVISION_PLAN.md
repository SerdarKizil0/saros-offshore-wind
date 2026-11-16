# Phase 5D-0 — Minimal revision plan

*16 November 2026. This plan follows from `PHASE5D0_REVIEW_RESPONSE_MATRIX.md` and
`PHASE5D0_STATISTICAL_AUDIT.md`. It is a plan only; nothing has been implemented. The aim
is the smallest package that makes every claim in the manuscript defensible. It adds no
new datasets and no new modelling.*

## 1. Principles

1. **Correct overstatements before adding analysis.** The two substantive problems are
   statistical wording (reference period) and a wrong description of the ERA5 grid
   (spatial representation). Both are solved by text, figure labels and one source check.
2. **No new authoritative numbers unless a sentence needs them.** Every number the
   revised text requires already exists in `results/revised/`. That includes the
   per-window 90 % half-widths in `rolling_11yr_windows.csv`.
3. **The audit's exploratory values are not results.** These are the permutation
   p-values, the trend tests and the curve shifts. If any of them is wanted in the
   manuscript, it must first be produced by the pipeline (`scripts/08`) and written to
   `results/revised/`.
4. **Keep the framing.** The paper stays a sensitivity and representativeness study:
   - no probabilistic reading of node or product differences;
   - no combined interval;
   - no feasibility language.

## 2. P0 — necessary before submission

| # | Change | Location | Kind | Source of numbers |
|---|---|---|---|---|
| P0-1 | Rewrite the period result: the recent decade is higher in this record (2014–2024 +3.1 %; 2015–2024 +5.0 %), by an amount comparable to the sampling uncertainty of an 11-year mean (±3.8 % for 2014–2024). Remove "systematic" and "biased high". Present period selection as the sampling uncertainty of a short record plus possible low-frequency variability or reanalysis inhomogeneity, not as a larger, independent source | Abstract (sentence "Three sensitivity experiments move the result …" and "The most recent 11 years …"); §4.3 ¶2; §4.6 last ¶; §5.2 ¶1–2; §6 first and third findings; Table 4 row 3 (add "own 90 % half-width of an 11-year mean ≈ ±4 %"); Fig. 2 and Fig. 4 captions (one clause each) | T | `rolling_11yr_windows.csv` (`t90_half_width_rel_pct`), `period_sensitivity.json` |
| P0-2 | Remove the window sign pattern ("the 6 most recent … all 15 earlier …") as evidence; keep the annual-count description | §5.2 ¶1; builder `derived()` windows facts (text placeholders only) | T | existing |
| P0-3 | Correct the ERA5 grid description: native resolution about 31 km; 0.25° is the interpolated output grid; output nodes 21 km apart share native grid points; the land–sea-mask value at a node reflects smoothed land influence (0.44 at the primary node, against a 12.8 % land share of its 0.25° box). Replace "cell" by "output node", "nearest-node area" or "land influence at the node" | Exact list in audit §B3: Abstract; §1 ¶4; §2.6 ¶2; §3.2; §3.7 (Grid node); §4.4 ¶2–3; §4.5 ¶2; §5.3 (heading and ¶2); §5.4 ¶2; §5.6; §6 second finding; Table 2 row 1; Table 4 row 4; Fig. 1 legend and caption; Fig. 3 legend and caption | T + F | existing. The 12.8 % land share is in `PHASE5PRE_ERA5_ROBUSTNESS.md` and is not yet a result-file value: either cite it qualitatively ("much smaller") or add it to `node_sensitivity.json` by pipeline |
| P0-4 | Add the gradient alternative for node differences: possible real east–west exposure gradient, smoothed model land influence and shear together; not separable without observations | §4.4 ¶3; §5.3 ¶2 | T | — |
| P0-5 | Verify the native-resolution statement in Hersbach et al. (2020) and cite it at §3.2 | §3.2 | S | — |
| P0-6 | Obtain the Yildirim (2023) full text; revise the §1 paragraph. Compare quantitatively only if the area and method allow | §1 ¶3 | S | — |
| P0-7 | Cite a source for the GWA 4.0 reference period 2008–2017, or label it as provider information with that caveat | §3.7 (Wind data product); Table 3; Table S11 | S | — |
| P0-8 | Carried over from the Phase 5C-2 checklist (not reviewer items): author declarations B1–B8; re-check the tender status in the week of submission | Title page; Declarations; §1; §2.2 | author | — |

P0-1 to P0-4 are text and label edits. P0-5 to P0-7 need sources; P0-8 needs the authors.

## 3. P1 — important for publication quality

| # | Change | Location | Kind |
|---|---|---|---|
| P1-1 | State the stationarity assumption of Eq. 6, and what the interval does not cover if a low-frequency change exists | §3.6 | T |
| P1-2 | Rename "sampling interval" to "sampling confidence interval" (define at first use) | global; tables; Fig. 4 row label | T + F |
| P1-3 | State that power-curve and turbine-choice uncertainty were not quantified and are not among the compared categories. Keep "categories examined" in §6 | §5.6; §6 first finding | T |
| P1-4 | Cite typical offshore loss ranges, or state that the values are the authors' illustrative choices; describe the loss row as arithmetic | §3.5; §4.6; Table 4 row 6 | S + T |
| P1-5 | Round headline numbers in the Abstract and Conclusions (about 2.35 GWh MW⁻¹ yr⁻¹; about 27 %) | Abstract; §6 | T |
| P1-6 | Disclose that the CDS cross-check covers 2014–2024 only | §3.2; §5.6 | T |
| P1-7 | Rationale for 1994: recent 31-year period ending in the last complete year; extended record in §4.3 | §3.2 | T |
| P1-8 | ERA5 bias literature: read two or three of the cited evaluations, then either add one evidence-based sentence or soften "direction unknown" to "not established at this site" | §1 ¶4; §5.6 | S + T |
| P1-9 | Reference-period and long-term-correction literature; verify Zeng et al. (2019) before citing; rephrase the §6 "practices" as confirming established practice | §1; §5.2; §6 | S + T |
| P1-10 | Frame the contribution as quantified sensitivity to representation choices, not measured representativeness | §1 objective; §6 | T |
| P1-11 | 2018 tender: primary source, or "according to Yildirim (2023)" | §1 ¶1 | S/T |
| P1-12 | Database literature sweep, including Turkish sources (checklist A3) | §1 if relevant | S |

## 4. P2 — optional

- Shorten §4.8 and §5.8 and round the conditional column of Table 6 (M8a).
- Remove Table S15 and its sentence in §4.7 (m8).
- Soften "no physical meaning" for node averaging; do not add a weighted value (m4).
- Add "in-situ or satellite-derived" to the measurement statement in §5.9 (X4).
- Change "requires clarification" in §6 to "raises a question for" (m10).
- Note the high specific rating of the reference machine (Z3c).
- Fig. 4 row 5: axis break or off-scale annotation (m5).
- Shorten captions once the journal is chosen (m6).
- Pipeline additions, only if the text should quote numbers:
  - descriptive trend over 1994–2024 and 1979–2024;
  - ±0.2 m/s power-curve shift;
  - ÖÇK datum shift;
  - CDS re-download of 1994–2013 (needs credentials).

## 5. New calculations

**None is required for P0 or P1.** Every number the revised text needs is already in
`results/revised/`, with one exception: the 12.8 % land share used in P0-3. Either cite it
qualitatively or add it to `node_sensitivity.json` through `scripts/08`, together with the
native-resolution note. Optional P2 calculations must be implemented in the pipeline, not
copied from the audit.

**New observational data are not necessary** for the paper's existing claims. They would
be necessary only for a claim the paper does not make: the true resource level or the
correct node or product.

## 6. Implementation sequence (for a later phase)

1. **P0-5, P0-6, P0-7 (sources).** Their outcome may change wording, especially P0-6.
2. **P0-1 to P0-4 and P1 text items.** Edit the source templates in `manuscript/src/`. Edit
   table labels in `scripts/11_build_manuscript_sections.py` and figure labels in
   `scripts/fig1_site_map.py` and `scripts/fig3_nodes_and_products.py`. No value changes.
3. **Rebuild** with `12_build_figures.py`, `11_build_manuscript_sections.py` and
   `10_build_docx.py`. Update the tests that pin wording:
   - `test_manuscript_5b2.py` phrases for §5.2, the period wording and the "cell" wording;
   - `test_figures_5c1.py` legend text;
   - `test_fig1_site_map.py` legend text.
   Add tests that ban the corrected phrases ("systematic", "biased high", "0.25° cell").
4. **Inspect every rendered page again.** Run the full test suite.
5. **Response letter**: point-by-point, using the matrix. Include the explanations for the
   rejected items (Z1b, Z3a, X1).

## 7. Is another review needed?

**Yes, a targeted re-review**, for two reasons.

1. The review assessed here was produced in the same working session that prepared the
   manuscript. It is an internal critical review, not an independent one.
2. P0-1 and P0-3 change how the two central findings are stated, and P0-6 may change the
   literature position.

**Recommendation.** After implementation, ask a human colleague with wind-resource or
reanalysis experience, who has not seen the earlier drafts, to read:
- the Abstract;
- §2.6, §4.3–4.6 and §5.2–5.3;
- §6;
- Figs 1, 2 and 4.

A full re-review is not necessary unless the Yildirim full text changes the framing of §1.
