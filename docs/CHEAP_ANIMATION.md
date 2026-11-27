# Small, cheap cartoons

Limited animation is not "cheap animation"; it is choosing where motion matters and holding
everything else. The levers, in the order they save the most:

1. **Camera move** — one drawing for a whole shot; the pan or zoom carries the motion.
2. **Hold** — one drawing for a long beat; only a mouth or a hand changes.
3. **On twos** — 12 drawings per second instead of 24.
4. **Reuse cycle** — a walk built once, looped wherever it is needed.
5. **Partial** — animate one layer over a held body.

`cheap.py` plans a shot list against those and reports the real count, so the saving is a number:

| shot | secs | technique | drawings | frames | saved |
| --- | --- | --- | --- | --- | --- |
| cold open | 5.0 | camera | 5 | 120 | 96% |
| establish | 7.0 | twos | 84 | 168 | 50% |
| turn | 7.0 | hold | 11 | 168 | 93% |
| escalate | 8.5 | twos | 102 | 204 | 50% |
| fallout | 6.0 | cycle | 18 | 144 | 88% |
| button | 4.5 | camera | 5 | 108 | 95% |
| **total** | **38.0** | | **225** | **912** | **75%** |

225 unique drawings for a 38-second short at 24 fps, against 912 if every frame were drawn.
