"""F multi-benchmark planted-trend audit: core. Frozen by sha256 in PLAN_AMENDMENT_1.md BEFORE any statistic is computed.
numpy/scipy/pandas only. Release dates only; every score-date association is destroyed (N0) or planted (P1,P2+-)."""
import math, json, hashlib
import numpy as np, pandas as pd
from scipy import stats

ROOT = __file__.rsplit('/multibench_audit/', 1)[0]
DATA = ROOT + '/data/epoch/epoch_benchmarks'
SAT = 0.90; B = 400; BASE_SEED = 44
MIN_MODELS, MIN_RECORDS, MIN_MONTHS, MIN_ORGS = 30, 8, 15, 8
CONSTR = ('N0', 'P1', 'P2p', 'P2m')

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def dyear(s):
    t = pd.to_datetime(s, errors='coerce')
    return t.dt.year + (t.dt.dayofyear - 1) / 365.25

def running_max_records(y):
    """strict running maximum over arrays already sorted by (date, name)."""
    cm = np.maximum.accumulate(y)
    m = np.ones(len(y), bool); m[1:] = y[1:] > cm[:-1]
    return m

def load_series(fname, col, scale, ceiling, tcol_override=None):
    """-> dict(raw, t, name, org, months) after dedupe (max score per model version) and date/score drop, BEFORE truncation."""
    d = pd.read_csv(f'{DATA}/{fname}')
    sc = pd.to_numeric(d[col], errors='coerce') * scale
    out = pd.DataFrame({'n': d['Model version'].astype(str), 't': dyear(d['Release date']), 'ym': pd.to_datetime(d['Release date'], errors='coerce').dt.strftime('%Y-%m'),
                        'o': d['Organization'].fillna('NA').astype(str), 'v': sc}).dropna(subset=['t', 'v', 'ym'])
    out = out.sort_values(['n', 'v'], kind='mergesort').drop_duplicates('n', keep='last')   # max score per model version
    out = out.sort_values(['t', 'n'], kind='mergesort').reset_index(drop=True)
    return out, ceiling

def prepare(d, ceiling, transform=None):
    """saturation truncation (first record >= SAT*ceiling) then transform choice. returns frame + transform name."""
    d = d.copy()
    if ceiling and ceiling > 0:
        rm = running_max_records(d.v.values)
        hit = np.where(rm & (d.v.values >= SAT * ceiling))[0]
        if len(hit): d = d.iloc[:hit[0]].reset_index(drop=True)
    v = d.v.values
    if transform is None:
        if len(v) and v.min() >= 0 and v.max() <= 1: transform = 'logit'
        elif len(v) and v.min() > 0 and v.max() / v.min() > 20: transform = 'log2'
        else: transform = 'z'
    if transform == 'logit': y = np.log(np.clip(v, 0.005, 0.995) / (1 - np.clip(v, 0.005, 0.995)))
    elif transform == 'log2': y = np.log2(v)
    else: y = (v - v.mean()) / (v.std() if v.std() > 0 else 1.0)
    d['y'] = y
    return d, transform

def eligibility(d):
    n = len(d)
    if n == 0: return False, 'no rows', {}
    rec = int(running_max_records(d.y.values).sum()); months = int(d.ym.nunique()); orgs = int(d.o.nunique())
    info = dict(models=n, records=rec, months=months, orgs=orgs)
    why = [k for k, ok in (('models<30', n >= MIN_MODELS), ('records<8', rec >= MIN_RECORDS), ('months<15', months >= MIN_MONTHS)) if not ok]
    return (not why), ','.join(why), info

# ---------------- quadratic fit machinery (batched) ----------------
def quad_coef_batch(u, y, w):
    """u,y,w: (R,L); w in {0,1}. weighted LSQ of y on (1,u,u^2). returns (coef_u2 (R,), ok (R,))."""
    S = [ (w * u ** k).sum(1) for k in range(5) ]
    Ty = [ (w * y * u ** k).sum(1) for k in range(3) ]
    A = np.stack([np.stack([S[0], S[1], S[2]], 1), np.stack([S[1], S[2], S[3]], 1), np.stack([S[2], S[3], S[4]], 1)], 1)
    b = np.stack(Ty, 1)
    det = np.linalg.det(A)
    ok = np.abs(det) > 1e-9
    A2 = np.where(ok[:, None, None], A, np.eye(3)); x = np.linalg.solve(A2, b[..., None])[..., 0]
    return x[:, 2], ok

def t_iid(u, y, span):
    """OLS F-test of t^2 on record points. returns (coef per year^2, p). None if <4 records."""
    n = len(u)
    if n < 4: return None
    X1 = np.column_stack([np.ones(n), u]); X2 = np.column_stack([np.ones(n), u, u ** 2])
    b1, *_ = np.linalg.lstsq(X1, y, rcond=None); b2, *_ = np.linalg.lstsq(X2, y, rcond=None)
    r1 = y - X1 @ b1; r2 = y - X2 @ b2; s1 = r1 @ r1; s2 = r2 @ r2
    if s2 <= 1e-14 * max(1.0, s1): return (b2[2] / span ** 2, 0.0 if s1 > 1e-12 else 1.0)
    F = (s1 - s2) / (s2 / (n - 3)); p = float(stats.f.sf(F, 1, n - 3))
    return (b2[2] / span ** 2, p)

def _boot_idx_models(M, rng):
    return np.sort(rng.integers(0, M, (B, M)), axis=1), None

def _boot_idx_clustered(org_codes, rng):
    """org resample then within-org model resample. returns padded index matrix (B,Lmax) with sentinel M for padding."""
    M = len(org_codes); K = int(org_codes.max()) + 1
    order = np.argsort(org_codes, kind='stable'); sizes = np.bincount(org_codes, minlength=K); starts = np.concatenate([[0], np.cumsum(sizes)[:-1]])
    rows = []
    for _ in range(B):
        og = rng.integers(0, K, K)                        # K orgs with replacement
        n_o = sizes[og]
        tot = int(n_o.sum())
        base = np.repeat(starts[og], n_o); sz = np.repeat(n_o, n_o)
        pick = base + np.floor(rng.random(tot) * sz).astype(int)
        rows.append(np.sort(order[pick]))
    L = max(len(r) for r in rows)
    mat = np.full((B, L), M, dtype=int)
    for i, r in enumerate(rows): mat[i, :len(r)] = r
    return mat, None

def boot_ci(idx, y, u, span, M):
    """percentile 95% CI of the record-series t^2 coefficient (per year^2). idx (B,L) of model positions, M = sentinel."""
    ye = np.append(y, -1e9); ue = np.append(u, 0.0)
    Y = ye[idx]; U = ue[idx]
    cm = np.maximum.accumulate(Y, axis=1)
    rec = np.ones_like(Y, bool); rec[:, 1:] = Y[:, 1:] > cm[:, :-1]
    rec &= (idx < M)
    nrec = rec.sum(1)
    c, ok = quad_coef_batch(U, np.where(rec, Y, 0.0), rec.astype(float))
    valid = ok & (nrec >= 5)
    nv = int(valid.sum())
    if nv < 20: return None, int(B - nv)
    lo, hi = np.percentile(c[valid], [2.5, 97.5]) / span ** 2
    return (float(lo), float(hi)), int(B - nv)

def run_one(t, y, org_codes, rng_seed, span):
    """t,y sorted by (date,name) arrays (already permuted/planted), org_codes per model. returns dict of stats."""
    M = len(y); u = (t - t[0]) / span
    rm = running_max_records(y)
    out = {'nrec': int(rm.sum())}
    iid = t_iid(u[rm], y[rm], span)
    out['iid_coef'], out['iid_p'] = (iid if iid else (np.nan, np.nan))
    rng = np.random.default_rng(np.random.SeedSequence(rng_seed))
    idx, _ = _boot_idx_models(M, rng)
    ci, skipped = boot_ci(idx, y, u, span, M)
    out['mb_lo'], out['mb_hi'] = ci if ci else (np.nan, np.nan); out['mb_skip'] = skipped
    # point estimate of the record-series t^2 coefficient (no bootstrap), same units
    if rm.sum() >= 4:
        c, ok = quad_coef_batch(u[None, rm], y[None, rm], np.ones((1, int(rm.sum()))))
        out['coef'] = float(c[0] / span ** 2) if ok[0] else np.nan
    else: out['coef'] = np.nan
    if len(np.unique(org_codes)) >= MIN_ORGS:
        idx, _ = _boot_idx_clustered(org_codes, rng)
        ci, skipped = boot_ci(idx, y, u, span, M)
        out['cl_lo'], out['cl_hi'] = ci if ci else (np.nan, np.nan); out['cl_skip'] = skipped
    else:
        out['cl_lo'] = out['cl_hi'] = np.nan; out['cl_skip'] = -1
    return out

def planted(t, y, construction, sd, span):
    t0 = t.min()
    if construction == 'N0': return y.copy(), 0.0
    s = 0.5 * sd / span; tt = t - t0
    if construction == 'P1': return y + s * tt, 0.0
    c = (0.5 if construction == 'P2p' else -0.5) * sd / span ** 2
    return y + s * tt + c * tt ** 2, c

def permuted_frame(d, rep, sidx):
    """permute release dates among models (org moves with model -> clusters intact). returns arrays sorted by (date,name)."""
    rng = np.random.default_rng(np.random.SeedSequence([BASE_SEED, sidx, rep]))
    perm = rng.permutation(len(d))
    t = d.t.values[perm]
    name_rank = np.argsort(np.argsort(d.n.values, kind='stable'), kind='stable')
    order = np.lexsort((name_rank, t))
    return t[order], order        # model position order after sort; y, org taken as d.y[order] etc.
