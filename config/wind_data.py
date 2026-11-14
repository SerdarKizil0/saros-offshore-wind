"""
Wind input series for the production pipeline (since Phase 5-PRE-B, 14.11.2026)
================================================================================
Single source of truth for which ERA5 series the revised pipeline reads.

PRIMARY
    ERA5 1994-2024 at 40.50 N 26.25 E, obtained through the Open-Meteo
    historical API (calibrated against the CDS series; NOT bit-identical to
    a CDS download). Author decision, Phase 5-PRE-B.

HISTORICAL_CDS_2014_2024
    The original CDS-derived 2014-2024 series at the same node. Kept for
    comparison and to reproduce the historical results archived in
    the results archive folder baseline_2014_2024_cds. Never mixed with the primary.

Both files are pinned by SHA-256; scripts/04 refuses a file whose checksum
differs from the pin.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class WindSeries:
    key: str
    path: Path
    sha256: str
    storage: str                  # "openmeteo_int16" | "cds_processed_float32"
    period: tuple[int, int]
    node_lat: float
    node_lon: float
    data_product: str
    source_label: str             # used verbatim in output metadata

    @property
    def period_label(self) -> str:
        return f"{self.period[0]}-{self.period[1]}"

    @property
    def n_years(self) -> int:
        return self.period[1] - self.period[0] + 1

    @property
    def rel_path(self) -> str:
        try:
            return str(self.path.relative_to(ROOT))
        except ValueError:
            return str(self.path)


PRIMARY = WindSeries(
    key="primary_era5_openmeteo_1994_2024",
    path=ROOT / "data/external/era5_openmeteo/era5_openmeteo_40.50N_26.25E_1994_2024.parquet",
    sha256="34032f0761725097363b526be53937bbb4077571577d557881ce550eff0aada6",
    storage="openmeteo_int16",
    period=(1994, 2024),
    node_lat=40.50, node_lon=26.25,
    data_product="ECMWF ERA5 hourly single levels (10 m and 100 m wind) via the Open-Meteo historical-weather "
                 "API (models=era5, nearest 0.25 deg cell); lossy redistribution, calibrated against the CDS "
                 "series over 2014-2024 (Phase 5-PRE), not bit-identical to CDS",
    source_label="ERA5 hourly via Open-Meteo (calibrated; not bit-identical to CDS), "
                 "nearest 0.25 deg node (40.50N, 26.25E) to the polygon centroid",
)

HISTORICAL_CDS_2014_2024 = WindSeries(
    key="historical_cds_2014_2024",
    path=ROOT / "data/processed/wind_hub_105m.parquet",
    sha256="0cfc4742010acbc8cbdac4090527589393ab8b2858aaaa5d92cfc9fbfc1916a5",
    storage="cds_processed_float32",
    period=(2014, 2024),
    node_lat=40.50, node_lon=26.25,
    data_product="ECMWF ERA5 hourly single levels from the Copernicus CDS (scripts/02-03)",
    source_label="ERA5 hourly, nearest 0.25 deg node (40.50N, 26.25E) to the polygon centroid",
)

SERIES = {s.key: s for s in (PRIMARY, HISTORICAL_CDS_2014_2024)}
