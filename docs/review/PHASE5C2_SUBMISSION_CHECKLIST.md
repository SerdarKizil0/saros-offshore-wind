# Unresolved-submission checklist (after Phase 5C-2)

*15 November 2026. This list replaces `PHASE5B2_UNRESOLVED_REGISTER.md` as the working
list; the earlier file is kept as a record. **Blocking** means the item must be closed
before submission. A "Peer review" entry says whether the item matters before the
manuscript is sent to independent (pre-submission) reviewers.*

## A. Sources and facts

| # | Item | Status after 5C-2 | What closes it | Blocking | Peer review |
|---|---|---|---|---|---|
| A1 | Yildirim (2023) full text (doi:10.1007/s10098-022-02392-0) | Not accessed. The Introduction uses the abstract only and says so | Author reads the article and confirms or extends the paragraph | **Yes** | Disclose to reviewers |
| A2 | Spatial relation of the Yildirim Saros region to the 2026 polygon; 2018 candidate-area coordinates | Undetermined; stated in the text | A1, and the archived 2018 notice | Yes, with A1 | Disclose |
| A3 | Database literature sweep (Scopus or Web of Science) | Not done; the text makes no novelty claim | Author runs the queries | Recommended | Recommended |
| A4 | Legal currency of the 2010 ÖÇK boundary | No amendment found; disclosed | Official map service or written confirmation | No | — |
| A5 | YEKA DÜRES-2026 tender status | Draft as of 14 November 2026 | Re-check in the week of submission; update §1 and §2.2 | **Yes** (date-sensitive) | Note the date |
| A6 | GWA 4.0 reference period 2008–2017 and version | Cited to Davis et al. (2023), which describes the method generally | A citable GWA 4.0 source (release note or validation report) | Yes | Should be fixed |
| A7 | Studies cited from title or abstract (Argin 2019; Emeksiz & Demirci 2019; Görmüş 2022; Demirci 2026; Satir 2018; the ERA5 evaluation papers) | Cited only for their stated topic | Author reads them | Recommended | Recommended |
| A12 | Licence of the GWA extract stored in the repository | Not checked | Provider terms | Before the repository is public | — |

## B. Author-dependent declarations (highlighted `[AUTHOR TO CONFIRM]` in the DOCX)

| # | Item | Where in the master |
|---|---|---|
| B1 | Author names, affiliations, corresponding author | Title page; supplement title page |
| B2 | Author contributions (for example CRediT) | Declarations |
| B3 | Funding statement | Declarations |
| B4 | Conflicts of interest of every author | Declarations |
| B5 | Use of generative AI: wording to the journal's policy; authors' responsibility statement | Declarations |
| B6 | Repository location, archived-release DOI, software licence | Data and Code availability |
| B7 | Acknowledgements | Declarations |
| B8 | Target journal | Determines reference style, declaration headings, word and figure limits, figure-file format |

## C. Reference details (recorded, not invented)

| # | Entry | Missing or uncertain | Source of the fix |
|---|---|---|---|
| C1 | Hersbach et al. (2020); Davis et al. (2023); Dörenkämper et al. (2020) | Author lists truncated with "et al."; full lists not entered | Publisher or Crossref record |
| C2 | Schlömer et al. (2014) | Full author list of IPCC AR5 Annex III not entered | IPCC citation guidance |
| C3 | Aksoy, Kalverla, Ramon, Rubio, Gandoin & Garza and others | Initials from Crossref first initials only | Publisher pages |
| C4 | Duzcan & Kara (2023) | Pages 5571–5584 (Crossref) conflict with an earlier note (4361–4374) | Publisher page |
| C5 | Zippenfenig (2023) | Provider recommends 2023; DataCite record of the DOI says 2024 | Decide one; apply consistently |
| C6 | Official Gazette 29852 (2016) | No URL | Official Gazette archive |
| C7 | UNFCCC (2018) Tool 07 v07.0 | PDF not downloaded here; metadata from the UNFCCC tool index | Download and confirm the version and annex |
| C8 | Official and Turkish-language documents | Formatting of translated titles and access dates not standardised; no access dates given | Journal style (B8) |
| C9 | Whole list | No journal style applied (author–year, journal-neutral) | Apply after B8 |

## D. Document build and presentation

| # | Item | Status | Action |
|---|---|---|---|
| D1 | DOCX rendering in Microsoft Word | Rendered and inspected only through LibreOffice. The PDF is the LibreOffice rendering | Open the DOCX in Word once. Check equation appearance (Cambria Math), pagination and the yellow placeholders |
| D2 | Build dependency | LibreOffice **Math** must be installed (`apt-get install libreoffice-math`); without it the PDF shows no equations. The tests catch this | Add to the environment setup if the build is rerun in a fresh environment |
| D3 | Supplementary table numbering | S1–S15 are grouped by topic; their first citations in the text are not in numerical order | Renumber only if the target journal requires it (`supplementary_tables()` in the builder) |
| D4 | Figure size | Figures are drawn at 180 mm and scaled to the 17 cm text width (fonts about 6.6 pt) | Supply the 180 mm vector PDFs from `figures/revised/` as separate figure files if the journal asks |
| D5 | Inline floats | Small white gaps (3–6 lines) at four page feet where a float does not fit | Normal for a review manuscript; journals usually re-typeset |
| D6 | Line numbers and 1.5 spacing | Chosen for review | Adjust to journal instructions |

## E. Closed in Phase 5C-2

- Main tables numbered in order of first citation.
- All 15 supplementary tables cited.
- One alphabetical reference list.
- Every reference cited (TEDAŞ 2025 from Table S12 only, with a note in the supplement).
- Life-cycle sources cited in the main text.
- Native numbered equations with a working internal reference.
- Figure 4 marker overlap resolved.
- Retired figure and equation images no longer used by the build.
