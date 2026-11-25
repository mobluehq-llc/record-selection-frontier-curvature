# PREREG: split-task replication on the stored v1.1 runs (internal brainstorm pick; ChatGPT final-review request)
Status: EXPLORATORY (a descriptive audit of 20 models; it does not carry the paper's headline). Written and committed BEFORE any split statistic is computed (2026-11-24). [internal operations note redacted](20 dated models, 228 tasks, 79 task families; the `human` rows and the undated `flamingo_2` rows are excluded by that loader).

## Hypotheses
H1 (selection on measurement noise). Records chosen on half A show more curvature on A than the same models re-measured on half B: mean D1 > 0.
H2 (what survives). The same selected models, measured on B, still show more curvature than all models measured on B: mean D2 > 0.
H0: D1 = 0 (and D2 = 0). The paired differences below are the whole estimand set; nothing else is a claim.

## Quantities (curvature = quadratic coefficient, log2 horizon on years since 2019, OLS, `fcore.quad_fit`)
Per split s and direction (select on X, replicate on Y; (X,Y) = (A,B) and (B,A)):
- h_X, h_Y: per-model log2 h50 from the weighted ridge logistic of `fcore.fit_logistic` on the tasks of that half only (same weights, same lam).
- sel = record models on X: `fcore.sota_mask(h_X)` (date-then-name order, strict improvement), restricted to models with a valid fit on both halves.
- C_X(sel) = curvature of sel using h_X; C_Y(sel) = curvature of the same sel using h_Y; C_Y(all) = all-model quadratic curvature using h_Y (all valid models).
- D1 = C_X(sel) - C_Y(sel); D2 = C_Y(sel) - C_Y(all); D3 = D1 + D2 = C_X(sel) - C_Y(all).
- Secondary: C_Y(rec_Y) (records re-selected on Y); r_resid = correlation across models of the residuals of h_A and of h_B from each half's own linear date trend (all valid models) (replicable model quality vs independent noise).
- Split value = mean over the two directions; reported estimate = mean over splits.
**Validity of a half-fit:** valid iff a and b are strictly inside the optimiser bounds (|b - bound| > 1e-6 and a not at +-60). Invalid half-fits are dropped (model excluded from that split-direction in both halves) and counted. A split-direction is **estimable** iff sel has >= 4 valid models in both halves and all-model valid count >= 4. The report states the estimable fraction per model and overall; if overall < 50 percent the result is called not estimable.

## Splits (fixed before any run)
Unit = task family. Order families by (mean log2 human_minutes of their tasks, name); form consecutive pairs; in each pair a seeded coin sends one to A and the other to B (the 79th, unpaired, family is sent by coin). This balances difficulty. 200 splits, seed `SeedSequence([5301, s])`, s = 0..199. Reported balance: mean |difference| in mean log2 human_minutes and in task count between halves.

## Exactness gate (before any real result is read)
Horizons from the full 228 tasks must reproduce `results/F_holdout.json` per-model log2 horizons to 1e-9, else stop.

## Uncertainty (developers and task families)
Developers (frozen mapping from the alias string): Anthropic (Claude ...), OpenAI (GPT-*, o1, o3, o1-preview), Google (Gemini). Only 3 developer clusters exist, with 8 / 11 / 1 models: developer clustering cannot be done credibly, and this is stated, not hidden.
1. **Family bootstrap** (task-family resampling; each family is the unit; multiplicities weight the cell counts N and S as in `fcore.hb_weights`; distinct families are then split as above): B = 300 bootstrap draws x 10 splits each, seed `SeedSequence([5302, b])`. 95 percent percentile interval of the draw-mean of each D.
2. **Developer + family two-way bootstrap**: same draws, additionally resampling the 3 developer clusters with replacement (their models are duplicated; the same-name duplicates cannot be records). Draws with fewer than 4 estimable direction-splits are counted and dropped; the count is reported. Flagged as unreliable with G=3.
3. **Leave-one-developer-out** on the 200 real splits (3 drops), point estimates only.
Reading rule: "supported" for H1 requires the lower end of BOTH interval 1 and interval 2 above 0, and the control gates below met; otherwise "not supported" (an interval that includes 0 is a null, not a negative). Same rule for H2.

## Controls (simulation on the real dates, real run counts n[m,k], real task difficulties and weights; per model b_m = real full-fit slope, true h_m = linear trend with the real all-model slope plus model effects e_m ~ N(0, s^2) with s = real all-model residual SD about the linear trend, **true curvature 0**; 100 draws, 20 splits each, seed `SeedSequence([5303, w, d])`)
- C0 noise-free, no shock: successes = n * p (fractional, exact logistic probabilities). Bar: max |D1| < 1e-6 (the instrument must reproduce itself exactly).
- C1 binomial run noise only (S ~ Binomial(n, p)): Bar: mean D1 > 0 by more than 2 MC SE, AND mean D1 with run counts x10 is smaller than at x1.
- C2 shared task shock only, noise-free: logit(p_mk) gets u_k + v_family(k) with u ~ N(0, 0.5^2), v ~ N(0, 0.5^2), identical for all models. Bar: |mean D1| < 2 MC SE of zero or < half of the C1 mean D1 (a shared shock must not look like selection on model noise). Also report mean C_Y(sel) and mean C_Y(all) against the planted truth 0 (does not wash out on B).
- C3 both. Report only.
If C0 or C1 fails, real-data D's are reported as uninterpretable. C2 failing is reported as "D1 conflates shared shock with selection".

## Falsifiers and what would count against H1
D1 CI includes 0, or any gating control fails. Report the answer either way. If the data cannot support a half-task horizon fit for some models (invalid fits, e.g. the weakest model near the floor), they are reported by name with their invalid fractions and the analysis uses the estimable ones.
