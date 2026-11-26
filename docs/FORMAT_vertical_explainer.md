# The vertical explainer format

Measured from a 69 s reference: "Why he dumped 50 gun locks into one big pile"
(@Katheri23760769, 2026-11-26). This is the format the pipeline should be able to make,
written down as numbers rather than adjectives.

## What the reference actually does

| property | measured |
|---|---|
| frame | 1080×1920, 60 fps, vertical, no cinema bars |
| length | 69.4 s |
| cuts | 14 hard cuts + 15 short moves (fades/wipes) — a new shot every ~4.9 s |
| narration | continuous speech, no music bed, pauses of 0.3–0.5 s between sentences |
| sound | foley on action (clicks, drops, scrapes); "no steady pulse found" — there is no beat to cut to |
| captions | one word at a time, white bold condensed (Anton-like), black outline, centred at ~62% of frame height, about 0.8 s per word |
| lighting | warm torch/lantern key from the left, cool ambient, deep falloff into the vault |
| cast | stylised humans, big noses, toon-shaded, simple shapes — the character-forge look |
| set | stone vault, timber table, brick; painted-looking surfaces |
| structure | hook (one sentence, wide) → explain (medium, hand inserts) → assemble (macro inserts) → reveal (wide, the pile) → closing line |

Shot grammar, in order: wide two-shot → medium profile → hand macro → prop insert →
wide with all characters → object close-ups on the table → the reveal.

## How to make one in wubu3d

```json
{
  "preset": "vertical",          // 720x1280, no bars (landscape frames still get 2.39:1)
  "duration": 60, "fps": 60,
  "ambient": 0.09,               // interiors need a lower floor than the outdoor default
  "lights": {"key": {"energy": 9000, "size": 22, "color": [1.0, 0.66, 0.34], "loc": [-5, -6, 5]},
             "rim": {"energy": 3500, "size": 10, "color": [0.45, 0.60, 1.0], "loc": [5, 4, 5]}},
  "captions": {"words": "out/<film>/words.json"}   // whisper-style [{word,start,end}]
}
```

Rules that came out of the reference and hold for this format:

1. **One word per caption, 0.6–1.0 s.** Two words is a title, not a caption; the eye reads
   one word in the time the voice takes to say it.
2. **Caption at y ≈ 0.62**, not at the bottom: the subject's hands and the table are in the
   lower third and the caption must not cover the object being talked about.
3. **White fill, black outline, no box.** No drop shadow-only — on a warm set it vanishes.
4. **No music.** Narration plus foley; a bed makes the captions harder to read and the
   pauses disappear.
5. **The reveal is a wide shot of the pile with the count in the caption.** It is the only
   wide shot that holds longer than the average (about 6 s).
6. **Cut every ~5 s**, and cut *to a closer angle of the same object* rather than to a new
   location: the party trick of the format is that nothing new is introduced after 20 s.

## What the pipeline still needs to match it

* a toon/inked shading pass (the reference is cel-shaded; our raster and Cycles are not),
* set dressing (vault walls, timber) — meshes now import, none exist yet,
* foley: our score is synthesised music, so action sounds have to be placed per event,
* 60 fps at 1080×1920: the raster path is ~0.04 s/frame at 320×180; 1080×1920 is ~20× the
  pixels, so a 60 s film is minutes on the raster path and hours on Cycles. Render the
  vertical cut from the raster path and keep Cycles for stills until that changes.
