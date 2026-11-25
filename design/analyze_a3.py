"""EXPLORATORY Design Amendment 3 analysis (idea F).  Usage: python3 analyze_a3.py <results_dir> [<a2_results_dir>]  -> summary_a3.md, counts_a3.csv.   Implements ONLY what AMENDMENT3.md section 3 prespecifies.
Tails (as A2): up5 := p_up<0.05 ; dn5 := p_dn<0.05 ; two5 := min(p_up,p_dn)<0.025.  Size bound: CP95 inside [3.5,6.5] % = OK, disjoint = OUT, else inconclusive."""
import sys, os, json, glob, csv, numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fcore as fc, fdesign3 as f3, grid_a3 as grid
RD = sys.argv[1]; RD2 = sys.argv[2] if len(sys.argv) > 2 else None
DATA = os.environ.get('FDATA', os.path.join(HERE, 'data')); fc.DATA = DATA
LO, HI = 3.5, 6.5
TESTS = ['ccl', 'tcl', 'mir', 'heck', 'ipw', 'audit', 'rrate', 'gap', 'contr', 'thr', 'sota']
KIND = {t: 'correction' for t in ('ccl', 'tcl', 'mir', 'heck', 'ipw', 'audit')}; KIND.update({t: 'DIAGNOSTIC' for t in ('rrate', 'gap', 'contr', 'thr')}); KIND['sota'] = 'reference (A2 pb_sota)'
BIAS = ['sota', 'mir', 'heck', 'ipw', 'audit']
rng = np.random.default_rng(20261124)
def cp(k, n, a=0.05):
    return (0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1), 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k))
def pct(k, n):
    if n == 0: return '-'
    lo, hi = cp(k, n); return f'{100*k/n:.2f} [{100*lo:.2f},{100*hi:.2f}]'
def verdict(k, n):
    if n == 0: return 'n/a'
    lo, hi = cp(k, n); return 'OK' if lo * 100 >= LO and hi * 100 <= HI else ('OUT' if hi * 100 < LO or lo * 100 > HI else 'inconclusive')
def load(rd):
    cells = {}
    for c in grid.CELLS:
        rows = [json.loads(l) for f in sorted(glob.glob(f"{rd}/cells/{c['name']}/c*.jsonl")) for l in open(f)]
        if rows: cells[c['name']] = rows
    return cells
def col(rows, key): return np.array([np.nan if r.get(key) is None else r.get(key) for r in rows], float)
def rules(rows, t):
    pu, pd = col(rows, t + '_pup'), col(rows, t + '_pdn'); ok = ~np.isnan(pu)
    return dict(ok=ok, up=(pu < .05) & ok, dn=(pd < .05) & ok, two=((pu < .025) | (pd < .025)) & ok)
P = json.load(open(f'{DATA}/F_simulator_validation.json'))['params']; D0 = fc.load_real(data=DATA); h0, _, b0 = fc.horizons_of(D0)
RATE = P['rate_null']; SPAN = float(D0.t.max() - D0.t.min())
def effect(cfg):
    # KNOWN ERROR, left as run (ERRATA.md 2026-11-23): h = 0.5 y makes these half-year SECANT rates, not endpoint rates, so the calendar table in
    # results_a3/summary_a3.md prints rr=2 as 304 -> 160 d (exact: 315 -> 157.5 d).  Descriptive table only; paper/make_numbers.py recomputes it exactly.
    s = f3.Sim3(D0, b0, P, cfg); t0 = s.tmin; h = 0.5
    r0 = (s.true_L(t0 + h) - s.true_L(t0)) / h; r1 = (s.true_L(t0 + SPAN) - s.true_L(t0 + SPAN - h)) / h
    return r0, r1, 365.25 / r0 if r0 > 0 else np.inf, 365.25 / r1 if r1 > 0 else np.inf
def rr_eq(b2): q = b2 * SPAN / RATE; return (1 + q) / (1 - q) if q < 1 else np.inf
def cutoffs(zc):
    zc = zc[~np.isnan(zc)]; return dict(up=np.quantile(zc, .95), dn=np.quantile(zc, .05), hi=np.quantile(zc, .975), lo=np.quantile(zc, .025))
def adj_rates(z, c):
    z = z[~np.isnan(z)]; n = len(z)
    return dict(up=(z > c['up']).sum(), dn=(z < c['dn']).sum(), two=((z > c['hi']) | (z < c['lo'])).sum(), n=n)
def main():
    cells = load(RD); G = {c['name']: c for c in grid.CELLS}; L = []
    nulls = [n for n in cells if G[n]['role'] in ('cal', 'val')]; alts = [n for n in cells if G[n]['role'] == 'alt']
    with open(f'{RD}/counts_a3.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['cell', 'role', 'planned', 'completed', 'test', 'n_valid', 'n_invalid', 'k_two', 'k_up', 'k_dn'])
        for nm, rows in cells.items():
            for t in TESTS:
                if t + '_pup' not in rows[0]: continue
                r = rules(rows, t); n = int(r['ok'].sum()); w.writerow([nm, G[nm]['role'], G[nm]['reps'], len(rows), t, n, len(rows) - n, int(r['two'].sum()), int(r['up'].sum()), int(r['dn'].sum())])
    L += ['# F Design Amendment 3 results -- EXPLORATORY, synthetic data only, no confirmatory claim', '', f'Bound: Clopper-Pearson 95% inside [{LO}, {HI}] % = OK; disjoint = OUT; else inconclusive. Rates % [CP95]. Counts k/n incl. invalid replicates: counts_a3.csv. Cells completed: ' + ', '.join(f'{n}:{len(r)}/{G[n]["reps"]}' for n, r in cells.items()), '']
    # ---- B1/B2 size
    L += ['## B1/B2 size under the exponential null (nominal reference; null_val cells)', '', '| test | kind | cell | n valid | up5 | two5 | dn5 | up verdict | two verdict |', '|---|---|---|---|---|---|---|---|---|']
    SV = {}
    for t in TESTS:
        for nm in [n for n in nulls if G[n]['role'] == 'val']:
            if t + '_pup' not in cells[nm][0]: continue
            r = rules(cells[nm], t); n = int(r['ok'].sum()); ku, kt, kd = int(r['up'].sum()), int(r['two'].sum()), int(r['dn'].sum())
            SV[(t, nm)] = (verdict(ku, n), verdict(kt, n))
            L.append(f'| {t} | {KIND[t]} | {nm} | {n} | {pct(ku,n)} | {pct(kt,n)} | {pct(kd,n)} | {SV[(t,nm)][0]} | {SV[(t,nm)][1]} |')
    L += ['', '### Classification (B1: size-valid = up AND two OK in R_null_val; B2: robust = also OK in E, K2, N50, MF1)', '', '| test | size-valid | robust |', '|---|---|---|']
    for t in TESTS:
        v = SV.get((t, 'R_null_val'));
        if not v: continue
        sv = v == ('OK', 'OK'); rob = sv and all(SV.get((t, f'{f}_null_val'), ('?', '?')) == ('OK', 'OK') for f in ('E', 'K2', 'N50', 'MF1'))
        L.append(f'| {t} | {"yes" if sv else "no"} | {"yes" if rob else "no"} |')
    # ---- B4 bias
    if 'R_null_val' in cells:
        rows = cells['R_null_val']; L += ['', '## B4 mean estimated curvature under the null (R_null_val)', '', '| estimator | mean beta2 | SE | within 2 SE of 0 | rr_eq | bias-removing (|rr_eq-1|<=0.10) |', '|---|---|---|---|---|---|']
        for t in BIAS + ['all']:
            v = col(rows, ('c_all' if t == 'all' else t + '_c')); v = v[~np.isnan(v)]
            if not len(v): continue
            m = v.mean(); se = v.std(ddof=1) / np.sqrt(len(v)); re = rr_eq(m)
            L.append(f'| {t} | {m:.4f} | {se:.4f} | {"yes" if abs(m) <= 2*se else "no"} | {re:.3f} | {"yes" if abs(re-1) <= .10 else "no"} |')
    # ---- B3 power
    L += ['', '## Effects in calendar terms (true trajectory; null mean rate 1.74 dbl/y = 210 d)', '', '| alt | start rate | end rate | start doubling d | end doubling d |', '|---|---|---|---|---|']
    for nm in alts:
        if nm.startswith('R_'):
            r0, r1, d0, d1 = effect(G[nm]['cfg']); L.append(f'| {nm} | {r0:.2f} | {r1:.2f} | {d0:.0f} | {d1:.0f} |')
    L += ['', '## B3 raw power (upward 5% = acceleration; dn5 = deceleration), real design', '', '| test | alt | n | up5 | dn5 | two5 |', '|---|---|---|---|---|---|']
    for t in TESTS:
        for nm in alts:
            if not nm.startswith('R_') or t + '_pup' not in cells[nm][0]: continue
            r = rules(cells[nm], t); n = int(r['ok'].sum()); L.append(f'| {t} | {nm} | {n} | {pct(int(r["up"].sum()),n)} | {pct(int(r["dn"].sum()),n)} | {pct(int(r["two"].sum()),n)} |')
    L += ['', '## B3 size-adjusted power (cutoffs from R_null_cal on z; validated on R_null_val; intervals = 400-draw double bootstrap incl. cutoff error)', '',
          '| test | validated size up [CP] | validated size dn | alt | adj power up | 95% interval | credited? |', '|---|---|---|---|---|---|---|']
    if 'R_null_cal' in cells and 'R_null_val' in cells:
        for t in TESTS:
            zc = col(cells['R_null_cal'], t + '_z'); zv = col(cells['R_null_val'], t + '_z')
            if np.all(np.isnan(zc)): continue
            c = cutoffs(zc); av = adj_rates(zv, c); sv_u, sv_d = verdict(av['up'], av['n']), verdict(av['dn'], av['n'])
            for nm in [n for n in alts if n in ('R_rr1.25', 'R_rr1.5', 'R_rr2', 'R_rr3', 'R_rr4')]:
                za = col(cells[nm], t + '_z'); za = za[~np.isnan(za)]; zcc = zc[~np.isnan(zc)]
                if not len(za): continue
                pw = (za > c['up']).mean(); bs = []
                for _ in range(400):
                    cc = np.quantile(rng.choice(zcc, len(zcc)), .95); bs.append((rng.choice(za, len(za)) > cc).mean())
                lo, hi = np.percentile(bs, [2.5, 97.5])
                L.append(f'| {t} | {pct(av["up"], av["n"])} ({sv_u}) | {pct(av["dn"], av["n"])} ({sv_d}) | {nm} | {100*pw:.1f} | [{100*lo:.1f}, {100*hi:.1f}] | {"yes" if sv_u == "OK" else "NO: validated size not OK"} |')
    # ---- B5 paired with A2
    if RD2 and os.path.isdir(f'{RD2}/cells'):
        c2 = {}
        for nm in ('R_null_val', 'R_rr2'):
            rows = [json.loads(l) for f in sorted(glob.glob(f'{RD2}/cells/{nm}/c*.jsonl')) for l in open(f)]
            if rows: c2[nm] = {r['rep']: r for r in rows}
        L += ['', '## B5 paired differences of upward-5% rejection vs Amendment 2 tests (same data; paired 95% interval)', '', '| new test | A2 test | cell | pairs | diff pp | 95% interval |', '|---|---|---|---|---|---|']
        for nm, d2 in c2.items():
            if nm not in cells: continue
            new = {r['rep']: r for r in cells[nm]}
            for t in TESTS:
                for a in ('ols', 'hc3', 'mb_sota', 'pb_sota'):
                    reps = [k for k in new if k in d2 and not np.isnan(new[k].get(t + '_pup', np.nan) or np.nan) and d2[k].get(a + '_pup') is not None and not np.isnan(d2[k][a + '_pup'])]
                    if len(reps) < 200: continue
                    x = np.array([new[k][t + '_pup'] < .05 for k in reps], float); y = np.array([d2[k][a + '_pup'] < .05 for k in reps], float); d = x - y; se = d.std(ddof=1) / np.sqrt(len(d))
                    L.append(f'| {t} | {a} | {nm} | {len(reps)} | {100*d.mean():+.2f} | [{100*(d.mean()-1.96*se):+.2f}, {100*(d.mean()+1.96*se):+.2f}] |')
    else: L += ['', '## B5 paired comparison with Amendment 2: A2 results not supplied to this analysis (pass the A2 results dir as 2nd argument when complete).']
    # ---- B6 D5
    if 'R_null_val' in cells and 'R_rr2' in cells:
        L += ['', '## B6 / D5 leave-one-record-out influence among replicates where `sota` rejects upward', '', '| cell | n rejecting | median max shift | median jackknife SD | median max shift / SD |', '|---|---|---|---|---|']
        S = {}
        for nm in ('R_null_val', 'R_rr2'):
            rw = cells[nm]; rj = rules(rw, 'sota')['up']; mx = col(rw, 'loro_max'); sd = col(rw, 'loro_sd'); k = rj & ~np.isnan(mx) & ~np.isnan(sd)
            S[nm] = (mx[k], sd[k]); L.append(f'| {nm} | {int(k.sum())} | {np.median(mx[k]):.4f} | {np.median(sd[k]):.4f} | {np.median(mx[k]/np.maximum(sd[k],1e-12)):.2f} |')
        a, b = S['R_null_val'][0] / np.maximum(S['R_null_val'][1], 1e-12), S['R_rr2'][0] / np.maximum(S['R_rr2'][1], 1e-12)
        if len(a) > 20 and len(b) > 20:
            auc = (stats.rankdata(np.concatenate([a, b]))[:len(a)].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(b))
            bs = []
            for _ in range(400):
                aa, bb = rng.choice(a, len(a)), rng.choice(b, len(b)); bs.append((stats.rankdata(np.concatenate([aa, bb]))[:len(aa)].sum() - len(aa) * (len(aa) + 1) / 2) / (len(aa) * len(bb)))
            L.append(f'\nAUC(null-rejection influence ratio > rr2-rejection ratio) = {auc:.3f}, bootstrap 95% [{np.percentile(bs,2.5):.3f}, {np.percentile(bs,97.5):.3f}]  (0.5 = no separation)')
    open(f'{RD}/summary_a3.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L[:12]))
if __name__ == '__main__': main()
