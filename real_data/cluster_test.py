"""F Amendment CL1: developer-clustered inference on the all-model quadratic curvature (PLAN.md 'AMENDMENT CL1'). numpy/scipy only; frozen code not modified.
Usage: python real_data/cluster_test.py"""
import os, sys, json, hashlib, itertools, datetime as dt
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'): os.environ[v] = '1'
import numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'out', 'real_v10.json'); OUT = os.path.join(HERE, 'out', 'cluster_v10.json')
SRC_SHA = open(os.path.join(HERE, '..', 'PLAN.md')).read().split('real_v10.json` (sha256 ')[1][:64]
B = 99999
DEV = {'GPT-2': 'OpenAI', 'davinci-002 (GPT-3)': 'OpenAI', 'gpt-3.5-turbo-instruct': 'OpenAI', 'GPT-4 0314': 'OpenAI', 'GPT-4 1106': 'OpenAI', 'GPT-4 0125': 'OpenAI',
       'GPT-4 Turbo': 'OpenAI', 'GPT-4o': 'OpenAI', 'o1-preview': 'OpenAI', 'o1': 'OpenAI', 'o3': 'OpenAI', 'o4-mini': 'OpenAI', 'gpt-oss-120b': 'OpenAI', 'GPT-5': 'OpenAI', 'GPT-5.1-Codex-Max': 'OpenAI',
       'Claude 3 Opus': 'Anthropic', 'Claude 3.5 Sonnet (Old)': 'Anthropic', 'Claude 3.5 Sonnet (New)': 'Anthropic', 'Claude 3.7 Sonnet': 'Anthropic', 'Claude 4 Opus': 'Anthropic',
       'Claude 4 Sonnet': 'Anthropic', 'Claude 4.1 Opus': 'Anthropic', 'Claude Sonnet 4.5': 'Anthropic', 'Claude Opus 4.5': 'Anthropic',
       'DeepSeek-V3': 'DeepSeek', 'DeepSeek-R1': 'DeepSeek', 'DeepSeek-V3-0324': 'DeepSeek', 'DeepSeek-R1-0528': 'DeepSeek', 'Qwen2-72B': 'Alibaba', 'Qwen2.5-72B': 'Alibaba',
       'Gemini 2.5 Pro Preview': 'Google', 'Grok 4': 'xAI', 'Kimi K2 Thinking': 'Moonshot'}
WEBB = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])

def inv_sqrt(S):
    w, V = np.linalg.eigh(S); return (V / np.sqrt(w)) @ V.T

class CR2:
    def __init__(self, t, cl):
        t = np.asarray(t, float); n = len(t); tc = (t - t.mean()) / 1.0
        self.X = X = np.stack([np.ones(n), tc, tc * tc], 1); self.Bm = Bm = np.linalg.inv(X.T @ X); self.H = H = X @ Bm @ X.T; self.M = M = np.eye(n) - H
        self.n = n; self.cl = np.asarray(cl); self.G = len(set(cl)); c = np.array([0, 0, 1.0]); self.a = X @ Bm @ c   # beta2 = a . y
        W = np.zeros((self.G, n))
        for gi, g in enumerate(sorted(set(cl))):
            idx = np.where(self.cl == g)[0]; Ag = inv_sqrt(M[np.ix_(idx, idx)])      # (I - H_gg)^(-1/2)
            W[gi, idx] = Ag @ self.a[idx]                                              # w_g = A_g (a_g)  (since X_g Bm c = a_g)
        self.W = W; Q = (W @ M).T @ (W @ M)                                              # V = y' Q y,  Q = sum_g (M W_g)(M W_g)'
        self.df = float(np.trace(Q) ** 2 / np.trace(Q @ Q)); self.Q = Q
        X0 = X[:, :2]; self.H0 = X0 @ np.linalg.inv(X0.T @ X0) @ X0.T
    def stat(self, y):                       # y (..., n)
        b2 = y @ self.a; e = y @ self.M; v = ((e @ self.W.T) ** 2).sum(-1); return b2, b2 / np.sqrt(np.maximum(v, 1e-300))
    def hc3(self, y):
        res = y - self.H @ y; v3 = ((self.a ** 2) * (res / (1 - np.diag(self.H))) ** 2).sum(); return float(self.a @ y / np.sqrt(v3))

def analyse(t, y, cl, seed):
    R = CR2(t, cl); b2, tobs = R.stat(y); b2, tobs = float(b2), float(tobs); out = dict(n=len(y), G=R.G, cluster_sizes={g: int(sum(1 for c in cl if c == g)) for g in sorted(set(cl))}, beta2=b2, cr2_t=tobs, cr2_df=R.df)
    out['cr2_p_up'] = float(stats.t.sf(tobs, R.df)); out['cr2_p_two'] = float(2 * stats.t.sf(abs(tobs), R.df))
    h = R.hc3(y); df0 = len(y) - 3; out['hc3_t'] = h; out['hc3_p_up_t(n-3)'] = float(stats.t.sf(h, df0))
    y0 = R.H0 @ y; e0 = y - y0; gi = np.array([sorted(set(cl)).index(c) for c in cl])
    rng = np.random.default_rng(np.random.SeedSequence([9200, seed]))
    w = rng.choice(WEBB, size=(B, R.G)); ys = y0[None] + e0[None] * w[:, gi]; _, ts = R.stat(ys)
    out['webb'] = dict(B=B, p_up=float((1 + (ts >= tobs).sum()) / (B + 1)), p_dn=float((1 + (ts <= tobs).sum()) / (B + 1)), p_two=float((1 + (np.abs(ts) >= abs(tobs)).sum()) / (B + 1)), null_t_q95=float(np.quantile(ts, .95)), null_t_q975=float(np.quantile(ts, .975)))
    pats = np.array(list(itertools.product([-1.0, 1.0], repeat=R.G))); ys = y0[None] + e0[None] * pats[:, gi]; _, tr = R.stat(ys)
    out['rademacher_exact'] = dict(patterns=len(pats), p_up=float((tr >= tobs - 1e-12).sum() / len(pats)), p_two=float((np.abs(tr) >= abs(tobs) - 1e-12).sum() / len(pats)), note='observed t is one of the enumerated patterns (all +1)')
    return out

def main():
    assert hashlib.sha256(open(SRC, 'rb').read()).hexdigest() == SRC_SHA, 'real_v10.json hash mismatch'
    d = json.load(open(SRC)); mh = d['model_horizons']; assert len(mh) == 33 and all(m[0] in DEV for m in mh)
    assert abs(d['reg']['reg_c'] - 0.13847089577971783) < 1e-12
    t = np.array([(dt.date.fromisoformat(m[1]) - dt.date(1970, 1, 1)).days / 365.25 for m in mh]); y = np.array([m[2] for m in mh]); cl = [DEV[m[0]] for m in mh]
    res = dict(source_sha256=SRC_SHA, numpy=np.__version__, scipy=__import__('scipy').__version__)
    res['full'] = analyse(t, y, cl, 1)
    # check reproduction of the registered unclustered statistic (HC3 t = 2.6881434385865317)
    assert abs(res['full']['hc3_t'] - d['reg']['hc3_z']) < 1e-6, (res['full']['hc3_t'], d['reg']['hc3_z'])
    keep = [i for i, m in enumerate(mh) if m[0] not in ('GPT-2', 'davinci-002 (GPT-3)')]
    res['drop_gpt2_gpt3'] = analyse(t[keep], y[keep], [cl[i] for i in keep], 2)
    json.dump(res, open(OUT, 'w'), indent=1, default=float); print(json.dumps(res, indent=1, default=float))
if __name__ == '__main__': main()
