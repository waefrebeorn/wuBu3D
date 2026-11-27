# Margins, alignment and proportion

A 49-query sweep on layout. Every frame in this project placed things by eye with hand-typed pixel
offsets; the research is unambiguous that there are numbers, and they are now in `layout.py`.

## For a 1080x1920 frame, measured

| guide | value |
| --- | --- |
| action safe | 3.5% margin — box 37,67 -> 1042,1852 |
| title safe | 5.0% margin — box 54,96 -> 1026,1824 |
| TikTok UI safe | 13% off the **right** edge, 18% off the bottom |
| thirds | x 360 / 720, y 640 / 1280 |
| golden sections | x 413 / 667, y 733 / 1187 |
| 12-column grid | first 54, last 967, column 59 px, gutter 24 px |
| type scale (major third) | 19, 24, 30, 38, 47, 59, 73, 92, 114, 143, 179, 224 |
| spacing (8pt grid) | 8, 16, 24, 32, 48, 64, 96 |
| optical centre | y 902, not the geometric 960 |

## The rules that were being broken

**Safe areas are inherited from broadcast, not invented.** Action safe is 93% of frame and title
safe 90%, from a era when CRT overscan ate the edges. Vertical platforms add their own: an action
rail down the right, a description block at the bottom.

**The platform safe area was inset on the wrong side.** The first version reserved 13% on the left
— where nothing is drawn — and left the subject free to sit under the buttons. It is the right edge.

**One spacing unit, not twelve numbers.** Every gap in a design should be a multiple of one unit;
8 px is the common choice because it divides evenly at the scales screens actually use.

**A type scale must reach the biggest thing on screen.** An 8-step 1.25 scale topped out at 92 px
when a title needs ~163 px, so the hierarchy had no room for a title at all. Twelve steps reach 224.

**Optical centre is not geometric centre.** Text placed at the true vertical centre looks low; the
eye weights the mass above the baseline more heavily. Placing a block at 47% reads centred.

**Camera distance is measured from the TARGET, not the set's far edge.** Adding the computed
distance to the set's furthest z put the camera ~40% farther away than the fit assumed, and every
set rendered as a diorama floating in the middle of the frame. That was one bug wearing two
different symptoms — it showed up as "the room is too small" and as "there is an empty band above
the set".

**A set has to be tall enough for the frame.** A 3.0-unit wall in a 9:16 frame fills about half the
height; at 5.0 it fills the frame and the empty band disappears.

## Using it

```python
import layout
x0, y0, x1, y1 = layout.safe("tiktok", 1080, 1920)
x = layout.place(text_w, 1080, align="center")
sizes = layout.display_sizes(1920)          # the whole scale for this frame
layout.overlay(im, ("safe", "thirds", "golden", "columns"))   # draw the guides on a frame
```

`layout.overlay` is the useful part: it draws the guides on a real render so a composition can be
checked against the rules instead of trusted.
