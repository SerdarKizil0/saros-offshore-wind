# Long-term reanalysis-based energy yield of the Gulf of Saros offshore wind candidate area, Türkiye: sensitivity to reference period, grid node and wind data source

## Abstract

Türkiye published four candidate areas for offshore wind in May 2026. For
the Gulf of Saros area, this study asks what a public reanalysis indicates about the long-term energy yield and how sensitive it is to often implicit choices. Hourly ERA5 wind speeds for 1994–2024 at the
grid node nearest the candidate polygon were extrapolated to 105 m and
converted hour by hour with a reference 9.5 MW power curve and assumed
losses. The net specific yield is about
{{energy_yield:net.gwh_per_mw|.2f}} GWh MW⁻¹ yr⁻¹ (net capacity factor about
{{energy_yield:net_cf|pct.0f}} %), with a 90 % sampling confidence interval
of ±{{interannual_and_sampling:sampling_ci_of_period_mean.primary_t_interval_90.half_width_rel_pct|.1f}} %
for the 31-year mean. The two neighbouring ERA5 output nodes give
{{node_sensitivity:nodes.W.energy_rel_to_primary_node_pct|+.1f}} % and
{{node_sensitivity:nodes.E.energy_rel_to_primary_node_pct|+.1f}} %, with the same sign in every year. The Global Wind Atlas indicates a mean wind speed about
{{d:gwa_polygon_excess_matched_pct|.0f}} % higher than ERA5 over its
mesoscale period, unresolvable from model data because the atlas is driven by ERA5. The most recent 11 years give a yield
{{period_sensitivity:periods.2014-2024.energy_change_vs_reference_pct|abs.1f}} %
higher than the 31-year mean; this is the same size as the
sampling uncertainty of an 11-year mean (±{{d:windows.last_t90_half_width_pct|.1f}} %)
and does not by itself establish a lasting change. The categories differ in
kind; they are not combined into one uncertainty interval. Screening shows
water depths below {{site_screening:bathymetry.depth_m.max|.0f}} m and an
overlap of about
{{site_screening:protected_area_overlap.saros_ock_2010.overlap_share_pct|.0f}} %
with a Special Environmental Protection Area. No result is validated against offshore measurements. For narrow coastal areas, the reference period, grid
node and wind product should be reported and tested.

**Keywords:** offshore wind energy; ERA5 reanalysis; energy yield; capacity
factor; spatial representativeness; reference period; sensitivity analysis;
Global Wind Atlas; Gulf of Saros; Türkiye
