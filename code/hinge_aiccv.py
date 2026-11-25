"""Re-run of the hinge-study selection simulation (hinge_study.py) with AICc counting the residual
variance as a parameter (k = regression coefficients + 1), the standard Hurvich-Tsai convention.
Same truths, seeds and draws as hinge_study.py. Usage: python hinge_aiccv.py SCENARIO -> results/hinge_aiccv/SCENARIO.json"""
import os, sys, json
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'): os.environ[v] = '1'
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
src = open(os.path.join(HERE, 'hinge_study.py')).read().split('# ---- exact cross-check')[0]
exec(compile(src, 'hinge_study_head', 'exec'))
def aicc_v(y, kind):
    X = Xmat(kind, t); c = ols(X, y); rss = ((y - X @ c) ** 2).sum(); k = KS[kind] + 1
    return n * np.log(max(rss, 1e-300) / n) + 2 * k + 2 * k * (k + 1) / (n - k - 1)
k = sys.argv[1]; j = order.index(k)
rng = np.random.default_rng(np.random.SeedSequence([9300, j])); s = sims[k]
cnt = np.zeros(3, int); cnt_old = np.zeros(3, int)
for r in range(R):
    d = s.draw(rng); y, _, _ = fc.horizons_of(d)
    cnt[int(np.argmin([aicc_v(y, m) for m in KIND]))] += 1
    cnt_old[int(np.argmin([crit(y, m)[0] for m in KIND]))] += 1
os.makedirs(f'{ROOT}/results/hinge_aiccv', exist_ok=True)
o = dict(R=R, scenario=k, select_AICc_kplus1={m: cnt[i] / R for i, m in enumerate(KIND)}, select_AICc_coefonly_recomputed={m: cnt_old[i] / R for i, m in enumerate(KIND)},
         real_AICc_kplus1={m: float(aicc_v(h_real, m)) for m in KIND})
json.dump(o, open(f'{ROOT}/results/hinge_aiccv/{k}.json', 'w'), indent=1); print(json.dumps(o))
