"""Pre-registered check D: one-sided OLS F test on records under N0 / P1 / PF, with the 90%-of-ceiling cut-off varied; spec PREREG_CHATGPT_FINAL_112426.md.
Run: python3 run_d.py  (frozen multibench_audit/audit_core.py imported, not modified; same permuted frames: seed [44, series, rep])."""
import os, sys, json, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.dirname(HERE); AU = os.path.join(F, 'multibench_audit'); sys.path.insert(0, AU)
import audit_core as ac
S = json.load(open(AU + '/results/audit_series.json')); series = S['eligible'] + [S['reference']]
def cp(k, n): return (stats.beta.ppf(.025, k, n - k + 1) if k else 0.0, stats.beta.ppf(.975, k + 1, n - k) if k < n else 1.0)
def verdict(k, n):
    if n < 500: return 'nm'
    lo, hi = cp(k, n); p = k / n
    if p > .10 and lo > .07: return 'OVER'
    if hi >= .03 and lo <= .07: return 'in'
    return 'under' if hi < .03 else 'mid'
man = {}
for l in open(AU + '/results/audit_manifest.jsonl'):
    j = json.loads(l)
    if j['construction'] in ('N0', 'P1'):
        for r in j['rows']: man[(j['series'], j['construction'], r['rep'])] = r
def frame(s, sat):
    ac.SAT = sat or 0.9
    d, ceil = ac.load_series(s['file'], s['col'], s['scale'], s['ceiling']); assert ac.sha256(f'{ac.DATA}/{s["file"]}') == s['sha256']
    d, _ = ac.prepare(d, ceil if sat else 0.0, transform=s['transform']); return d
res = {}; PERMS = 1000
for sat_name, sat in (('0.80', .80), ('0.90', .90), ('0.95', .95), ('none', None)):
    res[sat_name] = {}
    for s in series:
        d = frame(s, sat); sd = float(d.y.std()); span = float(d.t.max() - d.t.min()); t0 = d.t.min()
        slope = float(np.polyfit(d.t.values, d.y.values, 1)[0]); row = dict(models=len(d), fitted_slope_per_sd_span=slope * span / sd)
        for cons in ('N0', 'P1', 'PF'):
            if cons == 'PF' and slope <= 0: row[cons] = None; continue
            k_up = k_two = n_valid = 0
            for rep in range(PERMS):
                t, order = ac.permuted_frame(d, rep, s['index']); y0 = d.y.values[order]
                if cons == 'N0': y = y0
                elif cons == 'P1': y = y0 + 0.5 * sd / span * (t - t0)
                else: y = y0 + slope * (t - t0)
                rm = ac.running_max_records(y); u = (t - t0) / span; r = ac.t_iid(u[rm], y[rm], span)
                if r is None: continue
                n_valid += 1; k_two += r[1] < .05; k_up += (r[0] > 0 and r[1] / 2 < .05)
                if sat == .90 and cons in ('N0', 'P1'):
                    m = man[(s['index'], cons, rep)]; assert abs(m['iid_p'] - r[1]) < 1e-9 and abs(m['iid_coef'] - r[0]) < 1e-9, 'MISMATCH vs stored'   # reproduction gate
            row[cons] = dict(n_valid=n_valid, up=k_up, two=k_two, verdict_up=verdict(k_up, n_valid), rate_up=k_up / max(n_valid, 1), rate_two=k_two / max(n_valid, 1), undefined=PERMS - n_valid)
        res[sat_name][s['index']] = row
    print('SAT', sat_name, flush=True)
    for cons in ('N0', 'P1', 'PF'):
        rows = [(i, r[cons]) for i, r in res[sat_name].items() if i != 900 and r[cons]]; v = [x['verdict_up'] for _, x in rows]
        print('  %s: series %d, upward OVER %d, in %d, under %d, mid %d, not-measured %d; median one-sided %.3f, median undefined %d; METR ref up %.3f' % (cons, len(rows), v.count('OVER'), v.count('in'), v.count('under'), v.count('mid'), v.count('nm'),
              np.median([x['rate_up'] for _, x in rows]), np.median([x['undefined'] for _, x in rows]), (res[sat_name][900][cons] or {}).get('rate_up', float('nan'))))
json.dump(res, open(os.path.join(HERE, 'out_d.json'), 'w'), indent=1, default=float)
