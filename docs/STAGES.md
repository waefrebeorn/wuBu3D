# Stage plates and hard captions

The gap list put these first and second: a thousand characters with no rooms and no captions is a
casting sheet, not a short.

## Stages are geometry, not backdrops

A plate rendered behind a character is a lie the camera cannot move through: no occlusion, no
parallax, no shared light. These sets are meshes in the same world space as the cast, so a shot is
one camera and one depth buffer — a character standing behind the counter is *occluded by the
counter*, because the same zbuf decides it.

Three sets, each with its pieces exposed as bones so the set can be rigged:

| set | pieces |
| --- | --- |
| room | wall, door, lamp, counter, window |
| alley | door, bin, window |
| void | back |

Cost: **0.30 s** for three 1080x1920 plates through the C11 raster.

Two framing mistakes, both the same mistake twice: a **fixed camera** cropped the room the first
time and a **width-fitted** camera letterboxed it the second. A tall frame wants the *height* fitted
and the side walls running off frame — that is staging, not a bug. A wide shallow room in a 9:16
frame always floats in white; the floor has to be deep enough to own the bottom of the frame.

## Captions

The format is a voice under hard captions, one or two words at a time. What makes that readable is
measurable: cap height about 7-9% of frame height, a dark stroke ~0.16 of the cap height, word-by-
word reveal at 2-4 words a second, anchored in the upper third so the action stays clear.

`captions.py` draws it with a pop on the newest word — the difference between a caption that reads
as *timed* and one that reads as pasted — and exposes the reveal timing so the sound can be cut to
it:

```
t=0.00s words shown 1/9      t=1.00s words shown 4/9
t=0.60s words shown 2/9      t=2.00s words shown 7/9
```

## A real frame

Set + cast in one camera: `stages.shot("room", "peanut")` renders the room, the character at a
position inside it, and the face decal depth-tested against the room's own geometry.
