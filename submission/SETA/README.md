# Submission package — Sustainable Energy Technologies and Assessments (SETA)

*16 November 2026. Prepared after the pre-submission corrections. The scientific
manuscript is frozen; nothing in this package changes a result.*

Build and check:

```bash
python scripts/13_build_submission_package.py          # Highlights.docx, Cover_letter_DRAFT.docx, MANIFEST.json
python scripts/13_build_submission_package.py --zip    # also Saros_SETA_submission.zip (not versioned)
python scripts/13_build_submission_package.py --check
```

## 1. Files to upload

The authoritative list with SHA-256 checksums is in `MANIFEST.json`.

| Role in the submission system | File |
|---|---|
| Manuscript (editable) | `manuscript/output/Saros_Offshore_Wind_Master.docx` |
| Manuscript (PDF, for reference) | `manuscript/output/Saros_Offshore_Wind_Master.pdf` |
| Supplementary material | `manuscript/output/Saros_Supplementary_Material.docx` (and `.pdf`) |
| Figures 1–4 (vector, 180 mm wide) | `figures/revised/fig1_site_map.pdf` … `fig4_sensitivity_categories.pdf` |
| Highlights (separate editable file) | `submission/SETA/Highlights.docx` |
| Cover letter (draft with author placeholders) | `submission/SETA/Cover_letter_DRAFT.docx` |

**Excluded.** `Gulf of Saros Yield Figure.pdf` is a legacy figure from the retired 2014–2024
CDS-based analysis and must not be uploaded. It is not in this repository and is not part of
the current 1994–2024 Open-Meteo-based manuscript. The following are also excluded, and the
package script refuses them:
- pre-revision figures (`figures/F*.png`, `figures_final/`, `manuscript/figure*.png`);
- the interactive HTML;
- anything in `results/archive/`.

## 2. Journal requirements

The official guide for authors
(https://www.sciencedirect.com/journal/sustainable-energy-technologies-and-assessments/publish/guide-for-authors)
returned HTTP 403 to automated access from this environment; this was not bypassed. The
following requirements were confirmed from search excerpts of that official page, retrieved
16 November 2026:

| Requirement | Package status |
|---|---|
| Abstract of at most 250 words | **Met.** The abstract was shortened to 248 words; content and numbers unchanged in substance |
| Highlights: 3 to 5 bullet points, each at most 85 characters including spaces, in a separate file | **Met.** 5 highlights of 73–81 characters |
| Graphical abstract encouraged, not required | Not prepared (optional) |
| Article types include full-length research articles | Submit as a research article |

**Must be confirmed on the guide page before submission.** These were not verifiable here:

| Item | Current state of the manuscript |
|---|---|
| Reference style (numbered or author–year; journal abbreviations) | Journal-neutral author–year list, 39 entries |
| Maximum number of keywords | 10 keywords |
| Length limit for research articles | Main text (Sections 1–6) about 8 500 words; 6 tables and 4 figures |
| Review model (single- or double-anonymised; separate title page) | Author placeholder on the title page |
| Form and position of the declarations: competing interests, CRediT, funding, generative-AI use, data availability | Present as sections with `[AUTHOR TO CONFIRM]` placeholders |
| Line numbering and spacing preferences | Continuous line numbers, 1.5 spacing |
| Figure file formats and resolution | Vector PDF (and 600 dpi PNG available) |

## 3. Remaining submission requirements

1. **Authors.**
   - Fill every `[AUTHOR TO CONFIRM]` placeholder: authors and affiliations, CRediT roles,
     funding, competing interests, the generative-AI statement, the repository location,
     DOI and licence, and acknowledgements.
   - Complete the cover letter, including the originality statement and any suggested
     reviewers.
2. **Journal format.** Apply the confirmed reference style, keyword limit and declaration
   format (§2) in the source files, then rebuild with `scripts/10_build_docx.py` and this
   script.
3. **Date-sensitive fact.** Re-check the YEKA DÜRES-2026 tender status in the week of
   submission and update §1 and §2.2 only if it changed.
4. **Recommended.**
   - Run a database literature sweep.
   - Open the DOCX once in Microsoft Word; it was rendered only with LibreOffice.
5. **Repository.** Check the licence of the stored GWA extract before making the
   repository public.
