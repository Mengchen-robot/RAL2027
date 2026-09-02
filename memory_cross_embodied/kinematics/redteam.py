import numpy as np, os
os.chdir('/tmp/agxurdf')
src=open('taskspace.py').read()
head=src.split("P=load('piper'); X=load('piper_x')")[0].split('"""')[2]
exec(head)
P=load('piper'); X=load('piper_x')
rng=np.random.default_rng(7)
Y_R=+0.285
BOX=dict(x=(0.20,0.65),y=(-0.55,0.55),z=(-0.20,0.30)); COS_DOWN=np.cos(np.radians(60))
def in_box(p,a): return (BOX['x'][0]<=p[0]<=BOX['x'][1] and BOX['y'][0]<=p[1]<=BOX['y'][1]
                         and BOX['z'][0]<=p[2]<=BOX['z'][1] and a@np.array([0,0,-1.])>COS_DOWN)
lo=np.array([j['lo'] for j in P]);hi=np.array([j['hi'] for j in P])
lox=np.array([j['lo'] for j in X]);hix=np.array([j['hi'] for j in X])
S=[];t=0
while len(S)<450 and t<450*4000:
    t+=1;q=rng.uniform(lo,hi);T,_,_,_=fk(P,q,TCP['piper'])
    p=T[:3,3].copy();p[1]+=Y_R
    if in_box(p,T[:3,2]): S.append((q.copy(),T.copy()))
print(f'task-box samples: {len(S)}  (acceptance {100*len(S)/t:.2f}%)')

pairs=[]
for q,T in S:
    ok,qx,_,_=ik(X,TCP['piper_x'],T,np.clip(q,lox,hix))
    if not ok: ok,qx,_,_=ik_multi(X,TCP['piper_x'],T,rng,restarts=8)
    if ok: pairs.append((q.copy(),qx.copy(),T.copy()))
print(f'FK-matched (q_piper,q_x) pairs for calibration: {len(pairs)}')
ntr=int(0.6*len(pairs))
Atr=np.array([p[0] for p in pairs[:ntr]]); Btr=np.array([p[1] for p in pairs[:ntr]])
held=pairs[ntr:]
print(f'held-out: {len(held)}')

def report(name,qmap):
    pes=[];res=[]
    for q,_,T in held:
        qx=np.clip(qmap(q),lox,hix)
        Tc,_,_,_=fk(X,qx,TCP['piper_x'])
        pes.append(np.linalg.norm(Tc[:3,3]-T[:3,3]))
        res.append(np.degrees(np.linalg.norm(logSO3(T[:3,:3]@Tc[:3,:3].T))))
    print(f'   {name:48s} pos med {np.median(pes)*100:6.2f} cm | ori med {np.median(res):6.1f} deg | ori p90 {np.percentile(res,90):6.1f} deg')

print('='*78); print("A. CALIBRATED joint-space retarget (the counter the scripts never ran)")
report('naive copy  [redesign reports 87.5 deg]', lambda q:q)
s=np.zeros(6);b=np.zeros(6)
for k in range(6):
    M=np.stack([Atr[:,k],np.ones(len(Atr))],1)
    c,_,_,_=np.linalg.lstsq(M,Btr[:,k],rcond=None); s[k],b[k]=c
report("per-joint affine  q'=s*q+b   (12 params)", lambda q:s*q+b)
M=np.concatenate([Atr,np.ones((len(Atr),1))],1)
W,_,_,_=np.linalg.lstsq(M,Btr,rcond=None)
report("full linear       q'=Aq+b    (42 params)", lambda q:np.concatenate([q,[1.]])@W)
def feat(q): return np.concatenate([q,np.sin(q),np.cos(q),[1.]])
Mq=np.stack([feat(q) for q in Atr]); Wq,_,_,_=np.linalg.lstsq(Mq,Btr,rcond=None)
report("sin/cos-lifted linear        (114 params)", lambda q: feat(q)@Wq)
print(f'   fitted per-joint scales s = {np.round(s,3)}')
print(f'   fitted per-joint offsets b= {np.round(b,3)}')

print('='*78); print("B. TOLERANCE SENSITIVITY of the 80.0% layer-3 feasibility number")
for ptol,rd in [(1e-4,0.06),(1e-3,1.0),(3e-3,3.0),(5e-3,5.0),(1e-2,10.0)]:
    ok=0; N=200
    for q,T in S[:N]:
        got=False
        for r in range(8):
            q0=(lox+hix)/2 if r==0 else rng.uniform(lox,hix)
            o,_,_,_=ik(X,TCP['piper_x'],T,q0,ptol=ptol,rtol=np.radians(rd))
            if o: got=True;break
        ok+=got
    print(f'   ptol {ptol*1000:6.2f} mm / rtol {rd:5.2f} deg  ->  layer-3 feasible {100*ok/N:5.1f}%')
