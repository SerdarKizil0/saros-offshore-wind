# Phase 2B — Wind-resource representativeness and sensitivity

*11 November 2026. This is a review analysis. The baseline wind data, the
production Monte Carlo, the emissions method, the manuscript and the
Phase 2A outputs are unchanged. All outputs are **provisional**.*

**Labels used below:**

- **[OBS]** observed data
- **[MOD]** model or reanalysis output
- **[ASSUMP]** assumption
- **[INF]** inference by the reviewer

**Reproduce:**

```bash
python scripts/phase2b_fetch_inputs.py      # network; writes docs/review/phase2b_data/ (1.8 MB) + MANIFEST.json
python scripts/phase2b_wind_validation.py   # offline; writes results/provisional/phase2b/*.json
python -m pytest -q tests/                  # 23 passed
```

---

## 1. Are ERA5 and GWA comparable?

### 1.1 What each number is

| | ERA5 (study baseline) | Global Wind Atlas 4.0 |
|---|---|---|
| Nature | [MOD] Global reanalysis, ECMWF IFS 4D‑Var | [MOD] Downscaling: **ERA5-forced WRF at 3 km**, generalised wind climates, then WAsP/PyWAsP microscale |
| Period | 2014–2024, hourly instantaneous, UTC | **2008–2017** climatology |
| Spatial support | One 0.25° node (native grid about 31 km), 40.50° N 26.25° E | 0.0025° (≈250 m) grid |
| Height | 100 m above the model surface (`U100`) | 100 m above ground or sea |
| Quantity | Mean of 96 432 hourly speeds | Mean of the predicted wind climate. At the node, A·Γ(1+1/k) = mean speed = 8.185 exactly |
| Validation | Not validated at this site | 52 masts in Bangladesh, Ethiopia, Maldives, Pakistan, Papua New Guinea, Vietnam and Zambia: mean speed bias 0% ± 14%, mean absolute bias 11% ± 9%. **No offshore and no Turkish sites** (DTU report E‑0256) |

The GWA crop is from the `country_tifs_v4` raster `TUR_wind-speed_100m.tif`
(download URL in `MANIFEST.json`). The raster has no version tag, but it is
served from the v4 path, and GWA 4.0 was released in June 2025.

### 1.2 Values at 100 m

The ERA5 node mean for 2014–2024 is **7.120 m/s** [MOD]. Other ERA5 means:
2015–2024, 7.181 m/s; 2014–2017 (the overlap with the GWA period),
6.975 m/s.

| GWA 4.0 quantity [MOD] | Mean (m/s) | GWA / ERA5 |
|---|---|---|
| Pixel containing the ERA5 node | 8.185 | **1.150** |
| Official polygon (2 935 pixels) | **7.842** (7.23–8.16, σ 0.20) | **1.101** |
| 0.25° box around the node, all pixels | 7.988 | 1.122 |
| Same box, sea pixels only | 8.061 | 1.132 |
| Same box, land pixels only | 7.504 | 1.054 |

The review's value of 7.83 m/s is **verified** (7.84 with exact pixel
centres). The Weibull shape is similar (GWA polygon k = 2.08, ERA5 k = 2.04).
Power density is 534 W/m² for GWA against 408 W/m² for ERA5
(ρ = 1.225), consistent with the speed ratio cubed.

### 1.3 Land–sea representation of the ERA5 node

- The node is **outside the polygon**, 3.7 km south of its boundary and
  7.7 km from the centroid.
- It sits on the shelf slope at about 172 m water depth (EMODnet [OBS]),
  10.6 km from the Thrace coast and 15.3 km from the Gelibolu coast.
- Geometric land share [INF, from EMODnet; the ERA5 land–sea mask itself was
  not available]: 12.8% of the 0.25° box around the node and **41.7% of the
  0.5° box**. The ERA5 native grid spacing (about 31 km) lies between these
  two, so the node's value is influenced by Thrace and Gelibolu land surface.

### 1.4 Bias or disagreement?

**It is disagreement between models, not a demonstrated ERA5 bias.** Three
reasons:

1. GWA is not independent of ERA5. It is downscaled from it.
2. The two datasets cover different periods (2008–2017 against 2014–2024),
   and a period-matched ERA5 mean cannot be computed from the available
   data.
3. Neither dataset has been validated offshore in this region. GWA's own
   validation spread (±14% per site) is larger than the 10% gap.

A plausible mechanism is coarse ERA5 resolution with land influence near a
coast [INF], but there is **no observational evidence** at 100 m offshore.
Wording such as "ERA5 underestimates" is not supported.

---

## 2. Spatial and temporal representativeness

### 2.1 Spatial

- Assigning each polygon point to its nearest 0.25° node gives:
  **62.6% to 40.50/26.25 (the node used)**, 27.7% to 40.50/26.00 and 9.7%
  to 40.50/26.50 [INF from geometry].
- GWA models a north–south gradient across the zone [MOD]: 7.60 m/s in the
  band next to the coast (40.58–40.60° N) and 7.97 m/s in the southern band
  (40.50–40.53° N), a difference of about 5%.
- A single node cannot resolve either feature.

### 2.2 Neighbouring ERA5 cells

**Not available.** The repository has no series for other nodes, there are
no CDS credentials, and the Open‑Meteo archive API timed out from this
environment (its forecast API answered). No substitute was generated.

However, the original CDS request box (40.454–40.649° N,
25.989–26.511° E; `config/site.py`) should already contain the 40.50/26.00
and 40.50/26.50 nodes in the authors' raw NetCDF files [INF]. Check the
coordinates in the files.

### 2.3 The 2014 anomaly

| Series | 2014 vs 2015–2024 mean | z-score | Notes |
|---|---|---|---|
| ERA5 U100 [MOD] | −9.4% | −5.1 | |
| ERA5 U10 [MOD] | −10.1% | | |
| **Çanakkale (GSOD 17112099999), 43 km [OBS]** | **−18.5%** | **−6.7** | 365 days of data in 2014. Its 2014 monthly anomalies correlate with ERA5 U10 at **r = 0.94**, including the **positive October** in both (+11% station, +18% ERA5) |
| Alexandroupoli/Dimokritos (16627099999), 47 km [OBS] | All 8 complete months negative | | 249 days in 2014; r = 0.44 |

In 2014, shear (α = 0.153), the share of hours with U10 > U100 and the share
of hours below 3 m/s are within the range of the other years.

**Conclusion [INF]:** the anomaly is corroborated in sign and timing by an
independent observation. It is very likely a genuinely calm year in the
region, not a data or processing error. **2014 should stay in the record.**

The coastal 10 m station magnitudes are not comparable to 100 m offshore
winds, and possible instrument changes at the station cannot be excluded.

### 2.4 Completeness and internal consistency [OBS on the file]

- 96 432 hours, equal to the full hourly range 2014‑01‑01 00:00 to
  2024‑12‑31 23:00. No duplicates, no NaN, no repeated-value runs.
- Ranges are physically plausible (U100 0.02–25.3 m/s; wdir 0–360°).
- U_hub/U100 is constant at 1.0073074 (= 1.05^0.1492).
- Yearly hour counts are correct (8 760 / 8 784).
- Year-to-year α varies between 0.147 and 0.153.
- Inter-annual coefficient of variation: 3.35% (ddof = 1; the manuscript
  uses ddof = 0, giving 3.2%), and **1.83% without 2014**. The standard
  error of the 11-year mean is 1.0%.

### 2.5 Is more data needed?

The central estimate would need independent offshore observations
(LiDAR or a mast) to be called *validated*. Measurement is **not** required
for a transparently framed *preliminary, reanalysis-based* assessment. The
YEKA DÜRES‑2026 tender already obliges the winning bidder to measure for at
least 12 months.

---

## 3. AEP sensitivity to wind speed (corrected OEDB curve, nominal losses)

Method: every hourly U_hub value is multiplied by a factor; the turbine
curve and losses are fixed (script 04 method). These are **sensitivity
experiments only**: not corrections, forecasts or percentiles. Output:
`results/provisional/phase2b/wind_speed_sensitivity.json`.

| Case | Speed factor | Gross AEP (GWh/turbine) | Gross CF | Net AEP (GWh/turbine) | Net CF | Net yield (GWh/MW) | ΔAEP |
|---|---|---|---|---|---|---|---|
| −10% | 0.90 | 21.64 | 25.98% | 18.35 | 22.03% | 1.93 | −20.4% |
| −5% | 0.95 | 24.43 | 29.33% | 20.71 | 24.87% | 2.18 | −10.2% |
| **Baseline ERA5** | 1.00 | **27.20** | **32.66%** | **23.06** | **27.69%** | **2.43** | 0 |
| +5% | 1.05 | 29.92 | 35.93% | 25.37 | 30.46% | 2.67 | +10.0% |
| +10% | 1.10 | 32.56 | 39.10% | 27.60 | 33.14% | 2.91 | +19.7% |
| Scaled to GWA polygon mean (illustrative) | 1.1014 | 32.63 | 39.18% | 27.67 | 33.22% | 2.91 | +20.0% |

**Elasticity:** AEP changes about 2% for every 1% change in wind speed.

The 10% ERA5–GWA disagreement is therefore worth about **20% of AEP**,
roughly three times the Monte Carlo P10–P90 half-width (±8%). The current
MC does not represent this resource uncertainty.

Even the GWA-scaled case (33% net CF) stays below the 40% capacity-factor
threshold in the YEKA draft specification [MOD + ASSUMP: uniform scaling,
V164‑9.5, nominal losses].

---

## 4. Scientific judgement

1. **ERA5 remains defensible as the primary dataset.** It is a standard,
   documented and reproducible source; the 11-year series is complete and
   internally consistent; and its temporal variability, including 2014, is
   corroborated by an independent station. **It is not defensible to present
   its level as validated**, or as accurate to better than about ±10% in
   mean speed.

2. **The single-node design supports only node-level conclusions.** The node
   lies outside the zone, covers about 63% of it, carries notable land
   influence, and misses a modelled gradient of about 5%. "Site-specific"
   and zone-wide statements are not supported as written.

3. **The GWA difference does require additional quantitative analysis before
   submission**, but only light analysis (minimum list below), not new
   measurements.

4. **Claims that must be weakened:**
   - "first … site-specific assessment" (`00_abstract.md:6`,
     `01_introduction.md:65`, `03_methodology.md:22`,
     `06_conclusion.md:3`) → "a reanalysis-based assessment at the nearest
     ERA5 node".
   - "low inter-annual variability (3.2%) … reliability … financial risk …
     high confidence" (`00_abstract.md:20`, `04_results.md:26-30`,
     `05_discussion.md:18-22`, `06_conclusion.md:15,30`) → report 3.35%
     (or 1.8% without 2014) and the −9.4% calm year 2014; drop the
     confidence and finance claims.
   - "above the threshold generally regarded as economically viable"
     (`04_results.md:13-14`) → unsupported without a cited threshold and a
     resource uncertainty band.
   - "characterises the zone through its centroid grid cell"
     (`05_discussion.md:94`; also `03_methodology.md:44`) → the node is
     outside the polygon and not a "centroid cell".
   - The MC P10–P90 must not be called the total uncertainty.

5. **Minimum necessary corrective action before submission:**
   1. State the actual node, its position outside the polygon and its land
      share.
   2. Report the GWA 4.0 comparison (Table §1.2), describe it as
      disagreement between models, and give the different periods.
   3. Present the ±5% / ±10% AEP sensitivity (±10% / ±20%) as an explicit
      resource-uncertainty statement, and reframe the headline as
      preliminary.
   4. If the raw NetCDF files are available, re-extract the 26.00 and
      26.50 nodes (no new download) and report the spread or an
      area-weighted value.
   5. Revise the inter-annual variability text, keeping 2014.

   Optional but recommended: a single-node ERA5 2008–2017 retrieval for a
   period-matched GWA comparison. Field measurement is **not** required for
   a preliminary paper.

---

## 5. Inputs and sources

| Input | Source | Retrieved |
|---|---|---|
| ERA5 series | `data/processed/wind_hub_105m.parquet` (sha256 `0cfc4742…`; see `data/README.md`) | — |
| GWA 4.0 rasters (wind speed, power density, Weibull A and k at 100 m) | https://globalwindatlas.info/api/gis/country/TUR/{layer}/100 → https://gwa.cdn.nazkamapps.com/country_tifs_v4/ ; crops and checksums in `docs/review/phase2b_data/MANIFEST.json` | 11.11.2026 |
| GWA 4.0 method and validation | Hansen, Floors, Badger, *Global Wind Atlas 4 – Validation*, DTU Wind Energy Report E‑0256, https://backend.orbit.dtu.dk/ws/portalfiles/portal/400877326/DTU_Wind_Energy_Report-E-0256.pdf ; release note https://wasp.dtu.dk/NewsArchive/2025/06/Global-Wind-Atlas-4-0-released | 11.11.2026 |
| EMODnet DTM 2024 | doi:10.12770/cf51df64-56f9-4a99-b1aa-36b8d7b743a1, WCS https://ows.emodnet-bathymetry.eu/wcs | 11.11.2026 |
| GSOD daily summaries | https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/{year}/{station}.csv ; stations from https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv | 11.11.2026 |
| Official polygon | MENR KML (Phase 1), `docs/review/phase1_data/SAROS_DURES_official.kml` | — |
