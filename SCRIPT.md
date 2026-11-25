# THE LAMP — shooting script

Silent. 70 seconds. Six shots. Captions carry the narration; no voiceover.
One character we can draw, one we can draw smaller, one prop (a lantern), one set (the plain).

## Logline

Every night the lamplighter walks the plain with one light. Tonight someone is waiting in the
dark, and the light he gives away is his own.

## The turn

He is not lighting lamps. He is giving his light away, one night at a time. Shot 4 reveals it;
shot 5 confirms it. Everything before is misread on purpose.

## Beats

| # | time | beat | what we see | caption |
|---|---|---|---|---|
| 1 | 0:00–0:12 | establish | wide, night plain, small figure with a lantern crossing right to left | Every night, the lamplighter walks the plain. |
| 2 | 0:12–0:22 | routine | medium; he stops at a post, lifts the lantern, the lamp catches | He lights every lamp he passes. |
| 3 | 0:22–0:34 | disturbance | he stops mid-step; a small figure sits in the dark, knees up | Tonight someone is waiting. |
| 4 | 0:34–0:46 | choice | close; he looks at his lantern, then at the child, and holds it out | He has one light. |
| 5 | 0:46–0:58 | cost | wide; the child walks off with the light; he stands in the dark | So he gives it away. |
| 6 | 0:58–1:10 | result | he walks on into the dark; the frame empties | He walks home without it. |

End card: **THE LAMP** / a WuBu short / github.com/waefrebeorn

## Shot specs

1. **Wide** — camera drifts right to left with him, 3/4 view. He is 12% of frame height.
2. **Medium** — static, he fills 45% height; the post is off-frame left.
3. **Medium wide** — he stops; the child is a small shape at 20% height, screen right.
4. **Close** — his head and shoulders, 70% height; the child's hands enter from the right.
5. **Wide** — the child walks away with the light; he stays, lit only by the moon.
6. **Wide** — he walks away from camera; he shrinks and the lantern glow leaves with him.

## Cast and props

* **The lamplighter** — bean-head puppet, tall coat, hood, one lantern.
* **The child** — same rig, 62% scale, no coat, no hood.
* **The lantern** — a small warm emitter with a glow; it is the only warm light in the film.
* Set: night plain, three post silhouettes, mist. The raster renderer makes this in milliseconds.

## Performance rules (from the 33k-frame study)

* Nothing is still: camera moves on every shot, mist drifts, the glow flickers.
* The character acts on the caption, not after it — the pose changes on the word.
* Expression changes every 0.3–0.8 s in shots 3 and 4.
* No hard cuts in the middle of a beat; cuts land on the beat edge.

## What this needs to exist

1. `wubu2d.py` — puppet (done).
2. A compositor that puts the puppet over a 3D plate with per-frame x/y/scale/pose. **(next)**
3. Plate renders from the raster path, no character. (exists)
4. Captions with the same type as the WuBu3D demos. (exists)
5. Sound: wind bed, a match-strike, footsteps, a soft chime on the handover. (synthesised)
