"""EXPLORATORY design-stage, DESIGN AMENDMENT 2 (idea F).  Synthetic data only; no confirmatory claim.  Spec: AMENDMENT2.md.
Does NOT modify fcore.py / fdesign.py / fdesign_ext.py (frozen).  Adds (i) fixed-date all-model regression tests of the quadratic term
(OLS t, HC3 t, null-restricted wild bootstrap of the HC3 t, residual permutation), (ii) signed one-sided p-values for every test,
(iii) a clean Gaussian reference simulator and a no-task-jitter option for the stepwise ladder.
Convention everywhere: p_up = evidence for POSITIVE curvature (acceleration), p_dn = evidence for NEGATIVE curvature (deceleration)."""
import numpy as np, fcore as fc, fdesign
from scipy import stats

T0 = fc.T0


class Sim3(fdesign.Sim):
    """extra cfg keys: gauss (bool: horizons = true_L + N(0, sm^2) directly, no task outcomes), sjs (multiplier on the task-jitter SD sigma_j)."""
    def __init__(self, D, b_model, P, cfg):
        super().__init__(D, b_model, P, cfg); self.sj = self.sj * cfg.get('sjs', 1.0)

    def generate(self, rng):
        """returns (design used for the tests, observed log2 horizons per model)"""
        if self.cfg.get('gauss'):
            L = self.true_L(self.D.t) + rng.normal(0, self.sm, self.D.M)
            return self.D, self.obs(L)
        d = self.draw(rng); h, _, _ = fc.horizons_of(d)
        return d, self.obs(h)


# ------------------------------------------------------------------ fixed-date all-model regression (y on 1, t, t^2), t centred at the mean date
class Reg:
    def __init__(self, t):
        tc = np.asarray(t, float) - np.mean(t); self.M = len(tc)
        self.X = np.stack([np.ones_like(tc), tc, tc * tc], 1); self.XtXi = np.linalg.inv(self.X.T @ self.X)
        self.A = self.XtXi @ self.X.T; self.H = self.X @ self.A; self.hii = np.diag(self.H)
        X0 = self.X[:, :2]; self.H0 = X0 @ np.linalg.inv(X0.T @ X0) @ X0.T; self.h0 = np.diag(self.H0)
        self.df = self.M - 3

    def stats_(self, y):
        """y (..., M) -> (beta2, ols_t, hc3_t) (...,)"""
        b2 = y @ self.A[2]; res = y - y @ self.H            # H symmetric
        s2 = (res ** 2).sum(-1) / self.df
        ols_t = b2 / np.sqrt(np.maximum(s2 * self.XtXi[2, 2], 1e-300))
        v3 = ((self.A[2] ** 2) * (res / (1 - self.hii)) ** 2).sum(-1)
        hc3_t = b2 / np.sqrt(np.maximum(v3, 1e-300))
        return b2, ols_t, hc3_t


def _p_from_null(tobs, tnull):
    B = len(tnull)
    return (1 + (tnull >= tobs).sum()) / (B + 1), (1 + (tnull <= tobs).sum()) / (B + 1)


def reg_tests(R, y, rng_w, rng_p, B_w=499, B_p=999):
    out = {}
    b2, to, th = [float(v) for v in R.stats_(y)]
    out['reg_c'] = b2; out['ols_z'] = to; out['hc3_z'] = th
    out['ols_pup'] = float(stats.t.sf(to, R.df)); out['ols_pdn'] = float(stats.t.cdf(to, R.df))
    out['hc3_pup'] = float(stats.t.sf(th, R.df)); out['hc3_pdn'] = float(stats.t.cdf(th, R.df))
    y0 = R.H0 @ y; e0 = y - y0
    # null-restricted wild bootstrap, Rademacher weights, restricted residuals rescaled by 1/(1-h0_ii) (HC3-type), dates fixed
    v = rng_w.integers(0, 2, size=(B_w, R.M)) * 2.0 - 1.0
    ys = y0[None] + (e0 / (1 - R.h0))[None] * v
    tw = R.stats_(ys)[2]; out['wild_pup'], out['wild_pdn'] = [float(p) for p in _p_from_null(th, tw)]
    # residual permutation under the restricted (linear-trend) null; studentised by the OLS t
    idx = np.argsort(rng_p.random((B_p, R.M)), axis=1)
    yp = y0[None] + e0[idx]
    tp = R.stats_(yp)[1]; out['perm_pup'], out['perm_pdn'] = [float(p) for p in _p_from_null(to, tp)]
    return out


# ------------------------------------------------------------------ selection / existing cheap tests, now with signed p-values
def _boot_p(v, B, min_frac=0.5):
    v = v[~np.isnan(v)]
    if len(v) < min_frac * B or len(v) < 20: return np.nan, np.nan, len(v)
    return (1 + (v <= 0).sum()) / (len(v) + 1), (1 + (v >= 0).sum()) / (len(v) + 1), len(v)


def _z_from_pup(p):
    return float(stats.norm.ppf(1 - np.clip(p, 1e-9, 1 - 1e-9))) if not np.isnan(p) else np.nan


def run_cheap(D, sim, h, rng_seq, B_mb=2000, B_pb=1999, B_w=499, B_p=999):
    r_mb, r_pb, r_w, r_p = [np.random.default_rng(s) for s in rng_seq.spawn(4)]
    R = Reg(D.t); out = reg_tests(R, h, r_w, r_p, B_w, B_p)
    mask = fc.sota_mask(h, D); ti = fc.t_iid(D, h, mask)
    out['nS'] = ti['nS']; out['sota_c'] = ti['coef']
    if np.isnan(ti['p']): out['iid_sota_pup'] = out['iid_sota_pdn'] = out['iid_sota_z'] = np.nan
    else:
        pu = ti['p'] / 2 if ti['coef'] > 0 else 1 - ti['p'] / 2
        out['iid_sota_pup'] = pu; out['iid_sota_pdn'] = 1 - pu; out['iid_sota_z'] = float(np.sign(ti['coef']) * stats.t.isf(ti['p'] / 2, max(1, ti['nS'] - 3)))
    ca, cs = fdesign.model_boot(D, h, B_mb, r_mb)
    for nm, v in (('mb_all', ca), ('mb_sota', cs)):
        pu, pd, nv = _boot_p(v, B_mb); out[nm + '_pup'] = pu; out[nm + '_pdn'] = pd; out[nm + '_z'] = _z_from_pup(pu); out[nm + '_nvalid'] = nv
    c_obs, pu, pd, p2 = fdesign.param_boot_sota(D, sim, h, B_pb, r_pb)
    out['pb_sota_pup'] = pu; out['pb_sota_pdn'] = pd; out['pb_sota_z'] = _z_from_pup(pu)
    out['sd_all'] = float(np.std(h, ddof=1)); out['frac_at_ceiling'] = float((h >= sim.xmax - 1e-9).mean()) if sim.clip else 0.0
    return out


def run_expensive(D, sim, rng_seq, B_hb=400, B_xb=300):
    """adds the task-level hierarchical (hb) and crossed (xb) bootstraps with signed p-values"""
    r_hb, r_xb = [np.random.default_rng(s) for s in rng_seq.spawn(2)]
    out = {}
    qs, qa = fdesign.hb_sota_all(D, sim, B_hb, r_hb)
    for nm, v in (('hb_sota', qs), ('hb_all', qa)):
        pu, pd, nv = _boot_p(v, B_hb); out[nm + '_pup'] = pu; out[nm + '_pdn'] = pd; out[nm + '_z'] = _z_from_pup(pu)
    qs, qa = fdesign.crossed_boot(D, sim, B_xb, r_xb)
    for nm, v in (('xb_sota', qs), ('xb_all', qa)):
        pu, pd, nv = _boot_p(v, B_xb); out[nm + '_pup'] = pu; out[nm + '_pdn'] = pd; out[nm + '_z'] = _z_from_pup(pu)
    return out


def run_rep(sim, ci, rep, which, seed_tag=79):
    ss = np.random.SeedSequence([seed_tag, ci, rep]); s1, s2, s3 = ss.spawn(3)
    D, h = sim.generate(np.random.default_rng(s1))
    out = run_cheap(D, sim, h, s2)
    if which == 'all':
        # the horizons of the hb/xb bootstraps are refit from resampled task outcomes, so they need the drawn design D
        out.update(run_expensive(D, sim, s3))
    return out
