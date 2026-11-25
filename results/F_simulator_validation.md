# Null simulator validation (200 fresh datasets, seeds SeedSequence([36,i]); calibration used [35,*])

sigma_m=0.943 (model offset SD, log2 units), sigma_j=1.667 (task jitter SD, log2 min), phi=0.635 (family share of jitter variance)

| metric | real | sim median | sim 5-95% | share of sim below real |
|---|---|---|---|---|
| sd_all | 0.913 | 0.949 | [0.754, 1.166] | 0.38 |
| sd_sota | 0.574 | 0.767 | [0.436, 1.182] | 0.17 |
| crosscorr | 0.466 | 0.433 | [0.365, 0.513] | 0.73 |
| icc | 0.618 | 0.612 | [0.437, 0.731] | 0.52 |
| slope_all | 1.759 | 1.710 | [1.477, 2.018] | 0.61 |
