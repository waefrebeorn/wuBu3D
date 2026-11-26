"""Build a character body from metaballs, then convert it to a mesh.

Primitive tubes always read as tubes. Metaballs fuse into one continuous surface, which
is the cheapest way to get an organic body out of a script: place ellipsoids along the
skeleton, let them blend, convert, done.

Run inside Blender:
  blender -b -P build_body.py -- --out /tmp/body.blend --png /tmp/body.png
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, "/opt/data/work/wubu3d")
import wubu3d_rig as R

J = R.JOINTS


def add_element(mb, co, radius, stiffness=2.0, kind='BALL', size=(1, 1, 1)):
    e = mb.elements.new()
    e.co = Vector(co)
    e.radius = radius
    e.stiffness = stiffness
    e.type = kind
    e.size_x, e.size_y, e.size_z = size
    return e


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mb = bpy.data.metaballs.new("BodyMB")
    mb.resolution = 0.010
    mb.render_resolution = 0.010
    ob = bpy.data.objects.new("Body", mb)
    bpy.context.scene.collection.objects.link(ob)

    # torso: three blended ellipsoids — hips, waist/ribs, chest
    add_element(mb, (0, 0, 0.93), 0.26, kind='ELLIPSOID', size=(0.46, 0.34, 0.50))
    add_element(mb, (0, 0.005, 1.12), 0.30, kind='ELLIPSOID', size=(0.48, 0.34, 0.70))
    add_element(mb, (0, 0, 1.33), 0.30, kind='ELLIPSOID', size=(0.58, 0.38, 0.55))
    # shoulders
    for s in (1, -1):
        add_element(mb, (s * 0.17, 0, 1.38), 0.13, size=(1, 1, 1))
    # neck and skull
    add_element(mb, (0, 0.01, 1.47), 0.075)
    add_element(mb, (0, 0.012, 1.60), 0.135, kind='ELLIPSOID', size=(0.92, 1.02, 1.12))
    # limbs: a chain of balls along each bone fuses into a tapered limb
    def chain(a, b, r0, r1, n=7, side=1):
        """a capsule along the bone, plus a ball at each end to round the joint"""
        mid = tuple((a[k] + b[k]) * 0.5 for k in range(3))
        length = math.dist(a, b)
        e = mb.elements.new()
        e.type = 'CAPSULE'
        e.co = Vector(mid)
        e.radius = (r0 + r1) * 0.5
        e.size_x = max(0.02, length * 0.5 - e.radius * 0.5)
        e.stiffness = 2.0
        # orient the capsule along the bone: Blender aligns metaball capsules to +X
        d = Vector(b) - Vector(a)
        e.rotation = d.to_track_quat('X', 'Z')   # quaternion, 4 components
        add_element(mb, a, r0)
        add_element(mb, b, r1)

    for side, sx in (("L", 1), ("R", -1)):
        sh, el, wr = J[f"shoulder.{side}"], J[f"elbow.{side}"], J[f"wrist.{side}"]
        chain(sh, el, 0.058, 0.046, 6)
        chain(el, wr, 0.044, 0.034, 6)
        add_element(mb, (wr[0], wr[1] + 0.01, wr[2] - 0.06), 0.055, kind='ELLIPSOID', size=(0.7, 1.3, 1.2))
        hp, kn, an = J[f"hip.{side}"], J[f"knee.{side}"], J[f"ankle.{side}"]
        chain(hp, kn, 0.088, 0.062, 6)
        chain(kn, an, 0.058, 0.042, 6)
        add_element(mb, (an[0], an[1] + 0.05, 0.06), 0.075, kind='ELLIPSOID', size=(0.85, 1.6, 0.65))

    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    body = bpy.context.active_object
    body.name = "BodyMesh"
    for p in body.data.polygons:
        p.use_smooth = True
    return body


def ground(body):
    zs = [body.matrix_world @ v.co for v in body.data.vertices]
    dz = min(v.z for v in zs)
    body.location.z -= dz


def light_and_camera():
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 32
    sc.render.resolution_x, sc.render.resolution_y = 600, 800
    sc.render.film_transparent = False
    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.57, 0.62, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.9

    def area(loc, energy, size, color=(1, 1, 1)):
        d = bpy.data.lights.new("L", 'AREA')
        d.energy = energy
        d.size = size
        d.color = color
        o = bpy.data.objects.new("L", d)
        sc.collection.objects.link(o)
        o.location = loc
        tr = o.constraints.new('TRACK_TO')
        tr.target = bpy.data.objects.get("Aim") or bpy.data.objects.new("Aim", None)
        return o

    aim = bpy.data.objects.new("Aim", None)
    sc.collection.objects.link(aim)
    aim.location = (0, 0, 1.0)
    area((2.6, 3.2, 3.0), 900, 2.5, (1.0, 0.96, 0.90))
    area((-3.0, 2.0, 2.2), 380, 3.0, (0.72, 0.80, 1.0))

    cam_d = bpy.data.cameras.new("C")
    cam_d.lens = 65
    cam = bpy.data.objects.new("C", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = (3.2, 5.2, 1.30)
    tr = cam.constraints.new('TRACK_TO')
    tr.target = aim


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out_blend = "/tmp/body.blend"
    out_png = "/tmp/body.png"
    for i, a in enumerate(argv):
        if a == "--out":
            out_blend = argv[i + 1]
        if a == "--png":
            out_png = argv[i + 1]

    body = build()
    ground(body)
    light_and_camera()
    bpy.context.scene.render.filepath = out_png
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    bpy.ops.render.render(write_still=True)
    print("BODY_OK", len(body.data.vertices), "verts", len(body.data.polygons), "faces")


main()
