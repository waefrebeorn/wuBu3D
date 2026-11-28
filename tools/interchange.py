"""deliver — the three interchange formats a video pipeline is expected to hand over.

    srt     captions with real timings, because burnt-in words are not subtitles
    otio    an edit a human can open in Resolve or Premiere, not a Python list
    prores  a mezzanine codec, because h264 is a delivery format and everyone downstream wants to
            grade something that has not already been compressed to death

Each is small. Each is a separate rejection at a client review if it is missing.
"""

import json
import shutil
import subprocess


def _ts(t, comma=True):
    t = max(0.0, float(t))
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s += 1; ms = 0
    sep = "," if comma else "."
    return "%02d:%02d:%02d%s%03d" % (h, m, s, sep, ms)


def srt(lines, path):
    """lines: [(t_start, t_end, text)] -> a .srt with 1-based indices."""
    out = []
    for i, (a, b, text) in enumerate(lines, 1):
        out.append("%d\n%s --> %s\n%s\n" % (i, _ts(a), _ts(b), text.strip()))
    open(path, "w").write("\n".join(out))
    return len(lines)


def otio(shots, path, fps=24.0, name="wubu3d"):
    """shots: [(t_start, t_end, label)] -> an OpenTimelineIO JSON timeline.

    The schema strings are what make it openable: a file with the right shape but no OTIO_SCHEMA keys
    is JSON that no editorial tool will import.
    """
    clips = []
    for (a, b, label) in shots:
        dur = max(1, int(round((b - a) * fps)))
        start = int(round(a * fps))
        clips.append({
            "OTIO_SCHEMA": "Clip.1",
            "name": str(label),
            "source_range": {
                "OTIO_SCHEMA": "TimeRange.1",
                "duration": {"OTIO_SCHEMA": "RationalTime.1", "rate": fps, "value": float(dur)},
                "start_time": {"OTIO_SCHEMA": "RationalTime.1", "rate": fps, "value": 0.0},
            },
            "metadata": {"wubu": {"shot_start_frame": start}},
        })
    total = max([int(round(b * fps)) for (_a, b, _l) in shots], default=0)
    tl = {
        "OTIO_SCHEMA": "Timeline.1",
        "name": name,
        "global_start_time": {"OTIO_SCHEMA": "RationalTime.1", "rate": fps, "value": 0.0},
        "tracks": {
            "OTIO_SCHEMA": "Stack.1",
            "name": "shots",
            "children": [{
                "OTIO_SCHEMA": "Track.1",
                "name": "V1",
                "kind": "Video",
                "children": clips,
                "metadata": {"wubu": {"total_frames": total}},
            }],
            "metadata": {},
        },
        "metadata": {},
    }
    open(path, "w").write(json.dumps(tl, indent=1))
    return len(clips), total


def prores(src_mp4, out_mov, profile=3):
    """ffmpeg's prores_ks. profile 3 = HQ, which is the mezzanine every post house expects."""
    if not shutil.which("ffmpeg"):
        return None, "ffmpeg not found"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src_mp4, "-c:v", "prores_ks", "-profile:v", str(profile),
           "-pix_fmt", "yuv422p10le", "-c:a", "pcm_s16le", out_mov]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return None, (r.stderr or "").strip()[:200]
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "stream=codec_name,pix_fmt,width,height", "-of", "default=nw=1", out_mov],
                           capture_output=True, text=True)
    return (probe.stdout or "").strip(), None


def edl(shots, path, fps=24.0, title="wubu3d"):
    """CMX3600 EDL: still the lingua franca for conform, and 8 lines per event."""
    def tc(fr):
        f = int(round(fr))
        return "%02d:%02d:%02d:%02d" % (f // (3600 * int(fps)), (f // (60 * int(fps))) % 60,
                                        (f // int(fps)) % 60, f % int(fps))
    lines = ["TITLE: %s" % title, "FCM: NON-DROP FRAME", ""]
    for i, (a, b, label) in enumerate(shots, 1):
        lines.append("%03d  AX       V     C        %s %s %s %s"
                     % (i, tc(a * fps), tc(b * fps), tc(a * fps), tc(b * fps)))
        lines.append("* FROM CLIP NAME: %s" % label)
        lines.append("")
    open(path, "w").write("\n".join(lines))
    return len(shots)
