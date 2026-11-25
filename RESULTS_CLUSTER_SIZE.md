# F: size of the developer-clustered curvature tests (Amendment CS1; EXPLORATORY, synthetic data)
[internal operations note redacted]

## One-sided (upward) 5% size, % [Clopper-Pearson 95%]; VALID = CI inside [3.5, 6.5]
| cell | CR2 (Satterthwaite) | Webb wild cluster | Rademacher exact (128) |
|---|---|---|---|
| R_null_val (existing) | 3.38 [2.84, 3.98] inconclusive | 4.30 [3.69, 4.98] VALID | 4.30 [3.69, 4.98] VALID |
| MF1_null_val (existing) | 3.17 [2.65, 3.77] inconclusive | 4.28 [3.67, 4.95] VALID | 4.42 [3.81, 5.11] VALID |
| N50_null_val (existing) | 5.08 [4.42, 5.80] VALID | 5.45 [4.77, 6.20] VALID | 5.80 [5.10, 6.57] inconclusive |
| LAD0_gauss (existing) | 2.38 [1.93, 2.90] CONSERVATIVE | 3.72 [3.16, 4.36] inconclusive | 3.75 [3.18, 4.39] inconclusive |
| DEV rho 0.3 (new) | 2.70 [2.22, 3.25] CONSERVATIVE | 4.80 [4.16, 5.51] VALID | 4.88 [4.23, 5.59] VALID |
| DEV rho 0.6 (new) | 2.25 [1.81, 2.76] CONSERVATIVE | 4.52 [3.90, 5.22] VALID | 4.55 [3.93, 5.24] VALID |
Two-sided 5% rates (descriptive): CR2 1.2-3.7%, Webb 2.6-4.1%, Rademacher 3.9-5.3%. Lower-tail rates are similar to the upper-tail ones.

## Bar verdict (pre-registered: size-valid overall only if VALID in all 4 primary AND both extension cells)
- **CR2: NOT size-valid.** Valid in 1 of 6 cells; conservative in 3 (including both developer-dependence cells), inconclusive in 2. Never anti-conservative.
- **Webb wild cluster: NOT size-valid by the bar** (valid in 5 of 6; fails only on the idealised Gaussian cell LAD0, 3.72% [3.16, 4.36], inconclusive). Never anti-conservative; largest rate 5.45%.
- **Rademacher exact: NOT size-valid by the bar** (valid in 4 of 6; inconclusive in N50, 5.80% [5.10, 6.57], and LAD0).

## Can the real-data clustered p-values be interpreted? (reading rule fixed in CS1)
- **CR2 p_up 0.112: no, as a calibrated number.** The test rejects about half as often as nominal (2.3-3.4% in five of six cells), so 0.112 overstates the evidence against acceleration; a non-significant CR2 result carries little information (low power, and the df of 1.5 makes it very conservative).
- **Webb p_up 0.094: not certifiable by the bar, but not optimistic.** It is near nominal (3.7-5.5%) and never anti-conservative, including when a developer level shift is present (4.5-4.8%). It can be read as an approximately calibrated p-value, slightly on the conservative side, so that "not significant at 5% (0.094)" stands; the bar's label for it stays "inconclusive in one cell".
- Net: the CL1 conclusion ("p < 0.05 does not survive clustering") is not an artefact of an anti-conservative-test failure in the wrong direction; its weight rests on Webb, not CR2. No power is measured here, so it still does not show growth is not accelerating.

## Limits
Exponential null at one design only; developer effect is a shared level shift without drift (the brainstorm's AR(1) component was not run); the existing simulators carry no developer dependence (cells 1-4), so only the two DEV cells probe it; no power study; 4000 replicates (CP half-width about 0.7 points). EXPLORATORY, one amendment, bar unchanged after results.
