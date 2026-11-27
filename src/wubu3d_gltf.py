"""glTF 2.0 / GLB reader — static meshes, skins and animation clips.

Written against the spec rather than against a library, because the point of the project is
that a fresh clone can render an animated character with nothing but numpy installed. It
deliberately:

  * returns triangles in the same shape the OBJ loader returns, so callers do not care which
    format shipped the geometry;
  * resolves the node hierarchy and does linear-blend skinning on the CPU (four influences),
    which is what a rasteriser needs and what Blender would otherwise do for us;
  * samples animation clips by time, so a rigged GLB is an actor and not a statue.

Not implemented on purpose: Draco/meshopt compression, morph targets, sparse accessors and
texture decoding. Colour comes from `baseColorFactor`; a kit's texture atlas is its own
problem (see docs/GLTF.md).
"""
from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

COMP = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
        5125: np.uint32, 5126: np.float32}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}


class GltfError(RuntimeError):
    pass


def _rot(q) -> np.ndarray:
    x, y, z, w = q
    m = np.eye(4)
    m[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                 [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                 [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return m


def _trs(translation=None, rotation=None, scale=None) -> np.ndarray:
    T = np.eye(4)
    if translation is not None:
        T[:3, 3] = translation
    R = _rot(rotation) if rotation is not None else np.eye(4)
    S = np.eye(4)
    if scale is not None:
        S[0, 0], S[1, 1], S[2, 2] = scale
    return T @ R @ S


@dataclass
class Primitive:
    name: str
    positions: np.ndarray                 # (n, 3) mesh space
    indices: np.ndarray                   # (m, 3)
    color: tuple = (0.55, 0.52, 0.48)
    material: str = ""
    node: int = -1
    skin: int = -1
    joints: np.ndarray | None = None       # (n, 4)
    weights: np.ndarray | None = None      # (n, 4)


@dataclass
class Asset:
    path: Path
    nodes: list = field(default_factory=list)
    parent: dict = field(default_factory=dict)
    primitives: list = field(default_factory=list)
    animations: dict = field(default_factory=dict)   # name -> {(node, path): (times, values, interp)}
    skins: list = field(default_factory=list)        # [{"joints": [...], "ibm": (k,4,4)}]
    duration: float = 0.0

    def clip_names(self) -> list:
        return sorted(self.animations)

    def clip_length(self, clip: str) -> float:
        return float(self.animations.get(clip, {}).get("duration", 0.0))


# ─────────────────────────────────────────────────────────────────── container
def _read(path: Path):
    raw = path.read_bytes()
    if raw[:4] == b"glTF":
        _magic, version, length = struct.unpack("<III", raw[:12])
        if version != 2:
            raise GltfError(f"{path.name}: glTF {version} unsupported")
        off, js, bins = 12, None, []
        while off < length:
            clen, ctype = struct.unpack("<II", raw[off:off + 8])
            off += 8
            chunk = raw[off:off + clen]
            off += clen
            if ctype == 0x4E4F534A:
                js = json.loads(chunk.decode("utf-8"))
            elif ctype == 0x004E4942:
                bins.append(chunk)
        if js is None:
            raise GltfError(f"{path.name}: no JSON chunk")
        return js, bins, path.parent
    return json.loads(raw.decode("utf-8")), [], path.parent


def _buffers(js, bins, base: Path):
    out = []
    for i, b in enumerate(js.get("buffers", [])):
        if "uri" in b:
            uri = b["uri"]
            if uri.startswith("data:"):
                import base64
                out.append(base64.b64decode(uri.split(",", 1)[1]))
            else:
                out.append((base / uri).read_bytes())
        else:
            out.append(bins[i] if i < len(bins) else b"")
    return out


def _accessor(js, bufs, idx: int) -> np.ndarray:
    acc = js["accessors"][idx]
    n = NCOMP[acc["type"]]
    dtype = COMP[acc["componentType"]]
    count = acc["count"]
    if "bufferView" not in acc:
        return np.zeros((count, n), dtype=dtype)
    bv = js["bufferViews"][acc["bufferView"]]
    buf = bufs[bv["buffer"]]
    start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = bv.get("byteStride") or np.dtype(dtype).itemsize * n
    if stride == np.dtype(dtype).itemsize * n:
        arr = np.frombuffer(buf, dtype=dtype, count=count * n, offset=start).reshape(count, n)
    else:
        arr = np.empty((count, n), dtype=dtype)
        for i in range(count):
            arr[i] = np.frombuffer(buf, dtype=dtype, count=n, offset=start + i * stride)
    return np.array(arr)


# ─────────────────────────────────────────────────────────────────── loading
def load(path) -> Asset:
    path = Path(path)
    js, bins, base = _read(path)
    bufs = _buffers(js, bins, base)
    nodes = js.get("nodes", [])
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get("children", []):
            parent[c] = i
    asset = Asset(path=path, nodes=nodes, parent=parent)

    for a in js.get("animations", []):
        chans = {}
        for ch in a.get("channels", []):
            smp = a["samplers"][ch["sampler"]]
            key = (ch["target"]["node"], ch["target"]["path"])
            times = np.asarray(_accessor(js, bufs, smp["input"]), dtype=np.float64).ravel()
            vals = np.asarray(_accessor(js, bufs, smp["output"]), dtype=np.float64)
            chans[key] = (times, vals, smp.get("interpolation", "LINEAR"))
        dur = max((c[0][-1] for c in chans.values() if len(c[0])), default=0.0)
        asset.animations[a.get("name", f"clip{len(asset.animations)}")] = {
            "channels": chans, "duration": float(dur)}
        asset.duration = max(asset.duration, float(dur))

    for skin in js.get("skins", []):
        ibm = np.tile(np.eye(4), (len(skin["joints"]), 1, 1))
        if "inverseBindMatrices" in skin:
            raw = np.asarray(_accessor(js, bufs, skin["inverseBindMatrices"]), dtype=np.float64)
            ibm = raw.reshape(-1, 4, 4).transpose(0, 2, 1)      # glTF stores column-major
        asset.skins.append({"joints": list(skin["joints"]), "ibm": ibm})

    for mi, m in enumerate(js.get("meshes", [])):
        for pi, prim in enumerate(m.get("primitives", [])):
            attrs = prim["attributes"]
            pos = np.asarray(_accessor(js, bufs, attrs["POSITION"]), dtype=np.float64)
            if "indices" in prim:
                idx = np.asarray(_accessor(js, bufs, prim["indices"])).ravel().astype(np.int64)
            else:
                idx = np.arange(len(pos), dtype=np.int64)
            if len(idx) % 3:
                idx = idx[:len(idx) - len(idx) % 3]
            color, matname = (0.55, 0.52, 0.48), ""
            if "material" in prim:
                mtl = js["materials"][prim["material"]]
                matname = mtl.get("name", "")
                bcf = mtl.get("pbrMetallicRoughness", {}).get("baseColorFactor")
                if bcf:
                    color = (float(bcf[0]), float(bcf[1]), float(bcf[2]))
            joints = weights = None
            if "JOINTS_0" in attrs and "WEIGHTS_0" in attrs:
                joints = np.asarray(_accessor(js, bufs, attrs["JOINTS_0"])).astype(np.int64)
                weights = np.asarray(_accessor(js, bufs, attrs["WEIGHTS_0"]), dtype=np.float64)
                if weights.shape[1] < 4:
                    pad = 4 - weights.shape[1]
                    weights = np.pad(weights, ((0, 0), (0, pad)))
                    joints = np.pad(joints, ((0, 0), (0, pad)), constant_values=0)
            p = Primitive(name=m.get("name") or f"mesh{mi}" + (f"_{pi}" if pi else ""),
                          positions=pos, indices=idx.reshape(-1, 3),
                          color=color, material=matname, joints=joints, weights=weights)
            # find the node that carries this mesh
            for ni, n in enumerate(nodes):
                if n.get("mesh") == mi:
                    p.node = ni
                    p.skin = n.get("skin", -1)
                    break
            asset.primitives.append(p)
    return asset


# ─────────────────────────────────────────────────────────────────── posing
def _node_world(asset: Asset, idx: int, anim, t: float) -> np.ndarray:
    chain, cur = [], idx
    while cur is not None:
        chain.append(cur)
        cur = asset.parent.get(cur)
    m = np.eye(4)
    for i in reversed(chain):
        node = asset.nodes[i]
        if "matrix" in node:
            local = np.array(node["matrix"], dtype=np.float64).reshape(4, 4).T
        else:
            tr, ro, sc = node.get("translation"), node.get("rotation"), node.get("scale")
            if anim is not None:
                ch = anim["channels"]
                if (i, "translation") in ch:
                    tr = _sample(*ch[(i, "translation")], t)
                if (i, "rotation") in ch:
                    ro = _sample(*ch[(i, "rotation")], t)
                if (i, "scale") in ch:
                    sc = _sample(*ch[(i, "scale")], t)
            local = _trs(tr, ro, sc)
        m = m @ local
    return m


def _sample(times, values, interp, t):
    if len(times) == 0:
        return values[0]
    if t <= times[0]:
        return values[0]
    if t >= times[-1]:
        return values[-1]
    i = int(np.searchsorted(times, t) - 1)
    i = max(0, min(i, len(times) - 2))
    if interp == "STEP":
        return values[i]
    if interp == "CUBICSPLINE":
        v0, v1 = values[3 * i + 1], values[3 * (i + 1) + 1]
    else:
        v0, v1 = values[i], values[i + 1]
    span = times[i + 1] - times[i]
    u = 0.0 if span <= 0 else (t - times[i]) / span
    if np.ndim(v0) == 1 and len(v0) == 4:            # quaternion: slerp, shortest arc
        a = v0 / (np.linalg.norm(v0) or 1.0)
        b = v1 / (np.linalg.norm(v1) or 1.0)
        d = float(np.dot(a, b))
        if d < 0:
            b, d = -b, -d
        if d > 0.9995:
            q = a + u * (b - a)
            return q / (np.linalg.norm(q) or 1.0)
        th = np.arccos(np.clip(d, -1.0, 1.0))
        return (np.sin((1 - u) * th) * a + np.sin(u * th) * b) / np.sin(th)
    return v0 + (v1 - v0) * u


def pose(asset: Asset, clip: str | None = None, t: float = 0.0, scale: float = 1.0,
         ground: bool = False, to_z_up: bool = True):
    """[(name, verts(n,4) rgba-float, tris(m,3))] in the asset's own space at clip time t."""
    anim = asset.animations.get(clip) if clip else None
    world = [_node_world(asset, i, None, 0.0) for i in range(len(asset.nodes))] if anim is None else None
    out = []
    for p in asset.primitives:
        pos = p.positions
        if p.skin >= 0 and p.joints is not None:
            skin = asset.skins[p.skin]
            jw = np.stack([_node_world(asset, j, anim, t) for j in skin["joints"]])
            # glTF: jointMatrix = inverse(global(meshNode)) * global(joint) * inverseBind
            # dropping the mesh-node term leaves the mesh's own scale applied twice, which
            # halves the body and doubles the head — visible immediately, and now fixed
            inv_mesh = np.linalg.inv(_node_world(asset, p.node, None, 0.0)) if p.node >= 0 else np.eye(4)
            jm = inv_mesh @ (jw @ skin["ibm"])          # (k,4,4)
            h = np.hstack([pos, np.ones((len(pos), 1))])
            acc = np.zeros((len(pos), 4))
            for k in range(4):
                w = p.weights[:, k:k + 1]
                if not np.any(w):
                    continue
                ji = np.clip(p.joints[:, k], 0, len(jm) - 1)
                acc += np.einsum("nij,nj->ni", jm[ji], h) * w
            pos = acc[:, :3] / np.where(np.abs(acc[:, 3:4]) < 1e-9, 1.0, acc[:, 3:4])
        elif p.node >= 0:
            m = world[p.node] if world is not None else _node_world(asset, p.node, anim, t)
            pos = (pos @ m[:3, :3].T) + m[:3, 3]
        if to_z_up:                      # glTF is Y-up, the film graph is Z-up
            pos = np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], axis=1)
        verts = np.hstack([pos * scale, np.full((len(pos), 1), 255.0)])
        out.append((p.name, verts, p.indices))
    if ground and out:
        low = min(float(v[:, 2].min()) for _, v, _ in out)
        for _, v, _ in out:
            v[:, 2] -= low
    return out


def bounds(asset: Asset, clip: str | None = None, t: float = 0.0) -> tuple:
    vs = pose(asset, clip, t)
    pts = np.vstack([v[:, :3] for _, v, _ in vs]) if vs else np.zeros((1, 3))
    return pts.min(axis=0), pts.max(axis=0)
