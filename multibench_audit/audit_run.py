"""F multi-benchmark audit runner. usage: audit_run.py series | run --workers N --perms 1000 | checks | summarize
Never kills processes, refuses to overwrite outputs, resumable via manifest."""
import sys, os, json, argparse, platform, time
import numpy as np, pandas as pd, scipy
from multiprocessing import Pool
import audit_core as ac

HERE = os.path.dirname(os.path.abspath(__file__)); RES = HERE + '/results'
SERIES_JSON = RES + '/audit_series.json'; MANIFEST = RES + '/audit_manifest.jsonl'; BLOCK = 50

def build_series():
    if os.path.exists(SERIES_JSON): sys.exit('refusing to overwrite ' + SERIES_JSON)
    meta = pd.read_csv(f'{ac.DATA}/benchmark_metadata.csv')
    elig, excl = [], []
    for _, r in meta.sort_values('source_file').iterrows():
        if not isinstance(r.source_file, str) or not isinstance(r.score_column, str):
            excl.append(dict(benchmark=r.benchmark, reason='no source_file/score_column in metadata')); continue
        try:
            d, ceil = ac.load_series(r.source_file, r.score_column, float(r.scale), float(r.score_ceiling))
            d, tr = ac.prepare(d, ceil)
            ok, why, info = ac.eligibility(d)
        except Exception as e:
            excl.append(dict(benchmark=r.benchmark, file=r.source_file, reason='error ' + repr(e)[:120])); continue
        rec = dict(benchmark=r.benchmark, file=r.source_file, col=r.score_column, scale=float(r.scale), ceiling=float(r.score_ceiling), transform=tr, **info,
                   sha256=ac.sha256(f'{ac.DATA}/{r.source_file}'))
        (elig if ok else excl).append(rec if ok else dict(rec, reason=why))
    elig = sorted(elig, key=lambda x: x['file'])
    for i, e in enumerate(elig): e['index'] = i
    # METR reference (F's reference series; not in bar denominators)
    d, ceil = ac.load_series('metr_time_horizons_external.csv', 'Time horizon', 1.0, 0.0)
    d, tr = ac.prepare(d, 0.0, transform='log2'); ok, why, info = ac.eligibility(d)
    ref = dict(benchmark='METR v1.1 time horizon (minutes)', file='metr_time_horizons_external.csv', col='Time horizon', scale=1.0, ceiling=0.0, transform='log2', index=900, **info, eligible=ok, why=why,
               sha256=ac.sha256(f'{ac.DATA}/metr_time_horizons_external.csv'))
    json.dump(dict(eligible=elig, excluded=excl, reference=ref), open(SERIES_JSON, 'w'), indent=1)
    with open(RES + '/audit_pins.txt', 'w') as f:
        f.write(f'python {platform.python_version()}\nnumpy {np.__version__}\nscipy {scipy.__version__}\npandas {pd.__version__}\nB={ac.B} SAT={ac.SAT} seed_base={ac.BASE_SEED}\n')
        f.write(f'audit_core.py {ac.sha256(HERE + "/audit_core.py")}\naudit_run.py {ac.sha256(HERE + "/audit_run.py")}\n')
        f.write(f'epoch benchmark_metadata.csv {ac.sha256(ac.DATA + "/benchmark_metadata.csv")}\n')
        for e in elig + [ref]: f.write(f'{e["file"]} {e["sha256"]}\n')
    print(len(elig), 'eligible;', len(excl), 'excluded')
    for e in elig: print(e['index'], e['file'], e['transform'], e['models'], e['records'], e['months'], e['orgs'])

def get_frame(s):
    d, ceil = ac.load_series(s['file'], s['col'], s['scale'], s['ceiling'])
    d, tr = ac.prepare(d, ceil, transform=s['transform'])
    assert ac.sha256(f'{ac.DATA}/{s["file"]}') == s['sha256'], 'HASH MISMATCH ' + s['file']
    return d

def cell(args):
    s, cname, block, perms = args
    d = get_frame(s); cidx = ac.CONSTR.index(cname)
    sd = float(d.y.std()); span = float(d.t.max() - d.t.min())
    codes_all = pd.factorize(d.o.values)[0]
    rows = []
    for rep in range(block * BLOCK, min(perms, (block + 1) * BLOCK)):
        t, order = ac.permuted_frame(d, rep, s['index'])
        y0 = d.y.values[order]; codes = codes_all[order]
        y, c = ac.planted(t, y0, cname, sd, span)
        r = ac.run_one(t, y, codes, [ac.BASE_SEED, s['index'], rep, cidx, 1], span)
        r.update(rep=rep, c=c); rows.append(r)
    return dict(series=s['index'], construction=cname, block=block, rows=rows)

def run(workers, perms):
    S = json.load(open(SERIES_JSON)); series = S['eligible'] + ([S['reference']] if S['reference'].get('eligible') else [])
    done = set()
    if os.path.exists(MANIFEST):
        for l in open(MANIFEST):
            j = json.loads(l); done.add((j['series'], j['construction'], j['block']))
    nb = (perms + BLOCK - 1) // BLOCK
    tasks = [(s, c, b, perms) for s in series for c in ac.CONSTR for b in range(nb) if (s['index'], c, b) not in done]
    print(len(tasks), 'blocks to do', flush=True); t0 = time.time()
    with Pool(workers) as p, open(MANIFEST, 'a') as f:
        for k, res in enumerate(p.imap_unordered(cell, tasks)):
            f.write(json.dumps(res) + '\n'); f.flush()
            if k % 20 == 0: print(k, len(tasks), round(time.time() - t0), flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('--workers', type=int, default=4); ap.add_argument('--perms', type=int, default=1000)
    a = ap.parse_args()
    if a.cmd == 'series': build_series()
    elif a.cmd == 'run': run(a.workers, a.perms)
    else: sys.exit('unknown')
