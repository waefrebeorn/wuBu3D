# Craft: what a cartoon needs, and what we were missing

Three research threads, and what each one changed.

## 1. The format (brainrot)

The 2026 consensus on the format is unromantic: a **vertical short**, an **AI voice**, **hard
captions**, over **looping footage**, with a hook inside the first second and something changing on
screen constantly. Oxford named "brain rot" its Word of the Year for 2024 (usage up 230% year on
year), and "rage bait" in 2025 — two years, two words for content optimised for a metric.

What that means for a code-drawn cartoon:

| element | have | missing |
| --- | --- | --- |
| vertical frame | 1080x1920 renderers | — |
| hook in <1s | shot tables can do it | no explicit hook beat in the planner |
| hard captions | text drawn per frame | no caption style set, no bounce/timing library |
| loopable footage | cycles exist | no seamless-loop check |
| voice | TTS available | no timing fit to captions |

## 2. Character continuity sheets

Every AI-cartoon guide converges on one asset: a **single dense board per character** — turnaround,
expressions, poses, costume, exact palette — because a written description re-decides a thousand
small things on every generation, and that re-decision IS the drift.

We build the mesh, so our geometry cannot drift; but a board is still the reference a shot list, a
rigger and an editor work from. `sheetgen.py` renders one per character in **under a second**:
three views (3/4, front, side) plus three expressions, labelled, with the palette printed.

The build found two real faults:

- a fixed camera distance **cropped the character's head** — the camera now fits the bounding box
- "angry" and "neutral" differed only by the curvature of one line, because the simple face has no
  brows; expressions now carry a second channel (angled brows)

## 3. Twist, and why weights cannot fix it

The candy-wrapper is not a weight-painting problem. Linear blend skinning averages bone MATRICES, so
two rotations 180 degrees apart average to near-zero scale — every weight value still averages two
opposed rotations. Blender's "Preserve Volume" (dual quaternions) fixes it visually but **does not
survive export**: glTF, Unity and Unreal all skin with LBS.

The rig-side fix is to never let a joint twist that far. Spread it across the chain:

```
LBS radius at a joint:   180 deg 0.000 (collapse)   90 deg 0.707   60 deg 0.866
```

A wrist twisting 180 degrees with no twist bones keeps **0%** of its radius. Spread over three bones,
the worst joint keeps **87%**. `wuburig.c` implements the decomposition (swing-twist) and the
distribution (even or ramped), plus FK/IK blending.

## The asset gap list

What the show still has none of, in the order it hurts:

1. ~~**Stage plates**~~ — done: three riggable sets, one camera with the cast (see STAGES.md)
2. **Expression library** — three per character is a start, not a library
3. **Pose silhouettes** — walk, run, idle, react; the rig can pose, nothing drives it
4. **Caption set** — typography, bounce timing, the hard-caption look the format runs on
5. **Sound stings** — whooshes, pops, the one-second button
6. **Loop check** — nothing verifies a cycle is seamless
