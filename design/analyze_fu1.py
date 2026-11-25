"""EXPLORATORY follow-up-1 summary (idea F).  Usage: /usr/bin/python3 analyze_fu1.py <results_dir>  -> summary_fu1.md / summary_fu1.json
Reuses rej()/cp() of analyze_design.  Tests absent from a cell (cheap cells have no hb/xb) are skipped."""
import sys, os, json, glob, numpy as np
RD = sys.argv[1]; sys.argv = [sys.argv[0], RD]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_design as ad, grid_fu1 as g
TESTS = ad.TESTS
def zq(rows, t): return ad.zstat(rows, t)
def main():
    man = json.load(open(f'{RD}/manifest.json')); plan = man['plan']; S = {}; Z = {}
    for ci, c in enumerate(g.CELLS):
        d = f"{RD}/cells/{c['name']}"
        rows = [json.loads(l) for f in sorted(glob.glob(d + '/c*.jsonl')) for l in open(f)]
        if not rows: continue
        S[c['name']] = dict(n=len(rows), planned=plan.get(c['name']), M=rows[0].get('M'), tests={}); Z[c['name']] = rows
        for t in TESTS:
            key = t + '_p' if t.startswith('iid') else (t + '_pup' if t.startswith('pb') else t + '_lo')
            if key not in rows[0]: continue
            two, up, ok = ad.rej(rows, t); n = int(ok.sum()); k2 = int(two[ok].sum()); ku = int(up[ok].sum())
            S[c['name']]['tests'][t] = dict(n=n, rej2=k2 / n, cp2=ad.cp(k2, n), rej_up=ku / n, cp_up=ad.cp(ku, n))
    # size-adjusted power: matching null = same cfg with truth exp
    def nullname(nm):
        if nm.startswith('P_sup'): return {'P_sup_rr2': 'P_null_exp', 'P_sup_rr3': 'P_null_exp', 'P_sup_rr2_mf1': 'P_null_mf1'}[nm]
        if nm.startswith('M_sup_rr2_x'): return 'M_null_x' + nm.split('_x')[1]
        if nm.startswith('H_sup_rr2_x'): return 'H_null_x' + nm.split('_x')[1]
    for nm in S:
        nl = nullname(nm) if '_sup' in nm else None
        if not nl or nl not in S: continue
        for t in S[nm]['tests']:
            if t not in S[nl]['tests']: continue
            zn = zq(Z[nl], t); za = zq(Z[nm], t); zn = zn[~np.isnan(zn)]; za = za[~np.isnan(za)]
            if len(zn) < 100 or not len(za): continue
            S[nm]['tests'][t]['adj_power_2'] = float(((za > np.quantile(zn, .975)) | (za < np.quantile(zn, .025))).mean())
    json.dump(S, open(f'{RD}/summary_fu1.json', 'w'), indent=1)
    L = ['# F follow-up 1 -- EXPLORATORY, synthetic only', '', 'two-sided rejection % [CP95]; sup cells: "adj" = size-adjusted power %. n = completed/planned reps.', '']
    for blk, title in (('P_', 'Arm P (real design, cheap tests)'), ('M_', 'Arm M (model-count scaling, cheap tests)'), ('H_', 'Arm H (model-count scaling, incl. hb/xb)')):
        L += [f'## {title}', '', '| cell | M | n/plan | ' + ' | '.join(TESTS) + ' |', '|---|---|---|' + '---|' * len(TESTS)]
        for nm in S:
            if not nm.startswith(blk): continue
            row = []
            for t in TESTS:
                x = S[nm]['tests'].get(t)
                if not x: row.append('-'); continue
                s = f"{100*x['rej2']:.2f} [{100*x['cp2'][0]:.2f},{100*x['cp2'][1]:.2f}]"
                if 'adj_power_2' in x: s += f" adj {100*x['adj_power_2']:.0f}"
                row.append(s)
            L.append(f"| {nm} | {S[nm]['M']} | {S[nm]['n']}/{S[nm]['planned']} | " + ' | '.join(row) + ' |')
        L.append('')
    L += ['## M-trend rule (pre-stated): worse := CP lower(mfac=8) > CP upper(mfac=1) on the null cells', '', '| arm | test | rej2 x1 | rej2 x8 | verdict |', '|---|---|---|---|---|']
    for arm in ('M', 'H'):
        a, b = S.get(f'{arm}_null_x1'), S.get(f'{arm}_null_x8')
        if not a or not b: continue
        for t in TESTS:
            if t not in a['tests'] or t not in b['tests']: continue
            x, y = a['tests'][t], b['tests'][t]
            v = 'WORSE' if y['cp2'][0] > x['cp2'][1] else ('BETTER' if y['cp2'][1] < x['cp2'][0] else 'no detectable trend')
            L.append(f"| {arm} | {t} | {100*x['rej2']:.2f} | {100*y['rej2']:.2f} | {v} |")
    open(f'{RD}/summary_fu1.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
if __name__ == '__main__': main()
