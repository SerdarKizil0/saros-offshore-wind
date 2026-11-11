"""
Run the revised production pipeline and write results/revised/MANIFEST.json.

    python scripts/run_revised_pipeline.py

Steps (inputs are all committed; no download):
  04_fit_weibull_aep.py         wind resource, energy, Weibull cross-check, uncertainty, losses, sensitivity
  06_emissions_and_scenarios.py avoided operational CO2, life-cycle GHG, active scenarios S1-S3
  07_site_screening.py          bathymetry, protected-area overlap, packing and screening classes

Scripts 01-03 (ERA5 download and processing) are only needed to regenerate
the committed Parquet. The legacy scripts in scripts/legacy/ are not part of
this pipeline.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REV = ROOT / "results" / "revised"
STEPS = ["scripts/04_fit_weibull_aep.py", "scripts/06_emissions_and_scenarios.py", "scripts/07_site_screening.py"]

DESCRIPTION = {
    "wind_resource.json": "1. Wind resource statistics (ERA5 node, hub height 105 m)",
    "energy_yield.json": "2. Empirical AEP and capacity factor (primary estimator)",
    "weibull_crosscheck.json": "3. Weibull fit (descriptive) and AEP cross-check",
    "interannual_and_sampling.json": "4. Observed interannual variability and sampling CI of the 11-year mean",
    "annual_energy.csv": "4. Annual energy table (calendar years)",
    "wind_speed_sensitivity.json": "5. Wind-speed sensitivity experiments (not probabilities)",
    "loss_scenarios.json": "6. Loss scenarios (labelled assumptions)",
    "emissions.json": "7. Avoided operational CO2 (primary) and life-cycle GHG (secondary)",
    "scenarios.json": "8. Active deployment scenarios S1-S3 (illustrative)",
    "site_screening.json": "9. Geographic and environmental screening",
}


def main() -> int:
    for step in STEPS:
        print(f"\n=== {step} ===")
        r = subprocess.run([sys.executable, str(ROOT / step)], cwd=ROOT)
        if r.returncode != 0:
            print(f"✗ {step} failed")
            return r.returncode
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip() or None
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "scripts", "config", "data"], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if commit and dirty:
        commit += "+uncommitted-changes"
    manifest = {
        "status": "PRE-SUBMISSION MODEL ESTIMATES — not validated project forecasts",
        "generated_by": "scripts/run_revised_pipeline.py",
        "code_commit_at_generation": commit,
        "inputs": {"wind_series": "data/processed/wind_hub_105m.parquet",
                   "wind_series_sha256": hashlib.sha256((ROOT / "data/processed/wind_hub_105m.parquet")
                                                        .read_bytes()).hexdigest()},
        "files": {f: {"description": d, "sha256": hashlib.sha256((REV / f).read_bytes()).hexdigest()}
                  for f, d in DESCRIPTION.items()},
        "documentation": "docs/review/PHASE4B_INTEGRATION.md",
    }
    (REV / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\n✓ MANIFEST written ({len(manifest['files'])} files) at {dt.date.today()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
