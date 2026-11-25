# outcome-free power statement: n_eff = origins thinned to >=12 months apart, summed over eligible series
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
import ucore as u, numpy as np
from scipy import stats
n=0
for s in u.ORDER:
    t,y,nm=u.load(s); ok,og,rt=u.eligible(t,y,nm)
    if not ok: continue
    og12=[o for o in og if o+1<=t.max()+1e-9]; k=len(og12[::2]) if og12 else 0
    print(s,len(og12),'thinned',k); n+=k
print('n_eff',n)
def cp_upper(k,n,a=0.05): return 1.0 if k==n else stats.beta.ppf(1-a,k+1,n-k)
for nom in (0.95,0.80):
    # reject H0 coverage>=nom if one-sided CP upper(95%) < nom
    kmax=max([k for k in range(n+1) if cp_upper(k,n)<nom],default=-1)
    for g in np.arange(0.01,0.60,0.01):
        pw=stats.binom.cdf(kmax,n,nom-g)
        if pw>=0.8: print('nominal',nom,'kmax',kmax,'detectable gap (power>=0.8)',round(g,2)); break
    else: print('nominal',nom,'no gap detectable')
