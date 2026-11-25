"""EXPLORATORY design-stage cell table.  Cell index = position in CELLS (FIXED; append only, never reorder: seeds depend on it).
reps are multiplied by the REPS_SCALE given to run_grid.py."""
import hashlib, json
def C(name, reps, **cfg): return dict(name=name, reps=reps, cfg=cfg)
NULL, POW = 100, 40            # base replicate counts (x scale): null cells need small CP width, power cells less
CELLS = [
 # (a) real design, real dates, calibrated noise: exp null vs super-exp (rr = end/start rate) vs logistic (S-curve) alternatives
 C('A_null_exp', NULL, truth='exp'),
 C('A_sup_rr1.5', POW, truth='quad', rr=1.5), C('A_sup_rr2', POW, truth='quad', rr=2.0),
 C('A_sup_rr3', POW, truth='quad', rr=3.0), C('A_sup_rr4', POW, truth='quad', rr=4.0),
 C('A_logi_dec', POW, truth='logi', um=0.35, ks=5.0), C('A_logi_mid', POW, truth='logi', um=0.65, ks=6.0),
 # (a') lower model-offset noise (x0.5, x0.25): does any test reach size when selection noise shrinks?
 C('A_null_n0.5', NULL // 2 + 20, truth='exp', noise=0.5), C('A_null_n0.25', NULL // 2 + 20, truth='exp', noise=0.25),
 C('A_sup_rr2_n0.5', POW, truth='quad', rr=2.0, noise=0.5), C('A_sup_rr2_n0.25', POW, truth='quad', rr=2.0, noise=0.25),
 # (b) null with stronger crossed model x task-family effects (model-level vs crossed bootstrap)
 C('B_null_mf1', NULL, truth='exp', smf=1.0), C('B_null_mf2', NULL, truth='exp', smf=2.0),
 C('B_sup_rr2_mf1', POW, truth='quad', rr=2.0, smf=1.0),
 # (c) censoring: suite ceiling at max task length; delta = shift of whole trajectory (log2 min) toward the ceiling
 C('C_null_clip0', NULL // 2 + 20, truth='exp', clip=True),
 C('C_null_clip2', NULL // 2 + 20, truth='exp', clip=True, delta=2.0), C('C_null_clip4', NULL // 2 + 20, truth='exp', clip=True, delta=4.0),
 C('C_sup_rr2_clip2', POW, truth='quad', rr=2.0, clip=True, delta=2.0), C('C_sup_rr2_clip4', POW, truth='quad', rr=2.0, clip=True, delta=4.0),
 C('C_null_noclip4', NULL // 2 + 20, truth='exp', delta=4.0),
 # (d) the null at actual vs evenly spaced release dates
 C('D_null_even', NULL, truth='exp', dates='even'), C('D_sup_rr2_even', POW, truth='quad', rr=2.0, dates='even'),
 C('D_logi_dec_even', POW, truth='logi', um=0.35, ks=5.0, dates='even'),
]
def grid_hash(): return hashlib.sha256(json.dumps(CELLS, sort_keys=True).encode()).hexdigest()[:16]
