"""EXPLORATORY design-stage follow-up 1 (idea F): model-count scaling + cheap-test subset.  Synthetic data only; no confirmatory claim.
Does NOT modify fdesign.py/grid.py (frozen: seeds depend on them).
mfac = factor on the number of models.  mfac<1: keep every round(1/mfac)-th model in date order.  mfac>=1 (int): each real model
is followed by mfac-1 clones whose release dates are evenly interpolated between it and the next model (last: mirrored gap), same
task coverage / slope b / n.  So the date span, task set and per-model noise are unchanged and ONLY the number of models grows."""
import datetime as dt, numpy as np, fcore as fc, fdesign
def expand(D, b, mfac):
    o = list(D.order); M = D.M
    if mfac < 1:
        step = int(round(1 / mfac)); keep = o[::step]
        return fc.Design([D.names[i] for i in keep], [D.dates[i] for i in keep], D.x, D.fam, D.n[keep], D.kk[keep], D.w[keep]), np.asarray(b)[keep]
    f = int(mfac); idx = []; dates = []; names = []
    for r, i in enumerate(o):
        nxt = D.dates[o[r + 1]] if r + 1 < M else D.dates[i] + (D.dates[i] - D.dates[o[r - 1]])
        gap = (nxt - D.dates[i]).days
        for c in range(f):
            idx.append(i); dates.append(D.dates[i] + dt.timedelta(days=int(round(c * gap / f)))); names.append(D.names[i] + ('' if c == 0 else f'~c{c}'))
    return fc.Design(names, dates, D.x, D.fam, D.n[idx], D.kk[idx], D.w[idx]), np.asarray(b)[idx]
class Sim2(fdesign.Sim):
    def __init__(self, D, b_model, P, cfg):
        D2, b2 = expand(D, b_model, cfg.get('mfac', 1)); super().__init__(D2, b2, P, cfg)
def run_tests2(D, sim, rng_seq, which, B_hb=400, B_xb=300, B_mb=2000, B_pb=1999):
    """which: 'cheap' = iid, model-bootstrap, param-bootstrap ;  'all' = cheap + hierarchical + crossed bootstrap.  Same streams as fdesign.run_tests."""
    r_mb, r_hb, r_xb, r_pb = [np.random.default_rng(s) for s in rng_seq.spawn(4)]
    h, _, _ = fc.horizons_of(D); h = sim.obs(h); out = {}
    mask = fc.sota_mask(h, D); ti = fc.t_iid(D, h, mask); ta = fc.t_iid(D, h, np.ones(D.M, bool))
    out['iid_sota_p'] = ti['p']; out['iid_sota_c'] = ti['coef']; out['nS'] = ti['nS']; out['iid_all_p'] = ta['p']; out['iid_all_c'] = ta['coef']
    ca, cs = fdesign.model_boot(D, h, B_mb, r_mb)
    out['mb_all_lo'], out['mb_all_hi'] = fdesign._ci(ca, B=B_mb); out['mb_sota_lo'], out['mb_sota_hi'] = fdesign._ci(cs, B=B_mb)
    if which == 'all':
        qs, qa = fdesign.hb_sota_all(D, sim, B_hb, r_hb); out['hb_sota_lo'], out['hb_sota_hi'] = fdesign._ci(qs, B=B_hb); out['hb_all_lo'], out['hb_all_hi'] = fdesign._ci(qa, B=B_hb)
        qs, qa = fdesign.crossed_boot(D, sim, B_xb, r_xb); out['xb_sota_lo'], out['xb_sota_hi'] = fdesign._ci(qs, B=B_xb); out['xb_all_lo'], out['xb_all_hi'] = fdesign._ci(qa, B=B_xb)
    c_obs, pu, pd, p2 = fdesign.param_boot_sota(D, sim, h, B_pb, r_pb)
    out['pb_sota_c'] = c_obs; out['pb_sota_pup'] = pu; out['pb_sota_pdn'] = pd; out['pb_sota_p'] = p2
    out['sd_all'] = float(np.std(h, ddof=1)); out['M'] = int(D.M)
    return out
