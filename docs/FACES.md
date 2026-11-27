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
