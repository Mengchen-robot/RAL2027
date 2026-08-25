import numpy as np, xml.etree.ElementTree as ET, itertools
np.set_printoptions(precision=4, suppress=True)
rng = np.random.default_rng(0)

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
    a=a/np.linalg.norm(a); K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+np.sin(th)*K+(1-np.cos(th))*K@K

def fk(J,q,upto=None):
    T=np.eye(4); frames=[]
    n=len(J) if upto is None else upto
    for i in range(n):
        Tj=np.eye(4); Tj[:3,:3]=J[i]['R']; Tj[:3,3]=J[i]['p']
        T=T@Tj
        frames.append((T[:3,3].copy(), T[:3,:3]@J[i]['a']))   # joint i axis origin+dir in base
        Tr=np.eye(4); Tr[:3,:3]=axrot(J[i]['a'],q[i]); T=T@Tr
    return T, frames

def line_dist(p1,d1,p2,d2):
    d1=d1/np.linalg.norm(d1); d2=d2/np.linalg.norm(d2)
    c=np.cross(d1,d2); n=np.linalg.norm(c)
    if n<1e-9: return np.linalg.norm(np.cross(p2-p1,d1))  # parallel
    return abs((p2-p1)@c)/n

models=['piper','piper_x','piper_h','piper_l']
M={m:load(m) for m in models}

print('='*70); print('A. WRIST STRUCTURE: pairwise min-distance between joint axis lines (m)')
print('   (0 => axes intersect; checked at 5 random configs, max over configs)')
for m in models:
    J=M[m]
    worst=np.zeros((6,6))
    for _ in range(5):
        q=np.array([rng.uniform(j['lo'],j['hi']) for j in J])
        _,fr=fk(J,q)
        for i in range(6):
            for k in range(6):
                worst[i,k]=max(worst[i,k], line_dist(fr[i][0],fr[i][1],fr[k][0],fr[k][1]))
    print(f'--- {m}')
    for i in range(6):
        print('   ', ' '.join(f'{worst[i,k]:7.4f}' for k in range(6)))
    # explicit last-3 common intersection test
    q=np.array([rng.uniform(j['lo'],j['hi']) for j in J]); _,fr=fk(J,q)
    d45=line_dist(*fr[3],*fr[4]); d56=line_dist(*fr[4],*fr[5]); d46=line_dist(*fr[3],*fr[5])
    print(f'    last-3 axis distances: d(4,5)={d45:.5f} d(5,6)={d56:.5f} d(4,6)={d46:.5f}'
          f'  -> spherical wrist? {"YES" if max(d45,d56,d46)<1e-4 else "NO"}')
    a2,a3,a4=fr[1][1],fr[2][1],fr[3][1]
    par=abs(a2@a3)>0.9999 and abs(a3@a4)>0.9999
    print(f'    axes 2,3,4 mutually parallel? {"YES" if par else "NO"}')

print(); print('='*70); print('B. REACH / WORKSPACE (Monte Carlo, N=200000, flange = link6 frame origin)')
N=200000
pts={}
for m in models:
    J=M[m]
    lo=np.array([j['lo'] for j in J]); hi=np.array([j['hi'] for j in J])
    Q=rng.uniform(lo,hi,size=(N,6))
    P=np.empty((N,3))
    for i in range(N):
        T,_=fk(J,Q[i]); P[i]=T[:3,3]
    pts[m]=P
    d=np.linalg.norm(P-np.array([0,0,0.123]),axis=1)
    print(f'{m:8s} max|p-shoulder|={d.max():.4f} m  mean={d.mean():.4f}  '
          f'z range=[{P[:,2].min():.3f},{P[:,2].max():.3f}]  '
          f'|xy| max={np.linalg.norm(P[:,:2],axis=1).max():.4f}')

print(); print('C. WORKSPACE OVERLAP via 2cm voxel occupancy (flange positions)')
vox=0.02
def vset(P): return set(map(tuple,np.floor(P/vox).astype(int)))
V={m:vset(pts[m]) for m in models}
for a,b in [('piper','piper_x'),('piper','piper_h'),('piper','piper_l'),('piper_h','piper_x')]:
    I=len(V[a]&V[b]); U=len(V[a]|V[b])
    print(f'  {a:8s} vs {b:8s}: IoU={I/U:.3f}  |A|={len(V[a])} |B|={len(V[b])} '
          f' frac of A covered by B={I/len(V[a]):.3f}  frac of B covered by A={I/len(V[b]):.3f}')

print(); print('='*70); print('D. NAIVE JOINT-COPY TRANSFER: apply Piper q directly to target arm')
J0=M['piper']
lo=np.array([j['lo'] for j in J0]); hi=np.array([j['hi'] for j in J0])
Q=rng.uniform(lo,hi,size=(20000,6))
for m in ['piper_x','piper_h','piper_l']:
    Jt=M[m]
    tlo=np.array([j['lo'] for j in Jt]); thi=np.array([j['hi'] for j in Jt])
    viol=np.mean(np.any((Q<tlo)|(Q>thi),axis=1))
    perr=[]; rerr=[]
    for i in range(len(Q)):
        q=np.clip(Q[i],tlo,thi)
        Ta,_=fk(J0,Q[i]); Tb,_=fk(Jt,q)
        perr.append(np.linalg.norm(Ta[:3,3]-Tb[:3,3]))
        c=(np.trace(Ta[:3,:3].T@Tb[:3,:3])-1)/2
        rerr.append(np.degrees(np.arccos(np.clip(c,-1,1))))
    perr=np.array(perr); rerr=np.array(rerr)
    print(f'  piper -> {m:8s}: joint-limit violation rate={viol*100:5.1f}%  '
          f'pos err median={np.median(perr)*100:6.2f} cm  p90={np.percentile(perr,90)*100:6.2f} cm  '
          f'rot err median={np.median(rerr):6.1f} deg')

print(); print('E. JOINT LIMIT TABLE (deg)')
hdr=f"{'joint':7s}"+''.join(f'{m:>22s}' for m in models); print(hdr)
for i in range(6):
    row=f'j{i+1:<6d}'
    for m in models:
        j=M[m][i]; row+=f'{np.degrees(j["lo"]):9.1f}..{np.degrees(j["hi"]):<8.1f} '
    print(row)
