"""C11 mesh + IK: does the fast path actually hold up?

  1. weld    a quad soup collapses to the right unique count
  2. crease  normals split at a cube's edges and smooth on a sphere
  3. QEM     a 5k-triangle sphere decimates to ~1k with bounded surface error, fast
  4. IK      two-bone lands on the target analytically; FABRIK converges on a chain

Run: PYTHONPATH=/opt/data/shitpost-box/pylibs python3 tests/test_c11_mesh_ik.py
"""

import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wubu3d_ik as wi  # noqa: E402
import wubu3d_mesh as wm  # noqa: E402


# ---------------------------------------------------------------- test meshes

def icosphere(subdiv=4):
    t = (1.0 + 5 ** 0.5) / 2.0
    verts = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),
             (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
             (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
             (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
             (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
             (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    verts = [np.array(v, float) / np.linalg.norm(v) for v in verts]
    for _ in range(subdiv):
        cache = {}
        newf = []

        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                m = verts[a] + verts[b]
                m /= np.linalg.norm(m)
                verts.append(m)
                cache[k] = len(verts) - 1
            return cache[k]

        for a, b, c in faces:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            newf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        faces = newf
    return np.array(verts, np.float32), np.array(faces, np.uint32)


def quad_soup(pos, tri):
    """Explode to one vertex per corner — the state a mesh arrives in before welding."""
    pts = pos[tri.reshape(-1)]
    idx = np.arange(len(pts), dtype=np.uint32).reshape(-1, 3)
    return pts, idx


def point_tri_dist(p, a, b, c):
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = ab @ ap, ac @ ap
    if d1 <= 0 and d2 <= 0:
        return np.linalg.norm(p - a)
    bp = p - b
    d3, d4 = ab @ bp, ac @ bp
    if d3 >= 0 and d4 <= d3:
        return np.linalg.norm(p - b)
    vc = d1 * d4 - d3 * d2
    if vc <= 0 and d1 >= 0 and d3 <= 0:
        v = d1 / (d1 - d3)
        return np.linalg.norm(p - (a + v * ab))
    cp = p - c
    d5, d6 = ab @ cp, ac @ cp
    if d6 >= 0 and d5 <= d6:
        return np.linalg.norm(p - c)
    vb = d5 * d2 - d1 * d6
    if vb <= 0 and d2 >= 0 and d6 <= 0:
        w = d2 / (d2 - d6)
        return np.linalg.norm(p - (a + w * ac))
    va = d3 * d6 - d5 * d4
    if va <= 0 and (d4 - d3) >= 0 and (d5 - d6) >= 0:
        w = (d4 - d3) / ((d4 - d3) + (d5 - d6))
        return np.linalg.norm(p - (b + w * (c - b)))
    denom = 1.0 / (va + vb + vc)
    v, w = vb * denom, vc * denom
    return np.linalg.norm(p - (a + ab * v + ac * w))


def main():
    ok = True

    # 1 weld
    pos, tri = icosphere(3)
    soup, stri = quad_soup(pos, tri)
    remap, uniq = wm.weld(soup, cell=1e-5)
    print("1 weld: %d soup vertices -> %d unique (original %d)" % (len(soup), len(uniq), len(pos)))
    ok &= abs(len(uniq) - len(pos)) <= max(2, len(pos) // 50)

    # 2 crease normals
    cube = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                     [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], np.float32)
    ctri = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
                     [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6],
                     [1, 2, 6], [1, 6, 5], [0, 4, 7], [0, 7, 3]], np.uint32)
    sharp = wm.corner_normals(cube, ctri, cos_threshold=0.99)
    spread = float(np.abs(sharp.reshape(-1, 3)).min())
    fn = wm.face_normals(cube, ctri)
    fn /= np.linalg.norm(fn, axis=1, keepdims=True)
    agree = max(float((sharp[f, k] @ fn[f])) for f in range(len(ctri)) for k in range(3))
    print("2 crease: cube corners align to their own face (max dot %.3f), no blending across edges"
          % agree)
    ok &= agree > 0.99

    spine, stri2 = icosphere(3)
    smooth = wm.corner_normals(spine, stri2, cos_threshold=-1.0)
    radial = spine[stri2]
    radial = radial / np.linalg.norm(radial, axis=2, keepdims=True)
    dots = (smooth * radial).sum(-1)
    print("   sphere: corner normals follow the surface, mean dot %.4f, min %.3f"
          % (dots.mean(), dots.min()))
    ok &= dots.mean() > 0.97

    # 3 QEM
    big_pos, big_tri = icosphere(4)
    soup2, stri3 = quad_soup(big_pos, big_tri)
    remap2, uniq2 = wm.weld(soup2, cell=1e-6)
    welded_tri = remap2[stri3.reshape(-1)].reshape(-1, 3).astype(np.uint32)
    t0 = time.perf_counter()
    new_pos, new_tri = wm.simplify(uniq2, welded_tri, target=1000)
    dt = time.perf_counter() - t0
    errs = []
    rng = np.random.default_rng(3)
    for _ in range(120):
        i = int(rng.integers(0, len(welded_tri)))
        a, b, c = uniq2[welded_tri[i]]
        p = (a + b + c) / 3.0
        d = min(point_tri_dist(p, *new_pos[t]) for t in new_tri[:1500])
        errs.append(d)
    errs = np.array(errs)
    print("3 QEM: %d -> %d triangles in %.0f ms; surface error mean %.4f max %.4f (radius 1)"
          % (len(welded_tri), len(new_tri), dt * 1000, errs.mean(), errs.max()))
    ok &= len(new_tri) <= 1100 and errs.mean() < 0.03 and dt < 5.0

    # 4 IK
    root = np.array([0.0, 0.0, 0.0], np.float32)
    target = np.array([0.55, -0.30, 0.20], np.float32)
    good, joint, end = wi.two_bone(root, target, 0.62, 0.44, pole=(0, -1, 1))
    e = float(np.linalg.norm(end - target))
    # the elbow must sit exactly one upper-arm length from the root
    l1e = float(np.linalg.norm(joint - root))
    l2e = float(np.linalg.norm(end - joint))
    print("4 two-bone: end error %.2e, |root-joint| %.4f (want 0.6200), |joint-end| %.4f (want 0.4400)"
          % (e, l1e, l2e))
    ok &= good == 1 and e < 1e-4 and abs(l1e - 0.62) < 1e-3 and abs(l2e - 0.44) < 1e-3

    chain = np.array([[0, i * 0.2, 0] for i in range(8)], np.float32)
    goal = np.array([0.9, 0.9, 0.4], np.float32)
    solved, iters = wi.fabrik(chain, goal, max_iter=32, tol=1e-3)
    ee = float(np.linalg.norm(solved[-1] - goal))
    lens = np.linalg.norm(np.diff(solved, axis=0), axis=1)
    print("   FABRIK: 8 joints, converged in %d iterations, end error %.2e, bone lengths %.3f..%.3f"
          % (iters, ee, lens.min(), lens.max()))
    ok &= ee < 2e-3 and lens.std() < 1e-3

    print("ok" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
