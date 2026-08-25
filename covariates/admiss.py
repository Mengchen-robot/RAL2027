"""
admiss.py -- offline per-stage admissibility difference  dA(k) = A3(k) - A4(k)

Motivation (see idea/reframe_primitive_conditional.md, section 3):
    zeta (absorb2.py) is rank-identical to the trivial predictor -log min(T_y)
    (Spearman = 1.000 over the six archetypes), so a regression of gain on zeta
    can only confirm "tight stages transfer worse".  The admissibility difference
    is NOT rank-equivalent to that trivial predictor: it is non-monotone in
    tolerance and it CHANGES SIGN, because layer 3 buys precision at the price of
    an IK-abstain rate while layer 4 is always available.

    A_l(k) = P_frames[ || diag(1/T_y) J_k e_l || < 1 ] * (1 - abstain_l(k))

Inputs that must be MEASURED, not asserted:
    T_y(k)        stage outcome tolerance   -> Ty_measured.csv (calipers / CAD / E2)
    J_k           outcome-sensitivity map   -> measured geometry (lever arms!) or
                                               cross-demo regression on writer logs
    Sigma_e(l)    retarget residual cov     -> /tmp/agxurdf/redteam.py (layer 4),
                                               taskspace.py (layer 3)
    abstain_l(k)  per-stage IK failure rate -> taskspace.py, per stage not global
"""
import numpy as np
from scipy.stats import spearmanr

rng = np.random.default_rng(3)
N = 40000

# ---- measured retarget residuals (v5: best fixed 42-param calibration) --------
# NOTE: isotropic split is a PLACEHOLDER.  Replace with the empirical 6x6
# covariance from redteam.py before freezing F-zeta.
E4P, E4O = 0.0710 / np.sqrt(3), np.deg2rad(17.8) / np.sqrt(3)
E3P, E3O = 0.0100 / np.sqrt(3), np.deg2rad(5.0) / np.sqrt(3)
ABSTAIN3 = 0.192          # 1 - 80.8% full-pose IK feasibility (taskspace.py)
ABSTAIN4 = 0.0            # naive joint copy never abstains


def A(J, Ty, sp, so, abstain=0.0):
    E = np.concatenate([rng.normal(0, sp, (N, 3)), rng.normal(0, so, (N, 3))], 1)
    z = np.linalg.norm((E @ J.T) / Ty, axis=1)
    return float((z < 1).mean()) * (1.0 - abstain)


def dA(J, Ty, abstain3=ABSTAIN3, abstain4=ABSTAIN4):
    a4 = A(J, Ty, E4P, E4O, abstain4)
    a3 = A(J, Ty, E3P, E3O, abstain3)
    return a3, a4, a3 - a4


if __name__ == "__main__":
    arch = {}
    t = np.zeros((1, 6)); t[0, 1] = 1.0 / 0.35      # hinge, lever arm r = 0.35 m (MEASURE IT)
    arch["hinge door r=.35"] = (t, np.array([np.deg2rad(8)]))
    t2 = np.zeros((1, 6)); t2[0, 1] = 1.0           # the r = 1.0 m implicit in absorb2.py
    arch["hinge door r=1.0"] = (t2, np.array([np.deg2rad(8)]))
    z = np.zeros((1, 6)); z[0, 0] = 1.0
    arch["zip (arclength)"] = (z, np.array([0.003]))
    P = np.zeros((5, 6)); P[0, 0] = P[1, 1] = P[2, 2] = 1.0; P[3, 3] = P[4, 4] = 1.0
    arch["insert (roll free)"] = (P, np.array([.002, .002, .004, np.deg2rad(3), np.deg2rad(3)]))
    G = P.copy()
    arch["pick (axis-aligned)"] = (G, np.array([.008, .008, .010, np.deg2rad(6), np.deg2rad(6)]))
    Tr = np.zeros((3, 6)); Tr[0, 0] = Tr[1, 1] = Tr[2, 2] = 1.0
    arch["transport"] = (Tr, np.array([.05, .05, .04]))
    arch["place (6-DoF)"] = (np.eye(6), np.array([.006, .006, .006, np.deg2rad(5),
                                                  np.deg2rad(5), np.deg2rad(12)]))

    print(f"{'archetype':22s} {'A4':>6s} {'A3':>6s} {'dA=A3-A4':>9s} {'ell*':>5s} {'-logminTy':>10s}")
    d, tr = [], []
    for k, (J, Ty) in arch.items():
        a3, a4, diff = dA(J, Ty)
        star = "(4)" if diff < 0 else "(3)"
        print(f"{k:22s} {a4:6.3f} {a3:6.3f} {diff:+9.3f} {star:>5s} {-np.log(min(Ty)):10.2f}")
        if "r=1.0" not in k:
            d.append(diff); tr.append(-np.log(min(Ty)))
    print(f"\nSpearman(dA, trivial -log min Ty) = {spearmanr(d, tr).statistic:+.3f}"
          "   <- near zero: dA is NOT a relabelling of 'tightest tolerance'")

    print("\ntolerance sweep, pure-position stage (inverted-U + sign flip):")
    Jp = np.zeros((1, 6)); Jp[0, 0] = 1.0
    print("  tol(mm)     A4     A3     dA")
    for tp in [1, 2, 3, 5, 8, 12, 20, 35, 60, 100, 200]:
        a3, a4, diff = dA(Jp, np.array([tp / 1000.0]))
        print(f"  {tp:6d}  {a4:6.3f} {a3:6.3f} {diff:+7.3f}")

    print("\nhinge zeta/dA sensitivity to the (currently undeclared) lever arm r:")
    for r in [1.0, 0.8, 0.35, 0.2, 0.12]:
        Jh = np.zeros((1, 6)); Jh[0, 1] = 1.0 / r
        a3, a4, diff = dA(Jh, np.array([np.deg2rad(8)]))
        print(f"  r={r:4.2f} m   A4={a4:.3f} A3={a3:.3f} dA={diff:+.3f}  "
              f"ell*={'4' if diff < 0 else '3'}")
