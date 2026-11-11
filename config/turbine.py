"""
Turbine configuration — Vestas V164-9.5 MW + capacity scenarios
================================================================
Reference machine for most peer-reviewed Aegean/Mediterranean offshore
wind studies. Capacity is reported per-MW (primary) plus scenarios.
"""
from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=True)
class Turbine:
    manufacturer: str = "Vestas"
    model: str = "V164-9.5 MW"
    rated_power_mw: float = 9.5
    rotor_diameter_m: float = 164.0
    hub_height_m: float = 105.0
    swept_area_m2: float = field(default_factory=lambda: np.pi * (164.0/2)**2)
    cut_in_ms: float = 3.5
    rated_ms: float = 14.0
    cut_out_ms: float = 25.0


# --------------------------------------------------------------------
# Power curves (hub-height free-stream wind speed in m/s, electrical kW)
# --------------------------------------------------------------------
# ACTIVE (Phase 2A, provisional): OEDB turbine library row "V164/9500".
#   Source  : Open Energy Database turbine library, distributed with
#             windpowerlib (github.com/wind-python/windpowerlib, branch dev,
#             commit 191d8ca, file windpowerlib/oedb/power_curves.csv).
#   Origin  : third-party digitisation ("engauge digitizer") of the power
#             curve graph published by MHI Vestas (mhivestasoffshore.com;
#             thewindpower.net). NOT a manufacturer-certified table.
#   Basis   : air density not documented; standard 1.225 kg/m3 assumed.
#   Values  : OEDB W converted to kW (/1000), every OEDB point 0-24.5 m/s,
#             unchanged. Copy kept in docs/review/phase1_data/.
#   Checks  : 0 kW up to 3.0 m/s, 115 kW at 3.5 m/s (cut-in), 9500 kW
#             first reached at 14.0 m/s (= rated_ms), peak electrical
#             Cp 0.476 at 8.5 m/s (rho 1.225, A = 21 124 m2).
#   Boundary: the OEDB table ends at 24.5 m/s. (25.0, 9500) holds the
#             rated plateau to the 25 m/s cut-out stated by Vestas, and
#             (25.01, 0), (30.0, 0) reproduce the cut-out convention of
#             the original curve. These three points are not OEDB data.
# See docs/review/PHASE1_TECHNICAL_VALIDATION.md and PHASE2A_POWER_CURVE.md.
POWER_CURVE_OEDB_V164_9500_MS_KW: list[tuple[float, float]] = [
    (0.0, 0.0), (0.5, 0.0), (1.0, 0.0), (1.5, 0.0), (2.0, 0.0), (2.5, 0.0),
    (3.0, 0.0), (3.5, 115.0), (4.0, 249.0), (4.5, 430.0), (5.0, 613.0),
    (5.5, 900.0), (6.0, 1226.0), (6.5, 1600.0), (7.0, 2030.0),
    (7.5, 2570.0), (8.0, 3123.0), (8.5, 3784.0), (9.0, 4444.0),
    (9.5, 5170.0), (10.0, 5900.0), (10.5, 6600.0), (11.0, 7299.0),
    (11.5, 7960.0), (12.0, 8601.0), (12.5, 9080.0), (13.0, 9272.0),
    (13.5, 9410.0), (14.0, 9500.0), (15.0, 9500.0), (15.5, 9500.0),
    (16.0, 9500.0), (16.5, 9500.0), (17.0, 9500.0), (17.5, 9500.0),
    (18.0, 9500.0), (18.5, 9500.0), (19.0, 9500.0), (19.5, 9500.0),
    (20.0, 9500.0), (20.5, 9500.0), (21.0, 9500.0), (21.5, 9500.0),
    (22.0, 9500.0), (22.5, 9500.0), (23.0, 9500.0), (23.5, 9500.0),
    (24.0, 9500.0), (24.5, 9500.0),
    # --- boundary points (not OEDB data, see header) ---
    (25.0, 9500.0), (25.01, 0.0), (30.0, 0.0),
]

# RETIRED: curve used for all results published before Phase 2A
# (results/archive/baseline_original_curve/). Undocumented provenance,
# reaches 9500 kW at 13 m/s (inconsistent with rated_ms = 14.0) and
# implies electrical Cp up to 0.564. Kept only for baseline comparison
# and regression tests; do not use for production.
POWER_CURVE_ORIGINAL_MS_KW: list[tuple[float, float]] = [
    (0.0, 0), (3.0, 0), (3.5, 60), (4.0, 170), (4.5, 340), (5.0, 570),
    (5.5, 900), (6.0, 1310), (6.5, 1800), (7.0, 2350), (7.5, 2980),
    (8.0, 3690), (8.5, 4480), (9.0, 5320), (9.5, 6180), (10.0, 7050),
    (10.5, 7870), (11.0, 8550), (11.5, 9050), (12.0, 9350), (12.5, 9450),
    (13.0, 9500), (14.0, 9500), (20.0, 9500), (25.0, 9500),
    (25.01, 0), (30.0, 0),
]

# The curve every pipeline script uses.
POWER_CURVE_ID = "OEDB_V164_9500"
POWER_CURVE_MS_KW: list[tuple[float, float]] = POWER_CURVE_OEDB_V164_9500_MS_KW


@dataclass(frozen=True)
class CapacityScenario:
    name: str
    n_turbines: int
    description: str

    @property
    def installed_mw(self) -> float:
        return self.n_turbines * 9.5


SCENARIOS: list[CapacityScenario] = [
    CapacityScenario("S1_pilot",   26, "Pilot first-phase commissioning (~250 MW)"),
    CapacityScenario("S2_phase1",  53, "Reasonable first allocation (~500 MW)"),
    CapacityScenario("S3_phase2", 105, "Full Phase-2 deployment (~1 GW, illustrative total)"),
    CapacityScenario("S4_max",    183, "Theoretical maximum (7D×5D layout, ~1.74 GW)"),
]
DEFAULT_SCENARIO = SCENARIOS[2]

WAKE_LOSS_DEFAULT = 0.08
AVAILABILITY_DEFAULT = 0.95
ELECTRICAL_LOSS_DEFAULT = 0.03

TURBINE = Turbine()
