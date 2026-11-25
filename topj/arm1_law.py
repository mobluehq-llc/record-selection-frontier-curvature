"""ARM (i): analytic sign law for record-selection curvature (F/PLAN.md TOP-JOURNAL AMENDMENT). All design choices below are frozen by the sha of this file.
Model (sigma=1 units): releases Poisson with intensity N*exp(a s + b s^2/2)/Z on s=t/T in [0,1]; y = x*s + Z, x = rT/sigma.
Registered C(x,b,N) has no 'a' argument, so the registered law uses a=0 (a is a nuisance normalisation); C_a (a fitted) is an EXPLORATORY extension reported beside it.
LAW (fluid/first-moment): a release at (s,v) is a record with exact Poisson probability exp(-A(s,v)), A=int_0^s lam(u) Phibar(v-x u)du  (earlier releases are independent of it).
Record first-moment density rho(s,v)=lam(s) phi(v-xs) exp(-A). E[beta2_rec] ~ quadratic coefficient of the rho-weighted least squares of mu(s)=E[v|record at s] on (1,u,u^2), u=s-1/2 (set-dependent design = the record density itself; NOT the CF1 marginal-probability WLS).
Grid: x 25 log-spaced [0.5,20], b 25 in [-3,3], N in {15,33,100}; 20,000 histories per cell; seeds SeedSequence([41,cell,block]) with block = batch of 2000 histories (granularity of 'rep' is the batch)."""
import sys, os, json, time, math
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import numpy as np
from scipy import stats, optimize
from scipy.integrate import cumulative_trapezoid, trapezoid
from multiprocessing import Pool
from topj_common import *

XS = np.exp(np.linspace(math.log(0.5), math.log(20), 25)); BS = np.linspace(-3, 3, 25); NS = [15, 33, 100]
REPS = 20000; BATCH = 2000


def C_law(x, b, N, a=0.0, ns=241, nv=321):
    s = np.linspace(0, 1, ns); lam = np.exp(a * s + 0.5 * b * s * s); lam = N * lam / trapezoid(lam, s)
    v = np.linspace(-6.0, max(x, 0) + 7.0, nv) if x >= 0 else np.linspace(x - 6.0, 7.0, nv)
    z = v[None, :] - x * s[:, None]
    A = cumulative_trapezoid(lam[:, None] * stats.norm.sf(z), s, axis=0, initial=0)
    rho = lam[:, None] * stats.norm.pdf(z) * np.exp(-A)
    rs = trapezoid(rho, v, axis=1); ms = trapezoid(v[None, :] * rho, v, axis=1) / np.maximum(rs, 1e-300)
    ds = np.gradient(s); om = rs * ds; u = s - 0.5
    P = np.stack([np.ones_like(u), u, u * u], 1)
    G = P.T @ (om[:, None] * P); Tm = P.T @ (om * ms)
    return float(np.linalg.solve(G, Tm)[2]), float(trapezoid(rs, s))


def quad_records(s, y, rec, tc):
    """batched OLS of y on (1,tc,tc^2) over rec-flagged points. s,y,rec: (B,L). returns beta2 (B,), valid (B,), nrec"""
    w = rec.astype(float); n = w.sum(1)
    S = [(w * tc ** k).sum(1) for k in range(5)]; T = [(w * y * tc ** k).sum(1) for k in range(3)]
    A = np.stack([np.stack([S[0], S[1], S[2]], 1), np.stack([S[1], S[2], S[3]], 1), np.stack([S[2], S[3], S[4]], 1)], 1)
    b = np.stack(T, 1); det = np.linalg.det(A); ok = (n >= 4) & (np.abs(det) > 1e-9)
    x = np.linalg.solve(np.where(ok[:, None, None], A, np.eye(3)), b[..., None])[..., 0]
    return x[:, 2], ok, n


def sim_grid_cell(args):
    cell, x, b, N = args
    sg = np.linspace(0, 1, 4001); lam = np.exp(0.5 * b * sg * sg); cum = cumulative_trapezoid(lam, sg, initial=0); cum /= cum[-1]
    vals = []; nrec = []; bad = 0
    for blk in range(REPS // BATCH):
        rng = np.random.default_rng(np.random.SeedSequence([41, cell, blk]))
        cnt = rng.poisson(N, BATCH); L = int(cnt.max()) + 1
        U = rng.random((BATCH, L)); mask = np.arange(L)[None, :] < cnt[:, None]
        s = np.where(mask, np.interp(U, cum, sg), np.inf); s.sort(1)
        mask = np.isfinite(s); s0 = np.where(mask, s, 0.0)
        y = np.where(mask, x * s0 + rng.standard_normal((BATCH, L)), -np.inf)
        cm = np.maximum.accumulate(y, 1); rec = mask.copy(); rec[:, 1:] &= y[:, 1:] > cm[:, :-1]
        y = np.where(mask, y, 0.0)
        be, ok, n = quad_records(s0, y, rec, s0 - 0.5)
        vals.append(be[ok]); nrec.append(n[ok]); bad += int((~ok).sum())
    v = np.concatenate(vals); nr = np.concatenate(nrec)
    m = float(v.mean()); se = float(v.std(ddof=1) / math.sqrt(len(v)))
    return dict(cell=cell, x=x, b=b, N=N, mean=m, se=se, nvalid=len(v), ninvalid=bad, npos=int((v > 0).sum()), mean_nrec=float(nr.mean()),
                sign='TIE' if abs(m) <= 2 * se else ('+' if m > 0 else '-'))


def sim_real_calendar(args):
    idx, name, t, c0, r, sig = args
    tc = t - t.mean(); vals = []; bad = 0
    for blk in range(REPS // BATCH):
        rng = np.random.default_rng(np.random.SeedSequence([41, 10000 + idx, blk]))
        y = c0 + r * t[None, :] + sig * rng.standard_normal((BATCH, len(t)))
        cm = np.maximum.accumulate(y, 1); rec = np.ones_like(y, bool); rec[:, 1:] = y[:, 1:] > cm[:, :-1]
        be, ok, n = quad_records(None, y, rec, np.broadcast_to(tc, y.shape))
        vals.append(be[ok]); bad += int((~ok).sum())
    v = np.concatenate(vals); m = float(v.mean()); se = float(v.std(ddof=1) / math.sqrt(len(v)))
    return dict(name=name, sim_mean=m, sim_se=se, nvalid=len(v), ninvalid=bad, sim_npos=int((v > 0).sum()), sim_sign='TIE' if abs(m) <= 2 * se else ('+' if m > 0 else '-'))


def fit_poisson_g(t):
    """profile MLE of g(s)=a s + b s^2/2 for a Poisson process observed at dates t (n fixed)."""
    s = (t - t.min()) / (t.max() - t.min()); sg = np.linspace(0, 1, 2001); n = len(s)
    def nll(p):
        a, b = p; g = lambda u: a * u + 0.5 * b * u * u
        return -(g(s).sum() - n * math.log(trapezoid(np.exp(g(sg)), sg)))
    best = None
    for st in ([0, 0], [1, 0], [-1, 0], [0, 2], [0, -2]):
        r_ = optimize.minimize(nll, st, method='BFGS')
        if best is None or r_.fun < best.fun: best = r_
    return float(best.x[0]), float(best.x[1])


def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1); hi = 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k)
    return lo, hi


def sgn(x): return '+' if x > 0 else '-'


def main():
    t0 = time.time(); NPROC = 4
    # ---- analytic law on grid (no simulation)
    Cg = np.zeros((len(NS), len(XS), len(BS)))
    for k, N in enumerate(NS):
        for i, x in enumerate(XS):
            for j, b in enumerate(BS): Cg[k, i, j] = C_law(x, b, N)[0]
    print('law grid done', time.time() - t0, flush=True)
    jobs = [((i * len(BS) + j) * len(NS) + k, float(XS[i]), float(BS[j]), N) for i in range(len(XS)) for j in range(len(BS)) for k, N in enumerate(NS)]
    with Pool(NPROC) as P: cells = P.map(sim_grid_cell, jobs, chunksize=4)
    print('sim grid done', time.time() - t0, flush=True)
    cellmap = {c['cell']: c for c in cells}
    Mg = np.zeros_like(Cg); Sg = np.zeros_like(Cg); Pg = np.zeros_like(Cg)
    for i in range(len(XS)):
        for j in range(len(BS)):
            for k in range(len(NS)):
                c = cellmap[(i * len(BS) + j) * len(NS) + k]; Mg[k, i, j] = c['mean']; Sg[k, i, j] = c['se']; Pg[k, i, j] = c['npos'] / c['nvalid']
    # ---- boundaries on the N=33 grid
    def first_cross(vec):
        for j in range(len(vec) - 1):
            if vec[j] == 0: return float(BS[j])
            if vec[j] * vec[j + 1] < 0: return float(BS[j] + (BS[j + 1] - BS[j]) * vec[j] / (vec[j] - vec[j + 1]))
        return None
    step = BS[1] - BS[0]; cols = []; agree = 0; k33 = NS.index(33)
    for i in range(len(XS)):
        ba = first_cross(Cg[k33, i]); bs = first_cross(Mg[k33, i])
        if ba is None and bs is None: ok = np.sign(Cg[k33, i, 0]) == np.sign(Mg[k33, i, 0])
        elif ba is None or bs is None: ok = False
        else: ok = abs(ba - bs) <= step + 1e-9
        agree += int(ok); cols.append(dict(x=float(XS[i]), b_analytic=ba, b_sim=bs, agree=bool(ok)))
    frac_cols = agree / len(XS)
    # ---- placement
    series = [metr('1.0'), metr('1.1')] + epoch_all(); place = []; jobs2 = []
    for idx, s in enumerate(series):
        t, y = s['t'], s['y']; n = len(y); T = float(t.max() - t.min())
        A = np.stack([np.ones(n), t], 1); coef = np.linalg.lstsq(A, y, rcond=None)[0]; res = y - A @ coef; sig = float(math.sqrt((res ** 2).sum() / (n - 2)))
        r = float(coef[1]); x = r * T / sig; a_fit, b_fit = fit_poisson_g(t)
        Cp, _ = C_law(x, b_fit, n); Ca, _ = C_law(x, b_fit, n, a=a_fit)
        place.append(dict(name=s['name'], kind=s['kind'], n=n, T=T, r=r, sigma=sig, x=x, b=b_fit, a_fit=a_fit, C=Cp, C_a=Ca, pred=sgn(Cp), pred_a=sgn(Ca)))
        jobs2.append((idx, s['name'], t, float(coef[0]), r, sig))
    with Pool(NPROC) as P: sims = P.map(sim_real_calendar, jobs2)
    for p, sm in zip(place, sims): p.update(sm)
    nonTie = [p for p in place if p['sim_sign'] != 'TIE']
    dis = [p['name'] for p in nonTie if p['pred'] != p['sim_sign']]
    dis_a = [p['name'] for p in nonTie if p['pred_a'] != p['sim_sign']]
    agree_frac = 1 - len(dis) / len(nonTie) if nonTie else float('nan')
    agree_frac_a = 1 - len(dis_a) / len(nonTie) if nonTie else float('nan')
    # falsifier (3): nearest grid cell, CP lower limit of the opposite-sign proportion > 0.90
    conf = []
    for p in place:
        i = int(np.argmin(abs(np.log(XS) - math.log(max(p['x'], 1e-3))))); j = int(np.argmin(abs(BS - p['b']))); k = int(np.argmin(abs(np.log(NS) - math.log(p['n']))))
        c = cellmap[(i * len(BS) + j) * len(NS) + k]; opp = (c['nvalid'] - c['npos']) if p['pred'] == '+' else c['npos']
        lo_, _ = cp(opp, c['nvalid']); p['grid_cell'] = dict(x=float(XS[i]), b=float(BS[j]), N=NS[k], opp_frac=opp / c['nvalid'], cp_lo=lo_)
        if lo_ > 0.90: conf.append(p['name'])
    cond1 = agree_frac >= 0.80; cond2 = frac_cols >= 0.80
    verdict = 'MET' if (cond1 and cond2) else 'FAILS'
    if len(conf) or not cond1 or not cond2: verdict = 'FAILS' if not (cond1 and cond2) else 'MET (but see confident contradictions)'
    out = dict(label='CONFIRMATORY (pre-registered, F/PLAN.md TOP-JOURNAL AMENDMENT arm i)', verdict=verdict, sign_agreement=agree_frac, n_nonTIE=len(nonTie), n_placed=len(place),
               disagreements=dis, sign_agreement_exploratory_C_a=agree_frac_a, disagreements_C_a=dis_a, boundary_columns_agree=frac_cols, boundary_columns=cols,
               confident_contradictions=conf, placement=place, runtime_s=time.time() - t0, grid_cells_TIE=int(sum(c['sign'] == 'TIE' for c in cells)),
               grid_sign_agreement_all_N=float(np.mean([np.sign(Cg[k, i, j]) == np.sign(Mg[k, i, j]) for k in range(3) for i in range(25) for j in range(25) if abs(Mg[k, i, j]) > 2 * Sg[k, i, j]])),
               grid_sign_agreement_by_N={str(N): float(np.mean([np.sign(Cg[k, i, j]) == np.sign(Mg[k, i, j]) for i in range(25) for j in range(25) if abs(Mg[k, i, j]) > 2 * Sg[k, i, j]])) for k, N in enumerate(NS)})
    json.dump(out, open(OUT + '/arm1_results.json', 'w'), indent=1, default=float)
    np.savez(OUT + '/arm1_grid.npz', C=Cg, mean=Mg, se=Sg, ppos=Pg, XS=XS, BS=BS)
    print(json.dumps({k: v for k, v in out.items() if k not in ('placement', 'boundary_columns')}, indent=1, default=float))
    for p in place: print(p['name'], 'n', p['n'], 'x %.2f b %.2f' % (p['x'], p['b']), 'pred', p['pred'], 'sim', p['sim_sign'], '%.3g+-%.2g' % (p['sim_mean'], p['sim_se']))


if __name__ == '__main__':
    main()
