"""Bars (1)-(2): size of T-iid and T-hb under the calibrated exponential null. 1000 datasets, seeds SeedSequence([33, rep]); B=400.
Usage: python -I size_sim.py [reps=1000] [workers=4]"""
import os
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS'): os.environ[v] = '1'
import sys, json, time, numpy as np, multiprocessing as mp
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import fcore as fc, fsim
R = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/results'
P = json.load(open(f'{R}/F_simulator_validation.json'))['params']
D = fc.load_real(); h0, a0_, b0 = fc.horizons_of(D)
SIM = fsim.NullSim(D, b0, P['a0'], P['sigma_m'], P['sigma_j'], P['phi'])
def work(rep):
    ss = np.random.SeedSequence([33, rep]); s_sim, s_bs = ss.spawn(2)
    d = SIM.draw(np.random.default_rng(s_sim)); h, _, _ = fc.horizons_of(d)
    ti = fc.t_iid(d, h); tb = fc.t_hb(d, 400, np.random.default_rng(s_bs), h0=h)
    allm = fc.t_iid(d, h, mask=np.ones(d.M, bool))
    return dict(rep=rep, p_iid=ti['p'], coef=ti['coef'], nS=ti['nS'], p_iid_all=allm['p'], hb_lo=tb['lo'], hb_hi=tb['hi'], hb_rej=tb['reject'], hb_nvalid=tb['nvalid'],
                hb_rej_up=tb.get('rej_up', False), hb_lo_all=tb['lo_all'], hb_hi_all=tb['hi_all'], hb_rej_all=tb['reject_all'], h=h.tolist())
if __name__ == '__main__':
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 1000; nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    t0 = time.time(); out = []
    with mp.Pool(nw) as pool:
        for i, r in enumerate(pool.imap_unordered(work, range(reps), chunksize=2)):
            out.append(r)
            if i % 50 == 0: print(i, '%.0fs' % (time.time() - t0), flush=True)
    out.sort(key=lambda r: r['rep'])
    import csv
    keys = [k for k in out[0] if k != 'h']
    with open(f'{R}/F_size.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(keys); [w.writerow([r[k] for k in keys]) for r in out]
    np.save(f'{R}/null_horizons.npy', np.array([r['h'] for r in out]))
    print('done %.0fs' % (time.time() - t0))
