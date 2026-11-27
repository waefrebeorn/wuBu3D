# Faces

A face is the only part of a character an audience reads at 100 ms, so it is the part where a dark
bead instead of an eye costs the most. Rebuilt from a 25-facet sweep of face design, caricature,
expression and eye craft.

## The eye is a stack, not a dot

| layer | why |
| --- | --- |
| sclera | establishes the shape before anything else is placed |
| iris | gives the eye a *direction* — this is what "looking" is |
| pupil | focus; a small pupil reads startled, a large one reads soft |
| catchlight | life. One or two dots, upper-left, and the eye stops being a hole |
| lash line | weight; it follows the eye's own upper contour |
| lower lid | a thin warm line, stopping short of the corners |

A single dark bead is readable at thumbnail size but lifeless; the stack costs five draws and reads
as a character.

## The expression channels are separate

Eyebrows, eyes and mouth are three independent channels, and expressions are combinations:

- **anger** — brow tilt inward/down, lid lowered, mouth a flat line
- **surprise** — brow lift, eye wide (small lid coverage), mouth open round
- **worry** — brow lift with inner ends up, mouth small
- **happy** — brow slight lift, mouth curved up, teeth allowed

With only the mouth, "angry" and "neutral" differ by a line's curvature and read as the same face.
That was a real bug in the cast: the simple face had no brows at all.

## Construction rules from a 100-query sweep

The face is a proportion problem before it is a detail problem. These are the rules that survived
the sweep, and each one is now a constant in the code:

| rule | value | why |
| --- | --- | --- |
| five-eye width | face = 5 eye widths, gap = 1 eye width | the single most common beginner error is eyes that collide into one mass |
| eyes at the vertical middle | `eye_v = 0.46` | not above the middle; almost every drawn face puts them too high |
| mouth width | interpupillary distance, narrowed ~30% for appeal | wider reads as a muppet, narrower reads as a doll |
| nose | halfway between eye line and mouth | not at the mouth |
| ear (where a character has one) | top at brow, bottom at nose base | |
| lid at rest | covers 15-25% of the iris | more reads sleepy, less reads startled |
| sclera | warm tint `(247,243,238)` | pure white reads as a sticker pasted on |
| catchlight | two: a large one offset to the key side, a small opposite | one dot reads dead |
| asymmetry | 2-5% | measured believability work is unambiguous: perfect symmetry reads as a mask |
| mouth curve | scales with mouth WIDTH | scaled with height, a closed mouth can never smile (it was a real bug) |

## Proportions that matter (measured, not taste)

- mouth width ≈ **1/6** of the face; at 1/3 the face becomes a muppet
- an open mouth must be **tall as well as wide** — a flat lens reads as a slot
- teeth on the upper edge and a tongue at the bottom turn a black shape into a mouth
- blush at ~0.46 eye-width, low alpha, sits under the eyes
- the nose is a dot or a short shadow; anything more is a different style
- **dynamic asymmetry of ~3%** — one eye a little larger, one slightly higher. Perfect symmetry
  reads as a mask; the tiny difference reads as alive (the believability research on facial
  asymmetry is unambiguous).

## Three bugs the rebuild exposed

1. **The lid patch painted a rectangle.** The skin wedge that hides an eye's top only makes sense on
   an opaque face sheet; on a transparent decal it drew a skin box above each eye, which read as a
   pair of glasses.
2. **The lash line floated.** Drawn as a near-straight bar above the sclera, it read as a second,
   disconnected eyebrow. It now follows the eye's own upper contour.
3. **Every viseme looked identical** because the mouth opening was `0.030` of the sheet — a thin
   lens at every value. At `0.078` the six shapes are distinct.

## Still missing on the face

- **blink** — no lid-close animation yet, and a face that never blinks reads as a mannequin
- **squash & stretch** on expressions (the mouth and eyes should deform, not just move)
- **line-weight variation** — our outlines are one thickness everywhere
- **expression library** — six states exist; a sheet needs twenty

## The eye, after 100 more queries

The eye is a **clipped stack inside a symmetric ellipse**, not shapes drawn loose on a face:

```
ellipse sclera (tinted, shaded top, bounce bottom)   <- clip mask
  iris  56% of eye height, radial gradient, limbal ring
    pupil 46% of iris, pure black
    catchlights: large key-side, small opposite
tapered lash band along the ellipse's top edge
lower lid: thin, outer half only
```

Four things broke on the way, each worth recording:

1. **The almond path is asymmetric.** Every eye drawn from it read as a *profile* eye — a wedge of
   white on one side and the iris filling the other. An ellipse is symmetric by construction.
2. **A thick `arc()` cannot taper.** PIL draws a constant-width stroke whose ends are radial cuts:
   blunt black triangles at both corners. Stopping the arc short of the corners only moves the
   wedge. The lash is now a polygon whose thickness tapers to zero at both ends.
3. **Mirroring matters.** Building both eyes the same way puts the lash flick on the INNER corner of
   one of them — a stray hair growing out of the eye. The layer is built as a right eye and mirrored.
4. **The tilt sign was inverted.** Positive PIL rotation is counter-clockwise, which raises the
   outer corner of the right eye. Passing `-tilt` dropped it and gave every eye a sad, drooping read.

Measured proportions: iris 56% of the eye's height (below ~45% the eye reads blank, above ~70% the
sclera disappears), pupil 46% of the iris, lash thickness 15-20% of eye height, catchlight 26% of
the iris radius, lid at rest covering 15-20% of the iris.
