"""wubu3d_heat — bone weights by heat diffusion, after Baran & Popović (SIGGRAPH 2007).

wubu3d_skin paints weights from distance to a bone SEGMENT. It is cheap and it is what most engines
default to, but it is a proximity proxy: two bones equidistant from a vertex get the same weight
even when one is buried inside the body and the other is on the surface.

Baran & Popović attach skin by solving the heat equation over the MESH, not through space:

    each bone seeds the vertices it is the nearest bone to
    those seeds are held at 1, every other bone's seeds at 0
    the weights diffuse along mesh edges until they settle

The result respects the surface: a vertex is influenced by bones whose seed region it is connected
to across the mesh, so a bone on the far side of an arm cannot grab the near side.

Reference: Baran, I. & Popović, J., "Automatic Rigging and Animation of 3D Characters",
ACM SIGGRAPH 2007 — skin attachment by constrained diffusion of bone weights over the mesh.

Pure python, no numpy, matching the rest of the box tree.
"""

import math

MAX_INFLUENCES = 4


def weld(points, q):
    """Merge coincident vertices; meshes here build faces independently, so nothing is shared."""
    uniq, index, mapping = [], {}, []
    for p in points:
        key = (round(p[0] / q), round(p[1] / q), round(p[2] / q))
        i = index.get(key)
        if i is None:
            i = len(uniq)
            index[key] = i
            uniq.append(p)
        mapping.append(i)
    return uniq, mapping


def graph(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        if a != b:
            adj[a].add(b)
            adj[b].add(a)
    return [tuple(sorted(s)) for s in adj]


def mesh_edges(faces, mapping):
    """Edges of each quad, in welded index space."""
    out = set()
    for item in faces:
        idx = [mapping[i] for i in range(0, 0)]  # placeholder, replaced below
    return out


def edges_from_faces(faces, mapping, per_face, offset=0):
    out = set()
    k = 0
    for item in faces:
        n = per_face
        ids = [mapping[k + j] for j in range(n)]
        k += n
        for j in range(n):
            a, b = ids[j], ids[(j + 1) % n]
            out.add((a, b) if a < b else (b, a))
    return out


def seg_dist(p, a, b):
    ax, ay, az = a
    dx, dy, dz = b[0] - ax, b[1] - ay, b[2] - az
    L2 = dx * dx + dy * dy + dz * dz
    if L2 < 1e-12:
        return math.dist(p, a)
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy + (p[2] - az) * dz) / L2
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return math.dist(p, (ax + dx * t, ay + dy * t, az + dz * t))


def heat_weights(points, faces, bones, per_face=4, iterations=90, rel=0.35):
    """Weights by constrained diffusion over the mesh.

    points: raw (unwelded) vertex list, in face order.
    faces: list of quads, each contributing per_face vertices to `points` in order.
    bones: {name: (head, tail)}.
    """
    V = [(float(p[0]), float(p[1]), float(p[2])) for p in points]
    lo = [min(p[k] for p in V) for k in range(3)]
    hi = [max(p[k] for p in V) for k in range(3)]
    diag = math.dist(lo, hi) or 1.0
    U, mapping = weld(V, diag / 60.0)

    edges = edges_from_faces(faces, mapping, per_face)
    adj = graph(len(U), edges)
    names = list(bones)

    # nearest bone per welded vertex, and a seed region for each bone
    nearest = []
    dists = []
    for p in U:
        d = [seg_dist(p, bones[n][0], bones[n][1]) for n in names]
        dists.append(d)
        nearest.append(d.index(min(d)))

    # a vertex is a seed for its nearest bone when it is close to it compared with the body size.
    # Seeding everything lets one bone claim the whole mesh; seeding nothing leaves no boundary.
    seeds = {n: set() for n in names}
    for i, p in enumerate(U):
        d = sorted(dists[i])
        # seed only where one bone CLEARLY owns the vertex (it is less than 60% as far as any
        # other). Seeding everything within a radius fixed every vertex and the diffusion had
        # nothing left to solve, which is why the first version produced hard 100/0 weights.
        if d[0] <= diag * rel and d[0] <= 0.6 * max(d[1], 1e-6):
            seeds[names[nearest[i]]].add(i)
    if not any(seeds.values()):
        for i, p in enumerate(U):
            seeds[names[nearest[i]]].add(i)

    W = [[0.0] * len(names) for _ in range(len(U))]
    for bi, n in enumerate(names):
        fixed = {}
        for k in names:
            if k == n:
                for i in seeds[k]:
                    fixed[i] = 1.0
            else:
                for i in seeds[k]:
                    fixed[i] = 0.0
        cur = [fixed.get(i, 0.5) for i in range(len(U))]
        for i, v in fixed.items():
            cur[i] = v
        # Gauss-Seidel: each free vertex relaxes to the mean of its neighbours, i.e. the discrete
        # Laplace equation with Dirichlet boundaries
        for _ in range(iterations):
            for i in range(len(U)):
                if i in fixed or not adj[i]:
                    continue
                s = 0.0
                for j in adj[i]:
                    s += cur[j]
                cur[i] = s / len(adj[i])
        for i in range(len(U)):
            W[i][bi] = cur[i]

    # back to raw vertex order, normalised, capped
    out = []
    for raw_i in range(len(V)):
        row = list(W[mapping[raw_i]])
        s = sum(row)
        if s <= 1e-9:
            # isolated vertex: fall back to proximity
            d = dists[mapping[raw_i]]
            row = [1.0 if k == d.index(min(d)) else 0.0 for k in range(len(names))]
            s = 1.0
        row = [v / s for v in row]
        pairs = sorted(enumerate(row), key=lambda kv: -kv[1])[:MAX_INFLUENCES]
        cap = [0.0] * len(row)
        tot = sum(v for _i, v in pairs) or 1.0
        for i, v in pairs:
            cap[i] = v / tot
        out.append(cap)
    return names, out, len(U), len(edges)
