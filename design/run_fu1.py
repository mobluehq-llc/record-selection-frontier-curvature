"""EXPLORATORY follow-up-1 runner (synthetic data only).  Resumable: work unit = (cell, chunk of CHUNK reps) -> results/cells/<name>/c<idx>.jsonl (tmp+rename).
Units are ordered by fraction-complete so every cell progresses evenly.  manifest.json is rewritten after every finished unit.
Usage: python -I run_grid.py SCALE WORKERS [--cells name,name] [--smoke]
Seeds: SeedSequence([77, cell_index, rep]).  Never kills processes by name."""
import os
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'): os.environ[v] = '1'
import sys, json, time, math, multiprocessing as mp, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fcore as fc, fdesign, fdesign_ext as fx, grid_fu1 as grid
DATA = os.environ.get('FDATA', os.path.join(HERE, 'data')); OUT = os.environ.get('FOUT', os.path.join(HERE, 'results'))
CHUNK = 50
fc.DATA = DATA
D0 = fc.load_real(data=DATA); h0, _, b0 = fc.horizons_of(D0)
P = json.load(open(f'{DATA}/F_simulator_validation.json'))['params']
SIMS = {}
def get_sim(ci):
    if ci not in SIMS: SIMS[ci] = fx.Sim2(D0, b0, P, grid.CELLS[ci]['cfg'])
    return SIMS[ci]
def work(u):
    ci, chunk, nrep = u; cell = grid.CELLS[ci]; sim = get_sim(ci); rows = []; t0 = time.time()
    for rep in range(chunk * CHUNK, min(nrep, (chunk + 1) * CHUNK)):
        ss = np.random.SeedSequence([78, ci, rep]); s1, s2 = ss.spawn(2)
        d = sim.draw(np.random.default_rng(s1)); o = fx.run_tests2(d, sim, s2, cell["which"]); o.update(cell=cell['name'], rep=rep); rows.append(o)
    dd = f"{OUT}/cells/{cell['name']}"; os.makedirs(dd, exist_ok=True)
    tmp = f"{dd}/.c{chunk:04d}.tmp"; open(tmp, 'w').write('\n'.join(json.dumps(r, default=float) for r in rows) + '\n'); os.replace(tmp, f"{dd}/c{chunk:04d}.jsonl")
    return ci, chunk, len(rows), time.time() - t0
def main():
    scale = float(sys.argv[1]); nw = int(sys.argv[2]); smoke = '--smoke' in sys.argv
    only = None
    if '--cells' in sys.argv: only = set(sys.argv[sys.argv.index('--cells') + 1].split(','))
    os.makedirs(OUT, exist_ok=True)
    plan = {}
    for ci, c in enumerate(grid.CELLS):
        if only and c['name'] not in only: continue
        plan[ci] = max(CHUNK if smoke else 1, int(round(c['reps'] * scale)))
        if smoke: plan[ci] = CHUNK
    units = []
    for ci, n in plan.items():
        nch = math.ceil(n / CHUNK)
        for k in range(nch):
            if not os.path.exists(f"{OUT}/cells/{grid.CELLS[ci]['name']}/c{k:04d}.jsonl"): units.append((k / nch, ci, k, n))
    units.sort(); total_u = sum(math.ceil(n / CHUNK) for n in plan.values())
    man = dict(grid_hash=grid.grid_hash(), runs_sha_ok=fc.sha256(f'{DATA}/runs_v1_0.jsonl') == fc.RUNS_SHA, scale=scale, chunk=CHUNK,
               plan={grid.CELLS[ci]['name']: n for ci, n in plan.items()}, status='EXPLORATORY design-stage; synthetic data only', started=time.ctime())
    assert man['runs_sha_ok'], 'runs file sha mismatch'
    def write_man(done_units, state):
        man.update(units_total=total_u, units_pending_at_start=len(units), units_done_this_launch=done_units, state=state, updated=time.ctime())
        json.dump(man, open(f'{OUT}/manifest.json.tmp', 'w'), indent=1); os.replace(f'{OUT}/manifest.json.tmp', f'{OUT}/manifest.json')
    write_man(0, 'running'); t0 = time.time(); dn = 0
    print(f'pending units {len(units)} / {total_u}, workers {nw}', flush=True)
    with mp.Pool(nw) as pool:
        for ci, k, n, dt_ in pool.imap_unordered(work, [(ci, k, nr) for _, ci, k, nr in units], chunksize=1):
            dn += 1; write_man(dn, 'running')
            print(f"{dn}/{len(units)} {grid.CELLS[ci]['name']} chunk{k} {n}reps {dt_:.0f}s elapsed {(time.time()-t0)/3600:.2f}h", flush=True)
    write_man(dn, 'complete'); print('complete', flush=True)
if __name__ == '__main__': main()
