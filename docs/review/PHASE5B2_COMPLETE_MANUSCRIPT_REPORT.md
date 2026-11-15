# Phase 5B-2 — Complete manuscript narrative

*15 November 2026. Title, Abstract, Introduction, Discussion, Conclusions,
declarations and a working reference list were written. Study Area, Methods,
Results and the tables are scientifically unchanged. The models, the input
data, `results/revised/`, the publication figures, the figure generators and
the DOCX build were not touched. Phase 5C has not started.*

**Reproduce**

```bash
python scripts/11_build_manuscript_sections.py --check              # "up to date"
python -m pytest -q tests/test_manuscript_5b1.py tests/test_manuscript_5b2.py   # 112 passed
```

Unresolved source and author-declaration items are in
`PHASE5B2_UNRESOLVED_REGISTER.md`. The verification status of every
reference is in `phase5b2_reference_register.csv`.

---

## 1. What was written

| File (source in `manuscript/src/`) | Content | Words |
|---|---|---|
| `00_abstract.md` | Title (the approved working title), Abstract, ten keywords | Abstract ≈ 290 |
| `01_introduction.md` | Section 1 | ≈ 940 |
| `02_study_area.md` | Section 2 (unchanged) | ≈ 1 020 |
| `03_methodology.md` | Section 3 (one citation given its year) | ≈ 2 010 |
| `04_results.md` | Section 4 (unchanged) | ≈ 1 670 |
| `05_discussion.md` | Section 5, nine subsections | ≈ 1 740 |
| `06_conclusion.md` | Section 6 | ≈ 390 |
| `07_declarations.md` | Data and code availability; author-dependent items marked | ≈ 450 |
| `08_references.md` | Working reference list, 38 entries | — |

Main text (title to Conclusions): about 8 100 words. All files follow the
`manuscript/src/` → generated Markdown architecture; every number is a
placeholder into `results/revised/`.

---

## 2. Scientific narrative

### 2.1 Introduction

1. Offshore wind in national planning: 29.6 GW of wind by 2035, of which
   5 GW offshore (National Energy Plan); 75 GW technical potential and the
   2053 net-zero pledge (World Bank roadmap).
2. The 2018 tender process and the candidate areas of 13 May 2026; the
   draft specification for 1 000 MWe in any one of the areas. Saros is a
   candidate area, not an approved project, with no capacity assigned.
3. Earlier Turkish work: site-selection studies and site-level studies,
   each described only as far as its title, abstract or full text was
   verified.
4. **Yildirim (2023):** three candidate regions of the 2018 tender process
   (two Aegean, one Black Sea), Global Wind Atlas data, best results for a
   Saros region. The text states that the abstract does not define that
   region, that the full text was not available, that the spatial relation
   to the 2026 polygon could not be established, and that the two sets of
   results are not compared.
5. Why representativeness matters: every study rests on one model-based
   wind source; ERA5 has a 0.25° grid, and in a narrow gulf one cell mixes
   land and sea; the Global Wind Atlas is a downscaling of ERA5. Three
   choices follow: period, grid cell, product.
6. Objective and four contributions, with an explicit statement of what the
   study does not do.

There is **no novelty claim** and no "to our knowledge" sentence. The gap is
stated as a practical question, not as an absence in the literature, because
the database literature sweep has not been done.

### 2.2 Discussion

| Subsection | Demonstrated | Stated as hypothesis or limit |
|---|---|---|
| 5.1 Long-term estimate | Reproducible; stable when the record is extended to 1979; narrow sampling interval | Not a test of the reanalysis; not a prediction; representativeness for a future plant is an untested assumption |
| 5.2 Reference period | The 6 most recent 11-year windows are above the mean and all 15 earlier ones below; 9 of the 10 years 2015–2024 are above the mean | Decadal variability or a reanalysis artefact: cannot be separated here |
| 5.3 Grid cell | Node differences are about 3 and 4 times the sampling half-width and recur every year; the polygon is narrower than the grid | Land influence as a plausible, unestablished hypothesis (the eastern cell contradicts a simple ordering by land fraction) |
| 5.4 Wind products | About 12 % disagreement, 7–15 % by cell; different spatial ordering | Which product is closer to the truth cannot be decided; the estimate is not scaled |
| 5.5 Six categories | Only one is probabilistic; node and product are not independent; alternatives are not exhaustive | — |
| 5.6 Data and turbine limits | Mixed cell; no measurements; digitised curve; assumed losses | The direction of any error is unknown |
| 5.7 Screening | Depth below 62 m; about 14 % overlap with the reconstructed boundary | No conclusion on availability of either part |
| 5.8 CO₂ | A factor of 2.0 between build and operating margin | Not a forecast of displaced generation |
| 5.9 Implications | Further reanalysis years add little; cell and product questions need observation | Desk-based improvements listed; none replaces measurement |

### 2.3 Abstract and Conclusions

- **Abstract:** context and objective; data and hourly method; yield
  2.354 GWh MW⁻¹ yr⁻¹ (net CF 26.85 %); sampling interval 2.300–2.407;
  period (+3.1 %), node (+6.7 % / −8.5 %) and product (about 12 % in speed)
  results; non-combination; one screening sentence; a qualified implication.
  No capacity scenario and no CO₂ figure.
- **Conclusions:** three findings about screening with coastal reanalysis
  (the sampling interval is a poor guide; grid and coastal limitations; a
  recent decade is not a neutral reference period), three recommended
  practices, the screening result and the need for measurement. It is not a
  restatement of the Abstract.

### 2.4 Principal conclusions of the manuscript

1. ERA5 at the nearest node gives a long-term net yield of
   2.354 GWh MW⁻¹ yr⁻¹ for the reference turbine: preliminary, model-based
   and unvalidated.
2. The sampling interval of the 31-year mean (±2.3 %) is the smallest of
   the six reported categories.
3. The most recent 11-year window is the highest in the record (+3.1 %).
4. Neighbouring cells differ by +6.7 % and −8.5 %, systematically.
5. ERA5 and the Global Wind Atlas disagree by about 12 % in mean speed; the
   comparison cannot decide between them.
6. These categories are different in kind and are not combined.
7. Measurement inside the polygon is the step that would most improve
   knowledge of the resource.

---

## 3. Source verification in this phase

| Item | Outcome |
|---|---|
| Yildirim (2023) full text | **Not obtained.** One bounded attempt: Unpaywall (closed, no open copy), the institutional repository (unreachable), ResearchGate (HTTP 403). No access control was bypassed. The manuscript uses abstract-level statements only |
| Aksoy et al. (2022) | **Resolved** (5A item M27): doi:10.1093/gji/ggab462, GJI 229(1), 589–604, eight authors (Crossref). The DOI in `REFERENCES_VERIFIED.md` belongs to a different article |
| Yaltırak & Alpar (2002); Koukouvelas & Aydin (2002); Bonou et al. (2016) | Metadata confirmed in Crossref |
| EMODnet DTM 2024; Open-Meteo; ERA5 dataset DOI | Resolved in DataCite |
| UNFCCC Tool 07, version 07.0 | EB 100 annex 4, valid from 31 August 2018 (UNFCCC tool index, via search); cited as UNFCCC (2018). The PDF could not be downloaded here |
| All other references | Records from the Phase 5-PRE-C inventory (Crossref-verified DOIs, or primary official documents with checksums) |

Every one of the 38 in-text citations has a reference entry and a register
row, and every reference entry is cited (tested).

---

## 4. Changes outside the new sections

| Change | Reason |
|---|---|
| Methods: "(UNFCCC, Tool 07)" → "(UNFCCC, 2018)" | Author–year citation; no scientific change |
| Table S12 note: "(…; TEDAŞ, 2025)" added | Source of the consumption value |
| Table S14 labels: "(Schlömer et al., 2014)" added | Author–year citation |
| `scripts/11_build_manuscript_sections.py` | Builds all nine text files; a few derived facts for the Discussion (window counts, years above the mean, convention ratio), each computed from result files |
| `tests/test_manuscript_5b1.py` | The pins that froze the four unrevised sections were removed, as planned |

**No contradiction was found** between the new narrative and Sections 2 to
4, the six main tables or the supplementary tables. Tables 1–6 are
byte-identical to Phase 5B-1 (tested).

---

## 5. Quality assurance

`tests/test_manuscript_5b2.py` (65 tests), in addition to the 47 tests of
Phase 5B-1:

| Check | What it enforces |
|---|---|
| Reproducible generation | All 11 generated files equal a fresh build; `--check` passes |
| No hand-typed results | In all eight prose sources; a short list of documented constants is allowed |
| Period, source, units | 1994–2024 in every section; Open-Meteo and "not bit-identical" in Methods and Data availability; 2014–2024 only as a comparison |
| Numbers across sections | Yield, capacity factor, interval, node and period values are the same strings in Abstract, Results, Discussion and Conclusions; every value with the yield unit exists in the result files |
| Discussion statements | The derived facts quoted (window pattern, 2014 as second-lowest year, ordering of the cells, polygon narrower than a cell) hold in the results |
| Obsolete methods | 17 patterns (Monte Carlo, P10/P50, fuel-resolved comparison, life-cycle subtraction, …); Weibull only in the supplementary subsection of Methods |
| Claims | 19 patterns: "first …", "designated", "bankable", "site-specific", "novel", "to our knowledge", "reliable", "proves", … |
| Negated-only words | "validated", "P90", "total uncertainty", "measured", "viable", "approved project", "prediction", "bound" |
| Intervals vs sensitivities | "±", "confidence" and the interval values only with "sampling"; node, cell, product and period results never with probability vocabulary |
| Separation of categories | Stated in Abstract, Introduction, Results, Discussion and Conclusions |
| Findings vs hypotheses | Nine Discussion subsections; twelve required qualifying statements |
| Capacity and status | Candidate status; no allocation; conditional wording; no capacity case in the narrative sections |
| CO₂ | "avoid…" only with "accounting" or "convention"; no displacement claim; no CO₂ in the Abstract |
| Yildirim (2023) | Cited only in the Introduction; eight required statements; no number attributed to it; register row says full text not accessed |
| References | Every citation has an entry; every entry is cited; every entry has an identifier and a register row; cited DOIs are registry-verified |
| Declarations | Seven headings; funding, conflicts, contributions and acknowledgements contain only an `[AUTHOR TO CONFIRM]` marker; no invented statement |
| Unchanged substance | Sections 2 and 4 sources identical to Phase 5B-1; Section 3 differs by one citation; tables as above; all result files and the archive unchanged |

**Full suite:** 318 passed, 5 failed. The 5 failures are the known figure
byte-comparison tests, deferred to Phase 5C.

---

## 6. Remaining work for Phase 5C

1. **Figures.** Regenerate all figures from `results/revised/` (they still
   show 2014–2024 values); add figures for the rolling windows and the node
   comparison; insert figure call-outs in the text (none exist yet); remove
   the temporary figure-test pin; resolve the five byte-comparison tests.
2. **Build.** Rewrite `scripts/10_build_docx.py`: new title; nine text
   files and two table files; native equations (eight, numbered in the
   text); no positional equation images; no hard-coded captions.
3. **References.** Format the working list in the journal style; complete
   author lists and initials; resolve the minor items in the register.
4. **Before submission** (register items A1, A2, A5, A6 and B1–B8): the
   Yildirim full text; tender status; a GWA 4.0 citation for the period;
   all author-dependent declarations; the target journal.
5. **Other material.** `medium_yazisi.md`, `FIGURE_BRIEFS.md` and
   `REFERENCES_VERIFIED.md` still carry superseded content and must not be
   published as they are.
