"""TOP-JOURNAL AMENDMENT (F/PLAN.md, commit 947b4ea): shared loaders. Stage layout in $TOPJ_STAGE (default: the bundle root)."""
import os, sys, json, hashlib, math
import numpy as np
STAGE = os.environ.get('TOPJ_STAGE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, STAGE + '/code'); sys.path.insert(0, STAGE + '/multibench_audit')
import fcore as fc          # noqa
import audit_core as ac     # noqa
fc.DATA = STAGE + '/data/metr'
ac.DATA = STAGE + '/data/epoch/epoch_benchmarks'
OUT = os.environ.get('TOPJ_OUT', STAGE + '/topj/results_rerun'); os.makedirs(OUT, exist_ok=True)
LOGIT_FLOOR = math.log(0.005 / 0.995)   # prepare() clips scores to [0.005,0.995] before logit


def sha256_str(s):
    return hashlib.sha256(s.encode()).hexdigest()


def metr(version):
    """METR series sorted by (date, name). lo = 0 (log2 horizon scale floor as registered); flagged if any observed y < 0."""
    if version == '1.0':
        D = fc.load_real(runs_path=STAGE + '/F/data_metr/runs_v1_0.jsonl', dates_path=STAGE + '/F/data_metr/release_dates.yaml')
        assert fc.sha256(STAGE + '/F/data_metr/runs_v1_0.jsonl') == fc.RUNS_SHA
    else:
        D = fc.load_real(runs_path=STAGE + '/F/holdout_data/runs_v1_1.jsonl', dates_path=STAGE + '/F/holdout_data/release_dates_main.yaml')
    h, _, _ = fc.horizons_of(D); o = D.order
    y = h[o]; lo = 0.0; flag = None
    if y.min() < lo:
        flag = f'observed y min {y.min():.4f} < 0; lo set to observed min'; lo = float(y.min())
    return dict(name=f'METR v{version}', names=[D.names[i] for i in o], t=D.t[o].copy(), y=y.copy(), lo=lo, lo_flag=flag, kind='metr')


def epoch_all():
    S = json.load(open(STAGE + '/F/multibench_audit/results/audit_series.json'))['eligible']
    out = []
    for s in S:
        d, ceil = ac.load_series(s['file'], s['col'], s['scale'], s['ceiling'])
        d, tr = ac.prepare(d, ceil, transform=s['transform'])
        y = d.y.values.astype(float)
        lo = LOGIT_FLOOR if tr == 'logit' else float(y.min())
        out.append(dict(name=s['benchmark'], names=list(d.n), t=d.t.values.astype(float), y=y, lo=lo, lo_flag=None, kind='epoch:' + tr))
    return out


def records(y):
    cm = np.maximum.accumulate(y); r = np.ones(len(y), bool); r[1:] = y[1:] > cm[:-1]
    prev = np.concatenate([[-np.inf], cm[:-1]])   # standing record at release j
    return r, prev


def quad_w(t):
    """third row of (X'X)^-1 X' for the full roster, X=[1,tc,tc^2] (tc = t - mean t)."""
    tc = t - t.mean(); X = np.stack([np.ones_like(tc), tc, tc * tc], 1)
    return np.linalg.solve(X.T @ X, X.T)[2]


def heldout_rule(epoch):
    """frozen rule: 22 Epoch series sorted by sha256(series name); first three with n>=20 and >=10 non-records."""
    rows = []
    for s in sorted(epoch, key=lambda s: sha256_str(s['name'])):
        r, _ = records(s['y']); rows.append((s['name'], len(s['y']), int((~r).sum())))
    chosen = [n for n, m, nr in rows if m >= 20 and nr >= 10][:3]
    return chosen, rows
