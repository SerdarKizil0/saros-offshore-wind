# Phase 5B-1 — Rewrite of Study Area, Methods and Results

*14 November 2026. Sections 2 to 4 and the tables were rewritten from the
current evidence. Introduction, Discussion, Abstract, Conclusion, publication
figures, figure generators, the DOCX build, the scientific models, the input
data and `results/revised/` are unchanged. Phase 5B-2 has not started.*

**Reproduce**

```bash
python scripts/11_build_manuscript_sections.py          # writes the 3 sections and 2 table files
python scripts/11_build_manuscript_sections.py --check  # "up to date"
python -m pytest -q tests/test_manuscript_5b1.py        # 51 passed
```

---

## 1. What was rewritten and how

| File | Content | Words |
|---|---|---|
| `manuscript/src/02_study_area.md` → `manuscript/02_study_area.md` | Section 2, Study Area | ≈1 000 |
| `manuscript/src/03_methodology.md` → `manuscript/03_methodology.md` | Section 3, Materials and Methods | ≈2 000 |
| `manuscript/src/04_results.md` → `manuscript/04_results.md` | Section 4, Results | ≈1 650 |
| `manuscript/tables.md` | Tables 1–6 (generated) | — |
| `manuscript/supplementary_tables.md` | Tables S1–S15 (generated) | — |

**Numbers are not typed.** The prose lives in `manuscript/src/`. Every result
is a placeholder that points into `results/revised/`, for example
`{{energy_yield:net.gwh_per_mw|.3f}}`.
`scripts/11_build_manuscript_sections.py` resolves the placeholders, re-wraps
the text and writes the generated files; it also builds both table files
directly from the result files.

- A small set of derived values (for example the share shallower than 10 m,
  or the relative deviation of the lowest year) is computed in the script
  from result and input files and documented there.
- A test rejects any hand-typed decimal or large integer in the sources that
  is not on a short list of documented constants (coordinates, turbine
  rating, legal document numbers, experiment settings).
- If the results change, re-running the script updates text and tables
  together.

---

## 2. Section contents

### 2.1 Study Area (Section 2)

1. **Geographic setting.** The polygon lies on the northern (Thracian)
   shelf. The earlier "north of the Gelibolu Peninsula" description is
   corrected. Area 172.6 km², principal axis 35.9 × 11.3 km.
2. **Official status.** Candidate YEKA (notice of 13 May 2026); not a
   declared YEKA and not an approved project. The draft specification of
   22 June 2026 concerns 1 000 MWe for any one of four areas and assigns no
   capacity to Saros. Status as of 14 November 2026.
3. **Bathymetry.** EMODnet DTM 2024: 1.0–61.6 m, median 27.8 m. This
   replaces the earlier "~50 to >200 m".
4. **Protected-area context.** Saros ÖÇK boundary reconstructed from the
   13 decree points of Decision 2010/1089; datum not stated; later
   amendments not confirmed either way; overlap about 25 km² (about 14 %).
   No permitting determination. The unscreened topics are listed.
5. **Seismotectonic context.** Three sentences. "The gulf", not "the zone",
   lies on the fault; distance and hazard not assessed.
6. **Polygon and reanalysis grid.** The node is outside the polygon (3.7 km
   south), nearest for 62.6 % of the area; ERA5 land–sea mask 0.44 (mixed
   cell), neighbours 0.12 and 0.46. All results are node-level.

### 2.2 Methods (Section 3)

| Subsection | Content |
|---|---|
| 3.1 | Scope; four kinds of quantity (reanalysis output, model results, sensitivity experiments, assumptions); only one probabilistic interval; reproducibility |
| 3.2 | ERA5 delivered through Open-Meteo, 1994–2024, 271 752 h; input check against the CDS series (not bit-identical; −0.004 % gross CF) |
| 3.3 | Hub-height reconstruction, Eqs. 1–2; exponent derived from reanalysis levels, not measured |
| 3.4 | Reference turbine; OEDB V164/9500 curve as a third-party digitisation, not manufacturer-certified |
| 3.5 | Empirical hourly conversion, Eqs. 3–5; gross and net capacity factor; losses as illustrative assumptions, no wake model |
| 3.6 | Sampling interval of the 31-year mean, Eq. 6; interannual variability reported separately |
| 3.7 | Sensitivity experiments, Eq. 7: period selection and rolling 11-year windows; three nodes; ERA5–GWA with explicit periods; loss scenarios |
| 3.8 | First-order bathymetric and protected-area screening |
| 3.9 | Operational grid-CO₂ accounting, Eq. 8, under the 2023 combined-margin convention; one conditional illustrative capacity |
| 3.10 | Weibull fit, monthly means and directions as supplementary description only |

The former Weibull-integration equation, the life-cycle subtraction, the
Monte Carlo and the capacity-scenario section are gone. There are eight
numbered equations.

### 2.3 Results (Section 4), in the requested order

| Subsection | Main statement | Kind |
|---|---|---|
| 4.1 | Mean wind speed 7.01 m s⁻¹ at 100 m, 7.06 m s⁻¹ at 105 m; gross CF 31.67 %; net CF 26.85 %; **net yield 2.354 GWh MW⁻¹ yr⁻¹** | Reanalysis output; model result |
| 4.2 | 90 % sampling interval 2.300–2.407 (±2.3 %); annual CoV 7.4 %; lowest year 2002, second lowest 2014 | Sampling statistic; observed spread |
| 4.3 | 1979–2024: −0.2 %. 2014–2024 comparison period: higher by 3.1 %, and the highest of all 21 (and 36) rolling 11-year windows | Sensitivity experiment |
| 4.4 | Western neighbour +6.7 %, eastern neighbour −8.5 %, in every year; not averaged, not a bound | Sensitivity experiment |
| 4.5 | GWA/ERA5 ratio 1.119 (1994–2024) and 1.122 (period-matched); 1.067–1.153 by node; the products rank the cells differently; not a validation | Inter-model comparison |
| 4.6 | Low losses +6.5 %, high losses −8.3 %; Table 2 places the six categories side by side, not combined | Assumption scenarios |
| 4.7 | Whole polygon shallower than 62 m; about 14 % inside the reconstructed ÖÇK boundary; screening only | Screening |
| 4.8 | 1 469 tCO₂ MW⁻¹ yr⁻¹ as an accounting equivalent under the 2023 combined margin; conventions range 840–1 679; conditional 997.5 MW case | Accounting |

---

## 3. Tables

**Main text** (`manuscript/tables.md`):

| Table | Content |
|---|---|
| 1 | Long-term wind resource and energy yield, with the type of each quantity |
| 2 | The six uncertainty/sensitivity categories, explicitly not combined |
| 3 | Three-node comparison, 1994–2024 (land–sea mask, geometry, α, yield, paired annual difference) |
| 4 | ERA5 vs GWA 4.0 mean speed with the period of each value |
| 5 | First-order screening (area, depth, ÖÇK overlap, node position) |
| 6 | Operational grid-CO₂ accounting by convention, with the single conditional 997.5 MW case |

**Supplementary** (`manuscript/supplementary_tables.md`):

| Table | Content |
|---|---|
| S1 | Data, turbine and assumptions |
| S2 | Open-Meteo vs CDS input check |
| S3 | Annual values |
| S4 | Sampling-interval checks |
| S5 | Period comparison |
| S6 | All 36 rolling windows |
| S7 | Weibull description |
| S8 | Monthly means |
| S9 | Direction distribution |
| S10 | Speed-scaling experiments |
| S11 | GWA and ERA5 around each node |
| S12 | Illustrative capacities, including the two smaller ones |
| S13 | All 2023 emission-factor conventions |
| S14 | Life-cycle GHG from the literature |
| S15 | Screening-class counts of one illustrative grid (labelled not robust) |

The old Tables 1–7 are not carried forward. Their numbering and content
(Monte Carlo columns, S4, fuel comparison, household and car equivalents)
are retired.

---

## 4. Quality assurance

`tests/test_manuscript_5b1.py` (51 tests):

| Check | What it enforces |
|---|---|
| Reproducibility | The five generated files equal a fresh build; no unresolved placeholder |
| No hand-typed results | Decimals and large integers in the sources must be documented constants |
| Current numbers | Headline values in the text equal the result files (formatted the same way); period 1994–2024, 271 752 h, node and source stated |
| Periods | 2014–2024 and 2008–2017 appear only as labelled comparison periods |
| Units | GWh MW⁻¹ yr⁻¹, tCO₂ MWh⁻¹, tCO₂ MW⁻¹ yr⁻¹; CO₂-eq only for life-cycle and all-gas values |
| Retired values | 66 patterns (2014–2024 results and the older Monte Carlo values) may not appear outside an explicit 2014–2024 comparison |
| Terminology | 25 banned wordings; "validated", "P90", "measured", "total uncertainty" only in negated statements; "±" and "confidence" only with the sampling interval; "bound" only negated |
| Categories | Table 2 has exactly six rows, one probabilistic; non-combination stated in text and table |
| Legal status | "candidate YEKA … not a declared YEKA and not an approved project"; no capacity assigned; every mention of 1 000 MWe / 997.5 MW is conditional |
| Protected area | Reconstruction, missing datum and unconfirmed amendments stated; "about 25 km², about 14 %"; no legal verdict wording; all unscreened topics named |
| CO₂ | Every "avoid…" needs "accounting" or "convention"; no "avoids / will avoid / displaces / offsets / emission-free"; "displaced" only negated |
| Capacity | Only one illustrative capacity in the main text and tables; the smaller two only in Table S12 |
| Tables | Tables 1–6 and S1–S15 numbered consecutively; every main table cited; cited supplementary tables exist; Weibull, life-cycle, directions, calibration and layout counts are supplementary only |
| Integrity | All 16 result files and the manifest equal their checksums from before this phase; the 2014–2024 archive is untouched; the four unrevised sections are byte-identical |

**Full suite:** 257 passed, 5 failed. The 5 failures are the known figure
byte-comparison tests, deferred to Phase 5C.

---

## 5. Decisions taken while writing (for the author's review)

1. **No coast distances in the text.** Phase 1 computed 0.25–9.3 km to the
   Thracian coast and ≥13.6 km to Gelibolu, but these values are not in
   `results/revised/`. The text describes the position qualitatively. To
   quote the distances, promote them into the screening output first.
2. **No figure call-outs.** The publication figures are stale and their
   final set is a Phase 5C decision. Insertion points are obvious (map in
   2.1/2.6; annual series in 4.2; rolling windows in 4.3; nodes in 4.4).
3. **Three decimals for yields** (2.354), matching the sampling interval.
   The four-decimal value (2.3539) stays in the result files.
4. **Gulf-scale bathymetry and slip-rate numbers were dropped.** Their
   sources are still unconfirmed (5A items M26, M28). Only the EMODnet
   statistics for the polygon remain.
5. **The ÖÇK legal-effect sentence was not kept** ("requires permission, not
   a prohibition"). The text only says that no determination is made.
6. **The World Bank roadmap is cited once**, for the verified fact that it
   placed marine Special Environmental Protection Areas, Saros Körfezi among
   them, in its exclusion layer.
7. **Yildirim (2023) is not cited in Sections 2 to 4.** It belongs in the
   Introduction and Discussion (Phase 5B-2), within the limits of the
   Phase 5-PRE-C audit.
8. **The share of national consumption and of the 5 GW projection appear
   only in Table S12**, following the scope decision.

---

## 6. References used in the new text (to be listed in Phase 5C)

- Hersbach et al. (2020).
- Zippenfenig (2023), Open-Meteo.
- Davis et al. (2023), Global Wind Atlas.
- EMODnet Bathymetry Consortium (2024).
- MENR (2026a), notice of 13 May 2026.
- MENR (2026b), draft YEKA DÜRES-2026 specification.
- MENR (2025), 2023 grid emission-factor form.
- UNFCCC CDM Tool 07.
- World Bank (2024).
- Yaltırak and Alpar (2002).
- Koukouvelas and Aydin (2002).
- Aksoy et al. (2022).
- Official Gazette 29852, 27793 and 30791.
- Bonou et al. (2016) and IPCC AR5 Annex III (Table S14 only).

The in-file "References cited in this section" blocks were removed from the
three rewritten sections.

---

## 7. Remaining work

**Phase 5B-2 (text):**

- Introduction, Discussion, Abstract and Conclusion still carry the
  superseded values and claims (2.62, 1 525, Monte Carlo, "designated",
  "first peer-reviewed", winter-demand alignment). They now contradict
  Sections 2 to 4 and must be rewritten from the 5B-0 addendum §6.
- Title and keywords.
- Limitations and future work, from addendum §3.
- Data and code availability statement.

**Phase 5C:**

- Regenerate all figures from `results/revised/`; add figures for the
  rolling windows and the node comparison; remove the figure-test pin.
- Rewrite the DOCX build: native equations (there are now eight), new
  captions, the generated table files.
- Compile and verify the reference list.

---

## 8. Unresolved source limitations

1. **Yildirim (2023) full text and the 2018 Saros polygon** are still
   unavailable. This does not affect Sections 2 to 4, but it blocks the
   final Introduction and Discussion.
2. **Current legal boundary of the Saros ÖÇK.** No amendment was found, but
   the ministry's boundary data could not be consulted. The text says so.
3. **Tender status** is stated as of 14 November 2026 and must be
   re-checked in the week of submission.
4. **GWA 4.0 documentation.** The reference period (2008–2017) and the
   description of the method come from the Phase 2B review of the DTU
   material, not from a re-reading in this phase.
5. **Bibliographic details** of Aksoy et al. (2022) (pages and DOI) still
   need confirmation (5A item M27).
6. **Scientific limits unchanged:** no offshore measurement; a single
   mixed land–sea ERA5 cell outside the polygon; Open-Meteo redistribution
   of ERA5; digitised power curve; assumed losses; static 2023 emission
   factor.
