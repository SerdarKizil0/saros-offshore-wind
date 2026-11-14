# Results

| Folder | Status | Use |
|---|---|---|
| `revised/` | **Authoritative** pre-submission model estimates. Since Phase 5-PRE-B: primary period **1994–2024**, ERA5 via Open-Meteo (calibrated), node 40.50° N 26.25° E. `MANIFEST.json` lists files, descriptions, SHA-256 and the pinned input | All future manuscript tables and figures must read from here |
| `archive/baseline_2014_2024_cds/` | Historical results (Phase 4B to 5-PRE): CDS ERA5 2014–2024, byte-identical copy of the former `revised/` | Historical comparison and regression tests only; never mixed with the primary results |
| `provisional/phase2a … phase5pre/` | Review-phase outputs | Evidence trail; not for publication tables |
| `archive/baseline_original_curve/` | Historical results as originally published (retired curve, Weibull Monte Carlo, S4) | Historical comparison only |

Regenerate `revised/` with `python scripts/run_revised_pipeline.py` (no download; the
input is committed and checksum-pinned). The figures in `figures/revised/` were generated
from the 2014–2024 results now in `archive/baseline_2014_2024_cds/`; the figures in
`figures/` and `figures_final/` show the pre-revision results. All must be regenerated
from `revised/` before submission (Phase 5C).
