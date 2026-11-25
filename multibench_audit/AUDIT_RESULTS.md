# F multi-benchmark planted-trend audit: RESULTS (run 2026-11-24; pre-registration PLAN.md + PLAN_AMENDMENT_1.md)

Series: 22 eligible Epoch benchmark series (+ METR reference, not in the bar denominators). 1000 permutations x 4 constructions each. Counts below are met / not met / not measured.

## Verdicts

- **Bar 1** (T-iid size >10% with CP-lower >7% on N0 in >=50% of series): 18/22 series -> **MET**; not measured 0.
- **Bar 2** (T-mb size CP-overlaps [3,7]% on N0 and P1 in >=80% of series): 9/22 -> **NOT MET**; not measured 0.
- **Bar 3** (pooled T-mb coverage of planted coefficient >=0.90 both signs; pooled |relative bias| <25%): coverage P2+ 0.801, P2- 0.907; |rel bias| 9.32 -> **NOT MET**.
- **Falsifier** (T-mb oversized in >=25% of series, or pooled coverage <0.85): oversized in 41% of series, min coverage 0.801 -> **TRIGGERED**.
- Instrument checks: (i) no-selection T-iid size 4.9% -> pass; (ii) zero planting reproduces N0 -> pass; (iii) METR reference T-mb N0 size 4.7% vs F simulator base 5.2% +/-2 -> pass.
- T-cl not measured (<8 orgs or <500 valid): 2 series.

## Per-series table (size % [Clopper-Pearson 95%]; N0 = permutation null, P1 = planted linear)

| series | M | rec | iid N0 | mb N0 | mb P1 | cl N0 | cl P1 | mb pw P2+ | mb pw P2- | mb cov P2+ | mb cov P2- | cl cov P2+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aider_polyglot | 71 | 11 | 19.7 [16.9,22.7] | 8.7 [7.0,10.7] | 5.1 [3.8,6.6] | 3.2 [2.2,4.6] | 1.9 [1.2,3.0] | 0.0 | 7.2 | 92.2 | 95.4 | 97.2 |
| arc_agi_2 | 149 | 18 | 28.0 [25.0,31.1] | 27.1 [24.3,30.0] | 65.8 [62.8,68.7] | 13.0 [11.0,15.3] | 38.2 [35.2,41.3] | 0.0 | 17.5 | 26.9 | 84.7 | 52.7 |
| arc_agi | 103 | 13 | 8.6 [6.8,10.7] | 5.4 [4.1,7.0] | 6.1 [4.7,7.8] | 2.2 [1.4,3.3] | 0.8 [0.3,1.6] | 0.0 | 4.9 | 84.1 | 96.8 | 97.6 |
| balrog | 40 | 9 | 15.0 [12.4,18.0] | 31.2 [28.1,34.4] | 30.9 [28.0,34.0] | 20.7 [18.1,23.6] | 12.8 [10.8,15.1] | 0.0 | 26.6 | 58.6 | 76.0 | 80.0 |
| chess_puzzles | 169 | 16 | 14.4 [12.1,16.9] | 5.4 [4.1,7.1] | 6.0 [4.6,7.7] | 0.6 [0.2,1.3] | 0.1 [0.0,0.6] | 0.3 | 4.7 | 90.4 | 96.9 | 99.7 |
| frontiermath | 95 | 15 | 19.9 [17.2,22.9] | 38.1 [35.0,41.3] | 35.2 [32.2,38.3] | 26.7 [24.0,29.6] | 26.7 [24.0,29.6] | 0.0 | 34.1 | 49.2 | 74.1 | 66.2 |
| frontiermath_tier_4 | 72 | 12 | 13.0 [10.7,15.7] | 6.0 [4.6,7.7] | 3.9 [2.8,5.3] | 2.8 [1.9,4.1] | 1.7 [1.0,2.7] | 0.0 | 2.9 | 94.2 | 97.5 | 98.7 |
| frontiermath_tiers_1_3_v2 | 65 | 12 | 10.2 [8.1,12.5] | 3.7 [2.6,5.1] | 2.8 [1.9,4.1] | 2.2 [1.4,3.4] | 1.2 [0.6,2.1] | 0.2 | 5.1 | 95.9 | 96.9 | 98.6 |
| gpqa_diamond | 179 | 13 | 26.4 [23.5,29.5] | 26.6 [23.9,29.5] | 35.1 [32.1,38.1] | 8.3 [6.7,10.2] | 11.1 [9.2,13.2] | 0.0 | 25.7 | 56.3 | 78.5 | 84.8 |
| gso | 42 | 13 | 12.4 [10.0,15.1] | 8.5 [6.7,10.6] | 4.6 [3.3,6.1] | nan [nan,nan] | nan [nan,nan] | 0.1 | 7.0 | 96.8 | 93.8 | nan |
| lmca | 204 | 23 | 32.3 [29.3,35.6] | 35.4 [32.4,38.5] | 41.7 [38.6,44.8] | 14.6 [12.5,16.9] | 17.1 [14.8,19.6] | 0.0 | 24.0 | 60.8 | 84.2 | 87.9 |
| math_level_5 | 60 | 8 | 5.3 [3.8,7.1] | 3.1 [2.1,4.4] | 0.8 [0.4,1.6] | 1.8 [1.1,2.9] | 0.2 [0.0,0.7] | 0.6 | 2.3 | 98.9 | 97.7 | 99.7 |
| metr_time_horizons | 45 | 21 | 18.0 [15.1,21.2] | 3.7 [2.5,5.2] | 1.2 [0.6,2.1] | nan [nan,nan] | nan [nan,nan] | 0.8 | 1.2 | 99.2 | 96.0 | nan |
| mmlu | 135 | 8 | 16.1 [13.7,18.7] | 16.6 [14.3,19.1] | 19.1 [16.7,21.7] | 2.8 [1.9,4.0] | 3.1 [2.1,4.4] | 0.0 | 15.3 | 69.8 | 89.3 | 91.8 |
| mystery_game_puzzles | 144 | 9 | 12.6 [10.5,15.0] | 3.7 [2.6,5.1] | 5.3 [4.0,6.9] | 0.6 [0.2,1.3] | 0.7 [0.3,1.4] | 5.5 | 0.1 | 95.4 | 95.5 | 99.8 |
| open_book_qa | 42 | 10 | 9.9 [7.5,12.6] | 5.5 [4.1,7.3] | 3.2 [2.1,4.5] | 3.9 [2.7,5.4] | 1.3 [0.7,2.3] | 1.1 | 1.3 | 97.2 | 94.6 | 99.2 |
| otis_mock_aime_2024_2025 | 131 | 17 | 16.4 [14.0,19.1] | 15.3 [13.1,17.7] | 15.3 [13.1,17.7] | 3.8 [2.7,5.2] | 3.0 [2.0,4.3] | 0.3 | 13.4 | 79.9 | 91.0 | 95.6 |
| simplebench | 120 | 15 | 21.3 [18.5,24.2] | 24.3 [21.6,27.1] | 26.5 [23.8,29.4] | 7.1 [5.6,8.9] | 7.6 [6.0,9.4] | 0.0 | 23.2 | 56.2 | 80.8 | 84.7 |
| simpleqa_verified | 101 | 9 | 17.9 [15.3,20.7] | 7.4 [5.8,9.2] | 7.7 [6.1,9.6] | 1.1 [0.6,2.0] | 0.7 [0.3,1.4] | 0.0 | 6.5 | 87.5 | 95.0 | 99.2 |
| trivia_qa | 38 | 8 | 5.4 [3.8,7.4] | 12.8 [10.6,15.2] | 12.4 [10.4,14.6] | 5.2 [3.8,6.9] | 3.1 [2.1,4.4] | 0.2 | 11.3 | 86.4 | 91.4 | 95.6 |
| weirdml | 140 | 17 | 13.8 [11.5,16.3] | 8.1 [6.5,9.9] | 6.0 [4.6,7.7] | 0.8 [0.3,1.6] | 0.5 [0.2,1.2] | 0.0 | 8.7 | 89.4 | 93.8 | 99.6 |
| wino_grande | 80 | 9 | 10.9 [8.8,13.3] | 1.8 [1.0,2.8] | 1.4 [0.8,2.4] | 0.7 [0.3,1.5] | 0.2 [0.0,0.7] | 0.1 | 3.1 | 98.6 | 97.4 | 99.7 |
| metr_time_horizons (REF) | 45 | 18 | 18.6 [15.7,21.8] | 4.7 [3.4,6.3] | 2.3 [1.4,3.4] | nan [nan,nan] | nan [nan,nan] | 0.5 | 1.8 | 99.6 | 92.8 | nan |

## Exploratory (Spearman of T-mb N0 size against): M rho=0.27 (p=0.22); records rho=0.29 (p=0.19); months_per_model rho=-0.19 (p=0.40). Saturation-rule sensitivity: not run (not measured).

## Reading (added after the run; no statistic changed)
- The naive record-series F-test is oversized on 18/22 series, so claim 1 of F generalises beyond METR (Bar 1 met).
- The selection-aware model bootstrap does NOT generalise: it is near nominal on METR (4.7% reference, 3.7% in the series table) and on about 9 other series, but badly oversized on series with few models or hard saturation structure (arc_agi_2, balrog, frontiermath, gpqa_diamond, lmca, simplebench, mmlu, otis, trivia_qa: 12-38%). Falsifier triggered: F's "near nominal" is a METR-specific statement.
- Planted convex curvature (P2+) is essentially undetected (power 0-5%) and the record-series coefficient is biased well below the planted value (pooled |relative bias| 9.3, because the selection-induced concavity under date permutation dwarfs the planted effect), so the bootstrap CI under-covers P2+ (0.80). P2- coverage is 0.91 but the power there partly reflects that same selection concavity.
[internal operations note redacted]
