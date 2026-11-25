# F real-data results (EXPLORATORY; one public series; no confirmatory claim)

Pre-registered in `PLAN.md` "Real-data amendment" (commit 17d741c, pushed before the run). Runner `real_data/real_data_run.py`, output `real_data/out/real_v10.json` (one-shot, ran once, about 10 s, this Mac, numpy 2.5.5, scipy 1.18.1). Data pinned by sha256 (`real_data/PINS.txt`; the runner asserted the runs-file hash).
Sample: METR time-horizon v1.0, **33 models**, released 2019-02-14 to 2025-11-24 (span 6.78 y), **17 SOTA records**. Real all-model linear trend: 1.76 doublings/y = doubling time 208 d (the simulator's null reference is 210 d).

## Read this first (pre-registered power statement, R5.1)
**Power to detect the meaningful acceleration (rr = 2: doubling time about 304 d falling to about 160 d across the window) is low at this design.** Size-adjusted upward power at rr=2 in the simulator: audit 24.5%, heck 19.4%, rrate 13.4%, pb_sota 17.9%, thr 4.0%, contr 2.9%; no method above 28%; at rr=3 the best is 42% (audit); none reaches 80%. All-model power [filled 2026-11-24 from RESULTS_A2.md; was "pending Amendment 2"]: size-adjusted upward power at rr=2 is hc3 = wild 34.0% [32.8, 35.1], ols = perm 40.2% (ols is oversized at nominal, so that figure needs a simulator-calibrated cutoff), mb_all 29.4%; hc3/wild 56.7% at rr=3 and 68.5% at rr=4; raw hc3 34.7%, wild 33.0%. Still below 80% for every valid test, so this statement stands. **A non-rejection would not show that growth is not accelerating; and a rejection obtained at low power overstates the effect size on average (winner's curse), so the point estimates below should be read as upper-leaning.**

## The pre-registered family of six (upward tail = acceleration)
| test | what it is | estimate (beta2, per yr^2) | rr_eq | p_up | Holm p_up (6) | p_dn | size verdict (simulator) |
|---|---|---|---|---|---|---|---|
| `hc3` | all 33 models, fixed dates, HC3 t(30) | +0.138 | 3.3 | 0.0058 | 0.029 | 0.994 | [filled 2026-11-24, A2] **OK on R_null_val** (up 5.11%, CP 4.89-5.33; two-sided 5.13%); OK also in K0, K2, MF1, MF2; **not robust: OUT in E (even dates, up 8.29%), K4 (ceiling 4: up 0.62%, two-sided 12.2%), N50 (9.3% / 10.5%) and N25 (14.7% / 18.9%)**. OLS t is OUT on R_null_val (6.75% / 8.12%) |
| `audit` | 25% random audit of non-records, 1/q weights; pb null | +0.192 (200 audit draws: median +0.128, IQR 0.095-0.177, range 0.019-0.252) | 6.7 (single draw) | 0.0064 | 0.029 | 0.994 | OK on R_null_val (up 6.0%, CP 5.8-6.3: A3 verdict OK), not robust (N50 up 9.1%) |
| `heck` | inverse-Mills corrected SOTA curvature; pb null | +0.054 | 1.5 | 0.209 | 0.63 | 0.79 | inconclusive (up 6.6%); not used in the reading rule |
| `rrate` | mean record date minus mean date of all models | -0.43 y (null mean -1.05 y) | n/a | 0.0042 | 0.025 | 0.996 | OK and robust (diagnostic) |
| `contr` | beta2(SOTA) minus beta2(all models) | -0.024 (null mean +0.062) | n/a | 0.941 | 1 | 0.059 | OK and robust (diagnostic) |
| `thr` | threshold perturbation | +0.004 (null mean +0.011) | n/a | 0.527 | 1 | 0.473 | OK and robust (diagnostic) |
Secondary tests of the same all-model regression: OLS t p_up = 0.0035; null-restricted wild bootstrap (B=9999) p_up = **0.022**; residual permutation (B=9999) p_up = 0.0027. The HC3 t(30) p (0.0058) is smaller than the wild-bootstrap p (0.022), a sign that the t reference is somewhat optimistic here. [A2, 2026-11-24: both are size-valid on R_null_val (hc3 5.11% up, wild 4.80% up); on R_rr2 wild rejects 1.67 pp less often than hc3. OLS t (6.75% up) is OUT and permutation (6.72% up, 7.86% two-sided) is inconclusive / OUT, so the OLS and permutation p-values above are from oversized references.]
Reference rows (same pb draw, B=19,999): `sota` (pb_sota) beta2 = +0.114, p_up = 0.240 (null mean of the statistic +0.062, i.e. most of it is the selection bias); `mir` +0.177, p_up = 0.015 (not size-valid in A3; descriptive); `ipw` +0.120, p_up = 0.195 (negative control); `gap` p_up = 0.108. Original one-shot T-hb on the SOTA records (earlier, oversized family): +0.114, 95% CI [-0.044, +0.244], not rejected.
Leave-one-record-out: max shift of the SOTA curvature 0.030, jackknife SD 0.039.

## Reading rule outcome (R5.2)
`hc3` p_up < 0.05, `audit` p_up < 0.05, and the Holm-adjusted `hc3` p_up = 0.029 < 0.10: the pre-registered condition for the wording "**evidence of acceleration**" is met. Labelled as required: **exploratory, one series, 33 models** [A2, 2026-11-24: HC3 size verdict now available, OK on R_null_val, not robust to the even-date, ceiling-4 and N50/N25 cells; see also the 2026-11-24 update at the end: the result does not survive developer clustering], and the wild-bootstrap p is 0.022 rather than 0.006. The SOTA-record tests (`sota`, `heck`, `ipw`) do NOT reject, and `contr` is slightly negative (the record subset curves no more than all models): the signal sits in the all-model trajectory and in record timing (records come later than a linear trend predicts), not in the record heights alone. The downward tail is clean (p_dn >= 0.059 everywhere).

## Estimates in calendar terms, with uncertainty (R4)
| quantity | estimate | HC3 95% | model-bootstrap 95% (descriptive, coverage unvalidated) |
|---|---|---|---|
| beta2, all models | +0.138 /yr^2 | [+0.033, +0.244] | [+0.045, +0.629] |
| beta2, SOTA records | +0.114 | n/a | [+0.002, +0.440] |
| beta2, heck | +0.054 | n/a | [-0.044, +0.455] |
| beta2, audit (single draw) | +0.192 | n/a | [-0.019, +0.644] |
| all-model quadratic fit, growth at window start | 0.71 doublings/y (doubling 515 d) | | rr_hat bootstrap [1.3, 17.5]; 50 of 2000 resamples have a non-positive start rate (rr undefined) |
| growth at window end | 2.59 doublings/y (doubling 141 d) | | |
| rr_hat = end/start, all-model | 3.6 (rr_eq 3.3) | | median 3.2 |
Reading: the data are compatible with anything from a modest speed-up (rr about 1.4, bootstrap lower end of rr_eq for the all-model curvature) to a very large one; the upper ends are not bounded (rr_eq undefined when q >= 1). The start-of-window rate (0.71/y) rests on the earliest few models (GPT-2, GPT-3, 2019-2022) and is the least reliable end of the quadratic and the estimated rr is driven by that early flat segment.

## What this does and does not say
- It does: report that on METR v1.0 the all-model curvature and record timing point to acceleration at the pre-registered one-sided 5% level, with Holm-adjusted p = 0.029, and that the SOTA-only tests (the usual way trend claims are made) do not detect it.
- It does not: establish acceleration ([A2, 2026-11-24] HC3's size is OK in the matched simulator cell but not in the even-date, ceiling-4, N50 or N25 cells, wild p is 0.022, the series is one benchmark with 33 correlated models, the bootstrap intervals are descriptive, and low power inflates significant estimates). Not a basis for a published claim; the confirmatory step would be the next METR release (v1.1 holdout is already seen), with the same code.
- Other public series (idea U) were not analysed (see PLAN R1).


## CORRECTION 2026-11-23 (calendar figures only; see /ERRATA.md)
The doubling times quoted above for the quadratic alternatives (rr=2: 304 -> 160 d; rr=1.25: 234 -> 190; rr=1.5: 258 -> 177; rr=3: 391 -> 144; rr=4: 473 -> 135; logistic early 239 -> 800) are half-year secant rates produced by `design/analyze_a3.py effect()` (h = 0.5 y), not end-point rates. The exact end-point values are rr=2: 315 -> 157.5 d; 1.25: 236 -> 189; 1.5: 262 -> 175; 3: 420 -> 140; 4: 525 -> 131; logistic early 271 -> 952. The alternatives themselves, the rr labels, and every size, power and p-value are unchanged (checked by running the simulator: end/start slope ratio of the true trajectory at the real window end points = 2.000, 3.000, 4.000). No test, bar or reading rule is altered by this note; the text above is left as written.


## UPDATE 2026-11-24: Amendment 2 tags filled; the acceleration evidence is FRAGILE (paper v3)
- Every "pending A2" tag above is filled from `RESULTS_A2.md` (ef62b83); the bracketed, dated insertions mark what changed. No registered statistic, p-value or reading-rule outcome was altered.
- **A2 ladder (P3):** first rung with mean all-model beta2 more than 2 SE from 0 is LAD1_estimation (+0.0025, SE 0.0004); rung 0 (Gaussian) is unbiased (-0.0004). The record-only (SOTA) bias is already present at rung 0 (rr_eq 1.66) and stays 1.58-1.73 over the rungs.
- **Developer clustering (CL1, `RESULTS_CLUSTER.md`, d9cfde6):** all 33 models, CR2 p_up 0.112, Webb wild-cluster p_up 0.094 (Rademacher exact 0.086), against unclustered HC3 0.0058. Without GPT-2 and GPT-3: HC3 0.310, CR2 0.168, Webb 0.060. The registered CL1 bar ("p < 0.05 survives clustering") is NOT met.
- **Revised reading.** The prespecified R5.2 rule was met and that fact is unchanged. The wording it permits ("evidence of acceleration") is NOT adopted in paper v3: the evidence does not survive developer clustering or dropping GPT-2/GPT-3, and is described as **fragile**. Neither check has a size study or much power, so this is not evidence of steady growth either. The selection-bias result stays the headline.
- Not computed: the false-alarm rate and exaggeration factor of the joint rule (needs A2 and A3 replicates paired; bar B5); a clustered version of the record-timing diagnostic.
