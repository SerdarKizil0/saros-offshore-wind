# Phase 3B — Corrected avoided-emissions accounting

*11 November 2026. Energy input: the Phase 3A central estimate. The turbine
curve, ERA5 data, losses and capacity scenarios are unchanged, as are the
production model, `results/*.json`, the archived and Phase 2A/2B/3A outputs,
and the manuscript. All outputs are **provisional**.*

**Reproduce:**

```bash
python scripts/phase3b_carbon_accounting.py   # writes results/provisional/phase3b/carbon_accounting.json
python -m pytest -q tests/                    # 39 passed
```

---

## 1. Verified accounting basis

| Factor (2023) | Value | Gas / unit | Document | Verified |
|---|---|---|---|---|
| **Combined margin, wind/solar** | **0.6242** | **tCO₂/MWh** (CO₂ only) | ETKB‑EVÇED‑FRM‑039 Rev.03, period 2023, published 26.12.2025, p.2 | ✓ |
| Operating margin | 0.7134 | tCO₂/MWh | Same form, p.1 | ✓ |
| Build margin | 0.3567 | tCO₂/MWh | Same form, p.1 | ✓ |
| Combined margin, other renewables | 0.5350 | tCO₂/MWh | Same form, p.2 | ✓ (not used) |
| Generation average | 0.430 | tCO₂/MWh | ETKB‑EVÇED‑FRM‑042 Rev.01, period 2023, published 26.12.2025, p.1 | ✓ |
| Generation average, all GHGs | 0.434 | **tCO₂‑eq/MWh** | Same form, p.1 | ✓ |
| Fuel factors: lignite / imported coal / natural gas | 1.122 / 0.800 / 0.400 (CO₂); 1.133 / 0.803 / 0.405 (CO₂‑eq) | Both columns | Same form, p.2 | ✓ |

**Method checks:**

- The grid form uses UNFCCC CDM **Tool 07 v07.0**. Its wind/solar combined
  margin reproduces exactly as 0.75 × OM + 0.25 × BM = 0.62423 (test
  included).
- The form says the combined margin "kullanılabilecektir", i.e. it **may be
  used** for GHG-reduction calculations. The manuscript's "officially
  mandated" overstates this; "official factor published for this purpose" is
  accurate.
- The generation-average form follows the IEA *Emission Factors 2021*
  method.
- Checksums of both PDFs are recorded in the script.

**Life-cycle intensity of offshore wind** (gCO₂‑eq/kWh = kgCO₂‑eq/MWh):

| Source | Value | Conditions |
|---|---|---|
| Bonou, Laurent & Olsen (2016), *Applied Energy* 180:327, Table 4 | 10.9 (4 MW, 130 m rotor); 7.8 (6 MW, 154 m rotor). The abstract says "< 11" | Siemens plants, 9.5–10 m/s, about 59% capacity factor to grid, 20/25-year life, **end-of-life recycling credited** (Table 3) |
| IPCC AR5 WGIII Annex III (Schlömer et al. 2014), Table A.III.2 | **8 / 12 / 35** (minimum / median / maximum) | Literature harmonisation |

**Refuted claims in the current text and code:**

- **"IPCC 2025"** does not exist.
- The range **"8–14"** is wrong; AR5 gives 8–35.
- **"No recycling credits, therefore conservative"** is wrong. Bonou credits
  recycling, and its plants are much windier than Saros. Rescaling the Bonou
  values to the Saros yield per MW (2 427 against about 5 150 MWh MW⁻¹ yr⁻¹)
  gives roughly 17–23 g/kWh. This is illustrative only: it assumes equal
  embodied emissions per MW and equal lifetime.

---

## 2. The methodological problem and its resolution

The original model computed
`avoided = AEP × (Triangular(434, 624.2, 713.4) − Triangular(8, 11, 14))`.
This has three defects:

1. **Methods mixed into one probability distribution.** Generation average
   (attributional), combined margin (Tool 07 crediting) and operating margin
   (short-run marginal) answer different questions. They are not samples of
   one uncertain quantity. The triangle's median is 597 against the mode of
   624.2, and the grid factor drove about 71% of the variance (Phase 0
   review).
2. **Units mixed.** The 434 value is CO₂‑eq, while 624.2 and 713.4 are
   CO₂‑only. The manuscript labels all three "gCO₂‑eq".
3. **Boundaries mixed.** A cradle-to-grave wind CO₂‑eq intensity was
   subtracted from a combustion-only grid CO₂ factor. That factor excludes
   upstream fossil-fuel emissions and non-CO₂ gases, so the subtraction is
   neither like-for-like nor a "net life-cycle benefit".

**Defensible structure, now implemented:**

- **Primary:** avoided operational grid CO₂ = E × 0.6242 tCO₂/MWh.
- **Secondary:** life-cycle GHG of the wind generation = E × intensity, in
  tCO₂‑eq. It is reported alongside, **not subtracted**.
- **Context:** operating margin, build margin and generation average
  (CO₂ and CO₂‑eq). These are labelled methods, not bounds.

All factors are static 2023 values. Over a 25–30-year project life the
displaced margin is likely to fall: the build margin of 0.357 already
shows that recent additions are cleaner. No forecast is made here.

---

## 3. Results

Energy: E = 2 427.37 MWh MW⁻¹ yr⁻¹ (Phase 3A, empirical, nominal losses).
Its sampling-only 90% CI is 2 334–2 520 MWh MW⁻¹ yr⁻¹.

**Unit chain:** MWh × tCO₂/MWh = tCO₂. For life-cycle values,
MWh × g/kWh ÷ 1000 = tCO₂‑eq.

### 3.1 Per MW installed per year

| Quantity | Factor | Result | vs primary |
|---|---|---|---|
| **Primary: avoided grid CO₂ (combined margin, wind/solar)** | 0.6242 tCO₂/MWh | **1 515.2 tCO₂ MW⁻¹ yr⁻¹** (90% CI 1 457–1 573, energy sampling only) | — |
| Context: operating margin | 0.7134 tCO₂/MWh | 1 731.7 tCO₂ | +14.3% |
| Context: build margin | 0.3567 tCO₂/MWh | 865.8 tCO₂ | −42.9% |
| Context: generation average (CO₂) | 0.430 tCO₂/MWh | 1 043.8 tCO₂ | −31.1% |
| Context: generation average (CO₂‑eq) | 0.434 tCO₂‑eq/MWh | 1 053.5 **tCO₂‑eq** | different unit |
| **Secondary: life-cycle GHG of wind** (AR5 median) | 12 g/kWh | **29.1 tCO₂‑eq MW⁻¹ yr⁻¹** | — |
| Life-cycle, AR5 range | 8–35 g/kWh | 19.4–85.0 tCO₂‑eq | |
| Life-cycle, Bonou plants | 7.8–10.9 g/kWh | 18.9–26.5 tCO₂‑eq | |

The 90% CI on the primary value propagates **only** the sampling
uncertainty of the 2014–2024 mean energy through a fixed factor. It is
**not** total carbon uncertainty. It excludes the wind-speed level
(about ±20% for ±10% speed), losses, the choice of power curve, the
accounting method and future change in the grid mix.

As an indicative ratio only (the gases and boundaries differ), life-cycle
GHG equals about 1.9% (1.3–5.6%) of the primary avoided CO₂.

### 3.2 Capacity scenarios (CO₂ in kt yr⁻¹; CI = energy sampling only)

| Scenario | MW | Net energy (GWh yr⁻¹) | **Avoided CO₂, combined margin** | Operating margin | Generation average (CO₂) | Life-cycle (kt CO₂‑eq), AR5 median [range] |
|---|---|---|---|---|---|---|
| S1 | 247.0 | 600 | **374** [360–389] | 428 | 258 | 7.2 [4.8–21.0] |
| S2 | 503.5 | 1 222 | **763** [734–792] | 872 | 526 | 14.7 [9.8–42.8] |
| S3 | 997.5 | 2 421 | **1 511** [1 453–1 569] | 1 727 | 1 041 | 29.1 [19.4–84.7] |
| S4 | 1 738.5 | 4 220 | **2 634** [2 533–2 735] | 3 011 | 1 815 | 50.6 [33.8–147.7] |

Capacity scenarios scale linearly with the same per-MW wake assumption; no
layout effects are modelled.

### 3.3 Relationship to the previously reported 1 525 tCO₂/MW/yr

| Estimate | tCO₂ MW⁻¹ yr⁻¹ | Composition |
|---|---|---|
| Original manuscript, P50 | 1 525 (P10–P90 1 277–1 754) | Retired curve with Weibull MC (2.622 GWh/MW) × mixed-method factor (effective 581.6 g/kWh, of which 11 g is CO₂‑eq subtracted) |
| Phase 2A provisional MC P50 | 1 375 | Corrected curve, old emissions method |
| **Phase 3B primary** | **1 515.2** | 2.427 GWh/MW × 624.2 g/kWh |

The new value is −0.6% from the old, but the agreement is
**coincidental**:

- energy fell 7.4% (power curve and estimator);
- the effective factor rose 7.3% (mixed-method median replaced by the
  official combined margin, with no life-cycle subtraction).

The old P10–P90 band was mostly the spread between accounting methods,
presented as statistical uncertainty.

---

## 4. Conditional and unvalidated elements

1. **Energy.** All values scale one-to-one with E, which relies on one ERA5
   node and a digitised curve. The ±10% ERA5–GWA wind disagreement means
   about ±20% in E and in avoided CO₂ (Phase 2B).
2. **Static 2023 factors.** Future displacement depends on grid evolution,
   curtailment and dispatch. Neither the combined margin nor the operating
   margin is a forecast.
3. **Combined margin is a crediting convention.** It is not a measured
   marginal response of the Turkish system.
4. **Life-cycle intensities are not Saros-specific.** Water depth, distance
   to shore, turbine size, lifetime and recycling all differ from the
   literature plants, and the lower Saros capacity factor raises per-kWh
   intensity.
5. **Fuel-resolved "fossil displacement" scenario** (1.98 / 1.95 Mt in the
   manuscript). Its fuel shares (36.8 / 33.3 / 29.9%) are unsourced, and its
   factors are the CO₂‑eq column. It was **not recomputed** and should be
   dropped or rebuilt from TEİAŞ generation data.

---

## 5. Required later changes (not made here)

**Code (`config/emissions.py`):**

- Rename or relabel `GRID_CO2.low` (434, which is CO₂‑eq). Use 0.430 for a
  CO₂ comparison.
- Delete "IPCC 2025 range 8–14" and "no recycling credit".
- Note that the fuel factors are CO₂‑eq.

**Code (`scripts/06` and `07`):** stop sampling the grid factor and the
life-cycle intensity from triangular distributions, and stop subtracting
life-cycle from grid.

**Manuscript:**

| Location | Change |
|---|---|
| Abstract, §1, §3.7, §4.4–4.6, §5.3, conclusion | Primary metric: "avoided grid CO₂ (official 2023 combined margin)", 1 515 tCO₂ MW⁻¹ yr⁻¹ and 1.51 Mt yr⁻¹ for S3 (≈1 GW). State life-cycle GHG separately (about 29 tCO₂‑eq MW⁻¹ yr⁻¹; 19–85) |
| §3.7 l.165, §4.5 l.136, §5.3 l.62 | "officially sanctioned / mandated" → "official factor published for this purpose" |
| §1 l.8; §3.7 l.169; §3.8 l.203; §5.3 l.64; Tables 5–6 | Correct the units: 434 is CO₂‑eq (use 430 for CO₂); 713.4 and 624.2 are tCO₂/MWh, not CO₂‑eq |
| §1 l.19; §3.7 l.175–177; Tables 5–6 | Life-cycle: AR5 8 / 12 / 35; Bonou 7.8–10.9 with recycling credited. Remove "IPCC 2025" and "conservative upper estimate" |
| §3.8; Table 6 | Remove the grid and life-cycle triangular distributions. Report operating margin, build margin and generation average as labelled method scenarios |
| §4.5, §5.3, Figure 6, Table 7 | Rebuild the fuel-resolved comparison with CO₂ factors and sourced shares, or remove it. The "≈69×" ratio compares different boundaries |
| §4.6, Figure 7, Table 4 | Recompute household and car equivalents from the new energy and CO₂ values (not done here) |
| Wherever avoided-CO₂ intervals appear | Label them "energy sampling only, fixed 2023 factor". Add the wind-speed sensitivity (about ±20%) as a separate statement |

---

## Sources

- ETKB/EVÇED, *Türkiye Ulusal Elektrik Şebekesi Emisyon Faktörü Bilgi Formu*,
  2023 (FRM‑039 Rev.03):
  https://enerji.gov.tr/Media/Dizin/EVCED/tr/%C3%87evreVe%C4%B0klim/%C4%B0klimDe%C4%9Fi%C5%9Fikli%C4%9Fi/TUESEmisyonFktr/Belgeler/Sebeke_EF_Bilgi_Formu_2023.pdf
- ETKB/EVÇED, *Türkiye Elektrik Üretimi ve Elektrik Tüketim Noktası Emisyon
  Faktörleri Bilgi Formu*, 2023 (FRM‑042 Rev.01):
  https://enerji.gov.tr/Media/Dizin/EVCED/tr/%C3%87evreVe%C4%B0klim/%C4%B0klimDe%C4%9Fi%C5%9Fikli%C4%9Fi/EmisyonFaktorleri/2023_Turkiye_Elektrik_UretimiveElektrik_Tuketim_Noktasi_Emisyon_Faktorleri.pdf
- Bonou, A., Laurent, A., Olsen, S.I. (2016). *Applied Energy* 180, 327–337,
  doi:10.1016/j.apenergy.2016.07.058. Open copy:
  https://tethys.pnnl.gov/sites/default/files/publications/lca_onshore_offshore.pdf
- Schlömer, S. et al. (2014). Annex III, IPCC AR5 WGIII, Table A.III.2:
  https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-iii.pdf
