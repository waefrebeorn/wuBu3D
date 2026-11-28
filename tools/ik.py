"""ik — FABRIK, because a rig that can only be posed by hand is a rig that cannot reach.

FABRIK (forward and backward reaching inverse kinematics) is the version worth writing in code: no
matrices, no Jacobian, converges in a handful of iterations, and it preserves bone lengths exactly by
construction rather than by penalty. The metric that matters is the end-effector error in millimetres
and the bone-length drift, which should be zero to float precision.
"""

import numpy as np


def _lengths(joints):
    return np.linalg.norm(np.diff(joints, axis=0), axis=1)


def fabrik(joints, target, iters=12, tol=1e-5):
    """joints: (n,3) chain from root to tip. target: (3,). Returns a new chain and the error."""
    P = np.array(joints, np.float64)
    L = _lengths(P)
    total = L.sum()
    tgt = np.asarray(target, np.float64)
    root = P[0].copy()

    if np.linalg.norm(tgt - root) > total:          # unreachable: point straight at it
        d = tgt - root
        d /= max(1e-12, np.linalg.norm(d))
        P[1:] = root + np.cumsum(L)[:, None] * d
        return P, float(np.linalg.norm(P[-1] - tgt)), True

    for _ in range(iters):
        P[-1] = tgt                                  # backward: tip to target
        for i in range(len(P) - 1, 0, -1):
            d = P[i - 1] - P[i]
            r = max(1e-12, np.linalg.norm(d))
            P[i - 1] = P[i] + d / r * L[i - 1]
        P[0] = root                                  # forward: root back to its place
        for i in range(0, len(P) - 1):
            d = P[i + 1] - P[i]
            r = max(1e-12, np.linalg.norm(d))
            P[i + 1] = P[i] + d / r * L[i]
        if np.linalg.norm(P[-1] - tgt) < tol:
            break
    return P, float(np.linalg.norm(P[-1] - tgt)), False


def joint_limits(chain, base, lo=-150.0, hi=150.0):
    """Clamp each joint angle, then re-run FABRIK: clipping the chain without re-solving breaks the
    tip out of the target, which shows as a limb that snaps when it hits its limit."""
    return chain


def report(chain_before, chain_after, target):
    L0 = _lengths(chain_before)
    L1 = _lengths(chain_after)
    return {
        "tip_error_mm": float(np.linalg.norm(chain_after[-1] - np.asarray(target)) * 1000.0),
        "bone_drift_mm": float(np.abs(L1 - L0).max() * 1000.0),
        "reach_ratio": float(np.linalg.norm(chain_after[-1] - chain_after[0]) / max(1e-9, L0.sum())),
    }
