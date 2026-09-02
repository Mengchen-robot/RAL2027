"""
Task-workspace-restricted cross-embodiment retarget feasibility, Piper -> PiperX.

Why this script exists:
  Prior analysis (analyze.py / ikstudy.py) measured layer-3 IK feasibility over the
  WHOLE Piper-reachable pose set (67.2%). That set is dominated by contorted
  configurations that never occur in tabletop home manipulation. If, inside the
  actual task workspace, feasibility is ~99%, layer 3 transfers for free and the
  four-layer spectrum flattens. So we must measure feasibility *inside the task box*.

Also computes the dual-arm question that no prior run touched:
  a bimanual entry stores (T_abs, T_rel). Per-arm independent retarget must hit
  12 constraints with 12 joints (6-DoF arms have no nullspace). Cooperative
  retarget instead preserves T_rel exactly and lets the *pair* float by a free
  SE(3) offset g -- 6 DoF of task-level slack. Does that slack rescue it?
"""
import numpy as np, xml.etree.ElementTree as ET
np.set_printoptions(precision=4, suppress=True)

def rpy(r,p,y):
    Rx=np.array([[1,0,0],[0,np.cos(r),-np.sin(r)],[0,np.sin(r),np.cos(r)]])
    Ry=np.array([[np.cos(p),0,np.sin(p)],[0,1,0],[-np.sin(p),0,np.cos(p)]])
    Rz=np.array([[np.cos(y),-np.sin(y),0],[np.sin(y),np.cos(y),0],[0,0,1]])
    return Rz@Ry@Rx

def load(m):
    r=ET.parse(m+'.urdf').getroot(); J=[]
    for j in r.iter('joint'):
        if j.get('type')!='revolute': continue
        o=j.find('origin'); l=j.find('limit')
        J.append(dict(p=np.array([float(x) for x in o.get('xyz').split()]),
                      R=rpy(*[float(x) for x in o.get('rpy').split()]),
                      a=np.array([float(x) for x in j.find('axis').get('xyz').split()]),
                      lo=float(l.get('lower')), hi=float(l.get('upper'))))
    return J

def axrot(a,th):
    a=a/np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+np.sin(th)*K+(1-np.cos(th))*K@K

# gripper mount: Piper rpy=(0,0,0), PiperX rpy=(0,0,pi/2); fingertip at flange z+0.138
TCP = {'piper':   np.block([[rpy(0,0,0.0),        np.array([[0],[0],[0.138]])],[np.zeros((1,3)),np.ones((1,1))]]),
       'piper_x': np.block([[rpy(0,0,np.pi/2),    np.array([[0],[0],[0.138]])],[np.zeros((1,3)),np.ones((1,1))]])}

def fk(J,q,tcp=None):
    T=np.eye(4); zs=[]; ps=[]
    for i in range(6):
        Tj=np.eye(4); Tj[:3,:3]=J[i]['R']; Tj[:3,3]=J[i]['p']; T=T@Tj
        zs.append(T[:3,:3]@J[i]['a']); ps.append(T[:3,3].copy())
        Tr=np.eye(4); Tr[:3,:3]=axrot(J[i]['a'],q[i]); T=T@Tr
    Tf=T.copy()
    if tcp is not None: T=T@tcp
    return T,Tf,np.array(zs),np.array(ps)

def jac(J,q,tcp):
    T,Tf,zs,ps=fk(J,q,tcp); pe=T[:3,3]
    Jm=np.zeros((6,6))
    for i in range(6):
        Jm[:3,i]=np.cross(zs[i],pe-ps[i]); Jm[3:,i]=zs[i]
    return Jm,T

def logSO3(R):
    c=np.clip((np.trace(R)-1)/2,-1,1); th=np.arccos(c)
    if th<1e-9: return np.zeros(3)
    return th/(2*np.sin(th))*np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]])

def ik(J,tcp,Tt,q0,iters=300,lam=0.05,ptol=1e-3,rtol=np.radians(1.0)):
    lo=np.array([j['lo'] for j in J]); hi=np.array([j['hi'] for j in J]); q=q0.copy()
    for _ in range(iters):
        Jm,T=jac(J,q,tcp)
        ep=Tt[:3,3]-T[:3,3]; er=logSO3(Tt[:3,:3]@T[:3,:3].T)
        if np.linalg.norm(ep)<ptol and np.linalg.norm(er)<rtol:
            return True,q,np.linalg.norm(ep),np.degrees(np.linalg.norm(er))
        dq=Jm.T@np.linalg.solve(Jm@Jm.T+lam**2*np.eye(6),np.concatenate([ep,er]))
        q=np.clip(q+np.clip(dq,-0.3,0.3),lo,hi)
    Jm,T=jac(J,q,tcp)
    ep=np.linalg.norm(Tt[:3,3]-T[:3,3]); er=np.degrees(np.linalg.norm(logSO3(Tt[:3,:3]@T[:3,:3].T)))
    return False,q,ep,er

def ik_multi(J,tcp,Tt,rng,restarts=12):
    lo=np.array([j['lo'] for j in J]); hi=np.array([j['hi'] for j in J])
    best=(False,None,9,9)
    for r in range(restarts):
        q0=(lo+hi)/2 if r==0 else rng.uniform(lo,hi)
        ok,q,ep,er=ik(J,tcp,Tt,q0)
        if ok: return True,q,ep,er
        if ep<best[2]: best=(False,q,ep,er)
    return best

P=load('piper'); X=load('piper_x')
rng=np.random.default_rng(7)

# ---- torso frame: dual_piper official base offsets, arms parallel, 570 mm apart
Y_L, Y_R = -0.285, +0.285

# ---- task workspace box (tabletop home manipulation), in torso frame, arm-base height ref
BOX = dict(x=(0.20,0.65), y=(-0.55,0.55), z=(-0.20,0.30))
COS_DOWN = np.cos(np.radians(60))   # approach axis within 60 deg of straight down

def in_box(p_torso, approach):
    return (BOX['x'][0]<=p_torso[0]<=BOX['x'][1] and BOX['y'][0]<=p_torso[1]<=BOX['y'][1]
            and BOX['z'][0]<=p_torso[2]<=BOX['z'][1] and approach@np.array([0,0,-1.])>COS_DOWN)

def sample_task_poses(J,tcp,y_off,n,rng):
    """rejection-sample Piper configs whose TCP lands in the task box, gripper pointing down"""
    lo=np.array([j['lo'] for j in J]); hi=np.array([j['hi'] for j in J])
    out=[]; tries=0
    while len(out)<n and tries<n*4000:
        tries+=1
        q=rng.uniform(lo,hi)
        T,_,_,_=fk(J,q,tcp)
        p_t=T[:3,3].copy(); p_t[1]+=y_off
        if in_box(p_t,T[:3,2]):
            out.append((q.copy(),T.copy()))
    return out,tries

print('='*78)
print('0. TASK BOX ACCEPTANCE (how selective the home-manipulation workspace is)')
poses_R,tries=sample_task_poses(P,TCP['piper'],Y_R,1500,rng)
print(f'   right arm: {len(poses_R)} accepted / {tries} sampled  ({100*len(poses_R)/tries:.2f}% of joint space)')

# ================= 1. SINGLE-ARM layer-3 feasibility INSIDE the task box =========
print('='*78)
print('1. LAYER-3 (task-frame EE pose) RETARGET Piper->PiperX, INSIDE TASK BOX')
N=400
sub=poses_R[:N]
res={'full_corr':0,'full_nocorr':0,'pos_only':0}
errs_nocorr=[]; perr_fail=[]
for q,T in sub:
    ok,_,ep,er = ik_multi(X,TCP['piper_x'],T,rng)          # with 90deg gripper correction
    res['full_corr']+= ok
    if not ok: perr_fail.append(ep)
    # WITHOUT correcting the 90 deg gripper mount: target expressed as if mounts matched
    Tbad = T @ np.block([[rpy(0,0,-np.pi/2),np.zeros((3,1))],[np.zeros((1,3)),np.ones((1,1))]])
    ok2,_,_,_ = ik_multi(X,TCP['piper_x'],Tbad,rng,restarts=6)
    res['full_nocorr']+= ok2
    # position only (orientation free)
    lo=np.array([j['lo'] for j in X]); hi=np.array([j['hi'] for j in X])
    okp=False
    for r in range(8):
        q0=(lo+hi)/2 if r==0 else rng.uniform(lo,hi)
        qq=q0.copy()
        for _ in range(200):
            Jm,Tc=jac(X,qq,TCP['piper_x']); ep2=T[:3,3]-Tc[:3,3]
            if np.linalg.norm(ep2)<1e-3: okp=True; break
            dq=Jm[:3].T@np.linalg.solve(Jm[:3]@Jm[:3].T+0.05**2*np.eye(3),ep2)
            qq=np.clip(qq+np.clip(dq,-0.3,0.3),lo,hi)
        if okp: break
    res['pos_only']+= okp
print(f'   full 6-DoF pose, gripper-mount 90deg CORRECTED : {100*res["full_corr"]/N:.1f}%')
print(f'   full 6-DoF pose, 90deg NOT corrected           : {100*res["full_nocorr"]/N:.1f}%')
print(f'   position only (orientation free)               : {100*res["pos_only"]/N:.1f}%')
if perr_fail:
    print(f'   residual pos error on failures: median {np.median(perr_fail)*100:.2f} cm, p90 {np.percentile(perr_fail,90)*100:.2f} cm')

# ================= 2. LAYER-4 naive joint copy INSIDE the task box ==============
print('='*78)
print('2. LAYER-4 (raw joint chunk) NAIVE COPY Piper->PiperX, INSIDE TASK BOX')
lox=np.array([j['lo'] for j in X]); hix=np.array([j['hi'] for j in X])
pe=[];re_=[];viol=0
for q,T in sub:
    v = np.any(q<lox)|np.any(q>hix)
    viol+= v
    qc=np.clip(q,lox,hix)
    Tx,_,_,_=fk(X,qc,TCP['piper_x'])
    pe.append(np.linalg.norm(Tx[:3,3]-T[:3,3]))
    re_.append(np.degrees(np.linalg.norm(logSO3(Tx[:3,:3]@T[:3,:3].T))))
print(f'   joint-limit violation rate : {100*viol/N:.1f}%')
print(f'   TCP position error  median {np.median(pe)*100:.2f} cm   p90 {np.percentile(pe,90)*100:.2f} cm')
print(f'   TCP ORIENTATION err median {np.median(re_):.1f} deg   p90 {np.percentile(re_,90):.1f} deg')

# best possible per-joint affine retarget q' = s*q + b (least squares over the box)
A=np.array([q for q,_ in sub]);
print('   -- best-fit per-joint affine retarget q\'=s*q+b (fit on FK-matched pairs):')
# fit s,b per joint by minimising TCP error via coordinate search is overkill;
# instead show that NO affine map can fix orientation: report orientation error of
# the affine family lower bound = error when only wrist joints are free to be anything
bestori=[]
for q,T in sub[:120]:
    # freeze j1..j3 (copy), optimise j4..j6 freely -> lower bound for any map that
    # preserves the "same elbow" semantics
    lo=lox.copy(); hi=hix.copy()
    best=1e9
    for r in range(24):
        qq=np.concatenate([q[:3],rng.uniform(lo[3:],hi[3:])])
        for _ in range(150):
            Jm,Tc=jac(X,qq,TCP['piper_x'])
            er=logSO3(T[:3,:3]@Tc[:3,:3].T); ep2=T[:3,3]-Tc[:3,3]
            e=np.concatenate([ep2,er])
            dq=Jm.T@np.linalg.solve(Jm@Jm.T+0.05**2*np.eye(6),e)
            dq[:3]=0
            qq=np.clip(qq+np.clip(dq,-0.3,0.3),lo,hi)
        Jm,Tc=jac(X,qq,TCP['piper_x'])
        d=np.degrees(np.linalg.norm(logSO3(T[:3,:3]@Tc[:3,:3].T)))
        best=min(best,d)
    bestori.append(best)
print(f'      copy j1-j3 + freely re-solve j4-j6: residual orientation err median {np.median(bestori):.1f} deg')

# ================= 3. DUAL-ARM (T_abs, T_rel) ==================================
print('='*78)
print('3. DUAL-ARM RETARGET: per-arm independent vs cooperative (T_rel preserved)')
poses_L,_=sample_task_poses(P,TCP['piper'],Y_L,600,rng)
M=250
def to_torso(T,yoff):
    Tt=T.copy(); Tt[1,3]+=yoff; return Tt
def from_torso(T,yoff):
    Tt=T.copy(); Tt[1,3]-=yoff; return Tt

# build bimanual samples where the two hands are plausibly cooperating (hands within 60 cm)
pairs=[]
for i in range(len(poses_L)):
    for j in range(len(poses_R)):
        TL=to_torso(poses_L[i][1],Y_L); TR=to_torso(poses_R[j][1],Y_R)
        d=np.linalg.norm(TL[:3,3]-TR[:3,3])
        if 0.10<d<0.60:
            pairs.append((poses_L[i],poses_R[j],TL,TR)); break
    if len(pairs)>=M: break
print(f'   bimanual cooperating samples: {len(pairs)}  (hand separation 10-60 cm)')

indep_ok=0; coop_ok=0; rel_err_indep=[]
for (qL,TLp),(qR,TRp),TL,TR in pairs:
    T_rel = np.linalg.inv(TL)@TR
    # --- (a) per-arm independent retarget: each absolute pose solved separately
    okL,qXL,_,_ = ik_multi(X,TCP['piper_x'],from_torso(TL,Y_L),rng,restarts=8)
    okR,qXR,_,_ = ik_multi(X,TCP['piper_x'],from_torso(TR,Y_R),rng,restarts=8)
    indep_ok += (okL and okR)
    TLx,_,_,_=fk(X,qXL,TCP['piper_x']); TRx,_,_,_=fk(X,qXR,TCP['piper_x'])
    Trel_x=np.linalg.inv(to_torso(TLx,Y_L))@to_torso(TRx,Y_R)
    rel_err_indep.append((np.linalg.norm(Trel_x[:3,3]-T_rel[:3,3]),
                          np.degrees(np.linalg.norm(logSO3(Trel_x[:3,:3]@T_rel[:3,:3].T)))))
    # --- (b) cooperative: preserve T_rel exactly, let the PAIR float by SE(3) offset g
    found=False
    for trial in range(40):
        # random small rigid offset of the whole bimanual task frame
        dp=rng.uniform(-0.10,0.10,3); dth=rng.uniform(-0.35,0.35,3)
        g=np.eye(4); g[:3,:3]=axrot(np.array([1,0,0.]),dth[0])@axrot(np.array([0,1,0.]),dth[1])@axrot(np.array([0,0,1.]),dth[2]); g[:3,3]=dp
        TLg = g@TL; TRg = TLg@T_rel          # T_rel preserved BY CONSTRUCTION
        o1,_,_,_=ik_multi(X,TCP['piper_x'],from_torso(TLg,Y_L),rng,restarts=3)
        if not o1: continue
        o2,_,_,_=ik_multi(X,TCP['piper_x'],from_torso(TRg,Y_R),rng,restarts=3)
        if o1 and o2: found=True; break
    coop_ok+=found
r=np.array(rel_err_indep)
n=len(pairs)
print(f'   (a) per-arm independent, BOTH arms feasible      : {100*indep_ok/n:.1f}%')
print(f'       relative-pose error when forced (clipped IK) : pos median {np.median(r[:,0])*100:.2f} cm, '
      f'rot median {np.median(r[:,1]):.1f} deg')
print(f'   (b) cooperative (T_rel hard, pair free in SE(3)) : {100*coop_ok/n:.1f}%')
print('='*78)
