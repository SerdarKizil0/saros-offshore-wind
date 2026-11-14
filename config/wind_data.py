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


# --------------------------------------------------------------------------
# Sensitivity inputs (since Phase 5B-0): ERA5 via Open-Meteo, 1979-2024, at the
# primary node and its two neighbours on the 40.50 N row. Speeds only (U10,
# U100; int16 centi-m/s; row i = 1979-01-01 00:00 UTC + i hours). Used ONLY by
# scripts/08 for the period-selection and grid-node sensitivity experiments.
# They never replace the primary series; the node "C" file is checked to be
# identical to the primary over 1994-2024 on every run.
# Provenance: data/external/phase5pre/README.md and MANIFEST.json.
# --------------------------------------------------------------------------
_P5 = ROOT / "data/external/phase5pre"
_NODE_PRODUCT = ("ECMWF ERA5 hourly 10 m and 100 m wind speed via the Open-Meteo historical-weather API "
                 "(models=era5, nearest 0.25 deg cell); calibrated at node C against the CDS series, "
                 "not bit-identical to CDS")


def _node(key, lon, sha):
    return WindSeries(key=f"sensitivity_node_{key}", storage="openmeteo_int16_speeds", period=(1979, 2024),
                      path=_P5 / f"era5_openmeteo_40.50N_{lon:.2f}E_1979_2024.parquet", sha256=sha,
                      node_lat=40.50, node_lon=lon, data_product=_NODE_PRODUCT,
                      source_label=f"ERA5 hourly via Open-Meteo, 0.25 deg node (40.50N, {lon:.2f}E)")


NODE_SERIES = {
    "W": _node("W", 26.00, "9135bd806f3e5828a4d0f29d3af5174dd19c2b29864191b41a4ca0489e1cc0ae"),
    "C": _node("C", 26.25, "c3ce1d44c9679f6ba75ca2c82b467e18f683a122e6f1a3a7d83a85442aac0fb2"),
    "E": _node("E", 26.50, "0df4cb82a0c8e788a2146f2263871da4c56240f45ea4a5fdb4ca7f7e42e707af"),
}
PRIMARY_NODE = "C"

# Static inputs of the sensitivity step, pinned by SHA-256: (path, sha256)
ERA5_LAND_SEA_MASK = (_P5 / "era5_land_sea_mask_saros.json",
                      "1d7f1090d7e8afbbb252af7d72814cd76faa34e54e405d5950fe7cd6c3300fe0")
GWA4_WIND_SPEED_100M = (ROOT / "docs/review/phase2b_data/gwa4_wind-speed_100m_saros.tif",
                        "960ecf52bf23bb570781a9a4d8d08c41217e51b967fe2c9099d739d93be62eed")
EMODNET_NODE_BOX = (ROOT / "docs/review/phase2b_data/emodnet_dtm2024_era5cell_x0.25.tif",
                    "5a0095a3cd87e525f96b055bc87cd5f26e025f7917371f6d1d0cf3033b7ad42b")
