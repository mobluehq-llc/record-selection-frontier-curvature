"""Verifier before generation: (a) batched fit == scipy run-level fit (metr_repro.fit) on real data; (b) cell-binomial bootstrap == run-level bootstrap in distribution; (c) negative control."""
import sys, json, time, collections, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from scipy.optimize import minimize
import fcore as fc
print('runs sha256 ok:', fc.sha256(f'{fc.DATA}/runs_v1_0.jsonl') == fc.RUNS_SHA)
D = fc.load_real()
print('models', D.M, 'tasks', D.K, 'families', D.F, 'runs', int(D.n.sum()))
def fit_ref(x, y, w, lam=0.01):
    w = w / w.sum() * len(w)
    def nll(p):
        z = p[0] + p[1] * x; return np.sum(w * (np.logaddexp(0, z) - y * z)) + 0.5 * lam * p[1] ** 2
    def g(p):
        s = 1 / (1 + np.exp(-(p[0] + p[1] * x))); r = w * (s - y); return np.array([r.sum(), (r * x).sum() + lam * p[1]])
    o = minimize(nll, [0, -0.5], jac=g, method='L-BFGS-B', bounds=[(-60, 60), (-5, -1e-3)], options=dict(ftol=1e-15, gtol=1e-10))
    return -o.x[0] / o.x[1], o.x
rows = [json.loads(l) for l in open(f'{fc.DATA}/runs_v1_0.jsonl')]
by = collections.defaultdict(list)
for r in rows:
    by[r['alias']].append(r)
h, a, b = fc.horizons_of(D)
mx = 0
for i, m in enumerate(D.names):
    q = by[m]; x = np.log2([r['human_minutes'] for r in q]); y = np.array([r['score_binarized'] for r in q], float); w = np.array([r['invsqrt_task_weight'] or 0 for r in q], float)
    hr, p = fit_ref(x, y, w)
    mx = max(mx, abs(hr - h[i]))
    if abs(hr - h[i]) > 1e-3: print('DIFF', m, hr, h[i], p, a[i], b[i])
print('max |log2h batched - scipy| over 33 models = %.2e' % mx)
# (b) bootstrap equivalence for one model, run-level vs cell-level, same 3-level scheme
rng = np.random.default_rng(1)
mname = 'o3'; im = D.names.index(mname)
q = [r for r in rows if r['alias'] == mname]
fam = collections.defaultdict(lambda: collections.defaultdict(list))
for r in q: fam[r['task_family']][r['task_id']].append(r)
# run-level bootstrap restricted to this single model's data, but families/tasks drawn from ALL (as in metr) -> use families that this model has
fl = list(fam); ref = []
for _ in range(300):
    samp = []
    for f in rng.choice(len(fl), len(fl)):
        ts = list(fam[fl[f]])
        for t in rng.choice(len(ts), len(ts)):
            rr = fam[fl[f]][ts[t]]
            for i in rng.choice(len(rr), len(rr)): samp.append(rr[i])
    x = np.log2([r['human_minutes'] for r in samp]); y = np.array([r['score_binarized'] for r in samp], float); w = np.array([r['invsqrt_task_weight'] or 0 for r in samp], float)
    ref.append(fit_ref(x, y, w)[0])
# cell-level with a one-model design
sub = fc.Design([mname], [D.dates[im]], D.x, D.fam, D.n[im:im+1], D.kk[im:im+1], D.w[im:im+1])
# families restricted to those present for this model: reindex
present = np.where(D.n[im] > 0)[0]
fm = {f: i for i, f in enumerate(sorted(set(D.fam[present])))}
sub = fc.Design([mname], [D.dates[im]], D.x[present], [fm[f] for f in D.fam[present]], D.n[im:im+1, present], D.kk[im:im+1, present], D.w[im:im+1, present])
Nb, Sb = fc.hb_weights(sub, 3000, np.random.default_rng(2))
hh, _, _ = fc.horizons_of(sub, Sb, Nb)
hh = hh[:, 0]
print('bootstrap run-level (300): mean %.3f sd %.3f | cell-level (3000): mean %.3f sd %.3f' % (np.mean(ref), np.std(ref), hh.mean(), hh.std()))
# (c) negative control: a wrong (shifted) horizon is NOT reproduced
print('negative control: perturbed data gives different horizon:', abs(fc.horizons_of(D, S=np.minimum(D.n, D.kk + 1))[0][im] - h[im]) > 0.05)
# SOTA tie-break: old (set-order dependent) vs fixed
mask = fc.sota_mask(h, D)
print('SOTA (date,name):', [D.names[i] for i in D.order if mask[i]])
t0 = time.time(); fc.hb_quad(D, 400, np.random.default_rng(0)); print('hb B=400 time %.2fs' % (time.time() - t0))
