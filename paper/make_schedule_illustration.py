"""ILLUSTRATION (EXPLORATORY, not pre-registered, not the calibrated simulator; made for paper v2 on 2026-11-23 after an outside review asked
what makes the record-selection bias bend UPWARD).  Independent Gaussian model errors (SD = calibrated sigma_m) about an exactly exponential
trend, 33 models, same span and rate, three release schedules: the real dates, evenly spaced dates, and the real schedule reflected about the
window midpoint (dense early, sparse late).  Mean quadratic coefficient of the record-only fit (>= 4 records) and of the all-model fit.
Output: schedule_illustration.json.  Run: python3 -I make_schedule_illustration.py"""
import json, os, datetime as dt, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.dirname(HERE)
real = json.load(open(os.path.join(F, "real_data", "out", "real_v10.json"))); sv = json.load(open(os.path.join(F, "results", "F_simulator_validation.json")))["params"]
d = sorted(dt.date.fromisoformat(r[1]) for r in real["model_horizons"]); t = np.array([(x - d[0]).days for x in d], float) / 365.25
span = t[-1]; rate = sv["rate_null"]; s = sv["sigma_m"]; REPS = 40000
SCHED = dict(real=t, even=np.linspace(0, span, len(t)), reflected=np.sort(span - t))
res = dict(what="Gaussian schedule illustration, exponential truth, sigma = sigma_m", reps=REPS, rate=rate, span_years=float(span), sigma=s, seed="SeedSequence([4713, k])", rows={})
for k, (nm, tt) in enumerate(SCHED.items()):
    X = np.stack([np.ones_like(tt), tt - tt.mean(), (tt - tt.mean()) ** 2], 1); rng = np.random.default_rng(np.random.SeedSequence([4713, k]))
    y = rate * tt + rng.normal(0, s, (REPS, len(tt))); pm = np.full_like(y, -np.inf); pm[:, 1:] = np.maximum.accumulate(y, axis=1)[:, :-1]; rec = y > pm
    cs = np.full(REPS, np.nan)
    for i in range(REPS):
        m = rec[i]
        if m.sum() >= 4: cs[i] = np.linalg.lstsq(X[m], y[i, m], rcond=None)[0][2]
    ca = (y @ np.linalg.pinv(X).T)[:, 2]; v = ~np.isnan(cs); m_ = float(cs[v].mean()); q = m_ * span / rate
    res["rows"][nm] = dict(mean_beta2_sota=m_, se_sota=float(cs[v].std(ddof=1) / np.sqrt(v.sum())), n_valid=int(v.sum()), mean_records=float(rec.sum(1).mean()), rr_eq_sota=float((1 + q) / (1 - q)),
                           mean_beta2_all=float(ca.mean()), se_all=float(ca.std(ddof=1) / np.sqrt(REPS)))
    print(nm, res["rows"][nm])
json.dump(res, open(os.path.join(HERE, "schedule_illustration.json"), "w"), indent=1)
