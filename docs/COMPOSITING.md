# Compositing a code-rendered character into a plate

The brainrot reference ("Creative DIY Brainrot", 61 s, 720x1280) is cheap characters inside
expensive-looking photographic plates — a temple garden at dusk, a fleshy cave, a floor of petals.
The characters carry none of the weight; the plate does. That is the skill-file rule made concrete:
paint the world, do not simulate it.

`plate.py` does the four operations that compositing actually needs:

    matte()      cut the render off its key colour, one-pixel erosion so no halo survives
    shadow()     multiply the plate toward black under the feet, soft ellipse
    match()      pull the character toward the plate's LOCAL statistics
    composite()  the above + a DOF blur of the plate

## The three failures, in the order they happened

**1. Grade over the whole buffer.** The render still carries its key-colour background — 66 % of the
frame. Matching LAB statistics over all of it drags every pixel toward the key, and the character
comes out a flat magenta figure with perfectly clean edges. Fix: mask to the alpha before computing
statistics, and fill the background with the character's own mean so only the subject moves.

**2. Match to the local plate makes the subject invisible.** Correct colour, correct value — the same
value as the ground it stands on. Photographic, and unreadable. Fix: `separate()`, a lift in L only
(L x 1.55) so a subject sits above its local background the way a real subject does.

**3. No rim.** The character is lit by generic lights, not by the lanterns in the plate.
`key_light()` reads the plate's brightest 3 % and returns its colour and its position; the key colour
warms the character, the position gives the light direction. Still the weakest part of the comp.

## Measured, three states of the same composited frame

| state | edge luminance break | reads as |
|---|---|---|
| magenta | 0.153 | a sticker, and the wrong colour |
| matched only | 0.039 | invisible — correct and dead |
| matched + separated | 0.103 | in the scene, slightly flat |

The metric is a diagnostic, not a score: **low is not good here.** 0.039 means the subject has become
its background; 0.103 is separation. What separates a seam from intended contrast is whether the
subject's *interior* sits above its local surround, which is what `separate()` guarantees.

## What plates cost

Nothing in this module makes a plate. A plate comes from an image model or a camera, and that is the
one place where "all in code" stops paying: a code-built set of the same shot reads as a diagram, at
any quality of shading. The honest position is that the renderer's job is the character, the light
match and the comp — not the world behind it.
