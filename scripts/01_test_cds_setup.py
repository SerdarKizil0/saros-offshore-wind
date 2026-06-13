"""
01 — CDS API Setup Diagnostic (Saros project)
Verifies Copernicus CDS credentials before the full ERA5 download.
Run: python scripts/01_test_cds_setup.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.site import SITE

NEW_URL = "https://cds.climate.copernicus.eu/api"
print("=== CDS API diagnostic ===")
try:
    import cdsapi
    print(f"[ok] cdsapi {getattr(cdsapi,'__version__','?')}")
except ImportError:
    print("[FAIL] cdsapi not installed: pip install 'cdsapi>=0.7.7'"); sys.exit(1)

rc = Path.home()/".cdsapirc"
if not rc.exists():
    print(f"[FAIL] {rc} missing. Add two lines:\n  url: {NEW_URL}\n  key: <token>"); sys.exit(1)
print(f"[ok] {rc} found")

txt = rc.read_text()
if NEW_URL not in txt: print(f"[WARN] url should be: {NEW_URL}")
if "key:" not in txt: print("[FAIL] no key line"); sys.exit(1)
print("[ok] config looks valid")

print("Submitting tiny test request (1h, 1 var, Saros bbox)...")
try:
    c = cdsapi.Client()
    t = Path(__file__).parent.parent/"data"/"_cds_test.nc"
    t.parent.mkdir(parents=True, exist_ok=True)
    c.retrieve("reanalysis-era5-single-levels", {
        "product_type":["reanalysis"], "variable":["100m_u_component_of_wind"],
        "year":["2020"],"month":["06"],"day":["15"],"time":["12:00"],
        "area": SITE.era5_area_request, "data_format":"netcdf","download_format":"unarchived",
    }, str(t))
    if t.exists():
        print(f"[ok] test file {t.stat().st_size/1024:.0f} KB — ALL GOOD"); t.unlink()
except Exception as e:
    print(f"[FAIL] {e}\nCheck: ERA5 licence accepted? token valid?"); sys.exit(1)
print("\nReady. Next: python scripts/02_download_era5_saros.py")
