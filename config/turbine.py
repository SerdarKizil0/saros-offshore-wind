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


POWER_CURVE_MS_KW: list[tuple[float, float]] = [
    (0.0, 0), (3.0, 0), (3.5, 60), (4.0, 170), (4.5, 340), (5.0, 570),
    (5.5, 900), (6.0, 1310), (6.5, 1800), (7.0, 2350), (7.5, 2980),
    (8.0, 3690), (8.5, 4480), (9.0, 5320), (9.5, 6180), (10.0, 7050),
    (10.5, 7870), (11.0, 8550), (11.5, 9050), (12.0, 9350), (12.5, 9450),
    (13.0, 9500), (14.0, 9500), (20.0, 9500), (25.0, 9500),
    (25.01, 0), (30.0, 0),
]


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
