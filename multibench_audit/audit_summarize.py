"""Summarize manifest -> results/audit_summary.json and AUDIT_RESULTS.md (refuses to overwrite)."""
import json, os, numpy as np, pandas as pd
from scipy import stats
import audit_run as ar, audit_core as ac
OUT_J = ar.RES + '/audit_summary.json'; OUT_M = ar.HERE + '/AUDIT_RESULTS.md'
assert not os.path.exists(OUT_J) and not os.path.exists(OUT_M), 'refusing to overwrite'
S = json.load(open(ar.SERIES_JSON)); ser = S['eligible'] + ([S['reference']] if S['reference'].get('eligible') else [])
rows = []
for l in open(ar.MANIFEST):
    j = json.loads(l)
    for r in j['rows']: rows.append(dict(r, series=j['series'], construction=j['construction']))
D = pd.DataFrame(rows)
D['iid_rej'] = D.iid_p < 0.05; D['mb_ok'] = D.mb_lo.notna(); D['mb_rej'] = (D.mb_lo > 0) | (D.mb_hi < 0)
D['cl_ok'] = D.cl_lo.notna(); D['cl_rej'] = (D.cl_lo > 0) | (D.cl_hi < 0); D['iid_ok'] = D.iid_p.notna()
D['mb_cov'] = (D.mb_lo <= D.c) & (D.c <= D.mb_hi); D['cl_cov'] = (D.cl_lo <= D.c) & (D.c <= D.cl_hi)
def cp(k, n):
    if n == 0: return (np.nan, np.nan)
    return (stats.beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0, stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0)
MINVALID = 500
per = []
for s in ser:
    g = D[D.series == s['index']]; row = dict(index=s['index'], file=s['file'], M=s['models'], rec=s['records'], months=s['months'], orgs=s['orgs'], ref=s['index'] == 900)
    for c in ac.CONSTR:
        h = g[g.construction == c]
        for stat in ('iid', 'mb', 'cl'):
            v = h[h[stat + '_ok']]; n = len(v); k = int(v[stat + '_rej'].sum())
            row[f'{stat}_{c}_n'] = n; row[f'{stat}_{c}_size'] = k / n if n else np.nan; row[f'{stat}_{c}_cp'] = cp(k, n)
    for c, direction in (('P2p', 1), ('P2m', -1)):
        h = g[g.construction == c]
        for stat in ('iid', 'mb', 'cl'):
            v = h[h[stat + '_ok']]
            if stat == 'iid': pw = ((v.iid_p < 0.05) & (np.sign(v.iid_coef) == direction)).mean() if len(v) else np.nan
            else: pw = (((v[stat + '_lo'] > 0) if direction > 0 else (v[stat + '_hi'] < 0))).mean() if len(v) else np.nan
            row[f'{stat}_{c}_power'] = pw
        for stat in ('mb', 'cl'):
            v = h[h[stat + '_ok']]; row[f'{stat}_{c}_cov'] = v[stat + '_cov'].mean() if len(v) else np.nan; row[f'{stat}_{c}_covn'] = len(v)
        vv = h[h.coef.notna()]; cc = float(h.c.iloc[0]) if len(h) else np.nan
        row[f'{c}_relbias'] = float((vv.coef - vv.c).mean() / abs(cc)) if len(vv) and cc else np.nan
    per.append(row)
P = pd.DataFrame(per); M = P[~P.ref]
def measured(stat): return M[(M[f'{stat}_N0_n'] >= MINVALID)]
# Bar 1
m1 = measured('iid'); b1 = int(((m1.iid_N0_size > 0.10) & m1.iid_N0_cp.apply(lambda x: x[0] > 0.07)).sum()); n1 = len(m1)
bar1 = b1 >= 0.5 * n1
# Bar 2
m2 = measured('mb'); in37 = lambda sz, c: bool(c[0] <= 0.07 and c[1] >= 0.03)
ok2 = m2.apply(lambda r: in37(r.mb_N0_size, r.mb_N0_cp) and (r.mb_P1_n >= MINVALID) and in37(r.mb_P1_size, r.mb_P1_cp), axis=1); b2 = int(ok2.sum()); n2 = len(m2)
bar2 = b2 >= 0.8 * n2
# Bar 3 (pooled over measured series)
def pooled_cov(c, stat='mb'):
    h = D[(D.construction == c) & (D.series != 900) & D[stat + '_ok']]
    return float(h[stat + '_cov'].mean()), len(h)
cov_p, ncp = pooled_cov('P2p'); cov_m, ncm = pooled_cov('P2m')
rb = pd.concat([M.P2p_relbias, M.P2m_relbias]).abs().dropna(); bias_pool = float(rb.mean())
bar3 = (cov_p >= 0.90) and (cov_m >= 0.90) and bias_pool < 0.25
# Falsifier
over = M.apply(lambda r: any((r[f'mb_{c}_n'] >= MINVALID) and (r[f'mb_{c}_size'] > 0.10) and (r[f'mb_{c}_cp'][0] > 0.07) for c in ('N0', 'P1')), axis=1)
fal_frac = float(over.sum()) / max(1, len(M)); fal = fal_frac >= 0.25 or min(cov_p, cov_m) < 0.85
ch = json.load(open(ar.RES + '/audit_checks.json'))
ref = P[P.ref]; ref_mb = float(ref.mb_N0_size.iloc[0]) if len(ref) else np.nan; ref_pass = bool(len(ref) and 0.032 <= ref_mb <= 0.072)
# exploratory spearman
ex = {}
for nm, col in (('M', 'M'), ('records', 'rec'), ('months_per_model', None)):
    x = M[col] if col else M.months / M.M
    r, p = stats.spearmanr(x, M.mb_N0_size, nan_policy='omit'); ex[nm] = (float(r), float(p))
n_cl_unmeasured = int((M.cl_N0_n < MINVALID).sum())
summ = dict(bar1=dict(met=b1, of=n1, pass_=bool(bar1)), bar2=dict(met=b2, of=n2, pass_=bool(bar2)),
            bar3=dict(cov_P2p=cov_p, cov_P2m=cov_m, n=[ncp, ncm], abs_relbias_pooled=bias_pool, pass_=bool(bar3)),
            falsifier=dict(oversized_mb_frac=fal_frac, min_cov=min(cov_p, cov_m), triggered=bool(fal)),
            checks=ch, ref_mb_N0_size=ref_mb, ref_pass=ref_pass, exploratory_spearman_mb_N0_size=ex, cl_unmeasured_series=n_cl_unmeasured,
            n_series=len(M), unmeasured_mb=int(len(M) - len(m2)))
json.dump(summ, open(OUT_J, 'w'), indent=1, default=str)
f = lambda x: 'nan' if pd.isna(x) else f'{100*x:.1f}'
L = ['# F multi-benchmark planted-trend audit: RESULTS (run 2026-11-24; pre-registration PLAN.md + PLAN_AMENDMENT_1.md)\n']
L.append(f'Series: {len(M)} eligible Epoch benchmark series (+ METR reference, not in the bar denominators). 1000 permutations x 4 constructions each. Counts below are met / not met / not measured.\n')
L.append('## Verdicts\n')
L.append(f'- **Bar 1** (T-iid size >10% with CP-lower >7% on N0 in >=50% of series): {b1}/{n1} series -> **{"MET" if bar1 else "NOT MET"}**; not measured {len(M)-n1}.')
L.append(f'- **Bar 2** (T-mb size CP-overlaps [3,7]% on N0 and P1 in >=80% of series): {b2}/{n2} -> **{"MET" if bar2 else "NOT MET"}**; not measured {len(M)-n2}.')
L.append(f'- **Bar 3** (pooled T-mb coverage of planted coefficient >=0.90 both signs; pooled |relative bias| <25%): coverage P2+ {cov_p:.3f}, P2- {cov_m:.3f}; |rel bias| {bias_pool:.2f} -> **{"MET" if bar3 else "NOT MET"}**.')
L.append(f'- **Falsifier** (T-mb oversized in >=25% of series, or pooled coverage <0.85): oversized in {100*fal_frac:.0f}% of series, min coverage {min(cov_p,cov_m):.3f} -> **{"TRIGGERED" if fal else "not triggered"}**.')
L.append(f'- Instrument checks: (i) no-selection T-iid size {100*ch["i_noselection_tiid_size"]:.1f}% -> {"pass" if ch["i_pass"] else "FAIL"}; (ii) zero planting reproduces N0 -> {"pass" if ch["ii_zero_plant_equals_N0"] else "FAIL"}; (iii) METR reference T-mb N0 size {100*ref_mb:.1f}% vs F simulator base 5.2% +/-2 -> {"pass" if ref_pass else "FAIL (see note)"}.')
L.append(f'- T-cl not measured (<8 orgs or <{MINVALID} valid): {n_cl_unmeasured} series.\n')
L.append('## Per-series table (size % [Clopper-Pearson 95%]; N0 = permutation null, P1 = planted linear)\n')
L.append('| series | M | rec | iid N0 | mb N0 | mb P1 | cl N0 | cl P1 | mb pw P2+ | mb pw P2- | mb cov P2+ | mb cov P2- | cl cov P2+ |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
cell_ = lambda r, k: f'{f(r[k+"_size"])} [{f(r[k+"_cp"][0])},{f(r[k+"_cp"][1])}]'
for _, r in P.iterrows():
    L.append(f'| {r.file.replace("_external.csv","").replace(".csv","")}{" (REF)" if r.ref else ""} | {r.M} | {r.rec} | {cell_(r,"iid_N0")} | {cell_(r,"mb_N0")} | {cell_(r,"mb_P1")} | {cell_(r,"cl_N0")} | {cell_(r,"cl_P1")} | {f(r.mb_P2p_power)} | {f(r.mb_P2m_power)} | {f(r.mb_P2p_cov)} | {f(r.mb_P2m_cov)} | {f(r.cl_P2p_cov)} |')
L.append('\n## Exploratory (Spearman of T-mb N0 size against): ' + '; '.join(f'{k} rho={v[0]:.2f} (p={v[1]:.2f})' for k, v in ex.items()) + '. Saturation-rule sensitivity: not run (not measured).')
open(OUT_M, 'w').write('\n'.join(L) + '\n'); P.to_json(ar.RES + '/audit_per_series.json', orient='records', indent=1)
print('\n'.join(L[:12]))
