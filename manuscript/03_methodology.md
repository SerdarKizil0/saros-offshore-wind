# 3. Materials and Methods

## 3.1. Study Site

The study site is the Saros Bay offshore wind candidate zone, one of four
offshore renewable energy zones (*Deniz Üstü Yenilenebilir Enerji Kaynak
Alanları*, DÜRES) announced by the Republic of Türkiye Ministry of Energy
and Natural Resources (MENR) on 14 May 2026. The zone is located in the
North Aegean Sea, immediately north of the Gelibolu (Gallipoli) Peninsula,
at the western approach to the Çanakkale Strait. Its boundary, supplied by
MENR as a georeferenced polygon, comprises 27 vertices enclosing an area of
172.5 km², with a centroid at 40.557° N, 26.198° E. The zone extends
approximately 35.7 km east–west and 10.5 km north–south, forming an
elongated corridor parallel to the peninsular coastline.

The site lies within a region repeatedly identified as having among the
highest offshore wind potential along the Turkish coastline, and is
consistent with the exploration areas highlighted in the World Bank's
*Offshore Wind Roadmap for Türkiye* (World Bank, 2024). Whereas the
Roadmap provides strategic, country-level policy guidance toward Türkiye's
2035 offshore wind target of 5 GW, the present study provides a
quantitative, site-specific resource and environmental assessment for the
Saros zone under the technical configuration described below.

## 3.2. Wind Data: ERA5 Reanalysis

Hourly wind data were obtained from the ERA5 reanalysis produced by the
European Centre for Medium-Range Weather Forecasts (ECMWF) and distributed
through the Copernicus Climate Data Store (Hersbach et al., 2020). ERA5
provides global coverage at a native horizontal resolution of 0.25° × 0.25°
(approximately 28 km at this latitude) with hourly temporal resolution.
The eastward and northward wind components were retrieved at both 10 m
(*u₁₀*, *v₁₀*) and 100 m (*u₁₀₀*, *v₁₀₀*) above the surface for the
11-year period 2014–2024, yielding 96 432 hourly records.

An 11-year analysis window was adopted to capture inter-annual variability,
which in the Mediterranean and Aegean basins is of the order of 5–8% in
mean wind speed (Soukissian et al., 2018). At this sample size the standard
error of the long-term mean falls below 2%, mitigating the sampling bias
that affects single-year assessments. Data were requested over a bounding
box (40.45–40.65° N, 25.99–26.51° E) that encloses the candidate-zone
polygon with an approximately 5 km buffer, ensuring that interior grid
cells are well inside the requested domain on all sides. The grid cell
nearest the polygon centroid was selected for the point analysis. No
missing or invalid records were present in the retrieved series.

The horizontal wind speed at each reference height was computed as the
magnitude of the vector components,

$$ U_h = \sqrt{u_h^2 + v_h^2}, $$

and the meteorological wind direction was derived from the 100 m
components.

## 3.3. Hub-Height Extrapolation

The reference turbine (Section 3.5) has a hub height of 105 m, which lies
above the ERA5 100 m level. Wind speed was extrapolated from 100 m to the
hub height using the power-law (Hellmann) profile,

$$ U(z) = U(z_\mathrm{ref}) \left( \frac{z}{z_\mathrm{ref}} \right)^{\alpha}, $$

where *α* is the wind-shear exponent. Rather than assuming the open-sea
literature value of *α* = 0.10, the shear exponent was estimated directly
from the data on an hour-by-hour basis from the ratio of the 10 m and
100 m wind speeds,

$$ \alpha = \frac{\ln\!\left(U_{100}/U_{10}\right)}{\ln\!\left(100/10\right)}, $$

restricted to hours in which both speeds exceeded 1 m s⁻¹ and trimmed at
the 1st and 99th percentiles to suppress ratio noise. The resulting mean
shear exponent was *α* = 0.149 (median 0.142, standard deviation 0.054;
5th–95th percentile range 0.074–0.252). This value exceeds the canonical
open-sea figure, reflecting the partly coastal character of the site owing
to the proximity of the Gelibolu Peninsula, and its use in place of an
assumed constant is a deliberate methodological refinement. The
extrapolation from 100 m to 105 m is small in magnitude and therefore
robust to the residual uncertainty in *α*, which is nonetheless propagated
implicitly through the resource statistics.

## 3.4. Weibull Distribution

The probability distribution of hub-height wind speed was characterised by
the two-parameter Weibull distribution, which is standard in wind resource
assessment. Its probability density function is

$$ f(U) = \frac{k}{c}\left(\frac{U}{c}\right)^{k-1}
          \exp\!\left[-\left(\frac{U}{c}\right)^{k}\right], $$

where *k* is the dimensionless shape parameter and *c* (m s⁻¹) is the
scale parameter. Parameters were estimated by maximum-likelihood
estimation (MLE) with the location fixed at zero, and cross-checked against
the method of moments. For the full 11-year hub-height series the MLE
yielded *k* = 2.04 and *c* = 8.08 m s⁻¹, in close agreement with the
method-of-moments estimate (*k* = 2.08, *c* = 8.10 m s⁻¹). Goodness of fit
was excellent, with a coefficient of determination of *R²* = 0.998 on the
cumulative distribution and a Kolmogorov–Smirnov statistic of 0.022. The
Weibull-implied mean wind speed (7.16 m s⁻¹) reproduced the empirical mean
(7.17 m s⁻¹) to within 0.2%, and the mean wind power density agreed to
within 1% (422 versus 417 W m⁻²).

## 3.5. Energy Production Model

The reference wind turbine was the Vestas V164-9.5 MW, a fixed-bottom
offshore machine with a 164 m rotor diameter and a 105 m hub height, widely
adopted as a reference in peer-reviewed Aegean and Mediterranean offshore
wind assessments. Its manufacturer power curve defines a cut-in wind speed
of 3.5 m s⁻¹, rated power of 9.5 MW at 14 m s⁻¹, and cut-out at 25 m s⁻¹.

Gross annual energy production (AEP) per turbine was computed by convolving
the turbine power curve *P(U)* with the fitted Weibull density,

$$ \mathrm{AEP}_\mathrm{gross} = 8766 \int_{0}^{\infty} P(U)\, f(U)\, \mathrm{d}U, $$

where 8766 is the mean number of hours per year. The integral was evaluated
numerically on a 0.1 m s⁻¹ wind-speed grid using the interpolated power
curve. The gross capacity factor was obtained as the ratio of mean power
output to rated power.

Net AEP was obtained by applying three multiplicative loss factors: an
array (wake) loss, turbine availability, and electrical (array plus export
cable plus transformer) losses,

$$ \mathrm{AEP}_\mathrm{net} = \mathrm{AEP}_\mathrm{gross}
   \,(1 - L_\mathrm{wake})\, A \,(1 - L_\mathrm{elec}), $$

with default values of *L*~wake~ = 0.08, *A* = 0.95 and *L*~elec~ = 0.03.
The deterministic net specific yield was 2.71 GWh yr⁻¹ MW⁻¹, corresponding
to a net capacity factor of 31.0% and 2714 equivalent full-load hours per
year.

## 3.6. Capacity Scenarios

Because the installed capacity ultimately allocated to the Saros zone is
not yet finalised — and because domestic-content requirements may influence
the turbine specification — all primary results are reported per megawatt
of installed capacity, a normalisation that is robust to capacity
uncertainty and consistent with the convention in life-cycle offshore wind
literature. For context, four illustrative deployment scenarios were also
evaluated, derived from a regular 7*D* × 5*D* turbine spacing (where *D* is
the rotor diameter) applied to the zone area: a pilot phase (26 turbines,
247 MW), a first-allocation phase (53 turbines, 504 MW), a full Phase-2
deployment (105 turbines, 998 MW), and a theoretical maximum
(183 turbines, 1739 MW). The model is linear in installed capacity at fixed
turbine specification, so farm-level quantities scale directly from the
per-MW results.

## 3.7. Avoided-Emissions Model

The environmental benefit of the wind farm was quantified as the net carbon
dioxide emission avoided by displacing conventional grid electricity. The
net avoided emission per unit of wind generation is

$$ E_\mathrm{avoided} = \mathrm{EF}_\mathrm{grid} - \mathrm{EF}_\mathrm{wind}, $$

where EF~grid~ is the grid emission factor displaced by wind generation and
EF~wind~ is the life-cycle emission factor of the offshore wind farm
itself.

For EF~grid~, the official combined-margin emission factor for wind and
solar plants published by the Turkish Ministry of Energy and Natural
Resources (ETKB, Energy Efficiency and Environment Directorate) for 2023
was adopted as the primary value: 624.2 gCO₂-eq kWh⁻¹, computed according
to the IPCC grid emission-factor methodology (Tool07). This combined-margin
value is the officially sanctioned factor for crediting avoided emissions
from new wind and solar generation in Türkiye, and its use removes the
ambiguity associated with selecting between operating-margin and
build-margin conventions. The official generation-average factor
(434 gCO₂-eq kWh⁻¹) and operating-margin factor (713.4 gCO₂-eq kWh⁻¹) for
the same year were used as the lower and upper bounds, respectively, in the
uncertainty analysis.

For EF~wind~, the life-cycle emission factor of fixed-bottom offshore wind
was taken as 11 gCO₂-eq kWh⁻¹ (Bonou et al., 2016), consistent with the
8–14 gCO₂-eq kWh⁻¹ range reported for offshore wind in the IPCC AR5 inventory (Schlömer et al., 2014). This value
includes manufacturing, installation, operation and decommissioning without
recycling credits, and is therefore a conservative (upper) estimate of the
technology's footprint.

To complement the combined-margin accounting with a more concrete
comparison, a fuel-resolved conventional scenario was also constructed, in
which the same annual generation is assumed to be produced by a
fossil-thermal mix. The fossil component was apportioned among natural gas,
imported coal and lignite using the official 2023 fuel-specific emission
factors (405, 803 and 1133 gCO₂-eq kWh⁻¹, respectively) weighted by an
approximate fossil-thermal generation share. This scenario yields a
fossil-displacement avoided emission that is reported as an upper bound
alongside the combined-margin headline value. Finally, to aid
interpretation, results were converted to tangible equivalents using a mean
Turkish household consumption of 3036 kWh yr⁻¹ (TEİAŞ) and a mean passenger
vehicle emission of 2 tCO₂ yr⁻¹.

## 3.8. Monte Carlo Uncertainty Quantification

Uncertainty in the energy and emission estimates was propagated through a
Monte Carlo simulation of 10 000 iterations. Seven input parameters were
sampled independently in each iteration: the Weibull shape parameter
(*k* ~ Normal(2.04, 0.04)); the Weibull scale parameter (*c* ~
Normal(8.08, 0.26), with the standard deviation set equal to the
inter-annual standard deviation of the eleven annual scale-parameter fits);
the array wake loss (Triangular(0.05, 0.08, 0.12)); turbine availability
(Triangular(0.92, 0.95, 0.97)); electrical loss (Triangular(0.02, 0.03,
0.04)); the grid emission factor (Triangular(434, 624.2, 713.4) gCO₂-eq
kWh⁻¹, spanning the official generation-average, combined-margin and
operating-margin values); and the offshore wind life-cycle emission factor
(Triangular(8, 11, 14) gCO₂-eq kWh⁻¹).

In each iteration the gross AEP was recomputed analytically from the sampled
Weibull parameters, net losses were applied, and the wind generation was
converted to avoided emissions using the sampled net emission factor.
Results are reported as the 10th, 50th and 90th percentiles (P10, P50, P90)
of the resulting distributions for specific yield, capacity factor and
avoided emissions, both per megawatt and aggregated to each deployment
scenario.

---

### References cited in this section (to be formatted to journal style)

- Bonou, A., Laurent, A., Olsen, S.I. (2016). Life cycle assessment of
  onshore and offshore wind energy — from theory to application. *Applied
  Energy*, 180, 327–337.
- Hersbach, H., et al. (2020). The ERA5 global reanalysis. *Quarterly
  Journal of the Royal Meteorological Society*, 146(730), 1999–2049.
- IPCC (2025). [Life-cycle emissions of electricity generation
  technologies — offshore wind range 8–14 gCO₂-eq kWh⁻¹.] *to be cited from
  the relevant AR6/2025 working-group annex.*
- Republic of Türkiye Ministry of Energy and Natural Resources, Energy
  Efficiency and Environment Directorate (EVÇED) (2024). *Türkiye Ulusal
  Elektrik Şebekesi Emisyon Faktörü Bilgi Formu (2023)*.
- Soukissian, T., et al. (2017). [Offshore wind climate and variability in
  the Mediterranean basin.] *to be confirmed.*
- World Bank (2024). *Offshore Wind Roadmap for Türkiye*. Energy Sector
  Management Assistance Program (ESMAP), Washington, DC.

*Note: ERA5 citation (Hersbach et al., 2020) and the offshore-LCA source
(Bonou et al., 2016) are verified. The IPCC 2025 range and the Soukissian
inter-annual-variability figure should be located precisely and cited to a
specific page/table before submission.*
