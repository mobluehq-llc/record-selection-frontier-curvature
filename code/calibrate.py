"""Calibrate the null simulator (sigma_m, sigma_j, phi) to the real data's residual SD (all-model OLS), cross-model residual correlation, family ICC.
Then validate with 200 fresh datasets (different seeds) and write results/F_simulator_validation.md/json."""
import sys, json, time, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import fcore as fc, fsim
R = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/results'
D = fc.load_real(); h, a, b = fc.horizons_of(D); real = fsim.metrics(D, h, a, b)
a0 = float(h.mean() - fsim.RATE_NULL * (D.t - D.t.min()).mean())
NS = 30
def simmed(sm, sj, phi, tag, n=NS):
    sim = fsim.NullSim(D, b, a0, sm, sj, phi)
    out = []
    for i in range(n):
        rng = np.random.default_rng(np.random.SeedSequence([35, tag, i]))
        d = sim.draw(rng); hh, aa, bb = fc.horizons_of(d); out.append(fsim.metrics(d, hh, aa, bb))
    return {k: float(np.median([o[k] for o in out])) for k in out[0]}
def bisect(f, lo, hi, target, it=12):
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        if f(mid) < target: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)
sm, sj, phi = 0.5, 0.8, 0.5
log = []
for sweep in range(3):
    sj = bisect(lambda v: simmed(sm, v, phi, 1)['crosscorr'], 0.05, 3.0, real['crosscorr'])
    phi = bisect(lambda v: simmed(sm, sj, v, 2)['icc'], 0.0, 1.0, real['icc'], 10)
    sm = bisect(lambda v: simmed(v, sj, phi, 3)['sd_all'], 0.0, 2.5, real['sd_all'])
    m = simmed(sm, sj, phi, 4); log.append(dict(sweep=sweep, sigma_m=sm, sigma_j=sj, phi=phi, **m)); print(log[-1], flush=True)
# validation on fresh seeds
sim = fsim.NullSim(D, b, a0, sm, sj, phi); V = []
for i in range(200):
    rng = np.random.default_rng(np.random.SeedSequence([36, i])); d = sim.draw(rng); hh, aa, bb = fc.horizons_of(d); V.append(fsim.metrics(d, hh, aa, bb))
summ = {}
for k in real:
    v = np.array([o[k] for o in V]); summ[k] = dict(real=real[k], sim_median=float(np.median(v)), sim_p05=float(np.percentile(v, 5)), sim_p95=float(np.percentile(v, 95)),
                                                       real_pctile_in_sim=float((v < real[k]).mean()))
res = dict(params=dict(sigma_m=sm, sigma_j=sj, phi=phi, a0=a0, rate_null=fsim.RATE_NULL), calibration_sweeps=log, validation_n=200, metrics=summ,
           runs_sha256=fc.sha256(f'{fc.DATA}/runs_v1_0.jsonl'))
json.dump(res, open(f'{R}/F_simulator_validation.json', 'w'), indent=1)
L = ['# Null simulator validation (200 fresh datasets, seeds SeedSequence([36,i]); calibration used [35,*])', '',
     f'sigma_m={sm:.3f} (model offset SD, log2 units), sigma_j={sj:.3f} (task jitter SD, log2 min), phi={phi:.3f} (family share of jitter variance)', '',
     '| metric | real | sim median | sim 5-95% | share of sim below real |', '|---|---|---|---|---|']
for k, v in summ.items():
    L.append(f"| {k} | {v['real']:.3f} | {v['sim_median']:.3f} | [{v['sim_p05']:.3f}, {v['sim_p95']:.3f}] | {v['real_pctile_in_sim']:.2f} |")
open(f'{R}/F_simulator_validation.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
