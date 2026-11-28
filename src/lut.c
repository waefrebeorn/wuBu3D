/* lut.c — 3D LUT application, because "every look in the references was graded by someone with a LUT"
 * and a statistics match is not that tool.

Two directions, because both are needed:

    wubu_lut_apply   trilinear sample of an N^3 RGB lattice, per pixel, with strength
    wubu_lut_identity / wubu_lut_curves   build one from a set of channel curves, so a look can be
                                          authored here instead of bought

The lattice is stored as N^3 * 3 floats, fastest-varying on the red axis, which is what both .cube
parsers and every grading app assume. Getting the axis order wrong gives a LUT that looks like a
colour channel swap rather than a grade — subtle enough to ship by accident.

    gcc -O2 -march=native -shared -fPIC -o liblut.so lut.c -lm
*/

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static inline float _cl(float v) { return v < 0.0f ? 0.0f : (v > 1.0f ? 1.0f : v); }

int wubu_lut_apply(float *rgb, int n, const float *lut, int size, float strength)
{
    if (!rgb || !lut || size < 2 || n < 1) return -1;
    float s = _cl(strength);
    float maxi = (float)(size - 1);
    for (int i = 0; i < n; ++i) {
        float r = _cl(rgb[i * 3]) * maxi;
        float g = _cl(rgb[i * 3 + 1]) * maxi;
        float b = _cl(rgb[i * 3 + 2]) * maxi;
        int r0 = (int)r, g0 = (int)g, b0 = (int)b;
        if (r0 > size - 2) r0 = size - 2;
        if (g0 > size - 2) g0 = size - 2;
        if (b0 > size - 2) b0 = size - 2;
        float fr = r - r0, fg = g - g0, fb = b - b0;
        const float *o = lut;
        float out[3] = {0.0f, 0.0f, 0.0f};
        for (int c = 0; c < 3; ++c) {
            float acc = 0.0f;
            for (int dr = 0; dr < 2; ++dr) {
                for (int dg = 0; dg < 2; ++dg) {
                    for (int db = 0; db < 2; ++db) {
                        int idx = (((b0 + db) * size + (g0 + dg)) * size + (r0 + dr)) * 3 + c;
                        float w = (dr ? fr : 1.0f - fr) * (dg ? fg : 1.0f - fg) * (db ? fb : 1.0f - fb);
                        acc += o[idx] * w;
                    }
                }
            }
            out[c] = acc;
        }
        for (int c = 0; c < 3; ++c) {
            float v = rgb[i * 3 + c] * (1.0f - s) + out[c] * s;
            rgb[i * 3 + c] = _cl(v);
        }
    }
    return 0;
}

/* a LUT from three channel curves: y = x + amount * x*(1-x)*bend, the classic S-curve shoulder.
   Not a film emulation; a real look needs real measured data. This is the plumbing a look plugs into. */
int wubu_lut_from_curve(float *lut, int size, float contrast, float lift, float gamma)
{
    if (!lut || size < 2) return -1;
    for (int b = 0; b < size; ++b) {
        for (int g = 0; g < size; ++g) {
            for (int r = 0; r < size; ++r) {
                float v[3] = {r / (float)(size - 1), g / (float)(size - 1), b / (float)(size - 1)};
                for (int c = 0; c < 3; ++c) {
                    float x = v[c];
                    x = powf(_cl(x), 1.0f / (gamma > 0.01f ? gamma : 1.0f));
                    x = x + contrast * (x - 0.5f) * (1.0f - fabsf(2.0f * x - 1.0f));
                    x = lift + x * (1.0f - 2.0f * lift);
                    int idx = ((b * size + g) * size + r) * 3 + c;
                    lut[idx] = _cl(x);
                }
            }
        }
    }
    return 0;
}

/* identity, for measuring that apply() is a no-op where it should be */
int wubu_lut_identity(float *lut, int size)
{
    if (!lut || size < 2) return -1;
    for (int b = 0; b < size; ++b)
        for (int g = 0; g < size; ++g)
            for (int r = 0; r < size; ++r) {
                int idx = ((b * size + g) * size + r) * 3;
                lut[idx] = r / (float)(size - 1);
                lut[idx + 1] = g / (float)(size - 1);
                lut[idx + 2] = b / (float)(size - 1);
            }
    return 0;
}

/* .cube export: what every grading app reads back */
int wubu_lut_write_cube(const char *path, const float *lut, int size)
{
    if (!path || !lut || size < 2) return -1;
    FILE *f = fopen(path, "w");
    if (!f) return -2;
    fprintf(f, "TITLE \"wubu3d\"\nLUT_3D_SIZE %d\n", size);
    for (int b = 0; b < size; ++b)
        for (int g = 0; g < size; ++g)
            for (int r = 0; r < size; ++r) {
                int idx = ((b * size + g) * size + r) * 3;
                fprintf(f, "%.6f %.6f %.6f\n", lut[idx], lut[idx + 1], lut[idx + 2]);
            }
    fclose(f);
    return 0;
}
