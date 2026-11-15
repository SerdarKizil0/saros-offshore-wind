# Phase 5C-1 — Publication figures and manuscript integration

*15 November 2026. A new set of four publication figures was built from the
1994–2024 results and linked into the manuscript. The scientific models, the
wind inputs, `results/revised/` and the archive were not changed. No DOCX or
PDF manuscript was built. Phase 5C-2 has not started.*

**Reproduce**

```bash
python scripts/12_build_figures.py            # regenerate figures/revised/
python scripts/12_build_figures.py --check    # "figures up to date"
python scripts/11_build_manuscript_sections.py --check
python -m pytest -q                           # 303 passed
```

---

## 1. Figure architecture

The set has four figures. Together they cover the six priorities, and the
central contribution (sensitivity and representativeness) gets three of the
four.

| Figure | File stem | Content | Priorities |
|---|---|---|---|
| 1 | `fig1_site_map` | Candidate polygon; the three ERA5 nodes on 40.50° N (primary filled, neighbours open) with the outlines of their 0.25° cells and each cell's ERA5 land fraction; bathymetry (EMODnet DTM 2024) with the 10/50 m screening isobaths; reconstructed ÖÇK boundary and overlap; CRS, scale bar, north arrow and source note | 1, plus bathymetry |
| 2 | `fig2_temporal_sensitivity` | (a) Net yield of each year 1994–2024 with the long-term mean, with the 2014–2024 comparison years shaded. (b) All 36 rolling 11-year windows of 1979–2024, relative to the primary estimate; windows inside 1994–2024 filled, earlier windows open, 2014–2024 emphasised | 2, 3 |
| 3 | `fig3_nodes_and_products` | Shared longitude axis showing the polygon's longitude range and the cell boundaries. (a) Net yield at the three nodes, 1994–2024, with land fraction and difference. (b) Mean 100 m speed for the GWA period 2008–2017: ERA5 per node, GWA 4.0 sea pixels per cell, and the GWA 4.0 polygon mean, with the GWA/ERA5 ratios | 4, 5 |
| 4 | `fig4_sensitivity_categories` | Six rows in the order of `sensitivity_index.json`, on one axis of relative change. Each row has its own kind of mark and a label stating its kind; nothing spans rows | 6 |

**Bathymetry** is part of the map rather than a separate figure. Its role is
limited to screening: depth range, the 10 m and 50 m classes, and the
deep-basin context. Table 5 already gives the depth statistics. A separate
depth figure would repeat the map without adding information.

**Retired figures.** The seven Phase 4C figures were generated from the
2014–2024 results and showed retired values (for example 2.427). They are
removed from `figures/revised/`, together with their generators, captions and
contact sheet. They remain in the git history (last at `9a6bc0a`).

| Retired figure | Reason |
|---|---|
| Annual energy and sampling interval | Replaced by Fig. 2a and Fig. 4, row 1 |
| Weibull fit | Weibull is a supplementary descriptive statistic (§3.10, Table S7) |
| Power curve | An assumption documented in §3.4; no result depends on seeing it. The superseded original curve it showed is not part of the revised paper |
| Energy sensitivity (speed scaling, losses) | Losses are in Fig. 4, row 6. Speed scaling is in Table S10, and its consequence is in Fig. 4, row 5 |
| Avoided CO₂ | Secondary accounting result; Table 6 covers it fully |
| Methodology diagram | Described the 2014–2024 workflow; the revised workflow is specified in §3 |
| Study area | Rebuilt as Fig. 1 |

`figures/F*.png` and `manuscript/figure*.png` are untouched pre-revision
material. `figures/README.md` now marks them as not for publication. The DOCX
script still references the latter (see §6).

---

## 2. Scientific accuracy: how each rule is met

| Rule | Implementation (and the test that enforces it) |
|---|---|
| Every value from `results/revised/` or documented geography | Each generator reads only `results/revised/` and, for the map and the polygon longitude range, the official KML, `config/site.py`, the EMODnet DTM and the decree points. Generators carry data checks that stop on disagreement. Tests compare each plotted array with the result files element by element |
| 1994–2024 baseline | Period strings come from the result files; the tests require 1994–2024 in Figs 2–4 and their captions. 2014–2024 appears only as the shaded comparison period and the emphasised window |
| GWA period explicit | "2008–2017" is in the panel heading, all three legend entries and the caption of Fig. 3, and in row 5 of Fig. 4. ERA5 in Fig. 3b is the period-matched value |
| Sampling interval is not total uncertainty | It appears only as row 1 of Fig. 4, labelled "the only probabilistic interval". No figure prints "confidence", "±", "total", "combined" or "bound" (tested) |
| Node differences are not confidence limits | Nodes are separate markers; no line joins them and no interval is drawn. The caption says they are not averaged and not limits on the resource |
| Protected-area reconstruction is not official | Map legend: "Saros ÖÇK boundary (approximate)". The caption says "an approximate reconstruction, not an official verified boundary" |
| No layout implied | No turbine, layout, cable or footprint artist exists (tested), and the caption says so. The illustrative grid of Table S15 is not drawn |
| GWA is not ground truth | Fig. 3 caption: "not an observation or ground truth … not used to correct the primary estimate". The scaled case in Fig. 4 is an open marker labelled "not adopted" |
| No combined distribution | Fig. 4 has no envelope, sum or total. Every data mark sits on its own row (tested); the caption says "not samples of one distribution … not combined" |

**Values computed inside the figure scripts:** the relative change
(value / primary − 1) × 100 for the annual values and the sampling-interval
ends (the definition used in the text), and, in the map, geometric quantities
(cell outlines, cell shares, distances). The cell shares agree with
`node_sensitivity.json` within 0.3 percentage points (tested). Their displayed
values in the caption are taken from the results file.

---

## 3. Production

- Shared style (`config/figure_style.py`): DejaVu Sans at 7, 8 and 8.5 pt,
  strokes of at least 0.5 pt, 180 mm width at final size, no rescaling.
- Okabe–Ito blue for ERA5 and data, vermillion for GWA or the one emphasised
  item. The palette passes the colour-vision checks (ΔE 21.9 protan, 3:1
  contrast). ERA5 and GWA are also told apart by marker shape.
- Exports: vector PDF with embedded TrueType fonts; SVG with editable text;
  600 dpi PNG. All three are deterministic. Only the map contains a raster
  layer (the bathymetry).
- Map: CRS (EPSG:32635) in the source note and caption; exact scale bar and
  true-north arrow; source note "MENR (2026a); EMODnet DTM 2024;
  Decision 2010/1089; ERA5 (C3S)".
- Every figure was rendered and inspected for collisions. The automatic checks
  cover overlap, clipping, text crossing boundary lines, minimum font size and
  minimum stroke width.
- `.gitignore` excluded `*.pdf`. An exception now versions
  `figures/revised/*.pdf`.

---

## 4. Manuscript integration

- **Captions**: `manuscript/src/09_figures.md`, rendered by the existing
  builder into `manuscript/09_figures.md`. Each caption takes its numbers from
  placeholders and states what is shown, the period and the limits. Each is
  preceded by an image link to its PNG, and the builder stops if a linked file
  is missing.
- **Call-outs** use the form "Fig. N". They were inserted without changing any
  sentence:

| Figure | Section 2 | Section 4 | Section 5 |
|---|---|---|---|
| 1 | 2.1, 2.4, 2.6 | 4.7 | — |
| 2 | — | 4.2 (2a), 4.3 (2b) | 5.2 (2b) |
| 3 | — | 4.4 (3a), 4.5 (3b) | 5.4 (3b) |
| 4 | — | 4.6 | 5.3, 5.5 |

  First mentions follow numerical order (tested). The Abstract, Introduction,
  Conclusions and declarations contain no call-outs.
- **Section 2.4**: the call-out sits after "reading the coordinates as WGS 84",
  not after "the eastern arm". The following sentence begins "The figure is
  approximate…", where "figure" means the overlap value, and must not read as
  a reference to Fig. 1.
- **Builder**: `09_figures.md` was added to the build. Reflow now keeps
  "26.25° E" on one line, which changed one line break in the generated
  Section 2.
- **Unchanged**: no number, equation, table or method changed. With the
  call-outs removed, the sources of Sections 2 and 4 are byte-identical to
  Phase 5B-1 (tested). Tables 1–6 and the supplementary tables are unchanged.

---

## 5. Tests

| Before | After |
|---|---|
| 318 passed, **5 failed** (byte comparison of PDF/PNG) | **303 passed, 0 failed** |

| Change | Tests |
|---|---|
| `tests/test_phase4c_figure.py` (18) and `tests/test_phase4c_final_figures.py` (16) removed | Their figures were retired. They contained the archive pin (`FIGURE_RESULTS`) and the five byte tests |
| `tests/test_phase4c_study_area.py` (27) → `tests/test_fig1_site_map.py` (31) | All geometry, bathymetry, ÖÇK, scale, north-arrow, CRS and layout checks kept. New checks: node positions from the results; cells exactly ±0.125°; cell shares against the results; land-fraction labels; CRS and source note; caption read from the manuscript |
| `tests/test_figures_5c1.py` (17 functions, 29 cases) | Set composition; content comparison with the generators; proof that the comparison catches a real change and ignores recompression; generators read only authoritative inputs; layout, typography and strokes; vector exports; no retired values or probability language; element-by-element provenance for Figs 2–4; periods, units and the GWA period; nodes not joined; rows of Fig. 4 never combined; captions; call-out order |
| `tests/test_manuscript_5b2.py` | Captions included in all prose checks (hand-typed numbers, vocabulary, units). The unchanged-substance check now removes call-outs before comparing and requires that they exist |

**The five byte failures are resolved, not skipped.** The committed figures
are compared with a fresh rendering by content:

- SVG markup without the version metadata;
- decoded RGBA pixels of the PNG and of the embedded rasters;
- PDF page size, fonts and image count.

A test shows that a one-pixel-block change or an edited label is detected,
and that recompressing identical pixels is not reported as a change.

**Checks removed with the retired figures.** These were specific to those
figures, such as the Weibull histogram using every hour and the power-curve
interpolation identity in the plot. The underlying model checks remain in
`test_power_curve.py`, `test_phase3a_energy.py`, `test_phase3b_carbon.py` and
`test_phase5b0_sensitivity.py`.

---

## 6. Unresolved visual limitations and items for Phase 5C-2

1. **DOCX build**: `scripts/10_build_docx.py` still inserts
   `manuscript/figure1.png`–`figure7.png` with hard-coded old captions. 5C-2
   must use `figures/revised/fig1–fig4` (PDF or 600 dpi PNG) and the captions
   of `manuscript/09_figures.md`, and decide whether captions are placed with
   the figures or listed at the end, per journal style.
2. **Journal format**: all figures are 180 mm (double column). If the target
   journal prefers single-column figures, Figs 3 and 4 would need a narrower
   layout. Heights: Fig. 1 = 117.8 mm, Fig. 2 = 120 mm, Fig. 3 = 87.5 mm,
   Fig. 4 = 104 mm.
3. **Dense markers in Fig. 4**: rows 2 and 3 have 31 and 21 dots in a narrow
   range, and some overlap. Every value is present (tested), and white marker
   edges keep them apart. A beeswarm layout would be a cosmetic option.
4. **Map detail**: islets and enclosed water smaller than about 0.1 km² are not
   drawn. The ÖÇK continues beyond the frame. The map extent is that of the
   cropped DTM, so the Gelibolu shore is only a corner.
5. **Polygon share by cell**: the map geometry gives 27.9 / 62.4 / 9.7 %, and
   `node_sensitivity.json` gives 27.7 / 62.6 / 9.7 %. The difference comes from
   the raster method used in the results. The caption shows the results-file
   values.
6. **Font**: DejaVu Sans is embedded. If the journal requires Arial or
   Helvetica, change one token (`FONT_FAMILY`) and rebuild.
7. **Old material**: `figures/F*.png`, `figures_final/` and
   `manuscript/figure*.png` (pre-revision) are still in the repository and are
   marked not for publication. They can be deleted in 5C-2, once the DOCX
   build no longer uses them.
