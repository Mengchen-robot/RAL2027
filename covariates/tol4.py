import numpy as np
rng=np.random.default_rng(3)
def irls(X,y,ridge=1e-3,eps=0.02,iters=400):
    y=np.clip(y,eps,1-eps); w=np.zeros(X.shape[1])
    for _ in range(iters):
        p=1/(1+np.exp(-np.clip(X@w,-30,30)))
        g=X.T@(y-p)-ridge*w; H=(X*(p*(1-p)+1e-8)[:,None]).T@X+ridge*np.eye(X.shape[1])
        s=np.linalg.solve(H,g); w=w+np.clip(s,-3,3)
        if np.max(np.abs(s))<1e-10: break
    return w
def e2(R,y,scale):
    Z=R/scale; X=np.column_stack([np.ones(len(Z)),Z**2]); w=irls(X,y); a=-w[1:]
    ok=a>1e-8; out=np.full(6,np.nan); out[ok]=np.sqrt(max(w[0],0)/a[ok])*scale[ok]; return out
def fmt(v): return np.array2string(np.array([v[0]*1e3,v[1]*1e3,v[2]*1e3,*np.rad2deg(v[3:])]),precision=1)
h=np.array([0.004,0.004,0.010,0.05,0.05,0.60])
floor=np.array([0.0015]*3+[np.deg2rad(1.0)]*3)
Dm=rng.normal(0,1,(4000,6))*np.maximum(h/3.,floor); Dm=Dm[np.linalg.norm(Dm/h,axis=1)<=1.]
s1=Dm[:40].std(0)
print("A) label smoothing fixes the perfect-separation blow-up (noiseless labels):")
for nr in [400,2000,5000]:
    R=rng.normal(0,1,(nr,6))*(h*0.42); y=(np.linalg.norm(R/h,axis=1)<=1.).astype(float)
    print(f"   n={nr:5d}",fmt(e2(R,y,s1)),"   truth",fmt(h))

print("\nB) does demo dispersion recover the SHAPE of the tolerance tensor across many stages?")
def logratio(v,rho=0.05): return np.mean(np.log(rho*v[3:]))-np.mean(np.log(v[:3]))
def loganiso(v,rho=0.05):
    hs=np.array([v[0],v[1],v[2],rho*v[3],rho*v[4],rho*v[5]]); return np.log(hs.max()/hs.min())
def logscale(v,rho=0.05):
    hs=np.array([v[0],v[1],v[2],rho*v[3],rho*v[4],rho*v[5]]); return np.mean(np.log(hs))
def run(kappa_sd, n_demo=40, nstage=60, floor_on=True):
    T=[];E=[]
    for _ in range(nstage):
        hh=np.concatenate([np.exp(rng.normal(np.log(0.008),1.0,3)),np.exp(rng.normal(np.log(0.15),1.0,3))])
        k=np.exp(np.log(3.0)+rng.normal(0,kappa_sd,6))            # per-axis operator caution, heterogeneous
        sd=hh/k
        if floor_on: sd=np.maximum(sd,floor)
        Dd=rng.normal(0,1,(4000,6))*sd; Dd=Dd[np.linalg.norm(Dd/hh,axis=1)<=1.][:n_demo]
        if len(Dd)<8: continue
        T.append(hh); E.append(Dd.std(0))
    T=np.array(T);E=np.array(E)
    def sp(a,b):
        ra=np.argsort(np.argsort(a)); rb=np.argsort(np.argsort(b)); return np.corrcoef(ra,rb)[0,1]
    return (len(T),
            sp([logratio(t) for t in T],[logratio(e) for e in E]),
            sp([loganiso(t) for t in T],[loganiso(e) for e in E]),
            sp([logscale(t) for t in T],[logscale(e) for e in E]))
print(f"   {'operator-caution heterogeneity':38s} {'n':>4s} {'rho(C1 rot/trans)':>18s} {'rho(C3 aniso)':>14s} {'rho(C2 scale)':>14s}")
for ks,lbl in [(0.0,'homogeneous kappa=3'),(0.3,'kappa sd=0.3 nats (+-35%)'),(0.6,'kappa sd=0.6 nats (+-82%)'),(1.0,'kappa sd=1.0 nats')]:
    n,a,b,c=run(ks); print(f"   {lbl:38s} {n:4d} {a:18.2f} {b:14.2f} {c:14.2f}")
print("   (with the teleop noise floor switched OFF, kappa sd=0.6):")
n,a,b,c=run(0.6,floor_on=False); print(f"   {'':38s} {n:4d} {a:18.2f} {b:14.2f} {c:14.2f}")
for nd in [10,20,40,100]:
    n,a,b,c=run(0.3,n_demo=nd); print(f"   n_demo={nd:4d}, kappa sd=0.3           {n:4d} {a:18.2f} {b:14.2f} {c:14.2f}")
