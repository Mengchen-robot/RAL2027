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
z=(zr-zr.mean())/zr.std(ddof=1); fs=sorted(set(F)); n=len(rows)

# CO-PRIMARY 2: slope difference between level 3 and level 4
# stacked design: 2 levels x 29 stages, outcome Delta_k(level)
# X = [family FE (x2 levels shared)], level dummy, z, level:z   -> estimand = level:z coefficient
Xf=np.column_stack([(F==f).astype(float) for f in fs])
big=np.vstack([np.column_stack([Xf, np.zeros(n), z, np.zeros(n)]),
               np.column_stack([Xf, np.ones(n),  z, z          ])])
c=np.linalg.inv(big.T@big)[-1,-1]
print("co-primary 2 (level x zeta): 2x29=58 rows, 1/c =", round(1/c,1))
for npair,pid,sds in [(15,.30,4.0),(15,.50,4.0),(20,.30,4.0),(20,.30,2.0)]:
    sig=np.sqrt(sds**2+(100*np.sqrt(pid))**2/npair)          # binary
    sigo=np.sqrt(sds**2+(100*np.sqrt(pid/4))**2/npair)       # ordinal progress
    m=(stats.norm.ppf(.975)+stats.norm.ppf(.8))*np.sqrt(sig**2*c)
    mo=(stats.norm.ppf(.975)+stats.norm.ppf(.8))*np.sqrt(sigo**2*c)
    print(f"  npair={npair} pi_d={pid} sd_stage={sds}: MDE(slope diff) binary={m:.2f}  ordinal={mo:.2f} pp/SD")
print(f"  predicted effect size: zeta spans {z.max()-z.min():.2f} SD; if level-4 collapses only at high zeta,")
print(f"  a slope difference of 5 pp/SD = {5*(z.max()-z.min()):.0f} pp swing between hinge and insert stages.")
