# RESULTS CF1: cadence-curvature closed form (PLAN.md Amendment CF1, pre-registered in 3485fc9 before the run)
[internal operations note redacted]

**Verdict: BAR NOT MET. Closed form FALSIFIED as pre-registered (2/8 within tolerance, sign 7/8; bar was >= 7/8 and 8/8).** No retuning done.

| schedule | closed form | simulator mean (SE) | rel. err | pass | sign |
|---|---|---|---|---|---|
| real | 0.05664 | 0.06355 (0.00040) | -10.9% | yes | yes |
| even | -0.02444 | -0.01873 (0.00033) | +30.5% | no | yes |
| reflected | -0.02925 | -0.02488 (0.00039) | +17.6% | no | yes |
| late_g0.5 | -0.01565 | -0.01292 (0.00034) | +21.1% | no | yes |
| late_g0.75 | -0.02556 | -0.02175 (0.00034) | +17.5% | no | yes |
| early_g1.5 | -0.01808 | -0.01223 (0.00033) | +47.8% | no | yes |
| early_g2 | -0.01227 | -0.00608 (0.00032) | +101.7% | no | yes |
| bursty | -0.0000054 | +0.00023 (0.00032) | within 1 SE of 0 | yes | NO (sim indistinguishable from 0) |

Observations (descriptive, not tested): the exact expected record count from the quadrature matches the simulator to under 0.2% in every schedule, so p_i is right; the error comes from replacing the random-record-set OLS by a p-weighted fit (mean-field step). It captures the sign reversal (real positive, even/reflected negative) and the real-schedule magnitude (within 11%), but overstates negative curvature in the other schedules. The re-run reproduces schedule_illustration.json for real/even/reflected within MC error-ish (0.0635 vs 0.0642; -0.0187 vs -0.0192; -0.0249 vs -0.0251).
Next (a NEW amendment, not a retune here): a second-order or conditional-record-set correction, or an exact enumeration check at n=2,3.
