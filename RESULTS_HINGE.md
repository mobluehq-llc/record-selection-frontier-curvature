# RESULTS_HINGE: hinge (o1-preview, 2024-09-12) vs smooth quadratic at the real METR v1.0 dates
Pre-registration: `design/PREREG_HINGE.md` (commit 4a0bf57, before any computation). Code `code/hinge_study.py`; numbers `results/F_hinge.json`, `results/hinge.log`. EXPLORATORY w.r.t. the paper headline; no paper text or CLAIMS change. R = 10,000 draws per truth (MC SE <= 0.5 pp). 33 models, 22 at or after the break.

## Registered verdict
**No identifiability verdict (instrument bar missed).** The registered validity bar needed both positive controls >= 90 percent under AICc. PC_H (4x kink) passed at 98.0 percent. PC_Q (quadratic, rr = 4) selected Q only 77.2 percent, so the bar failed and, by the registered rule, the 70 percent identifiability rule is not to be read as a verdict. Exact noiseless cross-check passed (L, Q, H each selected correctly; coefficients to 1e-14).
Descriptive rates (not a verdict): correct selection under T_H 41.9 percent, under T_Q 69.3 percent (both under the 70 percent line); the PC_Q shortfall means even a strong smooth curve is mislabelled about 1 in 4 times at this design.

## Selection rates by truth (AICc; rows = truth, columns = selected)
| truth | L | Q | H | pairwise H vs Q (H / Q) |
|---|---|---|---|---|
| T_L line | 76.1 | 15.5 | 8.3 | 16.3 / 83.7 |
| T_Q fitted quad | 17.6 | **69.3** | 13.1 | 14.7 / 85.4 |
| T_H fitted hinge | 14.4 | 43.7 | **41.9** | 45.0 / 55.0 |
| PC_H kink x4 | 0.4 | 1.7 | **98.0** | 98.0 / 2.0 |
| PC_Q quad rr 4 | 10.6 | **77.2** | 12.2 | 13.0 / 87.0 |
Under T_H the quadratic is chosen slightly more often than the hinge (43.7 vs 41.9). BIC (correct): T_Q 65.6, T_H 30.4, PC_H 97.4, PC_Q 75.0. Leave-one-month-out CV (correct): T_Q 64.2, T_H 48.9, PC_H 97.1, PC_Q 71.3. Mean held-out MSE under T_H: L 1.34, Q 1.19, H 1.10 (hinge best on average, quadratic second); under T_Q: L 1.33, Q 1.09, H 1.19. So H and Q are mutually confusable, mostly in the direction H truth -> Q label.

## Real series (all 33 models)
| model | AICc | BIC | LOMO-CV MSE |
|---|---|---|---|
| line | -3.67 | -1.07 | 0.933 |
| quad | -9.38 | -5.72 | 0.683 |
| hinge | -9.51 | -4.95 | 0.649 |
AICc difference hinge - quad = 0.13 (a tie); BIC prefers quad by 0.8; CV prefers hinge by 0.03 MSE. The simulation shows these three signals are what either truth produces about equally often, so the real data cannot choose.
Hinge coefficients: level jump d = +0.375 (Webb p two-sided 0.227), slope change g = +1.23 doublings/yr (p 0.089 two-sided, 0.045 one-sided up), joint (d, g) p 0.235.
**Curvature after adding the hinge (Q+H):** c = -0.0147 per yr^2 vs 0.1385 for Q alone, a ratio of -0.11, i.e. essentially all of the quadratic curvature is absorbed; Webb p two-sided 0.89 (CR2 t -0.14). Conversely, with c in the model the hinge terms are weak: joint (d, g) p 0.61, g alone 0.139 two-sided. The two terms share the same variance; neither is detected once the other is present.
Instrument check for the clustered tests passed: Q-alone c = 0.13847 (CR2 t 1.99), Webb one-sided p 0.0936 (CL1 reported 0.0942). No cluster needed the CR2 fallback. Clustered inference rests on 7 developers (15/9/4/2/1/1/1); coverage is not validated; Webb p-values are descriptive.

## Reading
The data fit a break at o1 as well as a smooth curve, and the design cannot separate them: that is a power statement about this design (consistent with F's 34 percent curvature power), not evidence for or against a regime change. The registered verdict is withheld because the quadratic positive control missed its 90 percent bar; the control's own result is informative (rr = 4 is not strong enough here). Not run: record-only series, 2024-12 break, bootstrap-LR classifier, leave-OpenAI-out, proxies dropped.
