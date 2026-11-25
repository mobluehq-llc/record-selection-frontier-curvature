"""ONE-SHOT real-data run (PLAN): T-hb on METR v1.0 real data, cutoff 2025-11-30, B=400, seed SeedSequence([33, 1000000]). Refuses to run twice."""
import sys, os, json, time, datetime as dt, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import fcore as fc
R = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/results'
out = f'{R}/F_real.csv'
assert not os.path.exists(out), 'one-shot already used'
assert fc.sha256(f'{fc.DATA}/runs_v1_0.jsonl') == fc.RUNS_SHA
t0 = time.time()
D = fc.load_real(cutoff=dt.date(2025, 11, 30)); h, a, b = fc.horizons_of(D)
mask = fc.sota_mask(h, D); ti = fc.t_iid(D, h)
tb = fc.t_hb(D, 400, np.random.default_rng(np.random.SeedSequence([33, 1000000])), h0=h)
c, n, _ = fc.quad_fit(D.t, h, mask)
cl, _ = fc.lin_ssr(D.t, h, mask)
row = dict(models=D.M, n_sota=int(n), quad_coef_per_yr2=float(c[2]), hb_ci_lo=tb['lo'], hb_ci_hi=tb['hi'], hb_reject_5pct=tb['reject'], hb_nvalid=tb['nvalid'],
           iid_F_p=ti['p'], lin_slope_doublings_per_yr=float(cl[1]), lin_doubling_days=float(365.25 / cl[1]), hb_ci_all_models_lo=tb['lo_all'], hb_ci_all_models_hi=tb['hi_all'],
           hb_reject_all_models=tb['reject_all'], runs_sha256=fc.sha256(f'{fc.DATA}/runs_v1_0.jsonl'), runtime_s=time.time() - t0)
import csv
with open(out, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(list(row)); w.writerow(list(row.values()))
json.dump(dict(row, sota=[D.names[i] for i in D.order if mask[i]]), open(f'{R}/F_real.json', 'w'), indent=1)
print(json.dumps(row, indent=1)); print([D.names[i] for i in D.order if mask[i]])
