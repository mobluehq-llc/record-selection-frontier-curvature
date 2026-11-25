import sys, csv, collections
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import fcore as fc
R = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/results'
rows = list(csv.DictReader(open(f'{R}/F_power_null_raw.csv')))
g = collections.defaultdict(list)
for r in rows: g[(int(r['cell']), int(r['N']), int(r['mult']))].append(r)
out = [['cell', 'N_models', 'task_mult', 'n_tasks', 'reps', 'power_T-hb', 'hb_cp_lo', 'hb_cp_hi', 'power_T-iid', 'iid_cp_lo', 'iid_cp_hi', 'mean_nSOTA']]
L = []
for (c, N, m), rs in sorted(g.items()):
    n = len(rs); kh = sum(r['hb_rej'] == 'True' for r in rs); ki = sum(r['iid_rej'] == 'True' for r in rs)
    a, b = fc.cp(kh, n); c2, d2 = fc.cp(ki, n); ms = sum(int(r['nS']) for r in rs) / n
    out.append([c, N, m, 170 * m, n, f'{kh/n:.3f}', f'{a:.3f}', f'{b:.3f}', f'{ki/n:.3f}', f'{c2:.3f}', f'{d2:.3f}', f'{ms:.1f}'])
csv.writer(open(f'{R}/F_power_null_size.csv', 'w', newline='')).writerows(out)
for r in out: print(*r, sep='\t')
