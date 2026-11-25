"""Audit of the size-adjusted-power calculation of analyze_design.py (referee item 4: mb_sota adjusted early-logistic power 4.8% -> 26%).
Usage: python3 audit_adjustment.py <base results dir, e.g. design/results>.  Reads cells only; changes nothing.
For the percentile-CI tests the raw rule is 'CI excludes 0' which is EXACTLY |z|>1 for z=(lo+hi)/(hi-lo).  analyze_design's adjustment replaced it by EQUAL-TAIL
null quantiles of z (2.5% each).  When the null z-distribution is not symmetric about 0 the two rules are different two-sided rules, so rejection sets are not nested."""
import sys, os, numpy as np
RD = sys.argv[1]; sys.argv = [sys.argv[0], RD]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_design as a
cells = a.load()
print('cell A_null_exp n =', len(cells['A_null_exp']))
for t in ['mb_all', 'mb_sota', 'hb_all', 'hb_sota', 'xb_all', 'xb_sota']:
    zn = a.zstat(cells['A_null_exp'], t); zn = zn[~np.isnan(zn)]; lo, hi = np.quantile(zn, [.025, .975])
    # identity check: raw two-sided rule == |z|>1 on every replicate
    r = cells['A_null_exp']; L = np.array([x[t + '_lo'] for x in r]); H = np.array([x[t + '_hi'] for x in r]); z = (L + H) / np.maximum(H - L, 1e-9)
    ident = bool(np.all(((L > 0) | (H < 0)) == (np.abs(z) > 1)))
    print(f'\n{t}: raw rule == |z|>1 on all null replicates: {ident}; null z quantiles 2.5/50/97.5 = {np.quantile(zn,[.025,.5,.975]).round(3)}')
    print(f'  null raw rejection: upward (z>1) {100*(zn>1).mean():.2f}%  downward (z<-1) {100*(zn<-1).mean():.2f}%   | adjusted equal-tail cutoffs [{lo:.3f},{hi:.3f}]')
    for c in ['A_logi_dec', 'A_logi_mid', 'A_sup_rr2']:
        za = a.zstat(cells[c], t); za = za[~np.isnan(za)]
        print(f'  {c}: raw up {100*(za>1).mean():.1f}% down {100*(za<-1).mean():.1f}% | adjusted equal-tail up {100*(za>hi).mean():.1f}% down {100*(za<lo).mean():.1f}% two {100*((za>hi)|(za<lo)).mean():.1f}%')
