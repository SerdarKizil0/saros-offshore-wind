# Remaining submission items (after Phase 5D-1, manuscript frozen)

*16 November 2026. This list replaces `PHASE5C2_SUBMISSION_CHECKLIST.md` as the working
list; the earlier file is kept as a record. The scientific manuscript is **frozen** (see
`PHASE5D1_FINAL_REVISION_REPORT.md` §8). The items below are author actions, external
sources or formatting choices. None requires a new analysis. "Text change" says whether
closing the item would alter the manuscript text; any such change is a frozen-manuscript
exception and must be limited to that item.*

## A. Author-dependent items (marked `[AUTHOR TO CONFIRM]` and shaded in the DOCX)

| # | Item | Where | Text change |
|---|---|---|---|
| A1 | Author names, affiliations, corresponding author | Title page of the master and the supplement | Yes (placeholder) |
| A2 | Author contributions, for example CRediT | Declarations | Yes (placeholder) |
| A3 | Funding statement | Declarations | Yes (placeholder) |
| A4 | Conflicts of interest of every author | Declarations | Yes (placeholder) |
| A5 | Use of generative AI: wording to the journal's policy and the authors' responsibility statement | Declarations | Yes (placeholder) |
| A6 | Repository location, archived-release DOI, software licence | Data and Code availability | Yes (placeholder) |
| A7 | Acknowledgements | Declarations | Yes (placeholder) |
| A8 | Target journal | Determines reference style, declaration headings, word and figure limits, line numbering and spacing | Formatting only |

## B. External sources and date-sensitive facts

| # | Item | Status after 5D-1 | What closes it | Blocking |
|---|---|---|---|---|
| B1 | **Yildirim (2023) full text** (doi:10.1007/s10098-022-02392-0) | Not accessible by legitimate means in this environment. The 16 November 2026 attempt found no open-access copy (Unpaywall: closed), no abstract in the Semantic Scholar record (elided by the publisher), and that the publisher page requires authentication. The Introduction states that the full text was not available and does not compare the two studies | An author reads the article (institutional access or interlibrary loan) and either confirms the paragraph in §1 or adds a sentence on its study area. A numerical comparison should be added only if area and method allow | **Yes**, or disclose explicitly to editor and reviewers |
| B2 | Spatial relation of the Yildirim Saros region to the 2026 polygon | Undetermined; stated in the text | B1 | With B1 |
| B3 | YEKA DÜRES-2026 tender status | Draft as of 14 November 2026; the text dates the statement | Re-check MENR notices and the Official Gazette in the week of submission; update §1 and §2.2 only if the status changed | **Yes** (date-sensitive) |
| B4 | Database literature sweep (Scopus or Web of Science, including Turkish journals and theses) | Not done; the manuscript makes no novelty claim and calls its contributions "limited" | An author runs the queries; any relevant hit is added to §1 | Recommended |
| B5 | Studies cited for their topic only (Argin 2019; Emeksiz & Demirci 2019; Görmüş 2022; Demirci 2026; Satir 2018; the ERA5 evaluation papers) | Cited only for the scope stated in their titles or abstracts | An author reads them before submission | Recommended |
| B6 | Legal currency of the 2010 ÖÇK boundary | No amendment found; disclosed in §2.4 | Official map service or written confirmation | No |
| B7 | Licence of the GWA extract stored in the repository | Not checked | Provider terms | Before the repository is made public |

**Closed in Phase 5D-1 (no longer open):**
- GWA 4.0 reference period: now cited to Hansen et al. (2025), DTU report E-0256, read in full.
- ERA5 resolution: confirmed in the Hersbach et al. (2020) abstract and the ECMWF and CDS documentation.
- Duzcan & Kara page range: Crossref.
- Zippenfenig year and version: DataCite 2024, v1.4.0.
- Author initials of seven entries: Crossref given names.

## C. Reference details that remain incomplete (recorded, not invented)

| # | Entry | Missing | Source of the fix |
|---|---|---|---|
| C1 | Hersbach et al. (2020) (43 authors), Davis et al. (2023) (22), Dörenkämper et al. (2020) (18), Schlömer et al. (2014) | Full author lists not entered ("et al.") | Apply the journal's rule for long author lists (A8) |
| C2 | Official Gazette 29852 (2016) | No URL | Official Gazette archive |
| C3 | UNFCCC (2018), Tool 07 v07.0 | PDF not downloaded here; metadata from the UNFCCC tool index | Download and confirm the version and annex |
| C4 | Official and Turkish-language documents | No access dates; translated titles in brackets | Journal style (A8) |
| C5 | Whole list | Journal-neutral author–year format | Apply the style after A8 |

## D. Presentation and build

| # | Item | Status | Action |
|---|---|---|---|
| D1 | Rendering in Microsoft Word | Inspected only through LibreOffice; the PDF is the LibreOffice rendering | Open the DOCX in Word once: check equations (Cambria Math), pagination and the shaded placeholders |
| D2 | Build dependency | The PDF needs LibreOffice with its Math component (`libreoffice-math`); the tests detect missing equations | Install it when rebuilding in a fresh environment |
| D3 | Figure files | Figures are drawn at 180 mm and placed at the 17 cm text width (fonts about 6.6 pt) | Supply the 180 mm vector PDFs from `figures/revised/` as separate files if the journal asks |
| D4 | White space | A few pages end early where a figure or a table with its caption does not fit (see the report §6) | Normal for a review manuscript; journals re-typeset |
| D5 | Supplementary table order | S1–S15 grouped by topic; first citations are not in numerical order | Renumber only if the journal requires it |

## E. Not required

No item above calls for new data, new modelling, a new turbine, a CDS re-download or
additional sensitivity experiments. The following were considered in Phase 5D-0 and
deliberately not done, as optional work outside the manuscript's claims:
- a trend test;
- a permutation test;
- a power-curve shift experiment;
- an ÖÇK datum shift experiment.
