# F: pre-registration (2026-11-22, BEFORE any run)

**Data:** METR eval-analysis-public, time-horizon-1-0 runs file (sha256 f489d117…6236), with a fixed SOTA tie-break (date, then name).

**Null simulator** (calibrated to the real data):
- Resample the real task-family/task/run structure.
- Generate per-model success probabilities from a logistic in log2(task minutes), with model horizons following an exact exponential in release date (doubling 210 d).
- Model-level offsets drawn from the empirical residual SD.
- **Task difficulty jitter shared across models,** to reproduce the cross-model correlation.
- 1000 null datasets, seeds `SeedSequence([33, rep])`.

**Tests (each at nominal 5%):**
- T-iid: OLS of log2(horizon) on (t, t²), F-test on t²;
- T-hb: three-level hierarchical bootstrap (B = 400) percentile CI on the t² coefficient;
- T-v (EXPLORATORY): Vuong exponential vs logistic.

**Bars:**
- (1) T-iid size > 10% (CP-lower > 7%) supports claim 1;
- (2) T-hb size in [3, 7]%;
- (3) **Power:** for the alternative "doubling time halves over the window", report power vs number of models (12, 20, 40) and task count (×1, ×2, ×4), with no bar.

**Real-data run (one-shot, after bars 1–2 are evaluated):** T-hb on the real data with cutoff 2025-11-30. Report the coefficient CI.

**Holdout:** models released after 2025-11-30, if any are in a later METR release. Otherwise this is stated as unavailable.
