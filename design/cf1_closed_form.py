"""CF1 (PLAN.md Amendment CF1): closed-form (quadrature) mean-field E[beta2 of record-only fit] vs direct Gaussian simulator, 8 schedules.
Run: PY design/cf1_closed_form.py"""
import json, os, math, datetime as dt, numpy as np
F = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
real = json.load(open(os.path.join(F, "real_data", "out", "real_v10.json")))
d = sorted(dt.date.fromisoformat(r[1]) for r in real["model_horizons"]); t_real = np.array([(x - d[0]).days for x in d], float) / 365.25
n = len(t_real); span = 6.776180698151951; r = 1.7392857142857143; s = 0.94268798828125; REPS = 40000
assert abs(t_real[-1] - span) < 1e-9, t_real[-1]
u = np.arange(n) / (n - 1)
SCHED = dict(real=t_real, even=np.linspace(0, span, n), reflected=np.sort(span - t_real),
             late_g0_5=span * u ** 0.5, late_g0_75=span * u ** 0.75, early_g1_5=span * u ** 1.5, early_g2=span * u ** 2.0,
             bursty=span * np.concatenate([np.linspace(0, .1, 11), np.linspace(.45, .55, 11), np.linspace(.9, 1, 11)]))
z = np.linspace(-10, 10, 8001); dz = z[1] - z[0]; phi = np.exp(-z * z / 2) / math.sqrt(2 * math.pi)
Phi = lambda x: 0.5 * (1 + np.vectorize(math.erf)(x / math.sqrt(2)))
def closed_form(t):
    p = np.zeros(n); m = np.zeros(n)
    for i in range(n):
        prod = np.ones_like(z)
        for j in range(i): prod *= Phi(z + r * (t[i] - t[j]) / s)
        w = phi * prod; p[i] = w.sum() * dz; m[i] = (z * w).sum() * dz / p[i]
    tc = t - t.mean(); X = np.stack([np.ones(n), tc, tc ** 2], 1); W = p
    beta = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (W * (s * m)))
    return float(beta[2]), float(p.sum())
out = dict(reps=REPS, rows={}); prev = json.load(open(os.path.join(F, "paper", "schedule_illustration.json")))["rows"]
for k, (nm, tt) in enumerate(SCHED.items()):
    cf, ER = closed_form(tt)
    X = np.stack([np.ones_like(tt), tt - tt.mean(), (tt - tt.mean()) ** 2], 1); rng = np.random.default_rng(np.random.SeedSequence([4714, k]))
    y = r * tt + rng.normal(0, s, (REPS, n)); pm = np.full_like(y, -np.inf); pm[:, 1:] = np.maximum.accumulate(y, axis=1)[:, :-1]; rec = y > pm
    cs = np.full(REPS, np.nan)
    for i in range(REPS):
        mk = rec[i]
        if mk.sum() >= 4: cs[i] = np.linalg.lstsq(X[mk], y[i, mk], rcond=None)[0][2]
    v = ~np.isnan(cs); mean = float(cs[v].mean()); se = float(cs[v].std(ddof=1) / np.sqrt(v.sum()))
    tol = max(0.15 * abs(mean), 2 * se); ok = abs(cf - mean) <= tol; sg = (cf > 0) == (mean > 0)
    out["rows"][nm] = dict(cf=cf, sim=mean, se=se, rel_err=(cf - mean) / mean, tol=tol, pass_=bool(ok), sign_ok=bool(sg), n_valid=int(v.sum()),
                           sim_mean_records=float(rec.sum(1).mean()), cf_mean_records=ER, prev_sim=prev.get(nm, {}).get("mean_beta2_sota"))
    print(nm, out["rows"][nm], flush=True)
npass = sum(r_["pass_"] for r_ in out["rows"].values()); nsign = sum(r_["sign_ok"] for r_ in out["rows"].values())
out["n_pass"] = npass; out["n_sign"] = nsign; out["bar_met"] = bool(npass >= 7 and nsign == 8)
print("pass", npass, "sign", nsign, "BAR", out["bar_met"])
json.dump(out, open(os.path.join(F, "design", "cf1_out.json"), "w"), indent=1)
