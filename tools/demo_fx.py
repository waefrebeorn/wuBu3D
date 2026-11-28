"""demo_fx — fill the three ranked gaps in one shot: shadows, particles, colour management.

Each stage adds one thing and reports what it changed:

    base            what we had: bytes out of the rasteriser, clipped at 255
    +shadows        shadow map from a key light, floor darkened where the character occludes it
    +particles      a C particle field, additive splats with a depth test
    +post           linear light -> ACES -> bloom -> god rays
    +motion blur    three subframes accumulated along a camera drift
"""

import ctypes

import numpy as np
from PIL import Image

import blocky as B
import cast_blocky as CB
import render_shaded as RS
import r15

_F, _I, _P = ctypes.c_float, ctypes.c_int, ctypes.c_void_p

fx = ctypes.CDLL("/opt/data/work/wubu3d/libfx.so")
fx.wubu_to_linear.argtypes = [_P, _P, _I, _F]
fx.wubu_tonemap.argtypes = [_P, _I, _F, _I]
fx.wubu_bloom.argtypes = [_P, _I, _I, _F, _F, _I]
fx.wubu_rays.argtypes = [_P, _I, _I, _F, _F, _F, _F, _I, _F]
fx.wubu_to_bytes.argtypes = [_P, _P, _I]

sh = ctypes.CDLL("/opt/data/work/wubu3d/libshadow.so")
sh.wubu_shadowmap.argtypes = [_P, _I, _P, _P, _I, _F, _P]
sh.wubu_shadow_floor.argtypes = [_P, _I, _P, _P, _F, _P, _P, _F, _I, _I, _F, _F, _P]

pt = ctypes.CDLL("/opt/data/work/wubu3d/libparticles.so")
pt.wubu_psys_step.argtypes = [_P, _I, _F, _F, _F, _F, _F, _F, _F, _F, _I]
pt.wubu_splat.argtypes = [_P, _P, _I, _I, _P, _I]

W, H = 420, 700
LIGHT_EYE = np.array([4.6, 7.2, 4.1], np.float32)
LIGHT_TGT = np.array([0.0, 0.0, 0.0], np.float32)
CAM_EYE = np.array([0.55, 0.75, 2.05], np.float32)
CAM_TGT = np.array([0.05, 0.48, 0.0], np.float32)


def scene():
    f, piv = r15.build({"RUpperArm": (-24, 0, -6), "Head": (0, -10, 0)}, H=1.0,
                       hair=(30, 40, 74), shirt=(96, 92, 132))
    f += [(q, c, o) for q, c, o in CB.box(0, -0.05, 0.3, 7.0, 0.1, 6.0, (104, 88, 62))]
    f += [(q, c, o) for q, c, o in CB.box(-1.5, 1.1, -1.3, 1.4, 2.2, 0.25, (86, 74, 58))]
    return f


def render(eye=None, tgt=None, w=W, h=H):
    eye = CAM_EYE + (np.array([0.0, 0.0, 0.0], np.float32) if eye is None else eye)
    tgt = CAM_TGT if tgt is None else tgt
    sky = CB.sky(top=(70, 58, 44), bottom=(96, 78, 56), z=-40, span_y=28, span_x=70, y0=-6)
    return RS.aa(scene(), tuple(eye), tuple(tgt), w, h, ss=2, fov=46,
                 flat=[(q[:4], c) for q, c, o in sky], bg=(96, 78, 56),
                 lights=[tuple(LIGHT_EYE) + (2.8,), (-1.8, 1.2, 1.6, 3.2)],
                 ambient=0.42, gain=0.42, rim=0.10), eye, tgt


def tris_of(faces):
    out = []
    for q, c, o in faces:
        for idx in ((0, 1, 2), (0, 2, 3)):
            for i in idx:
                out.extend(q[i])
    return np.asarray(out, np.float32)


def main():
    base, eye, tgt = render()
    faces = scene()

    # ---- shadow map from the key light, applied to the floor
    D = 512
    tri = tris_of(faces)
    dep = np.full(D * D, 1e30, np.float32)
    sh.wubu_shadowmap(tri.ctypes.data_as(_P), len(tri) // 9,
                      LIGHT_EYE.ctypes.data_as(_P), LIGHT_TGT.ctypes.data_as(_P), D, 60.0,
                      dep.ctypes.data_as(_P))
    fac = np.ones((H, W), np.float32)
    sh.wubu_shadow_floor(dep.ctypes.data_as(_P), D, LIGHT_EYE.ctypes.data_as(_P),
                         LIGHT_TGT.ctypes.data_as(_P), 60.0,
                         eye.astype(np.float32).ctypes.data_as(_P),
                         np.asarray(tgt, np.float32).ctypes.data_as(_P), 46.0,
                         W, H, 0.0, 0.012, fac.ctypes.data_as(_P))
    shaded = (fac < 0.9).mean()
    b = np.asarray(base.convert("RGB"), np.float32)
    b_sh = b * (0.45 + 0.55 * fac[..., None])
    sh_img = Image.fromarray(np.clip(b_sh, 0, 255).astype(np.uint8))
    print("shadow: %.1f%% of floor pixels occluded, mean floor factor %.2f"
          % (100 * shaded, float(fac.mean())))

    # ---- particles: a hot burst at the character's feet
    N = 900
    st = np.zeros((N, 9), np.float32)
    rng = np.random.default_rng(3)
    st[:, 0] = rng.normal(0.0, 0.12, N)
    st[:, 1] = 0.05
    st[:, 2] = rng.normal(0.0, 0.12, N)
    st[:, 3] = rng.normal(0.0, 0.55, N)
    st[:, 4] = rng.uniform(0.6, 1.9, N)
    st[:, 5] = rng.normal(0.0, 0.55, N)
    st[:, 7] = rng.uniform(0.5, 1.3, N)
    st[:, 8] = rng.uniform(0.6, 1.6, N)
    for _ in range(14):
        pt.wubu_psys_step(st.ctypes.data_as(_P), N, 0.05, 0.0, -8.5, 0.0, 0.9, 0.2, 0.0, 3.0, 11)
    alive = st[st[:, 6] < st[:, 7]]
    proj = B.Cam(tuple(eye), tuple(tgt), fov=46, w=W, h=H)
    scr = []
    for q in alive:
        pr, zz = proj.project(np.array([[q[0], q[1], q[2]]] * 4, np.float32))
        z = float(zz[0])
        if z <= 0.1:
            continue
        px = float(pr[0][0])
        py = float(pr[0][1])
        rad = max(1.0, 90.0 * float(q[8]) / z)
        life = 1.0 - float(q[6] / max(1e-3, q[7]))
        scr.append((px, py, z, rad, 1.0 * life, 0.45 * life, 0.10 * life))
    s = np.asarray(scr, np.float32)
    rgb = np.asarray(sh_img, np.uint8).copy()
    zb = np.full((H, W), np.inf, np.float32)
    drawn = pt.wubu_splat(rgb.ctypes.data_as(_P), zb.ctypes.data_as(_P), W, H,
                          s.ctypes.data_as(_P), len(s)) if len(s) else 0
    print("particles: %d alive, %d splatted, %d blended pixels" % (len(alive), len(s), drawn))
    part_img = Image.fromarray(rgb)

    # ---- post: linear -> ACES -> bloom -> rays
    lin = np.zeros((H, W, 3), np.float32)
    fx.wubu_to_linear(rgb.ctypes.data_as(_P), lin.ctypes.data_as(_P), H * W * 3, 1.45)
    fx.wubu_bloom(lin.ctypes.data_as(_P), W, H, 0.95, 0.40, 7)
    fx.wubu_rays(lin.ctypes.data_as(_P), W, H, 0.62, 0.18, 0.7, 0.35, 32, 0.94)
    fx.wubu_tonemap(lin.ctypes.data_as(_P), H * W, 0.95, 1)
    out = np.zeros((H, W, 3), np.uint8)
    fx.wubu_to_bytes(lin.ctypes.data_as(_P), out.ctypes.data_as(_P), H * W * 3)
    post = Image.fromarray(out)
    clip_before = float((np.asarray(part_img) >= 254).mean())
    clip_after = float((out >= 254).mean())
    print("post: clipped pixels %.3f%% -> %.3f%% (ACES shoulder), mean luma %.1f -> %.1f"
          % (100 * clip_before, 100 * clip_after,
             np.asarray(part_img, np.float32).mean(), out.astype(np.float32).mean()))

    # ---- motion blur: three subframes along a drift
    acc = None
    for i in range(3):
        dx = (i - 1) * 0.012
        im, e2, t2 = render(eye=CAM_EYE + np.array([dx, 0, 0], np.float32),
                            tgt=CAM_TGT + np.array([dx * 0.4, 0, 0], np.float32))
        a = np.asarray(im.convert("RGB"), np.float32)
        acc = a / 3.0 if acc is None else acc + a / 3.0
    mb = Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8))

    sheet = Image.new("RGB", (W * 3, H), (18, 18, 20))
    for i, im in enumerate((sh_img, part_img, post)):
        sheet.paste(im.convert("RGB"), (i * W, 0))
    sheet.save("/opt/data/cache/scratch/fx_sheet.png")
    mb.save("/opt/data/cache/scratch/fx_mblur.png")
    print("wrote fx_sheet.png and fx_mblur.png")


if __name__ == "__main__":
    main()
