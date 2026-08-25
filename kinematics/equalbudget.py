"""Equal-budget dual-arm contrast (answers adversarial blocking issue: the
'+10pt cooperative gain' may be a search-budget / task-float artifact).

Three arms, ALL given the same total IK budget and the same task-level float:
  A. independent, no float,  budget 120 restarts/arm
  B. independent, WITH float (per-arm independent offsets), 40 trials x 3 restarts
  C. cooperative, WITH float (T_rel hard, pair floats rigidly), 40 x 3   <- original
Same script, same seed, same pair list.
"""
import numpy as np, os
os.chdir('/tmp/agxurdf')
src = open('taskspace.py').read()
head = src.split("print('='*78)")[0]
exec(compile(head, 'head', 'exec'))
P = load('piper'); X = load('piper_x')
rng = np.random.default_rng(11)
Y_L, Y_R = -0.285, +0.285


def to_torso(T, yoff):
    Tt = T.copy(); Tt[1, 3] += yoff; return Tt


def from_torso(T, yoff):
    Tt = T.copy(); Tt[1, 3] -= yoff; return Tt


def rand_g(rng, dp=0.10, dth=0.35):
    p = rng.uniform(-dp, dp, 3); a = rng.uniform(-dth, dth, 3)
    g = np.eye(4)
    g[:3, :3] = axrot(np.array([1, 0, 0.]), a[0]) @ axrot(np.array([0, 1, 0.]), a[1]) \
        @ axrot(np.array([0, 0, 1.]), a[2])
    g[:3, 3] = p
    return g


poses_L, _ = sample_task_poses(P, TCP['piper'], Y_L, 1200, rng)
poses_R, _ = sample_task_poses(P, TCP['piper'], Y_R, 1200, rng)
M = 400
pairs = []
for i in range(len(poses_L)):
    for j in range(len(poses_R)):
        TL = to_torso(poses_L[i][1], Y_L); TR = to_torso(poses_R[j][1], Y_R)
        d = np.linalg.norm(TL[:3, 3] - TR[:3, 3])
        if 0.10 < d < 0.60:
            pairs.append((TL, TR)); break
    if len(pairs) >= M:
        break
n = len(pairs)
print(f'bimanual cooperating pairs: {n}')

a_ok = b_ok = c_ok = 0
for TL, TR in pairs:
    T_rel = np.linalg.inv(TL) @ TR
    # A: independent, no float, 120 restarts each
    oL, _, _, _ = ik_multi(X, TCP['piper_x'], from_torso(TL, Y_L), rng, restarts=120)
    oR, _, _, _ = ik_multi(X, TCP['piper_x'], from_torso(TR, Y_R), rng, restarts=120)
    a_ok += (oL and oR)
    # B: independent WITH per-arm float, 40 x 3
    got = False
    for _ in range(40):
        gL = rand_g(rng); gR = rand_g(rng)
        o1, _, _, _ = ik_multi(X, TCP['piper_x'], from_torso(gL @ TL, Y_L), rng, restarts=3)
        if not o1:
            continue
        o2, _, _, _ = ik_multi(X, TCP['piper_x'], from_torso(gR @ TR, Y_R), rng, restarts=3)
        if o2:
            got = True; break
    b_ok += got
    # C: cooperative, T_rel hard, pair floats rigidly, 40 x 3
    got = False
    for _ in range(40):
        g = rand_g(rng)
        TLg = g @ TL; TRg = TLg @ T_rel
        o1, _, _, _ = ik_multi(X, TCP['piper_x'], from_torso(TLg, Y_L), rng, restarts=3)
        if not o1:
            continue
        o2, _, _, _ = ik_multi(X, TCP['piper_x'], from_torso(TRg, Y_R), rng, restarts=3)
        if o2:
            got = True; break
    c_ok += got


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


for nm, k in [('A independent, NO float, 120 restarts/arm', a_ok),
              ('B independent, per-arm float, 40x3       ', b_ok),
              ('C cooperative, T_rel hard + float, 40x3  ', c_ok)]:
    lo, hi = wilson(k, n)
    print(f'   {nm}: {100*k/n:5.1f}%  Wilson95 [{lo:.1f}, {hi:.1f}]')
