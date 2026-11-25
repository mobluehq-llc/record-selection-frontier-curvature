"""F Amendment CS1: size of the developer-clustered curvature tests (PLAN.md 'AMENDMENT CS1'). Imports (does not modify) real_data/cluster_test.py and design/ code.
Usage: python cluster_size.py [reps=4000] [workers=3]"""
import os, sys, json, time, multiprocessing as mp
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS'): os.environ[v] = '1'
import numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'design')); sys.path.insert(0, HERE)
import fcore as fc, fdesign3 as f3, cluster_test as ct
DATA = fc.DATA; P = json.load(open(os.path.join(ROOT, 'results', 'F_simulator_validation.json')))['params']
D0 = fc.load_real(); h0, _, b0 = fc.horizons_of(D0)
assert fc.sha256(f'{DATA}/runs_v1_0.jsonl') == fc.RUNS_SHA
CL = [ct.DEV[n] for n in D0.names]                      # asserts all 33 names are in the frozen CL1.1 map
assert D0.M == 33 and sorted(set(CL)) == sorted(set(ct.DEV.values())) and len(set(CL)) == 7
SIZES = {g: CL.count(g) for g in sorted(set(CL))}; assert sorted(SIZES.values()) == [1, 1, 1, 2, 4, 9, 15], SIZES
GI = np.array([sorted(set(CL)).index(c) for c in CL]); G = 7
R = ct.CR2(D0.t, CL); B = 999; PATS = np.array(np.meshgrid(*[[-1.0, 1.0]] * G, indexing='ij')).reshape(G, -1).T
CELLS = [('R_null_val', dict(truth='exp')), ('MF1_null_val', dict(truth='exp', smf=1.0)), ('N50_null_val', dict(truth='exp', noise=0.5)), ('LAD0_gauss', dict(truth='exp', gauss=True)),
         ('DEV_rho0.3', dict(truth='exp', dev_rho=0.3)), ('DEV_rho0.6', dict(truth='exp', dev_rho=0.6))]

class SimDev(f3.Sim3):
    def generate(self, rng):
        rho = self.cfg['dev_rho']; D = self.D
        u = rng.normal(size=G)[GI]; e = rng.normal(size=D.M)
        L = self.true_L(D.t) + self.sm * (np.sqrt(rho) * u + np.sqrt(1 - rho) * e)
        F = rng.normal(size=D.F); g = rng.normal(size=D.K)
        j = self.sj * (np.sqrt(self.phi) * F[D.fam] + np.sqrt(1 - self.phi) * g)
        z = self.b[:, None] * (D.x[None, :] + j[None, :] - L[:, None]); p = fc._sig(z)
        kk = rng.binomial(D.n.astype(np.int64), p).astype(float)
        d = fc.Design(D.names, D.dates, D.x, D.fam, D.n, kk, D.w); h, _, _ = fc.horizons_of(d); return d, self.obs(h)
SIMS = {nm: (SimDev if 'dev_rho' in c else f3.Sim3)(D0, b0, P, c) for nm, c in CELLS}

def work(u):
    ci, rep = u; nm = CELLS[ci][0]
    s1, s2 = np.random.SeedSequence([5301, ci, rep]).spawn(2)
    _, y = SIMS[nm].generate(np.random.default_rng(s1)); y = np.asarray(y, float)
    b2, t = R.stat(y); b2, t = float(b2), float(t)
    pcr = float(stats.t.sf(t, R.df)); pcr_dn = float(stats.t.cdf(t, R.df))
    y0 = R.H0 @ y; e0 = y - y0; w = np.random.default_rng(s2).choice(ct.WEBB, size=(B, G)); _, ts = R.stat(y0[None] + e0[None] * w[:, GI])
    pw = float((1 + (ts >= t).sum()) / (B + 1)); pw_dn = float((1 + (ts <= t).sum()) / (B + 1))
    _, tr = R.stat(y0[None] + e0[None] * PATS[:, GI]); pr = float((tr >= t - 1e-12).sum() / len(PATS)); pr_dn = float((tr <= t + 1e-12).sum() / len(PATS))
    return ci, rep, dict(b2=b2, t=t, cr2_up=pcr, cr2_dn=pcr_dn, webb_up=pw, webb_dn=pw_dn, rad_up=pr, rad_dn=pr_dn)

def cp(k, n, a=0.05): return (0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1), 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k))
def verdict(lo, hi): return 'VALID' if lo >= .035 and hi <= .065 else 'CONSERVATIVE' if hi < .035 else 'ANTI-CONSERVATIVE' if lo > .065 else 'INCONCLUSIVE'

if __name__ == '__main__':
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 4000; nw = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    if '--smoke' in sys.argv: reps = 40
    t0 = time.time(); rows = {nm: [] for nm, _ in CELLS}
    jobs = [(ci, r) for ci in range(len(CELLS)) for r in range(reps)]
    with mp.Pool(nw) as pool:
        for i, (ci, rep, o) in enumerate(pool.imap_unordered(work, jobs, chunksize=20)):
            rows[CELLS[ci][0]].append(o)
            if i % 2000 == 0: print(i, len(jobs), '%.0fs' % (time.time() - t0), flush=True)
    res = dict(amendment='CS1', reps=reps, B_webb=B, cr2_df=R.df, cluster_sizes=SIZES, numpy=np.__version__, scipy=__import__('scipy').__version__, runtime_s=time.time() - t0, cells={})
    for nm, rs in rows.items():
        n = len(rs); c = dict(n=n, mean_b2=float(np.mean([r['b2'] for r in rs])), tests={})
        for tname in ('cr2', 'webb', 'rad'):
            pu = np.array([r[tname + '_up'] for r in rs]); pd_ = np.array([r[tname + '_dn'] for r in rs])
            k = int((pu < .05).sum()); lo, hi = cp(k, n); k2 = int(((pu < .025) | (pd_ < .025)).sum()); kd = int((pd_ < .05).sum()); l2, h2 = cp(k2, n); ld, hd = cp(kd, n)
            c['tests'][tname] = dict(k_up=k, rate_up=k / n, cp_up=[lo, hi], verdict=verdict(lo, hi), k_two=k2, rate_two=k2 / n, cp_two=[l2, h2], k_dn=kd, rate_dn=kd / n, cp_dn=[ld, hd], min_p=float(pu.min()))
        res['cells'][nm] = c
    out = os.path.join(HERE, 'out', 'cluster_size_smoke.json' if '--smoke' in sys.argv else 'cluster_size_v1.json')
    json.dump(res, open(out, 'w'), indent=1, default=float); print(json.dumps({k: {t: (v['rate_up'], v['verdict']) for t, v in c['tests'].items()} for k, c in res['cells'].items()}, indent=1)); print('%.0fs' % res['runtime_s'])
