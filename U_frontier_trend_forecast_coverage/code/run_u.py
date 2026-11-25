import sys, json, time; sys.path.insert(0, __file__.rsplit('/',1)[0])
import ucore as u, numpy as np, pandas as pd
from scipy import stats
t0=time.time(); rows=[]; elig={}
for s in u.ORDER:
    ok,r,_=u.run_series(s); elig[s]=ok; rows+=r; print(s,ok,len(r),round(time.time()-t0),flush=True)
df=pd.DataFrame(rows); df['na']=df.lo.isna()
df['cov']=((df.lo<=df.truth)&(df.truth<=df.hi)).astype(float).where(~df.na)
df['w']=df.hi-df.lo
# interval score (Winkler), alpha=1-level
al=1-df.level
df['iscore']=df.w+(2/al)*np.clip(df.lo-df.truth,0,None)+(2/al)*np.clip(df.truth-df.hi,0,None)
df.to_csv(u.ROOT+'/results/U_rows.csv',index=False)
def cp(k,n,a=0.05):
    if n==0: return (np.nan,np.nan)
    lo=0 if k==0 else stats.beta.ppf(a/2,k,n-k+1); hi=1 if k==n else stats.beta.ppf(1-a/2,k+1,n-k); return lo,hi
rng=np.random.default_rng(np.random.SeedSequence([33,999]))
def cluster_boot(d,R=10000):
    ser=d.series.unique(); g={s:(d[d.series==s]['cov'].sum(),len(d[d.series==s])) for s in ser}
    out=[]
    for _ in range(R):
        pick=rng.choice(ser,len(ser)); k=sum(g[p][0] for p in pick); n=sum(g[p][1] for p in pick); out.append(k/n)
    return np.quantile(out,[0.05,0.5,0.95])
res=[]
for (m,l,h),d in df.groupby(['method','level','h']):
    dm=d[~d.na]; k=int(dm['cov'].sum()); n=len(dm); lo,hi=cp(k,n)
    cb=cluster_boot(dm) if n else (np.nan,)*3
    res.append(dict(method=m,level=l,h=h,met_inside=k,not_met_outside=n-k,not_measured=int(d.na.sum()),n=n,cov=k/n if n else np.nan,
        cp_lo=lo,cp_hi=hi,cb90_lo=cb[0],cb90_hi=cb[2],macro=dm.groupby('series')['cov'].mean().mean() if n else np.nan,
        mean_width=dm.w.mean() if n else np.nan,mean_iscore=dm.iscore.mean() if n else np.nan,n_series=dm.series.nunique()))
R=pd.DataFrame(res); R.to_csv(u.ROOT+'/results/U_summary.csv',index=False)
per=[]
for (s,m,l,h),d in df.groupby(['series','method','level','h']):
    dm=d[~d.na]; k=int(dm['cov'].sum()); n=len(dm); lo,hi=cp(k,n)
    per.append(dict(series=s,method=m,level=l,h=h,inside=k,n=n,not_measured=int(d.na.sum()),cov=k/n if n else np.nan,cp_lo=lo,cp_hi=hi,mean_width=dm.w.mean() if n else np.nan,mean_iscore=dm.iscore.mean() if n else np.nan))
P=pd.DataFrame(per); P.to_csv(u.ROOT+'/results/U_per_series.csv',index=False)
# bars
bars={}
def row(m,l,h): 
    r=R[(R.method==m)&(R.level==l)&(R.h==h)]; return r.iloc[0] if len(r) else None
r=row('M0',0.95,1.0)
bars['bar1_undercover_cb_upper_lt_95']=bool(r.cb90_hi<0.95); bars['bar1_practical_lt_85']=bool(r['cov']<0.85)
# bar2 falsifier: per-series CP contains nominal at both levels, h=1, >= 3 of 4 (4/5 rule scaled: ceil(0.8*n_series))
ns=len(P[(P.method=='M0')&(P.level==0.95)&(P.h==1.0)].series.unique()); need=int(np.ceil(0.8*ns))
within=0
for s in P.series.unique():
    ok=True
    for l in (0.8,0.95):
        q=P[(P.series==s)&(P.method=='M0')&(P.level==l)&(P.h==1.0)]
        if len(q)==0 or q.n.iloc[0]==0 or not (q.cp_lo.iloc[0]<=l<=q.cp_hi.iloc[0]): ok=False
    within+=ok
bars['bar2_series_within_error']=int(within); bars['bar2_needed']=need; bars['bar2_falsifier_fires']=bool(within>=need)
# bar3 for M2 and M3
for m in ('M1','M2','M3'):
    rm=row(m,0.95,1.0)
    if rm is None or rm.n==0: bars[f'bar3_{m}']='not measured'; continue
    a=df[(df.method=='M0')&(df.level==0.95)&(df.h==1.0)]; b=df[(df.method==m)&(df.level==0.95)&(df.h==1.0)&(~df.na)]
    mm=a.merge(b,on=['series','origin','h'],suffixes=('0','m')); wr=float((mm.wm/mm.w0).median()) if len(mm) else np.nan
    imp=0;tot=0
    for s in P.series.unique():
        p0=P[(P.series==s)&(P.method=='M0')&(P.level==0.95)&(P.h==1.0)]; pm=P[(P.series==s)&(P.method==m)&(P.level==0.95)&(P.h==1.0)]
        if len(pm) and pm.n.iloc[0]>0: tot+=1; imp+=int(pm['cov'].iloc[0]>p0['cov'].iloc[0])
    bars[f'bar3_{m}']=dict(pooled_cov=float(rm['cov']),median_width_ratio_vs_M0=wr,series_improved=imp,series_measured=tot,
        pass_=bool(rm['cov']>=0.90 and wr<=1.5 and imp>=int(np.ceil(0.8*max(tot,1)))))
json.dump(dict(elig=elig,bars=bars,runtime_s=time.time()-t0),open(u.ROOT+'/results/U_bars.json','w'),indent=1,default=float)
print(R.to_string()); print(P[(P.h==1.0)&(P.level==0.95)].to_string()); print(json.dumps(bars,indent=1,default=float))
