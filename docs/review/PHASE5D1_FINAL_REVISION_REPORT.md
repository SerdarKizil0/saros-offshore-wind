# Phase 5D-1 — Final scientific revision and manuscript freeze

*16 November 2026. This phase implements the P0 corrections and the justified P1 and P2
items of `PHASE5D0_MINIMAL_REVISION_PLAN.md` (matrix: `PHASE5D0_REVIEW_RESPONSE_MATRIX.md`).
Scientific models, wind inputs, `results/revised/` and the archive were not changed, and
every tabulated value is unchanged (tested). Open items are in
`PHASE5D1_REMAINING_SUBMISSION_ITEMS.md`. The manuscript is now frozen (§8).*

## 1. Deliverables

| File | Pages |
|---|---|
| `manuscript/output/Saros_Offshore_Wind_Master.docx` / `.pdf` | 27 |
| `manuscript/output/Saros_Supplementary_Material.docx` / `.pdf` | 6 |
| `figures/revised/fig1_site_map`, `fig2_temporal_sensitivity`, `fig3_nodes_and_products`, `fig4_sensitivity_categories` (`.pdf`, `.svg`, `.png`) | — |

Figure 2 was regenerated and is unchanged; Figures 1, 3 and 4 changed in label text only.

Build commands:

```bash
python scripts/12_build_figures.py && python scripts/11_build_manuscript_sections.py && python scripts/10_build_docx.py
python scripts/12_build_figures.py --check; python scripts/11_build_manuscript_sections.py --check; python scripts/10_build_docx.py --check
```

## 2. P0 corrections

### 2.1 Reference-period interpretation (Z1a, Z1c, Z1e)

| Location | Before | After |
|---|---|---|
| Abstract | "Three sensitivity experiments move the result by more than this interval. The most recent 11 years alone give a yield 3.1 % higher, and they form the highest of all 11-year windows" | Node and product effects are stated against the 31-year interval. The recent decade is +3.1 %, "of the same size as the sampling uncertainty of an 11-year mean (±3.8 %) and does not by itself establish a lasting change" |
| §4.3 | "The rolling windows show that this is systematic" | "put this difference in context". Adds the 90 % interval of the 2014–2024 mean (±3.8 %, Table S6), and that the difference "is not, on its own, evidence of a lasting change" |
| §4.6 | "the sampling interval is the smallest … a short recent reference period … can each move the result by more than" | The node, product and loss effects are several times the half-width. The recent period moves it "by about as much as the sampling uncertainty of that shorter record" |
| §5.2 | Heading "Why a recent reference period gives a higher estimate"; "What is demonstrated is the pattern"; the 6-above / 15-below window count used as evidence | Heading "What the higher estimate of a recent reference period means". The text says "What is observed is a difference, not a demonstrated shift", explains that overlapping windows add little evidence, and gives the ±3.8 % comparison. The window-count sentence was removed |
| §6, third finding | "not a neutral choice … biased high" | "a record of about a decade is too short to stand for the long-term mean … a difference of the same size as the sampling uncertainty of an 11-year mean" |
| Table 4, row 3; Fig. 2 and Fig. 4 captions; Table S6 | — | Add the 11-year half-width. Table S6 gains a column with each window's own 90 % half-width (from the existing `t90_half_width_rel_pct` in `rolling_11yr_windows.csv`) |
| §3.6 (P1) | — | Stationarity assumption of Eq. 6 and its consequence |

No permutation p-value, trend test or other exploratory statistic was added; a test
enforces this.

### 2.2 ERA5 spatial resolution (Z2a, Z2b)

**Source check.**
- The Hersbach et al. (2020) abstract states "horizontal resolution of 31 km" (read via the
  Semantic Scholar API; the publisher PDF returned HTTP 403).
- The ECMWF ERA5 data documentation gives HRES "31 km, 0.28125 degrees", archived as
  spectral T639 or Gaussian N320.
- The CDS dataset page (doi:10.24381/cds.adbb2d47) states "regridded to a regular lat-lon
  grid of 0.25 degrees".

**Changes.**
- "Cell" language was replaced throughout: Abstract, §1, §2.6, §3.2, §3.7, §4.4, §4.5,
  §5.3–5.4, §5.6, §5.9, §6, Tables 2 and 4, and the captions and labels of Figs 1 and 3.
- The text now distinguishes three things:
  - the model resolution of about 31 km;
  - interpolated 0.25° output nodes, about 21 km apart, which share model grid points;
  - land–sea-mask values at the nodes, described as indicators of land influence. At the
    primary node the value (0.44) exceeds the land share within 0.25° of the node; it is
    stated qualitatively.
- §4.4 and §5.3 now give a genuine east–west gradient as an alternative or additional
  explanation of the node differences, and say that the data cannot separate the
  explanations.
- **Figure 1**:
  - legend "Area nearest to each ERA5 node", replacing "ERA5 0.25° cell of each node";
  - node labels "land–sea mask 0.44", replacing "land fraction";
  - caption: output nodes are "not independent cells".
- **Figure 3**: "land–sea mask" labels; legend "Boundary between nearest-node areas" and
  "sea pixels, 0.25° box at node".

### 2.3 Yildirim (2023)

- Bounded legitimate attempt on 16 November 2026: Unpaywall reports closed access; the
  Semantic Scholar record has no abstract (elided by the publisher); the publisher page
  requires authentication.
- No content was inferred. The §1 paragraph keeps its explicit limitation ("the full text
  was not available to us … the results of the two studies are not compared here").
- The 2018 tender statement is now attributed: "According to Yildirim (2023), an earlier
  tender process was opened in 2018".
- Unresolved item B1.

### 2.4 GWA 4.0 reference period

- **Substantiated.** Hansen, Floors & Badger (2025), *Global Wind Atlas 4 – Validation*,
  DTU Wind Energy E-0256, was read in full (publisher's PDF, DTU Orbit). §1.1 states: "in
  GWA 4.0, the ERA5 dataset … is used for the simulation period 2008-2017". The validation
  section calls it "the same ten-year period that was used to create the mesoscale wind
  data used in GWA4".
- The reference was added to the list (39 entries) and the register (status V-FT).
- Wording changed from "GWA climatology refers to 2008–2017" or "reference period" to "the
  mesoscale simulation period of GWA 4.0 (Hansen et al., 2025)" in §3.7, §4.3, §4.5,
  Tables 3, 4 and S11, and the captions of Figs 3 and 4.
- The matched-period comparison now matches ERA5 to that mesoscale period.

## 3. P1 corrections

| Item | Implementation |
|---|---|
| Terminology | "Sampling interval" becomes "sampling confidence interval" throughout, including §3.6's heading, Tables 1, 4, 6, S4 and S12, and the Fig. 4 caption. A test forbids the old term |
| Turbine and power curve | §3.4: specific rating about 450 W m⁻² (computed from the turbine configuration) and the effect of a lower rating. "The uncertainty of the digitised curve and the effect of the choice of turbine were not quantified." Repeated in §5.6 and the first finding of §6 |
| Losses | §3.5: "illustrative assumptions chosen by the authors … not taken from a published loss study". Table 4 row 6: "Alternative assumed loss factors (arithmetic)" |
| CDS check scope | §3.2: "It covers the 2014–2024 common period only; the years 1994–2013 were not compared with a CDS download" |
| 1994 rationale | §3.2: the period ends in 2024 to contain the complete, CDS-checked 2014–2024 record and starts in 1994 to give 31 years; the 1979 record shows the start year matters little |
| Rounding | Abstract and §6: "about 2.35 GWh MW⁻¹ yr⁻¹", "about 27 %". Exact values remain in Sections 4–5 and the tables |
| Novelty | §1: "The study makes four limited contributions". §6: "three practices, none of them new" |
| Category overlap | Table 4 note and §5.5: the period category partly overlaps category 1 |
| Bias wording | §5.6: "the direction of any error in the resource level at this site is not established" (softened from "unknown") |

## 4. P2 wording

- §5.3: averaging "would not be better supported than any single node" (was "no physical
  meaning").
- §5.9: observations "in situ or, where their quality near the coast allows,
  satellite-derived".
- §6: the ÖÇK overlap "raises a question for the competent authorities" (was "requires
  clarification").
- **Not done**, as decided in 5D-0:
  - new turbine, datasets, trend or permutation tests, power-curve or datum shift
    experiments;
  - removal of Table S15 or of the CO₂ sections;
  - Fig. 4 axis break.

## 5. Bibliography

| Entry | Correction | Source |
|---|---|---|
| Hansen et al. (2025) | **Added** | DTU Orbit, full text |
| Aksoy et al. (2022) | Initials (Çağatay M.N., Yavuzoğlu A.Z., Ülgen U.B.) | Crossref |
| Davis et al. (2023); Dörenkämper et al. (2020) | Initials (N.N., A.N., B.O., N.G.; B.T.) | Crossref |
| Kalverla et al. (2020); Ramon et al. (2019); Rubio et al. (2025) | Initials | Crossref |
| Gandoin & Garza (2024) | Issue 9(8) | Crossref |
| Zippenfenig | Year 2024, version 1.4.0 (in-text and declarations) | DataCite record of the cited DOI |
| Duzcan & Kara (2023) | Pages 5571–5584 confirmed | Crossref |
| Hersbach et al. (2020) | Register status V-AB (abstract read) | Semantic Scholar API |

Long author lists are still abbreviated with "et al." pending the journal style (item C1).
Nothing was invented.

## 6. Rebuild and visual QA

- All 27 master pages and 6 supplementary pages were rendered and inspected. Equations
  (1)–(8) render with correct structure and numbering, and "Eq. 6" links to its equation.
  Figures 1–4 and their captions are placed after their first citation; labels are legible
  and none are clipped.
- **Layout changes made during QA (presentation only):**
  - Figure 3 is placed before Table 2, both cited in the same paragraph, so the long table
    does not push the figure to a new page (`FIGURE_FIRST`).
  - The reference list starts on a new page. LibreOffice otherwise left the "References"
    heading alone at the foot of a page.
- **Remaining white space:** pages 14 and 24 end early (about one third of a page): Table 2
  with its caption does not fit at the foot of page 14, and page 24 ends before the
  reference list. These are normal float and section breaks for a review manuscript.

## 7. Tests

- **Full suite: 340 passed, 0 failed.** All three `--check` commands report "up to date".
- **New `tests/test_revision_5d1.py` (11 tests).** It forbids:
  - "biased high", "systematic" (period) and "What is demonstrated is the pattern";
  - "cell" wording;
  - "sampling interval";
  - exploratory statistics.

  It requires:
  - the ±3.8 % comparison in the Abstract, Results and Discussion;
  - the 31 km and 0.25° description;
  - the gradient alternative;
  - the GWA source;
  - the Yildirim limitation;
  - the P1 sentences;
  - rounded headline values;
  - corrected reference details.
- **Updated wording locks.** `test_manuscript_5b1.py`, `test_manuscript_5b2.py`,
  `test_fig1_site_map.py`, `test_figures_5c1.py` and `test_docx_build_5c2.py` were updated
  to the corrected statements.
- **Numbers lock.** The Phase 5B-1 text lock is replaced by a numbers lock: the multiset of
  numbers in the main tables equals Phase 5B-1, and the supplementary tables differ only by
  the added half-width column of Table S6.
- Automated tests check completeness and consistency, not appearance. Appearance was
  checked page by page (§6).

## 8. Freeze declaration

The scientific manuscript is **FROZEN** as of this commit. Further changes are limited to:

1. a demonstrable factual error;
2. an essential missing source, such as the Yildirim (2023) full text or a changed tender
   status;
3. the author-dependent placeholders and journal formatting listed in
   `PHASE5D1_REMAINING_SUBMISSION_ITEMS.md`.

Any such change must not alter the methods, the results or the interpretation. The
results must still be rebuilt with the existing commands and checked with the existing
tests.
