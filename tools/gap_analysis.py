"""gap_analysis — what the market sells that wubu3d cannot do, counted from the census.

This is the useful half of a census: not "here are 438 products" but "here are the 20 operations they
collectively advertise, how many of them sell each one, and which of those we have not built".

Every gap row carries example products with their URLs, so the claim "hair grooms are a category" is
checkable rather than asserted.

    python3 tools/gap_analysis.py     ->  docs/WUBU3D_GAPS.md
"""

import json
import os
import re
import time

BOX = "/opt/data/work/wubu3d"
CENSUS = os.path.join(BOX, "specs/gumroad_tools.json")
HOPS = os.path.join(BOX, "specs/gumroad_hops.json")
DESC = "/opt/data/cache/scratch/gumroad_desc_all.json"
OUT = os.path.join(BOX, "docs/WUBU3D_GAPS.md")

# capability -> (keywords that name it, what we have, evidence in our tree)
CAPS = [
    ("skin & subsurface scattering", ["subsurface", " sss", "skin shader"], "none",
     "our characters are opaque lambert+specular"),
    ("translucency / transmission", ["transmission", "translucen", "glass shader", "refraction"], "none",
     "no transmission path at all"),
    ("texture sampling", ["texture", "pbr", "albedo", "orm"], "none",
     "src/shade.c has no sampler; every face is one flat colour"),
    ("normal mapping", ["normal map", "tangent space"], "none", "no tangent space in the mesh path"),
    ("cast shadows", ["shadow map", "cascade", "soft shadow", "pcf"], "none",
     "a contact ellipse stands in for a real shadow"),
    ("ambient occlusion", ["ssao", "ambient occlusion", "ao bake"], "partial",
     "ground-contact darkening only, not occlusion between parts"),
    ("bloom / glare", ["bloom", "glare", "lens flare"], "none", "a threshold blur exists but is unused"),
    ("depth of field", ["depth of field", "dof", "bokeh"], "done", "render_shaded.dof, z-buffer CoC"),
    ("motion blur", ["motion blur", "velocity buffer"], "none", "no velocity pass"),
    ("volumetrics / fog", ["volumetric", "god ray", "fog", "atmosphere"], "partial",
     "depth fog in render_blocky only"),
    ("hair / fur grooming", ["hair card", "groom", "fur"], "none", "hair is four boxes"),
    ("cloth simulation", ["cloth sim", "cloth physics", "garment"], "none", "no simulation of any kind"),
    ("soft body / jiggle", ["jiggle", "soft body", "squash", "stretch"], "none",
     "the walk bobs a whole body, no secondary motion"),
    ("ragdoll / physics", ["ragdoll", "physics", "constraint"], "none", "no solver"),
    ("retargeting", ["retarget", "motion matching"], "none",
     "poses only apply to our own joint names"),
    ("auto weighting", ["auto weight", "weight paint", "heat map"], "done", "src/rig.c, Laplacian smoothing"),
    ("auto rig", ["auto rig", "autorig", "skeleton fit"], "done", "src/rig.c wubu_autorig, 0.031 mean error"),
    ("IK solvers", ["ik solver", "two bone", "fabrik", "ik chain"], "done", "src/rig.c, end->target 0.000000"),
    ("retopology / remesh", ["retopolog", "remesh", "decimate"], "none", "no mesh editing at all"),
    ("UV unwrap / atlas", ["uv unwrap", "atlas", "uv pack"], "none", "meshes arrive with UVs, we never make them"),
    ("LOD generation", ["lod", "decimat", "impostor"], "none", "one resolution, always"),
    ("occlusion culling", ["occlusion cull", "pv", "visibility"], "none", "depth test only"),
    ("instancing / batching", ["gpu instancing", "batching", "draw call"], "none",
     "every face is pushed individually"),
    ("procedural placement", ["procedural", "scatter", "foliage"], "none",
     "props are placed by hand in the shot list"),
    ("tileable material authoring", ["tileable", "seamless", "substance"], "none", "no material system"),
    ("decal projection", ["decal", "projection"], "partial", "world-space flat decals for footprints"),
    ("node graph / shader authoring", ["shader graph", "node editor", "visual scripting"], "none",
     "shaders are hand-written C"),
    ("particle / VFX", ["particle", "vfx", "emitter"], "none", "no particles"),
    ("navmesh / pathfinding", ["navmesh", "pathfind", "ai "], "none", "no agents"),
    ("motion capture cleanup", ["mocap", "motion capture", "cleanup"], "none", "no mocap path"),
]


def main():
    census = json.load(open(CENSUS))
    hops = json.load(open(HOPS))["hops"] if os.path.exists(HOPS) else []
    desc = json.load(open(DESC)) if os.path.exists(DESC) else {}
    prods = census["tools"] + hops

    hits = {name: [] for name, _, _, _ in CAPS}
    for p in prods:
        text = ((p.get("name") or "") + " " + (desc.get(p["url"]) or "")).lower()
        for name, keys, _, _ in CAPS:
            if any(k in text for k in keys):
                hits[name].append(p)

    L, A = [], None
    A = L.append
    A("# wubu3d gaps, counted from the market\n")
    A("Generated from the census: %d products from search plus %d more found by seller and keyword "
      "hops (see `tools/lilypad.py`), scraped %s.\n" % (len(census["tools"]), len(hops),
                                                        time.strftime("%Y-%m-%d")))
    A("Each row counts how many products advertise the operation, what we have, and three examples "
      "with links. A row we have marked `done` also names the file and the measured number.\n")
    A("| operation | products selling it | wubu3d | evidence | examples |")
    A("|---|---|---|---|---|")
    for name, keys, have, why in CAPS:
        ex = hits[name][:3]
        exs = ", ".join("[%s](%s)" % (e["name"][:34].replace("|", "/"), e["url"]) for e in ex) or "--"
        A("| %s | %d | %s | %s | %s |" % (name, len(hits[name]), have, why, exs))

    gaps = [n for n, _, have, _ in CAPS if have == "none"]
    done = [n for n, _, have, _ in CAPS if have == "done"]
    A("\n**%d operations missing, %d partial, %d done.**\n" % (len(gaps),
                                                              len([1 for _, _, h, _ in CAPS if h == "partial"]),
                                                              len(done)))
    A("Ordered by how many products sell it, the top five missing are:\n")
    top = sorted(((len(hits[n]), n) for n in gaps), reverse=True)[:5]
    for n, name in top:
        A("- **%s** — %d products" % (name, n))
    open(OUT, "w").write("\n".join(L) + "\n")
    print("wrote %s (%d bytes)" % (OUT, os.path.getsize(OUT)))
    for n, name in top:
        print("  %-34s %3d products" % (name, n))


if __name__ == "__main__":
    main()
