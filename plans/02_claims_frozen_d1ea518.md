# Claims ledger: F (headline FROZEN 2026-11-22 at S2)

**Headline H1:** for METR-style task time-horizon trends, tests of acceleration (super-exponential curvature) that treat model points as independent are miscalibrated: their false-positive rate under a pure-exponential truth with realistic task-sampling correlation exceeds nominal. The hierarchical (task-family/task/run) bootstrap restores nominal size. Consequently, current data cannot yet establish acceleration.

| # | Claim | Evidence | Check | Status |
|---|---|---|---|---|
| 1 | The iid quadratic-term test has size > 10% at nominal 5% under a calibrated exponential null | results/F_size.csv | simulation, CP | pending |
| 2 | The hierarchical-bootstrap test has size in [3, 7]% | same | same | pending |
| 3 | On the real METR v1.0 data, the hierarchical test does not reject exponential at 5% | results/F_real.csv | one-shot | pending |
| 4 | The N (models) and task count needed for 80% power against "doubling time halves" | results/F_power.csv | simulation | pending |
