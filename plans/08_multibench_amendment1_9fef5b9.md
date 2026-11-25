# PLAN amendment 1 (2026-11-24), committed BEFORE any audit statistic is computed

[internal operations note redacted] the audit is light: about 27 ms per run measured on a discarded synthetic series), 4 workers, `nice`. Python venv (3.14.7, numpy 2.5.5, scipy 1.18.1, pandas 3.1.1; [internal operations note redacted] versions are in `results/audit_pins.txt`). Data: the Epoch `benchmark_data` files already pinned and re-checked today (94/94 sha256 match `U/data/SHA256SUMS.txt`; its self-entry is the empty-file hash and is ignored); no new download was needed, official source and licence (CC BY 4.0) as in the plan.

Code frozen (sha256): 
- audit_core.py f6b123ee344ef4cb8586008ef074cb4669d98b0a3e6875526f630b1f8548c8e2
- audit_run.py 43eb98a3ce9f6d689ede308ad79d7579cfd260b6de674a92a395c1afbd00c351
- audit_checks.py 331fdb2744fe870d57848504eac584c1efa1a0b094bebee2f7d00d35bcd5c6b4 (checks i, ii)
- audit_summarize.py a03b9c1c5586d7353ba3e066eefee01101ae7a77392592e33177af35b5eeec6e (bars, tables; a bug fix here after the run is allowed and will be disclosed, it cannot change a statistic)

Series list: `results/audit_series.json` (22 eligible, 69 excluded with reasons; no statistic computed to make it), committed with this amendment. Interpretations fixed here where the plan was open:
1. Eligibility counts are taken on the series actually analysed (after dedupe to the best score per model version, drop of rows without date or score, saturation truncation at 0.90 x metadata ceiling). Score column, scale and ceiling come from `benchmark_metadata.csv`; benchmarks with no source file there (e.g. SWE-bench Verified) are excluded with that reason, even where a csv exists.
2. Transform: all 22 are scores in [0,1] so logit(clip 0.005..0.995). METR reference series (index 900, 'Time horizon' minutes, log2) is outside the bar denominators and used only for check (iii).
3. Task blocks are (series, construction, block of 50 permutations); T-iid is an F-test of t^2 over record points; T-mb resamples models (B=400) and re-applies the record rule; T-cl resamples organisations then models within (B=400); t is rescaled to [0,1] for fitting and coefficients reported per year^2.
4. Planted truth: the planted term is exactly quadratic, so the record-series truth and the all-model truth are both c (the fitted coefficient of the noise-free planted function on any dates). Coverage is of c; selection effects therefore show as miscoverage, which is the object.
5. "Measured series" for a statistic: >= 500 of 1000 valid replicates on N0. Bar 3 pooled |bias| = mean over measured series (both signs) of |mean(estimate - c)| / |c| < 0.25. Falsifier oversize test applies to N0 or P1.
6. Check (ii) is run as: planting amplitude s=0, c=0 through the planting code on three series (0, 8, 10), 100 permutations, rejections and coefficient identical to N0. Check (iii) has no F-published METR-record-series size to compare with (F's published T-iid 27.9% / T-hb 35.4% are on run-level data, and 5.2% is its simulator base cell), so it is pre-declared as: METR reference T-mb N0 size in [3.2, 7.2]% (F's mb_sota simulator base 5.2 +/- 2). If it fails, the port is not declared wrong on that alone; it is reported as a reference discrepancy.
7. Saturation-rule sensitivity (exploratory) is not run; reported as not measured.
