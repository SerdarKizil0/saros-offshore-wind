<!-- GENERATED FILE - do not edit. Source: manuscript/src/03_methodology.md. Numbers come from results/revised/. Rebuild with: python scripts/11_build_manuscript_sections.py -->

# 3. Materials and Methods

## 3.1. Scope and kinds of quantity

This is a preliminary assessment based on reanalysis data. No offshore wind
measurements were available for the area, so no result is validated against
measurements. To keep the status of each number clear, four kinds of quantity
are distinguished throughout:

- **reanalysis output**: wind statistics of the ERA5 series at a grid node;
- **model results**: capacity factors and energy yields obtained from that
  series with a reference power curve and assumed losses;
- **sensitivity experiments**: recalculations in which one choice is changed
  (reference period, grid node, wind data product, loss assumptions);
- **assumptions**: the reference turbine, its power curve, the losses and the
  emission-factor convention.

Only one probabilistic interval is reported: the sampling interval of the
long-term mean (Section 3.6). The sensitivity experiments are reported
separately. They are not confidence intervals, and they are not combined with
the sampling interval or with each other.

All results are produced by a scripted pipeline from input files that are
pinned by checksum. A clean checkout of the repository reproduces the result
files byte for byte, and the numbers and tables in Sections 2 to 4 are
generated from those result files.

## 3.2. Wind data

The wind data are from the ERA5 reanalysis (Hersbach et al., 2020), which
provides hourly fields on a 0.25° grid. The variables used are the wind speed
at 10 m and at 100 m and the wind direction at 100 m, as instantaneous values
at each hour (UTC). The series was obtained through the Open-Meteo
historical-weather service (Zippenfenig, 2023), with the ERA5 model selected
and the nearest grid cell requested. The service returned exactly the node at
40.50° N, 26.25° E (Section 2.6).

The reference period is 1 January 1994 to 31 December 2024: 31 calendar years
and 271 752 hourly values, without gaps. The series was retrieved on 14
November 2026 and is stored with its checksum. A long reference period was
used because the result depends on the period chosen (Section 4.3).

Open-Meteo redistributes ERA5 on its native grid but stores it in compressed
form, and it returns speeds to two decimals and directions to whole degrees.
The series is therefore not bit-identical to a download from the Copernicus
Climate Data Store (CDS). As an input check, it was compared with a series for
the same node that had been downloaded from the CDS for 2014–2024 (96 432
common hours). The mean difference in 100 m wind speed is −0.00009 m s⁻¹, the
root-mean-square difference is 0.041 m s⁻¹ and the correlation is 0.99994.
With the same shear exponent, the gross capacity factor of the two series
differs by −0.004 % (Supplementary Table S2). This comparison checks the data
source. It does not test the accuracy of ERA5 at the site.

## 3.3. Wind speed at hub height

The reference turbine has a hub height of 105 m. The 100 m wind speed was
extrapolated to 105 m with a power law. For every hour $t$ in which both the
10 m speed $U_{10,t}$ and the 100 m speed $U_{100,t}$ exceed 1 m s⁻¹, a shear
exponent was computed from the two reanalysis levels,

$$ \alpha_t = \frac{\ln\left(U_{100,t}/U_{10,t}\right)}{\ln\left(100/10\right)} . \qquad (1) $$

The values were trimmed at their 1st and 99th percentiles, and their mean
$\bar{\alpha}$ was applied to all hours:

$$ U_{\mathrm{hub},t} = U_{100,t}\left(\frac{105}{100}\right)^{\bar{\alpha}} . \qquad (2) $$

For the primary series $\bar{\alpha}$ = 0.149. This exponent is derived from
two levels of the reanalysis. It is not a measured shear. Because the
extrapolation spans only 5 m, its influence is small: compared with an
exponent of 0.10, it changes the 105 m wind speed by +0.24 %.

## 3.4. Reference turbine and power curve

The reference turbine is the Vestas V164-9.5 MW: rated power 9.5 MW, rotor
diameter 164 m, cut-in wind speed 3.5 m s⁻¹, rated wind speed 14 m s⁻¹ and
cut-out wind speed 25 m s⁻¹. The hub height of 105 m is an assumption. The
turbine serves as a documented reference machine. It is not a design proposal
for the area.

The power curve $P(U)$ is the row "V164/9500" of the Open Energy Database
turbine library distributed with windpowerlib. It is a third-party
digitisation of a power-curve graph published by the manufacturer, given at 49
points from 0 to 24.5 m s⁻¹. It is not a manufacturer-certified power curve,
and the air density to which it refers is not documented (1.225 kg m⁻³ is
assumed). The curve was interpolated linearly. Power was set to zero below the
cut-in speed and at or above the cut-out speed. The curve was applied to the
hourly reanalysis values without corrections for air density or for
variability within the hour.

## 3.5. Energy yield

Energy was estimated by converting every hourly wind speed to power and
summing. With $N$ hours and rated power $P_r$, the gross capacity factor is

$$ \mathrm{CF}_g = \frac{1}{N\,P_r}\sum_{t=1}^{N} P\left(U_{\mathrm{hub},t}\right) . \qquad (3) $$

The net capacity factor applies three loss assumptions, a wake loss $L_w$, an
availability $A$ and an electrical loss $L_e$:

$$ \mathrm{CF}_n = \eta\,\mathrm{CF}_g , \qquad \eta = (1-L_w)\,A\,(1-L_e) . \qquad (4) $$

The nominal values are $L_w$ = 8 %, $A$ = 95 % and $L_e$ = 3 %, which give
$\eta$ = 0.848. These values are illustrative assumptions. They are not
derived from a turbine layout or from site data, and no wake model was run.
The net specific yield per unit of installed capacity is

$$ Y = \mathrm{CF}_n \times H , \qquad (5) $$

where $H$ = 8 766 h is the length of an average year. $Y$ is expressed in GWh
MW⁻¹ yr⁻¹. Results are reported per megawatt because no installed capacity has
been assigned to the area (Section 2.2).

## 3.6. Sampling interval of the mean and interannual variability

The long-term estimate is the mean over 31 calendar years. Its finite-sample
uncertainty was described by a sampling interval: a two-sided 90 % confidence
interval of the mean, computed from the $n$ = 31 annual yields $Y_i$ and their
standard deviation $s_Y$:

$$ \bar{Y} \pm t_{0.95,\,n-1}\,\frac{s_Y}{\sqrt{n}} . \qquad (6) $$

This sampling interval was checked with a bootstrap that resamples whole
calendar years (20 000 resamples) and with a jackknife standard error
(Supplementary Table S4). The interval has a narrow meaning. It describes how
well 31 reanalysis years determine their own long-term mean, on the condition
that ERA5 at this node is correct. It is not an exceedance value such as a P90
yield, and it does not include any of the sensitivities described in Section
3.7.

Interannual variability is reported separately, as the coefficient of
variation and the range of the annual yields. It describes how much single
reanalysis years differ from one another. It is not an uncertainty of the
mean.

## 3.7. Sensitivity experiments

Each experiment changes one choice and repeats the calculation of Sections 3.3
to 3.5. Its result is expressed relative to the primary estimate
$Y_{\mathrm{ref}}$:

$$ \Delta = \left(\frac{Y}{Y_{\mathrm{ref}}} - 1\right)\times 100\,\% . \qquad (7) $$

**Period selection.** The calculation was repeated for other reference periods
at the primary node, using a longer series from the same source (1979–2024).
Over 1994–2024 that series is identical to the primary series. The primary
$\bar{\alpha}$ was kept, so that only the wind changes. The comparison periods
are 1979–2024, 2014–2024, 2015–2024 and 2008–2017; the last is the reference
period of the wind atlas used below. In addition, the yield was computed for
every window of 11 consecutive years: 36 windows in 1979–2024, of which 21 lie
inside 1994–2024. The window length of eleven years is that of the 2014–2024
record with which this work began. Overlapping windows share years and are not
independent samples.

**Grid node.** The calculation was repeated for the two neighbouring ERA5
nodes on the same latitude row, at 26.00° E and 26.50° E, for the same period
and with the same method. Each node uses its own $\bar{\alpha}$. The land
fraction of each cell was read from the static ERA5 land–sea mask. The nodes
were not averaged or interpolated: the three cells differ in their land
fraction, and there is no measurement that would justify a weighting.

**Wind data product.** The ERA5 mean wind speed at 100 m was compared with the
Global Wind Atlas 4.0 (GWA; Davis et al., 2023). GWA is a downscaling product:
a mesoscale model driven by ERA5, followed by microscale modelling, on a grid
of about 250 m. The GWA climatology refers to 2008–2017. GWA values were
averaged over the pixel centres inside the candidate polygon and, for each of
the three nodes, over the sea pixels of a 0.25° box centred on the node. Each
GWA value was compared with the ERA5 mean of two periods: the primary period
and 2008–2017, so that the periods of the two products match. The comparison
measures the disagreement between two models. GWA is not independent of ERA5
and is not treated as a reference truth. To show what such a disagreement
means for energy, every hourly speed of the primary series was multiplied by a
factor (0.90, 0.95, 1.05, 1.10 and the GWA/ERA5 ratios) and the conversion was
repeated. These scaled cases are illustrative. None is adopted, and the
primary estimate is not rescaled.

**Loss assumptions.** A low-loss case ($L_w$ = 5 %, $A$ = 97 %, $L_e$ = 2 %)
and a high-loss case ($L_w$ = 12 %, $A$ = 92 %, $L_e$ = 4 %) were computed.
They are labelled assumptions, not probability bounds.

## 3.8. First-order site screening

Two spatial layers were overlaid on the polygon. Water depth was summarised
from the EMODnet grid cells inside the polygon (Section 2.3). The overlap with
the Saros Körfezi ÖÇK was computed on a 50 m grid from the boundary
reconstructed in Section 2.4. Both are first-order screening results. They do
not constitute a layout, a constraint map or an environmental impact
assessment, and no permitting judgement is made.

## 3.9. Operational grid-CO₂ accounting

The energy yield was also expressed as an operational grid-CO₂ accounting
equivalent,

$$ C = Y \times \mathrm{EF}_{\mathrm{CM}} , \qquad (8) $$

where $\mathrm{EF}_{\mathrm{CM}}$ = 0.6242 tCO₂ MWh⁻¹ is the combined-margin
emission factor for wind and solar plants that MENR published for 2023 (MENR,
2025). It follows the grid emission-factor tool of the Clean Development
Mechanism (UNFCCC, 2018), in which the combined margin for wind and solar is
0.75 times the operating margin plus 0.25 times the build margin. The factor
covers CO₂ from combustion only. For context, the same calculation was made
with the official operating margin (0.7134 tCO₂ MWh⁻¹), build margin (0.3567
tCO₂ MWh⁻¹) and generation average (0.430 tCO₂ MWh⁻¹).

$C$ is an accounting quantity under a stated convention. It uses a static 2023
factor. It is not a forecast of the generation that the plant would physically
displace, and the alternative conventions are not statistical bounds. Where an
interval is attached to $C$, it carries only the sampling interval of the mean
energy through the fixed factor. Life-cycle greenhouse-gas intensities from
the literature are in a different unit (CO₂-equivalent) and have a different
system boundary. They are reported separately in Supplementary Table S14 and
are not subtracted from $C$.

For orientation, the per-megawatt results are also scaled linearly to one
illustrative capacity of 105 turbines of 9.5 MW (997.5 MW). This size is
comparable to the 1 000 MWe of the draft tender, but that capacity has not
been allocated to Saros (Section 2.2), so the case is conditional on a future
allocation. It involves no layout and uses the same nominal losses as the
per-megawatt result.

## 3.10. Supplementary descriptive statistics

A two-parameter Weibull distribution was fitted to the hourly 105 m wind speed
by maximum likelihood. It is reported as a descriptive statistic
(Supplementary Table S7) and is not used to estimate energy. Monthly means and
the direction distribution are given in Supplementary Tables S8 and S9.
