import sys, csv, json, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import fcore as fc
R = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/results'
rows = list(csv.DictReader(open(f'{R}/F_size.csv'))); n = len(rows)
def b(v): return v in ('True', '1')
out = {}; L = []
def rep(name, k, n):
    lo, hi = fc.cp(k, n); out[name] = dict(k=k, n=n, size=k / n, cp_lo=lo, cp_hi=hi); L.append(f'{name}: {k}/{n} = {100*k/n:.2f}%  CP95 [{100*lo:.2f}, {100*hi:.2f}]%')
rep('T-iid (SOTA, F-test t^2, two-sided 5%)', sum(float(r['p_iid']) < 0.05 for r in rows if r['p_iid'] != 'nan'), n)
rep('T-hb (SOTA, B=400 percentile 95% CI excludes 0)', sum(b(r['hb_rej']) for r in rows), n)
rep('[secondary] T-hb one-sided upward (lo>0)', sum(b(r['hb_rej_up']) for r in rows), n)
rep('[secondary] T-iid all-models regression', sum(float(r['p_iid_all']) < 0.05 for r in rows if r['p_iid_all'] != 'nan'), n)
rep('[secondary] T-hb all-models regression', sum(b(r['hb_rej_all']) for r in rows), n)
L.append(f"datasets with nS<4 (T-iid undefined): {sum(int(r['nS'])<4 for r in rows)}; hb invalid(<50% valid reps): {sum(int(r['hb_nvalid'])<200 for r in rows)}; mean nSOTA {np.mean([int(r['nS']) for r in rows]):.1f}")
a = out['T-iid (SOTA, F-test t^2, two-sided 5%)']; h = out['T-hb (SOTA, B=400 percentile 95% CI excludes 0)']
v1 = 'BAR1_PASS' if (a['size'] > 0.10 and a['cp_lo'] > 0.07) else 'BAR1_FAIL'
v2 = 'BAR2_PASS' if 0.03 <= h['size'] <= 0.07 else 'BAR2_FAIL'
L.append(f'VERDICT bar(1) T-iid size>10% & CP-lower>7%: {v1}'); L.append(f'VERDICT bar(2) T-hb size in [3,7]%: {v2}  (CP interval [{100*h["cp_lo"]:.2f},{100*h["cp_hi"]:.2f}]% {"inside" if h["cp_lo"]>=0.03 and h["cp_hi"]<=0.07 else "not inside"} [3,7])')
open(f'{R}/F_size_summary.txt', 'w').write('\n'.join(L) + '\n'); json.dump(out, open(f'{R}/F_size_summary.json', 'w'), indent=1); print('\n'.join(L))
