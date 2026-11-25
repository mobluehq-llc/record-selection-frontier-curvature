"""EXPLORATORY T-v: Vuong (BIC-corrected) exponential [log2h linear in t] vs logistic-in-h [log2h = A - log2(1+exp(-k(t-t0)))], Gaussian errors, SOTA points.
Reject exponential in favour of logistic if Z < -1.96. Applied to the real data and the saved null horizons."""
import sys, json, numpy as np, datetime as dt
from scipy.optimize import least_squares
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import fcore as fc
R = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/results'
def vuong(t, y):
    n = len(y); A = np.stack([np.ones(n), t], 1); c = np.linalg.lstsq(A, y, rcond=None)[0]; r1 = y - A @ c
    best = None
    for k0 in (0.3, 1.0, 3.0):
        for t00 in (t.mean(), t.max(), t.max() + 2):
            try:
                f = lambda p: y - (p[0] - np.logaddexp(0, -p[1] * (t - p[2]))) / np.log(2) * 1.0
                # work in log2 units: A - log2(1+exp(-k(t-t0))) ; logaddexp is natural log
                f = lambda p: y - (p[0] - np.logaddexp(0, -p[1] * (t - p[2])) / np.log(2))
                o = least_squares(f, [y.max() + 2, k0, t00], bounds=([-50, 1e-3, -20], [200, 20, 60]))
                if best is None or o.cost < best.cost: best = o
            except Exception: pass
    r2 = best.fun
    s1, s2 = (r1 ** 2).mean(), (r2 ** 2).mean()
    l1 = -0.5 * np.log(2 * np.pi * s1) - r1 ** 2 / (2 * s1); l2 = -0.5 * np.log(2 * np.pi * s2) - r2 ** 2 / (2 * s2)
    d = l1 - l2; LR = d.sum() - (2 - 3) / 2 * np.log(n)      # BIC correction: (p1-p2)/2 log n
    w = d.std(ddof=1)
    return LR / (w * np.sqrt(n)) if w > 1e-12 else np.nan
D = fc.load_real(cutoff=dt.date(2025, 11, 30)); h, _, _ = fc.horizons_of(D)
m = fc.sota_mask(h, D); zr = vuong(D.t[m], h[m])
H = np.load(f'{R}/null_horizons.npy'); Z = []
for hh in H:
    mm = fc.sota_mask(hh, D)
    if mm.sum() >= 5: Z.append(vuong(D.t[mm], hh[mm]))
Z = np.array(Z); Z = Z[~np.isnan(Z)]; k = int((Z < -1.96).sum()); lo, hi = fc.cp(k, len(Z))
out = dict(real_Z=float(zr), real_reject_exp_for_logistic=bool(zr < -1.96), null_n=len(Z), null_rej=k, null_size=k / len(Z), null_cp=[lo, hi], null_Z_median=float(np.median(Z)))
json.dump(out, open(f'{R}/F_vuong_exploratory.json', 'w'), indent=1); print(out)
