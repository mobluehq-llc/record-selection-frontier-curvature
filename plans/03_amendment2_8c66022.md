# F design stage: DESIGN AMENDMENT 2 (pre-registration; EXPLORATORY, synthetic data only, no confirmatory claim)

Written and committed BEFORE the run is launched (2026-11-23). Responds to `REVIEWS/external_referee_chatgpt_2026-11-23.md` (required changes 1-4 as far as they are
simulation work; change 5 is handled in the analysis outputs: counts, replicate totals, interval wording; publishing the code is this directory). Base results: `DESIGN_RESULTS.md`.
Frozen and untouched: `fcore.py`, `fdesign.py`, `fsim.py`, `fdesign_ext.py`, `grid.py`, `grid_fu1.py` (sha256 recorded in the run manifest). New code: `fdesign3.py`, `grid_a2.py`, `run_a2.py`, `analyze_a2.py`.

## 0. Audit finding that motivates the definitions below (see `AUDIT_adjustment.md`, `audit_adjustment.py`)
The mb_sota "adjusted power rises 4.8% -> 26% for early logistic" is NOT a computational error. Percentile-CI tests reject when the CI excludes 0, which is exactly |z|>1 for z=(lo+hi)/(hi-lo);
the base `analyze_design.py` adjustment replaced that by EQUAL-TAIL (2.5% / 2.5%) null quantiles of z. For mb_sota the null z is shifted upward (median +0.17): the raw 5.2% is 5.10% upward + 0.07%
downward, i.e. a nearly one-sided upward test, while the adjusted rule spends 2.5% on each tail (lower cutoff -0.64, not -1). The two are different two-sided tail rules, so the rejection sets are not nested.
Consequence for this amendment: **every rejection rate is reported per tail (upward, downward) and never as an unsplit two-sided number alone, and size-adjusted power is defined per tail.**

## 1. Estimand, outcome, selection rule, inference target (referee change 1)
- Unit: model m (M=33 real releases, real dates unless stated; K=170 tasks, 50 families; run counts as in the real METR design). Inference CONDITIONS on the observed release dates and task suite; model offsets are the random element.
- Fitted outcome y_m = log2 of the 50% time horizon from each model's own weighted ridge-logistic fit (`fcore.fit_logistic`), optionally clipped at the suite ceiling (censoring arm).
- Estimand for ALL-model tests: beta2 in y = b0 + b1 (t - mean t) + beta2 (t - mean t)^2 + error, over the 33 fixed dates (doublings/year^2). Null: exponential trend, beta2 = 0 for the TRUE trajectory.
  Acceleration = beta2 > 0 (signed, upward). Deceleration = beta2 < 0.
- Estimand for SOTA tests: beta2 of the same quadratic over the SOTA records (strict running maximum of y in (date, name) order). Under the exponential null this is NOT zero (selection bends it, see `mean beta2 SOTA` rows) -- reported, not hidden.
- Effective frontier sample size = nS (number of SOTA records per replicate): its mean and 5/95% quantiles are reported for every null cell. Truth-side facts are exact in the simulator (true_L).
- Calendar-time effects: for each alternative the instantaneous growth rate (doublings/year) at the start and end of the window and the corresponding doubling times in days are tabulated from the true trajectory. rr = end rate / start rate for the quadratic family, with the window-mean rate fixed at the null rate (doubling 210 d, 1.74 dbl/y). **Prespecified meaningful acceleration: end-of-window growth rate >= 2x the start rate (rr >= 2; start/end doubling time approx 315 d / 157 d). rr = 1.25 and 1.5 are reported as small effects, rr = 3, 4 as large.** Estimated curvature is also converted to the equivalent rr (rr_eq = (1+q)/(1-q), q = beta2 * span / rate) so a null bias reads as "equivalent to an acceleration of x".

## 2. Tests (all one row per replicate; p_up = evidence for acceleration, p_dn = deceleration)
Tail rules, fixed in advance, for every test: **upward 5% := p_up < 0.05; downward 5% := p_dn < 0.05; two-sided 5% := min(p_up, p_dn) < 0.025.** Invalid replicates (SOTA set < 4, or < 50% valid bootstrap draws) are counted and excluded from the denominator as in the base grid; n_valid and n_invalid are reported.
New (fixed-date, all-model regression of y on centred t and t^2, `fdesign3.Reg`):
- `ols`: classical t of beta2 (df = M-3). Identical to the base `iid_all` F test; exact size under independent Gaussian errors.
- `hc3`: HC3 sandwich t of beta2 against t(M-3).
- `wild`: null-restricted wild bootstrap, dates fixed: fit the linear-trend model, residuals e0 rescaled by 1/(1-h0_ii), Rademacher weights, B=499; statistic = HC3 t; p_up = (1+#{t*>=t})/(B+1), p_dn analogous.
- `perm`: residual permutation under the restricted linear-trend null (permute restricted residuals across dates, dates fixed), B=999, studentised by the OLS t. (Approximate exchangeability, per the referee; evaluated, not assumed.)
Existing (frozen definitions, now with signed p-values from the same bootstrap draws): `iid_sota`, `mb_all`, `mb_sota` (model-level bootstrap, B=2000, p_up=(1+#{c*<=0})/(n+1)), `pb_sota` (parametric bootstrap, B=1999); and in the X arm only (expensive) `hb_all`, `hb_sota` (B=400), `xb_all`, `xb_sota` (B=300).
HAC and a censoring-aware task-level model are NOT run (HAC needs an assumed serial model; the censoring-aware fit is a separate project) -- recorded as not done, not as failed.

## 3. Stepwise ladder from a clean Gaussian reference (referee change 2), all null (exponential truth), real dates, all tests
| rung | cell | what is added |
|---|---|---|
| L0 | LAD0_gauss | horizons y_m = true + N(0, sigma_m^2) drawn directly: independent Gaussian, uncensored. `ols` has exact size here |
| L1 | LAD1_estimation | + horizon estimation: task outcomes Binomial(n, logistic), each model refit; no task jitter (sj = 0), no ceiling |
| L2 | LAD2_censoring | + suite ceiling (clip at max task length, delta = 2 log2-min closer to the ceiling) |
| L3 | LAD3_taskdep | + task-difficulty jitter shared across models (sigma_j, family correlation phi as calibrated): cross-model dependence |
| L4 | LAD4_modfam | + model x task-family interaction (smf = 1) |
SOTA selection is the SOTA-subset tests (`iid_sota`, `mb_sota`, `pb_sota`, `hb/xb_sota` in X) evaluated at every rung, so the selection effect is read as (SOTA row - all-model row) at the same rung. Reported at each rung: mean estimated beta2 (all-model and SOTA) with SE and rr_eq, nS, and upward/downward/two-sided rejection per test.
The base-design R_null_val cell is the "all of the above except ceiling" reference rung.

## 4. Cells (`grid_a2.py`, append-only; seeds `SeedSequence([79, cell_index, rep])`)
Families (each: `_null_cal` and `_null_val` with DIFFERENT seeds, plus alternatives): R real design (cal/val 40000 each; alternatives 10000 each: rr 0.5, 1.25, 1.5, 2, 3, 4, logistic early (decelerating), logistic mid);
E even dates (20000; rr1.5, rr2, logi_dec); K0/K2/K4 ceiling at delta 0/2/4 (20000; rr2); MF1/MF2 model x family (20000; MF1 rr2); N50/N25 model-offset noise x0.5/x0.25 (20000; rr2); ladder rungs (20000 each); X real design with hb/xb (cal/val 2000, rr2 1500, logi_dec 800, rr0.5 600).
Total 670,000 cheap + 6,900 expensive replicates.

## 5. Analysis (prespecified; `analyze_a2.py`)
**Acceptable size.** For each null cell, test, and tail rule (upward 5%, downward 5%, two-sided 5%): verdict OK if the Clopper-Pearson 95% interval lies inside [3.5%, 6.5%]; OUT if it lies entirely outside; otherwise inconclusive. Bonferroni-adjusted CP intervals (family = null cells x tests x 3 rules) are printed beside every size so a claim "this test is OK" is not read off a single pointwise interval after scanning. Rejection counts k/n and replicate totals per cell are in `counts_a2.csv`.
**Primary comparisons (the only ones carrying a verdict):** (P1) upward-5% and two-sided-5% size on `R_null_val` for ols, hc3, wild, perm, mb_sota, mb_all, pb_sota; (P2) size-adjusted signed power at rr=2 (`R_rr2`) for the tests OK in P1 and for the same tests regardless; (P3) the first ladder rung at which the mean all-model beta2 is more than 2 SE from 0. Everything else (other families, other effects, hb/xb) is descriptive.
**Paired differences:** between methods that share replicates, reported as paired differences of upward-5% rates with a 95% paired interval (not a difference of two pointwise intervals) on R_null_val, R_rr2, X_null_val, X_rr2.
**Signed power.** Acceleration power = P(upward 5%); deceleration power = P(downward 5%); two-sided reported separately. Power against rr<1 and logistic-early is deceleration power; against rr>1 acceleration power; each is shown together with the opposite tail.
**Size-adjusted power.** Per test a signed statistic z (ols: OLS t; hc3: HC3 t; iid_sota: signed t; bootstrap tests: Phi^-1(1-p_up)); cutoffs are the 95% (upward), 5% (downward), or 97.5%/2.5% (two-sided) empirical quantiles of z in the family's `_null_cal` cell ONLY, then applied to the alternative. wild/perm share the cutoff statistic of hc3/ols so their adjusted power equals those rows.
**Validation on independent null draws:** the same cutoffs are applied to the independent `_null_val` cell and the achieved size is reported with CP intervals. **Cutoff uncertainty:** adjusted-power intervals come from a 400-draw double bootstrap (resample cal null AND alternative replicates, recompute cutoff and power); the interval therefore includes cutoff error.
**Mean estimated curvature** under every null is reported next to rejection rates (and as rr_eq).
**Reading rules fixed in advance.** (1) A statement that a test "has acceptable size" requires the OK verdict in the primary cell AND in the other null families it is claimed for; (2) a test is credited with power only at the size-adjusted figure whose validated achieved size is OK; (3) "no test is honest" style statements are not made unless every test is OUT in the primary cell; (4) a result that contradicts these rules goes to INTERESTING.md without a post-hoc new rule.

## 6. Run
[internal operations note redacted](2 workers; follow-up 1 keeps its 6)[internal operations note redacted](re-run the same command)[internal operations note redacted] Estimated 25.7 core-hours = about 13 h on 2 workers (budget cap 24 h).

Grid hash (grid_a2.py): 0a4273ada95fbc6c. [internal operations note redacted](cheap 0.04 s/rep, hb+xb 9.5 s/rep) and are used only for the ETA.
