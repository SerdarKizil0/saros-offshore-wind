"""
Phase 1 technical validation: (A) V164-9.5 MW power curve, (B) Saros bathymetry.
==============================================================================
Run from the repository root:

    python docs/review/phase1_checks.py

Inputs (all committed under docs/review/phase1_data/, provenance in
docs/review/PHASE1_TECHNICAL_VALIDATION.md):
  SAROS_DURES_official.kml        MENR candidate-YEKA KML (13.05.2026)
  emodnet_dtm2024_saros_crop.tif  EMODnet DTM 2024, WCS coverage emodnet__mean
  gebco2020_saros_samples.json    GEBCO 2020 point samples (cross-check)
  oedb_V164_power_curves.csv      OEDB turbine library rows (windpowerlib)
  LEANWIND_Reference_8MW_164.csv  NREL turbine-models (physical reference only)

Needs numpy, scipy, rasterio. Reads results/*.json; writes nothing.
The production model (config/, scripts/, results/) is NOT modified.
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).resolve().parent / "phase1_data"
sys.path.insert(0, str(ROOT))

from config.site import SAROS_POLYGON_LONLAT, SITE           # noqa: E402
from config.turbine import POWER_CURVE_MS_KW, TURBINE         # noqa: E402

RHO = 1.225                      # kg/m3, IEC 61400-12-1 standard density
D_ROTOR = 164.0                  # m
AREA = math.pi * (D_ROTOR / 2) ** 2
R_EARTH = 6371.0
_trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz


# =====================================================================
# A. POWER CURVE
# =====================================================================
def load_oedb(name: str) -> list[tuple[float, float]]:
    pts = []
    with open(DATA / "oedb_V164_power_curves.csv") as f:
        for r in csv.DictReader(f):
            if r["turbine_type"] == name:
                pts.append((float(r["wind_speed_ms"]), float(r["power_W"]) / 1000))
    return pts


def cp(v, p_kw, rho=RHO):
    v = np.asarray(v, float)
    return np.asarray(p_kw, float) * 1000 / (0.5 * rho * AREA * v ** 3)


def gridded(curve, v):
    """Same convention as scripts/06: linear interpolation, 0 outside, 0 at >= 25 m/s."""
    ms = [c[0] for c in curve]
    kw = [c[1] for c in curve]
    if ms[-1] < 25.0:                      # OEDB V164/9500 table stops at 24.5 m/s
        ms.append(25.0); kw.append(kw[-1])
    p = np.interp(v, ms, kw, left=0, right=0)
    p[v >= 25.0] = 0.0
    return p


def part_a() -> None:
    print("=" * 78)
    print("A. POWER CURVE")
    print("=" * 78)
    print(f"rho = {RHO} kg/m3, D = {D_ROTOR} m, A = {AREA:.0f} m2, "
          f"Cp = P_el / (0.5 rho A v^3), v = hub-height free-stream speed")

    repo = [(v, p) for v, p in POWER_CURVE_MS_KW if v <= 25.0]
    oedb95 = load_oedb("V164/9500")
    oedb80 = load_oedb("V164/8000")
    lw = np.genfromtxt(DATA / "LEANWIND_Reference_8MW_164.csv", delimiter=",",
                       skip_header=1)

    def table(name, curve):
        v = np.array([c[0] for c in curve]); p = np.array([c[1] for c in curve])
        m = (v >= 3.0) & (v <= 15.0) & (p > 0)
        c = cp(v[m], p[m])
        i = int(np.argmax(c))
        rated = v[np.argmax(p >= 0.999 * p.max())]
        print(f"  {name:<28s} peak Cp {c[i]:.3f} at {v[m][i]:4.1f} m/s | "
              f"reaches rated at {rated:4.1f} m/s")
        return dict(zip(v[m], c))

    print("\nPeak electrical Cp and rated speed:")
    c_repo = table("repo (config/turbine.py)", repo)
    c_o95 = table("OEDB V164/9500 (digitised)", oedb95)
    table("OEDB V164/8000", oedb80)
    print(f"  {'LEANWIND 8MW/164 (ref.)':<28s} peak Cp {np.nanmax(lw[:,2]):.3f} "
          f"(file column), computed {np.nanmax(cp(lw[:,0], lw[:,1])):.3f}")

    print("\n  v(m/s)  repo kW  Cp   | OEDB9.5 kW  Cp   | repo/OEDB")
    o95 = dict(oedb95)
    for v in (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
        pr = dict(repo).get(float(v)); po = o95.get(float(v))
        print(f"  {v:5.1f}  {pr:7.0f} {c_repo[v]:.3f} | {po:9.0f} {c_o95[v]:.3f} | "
              f"{pr/po:5.3f}")
    print(f"  config rated_ms = {TURBINE.rated_ms} m/s; repo curve is already at "
          f"{dict(repo)[12.5]:.0f} kW at 12.5 m/s and 9500 kW at 13 m/s")

    # --- AEP effect on the Weibull basis used by the Monte Carlo ---
    mc = json.loads((ROOT / "results" / "monte_carlo_results.json").read_text())
    det = json.loads((ROOT / "results" / "weibull_aep_results.json").read_text())
    k0, c0 = mc["base_weibull"]["k"], mc["base_weibull"]["c"]
    sig_c = mc["base_weibull"]["sigma_c_interannual"]
    v = np.arange(0, 30, 0.1)                         # same grid as scripts/06
    nf = 0.92 * 0.95 * 0.97

    def gcf(curve, k, c):
        return _trapz(gridded(curve, v) * stats.weibull_min.pdf(v, k, 0, c), v) / 9500

    g_repo, g_o95 = gcf(repo, k0, c0), gcf(oedb95, k0, c0)
    r = g_o95 / g_repo
    print("\nWeibull(k0, c0) basis, nominal losses (net factor 0.84778):")
    for nm, g in (("repo", g_repo), ("OEDB V164/9500", g_o95)):
        print(f"  {nm:<15s} gross CF {g*100:5.2f}%  gross {g*8766*9.5/1000:5.2f} "
              f"GWh/turbine  net CF {g*nf*100:5.2f}%  net {g*nf*8.766:4.2f} GWh/MW")
    print(f"  ratio OEDB/repo = {r:.4f}  ({(r-1)*100:+.1f}%)")
    print(f"  Approx. effect on the empirical deterministic values (scaled by the "
          f"ratio): gross {det['aep']['gross_aep_per_turbine_gwh']:.1f} -> "
          f"{det['aep']['gross_aep_per_turbine_gwh']*r:.1f} GWh, net CF "
          f"{det['aep']['cf_net_pct']:.1f} -> {det['aep']['cf_net_pct']*r:.1f}%, "
          f"{det['aep']['net_aep_per_mw_gwh']:.2f} -> "
          f"{det['aep']['net_aep_per_mw_gwh']*r:.2f} GWh/MW  "
          f"[parquet absent; exact value requires scripts/04 rerun]")

    # --- full Monte Carlo rerun, identical seed and sampling to scripts/06 ---
    rng = np.random.default_rng(mc["seed"])
    N = mc["n_iterations"]
    k_s = rng.normal(k0, 0.04, N); c_s = rng.normal(c0, sig_c, N)
    wake = rng.triangular(0.05, 0.08, 0.12, N)
    av = rng.triangular(0.92, 0.95, 0.97, N)
    el = rng.triangular(0.02, 0.03, 0.04, N)
    grid = rng.triangular(434.0, 624.2, 713.4, N)
    lca = rng.triangular(8.0, 11.0, 14.0, N)
    pg = gridded(oedb95, v)
    g = np.array([_trapz(pg * stats.weibull_min.pdf(v, k_s[i], 0, c_s[i]), v)
                  for i in range(N)]) / 9500
    nfs = (1 - wake) * av * (1 - el)
    aep = g * 8766 / 1000 * nfs                       # GWh/yr/MW
    avd = aep * (grid - lca)                          # tCO2/yr/MW
    pc = lambda a: np.percentile(a, [10, 50, 90])
    ref = mc["per_mw"]
    print("\nMonte Carlo rerun with OEDB V164/9500 (seed and sampling unchanged):")
    for nm, arr, key, f in (("net AEP GWh/MW", aep, "net_aep_gwh_per_mw", "{:.3f}"),
                            ("net CF %", g * nfs * 100, "net_cf_pct", "{:.1f}"),
                            ("avoided tCO2/MW", avd, "avoided_co2_t_per_mw", "{:.0f}")):
        a = pc(arr); b = ref[key]
        print(f"  {nm:<16s} P10/P50/P90 " + "/".join(f.format(x) for x in a) +
              "   (published " + "/".join(f.format(b[q]) for q in ("p10", "p50", "p90")) + ")")
    s3 = 997.5
    print(f"  S3 (997.5 MW): {np.median(aep)*s3/1000:.2f} TWh/yr, "
          f"{np.median(avd)*s3/1e6:.2f} Mt/yr   (published 2.62 TWh, 1.52 Mt)")


# =====================================================================
# B. BATHYMETRY AND POLYGON
# =====================================================================
def read_kml(path: Path) -> list[tuple[float, float]]:
    t = path.read_text(encoding="utf-8")
    blocks = re.findall(r"<coordinates>(.*?)</coordinates>", t, flags=re.S)
    assert len(blocks) == 1, "expected one polygon ring"
    pts = [tuple(map(float, s.split(",")[:2])) for s in blocks[0].split()]
    return pts                                 # KML order: lon,lat[,alt], WGS84


def ring_area_centroid(poly):
    if poly[0] == poly[-1]:
        poly = poly[:-1]
    d = math.pi / 180
    lon0 = sum(p[0] for p in poly) / len(poly); lat0 = sum(p[1] for p in poly) / len(poly)
    xy = [((lo - lon0) * d * R_EARTH * math.cos(lat0 * d), (la - lat0) * d * R_EARTH)
          for lo, la in poly]
    a2 = cx = cy = 0.0
    for i in range(len(xy)):
        j = (i + 1) % len(xy)
        cr = xy[i][0] * xy[j][1] - xy[j][0] * xy[i][1]
        a2 += cr; cx += (xy[i][0] + xy[j][0]) * cr; cy += (xy[i][1] + xy[j][1]) * cr
    cx /= 3 * a2; cy /= 3 * a2
    return abs(a2) / 2, lat0 + cy / (d * R_EARTH), lon0 + cx / (d * R_EARTH * math.cos(lat0 * d))


def inside_mask(lon, lat, poly):
    """Vectorised even-odd point-in-polygon on arrays of lon/lat."""
    if poly[0] == poly[-1]:
        poly = poly[:-1]
    x = np.asarray(lon); y = np.asarray(lat)
    m = np.zeros(x.shape, bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        cond = (y1 > y) != (y2 > y)
        xint = (x2 - x1) * (y - y1) / ((y2 - y1) if y2 != y1 else 1e-30) + x1
        m ^= cond & (x < xint)
    return m


def km_dist(lon1, lat1, lon2, lat2):
    d = math.pi / 180
    x = (lon2 - lon1) * d * np.cos(0.5 * (lat1 + lat2) * d)
    y = (lat2 - lat1) * d
    return R_EARTH * np.sqrt(x * x + y * y)


def part_b() -> None:
    import rasterio

    print("\n" + "=" * 78)
    print("B. POLYGON AND BATHYMETRY")
    print("=" * 78)
    kml = read_kml(DATA / "SAROS_DURES_official.kml")
    ring = kml[:-1] if kml[0] == kml[-1] else kml
    cfg = list(SAROS_POLYGON_LONLAT)
    print(f"Official KML: {len(kml)} coordinate tuples, closed={kml[0] == kml[-1]}, "
          f"{len(ring)} distinct vertices; config: {len(cfg)} vertices")
    diff = max(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a, b in zip(ring, cfg))
    print(f"Same order, max |vertex difference| = {diff:.6f} deg (config rounded to 4 dp)")
    a_k, la_k, lo_k = ring_area_centroid(kml)
    a_c, la_c, lo_c = ring_area_centroid(cfg)
    print(f"Area/centroid  KML full precision: {a_k:.2f} km2, {la_k:.4f}N {lo_k:.4f}E")
    print(f"               config (4 dp)     : {a_c:.2f} km2, {la_c:.4f}N {lo_c:.4f}E "
          f"(SITE.area_km2 = {SITE.area_km2})")

    # ---------- EMODnet DTM 2024 ----------
    ds = rasterio.open(DATA / "emodnet_dtm2024_saros_crop.tif")
    z = ds.read(1).astype(float)
    rows, cols = np.indices(z.shape)
    xs, ys = rasterio.transform.xy(ds.transform, rows, cols, offset="center")
    lon = np.asarray(xs).reshape(z.shape); lat = np.asarray(ys).reshape(z.shape)
    print(f"\nEMODnet DTM 2024: {ds.crs}, cell {ds.res[0]:.7f} deg "
          f"(~{ds.res[0]*111200*math.cos(math.radians(40.55)):.0f} m E-W x "
          f"{ds.res[1]*111200:.0f} m N-S), elevation positive up, LAT datum")
    m = inside_mask(lon, lat, ring)
    zin = z[m]
    depth = -zin
    print(f"Cells with centre inside polygon: {m.sum()} "
          f"(cell area ~{m.sum()*ds.res[0]*ds.res[1]*111.2**2*math.cos(math.radians(40.55)):.1f} km2)")
    q = np.percentile(depth, [0, 5, 50, 95, 100])
    print(f"Water depth (m, positive down): min {q[0]:.1f}  P5 {q[1]:.1f}  "
          f"median {q[2]:.1f}  mean {depth.mean():.1f}  P95 {q[3]:.1f}  max {q[4]:.1f}")
    print(f"Cells at or above datum (z >= 0) inside polygon: {(zin >= 0).sum()}")
    for th in (10, 20, 30, 40, 50, 60):
        print(f"  share of zone area deeper than {th:2d} m: {(depth > th).mean()*100:5.1f}%")

    # where are the deepest cells?  (west vs east, south edge vs north edge)
    lin, lain = lon[m], lat[m]
    for lo1, lo2 in ((26.03, 26.12), (26.12, 26.22), (26.22, 26.32), (26.32, 26.47)):
        s = (lin >= lo1) & (lin < lo2)
        print(f"  lon {lo1:.2f}-{lo2:.2f}: n={s.sum():4d}  depth min/median/max "
              f"{depth[s].min():5.1f}/{np.median(depth[s]):5.1f}/{depth[s].max():5.1f} m")
    for la1, la2 in ((40.50, 40.53), (40.53, 40.56), (40.56, 40.58), (40.58, 40.60)):
        s = (lain >= la1) & (lain < la2)
        print(f"  lat {la1:.2f}-{la2:.2f}: n={s.sum():4d}  depth min/median/max "
              f"{depth[s].min():5.1f}/{np.median(depth[s]):5.1f}/{depth[s].max():5.1f} m")
    i = np.argmax(depth)
    print(f"  deepest cell {depth[i]:.1f} m at {lain[i]:.4f}N {lin[i]:.4f}E")

    # nearest land: Thrace (north shore) vs Gelibolu Peninsula (south shore)
    land = z >= 0
    north = land & (lat >= 40.58)
    south = land & (lat <= 40.50)
    mid = land & (lat > 40.50) & (lat < 40.58)
    print(f"\nLand cells in crop: north(>=40.58N) {north.sum()}, "
          f"south(<=40.50N) {south.sum()}, between {mid.sum()}")
    bl, bt = np.array([p[0] for p in ring]), np.array([p[1] for p in ring])

    def nearest(mask):
        L, T = lon[mask], lat[mask]
        dv = np.array([km_dist(x, y, L, T).min() for x, y in zip(bl, bt)])
        di = km_dist(lin[:, None], lain[:, None], L[None, ::4], T[None, ::4]).min(axis=1)
        return dv, di

    dvn, din = nearest(north)
    dvs, dis = nearest(south)
    print(f"Distance polygon -> Thrace coast:   min {min(dvn.min(), din.min()):.2f} km, "
          f"vertices median {np.median(dvn):.1f} km, max over zone {din.max():.1f} km")
    # the crop reaches only 40.45N, so south-shore distances are exact only
    # for the closest approach (eastern zone vs. peninsula at 26.4-26.5E)
    print(f"Distance polygon -> Gelibolu coast: min {min(dvs.min(), dis.min()):.2f} km "
          f"(closest approach; crop limited to >= 40.45N)")
    print(f"Share of zone within 1 / 2 / 5 km of the Thrace coast: "
          f"{(din < 1).mean()*100:.0f}% / {(din < 2).mean()*100:.0f}% / {(din < 5).mean()*100:.0f}%")

    # deep basin location relative to polygon
    deep = (z < -200)
    print(f"Cells deeper than 200 m: inside polygon {np.sum(deep & m)}, "
          f"nearest to polygon {min(km_dist(x, y, lon[deep], lat[deep]).min() for x, y in zip(bl, bt)):.1f} km")

    # ---------- GEBCO 2020 cross-check ----------
    g = json.loads((DATA / "gebco2020_saros_samples.json").read_text())
    ge = np.array([p[2] for p in g["points_lat_lon_elev"]], float)
    q = np.percentile(-ge, [0, 50, 100])
    print(f"\nGEBCO 2020 (15 arc-sec, {len(ge)} samples): depth min {q[0]:.0f}  "
          f"median {q[1]:.0f}  max {q[2]:.0f} m; deeper than 50 m: "
          f"{(-ge > 50).mean()*100:.0f}%, deeper than 60 m: {(-ge > 60).mean()*100:.0f}%")


if __name__ == "__main__":
    part_a()
    part_b()
