"""EXPLORATORY post-hoc follow-up to arm (ii) after the registered 'common range c' claim was found false (written after seeing arm2 results; NOT pre-registered).
Corrected Hoeffding ranges = width of the UNION support of the single-draw term: PPS: max_j zhi_j - min_j zlo_j with z=w*y/pi; uniform: nN*(max_j max(w lo,w R) - min_j min(w lo,w R)).
Reports (a) the counterexample to the registered claim, (b) corrected-range widths/gain/coverage on METR v1.0, v1.1 and the three frozen held-out families, and exact coverage on small rosters."""
import json, math, itertools, numpy as np
from topj_common import *
from arm2_audit import *

def terms_bounds(S):
    pos = S['a'] > 0; c = S['a'].sum(); fi = np.where(pos)[0]; pi = S['a'][fi] / c
    z1 = S['wn'][fi] * S['lo'] / pi; z2 = S['wn'][fi] * S['R'][fi] / pi
    return fi, pi, c, float(np.maximum(z1, z2).max() - np.minimum(z1, z2).min())

def uni_range(S):
    z1 = S['wn'] * S['lo']; z2 = S['wn'] * S['R']; return S['nN'] * float(np.maximum(z1, z2).max() - np.minimum(z1, z2).min())

def run(S, ycomp, rng, D=DRAWS):
    wy, pos, c, fixed = frames(S, ycomp); m = S['m']; nN = S['nN']; fi, pi, c, rp = terms_bounds(S); ru = uni_range(S)
    J = rng.choice(len(fi), size=(D, m), p=pi); est = S['QR'] + fixed + (wy[fi][J] / pi[J]).mean(1); wp, cp_, xp = clip(est, rp * math.sqrt(LN / (2 * m)), S)
    J = rng.integers(0, nN, size=(D, m)); est = S['QR'] + nN * wy[J].mean(1); wu, cu, xu = clip(est, ru * math.sqrt(LN / (2 * m)), S)
    return dict(med_w_pps=float(np.median(wp)), med_w_uni=float(np.median(wu)), gain=float(1 - np.median(wp) / np.median(wu)) if np.median(wu) > 0 else None,
                cov_pps=float(cp_.mean()), cov_uni=float(cu.mean()), sharp_width=S['U'] - S['L'], c_registered=c, range_pps_union=rp, range_uni_union_over_registered=ru / (S['nN'] * S['a'].max()))

out = {}
ep = epoch_all(); chosen, _ = heldout_rule(ep); byn = {s['name']: s for s in ep}
for s in [metr('1.0'), metr('1.1')] + [byn[n] for n in chosen]:
    S = setup(s['t'], s['y'], s['lo']); rg = np.random.default_rng(np.random.SeedSequence([44, sum(map(ord, s['name']))]))
    r = run(S, s['y'][S['NR']], rg); rows = []
    for cn, yc in worst_corners(S).items():
        S2 = dict(S); S2['truth'] = S['QR'] + float((S['wn'] * yc).sum()); q = run(S2, yc, rg, 20000); rows.append((q['cov_pps'], q['cov_uni']))
    r['min_cov_pps_corners'] = min(a for a, b in rows); r['min_cov_uni_corners'] = min(b for a, b in rows); out[s['name']] = r
# counterexample to the registered claim: smallest-roster exact coverage case
rg = np.random.default_rng(np.random.SeedSequence([43, 1])); found = None
while found is None:
    n = int(rg.integers(8, 13)); x = float(rg.uniform(0.3, 3)); s_ = np.sort(rg.random(n)); y = x * s_ + rg.standard_normal(n); lo = float(y.min()) - 0.5; S = setup(s_, y, lo)
    if S['nN'] < 3 or S['nN'] > 9: continue
    fi, pi, c, rp = terms_bounds(S)
    if rp > c * (1 + 1e-9): found = dict(n=n, nN=S['nN'], registered_c=c, union_range=rp, ratio=rp / c)
out['_counterexample_registered_common_range_c'] = found
json.dump(out, open(OUT + '/arm2_followup_exploratory.json', 'w'), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
