"""Locked-joint reader ladder with TASK-FRIENDLY lock angle sweep.
Answers adversarial blocking issue: dual_out.txt locked joints at ZERO, which is
PiperX's straight-out configuration -> trivially 0%.  Here we sweep the lock
angle over the joint's own range and report the BEST achievable feasibility,
under both a full 6-DoF pose criterion and a 5-DoF (position + approach axis)
criterion.
"""
import numpy as np, os
os.chdir('/tmp/agxurdf')
src = open('taskspace.py').read()
head = src.split("print('='*78)\nprint('0. TASK BOX")[0].split('"""')[2]
exec(head)
P = load('piper'); X = load('piper_x')
rng = np.random.default_rng(23)
Y_R = +0.285

poses, _ = sample_task_poses(P, TCP['piper'], Y_R, 200, rng)
print(f'writer task-box poses: {len(poses)}')

lox = np.array([j['lo'] for j in X]); hix = np.array([j['hi'] for j in X])


def locked(jidx, val):
    J = [dict(d) for d in X]
    J[jidx]['lo'] = val - 1e-6; J[jidx]['hi'] = val + 1e-6
    return J


print('reference (no lock):')
ok6 = sum(ik_multi(X, TCP['piper_x'], T, rng, restarts=10)[0] for _, T in poses)
print(f'   full 6-DoF: {100*ok6/len(poses):.1f}%')

for j in [3, 4, 5]:
    row6 = []; row5 = []
    for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
        val = lox[j] + frac * (hix[j] - lox[j])
        J = locked(j, val)
        a = sum(ik_multi(J, TCP['piper_x'], T, rng, restarts=10)[0] for _, T in poses)
        b = sum(ik_pos_axis(J, TCP['piper_x'], T, rng, restarts=10)[0]
                if 'ik_pos_axis' in dir() else 0 for _, T in poses)
        row6.append(100 * a / len(poses)); row5.append(100 * b / len(poses))
    print(f'   lock j{j+1}: angle sweep (deg) '
          f'{[round(np.degrees(lox[j]+f*(hix[j]-lox[j])),1) for f in [0,.25,.5,.75,1.]]}')
    print(f'      6-DoF feasible: {[round(v,1) for v in row6]}   best {max(row6):.1f}%')
    print(f'      5-DoF feasible: {[round(v,1) for v in row5]}   best {max(row5):.1f}%')
