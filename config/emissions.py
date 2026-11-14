"""
Emission factors — authoritative values for the revised pipeline (Phase 4B)
============================================================================
All grid factors are static 2023 historical values published by the
Republic of Türkiye Ministry of Energy and Natural Resources (ETKB),
Energy Efficiency and Environment Department (EVÇED). They are not
forecasts. Verified against the PDFs in docs/review/PHASE3B_CARBON_ACCOUNTING.md.

Accounting structure (do not mix):
  * PRIMARY   avoided operational grid CO2 = energy x combined margin
              (wind/solar), tCO2/MWh, CO2 only.
  * CONTEXT   operating margin, build margin, generation average: different
              accounting conventions, NOT statistical bounds.
  * SECONDARY offshore-wind life-cycle GHG, tCO2-eq, reported separately and
              never subtracted from the CO2-only grid factor (different gases
              and system boundaries).
"""
from __future__ import annotations

from dataclasses import dataclass

URL_GRID_2023 = ("https://enerji.gov.tr/Media/Dizin/EVCED/tr/%C3%87evreVe%C4%B0klim/"
                 "%C4%B0klimDe%C4%9Fi%C5%9Fikli%C4%9Fi/TUESEmisyonFktr/Belgeler/Sebeke_EF_Bilgi_Formu_2023.pdf")
URL_GEN_2023 = ("https://enerji.gov.tr/Media/Dizin/EVCED/tr/%C3%87evreVe%C4%B0klim/"
                "%C4%B0klimDe%C4%9Fi%C5%9Fikli%C4%9Fi/EmisyonFaktorleri/"
                "2023_Turkiye_Elektrik_UretimiveElektrik_Tuketim_Noktasi_Emisyon_Faktorleri.pdf")


@dataclass(frozen=True)
class GridFactor:
    value: float          # t per MWh
    unit: str             # "tCO2/MWh" or "tCO2-eq/MWh"
    role: str
    source: str


# ---------------------------------------------------------------- grid, 2023
GRID_EF_2023: dict[str, GridFactor] = {
    "combined_margin_wind_solar": GridFactor(
        0.6242, "tCO2/MWh", "PRIMARY: official factor published for GHG-reduction calculations "
        "of wind/solar generation (may be used; not mandated)",
        "ETKB-EVÇED-FRM-039 Rev.03, period 2023, publ. 26.12.2025, UNFCCC CDM Tool 07 v07.0"),
    "operating_margin": GridFactor(
        0.7134, "tCO2/MWh", "context: short-run displacement of existing generation",
        "ETKB-EVÇED-FRM-039 Rev.03 (2023)"),
    "build_margin": GridFactor(
        0.3567, "tCO2/MWh", "context: recent capacity additions",
        "ETKB-EVÇED-FRM-039 Rev.03 (2023)"),
    "generation_average_co2": GridFactor(
        0.430, "tCO2/MWh", "context: attributional average of all generation",
        "ETKB-EVÇED-FRM-042 Rev.01, period 2023, publ. 26.12.2025 (IEA method)"),
    "generation_average_co2eq": GridFactor(
        0.434, "tCO2-eq/MWh", "context, different unit: average incl. CH4 and N2O",
        "ETKB-EVÇED-FRM-042 Rev.01 (2023)"),
}
PRIMARY_GRID_FACTOR = "combined_margin_wind_solar"
CM_TOOL07_WEIGHTS_WIND_SOLAR = (0.75, 0.25)     # OM, BM

# Fuel-specific generation factors 2023 (FRM-042), both columns. Not used in
# the revised pipeline; the former fuel-mix scenario is retired.
FUEL_EF_2023 = {
    "lignite":       {"tCO2/MWh": 1.122, "tCO2-eq/MWh": 1.133},
    "hard_coal":     {"tCO2/MWh": 1.045, "tCO2-eq/MWh": 1.050},
    "imported_coal": {"tCO2/MWh": 0.800, "tCO2-eq/MWh": 0.803},
    "natural_gas":   {"tCO2/MWh": 0.400, "tCO2-eq/MWh": 0.405},
}

# ------------------------------------------- offshore wind life-cycle, gCO2-eq/kWh
# = kgCO2-eq/MWh. Literature values for other sites; not Saros-specific.
LIFECYCLE_GHG_G_PER_KWH = {
    "ipcc_ar5_min": 8.0,       # IPCC AR5 WGIII Annex III (Schlömer et al. 2014), Table A.III.2
    "ipcc_ar5_median": 12.0,   # reference value used for the secondary metric
    "ipcc_ar5_max": 35.0,
    "bonou2016_6MW": 7.8,      # Bonou et al. 2016, Table 4 (10 m/s site, EoL recycling credited)
    "bonou2016_4MW": 10.9,     # Bonou et al. 2016, Table 4 (9.5 m/s site, EoL recycling credited)
}
LIFECYCLE_REFERENCE = "ipcc_ar5_median"

# --------------------------------------------------------- context references
TR_OFFSHORE_TARGET_2035_GW = 5.0           # Türkiye Ulusal Enerji Planı 2022 (MENR): 2035 wind 29.6 GW
                                           # = 24.6 GW onshore + 5 GW offshore (planning projection)

# National electricity consumption used for the optional share metric (Phase 5B-0).
# Supersedes the unverified 347.9 TWh used until Phase 5-PRE-B (secondary sources only).
TR_GROSS_CONSUMPTION_2024 = {
    "year": 2024,
    "gwh": 353579.8,
    "definition": "gross consumption ('Türkiye tüketimi') = gross generation + imports - exports; it includes "
                  "power-plant internal use and transmission and distribution losses",
    "components_gwh": {"gross_generation": 354570.2, "imports": 2681.6, "exports": 3671.9},
    "net_consumption_gwh_not_used": 308673.9,
    "source": "TEDAŞ, 2025 Yılı Türkiye Elektrik Dağıtımı Sektör Raporu, Table 5 'Türkiye Elektrik Tüketimi "
              "(2020-2024)' (data: TEİAŞ)",
    "url": "https://www.tedas.gov.tr/FileUpload/MediaFolder/4f817ff3-1429-4ba2-86c7-d5afd7f9ea5d.pdf",
    "document_sha256": "72f0219337eadfb6a3a3292e5ffd98df4daae38bd9d145e2280816d11882b949",
    "verified": "Phase 5-PRE-C (docs/review/PHASE5PRE_C_NOVELTY_SOURCE_AUDIT.md)",
}


# ============================================================================
# LEGACY — retained only so archived results and the Phase 2A rerun stay
# reproducible. Do not use in the active pipeline. These objects mix
# accounting methods and units (434 is CO2-eq; 624.2 and 713.4 are CO2) and
# the "8-14" life-cycle range is not the IPCC AR5 range (8-35).
# ============================================================================
@dataclass(frozen=True)
class Factor:
    best: float
    low: float
    high: float
    unit: str
    source: str


GRID_CO2 = Factor(best=624.2, low=434.0, high=713.4, unit="g/kWh (mixed CO2 / CO2-eq — LEGACY)",
                  source="LEGACY triangular mixture used by the retired Monte Carlo")
OFFSHORE_WIND_CO2 = Factor(best=11.0, low=8.0, high=14.0, unit="gCO2-eq/kWh (LEGACY range)",
                           source="LEGACY; see LIFECYCLE_GHG_G_PER_KWH for verified values")
