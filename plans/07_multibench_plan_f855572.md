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
