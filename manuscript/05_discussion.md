<!-- GENERATED FILE - do not edit. Source: manuscript/src/05_discussion.md. Numbers come from results/revised/. Rebuild with: python scripts/11_build_manuscript_sections.py -->

# 5. Discussion

## 5.1. What the long-term estimate establishes

The primary result, 2.354 GWh MW⁻¹ yr⁻¹ at a net capacity factor of 26.85 %,
is a statement about a model chain. It says what the ERA5 wind series at one
grid node yields when it is passed through one reference power curve and one
set of assumed losses, averaged over 1994–2024. Within that chain the result
is well determined: it is reproducible from pinned inputs, it barely changes
when the record is extended to 1979 (−0.2 %), and the sampling confidence
interval of the mean is narrow (±2.3 %).

The result does not establish the wind resource of the candidate area. Nothing
in this study tests whether the reanalysis is right at this location, and the
sampling confidence interval is silent on that question by construction. Nor
is the 1994–2024 mean a prediction. It describes 31 past reanalysis years.
Whether those years represent the conditions under which a plant would operate
is an assumption that this study cannot test.

## 5.2. What the higher estimate of a recent reference period means

What is observed is a difference, not a demonstrated shift (Fig. 2b). The
2014–2024 comparison period is the highest window even though it contains
2014, the second-lowest year of the record: 9 of the 10 years from 2015 to
2024 are above the long-term mean, against 8 of the 20 years from 1994 to
2013. An estimate built only on recent years therefore inherits a run of
above-average years. Because overlapping windows share most of their years,
the sequence of window means changes slowly by construction, and the fact that
the recent windows lie above the long-term mean adds little evidence beyond
the annual values themselves. The difference of 3.1 % between the most recent
window and the 31-year mean is of the same size as the sampling uncertainty of
an 11-year mean (±3.8 %).

Whether the recent years reflect more than sampling variability is not
demonstrated. If they do, two explanations are possible, and they are not
exclusive. The wind climate of the region may vary on decadal time scales, so
that the recent years are a windier phase of a real fluctuation.
Alternatively, part of the difference may be an artefact of the reanalysis,
because the observations it assimilates have changed over the decades. This
study has no means of separating the two. The practical conclusion does not
depend on the explanation: a record of about a decade is too short to stand
for the long-term mean at this node, and the choice of period should be stated
and tested whenever such a record is used.

## 5.3. Why the grid node matters more than sampling uncertainty

The sampling confidence interval and the node experiment answer different
questions. The interval asks how well 31 years determine their own mean. The
node experiment asks what happens if a neighbouring output node is taken to
represent the same area. The second effect is larger: the differences of
+6.7 % and −8.5 % are about 3 and 4 times the half-width of the sampling
confidence interval (Fig. 4). They are also of a different nature. Because
they recur in every year with little scatter, more years would narrow the
sampling confidence interval further and leave the node differences unchanged.

The reason lies in the geometry and in the resolution of the model. The
candidate polygon is about 11 km wide, narrower than both the spacing of the
output nodes and the model resolution of about 31 km, and none of the nodes
falls inside it. Any node-based estimate is thus a statement about the model's
smoothed wind at a nearby point, not about the polygon. The nodes differ in
the model's own description of them: the value of the land–sea mask is 0.44 at
the primary node and 0.12 at the western node. It is a plausible hypothesis
that land influence lowers the modelled wind speed at the primary and eastern
nodes, and the lower shear exponent at the western node is consistent with it.
A genuine east–west gradient, with stronger winds towards the open gulf, is an
alternative or additional explanation. Neither is established here. The
eastern node has nearly the same mask value as the primary node and a clearly
lower yield, so land influence alone does not order the three nodes. For the
same reason the three values were not averaged: an average would not be better
supported than any single node, and there is no observation against which a
weighting could be judged.

## 5.4. Why the comparison with the Global Wind Atlas cannot decide which product is right

The two products differ by about 12 % in mean wind speed over the polygon when
their periods are matched, and by 7 % to 15 % depending on the node (Fig. 3b).
This shows that the model-based estimate of the resource level is not robust.
It does not show which product is closer to the truth, for three reasons. The
atlas is driven by ERA5 and is therefore not an independent source. Neither
product has been compared with offshore measurements in this area. And the two
products disagree not only on the level but also on the spatial pattern, so
that the difference cannot be reduced to one constant factor.

One observation is suggestive. The disagreement is smallest at the node where
the ERA5 land–sea mask indicates least land influence and largest at the
primary node. This is what would be expected if the coarse reanalysis were
affected by land near the coast. It is equally compatible with errors in the
downscaling near the coast. The comparison is therefore reported as a
discrepancy. The primary estimate is not scaled towards the atlas, because
doing so would replace one unverified level by another. Assessments that rest
on a single wind product, including atlas-based assessments such as the
feasibility assessment of a Saros region by Yildirim (2023), therefore remain
subject to an unresolved wind-product uncertainty. The size of the difference
found here applies to the 2026 polygon and the nodes examined; it is not
transferable to other study areas, heights or assumptions.

## 5.5. Why the six categories are not combined

It would be convenient to merge the categories of Table 4 into one uncertainty
band. There are three reasons not to. First, they are different kinds of
quantity. Only the sampling confidence interval has a probabilistic meaning.
Interannual variability describes single years, not the mean. The period, node
and product results are the outcomes of specific alternative choices, and the
loss cases are assumptions. None of the last four has a probability attached
to it, and assigning one would be arbitrary. The period result partly overlaps
category 1, because a shorter record carries a larger sampling uncertainty.
Second, they are not independent. The node and product comparisons both
reflect how the reanalysis represents a coastal area, so that adding them
would count the same deficiency twice. Third, the alternatives examined are
not exhaustive. Two neighbouring nodes and one other product do not span the
possible errors. A combined interval would therefore look more rigorous than
the evidence allows. The categories are best read side by side (Fig. 4), as a
statement of which choices matter and by how much.

## 5.6. Limits set by the data and the turbine model

Three limits apply to every number in this paper. One is the coastal node
discussed above: the wind series is the model's smoothed value at a point
outside the polygon whose representation is influenced by land. Another is the
absence of offshore measurements. Without them the direction of any error in
the resource level at this site is not established, and the sensitivity
experiments describe the spread among model-based choices, not the error of
any of them. The last is the turbine model. The power curve is a third-party
digitisation that has not been certified by the manufacturer, its air-density
basis is not documented, and it was applied to hourly values. The losses are
assumed, and no wake model was run because no layout exists. The uncertainty
of the digitised curve itself was not quantified. The loss cases alone change
the result by +6.5 % and −8.3 %. A different turbine, with a different ratio
of rotor area to rated power, would give a different capacity factor from the
same wind series. The capacity factor reported here should therefore not be
compared with reference values defined for other machines or under other
conventions.

## 5.7. What the screening shows

The screening establishes two geometric facts. The whole polygon lies in water
shallower than 62 m, and about 14 % of it lies inside the boundary of the
Saros Körfezi Special Environmental Protection Area as reconstructed from the
2010 decree. Neither fact is a conclusion about development. Depth says
nothing about seabed conditions, foundations or cost. The overlap identifies a
question for the competent authorities and for a future environmental
assessment. It does not show that the overlapping part is unavailable, and it
does not show that the remaining part is available. The boundary itself is
approximate, and bird migration, fisheries, navigation, military use, seismic
hazard and grid connection were not examined.

## 5.8. Why the CO₂ values are accounting equivalents

The CO₂ figure is the energy yield multiplied by a published factor. It adds
no information to the yield and inherits all of its sensitivities. Its own
largest source of spread is the convention: between the build margin and the
operating margin the result differs by a factor of 2.0. These conventions
answer different accounting questions. None of them describes which generation
a plant in the Gulf of Saros would physically displace. That would depend on
the generation mix, the dispatch and the curtailment in the years in which the
plant operates, none of which is modelled here, and a factor for 2023 cannot
stand for them. The value is therefore reported as an accounting equivalent
under a stated convention and not as a forecast of emissions.

## 5.9. Implications for measurement and for further assessment

The main implication concerns measurement. In this case the sampling
confidence interval of the 31-year mean is smaller than the node, product and
loss effects, so further years of reanalysis data would add little. The
choices that move the result, the grid node and the wind product, both concern
the level and the spatial pattern of the wind over a narrow coastal area, and
these can only be settled by observations, in situ or, where their quality
near the coast allows, satellite-derived. A measurement campaign inside the
candidate polygon would address them directly. The draft specification itself
lists meteorological and oceanographic measurements among the tasks of the
developer (MENR, 2026b). The period-selection result adds a caution for such a
campaign: a measurement record of one or a few years would need to be related
to a long reference record before it is taken as representative, and the
choice of that reference period is itself consequential.

Several further steps would improve a desk-based assessment at low cost. The
1994–2024 series could be retrieved again from the Copernicus Climate Data
Store to remove the dependence on a redistributed copy. A further
high-resolution product, such as the New European Wind Atlas (Dörenkämper et
al., 2020), could be added to the comparison, with the understanding that it
is also driven by ERA5. A reference turbine with a published tabulated power
curve would remove the dependence on a digitised curve. A layout-specific wake
calculation would replace the assumed wake loss once a layout is proposed.
None of these steps would remove the need for measurements.
