"""EXPLORATORY design-stage summary of results/cells/*: per cell x test rejection rate (two-sided + upward one-sided) with Clopper-Pearson,
size-adjusted power (critical value = null-quantiles of the SAME cell family's null), and a verdict on 'any test with ~5% size and useful power'.
Usage: python3 analyze_design.py [results_dir]   -> writes summary.md / summary.json in that dir.  No confirmatory claim."""
import sys, os, json, glob, numpy as np
from scipy import stats
R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
def cp(k, n, a=0.05):
    return (0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1), 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k))
def load():
    cells = {}
    for d in sorted(glob.glob(f'{R}/cells/*')):
        cells[os.path.basename(d)] = [json.loads(l) for f in sorted(glob.glob(d + '/c*.jsonl')) for l in open(f)]
    return cells
CI = ['mb_all', 'mb_sota', 'hb_sota', 'hb_all', 'xb_all', 'xb_sota']
PV = {'iid_sota': ('iid_sota_p', 'iid_sota_c'), 'iid_all': ('iid_all_p', 'iid_all_c')}
def rej(rows, t):
    """returns (two_sided_bool, up_bool, valid_mask)"""
    if t in PV:
        p = np.array([r[PV[t][0]] for r in rows], float); c = np.array([r[PV[t][1]] for r in rows], float); ok = ~np.isnan(p)
        return p < 0.05, (p < 0.1) & (c > 0), ok
    if t == 'pb_sota':
        pu = np.array([r['pb_sota_pup'] for r in rows], float); pd = np.array([r['pb_sota_pdn'] for r in rows], float); p = np.array([r['pb_sota_p'] for r in rows], float)
        return p < 0.05, pu < 0.05, ~np.isnan(p)
    lo = np.array([r[t + '_lo'] for r in rows], float); hi = np.array([r[t + '_hi'] for r in rows], float); ok = ~np.isnan(lo)
    return (lo > 0) | (hi < 0), lo > 0, ok
TESTS = ['iid_sota', 'iid_all', 'mb_all', 'mb_sota', 'hb_sota', 'hb_all', 'xb_all', 'xb_sota', 'pb_sota']
def zstat(rows, t):
    """a scalar statistic per replicate for size-adjusted power (+ = curvature upward)"""
    if t in PV: return np.array([r[PV[t][1]] for r in rows], float) / np.maximum(1e-9, np.array([abs(r[PV[t][1]]) / max(1e-9, stats.t.isf(r[PV[t][0]] / 2, 20)) for r in rows]))
    if t == 'pb_sota': return np.array([stats.norm.ppf(1 - np.clip(r['pb_sota_pup'], 1e-6, 1 - 1e-6)) for r in rows])
    lo = np.array([r[t + '_lo'] for r in rows], float); hi = np.array([r[t + '_hi'] for r in rows], float)
    return (lo + hi) / np.maximum(hi - lo, 1e-9)       # centre / width ~ z/3.92
def main():
    cells = load(); S = {}
    for name, rows in cells.items():
        S[name] = {'n': len(rows), 'mean_nS': float(np.mean([r['nS'] for r in rows])), 'frac_at_ceiling': float(np.mean([r['frac_at_ceiling'] for r in rows])), 'tests': {}}
        for t in TESTS:
            two, up, ok = rej(rows, t); n = int(ok.sum()); k2 = int(two[ok].sum()); ku = int(up[ok].sum())
            S[name]['tests'][t] = dict(n=n, rej2=k2 / n if n else None, cp2=cp(k2, n) if n else None, rej_up=ku / n if n else None, cp_up=cp(ku, n) if n else None)
    # size-adjusted power: threshold = null z quantiles of the matching null (same noise/dates/smf/clip settings)
    PAIR = {}
    for nm in S:
        if nm.startswith('A_sup') or nm.startswith('A_logi'): PAIR[nm] = 'A_null_n' + nm.split('_n')[1] if '_n0' in nm else 'A_null_exp'
        elif nm.startswith('B_sup'): PAIR[nm] = 'B_null_mf1'
        elif nm.startswith('C_sup'): PAIR[nm] = 'C_null_clip' + nm.split('clip')[1]
        elif nm.startswith('D_'): PAIR[nm] = 'D_null_even'
    for nm, nl in PAIR.items():
        if nm not in cells or nl not in cells: continue
        for t in TESTS:
            zn = zstat(cells[nl], t); za = zstat(cells[nm], t); zn = zn[~np.isnan(zn)]; za = za[~np.isnan(za)]
            if len(zn) < 100 or len(za) == 0: continue
            S[nm]['tests'][t]['null_cell'] = nl; S[nm]['tests'][t]['adj_power_up'] = float((za > np.quantile(zn, 0.95)).mean())
            S[nm]['tests'][t]['adj_power_2'] = float(((za > np.quantile(zn, 0.975)) | (za < np.quantile(zn, 0.025))).mean())
    json.dump(S, open(f'{R}/summary.json', 'w'), indent=1)
    L = ['# F design-stage size/power map -- EXPLORATORY, synthetic data only, no confirmatory claim', '',
         'Cell cells = rejection rate (two-sided 5%) [Clopper-Pearson 95%]; "up" = one-sided upward 5% (CI lower > 0 uses a 2.5% tail).', '']
    for blk in 'ABCD':
        L += [f'## Block {blk}', '', '| cell | n | ' + ' | '.join(TESTS) + ' |', '|---|---|' + '---|' * len(TESTS)]
        for nm in S:
            if not nm.startswith(blk + '_'): continue
            row = []
            for t in TESTS:
                x = S[nm]['tests'][t]
                if x['n'] == 0: row.append('-'); continue
                s = f"{100*x['rej2']:.1f} [{100*x['cp2'][0]:.1f},{100*x['cp2'][1]:.1f}]"
                if 'adj_power_2' in x: s += f" adj {100*x['adj_power_2']:.0f}"
                row.append(s)
            L.append(f"| {nm} | {S[nm]['n']} | " + ' | '.join(row) + ' |')
        L.append('')
    # verdict: nominal size = CP interval of base null contains 5% (and within [3.5,6.5]); useful power = >=80% at rr=2 (raw) in the same design
    L += ['## Verdict screen (EXPLORATORY)', '', 'size ok := CP95 on A_null_exp contains 5%; power ok := rate-ratio-2 power >= 80% (raw) in A_sup_rr2.', '',
          '| test | size A_null_exp | size ok | power rr2 | power ok | adj power rr2 | size ok in B/C/D nulls |', '|---|---|---|---|---|---|---|']
    for t in TESTS:
        a = S.get('A_null_exp', {}).get('tests', {}).get(t); p = S.get('A_sup_rr2', {}).get('tests', {}).get(t)
        if not a or not p or a['n'] == 0: continue
        so = a['cp2'][0] <= 0.05 <= a['cp2'][1]; po = p['rej2'] >= 0.8
        oth = [nm for nm in S if '_null' in nm and not nm.startswith('A_null_exp') and S[nm]['tests'][t]['n'] and S[nm]['tests'][t]['cp2'][0] <= 0.05 <= S[nm]['tests'][t]['cp2'][1]]
        L.append(f"| {t} | {100*a['rej2']:.1f}% | {so} | {100*p['rej2']:.1f}% | {po} | {100*p.get('adj_power_2', float('nan')):.0f}% | {', '.join(oth) or 'none'} |")
    open(f'{R}/summary.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
if __name__ == '__main__': main()
