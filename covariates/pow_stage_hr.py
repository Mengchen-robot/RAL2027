import numpy as np
from scipy import stats
Z = dict(hinge=0.3, transport=1.5, pick=8.7, place=12.2, zip=13.7, insert=31.1)
fam = {
 'C':[('C1','pick'),('C2','hinge'),('C3','transport'),('C4','pick'),('C5','transport'),
      ('C6','place'),('C7','transport'),('C8','hinge'),('C9','insert')],
 'B':[('B1','transport'),('B2','pick'),('B3','zip'),('B4','place'),('B5','pick'),('B6','zip')],
 'D':[('D1','pick'),('D2','hinge'),('D3','transport'),('D4','pick'),('D5','place'),('D6','transport'),('D7','hinge')],
 'E':[('E1','pick'),('E2','hinge'),('E3','transport'),('E4','pick'),('E5','place'),('E6','transport'),('E7','hinge')]}
rows=[(f,p) for f in fam for _,p in fam[f]]
F=np.array([r[0] for r in rows]); zr=np.array([np.log(Z[r[1]]) for r in rows])
z=(zr-zr.mean())/zr.std(ddof=1); fs=sorted(set(F))
X=np.column_stack([(F==f).astype(float) for f in fs]+[z]); c=np.linalg.inv(X.T@X)[-1,-1]
n=len(rows)
print("HR-slope test: HR_k ~ family FE + zeta,  n =",n," 1/c_z =",round(1/c,1))
print("  (HR_k a proportion over npair*2dir paired trials; binom sd = sqrt(HR(1-HR)/N))")
for HRbar in [0.08,0.15]:
    for npair in [20,30]:
        N=npair*2   # both directions pooled per stage
        sd_bin=100*np.sqrt(HRbar*(1-HRbar)/N)
        for sds in [2.0,4.0]:
            sig=np.sqrt(sds**2+sd_bin**2)
            m=(stats.norm.ppf(.975)+stats.norm.ppf(.8))*np.sqrt(sig**2*c)
            print(f"  HRbar={HRbar:.2f} npair={npair} sd_stage={sds:.1f}pp: binom sd={sd_bin:.1f}pp  MDE(slope)={m:.2f} pp/SD"
                  f"  end-to-end over {z.max()-z.min():.2f}SD = {m*(z.max()-z.min()):.1f} pp")
print("\n compare: per-stage Holm@3 point test power was 0.18-0.39  ->  slope test is the only viable HR claim")
