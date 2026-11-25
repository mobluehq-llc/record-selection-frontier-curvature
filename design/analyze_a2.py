"""EXPLORATORY Design Amendment 2 analysis (idea F).  Usage: /usr/bin/python3 analyze_a2.py <results_dir>  -> summary_a2.md / summary_a2.json / counts_a2.csv
Implements ONLY what AMENDMENT2.md section 'Analysis' prespecifies.  Tails: p_up = evidence for positive curvature (acceleration); p_dn = deceleration.
 two-sided 5%  := min(p_up,p_dn) < 0.025 ;  up5 := p_up < 0.05 ;  dn5 := p_dn < 0.05.   Size bound for 'acceptable' := CP95 inside [3.5, 6.5] %."""
import sys, os, json, glob, csv, numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fcore as fc, fdesign3 as f3, grid_a2 as grid
RD = sys.argv[1]; DATA = os.environ.get('FDATA', os.path.join(HERE, 'data')); fc.DATA = DATA
LO, HI = 3.5, 6.5
TESTS = ['ols', 'hc3', 'wild', 'perm', 'iid_sota', 'mb_all', 'mb_sota', 'pb_sota', 'hb_all', 'hb_sota', 'xb_all', 'xb_sota']
ZTESTS = ['ols', 'hc3', 'iid_sota', 'mb_all', 'mb_sota', 'pb_sota', 'hb_all', 'hb_sota', 'xb_all', 'xb_sota']   # wild == hc3 cutoff, perm == ols cutoff (same statistic; only the cutoff source differs)
PAIRS = [('wild', 'hc3'), ('wild', 'ols'), ('perm', 'ols'), ('hc3', 'ols'), ('wild', 'mb_sota'), ('hc3', 'mb_sota')]
rng = np.random.default_rng(20261123)
def cp(k, n, a=0.05):
    return (0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1), 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k))
def pct(k, n, a=0.05):
    if n == 0: return '-'
    lo, hi = cp(k, n, a); return f'{100*k/n:.2f} [{100*lo:.2f},{100*hi:.2f}]'
def load():
    cells = {}
    for c in grid.CELLS:
        rows = [json.loads(l) for f in sorted(glob.glob(f"{RD}/cells/{c['name']}/c*.jsonl")) for l in open(f)]
        if rows: cells[c['name']] = rows
    return cells
def col(rows, key): return np.array([r.get(key, np.nan) if r.get(key) is not None else np.nan for r in rows], float)
def verdict(k, n, a=0.05):
    lo, hi = cp(k, n, a)
    return 'OK' if lo * 100 >= LO and hi * 100 <= HI else ('OUT' if hi * 100 < LO or lo * 100 > HI else 'inconclusive')
P = json.load(open(f'{DATA}/F_simulator_validation.json'))['params']; D0 = fc.load_real(data=DATA); h0, _, b0 = fc.horizons_of(D0)
RATE = P['rate_null']; SPAN = float(D0.t.max() - D0.t.min())
def effect(cfg):
    # CORRECTED 2026-11-23 (ERRATA.md): h was 0.5 y, which reported half-year secant rates, not endpoint rates (rr=2 printed as 304 -> 160 d, ratio 1.90).
    # Descriptive calendar table only; no test, size or power figure depends on this function.
    s = f3.Sim3(D0, b0, P, cfg); t0 = s.tmin; h = 1e-6
    r0 = (s.true_L(t0 + h) - s.true_L(t0)) / h; r1 = (s.true_L(t0 + SPAN) - s.true_L(t0 + SPAN - h)) / h; rm = (s.true_L(t0 + SPAN) - s.true_L(t0)) / SPAN
    return dict(rate_start=float(r0), rate_end=float(r1), rate_mean=float(rm), dt_start_d=365.25 / float(r0) if r0 > 0 else np.inf, dt_end_d=365.25 / float(r1) if r1 > 0 else np.inf)
def rr_eq(b2): q = b2 * SPAN / RATE; return (1 + q) / (1 - q) if q < 1 else np.inf
def rules(rows, t):
    pu, pd = col(rows, t + '_pup'), col(rows, t + '_pdn'); ok = ~np.isnan(pu)
    return dict(ok=ok, two=((pu < .025) | (pd < .025)) & ok, up=(pu < .05) & ok, dn=(pd < .05) & ok)
def main():
    cells = load(); G = {c['name']: c for c in grid.CELLS}; S = {'size': {}, 'power': {}, 'validation': {}, 'curv': {}, 'effects': {}, 'paired': {}}; L = []
    nulls = [n for n in cells if G[n]['role'] in ('cal', 'val', 'lad')]
    m_size = max(1, len(nulls) * len(TESTS) * 3)          # Bonferroni family: every null cell x test x rule in this table
    # ---------------- counts csv + size table
    with open(f'{RD}/counts_a2.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['cell', 'role', 'planned', 'completed', 'test', 'n_valid', 'n_invalid', 'k_two', 'k_up', 'k_dn'])
        for nm, rows in cells.items():
            for t in TESTS:
                if t + '_pup' not in rows[0]: continue
                r = rules(rows, t); n = int(r['ok'].sum()); w.writerow([nm, G[nm]['role'], G[nm]['reps'], len(rows), t, n, len(rows) - n, int(r['two'].sum()), int(r['up'].sum()), int(r['dn'].sum())])
    L += ['# F Design Amendment 2 results -- EXPLORATORY, synthetic data only', '', f'Size bound (prespecified): CP95 inside [{LO}, {HI}] % = OK; CP95 disjoint = OUT; else inconclusive. Bonferroni family for the size tables: {m_size} intervals (alpha {0.05/m_size:.2e}).',
          'Rates are % [Clopper-Pearson 95%]. Counts k/n are in counts_a2.csv (also invalid replicates). wild/perm are bootstrap/permutation p-values for the HC3 t / OLS t.', '']
    for title, roles in (('Null size, primary and validation cells', ('val', 'cal')), ('Ladder rungs (null)', ('lad',))):
        for rule, lab in (('up', 'upward one-sided 5% (acceleration claim)'), ('two', 'two-sided 5%'), ('dn', 'downward one-sided 5%')):
            L += [f'## {title}: {lab}', '', '| cell | n | ' + ' | '.join(TESTS) + ' |', '|---|---|' + '---|' * len(TESTS)]
            for nm in nulls:
                if G[nm]['role'] not in roles or (roles == ('val', 'cal') and G[nm]['role'] == 'cal' and not nm.startswith('R_')): continue
                row = []
                for t in TESTS:
                    if t + '_pup' not in cells[nm][0]: row.append('-'); continue
                    r = rules(cells[nm], t); n = int(r['ok'].sum()); k = int(r[rule].sum()); v = verdict(k, n)
                    blo, bhi = cp(k, n, 0.05 / m_size); row.append(f'{pct(k, n)} {v} (B[{100*blo:.1f},{100*bhi:.1f}])'); S['size'].setdefault(nm, {}).setdefault(t, {})[rule] = dict(k=k, n=n, verdict=v)
                L.append(f'| {nm} | {len(cells[nm])} | ' + ' | '.join(row) + ' |')
            L.append('')
    # ---------------- curvature + selection sample size
    L += ['## Mean estimated curvature under each null (all-model OLS beta2, doublings/yr^2; SOTA-subset beta2) and effective frontier sample size', '',
          'rr_eq = acceleration ratio that would produce the mean curvature (rr_eq = (1+q)/(1-q), q = beta2*span/rate). A mean +-2 SE away from 0 is a systematic bias of that statistic under the null.', '',
          '| cell | n | mean beta2 all (SE) | rr_eq all | mean beta2 SOTA (SE) | rr_eq SOTA | nS mean [q05,q95] | frac of models at ceiling |', '|---|---|---|---|---|---|---|---|']
    for nm in nulls:
        rows = cells[nm]; a = col(rows, 'reg_c'); s = col(rows, 'sota_c'); s = s[~np.isnan(s)]; nS = col(rows, 'nS'); fr = col(rows, 'frac_at_ceiling')
        S['curv'][nm] = dict(beta2_all=float(a.mean()), se_all=float(a.std(ddof=1) / np.sqrt(len(a))), beta2_sota=float(s.mean()), se_sota=float(s.std(ddof=1) / np.sqrt(len(s))), nS_mean=float(np.nanmean(nS)))
        L.append(f'| {nm} | {len(rows)} | {a.mean():+.4f} ({a.std(ddof=1)/np.sqrt(len(a)):.4f}) | {rr_eq(a.mean()):.2f} | {s.mean():+.4f} ({s.std(ddof=1)/np.sqrt(len(s)):.4f}) | {rr_eq(s.mean()):.2f} | {np.nanmean(nS):.1f} [{np.nanquantile(nS,.05):.0f},{np.nanquantile(nS,.95):.0f}] | {fr.mean():.3f} |')
    L.append('')
    # ---------------- effects in calendar-time terms
    alts = [n for n in cells if G[n]['role'] == 'alt']
    L += ['## Alternatives in calendar-time terms (real design, span %.2f y; null growth %.2f doublings/y = doubling time %.0f d)' % (SPAN, RATE, 365.25 / RATE), '',
          '| alternative | rate start (dbl/y) | rate end | doubling time start (d) | end (d) | change in rate over window | intended direction |', '|---|---|---|---|---|---|---|']
    for nm in alts + [n for n in ('R_null_val',) if n in cells]:
        e = effect(G[nm]['cfg']); S['effects'][nm] = e; d = 'acceleration' if e['rate_end'] > 1.05 * e['rate_start'] else ('deceleration' if e['rate_end'] < 0.95 * e['rate_start'] else 'none/mixed')
        if 'logi_mid' in nm: d = 'mixed (accelerate then decelerate)'
        L.append(f"| {nm} | {e['rate_start']:.2f} | {e['rate_end']:.2f} | {e['dt_start_d']:.0f} | {e['dt_end_d']:.0f} | x{e['rate_end']/e['rate_start']:.2f} | {d} |")
    L += ['', 'Prespecified meaningful acceleration: end-of-window growth rate >= 2x the start rate (rr >= 2). rr = 1.5 and 1.25 are reported as smaller effects.', '']
    # ---------------- size-adjusted power with independent validation and cutoff uncertainty
    Bc = 400
    def zof(rows, t): return col(rows, t + '_z')
    def cut(zc, rule):
        zc = zc[~np.isnan(zc)]
        return (np.quantile(zc, .95), None) if rule == 'up' else ((None, np.quantile(zc, .05)) if rule == 'dn' else (np.quantile(zc, .975), np.quantile(zc, .025)))
    def rej(z, rule, c):
        ok = ~np.isnan(z)
        if rule == 'up': return (z > c[0]) & ok
        if rule == 'dn': return (z < c[1]) & ok
        return ((z > c[0]) | (z < c[1])) & ok
    L += ['## Signed power: raw rejection and size-adjusted power (cutoff from the fam\'s cal null; 95% interval carries cutoff uncertainty + alternative Monte Carlo error, 400 double-bootstrap draws)', '',
          'Acceleration power = P(upward one-sided 5%); deceleration power = P(downward one-sided 5%); "two" = two-sided 5%. Adjusted entries for wild/perm equal those of hc3/ols (same statistic).', '']
    for rule, lab in (('up', 'ACCELERATION power (upward one-sided 5%)'), ('dn', 'DECELERATION power (downward one-sided 5%)'), ('two', 'two-sided 5% power')):
        L += [f'### {lab}: raw % / adjusted % [interval]', '', '| alternative | n | ' + ' | '.join(TESTS) + ' |', '|---|---|' + '---|' * len(TESTS)]
        for nm in alts:
            fam = G[nm]['fam']; cal = fam + '_null_cal'; row = []
            for t in TESTS:
                if t + '_pup' not in cells[nm][0]: row.append('-'); continue
                r = rules(cells[nm], t); n = int(r['ok'].sum()); k = int(r[rule].sum()); s = f'{100*k/n:.1f}'
                tz = 'hc3' if t == 'wild' else ('ols' if t == 'perm' else t)
                if tz in ZTESTS and cal in cells and tz + '_z' in cells[cal][0]:
                    zc, za = zof(cells[cal], tz), zof(cells[nm], tz); zc = zc[~np.isnan(zc)]; za = za[~np.isnan(za)]
                    c0 = cut(zc, rule); a0 = rej(za, rule, c0).mean(); bs = []
                    for _ in range(Bc):
                        cb = cut(rng.choice(zc, len(zc)), rule); bs.append(rej(rng.choice(za, len(za)), rule, cb).mean())
                    lo, hi = np.percentile(bs, [2.5, 97.5]); s += f' / {100*a0:.1f} [{100*lo:.1f},{100*hi:.1f}]'
                    S['power'].setdefault(nm, {}).setdefault(t, {})[rule] = dict(raw=k / n, adj=float(a0), adj_lo=float(lo), adj_hi=float(hi), n=n, k=k)
                else: S['power'].setdefault(nm, {}).setdefault(t, {})[rule] = dict(raw=k / n, n=n, k=k)
                row.append(s)
            L.append(f'| {nm} | {len(cells[nm])} | ' + ' | '.join(row) + ' |')
        L.append('')
    # validation of cutoffs on independent null draws
    L += ['## Validation: achieved size of the cal-derived cutoffs on the INDEPENDENT val null draws (nominal 5% one-sided / 5% two-sided)', '', '| fam | test | n cal | n val | up5 achieved % [CP] | dn5 achieved % [CP] | two achieved % [CP] | raw-rule up5 on val % |', '|---|---|---|---|---|---|---|---|']
    for c in grid.CELLS:
        if c['role'] != 'val' or c['name'] not in cells: continue
        fam = c['fam']; cal = fam + '_null_cal'
        if cal not in cells: continue
        for t in ZTESTS:
            if t + '_z' not in cells[cal][0]: continue
            zc, zv = zof(cells[cal], t), zof(cells[c['name']], t); zc = zc[~np.isnan(zc)]; zv = zv[~np.isnan(zv)]; res = []
            for rule in ('up', 'dn', 'two'):
                k = int(rej(zv, rule, cut(zc, rule)).sum()); res.append(pct(k, len(zv))); S['validation'].setdefault(fam, {}).setdefault(t, {})[rule] = dict(k=k, n=len(zv))
            r = rules(cells[c['name']], t)
            L.append(f"| {fam} | {t} | {len(zc)} | {len(zv)} | {res[0]} | {res[1]} | {res[2]} | {pct(int(r['up'].sum()), int(r['ok'].sum()))} |")
    L.append('')
    # ---------------- paired differences
    L += ['## Paired Monte Carlo differences in upward-5% rejection (same replicates; difference of rates in pp, 95% normal interval of the paired difference)', '', '| cell | pair | diff pp [95%] |', '|---|---|---|']
    for nm in [n for n in ('R_null_val', 'R_rr2', 'X_null_val', 'X_rr2') if n in cells]:
        for a, b in PAIRS:
            ra, rb = rules(cells[nm], a), rules(cells[nm], b); ok = ra['ok'] & rb['ok']; d = ra['up'][ok].astype(float) - rb['up'][ok].astype(float)
            if not len(d): continue
            se = d.std(ddof=1) / np.sqrt(len(d)); L.append(f'| {nm} | {a} - {b} | {100*d.mean():+.2f} [{100*(d.mean()-1.96*se):+.2f},{100*(d.mean()+1.96*se):+.2f}] |')
    L.append('')
    L += ['## Completion', '', '| cell | completed / planned |', '|---|---|'] + [f"| {c['name']} | {len(cells.get(c['name'], []))} / {c['reps']} |" for c in grid.CELLS]
    json.dump(S, open(f'{RD}/summary_a2.json', 'w'), indent=1, default=float); open(f'{RD}/summary_a2.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
if __name__ == '__main__': main()
