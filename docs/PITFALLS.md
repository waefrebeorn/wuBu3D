# Pitfalls that cost an hour each

## A scratch script named after a stdlib module shadows the import

`/opt/data/work/wubu3d` is on `PYTHONPATH`, so any file there wins over the standard library. A file
called `inspect.py` in that directory made `import numpy` fail with
`module 'inspect' has no attribute 'cleandoc'` — and running `python3 demo_oit.py` printed a social
feed instead of rendering, because numpy's `import inspect` executed the script.

Rule: prefix throwaway scripts with `_`, and never name one after a stdlib module
(`inspect`, `types`, `json`, `copy`, `io`, `code`, `queue`, `select`, `token`, `parser`, `string`).

Symptom to recognise: an import error from inside numpy mentioning a stdlib attribute, or output that
belongs to a different script entirely.

## Measuring a depth effect by image band

Fog, DOF and AO all key off depth. Selecting "the top third of the frame" as "far" is only true for a
level camera; with any pitch it is not, and the first fog measurement said fog brightened the near
geometry and left the far plane untouched, which was the opposite of the truth. Select pixels by
`_LAST_ZB`, never by their position in the frame.

## A mean over the whole frame hides a localised effect

The same fog pass read 4.5 -> 8.9 mean over the frame (looks broken) and 77.8 -> 153.7 over the lit
pixels (saturating at the fog colour, exactly right). Measure the pixels the effect applies to.

## Sky is a legitimate constant

Twice now a pass read all-zero on scanline 0 and looked broken: both times row 0 was sky, where a zero
normal or zero motion vector is correct. Re-read the row that contains geometry.
