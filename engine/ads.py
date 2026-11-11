"""
Build a Meta ad reel in every placement ratio, for either brand.

    python3 engine/ads.py posts/ads-01/manhajiya-thesis-ad.json
    python3 engine/ads.py asa/posts/ads-01/asa-thesis-ad.json

Renders <stem>-9x16.mp4 with the reel engine that belongs to the spec's brand
(engine/reel.py at the repo root, asa/engine/reel.py under asa/), then cuts
<stem>-4x5.mp4 from it and writes <stem>-cover.png.

Why the 4:5 cut is taken from the TOP and not the centre: both ad reels open
with their hook near the top of the 1080x1920 frame, so a centre cut (y=285)
sliced the first line off every headline. Cutting 1080x1350 from y=0 keeps the
whole hook, the body and the CTA, and loses only the empty floor under them.
Compose ad scenes for that: everything that must survive the 4:5 placement goes
in y 0-1350, and a person may stand below it.
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROP_TOP = 0          # 4:5 is cut from the top edge; see the module docstring
RATIOS = {"4x5": f"crop=1080:1350:0:{CROP_TOP}"}


def run(*cmd):
    subprocess.run(cmd, check=True)


def build(spec_path):
    spec_path = os.path.abspath(spec_path)
    rel = os.path.relpath(spec_path, ROOT)
    engine = os.path.join(ROOT, "asa/engine/reel.py") if rel.startswith("asa" + os.sep) \
        else os.path.join(ROOT, "engine/reel.py")
    stem = spec_path[:-5]          # drop ".json"
    wide = f"{stem}-9x16.mp4"

    run(sys.executable, engine, spec_path, wide)

    # the reel engine writes its cover next to the video it rendered
    rendered_cover = f"{stem}-9x16-cover.png"
    cover = f"{stem}-cover.png"
    if os.path.exists(rendered_cover):
        shutil.move(rendered_cover, cover)

    for name, vf in RATIOS.items():
        out = f"{stem}-{name}.mp4"
        run("ffmpeg", "-y", "-loglevel", "error", "-i", wide, "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "copy", "-movflags", "+faststart", "-use_editlist", "0", out)
        print("wrote", os.path.relpath(out, ROOT))
    print("wrote", os.path.relpath(wide, ROOT), "and", os.path.relpath(cover, ROOT))


if __name__ == "__main__":
    build(sys.argv[1])
