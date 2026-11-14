"""
07 — Geographic and environmental screening (revised production pipeline)
==========================================================================
Writes results/revised/site_screening.json from documented inputs:
  * official MENR polygon (docs/review/phase1_data/SAROS_DURES_official.kml)
  * EMODnet DTM 2024 crop (docs/review/phase1_data/emodnet_dtm2024_saros_crop.tif)
  * ERA5 directions and hub-height speeds of the PRIMARY wind series
    (config/wind_data.py; loaded and checksum-verified by scripts/04)
  * Saros ÖÇK boundary, Decision 2010/1089 (Official Gazette 27793)

Geometry and grid-fitting are computed by scripts/phase4a_site_checks.py
(compute()), restricted here to the ACTIVE scenarios. Screening classes are
not exclusion zones, and the grid fits are not layouts.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import rasterio

from config.site import RESULTS_DIR
from config.turbine import ACTIVE_SCENARIOS, RETIRED_SCENARIOS, TURBINE_SPACING_ASSUMPTION
from config.wind_data import PRIMARY, SERIES

REV = RESULTS_DIR / "revised"
STATUS = "PRE-SUBMISSION SCREENING — not a layout design, permit or environmental assessment"
ERA5_NODE = (26.25, 40.50)            # lon, lat


def _p4a():
    spec = importlib.util.spec_from_file_location("p4a", ROOT / "scripts/phase4a_site_checks.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def bathymetry(p4a) -> dict:
    ds = rasterio.open(p4a.DTM)
    z = ds.read(1).astype(float)
    r, c = np.indices(z.shape)
    xs, ys = rasterio.transform.xy(ds.transform, r, c, offset="center")
    lon, lat = np.asarray(xs).reshape(z.shape), np.asarray(ys).reshape(z.shape)
    m = p4a.inside(lon, lat, p4a.P)
    depth = -z[m]
    return {"source": "EMODnet DTM 2024 (doi:10.12770/cf51df64-56f9-4a99-b1aa-36b8d7b743a1), LAT datum, "
                      "cell centres inside the official polygon",
            "n_cells": int(m.sum()),
            "depth_m": {"min": float(depth.min()), "p5": float(np.percentile(depth, 5)),
                        "median": float(np.median(depth)), "p95": float(np.percentile(depth, 95)),
                        "max": float(depth.max())},
            "share_deeper_than_pct": {str(t): float((depth > t).mean() * 100) for t in (10, 30, 50, 60)},
            "inside_polygon_deeper_than_200m_cells": int((depth > 200).sum())}


def era5_node(p4a) -> dict:
    x, y = p4a.to_xy([ERA5_NODE[0]], [ERA5_NODE[1]])
    d = float(p4a.dist_to_edges(x, y, p4a.PXY)[0])
    gx, gy = np.meshgrid(np.arange(26.03, 26.47, 0.001), np.arange(40.50, 40.60, 0.001))
    m = p4a.inside(gx, gy, p4a.P)
    nearest = (np.round(gx[m] * 4) / 4 == ERA5_NODE[0]) & (np.round(gy[m] * 4) / 4 == ERA5_NODE[1])
    return {"node_lon_lat": list(ERA5_NODE),
            "inside_polygon": bool(p4a.inside(np.array([ERA5_NODE[0]]), np.array([ERA5_NODE[1]]), p4a.P)[0]),
            "distance_to_polygon_boundary_km": d,
            "polygon_share_nearest_to_this_node_pct": float(nearest.mean() * 100)}


def _s04():
    spec = importlib.util.spec_from_file_location("s04_for_07", ROOT / "scripts/04_fit_weibull_aep.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def compute(series_key: str | None = None) -> dict:
    s04 = _s04()
    spec = SERIES[series_key] if series_key else PRIMARY
    wind, _ = s04.load_series(spec)
    p4a = _p4a()
    g = p4a.compute(ACTIVE_SCENARIOS, wind=wind)
    scr = g["screening_of_best_prevailing_axis_layout"]
    return {
        "status": STATUS,
        "polygon": g["polygon"] | {"source": "MENR candidate-YEKA notice 13.05.2026, SAROS DÜRES.kml"},
        "bathymetry": bathymetry(p4a),
        "era5_node_representativeness": era5_node(p4a),
        "protected_area_overlap": {
            "saros_ock_2010": {"overlap_km2": g["ock_overlap_km2"], "overlap_share_pct": g["ock_overlap_share_pct"],
                               "source": "Council of Ministers Decision 2010/1089, Official Gazette 27793 (22.12.2010)",
                               "status": "verified overlap; ÖÇK requires ministry permission, not an automatic prohibition"},
            "gelibolu_kkha_2019": {"overlap": False, "source": "Presidential Decision 1133, Official Gazette 30791"},
        },
        "spacing_and_packing": {
            "assumption": TURBINE_SPACING_ASSUMPTION, "cell_km2": g["spacing"]["cell_km2"],
            "area_division_count": g["spacing"]["area_division_count"],
            "max_grid_positions_with_tip_setback": g["grid_fits"]["7D_along_prevailing_axis|tip_setback_82m"]["max_positions"],
            "note": "geometric packing limit at minimum spacing; not a feasible capacity"},
        "screening_classes_best_fit_layout": {
            "label": "SCREENING classes, not exclusion zones",
            "n_positions": scr["n_positions"], "depth_lt_10m": scr["depth_lt_10m"],
            "depth_50_to_62m": scr["depth_50_to_62m"], "within_1km_of_shore": scr["within_1km_of_shore"],
            "inside_saros_ock_2010": scr["inside_saros_ock_2010"],
            "outside_all_classes": scr["outside_ock_and_10_50m_and_ge1km"]},
        "wind_direction": g["wind_direction"] | {"series": spec.key, "period": spec.period_label},
        "active_scenarios_density": [
            {k: s[k] for k in ("name", "n_turbines", "installed_mw", "density_mw_per_km2_full_polygon",
                               "density_mw_per_km2_outside_ock", "share_of_fitted_positions_pct")}
            for s in g["scenarios"]],
        "retired": RETIRED_SCENARIOS,
        "not_screened": ["bird migration (Evros delta SPA ~14 km, regional flyway)", "fisheries (current trawl-ban boundary)",
                         "navigation and LNG traffic (Saros FSRU ~16 km east, unverified coordinate)",
                         "military exercise areas", "North Anatolian Fault distance", "grid connection point"],
    }


def main() -> int:
    out = compute()
    REV.mkdir(parents=True, exist_ok=True)
    (REV / "site_screening.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    b = out["bathymetry"]["depth_m"]
    print(f"Depth {b['min']:.1f}/{b['median']:.1f}/{b['max']:.1f} m; ÖÇK overlap "
          f"{out['protected_area_overlap']['saros_ock_2010']['overlap_km2']:.2f} km2; "
          f"node outside polygon by {out['era5_node_representativeness']['distance_to_polygon_boundary_km']:.2f} km")
    print(f"✓ wrote {REV / 'site_screening.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
