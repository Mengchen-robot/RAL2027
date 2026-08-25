import numpy as np
from scipy import stats
rng = np.random.default_rng(7)

# stage table (confirmatory rigid families) -- same as design_stage.py
Z = dict(hinge=0.3, transport=1.5, pick=8.7, place=12.2, zip=13.7, insert=31.1)
fam = {
 'C':[('C1','pick'),('C2','hinge'),('C3','transport'),('C4','pick'),('C5','transport'),
      ('C6','place'),('C7','transport'),('C8','hinge'),('C9','insert')],
 'B':[('B1','transport'),('B2','pick'),('B3','zip'),('B4','place'),('B5','pick'),('B6','zip')],
 'D':[('D1','pick'),('D2','hinge'),('D3','transport'),('D4','pick'),('D5','place'),('D6','transport'),('D7','hinge')],
 'E':[('E1','pick'),('E2','hinge'),('E3','transport'),('E4','pick'),('E5','place'),('E6','transport'),('E7','hinge')],
}
rows=[(f,s,p) for f in fam for s,p in fam[f]]
F=np.array([r[0] for r in rows]); P=np.array([r[2] for r in rows])
z_raw=np.array([np.log(Z[p]) for p in rows and P])
z=(z_raw-z_raw.mean())/z_raw.std(ddof=1)          # standardized log-zeta
n=len(rows); fams=sorted(set(F))
print("n stages =",n," families =",len(fams))

# ---- design matrix with family FIXED effects + z ----
X=np.column_stack([ (F==f).astype(float) for f in fams ] + [z])
XtXi=np.linalg.inv(X.T@X)
c_z = XtXi[-1,-1]          # SE(beta_z) = sigma * sqrt(c_z)
print("c_z (SE multiplier^2) =",round(c_z,5), "-> effective n for slope =", round(1/c_z,2))

def mde(sd_stage, sd_trial, npair, pw=0.80, alpha=0.05):
    """sd_stage: residual sd of stage-level Delta (pp) not explained by z/family
       sd_trial: per-stage paired-trial noise sd of Delta (pp) for ONE trial-pair"""
    sig2 = sd_stage**2 + sd_trial**2/npair
    se = np.sqrt(sig2*c_z)
    return (stats.norm.ppf(1-alpha/2)+stats.norm.ppf(pw))*se

# per-trial paired Delta noise: Delta_k = mean(y_ours)-mean(y_base); for binary paired with
# discordance pi_d, sd of single paired difference = sqrt(pi_d) -> *100 pp
for pid,label in [(0.30,'binary pi_d=.30'),(0.50,'binary pi_d=.50'),(0.075,'ordinal 0-4 progress (var/4)')]:
    sdt=100*np.sqrt(pid)
    for npair in [20,30]:
        for sds in [3.0,6.0]:
            print(f"  {label:32s} npair={npair:3d} sd_stage={sds:.1f}pp -> MDE(beta_z)={mde(sds,sdt,npair):.2f} pp per SD of log-zeta")

# ---- continuous regression vs 6-group Holm ----
print("\n=== continuous vs grouped ===")
prim=sorted(set(P)); print("primitives:",prim,"counts:",[int((P==p).sum()) for p in prim])
# grouped: 6 group means, Holm over 5 pairwise-vs-grand or 6 one-sample tests
# one-sample per group: SE = sigma/sqrt(n_g); alpha_Holm worst = .05/6
for p in prim:
    ng=int((P==p).sum())
    sdt=100*np.sqrt(0.30); sig=np.sqrt(6.0**2+sdt**2/20)
    se_g=sig/np.sqrt(ng)
    m_holm=(stats.norm.ppf(1-0.05/6/2)+stats.norm.ppf(0.80))*se_g
    print(f"  {p:10s} n_g={ng:2d}  MDE(group mean, Holm@6)= {m_holm:6.2f} pp")
sig=np.sqrt(6.0**2+(100*np.sqrt(0.30))**2/20)
print(f"  continuous slope        MDE = {(stats.norm.ppf(1-0.025)+stats.norm.ppf(0.80))*np.sqrt(sig**2*c_z):6.2f} pp per SD")
# translate: predicted spread over the 6 prototypes in SD units of z
print(f"  spread of log-zeta across prototypes = {z.max()-z.min():.2f} SD  ->",
      f"a slope of s pp/SD implies {(z.max()-z.min()):.2f}*s pp end-to-end")

# ---- simulation check of the primary interaction test ----
def sim(beta_z, npair=20, sd_stage=6.0, pid=0.30, reps=4000):
    sdt=100*np.sqrt(pid); hits=0
    for _ in range(reps):
        y = beta_z*z + rng.normal(0,sd_stage,n) + rng.normal(0,sdt/np.sqrt(npair),n)
        # family FE + z OLS
        b,_,_,_ = np.linalg.lstsq(X,y,rcond=None)
        res=y-X@b; s2=res@res/(n-X.shape[1]); se=np.sqrt(s2*c_z)
        t=b[-1]/se
        if abs(t) > stats.t.ppf(0.975, n-X.shape[1]): hits+=1
    return hits/reps
for b in [3.0,4.0,5.0,6.0]:
    print(f"  power at beta_z={b:.1f} pp/SD : {sim(b):.3f}")

# ---- family-level clustering: is family FE enough? ----
print("\n=== n_eff sanity (v5 rho=0.6 concern) ===")
print("with family FIXED effects the slope is identified from WITHIN-family z-variation only;")
print("within-family share of Var(log zeta) = 0.879 (design_stage.py) -> design effect")
print("  naive n=%d  ->  n_eff_slope = 1/c_z = %.1f"%(n,1/c_z))
