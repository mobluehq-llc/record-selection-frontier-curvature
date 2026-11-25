"""EXPLORATORY, POST HOC (NOT pre-registered; made for paper v2 on 2026-11-23 after two outside reviews asked for it).
Sensitivity of the all-model quadratic on the real series to early models, and the audit statistic over many audit draws.
Uses the stored refitted horizons (real_data/out/real_v10.json) and the frozen, unmodified test code in ../design (fdesign3.Reg / reg_tests,
fdesign4.stat_batch).  Asserts that it reproduces the stored full-sample values before reporting anything.  None of these numbers has a
size verdict; none enters the pre-registered reading rule.  Output: sensitivity_exploratory.json.
Run: python3 make_sensitivity.py"""
import os, sys, json, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.dirname(HERE); sys.path.insert(0, os.path.join(F, "design"))
import fdesign3 as f3, fdesign4 as f4
R = json.load(open(os.path.join(F, "real_data", "out", "real_v10.json")))
rows = sorted(R["model_horizons"], key=lambda r: (r[1], r[0])); names = [r[0] for r in rows]; d = [dt.date.fromisoformat(r[1]) for r in rows]
t = np.array([(x - d[0]).days for x in d], float) / 365.25; y = np.array([r[2] for r in rows], float); M = len(y)
SEED = 9101   # new stream; the pre-registered run used 9100
def fit(mask, k):
    Rg = f3.Reg(t[mask]); g = f3.reg_tests(Rg, y[mask], np.random.default_rng(np.random.SeedSequence([SEED, 1, k])), np.random.default_rng(np.random.SeedSequence([SEED, 2, k])), B_w=9999, B_p=999)
    tc = t[mask] - t[mask].mean(); X = np.stack([np.ones_like(tc), tc, tc * tc], 1); b = np.linalg.lstsq(X, y[mask], rcond=None)[0]
    r0 = b[1] + 2 * b[2] * tc.min(); r1 = b[1] + 2 * b[2] * tc.max()
    return dict(n=int(mask.sum()), beta2=g["reg_c"], hc3_t=g["hc3_z"], hc3_pup=g["hc3_pup"], wild_pup=g["wild_pup"], rate_start=float(r0), rate_end=float(r1),
                rr_hat=float(r1 / r0) if r0 > 0 else None)
full = fit(np.ones(M, bool), 0)
assert abs(full["beta2"] - R["reg"]["reg_c"]) < 1e-9 and abs(full["hc3_pup"] - R["reg"]["hc3_pup"]) < 1e-9, (full, R["reg"])
out = dict(what="EXPLORATORY post hoc sensitivity; not pre-registered; no size verdicts", seed="SeedSequence([9101, ...])", full=full, leave_one_out=[], drops={})
for i in range(M):
    m = np.ones(M, bool); m[i] = False; r = fit(m, 100 + i); r.update(dropped=names[i], date=str(d[i])); out["leave_one_out"].append(r)
b = np.array([r["beta2"] for r in out["leave_one_out"]]); p = np.array([r["hc3_pup"] for r in out["leave_one_out"]])
out["loo_summary"] = dict(beta2_min=float(b.min()), beta2_max=float(b.max()), dropped_at_min=names[int(b.argmin())], dropped_at_max=names[int(b.argmax())],
                          hc3_pup_max=float(p.max()), dropped_at_pmax=names[int(p.argmax())], n_hc3_pup_below_05=int((p < 0.05).sum()))
pre23 = np.array([x < dt.date(2023, 1, 1) for x in d]); out["n_pre2023"] = int(pre23.sum()); out["pre2023_names"] = [n for n, q in zip(names, pre23) if q]
out["drops"]["pre2023"] = fit(~pre23, 1)
m = np.ones(M, bool); m[:2] = False; out["drops"]["first_two"] = dict(fit(m, 2), dropped=names[:2])
# ---- audit over many draws (same statistic as the registered one: every record, each non-record with probability 0.25 and weight 4)
ra = np.random.default_rng(np.random.SeedSequence([9100, 4])); Y = np.repeat(y[None], 200, 0); au = f4.stat_batch(t, Y, 0.25, ra.random(Y.shape))["audit"]
assert abs(float(np.nanmedian(au)) - R["audit_draws"]["median"]) < 1e-9, "audit draws of the registered run not reproduced"
ra = np.random.default_rng(np.random.SeedSequence([SEED, 3])); N = 20000; Y = np.repeat(y[None], N, 0); au = f4.stat_batch(t, Y, 0.25, ra.random(Y.shape))["audit"]; v = au[~np.isnan(au)]
out["audit_many"] = dict(n=int(N), n_valid=int(len(v)), mean=float(v.mean()), se_mean=float(v.std(ddof=1) / np.sqrt(len(v))), median=float(np.median(v)), q25=float(np.quantile(v, .25)), q75=float(np.quantile(v, .75)),
                         sd=float(v.std(ddof=1)), registered_draw=R["pb"]["audit_c"], share_below_registered=float((v < R["pb"]["audit_c"]).mean()), all_model_beta2=full["beta2"])
json.dump(out, open(os.path.join(HERE, "sensitivity_exploratory.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("full", "loo_summary", "n_pre2023", "pre2023_names", "drops", "audit_many")}, indent=1))
for r in out["leave_one_out"][:5]: print(r["dropped"], round(r["beta2"], 4), round(r["hc3_pup"], 4), round(r["wild_pup"], 4))
