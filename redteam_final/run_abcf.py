"""Pre-registered checks A (proxy dates), B (GPT-2 imputed rows), C (same-day ties), F (developer influence); spec: PREREG_CHATGPT_FINAL_112426.md.
Run: python3 run_abcf.py   -> out_abcf.json + printed tables.  Frozen code in ../design is imported, not modified."""
import os, sys, json, datetime as dt, numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(F, 'design')); sys.path.insert(0, os.path.join(F, 'real_data'))
import fcore as fc, fdesign3 as f3
RP = json.load(open(os.path.join(F, 'real_data', 'out', 'real_v10.json'))); sv = json.load(open(os.path.join(F, 'results', 'F_simulator_validation.json')))['params']
RATE, SIG = sv['rate_null'], sv['sigma_m']; REPS = 40000
names = [m[0] for m in RP['model_horizons']]; dates0 = [dt.date.fromisoformat(m[1]) for m in RP['model_horizons']]; h0 = np.array([m[2] for m in RP['model_horizons']])
DEV = __import__('cluster_test').DEV
PROX = {'davinci-002 (GPT-3)': 0, 'gpt-3.5-turbo-instruct': 0}
def years(ds): return np.array([(d - min(ds)).days for d in ds], float) / 365.25
def order(ds, nm, rule):
    if rule == 'rev': return sorted(range(len(ds)), key=lambda i: (ds[i], [-ord(c) for c in nm[i]]))
    return sorted(range(len(ds)), key=lambda i: (ds[i], nm[i]))
def rec_flags(y, ds, nm, rule='name'):
    """y (..., M) in model order -> bool records in model order. rules: name (frozen pipeline), rev, group (one record per date: the day's maximum if it beats all earlier days)."""
    o = order(ds, nm, rule); yo = y[..., o]; M = len(o)
    if rule == 'group':
        days = [ds[i] for i in o]; flag = np.zeros(yo.shape, bool); prev = np.full(yo.shape[:-1], -np.inf); i = 0
        while i < M:
            j = i
            while j < M and days[j] == days[i]: j += 1
            blk = yo[..., i:j]; mx = blk.max(-1); arg = blk.argmax(-1)   # argmax picks first maximal; exact ties have prob 0
            win = mx > prev
            for k in range(j - i): flag[..., i + k] = win & (arg == k)
            prev = np.maximum(prev, mx); i = j
    else:
        cm = np.maximum.accumulate(yo, axis=-1); flag = np.ones(yo.shape, bool); flag[..., 1:] = yo[..., 1:] > cm[..., :-1]
    out = np.zeros_like(flag); out[..., o] = flag; return out
def quad2(t, y, m):
    tc = t[m] - t[m].mean(); X = np.stack([np.ones_like(tc), tc, tc * tc], 1); return np.linalg.lstsq(X, y[m], rcond=None)[0][2]
def req(b2, span, rate):
    q = b2 * span / rate; return (1 + q) / (1 - q) if abs(q) < 1 else float('nan')
def observed(ds, nm, h, rule='name', rate=None):
    t = years(ds); span = t.max() - t.min(); R = f3.Reg(t); b2, ols_t, hc3_t = R.stats_(h); rate_lin = float(np.polyfit(t, h, 1)[0]); m = rec_flags(h, ds, nm, rule)
    cs = quad2(t, h, m) if m.sum() >= 4 else float('nan')
    return dict(M=len(h), n_rec=int(m.sum()), records=[nm[i] for i in order(ds, nm, rule) if m[i]], span=float(span), lin_rate=rate_lin, beta2_all=float(b2), hc3_t=float(hc3_t), hc3_p_up=float(stats.t.sf(hc3_t, R.df)),
                beta2_rec=float(cs), req_all=req(b2, span, rate_lin), req_rec=req(cs, span, rate_lin))
def sim(ds, nm, Z, rule='name', keep=None):
    keep = list(range(len(ds))) if keep is None else keep; ds = [ds[i] for i in keep]; nm = [nm[i] for i in keep]; t = years(ds); span = t.max() - t.min()
    y = RATE * t + Z[:, keep]; m = rec_flags(y, ds, nm, rule); cs = np.full(len(y), np.nan)
    for i in range(len(y)):
        if m[i].sum() >= 4: cs[i] = quad2(t, y[i], m[i])
    v = ~np.isnan(cs); R = f3.Reg(t); ba = y @ R.A[2]; mb = float(cs[v].mean()); return dict(M=len(ds), span=float(span), n_valid=int(v.sum()), mean_records=float(m.sum(1).mean()), beta2_rec=mb, se_rec=float(cs[v].std(ddof=1) / np.sqrt(v.sum())), req_rec=req(mb, span, RATE),
                beta2_all=float(ba.mean()), se_all=float(ba.std(ddof=1) / np.sqrt(len(y))))
out = {}
# gate: reproduce registered observed statistics
g = observed(dates0, names, h0); assert abs(g['beta2_all'] - 0.1385) < 1e-3 and abs(g['hc3_p_up'] - 0.0058) < 5e-4 and abs(g['beta2_rec'] - RP['pb']['sota_c']) < 1e-6, g
out['gate'] = g; print('GATE ok', g['beta2_all'], g['hc3_p_up'], g['beta2_rec'], g['n_rec'])
Z = np.random.default_rng(np.random.SeedSequence([4714, 0])).normal(0, SIG, (REPS, len(names)))
# ---- A: proxy dates
sc = {'S0 original': dict(d={}), 'S1 availability (davinci 2023-08-22, instruct 2023-09-18, unverified)': dict(d={'davinci-002 (GPT-3)': dt.date(2023, 8, 22), 'gpt-3.5-turbo-instruct': dt.date(2023, 9, 18)}),
      'S1b availability, earliest documented (instruct 2023-07-06)': dict(d={'davinci-002 (GPT-3)': dt.date(2023, 8, 22), 'gpt-3.5-turbo-instruct': dt.date(2023, 7, 6)}),
      'S2 proxy anchors excluded': dict(drop=True)}
out['A'] = {}
for k, s in sc.items():
    ds = [s.get('d', {}).get(n, d) for n, d in zip(names, dates0)]; keep = [i for i, n in enumerate(names) if not (s.get('drop') and n in PROX)]
    ob = observed([ds[i] for i in keep], [names[i] for i in keep], h0[keep]); si = sim(ds, names, Z, keep=keep); out['A'][k] = dict(observed=ob, sim=si)
    print('A', k, '| sim rec beta2 %.4f (%.4f) r_eq %.2f all %.4f recs %.1f | obs all %.3f p_up %.4f rec %.3f req_all %.2f req_rec %.2f nrec %d' % (si['beta2_rec'], si['se_rec'], si['req_rec'], si['beta2_all'], si['mean_records'], ob['beta2_all'], ob['hc3_p_up'], ob['beta2_rec'], ob['req_all'], ob['req_rec'], ob['n_rec']))
# ---- B: GPT-2 imputed rows
rows = [json.loads(l) for l in open(f'{fc.DATA}/runs_v1_0.jsonl')]; kept = [r for r in rows if not str(r['run_id']).startswith('fake_')]; imp = [r for r in rows if str(r['run_id']).startswith('fake_')]
out['B'] = dict(n_imputed=len(imp), aliases=sorted({r['alias'] for r in imp}), by_source={s: sum(1 for r in imp if r['task_source'] == s) for s in ('HCAST', 'RE-Bench')}, all_zero=all(r['score_binarized'] == 0 for r in imp), gpt2_real_swaa=sum(1 for r in kept if r['alias'] == 'GPT-2'))
tmp = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'runs_noimputed.jsonl'); open(tmp, 'w').write('\n'.join(json.dumps(r) for r in kept) + '\n')
D1 = fc.load_real(cutoff=dt.date(2025, 11, 30), runs_path=tmp); h1, _, _ = fc.horizons_of(D1)
Dall = fc.load_real(cutoff=dt.date(2025, 11, 30)); hall, _, _ = fc.horizons_of(Dall); assert np.allclose(sorted(hall), sorted(h0), atol=1e-6)
nm1 = D1.names; ds1 = D1.dates; assert sorted(nm1) == sorted(names)
ob = observed(ds1, nm1, h1); out['B']['without_imputed'] = ob; out['B']['gpt2_h_with'] = float(h0[names.index('GPT-2')]); out['B']['gpt2_h_without'] = float(h1[nm1.index('GPT-2')])
out['B']['horizon_shift_max_other'] = float(max(abs(h1[nm1.index(n)] - h0[names.index(n)]) for n in names if n != 'GPT-2'))
print('B imputed', out['B']['n_imputed'], out['B']['by_source'], 'GPT-2 h', out['B']['gpt2_h_with'], '->', out['B']['gpt2_h_without'], 'max other shift', out['B']['horizon_shift_max_other']); print('B refit', {k: ob[k] for k in ('beta2_all', 'hc3_p_up', 'beta2_rec', 'req_all', 'req_rec', 'n_rec')})
# ---- C: same-day ties
out['C'] = dict(observed={}, sim={})
for rule in ('name', 'rev', 'group'):
    o_ = observed(dates0, names, h0, rule); out['C']['observed'][rule] = o_; print('C obs', rule, o_['n_rec'], o_['beta2_rec'], o_['req_rec'], o_['records'][-4:])
rng = np.random.default_rng(np.random.SeedSequence([4714, 9])); rr_ = []
for _ in range(100):   # random within-day orders: relabel the names within each date block
    nm = list(names)
    for d in set(dates0):
        idx = [i for i in range(len(names)) if dates0[i] == d]
        if len(idx) > 1: sh = [names[i] for i in rng.permutation(idx)]; [nm.__setitem__(i, s) for i, s in zip(idx, sh)]
    rr_.append(observed(dates0, nm, h0)['n_rec'])
out['C']['observed']['random_within_day_nrec_counts'] = {int(k): int((np.array(rr_) == k).sum()) for k in set(rr_)}; print('C random within-day n_rec', out['C']['observed']['random_within_day_nrec_counts'])
for rule in ('name', 'rev', 'group'):
    si = sim(dates0, names, Z, rule); out['C']['sim'][rule] = si; print('C sim', rule, 'beta2_rec %.4f (%.4f) req %.2f recs %.2f' % (si['beta2_rec'], si['se_rec'], si['req_rec'], si['mean_records']))
perm = np.random.default_rng(np.random.SeedSequence([4714, 5])).permutation(len(names)); si = sim([dates0[i] for i in perm], [names[i] for i in perm], Z[:, perm], 'name'); out['C']['sim']['name_input_shuffled'] = si
print('C sim name, input rows shuffled (same draws per model): beta2_rec %.6f (identical expected: %.6f)' % (si['beta2_rec'], out['C']['sim']['name']['beta2_rec']))
# ---- F: developer influence
t = years(dates0); R = f3.Reg(t); dev = np.array([DEV[n] for n in names]); out['F'] = dict(loo={}, leverage={})
for d in sorted(set(dev)):
    k = [i for i in range(len(names)) if dev[i] != d]
    if len(k) < 6: continue
    o_ = observed([dates0[i] for i in k], [names[i] for i in k], h0[k]); out['F']['loo'][d] = dict(n_removed=len(names) - len(k), **{x: o_[x] for x in ('M', 'beta2_all', 'hc3_t', 'hc3_p_up', 'beta2_rec', 'n_rec', 'req_all')}); print('F LOO', d, out['F']['loo'][d])
tc = t - t.mean(); X0 = np.stack([np.ones_like(tc), tc], 1); q = tc * tc; res = q - X0 @ np.linalg.lstsq(X0, q, rcond=None)[0]; share = res ** 2 / (res ** 2).sum()
out['F']['leverage']['by_model'] = {n: float(s) for n, s in sorted(zip(names, share), key=lambda x: -x[1])}; out['F']['leverage']['by_developer'] = {d: float(share[dev == d].sum()) for d in sorted(set(dev))}
out['F']['leverage']['top5_models'] = list(out['F']['leverage']['by_model'].items())[:5]; print('F leverage by developer', out['F']['leverage']['by_developer']); print('F top5', out['F']['leverage']['top5_models'])
# contribution to beta2 (signed): res_i * y_i / sum res^2
contrib = res * h0 / (res ** 2).sum(); out['F']['leverage']['signed_contribution_to_beta2_by_developer'] = {d: float(contrib[dev == d].sum()) for d in sorted(set(dev))}; print('F contribution', out['F']['leverage']['signed_contribution_to_beta2_by_developer'], 'sum', contrib.sum())
json.dump(out, open(os.path.join(HERE, 'out_abcf.json'), 'w'), indent=1, default=float)
