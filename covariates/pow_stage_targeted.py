import numpy as np
from scipy import stats
Z = dict(hinge=0.3, transport=1.5, pick=8.7, place=12.2, zip=13.7, insert=31.1)

print("=== stage-targeted arm used as a POOLED slope test (8 stages) ===")
# choose 8 targeted stages spanning zeta: 2 hinge, 2 transport, 2 pick/place, 1 zip, 1 insert
sel=['hinge','hinge','transport','transport','pick','place','zip','insert']
zr=np.array([np.log(Z[p]) for p in sel]); z=(zr-zr.mean())/zr.std(ddof=1)
X=np.column_stack([np.ones(8),z]); c=np.linalg.inv(X.T@X)[1,1]
for npair in [20,30]:
    for pid in [.30,.50]:
        sig=np.sqrt(4.0**2+(100*np.sqrt(pid))**2/npair)
        m=(stats.norm.ppf(.975)+stats.norm.ppf(.8))*np.sqrt(sig**2*c)
        print(f"  npair={npair} pi_d={pid}: MDE(slope)={m:.2f} pp/SD ; end-to-end over {z.max()-z.min():.2f} SD = {m*(z.max()-z.min()):.1f} pp")

print("\n=== harm rate vs a REALISTIC A/A floor ===")
print("v5 6.8(b) warns pure noise can give n10 = 20-25%% on deformables.")
print("If HR_floor is estimated from A/A with n_AA pairs, the test is a 2-sample binomial:")
for floor in [0.05,0.10,0.125]:
    for npair,n_aa in [(20,20),(30,20),(30,40)]:
        p1=floor+0.15
        se=np.sqrt(p1*(1-p1)/npair+floor*(1-floor)/n_aa)
        pw=stats.norm.cdf((p1-floor)/se-stats.norm.ppf(1-0.05/3))
        print(f"  floor={floor:.3f} npair={npair} n_AA={n_aa}: power(HR=floor+.15, Holm@3) = {pw:.3f}")
print("\n  -> deformable family A cannot support a per-stage HR claim; rigid families can.")

print("\n=== cost of npair 20 -> 30 on main endpoint ===")
mins=dict(C=1.9,B=4.25,D=1.75,E=2.5,A=5.9); conf=['C','B','D','E']
for npair in [20,30]:
    h=sum(2*npair*2*mins[f] for f in conf+['A'])/60*1.4
    hr=sum(2*npair*2*mins[f] for f in conf)/60*1.4
    print(f"  npair={npair}: main endpoint {h:.1f} h (rigid-only {hr:.1f} h)")
print("  delta for rigid-only 20->30 =", round(sum(2*10*2*mins[f] for f in conf)/60*1.4,1),"h")
