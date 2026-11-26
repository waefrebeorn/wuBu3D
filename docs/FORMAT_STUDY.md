# Reference format: vertical word-caption explainer ("50 gun locks")

Measured 2026-11-26 from a 69.4 s reference (@Katheri23760769 on X, "Why he dumped 50 gun
locks Into one big pile"). Numbers are measured with `perceive.py` (frames, cuts, spectrogram,
audio timeline); the reading below is what a spec has to carry to sit in that format.

## The numbers

| property | measured |
|---|---|
| frame | 1080×1920 (9:16), 60 fps, 69.4 s |
| shots | 15, hard cuts at 0, 10.10, 15.65, 17.78, 17.83, 26.85, 31.52, 32.93, 37.12, 37.72, 40.07, 41.70, 55.90, 62.55, 65.07 |
| shot length | median 4.19 s, mean 4.63 s, one 0.05 s flash insert, one 14.2 s held reveal |
| captions | one word at a time, lowercase, heavy sans, pure white fill, thick black outline, centred, baseline ≈ 0.62 of frame height, letter height ≈ 9% of frame (em ≈ 11%) |
| palette | dark warm browns — dominant RGB clusters (32,16,0), (64,32,32), (96,64,32); lantern highlights (224,192,128) and (224,160,96) |
| art | 2D vector cartoon: flat fills, heavy black outlines, dots for eyes, big noses, no gradients |
| audio | 212 onsets in 69 s, 49 sound events, 26 dips, **no steady pulse**, **no tonal content detected** — the track is diegetic SFX (metal clicks, scrapes, weight landing), and the words on screen carry the story |

## The format, in one sentence

A question in the title ("why he ..."), answered by a physical process shown in close-up steps,
narrated by single words on screen, scored by the sound of the objects doing the thing.

## What this pipeline can carry

Everything structural, and it is now a spec rather than a description
(`specs/format_vertical.json`, rendered check below):

* **9:16 at any fps** — `preset: "vertical"` + `fps`, no cinema bars on portrait frames.
* **Word captions in that position and size** — `captions: {words, size: 0.10, y: 0.62, stroke:
  true, font: "sans"}`. The reference's font is a wide geometric bold; `sans` (DejaVu Bold) is
  closer than our default Anton, which is condensed display type.
* **The shot grammar** — medium, tight follow, an object/insert shot with a long lens, then a
  pull-back reveal; four shots of ~3 s, which is inside the reference's median.
* **The palette** — warm key light, cool rim, low ambient, and `tonemap: "aces"` so highlights
  roll off instead of clipping.
* **Diegetic hits** — `sound.sfx: [{at, type: clink|click|thud|scrape, gain, pan}]`, synthesised
  (noise transient + short ring, material-weighted). Tuned by placement, not by a music bed.

## What it cannot carry, and should not pretend to

* **The 2D vector art.** Our cast is 3D primitives on the raster path. The reference's charm is
  hand-drawn flat shapes with heavy outlines; that is the `wubu2d` cartoon path, a different
  renderer, and it would need its own spec and rig.
* **Character acting.** The reference cuts on expressions and gestures between words. We can cut
  on shots; we cannot yet mime.
* **Real foley.** The SFX generator is four synthesised families. Metal on metal at this density
  wants samples.

## How to use this

Start from `specs/format_vertical.json`, change the subject and the words, keep the timing
skeleton (4 shots × 3 s, one word per 0.4–0.8 s, a hit under each word). The format is the
skeleton; the subject is the variable.
