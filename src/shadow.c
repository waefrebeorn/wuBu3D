/* shadow.c — a real shadow map, so light stops passing through walls.

docs/ENGINE_GAPS.md ranked this third: every engine has cascaded shadow maps, and we had a grey
ellipse under the feet. The pass is small because the rasteriser already exists — render depth from
the light, then ask it a question per pixel.

    gcc -O2 -march=native -shared -fPIC -o libshadow.so shadow.c -lm
*/

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* Build a light-space view matrix looking from `eye` at `target` (row-major 3x4). */
static void look_at(const float eye[3], const float target[3], float m[12])
{
    float fx = target[0] - eye[0], fy = target[1] - eye[1], fz = target[2] - eye[2];
    float fl = sqrtf(fx * fx + fy * fy + fz * fz) + 1e-9f;
    fx /= fl; fy /= fl; fz /= fl;
    float ux = 0.0f, uy = 1.0f, uz = 0.0f;
    if (fabsf(fy) > 0.95f) { ux = 1.0f; uy = 0.0f; uz = 0.0f; }
    float sx = fy * uz - fz * uy, sy = fz * ux - fx * uz, sz = fx * uy - fy * ux;
    float sl = sqrtf(sx * sx + sy * sy + sz * sz) + 1e-9f;
    sx /= sl; sy /= sl; sz /= sl;
    float vx = sy * fz - sz * fy, vy = sz * fx - sx * fz, vz = sx * fy - sy * fx;
    m[0] = sx; m[1] = sy; m[2] = sz; m[3] = -(sx * eye[0] + sy * eye[1] + sz * eye[2]);
    m[4] = vx; m[5] = vy; m[6] = vz; m[7] = -(vx * eye[0] + vy * eye[1] + vz * eye[2]);
    /* depth along the light's forward axis: +f, not -f. With the negated row every vertex came out
       with negative z and was rejected, so the map was empty and everything read as fully lit. */
    m[8] = fx; m[9] = fy; m[10] = fz;
    m[11] = -(fx * eye[0] + fy * eye[1] + fz * eye[2]);
}

/* Render depth from the light. `tris` is n*9 (three world-space vertices per triangle). */
int wubu_shadowmap(const float *tris, int ntris, const float eye[3], const float target[3],
                   int size, float fov_deg, float *depth_out)
{
    if (!tris || !depth_out || size < 8) return -1;
    float m[12];
    look_at(eye, target, m);
    float tan_half = tanf(fov_deg * 0.5f * 3.14159265f / 180.0f);
    for (int i = 0; i < size * size; ++i) depth_out[i] = 1e30f;

    for (int t = 0; t < ntris; ++t) {
        float sx[3], sy[3], sz[3];
        int bad = 0;
        for (int k = 0; k < 3; ++k) {
            const float *p = tris + (t * 3 + k) * 3;
            float x = m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + m[3];
            float y = m[4] * p[0] + m[5] * p[1] + m[6] * p[2] + m[7];
            float z = m[8] * p[0] + m[9] * p[1] + m[10] * p[2] + m[11];
            if (z <= 0.05f) bad = 1;
            sx[k] = (x / (z * tan_half) * 0.5f + 0.5f) * size;
            sy[k] = (0.5f - y / (z * tan_half) * 0.5f) * size;
            sz[k] = z;
        }
        if (bad) continue;
        float minx = fminf(sx[0], fminf(sx[1], sx[2])), maxx = fmaxf(sx[0], fmaxf(sx[1], sx[2]));
        float miny = fminf(sy[0], fminf(sy[1], sy[2])), maxy = fmaxf(sy[0], fmaxf(sy[1], sy[2]));
        int x0 = (int)minx, x1 = (int)ceilf(maxx), y0 = (int)miny, y1 = (int)ceilf(maxy);
        if (x0 < 0) x0 = 0;
        if (y0 < 0) y0 = 0;
        if (x1 > size - 1) x1 = size - 1;
        if (y1 > size - 1) y1 = size - 1;
        if (x0 > x1 || y0 > y1) continue;
        float area = (sx[1] - sx[0]) * (sy[2] - sy[0]) - (sx[2] - sx[0]) * (sy[1] - sy[0]);
        if (fabsf(area) < 1e-9f) continue;
        float ia = 1.0f / area;
        for (int y = y0; y <= y1; ++y) {
            for (int x = x0; x <= x1; ++x) {
                float px = x + 0.5f, py = y + 0.5f;
                float w0 = ((sx[1] - px) * (sy[2] - py) - (sx[2] - px) * (sy[1] - py)) * ia;
                float w1 = ((sx[2] - px) * (sy[0] - py) - (sx[0] - px) * (sy[2] - py)) * ia;
                float w2 = 1.0f - w0 - w1;
                if (w0 < 0.0f || w1 < 0.0f || w2 < 0.0f) continue;
                float z = w0 * sz[0] + w1 * sz[1] + w2 * sz[2];
                float *d = &depth_out[y * size + x];
                if (z < *d) *d = z;
            }
        }
    }
    return 0;
}

/* Shadow test for a world point, with a 2x2 PCF tap and a slope-ish bias.
 * Returns 1 = lit, 0 = shadowed. */
float wubu_shadow_test(const float *depth, int size, const float eye[3], const float target[3],
                       float fov_deg, const float p[3], float bias)
{
    float m[12];
    look_at(eye, target, m);
    float tan_half = tanf(fov_deg * 0.5f * 3.14159265f / 180.0f);
    float x = m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + m[3];
    float y = m[4] * p[0] + m[5] * p[1] + m[6] * p[2] + m[7];
    float z = m[8] * p[0] + m[9] * p[1] + m[10] * p[2] + m[11];
    if (z <= 0.05f) return 1.0f;
    float u = (x / (z * tan_half) * 0.5f + 0.5f) * size;
    float v = (0.5f - y / (z * tan_half) * 0.5f) * size;
    int lit = 0, taps = 0;
    for (int dy = 0; dy < 2; ++dy) {
        for (int dx = 0; dx < 2; ++dx) {
            int ix = (int)(u + dx - 0.5f), iy = (int)(v + dy - 0.5f);
            if (ix < 0 || iy < 0 || ix >= size || iy >= size) { lit++; taps++; continue; }
            float d = depth[iy * size + ix];
            taps++;
            if (d + bias > z) lit++;
        }
    }
    return taps ? (float)lit / (float)taps : 1.0f;
}


/* Floor shadows in one pass: for every screen pixel, intersect the ground plane, transform the hit
 * into light space, and test the map. Writing this as one C loop instead of a per-pixel Python call
 * is the difference between 0.2 s and two minutes at video resolution. */
int wubu_shadow_floor(const float *depth, int size, const float light_eye[3],
                      const float light_target[3], float light_fov,
                      const float cam_eye[3], const float cam_target[3], float cam_fov,
                      int w, int h, float plane_y, float bias, float *out)
{
    if (!depth || !out || size < 8) return -1;
    float fx = cam_target[0] - cam_eye[0], fy = cam_target[1] - cam_eye[1], fz = cam_target[2] - cam_eye[2];
    float fl = sqrtf(fx * fx + fy * fy + fz * fz) + 1e-9f;
    fx /= fl; fy /= fl; fz /= fl;
    float ux = 0.0f, uy = 1.0f, uz = 0.0f;
    if (fabsf(fy) > 0.95f) { ux = 1.0f; uy = 0.0f; uz = 0.0f; }
    float sx = fy * uz - fz * uy, sy = fz * ux - fx * uz, sz = fx * uy - fy * ux;
    float sl = sqrtf(sx * sx + sy * sy + sz * sz) + 1e-9f;
    sx /= sl; sy /= sl; sz /= sl;
    float vx = sy * fz - sz * fy, vy = sz * fx - sx * fz, vz = sx * fy - sy * fx;
    float tan_half = tanf(cam_fov * 0.5f * 3.14159265f / 180.0f);
    float aspect = (float)w / (float)h;

    for (int py = 0; py < h; ++py) {
        float ndc_y = 1.0f - 2.0f * ((float)py + 0.5f) / (float)h;
        for (int px = 0; px < w; ++px) {
            float ndc_x = 2.0f * ((float)px + 0.5f) / (float)w - 1.0f;
            float dx = fx + sx * ndc_x * tan_half * aspect + vx * ndc_y * tan_half;
            float dy = fy + sy * ndc_x * tan_half * aspect + vy * ndc_y * tan_half;
            float dz = fz + sz * ndc_x * tan_half * aspect + vz * ndc_y * tan_half;
            if (fabsf(dy) < 1e-5f) { out[py * w + px] = 1.0f; continue; }
            float t = (plane_y - cam_eye[1]) / dy;
            if (t <= 0.0f) { out[py * w + px] = 1.0f; continue; }
            float hit[3] = {cam_eye[0] + dx * t, plane_y, cam_eye[2] + dz * t};
            out[py * w + px] = wubu_shadow_test(depth, size, light_eye, light_target, light_fov,
                                                hit, bias);
        }
    }
    return 0;
}
