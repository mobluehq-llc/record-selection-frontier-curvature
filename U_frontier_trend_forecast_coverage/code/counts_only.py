# outcome-free: record counts, eligibility and origin counts only
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
import ucore as u, numpy as np
for s in u.ORDER:
    t,y,nm=u.load(s); ok,og,rt=u.eligible(t,y,nm)
    print(s,'points',len(y),'records',len(rt),'eligible',ok,'origins',len(og),
          'first',round(og[0],2) if og else None,'last_data',round(t.max(),2),
          'n12m',sum(1 for o in og if o+1<=t.max()+1e-9),'n24m',sum(1 for o in og if o+2<=t.max()+1e-9))
