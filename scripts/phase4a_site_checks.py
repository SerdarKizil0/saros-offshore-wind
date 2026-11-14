"""
Phase 4A — minimal geometry checks for the capacity scenarios (provisional)
============================================================================
Not a layout design. Answers four questions with the official polygon, the
EMODnet DTM 2024 crop, the committed ERA5 directions and the Saros
Special Environmental Protection Area (ÖÇK) boundary from Council of
Ministers Decision 2010/1089 (Official Gazette 27793, 22.12.2010):

  1. How many 7D x 5D grid positions actually fit inside the polygon
     (turbine centre inside; and with an 82 m = D/2 rotor-tip setback),
     compared with the area-division figure of 183?
  2. How is the polygon oriented relative to the prevailing wind?
  3. How many fitted positions fall in screening classes: depth < 10 m,
     depth 50–62 m, < 1 km from the shoreline, inside the ÖÇK?
     These are screening classes, not exclusion zones.
  4. What capacity densities do S1–S4 imply?

No AEP or carbon values are computed. Writes
results/provisional/phase4a/site_checks.json.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import rasterio

from config.turbine import SCENARIOS, TURBINE, POWER_CURVE_MS_KW

KML = ROOT / "docs/review/phase1_data/SAROS_DURES_official.kml"
DTM = ROOT / "docs/review/phase1_data/emodnet_dtm2024_saros_crop.tif"
PARQUET = ROOT / "data/processed/wind_hub_105m.parquet"
OUT = ROOT / "results/provisional/phase4a"

D = TURBINE.rotor_diameter_m / 1000.0            # km
SP_ALONG, SP_ACROSS = 7 * D, 5 * D               # km
SETBACK = D / 2
R = 6371.0

# Saros ÖÇK boundary, Decision 2010/1089 annex (degrees-minutes-seconds; datum not stated)
OCK_DMS = [("26°19'20.10", "40°38'58.24"), ("26°32'30.23", "40°34'14.09"), ("26°48'36.41", "40°38'58.24"),
           ("26°49'27.76", "40°39'21.93"), ("26°50'08.85", "40°40'16.95"), ("26°51'50.14", "40°38'43.71"),
           ("26°53'18.45", "40°37'38.90"), ("26°54'04.22", "40°37'20.95"), ("26°54'36.19", "40°36'46.49"),
           ("26°55'05.37", "40°35'59.46"), ("26°45'43.90", "40°30'18.73"), ("26°34'44.79", "40°27'20.85"),
           ("26°20'05.81", "40°22'09.88")]


def dms(s):
    d, m, x = re.match(r"(\d+)°(\d+)'([\d.]+)", s).groups()
    return int(d) + int(m) / 60 + float(x) / 3600


OCK = [(dms(a), dms(b)) for a, b in OCK_DMS]


def ring():
    t = KML.read_text(encoding="utf-8")
    p = [tuple(map(float, s.split(",")[:2]))
         for s in re.findall(r"<coordinates>(.*?)</coordinates>", t, re.S)[0].split()]
    return p[:-1] if p[0] == p[-1] else p


P = ring()
LON0 = sum(p[0] for p in P) / len(P); LAT0 = sum(p[1] for p in P) / len(P)
KX = math.radians(1) * R * math.cos(math.radians(LAT0)); KY = math.radians(1) * R


def to_xy(lon, lat):
    return (np.asarray(lon) - LON0) * KX, (np.asarray(lat) - LAT0) * KY


def to_ll(x, y):
    return np.asarray(x) / KX + LON0, np.asarray(y) / KY + LAT0


def inside(x, y, poly):
    x = np.asarray(x); y = np.asarray(y); m = np.zeros(x.shape, bool)
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        c = (y1 > y) != (y2 > y)
        xi = (x2 - x1) * (y - y1) / ((y2 - y1) if y2 != y1 else 1e-30) + x1
        m ^= c & (x < xi)
    return m


def dist_to_edges(x, y, poly):
    x = np.asarray(x)[:, None]; y = np.asarray(y)[:, None]
    a = np.array(poly); b = np.roll(a, -1, axis=0)
    ax, ay, bx, by = a[:, 0], a[:, 1], b[:, 0], b[:, 1]
    dx, dy = bx - ax, by - ay
    t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.min(np.hypot(x - (ax + t * dx), y - (ay + t * dy)), axis=1)


PXY = list(zip(*to_xy([p[0] for p in P], [p[1] for p in P])))


def grid_positions(theta_deg, ox, oy, setback=0.0):
    """Rectangular grid, 7D along unit vector at compass bearing theta, 5D across."""
    th = math.radians(theta_deg)
    u = np.array([math.sin(th), math.cos(th)])        # along (bearing: 0 = north, 90 = east)
    v = np.array([u[1], -u[0]])                         # across
    n = int(60 / min(SP_ALONG, SP_ACROSS))
    i, j = np.meshgrid(np.arange(-n, n + 1), np.arange(-n, n + 1))
    pts = (i.ravel()[:, None] + ox) * SP_ALONG * u + (j.ravel()[:, None] + oy) * SP_ACROSS * v
    m = inside(pts[:, 0], pts[:, 1], PXY)
    pts = pts[m]
    if setback > 0 and len(pts):
        pts = pts[dist_to_edges(pts[:, 0], pts[:, 1], PXY) >= setback]
    return pts


def best_fit(thetas, setback, n_off=8):
    best = (0, None)
    for th in thetas:
        for ox in np.linspace(0, 1, n_off, endpoint=False):
            for oy in np.linspace(0, 1, n_off, endpoint=False):
                k = len(grid_positions(th, ox, oy, setback))
                if k > best[0]:
                    best = (k, (float(th), float(ox), float(oy)))
    return best


def compute(scenarios=SCENARIOS, wind: pd.DataFrame | None = None) -> dict:
    """Screening geometry. `wind` (columns wdir, U_hub) defaults to the Phase 4A series (PARQUET)."""
    # ---------- polygon area and principal axis ----------
    gx, gy = np.meshgrid(np.arange(-20, 20, 0.05), np.arange(-7, 7, 0.05))
    m = inside(gx, gy, PXY)
    area = m.sum() * 0.05 * 0.05
    pts = np.c_[gx[m], gy[m]]
    w, vec = np.linalg.eigh(np.cov(pts.T))
    major = vec[:, np.argmax(w)]
    axis_bearing = (math.degrees(math.atan2(major[0], major[1])) + 360) % 180
    proj_major = pts @ major; proj_minor = pts @ vec[:, np.argmin(w)]

    # ---------- prevailing wind ----------
    df = pd.read_parquet(PARQUET) if wind is None else wind
    wd = df["wdir"].to_numpy(); u = df["U_hub"].to_numpy().astype(float)
    p = np.interp(u, [q[0] for q in POWER_CURVE_MS_KW], [q[1] for q in POWER_CURVE_MS_KW], left=0, right=0)
    p[(u < TURBINE.cut_in_ms) | (u >= TURBINE.cut_out_ms)] = 0
    sect = ((wd + 11.25) // 22.5).astype(int) % 16
    names = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    hours = np.bincount(sect, minlength=16) / len(wd) * 100
    energy = np.bincount(sect, weights=p, minlength=16) / p.sum() * 100

    def ang_diff(a, b):
        d = np.abs((a - b + 180) % 360 - 180)
        return np.minimum(d, 180 - d)                    # axis is bidirectional
    along = ang_diff(wd, axis_bearing) <= 30
    share_along_hours = float(along.mean() * 100)
    share_along_energy = float(p[along].sum() / p.sum() * 100)
    # energy-weighted prevailing direction (circular mean on doubled angles = axis)
    ang2 = np.radians(2 * wd)
    prev_axis = (math.degrees(math.atan2((p * np.sin(ang2)).sum(), (p * np.cos(ang2)).sum())) / 2) % 180

    # ---------- grid fitting ----------
    fits = {}
    for label, thetas in (("7D_along_prevailing_axis", [prev_axis]),
                          ("7D_along_polygon_axis", [axis_bearing]),
                          ("any_orientation_5deg", list(range(0, 180, 5)))):
        for sb_name, sb in (("centre_inside", 0.0), ("tip_setback_82m", SETBACK)):
            k, par = best_fit(thetas, sb)
            fits[f"{label}|{sb_name}"] = {"max_positions": k, "theta_offx_offy": par,
                                          "capacity_mw": k * TURBINE.rated_power_mw}

    # screening classes for the best prevailing-axis layout with setback
    th, ox, oy = fits["7D_along_prevailing_axis|tip_setback_82m"]["theta_offx_offy"]
    lay = grid_positions(th, ox, oy, SETBACK)
    lon, lat = to_ll(lay[:, 0], lay[:, 1])
    ds = rasterio.open(DTM)
    z = np.array([v[0] for v in ds.sample(zip(lon, lat))])
    zz = ds.read(1)
    r_, c_ = np.where(zz >= 0)
    lx, ly = rasterio.transform.xy(ds.transform, r_, c_, offset="center")
    LX, LY = to_xy(np.asarray(lx), np.asarray(ly))
    d_shore = np.array([np.min(np.hypot(LX - a, LY - b)) for a, b in lay])
    in_ock = inside(lon, lat, OCK)
    # rows along the prevailing axis: turbines sharing the same across-index
    thr = math.radians(th); uvec = np.array([math.sin(thr), math.cos(thr)]); vvec = np.array([uvec[1], -uvec[0]])
    across_idx = np.round(lay @ vvec / SP_ACROSS).astype(int)
    row_len = pd.Series(across_idx).value_counts()
    screening = {
        "layout_used": "7D along energy-weighted prevailing axis, 5D across, 82 m tip setback",
        "n_positions": int(len(lay)),
        "depth_lt_10m": int((z > -10).sum()),
        "depth_50_to_62m": int(((z <= -50) & (z >= -62)).sum()),
        "within_1km_of_shore": int((d_shore < 1.0).sum()),
        "inside_saros_ock_2010": int(in_ock.sum()),
        "outside_ock_and_10_50m_and_ge1km": int(((~in_ock) & (z <= -10) & (z > -50) & (d_shore >= 1.0)).sum()),
        "rows_along_prevailing_axis": {"n_rows": int(len(row_len)), "max_turbines_in_row": int(row_len.max()),
                                       "median_turbines_in_row": float(row_len.median())},
    }
    # ÖÇK overlap area
    ock_xy = list(zip(*to_xy([q[0] for q in OCK], [q[1] for q in OCK])))
    ock_overlap = float((m & inside(gx, gy, ock_xy)).sum() * 0.05 * 0.05)

    scen = []
    for s in scenarios:
        scen.append({"name": s.name, "n_turbines": s.n_turbines, "installed_mw": s.installed_mw,
                     "density_mw_per_km2_full_polygon": s.installed_mw / area,
                     "density_mw_per_km2_outside_ock": s.installed_mw / (area - ock_overlap),
                     "share_of_fitted_positions_pct": s.n_turbines / screening["n_positions"] * 100})

    out = {
        "status": "PROVISIONAL — Phase 4A screening geometry; not a layout design or permit assessment",
        "polygon": {"area_km2": area, "principal_axis_bearing_deg": axis_bearing,
                    "length_along_axis_km": float(np.ptp(proj_major)),
                    "width_across_axis_km": float(np.ptp(proj_minor))},
        "spacing": {"D_m": TURBINE.rotor_diameter_m, "along_km": SP_ALONG, "across_km": SP_ACROSS,
                    "cell_km2": SP_ALONG * SP_ACROSS, "area_division_count": area / (SP_ALONG * SP_ACROSS)},
        "wind_direction": {"sector_share_hours_pct": dict(zip(names, map(float, hours.round(2)))),
                           "sector_share_energy_pct": dict(zip(names, map(float, energy.round(2)))),
                           "energy_weighted_prevailing_axis_deg": prev_axis,
                           "share_hours_within_30deg_of_polygon_axis_pct": share_along_hours,
                           "share_energy_within_30deg_of_polygon_axis_pct": share_along_energy},
        "grid_fits": fits, "screening_of_best_prevailing_axis_layout": screening,
        "ock_overlap_km2": ock_overlap, "ock_overlap_share_pct": ock_overlap / area * 100,
        "scenarios": scen,
    }
    return out


def main() -> int:
    out = compute()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "site_checks.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps({k: out[k] for k in ("polygon", "spacing")}, indent=1))
    wd = out["wind_direction"]
    print("prevailing axis", round(wd["energy_weighted_prevailing_axis_deg"], 1),
          "| within 30° of polygon axis: hours", round(wd["share_hours_within_30deg_of_polygon_axis_pct"], 1),
          "% energy", round(wd["share_energy_within_30deg_of_polygon_axis_pct"], 1), "%")
    for k, v in out["grid_fits"].items():
        print(f"{k:<48s} {v['max_positions']:4d} positions = {v['capacity_mw']:7.1f} MW  {v['theta_offx_offy']}")
    print(json.dumps(out["screening_of_best_prevailing_axis_layout"], indent=1))
    print("ÖÇK overlap", round(out["ock_overlap_km2"], 2), "km2")
    for sc in out["scenarios"]:
        print(sc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
