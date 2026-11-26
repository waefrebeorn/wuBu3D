# The ten steps, and where this project actually stands

Written because I presented a blockout as if it were the character. The sculpting workflow
the post describes is a pipeline, not a single act — a 380-step run that blocked a boss out of
boulders, grew arms and a face, then **refit the silhouette 20 times** until front, side and back
matched the drawing at 0.89–0.90 IoU.

That refit loop is the part I skipped. Here is the honest map.

| # | step | what it means | state here |
|---|---|---|---|
| 1 | **Blockout** | rough volumes that carry the mass: pelvis, ribcage, head, limb segments. Nothing detailed. | **done** — metaball/loft body, 1.76 m, reads as a figure |
| 2 | **Silhouette refit** | render front/side flat, compare against the reference, adjust proportions, repeat until IoU ≥ 0.90 | **next** — needs a measurement tool and a reference |
| 3 | **Anatomy pass** | knees, elbows, clavicles, pelvis tilt, skull planes, hands. Add volume where the body bends. | not started — this is where "no knees" lives |
| 4 | **Head and face** | the head is the read: brow, eye sockets, nose, jaw, chin. A block with two dots is not a head. | not started |
| 5 | **Detail pass** | cloth folds, seams, boot shape, hood volume away from the skull | not started |
| 6 | **Surface / paint** | materials: cloth vs skin vs leather, roughness, a colour script that holds at night | partial — flat colours only |
| 7 | **Rig and skin** | bones with correct roll, weights that blend across each joint, IK if the shot needs it | partial — rigid groups, no roll, no IK |
| 8 | **Performance** | keyed poses with timing: anticipation, contact, hold, follow-through. Not a sine wave. | partial — one keyed track, unverified |
| 9 | **Shoot** | staging, camera, light per shot; the cut | partial — 3 shots roughed |
| 10 | **Finish** | denoise, grade, sound, titles, deliver | exists from earlier work, untested on this film |

## What step 2 needs to be real

Not "looks better". Two numbers:

1. **Silhouette IoU** — render the character with flat emission on black, threshold to a mask,
   compare with the reference mask for the same view. Front and side, separately.
2. **Proportion ratios** — head height as a fraction of total height (target 7.2–7.5 heads),
   shoulder width in head-widths (2.0–2.3), hip width (1.5–1.8), knee height as a fraction of
   leg length (0.50), elbow at waist height.

The ratios are checkable without a reference image, which matters because a self-authored
reference can only ever agree with my own mistakes.

## Order of work from here

1. Build `tools/silhouette.py`: mask extraction, IoU, ratio measurement.
2. Measure the current blockout. Publish the numbers.
3. Refit: head size, shoulder width, leg length, knee placement.
4. Re-measure until IoU and ratios are inside tolerance, then and only then go to step 3.
