"""EXPLORATORY Design Amendment 3 runner (synthetic data only).  Resumable and detached-safe: work unit = (cell, chunk) -> results/cells/<name>/c<idx>.jsonl (tmp+rename);
a re-launch with the same arguments skips every finished chunk.  Units are ordered by fraction-complete.  manifest.json is rewritten after every unit with a cost-weighted ETA basis.
Usage: /usr/bin/python3 run_a3.py WORKERS [--cells a,b] [--smoke]       env: FDATA, FOUT, PREREG_SHA.   Never kills processes."""
import os
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS'): os.environ[v] = '1'
import sys, json, time, math, hashlib, multiprocessing as mp, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fcore as fc, fdesign3 as f3, fdesign4 as f4, grid_a3 as grid
DATA = os.environ.get('FDATA', os.path.join(HERE, 'data')); OUT = os.environ.get('FOUT', os.path.join(HERE, 'results'))
fc.DATA = DATA
D0 = fc.load_real(data=DATA); h0, _, b0 = fc.horizons_of(D0)
P = json.load(open(f'{DATA}/F_simulator_validation.json'))['params']
SIMS = {}
def get_sim(ci):
    if ci not in SIMS: SIMS[ci] = f3.Sim3(D0, b0, P, grid.CELLS[ci]['cfg'])
    return SIMS[ci]
def work(u):
    ci, k, nrep = u; cell = grid.CELLS[ci]; sim = get_sim(ci); CH = cell['chunk']; rows = []; t0 = time.time()
    for rep in range(k * CH, min(nrep, (k + 1) * CH)):
        o = f4.run_rep4(sim, cell['a2_index'], rep, ci); o.update(cell=cell['name'], rep=rep); rows.append(o)
    dd = f"{OUT}/cells/{cell['name']}"; os.makedirs(dd, exist_ok=True)
    tmp = f"{dd}/.c{k:04d}.tmp"; open(tmp, 'w').write('\n'.join(json.dumps(r, default=float) for r in rows) + '\n'); os.replace(tmp, f"{dd}/c{k:04d}.jsonl")
    return ci, k, len(rows), time.time() - t0, len(rows) * cell['cost']
def fsha(p): return hashlib.sha256(open(os.path.join(HERE, p), 'rb').read()).hexdigest()[:16]
def main():
    nw = int(sys.argv[1]); smoke = '--smoke' in sys.argv; only = None
    if '--cells' in sys.argv: only = set(sys.argv[sys.argv.index('--cells') + 1].split(','))
    os.makedirs(OUT, exist_ok=True); plan = {}
    for ci, c in enumerate(grid.CELLS):
        if only and c['name'] not in only: continue
        plan[ci] = c['chunk'] if smoke else c['reps']
    units = []; total_cost = 0.0; done_cost0 = 0.0
    for ci, n in plan.items():
        CH = grid.CELLS[ci]['chunk']; nch = math.ceil(n / CH)
        for k in range(nch):
            reps_k = min(n, (k + 1) * CH) - k * CH; cst = reps_k * grid.CELLS[ci]['cost']; total_cost += cst
            if os.path.exists(f"{OUT}/cells/{grid.CELLS[ci]['name']}/c{k:04d}.jsonl"): done_cost0 += cst
            else: units.append((k / nch, ci, k, n))
    units.sort(); total_u = sum(math.ceil(n / grid.CELLS[ci]['chunk']) for ci, n in plan.items())
    man = dict(grid_hash=grid.grid_hash(), runs_sha_ok=fc.sha256(f'{DATA}/runs_v1_0.jsonl') == fc.RUNS_SHA, prereg_commit=os.environ.get('PREREG_SHA', 'unset'),
               code_sha16={f: fsha(f) for f in ('fcore.py', 'fdesign.py', 'fsim.py', 'fdesign3.py', 'fdesign4.py', 'grid_a3.py', 'run_a3.py')}, workers=nw, smoke=smoke,
               plan={grid.CELLS[ci]['name']: n for ci, n in plan.items()}, status='EXPLORATORY design-stage; synthetic data only', launched=time.ctime(),
               total_cost_core_s=total_cost, done_cost_at_launch=done_cost0)
    assert man['runs_sha_ok'], 'runs file sha mismatch'
    if not smoke and man['prereg_commit'] == 'unset': sys.exit('refusing a real run without PREREG_SHA (the pre-registration commit)')
    def write_man(done_units, done_cost, state):
        man.update(units_total=total_u, units_pending_at_launch=len(units), units_done_this_launch=done_units, done_cost_this_launch=done_cost,
                   elapsed_s_this_launch=time.time() - t0, state=state, updated=time.ctime())
        json.dump(man, open(f'{OUT}/manifest.json.tmp', 'w'), indent=1); os.replace(f'{OUT}/manifest.json.tmp', f'{OUT}/manifest.json')
    t0 = time.time(); dn = 0; dc = 0.0; write_man(0, 0.0, 'running')
    print(f'pending units {len(units)} / {total_u}, workers {nw}, grid {grid.grid_hash()}', flush=True)
    with mp.Pool(nw) as pool:
        for ci, k, n, dt_, cst in pool.imap_unordered(work, [(ci, k, nr) for _, ci, k, nr in units], chunksize=1):
            dn += 1; dc += cst; write_man(dn, dc, 'running')
            print(f"{dn}/{len(units)} {grid.CELLS[ci]['name']} chunk{k} {n}reps {dt_:.0f}s elapsed {(time.time()-t0)/3600:.2f}h", flush=True)
    write_man(dn, dc, 'complete'); print('complete', flush=True)
if __name__ == '__main__': main()
