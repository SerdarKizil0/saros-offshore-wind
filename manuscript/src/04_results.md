# 4. Results

## 4.1. Long-term wind resource and specific energy yield

Over 1994–2024 the ERA5 series at the primary node has a mean wind speed of
{{wind_resource:U100.mean_ms|.2f}} m s⁻¹ at 100 m. Extrapolated to the 105 m
hub height, the mean is {{wind_resource:U_hub.mean_ms|.2f}} m s⁻¹, the
standard deviation {{wind_resource:U_hub.std_ms|.2f}} m s⁻¹ and the median
{{wind_resource:U_hub.median_ms|.2f}} m s⁻¹ (Table 1). The mean wind power
density at 105 m is {{wind_resource:U_hub.power_density_wm2_rho1225|.0f}} W m⁻²
for an air density of 1.225 kg m⁻³. These are statistics of reanalysis
output, not of measurements.

The monthly mean wind speed is highest in {{d:month_max_name}}
({{d:month_max|.2f}} m s⁻¹) and lowest in {{d:month_min_name}}
({{d:month_min|.2f}} m s⁻¹) (Supplementary Table S8). North-easterly winds
dominate. The north-east and east-north-east sectors account for
{{wind_resource:direction_share_pct.hours.NE|.0f}} % and
{{wind_resource:direction_share_pct.hours.ENE|.0f}} % of the hours, and the
north-east sector alone carries
{{wind_resource:direction_share_pct.energy.NE|.0f}} % of the gross energy
(Supplementary Table S9).

Converting the hourly series with the reference power curve gives a gross
capacity factor of {{energy_yield:gross_cf|pct.2f}} %. With the nominal loss
assumptions the net capacity factor is {{energy_yield:net_cf|pct.2f}} % and
the net specific yield is **{{energy_yield:net.gwh_per_mw|.3f}} GWh MW⁻¹ yr⁻¹**,
or {{energy_yield:net_full_load_hours|sp.0f}} full-load hours per year. For
one 9.5 MW turbine this corresponds to
{{energy_yield:gross.gwh_per_turbine|.2f}} GWh yr⁻¹ gross and
{{energy_yield:net.gwh_per_turbine|.2f}} GWh yr⁻¹ net. This is the primary
estimate of the study. It is a model result. It depends on ERA5 at one grid
node, on a third-party digitised power curve and on assumed losses, and it is
not validated against offshore measurements.

## 4.2. Sampling uncertainty and interannual variability

The 90 % sampling interval of the mean net yield is
{{interannual_and_sampling:sampling_ci_of_period_mean.primary_t_interval_90.net_gwh_per_mw.0|.3f}}–{{interannual_and_sampling:sampling_ci_of_period_mean.primary_t_interval_90.net_gwh_per_mw.1|.3f}} GWh MW⁻¹ yr⁻¹,
that is ±{{interannual_and_sampling:sampling_ci_of_period_mean.primary_t_interval_90.half_width_rel_pct|.1f}} %
of the mean (Eq. 6). The bootstrap check gives
{{interannual_and_sampling:sampling_ci_of_period_mean.check_bootstrap_90.net_gwh_per_mw.0|.3f}}–{{interannual_and_sampling:sampling_ci_of_period_mean.check_bootstrap_90.net_gwh_per_mw.1|.3f}} GWh MW⁻¹ yr⁻¹,
and the standard error of the mean is
{{interannual_and_sampling:sampling_ci_of_period_mean.se_rel_pct.classical|.1f}} %
(Supplementary Table S4). This is the only probabilistic interval in the
study. It is conditional on the reanalysis at this node and says nothing
about the accuracy of the reanalysis itself.

Single years vary much more than the mean is uncertain. The coefficient of
variation of the annual net yield is
{{interannual_and_sampling:observed_interannual_variability.annual_net_cf_cov_pct|.1f}} %.
The lowest year is
{{interannual_and_sampling:observed_interannual_variability.min_year}}
({{interannual_and_sampling:observed_interannual_variability.min_net_gwh_per_mw|.3f}} GWh MW⁻¹ yr⁻¹,
{{d:min_year_rel_pct|+.1f}} % relative to the mean) and the highest is
{{interannual_and_sampling:observed_interannual_variability.max_year}}
({{interannual_and_sampling:observed_interannual_variability.max_net_gwh_per_mw|.3f}} GWh MW⁻¹ yr⁻¹,
{{d:max_year_rel_pct|+.1f}} %). The second-lowest year is
{{d:second_lowest_year}} ({{d:second_lowest_net|.3f}} GWh MW⁻¹ yr⁻¹,
{{d:second_lowest_rel_pct|+.1f}} %). The annual values show no appreciable
serial correlation (lag-1 coefficient
{{interannual_and_sampling:observed_interannual_variability.lag1_autocorrelation|+.2f}}).
All annual values are listed in Supplementary Table S3.

## 4.3. Period-selection sensitivity

The estimate depends on the reference period (sensitivity experiment;
Supplementary Table S5). For the longest record retrieved, 1979–2024, the net
yield is {{period_sensitivity:periods.1979-2024.net_gwh_per_mw|.3f}} GWh MW⁻¹ yr⁻¹,
which differs from the primary estimate by
{{period_sensitivity:periods.1979-2024.energy_change_vs_reference_pct|+.1f}} %.
The long-term level is thus insensitive to where a long record starts. A
short recent record gives a different picture. For the 2014–2024 comparison
period the yield is higher than the primary estimate by
{{period_sensitivity:periods.2014-2024.energy_change_vs_reference_pct|abs.1f}} %,
and for the 2015–2024 comparison period by
{{period_sensitivity:periods.2015-2024.energy_change_vs_reference_pct|abs.1f}} %.
For 2008–2017, the reference period of the wind atlas, it is lower by
{{period_sensitivity:periods.2008-2017.energy_change_vs_reference_pct|abs.1f}} %.

The rolling windows show that this is systematic. The
{{period_sensitivity:rolling_windows.within_primary_period.n_windows}}
windows of 11 years that lie inside 1994–2024 range from
{{period_sensitivity:rolling_windows.within_primary_period.lowest_window_rel_to_primary_mean_pct|+.1f}} %
(window {{period_sensitivity:rolling_windows.within_primary_period.lowest_window|en}})
to
{{period_sensitivity:rolling_windows.within_primary_period.highest_window_rel_to_primary_mean_pct|+.1f}} %
relative to the primary estimate. The most recent window, the 2014–2024
comparison period, is the highest of all
{{period_sensitivity:rolling_windows.within_primary_period.n_windows}}, and
also the highest of the
{{period_sensitivity:rolling_windows.all_windows.n_windows}} windows in
1979–2024 (Supplementary Table S6). An estimate based only on the most recent
11 years would therefore have been higher than the long-term estimate by
about {{period_sensitivity:periods.2014-2024.energy_change_vs_reference_pct|.0f}} %.
Two cautions apply. Overlapping windows share years and are not independent
samples. And differences between periods in a reanalysis may partly reflect
changes in the observations that the reanalysis assimilates, so they are not
evidence of a climatic trend.

## 4.4. Grid-node sensitivity

The result also depends on which reanalysis cell is used (sensitivity
experiment; Table 3). With the same period and method, the western neighbour
at 26.00° E gives a net yield of
{{node_sensitivity:nodes.W.net_gwh_per_mw|.3f}} GWh MW⁻¹ yr⁻¹
({{node_sensitivity:nodes.W.energy_rel_to_primary_node_pct|+.1f}} % relative
to the primary node), and the eastern neighbour at 26.50° E gives
{{node_sensitivity:nodes.E.net_gwh_per_mw|.3f}} GWh MW⁻¹ yr⁻¹
({{node_sensitivity:nodes.E.energy_rel_to_primary_node_pct|+.1f}} %). The
corresponding differences in mean 100 m wind speed are
{{node_sensitivity:nodes.W.U100_rel_to_primary_node_pct|+.1f}} % and
{{node_sensitivity:nodes.E.U100_rel_to_primary_node_pct|+.1f}} %.

These differences are persistent. Year by year, the western node is higher
than the primary node by
{{node_sensitivity:nodes.W.paired_annual_rel_diff_vs_primary_node_pct.min|.1f}} %
to {{node_sensitivity:nodes.W.paired_annual_rel_diff_vs_primary_node_pct.max|.1f}} %,
and the eastern node is lower by
{{node_sensitivity:nodes.E.paired_annual_rel_diff_vs_primary_node_pct.max|abs.1f}} %
to {{node_sensitivity:nodes.E.paired_annual_rel_diff_vs_primary_node_pct.min|abs.1f}} %,
in every one of the {{d:n_years}} years. They are systematic differences
between model cells, and a longer record does not reduce them.

The three cells differ in how the model represents them. The western cell is
predominantly marine in the ERA5 land–sea mask (land fraction
{{node_sensitivity:nodes.W.era5_land_sea_mask_fraction|.2f}}), whereas the
primary and eastern cells are mixed land–sea cells
({{node_sensitivity:nodes.C.era5_land_sea_mask_fraction|.2f}} and
{{node_sensitivity:nodes.E.era5_land_sea_mask_fraction|.2f}}). The western
cell also has the lowest shear exponent
({{node_sensitivity:nodes.W.alpha_node|.2f}}, against
{{node_sensitivity:nodes.C.alpha_node|.2f}} and
{{node_sensitivity:nodes.E.alpha_node|.2f}}). None of the nodes lies inside
the polygon, and the values are reanalysis output, not measurements. The
nodes are therefore not averaged, and the two differences are not a bound on
the resource of the candidate area. They show that the choice of cell moves
the result by several times the half-width of the sampling interval.

## 4.5. Disagreement between ERA5 and the Global Wind Atlas

The two wind products disagree on the mean wind speed (inter-model
comparison; Table 4). The GWA mean at 100 m over the candidate polygon is
{{wind_product_discrepancy:polygon_vs_primary_node.gwa4_polygon_mean_100m_ms|.2f}} m s⁻¹
for its reference period 2008–2017. The ERA5 mean at the primary node is
{{wind_product_discrepancy:polygon_vs_primary_node.era5_node_U100_ms.1994-2024|.2f}} m s⁻¹
for 1994–2024 and
{{wind_product_discrepancy:polygon_vs_primary_node.era5_node_U100_ms.2008-2017|.2f}} m s⁻¹
for the GWA period, 2008–2017. The GWA/ERA5 ratio is
{{wind_product_discrepancy:polygon_vs_primary_node.ratio_gwa_to_era5.era5_1994-2024|.3f}}
against the primary period and
{{wind_product_discrepancy:polygon_vs_primary_node.ratio_gwa_to_era5.era5_2008-2017_period_matched|.3f}}
when the periods are matched. Matching the periods therefore does not reduce
the disagreement.

The size of the disagreement depends on the cell. Comparing the sea pixels
of GWA around each node with ERA5 at that node, for matched periods, the
ratio is
{{wind_product_discrepancy:per_node_gwa_box_vs_era5.W.ratio_gwa_box_sea_pixels_to_era5_period_matched|.3f}}
at the western node,
{{wind_product_discrepancy:per_node_gwa_box_vs_era5.C.ratio_gwa_box_sea_pixels_to_era5_period_matched|.3f}}
at the primary node and
{{wind_product_discrepancy:per_node_gwa_box_vs_era5.E.ratio_gwa_box_sea_pixels_to_era5_period_matched|.3f}}
at the eastern node. The two products do not even rank the three cells in the
same order: ERA5 has the highest mean at the western node, GWA at the primary
node (Supplementary Table S11).

This comparison is not a validation. GWA is driven by ERA5, neither product
has been compared with offshore measurements in this area, and the ratio is
not an estimate of an ERA5 bias. Its practical weight can be illustrated with
the scaling experiments. Energy responds about twice as strongly as wind
speed: raising every hourly speed by 5 % raises the yield by
{{d:speed.p5.aep_change_vs_baseline_pct|.1f}} %, and lowering it by 5 %
lowers the yield by {{d:speed.m5.aep_change_vs_baseline_pct|abs.1f}} %
(Supplementary Table S10). If the primary series were scaled by the
period-matched GWA/ERA5 ratio, the yield would be higher by about
{{wind_product_discrepancy:energy_sensitivity_if_primary_hours_were_scaled.by_ratio_era5_2008-2017_period_matched.aep_change_vs_primary_pct|.0f}} %.
This scaled case is illustrative only. It is not adopted, and the primary
estimate is not rescaled.

## 4.6. Loss-assumption sensitivity

The net yield scales directly with the assumed losses (assumption scenarios).
The low-loss case gives
{{loss_scenarios:scenarios.low_loss.net_gwh_per_mw|.3f}} GWh MW⁻¹ yr⁻¹
({{loss_scenarios:scenarios.low_loss.rel_to_nominal_pct|+.1f}} %) and the
high-loss case
{{loss_scenarios:scenarios.high_loss.net_gwh_per_mw|.3f}} GWh MW⁻¹ yr⁻¹
({{loss_scenarios:scenarios.high_loss.rel_to_nominal_pct|+.1f}} %). No site
or layout information supports any of the three loss sets, and wake losses in
particular depend on a layout that does not exist.

Table 2 places the six categories side by side. They are different kinds of
quantity: one sampling interval, one description of year-to-year spread,
three sensitivity experiments or comparisons and one set of assumption
scenarios. They are not combined into a single interval. Read together, they
show that the sampling interval is the smallest of them. A short recent
reference period, a neighbouring grid cell, the other wind product and the
alternative loss assumptions can each move the result by more than the
half-width of that interval.

## 4.7. Bathymetry and protected-area screening

The whole candidate polygon lies in water shallower than
{{site_screening:bathymetry.depth_m.max|.0f}} m (Table 5). The median depth
is {{site_screening:bathymetry.depth_m.median|.0f}} m; about
{{d:share_shallower_10m_pct|.0f}} % of the area is shallower than 10 m and
about {{site_screening:bathymetry.share_deeper_than_pct.50|.0f}} % is deeper
than 50 m. These are depth statistics only. They say nothing about seabed
conditions or foundation suitability.

About {{site_screening:protected_area_overlap.saros_ock_2010.overlap_km2|.0f}} km²
of the polygon, or about
{{site_screening:protected_area_overlap.saros_ock_2010.overlap_share_pct|.0f}} %
of its area, lies inside the reconstructed boundary of the Saros Körfezi
Special Environmental Protection Area. The estimate is approximate, for the
reasons given in Section 2.4, and it is a screening result, not a permitting
judgement. An earlier national screening study treated the marine Special
Environmental Protection Areas, Saros Körfezi among them, as an exclusion
layer (World Bank, 2024). The polygon does not overlap the Gelibolu Peninsula
strictly protected sensitive area. Counts of grid positions by screening
class for one illustrative regular grid are given in Supplementary Table S15;
they are not robust and are not used further.

## 4.8. Operational grid-CO₂ accounting

Under the official 2023 combined-margin convention, the net yield
corresponds to an operational grid-CO₂ accounting equivalent of
{{emissions:primary_avoided_operational_co2.t_co2_per_mw_yr|sp.0f}} tCO₂ MW⁻¹ yr⁻¹
(Table 6). Carrying only the sampling interval of the mean energy through the
fixed factor gives
{{emissions:primary_avoided_operational_co2.ci90_t_co2_per_mw_yr.0|sp.0f}}–{{emissions:primary_avoided_operational_co2.ci90_t_co2_per_mw_yr.1|sp.0f}} tCO₂ MW⁻¹ yr⁻¹.
The choice of convention matters far more than that interval: the same
energy corresponds to
{{emissions:context_grid_methods.operating_margin.result_per_mw_yr|sp.0f}} tCO₂ MW⁻¹ yr⁻¹
with the operating margin,
{{emissions:context_grid_methods.build_margin.result_per_mw_yr|sp.0f}} tCO₂ MW⁻¹ yr⁻¹
with the build margin and
{{emissions:context_grid_methods.generation_average_co2.result_per_mw_yr|sp.0f}} tCO₂ MW⁻¹ yr⁻¹
with the generation average. These are accounting values under stated
conventions for 2023. They are proportional to the energy yield and inherit
all of its sensitivities, and they are not a forecast of the generation that
would physically be displaced.

If a capacity of the size named in the draft tender were allocated to Saros,
the illustrative {{d:s3.installed_mw|.1f}} MW case would correspond to a net
energy of {{d:s3.net_energy_gwh_yr|sp.0f}} GWh yr⁻¹ and, under the
combined-margin convention, to an accounting equivalent of
{{d:s3.avoided_co2_cm_kt_yr|sp.0f}} kt CO₂ yr⁻¹ (Table 6). No such
allocation has been made, and the case involves no layout.
