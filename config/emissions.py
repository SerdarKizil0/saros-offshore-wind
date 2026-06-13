"""
Emission factors — CO2 only (per user decision, focused scope)
===============================================================
Two datasets, both now verified against authoritative sources:

  (1) Türkiye national grid CO2 emission factor.
      OFFICIAL — Republic of Türkiye Ministry of Energy and Natural
      Resources (ETKB), Energy Efficiency and Environment Dept (EVÇED),
      "Türkiye Ulusal Elektrik Şebekesi Emisyon Faktörü", 2023 form,
      computed per IPCC Tool07 methodology.

  (2) Offshore wind life-cycle CO2 (per kWh, cradle-to-grave).
      Bonou et al. (2016, Applied Energy) + IPCC AR6/2025 range.

The avoided-emission framing uses the official COMBINED MARGIN factor
for wind/solar as the primary value, with the generation-average as a
conservative lower bound and the operating margin as an upper bound.
This bracket is sampled in the Monte Carlo step.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Factor:
    best: float      # deterministic / median (mode for triangular)
    low:  float      # conservative bound (≈ P5)
    high: float      # upper bound (≈ P95)
    unit: str
    source: str


# ====================================================================
# (1) Türkiye grid CO2 — OFFICIAL (ETKB/EVÇED 2023)
# ====================================================================
# Three official figures, all in tCO2/MWh → ×1000 = gCO2/kWh:
#   • Generation average        : 0.434  →  434  (attributional, conservative)
#   • Combined margin wind/solar : 0.6242 →  624  (PRIMARY — official avoided-EF)
#   • Operating (activity) margin: 0.7134 →  713  (consequential, upper bound)
# Source: "2023 Türkiye Ulusal Elektrik Şebekesi Emisyon Faktörü Bilgi
#          Formu", ETKB EVÇED; IPCC Grid EF Tool07.V07.
GRID_CO2 = Factor(
    best=624.2,   # combined margin for wind/solar (official, primary)
    low=434.0,    # generation average (conservative)
    high=713.4,   # operating/activity margin (upper)
    unit="gCO2-eq / kWh",
    source="ETKB/EVÇED 2023, Türkiye Ulusal Elektrik Şebekesi Emisyon "
           "Faktörü (IPCC Tool07): combined margin 0.6242, generation "
           "average 0.434, operating margin 0.7134 tCO2/MWh",
)

# Fuel-specific official CO2 factors (gCO2-eq/kWh), 2023 — for the
# conventional-mix narrative / breakdown if needed.
GRID_CO2_BY_FUEL = {
    "natural_gas":  405.0,   # 0.405 tCO2/MWh
    "imported_coal": 803.0,  # 0.803
    "lignite":      1133.0,  # 1.133
}

# Türkiye 2023 generation mix (% of total), for reporting context.
# Source: EPDK 2023/2024 sector report; Ember Climate verified.
TR_GENERATION_MIX_PCT = {
    "natural_gas":  21.0,
    "coal_lignite": 36.0,
    "hydro":        19.0,
    "wind":         10.5,
    "solar":         7.0,
    "geothermal":    3.3,
    "biomass":       2.3,
    "other":         0.9,
}


# ====================================================================
# (2) Offshore wind life-cycle CO2 (per kWh delivered)
# ====================================================================
# Fixed-bottom monopile, ~9.5 MW class, 25-yr lifetime, no recycling
# credit (conservative).
#   • Bonou et al. 2016 (Applied Energy 180:327): ~11 gCO2-eq/kWh
#   • IPCC 2025: offshore range 8–14 gCO2-eq/kWh
#   • Garrett & Rønde / others cluster around 11–12
OFFSHORE_WIND_CO2 = Factor(
    best=11.0,
    low=8.0,
    high=14.0,
    unit="gCO2-eq / kWh",
    source="Bonou et al. 2016 (Applied Energy); IPCC 2025 range 8–14 "
           "gCO2-eq/kWh for offshore wind",
)


def avoided_co2_per_kwh(grid: float = None, wind_lca: float = None) -> float:
    """Net avoided CO2 per kWh of wind generation (gCO2-eq/kWh)."""
    g = GRID_CO2.best if grid is None else grid
    w = OFFSHORE_WIND_CO2.best if wind_lca is None else wind_lca
    return g - w


# ====================================================================
# Context references (energy basis, not emissions)
# ====================================================================
# Türkiye 2024 total electricity consumption (TEİAŞ/TEDAŞ).
TR_TOTAL_CONSUMPTION_TWH_2024 = 347.9

# Türkiye 2035 offshore wind target.
# Source: T.C. ETKB 2035 Renewable Energy Roadmap (Oct 2024);
# World Bank Offshore Wind Roadmap for Türkiye (Nov 2024).
TR_OFFSHORE_TARGET_2035_GW = 5.0


if __name__ == "__main__":
    print("Türkiye grid CO2 (official ETKB/EVÇED 2023):")
    print(f"  PRIMARY (combined margin wind): {GRID_CO2.best} {GRID_CO2.unit}")
    print(f"  range: [{GRID_CO2.low} (gen avg), {GRID_CO2.high} (op margin)]")
    print(f"\nOffshore wind LCA CO2:")
    print(f"  {OFFSHORE_WIND_CO2.best} {OFFSHORE_WIND_CO2.unit} "
          f"[{OFFSHORE_WIND_CO2.low}, {OFFSHORE_WIND_CO2.high}]")
    print(f"\nNet avoided per kWh (best): "
          f"{avoided_co2_per_kwh():.1f} gCO2-eq/kWh")
    print(f"  = {avoided_co2_per_kwh()/1000:.4f} kg/kWh "
          f"= {avoided_co2_per_kwh():.0f} tCO2/GWh")
