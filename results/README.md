# Results

| Folder | Status | Use |
|---|---|---|
| `revised/` | **Authoritative** pre-submission model estimates. Since Phase 5-PRE-B: primary period **1994–2024**, ERA5 via Open-Meteo (calibrated), node 40.50° N 26.25° E. Since Phase 5B-0 it also holds the sensitivity outputs (period selection, rolling 11-year windows, grid node, ERA5–GWA discrepancy) and `sensitivity_index.json`, which lists the six separate, non-combinable categories. `MANIFEST.json` lists files, descriptions, SHA-256 and the pinned inputs | All future manuscript tables and figures must read from here |
| `archive/baseline_2014_2024_cds/` | Historical results (Phase 4B to 5-PRE): CDS ERA5 2014–2024, byte-identical copy of the former `revised/` | Historical comparison and regression tests only; never mixed with the primary results |
| `provisional/phase2a … phase5pre/` | Review-phase outputs | Evidence trail; not for publication tables |
| `archive/baseline_original_curve/` | Historical results as originally published (retired curve, Weibull Monte Carlo, S4) | Historical comparison only |

Regenerate `revised/` with `python scripts/run_revised_pipeline.py` (no download; the
input is committed and checksum-pinned). Since Phase 5C-1 the publication figures in
`figures/revised/` are generated from `revised/` by `scripts/12_build_figures.py`; the
figures in `figures/` and `figures_final/` show the pre-revision results and are not for
publication.
