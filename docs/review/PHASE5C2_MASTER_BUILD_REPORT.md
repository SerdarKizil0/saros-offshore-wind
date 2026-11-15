# Phase 5C-2 — Master manuscript build (DOCX and PDF)

*15 November 2026. The master manuscript and the supplementary material were built as
editable, journal-neutral DOCX files, each with a matching PDF for review. Nothing was
submitted to a journal. The scientific models, input data, `results/revised/` and the
archive were not changed. Phase 5C-2 ends here.*

## 1. Deliverables and build

| File | Pages | Content |
|---|---|---|
| `manuscript/output/Saros_Offshore_Wind_Master.docx` | — | Title, author placeholder, abstract, keywords; Sections 1–6; Tables 1–6; Figures 1–4 with captions; eight numbered equations; declarations; references |
| `manuscript/output/Saros_Offshore_Wind_Master.pdf` | 25 | The DOCX rendered by LibreOffice |
| `manuscript/output/Saros_Supplementary_Material.docx` | — | Title page and Tables S1–S15 |
| `manuscript/output/Saros_Supplementary_Material.pdf` | 6 | The DOCX rendered by LibreOffice |

```bash
python scripts/12_build_figures.py                 # figures (Phase 5C-1)
python scripts/11_build_manuscript_sections.py     # text and tables from results/revised/
python scripts/10_build_docx.py                    # the four documents
python scripts/10_build_docx.py --check            # "documents up to date"
```

**Requirements:** pandoc 3.1 or later; LibreOffice with its **Math component**
(`apt-get install libreoffice-math`); poppler-utils for the tests.

The Math component was not installed in this environment. Without it, LibreOffice
leaves every equation blank in the PDF, while the DOCX is unaffected. It was installed
for this phase. The tests fail if the equations are missing from the PDF.

### Pipeline (`scripts/10_build_docx.py`, rewritten)

1. **Sources.** The script reads only the generated Markdown (`00`–`09`, `tables.md`,
   `supplementary_tables.md`) and the four PNG files in `figures/revised/`. The old
   script, which referenced `figures_final/figure*.png`, equation images and hard-coded
   captions, has been replaced.
2. **Floats.** Each table and figure is placed after the paragraph that first cites it.
   The one exception is Figure 1, which sits one paragraph later (`FLOAT_DEFER`) to avoid
   a large gap before the tall map.
3. **Equations.** pandoc converts the LaTeX of the eight equations into native Word
   equations (OMML). `scripts/docx_filter.lua` places each equation in a borderless
   three-column row, with its number (1)–(8) at the right margin. Each number carries a
   bookmark `eqN`, and "Eq. 6" in the text is an internal link to it.
4. **Styles.** A reference document is generated in code, so no binary template is
   stored. Layout:
   - A4; margins 2.5 cm top and bottom, 2.0 cm left and right; text width 17 cm.
   - Times New Roman 11 pt, 1.5 line spacing, justified.
   - Numbered headings 13 / 11.5 / 11 pt, kept with the next paragraph.
   - Table text 9 pt (8 pt for tables of eight or more columns), with the header row
     repeated on each page.
   - Captions 10 pt.
   - Page numbers in the footer; continuous line numbers in the master only.
   - Author placeholders shaded yellow.
5. **Post-processing.**
   - Table rules: top and bottom lines, a rule under the header, light inner lines.
   - Rows are never split across pages.
   - The sentence that introduces an equation is kept on the same page as the equation.
   - Figures are set to the full 17 cm text width.
   - Page setup and footer are added, and ZIP entries get fixed dates.
6. **PDF.** LibreOffice converts the DOCX to PDF, with lossless images and fonts embedded.
7. **Reproducibility.** `SOURCE_DATE_EPOCH` and fixed ZIP timestamps make rebuilds
   identical part by part. `--check` rebuilds both documents and compares every DOCX part
   and the PDF text.

## 2. Equations

| Check | Outcome |
|---|---|
| Native and editable | 8 OMML display equations (41 `m:oMath` objects in total, including inline symbols). No equation is an image, and the equation rows contain no drawing (tested) |
| Structure | (1) fraction of logarithms; (2) power with superscript; (3) summation ∑ with limits; (4) losses; (5) product; (6) ± with square root and overline; (7) bracketed fraction ×100 %; (8) accounting product (tested element by element) |
| Numbering | (1)–(8) in order, right-aligned in both DOCX and PDF (tested in both) |
| References | The only equation reference in the text, "Eq. 6", links to bookmark `eq6` (tested) |
| Rendering | Every equation was inspected in the PDF. None is clipped, and each stays on the same page as its introducing sentence |
| Notation | Three substitutions are made only in the DOCX build and do not change meaning; the Markdown source keeps the original LaTeX. `\mathrm{X}` becomes `\text{X}` (LibreOffice ignored the upright style and set CF, hub, ref and EF in italic). `\bar{Y}` becomes `\overline{Y}` (LibreOffice drew an acute accent). `\qquad` in Eq. 4 becomes two em spaces (LibreOffice drops LaTeX spacing commands) |

**Remaining difference.** LibreOffice draws parentheses that grow with their content as
thin brackets. They are legible and mean the same, but differ in appearance from Word.
LibreOffice also sets inline symbols about 1 pt larger than the 11 pt body text. In Word
the same OMML renders with Cambria Math.

## 3. Tables

- The six main tables and fifteen supplementary tables are editable Word tables. Each
  cell matches the generated Markdown exactly (tested cell by cell).
- **Renumbering.** Main tables were renumbered in order of first citation, because the
  category overview was cited after the node and product tables. Old 1, 3, 4, 2, 5, 6
  became 1–6, and the four text references were updated. The numbering is set by
  `TABLE_ORDER` in `scripts/11_build_manuscript_sections.py`. Content is unchanged; the
  5B-2 lock test compares after mapping the numbers back.
- **Supplementary citations.** S1, S12 and S13 were not cited anywhere. They are now cited
  in Methods (3.2 and 3.9). All fifteen are cited (tested).
- **Visual check.**
  - Column widths are proportional to content, and every column is at least as wide as
    its longest word.
  - Long tables break between rows and repeat the header.
  - No table overflows the margins. A visible failure in an early build, Table S12's MW
    column wrapping digit by digit, was fixed.
  - Digit groups (271 752), values with their % sign and coordinates (26.25° E) are held
    together by non-breaking spaces.

## 4. Figures

- Only `figures/revised/fig1`–`fig4` are used. The embedded images are byte-identical to
  the committed 600 dpi PNG files (tested by SHA-256). The figures are 17 cm wide (tested)
  and their captions come verbatim from `manuscript/09_figures.md` (tested).
- **Figure 4 marker overlap.** At manuscript size the dots of rows 2 and 3 overlapped. The
  generator now stacks dots that would overlap vertically within their row: a
  deterministic beeswarm with step 0.12 row and gap 0.7 %. Horizontal positions, which
  carry the values, are unchanged. The caption says the vertical position has no meaning.
  A new test checks that no two dots overlap, and the existing tests check every plotted
  value.
- **Figure 1 protected-area labels.** At 17 cm, "Saros ÖÇK (approximate) continues beyond
  the map →" and the legend entry "Saros ÖÇK boundary (approximate)" are legible. No
  change was needed.
- **Scaling.** The figures are drawn at 180 mm, so at 17 cm they are scaled by 0.944 and
  7 pt text prints at about 6.6 pt. Axes and legends were legible at that size in the
  inspected pages. Journals that take separate figure files should receive the
  180 mm vector PDFs from `figures/revised/`.
- The PDF embeds the 600 dpi PNG, because it is converted from the DOCX. The vector
  versions remain available as separate files.

## 5. References

- **One list.** The reference list is now a single alphabetical author–year list. The
  split into scientific and official documents and the "working list" note were removed
  from `src/08_references.md`. All 38 entries were kept, with their DOIs and URLs
  unchanged (tested against the register).
- **Life-cycle sources.** Schlömer et al. (2014) and Bonou et al. (2016) were cited only in
  Supplementary Table S14. They are now also cited in Methods 3.9, where the life-cycle
  intensities are described.
- **TEDAŞ (2025)** is cited only in the note to Table S12. The supplement states that the
  sources in its tables are listed in the manuscript's reference list.
- Every citation has an entry and every entry is cited (tested).
- No style was imposed, pending the target journal. Unresolved details are listed in
  `PHASE5C2_SUBMISSION_CHECKLIST.md`, section C.

## 6. Document integrity (tests)

`tests/test_docx_build_5c2.py` has 24 tests. They cover:

- all four files exist and are valid; A4 page size; fonts embedded; page setup, footer and
  line numbers;
- the title, the section order and every Level 2 heading;
- every prose paragraph of the generated Markdown occurs in the DOCX;
- equations (count, structure, numbering, links, PDF rendering);
- tables (cell by cell, numbering, first-citation order, repeated header);
- supplementary tables and their citation;
- figures (bytes, width, captions, placement);
- references;
- primary numbers equal the results;
- retired values, methods and claims are absent;
- framing and qualifications survive;
- author placeholders are kept and highlighted;
- every word of nine or more letters, every caption and every reference in the DOCX also
  appears in the PDF;
- a fresh build reproduces the committed files.

**Full suite: 328 passed, 0 failed.** The automated tests check completeness and
consistency, not appearance. Appearance was checked by rendering every page of both PDFs
at 70 dpi, and the critical regions (equations, Figures 1 and 4, wide supplementary
tables) at 110–150 dpi.

## 7. Visual QA log

| Found in an earlier build | Resolution |
|---|---|
| All equations blank in the PDF | LibreOffice Math installed; the test now requires the equations in the PDF |
| CF and EF in italic, Ȳ drawn with an acute accent, no space in Eq. 4 | OMML-compatible notation (§2) |
| Line number printed next to the page number | `suppressLineNumbers` in the footer and on the page-break paragraph |
| Narrow columns wrapping ("N o.", "Windo w", "WS W", "24 7.0") | Width rule based on the longest word; compact style and margins for wide tables |
| Monospaced checksum in S1 too large | Verbatim style set to Courier New 8 pt |
| Author placeholders not visibly marked (Word ignores highlight in styles) | Shading in the character style; the regex also matches "[AUTHOR TO CONFIRM against …]" |
| Equation separated from its introducing sentence | Keep-with-next on the introducing paragraph |
| Figures only 14.8 cm wide (pandoc capped them) | Set to 17 cm in post-processing |
| Two references alone on a last page | Reference spacing tightened (25 pages) |
| Figure 4 dots overlapping | Deterministic stacking (§4) |

A suspected blank half-page before Section 4 turned out to be the bottom margin of a full
page; it was not a layout fault.

**Remaining gaps.** Short white spaces of 3–6 lines remain where a figure or a table with
its caption does not fit at the foot of a page (pages 3, 10, 13 and 22). This is normal for
inline floats in a review manuscript.

The DOCX was rendered only through LibreOffice. Word may paginate slightly differently.
Open the DOCX in Word once before circulating it.

## 8. Changes to manuscript sources in this phase

| Change | Scope |
|---|---|
| Main tables renumbered by first citation; text references updated | `11_build_manuscript_sections.py`, `src/04_results.md`, `src/05_discussion.md` |
| Supplementary Tables S1, S12, S13 cited in Methods | `src/03_methodology.md` (three call-outs) |
| Schlömer et al. (2014) and Bonou et al. (2016) cited in Methods 3.9 | `src/03_methodology.md` (one citation) |
| One alphabetical reference list | `src/08_references.md` |
| Figure 4 caption: stacked dots | `src/09_figures.md` |

No number, method, result or qualification changed. Tests `test_manuscript_5b1/5b2`
were updated to permit exactly these changes.

## 9. Open items before independent peer review

See `PHASE5C2_SUBMISSION_CHECKLIST.md`. In short:

- author-dependent declarations (B1–B8);
- the Yildirim (2023) full text (A1, A2);
- re-checking the tender status in the week of submission (A5);
- a GWA 4.0 citation for the 2008–2017 period (A6);
- reference details (section C);
- one pass of the DOCX in Microsoft Word (D1).
