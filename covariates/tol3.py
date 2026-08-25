import numpy as np
rng=np.random.default_rng(11)
h=np.array([0.004,0.004,0.010, 0.05,0.05,0.60])
def irls(X,y,ridge=1e-3,iters=300):
    w=np.zeros(X.shape[1])
    for _ in range(iters):
        p=1/(1+np.exp(-np.clip(X@w,-30,30)))
        g=X.T@(y-p)-ridge*w; H=(X*(p*(1-p)+1e-8)[:,None]).T@X+ridge*np.eye(X.shape[1])
        s=np.linalg.solve(H,g); w=w+np.clip(s,-5,5)
        if np.max(np.abs(s))<1e-10: break
    return w
def e2(R,y,scale):
    """scale: per-axis standardiser (use the E1 demo sd). Returns 50%-level half-widths."""
    Z=R/scale; X=np.column_stack([np.ones(len(Z)), Z**2]); w=irls(X,y)
    a=-w[1:]                                  # p=0.5 at  w0 - a z^2 = 0
    ok=a>1e-6
    out=np.full(6,np.nan); out[ok]=np.sqrt(max(w[0],0)/a[ok])*scale[ok]
    return out
def fmt(v): return np.array2string(np.array([v[0]*1e3,v[1]*1e3,v[2]*1e3,*np.rad2deg(v[3:])]),precision=1)
floor=np.array([0.0015]*3+[np.deg2rad(1.0)]*3); sd_op=np.maximum(h/3.0,floor)
Dm=rng.normal(0,1,(4000,6))*sd_op; Dm=Dm[np.linalg.norm(Dm/h,axis=1)<=1.0]
s1=Dm[:40].std(axis=0)
print("truth h                :",fmt(h))
print("E1 demo sd (n=40)      :",fmt(s1),"   h/E1 =",np.array2string(h/s1,precision=2))
print("E1*sqrt(6) heuristic   :",fmt(s1*np.sqrt(6)),"  <- chi-6 correction for an ellipsoidal domain")
for nr in [200,400,800,2000,5000]:
    R=rng.normal(0,1,(nr,6))*(h*0.42); y=(np.linalg.norm(R/h,axis=1)<=1.0).astype(int)
    est=e2(R,y,s1); print(f"E2 rollouts n={nr:5d}     :",fmt(est),f" SR={y.mean():.2f} med|rel err|={np.nanmedian(np.abs(est-h)/h):.2f}")
R=rng.normal(0,1,(2000,6))*(h*0.42); y0=(np.linalg.norm(R/h,axis=1)<=1.0).astype(int)
for nz in [0.05,0.15,0.30]:
    y=y0.copy(); f=rng.random(len(y))<nz; y[f]=1-y[f]
    print(f"E2 n=2000, label noise {nz:.0%}:",fmt(e2(R,y,s1)))
# anisotropy / ratio recovery is what we actually need, not absolute widths
for nr in [400,2000]:
    R=rng.normal(0,1,(nr,6))*(h*0.42); y=(np.linalg.norm(R/h,axis=1)<=1.0).astype(int); est=e2(R,y,s1)
    print(f"n={nr}: recovered rot/trans log-ratio err = {abs(np.mean(np.log(est[3:]*0.05))-np.mean(np.log(est[:3])) - (np.mean(np.log(h[3:]*0.05))-np.mean(np.log(h[:3])))):.3f} nats; "
          f"E1-based same quantity err = {abs(np.mean(np.log(s1[3:]*0.05))-np.mean(np.log(s1[:3])) - (np.mean(np.log(h[3:]*0.05))-np.mean(np.log(h[:3])))):.3f} nats")
