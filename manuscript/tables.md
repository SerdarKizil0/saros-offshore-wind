# Tables

*Working tables for the Saros OWF manuscript. Values are drawn directly
from the analysis outputs. Footnote sources to be formatted to journal
style at submission.*

---

## Table 1. Saros DÜRES candidate-zone specifications.

| Property | Value | Source / note |
|---|---|---|
| Designation | Saros DÜRES | MENR YEKA İlanı, 14 May 2026 |
| Region | North Aegean Sea | — |
| Nearest landfall | Gelibolu (Gallipoli) Peninsula | — |
| Polygon vertices | 27 | Official KML |
| Area | 172.5 km² | Computed from polygon |
| Centroid | 40.557° N, 26.198° E | Computed (shoelace) |
| East–west extent | 35.7 km | — |
| North–south extent | 10.5 km | — |
| Bounding box (N, S) | 40.599°, 40.504° N | — |
| Bounding box (W, E) | 26.039°, 26.461° E | — |
| Water depth (zone) | ~50 to >200 m (shelf → inner basin) | Yaltırak et al., 2008 |
| Dominant seabed (E/central) | shelf, fixed-foundation-compatible | Section 2.3 |
| Principal tectonic structure | North Anatolian Fault (Ganos segment) | Section 2.4 |

---

## Table 2. Reference turbine: Vestas V164-9.5 MW.

| Parameter | Value |
|---|---|
| Manufacturer / model | Vestas V164-9.5 MW |
| Rated power | 9.5 MW |
| Rotor diameter | 164 m |
| Swept area | 21 124 m² |
| Hub height | 105 m |
| Cut-in wind speed | 3.5 m s⁻¹ |
| Rated wind speed | 14.0 m s⁻¹ |
| Cut-out wind speed | 25.0 m s⁻¹ |
| Foundation (assumed) | Fixed-bottom monopile |

---

## Table 3. Wind resource and energy production at the Saros centroid (105 m hub, 2014–2024).

| Quantity | Deterministic | Monte Carlo P50 (P10–P90) |
|---|---|---|
| Mean wind speed (m s⁻¹) | 7.17 | — |
| Wind power density (W m⁻²) | 422 | — |
| Weibull shape *k* | 2.04 | — |
| Weibull scale *c* (m s⁻¹) | 8.08 | — |
| Goodness of fit *R²* (CDF) | 0.998 | — |
| Kolmogorov–Smirnov *D* | 0.022 | — |
| Measured shear exponent *α* | 0.149 | — |
| Inter-annual CoV (%) | 3.2 | — |
| Gross AEP per turbine (GWh yr⁻¹) | 30.4 | — |
| Net AEP per turbine (GWh yr⁻¹) | 25.8 | — |
| Gross capacity factor (%) | 36.5 | — |
| Net capacity factor (%) | 31.0 | 29.9 (27.5–32.3) |
| Net specific yield (GWh yr⁻¹ MW⁻¹) | 2.71 | 2.62 (2.41–2.83) |
| Net full-load hours (h yr⁻¹) | 2714 | — |
| Avoided CO₂ (tCO₂ yr⁻¹ MW⁻¹) | — | 1525 (1277–1754) |

*Loss assumptions: array wake 8%, availability 95%, electrical 3%.*

---

## Table 4. Deployment scenarios: capacity, energy and avoided emissions (Monte Carlo P50, P10–P90 in parentheses).

| Scenario | Turbines | Capacity (MW) | Net AEP (TWh yr⁻¹) | Avoided CO₂ (Mt yr⁻¹) | Share of national demand (%) | Households (M) | Car-equiv. (M) |
|---|---|---|---|---|---|---|---|
| S1 pilot | 26 | 247 | 0.65 (0.59–0.70) | 0.38 (0.32–0.43) | 0.19 | 0.21 | 0.19 |
| S2 phase-1 | 53 | 504 | 1.32 (1.21–1.43) | 0.77 (0.64–0.88) | 0.38 | 0.44 | 0.38 |
| **S3 phase-2** | **105** | **998** | **2.62 (2.40–2.83)** | **1.52 (1.27–1.75)** | **0.75** | **0.86** | **0.76** |
| S4 max | 183 | 1739 | 4.56 (4.19–4.93) | 2.65 (2.22–3.05) | 1.31 | 1.50 | 1.33 |

*National demand basis: 347.9 TWh (2024). Households: 3036 kWh yr⁻¹ each
(TEİAŞ). Car-equivalent: 2 tCO₂ yr⁻¹ each. Avoided CO₂ uses the official
combined-margin factor.*

---

## Table 5. Emission factors used in the avoided-emission calculation.

| Factor | Value (gCO₂-eq kWh⁻¹) | Role | Source |
|---|---|---|---|
| Grid — combined margin (wind/solar) | 624.2 | Primary (avoided-EF) | ETKB/EVÇED 2023 (IPCC Tool07) |
| Grid — generation average | 434.0 | MC lower bound | ETKB/EVÇED 2023 |
| Grid — operating margin | 713.4 | MC upper bound | ETKB/EVÇED 2023 |
| Fuel: natural gas | 405 | Fuel-resolved scenario | ETKB/EVÇED 2023 |
| Fuel: imported coal | 803 | Fuel-resolved scenario | ETKB/EVÇED 2023 |
| Fuel: lignite | 1133 | Fuel-resolved scenario | ETKB/EVÇED 2023 |
| Offshore wind life-cycle | 11 (8–14) | Subtracted from grid EF | Bonou et al., 2016; IPCC 2025 |

*The fuel-resolved conventional scenario (Figure F7a) apportions the
Phase-2 generation across the fossil-thermal mix, yielding a gross
conventional burden of 1.98 Mt CO₂ yr⁻¹ and a fossil-displacement avoided
emission of 1.95 Mt yr⁻¹, reported as an upper bound to the combined-margin
headline of 1.52 Mt yr⁻¹.*

---

## Table 6 (optional). Monte Carlo input distributions.

| Parameter | Distribution | Source of bounds |
|---|---|---|
| Weibull shape *k* | Normal(2.04, 0.04) | Fit uncertainty |
| Weibull scale *c* (m s⁻¹) | Normal(8.08, 0.26) | Inter-annual σ of 11 annual fits |
| Array wake loss | Triangular(0.05, 0.08, 0.12) | Literature range |
| Availability | Triangular(0.92, 0.95, 0.97) | Mature-offshore O&M |
| Electrical loss | Triangular(0.02, 0.03, 0.04) | Array + export + transformer |
| Grid emission factor (gCO₂-eq kWh⁻¹) | Triangular(434, 624.2, 713.4) | Official EVÇED 2023 margins |
| Offshore LCA (gCO₂-eq kWh⁻¹) | Triangular(8, 11, 14) | Bonou 2016; IPCC 2025 |

*10 000 iterations; independent sampling per iteration.*

---

## Table 7. The comparison at a glance — producing 2.62 TWh yr⁻¹ (Phase-2, ~1 GW).

| | Conventional (fossil-thermal mix) | Offshore wind (Saros) |
|---|---|---|
| Annual electricity | 2.62 TWh | 2.62 TWh |
| CO₂ emitted | **1.98 Mt yr⁻¹** | **0.029 Mt yr⁻¹** |
| — of which lignite | 0.89 Mt | — |
| — of which imported coal | 0.70 Mt | — |
| — of which natural gas | 0.39 Mt | — |
| Emission intensity | ~757 g CO₂/kWh (mix) | 11 g CO₂/kWh (life-cycle) |
| Carbon ratio | ≈69× higher | 1× |
| Fuel import dependence | High (gas + imported coal) | None (domestic resource) |
| **Avoided CO₂ (combined margin)** | — | **1.52 Mt yr⁻¹** [1.27–1.75] |
| Avoided CO₂ (fossil displacement) | — | 1.95 Mt yr⁻¹ (upper bound) |
| Tangible equivalent | — | ≈0.76 M cars; ≈0.86 M households |

*Fuel emission factors: official ETKB/EVÇED 2023 (405/803/1133 g/kWh). Offshore
life-cycle: Bonou et al. (2016). Avoided values from the Monte Carlo (P50, P10–P90).*
