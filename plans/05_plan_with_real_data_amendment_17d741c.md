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

# Real-data amendment (pre-registration, 2026-11-23, written and committed BEFORE the real-data statistics below are run)

**Status: EXPLORATORY reading of one real series. No confirmatory claim. Idea F stays a calibration project: the simulator work (Amendments 1-3) decides which statistics may be trusted; this amendment applies them once.**

## R0. What has already been looked at (disclosure)
- The one-shot T-hb run of the original PLAN was done (`results/F_real.json`: 33 models, 17 SOTA records, quadratic coefficient +0.114 per yr^2, T-hb 95% CI [-0.044, +0.244], not rejected; iid F p = 0.0009, known oversized). That result is already known. **None of the statistics below has been computed on real data**; the only run of this pipeline so far is a smoke test on one synthetic R_null_val dataset (its output is discarded).
- The METR v1.1 holdout (`holdout_data`, `results/F_holdout.json`) was analysed in the first pass: 3 post-cutoff models fall inside the linear 95% prediction interval; T-hb on pre-cutoff v1.1 and on all v1.1 rejects upward. It is already seen, so it is a **descriptive sensitivity only** here (R6), never a confirmation.
- Amendment 2 [internal operations note redacted] is NOT finished (about 72% by cost at writing; size/power of `ols`, `hc3`, `wild`, `perm`, `mb_*` are not yet analysed). Consequence: **the HC3 and wild/permutation rows below carry no size verdict until `analyze_a2.py` has run; they are reported as estimates with a "size pending A2" tag.** The base-grid `iid_all` (OLS F-test) was oversized (8.2% two-sided).

## R1. Data (pinned; the runner refuses to start on a mismatch)
| item | path | sha256 |
|---|---|---|
| METR time-horizon 1.0 runs | `frontier/F3_ai_scaling_trends/data_metr/runs_v1_0.jsonl` | f489d11728909937dad99ba1ed2d7c40efe12a766891e67dbc7c2486a3311236 |
| release dates | `frontier/F3_ai_scaling_trends/data_metr/release_dates.yaml` | 317b92915df5bf935908567a857116bcf6f0c7686ef8b0840897ed04a29232bc |
| simulator parameters | `results/F_simulator_validation.json` | recorded in the result file at run time |
| METR v1.1 runs (R6 only) | `holdout_data/runs_v1_1.jsonl` | 609f904f4b6ae32129388da89d036e00bac511ad94223d2be1e58fc2b45b55cd |
Primary sample: the 33 models with release date <= 2025-11-30 (identical to the simulator's design: M=33, K=170 tasks, 50 families). Per-model y = log2 of the 50% time horizon from the frozen ridge-logistic fit (`fcore.horizons_of`). Models are ordered by (date, name); a record = strict improvement over the running maximum.
Software pins: numpy 2.5.5, scipy 1.18.1 (this Mac, `.venv`); code frozen by sha256: `real_data/real_data_run.py` c8025904a2ba31bb03f5189ab8167a60ec03fe14fef2b58e88ee6f342a539d55; `design/fcore.py` 45cf8a06..., `fdesign.py` ae06a2ad..., `fsim.py` c9fad88c..., `fdesign3.py` 556135eb..., `fdesign4.py` a7927afa..., `grid_a2.py` e38c7ac6... (full hashes in `real_data/PINS.txt`).
**Other public series (idea U, Epoch benchmarks etc.): NOT analysed here.** U has not frozen its series list, U's card forbids reusing F's holdout, and every size/power figure we hold is for the METR run-level design; applying the statistics to a different series would be an uncalibrated use. They are recorded as a follow-up in INTERESTING, not as a failure.

## R2. Null and alternatives in calendar terms
- Window: first to last model release in the sample (reported from the data; the simulator span is the same dates). Growth rate r(t) = d(log2 horizon)/dt in doublings per year; doubling time = 365.25 / r days.
- **H0 (exponential trend):** r(t) is constant over the window, i.e. the true log2 horizon is linear in release date, beta2 = 0. Reference value: doubling time about 210 d (1.74 doublings/y), the null the simulator was run at; the real fitted slope is reported.
- **H1 (acceleration):** r(t) rises over the window, beta2 > 0 (one-sided, upward). Pre-specified *meaningful* acceleration: end-of-window rate >= 2x the start-of-window rate (rr >= 2; at a fixed mean rate of 1.74/y this is a doubling time of about 304 d at the window start falling to about 160 d at the end). Small effects: rr = 1.25 (234 -> 190 d), 1.5 (258 -> 177 d); large: rr = 3 (391 -> 144 d), 4 (473 -> 135 d).
- **H1' (deceleration):** beta2 < 0 (downward tail), reported with the same rules (decelerating logistic early inflection: 239 -> 800 d).
- Curvature is translated to calendar terms by rr_eq = (1+q)/(1-q), q = beta2 * span / rate, with rate = the real all-model linear slope; reported as "not defined" when |q| >= 1. Also reported for the all-model quadratic fit: instantaneous rate and doubling time at the window start and end and rr_hat = end/start (undefined when the start rate is <= 0).

## R3. The tests (all one-sided upward p_up and downward p_dn per the Amendment 2/3 tail rules; nominal 5% per tail; two-sided 5% := min(p_up,p_dn) < 0.025)
Family of six reported with Holm-adjusted p_up across the six (and raw):
1. `hc3`: all-model regression y ~ 1 + t + t^2 on the 33 fixed dates, HC3 t of beta2 vs t(30). Secondary, same regression: `ols` t (t(30)), `wild` (null-restricted wild bootstrap, B=9999), `perm` (residual permutation, B=9999). Estimand: beta2 of the all-model trajectory, free of SOTA selection.
2. `audit`: random audit of 25% of non-records with 1/q weights, parametric-bootstrap p (B=19999, audit redrawn inside the bootstrap). Bias-removing in A3 (rr_eq 1.02), size OK on R_null_val only (not robust to model-offset noise halving: up 9.1%). Because the audit is a random draw, the observed statistic is also recomputed over 200 independent audit draws (median, IQR, range reported); the p-value is the single pre-fixed draw (seed below).
3. `heck`: inverse-Mills corrected SOTA curvature, pb p. Bias-removing (rr_eq 1.07) but size only inconclusive on R_null_val (up 6.6%) and OUT under N50 and MF1; **reported as an estimate, its p-value carries the A3 size caveat and is not used in the reading rule.**
4. `rrate` (record timing), 5. `contr` (beta2 SOTA minus beta2 all-model), 6. `thr` (threshold perturbation): the size-valid, robust diagnostics (A3 B1/B2). They are DIAGNOSTICS of selection/record structure, not acceleration tests; they have almost no power at rr=2.
Reference rows also printed (A3 definitions, same pb draw): `sota` (pb_sota), `mir`, `ipw` (negative control), `gap`. `ccl` and `tcl` are not run (not size-valid, A3). `loro` (D5) influence is printed descriptively.
Parametric-bootstrap null (as `fdesign4.pb_calibrated`): line fitted to ALL model horizons + N(0, residual sd), 19,999 datasets; p_up = (1+#{null >= obs})/(n+1).
Seeds: `SeedSequence([9100, k])`, k = 1 wild, 2 permutation, 3 pb, 4 audit draws, 5 model bootstrap. Everything runs once; a re-run with other seeds is a sensitivity, labelled so.

## R4. Estimates and uncertainty (reporting rules)
For beta2 (all-model, SOTA, heck, audit) report: the point estimate, the rr_eq reading, the HC3 95% interval (all-model only), and a **model-level bootstrap percentile 95% interval (B=2000, models resampled with replacement, date order restored)**. The bootstrap interval is DESCRIPTIVE: its coverage is not validated in this project (A2 evaluates mb tests' size, not interval coverage), the SOTA-based ones inherit the selection bias in their centre, and they are wide. Also report the parametric-bootstrap null mean of each statistic so the reader sees what no-acceleration looks like for it. Counts are always given (33 models, number of records, 19,999 / 9,999 / 2,000 draws, valid draws).

## R5. Reading rules (fixed before the run; a contradicting result goes to INTERESTING, no post-hoc rule)
1. **Power statement, quoted verbatim in the results:** at the real design the power to detect the meaningful acceleration (rr = 2) is low: size-adjusted upward power at rr=2 is 24.5% (audit), 19.4% (heck), 13.4% (rrate), 4.0% (thr), 2.9% (contr), 17.9% (pb_sota), with no method above 28% (A3 table; ccl/mir 28%, not used here); at rr=3 the best is 42% (audit); no method reaches 80% by rr=3. The all-model OLS/HC3 power at rr=2 is pending A2 (base grid `iid_all`: 30% size-adjusted, with its oversize). **A non-rejection is therefore NOT evidence that growth is not accelerating.**
2. "Evidence of acceleration" may be stated only if `hc3` p_up < 0.05 AND `audit` p_up < 0.05 (both Holm-unadjusted) AND the Holm-adjusted p_up of `hc3` < 0.10 across the family of six; and then still labelled exploratory, one series, 33 models, with the `hc3` size verdict from A2 stated (or "not yet analysed"). If only one of the two rejects, the statement is "mixed signal". If neither: "not detected at this sample size" together with R5.1.
3. `contr` and `thr` interpret the SOTA-vs-all-model discrepancy only: a small `contr` p means the record subset curves differently from all models (selection or acceleration), it does not by itself support acceleration.
4. The downward tail is reported with the same rules (a decelerating signal is not hidden).
5. The original T-hb one-shot (R0) is quoted next to the new rows with its known oversize, not as a separate confirmation.
6. Under-reporting guard: all six rows, the reference rows, the 200-draw audit stability and the bootstrap intervals are printed whether or not they agree.

## R6. Sensitivity (descriptive, one pass, both sets of rows printed)
S1 (v1.1 suite) is NOT implemented in the frozen runner and is therefore not part of this pre-registration; if run later it is a separately labelled addendum with its own commit, descriptive only (the simulator is not calibrated to the 228-task suite; the data are already seen). No other sensitivities are pre-registered.

## R7. Run, outputs, compute
`PREREG_SHA=<this commit> ../.venv/bin/python real_data/real_data_run.py real` on this Mac (about seconds of compute, 1 thread). Output `real_data/out/real_v10.json`, then `REAL_DATA_RESULTS.md`; the runner refuses to overwrite its output. [internal operations note redacted]: none of the statistics is new in this amendment; no filing question arises. INTERESTING rows (section 17) are added with the results.
