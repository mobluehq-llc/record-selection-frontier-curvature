# F design stage: DESIGN AMENDMENT 3 (pre-registration; EXPLORATORY, synthetic data only, no confirmatory claim)

Written and committed BEFORE the run is launched (2026-11-23). Source of the candidate methods: a larger internal brainstorm of 240 candidates, all read and classified by hand
(18 testable in the existing simulator, 117 need new data/code, 33 duplicate or covered, 72 vague). [internal operations note redacted] the simulator decides.
Frozen and untouched: `fcore.py`, `fdesign.py`, `fsim.py`, `fdesign3.py`, `grid_a2.py`, `AMENDMENT2.md` and its definitions (tail rules, size bound, size-adjusted power, reading rules). New code: `fdesign4.py`, `grid_a3.py`, `run_a3.py`, `analyze_a3.py`, `check_a3.sh`.
**Disclosure of pre-run looks:** while debugging I ran 150 replicates of `R_null_val` (seeds as below) through the A3 code to fix a sign error in the tcl gradient (checked against finite differences) and to time it. I saw null rejection rates and mean curvature from those 150 replicates
(e.g. the mirror estimator removes only part of the SOTA bias there; the inverse-Mills estimator has mean curvature near 0; the two record likelihoods looked oversized at nominal). No design choice was made from them except keeping every method in the list; the 150 replicates are re-run inside the full cell, not selected out.

## 1. The ten (+1) methods (all computed on the SAME simulated datasets as Amendment 2)
Data: every A3 cell reuses an A2 cell (`grid_a3.py` copies its simulator config), regenerated with the A2 seeds `SeedSequence([79, a2_cell_index, rep])` so A3 rows pair exactly with A2 rows by (cell, rep). The A3 tests draw new randomness from `SeedSequence([83, a3_cell_index, rep])`.
Work is in date order (date, name); a **record** (SOTA model) = strict improvement over the running maximum of all earlier models. beta2 = quadratic coefficient (doublings/year^2). Tail rules, OK/OUT/inconclusive verdicts and the [3.5%, 6.5%] bound are exactly Amendment 2's.
All parametric-bootstrap (pb) tests: fit a line to ALL model horizons, simulate B=1999 datasets line + N(0, resid sd) (clipped at the suite ceiling in ceiling cells), recompute the statistic; p_up = (1+#{null >= obs})/(n+1), p_dn analogous; invalid if < 50% of draws valid or fewer than 4 effective points.
| id | name | source candidate | statistic | reference distribution |
|---|---|---|---|---|
| C1 | `ccl` censored-crossing likelihood, all 33 models | #10 (dups 59,98,140,178,186,187) | signed sqrt of the LRT of the quadratic term; records contribute a Gaussian density, each non-record contributes P(y < running max); (a, b, c, sigma) free | N(0,1) |
| C2 | `tcl` record-truncated likelihood, records only | #55 | same LRT, each record's density truncated to exceed the previous record (conditioning on the record-setting event); non-records dropped | N(0,1) |
| C3 | `mir` mirror-envelope curvature | #77 (time-reversal; derivation is mine) | mean of beta2 over forward upper records and beta2 over backward lower records (models strictly below every later model); first-order bias cancels under date symmetry | pb |
| C4 | `heck` inverse-Mills (sample-selection) corrected SOTA curvature | #188 | each non-first record y_i replaced by y_i - s*lambda((M_prev - mu_i)/s), mu, s from the line fit to all models in the same dataset; then the record quadratic | pb |
| C5 | `audit` random audit of 25% of non-records with 1/q weights | #216 (dups 86,99,107,219) | weighted quadratic over records (weight 1) and audited non-records (weight 4); the audit draw is fresh randomness | pb (audit redrawn in each bootstrap dataset) |
| C6 | `ipw` naive inverse-probability weighting of records | #97 (dups 166,227) | records weighted 1/pi_i, pi_i = plug-in P(record | line, s), clipped at 0.05. **Negative control: expected NOT to correct** (selection is on the outcome) | pb |
| D1 | `rrate` record timing | #74 | mean record date minus mean date of all models (years); needs >= 4 records | pb |
| D2 | `gap` record-spacing trend | #170 | mean record gap (log2 min) in the later half of the records minus the earlier half; needs >= 5 records | pb |
| D3 | `contr` challenger contrast | #29 | beta2(SOTA) minus beta2(all models) | pb |
| D4 | `thr` threshold perturbation | #240 | beta2 over records that beat the previous record by >= 0.5 sd minus beta2 over all records | pb |
| D5 | `loro` leave-one-record-out influence | #13 | max shift of beta2(SOTA) when one record is removed, and jackknife SD (observed only; >= 5 records); DESCRIPTIVE, no test | none |
Reference: `sota` = beta2(SOTA) with the same pb null (the A2 `pb_sota` test on fresh randomness) and `all` = beta2(all models). All stored per replicate: statistic, p_up, p_dn, z = Phi^-1(1-p_up), valid draws.
C1-C2 use scipy L-BFGS-B with analytic gradients (checked against finite differences, error < 1e-3); a fit that does not converge is invalid and counted.

## 2. Cells (`grid_a3.py`; reps = the A2 count; [internal operations note redacted]
`R_null_cal` 40000, `R_null_val` 40000, alternatives `R_rr0.5, R_rr1.25, R_rr1.5, R_rr2, R_rr3, R_rr4, R_logi_dec, R_logi_mid` 10000 each (real design); other null families for the robustness requirement (validation cells only, cutoffs taken from `R_null_cal`):
`E_null_val` 20000 (even dates), `K2_null_val` 20000 (ceiling delta 2), `N50_null_val` 20000 (model-offset noise x0.5), `MF1_null_val` 20000 (model x family interaction); alternatives rr2 at E, K2, N50 (10000 each).

## 3. Bars (fixed in advance; all verdicts per method on the stated cells)
- **B1 size, primary (R_null_val, n=40000, nominal reference):** for the upward-5% rule and for the two-sided-5% rule, the Clopper-Pearson 95% interval of the rejection rate must lie inside [3.5, 6.5] % (verdict OK, Amendment 2's bound). The downward-5% rate is reported beside it. A method is **size-valid** only if upward AND two-sided are OK.
- **B2 size, robustness:** size-valid in R_null_val AND OK (upward 5% and two-sided 5%) in each of E, K2, N50, MF1 null_val -> **robust**. A method that is OK only after replacing the nominal reference by the cutoff from `R_null_cal` (size-adjusted) is **adjusted-valid**: the cutoffs are validated on `R_null_val`/other null families and reported; it is not size-valid.
- **B3 power in calendar terms:** upward-5% power at rr = 1.5, 2, 3 (and 1.25, 4 for the table), each shown with its start/end growth rate and doubling time (null: 210 d, mean rate 1.74 dbl/y; rr=2 is 315 d -> 157 d, the prespecified meaningful effect), with Clopper-Pearson intervals. Power is credited ONLY at a size-valid or adjusted-valid figure (Amendment 2 reading rule 2). Also the smallest tabulated rr with adjusted power >= 80% ("not reached by rr=4" otherwise). Deceleration power (downward 5%) at rr0.5 and logistic-early is reported separately; the logistic-mid alternative is reported as is.
  Size-adjusted power uses the A2 definition (cutoffs on z from the family's `_null_cal` cell, per tail, double-bootstrap intervals with 400 draws).
- **B4 bias of the corrections C3-C6 and `sota`:** mean beta2 on R_null_val with its SE and the rr_eq reading (as in A2); a correction is **bias-removing** if |rr_eq - 1| <= 0.10 (practical) and reported separately whether the mean is within 2 SE of 0.
- **B5 paired comparison with Amendment 2** (when A2 results are complete): paired differences (same data) of upward-5% rejection between each new method and `mb_sota`, `hc3`, `ols`, `pb_sota` on `R_null_val` and `R_rr2`, with a paired 95% interval.
- **B6 diagnostics (D1-D5):** D1-D4 get the same size and power tables, labeled DIAGNOSTIC. D5 is descriptive: median max-shift and median jackknife SD among replicates where `sota` rejects upward, under the null cell versus `R_rr2`; a diagnostic is "useful" only if it separates those two sets (AUC with a CP-style bootstrap interval, reported, no threshold chosen).
- All tables show counts k/n, invalid replicates, and the number of replicates. Everything is labeled EXPLORATORY. A result that contradicts these bars goes to INTERESTING.md without a post-hoc new rule (Amendment 2 reading rule 4). "No method works" is not stated unless every method is OUT in R_null_val.

## 4. Run
[internal operations note redacted](8 workers; [internal operations note redacted], resumable (re-run the same command), manifest at `results/manifest.json`,
[internal operations note redacted](writes `summary_a3.md`, `counts_a3.csv`). Estimated 3.8 core-h = about 30 min wall on 8 cores.

## 5. [internal operations note redacted]
Any correction that passes B1/B2 and removes the bias (B4) [internal operations note redacted] results stay internal. Candidate flag set in advance: C3 (mirror envelope) is my own construction and C4/C5 are standard sample-selection/audit-sampling devices applied to a new setting (likely prior art for C1/C2/C4 in Tobit/Heckman/record-value literature; unscreened).
