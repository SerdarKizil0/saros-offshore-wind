"""
Tests for Figure 2 (Saros study area and environmental constraints).
Run from the repository root:  python -m pytest -q tests/
"""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import math
import re
import struct
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.collections import Collection
from matplotlib.lines import Line2D
from matplotlib.text import Text
from pyproj import Geod, Proj
from shapely.geometry import LineString, Point

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase4c_fig_saros_study_area.py"
SCREENING = ROOT / "results" / "revised" / "site_screening.json"
W_PT = 180 / 25.4 * 72


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("p4c_map", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def data(m):
    return m.load_data()


@pytest.fixture(scope="module")
def fig(m, data):
    f = m.build_figure(data)
    yield f
    plt.close(f)


@pytest.fixture(scope="module")
def outputs(m, tmp_path_factory):
    return m.main(tmp_path_factory.mktemp("map"))


@pytest.fixture(scope="module")
def screening():
    return json.loads(SCREENING.read_text(encoding="utf-8"))


def _ax(fig):
    return next(a for a in fig.axes if a.get_label() == "map")


def _lines(fig, gid):
    return [ln for ln in _ax(fig).lines if ln.get_gid() == gid]


# ---- sources and CRS ---------------------------------------------------------
def test_geometry_comes_from_the_official_sources(m, data):
    p4a = m._site_checks_module()
    assert data.zone_ll == [tuple(map(float, p)) for p in p4a.ring()]          # KML, full precision
    assert data.ock_ll == [tuple(map(float, p)) for p in p4a.OCK]              # Decision 2010/1089 annex
    assert len(data.zone_ll) == 27 and len(data.ock_ll) == 13
    from config.site import SAROS_POLYGON_LONLAT
    assert np.abs(np.array(data.zone_ll) - np.array(SAROS_POLYGON_LONLAT)).max() < 1e-4


def test_map_crs_is_utm_35n(m, data):
    assert m.CRS_MAP == "EPSG:32635"
    x, y = m.to_map().transform(27.0, 40.5)                  # central meridian of zone 35
    assert x == pytest.approx(500_000, abs=0.01)
    xs, ys = np.asarray(data.zone.exterior.coords).T
    assert 400e3 < xs.min() < xs.max() < 470e3 and 4.47e6 < ys.min() < ys.max() < 4.51e6
    back = m.to_geo().transform(*data.zone.exterior.coords[0])
    assert back == pytest.approx(data.zone_ll[0], abs=1e-9)


# ---- area, centroid, ERA5 node, ÖÇK -----------------------------------------
def test_zone_area_and_centroid(data, screening):
    assert data.area_km2 == pytest.approx(172.61, abs=0.02)
    assert data.area_km2 == pytest.approx(data.geodesic_area_km2, rel=2e-3)    # UTM scale ≈ 0.9997
    assert data.area_km2 == pytest.approx(screening["polygon"]["area_km2"], rel=5e-3)
    from config.site import SITE
    lon, lat = data.centroid_ll
    assert (lat, lon) == pytest.approx((SITE.centroid_lat, SITE.centroid_lon), abs=2e-4)
    assert data.zone.contains(data.zone.centroid)


def test_era5_node_is_outside_the_zone_and_drawn_there(fig, data, screening):
    assert data.era5_ll == (26.25, 40.5)
    assert not data.era5_inside and not data.zone.contains(data.era5)
    assert data.era5_distance_km == pytest.approx(3.685, abs=0.005)
    node = screening["era5_node_representativeness"]
    assert data.era5_distance_km == pytest.approx(node["distance_to_polygon_boundary_km"], abs=0.02)
    (ln,) = _lines(fig, "era5_node")
    assert (ln.get_xdata()[0], ln.get_ydata()[0]) == pytest.approx((data.era5.x, data.era5.y))
    # the dotted distance line ends on the zone boundary
    (dist,) = _lines(fig, "era5_distance")
    end = Point(dist.get_xdata()[1], dist.get_ydata()[1])
    assert data.zone.exterior.distance(end) < 1e-6
    assert math.hypot(np.diff(dist.get_xdata())[0], np.diff(dist.get_ydata())[0]) / 1e3 == \
        pytest.approx(data.era5_distance_km)


def test_centroid_is_a_separate_symbol(fig, data):
    (c,) = _lines(fig, "zone_centroid")
    (e,) = _lines(fig, "era5_node")
    assert c.get_marker() != e.get_marker()
    assert (c.get_xdata()[0], c.get_ydata()[0]) == pytest.approx((data.zone.centroid.x, data.zone.centroid.y))


def test_ock_overlap_recomputed(m, data, screening):
    ref = screening["protected_area_overlap"]["saros_ock_2010"]
    assert data.overlap_km2 == pytest.approx(24.98, abs=0.05)
    assert data.overlap_pct == pytest.approx(14.47, abs=0.05)
    assert data.overlap_km2 == pytest.approx(ref["overlap_km2"], rel=0.02)     # raster screening value
    assert data.overlap_pct == pytest.approx(ref["overlap_share_pct"], abs=0.3)
    assert data.overlap_km2 == pytest.approx(data.geodesic_overlap_km2, rel=2e-3)
    # the overlap is the eastern arm, east of the ÖÇK west boundary (~26.32-26.33° E)
    lons, _ = m.to_geo().transform(*np.asarray(data.overlap.exterior.coords).T)
    assert 26.32 < lons.min() < 26.33 and lons.max() == pytest.approx(max(p[0] for p in data.zone_ll))


def test_hatch_lies_exactly_inside_the_overlap(fig, data):
    segs = _lines(fig, "ock_overlap_hatch")
    assert len(segs) > 10
    inside = data.overlap.buffer(0.5)                       # 0.5 m numerical tolerance
    total = 0.0
    for ln in segs:
        seg = LineString(np.c_[ln.get_xdata(), ln.get_ydata()])
        assert inside.contains(seg)
        total += seg.length
    assert total > 0
    # hatch spans the whole overlap, end to end
    xs = np.concatenate([ln.get_xdata() for ln in segs])
    x0, _, x1, _ = data.overlap.bounds
    assert xs.min() - x0 < 600 and x1 - xs.max() < 600


def test_ock_boundary_is_the_annex_ring_not_the_map_frame(fig, data):
    (ln,) = _lines(fig, "ock_boundary")
    drawn = np.c_[ln.get_xdata(), ln.get_ydata()]
    assert drawn == pytest.approx(np.asarray(data.ock.exterior.coords))
    assert ln.get_clip_on()                                 # clipped by the frame, not reshaped to it
    x0, x1, y0, y1 = data.extent
    frame = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    for corner in frame:                                    # no ÖÇK vertex was moved onto the frame
        assert np.min(np.hypot(*(drawn - corner).T)) > 100


def test_no_project_layout_is_drawn(fig):
    gids = {a.get_gid() for a in _ax(fig).get_children() if a.get_gid()}
    assert not {g for g in gids if re.search(r"turbine|layout|cable|wtg|footprint", g)}
    markers = [ln for ln in _ax(fig).lines if ln.get_linestyle() == "None"]
    assert {ln.get_gid() for ln in markers} == {"era5_node", "zone_centroid", "zone_centroid_dot"}


# ---- bathymetry -----------------------------------------------------------------
def test_depth_convention_and_zone_depths(m, data, screening):
    assert np.array_equal(data.depth, -data.elevation)
    assert data.elevation.min() < -600 and data.elevation.max() > 100      # sea negative, land positive
    zd = data.depth[m._zone_mask(data)]
    rng = screening["bathymetry"]["depth_m"]
    assert (zd.min(), zd.max()) == pytest.approx((rng["min"], rng["max"]), abs=1e-3)
    assert len(zd) == screening["bathymetry"]["n_cells"]


def test_shading_and_isobaths_use_positive_depths(fig, m):
    ax = _ax(fig)
    (mesh,) = [c for c in ax.collections if c.get_gid() == "bathymetry"]
    arr = mesh.get_array()
    assert arr.min() >= 0 and arr.max() > 600
    assert mesh.norm.vmin == 0 and mesh.norm.vmax == m.DEPTH_MAX
    sets = {c.get_gid(): list(c.levels) for c in ax.collections if c.get_gid() and "isobath" in c.get_gid()}
    assert sets == {"isobaths_screening": [10, 50], "isobaths_reference": [100, 200, 400]}
    labels = {t.get_text() for t in ax.texts if t.get_text().endswith(" m")}
    assert labels == {"10 m", "50 m", "100 m", "200 m", "400 m"}


def test_land_is_elevation_at_or_above_zero(m, data):
    from scipy import ndimage
    e = m.display_land(data.elevation)
    changed = (e >= 0) != (data.elevation >= 0)
    # every reclassified cell belongs to a land or water fragment below the display threshold
    for mask in (data.elevation >= 0, data.elevation < 0):
        lab, _ = ndimage.label(mask)
        sizes = np.bincount(lab.ravel())
        assert (sizes[lab[changed & mask]] < m.MIN_FEATURE_CELLS).all()
    assert changed.sum() / changed.size < 0.005
    assert not ((e >= 0) & (data.elevation < -5)).any()     # no real water turned into land


# ---- cartographic furniture ------------------------------------------------------
def test_scale_bar_is_true_to_ground_distance(fig, m):
    (bar,) = _lines(fig, "scale_bar")
    xs, ys = bar.get_xdata(), bar.get_ydata()
    assert xs[1] - xs[0] == pytest.approx(10_000) and ys[0] == ys[1]
    lon0, lat0 = m.to_geo().transform(xs[0], ys[0])
    lon1, lat1 = m.to_geo().transform(xs[1], ys[1])
    _, _, dist = Geod(ellps="WGS84").inv(lon0, lat0, lon1, lat1)
    assert dist == pytest.approx(10_000, rel=1e-3)          # point scale factor ≈ 0.9997 here


def test_north_arrow_points_to_true_north(fig, m):
    (arrow,) = [p for p in _ax(fig).patches if p.get_gid() == "north_arrow"]
    xy = np.unique(arrow.get_xy(), axis=0)
    tip = xy[np.argmax(xy[:, 1])]
    tail = xy[np.argsort(xy[:, 1])[:2]].mean(axis=0)            # middle of the shaft end
    bearing = math.degrees(math.atan2(tip[0] - tail[0], tip[1] - tail[1]))
    lon, lat = m.to_geo().transform(*tail)
    conv = Proj("EPSG:32635").get_factors(lon, lat).meridian_convergence
    assert abs(conv) > 0.3                                  # true north differs from grid north here
    assert bearing == pytest.approx(-conv, abs=0.1)


def test_frame_lies_inside_the_dtm_and_holds_the_zone(m, data):
    poly = m._frame(data)
    assert data.zone.within(poly) and poly.contains(data.era5)
    g = m.to_geo()
    x0, x1, y0, y1 = data.extent
    lons, lats = g.transform([x0, x1, x1, x0], [y0, y0, y1, y1])
    assert data.lon.min() <= min(lons) and max(lons) <= data.lon.max()
    assert data.lat.min() <= min(lats) and max(lats) <= data.lat.max()


def test_graticule_labels_are_where_the_meridians_cross(fig, m, data):
    ax = _ax(fig)
    x0, x1, y0, y1 = data.extent
    for x, lab in zip(ax.get_xticks(), ax.get_xticklabels()):
        lon, _ = m.to_geo().transform(x, y0)
        assert lab.get_text() == f"{lon:.1f}° E"
    for y, lab in zip(ax.get_yticks(), ax.get_yticklabels()):
        _, lat = m.to_geo().transform(x0, y)
        assert lab.get_text() == f"{lat:.2f}° N"


# ---- layout, style and export ----------------------------------------------------
def test_layout_is_clean_and_fonts_are_bundled(m, fig):
    assert m.layout_problems(fig) == []
    texts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    assert {t.get_fontname() for t in texts} == {"DejaVu Sans"}
    sizes = {t.get_fontsize() for t in texts}
    assert min(sizes) >= 7.0 and len(sizes) <= 3


def test_crossing_check_catches_a_label_on_the_zone_boundary(m, data):
    f = m.build_figure(data)
    try:
        ax = _ax(f)
        x, y = np.asarray(data.zone.exterior.coords)[3]
        ax.text(x, y, "on the line", fontsize=7, ha="center", va="center")
        assert any("on the line" in p for p in m.crossing_problems(f))
    finally:
        plt.close(f)


def test_strokes_survive_print_at_actual_size(fig):
    widths = [ln.get_linewidth() for ln in fig.findobj(Line2D)
              if ln.get_visible() and ln.get_linestyle() != "None"]
    widths += [w for c in fig.findobj(Collection) if c.get_gid() and "isobath" in c.get_gid()
               for w in c.get_linewidths()]
    assert widths and min(widths) >= 0.5


def test_generator_takes_style_from_the_shared_module():
    src = SCRIPT.read_text(encoding="utf-8")
    assert "from config import figure_style" in src
    assert not re.findall(r"#[0-9A-Fa-f]{6}\b", src)
    assert "rc_context(" not in src and "savefig(" not in src
    assert not re.findall(r"requests|urllib|http[s]?://", src)          # local data only


def test_verify_rejects_a_node_moved_inside(m, data):
    moved = dataclasses.replace(data, era5=data.zone.representative_point())
    assert any("inside" in p for p in m.verify(moved))
    assert m.verify(data) == []


def test_exact_180_mm_outputs(outputs):
    pdf = outputs["pdf"].read_bytes()
    box = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
    w_pt = float(box.group(3))
    assert w_pt == pytest.approx(W_PT, abs=0.01)
    assert len(re.findall(rb"/Type\s*/Page\b", pdf)) == 1
    assert b"/FontFile2" in pdf and b"/Type3" not in pdf
    assert len(re.findall(rb"/Subtype\s*/Image", pdf)) <= 2          # bathymetry + colour bar only

    svg = outputs["svg"].read_text(encoding="utf-8")
    w = float(re.search(r'<svg[^>]*\bwidth="([\d.]+)pt"', svg, re.S).group(1))
    assert w == pytest.approx(W_PT, abs=0.01)
    assert svg.count("<text") > 30                                    # labels stay editable text

    png = outputs["png"].read_bytes()
    px_w, px_h = struct.unpack(">II", png[16:24])
    assert px_w / 600 * 25.4 == pytest.approx(180, abs=0.05)
    h_mm = float(box.group(4)) / 72 * 25.4
    assert px_h / 600 * 25.4 == pytest.approx(h_mm, abs=0.05)


def test_caption_states_sources_and_limits(m, data):
    c = m.caption(data)
    for token in ("13 May 2026", "candidate area, not an approved project", "2010/1089",
                  "approximate GIS reconstruction", "not a legally certified boundary",
                  "not an automatic prohibition", "EMODnet", "depth = −elevation",
                  "not legal or technical exclusion zones", f"{data.era5_distance_km:.1f} km",
                  "outside the zone", "UTM zone 35N"):
        assert token in c, token
    committed = ROOT / "figures" / "revised" / "saros_study_area_caption.md"
    assert committed.read_text(encoding="utf-8") == c
