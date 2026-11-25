"""EXPLORATORY design-stage, DESIGN AMENDMENT 3 (idea F).  Synthetic data only; no confirmatory claim.  Spec: AMENDMENT3.md.
Does NOT modify fcore/fdesign/fdesign3/fsim (frozen; imported).  Adds corrections for selection-induced curvature and diagnostics, all on the SAME
simulated datasets as Amendment 2 (data are regenerated with the A2 seeds, so rows pair with A2 rows by (cell, rep)); new randomness uses seed tag 83.
Conventions as in A2: p_up = evidence for POSITIVE curvature (acceleration), p_dn = deceleration; z = Phi^-1(1 - p_up).
Everything below works in DATE ORDER (D.order); a record = strict improvement over the running maximum of all earlier models."""
import numpy as np, fcore as fc, fdesign3 as f3
from scipy import stats, optimize
from scipy.special import log_ndtr

T0 = fc.T0


# ------------------------------------------------------------------ ordered-domain helpers (arrays (..., M))
def prev_max(yo):
    """running maximum of all EARLIER models; -inf for the first."""
    cm = np.maximum.accumulate(yo, axis=-1)
    pm = np.full_like(yo, -np.inf); pm[..., 1:] = cm[..., :-1]
    return pm


def rec_mask(yo):
    return yo > prev_max(yo)                                   # first model: > -inf -> True


def back_low_mask(yo):
    """backward lower record: strictly below every LATER model (last model always True)."""
    cm = np.minimum.accumulate(yo[..., ::-1], axis=-1)[..., ::-1]
    keep = np.ones_like(yo, bool); keep[..., :-1] = yo[..., :-1] < cm[..., 1:]
    return keep


def qcoef(to, yo, w):
    """weighted (w >= 0 floats) OLS quadratic coef; NaN when fewer than 4 effective points."""
    c, n, _ = fc.quad_fit(to, yo, w)
    return np.where(n >= 4, c[..., 2], np.nan)


def line_fit(to, yo):
    A = np.stack([np.ones_like(to), to - T0], 1); P = np.linalg.pinv(A)       # (2,M)
    cf = yo @ P.T; mu = cf @ A.T; res = yo - mu; s = np.sqrt((res ** 2).sum(-1) / (yo.shape[-1] - 2))
    return mu, s


# ------------------------------------------------------------------ the statistics computed on a batch (observed + bootstrap), all return dict of (...,)
def stat_batch(to, yo, q_aud, aud_u, h_frac=0.5):
    """to (M,), yo (...,M) in date order, aud_u (...,M) uniform draws for the random audit.  Returns dict of statistics (beta2-type unless noted)."""
    out = {}
    rec = rec_mask(yo); pm = prev_max(yo); nrec = rec.sum(-1)
    c_f = qcoef(to, yo, rec.astype(float)); out['sota'] = c_f
    low = back_low_mask(yo); c_b = qcoef(to, yo, low.astype(float)); out['mir'] = 0.5 * (c_f + c_b); out['mir_f'] = c_f; out['mir_b'] = c_b
    call = qcoef(to, yo, np.ones_like(yo)); out['all'] = call; out['contr'] = c_f - call
    mu, s = line_fit(to, yo); s = np.maximum(s, 1e-9)[..., None]
    # Heckman-type inverse-Mills de-truncation of each record (first record unconditional), plug-in line + sd from the same dataset
    w = (np.where(np.isfinite(pm), pm, 0.0) - mu) / s
    lam = np.exp(stats.norm.logpdf(w) - log_ndtr(-w)); corr = np.where(np.isfinite(pm), s * lam, 0.0)
    out['heck'] = qcoef(to, np.where(rec, yo - corr, 0.0), rec.astype(float))
    # naive inverse-probability weighting of records by the plug-in record probability (candidates 97/166): EXPECTED NOT to correct, selection is on the outcome; kept as a negative control
    pi = np.where(np.isfinite(pm), np.exp(log_ndtr(-w)), 1.0); out['ipw'] = qcoef(to, yo, rec / np.clip(pi, 0.05, 1.0))
    # random audit of non-records with inverse-probability weights (records observed w.p. 1, audited non-records w.p. q)
    aud = (~rec) & (aud_u < q_aud); wt = rec.astype(float) + aud.astype(float) / q_aud
    out['audit'] = qcoef(to, yo, wt)
    # record timing: mean record date minus mean date of all models (years)
    out['rrate'] = np.where(nrec >= 4, (rec * (to - to.mean())).sum(-1) / np.maximum(nrec, 1), np.nan)
    # record-gap trend: mean gap in the later half of records minus the earlier half (log2 min)
    gp = np.where(rec, yo - np.where(np.isfinite(pm), pm, yo), np.nan)           # gap over previous max; first record gap 0 -> excluded below
    ri = np.cumsum(rec, axis=-1) - 1                                              # record rank 0..n-1 at record positions
    first = rec & (ri == 0); gp = np.where(first, np.nan, gp)
    half = (nrec[..., None] // 2)
    early = rec & ~first & (ri < half); late = rec & (ri >= half)
    ge = np.where(early, gp, 0).sum(-1) / np.maximum(early.sum(-1), 1); gl = np.where(late, gp, 0).sum(-1) / np.maximum(late.sum(-1), 1)
    out['gap'] = np.where((nrec >= 5) & (early.sum(-1) >= 1) & (late.sum(-1) >= 1), gl - ge, np.nan)
    # threshold perturbation: keep only records that beat the previous max by >= h_frac * sd
    thr = rec & ((yo - np.where(np.isfinite(pm), pm, yo)) >= h_frac * s) | (rec & ~np.isfinite(pm))
    out['thr'] = qcoef(to, yo, thr.astype(float)) - c_f
    return out


TESTS_PB = ['sota', 'mir', 'heck', 'ipw', 'audit', 'rrate', 'gap', 'contr', 'thr']


def pb_calibrated(D, sim, h, rng, B=1999, q_aud=0.25):
    """observed statistics on h and parametric-bootstrap null (line fitted to ALL horizons + N(0, resid sd), as pb_sota in A2, clipped at the ceiling if the suite has one)."""
    o = D.order; to = D.t[o]; yo = h[o]
    r_a, r_b = np.random.default_rng(rng.integers(2**63)), rng
    obs = stat_batch(to, yo, q_aud, r_a.random(yo.shape))
    A = np.stack([np.ones_like(to), to - T0], 1); cf = np.linalg.lstsq(A, yo, rcond=None)[0]; res = yo - A @ cf; s = np.sqrt((res ** 2).sum() / (len(yo) - 2))
    hs = sim.obs(A @ cf + r_b.normal(0, s, (B, len(yo))))
    nul = stat_batch(to, hs, q_aud, r_b.random(hs.shape))
    out = {}
    for k in TESTS_PB:
        v = nul[k]; v = v[~np.isnan(v)]; c = float(obs[k])
        if np.isnan(c) or len(v) < 0.5 * B:
            out[k + '_pup'] = out[k + '_pdn'] = out[k + '_z'] = np.nan; out[k + '_nvalid'] = int(len(v)); out[k + '_c'] = c; continue
        pu = (1 + (v >= c).sum()) / (len(v) + 1); pd = (1 + (v <= c).sum()) / (len(v) + 1)
        out[k + '_pup'] = float(pu); out[k + '_pdn'] = float(pd); out[k + '_z'] = float(stats.norm.ppf(1 - np.clip(pu, 1e-9, 1 - 1e-9))); out[k + '_nvalid'] = int(len(v)); out[k + '_c'] = c
        out[k + '_nullmean'] = float(v.mean())
    out['c_all'] = float(obs['all']); out['c_mir_f'] = float(obs['mir_f']); out['c_mir_b'] = float(obs['mir_b'])
    # leave-one-record-out influence on the SOTA curvature (diagnostic D5; observed only)
    rec = rec_mask(yo); idx = np.where(rec)[0]; c0 = float(obs['sota']); infl = np.nan
    if len(idx) >= 5:
        cs = [float(qcoef(to, yo, np.where(np.arange(len(yo)) == i, 0.0, rec.astype(float)))) for i in idx]
        d = np.abs(c0 - np.array(cs)); infl = float(np.nanmax(d)); out['loro_sd'] = float(np.sqrt((len(cs) - 1) / len(cs) * np.nansum((np.array(cs) - np.nanmean(cs)) ** 2)))
    out['loro_max'] = infl; out['nS'] = int(rec.sum())
    return out


# ------------------------------------------------------------------ record likelihoods (all models): M1 censored crossing (ccl), M2 record-truncated (tcl)
def _nll(theta, to, yo, pm, rec, mode, deg):
    """negative log-likelihood and gradient.  theta = (a, b, [c], logsigma); u = (t - mean t)/span.  mode 'ccl': records density, non-records censored at the running max;
    mode 'tcl': record density truncated to (previous max, inf), non-records dropped.  The first model is an unconditioned density in both."""
    a, b = theta[0], theta[1]; c = theta[2] if deg == 2 else 0.0; ls = theta[-1]; sg = np.exp(ls)
    u = to
    mu = a + b * u + c * u * u
    z = (yo - mu) / sg
    f = 0.0; ga = np.zeros_like(mu); gl = 0.0
    r = rec                                                                  # record rows: Gaussian density
    f += np.sum(0.5 * z[r] ** 2 + ls + 0.5 * np.log(2 * np.pi)); ga[r] += -z[r] / sg; gl += np.sum(1.0 - z[r] ** 2)
    has_prev = np.isfinite(pm)
    if mode == 'ccl':
        n = (~r)                                                              # non-records: log Phi((M - mu)/sigma)
        w = (pm[n] - mu[n]) / sg; lp = log_ndtr(w); f += -np.sum(lp)
        rr = np.exp(stats.norm.logpdf(w) - lp); ga[n] += rr / sg; gl += np.sum(rr * w)
    else:
        t_ = r & has_prev                                                     # truncated records: - log(1 - Phi((M - mu)/sigma))
        w = (pm[t_] - mu[t_]) / sg; lq = log_ndtr(-w); f += np.sum(lq)
        rr = np.exp(stats.norm.logpdf(w) - lq); ga[t_] += rr / sg; gl += np.sum(rr * w)
    g = [ga.sum(), (ga * u).sum()] + ([(ga * u * u).sum()] if deg == 2 else []) + [gl]
    return f, np.array(g)


def record_lik(D, h, mode):
    """returns dict(z, c_hat, ok) for the signed LRT of the quadratic term in the record likelihood of the given mode ('ccl' or 'tcl')."""
    o = D.order; span = float(D.t.max() - D.t.min()); to = (D.t[o] - D.t[o].mean()) / span; yo = h[o]
    pm = prev_max(yo); rec = yo > pm
    A = np.stack([np.ones_like(to), to, to * to], 1); b0 = np.linalg.lstsq(A, yo, rcond=None)[0]; s0 = max(np.std(yo - A @ b0), 0.05)
    bnds2 = [(None, None)] * 3 + [(-6.0, 4.0)]; bnds1 = [(None, None)] * 2 + [(-6.0, 4.0)]
    th1 = np.array([b0[0], b0[1], np.log(s0)]); th2 = np.array([b0[0], b0[1], b0[2], np.log(s0)])
    r1 = optimize.minimize(_nll, th1, args=(to, yo, pm, rec, mode, 1), jac=True, method='L-BFGS-B', bounds=bnds1)
    r2 = optimize.minimize(_nll, np.concatenate([r1.x[:2], [0.0], r1.x[2:]]), args=(to, yo, pm, rec, mode, 2), jac=True, method='L-BFGS-B', bounds=bnds2)
    lrt = max(0.0, 2 * (r1.fun - r2.fun)); ch = float(r2.x[2]) / span ** 2                   # back to beta2 units (per year^2)
    z = float(np.sign(ch) * np.sqrt(lrt)); ok = bool(r1.success or r1.status in (0, 1)) and bool(r2.success or r2.status in (0, 1))
    return dict(z=z, c=ch, ok=ok, sig=float(np.exp(r2.x[3])))


def run_rep4(sim, ci_a2, rep, ci_a3, which_lik=True, B=1999):
    """regenerates the A2 dataset for (A2 cell index ci_a2, rep) -- identical D, h -- and applies the Amendment-3 battery with seed tag 83."""
    ss = np.random.SeedSequence([79, ci_a2, rep]); s1 = ss.spawn(3)[0]
    D, h = sim.generate(np.random.default_rng(s1))
    rng = np.random.default_rng(np.random.SeedSequence([83, ci_a3, rep]))
    out = pb_calibrated(D, sim, h, rng, B=B)
    if which_lik:
        for m in ('ccl', 'tcl'):
            try: r = record_lik(D, h, m)
            except Exception as e: r = dict(z=np.nan, c=np.nan, ok=False)
            z = r['z']; out[m + '_z'] = z; out[m + '_c'] = r['c']; out[m + '_ok'] = r['ok']
            out[m + '_pup'] = float(stats.norm.sf(z)) if np.isfinite(z) and r['ok'] else np.nan; out[m + '_pdn'] = float(stats.norm.cdf(z)) if np.isfinite(z) and r['ok'] else np.nan
    return out
