/* grab.c — objects: resting on surfaces, reaching for them, and holding them.

SLERM of what the interaction plugins sell:

  GripEditor (TemujinCalidius, free/open)  "visually edit Tool.Grip"
      -> the whole trick is one transform: grip = inverse(hand) * want, and the object rides
         hand * grip forever after. Roblox welds the handle to RightHand with exactly that offset.
  Surface Painter / AcesBrush / Prop Placer  "paint props onto any surface"
      -> placement is a support query: rest the object so its lowest point sits on the surface,
         plus optional grid snap. Floating and sinking are the two failure modes.
  Pick Up & Carry packs  "reach, take, carry"
      -> the reach is an IK target, not a pose: a standoff point along the approach normal,
         then the hand closes onto the object.

Everything is rigid-transform maths on 3x4 row-major matrices (rotation + translation), which is what
Roblox's CFrame is and what the rasteriser already speaks.

Build:  gcc -O2 -march=native -shared -fPIC -o libgrab.so grab.c -lm
*/

#include <math.h>
#include <string.h>

/* inverse of a rigid 3x4: R^T and -R^T t */
void wubu_m4_inv(const float m[12], float out[12])
{
    /* transpose the rotation block */
    out[0] = m[0]; out[1] = m[4]; out[2] = m[8];
    out[4] = m[1]; out[5] = m[5]; out[6] = m[9];
    out[8] = m[2]; out[9] = m[6]; out[10] = m[10];
    float tx = m[3], ty = m[7], tz = m[11];
    out[3] = -(out[0] * tx + out[1] * ty + out[2] * tz);
    out[7] = -(out[4] * tx + out[5] * ty + out[6] * tz);
    out[11] = -(out[8] * tx + out[9] * ty + out[10] * tz);
}

/* a * b, both rigid 3x4 */
void wubu_m4_mul(const float a[12], const float b[12], float out[12])
{
    for (int r = 0; r < 3; ++r) {
        for (int c = 0; c < 3; ++c) {
            float s = 0.0f;
            for (int k = 0; k < 3; ++k) s += a[r * 4 + k] * b[k * 4 + c];
            out[r * 4 + c] = s;
        }
        float s = a[r * 4 + 3];
        for (int k = 0; k < 3; ++k) s += a[r * 4 + k] * b[k * 4 + 3];
        out[r * 4 + 3] = s;
    }
}

/* The grip, as GripEditor exposes it: the offset that, composed onto the hand, puts the object
 * exactly where the author wanted it. */
int wubu_grip(const float hand[12], const float want[12], float out_grip[12])
{
    float inv[12];
    wubu_m4_inv(hand, inv);
    wubu_m4_mul(inv, want, out_grip);
    return 0;
}

/* Move an object's points into world space for a given hand pose and grip. */
int wubu_attach(const float *pts, int n, const float hand[12], const float grip[12], float *out)
{
    float m[12];
    wubu_m4_mul(hand, grip, m);
    for (int i = 0; i < n; ++i) {
        const float *p = pts + i * 3;
        for (int r = 0; r < 3; ++r)
            out[i * 3 + r] = m[r * 4 + 0] * p[0] + m[r * 4 + 1] * p[1] + m[r * 4 + 2] * p[2] + m[r * 4 + 3];
    }
    return 0;
}

/* Rest an object on a surface: translate it so its lowest point touches surface_y, and report how
 * far off it was (positive = it was floating, negative = sunk). */
float wubu_place_on(const float *pts, int n, float surface_y, float *out)
{
    float lo = 1e30f;
    for (int i = 0; i < n; ++i) if (pts[i * 3 + 1] < lo) lo = pts[i * 3 + 1];
    float dy = surface_y - lo;
    for (int i = 0; i < n; ++i) {
        out[i * 3 + 0] = pts[i * 3 + 0];
        out[i * 3 + 1] = pts[i * 3 + 1] + dy;
        out[i * 3 + 2] = pts[i * 3 + 2];
    }
    return dy;
}

/* Where the hand should be to take the object: back along the approach normal by `standoff`,
 * at the object's grip point. `approach` must be unit length and point AWAY from the object. */
void wubu_grab_target(const float obj[3], const float approach[3], float standoff, float out[3])
{
    out[0] = obj[0] + approach[0] * standoff;
    out[1] = obj[1] + approach[1] * standoff;
    out[2] = obj[2] + approach[2] * standoff;
}

/* Grid snap for placement tools. (0 disables on that axis.) */
void wubu_snap3(float *p, float grid)
{
    if (grid <= 0.0f) return;
    for (int i = 0; i < 3; ++i) p[i] = floorf(p[i] / grid + 0.5f) * grid;
}

/* Rigidity check used by the demo: the largest change in any pairwise distance after transforming.
 * A correct attach is 0; anything above a millimetre says points were transformed individually. */
float wubu_rigidity(const float *a, const float *b, int n)
{
    float worst = 0.0f;
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j) {
            float d0 = 0.0f, d1 = 0.0f;
            for (int k = 0; k < 3; ++k) {
                float x0 = a[i * 3 + k] - a[j * 3 + k];
                float x1 = b[i * 3 + k] - b[j * 3 + k];
                d0 += x0 * x0; d1 += x1 * x1;
            }
            float e = fabsf(sqrtf(d0) - sqrtf(d1));
            if (e > worst) worst = e;
        }
    return worst;
}
