"""Corrective amendment 2: one-sided upward re-score of the multi-benchmark audit. Imports audit_core UNMODIFIED.
Reproduces run_one's RNG stream exactly; extra output = 5th and 95th percentiles. Reproduction gate vs stored 2.5/97.5."""
import sys, os, json
import numpy as np, pandas as pd
import audit_core as ac, audit_run as ar

def pct(idx, y, u, span, M, qs):
    ye = np.append(y, -1e9); ue = np.append(u, 0.0); Y = ye[idx]; U = ue[idx]
    cm = np.maximum.accumulate(Y, axis=1); rec = np.ones_like(Y, bool); rec[:, 1:] = Y[:, 1:] > cm[:, :-1]; rec &= (idx < M)
    c, ok = ac.quad_coef_batch(U, np.where(rec, Y, 0.0), rec.astype(float)); valid = ok & (rec.sum(1) >= 5)
    if valid.sum() < 20: return None
    return np.percentile(c[valid], qs) / span ** 2

def work(args):
    s, cname = args
    d = ar.get_frame(s); cidx = ac.CONSTR.index(cname); sd = float(d.y.std()); span = float(d.t.max() - d.t.min())
    codes_all = pd.factorize(d.o.values)[0]; out = []
    for rep in range(1000):
        t, order = ac.permuted_frame(d, rep, s['index']); y0 = d.y.values[order]; codes = codes_all[order]
        y, c = ac.planted(t, y0, cname, sd, span); M = len(y); u = (t - t[0]) / span
        rng = np.random.default_rng(np.random.SeedSequence([ac.BASE_SEED, s['index'], rep, cidx, 1]))
        idx, _ = ac._boot_idx_models(M, rng); p = pct(idx, y, u, span, M, [2.5, 5, 95, 97.5])
        r = dict(rep=rep, mb=None if p is None else [float(x) for x in p], cl=None)
        if len(np.unique(codes)) >= ac.MIN_ORGS:
            idx, _ = ac._boot_idx_clustered(codes, rng); q = pct(idx, y, u, span, M, [2.5, 5, 95, 97.5])
            r['cl'] = None if q is None else [float(x) for x in q]
        out.append(r)
    return dict(series=s['index'], construction=cname, rows=out)

if __name__ == '__main__':
    from multiprocessing import Pool
    S = json.load(open(ar.SERIES_JSON)); series = S['eligible'] + [S['reference']]
    dst = ar.RES + '/audit_onesided_raw.jsonl'
    if os.path.exists(dst): sys.exit('refusing to overwrite ' + dst)
    tasks = [(s, c) for s in series for c in ('N0', 'P1')]
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as p, open(dst, 'w') as f:
        for k, r in enumerate(p.imap_unordered(work, tasks)):
            f.write(json.dumps(r) + '\n'); f.flush(); print(k, len(tasks), flush=True)
