# Long-term reanalysis-based energy yield of the Gulf of Saros offshore wind candidate area, Türkiye: sensitivity to reference period, grid node and wind data source

## Abstract

Türkiye published four candidate areas for offshore wind in May 2026. For
the Gulf of Saros area, this study asks what a public reanalysis indicates
about the long-term energy yield, and how sensitive the answer is to choices
that are often left implicit. Hourly ERA5 wind speeds for 1994–2024 at the
grid node nearest the candidate polygon were extrapolated to a hub height of
105 m and converted hour by hour with a reference 9.5 MW power curve and
assumed losses. The net specific yield is
{{energy_yield:net.gwh_per_mw|.3f}} GWh MW⁻¹ yr⁻¹, at a net capacity factor
of {{energy_yield:net_cf|pct.2f}} %. The 90 % sampling interval of the
31-year mean is
{{interannual_and_sampling:sampling_ci_of_period_mean.primary_t_interval_90.net_gwh_per_mw.0|.3f}}–{{interannual_and_sampling:sampling_ci_of_period_mean.primary_t_interval_90.net_gwh_per_mw.1|.3f}} GWh MW⁻¹ yr⁻¹.
Three sensitivity experiments move the result by more than this interval.
The most recent 11 years alone give a yield
{{period_sensitivity:periods.2014-2024.energy_change_vs_reference_pct|abs.1f}} %
higher, and they form the highest of all 11-year windows in the record. The
two neighbouring ERA5 nodes give
{{node_sensitivity:nodes.W.energy_rel_to_primary_node_pct|+.1f}} % and
{{node_sensitivity:nodes.E.energy_rel_to_primary_node_pct|+.1f}} %; the node
used is a mixed land–sea cell outside the polygon. The Global Wind Atlas
indicates a mean wind speed about
{{d:gwa_polygon_excess_matched_pct|.0f}} % higher than ERA5 for matched
periods. This disagreement cannot be resolved from model data, because the
atlas is itself driven by ERA5. The categories differ in kind and are
reported separately; they are not combined into one uncertainty interval. A
first-order screening shows water depths below
{{site_screening:bathymetry.depth_m.max|.0f}} m throughout the polygon and
an overlap of about
{{site_screening:protected_area_overlap.saros_ock_2010.overlap_share_pct|.0f}} %
with a Special Environmental Protection Area. No result is validated against
offshore measurements. For a narrow coastal area such as this one, the
reference period, the grid cell and the wind product should be reported and
tested, and measurements inside the polygon are the step that would most
improve knowledge of the resource.

**Keywords:** offshore wind energy; ERA5 reanalysis; energy yield; capacity
factor; spatial representativeness; reference period; sensitivity analysis;
Global Wind Atlas; Gulf of Saros; Türkiye
