# Proportions, applied to every model

The face rules were applied to the face texture and the layout rules to the frame, but nothing
checked the MODELS. A peanut with a 1.9-head body and a tower with a 5.4-head body were both
"finished" while breaking the same proportions.

`audit.py` measures every registered model and fails it against a rule set:

| rule | measure | range |
| --- | --- | --- |
| head:body | head bone length / model height | 0.22 - 0.50 |
| band coverage | face band height / head length | 0.55 - 1.00 |
| eye gap | gap between eyes / eye width | 0.70 - 1.30 |
| mouth width | mouth / face width | 0.18 - 0.45 |
| eye height | eyes as a fraction of the band | 0.38 - 0.55 |

## What it found, and what it cost to fix

```
before:  2 of 12 models violate a proportion rule
            can_legacy   head:body 0.60   (head bone too long for its drum)
            donut_legacy head:body 0.53
after:   0 of 12 models violate a proportion rule
```

Both were head BONES, not meshes: the geometry was fine and the rig's head segment was simply
longer than the body could carry. Shortening the bone re-framed the face and the ratio came back
into range. The same class of bug as the earlier "normal-only lighting" and "wrong-side safe area":
the model was right and the numbers describing it were not.

The audit also caught a registry fault. `models.py` was rebuilding each model's face options from
defaults, so the audit measured **the same eye_v and mouth_v for all twelve** while the renderer used
per-model overrides. Once the builder's own config was carried through, the donut reported its real
0.30 mouth and the tower its hand-set 0.34 eye height — the latter a genuine violation, now 0.42.

## The rule that keeps recurring

Every one of these faults is the same shape: a number that described the model was stored somewhere
the checker could not see, or was derived from the wrong axis. The fix is always to make the model
and the number the same object — which is what the collider work did for width and depth, and what
this does for proportion.
