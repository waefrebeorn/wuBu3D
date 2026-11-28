"""ragdoll — the newest top-five gap (16 products on a full census), on the solver cloth proved.

A ragdoll is not a different solver from a cape: it is particles at the joints, distance constraints
along the bones, and a few cross constraints per body so a limb does not fold through itself. What
makes it read as a body rather than a net is that **bones stay the right length**, so that is the
metric — max deviation from rest, as a fraction.

    ragdoll.step(...)   reuse the verlet core in cloth.c
    ragdoll.bones()     the joint graph, in rest pose
"""

import ctypes

import numpy as np

_P, _I, _F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float

_lib = ctypes.CDLL("/opt/data/work/wubu3d/libcloth.so")
_lib.wubu_cloth_step.argtypes = [_P, _I, _P, _P, _P, _I, _F, _F, _F, _F, _F, _I, _F, _I]
_lib.wubu_cloth_stretch.argtypes = [_P, _P, _P, _P, _I]
_lib.wubu_cloth_stretch.restype = _F
_lib.wubu_cloth_floor.argtypes = [_P, _I, _F, _F]
_lib.wubu_cloth_floor.restype = _I

# joint name -> rest position on a 1.0-high figure, and the bones as (a, b, stiffness)
JOINTS = {
    "head": (0.0, 0.90, 0.0),
    "neck": (0.0, 0.74, 0.0),
    "chest": (0.0, 0.62, 0.0),
    "hips": (0.0, 0.40, 0.0),
    "lsh": (-0.13, 0.66, 0.0), "rsh": (0.13, 0.66, 0.0),
    "lel": (-0.22, 0.46, 0.02), "rel": (0.22, 0.46, 0.02),
    "lhip": (-0.07, 0.38, 0.0), "rhip": (0.07, 0.38, 0.0),
    "lknee": (-0.07, 0.19, 0.0), "rknee": (0.07, 0.19, 0.0),
    "lfoot": (-0.07, 0.02, 0.04), "rfoot": (0.07, 0.02, 0.04),
}
NAMES = list(JOINTS)
IDX = {n: i for i, n in enumerate(NAMES)}

# (a, b) bones, plus the cross constraints that stop a torso collapsing into a line
BONES = [("neck", "head"), ("chest", "neck"), ("hips", "chest"),
         ("lsh", "chest"), ("rsh", "chest"), ("lsh", "lel"), ("rsh", "rel"),
         ("lhip", "hips"), ("rhip", "hips"), ("lhip", "lknee"), ("rhip", "rknee"),
         ("lknee", "lfoot"), ("rknee", "rfoot"),
         ("lsh", "hips"), ("rsh", "hips"), ("lsh", "rsh"), ("lhip", "rhip"),
         ("lhip", "chest"), ("rhip", "chest")]


def build(mass_head=1.0):
    n = len(NAMES)
    p = np.zeros((n, 7), np.float32)
    for i, nm in enumerate(NAMES):
        p[i, 0:3] = JOINTS[nm]
        p[i, 3:6] = JOINTS[nm]
        p[i, 6] = 1.0 / mass_head
    ca, cb, rest = [], [], []
    for a, b in BONES:
        ia, ib = IDX[a], IDX[b]
        ca.append(ia); cb.append(ib)
        rest.append(float(np.linalg.norm(p[ia, 0:3] - p[ib, 0:3])))
    return (p, np.asarray(ca, np.int32), np.asarray(cb, np.int32),
            np.asarray(rest, np.float32))


def bone_error(p, ca, cb, rest):
    d = np.array([np.linalg.norm(p[a, 0:3] - p[b, 0:3]) for a, b in zip(ca, cb)], np.float32)
    return float(np.abs(d - rest).max() / rest.max())


def simulate(steps=240, dt=1.0 / 120.0, iters=20, seed=3, drop=0.55, radius=0.075):
    p, ca, cb, rest = build()
    # start in the air and fall: a ragdoll that is already on the floor tests nothing
    p[:, 1] += drop
    p[:, 4] += drop
    rng = np.random.default_rng(seed)
    p[:, 0] += rng.normal(0, 0.02, len(p))
    hits = 0
    worst = 0.0
    # sub-stepping is what keeps a stiff chain from stretching at impact: one big step per frame
    # cannot converge in `iters` passes, and 14% bone stretch is visible
    sub = 3
    for s in range(steps):
        for _k in range(sub):
            _lib.wubu_cloth_step(p.ctypes.data_as(_P), len(p), ca.ctypes.data_as(_P),
                                 cb.ctypes.data_as(_P), rest.ctypes.data_as(_P), len(ca),
                                 dt / sub, 0.0, -9.8, 0.0, 0.996, iters, 0.0, seed)
            # joints are spheres, not points: resting AT y=0 pancakes the body flat, so the floor sits
            # at the joint radius and the chest ends up where a chest belongs
            hits += int(_lib.wubu_cloth_floor(p.ctypes.data_as(_P), len(p), radius, 0.35))
        worst = max(worst, bone_error(p, ca, cb, rest))
    return p, ca, cb, rest, hits, worst
