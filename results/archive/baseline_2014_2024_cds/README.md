# Historical results — 2014–2024 CDS baseline (archived in Phase 5-PRE-B)

These are byte-identical copies of `results/revised/` as committed at
`2ab13c1` (Phase 5-PRE). They were the authoritative results from Phase 4B
until the author adopted 1994–2024 as the primary period on
14 November 2026. `SHA256SUMS` lists the checksums, and the archived
`MANIFEST.json` is the original one.

| Item | Value |
|---|---|
| Wind input | `data/processed/wind_hub_105m.parquet` (CDS ERA5, 40.50° N 26.25° E, 2014–2024, sha256 `0cfc4742…`) |
| Method | As the current pipeline: empirical hourly conversion, OEDB V164/9500, nominal losses, 2023 combined margin |
| Net yield | 2.4274 GWh MW⁻¹ yr⁻¹ (net CF 27.69 %); 90 % sampling CI of the 11-year mean 2.334–2.520 |
| Avoided CO₂ | 1 515.2 tCO₂ MW⁻¹ yr⁻¹ |

**Use:** historical comparison and regression testing only. Do not combine
these values with the 1994–2024 primary results. Phase 5-PRE showed that
2014–2024 is the windiest 11-year window of 1979–2024
(`docs/review/PHASE5PRE_ERA5_ROBUSTNESS.md`).

**Reproduce:**

```bash
python scripts/04_fit_weibull_aep.py --series historical_cds_2014_2024 --out <dir>
```

This reproduces every archived number (`tests/test_historical_baseline_2014_2024.py`).

- `annual_energy.csv` is byte-identical.
- Three keys were renamed to period-neutral names:
  - `sampling_ci_of_11yr_mean` → `sampling_ci_of_period_mean`;
  - `annual_net_cf_cov_pct_excluding_2014` → `annual_net_cf_cov_pct_excluding_min_year`;
  - `ddof1_excluding_2014` → `ddof1_excluding_lowest_year`.
- One label was extended.

The publication figures in `figures/revised/` were generated from these
files. They have not yet been regenerated from the new primary results
(planned for Phase 5C).
