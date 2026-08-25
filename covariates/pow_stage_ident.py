import numpy as np
from scipy import stats
Z = dict(hinge=0.3, transport=1.5, pick=8.7, place=12.2, zip=13.7, insert=31.1)

print("=== v5 counterfactual, done correctly ===")
atomic={'F':['pick']*5,'D':['hinge']*4,'Z':['zip']*3}   # 12 atomic variants, 3 families
rows=[(f,p) for f in atomic for p in atomic[f]]
F=np.array([r[0] for r in rows]); zr=np.array([np.log(Z[r[1]]) for r in rows])
z=(zr-zr.mean())/zr.std(ddof=1); fs=sorted(set(F))
X=np.column_stack([(F==f).astype(float) for f in fs]+[z])
w=0.0
for f in fs:
    x=zr[F==f]; w+=((x-x.mean())**2).sum()
print("  within-family SS of log-zeta =",round(w,6)," (exactly 0 => z in span of family dummies)")
print("  rank(X)=",np.linalg.matrix_rank(X)," cols=",X.shape[1]," -> RANK DEFICIENT:", np.linalg.matrix_rank(X)<X.shape[1])
print("  => in v5's atomic-task design the primitive slope is NOT separable from the family effect.")
print("     Only a between-family comparison with n_eff = 3 is available.")

print("\n=== harm-rate power (stage-level) ===")
# HR_k = P(base completes k AND ours fails k) ; test H0: HR_k <= HR_k^AA (A/A floor)
# per stage, npair paired trials -> binomial. one-sided, Holm over the pre-registered
# HIGH-RISK stage subset only (H2 names 3 cells a priori)
for npair in [20,30,40]:
    for k_sub,lab in [(3,'H2 pre-named 3 stages'),(29,'all 29 stages')]:
        a=0.05/k_sub
        # detect HR=0.20 against floor 0.05
        p0,p1=0.05,0.20
        se0=np.sqrt(p0*(1-p0)/npair); se1=np.sqrt(p1*(1-p1)/npair)
        pw=stats.norm.cdf((abs(p1-p0)-stats.norm.ppf(1-a)*se0)/se1)
        print(f"  npair={npair:3d}  Holm over {k_sub:2d}  power(HR .05->.20) = {pw:.3f}")

print("\n=== stage-targeted injection arm: power for a single stage ===")
for npair in [20,30]:
    for d in [.10,.15,.20]:
        pid=.30; n=npair
        # McNemar approx
        se=np.sqrt(pid/n)
        pw=stats.norm.cdf(d/se-stats.norm.ppf(.975))
        print(f"  npair={npair}  delta={d:.2f} -> power {pw:.3f}")
