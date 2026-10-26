"""
Weekly reel renderer for المنهجية (1080 x 1920, 30 fps, H.264 + original music).

    python3 engine/reel.py posts/batch-01/reel.json posts/batch-01/reel.mp4

A reel is a list of scenes. Each scene has a background and elements; every
element is pre-rendered once as a sprite and then animated (slide / pop / fade)
while frames are piped straight into ffmpeg. Text stays inside the Reels safe
zone (y 260-1450) so Instagram/Facebook overlays never cover it.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402
from kit import C, RING, WARM, font, linear_gradient, rgb  # noqa: E402

RW, RH, FPS = 1080, 1920, 30
SS = 2  # supersampling for sprites (kit fonts are already 2x)
XFADE = 0.35


# ------------------------------------------------------------------ easing
def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_out_back(x, k=1.7):
    x -= 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


# ------------------------------------------------------------------ sprites
def _finish(img2x):
    return img2x.resize((img2x.width // SS, img2x.height // SS), Image.LANCZOS)


def _kw(t):
    return {"direction": "rtl", "language": "ar"} if any("؀" <= c <= "ۿ" for c in t) else {}


def sprite_text(text, fname, size, wght=None, color="#FFFFFF", gradient=None, shadow=True):
    f = font(fname, size, wght)
    l, t, r, b = f.getbbox(text, **_kw(text))
    pad = 40 * SS
    w, h = (r - l) + pad * 2, (b - t) + pad * 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - l, pad - t), text, font=f, fill=255, **_kw(text))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(10 * SS)).point(lambda v: int(v * 0.45))
        shl = Image.new("RGBA", (w, h), (20, 4, 30, 0))
        shl.putalpha(sh)
        img.alpha_composite(shl, (0, 8 * SS))
    if gradient:
        g = linear_gradient((w, h), gradient, 0)
    else:
        g = Image.new("RGBA", (w, h), rgb(color))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(g, (0, 0), mask)
    img.alpha_composite(layer)
    return _finish(img)


def _round_rect(size, radius, fill=None, gradient=None, angle=0, outline=None, width=0, shadow=False):
    w, h = size
    m = 30 * SS if shadow else 0
    img = Image.new("RGBA", (w * SS + 2 * m, h * SS + 2 * m), (0, 0, 0, 0))
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([m, m, m + w * SS, m + h * SS], radius=radius * SS, fill=255)
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(14 * SS)).point(lambda v: int(v * 0.35))
        shl = Image.new("RGBA", img.size, (20, 4, 30, 0))
        shl.putalpha(sh)
        img.alpha_composite(shl, (0, 10 * SS))
        img = img.crop((0, 0, img.width, img.height))
    if gradient or fill:
        src = linear_gradient(img.size, gradient, angle) if gradient else Image.new("RGBA", img.size, rgb(fill))
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        layer.paste(src, (0, 0), mask)
        img.alpha_composite(layer)
    if outline:
        ol = Image.new("L", img.size, 0)
        ImageDraw.Draw(ol).rounded_rectangle([m, m, m + w * SS, m + h * SS], radius=radius * SS,
                                             outline=255, width=int(width * SS))
        src = linear_gradient(img.size, outline, 0) if isinstance(outline, list) else Image.new("RGBA", img.size, rgb(outline))
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        layer.paste(src, (0, 0), ol)
        img.alpha_composite(layer)
    return img, m


def sprite_pill(text, size=40, fg="#FFFFFF", bg=None, gradient=None, outline=None, fname="almarai-xb", padx=46, h=None):
    f = font(fname, size)
    l, t, r, b = f.getbbox(text, **_kw(text))
    tw = (r - l) / SS
    ph = h or size * 2.0
    pw = tw + padx * 2
    img, m = _round_rect((int(pw), int(ph)), ph / 2, fill=bg, gradient=gradient, outline=outline, width=3,
                         shadow=bool(bg or gradient))
    d = ImageDraw.Draw(img)
    d.text((m + pw * SS / 2, m + ph * SS / 2), text, font=f, fill=rgb(fg), anchor="mm", **_kw(text))
    return _finish(img)


def sprite_whatsapp(scale=1.0):
    num = kit.CONTACT["whatsapp"]
    fnum = font("latin", 40 * scale)
    flab = font("almarai-xb", 36 * scale)
    nw = (fnum.getbbox(num)[2] - fnum.getbbox(num)[0]) / SS
    lw = (flab.getbbox("واتساب", **_kw("واتساب"))[2] - flab.getbbox("واتساب", **_kw("واتساب"))[0]) / SS
    ph = 104 * scale
    pw = nw + lw + 170 * scale
    img, m = _round_rect((int(pw), int(ph)), ph / 2, fill=C["green"], shadow=True)
    d = ImageDraw.Draw(img)
    gx, gy = m + (pw - 58 * scale) * SS, m + ph / 2 * SS
    r = 30 * scale * SS
    d.polygon([(gx - 0.7 * r, gy + 0.55 * r), (gx - 1.15 * r, gy + 1.15 * r), (gx - 0.15 * r, gy + 0.95 * r)], fill="#FFFFFF")
    d.ellipse([gx - r, gy - r, gx + r, gy + r], fill="#FFFFFF")
    d.text((gx, gy + 2 * SS), "☎", font=font("latin", 34 * scale), fill=rgb(C["green"]), anchor="mm")
    d.text((gx - 52 * scale * SS, gy), "واتساب", font=flab, fill="#FFFFFF", anchor="rm", **_kw("واتساب"))
    d.text((m + 34 * scale * SS, gy + 2 * SS), num, font=fnum, fill="#FFFFFF", anchor="lm")
    return _finish(img)


def sprite_logo(width):
    lg = Image.open(kit.LOGO).convert("RGBA")
    h = int(width * lg.height / lg.width)
    pad = 26
    img, m = _round_rect((width + 2 * pad, h + 2 * pad), 40, fill="#FFFFFF", shadow=True)
    lg2 = lg.resize((width * SS, h * SS), Image.LANCZOS)
    img.alpha_composite(lg2, (m + pad * SS, m + pad * SS))
    return _finish(img)


def sprite_card(icon, title, desc, w=900, h=170, dark=False):
    img, m = _round_rect((w, h), 34, fill="#FFFFFF", shadow=True)
    d = ImageDraw.Draw(img)
    # icon disc (right side, RTL)
    cx, cy, r = m + (w - 88) * SS, m + h / 2 * SS, 52 * SS
    disc = Image.new("L", img.size, 0)
    ImageDraw.Draw(disc).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    g = linear_gradient(img.size, RING, 45)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(g, (0, 0), disc)
    img.alpha_composite(layer)
    d.text((cx, cy + 2 * SS), icon, font=font("latin", 44), fill="#FFFFFF", anchor="mm")
    d.text((cx - 90 * SS, cy - 26 * SS), title, font=font("kufi", 36, 800), fill=rgb(C["ink"]), anchor="rm", **_kw(title))
    d.text((cx - 90 * SS, cy + 32 * SS), desc, font=font("almarai", 30), fill=rgb(C["muted"]), anchor="rm", **_kw(desc))
    return _finish(img)


def sprite_doc(w=150, h=186):
    img, m = _round_rect((w, h), 18, fill="#FFFFFF", shadow=True)
    d = ImageDraw.Draw(img)
    x0, y0 = m + 22 * SS, m + 26 * SS
    d.rounded_rectangle([x0, y0, x0 + (w - 44) * SS, y0 + 16 * SS], radius=8 * SS, fill=rgb(C["purple"]))
    for k in range(4):
        yy = y0 + (36 + k * 22) * SS
        ww = (w - 44) * (0.9 if k % 2 == 0 else 0.65)
        d.rounded_rectangle([x0, yy, x0 + ww * SS, yy + 10 * SS], radius=5 * SS, fill=rgb("#E4DAEC"))
    # mini bars
    bx = x0
    for k, hh in enumerate([22, 34, 28, 44]):
        d.rounded_rectangle([bx + k * 24 * SS, m + (h - 24 - hh) * SS, bx + (k * 24 + 14) * SS, m + (h - 24) * SS],
                            radius=4 * SS, fill=rgb([C["gold"], C["orange"], C["pink"], C["purple"]][k]))
    return _finish(img)


def sprite_table_header(cols, w=900, h=96):
    img, m = _round_rect((w, h), 26, gradient=[C["violet"], C["purple"], C["magenta"]], angle=0, shadow=True)
    d = ImageDraw.Draw(img)
    cw = w / len(cols)
    for i, c in enumerate(cols):
        cx = m + (w - cw * (i + 0.5)) * SS
        d.text((cx, m + h / 2 * SS), c, font=font("almarai-xb", 32), fill="#FFFFFF", anchor="mm", **_kw(c))
    return _finish(img)


def sprite_table_row(cells, w=900, h=88, idx=0):
    img, m = _round_rect((w, h), 22, fill="#FFFFFF" if idx % 2 == 0 else "#F7F2FA", shadow=True)
    d = ImageDraw.Draw(img)
    n = len(cells)
    cw = w / n
    for i, c in enumerate(cells):
        cx = m + (w - cw * (i + 0.5)) * SS
        cy = m + h / 2 * SS
        if c == "#bar":
            bw = (cw * 0.55) * SS
            d.rounded_rectangle([cx - bw / 2, cy - 9 * SS, cx + bw / 2, cy + 9 * SS], radius=9 * SS,
                                fill=rgb(["#E9D5F5", "#FBE0C2"][i % 2]))
        elif c == "#ok":
            r = 26 * SS
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(C["green"]))
            d.text((cx, cy + 1 * SS), "✓", font=font("latin", 30), fill="#FFFFFF", anchor="mm")
        else:
            fn = font("latin", 30) if c.isascii() else font("almarai-bold", 30)
            d.text((cx, cy), c, font=fn, fill=rgb(C["ink"]), anchor="mm", **_kw(c))
    return _finish(img)


def sprite_ring(r, width, alpha=255):
    size = int(2 * r + 4)
    img = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    c = size * SS / 2
    d.ellipse([c - r * SS, c - r * SS, c + r * SS, c + r * SS], fill=alpha)
    d.ellipse([c - (r - width) * SS, c - (r - width) * SS, c + (r - width) * SS, c + (r - width) * SS], fill=0)
    img.paste(linear_gradient(img.size, RING, 45), (0, 0), mask)
    return _finish(img)


def build_sprite(e):
    k = e["type"]
    if k == "text":
        return sprite_text(e["text"], e.get("font", "kufi"), e.get("size", 80), e.get("wght"),
                           e.get("color", "#FFFFFF"), WARM[::-1] if e.get("gradient") == "warm" else
                           (RING[::-1] if e.get("gradient") == "ring" else None), e.get("shadow", True))
    if k == "pill":
        grad = RING if e.get("gradient") == "ring" else (WARM[::-1] if e.get("gradient") == "warm" else None)
        return sprite_pill(e["text"], e.get("size", 40), e.get("fg", "#FFFFFF"), e.get("bg"), grad, e.get("outline"))
    if k == "whatsapp":
        return sprite_whatsapp(e.get("scale", 1.0))
    if k == "logo":
        return sprite_logo(e.get("width", 300))
    if k == "card":
        return sprite_card(e["icon"], e["title"], e["desc"])
    if k == "doc":
        return sprite_doc()
    if k == "thead":
        return sprite_table_header(e["cols"])
    if k == "trow":
        return sprite_table_row(e["cells"], idx=e.get("idx", 0))
    if k == "ring":
        return sprite_ring(e["r"], e.get("width", 14), e.get("alpha", 255))
    raise ValueError(k)


# ------------------------------------------------------------------ backgrounds
def background(kind, seed=0):
    if kind == "dark":
        bg = linear_gradient((RW, RH), [C["night"], "#3A1250", C["plum"]], 115)
    elif kind == "purple":
        bg = linear_gradient((RW, RH), [C["purple"], C["violet"], C["plum"]], 125)
    else:
        bg = linear_gradient((RW, RH), ["#FFFFFF", C["paper"], C["mist"]], 90)
    d = ImageDraw.Draw(bg)
    dot = (255, 255, 255, 70) if kind != "light" else rgb(C["purple"])[:3] + (90,)
    ox, oy = (70, 190) if seed % 2 == 0 else (820, 1560)
    for i in range(7):
        for j in range(4):
            cx, cy = ox + i * 26, oy + j * 26
            d.ellipse([cx - 3.5, cy - 3.5, cx + 3.5, cy + 3.5], fill=dot)
    ink = (255, 255, 255, 220) if kind != "light" else rgb(C["ink"])
    for (px, py) in ([(960, 240), (110, 1500)] if seed % 2 == 0 else [(120, 260), (980, 1480)]):
        d.rectangle([px - 13, py - 4, px + 13, py + 4], fill=ink)
        d.rectangle([px - 4, py - 13, px + 4, py + 13], fill=ink)
    return bg


def glow_sprite(color, r, alpha):
    size = int(r * 3)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    d.ellipse([c - r, c - r, c + r, c + r], fill=rgb(color)[:3] + (alpha,))
    return img.filter(ImageFilter.GaussianBlur(r * 0.45))


# ------------------------------------------------------------------ animation
def place(frame, spr, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01:
        return
    s = spr
    if abs(scale - 1.0) > 0.005:
        s = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        a = s.getchannel("A").point(lambda v: int(v * alpha))
        s = s.copy()
        s.putalpha(a)
    x, y = int(cx - s.width / 2), int(cy - s.height / 2)
    frame.alpha_composite(s, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


def animate(e, t):
    """Return (dx, dy, alpha, scale) for element e at scene-local time t."""
    t0 = e.get("t", 0.0)
    dur = e.get("dur", 0.55)
    p = clamp((t - t0) / dur)
    anim = e.get("anim", "up")
    if p <= 0:
        return None
    if anim == "up":
        q = ease_out_cubic(p)
        return 0, (1 - q) * 70, q, 1.0
    if anim == "right":
        q = ease_out_cubic(p)
        return (1 - q) * 160, 0, q, 1.0
    if anim == "pop":
        q = ease_out_back(p)
        return 0, 0, clamp(p * 2), 0.55 + 0.45 * q
    if anim == "fade":
        return 0, 0, p, 1.0
    if anim == "pulse":
        q = ease_out_back(p)
        base = 0.55 + 0.45 * q
        if p >= 1:
            base = 1 + 0.045 * math.sin((t - t0 - dur) * 2 * math.pi * 1.1)
        return 0, 0, clamp(p * 2), base
    return 0, 0, 1, 1


class Reel:
    def __init__(self, spec):
        self.spec = spec
        self.scenes = []
        start = 0.0
        for i, sc in enumerate(spec["scenes"]):
            bg = background(sc.get("bg", "dark"), i)
            glow = glow_sprite(sc.get("glow", C["purple"]), 380, 150 if sc.get("bg") != "light" else 60)
            els = []
            for e in sc["elements"]:
                if e["type"] == "grid":
                    base = build_sprite(e["item"])
                    for k in range(e["cols"] * e["rows"]):
                        r, c = divmod(k, e["cols"])
                        els.append(({"t": e["t"] + k * e.get("stagger", 0.07), "anim": "pop", "dur": 0.4},
                                    base, e["x0"] + c * e["dx"], e["y0"] + r * e["dy"]))
                elif e["type"] == "cycle":
                    sprs = [sprite_pill(v, e.get("size", 48), fname="latin", gradient=WARM[::-1]) for v in e["values"]]
                    els.append(({"t": e["t"], "anim": "pop", "cycle": sprs, "every": e.get("every", 0.28)},
                                None, e["x"], e["y"]))
                else:
                    els.append((e, build_sprite(e), e["x"], e["y"]))
            dur = sc["dur"]
            self.scenes.append(dict(start=start, dur=dur, bg=bg, glow=glow, els=els))
            start += dur
        self.total = start

    def scene_frame(self, sc, t):
        f = sc["bg"].copy()
        gx = 540 + 260 * math.sin(t * 0.7 + sc["start"])
        gy = 700 + 220 * math.cos(t * 0.5 + sc["start"])
        place(f, sc["glow"], gx, gy)
        for e, spr, x, y in sc["els"]:
            a = animate(e, t)
            if a is None:
                continue
            dx, dy, al, scale = a
            if "cycle" in e:
                k = min(int(max(t - e["t"], 0) / e["every"]), len(e["cycle"]) - 1)
                spr = e["cycle"][k]
            place(f, spr, x + dx, y + dy, al, scale)
        return f

    def frame(self, gt):
        for i, sc in enumerate(self.scenes):
            if sc["start"] <= gt < sc["start"] + sc["dur"] or i == len(self.scenes) - 1:
                lt = gt - sc["start"]
                f = self.scene_frame(sc, lt)
                end = sc["start"] + sc["dur"]
                if i + 1 < len(self.scenes) and gt > end - XFADE:
                    nxt = self.scene_frame(self.scenes[i + 1], 0.0)
                    a = clamp((gt - (end - XFADE)) / XFADE)
                    f = Image.blend(f, nxt, a)
                # global fade-in at start
                if gt < 0.25:
                    f = Image.blend(Image.new("RGBA", f.size, (0, 0, 0, 255)), f, gt / 0.25)
                return f
        return self.scenes[-1]["bg"].copy()


# ------------------------------------------------------------------ music
def music(path, seconds, bpm=96, sr=44100):
    """Original, royalty-free background track: soft pad chords + light beat."""
    n = int(seconds * sr)
    t = np.arange(n) / sr
    beat = 60 / bpm
    bar = beat * 4
    # Am - F - C - G (A minor, calm and modern)
    chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0 * 2 / 1.5 * 0.75 * 2, 261.63, 329.63],
              [196.0, 246.94, 293.66]]
    chords[2] = [130.81 * 2, 329.63, 392.0]
    out = np.zeros(n)
    for b in range(int(seconds / bar) + 1):
        ch = chords[b % 4]
        s0 = int(b * bar * sr)
        s1 = min(n, int((b + 1) * bar * sr))
        if s0 >= n:
            break
        tt = t[s0:s1] - b * bar
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.5)
        for fr in ch:
            out[s0:s1] += 0.10 * env * (np.sin(2 * np.pi * fr * tt) + 0.35 * np.sin(2 * np.pi * fr * 2.003 * tt))
        # bass
        out[s0:s1] += 0.12 * env * np.sin(2 * np.pi * ch[0] / 2 * tt)
        # arpeggio plucks on eighths
        for k in range(8):
            p0 = s0 + int(k * beat / 2 * sr)
            if p0 >= s1:
                break
            ln = min(int(0.35 * sr), s1 - p0)
            pt = np.arange(ln) / sr
            fr = ch[k % 3] * 2
            out[p0:p0 + ln] += 0.06 * np.exp(-pt * 9) * np.sin(2 * np.pi * fr * pt)
    # kick + hat
    for k in range(int(seconds / beat)):
        p0 = int(k * beat * sr)
        ln = min(int(0.25 * sr), n - p0)
        pt = np.arange(ln) / sr
        if k % 2 == 0:
            out[p0:p0 + ln] += 0.35 * np.exp(-pt * 18) * np.sin(2 * np.pi * (55 + 90 * np.exp(-pt * 30)) * pt)
        h0 = p0 + int(beat / 2 * sr)
        hl = min(int(0.05 * sr), max(0, n - h0))
        if hl > 0:
            rng = np.random.default_rng(k)
            out[h0:h0 + hl] += 0.05 * np.exp(-np.arange(hl) / sr * 60) * rng.standard_normal(hl)
    fade = np.minimum(1, t / 1.0) * np.minimum(1, (seconds - t) / 1.5)
    out *= fade
    out /= max(1e-6, np.abs(out).max()) / 0.7
    st = np.stack([out, out], axis=1)
    data = (st * 32767).astype("<i2").tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data)


# ------------------------------------------------------------------ main
def render(spec_path, out_path):
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    reel = Reel(spec)
    wav = out_path.replace(".mp4", ".wav")
    music(wav, reel.total)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(reel.total * FPS)
    for i in range(nframes):
        fr = reel.frame(i / FPS).convert("RGB")
        proc.stdin.write(fr.tobytes())
        if i % 60 == 0:
            print(f"frame {i}/{nframes}", flush=True)
    proc.stdin.close()
    proc.wait()
    os.remove(wav)
    # cover image (CTA scene, fully animated in)
    last = reel.scenes[-1]
    reel.scene_frame(last, last["dur"] - 0.01).convert("RGB").save(out_path.replace(".mp4", "-cover.png"))
    print("done", out_path)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
