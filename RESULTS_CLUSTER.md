# F: developer-clustered test of the all-model curvature (Amendment CL1; EXPLORATORY)
[internal operations note redacted]
Clusters (frozen from the METR release list): OpenAI 15, Anthropic 9, DeepSeek 4, Alibaba 2, Google 1, xAI 1, Moonshot 1 (G = 7).

| sample | beta2 (/yr^2) | unclustered HC3 p_up | CR2 t (Satterthwaite df) | CR2 p_up | wild cluster, Webb B=99,999 p_up | wild cluster, Rademacher exact (128) p_up |
|---|---|---|---|---|---|---|
| all 33 models | +0.138 | 0.0058 | 1.99 (df 1.5) | **0.112** | **0.094** | 0.086 |
| drop GPT-2, GPT-3 (n=31) | +0.232 | 0.310 | 1.31 (df 1.8) | **0.168** | **0.060** | 0.063 |
Two-sided p (all 33): CR2 0.224, Webb 0.188, Rademacher 0.172.

## Bar (CL1.5): p < 0.05 does NOT survive clustering
Neither the CR2 p_up (0.112) nor the Webb wild-cluster p_up (0.094) is below 0.05 on the full sample. The registered "evidence of acceleration" wording rested on HC3 p 0.0058 and wild-by-model 0.022; with releases grouped by developer the same statistic is not significant at the one-sided 5% level. The bootstrap 95th percentile of the null t is 2.55 against an observed 1.99.
Dropped-GPT-2/GPT-3 sensitivity: also not significant when clustered (CR2 0.168, Webb 0.060). Note that without those two early models the unclustered HC3 p is already 0.31 (curvature estimate larger, +0.23, but far noisier), so the original signal leans on the two earliest releases, consistent with the earlier note that the start-of-window rate rests on them.

## Caveats (stated, not hidden)
- G = 7 with three singleton clusters and one cluster holding 15 of 33 models: the CR2 df is only 1.5-1.8, so the CR2 t reference is very conservative, and the wild-cluster tests have no size study here (the simulator has no lineage dependence). A non-rejection has low power (R5.1 applies); it does not show growth is not accelerating.
- The tests agree in direction and order (p 0.09-0.11); the pre-registered wording therefore weakens from "evidence of acceleration" to "not detected once releases are clustered by developer" for this series. Paper v2's real-data wording should be revised accordingly (not done here).
- Developer is the only clustering tried (frozen); lineage-level or time-dependent dependence is not modelled.
