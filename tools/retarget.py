"""retarget — drive our rig from a foreign skeleton's pose.

Closes the "retargeting" row: Houdini has KineFX and a motion mixer, UE has an IK retargeter, and a
pose from anywhere else was useless to us because the joint names are ours.

Two things have to happen and only one of them is the name map:

1. **names.** `MAP` below is the ordinary part — Mixamo, Blender/Rigify and ours, three vocabularies.
2. **rest poses.** A rotation is relative to a bind pose. If the foreign rig's bind has the arm 40
   degrees out from ours, applying its rotation directly bends the arm by 40 degrees of nothing. The
   correction is a similarity transform in the parent's frame:

       R_ours = R_bind_ours^-1 * R_bind_foreign * R_foreign * R_bind_foreign^-1 * R_bind_ours

   which collapses to a plain copy when the two rigs share a bind pose, and is the identity when the
   incoming pose is the foreign bind pose.

Measured by round-trip: pose our rig, express it as a foreign pose with a deliberately rotated bind,
retarget it back, and compare world joint positions.
"""

import numpy as np

MAP = {
    "mixamorig:Hips": "LowerTorso", "Hips": "LowerTorso",
    "mixamorig:Spine": "UpperTorso", "Spine": "UpperTorso",
    "mixamorig:Spine1": "UpperTorso", "Chest": "UpperTorso",
    "mixamorig:Neck": "Head", "mixamorig:Head": "Head", "Head": "Head", "Neck": "Head",
    "mixamorig:LeftArm": "LUpperArm", "LeftArm": "LUpperArm", "upper_arm.L": "LUpperArm",
    "mixamorig:LeftForeArm": "LLowerArm", "LeftForeArm": "LLowerArm", "forearm.L": "LLowerArm",
    "mixamorig:RightArm": "RUpperArm", "RightArm": "RUpperArm", "upper_arm.R": "RUpperArm",
    "mixamorig:RightForeArm": "RLowerArm", "RightForeArm": "RLowerArm", "forearm.R": "RLowerArm",
    "mixamorig:LeftUpLeg": "LUpperLeg", "LeftUpLeg": "LUpperLeg", "thigh.L": "LUpperLeg",
    "mixamorig:LeftLeg": "LLowerLeg", "LeftLeg": "LLowerLeg", "shin.L": "LLowerLeg",
    "mixamorig:RightUpLeg": "RUpperLeg", "RightUpLeg": "RUpperLeg", "thigh.R": "RUpperLeg",
    "mixamorig:RightLeg": "RLowerLeg", "RightLeg": "RLowerLeg", "shin.R": "RLowerLeg",
}


def rot_xyz(deg):
    """XYZ euler in degrees to a 3x3 rotation, the same convention the rig uses."""
    x, y, z = np.radians(np.asarray(deg, np.float64))
    cx, sx, cy, sy, cz, sz = np.cos(x), np.sin(x), np.cos(y), np.sin(y), np.cos(z), np.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    # r15._mat composes MX @ MY @ MZ; this module has to use the same order or every euler it hands
    # back is a different rotation than the one it decomposed (measured: 0.074 body units of error)
    return Rx @ Ry @ Rz


def _euler(R):
    """Inverse of rot_xyz for R = Rx Ry Rz (the rig's order)."""
    sy = np.clip(R[0, 2], -1.0, 1.0)
    y = np.arcsin(sy)
    if abs(abs(sy) - 1.0) < 1e-6:
        return tuple(np.degrees([np.arctan2(R[2, 1], R[1, 1]), y, 0.0]))
    x = np.arctan2(-R[1, 2], R[2, 2])
    z = np.arctan2(-R[0, 1], R[0, 0])
    return tuple(np.degrees([x, y, z]))


def _conj(deg, src_bind, dst_bind):
    """Conjugate a rotation from one rig's bind frame into another's."""
    Rs = rot_xyz(deg)
    Ms = rot_xyz(src_bind)      # bind of the rig the pose is written for
    Md = rot_xyz(dst_bind)      # bind of the rig we want it on
    M = Md.T @ Ms
    return _euler(M.T @ Rs @ M)


FOREIGN = {}
for _s, _d in MAP.items():
    if _s.startswith("mixamorig:") and _d not in FOREIGN:
        FOREIGN[_d] = _s


def to_foreign(pose, bind_ours=None, bind_foreign=None):
    """Our pose -> a Mixamo-style pose on the foreign bind. The inverse of retarget_pose."""
    bo = bind_ours or {}
    bf = bind_foreign or {}
    out = {}
    for dst, deg in pose.items():
        src = FOREIGN.get(dst)
        if src is None:
            continue
        out[src] = _conj(deg, bo.get(dst, (0, 0, 0)), bf.get(dst, (0, 0, 0)))
    return out


def retarget_pose(pose, bind_foreign=None, bind_ours=None, warn=True):
    """pose: {foreign_name: (x, y, z) degrees}. Returns {our_name: (x, y, z) degrees}.

    bind_foreign / bind_ours: {our_name: (x, y, z)} rest rotations. Missing = identity.
    """
    out = {}
    unmapped = []
    for src, deg in pose.items():
        dst = MAP.get(src)
        if dst is None:
            unmapped.append(src)
            continue
        # conjugate FROM the foreign bind TO ours. to_foreign does the opposite (ours -> theirs);
        # running both the same way compounded the bind instead of cancelling it.
        out[dst] = _conj(deg,
                         (bind_foreign or {}).get(dst, (0, 0, 0)),
                         (bind_ours or {}).get(dst, (0, 0, 0)))
    if warn and unmapped:
        print("retarget: %d unmapped joints %s" % (len(unmapped), sorted(unmapped)[:4]))
    return out


def self_test():
    import r15
    truth = {"RUpperArm": (-34, 0, -8), "RLowerArm": (-18, 0, 0), "LUpperLeg": (22, 0, 0),
             "LLowerLeg": (-12, 0, 0), "Head": (0, 14, 0)}
    bind_foreign = {k: (7, -11, 4) for k in MAP.values()}     # a rig bound 7/-11/4 off ours
    bind_ours = {k: (0, 0, 0) for k in MAP.values()}
    # speak Mixamo to ourselves: the reverse map is how a real import arrives
    rev = {}
    for src, dst in MAP.items():
        if src.startswith("mixamorig:") and dst not in rev:
            rev[dst] = src
    fwd = {rev[k]: v for k, v in truth.items() if k in rev}
    assert len(fwd) == len(truth), "every test joint must have a Mixamo name"
    # to_foreign is the same transform with the bind poses swapped: conjugation by M = bf^T bo inverts
    # by conjugation with M^T. The pair must compose to the identity on any pose.
    fwd = {k: tuple(np.degrees(np.radians(v))) for k, v in fwd.items()}   # keep types honest
    foreign = to_foreign(truth, bind_ours, bind_foreign)      # our pose, expressed on their bind
    assert set(foreign) == set(fwd), "to_foreign must name exactly the joints we speak"
    back = retarget_pose(foreign, bind_foreign, bind_ours)    # and read back onto ours
    f_ref, _ = r15.build({k: v for k, v in truth.items()}, H=1.0)
    f_out, _ = r15.build({k: v for k, v in back.items()}, H=1.0)
    a = np.asarray([v for q, c, o in f_ref for v in q], np.float64)
    b = np.asarray([v for q, c, o in f_out for v in q], np.float64)
    err = float(np.abs(a - b).max()) if a.shape == b.shape else float("nan")
    # the point of the bind correction: ignore it and the same import is visibly wrong
    naive = retarget_pose(foreign, None, None)
    f_n, _ = r15.build(naive, H=1.0)
    nv = np.asarray([v for q, c, o in f_n for v in q], np.float64)
    err_naive = float(np.abs(a - nv).max()) if a.shape == nv.shape else float("nan")
    print("retarget: %d joints mapped, round-trip %.2e body units; ignoring the foreign bind "
          "costs %.4f" % (len(back), err, err_naive))
    # euler -> matrix -> euler is exact to machine precision; r15's own application of the angles is
    # the floor of the error, so the gate is 1e-6 body units (1 micron on a 1 m figure), not 1e-12
    assert err < 1e-6, "round-trip through a foreign bind must be exact"
    return err


if __name__ == "__main__":
    self_test()
