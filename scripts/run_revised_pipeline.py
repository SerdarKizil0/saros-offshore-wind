"""
Run the revised production pipeline and write results/revised/MANIFEST.json.

    python scripts/run_revised_pipeline.py

Primary wind input (since Phase 5-PRE-B): ERA5 1994-2024 at 40.50 N 26.25 E via
Open-Meteo, pinned in config/wind_data.py (data/external/era5_openmeteo/).
The historical CDS 2014-2024 series is read only for the input QA check; its
results are archived in the results archive folder baseline_2014_2024_cds.

Steps (inputs are all committed; no download):
  04_fit_weibull_aep.py         wind resource, energy, Weibull cross-check, uncertainty, losses, sensitivity,
                                input provenance
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
sys.path.insert(0, str(ROOT))
from config import wind_data as wd  # noqa: E402
REV = ROOT / "results" / "revised"
STEPS = ["scripts/04_fit_weibull_aep.py", "scripts/06_emissions_and_scenarios.py", "scripts/07_site_screening.py"]

DESCRIPTION = {
    "wind_resource.json": "1. Wind resource statistics (ERA5 node, hub height 105 m)",
    "energy_yield.json": "2. Empirical AEP and capacity factor (primary estimator)",
    "weibull_crosscheck.json": "3. Weibull fit (descriptive) and AEP cross-check",
    "interannual_and_sampling.json": "4. Observed interannual variability and sampling CI of the 1994-2024 mean "
                                     "(31 annual values)",
    "annual_energy.csv": "4. Annual energy table (calendar years)",
    "wind_speed_sensitivity.json": "5. Wind-speed sensitivity experiments (not probabilities)",
    "loss_scenarios.json": "6. Loss scenarios (labelled assumptions)",
    "emissions.json": "7. Avoided operational CO2 (primary) and life-cycle GHG (secondary)",
    "scenarios.json": "8. Active deployment scenarios S1-S3 (illustrative)",
    "site_screening.json": "9. Geographic and environmental screening",
    "input_provenance.json": "10. Primary wind input provenance and calibration QA against the CDS series",
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
        "inputs": {"wind_series": wd.PRIMARY.rel_path,
                   "wind_series_sha256": hashlib.sha256(wd.PRIMARY.path.read_bytes()).hexdigest(),
                   "wind_series_key": wd.PRIMARY.key, "period": wd.PRIMARY.period_label,
                   "data_product": wd.PRIMARY.data_product,
                   "comparison_only": {"wind_series": wd.HISTORICAL_CDS_2014_2024.rel_path,
                                       "sha256": wd.HISTORICAL_CDS_2014_2024.sha256,
                                       "role": "input QA; historical results in the results archive "
                                               "folder baseline_2014_2024_cds"}},
        "files": {f: {"description": d, "sha256": hashlib.sha256((REV / f).read_bytes()).hexdigest()}
                  for f, d in DESCRIPTION.items()},
        "documentation": ["docs/review/PHASE4B_INTEGRATION.md", "docs/review/PHASE5PRE_B_BASELINE_INTEGRATION.md"],
    }
    (REV / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\n✓ MANIFEST written ({len(manifest['files'])} files) at {dt.date.today()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
