# Phase 5-PRE-C — Novelty and official-source audit

*14 November 2026. Audit only. Manuscript, figures, data, models and
`results/` are unchanged. Phase 5B not started. The reference inventory
with access status and checksums is in
`docs/review/phase5pre_c_reference_inventory.csv`.*

**Status labels**

- **[V-FT]** verified from the full text or the primary document itself.
- **[V-AB]** verified from the publisher's abstract page or public metadata
  only.
- **[V-MD]** bibliographic metadata verified (Crossref) only.
- **[S]** secondary report.
- **[U]** unresolved or not accessible.

Absence of a discovered document is never treated as proof that it does not
exist.

---

## 1. Literature novelty review

### 1.1 Yildirim (2023): the closest prior work

| Item | Finding | Status |
|---|---|---|
| Identity | Yildirim, A. *The technical and economical feasibility study of offshore wind farms in Turkey.* *Clean Technologies and Environmental Policy* 25(1), 125–142. Published online 7 Sep 2022; issue 2023. doi:10.1007/s10098-022-02392-0. Single author, Osmaniye Korkut Ata University | [V-MD] Crossref, Unpaywall |
| Access | **Closed access.** Unpaywall: no OA copy. The publisher page shows "preview of subscription content". The institutional repository (openaccess.osmaniye.edu.tr) was unreachable from this environment. A university-proxy mirror found by search was **not used** | [U] full text |
| Study areas | "Three potential candidate regions were identified, two located in the Aegean Sea and one in the Black Sea", following the government tender opened in 2018 | [V-AB] |
| Saros | The abstract states that "the best results [were] obtained in the **Saros OWF region**". So Saros **was assessed**, and named in the abstract | [V-AB] |
| Data | Publisher's data-availability statement: "The datasets … are available in the [Global Wind Atlas] repository … Accessed 11 Nov 2021" | [V-AB] |
| Methods and findings | Techno-economic analysis and comparison of economic indicators; total capacity at the three sites 3 329.4 MW | [V-AB] |
| Saros capacity factor, AEP, layout, Saros polygon | **Not verifiable** without the full text | [U] |
| Which areas | The 2018 candidate regions were Saros, Gelibolu and Kıyıköy (YEGM notice of 23 Mar 2018). The paper's three regions are therefore probably these, but that is an inference: the abstract names only Saros | [S] for 2018 areas; [U] identity of the paper's areas |
| Spatial overlap with the 2026 polygon | **Unknown.** The 2018 notice (archived at `web.archive.org/web/20180328115842/http://www.eie.gov.tr:80/duyurular_haberler/aday_yeka_2018.aspx`) could not be opened: web.archive.org is blocked by this environment's network policy. No 2018 coordinates were found elsewhere | [U] |

**Overlap judgement.**

- A peer-reviewed resource and techno-economic assessment of a "Saros"
  offshore region **already exists** (Yildirim 2023).
- It used a different wind source (GWA, then version 3.x).
- It defined its area from the 2018 tender, not the 2026 polygon.
- Every "first assessment of Saros" claim is therefore false as worded.
- Whether the 2018 and 2026 Saros areas coincide must be established
  before Phase 5B (§6).

### 1.2 Comparison matrix

"Saros?" records whether Saros appears in the text that was actually read.

| Study (DOI) | Area | Wind data | Method | Main finding | Saros? | Overlap with this study | Status |
|---|---|---|---|---|---|---|---|
| Yildirim 2023 (10.1007/s10098-022-02392-0) | Three 2018 candidate regions (2 Aegean, 1 Black Sea) | Global Wind Atlas | Techno-economic analysis | 3 329.4 MW total; Saros best economically | **Yes** (abstract) | **High**: same named region; area definition unknown | [V-AB]; full text [U] |
| Cali et al. 2018 (10.1016/j.esr.2018.10.007) | Bozcaada, Gökçeada, Bandırma | Virtual Wind Farm model on bias-corrected MERRA | MCDM selection, AEP, electrical design, DCF | Bozcaada best; feasible only under certain conditions | **No** (0 occurrences in full text) | Method analogue; no site overlap | [V-FT] (UCC repository, CC BY-NC-ND) |
| Argın et al. 2019 (10.1016/j.esr.2018.12.005) | Turkish coasts | — | Multi-criteria site selection | National screening | Not checked (full text not opened) | Screening context | [V-MD] |
| Emeksiz & Demirci 2019 (10.1016/j.seta.2019.100562) | Turkish seas | — | Hybrid site selection | National screening | Not checked (closed) | Context | [V-MD] |
| Genç et al. 2021 (10.1007/s12145-021-00632-3) | All Turkish seas | EMODnet layers | GIS-MCDM, 13 sub-criteria | 3 294.8 km² (1.38 %) suitable; Marmara largest | Not in abstract | Context; EMODnet use as here | [V-AB] |
| Tercan et al. 2020 (10.1007/s10661-020-08603-9) | Cyclades (GR) and İzmir (TR) | — | Fuzzy MCDM + GIS | 519 km² suitable (İzmir) | Not in abstract | None (other areas) | [V-AB] |
| Duzcan & Kara 2022/2023 (10.1007/s13762-022-04577-y) | 8 Marmara + 16 Aegean regions | TSMS onshore stations 2011–2020, CFD to 84 m | AEP, P50/P90 | 12 suitable regions (CF > 35 %), Saros not among them | Not in abstract; whether Saros was among the 16 is [U] | Possible; unverified | [V-AB] |
| Satır et al. 2018 (10.1016/j.rser.2017.06.063) | "Aegean Sea, Turkey" | — | Feasibility and economics | — | Site [U]: repository behind a human-verification page, not bypassed | Unknown | [V-MD] |
| Özbek & Tunç 2021 (10.35378/gujs.734895) | Gulf of Edremit | MERRA + local met mast | Layout, wake, economics | 50–90 MW park | **No** (0 occurrences in full text) | Different candidate area | [V-FT] |
| Erkurtulmuş & Peşman 2024 (10.21278/brod75204) | 12 km NE of Gökçeada | — | F-AHP + GIS, floating | 12 km², 110 m depth, 9.26 m/s | No (abstract) | Different area (near the 2026 Gökçeada zone) | [V-AB] |
| Oğuz & İncecik 2014 (GRE2014 conference; no DOI found) | Bozcaada, Gökçeada stations | 20-year hourly station data | Weibull | Bozcaada windier | No | Context | [V-AB] (Strathclyde record) |
| Konstantinidis et al. 2014 (10.1063/1.4871484) | North Aegean, Greece | — | Viability | — | Not checked | Regional context | [V-MD] |
| Aslan 2020 (10.1063/5.0025753) | Çanakkale onshore, coastal, offshore | — | Technical and economic | — | Not checked (closed) | Regional context | [V-MD] |
| Görmüş et al. 2022 (10.1016/j.enconman.2022.116470) | Mediterranean, 1959–2020 | ERA5 | Multi-turbine potential | Basin climatology | — | Benchmark | [V-MD] (cited in manuscript) |
| Demirci et al. 2026 (10.1049/rpg2.70241) | Türkiye review: locations, foundations, seismicity | Review | Review | — | Full text **not retrieved**: gold OA, but Wiley blocked automated access; a browser workaround was refused | Context (seismic) | [V-MD] |
| World Bank 2024 roadmap (10.1596/42461) | Türkiye | Spatial analysis | Roadmap | 75 GW technical potential | **Saros mentioned only as a protected area** (SPA in the Exclusion Zone layer; overlap with the North Aegean EBSA and KBAs) | Environmental screening support | [V-FT] (English text) |

**ERA5 coastal uncertainty and representativeness (method context)**

| Study (DOI) | Relevance | Status |
|---|---|---|
| Hersbach et al. 2020 (10.1002/qj.3803) | ERA5 description | [V-MD] |
| Olauson 2018 (10.1016/j.renene.2018.03.056) | ERA5 for wind power modelling | [V-MD] |
| Ramon et al. 2019 (10.1002/qj.3616) | Reanalysis near-surface wind skill | [V-MD] |
| Gualtieri 2021 (10.3390/en14144169) | ERA5 against tall towers | [V-MD] |
| Gruber et al. 2022 (10.1016/j.energy.2021.121520) | ERA5/MERRA-2 wind power with GWA bias correction | [V-MD] |
| Murcia et al. 2022 (10.1016/j.apenergy.2021.117794) | European-scale wind validation | [V-MD] |
| Kalverla et al. 2020 (10.1002/qj.3748) | Wind atlases over the North Sea | [V-MD] |
| Gandoin & Garza 2024 (10.5194/wes-9-1727-2024) | ERA5 underestimates strong offshore winds | [V-MD] |
| Rubio et al. 2025 (10.5194/amt-18-4949-2025) | Ship lidar vs ERA5/ASCAT; coastal degradation | [V-MD] + abstract |
| Hahmann et al. 2020 (10.5194/gmd-13-5053-2020); Dörenkämper et al. 2020 (10.5194/gmd-13-5079-2020) | NEWA (ERA5-driven WRF; covers Türkiye) | [V-MD] |
| Davis et al. 2023 (10.1175/BAMS-D-21-0075.1) | Global Wind Atlas method | [V-MD] |
| Staffell & Pfenninger 2016 (10.1016/j.energy.2016.08.068) | Bias-corrected reanalysis (the basis of Cali et al.) | [V-MD] |

None of the Turkish studies read here separates period-selection, grid-node
and inter-model uncertainty. Each relies on one wind source:

- GWA (Yildirim);
- MERRA (Cali; Özbek & Tunç);
- onshore stations with CFD (Duzcan & Kara).

No study found applies an ERA5 temporal or spatial sensitivity analysis to
any Turkish candidate area. This is not proof of absence: Scopus and Web of
Science were not available.

---

## 2. Official-source verification

| Claim | Primary source | Finding | Status |
|---|---|---|---|
| Candidate-area announcement | MENR notice 30615, 13.05.2026 (`enerji.gov.tr/duyuru-detay?id=30615`) | The areas "Aday YEKA olarak belirlenmiş olup … YEKA olarak ilan edilmesine yönelik detay çalışmalara başlanmıştır", under the YEKA Regulation (RG 29852, 09.10.2016). **Legal status: candidate YEKA; not a declared YEKA.** | [V-FT] |
| Polygon | Notice attachment `Offshore_Aday_YEKA_Alanlari.zip` (sha256 `240de643…`; 4 KML, timestamps 13.05.2026) | `SAROS DÜRES.kml` is **byte-identical** to the repository copy (sha256 `190fda95…`) | [V-FT] |
| Later MENR action | Notices 30616–30672, scanned by ID | Offshore-related notices: 30621 (22.06.2026, draft specification, comments until 17.08.2026) and 30671 (11.11.2026, IPA seabed surveys in the **Sea of Marmara**, not Saros). **No final specification or tender notice up to 14.11.2026** | [V-FT] (ministry site, gaps in ID numbering possible) |
| Draft specification | `YEKA_DURES-2026_SARTNAME_TASLAGI.pdf` (22 pp., created 22.06.2026, sha256 `2bfb054a…`) | "ŞARTNAME TASLAĞI"; the Official Gazette tender date is left blank. Total **1 000 MWe**; 49-year YEKA use. Annex 7: the YEKA is "**any one**" of the areas of notice 30615. **No capacity is assigned to Saros.** Capacity may be modified up to 50 % after the feasibility report (§4.4); no capacity increase during the contract | [V-FT] |
| DÜRES meaning | Same draft, definition 12 | "Deniz Üstü Rüzgâr Enerjisi Santrali"; the manuscript's expansion is wrong (as found in Phase 4A) | [V-FT] (Phase 4A; draft re-read) |
| Saros ÖÇK designation | RG 27793, 22.12.2010, Council of Ministers Decision 2010/1089 (htm sha256 `820a2531…`; annex sha256 `92bbe585…`, same as Phase 4A) | Designated under Law 2872 art. 9. The annex table "Saros Körfezi ÖÇK Sınır Koordinatları" lists 13 points, identical to `scripts/phase4a_site_checks.py`. **No datum stated** on the table or map pages | [V-FT] (scanned annex read visually) |
| Later amendments | Searches of mevzuat.gov.tr (via web search) and news; RG 30791 (2019, Decision 1133, land strict-protection area); Decision 4758 (2021, Marmara Sea and Islands ÖÇK) | **No amendment or superseding decision found.** Decision 4758 concerns the Marmara ÖÇK, not Saros. The TVK and ÖÇK ministry sites (`tvk.csb.gov.tr`, `ockb.csb.gov.tr`) were unreachable (connection reset; HTTP 503 via WebFetch). A secondary snippet cites a 1990 decision (90/1117) for Saros; it was not checked and conflicts with 2010/1089 | [U] (absence not proven) |
| ÖÇK as screening reference | Decree annex + World Bank 2024 roadmap, Appendix C | The overlap depends only on the straight sea segments between decree points 13→1→2. A ±130 m datum shift changes the overlap by < 0.2 points (Phase 4A). The World Bank roadmap includes the Saros Körfezi SPA in its **Exclusion Zone layer**. **Defensible as a screening reference**, labelled approximate (no datum; currency not confirmed with TVKGM) | [V-FT] + [U] currency |
| ÖÇK area | — | Reconstructed polygon (13 straight segments, land included): 805.7 km² (geodesic). Only a secondary figure was found (~235 km², Küre Ansiklopedi), inconsistent and unexplained. No official area figure was obtained | [U] |
| 5 GW offshore by 2035 | *Türkiye Ulusal Enerji Planı 2022* (MENR; PDF created 09.03.2023, sha256 `88f00e56…`) | "2035 yılında kurulu güç … Rüzgar enerjisinde 29,6 GW (24,6 GW kara, 5 GW deniz)". A **planning projection** in the official national plan. The World Bank roadmap confirms the government published it in 2022; the Minister restated it in 2026 [S] | [V-FT] |
| 2024 consumption 347.9 TWh | TEDAŞ *2025 Yılı Türkiye Elektrik Dağıtımı Sektör Raporu*, Table 5 (sha256 `72f02193…`, citing TEİAŞ); MENR electricity page | **2024 "Türkiye tüketimi" = 353 579.8 GWh; net consumption = 308 673.9 GWh.** MENR: 2025 = 364.8 TWh (+3.2 %), implying ≈353.5 TWh for 2024. **347.9 TWh appears only in secondary sources** (SHURA; CNBC-e), probably provisional TEİAŞ load data. The figure in `config/emissions.py` and `scenarios.json` is therefore not the official final value | [V-FT] official values; 347.9 [S] |
| 2018 candidate areas | AA (25.03.2018) and Dünya Enerji Konseyi note citing the YEGM "Aday YEKA İlan Metni" of 23.03.2018 | Saros, Gelibolu, Kıyıköy; tender planned for 840–1 200 MW, later postponed [S] | [S]; official text [U] (archive blocked) |
| 2023 candidate areas | News (Capital, AA) | Bandırma 1 111 km², Bozcaada 299 km², Gelibolu 75.6 km², Karabiga 410 km²; MENR notice of 04.08.2023 [S]. The official notice was not located (non-sequential notice IDs). Either way, "first four zones" (2026) is wrong | [S] |

---

## 3. Unresolved-source register

| # | Item | Why unresolved | What closes it | Blocking for 5B? |
|---|---|---|---|---|
| U1 | Yildirim (2023) full text: Saros area definition, coordinates, CF, AEP | Closed access; repository unreachable | Institutional or interlibrary access, or an author request | **Yes**: it defines the novelty claim and needs a quantitative comparison |
| U2 | 2018 candidate-area coordinates (Saros, Gelibolu, Kıyıköy) | Official page only archived; web.archive.org blocked here | Open the archived URL manually, or file a MENR information request; then overlay on the 2026 polygon | **Yes**, together with U1 |
| U3 | Currency of the Saros ÖÇK boundary; official map or GIS; official area | TVK/ÖÇK sites unreachable; no amendment found, but absence is not proof | TVKGM written confirmation, or the official ÖÇK map service checked from another network | No: disclose as "2010 decree boundary, approximate" |
| U4 | Conflicting "90/1117 (1990)" designation snippet | Seen only in search snippets | Read the TVK page or the RG 1990 text | No |
| U5 | 347.9 TWh vs official 353.58 TWh (gross) / 308.67 TWh (net) | Definition and vintage differ | Author decision: adopt the TEDAŞ/TEİAŞ value with its definition, or drop the share statement | No, but it changes a reported share (0.675 % → 0.664 % gross); requires a production update, not done here |
| U6 | Demirci et al. (2026) full text | Wiley blocked automated access; bypass refused | Read manually (gold OA) | No: only if seismic or "location" claims cite it |
| U7 | Duzcan & Kara: whether Saros is among the 16 Aegean regions; correct pages | Paywalled. Crossref gives 20(5):5571–5584; `REFERENCES_VERIFIED.md` gives 4361–4374 | Publisher page or full text | Fix the reference pages before 5C |
| U8 | Satır et al. (2018) site | Repository behind a human check | Read manually | No |
| U9 | Official 2023 candidate-area notice | Not located on the MENR site | MENR archive | No (wording fix suffices) |
| U10 | A database-grade literature sweep (Scopus or WoS: "Saros" AND wind) | Not available here | Run by the author | Recommended |

---

## 4. Scientific contribution (judgement)

1. **What is genuinely new.** The analysis concerns the **exact polygon
   announced on 13 May 2026**. Published work predates it, so no study can
   have assessed that geometry. This is a dated, factual novelty, not a
   methodological one. It is weakened by Yildirim (2023), which assessed a
   "Saros" region with GWA data; the size of the overlap is open (U1/U2).
2. **The ERA5 sensitivity analysis strengthens the contribution most.**
   - **Period selection:** 2014–2024 is the windiest 11-year window of
     1979–2024; the long-term mean is 3.0 % lower.
   - **Node representativeness:** −8.7 % / +6.6 %. The node used is a
     mixed land–sea ERA5 cell (land fraction 0.44).
   - **Inter-model disagreement:** GWA/ERA5 1.07–1.15; period matching
     widens it.
   - **Sampling CI of the 31-year mean:** ±2.3 %.

   None of the Turkish studies read here quantifies these. They also
   explain why GWA-based estimates such as Yildirim's could be higher. This
   is the paper's defensible scientific content. The methods are standard
   (application, not new methodology), so the claim must be "first
   quantification for this candidate area", conditional on U10.
3. **Protected-area screening: a key secondary result, not the core.**
   - It is verified that ≈14 % (≈25 km²) of the candidate area lies inside
     the 2010 Saros ÖÇK.
   - The World Bank roadmap treats that ÖÇK as an exclusion layer.
   - This bears directly on usable area and belongs in the abstract (one
     sentence) and in Results, labelled approximate and not a permitting
     judgement.
   - It is not a research contribution in itself. The other screening
     topics remain unscreened.
4. **Avoided CO₂: secondary accounting.** It is a linear transform of
   energy with a static 2023 convention (1 469 tCO₂ MW⁻¹ yr⁻¹ under the
   combined margin; conventions range 840–1 679). It adds no independent
   evidence. Keep it as one short table and paragraph.
5. **Novelty claims to delete.**

| Claim to delete | Reason |
|---|---|
| "first peer-reviewed assessment" / "first site-specific assessment" | Yildirim 2023; single node outside the zone |
| "no peer-reviewed assessment yet exists for any of the four zones" | At least Saros (Yildirim) and the Gökçeada and Bozcaada areas (Cali 2018; Duzcan & Kara; Erkurtulmuş & Peşman) have prior assessments of nearby or same-named areas |
| "first four zones" / "designated" / "siting decision has been made" | Candidate status; 2018 and 2023 candidate sets existed |
| "measured shear exponent" as a contribution | — |
| Uncertainty "propagated" as total uncertainty | — |
| The 5 GW target attributed to the World Bank | Cite the National Energy Plan 2022 |
| "0.8 % of national consumption" based on 347.9 TWh | Replace with an official value and definition, or delete |

---

## 5. Recommended scope, research question and contribution

**Scope.** A preliminary, reanalysis-based energy-yield assessment of the
2026 Saros candidate area. The core is the long-term ERA5 estimate with
decomposed uncertainty. Secondary: the verified protected-area overlap,
bathymetric screening, and avoided-CO₂ accounting under the official 2023
convention. No feasibility, LCOE, layout or permitting claims.

**Research question.** For the Gulf of Saros offshore-wind candidate area
announced on 13 May 2026, what net specific energy yield does ERA5 indicate
over 1994–2024 for a reference 9.5 MW turbine, and how large are the
period-selection, grid-node, inter-model (ERA5–GWA) and loss-assumption
sensitivities compared with the sampling uncertainty of the long-term mean?

**Contribution statement.** We provide the first published energy-yield
assessment of the officially announced 2026 Saros candidate polygon, using
31 years of hourly ERA5 data (net yield 2.354 GWh MW⁻¹ yr⁻¹, net capacity
factor 26.9 %; 90 % sampling interval ±2.3 %). We show that the dominant
uncertainties are not sampling but representativeness:

- the commonly used recent decade overstates the long-term yield by 3 %;
- neighbouring reanalysis nodes differ by −9 % to +7 %;
- ERA5 and the Global Wind Atlas disagree by 7–15 % in mean speed.

We also document that about 14 % of the candidate area lies within the
Saros Special Environmental Protection Area.

The word "first" is defensible **only** for the 2026 polygon and only after
U1/U2/U10. Otherwise write "an assessment of …".

---

## 6. Minimum additional work before Phase 5B

1. **U1 + U2 (blocking).**
   - Obtain the full text of Yildirim (2023) and the 2018 Saros candidate
     coordinates.
   - Overlay them on the 2026 polygon and tabulate Yildirim's data, CF and
     AEP against ours.
   - Write the Introduction's novelty paragraph from that comparison.
2. **Literature sweep (U10).** Run Scopus/WoS queries ("Saros" AND wind;
   Turkish offshore wind 2022–2026) and add any hits to the matrix.
3. **Consumption figure (U5).** The author decides between the official
   TEDAŞ/TEİAŞ 2024 value (353 579.8 GWh gross; 308 673.9 GWh net, with
   definition) and dropping the share. If adopted, change
   `config/emissions.py` through a production update with tests (not in
   this audit).
4. **Policy wording.**
   - Candidate YEKA (notice 30615).
   - Draft specification, 1 000 MWe for any one of four areas.
   - 5 GW from the National Energy Plan 2022.
   - Re-check MENR and the Official Gazette in the week of submission.
5. **ÖÇK wording.** State "boundary of Decision 2010/1089, reconstructed
   from the decree coordinates (no datum stated); no later amendment found
   as of 14.11.2026". Attempt TVKGM confirmation (U3).
6. **Reference fixes.**
   - Duzcan & Kara pages (U7).
   - Add Yildirim 2023, Cali 2018, the National Energy Plan 2022, TEDAŞ
     2025, the draft specification, notice 30615, RG 27793, the World Bank
     2024 roadmap and Gandoin & Garza 2024.
   - Drop "first peer-reviewed".
