"""
One-shot reels: a single unbroken camera move through a tall world.

    python3 asa/engine/oneshot.py <spec.json> <out.mp4>

Every reel before this was scenes with cuts between them — however the scenes
were dressed, the structure read as a slideshow. Here there are no cuts. The
world is one tall canvas laid out bottom to top, and the camera flies through
it in a single take, slowing at each station and whipping between them.

What makes it read as filmed rather than assembled:
  · parallax — layers at different depths move at different rates
  · speed ramps — the camera eases out of and into every hold
  · whip blur — vertical motion blur scales with camera speed
  · reveals — type and marks appear as the camera arrives, not before
  · a light sweep across the gold when a station lands
  · grain and a vignette on every frame (filmic.py)

Spec shape:
  {"title", "caption", "mood", "bpm", "music_seed", "world_h": 9000,
   "stations": [{"y": 8600, "hold": 1.2, "travel": 0.9, "elements": [...]}, ...],
   "near": true}              # foreground bokeh layer on/off
Elements are the reel engine's sprites (type/text/check/doc/...) with a world
`y` and an optional `layer` of "far" | "mid" | "main" | "near" (default main).
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filmic  # noqa: E402
import kit  # noqa: E402
import reel as R  # noqa: E402
from kit import C, GOLD, rgb  # noqa: E402

RW, RH, FPS = 1080, 1920, 30
LAYERS = {"far": 0.38, "mid": 0.72, "main": 1.0, "near": 1.55}


def smooth(p):
    p = min(max(p, 0.0), 1.0)
    return p * p * (3 - 2 * p)


class Camera:
    """Piecewise path: hold at each station, then ease to the next."""

    def __init__(self, stations, lead=0.4, tail=0.6):
        self.keys = []
        t = lead
        for i, st in enumerate(stations):
            self.keys.append((t, st["y"]))
            t += st.get("hold", 1.2)
            self.keys.append((t, st["y"]))
            if i + 1 < len(stations):
                t += st.get("travel", 0.9)
        self.total = t + tail
        self.first_y = stations[0]["y"]

    def y(self, t):
        if t <= self.keys[0][0]:
            return self.first_y
        for (t0, y0), (t1, y1) in zip(self.keys, self.keys[1:]):
            if t0 <= t <= t1:
                if t1 == t0 or y0 == y1:
                    return y0
                return y0 + (y1 - y0) * smooth((t - t0) / (t1 - t0))
        return self.keys[-1][1]

    def speed(self, t, dt=1 / FPS):
        return abs(self.y(t + dt) - self.y(t - dt)) / (2 * dt)


def world_bg(world_h):
    """Far layer: the brand's girih field running the full height, dark to deep."""
    img = Image.new("RGBA", (RW, world_h))
    g = kit.linear_gradient((RW, world_h), [C["night"], C["deep"], C["emerald"], C["deep"]], 90)
    img.alpha_composite(g)
    d = ImageDraw.Draw(img)
    cell, rr = 190, 190 * 0.42
    col = rgb(C["gold"])[:3] + (26,)
    y, row = 0, 0
    while y < world_h + cell:
        x = cell / 2 if row % 2 else 0
        while x < RW + cell:
            pts = []
            for k in range(16):
                q = rr if k % 2 == 0 else rr * 0.76
                a = math.radians(k * 22.5)
                pts.append((x + q * math.cos(a), y + q * math.sin(a)))
            d.line(pts + [pts[0]], fill=col, width=2)
            x += cell
        y += cell * 0.866
        row += 1
    return img


def world_route(world_h, stations):
    """Mid layer: a thin gold thread joining the stations, with a glow at each."""
    img = Image.new("RGBA", (RW, world_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(540 + 160 * math.sin(i * 1.9), st["y"] * LAYERS["mid"]) for i, st in enumerate(stations)]
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=rgb(C["gold"])[:3] + (120,), width=3)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for x, y in pts:
        gd.ellipse([x - 90, y - 90, x + 90, y + 90], fill=rgb(C["gold"])[:3] + (70,))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img.alpha_composite(glow)
    for x, y in pts:
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=rgb(C["gold_lt"]))
    return img


def bokeh_layer(world_h, seed=5):
    """Near layer: soft gold discs drifting past the lens, the fastest-moving depth."""
    rng = np.random.default_rng(seed)
    img = Image.new("RGBA", (RW, world_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(int(world_h / 110)):
        x, y = rng.uniform(-60, RW + 60), rng.uniform(0, world_h)
        r = rng.uniform(14, 70)
        a = int(rng.uniform(18, 60))
        d.ellipse([x - r, y - r, x + r, y + r], fill=rgb(C["gold_lt"])[:3] + (a,))
    return img.filter(ImageFilter.GaussianBlur(9))


def light_sweep(frame, p, y_center, color=(255, 236, 170)):
    """A diagonal band of light crossing the frame around y_center as p runs 0..1."""
    band = Image.new("L", (RW, RH), 0)
    d = ImageDraw.Draw(band)
    x = -500 + p * (RW + 1000)
    d.polygon([(x, 0), (x + 180, 0), (x - 200, RH), (x - 380, RH)], fill=170)
    band = band.filter(ImageFilter.GaussianBlur(40))
    # confine it vertically to the station it lands on
    v = Image.new("L", (RW, RH), 0)
    ImageDraw.Draw(v).rectangle([0, y_center - 320, RW, y_center + 320], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(90))
    mask = Image.fromarray((np.asarray(band).astype(np.float32) * np.asarray(v) / 255).astype(np.uint8))
    layer = Image.new("RGBA", (RW, RH), color + (0,))
    layer.putalpha(mask)
    return Image.alpha_composite(frame, layer)


def whip_blur(frame, speed):
    """Vertical motion blur proportional to camera speed (px/s)."""
    k = min(int(speed / 220), 26)
    if k < 2:
        return frame
    a = np.asarray(frame).astype(np.float32)
    acc = np.zeros_like(a)
    for i in range(-k, k + 1):
        acc += np.roll(a, i, axis=0)
    return Image.fromarray((acc / (2 * k + 1)).astype(np.uint8), frame.mode)


class OneShot:
    def __init__(self, spec):
        self.spec = spec
        self.world_h = spec.get("world_h", 9000)
        self.stations = spec["stations"]
        self.cam = Camera(self.stations, spec.get("lead", 0.4), spec.get("tail", 0.7))
        self.total = self.cam.total
        self.layers = {
            "far": world_bg(int(self.world_h * LAYERS["far"]) + RH),
            "mid": world_route(int(self.world_h * LAYERS["mid"]) + RH, self.stations),
            "main": Image.new("RGBA", (RW, self.world_h + RH), (0, 0, 0, 0)),
            "near": bokeh_layer(int(self.world_h * LAYERS["near"]) + RH) if spec.get("near", True) else None,
        }
        # elements: build sprites once; each remembers its station's arrival time
        self.items = []
        t = spec.get("lead", 0.4)
        for st in self.stations:
            arrive = t
            for e in st.get("elements", []):
                e = dict(e)
                spr = R.SPRITES[e["type"]](e) if e["type"] != "counter" else None
                self.items.append(dict(e=e, spr=spr, arrive=arrive,
                                       layer=e.get("layer", "main"),
                                       y=st["y"] + e.get("dy", 0), x=e.get("x", 540),
                                       counter=R.Counter(dict(e, y=0)) if e["type"] == "counter" else None))
            t += st.get("hold", 1.2) + st.get("travel", 0.9)
        self.sweeps = [(st["y"], self.cam.keys[2 * i][0]) for i, st in enumerate(self.stations)]

    def frame(self, t):
        # the camera never truly stops: a slow breath through every hold, so the
        # frame is alive even when the route is not moving
        cy = self.cam.y(t) + 16 * math.sin(t * 0.9) + 6 * math.sin(t * 2.3)
        f = Image.new("RGBA", (RW, RH), rgb(C["night"]))
        for name in ("far", "mid", "main", "near"):
            lay = self.layers.get(name)
            if lay is None:
                continue
            k = LAYERS[name]
            top = int(cy * k - RH / 2)
            if name == "near":
                top -= int(t * 26)          # bokeh drifts past on its own
            win = lay.crop((0, max(top, 0), RW, max(top, 0) + RH))
            if top < 0:
                pad = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
                pad.paste(win, (0, -top))
                win = pad
            if name == "main":
                win = self.draw_main(win, t, cy)
            f.alpha_composite(win)
        # arrival light sweep on the station the camera has just reached
        for sy, at in self.sweeps:
            if at + 0.05 <= t < at + 0.95:
                f = light_sweep(f, (t - at - 0.05) / 0.9, int(sy - cy + RH / 2))
        f = whip_blur(f, self.cam.speed(t))
        return filmic.finish(f, t, self.total, None, self.spec.get("grain", 3.0),
                             self.spec.get("vignette", 0.42))

    def draw_main(self, win, t, cy):
        """Main-layer elements, revealed as the camera arrives at their station."""
        top = cy - RH / 2
        for it in self.items:
            if it["layer"] != "main":
                continue
            e = it["e"]
            t0 = it["arrive"] + e.get("t", 0.0)
            if t < t0:
                continue
            x, y = it["x"], it["y"] - top
            if y < -400 or y > RH + 400:
                continue
            if it["counter"]:
                it["counter"].e["x"], it["counter"].e["y"] = x, y
                it["counter"].e["t"] = t0
                it["counter"].draw(win, t)
                continue
            a = R.animate(dict(e, t=t0), t)
            if a is None:
                continue
            if len(a) == 4:
                a = a + (1.0,)
            dx, dy, al, sc, rev = a
            R.place(win, it["spr"], x + dx, y + dy, al, sc, rev)
        return win


def render(spec_path, out_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    shot = OneShot(spec)
    wav = out_path.replace(".mp4", ".wav")
    hits = [k[0] for k in shot.cam.keys[::2]]
    R.music(wav, shot.total, bpm=spec.get("bpm", 96), seed=spec.get("music_seed", 1),
            hits=hits, mood=spec.get("mood", "resolve"))
    if spec.get("vo"):
        R.mix_voice(wav, spec["vo"], shot.total, duck=spec.get("duck", 0.22))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{RW}x{RH}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", str(spec.get("crf", 22)),
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
           "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(shot.total * FPS)
    for i in range(n):
        proc.stdin.write(shot.frame(i / FPS).convert("RGB").tobytes())
        if i % 120 == 0:
            print(f"frame {i}/{n}", flush=True)
    proc.stdin.close()
    proc.wait()
    os.remove(wav)
    ct = spec.get("cover_t", shot.cam.keys[2 * spec.get("cover_station", 1)][0] + 1.0)
    shot.frame(ct).convert("RGB").save(out_path.replace(".mp4", "-cover.png"))
    print("done", out_path, f"{shot.total:.1f}s")


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
