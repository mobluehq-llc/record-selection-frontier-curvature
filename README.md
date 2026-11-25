# Record selection can mimic or mask acceleration in AI benchmarks

Reproducibility bundle for paper F (arXiv version v10). **Staged 24 November 2026; not yet published (no repository URL or DOI yet).**

**Author:** Adam Faust, MOBLUEHQ, Inc. See `CITATION.cff`.

## What the paper is
Acceleration claims for AI capability trends are often read off the best-so-far (record) curve of a benchmark. The paper simulates steady exponential progress on the release calendar and task structure of the public METR time-horizon data, shows that a quadratic fitted to the record-setting models has a spurious curvature, audits record-based and all-model tests on 22 Epoch AI benchmark series with date permutation and trend planting, and re-analyses the real METR series with cluster-robust (CR2, Webb) and permutation tests. Gated, confirmatory, corrective and exploratory results are labelled as such in the paper.

## One command
```
make verify          # python3 -I verify.py CLAIMS.md ; standard library only, about a minute
```
1. **Regeneration.** `paper/make_numbers.py` is re-run on the *stored* results in a temporary copy of `paper/`; all 693 macros of `paper/numbers.tex` and all 19 `paper/table_*.tex` must equal the arXiv v10 files. Every macro's source file and key is listed in `paper/numbers_manifest.txt`.
2. **Claims.** `CLAIMS.md` ties each abstract number to its macro, to the abstract text and, where a single file carries it, to the stored result (JSON keys, SHA-256 of the main stored results). Exit status is non-zero on any mismatch or missing file.

This regenerates every number and table from stored results; it does **not** repeat the simulations. The simulations are re-runnable with the scripts below (a fresh run under another NumPy/SciPy version draws different random numbers, so the stored files are the record). Pinned versions: `requirements.txt` (NumPy 2.5.5, SciPy 1.18.1, pandas 3.1.1, matplotlib 3.11.2, Python 3.12+).

## Layout
- `paper/` arXiv v10 source (`main.tex`, `supplement.tex`, tables, `numbers.tex`, `refs.bib`, `figs/`), the two PDFs, `ABSTRACT.txt`, and the builders (`make_numbers.py`, `make_figs.py`, `make_arxiv.py`, `build.sh`, illustration/sensitivity scripts and their stored JSON).
- `code/` the first-plan simulators and tests: `fcore.py` (METR runs to the dense model x task representation, logistic horizon fits, bootstraps), `fsim.py` (calibrated simulator), `size_sim.py`, `power_sim.py`, `real_run.py`, `holdout.py`, `hinge_study.py`, `split_task.py`, `vuong.py` (Smith/Vuong-type likelihood comparison), `validate_fit.py`, `calibrate.py`, analysis scripts.
- `design/` the design grid, Amendments 2 and 3 and follow-up 1 (frozen core `fcore.py`, `fdesign*.py`, `fsim.py`, `grid*.py`, `run_*.py`, `analyze_*.py`), including the censored-crossing and inverse-Mills arms, with stored results in `results_a2/`, `results_a3/`, `summary_base/`, and `cf1_closed_form.py`/`cf1_out.json`.
- `real_data/` the one-shot real-data run (`real_data_run.py`, `PINS.txt`) and the cluster-robust tests (`cluster_test.py`: CR2 and Webb; `cluster_size.py`), outputs in `out/`.
- `multibench_audit/` the 22-series Epoch audit with date permutation and trend planting (`audit_core.py`, `audit_run.py`, one-sided re-score), with the 46,000-row stored manifest (25 MB) in `results/`.
- `redteam_final/`, `topj/` the later red-team and top-journal amendments (hinge, split-task, permutation arms); `results/` first-plan and hinge/split-task results; `holdout_data/` (see data note).
- `U_frontier_trend_forecast_coverage/` the sibling forecast-coverage study used in one table (code, stored results).
- `plans/` the frozen pre-registration texts (files 01-12, redacted as described there) and the number manifest of the arXiv v2 build (file 13; the v10 manifest is `paper/numbers_manifest.txt`).
- `PATCHES.md`, `REDACTIONS.md` what differs from the working archive.
- `CLAIMS.md`, `verify.py`, `Makefile`.

## Data and licences of inputs
- **METR run files** (`runs.jsonl` of time-horizon 1.0 and 1.1, and `release_dates.yaml`) are public at github.com/METR/eval-analysis-public. That repository carries no licence file, so **they are not redistributed here.** `python3 data/fetch_metr.py` (or `make fetch-data`) downloads them into `data/metr/` and `holdout_data/` and verifies the SHA-256 in `data/SHA256SUMS_METR.txt` (v1.0 runs `f489d117...`, v1.1 runs `609f904f...`, dates `317b9291...`). They are needed only to re-run simulations or the real-data scripts.
- **Epoch AI benchmark files** (`data/epoch/`) are CC BY 4.0 (Epoch AI, "Capabilities & benchmarking", epoch.ai, retrieved 23 November 2026); redistributed with that attribution. Checksums: `data/epoch/SHA256SUMS.txt`.
- Code (`code/`, `design/`, `real_data/`, `multibench_audit/`, `redteam_final/`, `topj/`, `paper/*.py`, `verify.py`, the sibling study's `code/`): MIT, `LICENSE`. Paper text, figures, plans, stored results and the Epoch-derived data notice: CC BY 4.0, `LICENSE-DATA-TEXT`.

C1–C6 and D1–D5 were chosen from a larger internal brainstorm; the selection rule is in plans/04.

## Redactions and patches
Plans and narrative notes had internal operations notes (machine names, launch commands, local paths) replaced by "[internal operations note redacted]" (`REDACTIONS.md`). The redactions are operational only; the originals are available to referees on request. Scripts had absolute local paths replaced by script-relative ones (`PATCHES.md` lists the original and new SHA-256 of every patched file, because some files were pinned by checksum before their runs). No estimator, seed or statistic was edited.

## Known gap
`paper/main.tex` (v10, as submitted to the checks) still has the placeholder sentence in "Data and code availability" ("available on request pending cleanup"); it needs the final repository URL/DOI before posting.
