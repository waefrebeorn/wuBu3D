"""demo_fog_crowd — height fog in the shader, and a crowd that follows a flow field.

Fog must separate depth: far geometry loses contrast toward the fog colour while near geometry does
not. Measured as mean separation between a near band and a far band, before and after.

A flow field is the cheap answer to "two hundred agents, one goal": one distance field, computed once,
gives every cell a direction. The metric is arrival rate and, more importantly, wall penetrations —
a crowd that arrives by walking through the wall has not solved anything.
"""

import numpy as np
from PIL import Image

import cast_blocky as CB
import render_shaded as RS


def test_fog():
    f = []
    f += [(q, c, o) for q, c, o in CB.box(0, -0.05, -6.0, 3.2, 0.1, 9.0, (96, 88, 78))]
    for k in range(9):
        z = -1.0 - 1.1 * k
        f += [(q, c, o) for q, c, o in CB.box(-1.15 + 0.55 * (k % 3), 0.9, z, 0.11, 1.8, 0.11,
                                             (170, 150, 110))]
        f += [(q, c, o) for q, c, o in CB.box(1.15 - 0.55 * (k % 3), 0.9, z, 0.11, 1.8, 0.11,
                                             (150, 134, 100))]
    kw = dict(ss=1, fov=50, flat=[], bg=(22, 22, 28), lights=[(1.0, 3.0, 2.0, 7.0)],
              ambient=0.36, gain=0.5, rim=0.0)
    eye, tgt = (0.0, 1.1, 2.0), (0.0, 0.9, -6.0)

    RS.fog(0.0)
    a = np.asarray(RS.aa(f, eye, tgt, 300, 420, **kw).convert("L"), np.float32)
    RS.fog(0.11, 0.55)
    b = np.asarray(RS.aa(f, eye, tgt, 300, 420, **kw).convert("L"), np.float32)
    RS.fog(0.0)

    # select by DEPTH, not by image band: the top of the frame is not the far end of a pitched camera,
    # and band-based bands made the fog look like it was brightening the near geometry
    z = np.array(RS._LAST_ZB, np.float32)
    ok = np.isfinite(z) & (z > 0.1)
    far = ok & (z > 4.5)
    near = ok & (z < 3.6)
    if near.sum() < 50:                      # nothing that close in this corridor
        near = ok & (z < 4.2)
    print("fog: near (z<2.8) mean %.1f->%.1f, far (z>4.5) mean %.1f->%.1f"
          % (a[near].mean(), b[near].mean(), a[far].mean(), b[far].mean()))
    ns = (a[near].std(), b[near].std()) if near.sum() else (float("nan"), float("nan"))
    print("     far contrast std %.1f -> %.1f (fog must reduce it), near std %.1f -> %.1f"
          % (a[far].std(), b[far].std(), ns[0], ns[1]))
    sheet = Image.new("L", (600, 420))
    sheet.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))
    sheet.paste(Image.fromarray(b.astype(np.uint8)), (300, 0))
    sheet.save("/opt/data/cache/scratch/fog_sheet.png")


def test_crowd(n=200, steps=260, seed=4):
    """Grid world, one goal, BFS distance field, agents follow its gradient."""
    W, H = 64, 40
    solid = np.zeros((H, W), bool)
    solid[0, :] = solid[-1, :] = solid[:, 0] = solid[:, -1] = True
    for y in range(6, 34):
        if y not in (18, 19, 20):
            solid[y, 20] = True
    for x in range(30, 50):
        if x not in (38, 39):
            solid[12, x] = True
    goal = (52, 20)

    dist = np.full((H, W), 1e9, np.float32)
    if solid[goal[1], goal[0]]:
        goal = (52, 21)
    dist[goal[1], goal[0]] = 0
    cur = [(goal[0], goal[1])]
    while cur:
        nxt = []
        for (x, y) in cur:
            d = dist[y, x] + 1
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and not solid[ny, nx] and dist[ny, nx] > d:
                    dist[ny, nx] = d
                    nxt.append((nx, ny))
        cur = nxt

    rng = np.random.default_rng(seed)
    free = np.argwhere(~solid)
    pick = free[rng.choice(len(free), n, replace=False)]
    px = pick[:, 1].astype(np.float32) + 0.5
    py = pick[:, 0].astype(np.float32) + 0.5

    arrived = np.zeros(n, bool)
    wall_hits = 0
    for _ in range(steps):
        ix = np.clip(px.astype(np.int32), 0, W - 1)
        iy = np.clip(py.astype(np.int32), 0, H - 1)
        best_d = dist[iy, ix]
        bx, by = np.zeros(n, np.float32), np.zeros(n, np.float32)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx = np.clip(ix + dx, 0, W - 1)
            ny = np.clip(iy + dy, 0, H - 1)
            better = dist[ny, nx] < best_d
            bx[better] += dx
            by[better] += dy
        m = np.hypot(bx, by)
        live = ~arrived
        step = 0.35
        px = np.where(live, px + np.where(m > 0, bx / np.maximum(m, 1e-6), 0) * step, px)
        py = np.where(live, py + np.where(m > 0, by / np.maximum(m, 1e-6), 0) * step, py)
        # collision: anything that lands inside a solid cell is pushed back out and counted
        cx = np.clip(px.astype(np.int32), 0, W - 1)
        cy = np.clip(py.astype(np.int32), 0, H - 1)
        bad = solid[cy, cx] & live
        wall_hits += int(bad.sum())
        px = np.where(bad, np.floor(px) + 0.5, px)
        py = np.where(bad, np.floor(py) + 0.5, py)
        d = np.hypot(px - (goal[0] + 0.5), py - (goal[1] + 0.5))
        arrived |= d < 1.2

    print("crowd: %d agents, %d steps: %.1f%% arrived, %d wall contacts, mean dist to goal %.2f cells"
          % (n, steps, 100 * arrived.mean(), wall_hits,
             float(np.hypot(px - goal[0] - 0.5, py - goal[1] - 0.5).mean())))


def main():
    test_fog()
    test_crowd()


if __name__ == "__main__":
    main()
