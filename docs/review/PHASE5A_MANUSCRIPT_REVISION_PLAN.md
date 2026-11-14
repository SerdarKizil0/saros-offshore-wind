# Phase 5A — Manuscript integration audit and revision plan

*14 November 2026. Audit only. The manuscript, figures, scientific model and
`results/revised/` are unchanged. Nothing here starts Phase 5B.*

**What was read**

* Manuscript sources: `manuscript/00_abstract.md` … `06_conclusion.md`,
  `tables.md`, `REFERENCES_VERIFIED.md`, `FIGURE_BRIEFS.md` and
  `medium_yazisi.md` (both Medium material).
* The build script `scripts/10_build_docx.py`, with `equations/eq1–7.png` and
  `figures_final/figure1–7.png`.
* The rendered manuscript the author supplied: *off-shore.weibull.pdf*, Word for
  Microsoft 365, 13 June 2026, 27 pages.
* Review reports: Phase 1, 2A, 2B, 3A, 3B, 4A, 4B and 4C-FINAL
  (`docs/review/`).
* All files in `results/revised/` (the only numerical authority) and the
  relevant parts of `config/` and `scripts/03`/`04`.

Line numbers refer to the files at commit `533fbf6`. Every source file has one
line per wrapped line, so a range `l.21–24` marks a paragraph position.

**Classes**

* **Critical (C):** scientifically incorrect or misleading.
* **Major (M):** materially weakens the manuscript.
* **Minor (m):** presentation, terminology or formatting.

An *issue* is one required change. It may occur in several places, and each
issue is counted once.

---

## 0. Summary

| Class | Count |
|---|---|
| **Critical** | **18** |
| **Major** | **34** |
| **Minor** | **22** |
| Total | 74 |

**Bottom line.** None of the manuscript's headline results is current. Every
energy and avoided-emission value comes from the retired power curve and the
retired Weibull Monte Carlo. The avoided-CO₂ method subtracts CO₂-eq life-cycle
emissions from a CO₂-only factor, and it presents the alternative accounting
conventions as uncertainty bounds.

Four statements of fact are wrong:

* the zone is called *designated*; it is a *candidate* area;
* it is placed "north of the Gelibolu Peninsula"; it lies on the northern
  (Thrace) shelf;
* its depth is given as "~50 to >200 m"; EMODnet gives 1–62 m;
* its winter resource is said to "align with the winter peak in Turkish
  electricity demand"; the 2024 annual peak occurred in July.

Two required disclosures are absent: the ≈14.4% overlap with the Saros ÖÇK,
and the ERA5–GWA disagreement.

**Recommended order:**

1. Fix the build workflow and choose a single source of truth (§0.1).
2. Rewrite Methods (3.1–3.9) to the authoritative framework.
3. Regenerate Tables 1–6 from `results/revised/` by script.
4. Rewrite Results 4.1–4.4 and delete 4.5–4.6.
5. Correct Study Area 2.1–2.3.
6. Rewrite Discussion 5.1–5.4, Abstract, Introduction and Conclusion.
7. Correct and complete the references.
8. Do figure integration, numbering and automated consistency QA.

Details in §9.

### 0.1 What "the manuscript" currently is (workflow findings)

* **Text source.** The Markdown section files are concatenated by
  `scripts/10_build_docx.py` and converted with pandoc to
  `manuscript/Saros_OWF_manuscript.docx`. The .docx is not in the repository.
* **Figures.** The script inserts `figures_final/figure1–7.png` with **captions
  hard-coded in the script** (l.39–47). These captions carry retired values,
  including 2.62 TWh, 69× and P10–P90. The script also renames the provisional
  figure IDs through a `fix()` table (l.22–29).
* **Equations.** Every `$$…$$` block is replaced, **in order of appearance**,
  by `equations/eq1.png` … `eq7.png` (l.52–58). Adding, removing or reordering
  an equation silently attaches the wrong image.
* **Word-only content.** The supplied PDF matches the Markdown text, but it
  also contains a formatted reference list ("verified 13 June 2026") that
  exists only in the Word file. That list differs from `REFERENCES_VERIFIED.md`
  in four entries (§6.2), and its numbering restarts at 1 after item 21.
* **Separate material.** `medium_yazisi.md` and `FIGURE_BRIEFS.md` are Medium
  material, not part of the manuscript. Both carry retired numbers (69×,
  2.62 TWh, S4) (m21).

---

## 1. Section-by-section revision matrix

### 1.1 Cross-cutting issues (each counted once; locations listed)

#### Critical

| ID | Issue | Locations | Required change | Basis |
|---|---|---|---|---|
| **C01** | Primary energy estimate is Weibull convolution, with Monte Carlo P50 as headline | Abstract l.10–16; Intro l.71–76; §3.4 l.83–100; §3.5 l.110–118; §3.8 l.195–214; §4.2 l.49–56; §4.3 l.66–84; Concl. l.8–11; Table 3; Fig. 2 and Fig. 5 captions (build script l.41, l.45) | Primary method: empirical hourly power conversion, CF = ΣP(U_h)/(P_r·N), AEP = CF·P_r·8 766 h. Weibull fit kept as descriptive statistic and cross-check (−1.85% gross CF). New Methods subsections 3.4–3.6 (§9) | 3A §1; 4B §1; `energy_yield.json`, `weibull_crosscheck.json` |
| **C02** | Power curve presented as the "manufacturer power curve" | §3.5 l.107; Abstract l.12; Concl. l.9; Table 2 | "OEDB V164/9500 digitised power curve (third-party digitisation of a published graph; not manufacturer-certified; air density undocumented, 1.225 kg m⁻³ assumed); linear interpolation, zero below 3.5 and from 25 m s⁻¹; boundary points 25.0/25.01/30 m s⁻¹ added" | 2A §2; Fig. 4 caption |
| **C03** | All energy values come from the retired curve and estimator | §3.5 l.128–130; §4.2 l.49–62; §4.3; §4.4; §5.1 l.14; §5.3; Abstract l.21–27; Concl. l.19–25; Tables 3, 4, 7 | Replace using the map in §2 | `energy_yield.json`; `scenarios.json` |
| **C04** | Monte Carlo P10–P90 presented as the uncertainty of the results | Abstract l.15–16, l.22–24; Intro l.71–76; §3.8; §4.3 l.66–84; §5.3; Concl. l.10–11, l.19–21, l.27–28; Tables 3, 4, 6, 7; keywords | Four separate, labelled components, never combined: (i) 90% sampling CI of the 11-year mean (t-interval, 2.334–2.520); (ii) observed interannual variability (energy CoV 7.0%; 2014 −17.9%); (iii) loss scenarios (−8.3%/+6.5%); (iv) wind-speed sensitivity (±5%/±10% → −10.2/+10.0, −20.4/+19.7%). No P90, no "bankable" | 3A §2–3; `interannual_and_sampling.json`, `loss_scenarios.json`, `wind_speed_sensitivity.json` |
| **C05** | Life-cycle CO₂-eq subtracted from the CO₂-only grid factor | Eq. 7 (§3.7 l.154–158); Abstract l.14–15; §3.7 l.150–158; §4.4 l.88–94; Table 5 "Subtracted from grid EF" | Avoided operational grid CO₂ = Y × EF_CM (tCO₂). Life-cycle GHG reported separately in tCO₂-eq and never subtracted (different gases and boundaries) | 3B §1–2; `emissions.json` |
| **C06** | Generation average and operating margin used as "lower and upper bounds" and sampled from a triangular distribution | §3.7 l.168–171; §3.8 l.203–205; §5.3 l.63–66; Tables 5, 6 | Report operating margin, build margin and generation average as **alternative accounting conventions** (context), each a separate value, not bounds | 3B §2; Fig. 7 |
| **C07** | Life-cycle literature misquoted, and the conservatism claim is wrong | Intro l.19–20 ("8–14 … Schlömer et al., 2014"); §3.7 l.173–178 ("11 g … 8–14 … AR5 … without recycling credits … conservative (upper)"); Tables 5–6; in-file refs "IPCC 2025" (Intro l.114, Methods l.225) | AR5 Annex III: 8 / 12 / 35 g CO₂-eq kWh⁻¹ (min/median/max). Bonou et al. 2016: 7.8–10.9 g, recycling credited, much windier sites. Remove "IPCC 2025", "8–14" and "conservative upper estimate" | 3B §1; `emissions.json` |
| **C08** | Fuel-resolved fossil comparison: unsourced fuel shares, CO₂-eq fuel factors, boundaries mixed (1.98 Mt, 1.95 Mt, ≈69×, ≈757 g) | §3.7 l.180–188; §4.5 l.116–138; §5.3 l.68–74; Table 5 rows 4–6; Table 7; Fig. 6 (build l.46) | Remove. If a fossil-displacement case is wanted later, rebuild it from sourced TEİAŞ generation shares with CO₂ factors, as a separate convention (not in this revision) | 3B §4.5 |
| **C09** | Status misrepresented: "designated", "committed site", "siting decision has now been made", "Türkiye's first offshore wind development zone" | Abstract l.3–4; Intro l.44, l.50–60, l.62–66; §2.2 l.23–32; §3.1 l.5–8; §5.3 l.55–57; Concl. l.5–6, l.28–29 | "candidate offshore-wind YEKA announced by MENR on 13 May 2026 (notice 30615); not a declared YEKA and not an approved project; the draft tender (YEKA DÜRES-2026) covers 1 000 MWe for one of four candidate areas" | 4A §C1, C4 |
| **C10** | Zone location wrong: "central-southern part of the gulf, north of the Gelibolu Peninsula", "parallel to the peninsular coastline" | §2.1 l.10–11; §3.1 l.9, l.13–14; Table 1 l.15 ("Nearest landfall: Gelibolu") | Along the northern (Thrace) shelf of the gulf, 0.25–9.3 km offshore, ≥13.6 km from the Gelibolu Peninsula; parallel to the Thrace coast. Fig. 1 shows this | 1 §B7; Fig. 1 |
| **C11** | Bathymetry wrong: "~50 to >200 m", "deepening westward toward the inner basin", "deeper western margin … floating or exclusion" | §2.3 l.40–48; §5.4 l.113–117; Table 1 l.23–24 | EMODnet DTM 2024 inside the polygon: 1.0–61.6 m, median 27.8 m, P5–P95 7.2–54.7 m. 9.1% shallower than 10 m; 11.4% deeper than 50 m (southern strip, not a western margin). No cell deeper than 200 m. Fixed-bottom is plausible throughout; the open questions are the <10 m fringe, the 50–62 m strip and geotechnics | `site_screening.json` (bathymetry); 1 §B5–B7 |
| **C12** | Overlap with the Saros Special Environmental Protection Area (ÖÇK) not mentioned | — (missing in §2, §3, §5.4, Table 1) | Add to §2.2 or a new §2.x, Methods (screening), Table 1, §5.4: ≈25 km² (≈14.4%) of the zone, the eastern arm, lies inside the ÖÇK reconstructed from Decision 2010/1089. The annex states no datum, so the overlay is an approximate GIS reconstruction, not a legal boundary determination. ÖÇK status requires ministry permission and is not an automatic prohibition | `site_screening.json` (protected_area_overlap); 4A §B; Fig. 1 |
| **C13** | ERA5 node described as the "centroid grid cell" or as data "at the candidate-zone centroid" | §3.2 l.43–44; §4.1 l.5; §5.4 l.94; Table 3 title ("at the Saros centroid") | Nearest 0.25° node to the centroid, 40.50° N 26.25° E. It lies **outside** the polygon, 3.68 km from the boundary; 62.6% of the polygon is nearest to it. The box around it contains notable land share (12.8% in a 0.25° box; 41.7% in a 0.5° box) | `site_screening.json` (era5_node_representativeness); 2B §1.3, §2.1 |
| **C14** | S4 "theoretical maximum" (183 turbines, 1 739 MW, 4.56 TWh, 2.65 Mt) in Methods, Results and Tables | §3.6 l.143–144; §4.4 l.100–101; §4.6 l.148–150; Table 4 l.76 | Remove from all publication-facing results. If mentioned at all: "geometric packing limit at 7D × 5D (10.1 MW km⁻²), not a feasible capacity", with no energy or CO₂ values | 4A §A5; `scenarios.json` (retired) |
| **C15** | Winter-dominant resource said to "align with the winter peak in Turkish electricity demand driven by heating loads" | Abstract l.20–21; §4.1 l.21–24; §5.2 l.38–43; Concl. l.16–17, l.31 | Remove. Recent system data contradict the claim: Türkiye's 2024 annual peak load occurred on 23 July 2024, driven by cooling ([Ember](https://ember-energy.org/latest-insights/solar-surge-meeting-two-thirds-of-the-rise-in-turkiyes-peak-electricity-demand-in-2024/)). A supply–demand timing statement needs TEİAŞ hourly/monthly data and an explicit analysis, which is not in this study | External check, 14 Nov 2026 |
| **C16** | Reanalysis-derived shear exponent presented as "measured" and as a contribution | Abstract l.9–10; Intro l.67–68; §3.3 l.63–66; §4.1 l.31–35; Concl. l.8; Table 3 ("Measured shear exponent") | "derived from the ERA5 10 m and 100 m levels (model output, not measurement)". The 100→105 m effect is +0.24% relative to α = 0.10. Do not list it as a contribution | `wind_resource.json` (shear note); 2B §4 |
| **C17** | ERA5–GWA disagreement not disclosed; the resource level is implicitly treated as exact | — (missing in §3, §4, §5.4) | Add to Methods/Results and §5.4. At 100 m the ERA5 node mean is 7.12 m s⁻¹ against the GWA 4.0 polygon mean of 7.84 m s⁻¹ (ratio 1.10). This is inter-model disagreement, not a demonstrated ERA5 bias: GWA is ERA5-driven, the periods differ (2008–2017 vs 2014–2024) and neither is validated offshore here. A +10.1% speed scaling raises AEP by +20.0% (illustrative sensitivity) | `wind_speed_sensitivity.json` (gwa_reference, GWA case); 2B §1 |
| **C18** | "Low inter-annual variability (3.2%)" used to claim reliability, lower financial risk and high-confidence forecasts | Abstract l.19–20; §2.5 l.77; §4.1 l.26–31; §5.1 l.18–23; Concl. l.15, l.29–31; Table 3 | Annual mean speed CoV 3.35% (ddof 1; 1.83% without 2014). Annual **energy** CoV 7.0% (3.8% without 2014). 2014 is −17.9% in energy (−9.4% in speed against 2015–2024), corroborated as a calm year by the Çanakkale station. Remove the reliability, finance and forecast claims | `wind_resource.json`, `interannual_and_sampling.json`; 2B §2.3; 3A §6 |

#### Major

| ID | Issue | Locations | Required change | Basis |
|---|---|---|---|---|
| **M01** | Household and car equivalents (3 036 kWh, 2 tCO₂, 0.86 M, 0.76 M, 0.21–1.50 M, 0.19–1.33 M) | §3.7 l.188–191; §4.6 l.142–150; §5.3 l.75–79; Table 4 (two columns); Table 7; Fig. 7 (build l.47) | Remove. The primary sources are unverified, and the values rest on the old energy figures and on S4 | 4B §7.3; 3B §5 |
| **M02** | Grid factors labelled gCO₂-eq kWh⁻¹; the 434 (CO₂-eq) and 430 (CO₂) generation averages confused | Abstract l.14; Intro l.8–9; §3.7 l.163, l.169; §3.8 l.203; §5.3 l.60–64; Tables 5–6 | CM 0.6242, OM 0.7134 and BM 0.3567 are **tCO₂/MWh (CO₂ only)**. Generation average is 0.430 tCO₂/MWh (CO₂) or 0.434 tCO₂-eq/MWh (all GHGs, different unit) | 3B §1; `emissions.json` |
| **M03** | Combined margin called "officially sanctioned", "officially mandated", "removes the ambiguity" | §3.7 l.165–168; §4.5 l.130–137; §5.3 l.61–63 | "the official factor published for GHG-reduction calculations (the form states it *may be used*)"; the combined margin is a crediting convention, not a measured marginal response | 3B §1 |
| **M04** | DÜRES expanded as "Deniz Üstü Yenilenebilir Enerji Kaynak Alanları" | §2.2 l.25; §3.1 l.6–7 | In the draft specification DÜRES = "Deniz Üstü Rüzgâr Enerjisi Santrali". Use "Saros offshore-wind candidate YEKA (KML file 'SAROS DÜRES')" | 4A §C2 |
| **M05** | Date "14 May 2026" | Abstract l.3; Intro l.50; §2.2 l.23; §3.1 l.8; §5.3 l.57; Concl. l.6; Table 1 l.13 | 13 May 2026 (MENR notice id 30615) | 4A §C1; `config/site.py` |
| **M06** | "first four offshore wind candidate zones" / "first formal step" | Abstract l.3–4; §2.2 l.26–27 | Four offshore candidate areas were already announced in 2023 (Bandırma, Bozcaada, Gelibolu, Karabiga; secondary source). Confirm against the 2023 MENR notice, then write "following four candidate areas announced in 2023" or drop "first" | 4A §C3 [S] |
| **M07** | Self-description as "first peer-reviewed" assessment | Abstract l.6; §5.3 l.55–56; Concl. l.3 | Remove. "To our knowledge, no published assessment …" is acceptable only after a dated literature search | 2B §4; editorial |
| **M08** | "site-specific" and zone-wide claims from a single node | Abstract l.6; Intro l.65; §3.1 l.22; Concl. l.3 | "a reanalysis-based assessment at the nearest ERA5 node". Add that GWA models a ≈5% north–south gradient that one node cannot resolve | 2B §2.1, §4 |
| **M09** | Scenario labels and framing: "pilot", "first-allocation", "full Phase-2", "as-yet-unfinalised installed capacity"; 7D × 5D presented without source; 504/998 MW rounding | Abstract l.27–28; Intro l.75–76; §3.6 l.134–146; §4.4 l.96–100; §5.3 l.50; Concl. l.21–22; Table 4 | S1 247 MW, S2 503.5 MW, S3 997.5 MW as **illustrative** capacities. S3 ≈ the draft tender's 1 000 MWe, conditional on allocation to Saros. State that 7D × 5D is an assumption. Give densities (1.4 / 2.9 / 5.8 MW km⁻²) and note that one 8% wake value is used for all densities | 4A §A, §D; `scenarios.json`, `site_screening.json` (densities) |
| **M10** | National-context shares and the 5 GW extrapolation | Abstract l.25–27; §4.4 l.103–112 (incl. "13.1 TWh … 3.8%"); §5.3 l.51–53; Concl. l.23–24; Table 4 | S3: 0.70% of 2024 consumption, but only if the 347.9 TWh figure is verified from the primary TEİAŞ document (currently unverified); otherwise drop. S3 = 19.95% of the 5 GW 2035 target capacity, conditional on allocation. Remove the "entire 5 GW at Saros class" extrapolation: other areas have different resources | `scenarios.json` (consumption note) |
| **M11** | Mean wind power density 422 W m⁻² is the Weibull-derived value | Abstract l.19; §4.1 l.12–13; §5.1 l.6; Concl. l.14; Table 3; §3.4 l.99–100 | Empirical 416.8 W m⁻² (ρ = 1.225) as primary; Weibull 421.8 as cross-check | 4B §7.2; `wind_resource.json`, `weibull_crosscheck.json` |
| **M12** | Weibull fit framed as "excellent" and the KS statistic used as evidence; §4.3 explains the old difference | §3.4 l.95–100; §4.1 l.8–12; §4.3 l.76–84 | Descriptive only. Report R² = 0.998 and KS D = 0.022 without a p-value (autocorrelated hours). State the −1.85% gross CF difference and the 8–12 m s⁻¹ misfit. Delete the old deterministic-vs-MC paragraph | 3A §1; Fig. 3 caption |
| **M13** | Framing implies a definitive assessment: title "… under Uncertainty"; "reliable", "substantial", "quantitative, uncertainty-aware basis" | Title (build l.35); Abstract; Concl. l.27–32 | Frame as a **preliminary ERA5-based resource and avoided-emissions assessment**. Add one explicit sentence: not a bankable yield estimate, not a feasibility or buildability determination | Framework (Phase 5A brief); 4A §D5 |
| **M14** | Limitations section is incomplete | §5.4 l.83–122 | Add the items in §1.9 below (curve, air density, losses, single wake, static factors, life-cycle transfer, ÖÇK approximation, unscreened topics, period representativeness, hourly basis, draft tender status) | 2B–4B |
| **M15** | Regional benchmarks misquoted or uncited | §5.1 l.5–12 ("Gulf of Lion and the Aegean 800–1100"); §5.1 l.17–18 and §4.2 l.58–62 ("comparable to or better than several published Mediterranean assessments", "compares favourably") | Use verified values: Koletsis 2016, Aegean 500–800 and Gulf of Lion 700–1100 W m⁻²; Soukissian 2018, basin max ≈1 130. Cite specific studies or delete. Add a caution that cross-dataset comparisons inherit the ERA5-level issue (GWA polygon power density 534 vs ERA5 408 W m⁻² at 100 m) | `REFERENCES_VERIFIED.md` notes; 2B §1.2 |
| **M16** | Policy claims without a primary source: 5 GW 2035 target attributed to the World Bank roadmap; "highlighted in the Roadmap" | Intro l.53–55; §2.1 l.18–19; §3.1 l.16–23 | Cite the government source of the 5 GW target, or attribute it correctly. Verify that the Roadmap covers the Saros area before saying so | §6.3 |
| **M17** | "treats this officially designated boundary as fixed … which removes a common source of contestation" | §2.2 l.28–32 | Remove the contestation claim. The ÖÇK overlap shows the boundary is not free of environmental constraints | C09, C12 |
| **M18** | "The zone is traversed by the offshore continuation of the North Anatolian Fault" | §5.4 l.106–107 | "The gulf is traversed …". The fault's distance from the polygon was not computed | 4A §B |
| **M19** | "the standard error of the long-term mean falls below 2%" | §3.2 l.38–40 | Energy SE of the 11-year mean is 2.11% (classical), 2.02% (bootstrap), 2.11% (jackknife). Reword with these values, or drop | `interannual_and_sampling.json` |
| **M20** | Literature interannual-variability ranges contradict each other | §3.2 l.36–38 ("5–8% … Soukissian et al., 2018"); §5.1 l.19–21 ("2–8% … Soukissian et al., 2017") | Check both values against the papers. Keep one range with the correct paper and year (2018 = Int. J. Climatology; 2017 = Energies review) | §6.2 |
| **M21** | Shear uncertainty "propagated implicitly through the resource statistics" | §3.3 l.77–79 | Remove. Shear uncertainty is not propagated. State the +0.24% effect instead | `wind_resource.json` |
| **M22** | "above the threshold generally regarded as economically viable for offshore development" | §4.1 l.13–15 | Remove (no cited threshold; resource level uncertain by ±10% in speed) | 2B §4 |
| **M23** | Micro-siting claim: "rows can be oriented to minimise array wake losses … along the dominant northeast–southwest axis" | §4.1 l.42–45 | Qualify or remove. Only 31% of energy arrives within ±30° of the polygon's long axis. The energy-weighted axis is 41°, and rows along it are short (median 6, max 11 turbines) | 4A §A2; `site_screening.json` (wind_direction) |
| **M24** | Winter-dominance mechanism contradicts §2.1 and the data | §5.2 l.27–36 ("sheltered, northern position" vs §2.1 l.15–16 "open to the prevailing northerly flow"); secondary August maximum (7.55 m s⁻¹) ignored | Present the seasonality descriptively (Jan–Feb max, June min, August secondary peak). Offer any mechanism as a hypothesis with a citation | `wind_resource.json` (monthly) |
| **M25** | Polygon area and ÖÇK overlap exist in several versions | 172.5 km² (manuscript); 172.29 km² and 24.75 km² / 14.36% (`site_screening.json`, 50 m screening grid); 172.61 km² and 24.98 km² / 14.47% (exact polygon, UTM 35N; Fig. 1); 172.73 km² geodesic | Use one area in text and Table 1: 172.6 km², exact polygon, EPSG:32635, as in Fig. 1. Give the overlap as ≈25 km² (≈14.4%) with one footnote naming both methods. Label 172.3 km² as the screening-grid value wherever it appears | Fig. 1 generator checks; Phase 4C |
| **M26** | Müller et al. (2013) has conflicting bibliographic data | `REFERENCES_VERIFIED.md` #19 ("J. Geophys. Res. Solid Earth 118") vs Word list #19 (*Tectonophysics* 597–598, 34–49) | Tectonophysics, doi:10.1016/j.tecto.2012.08.003 (NTUA repository record). Correct `REFERENCES_VERIFIED.md`. Confirm the 21.2 mm yr⁻¹ and 5.6–8.9 km values on the cited pages | §6.2 |
| **M27** | Aksoy et al. (2022) has conflicting pages and DOI | `REFERENCES_VERIFIED.md` #18 (589–, ggab447); Word #18 (595–610, ggab481, single author, altered title) | Institutional record (ÇOMÜ): Aksoy, Meghraoui, Polonia, Çağatay, Yavuzoğlu, Önder, Ülgen; GJI 229(1), 589–604; doi:10.1093/gji/ggab462; title ends "…where is the western limit of the 1912 Mürefte–Şarköy earthquake rupture?". Confirm on the publisher page | §6.2 |
| **M28** | Yaltırak et al. 2008 cited in text; Word list substitutes Yaltırak et al. 2012 (Bababurnu Basin, Biga Peninsula) | §2.3 l.40; Word list #17; `REFERENCES_VERIFIED.md` #17 ⚠️ | Zone depths now come from EMODnet (C11). Keep a Yaltırak source only for gulf-scale morphology, and confirm which paper actually supports the −125 m shelf and −550/−700 m basin values | §6.2 |
| **M29** | ETKB/EVÇED cited as one 2024 document | Intro l.10; §3.7; Tables 5; ref lists | Two forms, both published 26.12.2025 for period 2023: FRM-039 Rev.03 (grid factors) and FRM-042 Rev.01 (generation average, fuel factors). Cite both, year 2025 | 3B §1, Sources |
| **M30** | References missing for the revised methods | — | Add (sources already identified in the review reports): MENR notice 30615; YEKA DÜRES-2026 draft specification; Official Gazette 27793 (Decision 2010/1089); EMODnet DTM 2024; OEDB turbine library (windpowerlib); GWA 4.0 with its DTU validation report; UNFCCC CDM Tool 07 v07.0. Details in §6.4 | §6.4 |
| **M31** | Build script hard-codes retired captions and the figure mapping | `scripts/10_build_docx.py` l.22–29, l.35–47 | Read the caption files in `figures/revised/*_caption.md` and the revised figures. Delete the `fix()` table. Set the new title | §5 |
| **M32** | Equation images inserted by position | `scripts/10_build_docx.py` l.52–58; `equations/eq1–7.png` | Use pandoc native TeX math (OMML in .docx), or regenerate the images with explicit labels. Never rely on position | §3 |
| **M33** | Two diverging manuscript versions | Markdown (repository) vs Word/PDF (13 June 2026; reference list only in Word) | Declare the Markdown plus build script the single source of truth for 5B/5C. Move the reference list into the repository (e.g. `manuscript/references.md` or BibTeX). Use Word only for final typesetting | §0.1 |
| **M34** | Text cites figures that are not in the revised set: wind rose (old Fig. 3) and monthly/interannual panels (old Fig. 4c–d) | §4.1 l.7, l.12, l.21, l.28, l.38 | Either cite values in text and Table 3 only, or add a supplementary figure built by a revised generator from `wind_resource.json`. Do not reuse `figures_final/` images | Phase 4C §7 |

#### Minor

| ID | Issue | Locations | Required change |
|---|---|---|---|
| m01 | Keywords "Weibull distribution", "Monte Carlo uncertainty" | Abstract l.33–35 | Replace with e.g. "empirical power conversion; sampling uncertainty; candidate area; ERA5"; keep "Weibull" only if still central |
| m02 | "35.7 km × 10.5 km" has no definition | §2.1 l.10; §3.1 l.13; Table 1 l.19–20 | State "bounding-box extents". Optionally add principal-axis 35.9 × 11.3 km |
| m03 | "funnel-shaped … strait system channels air masses" uncited | §2.1 l.14–17 | Cite or soften |
| m04 | Request box and "interior grid cells well inside the requested domain" | §3.2 l.40–44 | The box contains the 40.50° N row (26.00/26.25/26.50° E). Describe the node choice plainly |
| m05 | Shear: computed hourly, but one mean α applied; attributed to "proximity of the Gelibolu Peninsula" | §3.3 l.64–76; §4.1 l.31–34 | "hourly exponents; the trimmed mean ᾱ = 0.149 applied to all hours". The adjacent coast is Thrace; any interpretation needs care (reanalysis levels) |
| m06 | "method of moments" is in fact the Justus empirical formula | §3.4 l.92–95 | Rename. Add a citation for the formula (not identified in this audit) |
| m07 | "widely adopted as a reference in peer-reviewed Aegean and Mediterranean … assessments"; 105 m hub height unsourced | §3.5 l.104–108; Table 2 | Cite or delete. State 105 m as a model assumption (hub heights are project-specific) |
| m08 | 8 766 h and cut-in handling not explained | §3.5 | Define 8 766 h = 365.25 d. Leap years are handled through CF (96 432 h). Power is zero below 3.5 m s⁻¹ |
| m09 | "domestic-content requirements may influence the turbine specification"; "consistent with the convention in life-cycle offshore wind literature" | §3.6 l.135–139 | Cite the draft specification or delete. Delete the life-cycle-convention clause |
| m10 | "funnelling of northerly Thracian flow along the axis of the gulf toward the Çanakkale Strait" | §4.1 l.41–42 | Mark as interpretation, or cite |
| m11 | Direction shares by hours only | §4.1 l.37–41 | Keep hours (NE 25.8%, ENE 18.4%). Add energy shares (NE 33.0%, NNE 17.8%, ENE 17.3%, SSW 13.5%) and the 41° energy-weighted axis |
| m12 | "Duzcan and Kara (2022)" | Intro l.33 | 2023 (Int. J. Environ. Sci. Technol. 20, 4361–4374) |
| m13 | "Demirci (2026)"; in-file entry "Demirci, A." | Intro l.38; §5.4 l.111; Intro l.98 | Demirci, H.E., Tekince, Ö., Sezer, A., Bhattacharya, S. (2026); in text "Demirci et al., 2026" |
| m14 | "Yaltırak, 2002" | §2.4 l.54 | "Yaltırak and Alpar, 2002" |
| m15 | Koletsis et al. (2016) is a future-climate projection study, cited for the etesian regime | §5.2 l.32 | Check suitability, or replace with a climatology source the author has read |
| m16 | Outdated in-file "References cited in this section" blocks and notes (e.g. "Müller / Tüysüz 2007", "Kurt 2000", "IPCC 2025") | End of each section file | Delete after moving the reference list to one file. They are stripped by the build, but they mislead editors |
| m17 | Draft header: "target journal: Energies (MDPI). References verified 9 June 2026" | build l.36 | Update the date. Confirm the target journal: the figure style follows Elsevier energy journals |
| m18 | Approved caption files carry interim numbers | `figures/revised/saros_study_area_caption.md` ("Figure 2"), `annual_energy_uncertainty_caption.md` ("Figure 1") | Renumber to 1 and 5 (§5) |
| m19 | Future work lacks the cheap, specific next steps | §5.5 l.126–133 | Add: extracting the 26.00/26.50 nodes from the raw NetCDF; a period-matched ERA5 2008–2017 comparison with GWA; site air density; layout-resolved wake |
| m20 | No data/code availability statement | — | Add: repository, `results/revised/MANIFEST.json`, ERA5 licence and attribution, the status label "pre-submission model estimate" |
| m21 | Medium article and briefs carry retired numbers (69×, 2.62 TWh, S4, winter demand) | `manuscript/medium_yazisi.md`, `FIGURE_BRIEFS.md` | Do not publish until revised. Out of manuscript scope |
| m22 | General context statements uncited | Intro l.4–6 ("majority … natural gas and coal, much of it imported"); l.17–19 ("capacity factors … substantially exceed onshore") | Add sources or soften |

### 1.2 Abstract — `manuscript/00_abstract.md`

* **Remains valid:**
  * ERA5 hourly 2014–2024 (l.8–9) and the 105 m hub;
  * V164-9.5 MW as the reference turbine;
  * mean hub-height speed 7.17 m s⁻¹ (l.18);
  * per-MW reporting as the primary normalisation (l.27);
  * the limitation themes in l.29–31 (wake, resolution, no in-situ
    validation, fault).
* **Apply:** C01, C02, C03, C04, C05, C09, C15, C16, C18; M05–M08, M10, M11,
  M13; m01.
* **Rewrite target:** three sentences on the method (empirical hourly
  conversion with the OEDB curve; Weibull descriptive), followed by these
  results:
  * net CF 27.7%;
  * 2.43 GWh MW⁻¹ yr⁻¹ (90% sampling CI 2.33–2.52);
  * single years 1.99–2.65;
  * avoided operational CO₂ 1 515 tCO₂ MW⁻¹ yr⁻¹ (2023 combined margin);
  * life-cycle GHG ≈29 tCO₂-eq MW⁻¹ yr⁻¹, reported separately;
  * ERA5–GWA disagreement (±10% speed ≈ ±20% energy);
  * ≈14.4% ÖÇK overlap (approximate);
  * candidate status and the preliminary nature of the study.

### 1.3 Introduction — `manuscript/01_introduction.md`

* **Remains valid:**
  * l.3–12 (national context): keep 347.9 TWh only after verification (M10);
    fix units (M02);
  * l.25–40 (literature review), with the citation fixes m12–m13;
  * l.42–48 (gap), minus "committed site" (C09);
  * l.78–84 (outline): update to the new section structure.
* **Must change:**
  * l.14–23: life-cycle sentence (C07);
  * l.50–60: status, date and "siting decision" (C09, M05, M16);
  * l.62–76: the three contributions. Replace the "measured" shear exponent,
    "site-specific" and the Monte Carlo with reanalysis-based
    empirical-hourly energy, separated uncertainty components and
    avoided-CO₂ accounting by convention (C01, C04, C16, M08).
* **Apply:** C05, C07, C09, C16; M02, M05, M08, M09, M16; m12, m13, m22.

### 1.4 Study area — `manuscript/02_study_area.md`

* **Remains valid:**
  * §2.1 l.5–9: gulf-scale geography; centroid 40.557° N 26.198° E;
  * §2.4 entire (seismotectonics), with the citation fixes M26, M27, m14;
  * §2.5: mean speed and winter maximum.
* **Must change:**
  * §2.1 l.10–12 (C10, M25, m02);
  * §2.2 l.23–32 (C09, M04, M05, M06, M17);
  * §2.3 l.36–48 (C11, M28);
  * §2.5 l.77 (C18).
* **Add:** a short subsection *2.x Environmental designations and screening
  classes*:
  * the ÖÇK overlap (C12);
  * <10 m and <1 km fringe, 50–62 m strip (screening classes, not exclusions);
  * no overlap with the Gelibolu strictly protected area;
  * Greek Natura 2000 sites 14–15 km away;
  * the list of unscreened topics (birds, fisheries, navigation and LNG,
    military, fault distance, grid connection).

### 1.5 Methods — `manuscript/03_methodology.md`

* **Remains valid:**
  * ERA5 description (l.27–34);
  * Eq. 1;
  * no missing records (l.44–45);
  * α statistics (l.72–73: 0.149 / 0.142 / 0.054 / 0.074–0.252);
  * Weibull values k = 2.04, c = 8.08 m s⁻¹;
  * turbine specifications (3.5 / 14 / 25 m s⁻¹, 164 m, 9.5 MW);
  * nominal losses and Eq. 6;
  * the per-MW rationale (l.134–137, first clause);
  * linear scaling (l.144–146);
  * the 624.2 combined-margin value (unit fix) and Tool 07.
* **Must change:** C01–C07, C09, C10, C13, C14, C16; M02–M05, M09, M19, M20,
  M21; m04–m09.
* **Proposed structure** (replaces 3.1–3.8):
  1. 3.1 Study area and candidate status (C09, C10, M04, M05).
  2. 3.2 ERA5 data and node representativeness (C13, m04).
  3. 3.3 Hub-height reconstruction (C16, M21, m05).
  4. 3.4 Power curve and empirical hourly energy (C01, C02; new Eqs. 5–7).
  5. 3.5 Weibull fit as descriptive cross-check (M12, m06).
  6. 3.6 Uncertainty and sensitivity framework (C04, C17, M19; Eq. 9).
  7. 3.7 Site screening (C11, C12, M25).
  8. 3.8 Illustrative capacity scenarios (C14, M09).
  9. 3.9 Avoided grid CO₂ and life-cycle GHG (C05–C08, M01–M03; Eqs. 10–11).

### 1.6 Results — `manuscript/04_results.md`

* **Remains valid:**
  * mean 7.17, SD 3.66, median 6.96 m s⁻¹ (l.6–7);
  * Weibull k and c (l.9);
  * monthly values Feb 8.42, Jan 8.24, Jun 5.62, Aug 7.55 m s⁻¹ (l.19–21);
  * annual mean range 6.55 (2014) to 7.41 m s⁻¹ (2016) (l.26–28);
  * direction shares by hours: NE+ENE ≈44%, NE ≈26% (l.38–40).
* **Must change:**
  * §4.1: C15, C16, C18, M11, M12, M22, M23, M34, m10, m11;
  * §4.2: rewrite with the revised values (C01, C03, M15);
  * §4.3: replace with the four separate components (C04, M12; Figs. 5–6);
  * §4.4: C05, C14, M09, M10.
* **Delete:** §4.5 (C08) and §4.6 (M01).
* **New subsection:** *4.x Site screening*, presenting the Fig. 1 content and
  the ÖÇK overlap numbers (C12).

### 1.7 Discussion — `manuscript/05_discussion.md`

* **Remains valid:**
  * §5.4 wake (l.86–90): expand with the densities (M09);
  * validation (l.99–104);
  * seismic (l.106–111): fix M18;
  * single-zone scope (l.119–122);
  * §5.5 (with m19).
* **Must change:**
  * §5.1: M11, M15, C18, M20;
  * §5.2: rewrite descriptively (C15, M24);
  * §5.3: C03–C06, C08, C09, M01, M03, M07, M10;
  * §5.4 spatial resolution l.92–97 (C13, C17);
  * §5.4 bathymetric constraint l.113–117 (C11).
* **Add** to §5.4: M14 and C12.

### 1.8 Conclusion — `manuscript/06_conclusion.md`

* **Remains valid:** the structure (method → resource → results →
  limitations) and the limitation list in l.33–36.
* **Must change:**
  * l.3–11: C01, C09, C16, M05, M07;
  * l.13–17: M11, C18, C15;
  * l.19–25: C03, C04, C05, M10;
  * l.27–32: M13, C15, C18 ("reliable, low-variability resource whose
    winter-peaking profile is well matched to Turkish demand").

### 1.9 Limitations to add (M14; also C12, C13, C17)

1. A single ERA5 node outside the polygon, with land influence, and an
   unresolved north–south gradient (≈5% in GWA).
2. The ERA5–GWA level disagreement (ratio 1.10 at 100 m). This dominates every
   quantified term (≈±20% AEP).
3. Eleven years of record. Long-term representativeness is unknown; one calm
   year moves the mean by 1.8%.
4. The power curve is digitised, not certified. Air density, shear,
   10-minute vs hourly basis, curtailment and degradation are not modelled.
5. Losses are labelled assumptions. One wake value is used for every capacity
   density (S3 5.8 MW km⁻²; 6.8 MW km⁻² outside the ÖÇK).
6. Static 2023 grid factors. The combined margin is a crediting convention,
   not a forecast of future displacement.
7. Life-cycle intensities come from the literature for other, windier sites.
   They are not Saros-specific; rescaled Bonou values give ≈17–23 g kWh⁻¹.
8. The ÖÇK overlay is an approximate reconstruction (no datum stated); ÖÇK
   status means permission is required, not prohibition.
9. Topics not screened: bird migration, fisheries, navigation and LNG,
   military areas, fault distance, grid connection.
10. Policy status: candidate area; the tender specification is a draft;
    allocation of the 1 000 MWe to Saros is open.

### 1.10 Tables — `manuscript/tables.md` → §4. Figures and build → §5.

---

## 2. Old-to-new numerical replacement map

The **New** values are taken from `results/revised/`, file and key named. Apply
them through a table-generating script, not by hand (§9). "—" means remove.

### 2.1 Site and data

| Quantity | Old | Where | New | Source |
|---|---|---|---|---|
| Announcement date | 14 May 2026 | Abstract l.3; Intro l.50; §2.2 l.23; §3.1 l.8; §5.3 l.57; Concl. l.6; Table 1 | **13 May 2026** | `site_screening.json` polygon.source; 4A §C1 |
| Zone area | 172.5 km² | §2.1 l.10; §3.1 l.12; Table 1; build l.39 | **172.6 km²** (exact polygon, UTM 35N). Screening grid 172.3 km² | Fig. 1 generator; `site_screening.json` polygon.area_km2 (grid) |
| Extents | 35.7 × 10.5 km | §2.1; §3.1; Table 1 | Keep as bounding box; principal axis 35.9 × 11.3 km at 81° | `site_screening.json` polygon |
| Nearest coast | Gelibolu Peninsula | §2.1, §3.1, Table 1 | **Thrace coast (0.25 km)**; Gelibolu ≥13.6 km | 1 §B7 |
| Water depth in zone | ~50 to >200 m | §2.3; Table 1 | **1.0–61.6 m; median 27.8 m; P5–P95 7.2–54.7 m** | `site_screening.json` bathymetry.depth_m |
| Share <10 m / >50 m | — | new | **9.1% / 11.4%** (>60 m: 0.17%) | bathymetry.share_deeper_than_pct |
| ÖÇK overlap | — | new | **≈25 km² (≈14.4%)**; 24.75 km² / 14.36% (screening grid) and 24.98 km² / 14.47% (exact) | protected_area_overlap; Fig. 1 caption |
| ERA5 node | "centroid grid cell" | §3.2; §4.1; §5.4; Table 3 | **40.50° N 26.25° E, outside the polygon, 3.68 km from boundary; nearest node for 62.6% of the polygon** | era5_node_representativeness |
| Screening classes (182 grid positions) | — | new | <10 m: 14; 50–62 m: 19; <1 km of shore: 5; inside ÖÇK: 25; none: 123 | screening_classes_best_fit_layout |

### 2.2 Wind resource

| Quantity | Old | Where | New | Source |
|---|---|---|---|---|
| Mean / SD / median U_hub | 7.17 / 3.66 / 6.96 | §4.1; Table 3 | unchanged (7.17 / 3.66 / 6.96 m s⁻¹) | `wind_resource.json` U_hub |
| Wind power density | 422 W m⁻² | Abstract; §4.1; §5.1; Concl.; Table 3 | **417 W m⁻²** (empirical, ρ = 1.225); Weibull 422 | U_hub.power_density_wm2_rho1225; `weibull_crosscheck.json` |
| Weibull k, c | 2.04, 8.08 | §3.4; §4.1; Abstract; Concl. | unchanged (2.035, 8.080); descriptive | weibull_fit_U_hub |
| "MoM" k, c | 2.08, 8.10 | §3.4 l.95 | 2.08, 8.10 = **Justus formula** | k_justus_empirical, c_justus_empirical_ms |
| R², KS | 0.998, 0.022 | §3.4; §4.1; Table 3 | unchanged; no p-value | r2_cdf, ks_statistic, ks_note |
| Weibull vs empirical gross CF | — | new | **32.06% vs 32.66% (−1.85%)** | gross_cf_weibull, relative_difference_pct |
| Shear α | 0.149 "measured" | Abstract; §3.3; §4.1; Table 3 | 0.149, **ERA5-derived**; 100→105 m effect +0.24% vs α = 0.10 | shear_exponent_from_era5_10m_100m |
| Interannual variability | 3.2% | Abstract; §2.5; §4.1; §5.1; Concl.; Table 3 | **Speed CoV 3.35%** (1.83% without 2014); **energy CoV 7.0%** (3.8% without 2014) | annual_mean_cov_pct; observed_interannual_variability |
| Calm year | 2014 6.55 m s⁻¹ | §4.1 l.27 | keep, and add: 2014 net yield 1.99 GWh MW⁻¹ (−17.9%); speed −9.4% vs 2015–2024 | annual_energy.csv; 2B §2.3 |
| Direction | NE+ENE 44%; NE 26% (hours) | §4.1 | keep (25.8% + 18.4%); add energy: NE 33.0%, NNE 17.8%, ENE 17.3%, SSW 13.5%; axis 41° | direction_share_pct; site_screening wind_direction |
| ERA5 vs GWA at 100 m | — | new | **7.12 vs 7.84 m s⁻¹ (×1.10)**; scaled case 2.912 GWh MW⁻¹ (+20.0%) | `wind_speed_sensitivity.json` gwa_reference and GWA case |

### 2.3 Energy

| Quantity | Old | Where | New | Source |
|---|---|---|---|---|
| Gross AEP per turbine | 30.4 GWh | §4.2 l.50; Table 3 | **27.20 GWh** | `energy_yield.json` gross.gwh_per_turbine |
| Gross CF | 36.5% | §4.2 l.51; Table 3 | **32.66%** | gross_cf |
| Net AEP per turbine | 25.8 GWh | §4.2 l.53; Table 3 | **23.06 GWh** | net.gwh_per_turbine |
| Net CF | 31.0% (det.); 29.9% (MC P50; P10–P90 27.5–32.3) | §3.5; §4.2; §4.3; §5.1; Abstract; Concl.; Table 3 | **27.69%**; no P10–P90 | net_cf |
| Net yield | 2.71 (det.); 2.62 (MC P50; P10–P90 2.41–2.83) | §3.5; §4.2; §4.3; Abstract; §5.3; Concl.; Table 3 | **2.427 GWh MW⁻¹ yr⁻¹; 90% sampling CI 2.334–2.520** (t, df = 10); bootstrap check 2.340–2.500 | net.gwh_per_mw; sampling_ci_of_11yr_mean |
| Full-load hours | 2 714 h | §3.5; §4.2; Table 3 | **2 427 h** | net_full_load_hours |
| CoV of MC yield | 6.3% | §4.3 l.72–74 | — (remove) | — |
| Single-year range | — | new | **1.99 (2014) – 2.65 (2020) GWh MW⁻¹ yr⁻¹** | observed_interannual_variability |
| Loss scenarios | triangular samples | §3.8; Table 6 | **low 2.586 (+6.5%), nominal 2.427, high 2.225 (−8.3%)** | `loss_scenarios.json` |
| Wind-speed sensitivity | — | new | **−10%: 1.931 (−20.4%); −5%: 2.180 (−10.2%); +5%: 2.670 (+10.0%); +10%: 2.905 (+19.7%)** | `wind_speed_sensitivity.json` |

### 2.4 Emissions and scenarios

| Quantity | Old | Where | New | Source |
|---|---|---|---|---|
| Avoided CO₂ per MW | 1 525 tCO₂ (P10–P90 1 277–1 754), lifecycle-net | Abstract; §4.3; §4.4; §5.3; Concl.; Tables 3, 4 | **1 515.2 tCO₂ MW⁻¹ yr⁻¹** (combined margin 0.6242 tCO₂/MWh); sampling CI **1 457–1 573** (energy only, fixed factor) | `emissions.json` primary_avoided_operational_co2 |
| Context conventions | "bounds" 434 / 713.4 g | §3.7; §5.3; Table 5 | **OM 1 731.7; BM 865.8; generation average 1 043.8 tCO₂ MW⁻¹ yr⁻¹** (CO₂); generation average CO₂-eq 1 053.5 tCO₂-eq (other unit) | context_grid_methods |
| Life-cycle | 11 g (8–14), subtracted; "<2%" | Abstract; Intro; §3.7; §4.4; §4.5; §5.3; Concl.; Tables 5–7 | **29.1 tCO₂-eq MW⁻¹ yr⁻¹** (AR5 median 12 g); range **19.4–85.0** (8–35 g); Bonou 18.9–26.5; separate; drop the "<2%" comparison (different units and boundaries) | secondary_lifecycle_ghg |
| S1 | 26 / 247 MW; 0.65 TWh; 0.38 Mt | §3.6; §4.4; Table 4 | **247 MW; 600 GWh yr⁻¹ (577–623); 374 kt CO₂ yr⁻¹ (360–389)** | `scenarios.json` S1 |
| S2 | 53 / 504 MW; 1.32 TWh; 0.77 Mt | same | **503.5 MW; 1 222 GWh yr⁻¹ (1 175–1 269); 763 kt (734–792)** | S2 |
| S3 | 105 / 998 MW; 2.62 TWh; 1.52 Mt (1.27–1.75) | same; Abstract; §5.3; Concl.; Tables 4, 7 | **997.5 MW; 2 421 GWh yr⁻¹ (2 328–2 514); 1 511 kt CO₂ yr⁻¹ (1 453–1 569)**; life cycle 29.1 kt CO₂-eq (19.4–84.7) | S3 |
| S4 | 183 / 1 739 MW; 4.56 TWh; 2.65 Mt | §3.6; §4.4; §4.6; Table 4 | — (retired) | `scenarios.json` retired |
| Share of 2024 consumption (S3) | 0.8% / 0.75% | Abstract; §4.4; §5.3; Concl.; Table 4 | **0.70%**, only if 347.9 TWh is verified | S3.share_of_2024_consumption_pct |
| Share of 2035 target (S3) | 20% | same | **≈20% (19.95%)**, conditional on allocation | S3.share_of_2035_offshore_target_capacity_pct |
| 5 GW "Saros-class" output | 13.1 TWh, 3.8% | §4.4 l.107–109 | — (remove) | — |
| Scenario densities | — | new | **1.43 / 2.92 / 5.79 MW km⁻²** (S1/S2/S3, full polygon) | `site_screening.json` active_scenarios_density |
| Fossil pathway, 69×, 1.98 / 1.95 Mt, fuel split | as listed | §3.7; §4.5; §5.3; Tables 5, 7 | — (remove, C08) | — |
| Households, cars | 0.86 M; 0.76 M; ranges | §3.7; §4.6; §5.3; Tables 4, 7 | — (remove, M01) | — |

---

## 3. Equations requiring changes

Current numbering follows the order of `$$` blocks, which is also the image
mapping (`eq1–7.png`).

| No. | Current (location) | Action | Revised form |
|---|---|---|---|
| 1 | U_h = √(u_h² + v_h²) (§3.2 l.50) | **Keep** | unchanged |
| 2 | U(z) = U(z_ref)(z/z_ref)^α (§3.3 l.61) | **Modify** (m05) | U_hub,t = U_100,t (105/100)^ᾱ, with one ᾱ for all hours |
| 3 | α = ln(U₁₀₀/U₁₀)/ln(100/10) (§3.3 l.68) | **Keep; reword text** (C16) | α_t from the ERA5 10 m and 100 m levels; hours with both > 1 m s⁻¹; 1–99% trimmed; ᾱ = mean |
| 4 | Weibull pdf (§3.4 l.87–88) | **Keep; descriptive** (M12) | unchanged |
| 5 | AEP_gross = 8766 ∫P(U) f(U) dU (§3.5 l.113) | **Replace** (C01) | CF_g = (1/(N·P_r)) Σ_{t=1}^{N} P(U_hub,t), with N = 96 432 h, P_r = 9.5 MW, P(·) OEDB linear interpolation, P = 0 for U < 3.5 or U ≥ 25 m s⁻¹ |
| 6 | AEP_net = AEP_gross(1−L_w)A(1−L_e) (§3.5 l.124–125) | **Modify** | η = (1−L_wake)·A·(1−L_elec) = 0.84778; CF_n = η·CF_g |
| 7 | E_avoided = EF_grid − EF_wind (§3.7 l.154) | **Delete** (C05) | — |
| new 7 | — | **Add** | Y = CF_n · 8 766 h (MWh MW⁻¹ yr⁻¹); AEP_turbine = Y · 9.5 MW |
| new 8 | — | **Add, optional** (cross-check) | CF_g,W = (1/P_r) ∫₀^∞ P(U) f(U; k, c) dU; reported only against CF_g |
| new 9 | — | **Add** (C04) | Ȳ ± t_{0.95,10} · s_Y/√11, where Y_i are the 11 annual net yields, each normalised to 8 766 h |
| new 10 | — | **Add** (C05) | C_avoided = Y · EF_CM, with EF_CM = 0.6242 tCO₂ MWh⁻¹ (tCO₂ MW⁻¹ yr⁻¹). Context: the same with EF_OM, EF_BM, EF_GA |
| new 11 | — | **Add** (C05) | G_LC = Y · I_LC / 1000, with I_LC in gCO₂-eq kWh⁻¹ (tCO₂-eq MW⁻¹ yr⁻¹). Reported separately; not subtracted |
| optional | — | **Add if useful** | EF_CM = 0.75·EF_OM + 0.25·EF_BM (Tool 07 weights; reproduces 0.6242) |

**Build consequence (M32).** The revised set has 10–12 equations instead of
7. The positional PNG substitution must be removed before Phase 5B text is
built.

---

## 4. Table replacement plan

| Table | Current content | Action | Revised content | Source |
|---|---|---|---|---|
| **1** Zone specifications | 14 May; "nearest landfall Gelibolu"; 172.5 km²; depth ~50 to >200 m (Yaltırak 2008); "fixed-foundation-compatible" | **Regenerate** | Status (candidate YEKA, notice 30615, 13 May 2026; draft tender). Coast: Thrace, 0.25 km. Area 172.6 km². Centroid. Extents. Depth 1.0–61.6 m (median 27.8; P5–P95 7.2–54.7; 9.1% <10 m; 11.4% >50 m). ÖÇK overlap ≈25 km² (≈14.4%, approximate). ERA5 node (outside, 3.68 km, 62.6%). NAF in the gulf (distance not computed) | `site_screening.json`; Fig. 1 generator |
| **2** Turbine | specifications; "monopile (assumed)" | **Revise** | Add rows: power curve "OEDB V164/9500 digitised, 49 points 0–24.5 m s⁻¹, not certified, ρ undocumented (1.225 assumed)"; boundary points; hub height 105 m (assumption). Foundation "fixed-bottom (assumed; not assessed)" | `config/turbine.py`; 2A §2 |
| **3** Resource and energy | two columns (deterministic and MC P50, P10–P90) | **Regenerate, one column** | Mean, SD, median; empirical power density 417 (Weibull 422); k, c, R², KS; α (ERA5-derived); speed CoV 3.35%; energy CoV 7.0%; gross 27.20 GWh/turbine, CF 32.66%; net 23.06 GWh, CF 27.69%; **2.427 (90% sampling CI 2.334–2.520)**; FLH 2 427 h; Weibull cross-check −1.85%; single-year range 1.99–2.65. Move avoided CO₂ to Table 5 | `wind_resource.json`, `energy_yield.json`, `weibull_crosscheck.json`, `interannual_and_sampling.json` |
| **4** Scenarios | S1–S4; MC P50 (P10–P90); households and cars; demand share | **Regenerate, S1–S3 only** | Name ("illustrative"), turbines, MW, density, energy GWh yr⁻¹ (sampling CI), avoided CO₂ kt yr⁻¹ (sampling CI), life cycle kt CO₂-eq (reference and range), share of the 5 GW target, share of consumption (only if verified). Footnote: 7D × 5D assumption; one wake value; S3 conditional on the draft tender | `scenarios.json`, `site_screening.json` |
| **5** Emission factors | gCO₂-eq labels; "MC bounds"; fuel factors; life cycle "subtracted" | **Regenerate** | CM 0.6242 (primary), OM 0.7134, BM 0.3567, generation average 0.430 tCO₂/MWh, each with its avoided tCO₂ MW⁻¹ yr⁻¹. Generation average 0.434 tCO₂-eq/MWh flagged as a different unit. Life cycle AR5 8/12/35 and Bonou 7.8/10.9 g CO₂-eq kWh⁻¹ → tCO₂-eq MW⁻¹ yr⁻¹, "not subtracted". Sources FRM-039 and FRM-042 (2025) | `emissions.json` |
| **6** (optional) MC inputs | seven distributions | **Replace or delete** | Recommended: *Table 6. Uncertainty and sensitivity components (not combined)*: sampling CI ±3.8% (probabilistic); observed variability CoV 7.0%, −17.9%/+9.1% (observed); losses −8.3/+6.5% (scenario); speed ±5/±10% (sensitivity); ERA5–GWA ×1.10 (+20.0%, illustrative) | 3A §3.4; result files above |
| **7** "Comparison at a glance" (69×) | fuel-resolved fossil vs wind | **Delete** (C08, M01) | — | — |

**Contradiction guard.** After regeneration, no manuscript value may differ
from these tables, and the tables must equal the JSON values (§9, step 5C-4).

---

## 5. Figure replacement and numbering plan

| Old (build script / text ID) | Old content | Decision | Revised figure | Notes |
|---|---|---|---|---|
| Fig. 1 (F1) `figure1.png` | regional map + polygon with ERA5 grid | **Replace** | **Fig. 1** `saros_study_area` | Caption file reads "Figure 2" → renumber (m18). Cited in §2.1 and the new §2.x/§4.x |
| Fig. 2 (F2) `figure2.png` | workflow incl. Weibull AEP and MC | **Replace** | **Fig. 2** `methodology` | Cited in §3 (opening) |
| Fig. 3 (F3) `figure3.png` | wind rose | **Remove or supplementary** (M34) | — (optional Fig. S1 from a revised generator) | §4.1 l.38 must not cite an old image |
| Fig. 4a (F_wind_resource a) | distribution, Weibull fit, power curve | **Replace and split** | **Fig. 3** `wind_weibull` + **Fig. 4** `power_curve` | Fig. 3 in §3.5/§4.1; Fig. 4 in §3.4 |
| Fig. 4b | Q–Q plot | **Replace** | **Fig. 3b** (difference panel) | — |
| Fig. 4c–d | monthly climatology; interannual speed | **Remove or supplementary** (M34) | interannual variation in energy terms: **Fig. 5a** | Monthly values stay in text and Table 3 |
| Fig. 5 (F_monte_carlo) | MC histograms; scenario P10–P90 incl. S4 | **Replace** | **Fig. 5** `annual_energy_uncertainty` + **Fig. 6** `energy_sensitivity` | Caption file of Fig. 5 reads "Figure 1" → renumber |
| Fig. 6 (F7) | fossil vs wind, 69× | **Remove** (C08) | **Fig. 7** `avoided_co2` (different content: conventions + life cycle) | — |
| Fig. 7 (F8) | households and cars incl. S4 | **Remove** (M01) | — | — |

**Final numbering, in order of first citation:**

1. Study area (§2.1)
2. Methodology (§3)
3. Wind and Weibull (§3.5/§4.1)
4. Power curve (§3.4)
5. Annual yield and sampling CI (§4.3)
6. Sensitivity (§4.3)
7. Avoided CO₂ (§4.4)

If the power curve is cited before the Weibull figure (Methods order 3.4
before 3.5), swap Figs. 3 and 4 and update the caption files. The contact
sheet order follows the final numbering.

**Captions** come from `figures/revised/<stem>_caption.md`, generated with the
figures. They already state the sources, the limits, and the "not a
confidence interval / not P90 / not subtracted" distinctions. Use them
verbatim apart from the number.

---

## 6. Reference corrections

Status:

* **[V]** verified in the review reports or against a primary record during
  this audit;
* **[C]** conflict between repository and Word versions;
* **[MC]** requires manual confirmation.

No replacement citation is invented here.

### 6.1 Keep (verified), with text fixes

| Reference | Status | Text fix |
|---|---|---|
| Hersbach et al. 2020, QJRMS 146, 1999–2049 | [V] | none |
| Bonou, Laurent & Olsen 2016, Appl. Energy 180, 327–337 | [V] | Describe it correctly: 7.8–10.9 g, recycling credited, windier sites (C07) |
| Schlömer et al. 2014, IPCC AR5 WGIII Annex III | [V] | Values 8 / 12 / 35 g (C07) |
| Argın & Yerci 2015; Argın et al. 2019; Emeksiz & Demirci 2019; Genç et al. 2021; Tercan et al. 2020 | [V] | none (delete the stale "verify" notes, m16) |
| Duzcan & Kara 2023, IJEST 20, 4361–4374 | [V] ⚠ pages | text year 2022 → 2023 (m12) |
| Demirci, Tekince, Sezer & Bhattacharya 2026, IET RPG 20(1), e70241 | [V] | "Demirci et al." (m13) |
| Görmüş, Aydoğan & Ayat 2022, ECM 274, 116470 | [V] | Confirm the 373 W m⁻² basin mean on the page cited |
| Soukissian et al. 2018, Int. J. Climatol. 38, 384–402 | [V] ⚠ authors | Resolve against the 2017 Energies paper (M20) |
| Koletsis et al. 2016, RSER 60, 234–245 | [V] | Values: Aegean 500–800 W m⁻² (M15); check suitability for etesian characterisation (m15) |
| Yaltırak & Alpar 2002, Mar. Geol. 190, 351–366 | [V] | add co-author in text (m14) |
| Yaltırak, Alpar & Yüce 1998, Tectonophysics 300, 227–248 | [V] | none |
| Koukouvelas & Aydin 2002, Tectonics 21(5) | [V] | none |
| World Bank 2024, *Offshore Wind Roadmap for Türkiye* | [V] | Do not attribute the national 5 GW target to it without checking (M16) |

### 6.2 Conflicts to resolve

| Reference | Repository (`REFERENCES_VERIFIED.md`) | Word/PDF list | Evidence found in this audit | Action |
|---|---|---|---|---|
| Müller et al. (GPS, North Aegean) | J. Geophys. Res. Solid Earth 118 | Tectonophysics 597–598, 34–49, doi:10.1016/j.tecto.2012.08.003 | NTUA repository record: *Tectonophysics*, same DOI (online 2012; issue 2013) | Use Tectonophysics; correct the repository file; confirm the 21.2 mm yr⁻¹ and 5.6–8.9 km values on the page [M26] |
| Aksoy et al. 2022 | GJI 229(1), 589–; doi:…/ggab447; "et al." | GJI 229, 595–610; doi:…/ggab481; single author; shortened title | ÇOMÜ institutional record: seven authors; 229(1), 589–604; doi:10.1093/gji/ggab462 | Confirm on the publisher page, then correct both lists [M27] |
| Yaltırak et al. (bathymetry) | 2008, Geo-Mar. Lett. 28 ⚠ | 2012, J. Asian Earth Sci. 57, 103–119 (Bababurnu Basin, Biga) | — | Confirm which paper supports the cited gulf bathymetry; the 2012 paper concerns the Biga shelf [M28] |
| ETKB/EVÇED emission factor form | 2024 | 2024 | Forms dated 26.12.2025 (FRM-039 Rev.03; FRM-042 Rev.01), Phase 3B with URLs and checksums | Year 2025; two entries [M29] |
| Soukissian 2017 vs 2018 | correction 2017 → 2018 | both listed | — | Decide per sentence which paper is cited (M20) |

### 6.3 Requires manual confirmation before submission

| Item | Used for | Note |
|---|---|---|
| TEİAŞ 2024 consumption, 347.9 TWh | national share (M10) | Primary document not verified (`scenarios.json` note) |
| Source of the national 5 GW offshore target for 2035 | Intro, §3.1, Table 4 | Government source needed (M16) |
| 2023 MENR announcement of four offshore candidate areas | "first four" (M06) | Secondary source only (Capital, 9.8.2023) |
| Current status of the YEKA DÜRES-2026 tender | status sentences (C09) | Draft as of 11.11.2026; re-check immediately before submission |
| Justus empirical Weibull formula | §3.4 (m06) | Citation not identified in this audit |
| Fossil share and imports statements | Intro l.4–6 (m22) | Source needed |
| Literature claim "capacity factors substantially exceed onshore" | Intro l.17–19 (m22) | Source needed |

### 6.4 New references needed (documents already identified in the review reports)

| Document | Used for | Location of record |
|---|---|---|
| MENR, *Deniz Üstü Rüzgar Enerjisine Dayalı Aday YEKA İlanı*, 13.05.2026 (notice 30615) + KML | status, polygon | 4A Sources; 1 Sources |
| MENR, *YEKA DÜRES-2026 Şartname Taslağı* | 1 000 MWe, DÜRES definition | 4A Sources |
| Official Gazette 27793 (22.12.2010), Council of Ministers Decision 2010/1089 (Saros ÖÇK) | ÖÇK overlay | 4A Sources (with checksums) |
| EMODnet Bathymetry Consortium, DTM 2024, doi:10.12770/cf51df64-56f9-4a99-b1aa-36b8d7b743a1 | depth statistics | 1 and 2B Sources |
| Open Energy Database turbine library via windpowerlib (row V164/9500; commit 191d8ca) | power curve | 2A §2; 1 Sources |
| Global Wind Atlas 4.0, with Hansen, Floors & Badger, DTU Wind Energy Report E-0256 | ERA5–GWA comparison | 2B Sources |
| UNFCCC CDM Tool 07 v07.0 (grid emission factor tool) | combined margin method | 3B §1 |
| ETKB-EVÇED FRM-042 Rev.01 (2023 generation and consumption emission factors) | generation average | 3B Sources |
| NOAA GSOD, Çanakkale station 17112099999 | only if the 2014 corroboration is mentioned | 2B Sources |

### 6.5 Remove

* "IPCC 2025" (all in-file lists).
* "Müller / Tüysüz et al. (2007)".
* "Kurt et al. (2000)".
* McHugh et al. (2006), already dropped.
* Any TEİAŞ household-consumption source and the car-emission value, if M01
  is applied.

---

## 7. Claims to remove (not to soften)

| # | Claim (quoted) | Location | ID |
|---|---|---|---|
| 1 | "designated its first four offshore wind candidate zones" | Abstract l.3–4 | C09, M06 |
| 2 | "first peer-reviewed, site-specific assessment" | Abstract l.6; §5.3 l.55–56; Concl. l.3 | M07, M08 |
| 3 | "The siting decision has now been made by the state" / "committed site" / "Türkiye's first offshore wind development zone" | Intro l.44, l.56; Concl. l.28–29 | C09 |
| 4 | "removes a common source of contestation in offshore wind case studies" | §2.2 l.31–32 | M17 |
| 5 | "deeper western margin would require either exclusion or floating foundations" | §2.3 l.45–46; §5.4 l.115–116 | C11 |
| 6 | "Its manufacturer power curve defines …" | §3.5 l.107 | C02 |
| 7 | "propagated implicitly through the resource statistics" | §3.3 l.78–79 | M21 |
| 8 | "the Monte Carlo percentiles are preferred for inference because they carry the full uncertainty information" | §4.3 l.83–84 | C04 |
| 9 | "aligns with the winter peak in Turkish electricity demand" (all variants) | Abstract l.20–21; §4.1 l.22–24; §5.2 l.38–43; Concl. l.16–17, l.31 | C15 |
| 10 | "above the threshold generally regarded as economically viable" | §4.1 l.13–15 | M22 |
| 11 | "reduces the financial risk …" / "important consideration for project financing" / "forecast with relatively high confidence" | §4.1 l.29–31; §5.1 l.21–23 | C18 |
| 12 | "net of an offshore wind life-cycle factor" / "life-cycle emission represents under 2% of the displaced grid emission" | Abstract l.14–15; §4.4 l.91–94; §5.3 l.48–49; Concl. l.25 | C05 |
| 13 | "therefore a conservative (upper) estimate of the technology's footprint" | §3.7 l.176–178 | C07 |
| 14 | "officially sanctioned" / "officially mandated convention" / "removes the ambiguity" | §3.7 l.165–168; §4.5 l.135–136; §5.3 l.62–63 | M03 |
| 15 | Generation average and operating margin "used as the lower and upper bounds" | §3.7 l.169–171; §5.3 l.63–66 | C06 |
| 16 | Entire fuel-resolved comparison, "≈69×", "seventy-fold", "emission-free relative to the supply it displaces" | §3.7 l.180–188; §4.5; §5.3 l.68–74; Table 7 | C08 |
| 17 | Household and car equivalents | §3.7 l.188–191; §4.6; §5.3 l.75–79 | M01 |
| 18 | "theoretical maximum (183 turbines, 1739 MW)" and its results | §3.6; §4.4; §4.6; Table 4 | C14 |
| 19 | "pilot phase", "first-allocation phase", "full Phase-2 deployment" | §3.6; §4.4; §5.3; Concl.; Table 4 | M09 |
| 20 | "were the entire 5 GW target met by capacity of the Saros class … 13.1 TWh … 3.8%" | §4.4 l.107–109 | M10 |
| 21 | "measured rather than assumed wind-shear exponent" (as contribution) | Abstract l.9–10; Intro l.67–68; Concl. l.8 | C16 |
| 22 | "rows can be oriented to minimise array wake losses …" (unqualified) | §4.1 l.42–45 | M23 |
| 23 | "The zone is traversed by … the Ganos segment" | §5.4 l.106–107 | M18 |
| 24 | "Uncertainty in seven inputs was propagated through a 10 000-iteration Monte Carlo simulation" and all P10–P90 statements | Abstract l.15–16; Intro l.71–76; §3.8; §4.3; Concl. | C04 |

---

## 8. Remaining publication risks (after the revision)

1. **Resource level dominates.** The ERA5–GWA disagreement (≈±20% AEP) exceeds
   every quantified term. Reviewers may ask for the neighbouring nodes
   (26.00/26.50° E) or a period-matched comparison. Both are cheap if the raw
   NetCDF files still exist (m19). Without them the paper must be framed as
   preliminary throughout.
2. **Single node outside the zone.** This affects "zone" statements. Keep all
   results node-level.
3. **Legal and policy drift.** The candidate status, the draft tender and the
   1 000 MWe allocation can change before submission. Re-check MENR notices
   and the Official Gazette in the week of submission. The ÖÇK boundary has no
   stated datum; keep the "approximate" wording, and do not imply prohibition.
4. **Novelty.** Without "first peer-reviewed" and "site-specific", the
   contribution rests on transparent accounting and separated uncertainty for
   a newly announced candidate area. Make that explicit in the Introduction.
5. **Unverified external numbers.** These are 347.9 TWh, the 5 GW target
   source and the 2023 candidate areas. If they cannot be verified, drop the
   dependent sentences instead of keeping them uncited.
6. **Life-cycle transfer.** Literature intensities come from windier sites;
   the Saros-rescaled values would be ≈17–23 g. State this, or a reviewer
   will.
7. **Two manuscript versions.** Edits made only in Word would be lost or
   reintroduce retired values (M33).
8. **Equation images by position.** This creates a silent mismatch risk
   (M32).
9. **Public material.** The Medium draft states 69×, 2.62 TWh and the winter
   demand match. Publishing it would contradict the paper (m21).
10. **Target journal.** The header names *Energies* (MDPI, numbered
    references); the figures follow Elsevier energy-journal style. Decide
    before Phase 5C formatting.
11. **Contradictory versions of the area and overlap.** Pick one presentation
    (M25), and grep for the others.

---

## 9. Minimal implementation sequence

### Phase 5B — scientific content (text and tables)

| Step | Work | Closes |
|---|---|---|
| 5B-0 | Declare Markdown + `10_build_docx.py` the single source. Copy the Word-only reference list into the repository. Freeze the old text as an archive copy. | M33 |
| 5B-1 | **Tables first.** Write a table generator that reads only `results/revised/` and writes `tables.md` (Tables 1–6 per §4). Delete Table 7. | C03, C14, M01, M25 + all table rows |
| 5B-2 | **Methods 3.1–3.9** to the structure in §1.5, with the new equations (§3). | C01, C02, C04–C07, C09, C10, C13, C16, C17, M02–M05, M09, M12, M19–M21, m04–m09 |
| 5B-3 | **Results 4.1–4.4** (+ new site-screening subsection). Delete 4.5–4.6. Cite only the revised figures. | C03, C04, C08, C12, C15, C18, M10–M12, M22, M23, M34, m10, m11 |
| 5B-4 | **Study area 2.1–2.5** (+ new environmental subsection). | C10, C11, C12, M04–M06, M17, M28, m02, m03 |
| 5B-5 | **Discussion 5.1–5.5**, with the limitations in §1.9. | C13, C15, C17, C18, M14, M15, M18, M24, m19 |
| 5B-6 | **Abstract, Introduction, Conclusion, title, keywords**, written last from the finished Results. | C09, C15, C16, M07, M08, M13, M16, m01, m22 |
| 5B-7 | Numeric consistency test: every number in the text and tables traced to a JSON key; retired-value grep (Appendix B) returns nothing. | — |

### Phase 5C — references, figures, build and QA

| Step | Work | Closes |
|---|---|---|
| 5C-1 | Correct the reference list (§6.1–6.2). Add the new sources (§6.4). Resolve the [MC] items or drop the dependent sentences (§6.3). Fix in-text citations. Delete in-file reference notes. | M26–M30, m12–m16 |
| 5C-2 | Rewrite the build: revised figures and caption files; native math (or labelled images); new title and header; no `fix()` table. | M31, M32, m17 |
| 5C-3 | Renumber the approved captions; final figure order (§5); regenerate the contact sheet. | m18 |
| 5C-4 | Build the .docx. Automated checks: retired values absent; figure and table numbers sequential; every figure and table cited; JSON = tables = text. Then visual read-through of the .docx. | — |
| 5C-5 | Add the data/code availability statement; final status re-check (MENR, Official Gazette); independent read by someone who has not seen the edits. | m20; risks 3, 5 |

---

## Appendix A — Mandatory framework cross-check

| Framework item | Authoritative value (`results/revised/`) | Current manuscript | Plan |
|---|---|---|---|
| Preliminary ERA5-based assessment | status "PRE-SUBMISSION MODEL ESTIMATE" in every file | "under Uncertainty", "first peer-reviewed" | M13, M07 |
| 11-year hourly series 2014–2024 | 96 432 h, no gaps (`wind_resource.json` data) | correct | keep |
| Empirical hourly conversion primary | `energy_yield.json` estimator | Weibull + MC | C01 |
| OEDB digitised V164-9.5 MW curve | `energy_yield.json` power_curve = OEDB_V164_9500 | "manufacturer power curve" | C02 |
| Net CF ≈27.69% | net_cf = 0.27691 ✓ | 31.0% / 29.9% | C03 |
| Net yield ≈2.4274 GWh MW⁻¹ yr⁻¹ | net.gwh_per_mw = 2.42737 ✓ | 2.71 / 2.62 | C03 |
| 90% sampling CI ≈2.334–2.520 | primary_t_interval_90 = 2.3343–2.5203 ✓ | P10–P90 2.41–2.83 | C04 |
| Interannual variation ≠ uncertainty of mean | labels OBSERVED vs SAMPLING ✓ | conflated (3.2%) | C04, C18 |
| Wind-speed sensitivity ≠ CI | label SENSITIVITY ✓ | absent | C04 |
| ERA5–GWA as model disagreement | gwa_reference note ✓ | absent | C17 |
| Avoided CO₂ ≈1 515.2 tCO₂ MW⁻¹ yr⁻¹ (2023 CM) | 1 515.16 ✓ | 1 525 lifecycle-net | C03, C05 |
| Life cycle separate in CO₂-eq | secondary_lifecycle_ghg, not_subtracted ✓ | subtracted | C05, C07 |
| S1–S3 illustrative | `scenarios.json` S1–S3 ✓ | phase labels | M09 |
| S4 removed | retired note only ✓ | present | C14 |
| ≈14.4% ÖÇK overlap, approximate | 14.36% (grid); 14.47% exact ✓ | absent | C12, M25 |
| Candidate-area status | `config/site.py`; 4A §C1 ✓ | "designated" | C09 |
| No bankable, feasibility or buildability claim | — | financing and viability claims | C18, M13, M22 |

## Appendix B — Retired-value grep list for step 5B-7 / 5C-4

Each pattern must return no match in `manuscript/*.md`, `tables.md` or the built
.docx, except where marked:

* **Numbers:** `2.62`, `2.71`, `29.9`, `31.0 %`/`31%`, `30.4`, `36.5`, `25.8`,
  `2714`, `1525`, `1277`, `1754`, `2.41`, `2.83`, `6.3%`, `3.2%`, `422`
  (allowed only as the labelled Weibull cross-check), `172.5`, `4.56`, `1739`,
  `183 turbines`, `1.98 Mt`, `1.95 Mt`, `0.029`, `69×`, `seventy`, `757`,
  `0.86 million`, `0.76 million`, `3036`, `13.1 TWh`, `3.8%` (allowed only as
  the sampling half-width, ±3.8%).
* **Phrases:** `Monte Carlo`, `P10`, `P50`, `P90`, `IPCC 2025`, `8–14`,
  `14 May`, `designated`, `theoretical maximum`, `Phase-2`, `pilot`,
  `first-allocation`, `manufacturer power curve`, `measured … shear`,
  `Yenilenebilir Enerji Kaynak Alanları`, `winter peak in … demand`,
  `officially mandated`, `sanctioned`.
