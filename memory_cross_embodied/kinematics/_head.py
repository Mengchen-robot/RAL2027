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

