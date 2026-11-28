"""verify_exr — read our own file the way a compositor would: header channels, then a Z sample."""

import struct
import sys


def read_header(d):
    assert d[:4] == bytes([0x76, 0x2F, 0x31, 0x01]), "not an EXR"
    p = 8
    attrs = {}
    while d[p] != 0:
        e = d.index(0, p); name = d[p:e].decode(); p = e + 1
        e = d.index(0, p); typ = d[p:e].decode(); p = e + 1
        size = struct.unpack_from("<i", d, p)[0]; p += 4
        attrs[name] = (typ, d[p:p + size]); p += size
    return attrs, p + 1


def channel_list(payload):
    out, p = [], 0
    while payload[p] != 0:
        e = payload.index(0, p); name = payload[p:e].decode(); p = e + 1
        ptype, plin = struct.unpack_from("<iB", payload, p); p += 5 + 3
        xs, ys = struct.unpack_from("<ii", payload, p); p += 8
        out.append((name, ptype))
    return out


def half_to_float(h):
    import numpy as np
    return float(np.frombuffer(struct.pack("<H", h), dtype=np.float16)[0])


def main(path):
    d = open(path, "rb").read()
    attrs, _ = read_header(d)
    chans = channel_list(attrs["channels"][1])
    print("channels:", chans)
    w = struct.unpack_from("<i", attrs["dataWindow"][1], 8)[0] + 1
    h = struct.unpack_from("<i", attrs["dataWindow"][1], 12)[0] + 1
    print("size: %dx%d" % (w, h))

    n = len(chans)
    table_at = 8 + len(d[:0])  # offsets follow the header; find first scanline via the table
    # the offset table starts right after the header we just parsed
    _, header_end = read_header(d)
    first = struct.unpack_from("<q", d, header_end)[0]
    print("first scanline offset:", first)
    y, size = struct.unpack_from("<ii", d, first)
    row = d[first + 8: first + 8 + size]
    print("scanline y=%d size=%d (expect %d)" % (y, size, w * n * 2))
    for c, (name, _t) in enumerate(chans):
        vals = [half_to_float(struct.unpack_from("<H", row, (c * w + x) * 2)[0]) for x in (0, w // 2, w - 1)]
        print("  %-2s %s" % (name, ["%.3f" % v for v in vals]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/opt/data/cache/scratch/beauty_z.exr")
