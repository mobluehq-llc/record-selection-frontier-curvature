"""Holdout (PLAN): models released after 2025-11-30 exist in the later METR release time-horizon-1-1 (different, larger task suite, 228 tasks).
Within v1.1: fit exponential (linear) and quadratic on pre-cutoff SOTA models; compare post-cutoff models' log2 horizon with the forecast (95% prediction interval, linear).
Also T-hb (B=400) on the pre-cutoff v1.1 models and on all v1.1 models (post-hoc, descriptive). Seed SeedSequence([33, 2000000])."""
import sys, json, datetime as dt, numpy as np
from scipy import stats
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import fcore as fc
H = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/holdout_data'
R = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/results'
cut = dt.date(2025, 11, 30)
Dall = fc.load_real(runs_path=f'{H}/runs_v1_1.jsonl', dates_path=f'{H}/release_dates_main.yaml')
h, _, _ = fc.horizons_of(Dall)
out = dict(models=[(n, str(d), float(x)) for n, d, x in zip(Dall.names, Dall.dates, h)])
pre = np.array([d <= cut for d in Dall.dates]); post = ~pre
# SOTA on pre-cutoff models
idx = np.where(pre)[0]
sub = fc.Design([Dall.names[i] for i in idx], [Dall.dates[i] for i in idx], Dall.x, Dall.fam, Dall.n[idx], Dall.kk[idx], Dall.w[idx])
hp = h[idx]; ms = fc.sota_mask(hp, sub); ts, ys = sub.t[ms], hp[ms]
n = len(ys); A = np.stack([np.ones(n), ts - fc.T0], 1); c = np.linalg.lstsq(A, ys, rcond=None)[0]; s = np.sqrt(((ys - A @ c) ** 2).sum() / (n - 2))
out['pre_cutoff_sota'] = [sub.names[i] for i in sub.order if ms[i]]
out['pre_linear'] = dict(n=n, slope_doublings_per_yr=float(c[1]), doubling_days=float(365.25 / c[1]), resid_sd=float(s))
tq = fc.quad_fit(sub.t, hp, ms)[0]; out['pre_quad_coef'] = float(tq[2])
XtXi = np.linalg.inv(A.T @ A); hold = []
for i in np.where(post)[0]:
    a_ = np.array([1, Dall.t[i] - fc.T0]); pred = a_ @ c; se = s * np.sqrt(1 + a_ @ XtXi @ a_); tcrit = stats.t.ppf(0.975, n - 2)
    qpred = float(np.array([1, Dall.t[i] - fc.T0, (Dall.t[i] - fc.T0) ** 2]) @ tq)
    hold.append(dict(model=Dall.names[i], date=str(Dall.dates[i]), observed_log2h=float(h[i]), linear_forecast=float(pred), pi95=[float(pred - tcrit * se), float(pred + tcrit * se)],
                     above_upper_pi=bool(h[i] > pred + tcrit * se), below_lower_pi=bool(h[i] < pred - tcrit * se), quad_forecast=qpred, observed_minus_linear=float(h[i] - pred)))
out['holdout'] = hold
rng = np.random.default_rng(np.random.SeedSequence([33, 2000000]))
out['hb_pre_cutoff_v1_1'] = fc.t_hb(sub, 400, rng, h0=hp)
out['hb_all_v1_1_posthoc'] = fc.t_hb(Dall, 400, rng, h0=h)
json.dump(out, open(f'{R}/F_holdout.json', 'w'), indent=1, default=str); print(json.dumps(out, indent=1, default=str))
