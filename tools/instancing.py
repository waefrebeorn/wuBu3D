"""instancing — 9,000 quads built in numpy instead of 36,000 tuples.

A scatter field of 756 boxes is 9,072 quads. Built through the object layer that is 36,288 tuples
before a pixel exists, and the per-instance `CB.box` call is itself Python. This builds every quad as
arrays in one pass, so the whole field goes to `_draw_arrays` with no per-instance anything.
"""

import numpy as np

CORNERS = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], np.float32) - 0.5
IDX = np.array([[0, 1, 2, 3], [5, 4, 7, 6], [4, 0, 3, 7], [1, 5, 6, 2], [4, 5, 1, 0], [3, 2, 6, 7]])
NORMALS = np.array([[0, 0, -1], [0, 0, 1], [-1, 0, 0], [1, 0, 0], [0, -1, 0], [0, 1, 0]], np.float32)


def boxes(centres, size, colours=None, rot_y=None):
    """Returns (Q (N*6,4,3), cols (N*6,3), nrm (N*6,3)) ready for render_shaded._draw_arrays."""
    c = np.asarray(centres, np.float32).reshape(-1, 3)
    n = len(c)
    s = np.asarray(size, np.float32)
    half = s if s.ndim == 2 else np.tile(s.reshape(1, -1), (n, 1))
    half = np.broadcast_to(half, (n, 3))
    col = np.asarray(colours if colours is not None else (140, 120, 90), np.float32)
    col = np.broadcast_to(col if col.ndim == 2 else col.reshape(1, -1), (n, 3))

    corners = CORNERS[None, :, :] * (half[:, None, :] * 2.0)             # (N,8,3)
    nrm = np.broadcast_to(NORMALS, (n, 6, 3)).copy()

    if rot_y is not None:
        a = np.asarray(rot_y, np.float32).reshape(-1)
        ca, sa = np.cos(a), np.sin(a)
        R = np.zeros((n, 3, 3), np.float32)
        R[:, 0, 0], R[:, 0, 2] = ca, -sa
        R[:, 1, 1] = 1.0
        R[:, 2, 0], R[:, 2, 2] = sa, ca
        # corners and normals take the SAME rotation; turning only the geometry leaves the lighting
        # in world space and every rotated instance looks lit from the wrong side
        corners = np.einsum("nij,nkj->nki", R, corners)
        nrm = np.einsum("nij,nkj->nki", R, nrm)

    corners = corners + c[:, None, :]
    Q = corners[:, IDX, :]                                              # (N,6,4,3)
    return (Q.reshape(-1, 4, 3).astype(np.float32),
            np.repeat(col, 6, axis=0).astype(np.float32),
            nrm.reshape(-1, 3).astype(np.float32))
