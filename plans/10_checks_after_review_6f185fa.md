# Pre-registration: checks prompted by ChatGPT's final review of v6 (written 2026-11-24 BEFORE any of these runs; exploratory, descriptive, no new claims enter the paper beyond the stated notes)

Frozen inputs: pinned METR runs (sha256 f489d117...), `release_dates.yaml` (sha 317b9291...), `real_data/out/real_v10.json`, frozen code in `design/` and `multibench_audit/audit_core.py` (not modified). New code lives only in `redteam_final/`. Interpreter: `.venv/bin/python`.

## A. Proxy dates (ChatGPT item a)
Verified facts (sources fetched 2026-11-24): METR paper (arXiv 2503.14499v4) Sec. 3.2 footnote 6 gives davinci-002 GPT-3's release date and gpt-3.5-turbo-instruct GPT-3.5's date; OpenAI post of 22 Aug 2023 makes davinci-002 and babbage-002 available; OpenAI's deprecations page lists both as replacements in a notice dated 6 Jul 2023. A public date for gpt-3.5-turbo-instruct itself (18 Sep 2023 from memory) is NOT verified from a fetched source.
Scenarios for the paired Gaussian experiment (same code as `paper/make_schedule_illustration.py`: 33 models, exactly exponential truth at the calibrated rate 1.739 doublings/yr, iid N(0, sigma_m) model noise, 40,000 replicates, the SAME noise draws in every scenario, SeedSequence([4714, 0]); record = strict improvement, at least 4 records):
- S0 original pinned calendar;
- S1 availability: davinci-002 -> 2023-08-22, gpt-3.5-turbo-instruct -> 2023-09-18 (flagged unverified);
- S1b availability, earliest document-supported: davinci-002 -> 2023-08-22, gpt-3.5-turbo-instruct -> 2023-07-06;
- S2 both proxy anchors excluded (31 models, pinned dates).
Outputs: mean record-only beta2 (SE), r_eq = (1+q)/(1-q), q = beta2*span/rate (span from each scenario's own first and last date, rate 1.739), mean all-model beta2. The same three calendars applied to the observed horizons (all-model beta2, HC3 t and one-sided p, record-only beta2, r_eq). Prediction: S1/S1b move the late-dense geometry little (two of 33 dates move); r_eq stays above 1.4. A result that r_eq falls below 1.25 or changes sign in S1 or S2 would be reported as a material dependence on the proxies.

## B. GPT-2 imputed outcomes (item b)
Identification rule: rows with run_id beginning `fake_` (87 rows for GPT-2: 80 HCAST, 7 RE-Bench, all score 0; 660 real SWAA rows). Refit A: drop the imputed rows (GPT-2 fitted on SWAA only), all else unchanged, same ridge logistic. Refit B: also report the horizons of GPT-2 and davinci-002 on SWAA-only support for both models. Outputs: GPT-2 log2 horizon before and after, observed all-model beta2, HC3 p, record curvature, r_eq. Prediction: METR states removing the imputed zeros has a negligible effect; we expect GPT-2's horizon to move by less than 0.5 log2 units. Decision: report either way.

## C. Same-day ties (item c)
Observed series: three same-day pairs (o3/o4-mini 2025-04-16; Claude 4 Opus/Sonnet 2025-05-22; Claude 4.1 Opus/gpt-oss-120b 2025-08-05). Compare four rules on the observed horizons: R1 frozen pipeline order (date, then name; strict improvement); R2 date then reverse name; R3 group rule: at most one record per date, the day's maximum if it exceeds all earlier days; R4 100 random within-day orders. Frozen rule for all future work: R3 (order-invariant by construction). Simulation: the paired Gaussian experiment on the real calendar under R1, R2, R3, plus random shuffling of the input row order before sorting (R1 sorts by (date, name) so input order cannot matter; this is tested, not assumed). Prediction: simulation means under R1, R2, R3 agree within 2 MC SE (noise exchangeable); the observed record count differs between R1 and R2 only through o3/o4-mini.

## D. Audit: one-sided F test under planted linear trend; ceiling cut-off (item d)
Same 22 series and METR v1.1 reference (index 900), 1000 permutations each, same seeds (BASE_SEED 44; the permuted frames are those already stored). Constructions: N0, P1 (the pre-registered planted half-SD linear trend), PF (the series' own fitted OLS slope of y on t, planted when positive, series skipped otherwise). Statistic: the OLS F test on records (frozen `t_iid`), one-sided upward = coefficient > 0 and p/2 < 0.05; also two-sided and the undefined-fit rate (fewer than 4 records). SAT (the 90%-of-ceiling truncation) varied over {0.80, 0.90, 0.95, none}. Verdicts by the audit's own function (OVER if rate > 10% and CP lower > 7%; 'in' if CP overlaps [3,7]%). Report the number of series OVER in each cell and the median one-sided rate. No decision rule beyond description. Bootstrap tests are not re-run.

## E. Table IV (item e)
Not a run: the stored `summary_a2.md` power table already has separate columns for HC3, wild, OLS and permutation (raw and size-adjusted). Report them separately in the check note and in the table caption/rows. Expectation (from the code's own assertion): size-adjusted power of HC3 = wild and OLS = permutation identical, because they share a statistic and cut-offs come from the statistic's own calibrated null; raw power differs.

## F. Developer influence (item f)
Observed 33 horizons, developer map from `real_data/cluster_test.py`. (i) Leave-one-developer-out all-model beta2, HC3 t and one-sided p, record curvature. (ii) Partial leverage of the t^2 coefficient: residualise (t-tbar)^2 on (1, t-tbar); share_i = r_i^2 / sum r^2, by model and by developer. Descriptive.

## G, H. Citations and wording
G: Kinniment et al. (2026), Ballerini and Resnick (1987, J. Appl. Probab. 24, 827-837, doi 10.2307/3214208) and Franke, Wergen, Krug (2010) checked against sources/Crossref; added to refs.bib only if verified. H: delete "as it should" from S4.
