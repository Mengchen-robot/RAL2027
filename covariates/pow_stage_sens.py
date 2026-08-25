import numpy as np
from scipy import stats
Z = dict(hinge=0.3, transport=1.5, pick=8.7, place=12.2, zip=13.7, insert=31.1)
fam = {
 'C':[('C1','pick'),('C2','hinge'),('C3','transport'),('C4','pick'),('C5','transport'),
      ('C6','place'),('C7','transport'),('C8','hinge'),('C9','insert')],
 'B':[('B1','transport'),('B2','pick'),('B3','zip'),('B4','place'),('B5','pick'),('B6','zip')],
 'D':[('D1','pick'),('D2','hinge'),('D3','transport'),('D4','pick'),('D5','place'),('D6','transport'),('D7','hinge')],
 'E':[('E1','pick'),('E2','hinge'),('E3','transport'),('E4','pick'),('E5','place'),('E6','transport'),('E7','hinge')],
 'A':[('A1','transport'),('A2','pick'),('A3','transport'),('A4','place'),('A5','place'),('A6','pick'),('A7','transport'),('A8','place')],
}
def cz(fl):
    rows=[(f,p) for f in fl for _,p in fam[f]]
    F=np.array([r[0] for r in rows]); zr=np.array([np.log(Z[r[1]]) for r in rows])
    z=(zr-zr.mean())/zr.std(ddof=1); fs=sorted(set(F))
    X=np.column_stack([(F==f).astype(float) for f in fs]+[z])
    return len(rows), np.linalg.inv(X.T@X)[-1,-1]
def mde(c,sd_stage,pid,npair,pw=.8):
    sig2=sd_stage**2+ (100*np.sqrt(pid))**2/npair
    return (stats.norm.ppf(.975)+stats.norm.ppf(pw))*np.sqrt(sig2*c)

print("design                         n   1/c_z   MDE_bin(20)  MDE_ord(20)  MDE_ord(30)")
for name,fl in [("C+B (3-family user spec, no D/E)",['C','B']),
                ("C+B+D",['C','B','D']),
                ("C+B+D+E  [RECOMMENDED conf]",['C','B','D','E']),
                ("C+B+D+E+A (cloth in, exploratory)",['C','B','D','E','A'])]:
    n,c=cz(fl)
    print(f"{name:34s} {n:3d}  {1/c:6.1f}   {mde(c,6.0,.30,20):8.2f}   {mde(c,6.0,.075,20):8.2f}   {mde(c,6.0,.075,30):8.2f}")

# what if per-family stage count is cut to 4 (only "interesting" stages kept)?
fam4={'C':[('C2','hinge'),('C4','pick'),('C6','place'),('C9','insert')],
      'B':[('B2','pick'),('B3','zip'),('B4','place'),('B1','transport')],
      'D':[('D2','hinge'),('D4','pick'),('D5','place'),('D3','transport')],
      'E':[('E2','hinge'),('E4','pick'),('E5','place'),('E3','transport')]}
rows=[(f,p) for f in fam4 for _,p in fam4[f]]
F=np.array([r[0] for r in rows]); zr=np.array([np.log(Z[r[1]]) for r in rows])
z=(zr-zr.mean())/zr.std(ddof=1); fs=sorted(set(F))
X=np.column_stack([(F==f).astype(float) for f in fs]+[z]); c=np.linalg.inv(X.T@X)[-1,-1]
print(f"{'pruned to 4 stages/family':34s} {len(rows):3d}  {1/c:6.1f}   {mde(c,6.0,.30,20):8.2f}   {mde(c,6.0,.075,20):8.2f}   {mde(c,6.0,.075,30):8.2f}")

# v5 counterfactual: 12 ATOMIC variants, one stage each, 3 families -> z varies only BETWEEN families
print("\n=== v5 counterfactual: atomic tasks, 1 stage each ===")
atomic={'F':['pick']*5,'D':['hinge']*4,'Z':['zip']*3}
rows=[(f,p) for f in atomic for p in atomic[f]]
F=np.array([r[0] for r in rows]); zr=np.array([np.log(Z[r[1]]) for r in rows])
print("  Var(log zeta) within family =",round(float(np.var([np.log(Z[p]) for f in atomic for p in atomic[f]])),4),
      "-> with family FE, z is COLLINEAR with family dummies: slope NOT identified")
