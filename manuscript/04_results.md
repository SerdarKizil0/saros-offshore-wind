<!-- GENERATED FILE - do not edit. Source: manuscript/src/04_results.md. Numbers come from results/revised/. Rebuild with: python scripts/11_build_manuscript_sections.py -->

# 4. Results

## 4.1. Long-term wind resource and specific energy yield

Over 1994–2024 the ERA5 series at the primary node has a mean wind speed of
7.01 m s⁻¹ at 100 m. Extrapolated to the 105 m hub height, the mean is 7.06 m
s⁻¹, the standard deviation 3.69 m s⁻¹ and the median 6.80 m s⁻¹ (Table 1).
The mean wind power density at 105 m is 409 W m⁻² for an air density of 1.225
kg m⁻³. These are statistics of reanalysis output, not of measurements.

The monthly mean wind speed is highest in December (8.30 m s⁻¹) and lowest in
June (5.51 m s⁻¹) (Supplementary Table S8). North-easterly winds dominate. The
north-east and east-north-east sectors account for 26 % and 18 % of the hours,
and the north-east sector alone carries 33 % of the gross energy
(Supplementary Table S9).

Converting the hourly series with the reference power curve gives a gross
capacity factor of 31.67 %. With the nominal loss assumptions the net capacity
factor is 26.85 % and the net specific yield is **2.354 GWh MW⁻¹ yr⁻¹**, or 2
354 full-load hours per year. For one 9.5 MW turbine this corresponds to 26.38
GWh yr⁻¹ gross and 22.36 GWh yr⁻¹ net. This is the primary estimate of the
study. It is a model result. It depends on ERA5 at one grid node, on a
third-party digitised power curve and on assumed losses, and it is not
validated against offshore measurements.

## 4.2. Sampling uncertainty and interannual variability

The 90 % sampling interval of the mean net yield is 2.300–2.407 GWh MW⁻¹ yr⁻¹,
that is ±2.3 % of the mean (Eq. 6). The bootstrap check gives 2.302–2.403 GWh
MW⁻¹ yr⁻¹, and the standard error of the mean is 1.3 % (Supplementary Table
S4). This is the only probabilistic interval in the study. It is conditional
on the reanalysis at this node and says nothing about the accuracy of the
reanalysis itself.

Single years vary much more than the mean is uncertain (Fig. 2a). The
coefficient of variation of the annual net yield is 7.4 %. The lowest year is
2002 (1.944 GWh MW⁻¹ yr⁻¹, −17.4 % relative to the mean) and the highest is
2001 (2.674 GWh MW⁻¹ yr⁻¹, +13.6 %). The second-lowest year is 2014 (1.992 GWh
MW⁻¹ yr⁻¹, −15.4 %). The annual values show no appreciable serial correlation
(lag-1 coefficient −0.08). All annual values are listed in Supplementary Table
S3.

## 4.3. Period-selection sensitivity

The estimate depends on the reference period (sensitivity experiment;
Supplementary Table S5). For the longest record retrieved, 1979–2024, the net
yield is 2.350 GWh MW⁻¹ yr⁻¹, which differs from the primary estimate by
−0.2 %. The long-term level is thus insensitive to where a long record starts.
A short recent record gives a different picture. For the 2014–2024 comparison
period the yield is higher than the primary estimate by 3.1 %, and for the
2015–2024 comparison period by 5.0 %. For 2008–2017, the reference period of
the wind atlas, it is lower by 1.0 %.

The rolling windows show that this is systematic. The 21 windows of 11 years
that lie inside 1994–2024 range from −3.4 % (window 1999–2009) to +3.1 %
relative to the primary estimate. The most recent window, the 2014–2024
comparison period, is the highest of all 21, and also the highest of the 36
windows in 1979–2024 (Fig. 2b; Supplementary Table S6). An estimate based only
on the most recent 11 years would therefore have been higher than the
long-term estimate by about 3 %. Two cautions apply. Overlapping windows share
years and are not independent samples. And differences between periods in a
reanalysis may partly reflect changes in the observations that the reanalysis
assimilates, so they are not evidence of a climatic trend.

## 4.4. Grid-node sensitivity

The result also depends on which reanalysis cell is used (sensitivity
experiment; Table 3; Fig. 3a). With the same period and method, the western
neighbour at 26.00° E gives a net yield of 2.512 GWh MW⁻¹ yr⁻¹ (+6.7 %
relative to the primary node), and the eastern neighbour at 26.50° E gives
2.154 GWh MW⁻¹ yr⁻¹ (−8.5 %). The corresponding differences in mean 100 m wind
speed are +3.0 % and −3.7 %.

These differences are persistent. Year by year, the western node is higher
than the primary node by 5.0 % to 8.6 %, and the eastern node is lower by
6.4 % to 10.4 %, in every one of the 31 years. They are systematic differences
between model cells, and a longer record does not reduce them.

The three cells differ in how the model represents them. The western cell is
predominantly marine in the ERA5 land–sea mask (land fraction 0.12), whereas
the primary and eastern cells are mixed land–sea cells (0.44 and 0.46). The
western cell also has the lowest shear exponent (0.10, against 0.15 and 0.14).
None of the nodes lies inside the polygon, and the values are reanalysis
output, not measurements. The nodes are therefore not averaged, and the two
differences are not a bound on the resource of the candidate area. They show
that the choice of cell moves the result by several times the half-width of
the sampling interval.

## 4.5. Disagreement between ERA5 and the Global Wind Atlas

The two wind products disagree on the mean wind speed (inter-model comparison;
Table 4; Fig. 3b). The GWA mean at 100 m over the candidate polygon is 7.84 m
s⁻¹ for its reference period 2008–2017. The ERA5 mean at the primary node is
7.01 m s⁻¹ for 1994–2024 and 6.99 m s⁻¹ for the GWA period, 2008–2017. The
GWA/ERA5 ratio is 1.119 against the primary period and 1.122 when the periods
are matched. Matching the periods therefore does not reduce the disagreement.

The size of the disagreement depends on the cell. Comparing the sea pixels of
GWA around each node with ERA5 at that node, for matched periods, the ratio is
1.067 at the western node, 1.153 at the primary node and 1.102 at the eastern
node. The two products do not even rank the three cells in the same order:
ERA5 has the highest mean at the western node, GWA at the primary node
(Supplementary Table S11).

This comparison is not a validation. GWA is driven by ERA5, neither product
has been compared with offshore measurements in this area, and the ratio is
not an estimate of an ERA5 bias. Its practical weight can be illustrated with
the scaling experiments. Energy responds about twice as strongly as wind
speed: raising every hourly speed by 5 % raises the yield by 10.0 %, and
lowering it by 5 % lowers the yield by 10.1 % (Supplementary Table S10). If
the primary series were scaled by the period-matched GWA/ERA5 ratio, the yield
would be higher by about 24 %. This scaled case is illustrative only. It is
not adopted, and the primary estimate is not rescaled.

## 4.6. Loss-assumption sensitivity

The net yield scales directly with the assumed losses (assumption scenarios).
The low-loss case gives 2.507 GWh MW⁻¹ yr⁻¹ (+6.5 %) and the high-loss case
2.158 GWh MW⁻¹ yr⁻¹ (−8.3 %). No site or layout information supports any of
the three loss sets, and wake losses in particular depend on a layout that
does not exist.

Table 2 places the six categories side by side (see also Fig. 4). They are
different kinds of quantity: one sampling interval, one description of
year-to-year spread, three sensitivity experiments or comparisons and one set
of assumption scenarios. They are not combined into a single interval. Read
together, they show that the sampling interval is the smallest of them. A
short recent reference period, a neighbouring grid cell, the other wind
product and the alternative loss assumptions can each move the result by more
than the half-width of that interval.

## 4.7. Bathymetry and protected-area screening

The whole candidate polygon lies in water shallower than 62 m (Table 5; Fig.
1). The median depth is 28 m; about 9 % of the area is shallower than 10 m and
about 11 % is deeper than 50 m. These are depth statistics only. They say
nothing about seabed conditions or foundation suitability.

About 25 km² of the polygon, or about 14 % of its area, lies inside the
reconstructed boundary of the Saros Körfezi Special Environmental Protection
Area. The estimate is approximate, for the reasons given in Section 2.4, and
it is a screening result, not a permitting judgement. An earlier national
screening study treated the marine Special Environmental Protection Areas,
Saros Körfezi among them, as an exclusion layer (World Bank, 2024). The
polygon does not overlap the Gelibolu Peninsula strictly protected sensitive
area. Counts of grid positions by screening class for one illustrative regular
grid are given in Supplementary Table S15; they are not robust and are not
used further.

## 4.8. Operational grid-CO₂ accounting

Under the official 2023 combined-margin convention, the net yield corresponds
to an operational grid-CO₂ accounting equivalent of 1 469 tCO₂ MW⁻¹ yr⁻¹
(Table 6). Carrying only the sampling interval of the mean energy through the
fixed factor gives 1 436–1 503 tCO₂ MW⁻¹ yr⁻¹. The choice of convention
matters far more than that interval: the same energy corresponds to 1 679 tCO₂
MW⁻¹ yr⁻¹ with the operating margin, 840 tCO₂ MW⁻¹ yr⁻¹ with the build margin
and 1 012 tCO₂ MW⁻¹ yr⁻¹ with the generation average. These are accounting
values under stated conventions for 2023. They are proportional to the energy
yield and inherit all of its sensitivities, and they are not a forecast of the
generation that would physically be displaced.

If a capacity of the size named in the draft tender were allocated to Saros,
the illustrative 997.5 MW case would correspond to a net energy of 2 348 GWh
yr⁻¹ and, under the combined-margin convention, to an accounting equivalent of
1 466 kt CO₂ yr⁻¹ (Table 6). No such allocation has been made, and the case
involves no layout.
