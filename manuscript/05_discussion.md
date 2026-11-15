<!-- GENERATED FILE - do not edit. Source: manuscript/src/05_discussion.md. Numbers come from results/revised/. Rebuild with: python scripts/11_build_manuscript_sections.py -->

# 5. Discussion

## 5.1. What the long-term estimate establishes

The primary result, 2.354 GWh MW⁻¹ yr⁻¹ at a net capacity factor of 26.85 %,
is a statement about a model chain. It says what the ERA5 wind series at one
grid node yields when it is passed through one reference power curve and one
set of assumed losses, averaged over 1994–2024. Within that chain the result
is well determined: it is reproducible from pinned inputs, it barely changes
when the record is extended to 1979 (−0.2 %), and the sampling interval of the
mean is narrow (±2.3 %).

The result does not establish the wind resource of the candidate area. Nothing
in this study tests whether the reanalysis is right at this location, and the
sampling interval is silent on that question by construction. Nor is the
1994–2024 mean a prediction. It describes 31 past reanalysis years. Whether
those years represent the conditions under which a plant would operate is an
assumption that this study cannot test.

## 5.2. Why a recent reference period gives a higher estimate

What is demonstrated is the pattern. The 6 most recent 11-year windows, from
2009–2019 onwards, all lie above the 1994–2024 mean, and all 15 earlier
windows lie below it. The 2014–2024 comparison period is the highest window
even though it contains 2014, the second-lowest year of the record: 9 of the
10 years from 2015 to 2024 are above the long-term mean, against 8 of the 20
years from 1994 to 2013. An estimate built only on recent years therefore
inherits a run of above-average years.

Why the recent years are higher is not demonstrated. Two explanations are
possible, and they are not exclusive. The wind climate of the region may vary
on decadal time scales, so that the recent years are a windier phase of a real
fluctuation. Alternatively, part of the difference may be an artefact of the
reanalysis, because the observations it assimilates have changed over the
decades. This study has no means of separating the two. The practical
conclusion does not depend on the explanation: a record of about a decade is
too short to stand for the long-term mean at this node, and the choice of
period should be stated and tested whenever such a record is used.

## 5.3. Why the grid cell matters more than the sampling interval

The sampling interval and the node experiment answer different questions. The
interval asks how well 31 years determine their own mean. The node experiment
asks what happens if a neighbouring cell is taken to represent the same area.
The second effect is larger: the differences of +6.7 % and −8.5 % are about 3
and 4 times the half-width of the sampling interval. They are also of a
different nature. Because they recur in every year with little scatter, more
years would narrow the sampling interval further and leave the node
differences unchanged.

The reason lies in the geometry. The candidate polygon is about 11 km wide,
less than the spacing of the reanalysis grid, and it lies between grid nodes,
none of which falls inside it. Any node-based estimate is thus a statement
about a cell that only partly covers the area. The cells differ in the model's
own description of them: the primary cell has a land fraction of 0.44 and the
western cell 0.12. It is a plausible hypothesis that land influence lowers the
wind speed of the mixed cells, and the lower shear exponent of the western
cell is consistent with it. The hypothesis is not established here. The
eastern cell has nearly the same land fraction as the primary cell and a
clearly lower yield, so land fraction alone does not order the three cells.
For the same reason the three values were not averaged: an average would have
no physical meaning, and there is no observation against which a weighting
could be judged.

## 5.4. Why the comparison with the Global Wind Atlas cannot decide which product is right

The two products differ by about 12 % in mean wind speed over the polygon when
their periods are matched, and by 7 % to 15 % depending on the cell. This
shows that the model-based estimate of the resource level is not robust. It
does not show which product is closer to the truth, for three reasons. The
atlas is driven by ERA5 and is therefore not an independent source. Neither
product has been compared with offshore measurements in this area. And the two
products disagree not only on the level but also on the spatial pattern, so
that the difference cannot be reduced to one constant factor.

One observation is suggestive. The disagreement is smallest at the cell that
ERA5 treats as predominantly marine and largest at the primary cell. This is
what would be expected if the coarse reanalysis were affected by land in the
mixed cells. It is equally compatible with errors in the downscaling near the
coast. The comparison is therefore reported as a discrepancy. The primary
estimate is not scaled towards the atlas, because doing so would replace one
unverified level by another.

## 5.5. Why the six categories are not combined

It would be convenient to merge the categories of Table 2 into one uncertainty
band. There are three reasons not to. First, they are different kinds of
quantity. Only the sampling interval has a probabilistic meaning. Interannual
variability describes single years, not the mean. The period, node and product
results are the outcomes of specific alternative choices, and the loss cases
are assumptions. None of the last four has a probability attached to it, and
assigning one would be arbitrary. Second, they are not independent. The node
and product comparisons both reflect how the reanalysis represents a coastal
area, so that adding them would count the same deficiency twice. Third, the
alternatives examined are not exhaustive. Two neighbouring cells and one other
product do not span the possible errors. A combined interval would therefore
look more rigorous than the evidence allows. The categories are best read side
by side, as a statement of which choices matter and by how much.

## 5.6. Limits set by the data and the turbine model

Three limits apply to every number in this paper. One is the mixed coastal
cell discussed above: the wind series represents a cell that is partly land
and lies outside the polygon. Another is the absence of offshore measurements.
Without them the direction of any error in the resource level is unknown, and
the sensitivity experiments describe the spread among model-based choices, not
the error of any of them. The last is the turbine model. The power curve is a
third-party digitisation that has not been certified by the manufacturer, its
air-density basis is not documented, and it was applied to hourly values. The
losses are assumed, and no wake model was run because no layout exists. The
loss cases alone change the result by +6.5 % and −8.3 %. A different turbine,
with a different ratio of rotor area to rated power, would give a different
capacity factor from the same wind series. The capacity factor reported here
should therefore not be compared with reference values defined for other
machines or under other conventions.

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

The main implication concerns measurement. In this case the sampling interval
is the smallest of the reported categories, so further years of reanalysis
data would add little. The choices that move the result, the grid cell and the
wind product, both concern the level and the spatial pattern of the wind over
a narrow coastal area, and these can only be settled by observation. A
measurement campaign inside the candidate polygon would address them directly.
The draft specification itself lists meteorological and oceanographic
measurements among the tasks of the developer (MENR, 2026b). The
period-selection result adds a caution for such a campaign: a measurement
record of one or a few years would need to be related to a long reference
record before it is taken as representative, and the choice of that reference
period is itself consequential.

Several further steps would improve a desk-based assessment at low cost. The
1994–2024 series could be retrieved again from the Copernicus Climate Data
Store to remove the dependence on a redistributed copy. A further
high-resolution product, such as the New European Wind Atlas (Dörenkämper et
al., 2020), could be added to the comparison, with the understanding that it
is also driven by ERA5. A reference turbine with a published tabulated power
curve would remove the dependence on a digitised curve. A layout-specific wake
calculation would replace the assumed wake loss once a layout is proposed.
None of these steps would remove the need for measurements.
