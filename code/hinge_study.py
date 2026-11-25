"""Study H1 (design/PREREG_HINGE.md). Usage: python3 hinge_study.py"""
import os, sys, json, datetime as dt
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'): os.environ[v] = '1'
import numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'design')); sys.path.insert(0, os.path.join(ROOT, 'real_data'))
import fcore as fc, fdesign
R = 10000
P = json.load(open(f'{ROOT}/results/F_simulator_validation.json'))['params']
D = fc.load_real(cutoff=dt.date(2025, 11, 30)); h_real, _, b_model = fc.horizons_of(D)
assert D.M == 33
t = D.t; T = (dt.date(2024, 9, 12) - fc.EPOCH).days / 365.25; n = len(t)
mon = np.array([d.year * 12 + d.month for d in D.dates])

def Xmat(kind, t):
    one = np.ones_like(t); post = (t >= T).astype(float); hp = np.maximum(t - T, 0)
    tc = t - 4.0
    return {'L': np.stack([one, tc], 1), 'Q': np.stack([one, tc, tc * tc], 1), 'H': np.stack([one, tc, post, hp], 1),
            'QH': np.stack([one, tc, tc * tc, post, hp], 1)}[kind]
KS = {'L': 2, 'Q': 3, 'H': 4}
def ols(X, y): return np.linalg.lstsq(X, y, rcond=None)[0]
def crit(y, kind):
    X = Xmat(kind, t); c = ols(X, y); rss = ((y - X @ c) ** 2).sum(); k = KS[kind]
    ll = n * np.log(max(rss, 1e-300) / n)
    return ll + 2 * k + 2 * k * (k + 1) / (n - k - 1), ll + k * np.log(n), rss
def lomo(y, kind):
    X = Xmat(kind, t); se = 0.0
    for m in np.unique(mon):
        te = mon == m; c = ols(X[~te], y[~te]); se += ((y[te] - X[te] @ c) ** 2).sum()
    return se / n
KIND = ['L', 'Q', 'H']

# ---- truths
cL, cQ, cH = [ols(Xmat(k, t), h_real) for k in KIND]
def curve(kind, c): return lambda tt: Xmat(kind, tt) @ c
sL = cL[1]; vT = cL[0] + sL * (T - 4.0)
pc_h = lambda tt: np.where(tt < T, vT + sL * (tt - T), vT + 4 * sL * (tt - T))
truths = {'T_L': curve('L', cL), 'T_Q': curve('Q', cQ), 'T_H': curve('H', cH), 'PC_H': pc_h}
class SimC(fdesign.Sim):
    def __init__(self, f, cfg): super().__init__(D, b_model, P, cfg); self.f = f
    def true_L(self, tt): return self.f(tt) if self.f is not None else super().true_L(tt)
sims = {k: SimC(f, {}) for k, f in truths.items()}
sims['PC_Q'] = SimC(None, {'truth': 'quad', 'rr': 4.0})
order = ['T_L', 'T_Q', 'T_H', 'PC_H', 'PC_Q']
out = {'T_unix_years': T, 'n_post_break_models': int((t >= T).sum()), 'truth_coefs': {'L': cL.tolist(), 'Q': cQ.tolist(), 'H': cH.tolist()}, 'pc_h_post_slope': 4 * sL, 'sim': {}}

# ---- exact cross-check (noise = 0)
xc = {}
for k, ct, kind in [('T_L', cL, 'L'), ('T_Q', cQ, 'Q'), ('T_H', cH, 'H')]:
    y = truths[k](t); a = [crit(y, m)[0] for m in KIND]; sel = KIND[int(np.argmin(a))]
    err = np.abs(ols(Xmat(kind, t), y) - ct).max(); xc[k] = dict(selected=sel, expected=kind, max_coef_err=float(err))
    assert sel == kind and err < 1e-9, (k, sel, err)
out['exact_crosscheck'] = xc

# ---- simulation
def classify(y):
    A = np.array([crit(y, k)[:2] for k in KIND]); cv = np.array([lomo(y, k) for k in KIND])
    return int(np.argmin(A[:, 0])), int(np.argmin(A[:, 1])), int(np.argmin(cv)), cv
for j, k in enumerate(order):
    rng = np.random.default_rng(np.random.SeedSequence([9300, j])); s = sims[k]
    cnt = np.zeros((3, 3), int); cvs = np.zeros(3); pair = np.zeros(2, int)  # rows: AICc,BIC,CV ; cols: L,Q,H
    for r in range(R):
        d = s.draw(rng); y, _, _ = fc.horizons_of(d)
        a, b_, c_, cv = classify(y); cnt[0, a] += 1; cnt[1, b_] += 1; cnt[2, c_] += 1; cvs += cv
        AH, AQ = crit(y, 'H')[0], crit(y, 'Q')[0]; pair[0 if AH < AQ else 1] += 1
    out['sim'][k] = dict(R=R, select_AICc={m: cnt[0, i] / R for i, m in enumerate(KIND)}, select_BIC={m: cnt[1, i] / R for i, m in enumerate(KIND)},
                         select_LOMO={m: cnt[2, i] / R for i, m in enumerate(KIND)}, mean_heldout_mse={m: float(cvs[i] / R) for i, m in enumerate(KIND)},
                         pairwise_H_vs_Q_AICc=dict(H=pair[0] / R, Q=pair[1] / R))
    print(k, out['sim'][k], flush=True)

# ---- real series
y = h_real
out['real_fit'] = {m: dict(AICc=crit(y, m)[0], BIC=crit(y, m)[1], RSS=crit(y, m)[2], LOMO_mse=lomo(y, m), coef=ols(Xmat(m, t), y).tolist()) for m in KIND}
out['real_fit']['QH'] = dict(coef=ols(Xmat('QH', t), y).tolist(), RSS=float(((y - Xmat('QH', t) @ ols(Xmat('QH', t), y)) ** 2).sum()))
from cluster_test import DEV, WEBB, inv_sqrt
names = D.names; cl = np.array([DEV[nm] for nm in names]); gl = sorted(set(cl)); gi = np.array([gl.index(c) for c in cl]); G = len(gl)
out['clusters'] = {g: int((cl == g).sum()) for g in gl}
def cr_setup(X):
    B = np.linalg.inv(X.T @ X); H = X @ B @ X.T; M = np.eye(n) - H; A = []; flag = []
    for g in range(G):
        idx = np.where(gi == g)[0]; Mg = M[np.ix_(idx, idx)]; w = np.linalg.eigvalsh(Mg)
        if w.min() < 1e-8: A.append(np.eye(len(idx))); flag.append(gl[g])
        else: A.append(inv_sqrt(Mg))
    return B, M, A, flag
def cr_cov(X, e, B, A):
    S = np.zeros((X.shape[1], X.shape[1]))
    for g in range(G):
        idx = np.where(gi == g)[0]; s = X[idx].T @ (A[g] @ e[idx]); S += np.outer(s, s)
    return B @ S @ B
def webb_test(Xfull, cols, rng, Bn=99999):
    """test coefficients `cols`=0. Statistic: single col -> CR2 t ; multiple -> Wald with CR2 covariance. Null-restricted Webb wild cluster bootstrap."""
    keep = [i for i in range(Xfull.shape[1]) if i not in cols]; Xr = Xfull[:, keep]
    Bm, M, A, flag = cr_setup(Xfull)
    def stat(yv):
        c = np.linalg.lstsq(Xfull, yv, rcond=None)[0]; e = yv - Xfull @ c; V = cr_cov(Xfull, e, Bm, A); cc = c[cols]; Vc = V[np.ix_(cols, cols)]
        return (cc[0] / np.sqrt(Vc[0, 0]) if len(cols) == 1 else float(cc @ np.linalg.solve(Vc, cc))), c
    obs, cfull = stat(y); cr = np.linalg.lstsq(Xr, y, rcond=None)[0]; y0 = Xr @ cr; e0 = y - y0
    Pf = Xfull @ Bm @ Xfull.T @ np.eye(n)  # hat
    W = rng.choice(WEBB, size=(Bn, G)); ys = y0[None] + e0[None] * W[:, gi]
    # vectorised statistic
    C = ys @ (Bm @ Xfull.T).T; E = ys - C @ Xfull.T
    Sg = np.zeros((Bn, G, Xfull.shape[1]))
    for g in range(G):
        idx = np.where(gi == g)[0]; Eg = E[:, idx] @ A[g].T; Sg[:, g, :] = Eg @ Xfull[idx]
    # V = Bm (sum_g s s') Bm ; only need cols
    BmC = Bm[cols]; U = Sg @ BmC.T   # (Bn,G,len(cols)) = rows of c-part of B s_g
    Vc = np.einsum('bgi,bgj->bij', U, U); cc = C[:, cols]
    if len(cols) == 1: ts = cc[:, 0] / np.sqrt(Vc[:, 0, 0])
    else: ts = np.einsum('bi,bi->b', cc, np.linalg.solve(Vc, cc[..., None])[..., 0])
    res = dict(coef=[float(v) for v in cfull[cols]], stat=float(obs), cr2_flagged_clusters=flag)
    if len(cols) == 1:
        res.update(p_two=float((1 + (np.abs(ts) >= abs(obs)).sum()) / (Bn + 1)), p_up=float((1 + (ts >= obs).sum()) / (Bn + 1)))
    else: res.update(p=float((1 + (ts >= obs).sum()) / (Bn + 1)))
    return res
rng = np.random.default_rng(np.random.SeedSequence([9300, 100]))
Xq, Xh, Xqh = Xmat('Q', t), Xmat('H', t), Xmat('QH', t)
tests = {}
tests['Q_c'] = webb_test(Xq, [2], rng)
assert abs(tests['Q_c']['coef'][0] - 0.13847089577971783) < 1e-9, tests['Q_c']
assert abs(tests['Q_c']['p_up'] - 0.094) < 0.004, tests['Q_c']        # instrument check vs CL1 Webb 0.09418
tests['H_g'] = webb_test(Xh, [3], rng); tests['H_d'] = webb_test(Xh, [2], rng); tests['H_dg_joint'] = webb_test(Xh, [2, 3], rng)
tests['QH_c'] = webb_test(Xqh, [2], rng); tests['QH_dg_joint'] = webb_test(Xqh, [3, 4], rng)
tests['QH_g'] = webb_test(Xqh, [4], rng); tests['QH_d'] = webb_test(Xqh, [3], rng)
out['real_tests'] = tests
out['c_ratio_QH_over_Q'] = tests['QH_c']['coef'][0] / tests['Q_c']['coef'][0]
json.dump(out, open(f'{ROOT}/results/F_hinge.json', 'w'), indent=1, default=float)
print(json.dumps({k: out[k] for k in ['real_fit', 'real_tests', 'c_ratio_QH_over_Q', 'exact_crosscheck']}, indent=1, default=float))
