"""Step 0: recompute from the stored tables the METR v1.0 non-record count and the audit enumeration; apply the frozen held-out rule."""
import json, math
import numpy as np
from topj_common import *
res = {}
for v in ('1.0', '1.1'):
    s = metr(v); r, prev = records(s['y']); nn = int((~r).sum()); m = math.ceil(0.25 * nn)
    res[v] = dict(models=len(s['y']), records=int(r.sum()), nonrecords=nn, m=m, comb=math.comb(nn, m), tuples=nn ** m, lo=s['lo'], lo_flag=s['lo_flag'], y_min=float(s['y'].min()), y_max=float(s['y'].max()))
print('METR v1.0 non-records (recomputed):', res['1.0']['nonrecords'], 'review says 16; m =', res['1.0']['m'], 'C =', res['1.0']['comb'], '(review 1820)')
ep = epoch_all(); chosen, rows = heldout_rule(ep)
res['heldout_chosen'] = chosen; res['epoch_rows_sorted_by_sha'] = rows
print('held-out:', chosen)
json.dump(res, open(OUT + '/step0.json', 'w'), indent=1); print(json.dumps(res, indent=1))
