# 4. Results

## 4.1. Wind Resource

The 11-year ERA5 record (2014–2024) at the Saros candidate-zone centroid
yields a mean hub-height (105 m) wind speed of 7.17 m s⁻¹, with a standard
deviation of 3.66 m s⁻¹ and a median of 6.96 m s⁻¹ (Figure F_wind_resource).
The distribution is well represented by a two-parameter Weibull function
with shape parameter *k* = 2.04 and scale parameter *c* = 8.08 m s⁻¹; the
fit reproduces the empirical cumulative distribution with a coefficient of
determination of 0.998 and a Kolmogorov–Smirnov statistic of 0.022
(Figure F_wind_resource a, b). The corresponding mean wind power density is
422 W m⁻². These values place the Saros zone in a moderate-to-good offshore
wind class, above the threshold generally regarded as economically viable
for offshore development and consistent with the qualitative characterisation
of the North Aegean as among the most favourable Turkish offshore regions.

The wind regime exhibits a pronounced winter maximum. Mean monthly wind
speed peaks in February (8.42 m s⁻¹) and January (8.24 m s⁻¹) and reaches
its minimum in June (5.62 m s⁻¹), with a secondary rise in late summer
(7.55 m s⁻¹ in August) (Figure F_wind_resource c). This winter-dominant
seasonality is favourable from a system-integration perspective, since it
coincides with the seasonal peak in Turkish electricity demand driven by
winter heating loads.

Inter-annual variability is low. Annual mean hub-height wind speed ranged
from 6.55 m s⁻¹ (2014) to 7.41 m s⁻¹ (2016) over the eleven years, with a
coefficient of variation of only 3.2% (Figure F_wind_resource d). This
stability strengthens the reliability of the long-term resource estimate
and reduces the financial risk associated with year-to-year production
variability. The measured power-law shear exponent (*α* = 0.149) is higher
than the canonical open-sea value of 0.10, a difference attributable to the
partly coastal setting of the zone adjacent to the Gelibolu Peninsula;
using the measured rather than an assumed exponent removes a potential
source of systematic bias in the hub-height extrapolation.

The directional distribution of the resource is strongly anisotropic
(Figure F3). Winds from the northeast and east-northeast dominate, together
accounting for approximately 44% of all hours, with the single
north-easterly sector alone contributing about 26%. This pronounced
directional concentration reflects the funnelling of northerly Thracian
flow along the axis of the gulf toward the Çanakkale Strait. The strong
prevailing direction is advantageous for turbine micro-siting, since rows
can be oriented to minimise array wake losses by maximising spacing along
the dominant northeast–southwest axis.

## 4.2. Energy Production

Convolution of the fitted Weibull distribution with the Vestas V164-9.5 MW
power curve gives a gross annual energy production of 30.4 GWh yr⁻¹ per
turbine, corresponding to a gross capacity factor of 36.5%. After applying
array wake (8%), availability (95%) and electrical (3%) losses, the net
annual energy production is 25.8 GWh yr⁻¹ per turbine, a net capacity
factor of 31.0%, and 2714 equivalent full-load hours per year. Expressed
per unit of installed capacity — the primary normalisation adopted here —
the deterministic net specific yield is 2.71 GWh yr⁻¹ MW⁻¹.

These figures are competitive for a Mediterranean-basin offshore site. The
net capacity factor of approximately 31% is lower than that of North Sea
sites (typically 40–50%) but compares favourably with other Aegean and
eastern Mediterranean assessments, reflecting the moderate mean wind speed
of the basin.

## 4.3. Uncertainty Quantification

The Monte Carlo simulation (10 000 iterations, seven sampled inputs)
produces approximately normal output distributions for all three primary
metrics (Figure F_monte_carlo a–c). The net specific yield has a median
(P50) of 2.62 GWh yr⁻¹ MW⁻¹ with a 10th-to-90th-percentile range of
2.41–2.83 GWh yr⁻¹ MW⁻¹; the net capacity factor has a P50 of 29.9%
(P10–P90: 27.5–32.3%); and the avoided carbon dioxide emission has a P50 of
1525 tCO₂ yr⁻¹ MW⁻¹ (P10–P90: 1277–1754 tCO₂ yr⁻¹ MW⁻¹). The coefficient of
variation of the specific-yield distribution is 6.3%, indicating that the
combined parametric uncertainty in the energy estimate is modest.

The Monte Carlo median specific yield (2.62 GWh yr⁻¹ MW⁻¹) is marginally
lower than the deterministic value (2.71 GWh yr⁻¹ MW⁻¹). This small
difference arises because the deterministic calculation integrates the
turbine power curve directly against the full empirical wind-speed
distribution, whereas the Monte Carlo integrates against the fitted Weibull
density, which slightly under-represents the high-wind-speed tail that
contributes disproportionately to energy capture. Both values are reported
for transparency; the Monte Carlo percentiles are preferred for inference
because they carry the full uncertainty information.

## 4.4. Avoided Emissions and National Context

Using the official Turkish combined-margin grid emission factor for wind
and solar (624.2 gCO₂-eq kWh⁻¹) net of the offshore wind life-cycle factor
(11 gCO₂-eq kWh⁻¹), each megawatt of installed Saros capacity avoids a
median of 1525 tCO₂ yr⁻¹ (P10–P90: 1277–1754). The wind farm's own
life-cycle emission represents under 2% of the displaced grid emission,
confirming that the technology is overwhelmingly carbon-positive in the
Turkish grid context.

Aggregated to the four deployment scenarios (Figure F_monte_carlo d), the
median annual generation and avoided emissions are: 0.65 TWh yr⁻¹ and
0.38 Mt CO₂ yr⁻¹ for the pilot phase (247 MW); 1.32 TWh yr⁻¹ and
0.77 Mt CO₂ yr⁻¹ for the first-allocation phase (504 MW); 2.62 TWh yr⁻¹ and
1.52 Mt CO₂ yr⁻¹ for the full Phase-2 deployment (998 MW); and 4.56 TWh yr⁻¹
and 2.65 Mt CO₂ yr⁻¹ for the theoretical maximum (1739 MW).

To place these magnitudes in context, the full Phase-2 deployment
(approximately 1 GW) would generate the equivalent of 0.8% of Türkiye's
2024 national electricity consumption (347.9 TWh) from a single offshore
zone, while its installed capacity corresponds to 20% of the national 2035
offshore wind target of 5 GW. Equivalently, were the entire 5 GW target met
by capacity of the Saros class, it would generate a median of approximately
13.1 TWh yr⁻¹, or 3.8% of current national demand. These results indicate
that the Saros zone alone can make a material contribution to Türkiye's
offshore wind ambitions while displacing a quantitatively significant
volume of grid carbon emissions.

## 4.5. Offshore Wind versus Conventional Generation

The environmental advantage of the offshore option is made explicit by
contrasting the carbon burden of the same annual generation produced
conventionally versus by wind (Figure F7). Producing the Phase-2 output of
2.62 TWh yr⁻¹ from a fossil-thermal generation mix — apportioned using the
official 2023 fuel-specific emission factors of 405, 803 and 1133 gCO₂-eq
kWh⁻¹ for natural gas, imported coal and lignite respectively — would emit
approximately 1.98 Mt CO₂ yr⁻¹, of which lignite contributes the largest
share (0.89 Mt), followed by imported coal (0.70 Mt) and natural gas
(0.39 Mt) (Figure F7a). The same generation from offshore wind carries a
life-cycle burden of only 0.029 Mt CO₂ yr⁻¹ — under 2% of the conventional
figure — so that the technology is, for practical purposes, emission-free
relative to the supply it displaces.

The corresponding avoided emission depends on the accounting convention
adopted (Figure F7b). Using the official combined-margin factor, which is
the value sanctioned for crediting renewable displacement in Türkiye, the
Phase-2 deployment avoids a median of 1.52 Mt CO₂ yr⁻¹ (P10–P90:
1.27–1.75). Under the alternative assumption that wind displaces purely
fossil-thermal generation, the avoided emission rises to 1.95 Mt CO₂ yr⁻¹.
The combined-margin value is adopted as the headline figure throughout this
study because it is the officially mandated convention and is the more
conservative of the two; the fossil-displacement value is reported as an
upper bound.

## 4.6. Tangible Equivalents

To render these magnitudes intuitive, the results are expressed in terms of
households supplied and passenger cars displaced (Figure F8). At the Phase-2
scale, the annual generation is equivalent to the electricity consumption of
approximately 0.86 million Turkish households (at 3036 kWh per household per
year), and the avoided emissions correspond to removing approximately 0.76
million average passenger cars from the road (at 2 tCO₂ per car per year).
Across the scenario range these equivalents span 0.21–1.50 million
households and 0.19–1.33 million car-equivalents, from the pilot phase to
the theoretical maximum (Figure F8).

---

*Figures referenced: F1 (study-area map), F2 (workflow), F3 (wind rose),
F4 (wind resource), F6 (uncertainty and scenarios), F7 (offshore vs
conventional), F8 (tangible equivalents). Figure numbering is provisional
and will be consolidated at submission.*
