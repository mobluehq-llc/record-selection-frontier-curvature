"""EXPLORATORY (NOT pre-registered; added 2026-11-23 for paper v2 after an outside review asked for it).
Type M (exaggeration) summary from the stored Amendment-3 replicates: for each quadratic alternative at the real design, the mean
curvature estimate among replicates in which a test rejects upward at the nominal 5% (p_up < 0.05), divided by the true curvature.
Reads results/cells/<cell>/c*.jsonl (read-only), prints one JSON object on stdout.  No Amendment-2 statistic is read: the HC3 gate of
the real-data reading rule is NOT applied here, so the joint rule's exaggeration is still open.
Usage (on the machine holding the A3 cells): python3 analyze_typem.py results > typem_exploratory.json"""
import sys, os, json, glob
import numpy as np
RD = sys.argv[1]; RATE = 1.7392857142857143; SPAN = 6.776180698151951   # params.rate_null, real span (asserted by the caller against the result files)
CELLS = {'R_null_val': 1.0, 'R_rr1.25': 1.25, 'R_rr1.5': 1.5, 'R_rr2': 2.0, 'R_rr3': 3.0, 'R_rr4': 4.0}
out = dict(what='EXPLORATORY Type M summary from stored A3 replicates; nominal cut-off p_up < 0.05', rate=RATE, span=SPAN, cells={})
for nm, rr in CELLS.items():
    rows = []
    for fp in sorted(glob.glob(os.path.join(RD, 'cells', nm, 'c*.jsonl'))):
        for ln in open(fp):
            if ln.strip(): rows.append(json.loads(ln))
    g = lambda k: np.array([r.get(k, np.nan) if r.get(k) is not None else np.nan for r in rows], float)
    truth = RATE * (rr - 1.0) / ((1.0 + rr) * SPAN); call = g('c_all'); c = dict(n=len(rows), rr=rr, true_beta2=truth, mean_c_all=float(np.nanmean(call)), tests={})
    for t in ('audit', 'heck', 'sota'):
        est = g(t + '_c'); pu = g(t + '_pup'); ok = ~np.isnan(pu) & ~np.isnan(est); rej = ok & (pu < 0.05); k = int(rej.sum())
        d = dict(n_valid=int(ok.sum()), n_reject=k, mean_est_all=float(est[ok].mean()))
        if k >= 30:
            d.update(mean_est_given_reject=float(est[rej].mean()), median_est_given_reject=float(np.median(est[rej])), q05_est_given_reject=float(np.quantile(est[rej], .05)),
                     q95_est_given_reject=float(np.quantile(est[rej], .95)), mean_c_all_given_reject=float(call[rej].mean()), frac_negative_given_reject=float((est[rej] < 0).mean()))
            if truth > 0: d.update(exaggeration_own=float(est[rej].mean() / truth), exaggeration_c_all=float(call[rej].mean() / truth))
        c['tests'][t] = d
    out['cells'][nm] = c
json.dump(out, sys.stdout, indent=1)
