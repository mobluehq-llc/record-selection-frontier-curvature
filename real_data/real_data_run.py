"""F REAL-DATA AMENDMENT runner.  Spec: ../PLAN.md section "Real-data amendment" (pre-registered and committed BEFORE this ran on the real data).
Usage: python3 real_data_run.py real      -> real METR v1.0 data (one-shot: refuses to overwrite out/real_v10.json)
       python3 real_data_run.py smoke     -> synthetic dataset from the R_null_val simulator (pipeline test only; writes out/smoke.json)
Frozen code imported from ../design (fcore, fdesign, fdesign3, fdesign4, grid_a2); not modified."""
import os, sys, json, hashlib, datetime as dt, time
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'): os.environ[v] = '1'
import numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); DES = os.path.join(HERE, '..', 'design'); sys.path.insert(0, DES)
import fcore as fc, fdesign3 as f3, fdesign4 as f4, grid_a2 as g2
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
DATA = fc.DATA
SIMVAL = os.path.join(HERE, '..', 'results', 'F_simulator_validation.json')
CUTOFF = dt.date(2025, 11, 30)
B_PB, B_W, B_P, B_MB, N_AUD = 19999, 9999, 9999, 2000, 200
SEED = 9100  # SeedSequence([SEED, k])

def rr_eq(b2, span, rate):
    q = b2 * span / rate
    return (1 + q) / (1 - q) if -1 < q < 1 else float('nan')   # undefined (nan) when |q| >= 1

def calendar(t, y):
    """all-model quadratic y = a + b (t-mean) + c (t-mean)^2 -> instantaneous growth (doublings/yr) at window start and end, doubling days, rr_hat"""
    tc = t - t.mean(); X = np.stack([np.ones_like(tc), tc, tc * tc], 1); b = np.linalg.lstsq(X, y, rcond=None)[0]
    r0 = b[1] + 2 * b[2] * (tc.min()); r1 = b[1] + 2 * b[2] * (tc.max())
    return dict(rate_start=float(r0), rate_end=float(r1), dbl_days_start=float(365.25 / r0) if r0 > 0 else None, dbl_days_end=float(365.25 / r1) if r1 > 0 else None,
                rr_hat=float(r1 / r0) if r0 > 0 else None, beta2=float(b[2]))

def analyse(D, h, sim, tag):
    t0 = time.time(); o = D.order; to = D.t[o]; yo = h[o]; M = D.M; span = float(D.t.max() - D.t.min())
    lin = np.polyfit(D.t, h, 1); rate_lin = float(lin[0])
    res = dict(tag=tag, M=M, first_date=str(min(D.dates)), last_date=str(max(D.dates)), span_years=span, linear_slope_dbl_per_yr=rate_lin, linear_doubling_days=float(365.25 / rate_lin),
               sota_records=[D.names[i] for i in o if f4.rec_mask(h[o])[list(o).index(i)]], n_records=int(f4.rec_mask(yo).sum()))
    # ---- (1) all-model fixed-date regression: OLS, HC3 (t, M-3), wild, permutation
    R = f3.Reg(D.t); reg = f3.reg_tests(R, h, np.random.default_rng(np.random.SeedSequence([SEED, 1])), np.random.default_rng(np.random.SeedSequence([SEED, 2])), B_w=B_W, B_p=B_P)
    res['reg'] = reg; res['calendar_allmodel'] = calendar(D.t, h)
    b2 = reg['reg_c']; res['rr_eq_allmodel'] = rr_eq(b2, span, rate_lin)
    # HC3 analytic interval for beta2
    _, _, hc3t = R.stats_(h); se = b2 / hc3t if hc3t != 0 else float('nan'); tc_ = stats.t.ppf(0.975, R.df)
    res['hc3_ci95_beta2'] = [float(b2 - tc_ * abs(se)), float(b2 + tc_ * abs(se))]; res['hc3_se'] = float(abs(se))
    # ---- (2) parametric-bootstrap family on the selection statistics (A3 definitions, B=19999, audit q=0.25 redrawn inside the bootstrap)
    pb = f4.pb_calibrated(D, sim, h, np.random.default_rng(np.random.SeedSequence([SEED, 3])), B=B_PB)
    res['pb'] = pb
    for k in f4.TESTS_PB:
        c = pb.get(k + '_c')
        if c is not None and k in ('sota', 'mir', 'heck', 'ipw', 'audit'): res[f'rr_eq_{k}'] = rr_eq(c, span, rate_lin)
    # ---- (3) audit-draw stability: 200 independent audit draws of the observed statistic
    ra = np.random.default_rng(np.random.SeedSequence([SEED, 4])); Y = np.repeat(yo[None], N_AUD, 0)
    au = f4.stat_batch(to, Y, 0.25, ra.random(Y.shape))['audit']
    res['audit_draws'] = dict(median=float(np.nanmedian(au)), q25=float(np.nanquantile(au, .25)), q75=float(np.nanquantile(au, .75)), min=float(np.nanmin(au)), max=float(np.nanmax(au)), n_nan=int(np.isnan(au).sum()))
    # ---- (4) model-level bootstrap percentile intervals (descriptive; coverage NOT validated)
    rb = np.random.default_rng(np.random.SeedSequence([SEED, 5])); names = np.array(D.names); keys = ['all', 'sota', 'heck', 'audit']
    acc = {k: [] for k in keys}; cal = []
    for b in range(B_MB):
        idx = rb.integers(0, M, M); idx = idx[np.lexsort((idx, D.t[idx]))]   # sort by date (ties by original index)
        tb = D.t[idx]; yb = h[idx]; sb = f4.stat_batch(tb, yb, 0.25, rb.random(yb.shape))
        for k in keys: acc[k].append(float(sb[k]))
        cc = calendar(tb, yb) if len(np.unique(tb)) >= 3 else None
        if cc is not None: cal.append(cc)
    mb = {}
    for k in keys:
        v = np.array(acc[k]); v = v[~np.isnan(v)]
        mb[k] = dict(n=int(len(v)), lo=float(np.quantile(v, .025)), hi=float(np.quantile(v, .975)), median=float(np.median(v)))
        if k in ('all', 'sota', 'heck', 'audit'): mb[k]['rr_eq_lo'] = rr_eq(mb[k]['lo'], span, rate_lin); mb[k]['rr_eq_hi'] = rr_eq(mb[k]['hi'], span, rate_lin)
    rrh = np.array([c['rr_hat'] for c in cal if c['rr_hat'] is not None and np.isfinite(c['rr_hat'])])
    mb['rr_hat_allmodel'] = dict(n=int(len(rrh)), lo=float(np.quantile(rrh, .025)), hi=float(np.quantile(rrh, .975)), median=float(np.median(rrh)), n_start_rate_nonpositive=int(len(cal) - len(rrh)))
    res['model_bootstrap'] = mb; res['runtime_s'] = time.time() - t0
    return res

def main():
    mode = sys.argv[1]
    assert fc.sha256(f'{DATA}/runs_v1_0.jsonl') == fc.RUNS_SHA, 'runs sha mismatch'
    P = json.load(open(SIMVAL))['params']
    Dall = fc.load_real(); _, _, b0 = fc.horizons_of(Dall)
    cfg = [c for c in g2.CELLS if c['name'] == 'R_null_val'][0]['cfg']; sim = f3.Sim3(Dall, b0, P, cfg)
    if mode == 'smoke':
        D, h = sim.generate(np.random.default_rng(np.random.SeedSequence([SEED, 99]))); res = analyse(D, h, sim, 'smoke_synthetic_R_null_val')
        json.dump(res, open(f'{OUT}/smoke.json', 'w'), indent=1, default=float); print(json.dumps(res, indent=1, default=float)); return
    path = f'{OUT}/real_v10.json'; assert not os.path.exists(path), 'one-shot already used'
    D = fc.load_real(cutoff=CUTOFF); h, _, _ = fc.horizons_of(D)
    assert D.M == 33 and Dall.M == 33, (D.M, Dall.M)
    res = analyse(D, h, sim, 'real_METR_v1.0_cutoff_2025-11-30')
    res['pins'] = dict(runs_sha256=fc.sha256(f'{DATA}/runs_v1_0.jsonl'), dates_sha256=fc.sha256(f'{DATA}/release_dates.yaml'), simval_sha256=fc.sha256(SIMVAL),
                       numpy=np.__version__, scipy=__import__('scipy').__version__, prereg_commit=os.environ.get('PREREG_SHA', 'unset'))
    res['model_horizons'] = [(D.names[i], str(D.dates[i]), float(h[i])) for i in D.order]
    json.dump(res, open(path, 'w'), indent=1, default=float); print(json.dumps({k: v for k, v in res.items() if k != 'model_horizons'}, indent=1, default=float))
if __name__ == '__main__': main()
