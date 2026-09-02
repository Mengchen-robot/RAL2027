import numpy as np
rng=np.random.default_rng(23)
floor=np.array([0.0015]*3+[np.deg2rad(1.0)]*3)
def logratio(v,rho=0.05): return np.mean(np.log(rho*v[3:]))-np.mean(np.log(v[:3]))
def loganiso(v,rho=0.05):
    hs=np.array([v[0],v[1],v[2],rho*v[3],rho*v[4],rho*v[5]]); return np.log(hs.max()/hs.min())
def sp(a,b):
    ra=np.argsort(np.argsort(a)); rb=np.argsort(np.argsort(b)); return np.corrcoef(ra,rb)[0,1]
def run(mode,n_demo=40,nstage=80):
    T=[];E=[]
    for _ in range(nstage):
        hh=np.concatenate([np.exp(rng.normal(np.log(0.008),1.0,3)),np.exp(rng.normal(np.log(0.15),1.0,3))])
        if mode=='prop':   sd=hh/3.0
        elif mode=='indep':sd=np.concatenate([np.exp(rng.normal(np.log(0.004),1.0,3)),np.exp(rng.normal(np.log(0.08),1.0,3))])
        elif mode=='careless': sd=np.concatenate([np.full(3,0.05),np.full(3,1.2)])   # >> h : pure truncation
        sd=np.maximum(sd,floor)
        Dd=rng.normal(0,1,(6000,6))*sd; Dd=Dd[np.linalg.norm(Dd/hh,axis=1)<=1.][:n_demo]
        if len(Dd)<8: continue
        T.append(hh);E.append(Dd.std(0))
    return len(T),sp([logratio(t) for t in T],[logratio(e) for e in E]),sp([loganiso(t) for t in T],[loganiso(e) for e in E])
print("C) the proxy at both extremes of operator behaviour (Spearman rank rho vs ground truth)")
for m,l in [('prop','caution proportional to tolerance (kappa=3)'),
            ('indep','caution statistically INDEPENDENT of tolerance'),
            ('careless','caution >> tolerance: success-truncation only')]:
    n,a,b=run(m); print(f"   {l:48s} n={n:3d}  rho(C1)={a:5.2f}  rho(C3)={b:5.2f}")

print("\nD) power: is the per-stage interaction question cheaper than the between-family question?")
def power(nfam=5,stg_per_fam=8,ntrial=20,tau=0.60,beta=0.30,sig_stage=0.25,within_frac=0.7,reps=600,mode='within'):
    hit=0
    for _ in range(reps):
        fam=np.repeat(np.arange(nfam),stg_per_fam); n=len(fam)
        zf=rng.normal(0,1,nfam); zs=rng.normal(0,1,n)
        z=np.sqrt(1-within_frac)*zf[fam]+np.sqrt(within_frac)*zs      # covariate: within- vs between-family variance
        eta=beta*z+tau*rng.normal(0,1,nfam)[fam]+sig_stage*rng.normal(0,1,n)
        p_base=0.45; p_ours=np.clip(p_base+0.10*np.tanh(eta),0.02,0.98)
        k=rng.binomial(ntrial,p_ours); d=k/ntrial-p_base
        if mode=='within':                                            # family fixed effects
            X=np.column_stack([np.eye(nfam)[fam],z])
        else:
            X=np.column_stack([np.ones(n),z])
        b,_,_,_=np.linalg.lstsq(X,d,rcond=None); r=d-X@b
        # family-cluster bootstrap on the coefficient of z
        bs=[]
        for _ in range(150):
            pick=rng.integers(0,nfam,nfam); idx=np.concatenate([np.where(fam==f)[0] for f in pick])
            ff=np.repeat(np.arange(nfam),stg_per_fam)
            Xb=np.column_stack([np.eye(nfam)[ff],z[idx]]) if mode=='within' else np.column_stack([np.ones(len(idx)),z[idx]])
            bb,_,_,_=np.linalg.lstsq(Xb,d[idx],rcond=None); bs.append(bb[-1])
        lo,hi=np.percentile(bs,[2.5,97.5])
        if lo>0 or hi<0: hit+=1
    return hit/reps
for wf,lbl in [(0.9,'90% of covariate variance is WITHIN family'),(0.5,'50/50'),(0.1,'90% BETWEEN family (= the P3-prime situation)')]:
    print(f"   {lbl:46s} within-family FE: {power(within_frac=wf,mode='within'):.2f}   pooled: {power(within_frac=wf,mode='pooled'):.2f}")
for ns in [4,6,8,12]:
    print(f"   stages per family = {ns:2d} (n_stage={5*ns:3d})            within-family FE power = {power(stg_per_fam=ns,within_frac=0.9):.2f}")
for nt in [10,20,40]:
    print(f"   trials per stage  = {nt:2d}                        within-family FE power = {power(ntrial=nt,within_frac=0.9):.2f}")
