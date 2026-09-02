import numpy as np
rng=np.random.default_rng(9)
def eff_rank(S):
    p=(S**2)/max((S**2).sum(),1e-300); return float(np.exp(-(p*np.log(np.maximum(p,1e-300))).sum()))
def measure(J,Ty,Se):
    """J: (dy,6) outcome sensitivity;  Ty: (dy,) outcome tolerances;  Se: (6,6) retarget-residual covariance."""
    Jt=np.diag(1/Ty)@J@np.linalg.cholesky(Se)
    S=np.linalg.svd(Jt,compute_uv=False); S=np.concatenate([S,np.zeros(max(0,6-len(S)))])
    return dict(zeta=float(np.linalg.norm(Jt,'fro')), m=eff_rank(S+1e-15), A=6-eff_rank(S+1e-15))
# retarget residual, layer 4 after best fixed calibration: 7.10 cm / 17.8 deg (median), split isotropically
e=np.array([.0710/np.sqrt(3)]*3+[np.deg2rad(17.8)/np.sqrt(3)]*3); Se=np.diag(e**2)
arch={}
t=np.zeros((1,6)); t[0,1]=1.0;                        arch["hinge door (theta)"]=(t,np.array([np.deg2rad(8)]))
z=np.zeros((1,6)); z[0,0]=1.0;                        arch["zip (arclength s)"]=(z,np.array([0.003]))
P=np.zeros((5,6)); P[0,0]=P[1,1]=P[2,2]=1.;P[3,3]=P[4,4]=1.
arch["insert (roll free)"]=(P,np.array([.002,.002,.004,np.deg2rad(3),np.deg2rad(3)]))
G=np.zeros((5,6)); G[0,0]=G[1,1]=G[2,2]=1.;G[3,3]=G[4,4]=1.
arch["pick (axis-aligned)"]=(G,np.array([.008,.008,.010,np.deg2rad(6),np.deg2rad(6)]))
Tr=np.zeros((3,6)); Tr[0,0]=Tr[1,1]=Tr[2,2]=1.;       arch["transport"]=(Tr,np.array([.05,.05,.04]))
Pl=np.eye(6);                                         arch["place (6-DoF)"]=(Pl,np.array([.006,.006,.006,np.deg2rad(5),np.deg2rad(5),np.deg2rad(12)]))
print(f"{'archetype':22s} {'zeta (tol units)':>17s} {'eff task dim m':>15s} {'absorbed 6-m':>13s}")
for k,(J,Ty) in arch.items():
    r=measure(J,Ty,Se); print(f"{k:22s} {r['zeta']:17.1f} {r['m']:15.2f} {r['A']:13.2f}")
print("\ninvariance check: rescale the EE coordinate chart by a random diagonal S (m -> arbitrary units)")
S=np.diag(np.exp(rng.normal(0,1.5,6)))
for k,(J,Ty) in arch.items():
    a=measure(J,Ty,Se); b=measure(J@np.linalg.inv(S), Ty, S@Se@S.T)
    print(f"  {k:22s} zeta {a['zeta']:9.3f} -> {b['zeta']:9.3f}   m {a['m']:.3f} -> {b['m']:.3f}")
print("\nsame table but with the LAYER-3 residual (IK-clipped frames only, 19.2% of frames, assume 1 cm / 5 deg):")
e3=np.array([.01/np.sqrt(3)]*3+[np.deg2rad(5)/np.sqrt(3)]*3); Se3=np.diag(e3**2)*0.192
for k,(J,Ty) in arch.items():
    r=measure(J,Ty,Se3); print(f"  {k:22s} zeta={r['zeta']:8.2f}  absorbed={r['A']:.2f}")
