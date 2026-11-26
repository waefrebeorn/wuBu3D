"""Clay body — one continuous surface instead of stacked primitives.

Slermed idea from the sculpting-agent post: a body is built from blobs of clay that merge,
then worked, not from boxes glued together. Blender's metaballs give exactly that merge for
free — every element fuses into one skin, so there are no seams at shoulder, hip or neck,
and a negative element carves an opening instead of hiding the head behind a slab.

Authoring is still ours: a body plan in metres, converted to a mesh, rigged with the same
bones as before.
"""
import math
import bpy


def ell(mb, co, r, scale=(1, 1, 1), negative=False, stiff=2.0):
    e = mb.elements.new()
    e.type = 'ELLIPSOID'
    e.co = co
    e.radius = r
    e.size_x, e.size_y, e.size_z = (r * scale[0] * 1.0, r * scale[1] * 1.0, r * scale[2] * 1.0)
    e.stiffness = stiff
    e.use_negative = negative
    return e


def build_clay(name="Clay", resolution=0.012, hood=True):
    mb = bpy.data.metaballs.new(name)
    mb.resolution = resolution
    mb.render_resolution = resolution
    ob = bpy.data.objects.new(name, mb)
    bpy.context.scene.collection.objects.link(ob)

    # ── torso: chest, ribs, abdomen, pelvis, each flattened front-to-back
    ell(mb, (0, 0.000, 1.300), 0.105, (1.55, 1.00, 1.15))     # chest
    ell(mb, (0, 0.005, 1.180), 0.100, (1.50, 0.95, 1.10))     # ribs
    ell(mb, (0, 0.005, 1.060), 0.095, (1.35, 0.92, 1.05))     # waist
    ell(mb, (0, 0.000, 0.955), 0.100, (1.42, 0.95, 0.95))     # pelvis

    # ── neck and head
    ell(mb, (0, 0.005, 1.470), 0.048, (1.00, 1.00, 1.30))     # neck
    ell(mb, (0, 0.008, 1.610), 0.088, (1.02, 1.10, 1.22))     # skull
    ell(mb, (0, 0.030, 1.556), 0.070, (0.95, 1.00, 0.78))     # jaw / chin
    ell(mb, (0, 0.086, 1.612), 0.030, (0.72, 0.85, 0.90))     # brow / nose bridge
    ell(mb, (0, 0.098, 1.588), 0.017, (0.85, 1.1, 0.9))       # nose

    # ── arms
    for sgn in (1.0, -1.0):
        ell(mb, (sgn * 0.175, 0.000, 1.345), 0.062, (1.0, 1.0, 1.05))   # deltoid
        ell(mb, (sgn * 0.196, 0.004, 1.235), 0.050, (1.0, 1.0, 1.75))   # upper arm
        ell(mb, (sgn * 0.212, 0.010, 1.140), 0.044, (1.0, 1.0, 1.0))    # elbow
        ell(mb, (sgn * 0.222, 0.016, 1.030), 0.041, (1.0, 1.0, 1.85))   # forearm
        ell(mb, (sgn * 0.230, 0.020, 0.930), 0.036, (1.0, 1.0, 1.1))
        ell(mb, (sgn * 0.232, 0.030, 0.872), 0.038, (0.85, 0.62, 1.25))  # hand

    # ── legs, with a knee that is a joint rather than a narrowing
    for sgn in (1.0, -1.0):
        ell(mb, (sgn * 0.098, 0.004, 0.830), 0.082, (1.0, 1.0, 1.9))    # thigh
        ell(mb, (sgn * 0.102, 0.006, 0.640), 0.072, (1.0, 1.0, 1.9))
        ell(mb, (sgn * 0.104, 0.020, 0.505), 0.062, (1.02, 1.12, 1.0))  # knee
        ell(mb, (sgn * 0.104, 0.000, 0.390), 0.058, (1.0, 1.0, 2.0))    # shin
        ell(mb, (sgn * 0.104, 0.000, 0.180), 0.050, (1.0, 1.0, 1.8))
        ell(mb, (sgn * 0.104, 0.030, 0.075), 0.050, (1.0, 1.5, 0.75))   # ankle
        ell(mb, (sgn * 0.104, 0.090, 0.045), 0.050, (1.05, 2.1, 0.70))  # boot

    if hood:
        # a cowl that sits around the skull, then a negative to open the face
        ell(mb, (0, 0.030, 1.640), 0.128, (1.05, 1.10, 1.10), stiff=1.6)
        ell(mb, (0, 0.125, 1.618), 0.092, (0.95, 1.00, 1.05), negative=True, stiff=2.0)
        ell(mb, (0, 0.010, 1.500), 0.090, (1.15, 1.10, 0.55), stiff=1.6)   # shoulders of the cowl
    return ob


def to_mesh(ob, smooth=True):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    me = bpy.context.active_object
    if smooth:
        for p in me.data.polygons:
            p.use_smooth = True
    return me
