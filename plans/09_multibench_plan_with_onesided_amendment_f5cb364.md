# F multi-benchmark planted-trend audit: pre-registration (2026-11-24, written and committed BEFORE any statistic is computed)

Status: nothing has been run. Mechanics may be tested only on a synthetic series, and that output is discarded. Part of idea F (calibration of frontier-trend tests); [internal operations note redacted] CONFIRMATORY unless a line says EXPLORATORY. [internal operations note redacted].

## 0. What has already been looked at (disclosure)
F's METRs-only results (size/power of T-iid, T-hb, HC3, wild, perm, `mb_*`, developer-clustered tests) are known. Nothing computed on the Epoch benchmark files by F's statistics. Idea U's PLAN looked at record COUNTS per series only. The real-data amendment's rule stands: **no confirmatory claim about any real benchmark's trend is made here.** The real release dates are used only as the design; every score-date association is destroyed (permutation) or planted (known). U's card forbids reusing F's METR holdout; this audit does not touch it.

## 1. Question
F found, on METR run-level data, that the naive test for curvature of a record series (OLS F-test on t^2 over records) is oversized, and that a selection-aware model-level bootstrap is close to nominal. **Does that calibration generalise to other public benchmark series, with their own sizes, date patterns, saturation and developer clustering, when the truth is known by construction?**

## 2. Data (public, pinned; the runner refuses to start on a hash mismatch)
- Epoch AI `benchmark_data.zip` (CC BY 4.0), retrieved 2026-11-23 from `https://epoch.ai/data/`, held in `ideas/U_frontier_trend_forecast_coverage/data/epoch_benchmarks/` (89 files; sha256 of each in `ideas/U_frontier_trend_forecast_coverage/data/SHA256SUMS.txt`, re-checked at start and copied to `audit_pins.txt`). `benchmark_metadata.csv` gives scale, random baseline and ceiling. Columns used: `Model version`, `Release date`, the score column named in the metadata (`mean_score` or `Best score (across scorers)`), `Organization`. **Release dates only:** no training compute, no parameter counts, no other covariate enters.
- The METR series (U's copy of METR v1.1 time horizons, minutes) is included as a reference series so the audit can be read against F's known METR size.
- Software pins: Python 3.12.10 [internal operations note redacted], numpy and scipy versions written into `audit_pins.txt`; code frozen by sha256 in an amendment BEFORE launch: `audit_core.py` (record rule, T-iid, T-mb, T-cl, planting), `audit_run.py` (loop, manifest), reusing F's `design/fdesign.py::model_boot` logic and `U/code/ucore.py::record_mask` (strict running maximum in (date, name) order, the same tie-break as F).
- **Eligibility (frozen now, counts only to be taken by the runner and printed first):** a benchmark file is a series iff after dropping rows without date or score it has >= 30 distinct models, >= 8 records, and >= 15 distinct release months. Saturation rule as U: truncate before the first record >= 0.90 of the benchmark ceiling. Series list = whatever passes, written to `results/audit_series.json` and committed before any statistic; none added or dropped afterwards. Transform: scores in [0,1] -> logit(clip(s, 0.005, 0.995)); positive scores with max/min > 20 -> log2; otherwise z-score. Expected 15-35 series.

## 3. Constructions (per series; M = number of models)
- **N0 date-permutation null:** permute the release dates among the M models (organisation moves with the model, so developer clusters stay intact), 1000 permutations, seeds `SeedSequence([44, series_index, rep])`. Scores and the date set are unchanged, so there is NO score-date trend, yet the record rule still selects. The true quadratic coefficient is 0.
- **P1 planted linear:** N0 plus g(t) = s (t - t0) added to every model's transformed score, with s = 0.5 SD(y) per series span (span = last - first release date, in years). True quadratic coefficient 0.
- **P2+ / P2- planted curvature:** N0 plus g(t) = c (t - t0)^2 with c = +/- 0.5 SD(y) / span^2 (so the planted term moves scores by half a SD across the window), plus the linear P1 term. True quadratic coefficient = c on the model-level (all-models) scale. **Truth for the record series** is the coefficient fitted to the noise-free planted frontier on the same record dates, computed analytically in `audit_core.py` (so selection effects on the TRUE target are not mistaken for test error); both the all-model coefficient and this record-series truth are stored.
- t is in years from the first release date. Each construction x series x 1000 permutations = one cell.

## 4. Statistics (each two-sided at nominal 5%, sign of the coefficient stored)
- **T-iid:** OLS of the transformed record values on (t, t^2), F-test on t^2 over the record points.
- **T-mb (selection-aware, F's `mb_sota`):** resample the M models with replacement (B = 400), re-apply the record rule to each resample, refit the quadratic, percentile 95% CI of the t^2 coefficient; resamples with < 5 records skipped (count stored).
- **T-cl (developer-clustered, F's CL1 idea):** same, resampling organisations then models within them (B = 400). Series with < 8 organisations: T-cl "not measured" (a third count, not a pass).
- Rejection = CI excludes 0 (T-mb, T-cl) or p < 0.05 (T-iid). Coefficient and CI width stored per run.

## 5. Quantities and bars
For each series and construction: empirical size (N0 and P1; rejection rate, Clopper-Pearson 95% interval over the 1000 permutations), power (P2+, P2-: rejection in the planted direction), coverage of the true record-series coefficient by the T-mb and T-cl CI under P2+/P2-, and the bias of the point estimate.
- **Bar 1 (the naive test is miscalibrated beyond METR; replication of F claim 1):** T-iid size > 10% with CP-lower > 7% on N0 in >= 50% of series (as a count out of the measured series).
- **Bar 2 (selection-aware calibration generalises):** T-mb size in [3, 7]% (CP interval overlapping it counts as met) on N0 AND P1 in >= 80% of measured series, with the per-series table printed whatever the result.
- **Bar 3 (planted truth recovered):** pooled T-mb coverage of the planted record-series coefficient >= 0.90 (nominal 0.95) under P2+ and P2-, and pooled absolute bias < 25% of |c| .
- **Falsifier (the generalisation is dead):** T-mb size > 10% (CP lower > 7%) in >= 25% of series, or pooled coverage < 0.85. Then F's "selection-aware bootstrap is near nominal" is reported as METR-specific and the cause-by-series table (M, records, dates clustering) is the finding.
- **Power: no bar, reported** by series and by M.
- Three counts everywhere: met / not met / not measured. An unmeasured series is listed with the reason, never silently dropped.
- **Instrument checks (rule 18):** (i) a synthetic series with no selection (all models records) must give T-iid size in [3,7]%; (ii) planting c = 0 must reproduce N0 exactly (same rejections); (iii) the METR reference series must reproduce F's published T-mb size within +/- 2 points, else the port is wrong and no other number is used.
- EXPLORATORY: relation of size to M, record count, date clustering (Spearman); saturation-rule sensitivity (no truncation).

## 6. Compute, memory and launch [internal operations note redacted] NOT started)
Per run about 400 + 400 bootstrap refits of at most 200 points (about 0.05-0.1 ms each, vectorised) => about 0.1 s per (series, permutation, construction); 4 constructions x 1000 perms x about 25 series = 100,000 runs => about 3 h of one core; with **6 workers** (A Amendment 13a holds 5 of 16 cores) **about 40-70 min wall**, hard stop 3 h. Memory: under 300 MB per worker, under 2 GB total. Resumable manifest per (series, construction, block of 50 permutations); a killed run resumes.
```
[internal operations note redacted]
```
[internal operations note redacted](6 free cores) and `audit_core.py` / `audit_run.py` hashes are in an amendment. Outputs: `results/audit_summary.json` then `AUDIT_RESULTS.md` (per-series table, three counts, bars). The runner never kills processes and refuses to overwrite its output.

---
# CORRECTIVE AMENDMENT 2 (2026-11-24, written BEFORE any one-sided statistic is computed): audit the one-sided upward test
Trigger: Gemini red-team of F v4 (`paper/REVIEWS/GEMINI_REDTEAM_v4_112426.md`, point 4), checked in `REDTEAM_CHECKS_GEMINI.md`. Status: **CORRECTIVE**, not a new headline. The audit above scored only the two-sided 5% rule (percentile 95% interval; T-iid two-sided F p < 0.05). The paper's own test of acceleration is one-sided upward 5%. A claim that rested on the two-sided rule only ("near-nominal on METR") may therefore need qualifying. Nothing here replaces the registered bars, which stay as reported.

Known BEFORE computing (disclosure): F's simulator tables already show the METR model-bootstrap on records with the nominal rule at upward 13.68%, two-sided 5.85%, downward 0.37% (`design/results_a2/summary_a2.md` validation table, raw-rule column; paper Table S7). The prediction is therefore that the METR reference series will also be oversized one-sided in the audit. Wrong if it comes out otherwise.

Definitions (fixed now):
- **T-iid-1s:** reject iff fitted record-series t^2 coefficient > 0 and the F p-value / 2 < 0.05 (single-df F equals t^2). Computed exactly from the stored `iid_coef`, `iid_p`; no re-run.
- **T-mb-1s:** reject iff the 5th percentile of the valid bootstrap record-series coefficients (same resamples, same validity rule: >= 5 records, nonsingular, >= 20 valid) is > 0. The stored interval holds only the 2.5th and 97.5th percentiles, so the 5th is NOT in the stored outputs. It is obtained by a re-run of the bootstrap with the frozen `audit_core.py` and the identical seeds (`SeedSequence([44, series, rep, construction, 1])`), in a new script `audit_onesided.py` that imports `audit_core` unmodified. **Reproduction gate (rule 18):** the re-run 2.5th and 97.5th percentiles must equal stored `mb_lo`, `mb_hi` to 1e-9 in every row it covers; otherwise nothing from it is used.
- **T-cl-1s** (EXPLORATORY): same with the clustered resample (the RNG stream continues after the model bootstrap, as in `run_one`).
- Constructions N0 and P1 (size) for the 22 series and the METR reference (index 900). Power and coverage are not re-scored.
- Reading rule, same as the registered one: size consistent with [3,7]% if its Clopper-Pearson interval overlaps it; oversized if size > 10% with CP-lower > 7%. Report counts met / not met / not measured, per-series table whatever the result. One-sided Bar 2 (>= 80% of series consistent on N0 and P1) and the one-sided falsifier (oversized in >= 25% of series) are reported as DESCRIPTIVE restatements, not new pre-registered bars.

What would change a claim, fixed before computing: (a) if METR T-mb-1s on N0 is oversized (> 10%, CP-lower > 7%), the sentences saying the model-level bootstrap on records is near nominal on the METR design (main.tex Abstract/"What we do not claim"/Sec. III.E/Conclusion) must say "two-sided only; upward-one-sided it is oversized on METR too"; (b) if the number of series with T-mb-1s oversized differs from the two-sided count, the "oversized in x of 22" statement is qualified with both counts.

**Outcome of corrective amendment 2 (2026-11-24, after computing):** reproduction gate passed (46,000 rows, 0 mismatches). The prediction above was WRONG: METR reference T-mb one-sided N0 = 4.6% (in band). One-sided upward oversized on N0: T-iid 3/22 (two-sided 18), T-mb 1/22 (two-sided 9; 18/22 conservative), T-cl 0/22. Claim (b) triggers: the 18/22 and 9/22 statements are two-sided and need qualifying; claim (a) does not. Details `REDTEAM_CHECKS_GEMINI.md`, table `results/audit_onesided_scored.txt`.
