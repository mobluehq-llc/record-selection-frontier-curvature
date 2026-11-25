# U: results (run 2026-11-23 after the pre-registration commit f2e41bb; labels per PLAN.md section 4)

**STATUS: UNDERPOWERED / DESCRIPTIVE. Not a coverage claim.** Pre-registered power (20 effective targets, 4 series, 13 from one series) detects only a 21-point gap at 95% nominal. By the card's bar 4 the study stops at S2; it was run because the task asked for it. Runtime 6 s. Files: `results/U_summary.csv`, `U_per_series.csv`, `U_rows.csv`, `U_bars.json`.

Deviations (all logged before or at the run): MINREC 8 not 12 (before any fit); qubit series replaced by ML-hardware peak FLOP/s; M1 is a residual bootstrap, not task/run; GPQA failed the inclusion rule so 4 series, not 5; one script bug (a column name in the bar-3 width ratio, crash before any output) fixed after the first failed run, no result seen.

## Primary: 95% interval, 12-month horizon, truth = best-so-far at the target date
Counts are met (inside) / not met (outside) / not measured, over (series, origin) targets, 4 series (compute 26 origins, hw 8, eci 4, metr 2).

| method | inside / outside / not measured | coverage | cluster-bootstrap 90% | mean width* |
|---|---|---|---|---|
| M0 naive OLS on records | 35 / 5 / 0 | 0.875 | [0.67, 1.00] | 8.17 |
| M0all naive OLS on all points | 29 / 11 / 0 | 0.725 | [0.50, 0.80] | 11.57 |
| M1 residual bootstrap | 30 / 10 / 0 | 0.750 | [0.57, 1.00] | 6.56 |
| M2 selection-aware model bootstrap | 32 / 8 / 0 | 0.800 | [0.72, 0.92] | 5.78 |
| M3 conformal | 26 / 2 / 12 | 0.929 | [0.91, 1.00] | 3.46 (2 series only) |
*mean width in each series's transformed units (mixed), so compare methods, not series.

80% nominal, 12 m: M0 0.650 (26/14), M1 0.575, M2 0.600, M3 0.788 (26/7, 7 not measured), M0all 0.200. At 6 months M0 95% = 0.900, at 24 months 0.813 (3 series).

Per series, M0 95% at 12 m: compute 23/26 (0.88), hw 8/8, eci 4/4, metr 0/2 (both origins missed). The pooled number is mostly the compute series.

## Bars (pre-registered)
1. Undercoverage claim NOT supported: cluster upper bound 1.00 (>= 0.95). Practical bar (pooled < 0.85) NOT met: 0.875.
2. Falsifier did NOT fire: only 2 of 4 series have M0 within Clopper-Pearson error of the nominal at both 80% and 95% (need 4). The failure is at the 80% level (pooled 0.65), not 95%.
3. No correction passes. M1 0.75, M2 0.80 (width 0.75x M0, better on 1 of 4 series), M3 0.93 with width 1.28x M0 but measurable on only 2 of 4 series and better on 1 of 2. M2 is narrower and does NOT restore coverage here; on this data selection-aware resampling made intervals tighter, which worsened coverage.
4. UNDERPOWERED (see top).
5. Appendix row 8 (Sevilla et al.): stated 2010-2022 doubling 5.6 months [5.0, 6.2]. Realised post-2022-02 all-model doubling, 236 notable models: 4.7 months, 95% CI [4.0, 5.9]. Point estimate outside the stated interval (faster), intervals overlap. Other appendix rows (Steinhardt, Hypermind) are the cited percentiles only: MMLU 2022 and MATH 2022 Hypermind were far outside (MATH 12.7 vs 50.3; MMLU 57.1 vs 67.5); n too small for a coverage claim.

## Reading
- Naive 95% intervals on record fits cover about 88% at 12 months (35/40) and the 80% intervals only 65%: mild undercoverage that this sample cannot separate from 95% (power 21 points), but 80% undercoverage is clear in the Clopper-Pearson sense (0.48-0.79, optimistic since origins overlap).
- Fitting all points and scoring against the frontier is badly biased (80% interval covers 20%), the expected selection effect.
- METR missed both origins: the trend accelerated (consistent with the TH1.0 to TH1.1 revision).
- The kill clause (naive within error on all series) did not fire; the plan bar for a published claim (power) is not met. Recommendation: do not write this up as a coverage paper from these series; either wait for more METR/ECI origins, or add series (needs a sourced qubit table, more benchmarks) before S3.
