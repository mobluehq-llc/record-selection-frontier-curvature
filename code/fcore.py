"""Core library for idea F (trend-calibration).  Dense (model x task) cell representation of METR runs.
A cell = (model m, task k): n runs, kk successes, weight w (invsqrt_task_weight; constant within a cell - verified).
Run-level resampling inside a cell is EXACTLY equivalent to S ~ Binomial(N_cell, kk/n) with N_cell = (family mult)*(task mult)*n,
because with task multiplicity c the c independent run-resamples of n runs are one Multinomial(c*n, uniform) draw."""
import json, datetime as dt, hashlib, numpy as np
from scipy import stats

EPOCH = dt.date(2019, 1, 1)
LAM = 0.01
BLO, BHI = -5.0, -1e-3
ALO, AHI = -60.0, 60.0
DATA = __import__('os').environ.get('FDATA', __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/data/metr')
RUNS_SHA = 'f489d11728909937dad99ba1ed2d7c40efe12a766891e67dbc7c2486a3311236'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''):
            h.update(ch)
    return h.hexdigest()


def load_release_dates(path=None):
    rd = {}
    for l in open(path or f'{DATA}/release_dates.yaml'):
        if l.startswith('  ') and ': ' in l:
            k, v = l.strip().rsplit(': ', 1)
            rd[k] = dt.date.fromisoformat(v)
    return rd


class Design:
    """dense arrays: n[m,k] runs, kk[m,k] successes, w[m,k] weight; x[k]=log2 human minutes; fam[k]; names[m]; t[m] (years since 2019-01-01)"""
    def __init__(self, names, dates, x, fam, n, kk, w):
        self.names = list(names); self.dates = list(dates); self.x = np.asarray(x, float); self.fam = np.asarray(fam, int)
        self.n = np.asarray(n, float); self.kk = np.asarray(kk, float); self.w = np.asarray(w, float)
        self.t = np.array([(d - EPOCH).days for d in self.dates], float) / 365.25
        self.M, self.K = self.n.shape; self.F = int(self.fam.max()) + 1
        # date-then-name order (the SOTA tie-break fix)
        self.order = np.array(sorted(range(self.M), key=lambda i: (self.dates[i], self.names[i])))


def load_real(data=None, cutoff=None, runs_path=None, dates_path=None):
    data = data or DATA
    rp = runs_path or f'{data}/runs_v1_0.jsonl'
    rd = load_release_dates(dates_path or f'{data}/release_dates.yaml')
    rows = [json.loads(l) for l in open(rp)]
    rows = [r for r in rows if r['alias'] != 'human' and r['alias'] in rd and (cutoff is None or rd[r['alias']] <= cutoff)]
    models = sorted({r['alias'] for r in rows}); tasks = sorted({r['task_id'] for r in rows})
    mi = {m: i for i, m in enumerate(models)}; ti = {t: i for i, t in enumerate(tasks)}
    fams = sorted({r['task_family'] for r in rows}); fi = {f: i for i, f in enumerate(fams)}
    M, K = len(models), len(tasks)
    n = np.zeros((M, K)); kk = np.zeros((M, K)); w = np.zeros((M, K)); x = np.zeros(K); fam = np.zeros(K, int)
    for r in rows:
        a, b = mi[r['alias']], ti[r['task_id']]
        n[a, b] += 1; kk[a, b] += r['score_binarized']; w[a, b] = r['invsqrt_task_weight'] or 0.0
        x[b] = np.log2(r['human_minutes']); fam[b] = fi[r['task_family']]
    return Design(models, [rd[m] for m in models], x, fam, n, kk, w)


# ---------------------------------------------------------------- batched weighted logistic fit
def _sig(z):
    return 0.5 * (1 + np.tanh(0.5 * z))


def fit_logistic(x, S, N, W, lam=LAM, iters=60, tol=1e-9, init=None):
    """Batched ridge(b only) weighted logistic, matching metr_repro.fit.  Arrays (..., K): x broadcastable, S successes, N trials, W cell weight.
    Weights normalised per fit so that sum(W*N) = sum(N) (metr_repro: w/w.sum()*len).  Returns a,b (shape ...)."""
    sw = (W * N).sum(-1, keepdims=True); sn = N.sum(-1, keepdims=True)
    Wn = np.where(sw > 0, W * sn / np.where(sw > 0, sw, 1), 0.0)
    shp = N.shape[:-1]
    a = np.zeros(shp); b = np.full(shp, -0.5)
    if init is not None:
        a = np.broadcast_to(init[0], shp).copy(); b = np.broadcast_to(init[1], shp).copy()
    def nll(a, b):
        z = a[..., None] + b[..., None] * x
        return (Wn * (N * np.logaddexp(0, z) - S * z)).sum(-1) + 0.5 * lam * b * b
    f0 = nll(a, b)
    for it in range(iters):
        z = a[..., None] + b[..., None] * x
        p = _sig(z); r = Wn * (N * p - S); v = Wn * N * p * (1 - p)
        ga = r.sum(-1); gb = (r * x).sum(-1) + lam * b
        haa = v.sum(-1) + 1e-12; hab = (v * x).sum(-1); hbb = (v * x * x).sum(-1) + lam
        # active set on b bounds
        bl = (b <= BLO + 1e-12) & (gb > 0); bh = (b >= BHI - 1e-12) & (gb < 0)
        fb = bl | bh
        det = haa * hbb - hab * hab
        da = np.where(fb, ga / haa, (hbb * ga - hab * gb) / det)
        db = np.where(fb, 0.0, (-hab * ga + haa * gb) / det)
        # also a-bounds
        al = (a <= ALO + 1e-12) & (ga > 0); ah = (a >= AHI - 1e-12) & (ga < 0)
        da = np.where(al | ah, 0.0, da)
        s = np.ones(shp)
        for _ in range(8):
            an = np.clip(a - s * da, ALO, AHI); bn = np.clip(b - s * db, BLO, BHI)
            fn = nll(an, bn); bad = fn > f0 + 1e-12
            if not bad.any():
                break
            s = np.where(bad, s * 0.5, s)
        an = np.clip(a - s * da, ALO, AHI); bn = np.clip(b - s * db, BLO, BHI)
        fn = nll(an, bn); ok = fn <= f0 + 1e-12
        step = np.maximum(np.abs(an - a), np.abs(bn - b))
        a = np.where(ok, an, a); b = np.where(ok, bn, b); f0 = np.where(ok, fn, f0)
        if np.max(np.where(ok, step, 0)) < tol:
            break
    return a, b


def horizons_of(design, S=None, N=None, W=None):
    """log2 h50 per model for a design (optionally with bootstrap S,N of shape (B,M,K))."""
    S = design.kk if S is None else S; N = design.n if N is None else N; W = design.w if W is None else W
    init = None
    if N.ndim == 3:   # warm start bootstrap fits from the full-sample fit
        a0, b0 = fit_logistic(design.x, design.kk, design.n, design.w)
        init = (a0, b0)
    a, b = fit_logistic(design.x, S, N, np.broadcast_to(W, N.shape), init=init)
    return -a / b, a, b


# ---------------------------------------------------------------- SOTA and regressions
def sota_mask(h, design):
    """h: (..., M) log2 horizons. Running max over (date, name) order, strict improvement. Returns bool mask (..., M) in original model order."""
    o = design.order
    ho = h[..., o]
    cm = np.maximum.accumulate(ho, axis=-1)
    keep = np.ones_like(ho, bool); keep[..., 1:] = ho[..., 1:] > cm[..., :-1]
    out = np.zeros_like(keep); out[..., o] = keep
    return out


T0 = 2022.0 - 2019.0   # centring for numerical conditioning (the t^2 coefficient is invariant to centring)


def quad_fit(t, y, mask):
    """masked OLS of y on (1,t,t^2). Returns coef (...,3) [c0,c1,c2], n (...), ssr (...). t (M,), y,mask (...,M)."""
    tc = t - T0
    m = mask.astype(float)
    n = m.sum(-1)
    P = np.stack([np.ones_like(tc), tc, tc * tc], -1)           # (M,3)
    X = np.einsum('...m,mi,mj->...ij', m, P, P)
    Y = np.einsum('...m,mi,...m->...i', m, P, y)
    X = X + 1e-9 * np.eye(3)
    ok = n >= 4
    X = np.where(ok[..., None, None], X, np.eye(3));
    c = np.linalg.solve(X, Y[..., None])[..., 0]
    res = (y - np.einsum('mi,...i->...m', P, c)) * m
    return c, n, (res ** 2).sum(-1)


def lin_ssr(t, y, mask):
    tc = t - T0; m = mask.astype(float); n = m.sum(-1)
    P = np.stack([np.ones_like(tc), tc], -1)
    X = np.einsum('...m,mi,mj->...ij', m, P, P) + 1e-9 * np.eye(2)
    Y = np.einsum('...m,mi,...m->...i', m, P, y)
    X = np.where((n >= 3)[..., None, None], X, np.eye(2))
    c = np.linalg.solve(X, Y[..., None])[..., 0]
    res = (y - np.einsum('mi,...i->...m', P, c)) * m
    return c, (res ** 2).sum(-1)


def t_iid(design, h, mask=None):
    """F-test on the t^2 term; mask None => SOTA set. returns dict(p, coef, nS)"""
    mask = sota_mask(h, design) if mask is None else mask
    c, n, ssr2 = quad_fit(design.t, h, mask)
    _, ssr1 = lin_ssr(design.t, h, mask)
    df2 = n - 3
    if n < 4 or ssr2 <= 0:
        return dict(p=np.nan, coef=np.nan, nS=int(n))
    F = (ssr1 - ssr2) / (ssr2 / df2)
    return dict(p=float(stats.f.sf(F, 1, df2)), coef=float(c[2]), nS=int(n))


# ---------------------------------------------------------------- hierarchical bootstrap
def hb_weights(design, B, rng):
    """Three-level (family -> task -> run) bootstrap. Returns (N_b (B,M,K), S_b (B,M,K))."""
    F, K = design.F, design.K
    cf = rng.multinomial(F, np.full(F, 1.0 / F), size=B)               # (B,F)
    ct = np.zeros((B, K))
    for f in range(F):
        idx = np.where(design.fam == f)[0]
        if len(idx):
            ct[:, idx] = rng.multinomial(len(idx), np.full(len(idx), 1.0 / len(idx)), size=B)
    mT = cf[:, design.fam] * ct                                          # (B,K)
    Nb = mT[:, None, :] * design.n[None]                                 # (B,M,K)
    pr = np.where(design.n > 0, design.kk / np.maximum(design.n, 1), 0.0)
    Sb = rng.binomial(Nb.astype(np.int64), np.broadcast_to(pr, Nb.shape)).astype(float)
    return Nb, Sb


def hb_quad(design, B, rng, chunk=100, min_valid=4):
    """returns arrays: quad coefs (B,), valid mask, plus all-model quad coefs, and horizons optionally"""
    qs = np.full(B, np.nan); qa = np.full(B, np.nan); lin = np.full(B, np.nan); nS = np.zeros(B)
    for s in range(0, B, chunk):
        bb = min(chunk, B - s)
        Nb, Sb = hb_weights(design, bb, rng)
        h, _, _ = horizons_of(design, Sb, Nb)
        mask = sota_mask(h, design)
        c, n, _ = quad_fit(design.t, h, mask)
        ok = n >= min_valid
        qs[s:s + bb] = np.where(ok, c[:, 2], np.nan); nS[s:s + bb] = n
        ca, _, _ = quad_fit(design.t, h, np.ones_like(mask))
        qa[s:s + bb] = ca[:, 2]
        cl, _ = lin_ssr(design.t, h, mask); lin[s:s + bb] = np.where(ok, cl[:, 1], np.nan)
    return qs, qa, nS


def t_hb(design, B, rng, h0=None):
    h, _, _ = horizons_of(design) if h0 is None else (h0, None, None)
    qs, qa, nS = hb_quad(design, B, rng)
    v = qs[~np.isnan(qs)]
    if len(v) < 0.5 * B:
        return dict(lo=np.nan, hi=np.nan, reject=False, nvalid=len(v), lo_all=np.nan, hi_all=np.nan, reject_all=False)
    lo, hi = np.percentile(v, [2.5, 97.5])
    va = qa[~np.isnan(qa)]; loa, hia = np.percentile(va, [2.5, 97.5])
    return dict(lo=float(lo), hi=float(hi), reject=bool(lo > 0 or hi < 0), nvalid=len(v),
                lo_all=float(loa), hi_all=float(hia), reject_all=bool(loa > 0 or hia < 0), rej_up=bool(lo > 0))


# ---------------------------------------------------------------- Clopper-Pearson
def cp(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return lo, hi
