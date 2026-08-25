import numpy as np
from scipy import stats
Z = dict(hinge=0.3, transport=1.5, pick=8.7, place=12.2, zip=13.7, insert=31.1)
fam = {
 'C':[('C1','pick'),('C2','hinge'),('C3','transport'),('C4','pick'),('C5','transport'),
      ('C6','place'),('C7','transport'),('C8','hinge'),('C9','insert')],
 'B':[('B1','transport'),('B2','pick'),('B3','zip'),('B4','place'),('B5','pick'),('B6','zip')],
 'D':[('D1','pick'),('D2','hinge'),('D3','transport'),('D4','pick'),('D5','place'),('D6','transport'),('D7','hinge')],
 'E':[('E1','pick'),('E2','hinge'),('E3','transport'),('E4','pick'),('E5','place'),('E6','transport'),('E7','hinge')]}
rows=[(f,s,p) for f in fam for s,p in fam[f]]
n=len(rows); F=np.array([r[0] for r in rows]); S=np.arange(n)
zr=np.array([np.log(Z[r[2]]) for r in rows])
# direction-specific zeta: reverse direction (X->Piper) has larger Sigma_e (phi 57.3% vs 80.0%)
# scale factor on the residual covariance -> zeta scales; use +0.35 nats as the pre-registered offset
OFF=0.35
zz=np.concatenate([zr, zr+OFF]); FF=np.concatenate([F,F]); SS=np.concatenate([S,S])
DD=np.concatenate([np.zeros(n),np.ones(n)])
z=(zz-zz.mean())/zz.std(ddof=1)
fs=sorted(set(FF))
X=np.column_stack([(FF==f).astype(float) for f in fs]+[DD,z])
print("rows = stage x direction =",len(zz),"; cols =",X.shape[1])
# GLS with stage random intercept: V = tau2 * Z_s Z_s' + sigma2 I ; ICC = tau2/(tau2+sigma2)
def se_slope(icc, sig_tot2):
    tau2=icc*sig_tot2; s2=(1-icc)*sig_tot2
    V=np.eye(len(zz))*s2
    for k in range(n):
        idx=np.where(SS==k)[0]; V[np.ix_(idx,idx)]+=tau2
    Vi=np.linalg.inv(V); A=np.linalg.inv(X.T@Vi@X)
    return np.sqrt(A[-1,-1]), np.sqrt(A[-2,-2])   # (zeta slope, direction main effect)
print("\nICC(stage)  MDE(zeta slope)   MDE(direction main effect)   [ordinal, npair=20, pi_d=.30, sd_stage=4pp]")
sig_tot2 = 4.0**2 + (100*np.sqrt(0.30/4))**2/20
k=(stats.norm.ppf(.975)+stats.norm.ppf(.8))
for icc in [0.0,0.3,0.6,0.9]:
    a,b=se_slope(icc,sig_tot2)
    print(f"   {icc:.1f}      {k*a:8.2f} pp/SD    {k*b:8.2f} pp")
print("\n  reference: collapsing to n=29 (average over directions) gave MDE 4.84 pp/SD")
print("  -> stage x direction rows help only if ICC(stage) is low; pre-register the ICC-robust GLS,")
print("     report the n=29 direction-averaged fit as the pre-registered robustness check.")
