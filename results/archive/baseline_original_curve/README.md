# Baseline results — original (retired) power curve

Byte-identical copies of `results/*.json|npz` as committed at `d7bd6b2`
(before Phase 2A). These are the numbers in the current manuscript draft.
They were produced with `config.turbine.POWER_CURVE_ORIGINAL_MS_KW`, which
Phase 1 found to be undocumented and physically implausible (peak Cp 0.564,
rated power at 13 m/s instead of 14 m/s).

Kept unchanged for comparison and regression testing; `SHA256SUMS` lists
the checksums. Corrected, provisional outputs are in `results/provisional/phase2a/`.
See `docs/review/PHASE2A_POWER_CURVE.md`.
