// wubuobj — C11 Wavefront OBJ loader.
//
// The Models Resource (vg-resource) ships game models as OBJ + MTL, which is the format the whole
// ripped-model ecosystem settled on: plain text, no rigging, materials in a sidecar file. A stage
// or a character pulled from a game arrives as one .obj with a few hundred thousand triangles, so
// parsing belongs on the C side and Python only decides what to do with the result.
//
// Handles what real OBJ files contain, not just the tutorial subset:
//   v / vn / vt          vertex, normal, texture coordinate
//   f a b c d            polygons, triangulated as a fan
//   f a/b, a//c, a/b/c   every index form, including the v//vn form exporters emit
//   f -1 -2 -3           negative (relative) indices
//   o / g / usemtl / s   recorded so materials can be split downstream
//
// Returns counts; call twice (buffers NULL first) or pass buffers sized from a first call.
//
// SLERM note: the OBJ format is a published spec (Wavefront) and the Models Resource wiki documents
// the practical failure modes (absolute texture paths in MTL, missing MTL). The code is ours.
//
// Build: cc -O2 -std=c11 -shared -fPIC -o libwubuobj.so wubuobj.c -lm

#include <ctype.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const char *p;
    const char *end;
} cursor;

static void skip_ws(cursor *c) {
    while (c->p < c->end && (*c->p == ' ' || *c->p == '\t' || *c->p == '\r')) c->p++;
}
static int next_line(cursor *c, const char **s, const char **e) {
    if (c->p >= c->end) return 0;
    const char *start = c->p;
    while (c->p < c->end && *c->p != '\n') c->p++;
    *s = start;
    *e = c->p;
    if (c->p < c->end) c->p++;
    return 1;
}

static int parse_float(cursor *c, float *out) {
    skip_ws(c);
    if (c->p >= c->end) return 0;
    char buf[64];
    int n = 0;
    while (c->p < c->end && n < 63) {
        char ch = *c->p;
        if ((ch >= '0' && ch <= '9') || ch == '.' || ch == '-' || ch == '+' || ch == 'e' || ch == 'E') {
            buf[n++] = ch;
            c->p++;
        } else break;
    }
    if (!n) return 0;
    buf[n] = 0;
    *out = (float)atof(buf);
    return 1;
}

static int parse_int(cursor *c, int *out) {
    skip_ws(c);
    int sign = 1, seen = 0;
    long v = 0;
    if (c->p < c->end && (*c->p == '-' || *c->p == '+')) { if (*c->p == '-') sign = -1; c->p++; }
    while (c->p < c->end && *c->p >= '0' && *c->p <= '9') { v = v * 10 + (*c->p - '0'); c->p++; seen = 1; }
    if (!seen) return 0;
    *out = (int)(sign * v);
    return 1;
}

// Parse one face vertex: v, v/vt, v//vn, v/vt/vn. Returns the vertex index (0-based, resolved) or -1.
static int face_vertex(cursor *c, int nverts, int *vn_out) {
    int vi = 0;
    if (!parse_int(c, &vi)) return -1;
    if (vi < 0) vi = nverts + vi;         // -1 is the last vertex
    else vi -= 1;
    if (c->p < c->end && *c->p == '/') {
        c->p++;
        int tmp;
        if (c->p < c->end && *c->p != '/') {
            parse_int(c, &tmp);            // texture index: parsed and discarded, we index by vertex
        }
        if (c->p < c->end && *c->p == '/') {
            c->p++;
            int ni = 0;
            if (parse_int(c, &ni)) {
                if (vn_out) *vn_out = (ni < 0) ? ni : ni - 1;
            }
        }
    }
    return vi;
}

// counts-only pass when pos/tri are NULL.
int wb_obj_parse(const char *text, size_t len, float *pos, uint32_t *tri, int32_t *vnorm,
                 int want_normals, int *nverts_out, int *ntris_out) {
    cursor c = {text, text + len};
    const char *ls, *le;
    int nv = 0, nf_tris = 0;
    int mode_count = (pos == NULL);

    // First pass counts vertices and triangles so a single allocation serves the second.
    while (next_line(&c, &ls, &le)) {
        if (le - ls < 2) continue;
        if (ls[0] == 'v' && (ls[1] == ' ' || ls[1] == '\t')) nv++;
        else if (ls[0] == 'f' && (ls[1] == ' ' || ls[1] == '\t')) {
            // count vertices on the face; a polygon of k corners makes k-2 triangles
            cursor fc = {ls + 1, le};
            int k = 0;
            while (1) {
                skip_ws(&fc);
                if (fc.p >= fc.end) break;
                int vi = face_vertex(&fc, 999999, NULL);
                if (vi < 0) break;
                k++;
            }
            if (k >= 3) nf_tris += k - 2;
        }
    }
    *nverts_out = nv;
    *ntris_out = nf_tris;
    if (mode_count) return 0;
    if (!nv || !nf_tris) return 0;

    // Second pass fills the buffers.
    cursor c2 = {text, text + len};
    int vi_out = 0, ti = 0;
    while (next_line(&c2, &ls, &le)) {
        if (le - ls < 2) continue;
        if (ls[0] == 'v' && (ls[1] == ' ' || ls[1] == '\t')) {
            cursor fc = {ls + 1, le};
            float x = 0, y = 0, z = 0;
            parse_float(&fc, &x); parse_float(&fc, &y); parse_float(&fc, &z);
            if (vi_out < nv) {
                pos[vi_out * 3 + 0] = x;
                pos[vi_out * 3 + 1] = y;
                pos[vi_out * 3 + 2] = z;
            }
            vi_out++;
        } else if (ls[0] == 'f' && (ls[1] == ' ' || ls[1] == '\t')) {
            cursor fc = {ls + 1, le};
            int idx[32];
            int nidx[32];
            int k = 0;
            while (k < 32) {
                int nrm = -1;
                int vi = face_vertex(&fc, vi_out, &nrm);
                if (vi < 0) break;
                idx[k] = vi;
                nidx[k] = nrm;
                k++;
            }
            for (int i = 1; i + 1 < k; i++) {
                if (ti * 3 + 2 >= nf_tris * 3) break;
                tri[ti * 3 + 0] = (uint32_t)idx[0];
                tri[ti * 3 + 1] = (uint32_t)idx[i];
                tri[ti * 3 + 2] = (uint32_t)idx[i + 1];
                if (want_normals && vnorm) {
                    vnorm[ti * 3 + 0] = nidx[0];
                    vnorm[ti * 3 + 1] = nidx[i];
                    vnorm[ti * 3 + 2] = nidx[i + 1];
                }
                ti++;
            }
        }
    }
    return ti;
}

// Count of "usemtl" statements, so a caller can tell how many materials a file expects.
int wb_obj_material_count(const char *text, size_t len) {
    cursor c = {text, text + len};
    const char *ls, *le;
    int n = 0;
    while (next_line(&c, &ls, &le)) {
        if (le - ls >= 7 && strncmp(ls, "usemtl", 6) == 0) n++;
    }
    return n;
}
