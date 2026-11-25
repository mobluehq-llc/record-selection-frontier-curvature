"""Idea U core. Frozen with PLAN.md BEFORE any coverage is computed. numpy/scipy/pandas only."""
import math, hashlib
import numpy as np, pandas as pd
from scipy import stats

ROOT = __file__.rsplit('/code/', 1)[0]
DATA = ROOT + '/../data/epoch'
LEVELS = (0.80, 0.95)
HORIZONS = (0.5, 1.0, 2.0)       # years
STEP = 0.5                       # origin spacing, years
B = 500                          # bootstrap replicates
SAT = 0.90                       # GPQA saturation cut
MINREC = 8                       # records required at first origin (card draft said 12; changed before any fit, see PLAN)

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def dyear(s):
    t = pd.to_datetime(s, errors='coerce')
    return t.dt.year + (t.dt.dayofyear - 1) / 365.25

# name -> (file, name col, date col, value col, transform, filter)
SERIES = {
    'compute': ('notable_ai_models.csv', 'Model', 'Publication date', 'Training compute (FLOP)', 'log10', 2010.0),
    'metr':    ('epoch_benchmarks/metr_time_horizons_external.csv', 'Model version', 'Release date', 'Time horizon', 'log2', None),
    'gpqa':    ('epoch_benchmarks/gpqa_diamond.csv', 'Model version', 'Release date', 'mean_score', 'logit', None),
    'hw':      ('ml_hardware.csv', 'Hardware name', 'Release date', 'Tensor-FP16/BF16 performance (FLOP/s)', 'log10', None),
    'eci':     ('epoch_benchmarks/epoch_capabilities_index/eci_scores.csv', 'Model', 'date', 'eci', 'lin', None),
}
ORDER = list(SERIES)

def load(name):
    f, nc, dc, vc, tr, tmin = SERIES[name]
    d = pd.read_csv(f'{DATA}/{f}')
    d = pd.DataFrame({'n': d[nc].astype(str), 't': dyear(d[dc]), 'v': pd.to_numeric(d[vc], errors='coerce')}).dropna()
    d = d[d.v > 0] if tr != 'lin' else d
    if tmin: d = d[d.t >= tmin]
    if tr == 'logit':
        d = d[(d.v > 0) & (d.v < 1)]
    d = d.sort_values(['t', 'n', 'v'], kind='mergesort').reset_index(drop=True)
    if tr == 'logit':  # truncate before first record >= SAT (record rule on raw score)
        best = -1; cut = None
        for t, v in zip(d.t, d.v):
            if v > best:
                best = v
                if v >= SAT: cut = t; break
        d = d[d.t < cut].reset_index(drop=True)
    y = {'log10': np.log10, 'log2': np.log2, 'logit': lambda x: np.log(x / (1 - x)), 'lin': lambda x: x}[tr](d.v.values)
    return d.t.values.astype(float), y, d.n.values

def record_mask(t, y, n=None):
    """running strict maximum in (date, name) order (arrays assumed pre-sorted)."""
    m = np.zeros(len(y), bool); best = -np.inf
    for i in range(len(y)):
        if y[i] > best: m[i] = True; best = y[i]
    return m

def ols(x, y):
    X = np.column_stack([np.ones_like(x), x]); b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ b; return b, r

def pi_ols(x, y, x0, alpha):
    n = len(x); b, r = ols(x, y)
    if n < 4: return None
    s = math.sqrt((r @ r) / (n - 2)); xb = x.mean(); sxx = ((x - xb) ** 2).sum()
    se = s * math.sqrt(1 + 1 / n + (x0 - xb) ** 2 / sxx)
    c = b[0] + b[1] * x0; q = stats.t.ppf(1 - alpha / 2, n - 2)
    return c, c - q * se, c + q * se

def _pct(draws, alpha):
    return np.quantile(draws, [alpha / 2, 1 - alpha / 2])

def resid_boot(x, y, x0, rng):
    """M1: residual bootstrap of OLS on record points; draws of predicted y at x0 incl. a fresh residual."""
    n = len(x); b, r = ols(x, y); fit = y - r
    idx = rng.integers(0, n, (B, n)); out = np.empty(B)
    xc = x - x.mean()
    for k in range(B):
        ys = fit + r[idx[k]]
        bb, _ = ols(x, ys); out[k] = bb[0] + bb[1] * x0 + r[rng.integers(0, n)]
    return out

def model_boot(t, y, nm, x0, rng):
    """M2: model-level bootstrap; resample ALL points, re-apply the record rule, refit, add residual draw."""
    N = len(y); out = []
    for k in range(B):
        i = np.sort(rng.integers(0, N, N))   # sorted index == (date, name) order preserved
        ts, ys = t[i], y[i]
        m = record_mask(ts, ys)
        if m.sum() < 4: continue
        b, r = ols(ts[m], ys[m])
        out.append(b[0] + b[1] * x0 + r[rng.integers(0, len(r))])
    return np.array(out)

def sota_at(t, y, T):
    m = t <= T
    return y[m].max()

def origins(t, y, nm):
    """origin grid: from date of 12th record, every STEP years, while origin+1y <= last data date."""
    rm = record_mask(t, y); rt = t[rm]
    if len(rt) < MINREC: return [], rt
    o = rt[MINREC - 1]; last = t.max(); out = []
    while o + 1.0 <= last + 1e-9:
        out.append(o); o += STEP
    return out, rt

def eligible(t, y, nm):
    og, rt = origins(t, y, nm)
    ok = len(rt) >= MINREC and len([r for r in rt if r > (og[0] if og else 1e9)]) >= 4 and len(og) > 0
    return ok, og, rt

def point_forecast(t, y, o, h, family):
    m = t <= o
    ts, ys = t[m], y[m]
    if family == 'sota':
        rm = record_mask(ts, ys); ts, ys = ts[rm], ys[rm]
    if len(ts) < 5: return None
    b, r = ols(ts, ys); return b[0] + b[1] * (o + h)

def conformal(t, y, o, h, alpha, first_cal):
    errs = []
    c = first_cal
    while c + h <= o + 1e-9:
        pf = point_forecast(t, y, c, h, 'sota')
        if pf is not None: errs.append(abs(sota_at(t, y, c + h) - pf))
        c += 1 / 12
    n = len(errs); k = math.ceil((n + 1) * (1 - alpha))
    if k > n: return None, n
    return sorted(errs)[k - 1], n

def intervals(t, y, nm, o, h, rng_seed):
    """returns dict[(method, level)] = (lo, hi) in transformed scale; None = not measured."""
    m = t <= o; ts, ys, ns = t[m], y[m], nm[m]
    rm = record_mask(ts, ys); rts, rys = ts[rm], ys[rm]
    x0 = o + h; out = {}
    rng = np.random.default_rng(np.random.SeedSequence(rng_seed))
    for a in LEVELS:
        al = 1 - a
        p = pi_ols(rts, rys, x0, al); out[('M0', a)] = None if p is None else (p[1], p[2])
        p = pi_ols(ts, ys, x0, al); out[('M0all', a)] = None if p is None else (p[1], p[2])
    d1 = resid_boot(rts, rys, x0, rng) if len(rts) >= 5 else None
    d2 = model_boot(ts, ys, ns, x0, rng)
    for a in LEVELS:
        al = 1 - a
        out[('M1', a)] = None if d1 is None else tuple(_pct(d1, al))
        out[('M2', a)] = tuple(_pct(d2, al)) if len(d2) >= 100 else None
        pf = point_forecast(t, y, o, h, 'sota')
        q, ncal = (None, 0)
        if pf is not None:
            q, ncal = conformal(t, y, o, h, al, FIRST_CAL[nm_key(t, y)])
        out[('M3', a)] = None if q is None else (pf - q, pf + q)
    return out

FIRST_CAL = {}
def nm_key(t, y): return (len(t), float(t.sum()))
def set_first_cal(t, y):
    rm = record_mask(t, y); rt = t[rm]
    FIRST_CAL[nm_key(t, y)] = rt[MINREC - 3] if len(rt) >= MINREC - 2 else 1e9

def run_series(name, B_override=None):
    global B
    if B_override: B = B_override
    t, y, nm = load(name)
    ok, og, rt = eligible(t, y, nm)
    set_first_cal(t, y)
    rows = []
    if not ok: return ok, rows, (t, y, rt)
    for oi, o in enumerate(og):
        for hi, h in enumerate(HORIZONS):
            if o + h > t.max() + 1e-9: continue
            truth = sota_at(t, y, o + h)
            iv = intervals(t, y, nm, o, h, [33, ORDER.index(name), oi, hi])
            for (mth, a), v in iv.items():
                rows.append(dict(series=name, origin=o, h=h, method=mth, level=a, truth=truth,
                                 lo=None if v is None else v[0], hi=None if v is None else v[1]))
    return ok, rows, (t, y, rt)
