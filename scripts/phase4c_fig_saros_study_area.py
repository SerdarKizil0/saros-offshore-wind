"""
Phase 4C — Figure 2: Saros study area and environmental constraints
===================================================================
One map panel in WGS 84 / UTM zone 35N (EPSG:32635), drawn from local,
verified data only (no network access, no hand-drawn geometry):

  candidate zone   docs/review/phase1_data/SAROS_DURES_official.kml
                   (MENR candidate-YEKA notice, 13 May 2026)
  bathymetry       docs/review/phase1_data/emodnet_dtm2024_saros_crop.tif
                   (EMODnet DTM 2024, elevation positive up, LAT datum)
  Saros ÖÇK        boundary points of Decision 2010/1089, as encoded in
                   scripts/phase4a_site_checks.py (datum not stated in the
                   annex: read as WGS 84, so the overlay is approximate)
  ERA5 node        results/revised/site_screening.json

What is drawn
  * water depth = -elevation, on a square-root colour scale, with the 10 m
    and 50 m isobaths (the depth screening classes of Phase 4A) set apart
    from the deeper reference isobaths;
  * land = cells with elevation >= 0 (the Phase 4A rule), coastline = 0 m
    isoline. Display generalisation only: land islets and enclosed water
    pockets smaller than MIN_FEATURE_CELLS cells are not drawn;
  * the candidate-zone outline, the reconstructed ÖÇK boundary (dashed, only
    where it really runs: the map frame is never drawn as an ÖÇK edge), and
    the part of the zone inside the ÖÇK (hatched);
  * the ERA5 grid node used by the energy model and the zone centroid as
    separate symbols, with the node's distance to the zone boundary.
No turbine positions, layout, cable route or project footprint are drawn.

All areas and distances are computed in EPSG:32635 and cross-checked against
results/revised/site_screening.json (raster-count values) and geodesic
values on the WGS 84 ellipsoid; the script stops if they disagree.

Writes, at exactly 180 mm wide:
  figures/revised/saros_study_area.pdf   vector; bathymetry layer embedded as an image
  figures/revised/saros_study_area.svg   vector; text kept as text
  figures/revised/saros_study_area.png   600 dpi
  figures/revised/saros_study_area_caption.md

Style: config/figure_style.py (shared with Figure 1).
Run from the repository root:  python scripts/phase4c_fig_saros_study_area.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import LinearSegmentedColormap, PowerNorm, to_hex, to_rgb
from matplotlib.legend_handler import HandlerTuple
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrow, Patch
from matplotlib.path import Path as MplPath
from pyproj import Geod, Transformer
from scipy import ndimage
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import nearest_points

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import figure_style as fs
from config.figure_style import (AXIS, BLUE, FS_AXIS, FS_NOTE, INK, MUTED, PLATE,
                                 SURFACE, VERMILLION)
from config.site import SAROS_POLYGON_LONLAT

DATA = ROOT / "docs" / "review" / "phase1_data"
KML = DATA / "SAROS_DURES_official.kml"
DTM = DATA / "emodnet_dtm2024_saros_crop.tif"
SCREENING = ROOT / "results" / "revised" / "site_screening.json"
SITE_CHECKS = ROOT / "scripts" / "phase4a_site_checks.py"
FIG_DIR = ROOT / "figures" / "revised"
STEM = "saros_study_area"

CRS_GEO, CRS_MAP = "EPSG:4326", "EPSG:32635"
CRS_LABEL = "WGS 84 / UTM zone 35N (EPSG:32635)"

# ---- figure geometry (mm) -------------------------------------------------
W_MM = fs.FULL_WIDTH_MM
LEFT_MM, RIGHT_MM, TOP_MM = 15.0, 3.0, 3.0
TICKS_MM = 7.5                         # longitude labels under the frame
KEY_MM, BOTTOM_MM = 27.0, 2.0          # legend + colour bar band
INSET_KM = 0.15                        # map frame inset from the DTM footprint

# ---- cartographic choices --------------------------------------------------
SCREEN_ISOBATHS = (10, 50)             # Phase 4A depth screening classes (not exclusions)
REF_ISOBATHS = (100, 200, 400)
DEPTH_MAX = 700.0                      # colour-scale ceiling, m (DTM minimum is -662 m)
DEPTH_GAMMA = 0.5                      # square-root scale: shelf detail without losing the trough
CBAR_TICKS = (0, 10, 50, 100, 200, 400, 600)
MIN_FEATURE_CELLS = 10                 # ≈0.1 km²; smaller islets/pockets are not drawn
SCALE_KM = (0, 5, 10)

# Contour-label anchors (lon, lat): label placement hints only, the label sits
# on the isobath point nearest to the anchor.
ISOBATH_LABEL_AT = {10: (26.005, 40.632), 50: (26.012, 40.55), 100: (26.48, 40.524),
                    200: (26.13, 40.47), 400: (26.36, 40.493)}

# ---- colours, all derived from the shared tokens ---------------------------
def _mix(a, b, t):
    a, b = np.array(to_rgb(a)), np.array(to_rgb(b))
    return to_hex((1 - t) * a + t * b)


DEPTH_CMAP = LinearSegmentedColormap.from_list(
    "saros_depth", [_mix(SURFACE, BLUE, 0.07), _mix(SURFACE, _mix(BLUE, MUTED, 0.35), 0.38),
                    _mix(BLUE, MUTED, 0.45), _mix(BLUE, INK, 0.62)])
LAND = _mix(SURFACE, AXIS, 0.20)
COAST = MUTED
ISO_SCREEN = _mix(INK, BLUE, 0.25)
ISO_REF = _mix(SURFACE, BLUE, 0.12)
ZONE = INK
OCK = VERMILLION
LW_ZONE = 1.0
HATCH_SPACING_MM, LW_HATCH = 1.1, 0.6   # ÖÇK overlap hatch, drawn as real 45° vector lines


# ---- data ------------------------------------------------------------------
def _site_checks_module():
    spec = importlib.util.spec_from_file_location("phase4a_site_checks", SITE_CHECKS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@dataclass
class MapData:
    zone_ll: list                      # KML vertices (lon, lat)
    ock_ll: list                       # ÖÇK annex vertices (lon, lat)
    era5_ll: tuple
    zone: Polygon                      # EPSG:32635, metres
    ock: Polygon
    overlap: Polygon
    era5: Point
    era5_nearest: Point                # nearest point of the zone boundary
    centroid_ll: tuple
    geodesic_area_km2: float
    geodesic_overlap_km2: float
    screening: dict
    lon: np.ndarray                    # DTM cell centres, 2-D
    lat: np.ndarray
    x: np.ndarray                      # same, EPSG:32635 metres
    y: np.ndarray
    elevation: np.ndarray              # m, positive up (EMODnet convention)
    extent: tuple                      # map frame xmin, xmax, ymin, ymax (m)

    @property
    def area_km2(self) -> float:
        return self.zone.area / 1e6

    @property
    def overlap_km2(self) -> float:
        return self.overlap.area / 1e6

    @property
    def overlap_pct(self) -> float:
        return self.overlap.area / self.zone.area * 100

    @property
    def era5_inside(self) -> bool:
        return self.zone.contains(self.era5)

    @property
    def era5_distance_km(self) -> float:
        return self.zone.exterior.distance(self.era5) / 1e3

    @property
    def depth(self) -> np.ndarray:
        """Water depth below LAT (m, positive down) = -elevation."""
        return -self.elevation


def to_map():
    return Transformer.from_crs(CRS_GEO, CRS_MAP, always_xy=True)


def to_geo():
    return Transformer.from_crs(CRS_MAP, CRS_GEO, always_xy=True)


def load_data() -> MapData:
    p4a = _site_checks_module()
    zone_ll = [tuple(map(float, p)) for p in p4a.ring()]        # official KML, full precision
    ock_ll = [tuple(map(float, p)) for p in p4a.OCK]
    screening = json.loads(SCREENING.read_text(encoding="utf-8"))
    era5_ll = tuple(map(float, screening["era5_node_representativeness"]["node_lon_lat"]))

    t = to_map()
    zone = Polygon([t.transform(*p) for p in zone_ll])
    ock = Polygon([t.transform(*p) for p in ock_ll])
    overlap = zone.intersection(ock)
    era5 = Point(t.transform(*era5_ll))
    nearest = nearest_points(zone.exterior, era5)[0]
    c = zone.centroid
    centroid_ll = to_geo().transform(c.x, c.y)
    geod = Geod(ellps="WGS84")
    g_area = abs(geod.geometry_area_perimeter(Polygon(zone_ll))[0]) / 1e6
    g_overlap = abs(geod.geometry_area_perimeter(Polygon(zone_ll).intersection(Polygon(ock_ll)))[0]) / 1e6

    with rasterio.open(DTM) as ds:
        if ds.crs.to_epsg() != 4326:
            raise ValueError(f"unexpected DTM CRS {ds.crs}")
        elevation = ds.read(1).astype(float)
        rows, cols = np.indices(elevation.shape)
        lon, lat = rasterio.transform.xy(ds.transform, rows, cols, offset="center")
        lon, lat = np.asarray(lon).reshape(elevation.shape), np.asarray(lat).reshape(elevation.shape)
        b = ds.bounds
    x, y = t.transform(lon, lat)

    # map frame: the largest axis-aligned rectangle inside the DTM footprint
    edge = np.linspace(0, 1, 50)
    left = t.transform(np.full_like(edge, b.left), b.bottom + edge * (b.top - b.bottom))
    right = t.transform(np.full_like(edge, b.right), b.bottom + edge * (b.top - b.bottom))
    bottom = t.transform(b.left + edge * (b.right - b.left), np.full_like(edge, b.bottom))
    top = t.transform(b.left + edge * (b.right - b.left), np.full_like(edge, b.top))
    pad = INSET_KM * 1e3
    extent = (max(left[0]) + pad, min(right[0]) - pad, max(bottom[1]) + pad, min(top[1]) - pad)

    d = MapData(zone_ll, ock_ll, era5_ll, zone, ock, overlap, era5, nearest, centroid_ll,
                g_area, g_overlap, screening, lon, lat, np.asarray(x), np.asarray(y),
                elevation, extent)
    problems = verify(d)
    if problems:
        raise ValueError("geometry check failed: " + "; ".join(problems))
    return d


def verify(d: MapData) -> list[str]:
    """Cross-checks between the drawn geometry and the committed screening results."""
    s = d.screening
    out = []
    if not (d.zone.is_valid and d.ock.is_valid):
        out.append("invalid polygon")
    if max(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(d.zone_ll, SAROS_POLYGON_LONLAT)) > 1e-4 \
            or len(d.zone_ll) != len(SAROS_POLYGON_LONLAT):
        out.append("KML and config/site.py vertices disagree")
    if abs(d.area_km2 / s["polygon"]["area_km2"] - 1) > 0.005:
        out.append("zone area disagrees with site_screening.json by > 0.5%")
    if abs(d.area_km2 / d.geodesic_area_km2 - 1) > 0.002:
        out.append("UTM and geodesic zone areas differ by > 0.2%")
    ref = s["protected_area_overlap"]["saros_ock_2010"]
    if abs(d.overlap_km2 / ref["overlap_km2"] - 1) > 0.02 or abs(d.overlap_pct - ref["overlap_share_pct"]) > 0.3:
        out.append("ÖÇK overlap disagrees with site_screening.json")
    if abs(d.overlap_km2 / d.geodesic_overlap_km2 - 1) > 0.002:
        out.append("UTM and geodesic overlap areas differ by > 0.2%")
    node = s["era5_node_representativeness"]
    if d.era5_inside or node["inside_polygon"]:
        out.append("ERA5 node falls inside the zone")
    if abs(d.era5_distance_km - node["distance_to_polygon_boundary_km"]) > 0.05:
        out.append("ERA5 node distance disagrees with site_screening.json")
    if np.nanmin(d.elevation) >= 0 or np.nanmax(d.elevation) <= 0:
        out.append("DTM is not elevation-positive-up with sea and land")
    zone_depth = d.depth[_zone_mask(d)]
    rng = s["bathymetry"]["depth_m"]
    if abs(zone_depth.min() - rng["min"]) > 1e-3 or abs(zone_depth.max() - rng["max"]) > 1e-3:
        out.append("depth inside the zone disagrees with site_screening.json")
    x0, x1, y0, y1 = d.extent
    if not (x0 < d.era5.x < x1 and y0 < d.era5.y < y1) or not d.zone.within(_frame(d)):
        out.append("zone or ERA5 node outside the map frame")
    return out


def _zone_mask(d: MapData) -> np.ndarray:
    return MplPath(d.zone_ll).contains_points(np.c_[d.lon.ravel(), d.lat.ravel()]).reshape(d.lon.shape)


def _frame(d: MapData) -> Polygon:
    x0, x1, y0, y1 = d.extent
    return Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def display_land(elev: np.ndarray) -> np.ndarray:
    """Elevation for the coastline only: tiny islets and enclosed pockets removed."""
    # land = elevation >= 0 (Phase 4A rule); lift exact zeros so the 0 m isoline
    # does not trace flat 0 m plateaus inside land
    e = np.where(elev >= 0, np.maximum(elev, 0.01), elev)
    land = e >= 0
    lab, n = ndimage.label(land)
    sizes = ndimage.sum(np.ones_like(e), lab, range(1, n + 1))
    for i, size in enumerate(sizes, start=1):
        if size < MIN_FEATURE_CELLS:
            e[lab == i] = -0.05
    sea = e < 0
    lab, n = ndimage.label(sea)
    sizes = ndimage.sum(np.ones_like(e), lab, range(1, n + 1))
    for i, size in enumerate(sizes, start=1):
        if size < MIN_FEATURE_CELLS:
            e[lab == i] = 0.05
    return e


# ---- drawing helpers --------------------------------------------------------
def hatch_lines(geom, spacing_m: float, angle_deg: float = 45.0) -> list[np.ndarray]:
    """Parallel lines at `angle_deg`, `spacing_m` apart, clipped exactly to `geom`."""
    cx, cy = geom.centroid.x, geom.centroid.y
    minx, miny, maxx, maxy = geom.bounds
    r = math.hypot(maxx - minx, maxy - miny)
    a = math.radians(angle_deg)
    u = np.array([math.cos(a), math.sin(a)])          # line direction
    n = np.array([-u[1], u[0]])                       # offset direction
    segs = []
    for k in np.arange(-r, r + spacing_m, spacing_m):
        p0 = np.array([cx, cy]) + k * n - r * u
        p1 = np.array([cx, cy]) + k * n + r * u
        cut = geom.intersection(LineString([p0, p1]))
        for part in getattr(cut, "geoms", [cut]):
            if not part.is_empty and part.length > 0:
                segs.append(np.asarray(part.coords))
    return segs


class HatchKey:
    """Legend key for the ÖÇK overlap hatch."""


class HatchKeyHandler:
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        x0, y0, w, h = handlebox.xdescent, handlebox.ydescent, handlebox.width, handlebox.height
        x0, y0 = -x0, -y0
        step = h * 0.62
        for k in np.arange(-h, w, step):
            xa, xb = max(x0 + k, x0), min(x0 + k + h, x0 + w)
            if xb > xa:
                ln = Line2D([xa, xb], [y0 + (xa - x0 - k), y0 + (xb - x0 - k)], color=OCK,
                            linewidth=LW_HATCH, solid_capstyle="butt",
                            transform=handlebox.get_transform())
                handlebox.add_artist(ln)
        return ln


def _edge_crossing(d, target, along, fixed, coord):
    """Map coordinate on a frame edge where longitude/latitude equals `target`."""
    g = to_geo()
    s = np.linspace(*along, 400)
    if coord == "lon":
        lon, _ = g.transform(s, np.full_like(s, fixed))
        vals = lon
    else:
        _, lat = g.transform(np.full_like(s, fixed), s)
        vals = lat
    if not vals.min() <= target <= vals.max():
        return None
    return float(np.interp(target, vals, s))


def _true_north(x, y):
    """Unit vector of true north at a map point (meridian convergence)."""
    lon, lat = to_geo().transform(x, y)
    x2, y2 = to_map().transform(lon, lat + 0.01)
    v = np.array([x2 - x, y2 - y])
    return v / np.hypot(*v)


def build_figure(d: MapData):
    x0, x1, y0, y1 = d.extent
    map_w = W_MM - LEFT_MM - RIGHT_MM
    map_h = map_w * (y1 - y0) / (x1 - x0)
    h_mm = TOP_MM + map_h + TICKS_MM + KEY_MM + BOTTOM_MM
    with fs.style():
        fig = plt.figure(figsize=fs.figsize_mm(W_MM, h_mm), dpi=300)   # dpi: raster layer in PDF/SVG
        ax = fig.add_axes([LEFT_MM / W_MM, (BOTTOM_MM + KEY_MM + TICKS_MM) / h_mm,
                           map_w / W_MM, map_h / h_mm], label="map")
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.set_aspect("equal", adjustable="box")
        for side in ax.spines.values():
            side.set_visible(True)
            side.set_color(AXIS)
            side.set_linewidth(fs.LW_AXIS)

        # bathymetry: depth = -elevation, sea only
        norm = PowerNorm(DEPTH_GAMMA, vmin=0, vmax=DEPTH_MAX)
        mesh = ax.pcolormesh(d.x, d.y, np.clip(d.depth, 0, None), shading="gouraud",
                             cmap=DEPTH_CMAP, norm=norm, rasterized=True, zorder=0, gid="bathymetry")
        iso_ref = ax.contour(d.x, d.y, d.depth, levels=REF_ISOBATHS, colors=ISO_REF,
                             linewidths=fs.LW_MIN, zorder=1)
        iso_scr = ax.contour(d.x, d.y, d.depth, levels=SCREEN_ISOBATHS, colors=ISO_SCREEN,
                             linewidths=fs.LW_MIN, zorder=1)
        iso_ref.set_gid("isobaths_reference")
        iso_scr.set_gid("isobaths_screening")
        t = to_map()
        for cs in (iso_scr, iso_ref):
            manual = [t.transform(*ISOBATH_LABEL_AT[lv]) for lv in cs.levels]
            labels = ax.clabel(cs, levels=cs.levels, manual=manual, inline=True, inline_spacing=2,
                               fontsize=FS_NOTE, fmt=lambda v: f"{v:g} m")
            for lab in labels:
                lab.set_color(INK if cs is iso_scr else SURFACE)

        # land and coastline (display-generalised 0 m isoline)
        e = display_land(d.elevation)
        ax.contourf(d.x, d.y, e, levels=[0, np.inf], colors=[LAND], zorder=2).set_gid("land")
        ax.contour(d.x, d.y, e, levels=[0], colors=COAST, linewidths=fs.LW_MIN,
                   zorder=2.1).set_gid("coastline")

        # ÖÇK: hatch only the part of the zone inside it; dashed boundary where it really runs
        # explicit vector hatch: Matplotlib's PDF hatch ignores hatch colour and width
        m_per_mm = (x1 - x0) / map_w
        for seg in hatch_lines(d.overlap, HATCH_SPACING_MM * m_per_mm):
            ax.plot(seg[:, 0], seg[:, 1], color=OCK, linewidth=LW_HATCH, solid_capstyle="butt",
                    zorder=3, gid="ock_overlap_hatch")
        ock_xy = np.asarray(d.ock.exterior.coords)
        ax.plot(ock_xy[:, 0], ock_xy[:, 1], color=OCK, linewidth=fs.LW_DATA,
                linestyle=(0, (3.2, 1.8)), dash_capstyle="butt", zorder=4, gid="ock_boundary")
        zone_xy = np.asarray(d.zone.exterior.coords)
        ax.plot(zone_xy[:, 0], zone_xy[:, 1], color=ZONE, linewidth=LW_ZONE, solid_joinstyle="miter",
                zorder=5, gid="zone_boundary")

        # ERA5 node, its distance to the zone, and the zone centroid
        ax.plot([d.era5.x, d.era5_nearest.x], [d.era5.y, d.era5_nearest.y], color=INK,
                linewidth=fs.LW_GUIDE + 0.1, linestyle=fs.DOT_GUIDE, dash_capstyle="round",
                zorder=5, gid="era5_distance")
        ax.plot([d.era5.x], [d.era5.y], linestyle="none", marker="s", markersize=fs.MS_POINT - 0.4,
                color=INK, markeredgecolor=SURFACE, markeredgewidth=fs.MEW, zorder=6, gid="era5_node")
        c = d.zone.centroid
        ax.plot([c.x], [c.y], linestyle="none", marker="o", markersize=fs.MS_POINT,
                markerfacecolor=SURFACE, markeredgecolor=INK, markeredgewidth=fs.LW_DATA,
                zorder=6, gid="zone_centroid")
        ax.plot([c.x], [c.y], linestyle="none", marker="o", markersize=1.4, color=INK,
                markeredgewidth=0, zorder=6.1, gid="zone_centroid_dot")

        mid = ((d.era5.x + d.era5_nearest.x) / 2, (d.era5.y + d.era5_nearest.y) / 2)
        ax.annotate(f"{d.era5_distance_km:.1f} km", mid, xytext=(-3, -3), textcoords="offset points",
                    ha="right", va="top", fontsize=FS_NOTE, color=INK, bbox=PLATE, zorder=7)
        ax.annotate("ERA5 node", (d.era5.x, d.era5.y), xytext=(5, -0.5), textcoords="offset points",
                    ha="left", va="center", fontsize=FS_NOTE, color=INK, bbox=PLATE, zorder=7)
        ax.annotate("Centroid", (c.x, c.y), xytext=(0, 5.5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=FS_NOTE, color=INK, bbox=PLATE, zorder=7)

        # place names and the ÖÇK pointer
        def lbl(lon, lat, s, **kw):
            ax.text(*t.transform(lon, lat), s, fontsize=FS_NOTE, zorder=7, **kw)
        lbl(26.225, 40.633, "Thrace", color=MUTED, ha="center", va="center", style="italic")
        lbl(26.265, 40.461, "Gulf of Saros", color=SURFACE, ha="center", va="center", style="italic")
        lbl(26.488, 40.4597, "Gelibolu Peninsula", color=INK, ha="right", va="center",
            style="italic", bbox=PLATE)
        lbl(26.343, 40.5445, "Saros ÖÇK (approximate)\nextends east and south\nbeyond the map",
            color=INK, ha="left", va="center", linespacing=1.25, bbox=PLATE)

        # scale bar (UTM metres; point scale factor here 0.9997) and true-north arrow, on land
        sx, sy = t.transform(26.372, 40.644)
        sb = [sx + k * 1e3 for k in SCALE_KM]
        ax.plot([sb[0], sb[-1]], [sy, sy], color=INK, linewidth=fs.LW_DATA, solid_capstyle="butt",
                zorder=8, gid="scale_bar")
        tick = 0.28e3
        for xb in sb:
            ax.plot([xb, xb], [sy, sy + tick], color=INK, linewidth=fs.LW_DATA, solid_capstyle="butt",
                    zorder=8)
        for k, xb in zip(SCALE_KM, sb):
            ax.text(xb, sy + tick + 0.15e3, f"{k}", ha="center", va="bottom", fontsize=FS_NOTE,
                    color=INK, zorder=8)
        ax.text(sb[-1] + 0.45e3, sy, "km", ha="left", va="center_baseline", fontsize=FS_NOTE,
                color=INK, zorder=8)
        nx, ny = t.transform(26.125, 40.627)
        u = _true_north(nx, ny)
        L = 1.55e3
        ax.add_patch(FancyArrow(nx, ny, u[0] * L, u[1] * L, width=0.05e3, head_width=0.42e3,
                                head_length=0.5e3, length_includes_head=True, color=INK,
                                linewidth=0, zorder=8, gid="north_arrow"))
        ax.text(nx + u[0] * (L + 0.25e3), ny + u[1] * (L + 0.25e3), "N", ha="center", va="bottom",
                fontsize=FS_NOTE, fontweight="bold", color=INK, zorder=8)

        # graticule labels where meridians/parallels cross the frame (bottom, left)
        xt, xl = [], []
        for lon in np.arange(26.0, 26.51, 0.1):
            xv = _edge_crossing(d, lon, (x0, x1), y0, "lon")
            if xv is not None:
                xt.append(xv); xl.append(f"{lon:.1f}° E")
        yt, yl = [], []
        for lat in np.arange(40.45, 40.661, 0.05):
            yv = _edge_crossing(d, lat, (y0, y1), x0, "lat")
            if yv is not None:
                yt.append(yv); yl.append(f"{lat:.2f}° N")
        ax.set_xticks(xt, xl)
        ax.set_yticks(yt, yl)
        ax.tick_params(axis="both", which="major", length=fs.TICK_MAJOR, width=fs.LW_AXIS,
                       color=AXIS, labelsize=FS_AXIS, labelcolor=INK, pad=fs.TICK_PAD)
        ax.minorticks_off()

        # ---- key: colour bar (left) and legend (right) ----------------------
        key_top = BOTTOM_MM + KEY_MM
        cax = fig.add_axes([LEFT_MM / W_MM, (key_top - 11.5) / h_mm, 58 / W_MM, 2.6 / h_mm],
                           label="colorbar")
        cb = fig.colorbar(mesh, cax=cax, orientation="horizontal", ticks=CBAR_TICKS)
        cb.outline.set_linewidth(fs.LW_MIN)
        cb.outline.set_edgecolor(AXIS)
        cax.tick_params(length=fs.TICK_MAJOR - 0.8, width=fs.LW_MIN, color=AXIS, labelsize=FS_NOTE,
                        pad=1.8)
        cb.set_ticklabels([f"{v:g}" for v in CBAR_TICKS])
        for lv in SCREEN_ISOBATHS:
            cax.axvline(lv, color=ISO_SCREEN, linewidth=fs.LW_DATA)
        for lv in REF_ISOBATHS:
            cax.axvline(lv, color=ISO_REF, linewidth=fs.LW_DATA)
        fig.text(LEFT_MM, key_top - 7.6, "Water depth below LAT (m)", transform=fs.mm_transform(fig),
                 fontsize=FS_AXIS, color=INK, ha="left", va="baseline")
        fig.text(LEFT_MM, key_top - 22.2, "EMODnet DTM 2024; depth = −elevation.\n" + CRS_LABEL + ".",
                 transform=fs.mm_transform(fig), fontsize=FS_NOTE, color=MUTED, ha="left",
                 va="baseline", linespacing=1.35)

        handles = [
            Line2D([], [], color=ZONE, linewidth=LW_ZONE),
            Line2D([], [], color=OCK, linewidth=fs.LW_DATA, linestyle=(0, (3.2, 1.8))),
            HatchKey(),
            Line2D([], [], linestyle="none", marker="s", markersize=fs.MS_POINT - 0.4, color=INK,
                   markeredgecolor=SURFACE, markeredgewidth=fs.MEW),
            (Line2D([], [], linestyle="none", marker="o", markersize=fs.MS_POINT, markerfacecolor=SURFACE,
                    markeredgecolor=INK, markeredgewidth=fs.LW_DATA),
             Line2D([], [], linestyle="none", marker="o", markersize=1.4, color=INK, markeredgewidth=0)),
            Line2D([], [], color=ISO_SCREEN, linewidth=fs.LW_MIN),
            (Patch(facecolor=DEPTH_CMAP(norm(250.0)), edgecolor="none", linewidth=0),   # shown on water
             Line2D([], [], color=ISO_REF, linewidth=fs.LW_DATA)),
        ]
        labels = [
            "Candidate zone (MENR notice, 13 May 2026); not an approved project",
            "Saros ÖÇK boundary, Decision 2010/1089 (approximate reconstruction)",
            f"Zone inside the ÖÇK, ≈{d.overlap_km2:.0f} km² (≈{d.overlap_pct:.0f}%); permit needed, not excluded",
            f"ERA5 grid node used, {d.era5_ll[1]:.2f}° N, {d.era5_ll[0]:.2f}° E (outside the zone)",
            "Zone centroid (geometric)",
            "10 m and 50 m isobaths: depth screening classes, not exclusions",
            "100, 200 and 400 m isobaths",
        ]
        fig.legend(handles, labels, loc="upper left", frameon=False, fontsize=FS_NOTE,
                   bbox_to_anchor=((LEFT_MM + 66) / W_MM, (key_top - 2.4) / h_mm),
                   borderaxespad=0, borderpad=0, handlelength=2.2, handletextpad=0.7,
                   labelspacing=0.42, handler_map={tuple: HandlerTuple(ndivide=1, pad=0),
                                                   HatchKey: HatchKeyHandler()})
    return fig


CROSSING_GIDS = ("zone_boundary", "ock_boundary", "era5_distance", "scale_bar")


def crossing_problems(fig, gids=CROSSING_GIDS) -> list[str]:
    """Text whose box is crossed by the actual path of a named line (not its bounding box)."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = [t for t in fs._drawn_texts(fig)]
    out = []
    for ln in fig.findobj(lambda a: a.get_gid() in gids and isinstance(a, Line2D)):
        path = ln.get_transform().transform_path(ln.get_path())
        visible = ln.axes.get_window_extent(renderer)       # parts outside the frame are clipped
        for t in texts:
            bb = t.get_window_extent(renderer).expanded(1.0, 1.0)
            if not bb.overlaps(visible):
                continue
            if path.intersects_bbox(bb, filled=False):
                out.append(f"crossed by {ln.get_gid()}: {t.get_text()!r}")
    return out


def map_text_problems(fig) -> list[str]:
    """Labels drawn in the map must sit wholly inside the map frame."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ax = next(a for a in fig.axes if a.get_label() == "map")
    frame = ax.get_window_extent(renderer)
    out = []
    for t in ax.texts:
        bb = t.get_window_extent(renderer)
        if t.get_visible() and t.get_text().strip() and not (
                frame.x0 <= bb.x0 and bb.x1 <= frame.x1 and frame.y0 <= bb.y0 and bb.y1 <= frame.y1):
            out.append(f"outside the map frame: {t.get_text()!r}")
    return out


def layout_problems(fig) -> list[str]:
    """Overlap/clipping, text crossed by drawn boundaries, labels leaving the map, print floors."""
    return (fs.layout_problems(fig) + crossing_problems(fig) + map_text_problems(fig)
            + fs.print_problems(fig))


def caption(d: MapData) -> str:
    s = d.screening
    ref = s["protected_area_overlap"]["saros_ock_2010"]
    rng = s["bathymetry"]["depth_m"]
    lon_c, lat_c = d.centroid_ll
    return (
        f"**Figure 2.** Saros offshore-wind candidate zone and the environmental and bathymetric "
        f"context used for screening. The candidate-zone boundary (black) is the official polygon "
        f"published by the Ministry of Energy and Natural Resources in the candidate-YEKA notice of "
        f"13 May 2026 (file 'SAROS DÜRES'); it is a candidate area, not an approved project, and no "
        f"turbine layout, cable route or installation footprint is implied. The zone covers "
        f"{d.area_km2:.1f} km² (WGS 84 / UTM zone 35N); its geometric centroid (open circle) lies at "
        f"{lat_c:.3f}° N, {lon_c:.3f}° E. The energy model uses the ERA5 reanalysis grid node at "
        f"{d.era5_ll[1]:.2f}° N, {d.era5_ll[0]:.2f}° E (black square), which lies outside the zone, "
        f"{d.era5_distance_km:.1f} km from its nearest boundary (dotted line). "
        f"The dashed vermillion line is the boundary of the Saros Körfezi Special Environmental "
        f"Protection Area (ÖÇK) reconstructed from the coordinates in the annex to Council of "
        f"Ministers Decision 2010/1089 (Official Gazette 27793, 22 December 2010). The annex does not "
        f"state a geodetic datum; the coordinates were read as WGS 84, so the overlay is an "
        f"approximate GIS reconstruction, not a legally certified boundary. The ÖÇK continues east and "
        f"south of the map. About {d.overlap_km2:.0f} km² (≈{d.overlap_pct:.0f}%) of the zone, its "
        f"eastern arm, falls inside the ÖÇK (hatched; {ref['overlap_km2']:.1f} km² or "
        f"{ref['overlap_share_pct']:.1f}% in the raster screening, {d.overlap_km2:.1f} km² or "
        f"{d.overlap_pct:.1f}% by exact polygon intersection). ÖÇK status requires permission from the "
        f"environment ministry for activities; it is not an automatic prohibition of construction. "
        f"Shading shows water depth below lowest astronomical tide (depth = −elevation) from the "
        f"EMODnet Digital Bathymetry DTM 2024 (1/16 arc-minute grid) on a square-root colour scale. "
        f"Depth inside the zone ranges from {rng['min']:.0f} to {rng['max']:.0f} m (median "
        f"{rng['median']:.0f} m). The 10 m and 50 m isobaths mark the depth screening classes used in "
        f"the site checks (shallower than 10 m; 50 m and deeper); they are screening thresholds, not "
        f"legal or technical exclusion zones. Land is shown where the DTM elevation is 0 m or higher; "
        f"islets and enclosed water bodies smaller than about 0.1 km² are omitted for legibility. "
        f"The map extent is that of the bathymetry grid; only the tip of the Gelibolu Peninsula "
        f"appears, in the south-eastern corner. The arrow points to true north; the scale bar is exact to within 0.1% "
        f"across the map.\n"
    )


def summary(d: MapData) -> dict:
    s = d.screening
    return {
        "crs": CRS_MAP,
        "zone_area_km2_utm": round(d.area_km2, 3),
        "zone_area_km2_geodesic": round(d.geodesic_area_km2, 3),
        "zone_area_km2_screening_raster": s["polygon"]["area_km2"],
        "centroid_lat_lon": [round(d.centroid_ll[1], 5), round(d.centroid_ll[0], 5)],
        "ock_overlap_km2_utm": round(d.overlap_km2, 3),
        "ock_overlap_km2_geodesic": round(d.geodesic_overlap_km2, 3),
        "ock_overlap_pct_utm": round(d.overlap_pct, 2),
        "ock_overlap_screening_raster": [s["protected_area_overlap"]["saros_ock_2010"]["overlap_km2"],
                                         s["protected_area_overlap"]["saros_ock_2010"]["overlap_share_pct"]],
        "era5_inside_zone": d.era5_inside,
        "era5_distance_km_utm": round(d.era5_distance_km, 3),
        "era5_distance_km_screening": s["era5_node_representativeness"]["distance_to_polygon_boundary_km"],
    }


def main(out_dir: Path = FIG_DIR) -> dict[str, Path]:
    d = load_data()
    fig = build_figure(d)
    problems = layout_problems(fig)
    if problems:
        raise RuntimeError("figure layout check failed: " + "; ".join(problems))
    paths = fs.save_figure(fig, out_dir, STEM)
    plt.close(fig)
    paths["caption"] = Path(out_dir) / f"{STEM}_caption.md"
    paths["caption"].write_text(caption(d), encoding="utf-8")
    print(json.dumps(summary(d), indent=1, ensure_ascii=False))
    for p in paths.values():
        print("wrote", p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out-dir", type=Path, default=FIG_DIR)
    main(parser.parse_args().out_dir)
