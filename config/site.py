"""
Site configuration — Saros DÜRES (Bakanlık YEKA İlanı, 14 May 2026)
====================================================================
Single source of truth for the study site geometry.

EVERYTHING is derived from one list: SAROS_POLYGON_LONLAT (27 vertices).
Centroid, area, bounding box and the ERA5 request box are all computed
from those vertices at import time — there are no hand-typed geometry
numbers that could drift out of sync.

The polygon was supplied by MENR as a KML file (SAROS_DÜRES.kml).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path


# --------------------------------------------------------------------
# The ONE source of truth: 27 polygon vertices, (longitude, latitude)
# WGS84.  Source: SAROS_DÜRES.kml (MENR, 14 May 2026).
# --------------------------------------------------------------------
SAROS_POLYGON_LONLAT: list[tuple[float, float]] = [
    (26.4609, 40.5938), (26.4495, 40.5727), (26.4223, 40.5721),
    (26.3787, 40.5707), (26.3184, 40.5709), (26.3168, 40.5586),
    (26.2930, 40.5554), (26.2603, 40.5564), (26.2438, 40.5520),
    (26.2268, 40.5405), (26.2110, 40.5146), (26.2042, 40.5100),
    (26.1794, 40.5071), (26.1545, 40.5048), (26.1359, 40.5040),
    (26.1164, 40.5065), (26.1009, 40.5158), (26.0950, 40.5187),
    (26.0815, 40.5152), (26.0692, 40.5227), (26.0490, 40.5339),
    (26.0385, 40.5337), (26.0825, 40.5986), (26.1374, 40.5826),
    (26.2242, 40.5892), (26.3022, 40.5809), (26.3843, 40.5942),
]

# ERA5 request buffer around the polygon (degrees). 0.05° ≈ 5.5 km,
# guarantees the polygon's interior grid cells are well inside the box.
ERA5_BUFFER_DEG = 0.05


# --------------------------------------------------------------------
# Geometry helpers (computed once at import)
# --------------------------------------------------------------------
def _polygon_bounds(poly):
    lons = [p[0] for p in poly]
    lats = [p[1] for p in poly]
    return min(lons), max(lons), min(lats), max(lats)


def _polygon_centroid_and_area(poly):
    """Equirectangular projection + shoelace. Returns (lon_c, lat_c, area_km2)."""
    R = 6371.0
    d2r = math.pi / 180.0
    lon0 = sum(p[0] for p in poly) / len(poly)
    lat0 = sum(p[1] for p in poly) / len(poly)

    xs, ys = [], []
    for lon, lat in poly:
        x = (lon - lon0) * d2r * R * math.cos(lat0 * d2r)
        y = (lat - lat0) * d2r * R
        xs.append(x); ys.append(y)

    n = len(poly)
    a2 = 0.0   # twice signed area
    cx = cy = 0.0
    for i in range(n):
        j = (i + 1) % n
        cross = xs[i] * ys[j] - xs[j] * ys[i]
        a2 += cross
        cx += (xs[i] + xs[j]) * cross
        cy += (ys[i] + ys[j]) * cross
    area = a2 / 2.0
    if abs(area) < 1e-9:
        # Degenerate; fall back to bbox center
        return lon0, lat0, 0.0
    cx /= (3.0 * a2)
    cy /= (3.0 * a2)
    # back to lon/lat
    lon_c = lon0 + cx / (d2r * R * math.cos(lat0 * d2r))
    lat_c = lat0 + cy / (d2r * R)
    return lon_c, lat_c, abs(area)


_LON_MIN, _LON_MAX, _LAT_MIN, _LAT_MAX = _polygon_bounds(SAROS_POLYGON_LONLAT)
_LON_C, _LAT_C, _AREA_KM2 = _polygon_centroid_and_area(SAROS_POLYGON_LONLAT)

_R = 6371.0
_d2r = math.pi / 180.0
_EW_KM = (_LON_MAX - _LON_MIN) * _d2r * _R * math.cos(_LAT_C * _d2r)
_NS_KM = (_LAT_MAX - _LAT_MIN) * _d2r * _R


# --------------------------------------------------------------------
@dataclass(frozen=True)
class SarosSite:
    """Saros DÜRES site specification. All geometry derived from vertices."""

    name: str = "Saros DÜRES"
    full_name: str = "Saros Bay Offshore Wind YEKA Candidate Zone"
    source: str = "MENR YEKA İlanı, 14 May 2026 (KML)"
    country: str = "Türkiye"
    region: str = "North Aegean Sea"
    nearest_landfall: str = "Gelibolu Peninsula"

    # Derived geometry
    n_vertices: int = len(SAROS_POLYGON_LONLAT)
    area_km2: float = round(_AREA_KM2, 1)
    centroid_lat: float = round(_LAT_C, 4)
    centroid_lon: float = round(_LON_C, 4)
    lat_min: float = round(_LAT_MIN, 4)
    lat_max: float = round(_LAT_MAX, 4)
    lon_min: float = round(_LON_MIN, 4)
    lon_max: float = round(_LON_MAX, 4)
    ew_extent_km: float = round(_EW_KM, 1)
    ns_extent_km: float = round(_NS_KM, 1)

    # ERA5 request box = polygon bounds + buffer
    era5_north: float = round(_LAT_MAX + ERA5_BUFFER_DEG, 4)
    era5_west:  float = round(_LON_MIN - ERA5_BUFFER_DEG, 4)
    era5_south: float = round(_LAT_MIN - ERA5_BUFFER_DEG, 4)
    era5_east:  float = round(_LON_MAX + ERA5_BUFFER_DEG, 4)

    # Reference period
    era5_start_year: int = 2014
    era5_end_year:   int = 2024
    era5_n_years:    int = 11

    @property
    def era5_area_request(self) -> list[float]:
        """ERA5 'area' parameter order: [North, West, South, East]."""
        return [self.era5_north, self.era5_west,
                self.era5_south, self.era5_east]

    @property
    def years(self) -> list[int]:
        return list(range(self.era5_start_year, self.era5_end_year + 1))

    @property
    def polygon(self) -> list[tuple[float, float]]:
        return list(SAROS_POLYGON_LONLAT)


# The module-level object the rest of the project imports.
SITE = SarosSite()


# --------------------------------------------------------------------
# Project directories
# --------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR     = PROJECT_ROOT / "data"
ERA5_DIR     = DATA_DIR / "era5"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR  = PROJECT_ROOT / "results"
FIGURES_DIR  = PROJECT_ROOT / "figures"

for _d in (DATA_DIR, ERA5_DIR, PROCESSED_DIR, RESULTS_DIR, FIGURES_DIR):
    _d.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Site: {SITE.full_name}")
    print(f"  Source     : {SITE.source}")
    print(f"  Vertices   : {SITE.n_vertices}")
    print(f"  Centroid   : {SITE.centroid_lat}°N, {SITE.centroid_lon}°E")
    print(f"  Area       : {SITE.area_km2} km²")
    print(f"  Extent     : {SITE.ew_extent_km} × {SITE.ns_extent_km} km")
    print(f"  Poly bbox  : lat [{SITE.lat_min}, {SITE.lat_max}], "
          f"lon [{SITE.lon_min}, {SITE.lon_max}]")
    print(f"  ERA5 bbox  : N={SITE.era5_north} W={SITE.era5_west} "
          f"S={SITE.era5_south} E={SITE.era5_east}")
    print(f"  ERA5 period: {SITE.era5_start_year}–{SITE.era5_end_year} "
          f"({SITE.era5_n_years} years)")
    print(f"  Project root: {PROJECT_ROOT}")
    print(f"\n  ✓ SITE object is defined and importable.")
