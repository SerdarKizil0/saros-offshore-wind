# Phase 4A — Site feasibility and scenario audit

*11 November 2026. Screening only: this is not a layout design, permit
assessment or investment appraisal. No AEP or carbon values were recomputed.
The model, results, figures and manuscript are unchanged.*

**Reproduce:**

```bash
python scripts/phase4a_site_checks.py   # ~20 s; writes results/provisional/phase4a/site_checks.json
```

**Labels used below:**

- **[V]** verified against a primary source or the committed data
- **[S]** secondary source, not verified against the primary
- **[I]** inference

---

## A. Capacity scenarios and spatial feasibility

### A1. The 7D × 5D assumption

With D = 164 m, the grid cell is 1.148 × 0.820 km = 0.941 km². Dividing
172.3 km² by the cell area gives **183.0**, which is how S4 was derived [V].

Fitting a real grid to the polygon, with turbine centres inside it:

| Grid orientation | Centre inside polygon | With 82 m rotor-tip setback |
|---|---|---|
| 7D along the energy-weighted prevailing axis (41°) | 188 | **182** |
| 7D along the polygon's long axis (81°) | 189 | 180 |
| Best of 36 orientations | 194 | 187 |

So the area-division count is **geometrically achievable**, but only at the
minimum spacing everywhere, out to the boundary. The 7D × 5D spacing is an
assumption: no source is given for it in the code or manuscript, and it does
not account for perimeter, wake or permitting effects.

### A2. Geometry and wind direction [V, from the ERA5 series]

- **Polygon shape:** 35.9 km × 11.3 km, long axis at 81° (ENE–WSW). The
  eastern arm, east of about 26.32° E, is only 2.5–4 km wide.
- **Energy by direction:** NE 33%, NNE 18%, ENE 17%, SSW 13%. The
  energy-weighted prevailing axis is 41° (NE–SW).
- Only 31% of energy arrives within ±30° of the polygon's long axis. Rows
  along the prevailing axis are short: at most 11 turbines and a median of 6
  in the best-fit layout.

### A3. Screening classes in the best-fit layout (182 positions; not exclusions)

| Class | Positions | Basis |
|---|---|---|
| Depth < 10 m | 14 | EMODnet DTM 2024 [V] |
| Depth 50–62 m | 19 | EMODnet [V]. Above the ESMAP 50 m fixed/floating *screening* threshold; a substructure question, not an exclusion |
| < 1 km from shore | 5 | 0 m contour of the DTM [V] |
| **Inside the Saros ÖÇK (2010)** | **25** | Official Gazette 27793 (§B1) [V] |
| None of the above | 123 (≈1 170 MW) | — |

### A4. Why one 8% wake loss for all scenarios is inappropriate

The scenarios span 1.4–10.1 MW/km², a factor of 7:

- S1 could be spaced far more widely than 7D × 5D.
- S4 is packed at the minimum spacing everywhere.

Wake loss rises with density and with the number of upstream turbines, so a
single 8% cannot apply to both [I]. The direction of the error is clear: too
pessimistic for S1, optimistic for S4. Its size needs a wake model, which
does not exist here.

For reference, ESMAP's technical-potential screening assumes **3–4 MW/km²**
(Phase 1 source).

| Scenario | MW | MW/km², full polygon | MW/km², outside ÖÇK | Share of the 182 fitted positions |
|---|---|---|---|---|
| S1 | 247.0 | 1.4 | 1.7 | 14% |
| S2 | 503.5 | 2.9 | 3.4 | 29% |
| S3 | 997.5 | 5.8 | 6.8 | 58% |
| S4 | 1 738.5 | **10.1** | **11.8** | **≈100%** |

### A5. Verdicts by scenario

| Scenario | Verdict | Reason |
|---|---|---|
| **Per MW** (primary) | **Keep as primary** | Independent of layout. Losses are already given as scenarios (Phase 3A) |
| **S1, 247 MW** | Keep only as a generic illustrative capacity, or drop | "Pilot phase" has no official basis. Density is low, so 8% wake is likely conservative |
| **S2, 503.5 MW** | Keep only as a generic illustrative capacity, or drop | "First allocation (~500 MW)" contradicts the draft first tender of 1 000 MWe |
| **S3, 997.5 MW** | **Keep as the principal illustrative scenario, re-motivated** | Corresponds to the 1 000 MWe connection capacity of the *draft* YEKA DÜRES‑2026 tender **if** that tender were sited at Saros (see §C4). Fits geometrically (105 of 182 positions, and fewer than the 123 that avoid every screening class). Wake loss is held at the nominal value as a simplification, with the low and high loss scenarios as a bracket |
| **S4, 1 738.5 MW** | **Remove from the results.** If kept, relabel and give no energy or CO₂ values | Geometric packing is possible, but at 10.1 MW/km² it is 2.5–3.4× the ESMAP screening density. It fills every position, including 25 in the ÖÇK and 59 in at least one screening class, assumes 8% wake at maximum density, and has no policy anchor. "Theoretical maximum" implies a deployable ceiling, which this is not. Acceptable wording: "geometric packing limit at 7D × 5D (not a feasible capacity)" |

---

## B. Environmental and geographic screening

| Topic | Finding | Status |
|---|---|---|
| **Protected area: Saros Körfezi Special Environmental Protection Area (ÖÇK)** | Declared by Council of Ministers Decision **2010/1089**, Official Gazette **27793 of 22.12.2010**, under Environmental Law No. 2872, art. 9. The 13 boundary points are in the annex. The western boundary runs points 1–13 at about 26.32–26.33° E. **About 25 km² (14.4%) of the DÜRES polygon, the whole eastern arm east of about 26.325° E, lies inside the ÖÇK.** A ±130 m datum shift changes this by <0.2 percentage points | **[V] confirmed overlap.** ÖÇK status does not by itself prohibit wind farms; activities there need permission from the environment ministry. No later boundary change was found [S, search only] |
| Strictly protected sensitive area, Gelibolu Peninsula Part 1 | Presidential Decision 1133, Official Gazette 30791 (1.6.2019). Land area near the head of the gulf (UTM ≈ 483 km E, about 26.8° E) | [V] no overlap (about 30 km away) |
| Greek protected sites (WDPA) | Evros Delta National Park and SPA (Birds Directive): **14.3 km**. Thracian marine SCI (Habitats Directive): **15.2 km** | [V] no overlap; relevant to the bird-migration context |
| WDPA coverage of Türkiye | Only 17 Turkish polygons in the public WDPA | Absence from WDPA ≠ absence of protection |
| Bird migration and biodiversity | Regional concern (Evros delta, Dardanelles flyway) | [I] not quantified; needs an environmental impact assessment |
| Navigation and LNG | BOTAŞ Saros FSRU, operating since 2023, in Keşan–Sazlıdere [S, BOTAŞ page]. About 16 km east of the polygon, using an unverified coordinate. Tanker approach routes were not checked | Regional concern; overlap not verified |
| Military exercise areas | None verified | Do not claim |
| Fishing | Older fisheries communiqués (FAOLEX) ban trawling in part of Saros, north of a line at Boztepe Burnu. The current boundary and its overlap with the zone are not verified | Regional concern |
| Seabed and geotechnics | Depth 1–62 m (Phase 1). The North Anatolian Fault (Ganos) runs through the gulf; the fault's distance from the polygon was **not** computed (no fault geometry in the repository) | Keep the manuscript's existing limitation |
| Grid connection | The draft leaves the connection point to the grid operator (§10.5). No substation screening done | Not screened |

**What materially affects the manuscript:**

1. The confirmed ÖÇK overlap.
2. The nearshore and shallow fringe, and the 50–62 m strip, as screening
   classes.

The other items are regional context and should be disclosed as unscreened
limitations, not as restrictions.

---

## C. Official YEKA status and policy accuracy (primary sources)

| Item | Verified finding |
|---|---|
| **C1. Status** | **Candidate** (aday) YEKA. MENR notice "Deniz Üstü Rüzgar Enerjisine Dayalı **Aday** YEKA İlanı", **13.05.2026** (enerji.gov.tr, duyuru id 30615). Detailed studies have started for designation; the zone is **not yet a declared YEKA** in the Official Gazette, and there is **no approved project**. The specification is a **draft** (*YEKA DÜRES‑2026 Şartname Taslağı*; consultation until 17.08.2026). As of 11.11.2026 no final specification or tender notice was found (press of 08.10.2026 still describes a draft) |
| **C2. Terminology** | In the draft, **DÜRES = "Deniz Üstü Rüzgâr Enerjisi Santrali"** (offshore wind power plant; definition 12). The candidate-area KML files are named "SAROS DÜRES" etc. The manuscript's expansion "Deniz Üstü Yenilenebilir Enerji Kaynak Alanları" is **wrong**. Use "Saros offshore-wind candidate YEKA (file name 'SAROS DÜRES')" |
| **C3. History** | Four offshore candidate YEKAs were announced in **2023** (Bandırma, Bozcaada, Gelibolu, Karabiga) [S: Capital, 9.8.2023]. Confirm against the 2023 MENR notice before citing. The 2026 set (Saros, Gökçeada, Bozcaada, Edremit) is therefore not the "first four" |
| **C4. 1 000 MWe** | Draft §1 and §3: a competition for **total 1 000 MWe connection capacity**. Draft Ek‑7 defines the YEKA as **"any one of" the areas published under notice 30615**. It is **not Saros-specific**; which area is tendered is open in the draft. Draft §4.4 also lets the winner request a capacity change of up to 50% after seabed surveys |
| **C5. 40% / 43%** | **Price indexation, not eligibility:** the bid price is taken to correspond to a 43% capacity factor (§8.2.1). The tariff rises 2.5% per percentage point of capacity factor below 43%, with multipliers 1.025 / 1.050 / 1.075 at 42 / 41 / 40%, and is floored at the 40% price (§8.2.4). The final price uses the 4-year average capacity factor after first acceptance (definition 10, §8.2.3). **Exit right:** if measurements show a capacity factor below 40%, the *winner may request* termination with a justification report, and the guarantees are returned (§4.3). The right is exercisable within 4 years of signature (§4.5). **Termination is not automatic.** The draft excerpt does not define how capacity factor is measured (gross or net, or the metering point) |

**Correction to the earlier review.** `PRE_SUBMISSION_REVIEW.md` §0 summarised
this as the draft "treating below 40% as grounds for termination" ("%40'ın
altını fesih gerekçesi sayıyor"). The accurate reading is the optional exit
right described above. The 40% and 43% figures are tariff reference points,
not a feasibility threshold. Comparing them with the study's 27.7% net
capacity factor is only indicative, because the draft's capacity-factor
basis is undefined.

---

## D. Minimum defensible publication framework

### Keep

- **Per-MW** results as primary.
- **S3** as the single principal illustration. It can be accompanied by
  **S1/S2** only as generic capacities (for example "250 / 500 MW"), without
  phase labels.

### Change

1. **S3 label:** "full Phase‑2 deployment" → "≈1 GW illustrative scenario,
   equal to the draft first-tender connection capacity (1 000 MWe), if
  allocated to Saros". Also state that the 7D × 5D spacing is an assumption,
   and add the density (5.8 MW/km²) and the 8% wake caveat.
2. **S1 / S2:** remove "pilot" and "first allocation".
3. **Remove S4** from the results, Table 4, Figures 5d and 7, and the
   "theoretical maximum" wording (Methods l.141–143, Results l.98–101 and
   l.149–150). If mentioned at all, describe it as a geometric packing limit
   with no energy or CO₂ values.
4. **Policy wording:**
   - "designated", "committed site", "siting decision has now been made"
     (`01_introduction.md:44,56`; abstract l.3) → "candidate area announced
     on 13 May 2026".
   - Replace the DÜRES expansion (`02_study_area.md:25`,
     `03_methodology.md:6`).
   - "first four" → "following four candidate areas announced in 2023".
   - "14 May" → "13 May".
   - "as-yet-unfinalised installed capacity" (abstract l.28,
     `01_introduction.md:75`, `03_methodology.md:135`) → "the draft tender
     specifies 1 000 MWe for one of the four candidate areas".
5. **Disclose:**
   - the confirmed overlap of about 25 km² (14%) with the Saros ÖÇK;
   - the nearshore (<10 m, <1 km) fringe and the 50–62 m strip as screening
     classes;
   - that bird migration, fisheries, navigation and LNG traffic, the fault
     and grid connection were **not screened**;
   - that the study is a preliminary resource and emissions assessment, not
     a feasibility study.

### Remove rather than soften

- S4 as a "theoretical maximum".
- "Committed / designated site".
- The wrong DÜRES expansion.
- Any statement that the 40% capacity factor is a threshold or an automatic
  termination condition.
- "Pilot" and "first allocation" labels.

---

## Sources

- MENR, *Deniz Üstü Rüzgar Enerjisine Dayalı Aday YEKA İlanı* (13.05.2026),
  with the KML archive: https://enerji.gov.tr/duyuru-detay?id=30615
- MENR, *YEKA DÜRES‑2026 Şartname Taslağı*:
  https://enerji.gov.tr/Media/Dizin/ETKB/Duyurular/YEKA_DURES-2026_SARTNAME_TASLAGI.pdf
  (§1, §3, §4.3–4.5, §8.2, definition 12, Ek‑7)
- Official Gazette 27793 (22.12.2010), Council of Ministers Decision
  2010/1089 (Saros ÖÇK):
  - https://www.resmigazete.gov.tr/eskiler/2010/12/20101222-2..htm
    (sha256 `820a2531…`)
  - annex https://www.resmigazete.gov.tr/eskiler/2010/12/20101222-2-2.pdf
    (sha256 `92bbe585…`)
- Official Gazette 30791 (1.6.2019), Presidential Decision 1133:
  https://www.resmigazete.gov.tr/eskiler/2019/06/20190601-15.pdf
- WDPA (UNEP-WCMC) map service:
  https://data-gis.unep-wcmc.org/server/rest/services/ProtectedSites/The_World_Database_of_Protected_Areas/MapServer
- Para Dergi (08.10.2026), draft status:
  https://www.paradergi.com.tr/finans/2026/10/08/offshore-ruzgari-turkiyede-esiyor
- Capital (09.08.2023), 2023 candidate areas [S]:
  https://www.capital.com.tr/haberler/tum-haberler/deniz-ustu-res-icin-yeka-buyuklukleri-belirlendi
- BOTAŞ, Saros FSRU Terminal [S]: https://botas.gov.tr/pages/saros-fsru-terminal/769
- FAOLEX, older Turkish fisheries communiqué [S]:
  https://faolex.fao.org/docs/pdf/tur78180.pdf
