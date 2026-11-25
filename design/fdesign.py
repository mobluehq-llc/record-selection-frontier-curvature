"""EXPLORATORY, design-stage (idea F).  Synthetic-data-only size/power map for tests of curvature in AI-capability trends.
No confirmatory claim is made by anything in this file.  Extends fsim.NullSim with: logistic/superexp truths, even dates, noise scale,
model x family interaction (crossed effects), a suite-ceiling (censoring) arm, and the test battery (iid, model-level bootstrap,
hierarchical task/run bootstrap, crossed model x task bootstrap, horizon-level parametric bootstrap)."""
import numpy as np, fcore as fc, fsim, datetime as dt
from scipy import stats

T0 = fc.T0


class Sim:
    """cfg keys: truth in exp|quad|logi ; rr (rate ratio, quad) ; um,ks (logistic inflection frac of span, steepness*span) ; noise (x sigma_m) ;
    smf (model x family interaction SD, log2 min) ; delta (shift of whole trajectory, log2 min) ; dates in real|even ; clip (bool)"""
    def __init__(self, D, b_model, P, cfg):
        self.cfg = cfg
        if cfg.get('dates', 'real') == 'even':
            o = D.order; lo, hi = min(D.dates), max(D.dates); M = D.M
            nd = list(D.dates)
            for r, i in enumerate(o):
                nd[i] = lo + dt.timedelta(days=int(round(r * (hi - lo).days / (M - 1))))
            D = fc.Design(D.names, nd, D.x, D.fam, D.n, D.kk, D.w)
        self.D = D; self.b = np.asarray(b_model, float)
        self.P = P; self.sm = P['sigma_m'] * cfg.get('noise', 1.0); self.sj = P['sigma_j']; self.phi = P['phi']
        self.a0 = P['a0'] + cfg.get('delta', 0.0); self.rate = fsim.RATE_NULL
        self.tmin = D.t.min(); self.span = D.t.max() - D.t.min(); self.smf = cfg.get('smf', 0.0)
        self.xmax = float(D.x.max()); self.clip = bool(cfg.get('clip', False))

    def true_L(self, t):
        u = t - self.tmin; c = self.cfg; tr = c.get('truth', 'exp'); G = self.rate * self.span
        if tr == 'exp':
            return self.a0 + self.rate * u
        if tr == 'quad':   # instantaneous rate rises linearly by factor rr, same total gain as null
            rr = c['rr']; r_s = self.rate * 2.0 / (1.0 + rr)
            return self.a0 + r_s * u + 0.5 * (rr - 1.0) * r_s / self.span * u ** 2
        if tr == 'logi':   # S-curve in log-horizon, same total gain as null
            um = c['um'] * self.span; k = c['ks'] / self.span
            s = lambda v: 1 / (1 + np.exp(-v))
            return self.a0 + G * (s(k * (u - um)) - s(-k * um)) / (s(k * (self.span - um)) - s(-k * um))
        raise ValueError(tr)

    def draw(self, rng):
        D = self.D
        L = self.true_L(D.t) + rng.normal(0, self.sm, D.M)
        F = rng.normal(size=D.F); g = rng.normal(size=D.K)
        j = self.sj * (np.sqrt(self.phi) * F[D.fam] + np.sqrt(1 - self.phi) * g)
        Lmk = L[:, None] + (self.smf * rng.normal(size=(D.M, D.F))[:, D.fam] if self.smf > 0 else 0.0)
        z = self.b[:, None] * (D.x[None, :] + j[None, :] - Lmk)
        p = fc._sig(z)
        kk = rng.binomial(D.n.astype(np.int64), p).astype(float)
        return fc.Design(D.names, D.dates, D.x, D.fam, D.n, kk, D.w)

    def obs(self, h):
        return np.minimum(h, self.xmax) if self.clip else h


def _quad(D, h, wts, mask=None):
    """weighted (multiplicity) quadratic OLS on masked set; returns coef2 (...,), n"""
    m = wts if mask is None else wts * mask
    c, n, _ = fc.quad_fit(D.t, h, m)
    return c[..., 2], n


def sota_w(D, h, cm):
    """SOTA mask restricted to sampled models (cm>0); unsampled never set the running max."""
    hm = np.where(cm > 0, h, -np.inf)
    return fc.sota_mask(hm, D) & (cm > 0)


def model_boot(D, h, B, rng, min_n=4):
    """model-level (pairs) bootstrap over models of the fixed fitted horizons.  returns dict for all-models and SOTA"""
    M = D.M; cm = rng.multinomial(M, np.full(M, 1.0 / M), size=B).astype(float)
    hh = np.broadcast_to(h, (B, M))
    ca, na = _quad(D, hh, cm)
    msk = sota_w(D, hh, cm)
    cs, ns = _quad(D, hh, cm, msk)
    # count of DISTINCT sota models for validity
    ok_s = msk.sum(-1) >= 4
    return ca, np.where(ok_s, cs, np.nan)


def _ci(v, min_frac=0.5, B=None):
    v = v[~np.isnan(v)]
    if len(v) < min_frac * (B or len(v)) or len(v) < 20: return (np.nan, np.nan)
    return tuple(np.percentile(v, [2.5, 97.5]))


def hb_sota_all(D, sim, B, rng, chunk=100):
    qs = np.full(B, np.nan); qa = np.full(B, np.nan)
    for s in range(0, B, chunk):
        bb = min(chunk, B - s); Nb, Sb = fc.hb_weights(D, bb, rng)
        h, _, _ = fc.horizons_of(D, Sb, Nb); h = sim.obs(h)
        one = np.ones((bb, D.M)); mask = fc.sota_mask(h, D)
        c, n, _ = fc.quad_fit(D.t, h, mask); qs[s:s + bb] = np.where(n >= 4, c[:, 2], np.nan)
        ca, _, _ = fc.quad_fit(D.t, h, one); qa[s:s + bb] = ca[:, 2]
    return qs, qa


def crossed_boot(D, sim, B, rng, chunk=100):
    """two-way (task x model) crossed 'pigeonhole' bootstrap: model multiplicities cm ~ Multinomial(M) AND task multiplicities
    (family -> task cluster, as in hb) drawn independently; each model's horizon is refit on the resampled task set with its own
    observed success counts (no run-level resampling).  Percentile CI of the t^2 coefficient over all / SOTA models."""
    M = D.M; qs = np.full(B, np.nan); qa = np.full(B, np.nan)
    for s in range(0, B, chunk):
        bb = min(chunk, B - s)
        cf = rng.multinomial(D.F, np.full(D.F, 1.0 / D.F), size=bb); ct = np.zeros((bb, D.K))
        for f in range(D.F):
            idx = np.where(D.fam == f)[0]
            if len(idx): ct[:, idx] = rng.multinomial(len(idx), np.full(len(idx), 1.0 / len(idx)), size=bb)
        mT = cf[:, D.fam] * ct
        Nb = mT[:, None, :] * D.n[None]; Sb = mT[:, None, :] * D.kk[None]
        h, _, _ = fc.horizons_of(D, Sb, Nb); h = sim.obs(h)
        cm = rng.multinomial(M, np.full(M, 1.0 / M), size=bb).astype(float)
        ca, _ = _quad(D, h, cm); qa[s:s + bb] = ca
        msk = sota_w(D, h, cm); cs, _ = _quad(D, h, cm, msk)
        qs[s:s + bb] = np.where(msk.sum(-1) >= 4, cs, np.nan)
    return qs, qa


def param_boot_sota(D, sim, h, B, rng):
    """horizon-level parametric (Monte-Carlo) null test for the SOTA curvature: fit a LINE to all-model horizons, simulate B datasets
    h* = line + N(0, resid sd), applying the same ceiling clip if the suite has one, recompute the SOTA quad coef.  Calibrates the
    selection effect directly (the estimand of the SOTA test is NOT zero under the exponential null).  returns (c_obs, p_up, p_dn, p_two)."""
    t = D.t; A = np.stack([np.ones_like(t), t - T0], 1)
    cf = np.linalg.lstsq(A, h, rcond=None)[0]; res = h - A @ cf; s = np.sqrt((res ** 2).sum() / (len(h) - 2))
    mask = fc.sota_mask(h, D); c_obs = fc.quad_fit(t, h, mask)[0][2]
    hs = sim.obs(A @ cf + rng.normal(0, s, (B, D.M)))
    ms = fc.sota_mask(hs, D); c, n, _ = fc.quad_fit(t, hs, ms)
    c = c[:, 2][n >= 4]
    pu = (1 + (c >= c_obs).sum()) / (len(c) + 1); pd = (1 + (c <= c_obs).sum()) / (len(c) + 1)
    return float(c_obs), float(pu), float(pd), float(min(1.0, 2 * min(pu, pd)))


def run_tests(D, sim, rng_seq, B_hb=400, B_xb=300, B_mb=2000, B_pb=1999):
    r_mb, r_hb, r_xb, r_pb = [np.random.default_rng(s) for s in rng_seq.spawn(4)]
    h, _, _ = fc.horizons_of(D); h = sim.obs(h); out = {}
    mask = fc.sota_mask(h, D)
    ti = fc.t_iid(D, h, mask); ta = fc.t_iid(D, h, np.ones(D.M, bool))
    out['iid_sota_p'] = ti['p']; out['iid_sota_c'] = ti['coef']; out['nS'] = ti['nS']
    out['iid_all_p'] = ta['p']; out['iid_all_c'] = ta['coef']
    ca, cs = model_boot(D, h, B_mb, r_mb)
    out['mb_all_lo'], out['mb_all_hi'] = _ci(ca, B=B_mb); out['mb_sota_lo'], out['mb_sota_hi'] = _ci(cs, B=B_mb)
    qs, qa = hb_sota_all(D, sim, B_hb, r_hb)
    out['hb_sota_lo'], out['hb_sota_hi'] = _ci(qs, B=B_hb); out['hb_all_lo'], out['hb_all_hi'] = _ci(qa, B=B_hb)
    qs, qa = crossed_boot(D, sim, B_xb, r_xb)
    out['xb_sota_lo'], out['xb_sota_hi'] = _ci(qs, B=B_xb); out['xb_all_lo'], out['xb_all_hi'] = _ci(qa, B=B_xb)
    c_obs, pu, pd, p2 = param_boot_sota(D, sim, h, B_pb, r_pb)
    out['pb_sota_c'] = c_obs; out['pb_sota_pup'] = pu; out['pb_sota_pdn'] = pd; out['pb_sota_p'] = p2
    out['sd_all'] = float(np.std(h, ddof=1)); out['hmax'] = float(h.max()); out['xmax'] = sim.xmax
    out['frac_at_ceiling'] = float((h >= sim.xmax - 1e-9).mean()) if sim.clip else 0.0
    return out
