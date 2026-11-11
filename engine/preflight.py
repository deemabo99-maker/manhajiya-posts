"""
Meta pre-flight for a reel or ad video. Nothing goes to the owner without a PASS.

    python3 engine/preflight.py <video.mp4> [spec.json]

Owner's standing rule (12 Nov 2026): Meta's recommendations are applied to every
ad for both brands BEFORE it is sent. This script is that gate. It checks what
can be checked by machine; brand/ADS.md lists the rest.

Checks (sources: Meta's Reels ad specs and the unified 9:16 safe zone, 2026):
  format    9:16 at 1080x1920 or 1440x2560, H.264, yuv420p, constant 30 fps,
            stereo AAC-LC 48 kHz >= 128 kbps, under 4 GB, no edit list (elst) in the MP4
  length    between 6 s and 60 s (ads work best short; Reels allow more)
  borders   no near-flat band along any edge, on frames sampled across the whole
            reel — Instagram flags that as a border / reused content and throttles
            distribution (we were hit by exactly this on 12 Nov 2026)
  safe zone with a spec: every text / CTA / logo element sits inside the unified
            safe zone — clear of the top 14 %, the bottom 35 % and 6 % each side
  cover     a -cover.png exists next to the video
"""
import json
import os
import subprocess
import sys

import numpy as np

TOP, BOTTOM, SIDE = 0.14, 0.35, 0.06
TEXT_TYPES = {"text", "whatsapp", "pill", "check", "step", "chapter", "bar", "scale5",
              "counter", "badge", "seal", "stamp", "quote", "note", "emblem", "logo"}


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                          "-of", "json", path], capture_output=True, text=True).stdout
    return json.loads(out)


def has_edit_list(path):
    with open(path, "rb") as fh:
        head = fh.read(4_000_000)
    return b"elst" in head


def edge_bands(path, samples=12):
    """Std-dev of luminance in the outer 6 % band of each edge, per sampled frame."""
    info = probe(path)
    dur = float(info["format"]["duration"])
    w = int(info["streams"][0]["width"]); h = int(info["streams"][0]["height"])
    worst = {"top": 1e9, "bottom": 1e9, "left": 1e9, "right": 1e9}
    bw, bh = int(w * SIDE), int(h * SIDE)
    for i in range(samples):
        t = dur * (i + 0.5) / samples
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", path,
                              "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                             capture_output=True).stdout
        if len(raw) < w * h:
            continue
        a = np.frombuffer(raw, dtype=np.uint8)[: w * h].reshape(h, w).astype(float)
        for k, band in (("top", a[:bh]), ("bottom", a[-bh:]), ("left", a[:, :bw]), ("right", a[:, -bw:])):
            worst[k] = min(worst[k], band.std())
    return worst


def spec_safe_zone(spec, w=1080, h=1920):
    """Elements of a one-shot spec (stations with dy) or a scene spec (y) that leave
    the safe zone. Only the kinds a viewer must read count; a photo may bleed."""
    bad = []
    top, bot = TOP * h, h - BOTTOM * h
    left, right = SIDE * w, w - SIDE * w

    def check(e, cy, where):
        if e.get("type") not in TEXT_TYPES:
            return
        size = e.get("size", 60)
        half = size * 0.75 if e.get("type") == "text" else e.get("r", 70)
        ex = e.get("x", w / 2)
        if cy - half < top or cy + half > bot or ex < left or ex > right:
            bad.append(f'{where}: "{e.get("text", e.get("type"))}"[:30] centre y={cy:.0f}')

    if "stations" in spec:                       # one-shot: station is framed at centre
        for i, st in enumerate(spec["stations"]):
            for e in st.get("elements", []):
                check(e, h / 2 + e.get("dy", 0), f"station {i + 1}")
    else:
        for i, sc in enumerate(spec.get("scenes", [])):
            for e in sc.get("elements", []):
                cy = e.get("y")
                if cy is None and "bottom" in e:
                    cy = e["bottom"] - e.get("height", e.get("h", 0)) / 2
                if cy is not None:
                    check(e, cy, f"scene {i + 1}")
    return bad


def main(video, spec_path=None):
    results = []

    def res(ok, label, detail=""):
        results.append((ok, label, detail))

    info = probe(video)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    w, h = int(v["width"]), int(v["height"])
    num, den = v["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    dur = float(info["format"]["duration"])
    size = int(info["format"]["size"])

    res((w, h) in ((1080, 1920), (1440, 2560)), "9:16 resolution", f"{w}x{h}")
    res(v["codec_name"] == "h264" and v.get("pix_fmt") == "yuv420p", "H.264 yuv420p",
        f'{v["codec_name"]} {v.get("pix_fmt")}')
    res(abs(fps - 30) < 0.01 and v.get("avg_frame_rate") == v["r_frame_rate"],
        "constant 30 fps", v["r_frame_rate"])
    res(a is not None and a["codec_name"] == "aac" and int(a.get("channels", 0)) == 2
        and int(a.get("bit_rate", 0)) >= 128000, "stereo AAC >= 128 kbps",
        "none" if a is None else f'{a["codec_name"]} {a.get("channels")}ch {int(a.get("bit_rate", 0)) // 1000} kbps')
    res(a is not None and int(a.get("sample_rate", 0)) == 48000, "48 kHz audio",
        "none" if a is None else f'{a.get("sample_rate")} Hz')
    res(size < 4 * 1024 ** 3, "under 4 GB", f"{size / 1048576:.1f} MB")
    res(not has_edit_list(video), "no edit list (elst)")
    res(6 <= dur <= 60, "6-60 s", f"{dur:.1f} s")
    res(os.path.exists(video.replace(".mp4", "-cover.png")), "cover image present")

    bands = edge_bands(video)
    flat = {k: round(s, 1) for k, s in bands.items() if s < 6.0}
    res(not flat, "no flat edge band (border / reused-content flag)",
        "min edge std: " + ", ".join(f"{k} {s:.1f}" for k, s in bands.items()))

    if spec_path:
        spec = json.load(open(spec_path, encoding="utf-8"))
        bad = spec_safe_zone(spec, w, h)
        res(not bad, "text and CTA inside the safe zone (top 14 %, bottom 35 %, sides 6 %)",
            "; ".join(bad[:4]) if bad else "all inside")

    ok_all = all(r[0] for r in results)
    print(f"{'PASS' if ok_all else 'FAIL'}  {video}")
    for ok, label, detail in results:
        print(f"  [{'ok' if ok else 'XX'}] {label}" + (f"  — {detail}" if detail else ""))
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
