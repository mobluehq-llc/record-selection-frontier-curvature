# Design Amendment 2 results (idea F): EXPLORATORY, synthetic data only

[internal operations note redacted]
[internal operations note redacted]
[internal operations note redacted]

## P1: size on R_null_val (CP95 inside [3.5, 6.5] = OK)
| test | upward 5% | two-sided 5% |
|---|---|---|
| ols | 6.75 OUT | 8.12 OUT |
| hc3 | 5.11 OK | 5.13 OK |
| wild | 4.80 OK | 4.62 OK |
| perm | 6.72 inconclusive | 7.86 OUT |
| mb_all | 4.49 OK | 3.90 OK |
| mb_sota | 13.68 OUT | 5.85 OK |
| pb_sota | 5.89 OK | 6.58 inconclusive |
(iid_sota 34.6 / 27.5 OUT.) **HC3 size is now answered for the base design: OK.** Reading rule 1 (OK in other families too): hc3 is OK in K0, K2, MF1, MF2 (up) but OUT in E (8.29 up, 8.48 two-sided), K4, N50 (9.3 / 10.5) and N25 (14.7 / 18.9); wild is OK in R, K0, K2, MF1, MF2 and OUT in E, K4, N50, N25. So HC3/wild are "acceptable" for the real design and moderate perturbations, not robustly. Rule 3: not every test is OUT, so "no test is honest" is not claimed.

## P2: size-adjusted upward power at rr=2 (R_rr2; adjusted cutoffs validate OK, achieved size 4.7-5.1%)
ols 40.2 | hc3 = wild 34.0 [32.8,35.1] | perm 40.2 | mb_all 29.4 | mb_sota 16.1 | pb_sota 17.8 | iid_sota 21.1. Raw hc3 34.7, wild 33.0. Power at rr=3: hc3/wild 56.7; at rr=4: 68.5. Power is below 80% for every valid test at rr=2 (and the best valid, hc3, is about 34%): **a non-rejection at rr=2 remains uninformative; the Read-this-first warning in REAL_DATA_RESULTS.md stands.** Paired (R_rr2): wild - hc3 -1.67 pp [-2.37,-0.97].

## P3: ladder
First rung with mean all-model beta2 more than 2 SE from 0: **LAD1_estimation** (+0.0025, SE 0.0004). Rung 0 (Gaussian) is unbiased (-0.0004, SE 0.0004). Size at ladder rungs: hc3 3.4-4.1% (inconclusive or OK, mildly conservative); ols 4.8-5.7% OK; pb_sota OK throughout; mb_sota 11-12% OUT at every rung (SOTA selection alone breaks it).

## Consequence for the real-data reading
Real-data `hc3` p_up 0.0058 and `wild` 0.022 both come from tests that have OK size in the matched simulator cell (5.1% / 4.8%), so the "pending A2" tag on those rows can be replaced by "OK on R_null_val; not robust to even-date, ceiling-4, 0.5x/0.25x noise cells". Clustering (CL1) is a separate, unaddressed threat. Exploratory throughout; no confirmatory claim.

Not done: REAL_DATA_RESULTS.md table tags not yet edited; INTERESTING rows for the non-robust cells not yet added.
