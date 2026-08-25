import numpy as np
rng=np.random.default_rng(4)
def eff_rank(S,mode='pr'):
    s2=S**2; p=s2/s2.sum()
    if mode=='pr': return float(np.exp(-(p*np.log(np.maximum(p,1e-300))).sum()))   # participation ratio (entropy)
    return float((s2.sum()**2)/(s2**2).sum())
def fit_J(delta,y,ridge=1e-8):
    X=np.column_stack([np.ones(len(delta)),delta])
    B,_,_,_=np.linalg.lstsq(X.T@X+ridge*np.eye(X.shape[1]),X.T@y,rcond=None) if False else np.linalg.lstsq(X,y,rcond=None)
    return B[1:].T                      # (dim_y, 6)
def scaled(d,rho): return d*np.array([1,1,1,rho,rho,rho])

def scenario(name,Jtrue,dim_y,n=200,sd=np.array([.005,.005,.005,.05,.05,.05]),noise=0.0,rho=0.05):
    d=rng.normal(0,1,(n,6))*sd
    y=d@Jtrue.T+rng.normal(0,1,(n,dim_y))*noise
    ds=scaled(d,rho)
    # normalise y by its own tolerance so singular values are dimensionless
    Jh=fit_J(ds,y/ y.std(0))
    S=np.linalg.svd(Jh,compute_uv=False)
    S=np.concatenate([S,np.zeros(6-len(S))])
    er=eff_rank(S+1e-12)
    print(f"  {name:34s} sv={np.array2string(S/S.max(),precision=3,suppress_small=True):46s} eff-rank={er:5.2f}  absorbed={6-er:5.2f}")

print("Constraint absorption = 6 - effective rank of the outcome-sensitivity map J (rho=0.05 m)")
# hinge: only motion along the arc tangent changes theta
t=np.zeros((1,6)); t[0,1]=1.0
scenario("1-DoF hinge (theta only)",t,1)
scenario("1-DoF hinge + 10% sensor noise",t,1,noise=0.10)
# zipper: arclength s plus a weak normal coupling
z=np.zeros((2,6)); z[0,0]=1.0; z[1,2]=0.25
scenario("zip: arclength + weak normal",z,2)
# peg insertion: 3 pos + 2 orient matter, roll free
P=np.zeros((5,6)); P[0,0]=P[1,1]=P[2,2]=1.0; P[3,3]=P[4,4]=1.0
scenario("insertion (roll free)",P,5)
# free placement: all six matter
F=np.eye(6); scenario("free 6-DoF placement",F,6)
# transport: only the final position of the carried object matters
T=np.zeros((3,6)); T[0,0]=T[1,1]=T[2,2]=1.0
scenario("transport (orientation free)",T,3)

print("\nsensitivity of eff-rank to the length scale rho (metres) used to commensurate rad and m:")
for rho in [0.01,0.03,0.05,0.10,0.30]:
    print(f"  rho={rho:4.2f} m", end="")
    for nm,J,dy in [("hinge",t,1),("insert",P,5),("transport",T,3),("free",F,6)]:
        d=rng.normal(0,1,(400,6))*np.array([.005,.005,.005,.05,.05,.05])
        y=d@J.T; Jh=fit_J(scaled(d,rho), y/y.std(0)); S=np.linalg.svd(Jh,compute_uv=False)
        S=np.concatenate([S,np.zeros(6-len(S))]); print(f"   {nm}={6-eff_rank(S+1e-12):4.2f}",end="")
    print()
