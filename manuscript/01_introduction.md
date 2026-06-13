# 1. Introduction

Türkiye's electricity system remains heavily dependent on fossil fuels.
National electricity consumption reached 347.9 TWh in 2024, of which a
majority continues to be supplied by natural gas and coal, much of it
imported. This dependence exposes the country to fuel-price volatility and
import-security risks, and it underlies an electricity-sector carbon
intensity that the national authorities place at 434 gCO₂-eq kWh⁻¹ on a
generation-average basis and 624 gCO₂-eq kWh⁻¹ on the combined-margin basis
used for crediting renewable displacement (Republic of Türkiye MENR/EVÇED,
2024). Reducing this intensity through domestic renewable generation is
therefore both a decarbonisation and an energy-security objective.

Wind energy is central to this transition. Türkiye has expanded onshore
wind capacity rapidly over the past decade, but offshore wind — despite the
country being bordered by sea on three sides — has remained undeveloped.
Globally, offshore wind has matured into a multi-gigawatt industry with
capacity factors and reliability that substantially exceed onshore
equivalents, and its life-cycle carbon footprint of roughly 8–14 gCO₂-eq
kWh⁻¹ is among the lowest of any generation technology (Schlömer et al., 2014; Bonou
et al., 2016). For a fossil-dependent grid such as Türkiye's, each unit of
offshore wind generation therefore displaces a disproportionately large
quantity of carbon emissions.

A substantial body of research has assessed where offshore wind farms
should be sited along the Turkish coast. Argın and Yerci (2015) screened
more than fifty coastal areas, and Argın et al. (2019) developed a
multi-criteria site-selection framework that identified the Aegean Sea as
having the highest potential, with mean wind speeds near 6.9 m s⁻¹ at 50 m.
Emeksiz and Demirci (2019) introduced a hybrid site-selection method;
Genç et al. (2021) and Tercan et al. (2020) applied GIS-based
multi-criteria decision-making across Turkish and Aegean waters; and
Duzcan and Kara (2022) analysed twenty-four regions in the Marmara and
Aegean seas using computational fluid dynamics to transfer ten years of
meteorological-station data to hub height. More recent work has extended
to investment prioritisation, techno-economic feasibility, and, most
recently, a comprehensive review of candidate locations, foundation design
and seismic considerations for Turkish offshore wind (Demirci, 2026).
Görmüş et al. (2022) further characterised Mediterranean offshore wind
across multiple turbine classes over a six-decade reanalysis record.

Two features unite this literature. First, almost all of it addresses the
*site-selection* question — identifying or ranking candidate areas — rather
than the detailed assessment of a committed site. Second, the focus is
overwhelmingly on the wind *resource* and on techno-economic feasibility;
the *environmental* dimension, in particular the quantification of avoided
grid emissions with formal uncertainty propagation, is rarely treated as a
primary outcome.

The policy context changed decisively on 14 May 2026, when the Republic of
Türkiye Ministry of Energy and Natural Resources formally announced four
offshore renewable energy candidate zones (DÜRES) — at the Gulf of Saros,
Gökçeada, Bozcaada, and off Edremit. This announcement, which followed the
strategic framework of the World Bank's *Offshore Wind Roadmap for Türkiye*
(World Bank, 2024) and the national 2035 target of 5 GW of offshore wind,
transforms the research question. The siting decision has now been made by
the state; the relevant questions are no longer *where* to build, but *how
much energy* a designated zone can produce and *how much environmental
burden* it can displace relative to the conventional supply it would
replace.

To the best of our knowledge, no peer-reviewed assessment yet exists for
any of the four officially designated zones. This study addresses that gap
for the Gulf of Saros zone. Its contributions are threefold. First, it
provides the first site-specific resource and energy-production assessment
of an officially designated Turkish offshore wind zone, based on eleven
years (2014–2024) of hourly ERA5 reanalysis extrapolated to a 105 m hub
height using a *measured* rather than assumed wind-shear exponent. Second,
it quantifies the avoided carbon dioxide emissions relative to the official
Turkish grid emission factor, treating the environmental displacement — not
merely the resource — as a primary outcome. Third, it propagates the
combined uncertainty in wind resource, conversion losses and emission
factors through a 10 000-iteration Monte Carlo simulation, reporting all
principal results as probability distributions and on a
capacity-normalised (per-MW) basis that is robust to the as-yet-unfinalised
installed capacity of the zone.

The remainder of this paper is organised as follows. Section 2 describes
the study area, including its geographic, bathymetric and seismotectonic
setting. Section 3 details the data and methods. Section 4 presents the
wind resource, energy production, uncertainty and avoided-emission results.
Section 5 discusses these findings in the context of the international
literature and Turkish energy policy, together with the study's
limitations, and Section 6 concludes.

---

### References cited in this section (to be formatted to journal style)

- Argın, M., Yerci, V. (2015). The assessment of offshore wind power
  potential of Turkey. *9th Int. Conf. on Electrical and Electronics
  Engineering (ELECO)*, IEEE, 966–970.
- Argın, M., Yerci, V., Erdoğan, N., Küçüksarı, S., Çalı, Ü. (2019).
  Exploring the offshore wind energy potential of Turkey based on
  multi-criteria site selection. *Energy Strategy Reviews*, 23, 33–46.
- Bonou, A., Laurent, A., Olsen, S.I. (2016). Life cycle assessment of
  onshore and offshore wind energy. *Applied Energy*, 180, 327–337.
- Demirci, A. (2026). A comprehensive review of potential locations,
  foundation design, and seismic considerations for installation of
  offshore wind farms in Türkiye. *IET Renewable Power Generation*.
  [verify author initials and pages]
- Duzcan / Düzcan, ?, Kara, ? (2022). Offshore wind energy potential
  analysis of Turkish Marmara and Aegean seas. *International Journal of
  Environmental Science and Technology*. [verify authors/pages]
- Emeksiz, C., Demirci, B. (2019). The determination of offshore wind
  energy potential of Turkey by using a novel hybrid site selection method.
  *Sustainable Energy Technologies and Assessments*, 36, 100562.
- Genç, M.S., Karipoğlu, F., Koca, K., Azgın, Ş.T. (2021). Suitable site
  selection for offshore wind farms in Turkey's seas: GIS-MCDM based
  approach. *Earth Science Informatics*, 14(3), 1213–1225.
- Görmüş, T., Aydoğan, B., Ayat, B. (2022). Offshore wind power potential
  analysis for different wind turbines in the Mediterranean Region,
  1959–2020. *Energy Conversion and Management*, 274, 116470.
- IPCC (2025). [Life-cycle emissions of generation technologies.] — verify.
- Republic of Türkiye MENR / EVÇED (2024). *Türkiye Ulusal Elektrik
  Şebekesi Emisyon Faktörü Bilgi Formu (2023)*.
- Tercan, E., et al. (2020). [GIS multi-criteria offshore wind siting,
  Aegean.] — verify full citation.
- World Bank (2024). *Offshore Wind Roadmap for Türkiye*. ESMAP.

*Note: the national consumption figure (347.9 TWh, 2024) and grid emission
factors are verified (TEİAŞ/TEDAŞ; MENR/EVÇED). Several literature citations
are marked "verify" — author initials, years and page ranges must be
confirmed against the originals before submission. Demirci (2026) is highly
relevant (it covers seismic considerations for Turkish OWF, connecting to
the Ganos-fault discussion in Section 2.4) and should be read in full.*
