<!-- GENERATED FILE - do not edit. Source: manuscript/src/01_introduction.md. Numbers come from results/revised/. Rebuild with: python scripts/11_build_manuscript_sections.py -->

# 1. Introduction

Offshore wind has a defined place in Türkiye's energy planning. The National
Energy Plan projects a wind capacity of 29.6 GW in 2035, of which 5 GW would
be offshore (MENR, 2022). A roadmap prepared by the World Bank in
collaboration with the government estimates the technical offshore wind
potential of Turkish waters at 75 GW and places offshore wind in the context
of the country's pledge to reach net-zero emissions by 2053 (World Bank,
2024). According to Yildirim (2023), an earlier tender process was opened in
2018. On 13 May 2026 the Ministry of Energy and Natural Resources (MENR)
published four candidate areas for offshore wind, in the Gulf of Saros and off
Gökçeada, Bozcaada and Edremit (MENR, 2026a). A draft specification published
in June 2026 describes a competition for a total of 1 000 MWe in any one of
these areas (MENR, 2026b); at the time of writing it existed only as a draft.
The Gulf of Saros area is thus a candidate area defined by a published
polygon. It is not an approved project, and no capacity has been assigned to
it.

A candidate polygon raises a practical question: what can be said about its
energy yield from public data, before any measurement exists, and how firmly?
Earlier work on Turkish offshore wind has mostly addressed where to build.
National and regional site-selection studies have screened coastal waters with
multi-criteria and GIS methods (Argin et al., 2019; Emeksiz and Demirci, 2019;
Tercan et al., 2020; Genç et al., 2021), and a recent review covers candidate
locations, foundations and seismic conditions (Demirci et al., 2026). Other
studies have estimated energy production and cost for specific sites. Cali et
al. (2018) analysed Bozcaada, Gökçeada and Bandırma with a wind-farm model
driven by reanalysis data. Satir et al. (2018) presented a feasibility study
of an offshore wind farm in the Turkish Aegean. Özbek and Tunç (2021) studied
the Gulf of Edremit with reanalysis data and a local meteorological mast.
Duzcan and Kara (2023) assessed 24 regions of the Marmara and Aegean seas by
transferring ten years of 10 m wind data from onshore stations to hub height
with computational fluid dynamics, noting that no offshore meteorological mast
existed in Türkiye. Erkurtulmus and Pesman (2024) selected a site for floating
turbines north-east of Gökçeada. At the basin scale, Görmüş et al. (2022)
analysed the offshore wind power potential of the Mediterranean region.

The Gulf of Saros itself has been examined before. Yildirim (2023) carried out
a techno-economic analysis of three candidate regions identified in the 2018
tender process, two in the Aegean Sea and one in the Black Sea, using data
from the Global Wind Atlas, and reported the best results for a Saros region.
The published abstract does not define the region that was examined, and the
full text was not available to us. The spatial relationship between that
region and the polygon published in 2026 could therefore not be established,
and the results of the two studies are not compared here.

These studies share one feature that matters for the present purpose: each
rests on a single wind data source. In the absence of offshore measurements,
that source is a model product, and model products differ. The ERA5 reanalysis
(Hersbach et al., 2020) is widely used for wind energy studies and has been
evaluated against observations in several regions (Olauson, 2018; Ramon et
al., 2019; Kalverla et al., 2020; Gualtieri, 2021; Gandoin and Garza, 2024;
Rubio et al., 2025). Its model resolution is about 31 km, and its output is
distributed on a 0.25° latitude–longitude grid interpolated from the model
grid. In a gulf a few tens of kilometres wide, the model's representation of a
point near the coast mixes land and sea influence, and a value at an output
node then represents neither the open sea nor a particular site. The Global
Wind Atlas (Davis et al., 2023) offers much finer spatial detail, but it is a
downscaling of ERA5 for a fixed period and not an independent observation. An
analyst who uses such products therefore makes three choices, often
implicitly: the reference period, the grid node or pixels taken to represent
the site, and the product itself. Each choice can move the estimated yield,
and none of them is reflected in a confidence interval computed from the
interannual scatter of one series.

This study examines how much these choices matter for the Gulf of Saros
candidate area. Its objective is to provide a preliminary, long-term estimate
of the net specific energy yield at the reanalysis node nearest the candidate
polygon, and to show how sensitive that estimate is to the reference period,
the grid node, the wind data product and the loss assumptions. The study makes
four limited contributions. First, a reproducible estimate for 1994–2024 is
obtained by converting 31 years of hourly ERA5 wind speeds with a reference
power curve. Second, the sampling uncertainty of the long-term mean is
reported separately from interannual variability and from four sensitivity
experiments, and the reasons why these categories cannot be merged into one
interval are set out. Third, the candidate polygon is screened to first order
for water depth and for overlap with the Saros Körfezi Special Environmental
Protection Area. Fourth, the yield is expressed as an operational grid-CO₂
accounting equivalent under the official 2023 convention. The study uses no
offshore measurements. It does not establish the accuracy of the reanalysis at
the site, and it is not an assessment of technical, economic or legal
viability.

Section 2 describes the candidate area and its relation to the reanalysis
grid. Section 3 sets out the data and methods. Section 4 presents the results,
Section 5 discusses what they do and do not establish, and Section 6
concludes.
