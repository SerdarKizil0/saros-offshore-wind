# Phase 1 Technical Validation: Power Curve and Bathymetry

*11 November 2026. Scope: (A) the V164‑9.5 MW power curve in
`config/turbine.py`, and (B) Saros bathymetry and site geometry. No change was
made to the manuscript, `config/`, `scripts/` or `results/`. Every number
below comes from `python docs/review/phase1_checks.py`, which uses the inputs
in `docs/review/phase1_data/`.*

---

## A. Vestas V164‑9.5 MW power curve

### A1. Cp recalculated from the implemented curve

The definition used:

- Cp = P_el / (½ ρ A v³)
- ρ = 1.225 kg m⁻³, the IEC 61400‑12‑1 standard density, which is the usual
  basis for published curves.
- A = π·82² = 21 124 m², for a 164 m rotor.
- v = free-stream wind speed at hub height.
- P_el = electrical output, so this is an electrical Cp.

| v (m/s) | Repo (kW) | Cp | OEDB V164/9500 (kW) | Cp | Repo / OEDB |
|---|---|---|---|---|---|
| 6 | 1310 | 0.469 | 1226 | 0.439 | 1.07 |
| 7 | 2350 | 0.530 | 2030 | 0.457 | 1.16 |
| 8 | 3690 | 0.557 | 3123 | 0.471 | 1.18 |
| 9 | 5320 | **0.564** | 4444 | 0.471 | 1.20 |
| 10 | 7050 | 0.545 | 5900 | 0.456 | 1.20 |
| 11 | 8550 | 0.496 | 7299 | 0.424 | 1.17 |
| 12 | 9350 | 0.418 | 8601 | 0.385 | 1.09 |
| 13 | 9500 | 0.334 | 9272 | 0.326 | 1.03 |
| 14 | 9500 | 0.268 | 9500 | 0.268 | 1.00 |

**The reviewer's figure is confirmed:** the peak Cp is 0.564 at 9 m/s, which
is 95% of the Betz limit (0.593).

There is also an inconsistency inside the repository. The implemented curve
reaches 9.45 MW at 12.5 m/s and 9.5 MW at 13 m/s. Yet `config/turbine.py`
sets `rated_ms = 14.0`, and the manuscript states rated power at 14 m s⁻¹
(§3.5 line 108; Table 2). The curve does not match its own stated
specification.

### A2–A3. Sources and provenance

| Source | Type | V164‑9.5 data | Assessment |
|---|---|---|---|
| Vestas product page | Manufacturer | Rated 9.5 MW, rotor 164 m, cut‑out 25 m/s; no curve table | Confirms specs only |
| thewindpower.net (entry 1476) | Third party | 9.5 MW, 164 m, 21 125 m², 450 W/m²; cut-in/rated/cut-out and curve behind paywall | Not usable |
| wind-turbine-models.com | Third party | States that no power data is stored for the V164‑9.5 | Not usable |
| **OEDB turbine library** (row `V164/9500`, windpowerlib `dev` @191d8ca) | Third-party digitisation of the manufacturer's published graph. Listed source: "mhivestasoffshore.com; engauge digitizer; thewindpower.net" | Full curve in 0.5 m/s steps; rated at 14.0 m/s; peak Cp 0.476 | **Best available model-specific evidence.** Not manufacturer-certified. Digitisation error and density basis are not documented |
| OEDB row `V164/8000` | Third party (wind-turbine-models) | Peak Cp **0.731** | Physically impossible (above Betz). Shows that third-party entries must be checked with Cp |
| LEANWIND 8 MW/164 m (NREL turbine-models @e9e4ccc) | Theoretical reference turbine on the same rotor size | Peak Cp 0.44 | Physical plausibility check only; it is not the V164 |
| Repo curve | **No source.** No citation in code or manuscript; the repository has one initial commit | Peak Cp 0.564; rated 13 m/s | Origin unknown |

No public, manufacturer-tabulated V164‑9.5 curve was found. Certified curves
are normally released by Vestas under NDA or appear in project consent
documents. I did not search consent documents exhaustively.

### A4. Is the implemented curve defensible?

**No.** Three independent lines of evidence point the same way:

1. Its Cp of 0.53–0.56 over 7–10 m/s is far above the 0.47 peak of the
   model-specific digitised curve.
2. It is internally inconsistent with the 14 m/s rated speed used in the
   code and in the manuscript.
3. Its provenance is undocumented.

The comparison does not rest on a generic Cp cap. It uses a curve for this
specific model, which happens to land in the physically expected range
(0.44–0.48).

### A5–A6. Effect on AEP

The comparison uses the same Weibull(k = 2.035, c = 8.080) basis as the
Monte Carlo (MC), the same 0.1 m/s grid, and the same cut-out handling.

| | Repo curve | OEDB V164/9500 | Change |
|---|---|---|---|
| Gross CF (Weibull basis) | 35.54% | 32.06% | **−9.8%** |
| Gross AEP per turbine | 29.59 GWh | 26.70 GWh | |
| Net CF, nominal losses | 30.13% | 27.18% | |
| **MC net yield P10/P50/P90** (GWh yr⁻¹ MW⁻¹) | 2.41 / 2.62 / 2.83 | **2.17 / 2.37 / 2.57** | −9.8% |
| MC net CF P50 | 29.9% | **27.0%** | |
| MC avoided CO₂ P50 (t yr⁻¹ MW⁻¹) | 1525 | **1375** (1150–1586) | |
| S3 (997.5 MW) energy / avoided CO₂ | 2.62 TWh / 1.52 Mt | **2.36 TWh / 1.37 Mt** | |

The MC was rerun with the identical seed and sampling; only the curve
changed.

The deterministic values from the empirical series cannot be recomputed,
because `data/processed/wind_hub_105m.parquet` is not in the repository.
Scaling them by the −9.8% ratio gives approximately: gross 30.4 → 27.4 GWh,
net CF 31.0 → 27.9%, and 2.71 → 2.45 GWh MW⁻¹. These must be confirmed by
rerunning `scripts/04`.

The derived quantities in the abstract, §4.2–4.6, §5.3, the conclusion,
Tables 3, 4 and 7, Figures 2 and 5–7, and the README would change
proportionally:

| Derived quantity | Published | With OEDB curve (approx.) |
|---|---|---|
| Households | 0.86 M | ≈0.78 M |
| Car-equivalents | 0.76 M | ≈0.69 M |
| Share of national demand | 0.75% | ≈0.68% |
| Fossil comparison | 1.98 Mt | ≈1.78 Mt |

These numbers isolate the power-curve effect only. They do not include the
other review items (the ERA5 bias versus Global Wind Atlas, and the
grid-factor sampling). Combining them belongs to Phase 2.

### A7. Recommended modelling approach (not implemented)

1. **Retire the current curve.** It should not be kept even as a
   sensitivity case, because it is physically implausible and inconsistent
   with the stated rated speed.
2. **Adopt the OEDB `V164/9500` curve as the primary curve**, with explicit
   provenance in the code comment and in §3.5. Suggested wording: "power
   curve digitised from the manufacturer's published graph (Open Energy
   Database turbine library), standard air density 1.225 kg m⁻³ assumed;
   not a certified curve".
3. **Report a ±3% curve-uncertainty term** (a judgement for digitisation and
   density basis, to be stated as such), or ask Vestas for the certified
   curve.
4. Optionally, apply the IEC 61400‑12‑1 air-density correction once site
   density has been computed from ERA5 temperature and pressure. Those
   fields are not in the repository, so this has not been done.
5. **Validate before switching the production model:** rerun `scripts/04`
   on the parquet file and check that it reproduces −9.8% ± ~0.5% relative
   to the current empirical result.

---

## B. Gulf of Saros polygon and bathymetry

### B1–B2. Polygon versus the official KML

- **Official source:** the MENR announcement "Deniz Üstü Rüzgar Enerjisine
  Dayalı Aday YEKA İlanı" (13.05.2026), archive
  `Offshore_Aday_YEKA_Alanlari.zip` (sha256 `240de643…`), file
  `SAROS DÜRES.kml` (sha256 `190fda95…`).
- The ring has 28 tuples; it is closed, so there are 27 distinct vertices.
- **Coordinate system and order:** KML 2.2 uses WGS84 with `lon,lat`
  ordering. `config/site.py` also stores `(lon, lat)` in the same vertex
  order.
- The maximum vertex difference is 0.000049°, because the config rounds to
  4 decimal places.
- **Area at full precision is 172.53 km²**, which matches the manuscript's
  172.5. The config gives 172.56, stored as `SITE.area_km2 = 172.6`.
- **Centroid:** 40.5571° N, 26.1978° E. Both the manuscript and the code are
  correct.
- **Confirmed:** the polygon in the code is the official one.

### B3–B4. Bathymetric data

| Dataset | Access | Resolution | Convention |
|---|---|---|---|
| **EMODnet Digital Bathymetry DTM 2024** (doi:10.12770/cf51df64‑56f9‑4a99‑b1aa‑36b8d7b743a1) | WCS `emodnet__mean`, crop 25.98–26.52° E × 40.45–40.66° N | 1/16′ (≈88 m E–W × 116 m N–S) | EPSG:4326; elevation positive up; land included; vertical datum LAT |
| GEBCO 2020 (cross-check) | api.opentopodata.org, `interpolation=nearest`, 244 points | 15″ (≈350 × 460 m) | Elevation relative to MSL, positive up |

The Aegean is microtidal, so the LAT/MSL difference is negligible at 1 m
precision.

Method: a cell is counted as inside the zone when its centre falls inside the
full-precision KML ring (even-odd rule). That gives 16 907 cells, covering
172.4 km² and closely matching the polygon area. Depth is reported positive
downward. The coastline is taken as the 0 m contour of the same DTM.

### B5. Depth inside the polygon

**EMODnet DTM 2024:**

| Statistic | Depth (m) |
|---|---|
| Minimum | 1.0 |
| P5 | 7.2 |
| **Median** | **27.8** |
| Mean | 29.3 |
| P95 | 54.7 |
| **Maximum** | **61.6** |

No cells lie at or above the datum.

Share of zone area deeper than a given depth:

| Depth | Share |
|---|---|
| > 10 m | 90.9% |
| > 20 m | 68.5% |
| > 30 m | 45.3% |
| > 40 m | 25.9% |
| > 50 m | 11.4% |
| > 60 m | 0.2% |

**Spatial pattern:** depth increases **southward**, away from the Thrace
coast and toward the shelf edge. It does not increase westward:

| Band | Median depth (m) | Maximum (m) |
|---|---|---|
| Latitude 40.58–40.60° N (north) | 16 | 41 |
| Latitude 40.50–40.53° N (south) | 45 | 61 |
| Longitude 26.03–26.12° E (west) | 34 | 61 |
| Longitude 26.22–26.32° E (centre-east) | 39 | **62** |

The deepest cell (61.6 m) is at 40.5547° N, 26.2536° E, on the southern
edge of the central part of the zone, not on the western margin.

**GEBCO 2020** agrees: minimum 3 m, median 30 m, maximum 62 m; 12% of
samples deeper than 50 m and 1% deeper than 60 m.

**Geometry relative to the coasts:**

- Distance to the Thrace (northern) coast: minimum 0.25 km, median over the
  vertices 4.8 km, maximum anywhere in the zone 9.3 km.
- 5% of the zone is within 1 km of that coast, 23% within 2 km, and 65%
  within 5 km.
- The closest approach to the Gelibolu Peninsula is 13.6 km.
- No cell inside the polygon is deeper than 200 m. The slope down to more
  than 200 m begins **2.3 km** south of the polygon boundary.

### B6. Fixed-bottom versus floating foundations

- About 89% of the zone lies shallower than 50 m, the fixed/floating
  screening threshold used by World Bank/ESMAP for offshore wind technical
  potential.
- The rest of the zone is at 50–62 m. That is only slightly above the
  threshold and is a strip along the southern boundary, not a western
  margin.
- Nothing in the data supports the statement that a "deeper western margin
  would require exclusion or floating foundations". The whole zone is a
  shelf site. Fixed-bottom foundations are plausible throughout; the
  50–62 m strip is a foundation-design question (for example, the choice of
  substructure), which these data do not settle.
- The new constraints are on the shallow and nearshore side instead:
  9% of the area is shallower than 10 m and 5% is within 1 km of the shore.
  These are relevant to installation vessels, visual setback and buildable
  area. This study does not quantify those effects.

### B7. Manuscript statements to correct

| Location | Current text | Evidence-based correction |
|---|---|---|
| `02_study_area.md` l.11 | "in the central-southern part of the gulf, north of the Gelibolu Peninsula" | Along the **northern (Thrace) shore** of the gulf, 0.25–9.3 km offshore; ≥13.6 km from the Gelibolu Peninsula |
| `02_study_area.md` l.41–47 (§2.3) | "deepening westward toward the inner basin… eastern and central portions … plausibly compatible with fixed-bottom … whereas the deeper western margin would require either exclusion or floating foundations" | Zone depths 1–62 m (median 28 m), deepening southward toward the shelf edge. The inner basin lies outside the zone (>200 m begins about 2.3 km south of it). About 89% is shallower than 50 m. Remove the western-margin and floating statement |
| `02_study_area.md` l.40 citation | "(Yaltırak et al., 1998, 2008)" used for zone depth | Keep Yaltırak only for gulf-scale morphology. Cite EMODnet DTM 2024 for the zone statistics. The 2008 reference is also missing from the reference list |
| `03_methodology.md` l.9 | "immediately north of the Gelibolu (Gallipoli) Peninsula" | Off the Thrace coast, on the northern shelf of the Gulf of Saros |
| `03_methodology.md` l.14 | "parallel to the peninsular coastline" | Parallel to the northern (Thrace) coastline |
| `03_methodology.md` l.74–75; `04_results.md` l.32–33 | α attributed to "proximity of the Gelibolu Peninsula" | The adjacent coast is Thrace. Whether α is interpreted correctly at all is outside Phase 1 |
| `05_discussion.md` l.113–117 | "appropriate for the shallower eastern and central parts … not for its deeper western margin, where floating foundations or exclusion would be required" | Fixed-bottom is plausible across the zone (1–62 m). The remaining limitation is that the buildable area has not been resolved for the nearshore shallows (<10 m), the 50–62 m strip and geotechnics |
| `tables.md` l.15 | Nearest landfall: Gelibolu (Gallipoli) Peninsula | Thrace coast (0.25 km). Gelibolu is ≥13.6 km away |
| `tables.md` l.23 | Water depth: ~50 to >200 m (shelf → inner basin); Yaltırak et al., 2008 | 1–62 m (median 28 m; P5–P95 7–55 m); EMODnet DTM 2024 |
| `tables.md` l.24 | Dominant seabed (E/central): shelf, fixed-foundation-compatible | Whole zone on the northern shelf; about 89% shallower than 50 m |
| `03_methodology.md` l.107–108 | "Its manufacturer power curve defines…" | State the curve's provenance (see A7). The 14 m/s rated speed is consistent with the OEDB curve |

**Code corrections, to apply in Phase 2 after validation:**

- `config/site.py:103`: change `nearest_landfall = "Gelibolu Peninsula"` to
  the Thrace coast. Optionally read the KML at full precision, which gives
  an area of 172.5 km².
- `config/turbine.py:24–31`: replace `POWER_CURVE_MS_KW` with the OEDB
  `V164/9500` values, add a provenance comment, and set 25 m/s to 9500 kW
  with zero above 25 m/s, as in the current handling.

**Effect on published numbers:** none directly. Energy is reported per MW
and the power curve is independent of depth. The site description, Table 1
and the limitations section change. The S4 "theoretical maximum" (full
172.5 km² at 7D×5D) would shrink if nearshore and shallow areas are
excluded. That reduction is not quantified here.

---

## C. Previous review claims: confirmed or refuted

| Claim in `PRE_SUBMISSION_REVIEW.md` | Verdict |
|---|---|
| Curve Cp peaks at 0.564 | **Confirmed** (ρ 1.225, A 21 124 m²) |
| Curve has no source | **Confirmed** |
| Electrical Cp peak should be about 0.44–0.48 | **Supported** by a model-specific curve (0.476), not by a generic cap |
| Cp cap of 0.48 or 0.45 reduces AEP by 6.1% or 9.5% | **Superseded.** The cap method is inappropriate; the model-specific curve gives **−9.8%** |
| (New) curve reaches rated at 13 m/s, contradicting the stated 14 m/s | **New finding** |
| Polygon matches the official KML | **Confirmed** (172.53 km², 27 vertices) |
| Depth "4–57 m, median ~30 m" | **Confirmed in substance, refined:** 1.0–61.6 m, median 27.8 m (EMODnet 2024 at full resolution; the review used EMODnet 2018 at 75 bilinear points) |
| "5% of the area deeper than 50 m, 0% deeper than 60 m" | **Corrected:** 11.4% and 0.2% (EMODnet 2024); 12% and 1% (GEBCO) |
| Zone adjacent to the Thrace coast | **Confirmed** (minimum 0.25 km) |
| "Gelibolu is 15–25 km south" | **Slightly overstated:** closest approach 13.6 km |
| The 600 m trough is outside the polygon, to the south | **Confirmed:** no cell deeper than 200 m inside; more than 200 m starts 2.3 km south |
| "Western margin requires floating" is wrong | **Confirmed:** depth grows southward; the western maximum is 61 m, similar to the centre |

---

## D. Remaining uncertainties

1. **OEDB curve accuracy.** Manual digitisation error of a few percent is
   typical but undocumented. The air-density basis is assumed to be
   1.225 kg m⁻³. Vestas operating modes (noise or power modes) are unknown.
   Only a certified Vestas curve removes this uncertainty.
2. **Site air density.** It is not computed, because ERA5 temperature and
   pressure are not in the repository. A density about 1% below 1.225
   lowers ramp-region output by roughly 1%.
3. **Wind-speed averaging.** Applying a 10‑minute IEC curve to hourly
   reanalysis means introduces a small additional bias. It is not
   quantified here.
4. **EMODnet DTM quality.** Source-survey density and quality indices in
   Turkish waters were not checked. The nearshore cells (<10 m) and the
   0 m coastline carry about 100 m positional uncertainty. GEBCO agrees to
   within a few metres on the summary statistics.
5. **Deterministic AEP.** It cannot be recomputed exactly without the
   parquet file (see A6).

---

## Sources

- MENR, *Deniz Üstü Rüzgar Enerjisine Dayalı Aday YEKA İlanı* (13.05.2026)
  and KML archive: https://enerji.gov.tr/duyuru-detay?id=30615
- EMODnet Bathymetry Consortium, *EMODnet Digital Bathymetry (DTM 2024)*,
  doi:10.12770/cf51df64-56f9-4a99-b1aa-36b8d7b743a1; WCS:
  https://ows.emodnet-bathymetry.eu/wcs
- GEBCO Compilation Group, *GEBCO 2020 Grid*, via
  https://api.opentopodata.org/v1/gebco2020
- Open Energy Database turbine library (windpowerlib):
  https://github.com/wind-python/windpowerlib/tree/dev/windpowerlib/oedb
- NREL turbine-models (LEANWIND 8 MW/164 m reference):
  https://github.com/NREL/turbine-models
- Vestas, V164‑9.5 MW product page:
  https://us.vestas.com/en-us/products/offshore/V164-9-5-MW
- thewindpower.net, MHI Vestas V164‑9500:
  https://www.thewindpower.net/turbine_en_1476_mhi-vestas-offshore_v164-9500.php
- wind-turbine-models.com, V164‑9.5 MW:
  https://en.wind-turbine-models.com/turbines/1605-mhi-vestas-offshore-v164-9.5-mw
- ESMAP, *Offshore Wind Technical Potential* (fixed <50 m, floating
  50–1000 m): https://esmap.org/esmap_offshorewind_techpotential_analysis_maps
