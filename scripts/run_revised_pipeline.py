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
  08_sensitivity_representativeness.py
                                period-selection, grid-node and wind-product sensitivity experiments
                                and the index of the six separate uncertainty/sensitivity categories

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
STEPS = ["scripts/04_fit_weibull_aep.py", "scripts/06_emissions_and_scenarios.py", "scripts/07_site_screening.py",
         "scripts/08_sensitivity_representativeness.py"]

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
    "period_sensitivity.json": "11. Period-selection sensitivity at the primary node (sensitivity experiment)",
    "rolling_11yr_windows.csv": "11. All rolling 11-year windows 1979-2024 with ranks",
    "node_sensitivity.json": "12. Grid-node sensitivity, three ERA5 nodes, 1994-2024 (not averaged, not bounds)",
    "wind_product_discrepancy.json": "13. ERA5 vs Global Wind Atlas 4.0 (inter-model disagreement, not validation)",
    "sensitivity_index.json": "14. Index of the six separate uncertainty/sensitivity categories (not combinable)",
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
                   "sensitivity_only": {
                       "role": "period-selection and grid-node sensitivity experiments (scripts/08); never "
                               "replace the primary series",
                       "node_series": {k: {"file": v.rel_path, "sha256": v.sha256, "period_in_file": v.period_label,
                                           "node_lat_lon": [v.node_lat, v.node_lon]}
                                       for k, v in wd.NODE_SERIES.items()},
                       "static": {str(pth.relative_to(ROOT)): sha for pth, sha in
                                  (wd.ERA5_LAND_SEA_MASK, wd.GWA4_WIND_SPEED_100M, wd.EMODNET_NODE_BOX)}},
                   "comparison_only": {"wind_series": wd.HISTORICAL_CDS_2014_2024.rel_path,
                                       "sha256": wd.HISTORICAL_CDS_2014_2024.sha256,
                                       "role": "input QA; historical results in the results archive "
                                               "folder baseline_2014_2024_cds"}},
        "files": {f: {"description": d, "sha256": hashlib.sha256((REV / f).read_bytes()).hexdigest()}
                  for f, d in DESCRIPTION.items()},
        "documentation": ["docs/review/PHASE4B_INTEGRATION.md", "docs/review/PHASE5PRE_B_BASELINE_INTEGRATION.md",
                          "docs/review/PHASE5B0_REVISION_PLAN_ADDENDUM.md"],
    }
    (REV / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\n✓ MANIFEST written ({len(manifest['files'])} files) at {dt.date.today()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
