"""Split-task replication (PREREG_SPLIT_TASK.md). Run: python3 split_task.py [real|controls|boot|all]"""
import sys, types, json, numpy as np
try:
    import scipy  # noqa
except ImportError:
    sc = types.ModuleType('scipy'); sc.stats = types.ModuleType('scipy.stats'); sys.modules['scipy'] = sc; sys.modules['scipy.stats'] = sc.stats; sc.__dict__['stats'] = sc.stats
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import fcore as fc
ROOT = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
H = ROOT + '/holdout_data'; R = ROOT + '/results/split_task'
D = fc.load_real(runs_path=f'{H}/runs_v1_1.jsonl', dates_path=f'{H}/release_dates_main.yaml')
M, K, F = D.M, D.K, D.F
def dev_of(n):
    n = n.lower()
    if n.startswith('claude'): return 0
    if n.startswith('gemini'): return 2
    return 1
DEV = np.array([dev_of(n) for n in D.names])
# family difficulty
famx = np.array([D.x[D.fam == f].mean() for f in range(F)])
fam_names = [None] * F  # names not stored; tie-break by index (frozen: fam index = sorted name order)

def split_families(rng, fams):
    """fams: array of family indices present. returns bool array inA over F (False for absent)."""
    order = sorted(fams, key=lambda f: (famx[f], f))
    inA = np.zeros(F, bool)
    i = 0
    while i + 1 < len(order):
        c = rng.random() < 0.5
        inA[order[i]] = c; inA[order[i + 1]] = not c; i += 2
    if i < len(order): inA[order[i]] = rng.random() < 0.5
    return inA

BTOL = 1e-6
def valid(a, b):
    return (b > fc.BLO + BTOL) & (b < fc.BHI - BTOL) & (np.abs(a) < fc.AHI - BTOL)

def curv(h, mask):
    c, n, _ = fc.quad_fit(D.t, h, mask); return c[2] if n >= 4 else np.nan

def fit_halves(S, N, Wt, famw, inA):
    """S,N (M,K) cell counts (may carry bootstrap multiplicities), famw (F,) multiplicities or 1; returns hA,hB,vA,vB"""
    mA = (inA[D.fam] & (famw[D.fam] > 0)).astype(float); mB = ((~inA)[D.fam] & (famw[D.fam] > 0)).astype(float)
    Ss = np.stack([S * mA, S * mB]); Ns = np.stack([N * mA, N * mB])
    a, b = fc.fit_logistic(D.x, Ss, Ns, np.broadcast_to(Wt, Ns.shape))
    h = -a / b; v = valid(a, b) & (Ns.sum(-1) > 0)
    return h, v

def stats_dir(hX, vX, hY, vY, midx):
    """midx: model index array (possibly duplicated for bootstrap). Returns dict or None"""
    ok = (vX & vY)[midx]
    if ok.sum() < 4: return None
    mi = midx[ok]
    t = D.t[mi]
    # sota in date-then-name order on X among valid models
    order = sorted(range(len(mi)), key=lambda i: (D.dates[mi[i]], D.names[mi[i]]))
    hx = hX[mi]; keep = np.zeros(len(mi), bool); best = -np.inf
    for i in order:
        if hx[i] > best: keep[i] = True; best = hx[i]
        # strict improvement
    if keep.sum() < 4: return None
    def q(y, m):
        c, n, _ = fc.quad_fit(t, y, m); return c[2] if n >= 4 else np.nan
    allm = np.ones(len(mi), bool)
    CXs = q(hx, keep); CYs = q(hY[mi], keep); CYa = q(hY[mi], allm)
    hy = hY[mi]; keepY = np.zeros(len(mi), bool); best = -np.inf
    for i in order:
        if hy[i] > best: keepY[i] = True; best = hy[i]
    CYr = q(hy, keepY) if keepY.sum() >= 4 else np.nan
    # residual correlation from linear date trend on all valid models
    def res(y):
        A = np.stack([np.ones_like(t), t - fc.T0], 1); c = np.linalg.lstsq(A, y, rcond=None)[0]; return y - A @ c
    rr = np.corrcoef(res(hx), res(hy))[0, 1] if len(mi) >= 4 else np.nan
    return dict(D1=CXs - CYs, D2=CYs - CYa, D3=CXs - CYa, CXs=CXs, CYs=CYs, CYa=CYa, CYr=CYr, r=rr, nsel=int(keep.sum()), nall=len(mi))

def one_split(S, N, Wt, famw, inA, midx):
    h, v = fit_halves(S, N, Wt, famw, inA)
    out = []
    for X, Y in ((0, 1), (1, 0)):
        out.append(stats_dir(h[X], v[X], h[Y], v[Y], midx))
    return out, h, v

def agg(lst):
    """lst of per-direction dicts (None allowed). split value = mean over available directions"""
    keys = ['D1', 'D2', 'D3', 'CXs', 'CYs', 'CYa', 'CYr', 'r']
    return {k: float(np.nanmean([d[k] for d in lst if d is not None])) if any(d is not None for d in lst) else np.nan for k in keys}

def run_real(nspl=200):
    famw = np.ones(F); allf = list(range(F)); rows = []; Hs = []; Vs = []; bal = []
    midx = np.arange(M)
    for s in range(nspl):
        rng = np.random.default_rng(np.random.SeedSequence([5301, s]))
        inA = split_families(rng, allf)
        tA = inA[D.fam]
        bal.append((abs(D.x[tA].mean() - D.x[~tA].mean()), abs(tA.sum() - (~tA).sum())))
        out, h, v = one_split(D.kk, D.n, D.w, famw, inA, midx)
        rows.append(out); Hs.append(h); Vs.append(v)
    return rows, np.array(Hs), np.array(Vs), np.array(bal)

def exactness():
    h, _, _ = fc.horizons_of(D); ref = json.load(open(ROOT + '/results/F_holdout.json'))['models']
    d = {n: x for n, _, x in ref}
    mx = max(abs(h[i] - d[D.names[i]]) for i in range(M)); return float(mx)

def boot(B=300, per=10, two_way=False):
    out = []; ndrop = 0
    for b in range(B):
        rng = np.random.default_rng(np.random.SeedSequence([5302, b, int(two_way)]))
        cf = rng.multinomial(F, np.full(F, 1 / F)).astype(float)
        famw = cf
        mult = np.repeat(cf[D.fam][None], M, 0)
        Sb = D.kk * cf[D.fam][None]; Nb = D.n * cf[D.fam][None]
        present = [f for f in range(F) if cf[f] > 0]
        if two_way:
            cd = rng.multinomial(3, np.full(3, 1 / 3))
            midx = np.concatenate([np.where(DEV == g)[0] for g in range(3) for _ in range(cd[g])]).astype(int) if cd.sum() else np.array([], int)
        else:
            midx = np.arange(M)
        vals = []
        for s in range(per):
            inA = split_families(rng, present)
            res, _, _ = one_split(Sb, Nb, D.w, famw, inA, midx)
            vals.append(agg(res)) if any(r is not None for r in res) else None
        if len(vals) < 4: ndrop += 1; continue
        out.append({k: float(np.nanmean([v[k] for v in vals])) for k in vals[0]})
    return out, ndrop

def ci(lst, k):
    x = np.array([d[k] for d in lst]); x = x[~np.isnan(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5)), len(x)]

# ------------------------------------------------------------------ controls
def sim_counts(rng, world, nmult=1, shock=0.5):
    h0, a0, b0 = fc.horizons_of(D)
    t = D.t; A = np.stack([np.ones_like(t), t - fc.T0], 1); c = np.linalg.lstsq(A, h0, rcond=None)[0]; s = np.sqrt(((h0 - A @ c) ** 2).sum() / (M - 2))
    htrue = A @ c + rng.normal(0, s, M)
    # keep real slopes; intercept so that -a/b = htrue  (log2 minutes -> x is log2 minutes)
    a = -b0 * htrue
    z = a[:, None] + b0[:, None] * D.x[None]
    if world in ('C2', 'C3'):
        u = rng.normal(0, shock, K); v = rng.normal(0, shock, F)
        z = z + (u + v[D.fam])[None]
    p = fc._sig(z); N = D.n * nmult
    if world in ('C0', 'C2'): S = N * p
    else: S = rng.binomial(N.astype(np.int64), p).astype(float)
    return S, N, htrue

def run_controls(nd=100, per=20):
    res = {}
    for w, nm in (('C0', 1), ('C1', 1), ('C1x10', 10), ('C2', 1), ('C3', 1)):
        world = w[:2]; vals = []
        for d in range(nd):
            rng = np.random.default_rng(np.random.SeedSequence([5303, abs(hash(w)) % 1000 if False else ['C0', 'C1', 'C1x10', 'C2', 'C3'].index(w), d]))
            S, N, _ = sim_counts(rng, world, nm)
            famw = np.ones(F); sp = []
            for s in range(per):
                inA = split_families(rng, list(range(F)))
                r, _, _ = one_split(S, N, D.w, famw, inA, np.arange(M))
                if any(x is not None for x in r): sp.append(agg(r))
            if sp: vals.append({k: float(np.nanmean([x[k] for x in sp])) for k in sp[0]})
        arr = {k: np.array([v[k] for v in vals]) for k in vals[0]}
        res[w] = {k: dict(mean=float(np.nanmean(v)), se=float(np.nanstd(v, ddof=1) / np.sqrt(len(v))), maxabs=float(np.nanmax(np.abs(v)))) for k, v in arr.items()}
        res[w]['n_draws'] = len(vals)
        print(w, {k: round(res[w][k]['mean'], 5) for k in ('D1', 'D2', 'CYs', 'CYa')}, 'se D1', round(res[w]['D1']['se'], 5), flush=True)
    return res

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode in ('real', 'all'):
        ex = exactness(); print('exactness max|dh|', ex); assert ex < 1e-9, ex
        rows, Hs, Vs, bal = run_real()
        est = [agg(r) for r in rows if any(x is not None for x in r)]
        nest = sum(x is not None for r in rows for x in r)
        mean = {k: float(np.nanmean([e[k] for e in est])) for k in est[0]}
        sd = {k: float(np.nanstd([e[k] for e in est])) for k in est[0]}
        inval = {D.names[i]: float(1 - Vs[:, :, i].mean()) for i in range(M)}
        # leave-one-developer-out
        lodo = {}
        for g, gn in enumerate(['Anthropic', 'OpenAI', 'Google']):
            midx = np.where(DEV != g)[0]; rr = []
            for s in range(200):
                rng = np.random.default_rng(np.random.SeedSequence([5301, s])); inA = split_families(rng, list(range(F)))
                o, _, _ = one_split(D.kk, D.n, D.w, np.ones(F), inA, midx)
                if any(x is not None for x in o): rr.append(agg(o))
            lodo[gn] = {k: float(np.nanmean([e[k] for e in rr])) for k in ('D1', 'D2', 'D3')}; lodo[gn]['n_est_splits'] = len(rr)
        json.dump(dict(exactness=ex, n_splits=200, n_estimable_directions=nest, of=400, est_splits=len(est), mean=mean, sd_across_splits=sd, invalid_frac=inval,
                       balance=dict(mean_abs_dx=float(bal[:, 0].mean()), max_abs_dx=float(bal[:, 0].max()), mean_abs_ntask=float(bal[:, 1].mean())), lodo=lodo), open(R + '/real.json', 'w'), indent=1)
        print(json.dumps(mean, indent=1), nest, inval)
    if mode in ('boot', 'all'):
        o1, d1 = boot(two_way=False); o2, d2 = boot(two_way=True)
        res = dict(family=dict(n=len(o1), dropped=d1, **{k: ci(o1, k) for k in ('D1', 'D2', 'D3', 'r')}),
                   two_way=dict(n=len(o2), dropped=d2, **{k: ci(o2, k) for k in ('D1', 'D2', 'D3', 'r')}))
        json.dump(res, open(R + '/boot.json', 'w'), indent=1); print(json.dumps(res, indent=1))
    if mode in ('controls', 'all'):
        c = run_controls(); json.dump(c, open(R + '/controls.json', 'w'), indent=1)
