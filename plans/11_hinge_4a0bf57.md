# PREREG H1: hinge (o1-preview date) vs smooth quadratic, identifiability at the real METR v1.0 dates
Registered 2026-11-24, committed BEFORE any computation of this study. internal brainstorm pick 1 (ddf148d). EXPLORATORY with respect to the paper's headline (no change to CLAIMS.md); the bars below are CONFIRMATORY for this study (fixed before the run).
[internal operations note redacted] stored data only (METR v1.0 runs, sha256 f489d117..., cutoff 2025-11-30, 33 models; dates as in release_dates.yaml). Code: `code/hinge_study.py` (written after this commit; imports frozen `design/fcore.py`, `design/fdesign.py`).

## Hypothesis
At the real 33 release dates, with the simulator's task-level noise, a hinge fixed at the o1-preview release (T = 2024-09-12; level jump d and slope change g) and a smooth quadratic can be told apart: the correct model is selected at least 70 percent of the time under each truth.
## Models (OLS on the all-model log2 horizons, unweighted, t = years since 2019-01-01)
L: a+bt. Q: a+bt+ct^2. H: a+bt+d*1[t>=T]+g*(t-T)+.
## Truths (curves fitted by OLS to the real series, used as the true log2 horizon L(t))
T_L (line fit), T_Q (quadratic fit), T_H (hinge fit). Positive controls: PC_H = continuous kink at T, pre-slope = real line slope, post-slope = 4x, d = 0, anchored at the line-fit value at T; PC_Q = fdesign 'quad' truth rr = 4, same total gain as the null.
## Noise: `fdesign.Sim.draw` (task-level logistic outcomes, per-model slopes b from the real fit, sigma_m, sigma_j, phi from results/F_simulator_validation.json), horizons refit by `fc.horizons_of`. R = 10000 draws per truth, seeds SeedSequence([9300, k]).
## Selection rules
Primary: AICc (Gaussian RSS; k = 2, 3, 4). Secondary: BIC; leave-one-calendar-month-out CV mean squared prediction error (all models released in a month held out together, refit on the rest). Report the 3-way selection table per truth, the pairwise H-vs-Q table, and the mean held-out error per model per truth.
## Bars (AICc)
- Instrument valid only if: PC_H selects H >= 90 percent AND PC_Q selects Q >= 90 percent. Otherwise no identifiability verdict (instrument broken).
- Exact cross-check: with noise = 0 (true L observed exactly) T_L, T_Q, T_H must select L, Q, H respectively and refits recover the generating coefficients to 1e-9.
- Identifiable: P(select H | T_H) >= 70 AND P(select Q | T_Q) >= 70. Both < 70: "not identifiable at this design". One only: "asymmetric", reported as such.
- Falsifier of the hypothesis: either rate < 70 percent.
Also reported (no bar): P(select H | T_Q), P(select Q | T_H), P(select L | T_L).
## Real series
Fit L, Q, H, and Q+H (a+bt+ct^2+d*1+g(t-T)+); AICc, BIC, LOMO-CV. Developer clusters as in `real_data/cluster_test.py` (DEV map, 7 clusters). Inference: cluster-robust t with CR2 (A_g = (I-H_gg)^-1/2; a cluster whose I-H_gg has an eigenvalue < 1e-8 uses A_g = I for that cluster, flagged), null-restricted Webb 6-point wild cluster bootstrap, B = 99999, seed SeedSequence([9300, 100]). Tests: (i) Q alone c (must reproduce c = 0.13847 and Webb one-sided p 0.094 as an instrument check, else stop), (ii) H: g and d, plus joint (d, g) = 0 via Wald with CR2 covariance bootstrapped under the line null, (iii) Q+H: c = 0 (restricted model H), and (d, g) = 0 (restricted model Q). Report c in Q+H, its ratio to c in Q alone, and two-sided Webb p. Descriptive only; coverage of these tests with 7 clusters (15/9/4/2/1/1/1) is not validated.
## Not done here
Hinge date other than 2024-09-12 (a 2024-12 robustness cell is NOT run), record-only series, bootstrap-LR classifier of the brainstorm (replaced by AICc/BIC/CV above), proxies-dropped and leave-OpenAI-out variants.
