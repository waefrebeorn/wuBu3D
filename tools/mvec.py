"""mvec — motion vectors with no second render pass.

Every pixel's world position is reconstructible from the depth buffer plus the camera, so reprojecting
that position through the previous frame's camera gives the vector directly. This is the last of the
four passes a compositor expects, and it costs one numpy operation over data we already write.

    world  = eye + (right*dx + up*dy + fwd) * z         # z is view depth, not distance
    motion = project_prev(world) - screen

The classic error is the sign of `dy`: screen y grows downward and the camera's `up` axis does not, so
the y term is negated against x. Get it wrong and every vector points the wrong way vertically while
horizontal motion looks perfect, which reads as "mostly working".
"""

import numpy as np


def unproject(zb, cam):
    """zb (h,w) view depth -> world positions (h,w,3)."""
    zb = np.asarray(zb, np.float32)
    h, w = zb.shape
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (xs + 0.5 - cam.cx) / cam.f
    dy = -(ys + 0.5 - cam.cy) / cam.f
    r, u, f = cam.M[0], cam.M[1], cam.M[2]
    d = r[None, None, :] * dx[..., None] + u[None, None, :] * dy[..., None] + f[None, None, :]
    return cam.eye[None, None, :] + d * zb[..., None]


def project(world, cam):
    q = (world - cam.eye[None, None, :]) @ cam.M.T
    z = np.clip(q[..., 2], 0.05, None)
    return np.stack([cam.cx + q[..., 0] * cam.f / z, cam.cy - q[..., 1] * cam.f / z], -1), z


def motion_vectors(zb, cam_now, cam_prev, scale=1.0):
    """Screen-space motion in pixels, current frame back to the previous one. Sky gets zero."""
    zb = np.asarray(zb, np.float32)
    valid = np.isfinite(zb) & (zb > 0.05)
    z = np.where(valid, zb, 1.0).astype(np.float32)
    world = unproject(z, cam_now)
    prev_screen, _ = project(world, cam_prev)
    h, w = zb.shape
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    now = np.stack([xs + 0.5, ys + 0.5], -1)
    mv = (prev_screen - now) * float(scale)
    mv[~valid] = 0.0
    return mv.astype(np.float32), valid


def stats(mv, valid):
    m = np.abs(mv[valid])
    if not valid.any():
        return {"frac_valid": 0.0, "mean_px": 0.0, "p99_px": 0.0, "max_px": 0.0}
    return {"frac_valid": float(valid.mean()), "mean_px": float(m.mean()),
            "p99_px": float(np.percentile(m, 99)), "max_px": float(m.max())}


def resample(mv, t):
    """Motion at sub-frame time t: a camera pan is linear over the exposure, so the vector scales."""
    return mv * float(t)
