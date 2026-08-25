"""Follow-ups: (i) REVERSE direction X->Piper for P3; (ii) cooperative slack ladder."""
import numpy as np, xml.etree.ElementTree as ET
exec(open('taskspace.py').read().split("P=load('piper')")[0].split('"""')[2])

P=load('piper'); X=load('piper_x')
rng=np.random.default_rng(11)
Y_L,Y_R=-0.285,0.285
BOX=dict(x=(0.20,0.65),y=(-0.55,0.55),z=(-0.20,0.30)); COS_DOWN=np.cos(np.radians(60))
def in_box(p,a): return (BOX['x'][0]<=p[0]<=BOX['x'][1] and BOX['y'][0]<=p[1]<=BOX['y'][1]
                         and BOX['z'][0]<=p[2]<=BOX['z'][1] and a@np.array([0,0,-1.])>COS_DOWN)
def sample(J,tcp,yoff,n,rng):
    lo=np.array([j['lo'] for j in J]);hi=np.array([j['hi'] for j in J]);out=[];t=0
    while len(out)<n and t<n*5000:
        t+=1;q=rng.uniform(lo,hi);T,_,_,_=fk(J,q,tcp)
        p=T[:3,3].copy();p[1]+=yoff
        if in_box(p,T[:3,2]): out.append((q.copy(),T.copy()))
    return out,t

print('='*76);print('4. DIRECTIONAL ASYMMETRY inside task box (basis for new P3)')
N=300
for (src,dst,sn,dn) in [(P,X,'piper','piper_x'),(X,P,'piper_x','piper')]:
    ps,t=sample(src,TCP[sn],Y_R,N,rng)
    ok=0;fails=[]
    for q,T in ps:
        o,_,ep,_=ik_multi(dst,TCP[dn],T,rng,restarts=10); ok+=o
        if not o: fails.append(ep)
    print(f'   writer {sn:8s} -> reader {dn:8s} : layer-3 IK feasible {100*ok/len(ps):5.1f}%   '
          f'(box acceptance of writer {100*len(ps)/t:.2f}%)')

print('='*76);print('5. COOPERATIVE SLACK LADDER (how much task-level float the anchor allows)')
pl,_=sample(P,TCP['piper'],Y_L,400,rng); pr,_=sample(P,TCP['piper'],Y_R,400,rng)
pairs=[]
for i in range(len(pl)):
    for j in range(len(pr)):
        TL=pl[i][1].copy();TL[1,3]+=Y_L; TR=pr[j][1].copy();TR[1,3]+=Y_R
        if 0.10<np.linalg.norm(TL[:3,3]-TR[:3,3])<0.60: pairs.append((TL,TR));break
    if len(pairs)>=150: break
print(f'   {len(pairs)} bimanual pairs')
for name,dp_m,dth_d in [('rigid anchor  (doors: hinge fixed)',0.00,0.0),
                        ('tight  +/-2cm,5deg (articulated)',0.02,5.0),
                        ('loose  +/-10cm,20deg (free cloth)',0.10,20.0)]:
    ok=0
    for TL,TR in pairs:
        Trel=np.linalg.inv(TL)@TR; found=False
        ntr=1 if dp_m==0 else 30
        for _ in range(ntr):
            if dp_m==0: g=np.eye(4)
            else:
                d=rng.uniform(-dth_d,dth_d,3)*np.pi/180
                g=np.eye(4);g[:3,:3]=axrot(np.array([1,0,0.]),d[0])@axrot(np.array([0,1,0.]),d[1])@axrot(np.array([0,0,1.]),d[2])
                g[:3,3]=rng.uniform(-dp_m,dp_m,3)
            TLg=g@TL; TRg=TLg@Trel
            a=TLg.copy();a[1,3]-=Y_L; b=TRg.copy();b[1,3]-=Y_R
            o1,_,_,_=ik_multi(X,TCP['piper_x'],a,rng,restarts=3)
            if not o1: continue
            o2,_,_,_=ik_multi(X,TCP['piper_x'],b,rng,restarts=3)
            if o2: found=True;break
        ok+=found
    print(f'   {name:36s}: {100*ok/len(pairs):5.1f}%')
print('='*76)
