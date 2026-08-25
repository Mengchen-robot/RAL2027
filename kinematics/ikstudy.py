import numpy as np, xml.etree.ElementTree as ET
np.set_printoptions(precision=4, suppress=True)
rng = np.random.default_rng(1)

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
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+np.sin(th)*K+(1-np.cos(th))*K@K
def fk_full(J,q):
    T=np.eye(4); zs=[]; ps=[]
    for i in range(6):
        Tj=np.eye(4); Tj[:3,:3]=J[i]['R']; Tj[:3,3]=J[i]['p']; T=T@Tj
        zs.append(T[:3,:3]@J[i]['a']); ps.append(T[:3,3].copy())
        Tr=np.eye(4); Tr[:3,:3]=axrot(J[i]['a'],q[i]); T=T@Tr
    return T, np.array(zs), np.array(ps)
def jac(J,q):
    T,zs,ps=fk_full(J,q); pe=T[:3,3]
    Jm=np.zeros((6,6))
    for i in range(6):
        Jm[:3,i]=np.cross(zs[i],pe-ps[i]); Jm[3:,i]=zs[i]
    return Jm,T
def logSO3(R):
    c=(np.trace(R)-1)/2; c=np.clip(c,-1,1); th=np.arccos(c)
    if th<1e-9: return np.zeros(3)
    return th/(2*np.sin(th))*np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]])
def ik(J,Tt,q0,iters=200,lam=0.05):
    lo=np.array([j['lo'] for j in J]); hi=np.array([j['hi'] for j in J])
    q=q0.copy()
    for _ in range(iters):
        Jm,T=jac(J,q)
        ep=Tt[:3,3]-T[:3,3]; er=logSO3(Tt[:3,:3]@T[:3,:3].T)
        e=np.concatenate([ep,er])
        if np.linalg.norm(ep)<1e-4 and np.linalg.norm(er)<1e-3: return True,q,np.linalg.norm(ep),np.degrees(np.linalg.norm(er))
        dq=Jm.T@np.linalg.solve(Jm@Jm.T+lam**2*np.eye(6),e)
        q=np.clip(q+np.clip(dq,-0.3,0.3),lo,hi)
    Jm,T=jac(J,q)
    ep=np.linalg.norm(Tt[:3,3]-T[:3,3]); er=np.degrees(np.linalg.norm(logSO3(Tt[:3,:3]@T[:3,:3].T)))
    return (ep<1e-4 and er<0.06),q,ep,er

M={m:load(m) for m in ['piper','piper_x','piper_h','piper_l']}
src='piper'; Js=M[src]
lo=np.array([j['lo'] for j in Js]); hi=np.array([j['hi'] for j in Js])
NS=250
Qs=rng.uniform(lo,hi,size=(NS,6))
Ts=[fk_full(Js,q)[0] for q in Qs]

print('IK FEASIBILITY: take full 6-DoF flange poses reachable by PIPER, solve on target')
print('(20 random restarts of damped-least-squares; tol 0.1mm / 0.06deg)')
for m in ['piper_x','piper_h','piper_l']:
    Jt=M[m]; tlo=np.array([j['lo'] for j in Jt]); thi=np.array([j['hi'] for j in Jt])
    ok=0; okpos=0
    for k in range(NS):
        Tt=Ts[k]; s=False
        for r in range(10):
            q0 = np.clip(Qs[k],tlo,thi) if r==0 else rng.uniform(tlo,thi)
            good,q,ep,er = ik(Jt,Tt,q0)
            if good: s=True; break
        ok += s
        # position-only feasibility (ignore orientation)
        if not s:
            for r in range(10):
                q0=rng.uniform(tlo,thi)
                good,q,ep,er=ik(Jt,Tt,q0)
                if ep<1e-3: okpos+=1; break
        else: okpos+=1
    print(f'  piper -> {m:8s}: full 6-DoF pose IK success {ok/NS*100:5.1f}%   position-only reachable {okpos/NS*100:5.1f}%')

print()
print('SINGULARITY STRUCTURE: manipulability w = sqrt(det(J J^T)) sweeping each joint (others=0)')
for m in ['piper','piper_x']:
    J=M[m]
    print(f'--- {m}')
    for i in range(6):
        vals=[]
        for th in np.linspace(J[i]['lo'],J[i]['hi'],9):
            q=np.zeros(6); q[i]=th
            Jm,_=jac(J,q); w=np.sqrt(max(np.linalg.det(Jm@Jm.T),0))
            vals.append(w)
        print(f'   j{i+1}: w over range = '+' '.join(f'{v:.4f}' for v in vals))
    q=np.zeros(6); Jm,_=jac(J,q)
    print(f'   at q=0: w={np.sqrt(max(np.linalg.det(Jm@Jm.T),0)):.5f} cond={np.linalg.cond(Jm):.1f}')
