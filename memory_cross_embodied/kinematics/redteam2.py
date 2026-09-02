import numpy as np, os, copy
os.chdir('/tmp/agxurdf')
src=open('taskspace.py').read()
exec(src.split("P=load('piper'); X=load('piper_x')")[0].split('"""')[2])
P=load('piper'); X=load('piper_x')
Xfree=[dict(d) for d in X]
for d in Xfree: d['lo'],d['hi']=-np.pi*1.05,np.pi*1.05   # limits relaxed to full +/-189 deg
rng=np.random.default_rng(7); Y_R=+0.285
BOX=dict(x=(0.20,0.65),y=(-0.55,0.55),z=(-0.20,0.30)); C=np.cos(np.radians(60))
def in_box(p,a): return (BOX['x'][0]<=p[0]<=BOX['x'][1] and BOX['y'][0]<=p[1]<=BOX['y'][1]
                         and BOX['z'][0]<=p[2]<=BOX['z'][1] and a@np.array([0,0,-1.])>C)
lo=np.array([j['lo'] for j in P]);hi=np.array([j['hi'] for j in P])
S=[];t=0
while len(S)<250 and t<250*4000:
    t+=1;q=rng.uniform(lo,hi);T,_,_,_=fk(P,q,TCP['piper'])
    p=T[:3,3].copy();p[1]+=Y_R
    if in_box(p,T[:3,2]): S.append((q.copy(),T.copy()))
print("WHY does 20% of layer-3 fail? limits or geometry?")
for nm,J in [('PiperX with real joint limits',X),('PiperX with limits RELAXED to +/-189 deg',Xfree)]:
    ok=0
    for q,T in S:
        o,_,_,_=ik_multi(J,TCP['piper_x'],T,rng,restarts=14); ok+=o
    print(f'   {nm:44s}: layer-3 feasible {100*ok/len(S):5.1f}%')
# which joint saturates on successes?
lox=np.array([j['lo'] for j in X]);hix=np.array([j['hi'] for j in X])
sat=np.zeros(6); n=0
for q,T in S:
    o,qx,_,_=ik_multi(X,TCP['piper_x'],T,rng,restarts=14)
    if o:
        n+=1
        sat += ((qx-lox<np.radians(3))|(hix-qx<np.radians(3))).astype(float)
print(f'   among {n} successes, fraction sitting within 3 deg of a joint limit, per joint:')
print('     ', np.round(sat/max(n,1),3))
