<!-- GENERATED FILE - do not edit. Source: manuscript/src/02_study_area.md. Numbers come from results/revised/. Rebuild with: python scripts/11_build_manuscript_sections.py -->

# 2. Study Area

## 2.1. Geographic setting

The Gulf of Saros is an embayment of the north-eastern Aegean Sea. It is
bounded by the coast of Thrace to the north and by the Gelibolu (Gallipoli)
Peninsula to the south, and it opens westward to the North Aegean. The
candidate area examined here lies on the northern, Thracian shelf of the gulf
and runs roughly parallel to the Thracian coast. The Gelibolu Peninsula forms
the opposite, southern shore (Fig. 1).

The area is defined by the polygon that the Ministry of Energy and Natural
Resources (MENR) published with its notice of 13 May 2026 (file "SAROS
DÜRES.kml"; MENR, 2026a). The polygon has 27 vertices and an area of 172.6 km²
(computed in WGS 84 / UTM zone 35N). Its centroid lies at 40.557° N,
26.198° E. It is elongated: 35.9 km along its principal axis, which bears 81°
(east-north-east to west-south-west), and 11.3 km across it. This study takes
the published polygon as a fixed geometric object. It implies no turbine
layout, cable route or installation footprint.

## 2.2. Official status of the candidate area

The notice of 13 May 2026 states that the published areas were determined as
*candidate* renewable energy resource areas (aday YEKA) under the Renewable
Energy Resource Areas Regulation (Official Gazette 29852, 9 October 2016), and
that detailed studies towards their declaration as offshore-wind YEKA have
started (MENR, 2026a). Four polygons accompany the notice: Saros, Gökçeada,
Bozcaada and Edremit. The Saros polygon is therefore a candidate YEKA. It is
not a declared YEKA and not an approved project, and no installed capacity,
layout or developer is attached to it.

On 22 June 2026 MENR published a draft tender specification for comment (YEKA
DÜRES-2026; "DÜRES" abbreviates *Deniz Üstü Rüzgâr Enerjisi Santrali*,
offshore wind power plant). The draft concerns a competition for a total
connection capacity of 1 000 MWe and defines the area as any one of the areas
published with the May notice (MENR, 2026b). The draft therefore does not
assign that capacity, or any capacity, to Saros. No final specification or
tender notice had been found among the ministry's announcements by 14 November
2026. Statements about status in this paper refer to that date.

## 2.3. Bathymetry

Water depth inside the polygon was taken from the EMODnet Digital Bathymetry
DTM 2024 (EMODnet Bathymetry Consortium, 2024), using the 16 907 grid-cell
centres that fall inside the polygon. Depth below lowest astronomical tide
ranges from 1.0 m to 61.6 m, with a median of 27.8 m and a 5th–95th percentile
range of 7.2–54.7 m. About 9 % of the area is shallower than 10 m and about
11 % is deeper than 50 m. No cell inside the polygon is deeper than 200 m. The
10 m and 50 m values are screening thresholds chosen for this study. They are
not technical or legal limits. Seabed conditions, geotechnical suitability and
foundation design are outside the scope of this study.

## 2.4. Protected-area context

The Saros Körfezi Special Environmental Protection Area (*Özel Çevre Koruma
Bölgesi*, ÖÇK) was declared by Council of Ministers Decision 2010/1089
(Official Gazette 27793, 22 December 2010) under Article 9 of Environment Law
No. 2872. The annex to the decision lists 13 boundary points in geographic
coordinates. It does not state a geodetic datum. For screening, the boundary
was reconstructed by joining these points with straight segments and reading
the coordinates as WGS 84 (Fig. 1).

With this reconstruction, about 25 km² of the candidate polygon, or about 14 %
of its area, lies inside the ÖÇK. The overlap is the eastern arm of the
polygon. The figure is approximate for two reasons. First, the datum of the
decree coordinates is not stated. Second, it could not be confirmed that the
2010 boundary is still the one in force: no later amendment was found in the
searches made up to 14 November 2026, but the ministry's current boundary data
could not be consulted, and the absence of a discovered amendment does not
show that none exists. The polygon does not overlap the Gelibolu Peninsula
strictly protected sensitive area declared by Presidential Decision 1133
(Official Gazette 30791, 1 June 2019).

The overlap is reported as a screening result. This study makes no
determination on whether, or under what conditions, development inside the ÖÇK
could be authorised. Several other topics relevant to siting were not
screened: bird migration, fisheries, navigation and liquefied-natural-gas
traffic, military exercise areas, the distance to the North Anatolian Fault
and the grid connection point.

## 2.5. Seismotectonic context

The gulf lies on the offshore continuation of the northern strand of the North
Anatolian Fault, known in this sector as the Ganos fault (Yaltırak and Alpar,
2002; Koukouvelas and Aydin, 2002). The 1912 Mürefte–Şarköy earthquake
ruptured this fault, and its rupture has been traced offshore into the gulf
(Aksoy et al., 2022). The distance between the fault and the candidate polygon
was not computed here, and seismic hazard was not assessed.

## 2.6. The candidate polygon and the reanalysis grid

The wind data come from ERA5 output on its 0.25° latitude–longitude grid
(Section 3.2). The grid node nearest the polygon centroid is at 40.50° N,
26.25° E. This node lies outside the polygon, 3.7 km south of its boundary. It
is the nearest node for 62.6 % of the polygon area. The remainder is nearest
to the neighbouring nodes at 26.00° E (27.7 %) and 26.50° E (9.7 %). None of
the three nodes lies inside the polygon (Fig. 1).

A value at an output node is not a point measurement. The 0.25° output grid is
interpolated from a model grid of about 31 km (Section 3.2), so neighbouring
output nodes, which are 0.25° or about 21 km apart in longitude at this
latitude, share information from the same model grid points. The static ERA5
land–sea mask, interpolated in the same way, has a value of 0.44 at the
primary node, 0.46 at the eastern neighbour and 0.12 at the western neighbour.
These values indicate how strongly land influences the model's representation
of each node. At the primary node the value is much larger than the share of
land within 0.25° of the node, which is consistent with smoothing on the
coarser model grid. All results in this paper are therefore node-level
results. They do not resolve wind gradients inside the polygon, and the effect
of the node choice is examined as a separate sensitivity experiment (Sections
3.7 and 4.4).
