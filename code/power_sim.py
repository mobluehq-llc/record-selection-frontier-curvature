"""Bar (3): power vs number of models N in (12,20,40) and task multiplier (1,2,4), alternative = doubling time halves over the window
(instantaneous rate rises linearly x2, mean rate == null rate). Also an anchor cell = the real 33-model design. Seeds SeedSequence([34, cell, rep]).
Usage: python -I power_sim.py truth(quad|exp) reps workers outname"""
import os
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS'): os.environ[v] = '1'
import sys, json, time, csv, datetime as dt, numpy as np, multiprocessing as mp
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import fcore as fc, fsim
R = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/results'
P = json.load(open(f'{R}/F_simulator_validation.json'))['params']
D0 = fc.load_real(); h0, _, b0 = fc.horizons_of(D0)
d_start, d_end = dt.date(2019, 2, 14), dt.date(2025, 11, 24)
CELLS = [(0, 33, 1)] + [(1 + 3 * i + j, N, m) for i, N in enumerate((12, 20, 40)) for j, m in enumerate((1, 2, 4))]
def design(cell):
    cid, N, mult = cell
    if cid == 0: return D0, b0
    rng = np.random.default_rng(np.random.SeedSequence([34, 999, cid]))
    tm = rng.integers(0, D0.M, N)
    days = np.linspace(0, (d_end - d_start).days, N).round().astype(int)
    dates = [d_start + dt.timedelta(days=int(x)) for x in days]
    n = np.tile(D0.n[tm], (1, mult)); w = np.tile(D0.w[tm], (1, mult)); x = np.tile(D0.x, mult)
    fam = np.concatenate([D0.fam + D0.F * c for c in range(mult)])
    return fc.Design([f'm{i:02d}' for i in range(N)], dates, x, fam, n, np.zeros_like(n), w), b0[tm]
_cache = {}
def work(args):
    cid, rep, truth = args
    cell = CELLS[cid]
    if cid not in _cache:
        D, b = design(cell); _cache[cid] = (D, fsim.NullSim(D, b, P['a0'], P['sigma_m'], P['sigma_j'], P['phi'], truth=truth, rate_ratio=2.0))
    D, sim = _cache[cid]
    ss = np.random.SeedSequence([34, cid, rep]); s1, s2 = ss.spawn(2)
    d = sim.draw(np.random.default_rng(s1)); h, _, _ = fc.horizons_of(d)
    ti = fc.t_iid(d, h); tb = fc.t_hb(d, 400, np.random.default_rng(s2), h0=h)
    return dict(cell=cid, N=cell[1], mult=cell[2], rep=rep, p_iid=ti['p'], nS=ti['nS'], iid_rej=bool(ti['p'] < 0.05), hb_rej=tb['reject'], hb_rej_up=tb.get('rej_up', False), hb_lo=tb['lo'], hb_hi=tb['hi'], hb_nvalid=tb['nvalid'], coef=ti['coef'])
if __name__ == '__main__':
    truth, reps, nw, name = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    jobs = [(c[0], r, truth) for r in range(reps) for c in CELLS]
    t0 = time.time(); out = []
    with mp.Pool(nw) as pool:
        for i, r in enumerate(pool.imap_unordered(work, jobs, chunksize=1)):
            out.append(r)
            if i % 100 == 0: print(i, len(jobs), '%.0fs' % (time.time() - t0), flush=True)
    out.sort(key=lambda r: (r['cell'], r['rep']))
    with open(f'{R}/{name}', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(list(out[0])); [w.writerow(list(r.values())) for r in out]
    print('done %.0fs' % (time.time() - t0))
