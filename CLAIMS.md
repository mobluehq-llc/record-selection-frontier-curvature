# Claims ledger (F bundle, arXiv v10)
Headline numbers of the abstract (`paper/ABSTRACT.txt`, from `paper/main.tex`), each tied to (a) its macro in `paper/numbers.tex`, (b) the abstract text, and (c) the stored result file it was computed from where a single file carries it.
`make verify` first regenerates ALL 693 macros and 19 tables of the paper from the stored results (`paper/make_numbers.py`; every macro in `paper/numbers_manifest.txt` names its source file and key) and requires them to equal the arXiv v10 files; it then checks the rows below.
Evidence paths are relative to this file; checks use the verify.py grammar.

| # | claim | evidence | check | status |
|---|---|---|---|---|
| 1 | Abstract number 1.76-fold: macro \biasRrSota = 1.76 | paper/numbers.tex | `grep:\\newcommand\{\\biasRrSota\}\{1\.76\}` | verified |
| 2 | Abstract text states '1.76-fold' | paper/ABSTRACT.txt | `grep:1\.76\-fold` | verified |
| 3 | Abstract number negative on 6 of 7: macro \cfNeg = 6 | paper/numbers.tex | `grep:\\newcommand\{\\cfNeg\}\{6\}` | verified |
| 4 | Abstract text states 'negative on 6 of 7' | paper/ABSTRACT.txt | `grep:negative\ on\ 6\ of\ 7` | verified |
| 5 | Abstract number negative on 6 of 7: macro \cfOther = 7 | paper/numbers.tex | `grep:\\newcommand\{\\cfOther\}\{7\}` | verified |
| 6 | Abstract text states 'negative on 6 of 7' | paper/ABSTRACT.txt | `grep:negative\ on\ 6\ of\ 7` | verified |
| 7 | Abstract number in 20 of 22: macro \mbBiasNegSign = 20 | paper/numbers.tex | `grep:\\newcommand\{\\mbBiasNegSign\}\{20\}` | verified |
| 8 | Abstract text states 'in 20 of 22' | paper/ABSTRACT.txt | `grep:in\ 20\ of\ 22` | verified |
| 9 | Abstract number in 20 of 22: macro \mbN = 22 | paper/numbers.tex | `grep:\\newcommand\{\\mbN\}\{22\}` | verified |
| 10 | Abstract text states 'in 20 of 22' | paper/ABSTRACT.txt | `grep:in\ 20\ of\ 22` | verified |
| 11 | Abstract number 27.9%: macro \powMaxTwo = 27.9 | paper/numbers.tex | `grep:\\newcommand\{\\powMaxTwo\}\{27\.9\}` | verified |
| 12 | Abstract text states '27.9%' | paper/ABSTRACT.txt | `grep:27\.9%` | verified |
| 13 | Abstract number reached 34%: macro \aTwoPowHcTwoRound = 34 | paper/numbers.tex | `grep:\\newcommand\{\\aTwoPowHcTwoRound\}\{34\}` | verified |
| 14 | Abstract text states 'reached 34%' | paper/ABSTRACT.txt | `grep:reached\ 34%` | verified |
| 15 | Abstract number p = 0.24: macro \realSotaPup = 0.24 | paper/numbers.tex | `grep:\\newcommand\{\\realSotaPup\}\{0\.24\}` | verified |
| 16 | Abstract text states 'p = 0.24' | paper/ABSTRACT.txt | `grep:p\ =\ 0\.24` | verified |
| 17 | Abstract number p = 0.0058: macro \hcPup = 0.0058 | paper/numbers.tex | `grep:\\newcommand\{\\hcPup\}\{0\.0058\}` | verified |
| 18 | Abstract text states 'p = 0.0058' | paper/ABSTRACT.txt | `grep:p\ =\ 0\.0058` | verified |
| 19 | Abstract number p = 0.094: macro \clWebb = 0.094 | paper/numbers.tex | `grep:\\newcommand\{\\clWebb\}\{0\.094\}` | verified |
| 20 | Abstract text states 'p = 0.094' | paper/ABSTRACT.txt | `grep:p\ =\ 0\.094` | verified |
| 21 | Abstract number oversized in 18 of 22: macro \mbBarOne = 18 | paper/numbers.tex | `grep:\\newcommand\{\\mbBarOne\}\{18\}` | verified |
| 22 | Abstract text states 'oversized in 18 of 22' | paper/ABSTRACT.txt | `grep:oversized\ in\ 18\ of\ 22` | verified |
| 23 | Abstract number gives 14 of 22: macro \mbIidTwoOverAtt = 14 | paper/numbers.tex | `grep:\\newcommand\{\\mbIidTwoOverAtt\}\{14\}` | verified |
| 24 | Abstract text states 'gives 14 of 22' | paper/ABSTRACT.txt | `grep:gives\ 14\ of\ 22` | verified |
| 25 | Abstract number (33 models: macro \nModels = 33 | paper/numbers.tex | `grep:\\newcommand\{\\nModels\}\{33\}` | verified |
| 26 | Abstract text states '(33 models' | paper/ABSTRACT.txt | `grep:\(33\ models` | verified |
| 27 | 33 models, 17 records in the METR v1.0 real-data run | real_data/out/real_v10.json | `json:M == 33` | verified |
| 28 | 17 records | real_data/out/real_v10.json | `json:n_records == 17` | verified |
| 29 | All-model HC3 one-sided p = 0.0058 (stored value) | real_data/out/real_v10.json | `json:reg.hc3_pup == 0.0058 +- 0.00005` | verified |
| 30 | Record-curvature one-sided p (SOTA, parametric bootstrap) = 0.24 | real_data/out/real_v10.json | `json:pb.sota_pup == 0.24 +- 0.005` | verified |
| 31 | Equivalent rate ratio of the all-model curvature 3.3 | real_data/out/real_v10.json | `json:rr_eq_allmodel == 3.3 +- 0.05` | verified |
| 32 | Webb cluster-bootstrap one-sided p = 0.094 (stored value) | real_data/out/cluster_v10.json | `json:full.webb.p_up == 0.094 +- 0.0005` | verified |
| 33 | Cluster test was run on the stored real_v10.json (hash pinned) | real_data/out/cluster_v10.json | `json:source_sha256 == af18dc74a3b97694c2f7e39253d7f1845257fac41ffe400b721d8beefb8e61ae` | verified |
| 34 | Audit: 22 series | multibench_audit/results/audit_summary.json | `json:n_series == 22` | verified |
| 35 | Audit: naive two-sided record test oversized in 18 of 22 (bar 1 count) | multibench_audit/results/audit_summary.json | `json:bar1.met == 18` | verified |
| 36 | Audit: bar 2 met in 9 of 22 | multibench_audit/results/audit_summary.json | `json:bar2.met == 9` | verified |
| 37 | Audit: unmeasured series 0 for the record-based bootstrap | multibench_audit/results/audit_summary.json | `json:unmeasured_mb == 0` | verified |
| 38 | Simulated-vs-closed-form bias: real calendar closed form +0.0566 | design/cf1_out.json | `json:rows.real.cf == 0.0566 +- 0.00005` | verified |
| 39 | Simulated mean fitted curvature, real calendar +0.0635 | design/cf1_out.json | `json:rows.real.sim == 0.0635 +- 0.00005` | verified |
| 40 | Closed-form check passed on the real calendar | design/cf1_out.json | `json:rows.real.pass_ == True` | verified |
| 41 | Stored-result integrity: real_v10.json | real_data/out/real_v10.json | `sha256:af18dc74a3b97694c2f7e39253d7f1845257fac41ffe400b721d8beefb8e61ae` | verified |
| 42 | Stored-result integrity: cluster_v10.json | real_data/out/cluster_v10.json | `sha256:2ac47b14a5f6086543b3f6160b4a70e3bb1d4bb192837ba3224fc6a8dfd7e780` | verified |
| 43 | Stored-result integrity: audit_per_series.json | multibench_audit/results/audit_per_series.json | `sha256:fe187c20fcd4acaf0e3b713baa5d71785b2a58041ef2788c695006c98f9579e7` | verified |
| 44 | Stored-result integrity: audit_manifest.jsonl (46,000 audit rows) | multibench_audit/results/audit_manifest.jsonl | `sha256:407bccea9f414178d5142a45974ab9c8eea2b4d0653ae81afe63fe0354d8f4f1` | verified |
| 45 | Stored-result integrity: design A3 summary | design/results_a3/summary_a3.md | `sha256:61fefe916fc06c434eb8bd1499fb2f77707bd8753718bb8033c1560761b88164` | verified |
| 46 | Stored-result integrity: design A2 summary | design/results_a2/summary_a2.md | `sha256:5a7adfb3f60133ee64fef4f4d6e2e291de9ff9336fdf709dabc5695f3731fec2` | verified |
| 47 | A2 run complete: all planned units done | design/results_a2/manifest.json | `json:runs_sha_ok == True` | verified |
