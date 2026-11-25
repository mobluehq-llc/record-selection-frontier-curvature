"""EXPLORATORY follow-up-1 cell table (idea F design stage).  Append-only: seeds = SeedSequence([78, cell_index, rep]).
'cheap' cells run iid + model-bootstrap + parametric-bootstrap only (~0.1-1 s/rep); 'all' cells add hb + xb (~7 s/rep at M=33, ~linear in M)."""
import hashlib, json
def C(name, reps, which, **cfg): return dict(name=name, reps=reps, which=which, cfg=cfg)
CELLS = []
# Arm P: size/power of the cheap tests at the real design (base-grid CIs straddled 5%).  Timing on a compute host: ~0.02 s/rep -> 200000 reps = CP half-width ~0.1pp
for nm, reps, cfg in [('P_null_exp', 200000, dict(truth='exp')), ('P_null_mf1', 200000, dict(truth='exp', smf=1.0)), ('P_null_mf2', 200000, dict(truth='exp', smf=2.0)),
                      ('P_null_clip0', 200000, dict(truth='exp', clip=True)), ('P_null_clip2', 200000, dict(truth='exp', clip=True, delta=2.0)),
                      ('P_sup_rr2', 50000, dict(truth='quad', rr=2.0)), ('P_sup_rr3', 50000, dict(truth='quad', rr=3.0)), ('P_sup_rr2_mf1', 50000, dict(truth='quad', rr=2.0, smf=1.0))]:
    CELLS.append(C(nm, reps, 'cheap', **cfg))
# Arm M: does size get WORSE as the number of models grows?  mfac in {0.5,1,2,4,8,16} x (null | rr2), cheap tests; plus null with model x family effects
for mf in (0.5, 1, 2, 4, 8, 16):
    CELLS.append(C(f'M_null_x{mf}', 100000, 'cheap', truth='exp', mfac=mf)); CELLS.append(C(f'M_sup_rr2_x{mf}', 20000, 'cheap', truth='quad', rr=2.0, mfac=mf))
for mf in (0.5, 1, 2, 4):
    CELLS.append(C(f'M_null_mf1_x{mf}', 50000, 'cheap', truth='exp', smf=1.0, mfac=mf))
# Arm H: the same M-scaling for the expensive hierarchical / crossed bootstraps (~2-45 s/rep, ~linear in M)
for mf in (0.5, 1, 2, 4, 8):
    CELLS.append(C(f'H_null_x{mf}', 2200, 'all', truth='exp', mfac=mf)); CELLS.append(C(f'H_sup_rr2_x{mf}', 800, 'all', truth='quad', rr=2.0, mfac=mf))
for mf in (1, 2, 4):
    CELLS.append(C(f'H_null_mf1_x{mf}', 800, 'all', truth='exp', smf=1.0, mfac=mf))
def grid_hash(): return hashlib.sha256(json.dumps(CELLS, sort_keys=True).encode()).hexdigest()[:16]
