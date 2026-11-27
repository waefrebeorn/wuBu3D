// wubuzbuf — C11 z-buffered rasteriser and depth-tested decals.
//
// raster.py does this in numpy and it works, but it is the single hottest path in the render: every
// tile, and all 912 frames of a film, go through it. The operation is embarrassingly simple —
// triangle in, nearest-depth pixel wins — and it does not want a numpy temporary per triangle.
//
// Matches raster.py's contract exactly so the two can be diffed pixel for pixel:
//   rgb   uint8, w*h*3, cleared to the background
//   zbuf  float32, w*h, cleared to +inf
//   proj  per triangle: three screen points, three depths, one colour
//
// Decals test against the same zbuf: a face plane that sticks out of a curved body loses the depth
// test instead of painting over geometry that is nearer than it.
//
// Build: cc -O2 -std=c11 -shared -fPIC -o libwubuzbuf.so wubuzbuf.c -lm

#include <math.h>
#include <stdint.h>
#include <string.h>

#define INF_Z 1e30f

void wb_clear(uint8_t *rgb, float *zb, int w, int h, uint8_t r, uint8_t g, uint8_t b) {
    int n = w * h;
    // two loops, not one: interleaving the rgb writes with the float writes defeats the
    // vectoriser, and this runs over 2 million pixels per frame
    for (int i = 0; i < n; i++) {
        rgb[i * 3 + 0] = r;
        rgb[i * 3 + 1] = g;
        rgb[i * 3 + 2] = b;
    }
    for (int i = 0; i < n; i++) zb[i] = INF_Z;
}

static void tri(uint8_t *rgb, float *zb, int w, int h, const double *xs, const double *ys,
                const double *zs, uint8_t r, uint8_t g, uint8_t b) {
    int minx = (int)floor(xs[0] < xs[1] ? (xs[0] < xs[2] ? xs[0] : xs[2])
                                        : (xs[1] < xs[2] ? xs[1] : xs[2]));
    int maxx = (int)ceil(xs[0] > xs[1] ? (xs[0] > xs[2] ? xs[0] : xs[2])
                                       : (xs[1] > xs[2] ? xs[1] : xs[2]));
    int miny = (int)floor(ys[0] < ys[1] ? (ys[0] < ys[2] ? ys[0] : ys[2])
                                        : (ys[1] < ys[2] ? ys[1] : ys[2]));
    int maxy = (int)ceil(ys[0] > ys[1] ? (ys[0] > ys[2] ? ys[0] : ys[2])
                                       : (ys[1] > ys[2] ? ys[1] : ys[2]));
    if (minx < 0) minx = 0;
    if (miny < 0) miny = 0;
    if (maxx > w - 1) maxx = w - 1;
    if (maxy > h - 1) maxy = h - 1;
    if (maxx < minx || maxy < miny) return;

    double den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2]);
    if (fabs(den) < 1e-12) return;
    double iz0 = 1.0 / (zs[0] > 1e-6 ? zs[0] : 1e-6);
    double iz1 = 1.0 / (zs[1] > 1e-6 ? zs[1] : 1e-6);
    double iz2 = 1.0 / (zs[2] > 1e-6 ? zs[2] : 1e-6);

    for (int y = miny; y <= maxy; y++) {
        double py = y + 0.5;
        for (int x = minx; x <= maxx; x++) {
            double px = x + 0.5;
            double w0 = ((ys[1] - ys[2]) * (px - xs[2]) + (xs[2] - xs[1]) * (py - ys[2])) / den;
            if (w0 < -1e-6) continue;
            double w1 = ((ys[2] - ys[0]) * (px - xs[2]) + (xs[0] - xs[2]) * (py - ys[2])) / den;
            if (w1 < -1e-6) continue;
            double w2 = 1.0 - w0 - w1;
            if (w2 < -1e-6) continue;
            double iz = w0 * iz0 + w1 * iz1 + w2 * iz2;
            if (iz < 1e-6) continue;
            float z = (float)(1.0 / iz);
            int idx = y * w + x;
            if (z < zb[idx]) {
                zb[idx] = z;
                rgb[idx * 3 + 0] = r;
                rgb[idx * 3 + 1] = g;
                rgb[idx * 3 + 2] = b;
            }
        }
    }
}

// pts: n*6 (three x,y pairs), depth: n*3, colours: n*3 bytes (rgb), or paint_n per-triangle.
void wb_draw_tris(uint8_t *rgb, float *zb, int w, int h, const float *pts, const float *depth,
                  const uint8_t *cols, int n, const int *quads) {
    for (int i = 0; i < n; i++) {
        const float *p = pts + i * 6;
        const float *z = depth + i * 3;
        double xs[3] = {p[0], p[2], p[4]};
        double ys[3] = {p[1], p[3], p[5]};
        double zs[3] = {z[0], z[1], z[2]};
        (void)quads;
        tri(rgb, zb, w, h, xs, ys, zs, cols[i * 3], cols[i * 3 + 1], cols[i * 3 + 2]);
    }
}

// Quads arrive as two triangles already split by the caller (keeps this loop branch-free).

// Camera unprojection: world = cam_pt . M + eye, where M is 3x3 row-major and
// cam_pt = ((x+0.5-cx) * z / f, -(y+0.5-cy) * z / f, z).
static void unproject(int x, int y, float z, const float *M, const float *eye,
                      float f, float cx, float cy, float *out) {
    float px = (x + 0.5f - cx) * z / f;
    float py = -(y + 0.5f - cy) * z / f;
    float pz = z;
    out[0] = px * M[0] + py * M[3] + pz * M[6] + eye[0];
    out[1] = px * M[1] + py * M[4] + pz * M[7] + eye[1];
    out[2] = px * M[2] + py * M[5] + pz * M[8] + eye[2];
}

// Cylindrical decal: sample the texture by ANGLE around the body axis, alpha-tested.
// tex is tw*th*4 RGBA. Returns the number of pixels painted.
int wb_decal_cyl(uint8_t *rgb, const float *zb, int w, int h, const uint8_t *tex, int tw, int th,
                 const float *cx3, float half_h, float theta_max,
                 const float *M, const float *eye, float f, float camcx, float camcy) {
    int painted = 0;
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            float z = zb[y * w + x];
            if (z >= INF_Z) continue;
            float wp[3];
            unproject(x, y, z, M, eye, f, camcx, camcy, wp);
            float dx = wp[0] - cx3[0];
            float dz = wp[2] - cx3[2];
            float theta = atan2f(dx, dz);
            if (fabsf(theta) >= theta_max) continue;
            float hh = (wp[1] - cx3[1]) / (half_h > 1e-6f ? half_h : 1e-6f);
            if (fabsf(hh) >= 1.0f) continue;
            float u = theta / (2.0f * theta_max) + 0.5f;
            float v = 0.5f - hh * 0.5f;
            int tx = (int)(u * (tw - 1));
            int ty = (int)(v * (th - 1));
            if (tx < 0) tx = 0;
            if (ty < 0) ty = 0;
            if (tx > tw - 1) tx = tw - 1;
            if (ty > th - 1) ty = th - 1;
            const uint8_t *s = tex + ((size_t)ty * tw + tx) * 4;
            if (s[3] < 128) continue;
            rgb[(y * w + x) * 3 + 0] = s[0];
            rgb[(y * w + x) * 3 + 1] = s[1];
            rgb[(y * w + x) * 3 + 2] = s[2];
            painted++;
        }
    }
    return painted;
}
