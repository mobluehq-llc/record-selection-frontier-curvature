# F design-stage size/power map: results (EXPLORATORY, synthetic data only, no confirmatory claim)

[internal operations note redacted]
`summary_base/summary.md` and `summary.json` (produced by `analyze_design.py`; code in this directory is byte-identical to the code that ran, sha256 checked).
Real design: M=33 models, K=170 tasks, 50 families. All rates below are two-sided 5%-level rejection rates with Clopper-Pearson 95% intervals.
"adj" = size-adjusted power (critical value from the matching null cell), the only fair power comparison for oversized tests.

## Q1. Does ANY test reach nominal 5% size at the real design? (cell A_null_exp, n=3000)
| test | size % [CP95] | verdict |
|---|---|---|
| mb_sota (model-level bootstrap, SOTA models) | 5.2 [4.4, 6.0] | **only test whose interval contains 5%** |
| mb_all | 4.1 [3.4, 4.8] | slightly conservative |
| pb_sota (parametric bootstrap) | 6.5 [5.6, 7.4] | mildly oversized |
| iid_all | 8.2 [7.2, 9.2] | oversized |
| hb_all / iid_sota / hb_sota | 22.9 / 26.3 / 37.7 | grossly oversized (task-level resampling ignores model-level noise) |
| xb_all / xb_sota (crossed bootstrap) | 1.4 / 1.7 | very conservative |

**Answer (this simulator, two-sided 5%): among nine procedures only `mb_sota` has a CP interval containing 5% at the base cell, and its size moves with the design (see below); `mb_all` (4.1) is conservative, `pb_sota`/`iid_all` mildly oversized, the task-level resampling tests grossly oversized, the crossed bootstrap very conservative. This is a statement about these procedures under this simulator, not about trend tests in general.** It holds in B_null_mf1/mf2 (5.3 / 5.2) and C_null_clip2 (4.6), but not in C_null_clip0 (6.4 [5.4,7.5]),
C_null_noclip4 (6.3), D_null_even (9.2 [8.2,10.3], evenly spaced dates), C_null_clip4 (2.7), nor when model-level noise shrinks (A_null_n0.5: 7.8; n0.25: 12.3). Even `mb_sota`'s 5.2 has
a CP interval (4.4-6.0, about 1.6 pp wide at 3,000 replicates; about 2.6 pp wide at 1,200) that does not separate it from 4.5 or 6, and containing 5% does not establish calibration; this is why follow-up 1 spends 200k reps/null cell on it (Arm P). The 5.2% is 5.10% upward + 0.07% downward (`AUDIT_adjustment.md`): in effect a one-sided test for acceleration.

## Q2. Power against each alternative (A cells, 1200 reps each; raw % / size-adjusted %)
| alternative | mb_sota (the valid test) | mb_all | iid_all | hb_all | xb_all | pb_sota |
|---|---|---|---|---|---|---|
| super-exp rr=1.5 | 12.4 / 9 | 8.0 / 10 | 16.2 / 13 | 36.6 / 12 | 3.3 / 9 | 8.9 / 7 |
| super-exp rr=2 | 19.2 / 13 | 15.8 / 18 | 34.8 / 30 | 55.5 / 25 | 7.2 / 16 | 9.2 / 8 |
| super-exp rr=3 | 26.6 / 20 | 27.2 / 32 | 63.1 / 56 | 74.2 / 47 | 15.1 / 26 | 18.8 / 16 |
| super-exp rr=4 | 30.8 / 24 | 33.8 / 37 | 76.8 / 72 | 82.0 / 60 | 21.8 / 32 | 23.6 / 21 |
| logistic, early inflection (A_logi_dec) | 4.8 / 26 | 66.4 / 69 | 88.0 / 82 | 97.5 / 90 | 59.8 / 70 | 25.3 / 19 |
| logistic, mid inflection (A_logi_mid) | 7.1 / 5 | 0.9 / 1 | 36.6 / 31 | 62.1 / 35 | 0.8 / 2 | 48.2 / 45 |

**Answer (acceleration, this simulator): no procedure here combines near-5% size with useful power against rr<=3.** The one near-nominal test has 19% raw power at rr=2 (the 13% adjusted figure is at 2.5% per tail, see `AUDIT_adjustment.md`; signed one-sided adjusted power is re-estimated in Amendment 2) and 31% at rr=4; no test reaches 80% against rr<=3 once
size-adjusted (best: iid_all 56%, hb_all 47% at rr=3, and these need a simulation-calibrated cutoff because they are oversized). The decelerating logistic is detected well by the two-sided
all-model tests (mb_all 66%, xb_all 60%), but that is the opposite sign of curvature to a super-exponential speed-up, and the SOTA-model tests are blind to it (mb_sota 4.8%).
The power is limited by the selection/offset noise sigma_m: with noise x0.25 and rr=2, mb_sota reaches 53% (adj 39%), iid_all 91% (adj 71%).

## Other findings from the base grid (hypotheses, not claims)
- **Noise makes some tests better and some worse.** Lowering model-offset noise makes the cheap tests worse (mb_sota 5.2 -> 7.8 -> 12.3; iid_all 8.2 -> 17.9 -> 33.4; pb_sota 6.5 -> 12.6 -> 24.5) while hb/xb improve (hb_sota 37.7 -> 17.9 -> 6.6; hb_all 22.9 -> 8.0 -> 3.4). This is the same "bias exposed as variance shrinks" pattern as INTERESTING.md row 3, in the noise dimension. Follow-up 1 tests the model-count dimension directly.
- Model x family interaction (B nulls) helps hb_sota (31 -> 19%) and makes xb more conservative, as expected, but leaves mb_sota unchanged (5.3 / 5.2).
- A ceiling that censors the top of the trajectory (C_null_clip4, 20% of cells at the ceiling) breaks every all-model test (mb_all 14.3, hb_all 47.7), while xb_sota/mb_sota go conservative (0.4 / 2.7).
- Even date spacing (D) makes mb_all (12.5), mb_sota (9.2) and iid_all (10.4) oversized; the size depends on the actual clustered release dates of the real design.

## Limits
Synthetic data from one calibrated simulator (`F_simulator_validation.json`); replicates per cell 1200-3000 (CP95 intervals about 1.6 pp wide at 3,000 and 2.6 pp wide at 1,200 near 5%; they quantify Monte Carlo error, not calibration); alternatives are only two families (quadratic rate, logistic);
no real-data statistic is evaluated here. Size-adjusted power uses the same-family null cell, equal 2.5% tails (not the raw rule's own tail split, which for percentile-CI tests is asymmetric: audit), no independent validation of the cutoff and no cutoff uncertainty; Amendment 2 fixes all three. Not a confirmatory result.

## Follow-up 1 (launched 2026-11-23, see FOLLOWUP1_SPEC.md; results not yet in)
[internal operations note redacted]

## Referee response and Design Amendment 2 (2026-11-23)
[internal operations note redacted]

## Amendment 3 results (2026-11-24; EXPLORATORY, synthetic; `results_a3/summary_a3.md`, pre-registered in `AMENDMENT3.md`, commit 03dfe34)
[internal operations note redacted]
- **B1 size-valid on R_null_val (nominal reference):** ipw, audit, rrate, gap, contr, thr. **Robust (also E, K2, N50, MF1):** rrate, contr, thr only. NOT size-valid: ccl (up 11.8%), tcl (20.7%), mir (6.2 up / 7.0 two-sided), heck (6.6, inconclusive), sota/pb_sota (two-sided inconclusive; N50 OUT). Every method except the three diagnostics is oversized when model-offset noise is halved (N50).
- **Bias (B4), mean beta2 under the null:** SOTA 0.0706 (rr_eq 1.76); mirror 0.050 (1.49, only partial cancellation); inverse-Mills `heck` 0.0092 (1.07, bias-removing); random audit of 25% of non-records 0.0023 (1.02, bias-removing); naive IPW 0.062 (1.63, fails as predicted). All-model beta2 0.0021.
- **Power (rr=2, start/end doubling 304/160 d), size-adjusted, validated size OK:** ccl 27.9%, mir 27.6%, audit 24.5%, heck 19.4%, ipw 15.0%, tcl 13.4%, rrate 13.4%, gap 13.0%, pb_sota 17.9%, thr 4.0%, contr 2.9%. At rr=3: ccl 49%, mir 48%, audit 42%. No method reaches 80% adjusted power by rr=3.
- Diagnostics: contr and thr are exactly sized and robust but have almost no power (they remove the acceleration signal along with the selection bias); D5 influence ratio does not separate null rejections from rr=2 rejections (AUC 0.505 [0.49,0.52]).
- Reading: the only corrections that remove the selection bias are those that bring non-record information back (inverse-Mills with a plug-in line from all models, and a random audit of non-records); neither is size-valid across families, and their adjusted power at rr=2 (19-25%) does not beat a plain all-model fit. Nothing here changes the Amendment 2 conclusion; no confirmatory claim.


## CORRECTION 2026-11-23 (calendar figures only; see /ERRATA.md)
The doubling times quoted above for the quadratic alternatives (rr=2: 304 -> 160 d; rr=1.25: 234 -> 190; rr=1.5: 258 -> 177; rr=3: 391 -> 144; rr=4: 473 -> 135; logistic early 239 -> 800) are half-year secant rates produced by `design/analyze_a3.py effect()` (h = 0.5 y), not end-point rates. The exact end-point values are rr=2: 315 -> 157.5 d; 1.25: 236 -> 189; 1.5: 262 -> 175; 3: 420 -> 140; 4: 525 -> 131; logistic early 271 -> 952. The alternatives themselves, the rr labels, and every size, power and p-value are unchanged (checked by running the simulator: end/start slope ratio of the true trajectory at the real window end points = 2.000, 3.000, 4.000). No test, bar or reading rule is altered by this note; the text above is left as written.
