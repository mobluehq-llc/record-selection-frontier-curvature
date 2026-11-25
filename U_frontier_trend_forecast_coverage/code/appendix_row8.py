import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
import ucore as u, numpy as np
from scipy import stats
t,y,nm=u.load('compute'); m=t>=2022+31/365.25
x=t[m]; yy=y[m]*np.log2(10)  # log2 FLOP
r=stats.linregress(x,yy); ci=stats.t.ppf(.975,len(x)-2)*r.stderr
dt=lambda s:12/s
print('n',len(x),'doubling months',dt(r.slope),'95% CI',dt(r.slope+ci),dt(r.slope-ci))
