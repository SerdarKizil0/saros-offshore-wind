# Results

| Folder | Status | Use |
|---|---|---|
| `revised/` | **Authoritative** pre-submission model estimates (Phase 4B). `MANIFEST.json` lists files, descriptions and SHA-256 | All future manuscript tables and figures must read from here |
| `provisional/phase2a … phase4a/` | Review-phase outputs | Evidence trail; not for publication tables |
| `archive/baseline_original_curve/` | Historical results as originally published (retired curve, Weibull Monte Carlo, S4) | Historical comparison only |

Regenerate `revised/` with `python scripts/run_revised_pipeline.py`. The figures in
`figures/` and `figures_final/` still show the pre-revision results and must be
regenerated from `revised/` before submission.
