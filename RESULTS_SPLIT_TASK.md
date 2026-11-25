# RESULTS: split-task replication on v1.1 runs (EXPLORATORY; pre-registered in design/PREREG_SPLIT_TASK.md, commit 1a65771, before any computation)
[internal operations note redacted]

**Gates.** Exactness: full-task horizons reproduce F_holdout.json, max |dh| = 0 (the same code path; trivially met). All 20 models gave a valid half-task fit in all 400 half-fits per model, and all 400 split-directions were estimable (so every model supports a horizon fit on half the tasks here; invalid fraction 0 for each). Split balance: mean |difference| in mean log2 human_minutes between halves 0.98 (max 2.65), in task count 18.1 of 228; pairing balances family means, not task means, so the balance is only moderate.

**Controls (100 draws x 20 splits, truth curvature 0).** C0 noise-free: max |D1| = 0 exactly (bar met). C1 binomial noise: mean D1 = +0.0071, SE 0.0032 (2.25 SE, bar met; x10 run counts gives +0.00006, smaller, bar met). C2 shared task shock only: mean D1 = -0.00005, SE 0.0002 (|D1| inside 2 SE, bar met: a shared shock does not look like selection on model noise). So the instrument works, and the selection-on-run-noise effect it can detect is small, about +0.007.

**Real data (200 splits, 2 directions each).**
| quantity | mean | split SD | family-bootstrap 95% | two-way (family + developer) 95% |
|---|---|---|---|---|
| D1 = C_sel,select-half - C_sel,other-half | -0.0079 | 0.049 | [-0.141, +0.119] | [-0.170, +0.166] (293 of 300 usable) |
| D2 = C_sel,other-half - C_all,other-half | +0.0412 | 0.037 | [-0.078, +0.203] | [-0.204, +0.188] |
| D3 = D1 + D2 | +0.0333 | 0.039 | [-0.103, +0.219] | [-0.182, +0.268] |
Levels: C_sel on its selection half 0.657, same models on the other half 0.665, all models on the other half 0.624 (records re-selected on the other half 0.657). Residual correlation of h from the date trend across halves: mean 0.78 (family-bootstrap 95% [0.48, 0.76]; two-way [-0.04, 0.82]), so most of the model-to-model scatter replicates across independent task halves; it is not run noise.
Leave-one-developer-out (point estimates): D1 = +0.051 without Anthropic, -0.018 without OpenAI, -0.016 without Google; D2 = -0.052, -0.064, +0.044. The sign of D2 depends on which developer is dropped.

**Verdicts (registered reading rule).** H1 (selection on measurement noise inflates record curvature): NOT SUPPORTED. D1 is -0.008, a tenth of its split SD, both intervals contain 0, and the instrument's detectable effect (C1) is +0.007, so selection on run noise at this design is at most small. H2 (selected models' curvature survives independent measurement and exceeds all-model curvature): NOT SUPPORTED, point +0.04 with intervals containing 0 and sign flipping under developer drops. Shared task noise and run noise are not the explanation for the curvature here, but neither is the curvature shown to be reliable: the intervals are wide (about +-0.15), and only 3 developer clusters (8 / 11 / 1 models) exist, so the two-way interval is not credible and is a sensitivity row, not an estimate. Limits: 20 models, v1.1 suite only, descriptive; curvature 0.62-0.67 per yr^2 is a different window and model set from the v1.0 headline (+0.114 records, +0.138 all-model), not comparable; the 200 splits share the same tasks, so the split SD is not an uncertainty (the bootstrap rows are).
