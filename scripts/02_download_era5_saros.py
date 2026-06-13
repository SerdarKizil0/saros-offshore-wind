"""
02 — ERA5 11-Year Download (Saros Bay) — MONTHLY CHUNKED
=========================================================
Downloads hourly 10 m and 100 m wind components (u, v) over the Saros
DÜRES bounding box for 2014–2024, ONE FILE PER MONTH.

WHY MONTHLY:
The post-Sep-2024 CDS imposes a per-request cost limit. A full-year
request (4 vars × 12 months × 31 days × 24 h ≈ 35 700 fields) exceeds
it and returns "403 cost limits exceeded". A single month
(4 vars × 31 days × 24 h ≈ 2 976 fields) is comfortably under the
limit. We therefore request month by month: 11 years × 12 = 132 small,
fast, independently-resumable requests.

Output: data/era5/era5_saros_<YEAR>_<MM>.nc

Downstream `03_process_era5.py` globs `era5_saros_*.nc` and concatenates
by time, so it works unchanged with these monthly files.

The script is idempotent: existing valid monthly files are skipped.
You can Ctrl-C and re-run; completed months are not re-fetched.

If you prefer fewer, larger requests and your account's cost limit
allows it, set CHUNK_MONTHS = 3 (quarterly, 44 requests). Monthly
(CHUNK_MONTHS = 1) is the safe default.
"""
from __future__ import annotations

import sys
import time
import calendar
import traceback
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import cdsapi
except ImportError:
    print("ERROR: cdsapi not installed.  Run: pip install 'cdsapi>=0.7.7'")
    sys.exit(1)

from config.site import SITE, ERA5_DIR


# ----------------------------- Tunables -----------------------------
VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "100m_u_component_of_wind",
    "100m_v_component_of_wind",
]

# 1 = monthly (safe, 132 requests). 3 = quarterly (44 requests, larger).
CHUNK_MONTHS = 1

# A valid monthly file: 4 vars × ~6 cells × ~720 h × 4 B ≈ 70 KB raw,
# typically 25–55 KB compressed NetCDF. Anything under 12 KB is broken.
MIN_VALID_BYTES = 12_000

MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 60


# --------------------------- Internals ------------------------------
def days_in_month(year: int, month: int) -> list[str]:
    n = calendar.monthrange(year, month)[1]
    return [f"{d:02d}" for d in range(1, n + 1)]


def build_request(year: int, months: list[int]) -> dict:
    """CDS request body for a set of months within one year."""
    # Union of valid days across the months in this chunk
    max_days = max(calendar.monthrange(year, m)[1] for m in months)
    return {
        "product_type": ["reanalysis"],
        "variable": VARIABLES,
        "year":  [str(year)],
        "month": [f"{m:02d}" for m in months],
        "day":   [f"{d:02d}" for d in range(1, max_days + 1)],
        "time":  [f"{h:02d}:00" for h in range(24)],
        "area":  SITE.era5_area_request,         # [N, W, S, E]
        "data_format":     "netcdf",
        "download_format": "unarchived",
    }


def chunk_label(year: int, months: list[int]) -> str:
    if len(months) == 1:
        return f"{year}_{months[0]:02d}"
    return f"{year}_{months[0]:02d}-{months[-1]:02d}"


def file_is_valid(path: Path) -> bool:
    return path.exists() and path.stat().st_size >= MIN_VALID_BYTES


def download_chunk(client, year: int, months: list[int], target: Path) -> bool:
    request = build_request(year, months)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            t0 = time.time()
            client.retrieve(
                "reanalysis-era5-single-levels",
                request,
                str(target),
            )
            dt = time.time() - t0
            if file_is_valid(target):
                kb = target.stat().st_size / 1024
                print(f"      ✓ {kb:.0f} KB in {dt:.0f}s")
                return True
            print(f"      ⚠ file too small ({target.stat().st_size} B). retry.")
            target.unlink(missing_ok=True)
        except Exception as e:
            msg = str(e)
            print(f"      ✗ attempt {attempt}/{MAX_RETRIES}: {msg[:120]}")
            target.unlink(missing_ok=True)
            # If it's STILL a cost-limit error at monthly granularity,
            # retrying won't help — surface it loudly.
            if "cost limit" in msg.lower() or "too large" in msg.lower():
                print("      ! Cost limit hit even at this chunk size.")
                print("      ! Reduce CHUNK_MONTHS or split variables.")
                return False
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF_SEC * attempt
                print(f"      waiting {wait}s …")
                time.sleep(wait)
    return False


def build_chunks() -> list[tuple[int, list[int]]]:
    """List of (year, [months]) chunks honouring CHUNK_MONTHS."""
    chunks = []
    for year in SITE.years:
        for start in range(1, 13, CHUNK_MONTHS):
            months = list(range(start, min(start + CHUNK_MONTHS, 13)))
            chunks.append((year, months))
    return chunks


# --------------------------- Main flow ------------------------------
def main() -> int:
    print("=" * 72)
    print(" ERA5 Download (MONTHLY) — Saros Bay Offshore Wind YEKA Zone")
    print("=" * 72)
    print(f" Site          : {SITE.full_name}")
    print(f" Bbox (N,W,S,E): {SITE.era5_area_request}")
    print(f" Years         : {SITE.era5_start_year}–{SITE.era5_end_year}")
    print(f" Chunk size    : {CHUNK_MONTHS} month(s) per request")
    print(f" Variables     : {len(VARIABLES)}")
    print(f" Output dir    : {ERA5_DIR.resolve()}")
    print(f" Started       : {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 72)

    try:
        client = cdsapi.Client()
    except Exception as e:
        print(f"\n✗ CDS client init failed: {e}")
        print("  Run scripts/01_test_cds_setup.py first.")
        return 1

    chunks = build_chunks()
    print(f" Total requests: {len(chunks)}\n")

    succeeded = skipped = failed = 0
    failed_chunks: list[str] = []

    t_overall = time.time()
    for i, (year, months) in enumerate(chunks, 1):
        label = chunk_label(year, months)
        target = ERA5_DIR / f"era5_saros_{label}.nc"
        print(f"[{i:3d}/{len(chunks)}] {label}  →  {target.name}")

        if file_is_valid(target):
            print(f"      ↻ skip (already valid)")
            skipped += 1
            continue

        if download_chunk(client, year, months, target):
            succeeded += 1
        else:
            failed += 1
            failed_chunks.append(label)

    elapsed_min = (time.time() - t_overall) / 60
    existing = sorted(ERA5_DIR.glob("era5_saros_*.nc"))
    total_mb = sum(f.stat().st_size for f in existing) / (1024 * 1024)

    print("\n" + "=" * 72)
    print(" DOWNLOAD SUMMARY")
    print("=" * 72)
    print(f" Wall clock      : {elapsed_min:.1f} min")
    print(f" Newly downloaded: {succeeded}")
    print(f" Already present : {skipped}")
    print(f" Failed          : {failed}  {failed_chunks if failed_chunks else ''}")
    print(f" Files on disk   : {len(existing)}  ({total_mb:.1f} MB)")

    if failed:
        print(f"\n⚠ {failed} chunk(s) failed. Re-run to retry — "
              f"completed chunks are skipped.")
        return 1

    expected = len(SITE.years) * (12 // CHUNK_MONTHS +
                                  (1 if 12 % CHUNK_MONTHS else 0))
    print(f"\n✓ ALL CHUNKS DOWNLOADED ({len(existing)} files).")
    print("\nNext step: python scripts/03_process_era5.py")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted. Re-run to resume — completed chunks skipped.")
        sys.exit(130)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
