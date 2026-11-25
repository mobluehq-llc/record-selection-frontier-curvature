"""Null simulator + calibration metrics (idea F)."""
import numpy as np, fcore as fc
RATE_NULL = 365.25 / 210.0      # doublings per year (doubling time 210 d)


def metrics(D, h=None, a=None, b=None, min_common=40):
    if h is None:
        h, a, b = fc.horizons_of(D)
    t = D.t
    A = np.stack([np.ones_like(t), t - fc.T0], 1)
    c = np.linalg.lstsq(A, h, rcond=None)[0]; res = h - A @ c
    sd_all = np.sqrt((res ** 2).sum() / (len(h) - 2))
    sm = fc.sota_mask(h, D); ts, hs = t[sm], h[sm]
    As = np.stack([np.ones_like(ts), ts - fc.T0], 1); cs = np.linalg.lstsq(As, hs, rcond=None)[0]
    sd_sota = np.sqrt(((hs - As @ cs) ** 2).sum() / (len(hs) - 2))
    # task-level residuals vs each model's own fitted logistic
    has = D.n > 0
    s = np.where(has, D.kk / np.maximum(D.n, 1), np.nan)
    p = fc._sig(a[:, None] + b[:, None] * D.x[None])
    r = np.where(has, s - p, np.nan)
    # mean pairwise correlation of residuals over common tasks; skip models whose residual variance ~ 0
    cors = []
    for i in range(D.M):
        for j in range(i + 1, D.M):
            ok = has[i] & has[j]
            if ok.sum() < min_common: continue
            ri, rj = r[i, ok], r[j, ok]
            if ri.std() < 1e-9 or rj.std() < 1e-9: continue
            cors.append(np.corrcoef(ri, rj)[0, 1])
    xc = float(np.mean(cors))
    # family ICC of task-mean residual (one-way ANOVA estimator)
    rb = np.nanmean(r, axis=0)
    fam = D.fam; F = D.F
    grp = [rb[fam == f] for f in range(F) if (fam == f).sum() > 0]
    k = np.array([len(g) for g in grp], float); N = k.sum()
    gm = np.concatenate(grp).mean()
    ssb = sum(len(g) * (g.mean() - gm) ** 2 for g in grp); ssw = sum(((g - g.mean()) ** 2).sum() for g in grp)
    msb = ssb / (len(grp) - 1); msw = ssw / (N - len(grp)); k0 = (N - (k ** 2).sum() / N) / (len(grp) - 1)
    icc = float((msb - msw) / (msb + (k0 - 1) * msw))
    return dict(sd_all=float(sd_all), sd_sota=float(sd_sota), crosscorr=xc, icc=icc, slope_all=float(c[1]))


class NullSim:
    def __init__(self, D, b_model, a0, sigma_m, sigma_j, phi, rate=RATE_NULL, truth='exp', rate_ratio=2.0, span=None):
        self.D = D; self.b = np.asarray(b_model, float); self.a0 = a0; self.sm = sigma_m; self.sj = sigma_j; self.phi = phi
        self.rate = rate; self.truth = truth; self.rr = rate_ratio
        self.span = span if span is not None else (D.t.max() - D.t.min())
        self.tmin = D.t.min()

    def true_L(self, t):
        u = t - self.tmin
        if self.truth == 'exp':
            return self.a0 + self.rate * u
        # alternative: instantaneous rate rises linearly by factor rr over the window, mean rate == self.rate
        r_s = self.rate * 2.0 / (1.0 + self.rr)       # start rate; end rate = rr*r_s ; mean = rate
        return self.a0 + r_s * u + 0.5 * (self.rr - 1.0) * r_s / self.span * u ** 2

    def draw(self, rng):
        D = self.D
        L = self.true_L(D.t) + rng.normal(0, self.sm, D.M)
        F = rng.normal(size=D.F); g = rng.normal(size=D.K)
        j = self.sj * (np.sqrt(self.phi) * F[D.fam] + np.sqrt(1 - self.phi) * g)
        z = self.b[:, None] * (D.x[None, :] + j[None, :] - L[:, None])
        p = fc._sig(z)
        kk = rng.binomial(D.n.astype(np.int64), p).astype(float)
        return fc.Design(D.names, D.dates, D.x, D.fam, D.n, kk, D.w)
