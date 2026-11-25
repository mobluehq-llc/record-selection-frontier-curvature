"""ILLUSTRATION for Fig. 1 (not pre-registered, not the calibrated simulator; made for the paper on 2026-11-23).
Independent Gaussian model errors around an exactly exponential trend at the 33 real release dates:
y_m = a + r*t_m + N(0, sigma^2).  For each sigma: mean quadratic coefficient of the fit through the records (strict running maxima,
(date, name) order, >= 4 records) and through all models.  Output: bias_illustration.json.  Run: python3 -I make_bias_illustration.py"""
import json, os, datetime as dt, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.dirname(HERE)
real = json.load(open(os.path.join(F, "real_data", "out", "real_v10.json")))
sv = json.load(open(os.path.join(F, "results", "F_simulator_validation.json")))["params"]
rows = sorted(real["model_horizons"], key=lambda r: (r[1], r[0]))
d = [dt.date.fromisoformat(r[1]) for r in rows]
t = np.array([(x - d[0]).days for x in d], float) / 365.25
span = t[-1] - t[0]; rate = sv["rate_null"]; REPS = 40000
X = np.stack([np.ones_like(t), t - t.mean(), (t - t.mean()) ** 2], 1)

def qc(y, w):  # weighted quadratic coefficient per row
    out = np.full(len(y), np.nan)
    for i in range(len(y)):
        m = w[i]
        if m.sum() >= 4: out[i] = np.linalg.lstsq(X[m], y[i, m], rcond=None)[0][2]
    return out

res = dict(what="Gaussian illustration, independent errors, real dates, exponential truth", reps=REPS, rate=rate, span_years=float(span),
           seed="SeedSequence([4711, k])", rows=[])
for k, s in enumerate([0.1, 0.25, 0.5, 0.75, sv["sigma_m"], 1.25, 1.5, 2.0]):
    rng = np.random.default_rng(np.random.SeedSequence([4711, k]))
    y = rate * t + rng.normal(0, s, (REPS, len(t)))
    pm = np.full_like(y, -np.inf); pm[:, 1:] = np.maximum.accumulate(y, axis=1)[:, :-1]
    rec = y > pm
    cs = qc(y, rec); ca = (y @ np.linalg.pinv(X).T)[:, 2]
    v = ~np.isnan(cs); m = float(cs[v].mean()); q = m * span / rate
    res["rows"].append(dict(sigma=float(s), mean_beta2_sota=m, se_sota=float(cs[v].std(ddof=1) / np.sqrt(v.sum())), n_valid=int(v.sum()),
                            mean_records=float(rec.sum(1).mean()), rr_eq_sota=float((1 + q) / (1 - q)),
                            mean_beta2_all=float(ca.mean()), se_all=float(ca.std(ddof=1) / np.sqrt(REPS))))
    print(res["rows"][-1])
json.dump(res, open(os.path.join(HERE, "bias_illustration.json"), "w"), indent=1)
