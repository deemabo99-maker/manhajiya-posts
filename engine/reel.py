"""
Weekly reel renderer for المنهجية (1080 x 1920, 30 fps, H.264 + original music).

    python3 engine/reel.py posts/batch-01/reel.json posts/batch-01/reel.mp4

A reel is a list of scenes. Each scene has a background and elements; every
element is pre-rendered once as a sprite and then animated (slide / pop / fade)
while frames are piped straight into ffmpeg. Text stays inside the Reels safe
zone (y 260-1450) so Instagram/Facebook overlays never cover it.

Batch-02 added self-drawing ("dynamic") elements — path, chart, typewriter,
scatter, burst — plus box/stamp sprites, the slam/drop/wipe animations, a
scene camera (push-in + shake on impact), hard cuts, per-reel music moods
and synthesised sound effects that follow the edit.
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


def sprite_box(w, h, radius=36, fill="#FFFFFF", gradient=None, angle=0, outline=None, width=0, shadow=True):
    grad = RING if gradient == "ring" else (WARM[::-1] if gradient == "warm" else gradient)
    if isinstance(fill, str):
        fill = _rgba(fill)  # allows '#RRGGBBAA' for translucent bands
    img, m = _round_rect((w, h), radius, fill=fill if not grad else None, gradient=grad, angle=angle,
                         outline=outline, width=width, shadow=shadow)
    return _finish(img)


def sprite_stamp(text, sub=None, color="#D7266B", rot=-11, size=78):
    """Rubber stamp: double border, bold text, slightly rough ink, rotated."""
    f = font("kufi", size, 900)
    l, t, r, b = f.getbbox(text, **_kw(text))
    tw, th = (r - l) / SS, (b - t) / SS
    w, h = int(tw + 120), int(th + (150 if sub else 90))
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([6 * SS, 6 * SS, (w - 6) * SS, (h - 6) * SS], radius=26 * SS, outline=255, width=9 * SS)
    d.rounded_rectangle([20 * SS, 20 * SS, (w - 20) * SS, (h - 20) * SS], radius=18 * SS, outline=255, width=3 * SS)
    cy = (h / 2 - (22 if sub else 0)) * SS
    d.text((w / 2 * SS, cy), text, font=f, fill=255, anchor="mm", **_kw(text))
    if sub:
        d.text((w / 2 * SS, (h - 52) * SS), sub, font=font("latin", 30), fill=255, anchor="mm")
    # ink texture: knock out random speckles
    rng = np.random.default_rng(7)
    noise = (rng.random((img.height // 6, img.width // 6)) > 0.16).astype("uint8") * 255
    nimg = Image.fromarray(noise, "L").resize(img.size, Image.NEAREST).filter(ImageFilter.GaussianBlur(2))
    mask = Image.fromarray((np.asarray(mask, dtype=np.uint16) * np.asarray(nimg, dtype=np.uint16) // 255).astype("uint8"))
    layer = Image.new("RGBA", img.size, rgb(color))
    img.paste(layer, (0, 0), mask)
    img = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    return _finish(img)


def sprite_chip(text, size=30, color="#FFFFFF", alpha=40):
    """Small translucent data chip (a raw number floating around)."""
    f = font("latin", size)
    l, t, r, b = f.getbbox(text)
    w, h = int((r - l) / SS + 36), int(size * 1.7)
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=h * SS / 2, fill=rgb(color)[:3] + (alpha,),
                        outline=rgb(color)[:3] + (120,), width=2 * SS)
    d.text((w * SS / 2, h * SS / 2), text, font=f, fill=rgb(color)[:3] + (190,), anchor="mm")
    return _finish(img)


def build_sprite(e):
    k = e["type"]
    if k == "box":
        return sprite_box(e["w"], e["h"], e.get("radius", 36), e.get("fill", "#FFFFFF"), e.get("gradient"),
                          e.get("angle", 0), e.get("outline"), e.get("width", 0), e.get("shadow", True))
    if k == "stamp":
        return sprite_stamp(e["text"], e.get("sub"), e.get("color", "#D7266B"), e.get("rot", -11), e.get("size", 78))
    if k == "text":
        return sprite_text(e["text"], e.get("font", "kufi"), e.get("size", 80), e.get("wght"),
                           e.get("color", "#FFFFFF"), WARM[::-1] if e.get("gradient") == "warm" else
                           (RING[::-1] if e.get("gradient") == "ring" else None), e.get("shadow", True))
    if k == "pill":
        grad = RING if e.get("gradient") == "ring" else (WARM[::-1] if e.get("gradient") == "warm" else None)
        return sprite_pill(e["text"], e.get("size", 40), e.get("fg", "#FFFFFF"), e.get("bg"), grad, e.get("outline"),
                           fname=e.get("fname", "almarai-xb"), padx=e.get("padx", 46))
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
def background(kind, seed=0, tint=None):
    """A kinetic-type scene wants a flat field, not the brand's patterned gradient:
    pass bg "flat" and `tint` (one colour, or two for a soft duotone sweep)."""
    if kind == "flat":
        cols = tint if isinstance(tint, list) else [tint or C["purple"], tint or C["purple"]]
        return linear_gradient((RW, RH), cols, 115)
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
    size = int(r * 4.4)  # room for the blur tail (r*3 clipped it into a visible square on light scenes)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    d.ellipse([c - r, c - r, c + r, c + r], fill=rgb(color)[:3] + (alpha,))
    return img.filter(ImageFilter.GaussianBlur(r * 0.45))


# ------------------------------------------------------------------ dynamic elements (batch-02)
# These are redrawn every frame instead of being a single pre-rendered sprite,
# so they can *draw themselves*: a line that is traced on, bars that grow,
# words typed one by one, data points that drift and then snap into a trend.

def _partial(pts, p):
    """First fraction p (0..1) of a polyline, by length. Returns points + head."""
    if p <= 0:
        return [], None
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg) or 1
    want = total * clamp(p)
    out = [pts[0]]
    for i, L in enumerate(seg):
        if want >= L:
            out.append(pts[i + 1])
            want -= L
        else:
            a = want / L if L else 0
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * a
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * a
            out.append((x, y))
            break
    return out, out[-1]


def _rgba(c):
    """'#RRGGBB' or '#RRGGBBAA'."""
    c = c.lstrip("#")
    if len(c) == 8:
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4, 6))
    return rgb("#" + c)


def _bezier(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(n + 1):
        u = i / n
        a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def _overlay_draw(frame, box, fn):
    """Draw with fn(draw, ox, oy, k) on a 2x RGBA layer covering box, then composite."""
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, RW), min(y1, RH)
    if x1 <= x0 or y1 <= y0:
        return
    k = 2
    lay = Image.new("RGBA", ((x1 - x0) * k, (y1 - y0) * k), (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay), x0, y0, k)
    lay = lay.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    frame.alpha_composite(lay, (x0, y0))


class DynPath:
    """`path`: a line traced on over time (polyline `pts` or cubic `bezier`), with a glowing head."""

    def __init__(self, e):
        self.e = e
        self.pts = _bezier(*e["bezier"]) if "bezier" in e else [tuple(p) for p in e["pts"]]
        xs, ys = [p[0] for p in self.pts], [p[1] for p in self.pts]
        pad = e.get("width", 12) + 30
        self.box = (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)
        self.cols = [_rgba(c) for c in (e.get("colors") or [e.get("color", C["gold"])])]

    def progress(self, t):
        e = self.e
        p = clamp((t - e.get("t", 0)) / e.get("dur", 1.0))
        return ease_out_cubic(p) if e.get("ease", True) else p

    def head_at(self, t):
        """Where the travelling head is at scene time t (used by the follow camera)."""
        part, head = _partial(self.pts, max(self.progress(t), 1e-4))
        return head

    def draw(self, frame, t):
        e = self.e
        p = clamp((t - e.get("t", 0)) / e.get("dur", 1.0))
        if p <= 0:
            return
        part, head = _partial(self.pts, self.progress(t))
        w = e.get("width", 12)

        def fn(d, ox, oy, k):
            P = [((x - ox) * k, (y - oy) * k) for x, y in part]
            n = len(P)
            for i in range(n - 1):
                c = self.cols[min(int(i / max(n - 1, 1) * len(self.cols)), len(self.cols) - 1)]
                d.line([P[i], P[i + 1]], fill=c, width=int(w * k))
                r = w * k / 2
                d.ellipse([P[i][0] - r, P[i][1] - r, P[i][0] + r, P[i][1] + r], fill=c)
            if e.get("head", True) and head:
                hx, hy = (head[0] - ox) * k, (head[1] - oy) * k
                R = e.get("head_r", w * 1.25) * k
                d.ellipse([hx - R, hy - R, hx + R, hy + R], fill=(255, 255, 255, 255), outline=self.cols[-1], width=int(4 * k))

        _overlay_draw(frame, self.box, fn)


class DynChart:
    """`chart`: a white card whose axes draw on, bars grow one by one and a trend line traces their tops."""

    def __init__(self, e):
        self.e = e
        w, h = e.get("w", 900), e.get("h", 700)
        self.card = sprite_box(w, h, 44, "#FFFFFF")
        self.labels = [sprite_text(l, "almarai-xb", 28, color=C["ink"], shadow=False) for l in e.get("labels", [])]
        self.w, self.h = w, h

    def geom(self):
        e = self.e
        cx, cy, w, h = e["x"], e["y"], self.w, self.h
        x0, y0 = cx - w / 2, cy - h / 2
        ax0, ay1 = x0 + 80, y0 + h - 110
        ax1, ay0 = x0 + w - 60, y0 + 90
        return x0, y0, ax0, ax1, ay0, ay1

    def draw(self, frame, t):
        e = self.e
        t0 = e.get("t", 0)
        if t < t0:
            return
        pc = clamp((t - t0) / 0.45)
        place(frame, self.card, e["x"], e["y"] + (1 - ease_out_cubic(pc)) * 120, pc)
        x0, y0, ax0, ax1, ay0, ay1 = self.geom()
        vals = e["bars"]
        n = len(vals)
        pa = clamp((t - t0 - 0.35) / 0.45)
        span = ax1 - ax0 - 30
        bw = span / n * 0.54
        tops = []
        grads = [C["gold"], C["orange"], C["pink"], C["magenta"], C["purple"], C["violet"]]
        bar_start = t0 + 0.75
        line_t = bar_start + n * e.get("stagger", 0.22) + 0.25

        def fn(d, ox, oy, k):
            # axes draw on
            if pa > 0:
                d.line([((ax0 - ox) * k, (ay1 - oy) * k), ((ax0 - ox) * k, (ay1 - (ay1 - ay0) * pa - oy) * k)],
                       fill=rgb("#D9CFE0"), width=5 * k)
                d.line([((ax0 - ox) * k, (ay1 - oy) * k), ((ax0 + (ax1 - ax0) * pa - ox) * k, (ay1 - oy) * k)],
                       fill=rgb("#D9CFE0"), width=5 * k)
                for g in range(1, 4):
                    gy = ay1 - g * (ay1 - ay0) / 4
                    d.line([((ax0 + 6 - ox) * k, (gy - oy) * k), ((ax0 + (ax1 - ax0) * pa - ox) * k, (gy - oy) * k)],
                           fill=rgb("#F0EAF4"), width=2 * k)
            for i, v in enumerate(vals):
                pb = clamp((t - bar_start - i * e.get("stagger", 0.22)) / 0.5)
                bx = ax0 + 30 + i * span / n + (span / n - bw) / 2
                full = (ay1 - ay0 - 40) * v
                tops.append((bx + bw / 2, ay1 - full - 30))
                if pb <= 0:
                    continue
                hh = full * ease_out_back(pb, 1.2)
                c = rgb(grads[i % len(grads)])
                d.rounded_rectangle([(bx - ox) * k, (ay1 - hh - oy) * k, (bx + bw - ox) * k, (ay1 - 3 - oy) * k],
                                    radius=12 * k, fill=c)

        _overlay_draw(frame, (x0, y0, x0 + self.w, y0 + self.h), fn)
        for i, lab in enumerate(self.labels):
            pb = clamp((t - bar_start - i * e.get("stagger", 0.22)) / 0.4)
            if pb > 0:
                place(frame, lab, tops[i][0], ay1 + 52, pb)
        # trend line through the bar tops, traced on
        pl = clamp((t - line_t) / 0.9)
        if pl > 0:
            part, head = _partial(tops, ease_out_cubic(pl))

            def fl(d, ox, oy, k):
                P = [((x - ox) * k, (y - oy) * k) for x, y in part]
                d.line(P, fill=rgb(C["plum"]), width=7 * k, joint="curve")
                for (px, py) in [((x - ox) * k, (y - oy) * k) for x, y in tops[:len(part) - 1]] + ([P[-1]] if pl >= 1 else []):
                    r = 11 * k
                    d.ellipse([px - r, py - r, px + r, py + r], fill="#FFFFFF", outline=rgb(C["plum"]), width=5 * k)
                if head and pl < 1:
                    hx, hy = P[-1]
                    r = 16 * k
                    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=rgb(C["gold"]))

            _overlay_draw(frame, (x0, y0, x0 + self.w, y0 + self.h), fl)


class DynTypewriter:
    """`typewriter`: Arabic text appears word by word with a blinking caret (right-anchored, RTL)."""

    def __init__(self, e):
        self.e = e
        words = e["text"].split()
        self.sprites = [sprite_text(" ".join(words[:i + 1]), e.get("font", "almarai-xb"), e.get("size", 56),
                                    e.get("wght"), e.get("color", "#FFFFFF"), shadow=e.get("shadow", True))
                        for i in range(len(words))]
        self.n = len(words)
        self.pad = 40  # sprite_text padding (final px)

    def times(self):
        return [self.e.get("t", 0) + i * self.e.get("every", 0.16) for i in range(self.n)]

    def draw(self, frame, t):
        e = self.e
        t0 = e.get("t", 0)
        if t < t0:
            return
        k = min(int((t - t0) / e.get("every", 0.16)), self.n - 1)
        spr = self.sprites[k]
        align = e.get("align", "center")
        if align == "right":
            cx = e["x"] - spr.width / 2 + self.pad
        else:
            cx = e["x"]
        place(frame, spr, cx, e["y"])
        # caret on the left end of the text (RTL writing direction)
        if (int((t - t0) * 3) % 2 == 0) or k < self.n - 1:
            lx = cx - spr.width / 2 + self.pad - 14
            hgt = e.get("size", 56) * 0.95
            col = rgb(e.get("caret", C["gold"]))
            d = ImageDraw.Draw(frame)
            d.rectangle([lx - 3, e["y"] - hgt / 2, lx + 3, e["y"] + hgt / 2], fill=col)


class DynScatter:
    """`scatter`: raw data points / number chips drifting in chaos, then snapping onto a trend line at `snap`."""

    def __init__(self, e):
        self.e = e
        rng = np.random.default_rng(e.get("seed", 3))
        n = e.get("n", 30)
        x0, y0, x1, y1 = e["area"]
        self.home = []
        avoid = e.get("avoid")  # [y_top, y_bottom] band kept clear (e.g. behind the hook text)
        while len(self.home) < n:
            px, py = rng.uniform(x0, x1), rng.uniform(y0, y1)
            if avoid and avoid[0] < py < avoid[1]:
                continue
            self.home.append((px, py))
        self.phase = rng.uniform(0, 2 * math.pi, (n, 2))
        self.speed = rng.uniform(1.2, 2.6, n)
        vals = e.get("values")
        if vals:
            self.sprites = [sprite_chip(vals[i % len(vals)], e.get("size", 30), e.get("color", "#FFFFFF")) for i in range(n)]
        else:
            self.sprites = []
            for i in range(n):
                r = int(rng.uniform(9, 16))
                s_ = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
                ImageDraw.Draw(s_).ellipse([r, r, r * 3, r * 3], fill=rgb([C["gold"], C["pink"], "#FFFFFF", C["orange"]][i % 4]))
                self.sprites.append(s_)
        if "line" in e:
            (lx0, ly0), (lx1, ly1) = e["line"]
            order = sorted(range(n), key=lambda i: self.home[i][0])
            self.target = [None] * n
            for rank, i in enumerate(order):
                u = rank / max(n - 1, 1)
                self.target[i] = (lx0 + (lx1 - lx0) * u, ly0 + (ly1 - ly0) * u + rng.uniform(-14, 14))
        else:
            self.target = None

    def draw(self, frame, t):
        e = self.e
        t0 = e.get("t", 0)
        if t < t0:
            return
        a = clamp((t - t0) / 0.3)
        snap = e.get("snap")
        q = 0.0
        if snap is not None and self.target:
            q = ease_out_back(clamp((t - snap - (0 if True else 0)) / 0.8), 1.1) if t > snap else 0.0
        amp = e.get("jitter", 26) * (1 - min(q, 1))
        for i, (hx, hy) in enumerate(self.home):
            ph = self.phase[i]
            jx = math.sin(t * self.speed[i] * 2.2 + ph[0]) * amp
            jy = math.cos(t * self.speed[i] * 1.7 + ph[1]) * amp
            x, y = hx + jx, hy + jy
            if q > 0:
                tx, ty = self.target[i]
                x, y = x + (tx - x) * q, y + (ty - y) * q
            place(frame, self.sprites[i], x, y, a)


class DynBurst:
    """`burst`: ink rays + an expanding ring, fired on an impact (stamp, CTA)."""

    def __init__(self, e):
        self.e = e

    def draw(self, frame, t):
        e = self.e
        p = clamp((t - e.get("t", 0)) / e.get("dur", 0.6))
        if p <= 0 or p >= 1:
            return
        cx, cy = e["x"], e["y"]
        R = e.get("r", 260)
        col = rgb(e.get("color", C["gold"]))
        al = int(255 * (1 - p))

        def fn(d, ox, oy, k):
            rr = R * (0.5 + 0.7 * ease_out_cubic(p))
            d.ellipse([(cx - rr - ox) * k, (cy - rr - oy) * k, (cx + rr - ox) * k, (cy + rr - oy) * k],
                      outline=col[:3] + (al,), width=int(8 * k * (1 - p) + 2))
            for j in range(14):
                ang = j / 14 * 2 * math.pi + 0.2
                r0, r1 = rr * 1.05, rr * (1.18 + 0.25 * p)
                d.line([((cx + r0 * math.cos(ang) - ox) * k, (cy + r0 * math.sin(ang) - oy) * k),
                        ((cx + r1 * math.cos(ang) - ox) * k, (cy + r1 * math.sin(ang) - oy) * k)],
                       fill=col[:3] + (al,), width=int(9 * k))

        _overlay_draw(frame, (cx - R * 1.9, cy - R * 1.9, cx + R * 1.9, cy + R * 1.9), fn)


DYNAMIC = {"path": DynPath, "chart": DynChart, "typewriter": DynTypewriter, "scatter": DynScatter, "burst": DynBurst}


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
    if anim == "slam":   # lands hard from oversized — the kinetic-type accent
        q = ease_out_cubic(clamp(p * 1.6))
        return 0, 0, clamp(p * 3), 2.4 - 1.4 * q
    if anim == "zoom":   # grows in without pop's overshoot
        q = ease_out_cubic(p)
        return 0, 0, clamp(p * 2), 0.28 + 0.72 * q
    if anim == "fade":
        return 0, 0, p, 1.0
    if anim == "slam":
        # falls from a huge scale onto the page and lands hard (pair it with a scene shake)
        q = p ** 2.2
        return 0, 0, clamp(p * 3), e.get("from", 3.2) + (1 - e.get("from", 3.2)) * q
    if anim == "drop":
        # drops in from above and settles with a small bounce
        q = ease_out_back(p, 2.2)
        return 0, -(1 - q) * 420, clamp(p * 2.5), 1.0
    if anim == "blink":
        # caret-style on/off blinking after it appears
        on = int((t - t0) * 2.4) % 2 == 0
        return 0, 0, 1.0 if on else 0.0, 1.0
    if anim == "wipe":
        # mask reveal from the right edge (RTL reading direction); handled in scene_frame
        return 0, 0, 1.0, 1.0
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
            bg = background(sc.get("bg", "dark"), i, sc.get("tint"))
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
                elif e["type"] in DYNAMIC:
                    els.append(({**e, "dyn": DYNAMIC[e["type"]](e)}, None, e.get("x", 0), e.get("y", 0)))
                else:
                    els.append((e, build_sprite(e), e["x"], e["y"]))
            dur = sc["dur"]
            self.scenes.append(dict(start=start, dur=dur, bg=bg, glow=glow, els=els,
                                    camera=sc.get("camera"), shake=sc.get("shake", [])))
            start += dur
        self.total = start
        self.sfx = []
        for sc, raw in zip(self.scenes, spec["scenes"]):
            for e in raw["elements"]:
                t0 = sc["start"] + e.get("t", 0)
                if e.get("anim") == "slam":
                    self.sfx.append((t0 + e.get("dur", 0.55) * 0.95, "hit"))
                elif e.get("anim") in ("wipe", "drop"):
                    self.sfx.append((t0, "whoosh"))
                elif e["type"] == "typewriter":
                    self.sfx += [(sc["start"] + tt, "click") for tt in DynTypewriter(e).times()]
                elif e["type"] in ("path", "chart"):
                    self.sfx.append((t0 + (0.75 if e["type"] == "chart" else 0), "rise"))
            for e in raw.get("sfx", []):
                self.sfx.append((sc["start"] + e["t"], e["kind"]))

    def scene_frame(self, sc, t):
        f = sc["bg"].copy()
        gx = 540 + 260 * math.sin(t * 0.7 + sc["start"])
        gy = 700 + 220 * math.cos(t * 0.5 + sc["start"])
        place(f, sc["glow"], gx, gy)
        hud = []
        for e, spr, x, y in sc["els"]:
            if e.get("hud"):
                hud.append((e, spr, x, y))
                continue
            if "dyn" in e:
                e["dyn"].draw(f, t)
                continue
            a = animate(e, t)
            if a is None:
                continue
            dx, dy, al, scale = a
            if "cycle" in e:
                k = min(int(max(t - e["t"], 0) / e["every"]), len(e["cycle"]) - 1)
                spr = e["cycle"][k]
            if e.get("anim") == "wipe":
                p = ease_out_cubic(clamp((t - e.get("t", 0)) / e.get("dur", 0.55)))
                keep = max(1, int(spr.width * p))
                part = spr.crop((spr.width - keep, 0, spr.width, spr.height))
                place(f, part, x + spr.width / 2 - keep / 2, y)
                continue
            place(f, spr, x + dx, y + dy, al, scale)
        f = self.camera(sc, f, t)
        # HUD elements sit on top of the camera move (titles, brand bug)
        for e, spr, x, y in hud:
            if "dyn" in e:
                e["dyn"].draw(f, t)
                continue
            a = animate(e, t)
            if a is None:
                continue
            dx, dy, al, scale = a
            place(f, spr, x + dx, y + dy, al, scale)
        return f

    @staticmethod
    def camera(sc, f, t):
        """Scene camera: a slow push-in (zoom towards a point) and decaying shakes on impacts."""
        cam = sc.get("camera")
        zoom = 1.0
        cx, cy = RW / 2, RH / 2
        if cam and "follow" in cam:
            # follow camera: rides a path's travelling head zoomed in, then pulls back to reveal the whole map
            dyn = sc["els"][cam["follow"]][0]["dyn"]
            hx, hy = dyn.head_at(t)
            z = cam.get("zoom", 1.8)
            rel, rd = cam.get("release", 1e9), cam.get("release_dur", 0.9)
            q = clamp((t - rel) / rd)
            q = q * q * (3 - 2 * q)
            zoom = z + (1.0 - z) * q
            cx = hx + (RW / 2 - hx) * q
            cy = hy + (RH / 2 - hy) * q
        elif cam:
            u = clamp(t / sc["dur"])
            zoom = cam.get("from", 1.0) + (cam.get("to", 1.08) - cam.get("from", 1.0)) * (u * u * (3 - 2 * u))
            cx, cy = cam.get("x", cx), cam.get("y", cy)
        sx = sy = 0.0
        for sh in sc.get("shake", []):
            q = (t - sh["t"]) / sh.get("dur", 0.45)
            if 0 <= q < 1:
                amp = sh.get("amp", 22) * (1 - q) ** 2
                sx += amp * math.sin(q * 47)
                sy += amp * math.cos(q * 39)
        if zoom == 1.0 and sx == 0 and sy == 0:
            return f
        z = max(zoom, 1.0) + (0.03 if (sx or sy) else 0)
        w, h = RW / z, RH / z
        left = clamp(cx - w / 2 - sx / z, 0, RW - w)
        top = clamp(cy - h / 2 - sy / z, 0, RH - h)
        return f.crop((int(left), int(top), int(left + w), int(top + h))).resize((RW, RH), Image.BILINEAR)

    def frame(self, gt):
        for i, sc in enumerate(self.scenes):
            if sc["start"] <= gt < sc["start"] + sc["dur"] or i == len(self.scenes) - 1:
                lt = gt - sc["start"]
                f = self.scene_frame(sc, lt)
                end = sc["start"] + sc["dur"]
                if i + 1 < len(self.scenes) and gt > end - XFADE and not self.spec["scenes"][i + 1].get("cut"):
                    nxt = self.scene_frame(self.scenes[i + 1], 0.0)
                    a = clamp((gt - (end - XFADE)) / XFADE)
                    f = Image.blend(f, nxt, a)
                # global fade-in at start
                fi = self.spec.get("fadein", 0.25)
                if gt < fi:
                    f = Image.blend(Image.new("RGBA", f.size, (0, 0, 0, 255)), f, gt / fi)
                return f
        return self.scenes[-1]["bg"].copy()


# ------------------------------------------------------------------ music
MOODS = {
    # A minor, calm and modern (batch-01)
    "calm": [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.62, 329.63, 392.0], [196.0, 246.94, 293.66]],
    # D minor, driving: Dm - Bb - F - C
    "drive": [[146.83, 174.61, 220.0], [116.54, 146.83, 174.61], [174.61, 220.0, 261.63], [130.81, 164.81, 196.0]],
    # E minor, rising: Em - C - G - D (builds towards an impact)
    "rise": [[164.81, 196.0, 246.94], [130.81, 164.81, 196.0], [196.0, 246.94, 293.66], [146.83, 185.0, 220.0]],
}


def _sfx(out, sr, kind, t0):
    """Synthesised sound effects mixed onto the track (all original, numpy only)."""
    n = len(out)
    p0 = int(t0 * sr)
    if p0 >= n or p0 < 0:
        return
    rng = np.random.default_rng(int(t0 * 1000))
    if kind == "hit":        # deep impact for stamps / slams
        ln = min(int(0.9 * sr), n - p0)
        pt = np.arange(ln) / sr
        sig = 0.9 * np.exp(-pt * 6) * np.sin(2 * np.pi * (42 + 120 * np.exp(-pt * 22)) * pt)
        sig += 0.35 * np.exp(-pt * 30) * rng.standard_normal(ln)
    elif kind == "click":    # key press for the typewriter
        ln = min(int(0.04 * sr), n - p0)
        pt = np.arange(ln) / sr
        sig = 0.18 * np.exp(-pt * 180) * (rng.standard_normal(ln) + np.sin(2 * np.pi * 2400 * pt))
    elif kind == "whoosh":   # filtered noise sweep for wipes / drops
        ln = min(int(0.45 * sr), n - p0)
        pt = np.arange(ln) / sr
        env = np.sin(np.pi * pt / 0.45) ** 2
        noise = np.convolve(rng.standard_normal(ln), np.ones(12) / 12, mode="same")
        sig = 0.22 * env * noise
    elif kind == "rise":     # short riser under a drawing chart / line
        ln = min(int(1.2 * sr), n - p0)
        pt = np.arange(ln) / sr
        f = 300 + 900 * (pt / 1.2) ** 2
        sig = 0.07 * np.minimum(1, pt / 0.2) * np.exp(-np.maximum(0, pt - 1.0) * 20) * np.sin(2 * np.pi * np.cumsum(f) / sr)
    elif kind == "ding":     # bright bell when the CTA lands
        ln = min(int(1.0 * sr), n - p0)
        pt = np.arange(ln) / sr
        sig = 0.22 * np.exp(-pt * 5) * (np.sin(2 * np.pi * 1318.5 * pt) + 0.5 * np.sin(2 * np.pi * 1975.5 * pt))
    else:
        return
    out[p0:p0 + ln] += sig


def music(path, seconds, bpm=96, sr=44100, mood="calm", sfx=()):
    """Original, royalty-free background track: pad chords + plucks + beat, plus synthesised sfx."""
    n = int(seconds * sr)
    t = np.arange(n) / sr
    beat = 60 / bpm
    bar = beat * 4
    chords = MOODS.get(mood, MOODS["calm"])
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
    out /= max(1e-6, np.abs(out).max()) / 0.55
    for t0, kind in sfx:
        _sfx(out, sr, kind, t0)
    out = 0.89 * np.tanh(out * 1.1) / np.tanh(1.1)  # soft limiter, peaks ~ -1 dB
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
    m = spec.get("music", {})
    music(wav, reel.total, bpm=m.get("bpm", 96), mood=m.get("mood", "calm"), sfx=reel.sfx)
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
    cv = spec.get("cover", {})
    sc = reel.scenes[cv.get("scene", len(reel.scenes) - 1)]
    reel.scene_frame(sc, cv.get("t", sc["dur"] - 0.01)).convert("RGB").save(out_path.replace(".mp4", "-cover.png"))
    print("done", out_path)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
