# Legacy scripts (retired in Phase 4B)

| Script | Retired because |
|---|---|
| `04_fit_weibull_aep.py` | Original version: total ÷ 11 years, all four scenarios incl. S4, written to `results/weibull_aep_results.json`. Replaced by the revised `scripts/04_fit_weibull_aep.py` |
| `06_run_monte_carlo.py` | Seven-variable Weibull Monte Carlo: σ_c represents single-year variability, σ_k has no basis, triangular grid factor mixes accounting methods and units, life-cycle CO₂-eq subtracted from grid CO₂ |
| `07_compare_with_grid.py` | Reads the retired Monte Carlo samples; includes S4 |
| `08_generate_mc_figures.py` | Figures from the retired Monte Carlo |
| `09_generate_extra_figures.py` | Hard-coded old values, unsourced fossil-mix shares, CO₂-eq fuel factors, S4 |

Each script exits immediately unless `SAROS_ALLOW_LEGACY=1` is set, so the
retired files in `results/` cannot be recreated by accident. The archived
outputs are in `results/archive/baseline_original_curve/`. The archived Monte
Carlo is reproduced bit-for-bit by `scripts/phase2a_power_curve_rerun.py`
(original curve), without running these scripts.
