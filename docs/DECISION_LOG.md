# Decision Log — Saros OWF

Rationale behind the main scientific choices, for reviewers and reuse.

## Wind resource
- **ERA5, 2014–2024 (11 yr).** Captures inter-annual variability; standard
  error of the long-term mean < 2%. No offshore mast exists in Turkish waters.
- **Centroid grid cell.** ERA5 native resolution (~28 km) is comparable to the
  zone's east–west extent; intra-zone gradients are not resolved (a stated limitation).
- **Measured shear α = 0.149.** Computed hour-by-hour from the 10 m/100 m ratio,
  rather than assuming the open-sea 0.10. Higher value reflects the partly
  coastal setting near the Gelibolu Peninsula.
- **Weibull by MLE** (k=2.04, c=8.08), cross-checked vs method of moments;
  R²=0.998, KS=0.022.

## Energy
- **Vestas V164-9.5 MW** reference turbine (common in Aegean/Med literature).
- **Losses:** wake 8%, availability 95%, electrical 3% (sampled in MC).
- **Per-MW primary reporting.** Installed capacity not yet finalised; per-MW is
  robust and linear. Scenarios S1–S4 (247/504/998/1739 MW) for context.

## Emissions
- **Grid factor: official combined margin 624.2 gCO₂-eq/kWh** (ETKB/EVÇED 2023,
  IPCC Tool07) as primary — the value mandated for renewable-displacement
  crediting in Türkiye. Generation-average (434) and operating-margin (713.4)
  used as MC lower/upper bounds.
- **Offshore LCA 11 g/kWh** (Bonou et al. 2016; within IPCC AR5 8–35 range),
  subtracted from grid factor for net avoided emission.
- **Fuel-resolved scenario** (gas 405, imported coal 803, lignite 1133 g/kWh)
  gives an illustrative fossil-displacement upper bound (1.95 Mt) alongside the
  combined-margin headline (1.52 Mt).
- **CO₂ only.** No NOx/SO₂/water metrics (kept scope tight, data official).
- **Istanbul context dropped** (no official province-level data); national
  totals used (347.9 TWh, 2024).

## Out of scope (stated limitations)
Seismic/geotechnical design (Ganos fault), explicit wake/layout modelling,
bathymetry-resolved buildable area, in-situ validation, techno-economics.
