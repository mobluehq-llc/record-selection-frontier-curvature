"""Instrument checks (i) and (ii) from PLAN section 5. Writes results/audit_checks.json (refuses to overwrite)."""
import json, os, numpy as np, pandas as pd
import audit_core as ac, audit_run as ar
OUT = ar.RES + '/audit_checks.json'
assert not os.path.exists(OUT), 'refusing to overwrite'
res = {}
# (i) synthetic series with no selection: every model is used (no record rule); T-iid F-test on t^2 over ALL points, y iid noise
rej = 0; n = 1000
for rep in range(n):
    rng = np.random.default_rng(np.random.SeedSequence([44, 777, rep]))
    M = 60; t = np.sort(rng.random(M)) * 4; y = rng.normal(size=M); span = t.max() - t.min()
    r = ac.t_iid((t - t[0]) / span, y, span); rej += (r[1] < 0.05)
lo = float(__import__('scipy.stats', fromlist=['beta']).beta.ppf(0.025, rej, n - rej + 1)) if rej else 0.0
res['i_noselection_tiid_size'] = rej / n; res['i_pass'] = bool(0.03 <= rej / n <= 0.07)
# (ii) planting c=0,s=0 must reproduce N0 exactly (same rejections) on three series, 100 permutations
S = json.load(open(ar.SERIES_JSON))['eligible']; same = True; tot = 0
for si in (0, 8, 10):
    s = S[si]; d = ar.get_frame(s); sd = float(d.y.std()); span = float(d.t.max() - d.t.min()); codes_all = pd.factorize(d.o.values)[0]
    for rep in range(100):
        t, order = ac.permuted_frame(d, rep, s['index']); y0 = d.y.values[order]; codes = codes_all[order]
        a = ac.run_one(t, y0, codes, [44, s['index'], rep, 0, 1], span)
        y1, _ = ac.planted(t, y0, 'P2p', 0.0, span)       # amplitude 0 through the planting code path
        b = ac.run_one(t, y1, codes, [44, s['index'], rep, 0, 1], span)
        rj = lambda r: (r['iid_p'] < 0.05, r['mb_lo'] > 0 or r['mb_hi'] < 0, r['cl_lo'] > 0 or r['cl_hi'] < 0)
        same &= (rj(a) == rj(b)) and np.allclose(a['coef'], b['coef'], equal_nan=True); tot += 1
res['ii_zero_plant_equals_N0'] = bool(same); res['ii_n'] = tot
json.dump(res, open(OUT, 'w'), indent=1); print(res)
