/* occl.c — software occlusion culling against the previous depth buffer.

A box is culled when every sample of its screen-space rectangle is nearer to the camera than the box's
own nearest corner: something is already in front of all of it. The cheap version samples a grid rather
than every pixel, which is safe in one direction only — a grid can MISS an occluder gap and keep a
box that could have gone, but it can never cull a box that was actually visible, as long as the test is
"every sample is closer" and not "most samples are closer".

That asymmetry is the whole design: a wrong cull is a hole in the frame, a missed cull is wasted work.
*/

#include <math.h>
#include <stdint.h>
#include <stdlib.h>

int wubu_occl_test(const float *zb, int W, int H, const int *rects, const float *nearz, int n,
                   int step, int *visible)
{
    if (!zb || !rects || !nearz || !visible || n < 1) return -1;
    int kept = 0;
    int st = step < 1 ? 1 : step;
    for (int i = 0; i < n; ++i) {
        int x0 = rects[i * 4 + 0], y0 = rects[i * 4 + 1];
        int x1 = rects[i * 4 + 2], y1 = rects[i * 4 + 3];
        visible[i] = 1;
        if (x0 < 0 || y0 < 0 || x1 >= W || y1 >= H) { kept++; continue; }   /* partly offscreen: keep */
        if (x1 <= x0 || y1 <= y0) { kept++; continue; }
        float nz = nearz[i];
        int occluded = 1;
        for (int y = y0; y <= y1 && occluded; y += st) {
            for (int x = x0; x <= x1; x += st) {
                if (!(zb[y * W + x] < nz)) { occluded = 0; break; }        /* something is behind: visible */
            }
        }
        /* the last row and column of the rect are where a thin gap hides; check them explicitly */
        if (occluded) {
            for (int x = x0; x <= x1; x += st)
                if (!(zb[y1 * W + x] < nz)) { occluded = 0; break; }
            if (occluded)
                for (int y = y0; y <= y1; y += st)
                    if (!(zb[x1 + y * W] < nz)) { occluded = 0; break; }
        }
        if (occluded) { visible[i] = 0; }
        else kept++;
    }
    return kept;
}
