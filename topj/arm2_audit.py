"""ARM (ii): randomized PPS audit of non-record scores vs uniform at 25% budget (F/PLAN.md TOP-JOURNAL AMENDMENT). Frozen by the sha of this file.
beta2 = Q_R + sum_{j in N} w_j y_j, y_j in [lo_j, R_j] (R_j = standing record before j; lo = scale floor: METR 0 on log2; Epoch logit series logit(0.005) [the prepare() clip]; log2/z series: series minimum observed y).
PPS: m=ceil(.25|N|) draws WITH replacement, pi_j ~ a_j=|w_j|(R_j-lo), Hansen-Hurwitz, Hoeffding half-width c*sqrt(ln(40)/(2m)), c=sum a_j; terms have common range c.
Uniform: m uniform draws with replacement, estimator (|N|/m) sum w y, half-width |N|*max a_j * sqrt(ln(40)/(2m)). Both intersected with the sharp record-only range.
Items with a_j=0 are determined (y=lo) and moved to the known part."""
import sys, os, json, math, time, itertools
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
from scipy import stats
from multiprocessing import Pool
from topj_common import *

LN = math.log(2 / 0.05); DRAWS = 100000


def setup(t, y, lo):
    r, prev = records(y); w = quad_w(t); NR = np.where(~r)[0]
    assert np.all(y[NR] <= prev[NR] + 1e-12) and np.all(y >= lo - 1e-12)
    QR = float((w[r] * y[r]).sum()); truth = float((w * y).sum())
    R = prev[NR]; wn = w[NR]; a = np.abs(wn) * (R - lo)
    lo_t = np.minimum(wn * lo, wn * R); hi_t = np.maximum(wn * lo, wn * R)
    return dict(w=w, NR=NR, QR=QR, truth=truth, R=R, wn=wn, a=a, L=QR + lo_t.sum(), U=QR + hi_t.sum(), nN=len(NR), m=math.ceil(0.25 * len(NR)), lo=lo, rec=r, y=y)


def clip(est, hw, S):
    lo_ = np.maximum(est - hw, S['L']); hi_ = np.minimum(est + hw, S['U']); emp = lo_ > hi_
    width = np.where(emp, 0.0, hi_ - lo_)
    cover = (~emp) & (lo_ <= S['truth'] + 1e-12) & (S['truth'] - 1e-12 <= hi_)
    excl0 = emp | (lo_ > 0) | (hi_ < 0)
    return width, cover, excl0


def frames(S, ycomp):
    """returns pps frame (indices into NR with a>0), probs, fixed part, per-item values wy"""
    wy = S['wn'] * ycomp                     # w_j y_j for the completion
    pos = S['a'] > 0; c = S['a'].sum(); fixed = float((S['wn'][~pos] * S['lo']).sum())
    return wy, pos, c, fixed


def audit_draws(S, ycomp, rng, D):
    wy, pos, c, fixed = frames(S, ycomp); m = S['m']; nN = S['nN']
    # PPS
    fi = np.where(pos)[0]; pi = S['a'][fi] / c
    J = rng.choice(len(fi), size=(D, m), p=pi); est_p = S['QR'] + fixed + (wy[fi][J] / pi[J]).mean(1)
    hw_p = c * math.sqrt(LN / (2 * m)); wp, cp_, xp = clip(est_p, hw_p, S)
    # uniform (frame = all non-records)
    J = rng.integers(0, nN, size=(D, m)); est_u = S['QR'] + nN * wy[J].mean(1)
    hw_u = nN * S['a'].max() * math.sqrt(LN / (2 * m)); wu, cu, xu = clip(est_u, hw_u, S)
    return dict(w_pps=wp, w_uni=wu, cov_pps=cp_, cov_uni=cu, x_pps=xp, x_uni=xu, hw_p=hw_p, hw_u=hw_u, c=c)


def summarize(S, d):
    rng_w = S['U'] - S['L']
    return dict(nN=S['nN'], m=S['m'], sharp_L=S['L'], sharp_U=S['U'], sharp_width=rng_w, sharp_contains_0=bool(S['L'] <= 0 <= S['U']), truth=S['truth'],
                med_w_pps=float(np.median(d['w_pps'])), med_w_uni=float(np.median(d['w_uni'])), mean_w_pps=float(d['w_pps'].mean()), mean_w_uni=float(d['w_uni'].mean()),
                gain_median=float(1 - np.median(d['w_pps']) / np.median(d['w_uni'])) if np.median(d['w_uni']) > 0 else float('nan'),
                cov_pps=float(d['cov_pps'].mean()), cov_uni=float(d['cov_uni'].mean()), excl0_pps=float(d['x_pps'].mean()), excl0_uni=float(d['x_uni'].mean()),
                halfw_pps=d['hw_p'], halfw_uni=d['hw_u'], unclipped_ratio=d['hw_p'] / d['hw_u'])


def weighted_median(v, p):
    o = np.argsort(v); cs = np.cumsum(p[o]); return float(v[o][np.searchsorted(cs, 0.5 * cs[-1])])


def enumerate_metr(S, ycomp):
    """exact: uniform subsets C(nN,m) [registered]; uniform ordered with replacement nN^m [sensitivity]; PPS ordered tuples with prob prod pi."""
    wy, pos, c, fixed = frames(S, ycomp); m = S['m']; nN = S['nN']
    hw_u = nN * S['a'].max() * math.sqrt(LN / (2 * m)); hw_p = c * math.sqrt(LN / (2 * m))
    subs = np.array(list(itertools.combinations(range(nN), m))); est = S['QR'] + (nN / m) * wy[subs].sum(1)
    wu, cu, xu = clip(est, hw_u, S)
    fi = np.where(pos)[0]; pi = S['a'][fi] / c; k = len(fi)
    tup = np.array(list(itertools.product(range(k), repeat=m))); pr = np.prod(pi[tup], axis=1)
    estp = S['QR'] + fixed + (wy[fi][tup] / pi[tup]).mean(1); wp, cpv, xp = clip(estp, hw_p, S)
    tu = np.array(list(itertools.product(range(nN), repeat=m))); estw = S['QR'] + nN * wy[tu].mean(1); ww, cw, xw = clip(estw, hw_u, S)
    return dict(n_uniform_subsets=len(subs), uniform_subset_median_width=float(np.median(wu)), uniform_subset_mean_width=float(wu.mean()), uniform_subset_coverage=float(cu.mean()), uniform_subset_excl0=float(xu.mean()),
                uniform_subset_min_width=float(wu.min()), uniform_subset_max_width=float(wu.max()),
                n_pps_tuples=len(tup), pps_prob_sum=float(pr.sum()), pps_expected_width=float((pr * wp).sum()), pps_weighted_median_width=weighted_median(wp, pr), pps_exact_coverage=float((pr * cpv).sum()), pps_excl0=float((pr * xp).sum()),
                pps_min_width=float(wp.min()), pps_max_width=float(wp.max()),
                uniform_withrepl_median_width=float(np.median(ww)), uniform_withrepl_mean_width=float(ww.mean()), uniform_withrepl_coverage=float(cw.mean()), uniform_withrepl_excl0=float(xw.mean()),
                gain_vs_uniform_subsets_median=float(1 - weighted_median(wp, pr) / np.median(wu)) if np.median(wu) > 0 else float('nan'),
                gain_vs_uniform_withrepl_median=float(1 - weighted_median(wp, pr) / np.median(ww)) if np.median(ww) > 0 else float('nan'),
                gain_expected_vs_uniform_withrepl_mean=float(1 - (pr * wp).sum() / ww.mean()) if ww.mean() > 0 else float('nan'),
                halfw_pps=hw_p, halfw_uni=hw_u)


def worst_corners(S):
    """completion vectors (y_j for non-records) to stress coverage: all-lo, all-R, variance-maximising for PPS and for uniform, plus 20 random corners."""
    lo = S['lo']; R = S['R']; out = {'all_lo': np.full(S['nN'], lo), 'all_R': R.copy()}
    pos = S['a'] > 0; c = S['a'].sum()
    # PPS: u_j = sign(w)*(y-lo)/(R-lo) in {0,1}-ish; variance max <=> mass of {u=1 in the sign-adjusted sense} nearest 1/2
    top = np.where(S['wn'] >= 0, R, lo)   # y at which term = c*1 (sign-adjusted top)
    bot = np.where(S['wn'] >= 0, lo, R)
    order = np.argsort(-S['a']); cum = 0.0; y = bot.copy()
    for j in order:
        if cum + S['a'][j] / max(c, 1e-300) <= 0.5: y[j] = top[j]; cum += S['a'][j] / max(c, 1e-300)
    out['var_max_pps'] = y
    # uniform: terms z_j = nN*w_j*y_j with endpoints; lower half of midpoints -> lower endpoint, upper half -> upper
    zl = np.minimum(S['wn'] * lo, S['wn'] * R); zh = np.maximum(S['wn'] * lo, S['wn'] * R); mid = (zl + zh) / 2; o = np.argsort(mid); y2 = np.zeros(S['nN'])
    for rank, j in enumerate(o):
        useh = rank >= S['nN'] // 2
        y2[j] = (R[j] if (S['wn'][j] >= 0) == useh else lo) if True else 0
    out['var_max_uni'] = y2
    rg = np.random.default_rng(7)
    for q in range(20): out[f'rand{q}'] = np.where(rg.random(S['nN']) < 0.5, lo, R)
    return out


def coverage_check_real(S, name, D=DRAWS):
    rows = {}
    for cn, yc in worst_corners(S).items():
        # a corner is a completion: truth changes with it
        S2 = dict(S); S2['truth'] = S['QR'] + float((S['wn'] * yc).sum())
        # full completion y vector for audit_draws: only the non-record part is used via wn*ycomp
        d = audit_draws(S2, yc, np.random.default_rng(np.random.SeedSequence([42, sum(map(ord, name)), len(rows)])), D)
        rows[cn] = (float(d['cov_pps'].mean()), float(d['cov_uni'].mean()))
    mp = min(v[0] for v in rows.values()); mu = min(v[1] for v in rows.values())
    return dict(min_cov_pps=mp, min_cov_uni=mu, corners=len(rows))


def exhaustive_small(nroster=40):
    """(a): exhaustive enumeration of all audits on small synthetic rosters (n<=12) at ALL corners: exact coverage probability of both designs."""
    rg = np.random.default_rng(np.random.SeedSequence([43, 1])); worst_p = 1.0; worst_u = 1.0; used = 0; ncorner = 0
    while used < nroster:
        n = int(rg.integers(8, 13)); x = float(rg.uniform(0.3, 3)); s = np.sort(rg.random(n)); y = x * s + rg.standard_normal(n)
        lo = float(y.min()) - 0.5; S = setup(s, y, lo)
        if S['nN'] < 3 or S['nN'] > 9: continue
        used += 1; nN = S['nN']; m = S['m']
        for bits in itertools.product([0, 1], repeat=nN):
            yc = np.where(np.array(bits) == 1, S['R'], lo); S2 = dict(S); S2['truth'] = S['QR'] + float((S['wn'] * yc).sum()); ncorner += 1
            wy, pos, c, fixed = frames(S, yc); fi = np.where(pos)[0]
            if len(fi) == 0: continue
            pi = S['a'][fi] / c; tup = np.array(list(itertools.product(range(len(fi)), repeat=m))); pr = np.prod(pi[tup], axis=1)
            est = S['QR'] + fixed + (wy[fi][tup] / pi[tup]).mean(1); _, cv, _ = clip(est, c * math.sqrt(LN / (2 * m)), S2); worst_p = min(worst_p, float((pr * cv).sum()))
            tu = np.array(list(itertools.product(range(nN), repeat=m))); est = S['QR'] + nN * wy[tu].mean(1)
            _, cv, _ = clip(est, nN * S['a'].max() * math.sqrt(LN / (2 * m)), S2); worst_u = min(worst_u, float(cv.mean()))
    return dict(rosters=used, corners_checked=ncorner, min_exact_cov_pps=worst_p, min_exact_cov_uni=worst_u)


def synth_calendar(rg):
    x = float(math.exp(rg.uniform(math.log(0.5), math.log(20)))); b = float(rg.uniform(-3, 3)); N = int(rg.choice([15, 33, 100]))
    sg = np.linspace(0, 1, 2001); lam = np.exp(0.5 * b * sg * sg); cum = np.concatenate([[0], np.cumsum((lam[1:] + lam[:-1]) / 2)]); cum /= cum[-1]
    n = max(int(rg.poisson(N)), 5); s = np.sort(np.interp(rg.random(n), cum, sg)); y = x * s + rg.standard_normal(n)
    return x, b, N, s, y


def synthetic(nsets=2000, draws=1000):
    rg = np.random.default_rng(np.random.SeedSequence([43, 2])); rows = []; skipped = 0
    for q in range(nsets):
        x, b, N, s, y = synth_calendar(rg); lo = float(y.min()); S = setup(s, y, lo)
        if S['nN'] < 4 or S['a'].sum() <= 0: skipped += 1; continue
        d = audit_draws(S, y[S['NR']], rg, draws); sm = summarize(S, d)
        rows.append(dict(x=x, b=b, N=N, n=len(y), rec_share=float(S['rec'].mean()), sharp_width=sm['sharp_width'], contains0=sm['sharp_contains_0'], gain=sm['gain_median'], cov_pps=sm['cov_pps'], cov_uni=sm['cov_uni'], excl0_pps=sm['excl0_pps']))
    A = lambda k: np.array([r[k] for r in rows], float)
    sp = lambda k: float(stats.spearmanr(A(k), A('sharp_width'))[0])
    return dict(n_calendars=len(rows), skipped_lt4_nonrecords=skipped, frac_sharp_contains_0=float(A('contains0').mean()), median_sharp_width=float(np.median(A('sharp_width'))),
                spearman_width_vs=dict(n=sp('n'), b=sp('b'), x=sp('x'), rec_share=sp('rec_share')), median_gain=float(np.nanmedian(A('gain'))), min_cov_pps=float(A('cov_pps').min()), min_cov_uni=float(A('cov_uni').min()),
                frac_gain_ge_30=float(np.nanmean(A('gain') >= 0.30)))


def one_series(args):
    idx, s = args; S = setup(s['t'], s['y'], s['lo']); rg = np.random.default_rng(np.random.SeedSequence([42, idx]))
    d = audit_draws(S, s['y'][S['NR']], rg, DRAWS); out = summarize(S, d); out['name'] = s['name']; out['n'] = len(s['y']); out['lo'] = s['lo']; out['lo_flag'] = s['lo_flag']
    out['coverage_corner_check'] = coverage_check_real(S, s['name'])
    return out


def main():
    t0 = time.time(); NPROC = 4
    m10, m11 = metr('1.0'), metr('1.1'); ep = epoch_all(); chosen, rows = heldout_rule(ep)
    S10 = setup(m10['t'], m10['y'], m10['lo']); print('METR v1.0: n', len(m10['y']), 'non-records (recomputed)', S10['nN'], 'm', S10['m'], 'C =', math.comb(S10['nN'], S10['m']), '| review: 16, 1820', flush=True)
    enum = enumerate_metr(S10, m10['y'][S10['NR']])
    allseries = [m10, m11] + ep
    with Pool(NPROC) as P:
        res = P.map(one_series, list(enumerate(allseries)))
        ex = P.apply_async(exhaustive_small); sy = P.apply_async(synthetic)
        ex = ex.get(); sy = sy.get()
    byname = {r['name']: r for r in res}
    held = [byname[n] for n in chosen]
    gate = {}
    gate['coverage_by_construction'] = bool(all(r['cov_pps'] >= 0.95 for r in res) and enum['pps_exact_coverage'] >= 0.95 and ex['min_exact_cov_pps'] >= 0.95
                                            and all(r['coverage_corner_check']['min_cov_pps'] >= 0.95 for r in res) and sy['min_cov_pps'] >= 0.95)
    gate['metr_v10_gain_registered_enumeration'] = enum['gain_vs_uniform_subsets_median']
    gate['heldout_gains'] = {r['name']: r['gain_median'] for r in held}
    gate['bar2_all_ge_30pct'] = bool(enum['gain_vs_uniform_subsets_median'] >= 0.30 and all(r['gain_median'] >= 0.30 for r in held))
    gate['verdict'] = 'GO' if (gate['coverage_by_construction'] and gate['bar2_all_ge_30pct']) else 'NO-GO'
    out = dict(label='CONFIRMATORY (pre-registered, F/PLAN.md TOP-JOURNAL AMENDMENT arm ii)', gate=gate, metr_v10_enumeration=enum, metr_v10_nonrecords=S10['nN'], heldout_chosen=chosen,
               heldout=held, metr_v10=byname['METR v1.0'], metr_v11=byname['METR v1.1'], epoch_series=[byname[s['name']] for s in ep], exhaustive_small=ex, synthetic=sy, runtime_s=time.time() - t0)
    json.dump(out, open(OUT + '/arm2_results.json', 'w'), indent=1, default=float)
    print(json.dumps(dict(gate=gate, enum=enum, heldout=[(r['name'], r['gain_median'], r['sharp_width'], r['med_w_pps'], r['med_w_uni'], r['excl0_pps']) for r in held], exhaustive=ex, synthetic=sy), indent=1, default=float))


if __name__ == '__main__':
    main()
