# Phase 3A — Energy estimator and uncertainty framework

*11 November 2026. This phase uses only the committed hourly ERA5 series
(`data/processed/wind_hub_105m.parquet`), the OEDB V164/9500 curve and the
nominal losses. The wind data, power curve, emission factors, `results/*.json`,
archived results, Phase 2A/2B outputs and the manuscript are unchanged. No
avoided-emission quantities are computed. All outputs are **provisional**.*

**Reproduce:**

```bash
python scripts/phase3a_energy_uncertainty.py   # writes results/provisional/phase3a/{energy_uncertainty.json, annual_energy.csv}
python -m pytest -q tests/                     # 30 passed
```

---

## 1. Which estimator should be primary?

**Recommendation:** use **empirical hourly power conversion** as the primary
estimator. Keep the Weibull fit only as a descriptive statistic and a
cross-check.

Reasons:

- The hourly series is the actual model output. Converting each hour through
  the power curve requires no distributional assumption.
- The Weibull fit misrepresents the speed band where the power curve is
  steepest (Table 1).
- This choice is **not** made because the empirical estimate is higher. The
  Weibull fit mis-weights in both directions: it overstates 3–7 m/s and
  12–17 m/s and understates 8–12 m/s.

### Equations

- p_h = P(U_h): hourly electrical power from the OEDB curve, using
  `scripts/04` `power_from_speed`, which is imported directly.
- Gross capacity factor for any set of hours H: CF_g = Σ_H p_h / (P_r · |H|),
  where P_r = 9 500 kW. This is time-weighted, so leap-year hours count
  normally.
- Net capacity factor: CF_n = CF_g · η, where
  η = (1 − L_wake) · A · (1 − L_elec) = 0.92 · 0.95 · 0.97 = 0.84778
  (the nominal baseline).
- Energy for an average year: AEP = CF · P_r · 8 766 h (8 766 h = 365.25 d).
  Per MW of capacity: CF · 8.766 GWh MW⁻¹ yr⁻¹.

**Year normalisation.** Phase 2A divided total energy by 11. That implies
8 766.5 h per year, because the sample contains 3 leap years in 11 instead of
the long-run 2.75. Using CF × 8 766 h removes this sample artefact. The
difference is only +0.006%. The time-weighted CF and the mean of the annual
CFs differ by 0.0009 percentage points.

### Table 1 — Why Weibull-based AEP is 1.85% lower

Same curve, archived k = 2.035 and c = 8.080. The figures are each bin's
contribution to gross CF, in percentage points.

| Wind-speed bin (m/s) | Empirical hours (%) | Weibull probability (%) | Empirical contribution | Weibull contribution | Difference |
|---|---|---|---|---|---|
| 3–7 | 37.0 | 40.1 | 3.13 | 3.39 | +0.26 |
| 7–8 | 10.0 | 9.9 | 2.70 | 2.66 | −0.04 |
| **8–12** | **30.1** | **26.9** | **17.58** | **15.55** | **−2.03** |
| 12–17 | 8.4 | 9.6 | 8.23 | 9.40 | +1.18 |
| Other bins | | | | | +0.03 |
| **Total** | | | **32.66** | **32.06** | **−0.60 (−1.85%)** |

The ERA5 distribution has more hours at 8–12 m/s, where the curve rises
fastest, than a two-parameter Weibull can represent.

**Why the Monte Carlo P50 is lower still.** The Phase 2A Monte Carlo (MC)
P50 of 2.366 equals the nominal-loss Weibull value (2.383) multiplied by
0.99288, which is the ratio between the *means* and the *modes* of the
asymmetric triangular loss distributions. Reproduced: 2.3656 against
2.3655.

The full chain is: empirical 2.427 → Weibull −1.85% → loss asymmetry
−0.71% → MC P50 2.366.

**Erratum.** The Phase 2A report stated that the empirical–Weibull gap
"widens from −2.7% to −3.4%". It actually **narrows from −2.7% to −1.8%**.
`PHASE2A_POWER_CURVE.md` has been corrected.

---

## 2. Sources of uncertainty and how each is treated

| Source | Data basis | Treatment |
|---|---|---|
| Year-to-year meteorological variability | 11 calendar years of ERA5 [MOD] | Quantified (empirical spread; no distribution fitted) |
| Sampling uncertainty of the 11-year mean | Same 11 years | Quantified: year-block bootstrap, with t-interval and jackknife checks |
| Representativeness of 2014–2024 for the long-term climate | Would need a longer record | **Not quantified.** No new data was downloaded |
| Wake, availability, electrical losses | No site data; literature-type assumptions | **Scenarios** (low / nominal / high), not probabilities |
| ERA5 spatial representation and level (the GWA difference) | Phase 2B | **Sensitivity only.** The ERA5–GWA difference is not an error distribution |
| Power curve (digitised, not certified) | Phase 1/2A | Sensitivity only |
| Air density, shear extrapolation, hourly vs 10-min basis, layout wakes, curtailment, degradation | None in this repository | Listed; not quantified |

**Why the existing Weibull MC is not kept for energy uncertainty:**

- c is sampled with σ_c = the standard deviation of the 11 *annual* fits.
  That represents single-year variability, so its 6.6% coefficient of
  variation is close to the annual energy CoV (7.0%). The MC therefore
  mislabels year-to-year variability as uncertainty of the long-term mean.
- σ_k = 0.04 has no stated basis, and k contributes almost nothing.
- The triangular loss distributions turn assumed ranges into
  probabilities.
- Model-structural uncertainty is missing.

---

## 3. Results

### 3.1 Annual values (`annual_energy.csv`)

Net yield uses CF × 8.766 GWh MW⁻¹; hours are 8 760 or 8 784 by calendar
year.

| Year | Mean U_hub (m/s) | Gross CF | Net CF | Net yield (GWh MW⁻¹ yr⁻¹) |
|---|---|---|---|---|
| **2014** | 6.55 | 26.80% | 22.72% | **1.992** |
| 2015 | 7.17 | 32.10% | 27.22% | 2.386 |
| 2016 (leap) | 7.41 | 34.00% | 28.83% | 2.527 |
| 2017 | 6.97 | 31.56% | 26.75% | 2.345 |
| 2018 | 7.37 | 34.66% | 29.38% | 2.576 |
| 2019 | 7.19 | 32.46% | 27.52% | 2.412 |
| **2020** (leap) | 7.39 | 35.63% | 30.21% | **2.648** |
| 2021 | 7.26 | 33.53% | 28.43% | 2.492 |
| 2022 | 7.17 | 33.45% | 28.36% | 2.486 |
| 2023 | 7.23 | 33.05% | 28.02% | 2.456 |
| 2024 (leap) | 7.18 | 32.02% | 27.15% | 2.380 |

**Year-to-year variability:**

- Coefficient of variation of annual energy: **7.0%** (3.8% without 2014).
  Wind speed varies by 3.35%, so energy varies about 2.1 times as much.
- Range: −17.9% (2014) to +9.1% (2020) relative to the 11-year mean.
- Lag-1 autocorrelation of the annual CFs: r = +0.03, so treating years as
  independent is reasonable.

### 3.2 Central estimate and interval

| Quantity | Value |
|---|---|
| **Central estimate** (empirical, nominal losses) | **Net CF 27.69%, 2.427 GWh MW⁻¹ yr⁻¹**; gross 27.20 GWh/turbine (CF 32.66%) |
| 90% CI of the 2014–2024 mean, year-block bootstrap (B = 20 000, seed 2026) | 2.340–2.500 GWh MW⁻¹ yr⁻¹ (±3.3%) |
| 90% CI of the mean, t-interval (df = 10) | **2.334–2.520 GWh MW⁻¹ yr⁻¹ (±3.8%)** |
| Standard error of the mean (bootstrap / classical / jackknife) | 2.02% / 2.11% / 2.11% |
| Jackknife: omitting 2014 | Mean +1.8% (every other year: −0.9% to +0.3%) |

Is the bootstrap appropriate? Years are effectively independent and
resampling whole calendar years keeps the seasonal and hourly structure, so
in principle yes. But with n = 11 the percentile bootstrap is known to be
too narrow (by roughly √((n−1)/n) plus discreteness) and depends on a single
outlier year. **Recommendation:** report the t-interval (±3.8%) and cite the
bootstrap as a consistent check.

These intervals describe sampling uncertainty of an 11-year ERA5 mean only.
They are **not** P90 yields and not single-year production ranges. Single
years spread across 1.99–2.65 GWh MW⁻¹ yr⁻¹.

### 3.3 Loss scenarios (assumptions, not probabilities)

| Scenario | Wake | Availability | Electrical | η | Net yield (GWh MW⁻¹ yr⁻¹) | vs nominal |
|---|---|---|---|---|---|---|
| Low loss | 5% | 97% | 2% | 0.903 | 2.586 | +6.5% |
| **Nominal (baseline)** | 8% | 95% | 3% | 0.848 | **2.427** | 0 |
| High loss | 12% | 92% | 4% | 0.777 | 2.225 | −8.3% |

The bounds are the endpoints already used in `scripts/06`. There is no site
evidence for them, and wake loss depends on layout and capacity density
(S1–S4), which is not modelled.

### 3.4 Relative magnitudes (one table; do not add the rows)

| Component | Effect on mean AEP | Type |
|---|---|---|
| Sampling of the 11-year mean | ±3.8% (90% CI, t) | Probabilistic |
| Year-to-year variability (single years) | CoV 7.0%; −18% / +9% range | Observed spread |
| Losses | −8.3% / +6.5% | Scenario |
| Wind-speed level ±5% / ±10% (Phase 2B) | ±10% / −20.4%, +19.7% | Sensitivity |
| Power-curve choice (retired against OEDB) | +11.8% | Illustrates curve sensitivity; not a bound |

These components are deliberately **not combined** into a single total
interval: only the first row has a probabilistic basis.

### 3.5 Comparison of estimates (net GWh MW⁻¹ yr⁻¹)

| Estimate | Value | Why it differs |
|---|---|---|
| Original deterministic (retired curve, total ÷ 11) | 2.714 | Implausible power curve (+11.8%) |
| Original MC P50 (retired curve) | 2.622 | Plus Weibull (−2.7%) and loss asymmetry |
| Phase 2A empirical (OEDB, total ÷ 11) | 2.4275 | Corrected curve |
| Phase 2A Weibull, nominal losses | 2.383 | Weibull shape −1.85% |
| Phase 2A MC P50 | 2.366 | Plus triangular means ≠ modes (−0.71%) |
| **Phase 3A central** (empirical, CF × 8 766 h) | **2.4274** | Phase 2A empirical −0.006% (year normalisation) |

---

## 4. Tests

`tests/test_phase3a_energy.py` contains 7 tests (30 in the whole suite, all
passing). They check:

- 11 calendar years, leap years 2016/2020/2024, 8 760 / 8 784 hours each,
  96 432 in total;
- energy conservation: the annual sums equal the total;
- units: kW/kW for CF, and MW·h → GWh;
- that the central estimate differs from Phase 2A only by the factor
  (96 432/11)/8 766;
- that the Weibull bin contributions sum exactly to the Weibull total
  (0.320591);
- bootstrap reproducibility under a fixed seed, and that the interval
  contains the mean and is narrower than the year range;
- that the loss scenarios are ordered;
- that the committed outputs equal a fresh run.

---

## 5. Remaining limitations

1. Everything is conditional on ERA5 at one node being correct. The ±10%
   ERA5–GWA disagreement, about ±20% in AEP, outweighs every quantified
   term.
2. Eleven years give a weak estimate of the mean. A single calm year (2014)
   moves the mean by 1.8%, and long-term representativeness is unknown.
3. Losses are assumptions. No layout or wake model exists, so the scenario
   capacities S1–S4 share one wake value.
4. The power curve is digitised, not certified. Air density, shear,
   averaging time and turbine availability modes are not modelled.
5. Production `scripts/04` and `06` and `results/*.json` still reflect the
   retired curve and the Weibull MC. Replacing them is a separate step.

## 6. Manuscript changes required later (not made here)

- **Primary energy figure:** state the empirical estimate, 27.7% net CF and
  2.43 GWh MW⁻¹ yr⁻¹ (gross 27.2 GWh per turbine), defined as CF × 8 766 h.
- **Report two separate things:**
  - the 90% CI of the 11-year mean (2.33–2.52, sampling only);
  - year-to-year variability (CoV 7.0%; 2014 at −18%).
- **Report losses and wind-speed level as scenarios and sensitivities**,
  each in its own place.
- **Remove the Weibull-based MC as the energy uncertainty method.** Remove
  the "P10–P90 = uncertainty" wording and any P90/bankable wording.
- **Keep the Weibull fit as descriptive only.** State its −1.85% AEP
  difference and the 8–12 m/s misfit.
- **Replace "inter-annual variability 3.2%"** with the speed and energy
  figures above.
- **Recompute downstream emission figures** from the new central estimate
  in the next phase. That is not done here.
