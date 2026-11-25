"""Scores corrective amendment 2: reproduction gate, then one-sided upward size per series. Writes results/audit_onesided_summary.json + prints markdown."""
import json, numpy as np
from scipy import stats
R = 'results/'
S = json.load(open(R + 'audit_series.json')); names = {s['index']: s['file'].replace('_external.csv', '').replace('.csv', '') for s in S['eligible'] + [S['reference']]}
man = {}
for l in open(R + 'audit_manifest.jsonl'):
    j = json.loads(l)
    for r in j['rows']: man[(j['series'], j['construction'], r['rep'])] = r
raw = {}
for l in open(R + 'audit_onesided_raw.jsonl'):
    j = json.loads(l)
    for r in j['rows']: raw[(j['series'], j['construction'], r['rep'])] = r
# reproduction gate
bad = 0; n = 0; mx = 0.0
for k, r in raw.items():
    m = man[k]; n += 1
    for key, lo, hi in (('mb', 'mb_lo', 'mb_hi'), ('cl', 'cl_lo', 'cl_hi')):
        a = r[key]; sl, sh = m[lo], m[hi]
        if a is None: ok = (sl != sl); 
        else: ok = (sl == sl) and abs(a[0] - sl) < 1e-9 and abs(a[3] - sh) < 1e-9; mx = max(mx, abs(a[0] - sl) if sl == sl else 0)
        if not ok: bad += 1
print('REPRO GATE: rows', n, 'mismatches', bad, 'max |lo diff|', mx)
assert bad == 0, 'MISMATCH reproduction failed'
def cp(k, n):
    lo = stats.beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0; hi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return lo, hi
def verdict(k, n):
    lo, hi = cp(k, n); p = k / n
    if p > 0.10 and lo > 0.07: return 'OVER'
    if hi >= 0.03 and lo <= 0.07: return 'in'
    if hi < 0.03: return 'under'
    return 'mid'
out = {}; rows = []
for sidx in sorted(names):
    row = dict(name=names[sidx])
    for c in ('N0', 'P1'):
        iid2 = iid1 = mb2 = mb1 = cl2 = cl1 = niid = nmb = ncl = 0; mbup25 = 0
        for rep in range(1000):
            m = man[(sidx, c, rep)]; r = raw[(sidx, c, rep)]
            if m['iid_p'] == m['iid_p']:
                niid += 1; iid2 += m['iid_p'] < 0.05; iid1 += (m['iid_coef'] > 0 and m['iid_p'] / 2 < 0.05)
            if r['mb']:
                nmb += 1; mb2 += (r['mb'][0] > 0 or r['mb'][3] < 0); mb1 += r['mb'][1] > 0; mbup25 += r['mb'][0] > 0
            if r['cl']:
                ncl += 1; cl2 += (r['cl'][0] > 0 or r['cl'][3] < 0); cl1 += r['cl'][1] > 0
        row[c] = dict(iid=dict(n=niid, two=iid2, one=iid1), mb=dict(n=nmb, two=mb2, one=mb1, up25=mbup25), cl=dict(n=ncl, two=cl2, one=cl1))
    out[sidx] = row
json.dump(out, open(R + 'audit_onesided_summary.json', 'w'), indent=1)
def pct(d): return (100.0 * d['one'] / d['n']) if d['n'] else float('nan')
ser = [s for s in sorted(names) if s != 900]
def count(stat, key='one'):
    over = inn = nm = und = mid = 0
    for s in ser:
        v = []
        for c in ('N0',):
            d = out[s][c][stat]
            if d['n'] < 500: v.append(None)
            else: v.append(verdict(d[key], d['n']))
        if v[0] is None: nm += 1
        elif v[0] == 'OVER': over += 1
        elif v[0] == 'in': inn += 1
        elif v[0] == 'under': und += 1
        else: mid += 1
    return dict(oversized=over, consistent=inn, undersized_CPhi_below_3=und, other=mid, not_measured=nm)
def both_in(stat):
    k = 0
    for s in ser:
        ok = True
        for c in ('N0', 'P1'):
            d = out[s][c][stat]
            if d['n'] < 500 or verdict(d['one'], d['n']) != 'in': ok = False
        k += ok
    return k
print('\n| series | iid 2s N0 | iid 1s N0 | mb 2s N0 | mb 1s N0 | mb 1s P1 | cl 1s N0 |\n|---|---|---|---|---|---|---|')
for s in sorted(names):
    o = out[s]; f = lambda d, k: ('%.1f' % (100 * d[k] / d['n'])) if d['n'] else 'nan'
    print('| %s | %s | %s | %s | %s | %s | %s |' % (names[s], f(o['N0']['iid'], 'two'), f(o['N0']['iid'], 'one'), f(o['N0']['mb'], 'two'), f(o['N0']['mb'], 'one'), f(o['P1']['mb'], 'one'), f(o['N0']['cl'], 'one')))
for stat in ('iid', 'mb', 'cl'):
    print(stat, 'N0 one-sided: oversized / consistent / not measured =', count(stat), '; two-sided =', count(stat, 'two'), '; consistent on both N0 and P1 (one-sided):', both_in(stat), 'of', len(ser))
m = out[900]; print('METR ref mb: N0 two-sided %.1f one-sided %.1f (2.5%% tail %.1f); P1 one-sided %.1f' % (100 * m['N0']['mb']['two'] / m['N0']['mb']['n'], pct(m['N0']['mb']), 100 * m['N0']['mb']['up25'] / m['N0']['mb']['n'], pct(m['P1']['mb'])), 'n', m['N0']['mb']['n'], 'CP', cp(m['N0']['mb']['one'], m['N0']['mb']['n']))
print('METR ref iid N0 two %.1f one %.1f' % (100 * m['N0']['iid']['two'] / m['N0']['iid']['n'], pct(m['N0']['iid'])))
