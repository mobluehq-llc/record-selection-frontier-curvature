"""EXPLORATORY Design Amendment 2 cell table (idea F).  Append-only: seeds = SeedSequence([79, cell_index, rep]).
role: cal = null cell used ONLY to estimate size-adjusted cutoffs; val = independent null cell (different seeds) used ONLY to validate achieved size of those cutoffs
and as the primary size estimate; alt = alternative, paired with the cal/val cells of the same fam; lad = stepwise-ladder rung (null).
which: cheap = regression tests + iid_sota + mb + pb ; all = cheap + hb + xb.  cost = estimated core-seconds per rep (timed on a compute host; used only for ETA)."""
import hashlib, json
CELLS = []
def C(name, fam, role, reps, which='cheap', **cfg):
    CELLS.append(dict(name=name, fam=fam, role=role, reps=reps, which=which, chunk=100 if which == 'cheap' else 5, cost=0.04 if which == 'cheap' else 9.5, cfg=cfg))
def family(fam, nrep_null, alts, **base):
    C(f'{fam}_null_cal', fam, 'cal', nrep_null, truth='exp', **base); C(f'{fam}_null_val', fam, 'val', nrep_null, truth='exp', **base)
    for nm, n, a in alts: C(f'{fam}_{nm}', fam, 'alt', n, **{**base, **a})
RR = lambda r: dict(truth='quad', rr=r)
LOGI_DEC = dict(truth='logi', um=0.35, ks=5.0); LOGI_MID = dict(truth='logi', um=0.65, ks=6.0)
# F1: real design, real dates, calibrated noise (the primary family)
family('R', 40000, [('rr0.5', 10000, RR(0.5)), ('rr1.25', 10000, RR(1.25)), ('rr1.5', 10000, RR(1.5)), ('rr2', 10000, RR(2.0)), ('rr3', 10000, RR(3.0)),
                    ('rr4', 10000, RR(4.0)), ('logi_dec', 10000, LOGI_DEC), ('logi_mid', 10000, LOGI_MID)])
# F2: evenly spaced release dates
family('E', 20000, [('rr1.5', 10000, RR(1.5)), ('rr2', 10000, RR(2.0)), ('logi_dec', 10000, LOGI_DEC)], dates='even')
# F3: suite ceiling (censoring) at three levels of closeness
for d in (0.0, 2.0, 4.0): family(f'K{int(d)}', 20000, [('rr2', 10000, RR(2.0))], clip=True, delta=d)
# F4: model x family interaction; lower model-offset noise
family('MF1', 20000, [('rr2', 10000, RR(2.0))], smf=1.0); family('MF2', 20000, [], smf=2.0)
family('N50', 20000, [('rr2', 10000, RR(2.0))], noise=0.5); family('N25', 20000, [('rr2', 10000, RR(2.0))], noise=0.25)
# Ladder rungs (null): L0 clean Gaussian horizons; L1 + horizon estimation (no task jitter); L2 + censoring (ceiling, delta 2); L3 + task jitter shared across models; L4 + model x family effects
C('LAD0_gauss', 'LAD', 'lad', 20000, truth='exp', gauss=True)
C('LAD1_estimation', 'LAD', 'lad', 20000, truth='exp', sjs=0.0)
C('LAD2_censoring', 'LAD', 'lad', 20000, truth='exp', sjs=0.0, clip=True, delta=2.0)
C('LAD3_taskdep', 'LAD', 'lad', 20000, truth='exp', clip=True, delta=2.0)
C('LAD4_modfam', 'LAD', 'lad', 20000, truth='exp', clip=True, delta=2.0, smf=1.0)
# X: the expensive task-level bootstraps (hb, xb) alongside everything else, at the real design only
C('X_null_cal', 'X', 'cal', 2000, 'all', truth='exp'); C('X_null_val', 'X', 'val', 2000, 'all', truth='exp')
C('X_rr2', 'X', 'alt', 1500, 'all', **RR(2.0)); C('X_logi_dec', 'X', 'alt', 800, 'all', **LOGI_DEC); C('X_rr0.5', 'X', 'alt', 600, 'all', **RR(0.5))
def grid_hash(): return hashlib.sha256(json.dumps(CELLS, sort_keys=True).encode()).hexdigest()[:16]
if __name__ == '__main__':
    print(len(CELLS), 'cells; grid', grid_hash(), '; cheap reps', sum(c['reps'] for c in CELLS if c['which'] == 'cheap'), '; all reps', sum(c['reps'] for c in CELLS if c['which'] == 'all'),
          '; est core-h', round(sum(c['reps'] * c['cost'] for c in CELLS) / 3600, 1))
