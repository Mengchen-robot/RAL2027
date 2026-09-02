import numpy as np, xml.etree.ElementTree as ET, sys, os
os.chdir('/tmp/agxurdf')
np.set_printoptions(precision=4, suppress=True)
rng = np.random.default_rng(7)
exec(open('ikstudy.py').read().split("M={m:load")[0])  # reuse helpers

M={m:load(m) for m in ['piper','piper_x']}
def lims(J): return np.array([j['lo'] for j in J]), np.array([j['hi'] for j in J])

# dual base offsets from official dual_piper.xacro
BL=np.eye(4); BL[:3,3]=[0.0075,-0.285,0.01]
BR=np.eye(4); BR[:3,3]=[0.0075, 0.285,0.0]
# PiperX gripper flange rotated 90deg about z relative to Piper
Rz90=np.eye(4); Rz90[:3,:3]=rpy(0,0,np.pi/2)

def ik_ms(J,Tt,n=6,rng=rng):
    lo,hi=lims(J)
    for k in range(n):
        q0 = np.zeros(6) if k==0 else rng.uniform(lo,hi)
        ok,q,ep,er = ik(J,Tt,q0)
        if ok: return True,q
    return False,q

# ---------- A. dual-arm coupled retarget ----------
Jp, Jx = M['piper'], M['piper_x']
lo,hi = lims(Jp)
samples=[]
while len(samples)<80:
    qL=rng.uniform(lo,hi); qR=rng.uniform(lo,hi)
    TL=BL@fk_full(Jp,qL)[0]; TR=BR@fk_full(Jp,qR)[0]
    d=np.linalg.norm(TL[:3,3]-TR[:3,3])
    pmid=0.5*(TL[:3,3]+TR[:3,3])
    if not(0.05<d<0.60): continue                    # coordinated bimanual
    if not(0.15<pmid[0]<0.60 and abs(pmid[1])<0.35 and 0.0<pmid[2]<0.65): continue
    samples.append((TL,TR))
print("bimanual samples:",len(samples))

n_naive=0; n_rel=0; rel_err_p=[]; rel_err_r=[]
for TL,TR in samples:
    Trel = np.linalg.inv(TL)@TR
    okL,qL2 = ik_ms(Jx,TL); okR,qR2 = ik_ms(Jx,TR)
    if okL and okR:
        n_naive+=1
    # relative-preserving: rigid g applied to the pair, T_rel exactly preserved
    found=False
    for t in range(20):
        if t==0: g=np.eye(4)
        else:
            g=np.eye(4); g[:3,3]=rng.normal(0,0.10,3); g[:3,:3]=rpy(*rng.normal(0,0.25,3))
        a,_=ik_ms(Jx,g@TL,n=3); 
        if not a: continue
        b,_=ik_ms(Jx,g@TR,n=3)
        if b: found=True; break
    if found: n_rel+=1
print(f"A. dual-arm Piper->PiperX")
print(f"   naive per-arm independent IK (both arms exact):  {100*n_naive/len(samples):.1f}%")
print(f"   T_rel-preserving with free T_abs (rigid g search): {100*n_rel/len(samples):.1f}%")

# ---------- B. locked-joint configuration ladder ----------
# reader = PiperX with joint k locked at 0 -> 5 DoF
def ik_pos_axis(J,Tt,locked,q0,iters=300,lam=0.05):
    lo,hi=lims(J); q=q0.copy(); q[locked]=0.0
    for _ in range(iters):
        Jm,T=jac(J,q)
        ep=Tt[:3,3]-T[:3,3]
        # approach-axis alignment only (2 dof of orientation)
        za=T[:3,2]; zt=Tt[:3,2]
        er=np.cross(za,zt)
        e=np.concatenate([ep,er])
        if np.linalg.norm(ep)<1e-4 and np.linalg.norm(er)<2e-3:
            return True,q
        Jred=np.delete(Jm,locked,axis=1)
        dq=Jred.T@np.linalg.solve(Jred@Jred.T+lam**2*np.eye(6),e)
        full=np.zeros(6); idx=[i for i in range(6) if i!=locked]
        full[idx]=np.clip(dq,-0.3,0.3)
        q=np.clip(q+full,lo,hi); q[locked]=0.0
    return False,q
def ik_locked_full(J,Tt,locked,q0,iters=300,lam=0.05):
    lo,hi=lims(J); q=q0.copy(); q[locked]=0.0
    for _ in range(iters):
        Jm,T=jac(J,q)
        ep=Tt[:3,3]-T[:3,3]; er=logSO3(Tt[:3,:3]@T[:3,:3].T)
        e=np.concatenate([ep,er])
        if np.linalg.norm(ep)<1e-4 and np.linalg.norm(er)<1e-3: return True,q
        Jred=np.delete(Jm,locked,axis=1)
        dq=Jred.T@np.linalg.solve(Jred@Jred.T+lam**2*np.eye(6),e)
        full=np.zeros(6); idx=[i for i in range(6) if i!=locked]
        full[idx]=np.clip(dq,-0.3,0.3)
        q=np.clip(q+full,lo,hi); q[locked]=0.0
    return False,q

lo,hi=lims(Jp)
NS=120
Ts=[fk_full(Jp,rng.uniform(lo,hi))[0] for _ in range(NS)]
lox,hix=lims(Jx)
print("\nB. locked-joint ladder (reader = PiperX, writer = Piper), N=%d"%NS)
print("   locked | full 6-DoF pose IK | pos+approach-axis (5-DoF task)")
for locked in [3,4,5]:
    nf=0; na=0
    for Tt in Ts:
        for k in range(4):
            q0=np.zeros(6) if k==0 else rng.uniform(lox,hix)
            ok,_=ik_locked_full(Jx,Tt,locked,q0)
            if ok: nf+=1; break
        for k in range(4):
            q0=np.zeros(6) if k==0 else rng.uniform(lox,hix)
            ok,_=ik_pos_axis(Jx,Tt,locked,q0)
            if ok: na+=1; break
    print(f"     j{locked+1}  |      {100*nf/NS:5.1f}%        |   {100*na/NS:5.1f}%")
# unlocked reference
nf=0; na=0
for Tt in Ts:
    ok,_=ik_ms(Jx,Tt,n=6)
    if ok: nf+=1
print(f"    none  |      {100*nf/NS:5.1f}%        |     (6-DoF ref)")
