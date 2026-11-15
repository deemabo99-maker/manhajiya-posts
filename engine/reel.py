"""
Weekly reel renderer for المنهجية (1080 x 1920, 30 fps, H.264 + original music).

    python3 engine/reel.py posts/batch-01/reel.json posts/batch-01/reel.mp4

A reel is a list of scenes. Each scene has a background and elements; every
element is pre-rendered once as a sprite and then animated (slide / pop / fade)
while frames are piped straight into ffmpeg. Text stays inside the Reels safe
zone (y 260-1450) so Instagram/Facebook overlays never cover it.

Batch-03 added the questionnaire `likert` row, the reviewer's pen `mark`, flying
reference cards (`fly`), a world-space `dolly` camera for scale reveals (zoom in
or out by any factor, sprites built hi-res with `res`), the `iris` mask reveal,
a button `press`, a generic `out` exit and new sfx (tick, pen, flick, tap, swell).

Batch-04 added the `phone` chat screen that is typed into (letters land in the input,
the message flies up, "typing…" dots, replies pop, auto-scroll, a WhatsApp contact
bubble), the `proof` page (a magnifying `loupe` that leaves corrected words behind it,
or a `scan` beam with highlighter strokes and source tags), the `snap` page whose
crooked blocks snap onto dashed margin guides, a full-bleed edge texture on every
background (Meta border guard), the lower-third `orbit` imagery, and sfx
send/pop/scan/fix/snap.

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
        return sprite_doc(e.get("w", 150), e.get("h", 186))
    if k == "thead":
        return sprite_table_header(e["cols"])
    if k == "trow":
        return sprite_table_row(e["cells"], idx=e.get("idx", 0))
    if k == "refcard":
        return sprite_minicard(e["text"], 250, 110, e.get("band"), e.get("scale", 1.0))
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
    return edge_texture(bg, kind)


_TEX = {}


def edge_texture(bg, kind):
    """batch-04 — Meta border guard. A full-bleed brand texture (dot lattice + soft diagonal
    ribbons) that is strongest at the frame edges and quiet behind the text, so no edge of
    any frame is ever a flat band of colour (Instagram read the old flat edges as a
    "border"). Every scene background goes through this."""
    if kind not in _TEX:
        lay = Image.new("L", (RW, RH), 0)
        d = ImageDraw.Draw(lay)
        for yy in range(-30, RH + 60, 60):          # diagonal ribbons, 45 degrees
            d.line([(-60, yy), (RW + 60, yy - RW - 120)], fill=40, width=16)
        for yy in range(-RW, RH, 60):
            d.line([(-60, yy), (RW + 60, yy - RW - 120)], fill=40, width=16)
        for j in range(0, RH + 30, 30):              # dot lattice, offset rows
            for i in range(0, RW + 30, 30):
                cx = i + (15 if (j // 30) % 2 else 0)
                d.ellipse([cx - 3.2, j - 3.2, cx + 3.2, j + 3.2], fill=255)
        a = np.asarray(lay, dtype=np.float32) / 255.0
        yy, xx = np.mgrid[0:RH, 0:RW].astype(np.float32)
        edge = np.minimum.reduce([xx, RW - 1 - xx, yy, RH - 1 - yy])
        w = 0.35 + 0.65 * np.clip(1 - edge / 260.0, 0, 1)   # 1.0 at the edge, 0.35 inside
        _TEX[kind] = (a * w)
    a = _TEX[kind]
    col = (255, 255, 255) if kind != "light" else rgb(C["purple"])[:3]
    strength = 0.36 if kind != "light" else 0.34
    base = np.asarray(bg.convert("RGB"), dtype=np.float32)
    m = (a * strength)[..., None]
    out = base * (1 - m) + np.array(col, dtype=np.float32) * m
    return Image.fromarray(out.clip(0, 255).astype("uint8")).convert("RGBA")


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



# ------------------------------------------------------------------ dynamic elements (batch-03)
# A questionnaire that fills itself in (likert rows whose answer dots get
# picked), a reviewer's red pen that draws annotations on (mark), cards that
# fly from a scattered pile into their slots (fly), plus — in Reel below — a
# world-space "dolly" camera for scale reveals, the iris mask reveal, the
# button press and the generic `out` exit.

def _fit_font(text, fname, size, maxw, wght=None):
    while size > 16:
        f = font(fname, size, wght)
        l, t, r, b = f.getbbox(text, **_kw(text))
        if (r - l) / SS <= maxw:
            return f, size
        size -= 1
    return font(fname, size, wght), size


class DynLikert:
    """`likert`: one questionnaire item — statement on the right, five answer dots on the left.
    The row slides in at `t`; each [time, index] in `picks` moves the chosen answer there
    (several picks = an undecided respondent jumping between answers)."""

    def __init__(self, e):
        self.e = e
        w, h = e.get("w", 860), e.get("h", 104)
        self.w, self.h = w, h
        self.gap = e.get("gap", 74)
        self.r = e.get("r", 21)
        ink = e.get("color", C["ink"])
        img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        if e.get("rule", True):
            d.line([(0, (h - 2) * SS), (w * SS, (h - 2) * SS)], fill=rgb(e.get("rule_color", "#E7DDF0")), width=2 * SS)
        maxw = w - 5 * self.gap - 70
        f, _ = _fit_font(e["text"], e.get("font", "almarai-bold"), e.get("size", 30), maxw)
        d.text(((w - 14) * SS, h / 2 * SS), e["text"], font=f, fill=rgb(ink), anchor="rm", **_kw(e["text"]))
        for i in range(5):
            cx, cy = self.dot_x(i) * SS, h / 2 * SS
            r = self.r * SS
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgb(e.get("ring", "#CBB8D9")), width=3 * SS)
        self.base = _finish(img)

    def dot_x(self, i):
        # i = 0 is "strongly agree" (closest to the statement, RTL), 4 the far left
        return 30 + self.r + (4 - i) * self.gap

    def draw(self, frame, t):
        e = self.e
        t0 = e.get("t", 0)
        if t < t0:
            return
        p = ease_out_cubic(clamp((t - t0) / 0.45))
        x0 = e["x"] - self.w / 2 + (1 - p) * 140
        y0 = e["y"] - self.h / 2
        place(frame, self.base, x0 + self.w / 2, e["y"], clamp(p * 1.6))
        picks = [pk for pk in e.get("picks", []) if pk[0] <= t]
        if not picks:
            return
        tp, idx = picks[-1]
        q = clamp((t - tp) / 0.28)
        cx, cy = x0 + self.dot_x(idx), e["y"]
        col = rgb(e.get("fill", C["purple"]))

        def fn(d, ox, oy, k):
            r = self.r * ease_out_back(q, 2.4) * 0.98
            d.ellipse([(cx - r - ox) * k, (cy - r - oy) * k, (cx + r - ox) * k, (cy + r - oy) * k], fill=col)
            ri = self.r * 0.36
            d.ellipse([(cx - ri - ox) * k, (cy - ri - oy) * k, (cx + ri - ox) * k, (cy + ri - oy) * k], fill="#FFFFFF")
            rq = clamp((t - tp) / 0.5)
            if rq < 1:  # ripple
                rr = self.r * (1 + 1.3 * ease_out_cubic(rq))
                d.ellipse([(cx - rr - ox) * k, (cy - rr - oy) * k, (cx + rr - ox) * k, (cy + rr - oy) * k],
                          outline=col[:3] + (int(200 * (1 - rq)),), width=int(4 * k))

        _overlay_draw(frame, (cx - 60, cy - 60, cx + 60, cy + 60), fn)


class DynMark:
    """`mark`: a reviewer's pen stroke drawn on — kind circle / underline / strike / tick / arrow,
    with a hand-made wobble so it reads as ink, not geometry."""

    def __init__(self, e):
        self.e = e
        rng = np.random.default_rng(e.get("seed", 1))
        k = e.get("kind", "circle")
        if k == "circle":
            cx, cy, rx, ry = e["x"], e["y"], e["rx"], e["ry"]
            n = 70
            a0 = math.radians(-60)
            pts = []
            for i in range(n + 1):
                u = i / n
                a = a0 - u * 2 * math.pi * 1.08  # a little past a full turn, like a real pen loop
                wob = 1 + 0.035 * math.sin(u * 9 + 1) + 0.02 * u
                pts.append((cx + rx * wob * math.cos(a), cy + ry * wob * math.sin(a)))
        elif k in ("underline", "strike"):
            x0, x1, y = e["x1"], e["x0"], e["y"]  # drawn right -> left (RTL)
            n = 30
            pts = [(x0 + (x1 - x0) * i / n, y + 3 * math.sin(i * 0.9) + rng.uniform(-1.5, 1.5) + (i / n) * e.get("slope", 6))
                   for i in range(n + 1)]
        elif k == "tick":
            x, y, s = e["x"], e["y"], e.get("s", 40)
            pts = [(x - s * 0.55, y - s * 0.02), (x - s * 0.12, y + s * 0.42), (x + s * 0.7, y - s * 0.62)]
        else:  # arrow: polyline pts, head added at the end
            pts = [tuple(p) for p in e["pts"]]
        self.pts = pts
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        pad = e.get("width", 8) + 50
        self.box = (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)

    def draw(self, frame, t):
        e = self.e
        p = clamp((t - e.get("t", 0)) / e.get("dur", 0.5))
        if p <= 0:
            return
        part, head = _partial(self.pts, ease_out_cubic(p))
        col = _rgba(e.get("color", "#E0245E"))
        w = e.get("width", 8)

        def fn(d, ox, oy, k):
            P = [((x - ox) * k, (y - oy) * k) for x, y in part]
            if len(P) > 1:
                d.line(P, fill=col, width=int(w * k), joint="curve")
            for q in (P[0], P[-1]):
                r = w * k / 2
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=col)
            if e.get("kind") == "arrow" and p >= 1 and len(P) > 1:
                (ax, ay), (bx, by) = P[-2], P[-1]
                ang = math.atan2(by - ay, bx - ax)
                L = 30 * k
                for s_ in (2.6, -2.6):
                    d.line([(bx, by), (bx + L * math.cos(ang + s_), by + L * math.sin(ang + s_))], fill=col, width=int(w * k))

        _overlay_draw(frame, self.box, fn)


def sprite_minicard(text, w=250, h=110, band=None, k=1.0):
    """Small reference card: coloured top band, a title and two grey text lines (k scales it all)."""
    W_, H_ = int(w * k), int(h * k)
    img, m = _round_rect((W_, H_), 18 * k, fill="#FFFFFF", shadow=True)
    d = ImageDraw.Draw(img)
    band = band or C["purple"]
    d.rounded_rectangle([m, m, m + W_ * SS, m + 18 * k * SS], radius=9 * k * SS, fill=rgb(band))
    d.rectangle([m, m + 9 * k * SS, m + W_ * SS, m + 18 * k * SS], fill=rgb(band))
    fn = font("latin", 22 * k) if text.isascii() else font("almarai-xb", 26 * k)
    d.text((m + (w - 18) * k * SS, m + 46 * k * SS), text, font=fn, fill=rgb(C["ink"]), anchor="rm", **_kw(text))
    for j, ww in enumerate([0.82, 0.58]):
        yy = m + (72 + j * 18) * k * SS
        d.rounded_rectangle([m + (w - 18 - (w - 36) * ww) * k * SS, yy, m + (w - 18) * k * SS, yy + 8 * k * SS],
                            radius=4 * k * SS, fill=rgb("#E4DAEC"))
    return _finish(img)


class DynFly:
    """`fly`: mini reference cards start scattered and tilted, then fly one by one into their slots."""

    def __init__(self, e):
        self.e = e
        rng = np.random.default_rng(e.get("seed", 4))
        self.items = []
        for i, it in enumerate(e["items"]):
            spr = sprite_minicard(it["text"], e.get("w", 250), e.get("h", 110), it.get("band"))
            fx, fy = it.get("from") or (rng.uniform(80, 1000), rng.uniform(300, 1500))
            rot = it.get("rot", rng.uniform(-24, 24))
            rots = [spr.rotate(rot * (1 - j / 6), resample=Image.BICUBIC, expand=True) for j in range(7)]
            self.items.append(dict(rots=rots, fx=fx, fy=fy, tx=it["to"][0], ty=it["to"][1],
                                   go=e.get("go", 1.0) + i * e.get("stagger", 0.12)))

    def draw(self, frame, t):
        e = self.e
        t0 = e.get("t", 0)
        if t < t0:
            return
        a = clamp((t - t0) / 0.3)
        for it in self.items:
            q = clamp((t - it["go"]) / e.get("fly", 0.55))
            qq = ease_out_back(q, 1.3)
            if q <= 0:  # waiting in the pile, drifting slightly
                x = it["fx"] + 6 * math.sin(t * 2 + it["fx"])
                y = it["fy"] + 6 * math.cos(t * 1.7 + it["fy"])
            else:
                x = it["fx"] + (it["tx"] - it["fx"]) * qq
                y = it["fy"] + (it["ty"] - it["fy"]) * qq
            spr = it["rots"][min(int(clamp(q) * 6.99), 6)]
            place(frame, spr, x, y, a, 1.0 + 0.12 * math.sin(math.pi * clamp(q)))


class DynSplit:
    """Two states of the same page, with a divider that sweeps across: right of it the page
    as it came back (red marks and queries), left of it the page after the work (ticks and a
    clean rule). The sweep is the whole idea — one page turning into the other.

    Everything is drawn on a 2x layer and downsampled, because kit's fonts are already 2x:
    drawing them straight onto the 1080x1920 frame renders every label at double size.
    batch-04 format: split screen."""

    K = 2

    def __init__(self, e):
        self.e = e
        self.w = e.get("w", 760)
        self.h = e.get("h", 900)
        self.t0 = e.get("t", 0.0)
        self.dur = e.get("dur", 2.4)
        self.before = e.get("before", "قبل")
        self.after = e.get("after", "بعد")
        self._cache = {}

    def _page(self, clean):
        if clean in self._cache:
            return self._cache[clean]
        k = self.K
        w, h = self.w * k, self.h * k
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=26 * k, fill="#FFFFFF")
        d.rounded_rectangle([46 * k, 50 * k, w - 46 * k, 96 * k], radius=10 * k,
                            fill=rgb(C["purple"]) if clean else rgb("#D9D2DE"))
        rng = np.random.default_rng(4)
        rows = int((self.h - 190) // 56)
        for i in range(rows):
            yy = (150 + i * 56) * k
            ww = (self.w - 120) * (0.9 if i % 3 else 0.52) * k
            d.rounded_rectangle([w - 60 * k - ww, yy, w - 60 * k, yy + 14 * k],
                                radius=7 * k, fill=rgb("#E4DEEA") if clean else rgb("#DED7E4"))
            if not clean and i % 3 == 1:
                x0 = w - 60 * k - ww * float(rng.uniform(0.8, 0.95))
                x1 = w - 60 * k - ww * float(rng.uniform(0.08, 0.25))
                d.line([(x0, yy + 22 * k), (x1, yy + 26 * k)], fill=rgb("#E03B3B"), width=5 * k)
            if clean and i % 3 == 1:
                cx, cy = 92 * k, yy + 8 * k
                d.line([(cx - 13 * k, cy), (cx - 3 * k, cy + 12 * k), (cx + 17 * k, cy - 13 * k)],
                       fill=rgb(C["green"]) if "green" in C else rgb("#1FAF5A"), width=6 * k)
        if not clean:
            for (cx, cy) in ((100, 260), (108, 540), (96, 806)):
                if cy > self.h - 60:
                    continue
                d.ellipse([(cx - 21) * k, (cy - 21) * k, (cx + 21) * k, (cy + 21) * k],
                          outline=rgb("#E03B3B"), width=4 * k)
                d.text((cx * k, cy * k), "?", font=font("latin", 22), fill=rgb("#E03B3B"),
                       anchor="mm")
        self._cache[clean] = img
        return img

    def draw(self, frame, t):
        if t < self.t0:
            return
        p = clamp((t - self.t0) / self.dur)
        p = p * p * (3 - 2 * p)
        k = self.K
        x, y = self.e.get("x", 540), self.e.get("y", 960)
        padx, padt, padb = 46, 100, 46
        bx0 = int(x - self.w / 2 - padx)
        by0 = int(y - self.h / 2 - padt)
        bw, bh = self.w + 2 * padx, self.h + padt + padb
        lay = Image.new("RGBA", (bw * k, bh * k), (0, 0, 0, 0))
        px, py = padx * k, padt * k

        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(
            [px + 8 * k, py + 18 * k, px + self.w * k + 8 * k, py + self.h * k + 18 * k],
            radius=26 * k, fill=(20, 6, 28, 120))
        lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16 * k)))
        lay.alpha_composite(self._page(False), (px, py))
        cut = int(self.w * k * p)
        if cut > 0:
            lay.alpha_composite(self._page(True).crop((0, 0, cut, self.h * k)), (px, py))
        d = ImageDraw.Draw(lay)
        if 0 < cut < self.w * k:
            dx = px + cut
            d.rectangle([dx - 3 * k, py - 16 * k, dx + 3 * k, py + (self.h + 16) * k],
                        fill=rgb(C["yellow"]))
            cy = py + self.h * k / 2
            d.ellipse([dx - 27 * k, cy - 27 * k, dx + 27 * k, cy + 27 * k], fill=rgb(C["yellow"]))
            d.polygon([(dx - 14 * k, cy), (dx - 3 * k, cy - 10 * k), (dx - 3 * k, cy + 10 * k)],
                      fill=rgb(C["plum"]))
            d.polygon([(dx + 14 * k, cy), (dx + 3 * k, cy - 10 * k), (dx + 3 * k, cy + 10 * k)],
                      fill=rgb(C["plum"]))
        f = font("almarai-xb", 30)
        for txt, lx, show, col in ((self.after, px + 150 * k, p > 0.14, rgb(C["purple"])),
                                   (self.before, px + (self.w - 150) * k, p < 0.92, rgb("#6B5B74"))):
            if not show:
                continue
            b = f.getbbox(txt, direction="rtl", language="ar")
            ww = (b[2] - b[0]) + 54 * k
            d.rounded_rectangle([lx - ww / 2, py - 84 * k, lx + ww / 2, py - 20 * k],
                                radius=32 * k, fill=col)
            d.text((lx, py - 52 * k), txt, font=f, fill="#FFFFFF", anchor="mm",
                   direction="rtl", language="ar")
        frame.alpha_composite(lay.resize((bw, bh), Image.LANCZOS), (max(bx0, 0), max(by0, 0)))


class DynTimer:
    """A ring that drains to empty, with a label inside: the deadline the work is running
    against. Turns from gold to pink in the last quarter. batch-04 format: a countdown
    driving the edit."""

    K = 2

    def __init__(self, e):
        self.e = e
        self.r = e.get("r", 160)
        self.t0 = e.get("t", 0.0)
        self.dur = e.get("dur", 3.0)

    def draw(self, frame, t):
        if t < self.t0:
            return
        p = clamp((t - self.t0) / self.dur)
        k = self.K
        x, y = self.e.get("x", 540), self.e.get("y", 760)
        r = self.r
        pad = 40
        bw = bh = int((r + pad) * 2)
        lay = Image.new("RGBA", (bw * k, bh * k), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        c = bw * k / 2
        box = [c - r * k, c - r * k, c + r * k, c + r * k]
        d.ellipse(box, fill=(255, 255, 255, 28))
        d.arc(box, 0, 360, fill=(255, 255, 255, 70), width=3 * k)
        sweep = 360 * (1 - p)
        if sweep > 0.5:
            d.arc(box, -90, -90 + sweep,
                  fill=rgb(C["pink"]) if p > 0.74 else rgb(C["yellow"]), width=20 * k)
        txt = self.e.get("text", "")
        if txt:
            d.text((c, c - 18 * k), txt, font=font("kufi", self.e.get("size", 44), 900),
                   fill="#FFFFFF", anchor="mm", direction="rtl", language="ar")
        sub = self.e.get("sub")
        if sub:
            d.text((c, c + 42 * k), sub, font=font("almarai-xb", 24),
                   fill=rgb(C["yellow"]) if p <= 0.74 else rgb(C["pink"]),
                   anchor="mm", direction="rtl", language="ar")
        frame.alpha_composite(lay.resize((bw, bh), Image.LANCZOS),
                              (max(int(x - bw / 2), 0), max(int(y - bh / 2), 0)))


# ------------------------------------------------------------------ batch-04 elements
# phone  — a chat screen that is typed into: letters land in the input field one by one,
#          the message flies up as a bubble, the other side shows "typing…" dots, replies
#          pop in and the chat auto-scrolls; a `contact` bubble carries the WhatsApp CTA.
# proof  — a page of real Arabic text inspected two ways: `loupe` (a magnifier reads the
#          page right to left and leaves corrected words behind it) and `scan` (a beam
#          sweeps down and highlighter strokes mark quoted passages, each getting a
#          source tag).
# snap   — a page whose blocks start crooked and scattered, then snap one by one onto
#          dashed margin guides (formatting to a university's style guide).

def _wrap(text, f, maxw):
    """Greedy RTL word wrap; widths in the font's own (2x) pixels."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and f.getlength(trial, **_kw(trial)) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _mul_alpha(img, a):
    if a >= 0.999:
        return img
    out = img.copy()
    out.putalpha(out.getchannel("A").point(lambda v: int(v * a)))
    return out


class DynPhone:
    K = 2

    def __init__(self, e):
        self.e = e
        self.w, self.h = e.get("w", 600), e.get("h", 950)
        k = self.K
        self.f_msg = font("almarai-bold", e.get("msg_size", 29))
        self.f_in = font("almarai-bold", e.get("msg_size", 29))
        self.bez = 18
        self.sw, self.sh = self.w - 2 * self.bez, self.h - 2 * self.bez
        self.head_h, self.in_h = 118, 108
        self.area_h = self.sh - self.head_h - self.in_h
        self.maxw = (self.sw * 0.74 - 44) * k
        self.msgs = []
        for m in e["messages"]:
            m = dict(m)
            if m.get("from") == "me" and m.get("typed", True):
                m["type0"] = m["t"]
                m["show"] = m["t"] + m.get("type_dur", 0.05 * len(m["text"]))
            else:
                m["dots0"] = m["t"]
                m["show"] = m["t"] + m.get("dots", 0.75 if m.get("from") != "me" else 0)
            m["spr"] = self._bubble(m)
            self.msgs.append(m)
        self.frame_img = self._body()

    # ---- static parts
    def _body(self):
        k = self.K
        W, H = self.w * k, self.h * k
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, W - 1, H - 1], radius=74 * k, fill=rgb("#17091F"))
        d.rounded_rectangle([3 * k, 3 * k, W - 4 * k, H - 4 * k], radius=72 * k, outline=rgb("#4B2A5C"), width=3 * k)
        b = self.bez * k
        sx1, sy1 = W - b, H - b
        # wallpaper: soft lilac with a faint dot pattern
        wall = linear_gradient((sx1 - b, sy1 - b), ["#F4EEF8", "#EDE3F3"], 90)
        wd = ImageDraw.Draw(wall)
        for j in range(0, wall.height, 44):
            for i in range(0, wall.width, 44):
                cx = i + (22 if (j // 44) % 2 else 0)
                wd.ellipse([cx - 3, j - 3, cx + 3, j + 3], fill=rgb("#DCCBE6"))
        mask = Image.new("L", wall.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, wall.width - 1, wall.height - 1], radius=58 * k, fill=255)
        img.paste(wall, (b, b), mask)
        # header
        hh = self.head_h * k
        head = linear_gradient((sx1 - b, hh), [C["violet"], C["purple"], C["magenta"]], 0)
        hm = Image.new("L", head.size, 0)
        ImageDraw.Draw(hm).rounded_rectangle([0, 0, head.width - 1, hh + 80 * k], radius=58 * k, fill=255)
        img.paste(head, (b, b), hm)
        d = ImageDraw.Draw(img)
        # logo disc on the right (RTL chat header)
        cx, cy, r = sx1 - 74 * k, b + hh / 2 + 8 * k, 38 * k
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FFFFFF")
        lg = Image.open(kit.LOGO).convert("RGBA")
        lw = int(r * 1.5)
        lg = lg.resize((lw, int(lw * lg.height / lg.width)), Image.LANCZOS)
        img.alpha_composite(lg, (int(cx - lg.width / 2), int(cy - lg.height / 2)))
        title = self.e.get("title", "المنهجية")
        d.text((cx - 56 * k, cy - 14 * k), title, font=font("kufi", 30, 800), fill="#FFFFFF", anchor="rm", **_kw(title))
        sub = self.e.get("status", "متصل الآن")
        d.text((cx - 56 * k, cy + 26 * k), sub, font=font("almarai", 22), fill=rgb("#F3D9FF"), anchor="rm", **_kw(sub))
        # back chevron on the left
        d.line([(b + 52 * k, cy - 16 * k), (b + 36 * k, cy), (b + 52 * k, cy + 16 * k)], fill="#FFFFFF", width=5 * k)
        # notch
        d.rounded_rectangle([W / 2 - 70 * k, b + 10 * k, W / 2 + 70 * k, b + 34 * k], radius=12 * k, fill=rgb("#17091F"))
        return img

    def _bubble(self, m):
        k = self.K
        me = m.get("from") == "me"
        if m.get("kind") == "contact":
            w, h = int(self.sw * 0.78) * k, 214 * k
            img = Image.new("RGBA", (w + 24 * k, h + 24 * k), (0, 0, 0, 0))
            sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([12 * k, 18 * k, w + 12 * k, h + 18 * k], radius=30 * k, fill=(40, 10, 50, 70))
            img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8 * k)))
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([12 * k, 10 * k, w + 12 * k, h + 10 * k], radius=30 * k, fill="#FFFFFF")
            d.rounded_rectangle([12 * k, 10 * k, w + 12 * k, 96 * k], radius=30 * k, fill=rgb(C["green"]))
            d.rectangle([12 * k, 60 * k, w + 12 * k, 96 * k], fill=rgb(C["green"]))
            lab = m.get("label", "راسلنا على واتساب")
            d.text((w - 18 * k, 53 * k), lab, font=font("almarai-xb", 28), fill="#FFFFFF", anchor="rm", **_kw(lab))
            gx, gy, gr = 62 * k, 53 * k, 24 * k
            d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill="#FFFFFF")
            d.text((gx, gy + 2 * k), "☎", font=font("latin", 24), fill=rgb(C["green"]), anchor="mm")
            d.text((w / 2 + 12 * k, 146 * k), kit.CONTACT["whatsapp"], font=font("latin", 38), fill=rgb(C["ink"]), anchor="mm")
            sub = m.get("text", "الاستشارة الأولى مجانية")
            d.text((w / 2 + 12 * k, 192 * k), sub, font=font("almarai-xb", 24), fill=rgb(C["purple"]), anchor="mm", **_kw(sub))
            return img
        lines = _wrap(m["text"], self.f_msg, self.maxw)
        lh = 44 * k
        tw = max(self.f_msg.getlength(l, **_kw(l)) for l in lines)
        w, h = int(tw + 44 * k), int(len(lines) * lh + 34 * k)
        img = Image.new("RGBA", (w + 24 * k, h + 24 * k), (0, 0, 0, 0))
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([12 * k, 16 * k, w + 12 * k, h + 16 * k], radius=26 * k, fill=(40, 10, 50, 50))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6 * k)))
        d = ImageDraw.Draw(img)
        fill = rgb("#D9FDD3") if me else rgb(m.get("bg", "#FFFFFF"))
        d.rounded_rectangle([12 * k, 10 * k, w + 12 * k, h + 10 * k], radius=26 * k, fill=fill)
        ink = rgb(m.get("color", C["ink"]))
        for i, l in enumerate(lines):
            d.text((w - 10 * k, 10 * k + 17 * k + lh * i + lh / 2), l, font=self.f_msg, fill=ink, anchor="rm", **_kw(l))
        if me:   # double tick, bottom-left
            for o in (0, 9):
                x0, y0 = 26 * k + o * k, h - 4 * k
                d.line([(x0, y0 - 6 * k), (x0 + 6 * k, y0), (x0 + 16 * k, y0 - 12 * k)], fill=rgb("#34B7F1"), width=3 * k)
        return img

    def times(self):
        """(time, sfx) pairs: a key click per typed letter, a send swoosh, a pop per reply."""
        out = []
        for m in self.msgs:
            if "type0" in m:
                n = len(m["text"])
                step = (m["show"] - m["type0"]) / max(n, 1)
                out += [(m["type0"] + i * step, "click") for i in range(0, n, 2)]
                out.append((m["show"], "send"))
            else:
                out.append((m["show"], "pop"))
        return out

    # ---- per frame
    def draw(self, frame, t):
        e = self.e
        t0 = e.get("t", 0)
        if t < t0:
            return
        k = self.K
        p_in = ease_out_cubic(clamp((t - t0) / e.get("in_dur", 0.5)))
        lay = self.frame_img.copy()
        b = self.bez * k
        ax0, ay0 = b, b + self.head_h * k
        aw, ah = self.sw * k, self.area_h * k
        # chat area
        area = Image.new("RGBA", (aw, ah), (0, 0, 0, 0))
        gap = 14 * k
        items = []
        for m in self.msgs:
            if t >= m["show"]:
                q = clamp((t - m["show"]) / 0.32)
                items.append((m, m["spr"], q))
            elif "dots0" in m and t >= m["dots0"] and m["show"] > m["dots0"]:
                items.append((m, None, 1.0))
        heights = []
        for m, spr, q in items:
            hh = (spr.height if spr is not None else 74 * k) + gap
            heights.append(hh * (ease_out_cubic(q) if spr is not None else 1))
        total = sum(heights) + 24 * k
        off = max(0.0, total - ah)
        y = 18 * k - off
        for (m, spr, q), hh in zip(items, heights):
            me = m.get("from") == "me"
            if spr is None:   # typing dots bubble on the right
                bw_, bh_ = 128 * k, 64 * k
                bx = aw - 22 * k - bw_
                dd = ImageDraw.Draw(area)
                dd.rounded_rectangle([bx, y, bx + bw_, y + bh_], radius=30 * k, fill="#FFFFFF")
                for i in range(3):
                    ph = (t * 4.2 - i * 0.55)
                    lift = max(0.0, math.sin(ph * math.pi)) * 9 * k
                    cx = bx + bw_ / 2 + (i - 1) * 28 * k
                    cy = y + bh_ / 2 - lift
                    dd.ellipse([cx - 8 * k, cy - 8 * k, cx + 8 * k, cy + 8 * k], fill=rgb("#9A8AA6"))
                y += hh
                continue
            qq = ease_out_back(q, 1.4)
            s_ = _mul_alpha(spr, clamp(q * 2.2))
            if q < 1:
                s_ = s_.resize((max(1, int(spr.width * (0.7 + 0.3 * qq))), max(1, int(spr.height * (0.7 + 0.3 * qq)))), Image.BILINEAR)
            if me:
                bx = 10 * k
                yy = y + (1 - ease_out_cubic(q)) * 70 * k
            else:
                bx = aw - 10 * k - s_.width
                yy = y
            if yy + s_.height > 1 and yy < area.height:
                area.alpha_composite(s_, (int(bx), int(yy)) if yy >= 0 else (int(bx), 0),
                                     (0, int(-yy)) if yy < 0 else (0, 0))
            y += hh
        amask = Image.new("L", (aw, ah), 0)
        ImageDraw.Draw(amask).rectangle([0, 0, aw, ah], fill=255)
        lay.alpha_composite(area, (ax0, ay0))
        # input bar
        d = ImageDraw.Draw(lay)
        iy0 = ay0 + ah
        d.rectangle([ax0, iy0, ax0 + aw, iy0 + self.in_h * k - 1], fill=rgb("#F7F2FA"))
        fx0, fx1 = ax0 + 18 * k, ax0 + aw - 104 * k
        fy0, fy1 = iy0 + 18 * k, iy0 + 18 * k + 70 * k
        d.rounded_rectangle([fx0, fy0, fx1, fy1], radius=35 * k, fill="#FFFFFF", outline=rgb("#E2D6EA"), width=2 * k)
        sx_, sy_ = ax0 + aw - 54 * k, (fy0 + fy1) / 2
        typing = None
        for m in self.msgs:
            if "type0" in m and m["type0"] <= t < m["show"]:
                typing = m
        send_hot = any("type0" in m and 0 <= t - m["show"] < 0.25 for m in self.msgs)
        rr = 38 * k * (0.86 if send_hot else 1)
        d.ellipse([sx_ - rr, sy_ - rr, sx_ + rr, sy_ + rr], fill=rgb(C["green"]))
        d.polygon([(sx_ - 15 * k, sy_ - 15 * k), (sx_ + 17 * k, sy_), (sx_ - 15 * k, sy_ + 15 * k), (sx_ - 8 * k, sy_)], fill="#FFFFFF")
        if typing:
            n = len(typing["text"])
            c = int(n * clamp((t - typing["type0"]) / (typing["show"] - typing["type0"])))
            txt = typing["text"][:c]
            # show the tail that fits, RTL: text grows leftwards from the right edge of the field
            maxw = (fx1 - fx0) - 50 * k
            while txt and self.f_in.getlength(txt, **_kw(txt)) > maxw:
                sp = txt.find(" ")
                txt = txt[sp + 1:] if sp >= 0 else txt[1:]
            tx = fx1 - 26 * k
            if txt:
                d.text((tx, (fy0 + fy1) / 2), txt, font=self.f_in, fill=rgb(C["ink"]), anchor="rm", **_kw(txt))
                lw = self.f_in.getlength(txt, **_kw(txt))
            else:
                lw = 0
            if int(t * 3) % 2 == 0:
                cx = tx - lw - 6 * k
                d.rectangle([cx - 2 * k, (fy0 + fy1) / 2 - 20 * k, cx + 2 * k, (fy0 + fy1) / 2 + 20 * k], fill=rgb(C["purple"]))
        else:
            ph = self.e.get("placeholder", "اكتب رسالة")
            d.text((fx1 - 26 * k, (fy0 + fy1) / 2), ph, font=font("almarai", 26), fill=rgb("#A99BB4"), anchor="rm", **_kw(ph))
        # round the screen corners again (area may have painted over them)
        out = lay.resize((self.w, self.h), Image.LANCZOS)
        if p_in < 1:
            out = _mul_alpha(out, p_in)
        x, y_ = e.get("x", 540), e.get("y", 760) + (1 - p_in) * 160
        # soft shadow
        place(frame, self._shadow(), x, y_ + 26, 0.9 * p_in)
        place(frame, out, x, y_)

    def _shadow(self):
        if not hasattr(self, "_sh"):
            pad = 60
            sh = Image.new("RGBA", (self.w + 2 * pad, self.h + 2 * pad), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([pad, pad, pad + self.w, pad + self.h], radius=74, fill=(15, 3, 22, 150))
            self._sh = sh.filter(ImageFilter.GaussianBlur(26))
        return self._sh


class DynProof:
    K = 2

    def __init__(self, e):
        self.e = e
        k = self.K
        self.w, self.h = e.get("w", 860), e.get("h", 620)
        self.mode = e.get("mode", "loupe")
        self.f = font("almarai-bold", e.get("size", 38))
        self.lh = e.get("line_h", 92)
        self.top = e.get("pad_top", 96)
        self.lines = e["lines"]
        self.dirty, self.clean, self.boxes = self._pages()
        self.t0, self.dur = e.get("t", 0.0), e.get("dur", 3.0)
        n = len(self.lines)
        # loupe timing: one line per slice of the duration
        self.slice = self.dur / n

    def _line_words(self, words, y, d, errs, mode):
        """Place words right to left; returns their boxes (2x px)."""
        k = self.K
        x = (self.w - 60) * k
        sp = self.f.getlength(" ")
        boxes = []
        for i, w in enumerate(words):
            wl = self.f.getlength(w, **_kw(w))
            x0, x1 = x - wl, x
            boxes.append((x0, x1))
            col = rgb(C["ink"])
            if mode == "dirty" and i in errs:
                col = rgb("#D7263D")
            if mode == "clean" and i in errs:
                col = rgb("#128A43")
            if d is not None:
                if mode == "clean" and i in errs:
                    d.rounded_rectangle([x0 - 8 * k, y - 30 * k, x1 + 8 * k, y + 30 * k], radius=12 * k, fill=rgb("#DDF6E5"))
                d.text((x1, y), w, font=self.f, fill=col, anchor="rm", **_kw(w))
                if mode == "dirty" and i in errs:   # red wavy underline
                    pts, xx = [], x0
                    while xx <= x1:
                        pts.append((xx, y + 30 * k + 5 * k * math.sin((xx - x0) / (6 * k))))
                        xx += 2 * k
                    if len(pts) > 1:
                        d.line(pts, fill=rgb("#D7263D"), width=3 * k)
            x = x0 - sp
        return boxes

    def _pages(self):
        k = self.K
        W, H = self.w * k, self.h * k
        out, boxes = [], []
        for mode in ("dirty", "clean"):
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([0, 0, W - 1, H - 1], radius=28 * k, fill="#FFFFFF")
            # header strip + page fold motif
            d.rounded_rectangle([60 * k, 34 * k, W - 60 * k, 52 * k], radius=9 * k, fill=rgb(C["purple"]))
            d.rounded_rectangle([W - 260 * k, 34 * k, W - 60 * k, 52 * k], radius=9 * k, fill=rgb(C["pink"]))
            bx = []
            for i, ln in enumerate(self.lines):
                y = (self.top + i * self.lh + self.lh / 2) * k
                if self.mode == "loupe":
                    words = (ln["clean"] if mode == "clean" else ln["dirty"]).split()
                    bx.append(self._line_words(words, y, d, set(ln.get("errs", [])), mode))
                else:
                    words = ln["text"].split()
                    bx.append(self._line_words(words, y, d, set(), "plain"))
            out.append(img)
            boxes.append(bx)
        return out[0], out[1], boxes[0]

    def times(self):
        if self.mode == "scan":
            out = [(self.t0, "scan")]
            for i, ln in enumerate(self.lines):
                if ln.get("quote"):
                    out.append((self._line_t(i) + 0.1, "pen"))
            return out
        out = []
        for i, ln in enumerate(self.lines):
            for j in ln.get("errs", []):
                out.append((self._word_t(i, j), "fix"))
        return out

    # loupe x position along line i at local progress u (RTL: right -> left)
    def _loupe_x(self, u):
        return (self.w - 70) - u * (self.w - 140)

    def _word_t(self, i, j):
        x0, x1 = self.boxes[i][j]
        cx = (x0 + x1) / 2 / self.K
        u = ((self.w - 70) - cx) / (self.w - 140)
        return self.t0 + self.slice * (i + clamp(u))

    def _line_t(self, i):
        return self.t0 + self.dur * (self.top + i * self.lh + self.lh / 2) / self.h

    def draw(self, frame, t):
        e = self.e
        k = self.K
        appear = e.get("appear", self.t0 - 0.5)
        if t < appear:
            return
        pa = ease_out_cubic(clamp((t - appear) / 0.45))
        x, y = e.get("x", 540), e.get("y", 760)
        if self.mode == "loupe":
            page = self.dirty.copy()
            if t > self.t0:
                pos = (t - self.t0) / self.slice
                li = int(pos)
                u = pos - li
                m = Image.new("L", page.size, 0)
                md = ImageDraw.Draw(m)
                for i in range(len(self.lines)):
                    y0 = (self.top + i * self.lh) * k
                    y1 = y0 + self.lh * k
                    if i < li:
                        md.rectangle([0, y0, page.width, y1], fill=255)
                    elif i == li and li < len(self.lines):
                        lx = self._loupe_x(clamp(u)) * k
                        md.rectangle([lx, y0, page.width, y1], fill=255)
                page.paste(self.clean, (0, 0), m)
            out = page.resize((self.w, self.h), Image.LANCZOS)
            place(frame, self._shadow(), x, y + 20 + (1 - pa) * 120, 0.85 * pa)
            place(frame, _mul_alpha(out, pa), x, y + (1 - pa) * 120)
            # the loupe
            if self.t0 <= t < self.t0 + self.dur + 0.6:
                pos = clamp((t - self.t0) / self.slice, 0, len(self.lines) - 1e-3)
                li = int(pos)
                u = clamp(pos - li)
                lx = self._loupe_x(u)
                ly = self.top + li * self.lh + self.lh / 2
                if t >= self.t0 + self.dur:   # leaves to the bottom-left
                    q = ease_out_cubic(clamp((t - self.t0 - self.dur) / 0.6))
                    lx -= 300 * q
                    ly += 260 * q
                self._loupe(frame, x - self.w / 2 + lx, y - self.h / 2 + ly, lx, ly)
        else:
            page = self.dirty.copy()
            d = ImageDraw.Draw(page)
            beam_y = self.h * clamp((t - self.t0) / self.dur) if t >= self.t0 else -1
            for i, ln in enumerate(self.lines):
                if not ln.get("quote"):
                    continue
                lt = self._line_t(i)
                q = ease_out_cubic(clamp((t - lt) / 0.45))
                if q <= 0:
                    continue
                bxs = self.boxes[i]
                xr, xl = bxs[0][1] + 10 * k, bxs[-1][0] - 10 * k
                yc = (self.top + i * self.lh + self.lh / 2) * k
                cur = xr - (xr - xl) * q
                hl = Image.new("RGBA", page.size, (0, 0, 0, 0))
                ImageDraw.Draw(hl).rounded_rectangle([cur, yc - 28 * k, xr, yc + 28 * k], radius=10 * k,
                                                     fill=rgb(ln.get("hl", C["yellow"]))[:3] + (110,))
                page = Image.alpha_composite(page, hl)
                # redraw the words above the highlight
                self._line_words(ln["text"].split(), yc, ImageDraw.Draw(page), set(), "plain")
                tag = ln.get("tag")
                tq = clamp((t - lt - 0.5) / 0.3)
                if tag and tq > 0:
                    d2 = ImageDraw.Draw(page)
                    ft = font("almarai-xb", 22)
                    tw = ft.getlength(tag, **_kw(tag)) + 34 * k
                    tx1 = xl - 8 * k
                    tx0 = tx1 - tw
                    if tx0 < 30 * k:      # no room on the left: hang it under the line end
                        tx0, tx1 = 30 * k, 30 * k + tw
                    col = rgb(ln.get("tagc", C["purple"]))
                    d2.rounded_rectangle([tx0, yc - 22 * k, tx1, yc + 22 * k], radius=22 * k, fill=col[:3] + (int(255 * tq),))
                    d2.text(((tx0 + tx1) / 2, yc), tag, font=ft, fill=(255, 255, 255, int(255 * tq)), anchor="mm", **_kw(tag))
            if 0 <= beam_y <= self.h and t < self.t0 + self.dur:
                by = beam_y * k
                glow = Image.new("RGBA", page.size, (0, 0, 0, 0))
                gd = ImageDraw.Draw(glow)
                for j in range(14):
                    a = int(70 * (1 - j / 14))
                    gd.rectangle([0, by - j * 6 * k, page.width, by - (j - 1) * 6 * k], fill=rgb(C["magenta"])[:3] + (a // 2,))
                gd.rectangle([0, by - 3 * k, page.width, by + 3 * k], fill=rgb(C["pink"]))
                gm = Image.new("L", page.size, 0)
                ImageDraw.Draw(gm).rounded_rectangle([0, 0, page.width - 1, page.height - 1], radius=28 * k, fill=255)
                glow.putalpha(Image.fromarray(np.minimum(np.asarray(glow.getchannel("A")), np.asarray(gm))))
                page = Image.alpha_composite(page, glow)
            out = page.resize((self.w, self.h), Image.LANCZOS)
            place(frame, self._shadow(), x, y + 20 + (1 - pa) * 120, 0.85 * pa)
            place(frame, _mul_alpha(out, pa), x, y + (1 - pa) * 120)

    def _loupe(self, frame, fx, fy, lx, ly):
        """Magnifier at frame (fx, fy) showing page point (lx, ly) of the DIRTY page, 1.9x."""
        k = self.K
        r = self.e.get("loupe_r", 120)
        mag = self.e.get("mag", 1.9)
        src_r = r / mag * k
        cx, cy = lx * k, ly * k
        box = (cx - src_r, cy - src_r, cx + src_r, cy + src_r)
        pad = Image.new("RGBA", (int(2 * src_r) + 2, int(2 * src_r) + 2), (255, 255, 255, 255))
        crop = self.dirty.crop(tuple(int(v) for v in box))
        pad.alpha_composite(crop)
        zoom = pad.resize((2 * r * k, 2 * r * k), Image.LANCZOS)
        S2 = 2 * r * k + 120 * k
        lay = Image.new("RGBA", (S2 + 160 * k, S2 + 160 * k), (0, 0, 0, 0))
        c = S2 / 2
        m = Image.new("L", zoom.size, 0)
        ImageDraw.Draw(m).ellipse([0, 0, zoom.width - 1, zoom.height - 1], fill=255)
        d = ImageDraw.Draw(lay)
        # handle toward bottom-left
        ang = math.radians(135)
        hx0, hy0 = c + (r + 6) * k * math.cos(ang), c + (r + 6) * k * math.sin(ang)
        hx1, hy1 = c + (r + 120) * k * math.cos(ang), c + (r + 120) * k * math.sin(ang)
        d.line([(hx0, hy0), (hx1, hy1)], fill=rgb(C["plum"]), width=30 * k)
        d.ellipse([hx1 - 15 * k, hy1 - 15 * k, hx1 + 15 * k, hy1 + 15 * k], fill=rgb(C["plum"]))
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([c - r * k, c - r * k + 14 * k, c + r * k, c + r * k + 14 * k], fill=(20, 4, 30, 110))
        lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12 * k)))
        lay.paste(zoom, (int(c - r * k), int(c - r * k)), m)
        d = ImageDraw.Draw(lay)
        d.ellipse([c - r * k, c - r * k, c + r * k, c + r * k], outline=rgb(C["yellow"]), width=12 * k)
        d.ellipse([c - (r - 7) * k, c - (r - 7) * k, c + (r - 7) * k, c + (r - 7) * k], outline=rgb(C["orange"]), width=3 * k)
        # glint
        d.arc([c - (r - 22) * k, c - (r - 22) * k, c + (r - 22) * k, c + (r - 22) * k], 200, 245, fill=(255, 255, 255, 170), width=7 * k)
        out = lay.resize((lay.width // k, lay.height // k), Image.LANCZOS)
        place(frame, out, fx + (out.width / 2 - c / k), fy + (out.height / 2 - c / k))

    def _shadow(self):
        if not hasattr(self, "_sh"):
            pad = 60
            sh = Image.new("RGBA", (self.w + 2 * pad, self.h + 2 * pad), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([pad, pad, pad + self.w, pad + self.h], radius=28, fill=(15, 3, 22, 120))
            self._sh = sh.filter(ImageFilter.GaussianBlur(24))
        return self._sh


class DynSnap:
    """Blocks of a page start crooked and scattered; dashed margin guides draw on, then each
    block snaps onto its place with a small overshoot. Blocks: {kind: title|para|figure|num,
    y, h, w?, dx, dy, rot, t}."""
    K = 2

    def __init__(self, e):
        self.e = e
        self.w, self.h = e.get("w", 700), e.get("h", 880)
        self.m = e.get("margin", 70)
        self.blocks = []
        for b in e["blocks"]:
            self.blocks.append((b, self._block(b)))

    def _block(self, b):
        k = self.K
        bw = b.get("w", self.w - 2 * self.m)
        bh = b["h"]
        img = Image.new("RGBA", ((bw + 20) * k, (bh + 20) * k), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        o = 10 * k
        kind = b["kind"]
        if kind == "title":
            d.rounded_rectangle([o, o, o + bw * k, o + bh * k], radius=14 * k, fill=rgb(C["purple"]))
            txt = b.get("text", "")
            if txt:
                d.text((o + bw * k / 2, o + bh * k / 2), txt, font=font("kufi", b.get("size", 30), 800),
                       fill="#FFFFFF", anchor="mm", **_kw(txt))
        elif kind == "para":
            n = max(1, int((bh + 6) // 30))
            for i in range(n):
                ww = bw * (0.62 if i == n - 1 else 1.0)
                d.rounded_rectangle([o + (bw - ww) * k, o + i * 30 * k, o + bw * k, o + (i * 30 + 14) * k],
                                    radius=7 * k, fill=rgb("#CFC3D8"))
        elif kind == "figure":
            d.rounded_rectangle([o, o, o + bw * k, o + bh * k], radius=16 * k, fill=rgb("#F1E9F6"),
                                outline=rgb("#D8C6E4"), width=2 * k)
            cols = [C["purple"], C["magenta"], C["pink"], C["orange"], C["yellow"]]
            n = 5
            gw = bw / (n * 1.6)
            for i in range(n):
                hh = bh * (0.3 + 0.12 * ((i * 3) % 5))
                x0 = o + (bw * 0.12 + i * gw * 1.5) * k
                d.rounded_rectangle([x0, o + (bh - 18 - hh) * k, x0 + gw * k, o + (bh - 18) * k], radius=6 * k, fill=rgb(cols[i]))
        elif kind == "num":
            d.ellipse([o, o, o + bw * k, o + bh * k], fill=rgb(C["plum"]))
            d.text((o + bw * k / 2, o + bh * k / 2), b.get("text", "1"), font=font("latin", 20), fill="#FFFFFF", anchor="mm")
        return img.resize((img.width // k, img.height // k), Image.LANCZOS)

    def times(self):
        return [(self.e.get("t", 0) + b["t"] + b.get("dur", 0.45) * 0.8, "snap") for b, _ in self.blocks]

    def draw(self, frame, t):
        e = self.e
        t0 = e.get("t", 0)
        if t < t0 - 0.4:
            return
        lt = t - t0
        pa = ease_out_cubic(clamp((lt + 0.4) / 0.4))
        x, y = e.get("x", 540), e.get("y", 760)
        px0, py0 = x - self.w / 2, y - self.h / 2
        k = 2
        # page
        if not hasattr(self, "_page"):
            pg = Image.new("RGBA", (self.w * k + 120, self.h * k + 140), (0, 0, 0, 0))
            sh = Image.new("RGBA", pg.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([60, 80, 60 + self.w * k, 80 + self.h * k], radius=26 * k, fill=(15, 3, 22, 120))
            pg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24 * k)))
            ImageDraw.Draw(pg).rounded_rectangle([60, 60, 60 + self.w * k, 60 + self.h * k], radius=26 * k, fill="#FFFFFF")
            self._page = pg.resize((pg.width // k, pg.height // k), Image.LANCZOS)
        place(frame, _mul_alpha(self._page, pa), x, y + 10 + (1 - pa) * 100)
        # guides: dashed lines drawn on from the corners
        gq = clamp((lt - e.get("guides_t", 0.0)) / 0.6)
        if gq > 0:
            m = self.m
            col = rgb(C["pink"])
            def fn(d, ox, oy, kk):
                L = gq
                segs = [((px0 + m, py0 + 20), (px0 + m, py0 + 20 + (self.h - 40) * L)),
                        ((px0 + self.w - m, py0 + 20), (px0 + self.w - m, py0 + 20 + (self.h - 40) * L)),
                        ((px0 + 20, py0 + m), (px0 + 20 + (self.w - 40) * L, py0 + m)),
                        ((px0 + 20, py0 + self.h - m), (px0 + 20 + (self.w - 40) * L, py0 + self.h - m))]
                for (a, b) in segs:
                    n = int(math.dist(a, b) // 18)
                    for i in range(n):
                        if i % 2:
                            continue
                        u0, u1 = i / max(n, 1), (i + 1) / max(n, 1)
                        p0 = (a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0)
                        p1 = (a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1)
                        d.line([((p0[0] - ox) * kk, (p0[1] - oy) * kk), ((p1[0] - ox) * kk, (p1[1] - oy) * kk)],
                               fill=col[:3] + (200,), width=3 * kk)
            _overlay_draw(frame, (px0, py0, px0 + self.w, py0 + self.h), fn)
        for b, spr in self.blocks:
            q = clamp((lt - b["t"]) / b.get("dur", 0.45))
            qq = ease_out_back(q, 2.0) if q > 0 else 0
            bw = b.get("w", self.w - 2 * self.m)
            tx = px0 + self.w - self.m - bw / 2 + b.get("xoff", 0)
            ty = py0 + b["y"] + b["h"] / 2
            cx = tx + b.get("dx", 0) * (1 - qq)
            cy = ty + b.get("dy", 0) * (1 - qq)
            rot = b.get("rot", 0) * (1 - qq)
            s_ = spr.rotate(rot, resample=Image.BICUBIC, expand=True) if abs(rot) > 0.2 else spr
            place(frame, _mul_alpha(s_, pa), cx, cy)
            if 0 < q < 1 and q > 0.6:   # snap flash
                fl = 1 - (q - 0.6) / 0.4
                def fn2(d, ox, oy, kk, cx=cx, cy=cy, bw=bw, bh=b["h"], fl=fl):
                    d.rounded_rectangle([(cx - bw / 2 - 8 - ox) * kk, (cy - bh / 2 - 8 - oy) * kk,
                                         (cx + bw / 2 + 8 - ox) * kk, (cy + bh / 2 + 8 - oy) * kk],
                                        radius=14 * kk, outline=rgb(C["yellow"])[:3] + (int(255 * fl),), width=4 * kk)
                _overlay_draw(frame, (cx - bw / 2 - 20, cy - b["h"] / 2 - 20, cx + bw / 2 + 20, cy + b["h"] / 2 + 20), fn2)


class DynOrbit:
    """batch-04 `orbit`: decorative imagery for the lower third that Meta's safe zone keeps
    free of words — broken ring-gradient arcs and a satellite dot turning slowly, so the
    bottom of the frame keeps moving without carrying text. May bleed off the frame."""

    def __init__(self, e):
        self.e = e
        r = e.get("r", 300)
        size = int(2 * r + 40)
        k = 2
        img = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
        m = Image.new("L", img.size, 0)
        d = ImageDraw.Draw(m)
        c = size * k / 2
        a = e.get("alpha", 120)
        for rr, w, segs in ((r, e.get("width", 26), [(10, 120), (150, 250), (275, 335)]),
                            (r * 0.72, 8, [(40, 200), (230, 350)])):
            for a0, a1 in segs:
                d.arc([c - rr * k, c - rr * k, c + rr * k, c + rr * k], a0, a1, fill=a, width=int(w * k))
        img.paste(linear_gradient(img.size, RING, 45), (0, 0), m)
        dd = ImageDraw.Draw(img)
        sr = 14 * k
        dd.ellipse([c + r * k - sr, c - sr, c + r * k + sr, c + sr], fill=rgb(C["yellow"])[:3] + (min(255, a + 80),))
        self.spr = img.resize((size, size), Image.LANCZOS)

    def times(self):
        return []

    def draw(self, frame, t):
        e = self.e
        al = clamp((t - e.get("t", 0)) / 0.5)
        if al <= 0:
            return
        ang = e.get("a0", 0) + t * e.get("spin", 14)
        spr = self.spr.rotate(ang, resample=Image.BILINEAR)
        place(frame, spr, e["x"], e["y"], al)


DYNAMIC = {"path": DynPath, "chart": DynChart, "typewriter": DynTypewriter, "scatter": DynScatter, "burst": DynBurst,
           "likert": DynLikert, "mark": DynMark, "fly": DynFly,
           "split": DynSplit, "timer": DynTimer,
           "phone": DynPhone, "proof": DynProof, "snap": DynSnap, "orbit": DynOrbit}


# ------------------------------------------------------------------ animation
def place(frame, spr, cx, cy, alpha=1.0, scale=1.0, sx=1.0):
    if alpha <= 0.01:
        return
    s = spr
    if abs(scale - 1.0) > 0.005 or abs(sx - 1.0) > 0.005:
        s = spr.resize((max(1, int(spr.width * scale * sx)), max(1, int(spr.height * scale))),
                       Image.BILINEAR)
    if alpha < 0.999:
        a = s.getchannel("A").point(lambda v: int(v * alpha))
        s = s.copy()
        s.putalpha(a)
    x, y = int(cx - s.width / 2), int(cy - s.height / 2)
    frame.alpha_composite(s, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


def place_world(frame, spr, cx, cy, s, alpha=1.0):
    """Place a (hi-res) sprite scaled by s, cropping to the visible part *before* resizing,
    so a sprite blown up 6x by the dolly camera costs no more than one screen of pixels."""
    if alpha <= 0.01 or s <= 0:
        return
    W2, H2 = spr.width * s, spr.height * s
    x0, y0 = cx - W2 / 2, cy - H2 / 2
    vx0, vy0, vx1, vy1 = max(0.0, x0), max(0.0, y0), min(float(RW), x0 + W2), min(float(RH), y0 + H2)
    if vx1 - vx0 < 1 or vy1 - vy0 < 1:
        return
    box = ((vx0 - x0) / s, (vy0 - y0) / s, (vx1 - x0) / s, (vy1 - y0) / s)
    part = spr.resize((max(1, int(round(vx1 - vx0))), max(1, int(round(vy1 - vy0)))), Image.BILINEAR, box=box)
    if alpha < 0.999:
        part.putalpha(part.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(part, (int(vx0), int(vy0)))


def iris(spr, p):
    """Sprite revealed through a growing circle (p 0..1)."""
    w, h = spr.size
    r = ease_out_cubic(p) * math.hypot(w, h) / 2
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r], fill=255)
    out = spr.copy()
    out.putalpha(Image.fromarray((np.asarray(spr.getchannel("A"), dtype=np.uint16) * np.asarray(m, dtype=np.uint16) // 255).astype("uint8")))
    return out


RES_KEYS = ("size", "w", "h", "radius", "width", "padx", "scale")


def at_res(e, r):
    """Copy of a sprite spec with its pixel sizes multiplied by r (built hi-res for the dolly)."""
    if r == 1:
        return e
    e2 = dict(e)
    if e2["type"] == "pill":
        e2.setdefault("padx", 46)
    if e2["type"] == "logo":
        e2["width"] = e2.get("width", 300) * r
    for k in RES_KEYS:
        if k in e2 and isinstance(e2[k], (int, float)) and not isinstance(e2[k], bool):
            e2[k] = int(round(e2[k] * r)) if k != "scale" else e2[k] * r
    return e2


def dolly_at(keys, t):
    """World camera keyframes [[t, zoom, cx, cy], ...]: eased between keys, zoom in log space
    so a 6x pull-back feels like one steady move (powers-of-ten style)."""
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = (t - a[0]) / max(b[0] - a[0], 1e-6)
            u = u * u * (3 - 2 * u)
            z = math.exp(math.log(a[1]) + (math.log(b[1]) - math.log(a[1])) * u)
            return z, a[2] + (b[2] - a[2]) * u, a[3] + (b[3] - a[3]) * u
    return keys[-1][1:]


def animate(e, t):
    """Base entrance animation, then the batch-03 modifiers: a button `press` (squash and
    rebound at that time) and a generic `out` exit (fades and swells away)."""
    a = _animate_in(e, t)
    if a is None:
        return None
    dx, dy, al, sc = a[:4]
    sx = a[4] if len(a) > 4 else 1.0
    if "press" in e:
        q = (t - e["press"]) / 0.4
        if 0 <= q < 1:
            sc *= (1 - 0.18 * math.sin(math.pi * q * 2)) if q < 0.5 else (1 + 0.08 * math.sin(math.pi * (q - 0.5) * 2))
    if "out" in e and t >= e["out"]:
        q = clamp((t - e["out"]) / e.get("out_dur", 0.25))
        al *= 1 - q
        sc *= 1 + 0.25 * q
    return dx, dy, al, sc, sx


def _animate_in(e, t):
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
    if anim == "iris":
        # circular mask reveal from the centre; handled in scene_frame
        return 0, 0, 1.0, 1.0
    if anim == "wipe":
        # mask reveal from the right edge (RTL reading direction); handled in scene_frame
        return 0, 0, 1.0, 1.0
    if anim == "flip":   # turns over on its vertical axis, the way a page is turned
        q = ease_out_cubic(p)
        return 0, 0, 1.0, 1.0, max(abs(math.cos(q * math.pi)), 0.02)
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
                elif "dolly" in sc and not e.get("hud"):
                    r = e.get("res", 1)
                    els.append(({**e, "_res": r}, build_sprite(at_res(e, r)), e["x"], e["y"]))
                else:
                    els.append((e, build_sprite(e), e["x"], e["y"]))
            dur = sc["dur"]
            self.scenes.append(dict(start=start, dur=dur, bg=bg, glow=glow, els=els, dolly=sc.get("dolly"),
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
                elif e["type"] == "likert":
                    self.sfx += [(sc["start"] + pk[0], "tick") for pk in e.get("picks", [])]
                elif e["type"] == "mark":
                    self.sfx.append((t0, "pen"))
                elif e["type"] == "fly":
                    self.sfx += [(sc["start"] + e.get("go", 1.0) + i * e.get("stagger", 0.12), "flick")
                                 for i in range(len(e["items"]))]
                elif e.get("anim") == "iris":
                    self.sfx.append((t0, "whoosh"))
                elif e["type"] in ("phone", "proof", "snap"):   # batch-04: scene-local (time, sfx) pairs
                    self.sfx += [(sc["start"] + tt, kd) for tt, kd in DYNAMIC[e["type"]](e).times()]
                if "press" in e:
                    self.sfx.append((sc["start"] + e["press"], "tap"))
            if raw.get("dolly"):
                k = raw["dolly"]
                moves = [a[0] for a, b in zip(k, k[1:]) if a[1] != b[1]]
                if moves:
                    self.sfx.append((sc["start"] + moves[0], "swell"))
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
                if "out" not in e or t < e["out"]:
                    e["dyn"].draw(f, t)
                continue
            a = animate(e, t)
            if a is None:
                continue
            dx, dy, al, scale, sx = a
            if "cycle" in e:
                k = min(int(max(t - e["t"], 0) / e["every"]), len(e["cycle"]) - 1)
                spr = e["cycle"][k]
            if sc.get("dolly"):
                z, wx, wy = dolly_at(sc["dolly"], t)
                place_world(f, spr, RW / 2 + (x + dx - wx) * z, RH / 2 + (y + dy - wy) * z,
                            scale * z / e.get("_res", 1), al)
                continue
            if e.get("anim") == "iris":
                p = clamp((t - e.get("t", 0)) / e.get("dur", 0.55))
                place(f, iris(spr, p) if p < 1 else spr, x, y, al, scale)
                continue
            if e.get("anim") == "wipe":
                p = ease_out_cubic(clamp((t - e.get("t", 0)) / e.get("dur", 0.55)))
                keep = max(1, int(spr.width * p))
                part = spr.crop((spr.width - keep, 0, spr.width, spr.height))
                place(f, part, x + spr.width / 2 - keep / 2, y)
                continue
            place(f, spr, x + dx, y + dy, al, scale, sx)
        f = self.camera(sc, f, t)
        # HUD elements sit on top of the camera move (titles, brand bug)
        for e, spr, x, y in hud:
            if "dyn" in e:
                e["dyn"].draw(f, t)
                continue
            a = animate(e, t)
            if a is None:
                continue
            dx, dy, al, scale, sx = a
            place(f, spr, x + dx, y + dy, al, scale, sx)
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
    # batch-03 — B minor, focused/tense: Bm - G - D - A (a questionnaire under review)
    "focus": [[123.47, 146.83, 185.0], [98.0, 123.47, 146.83], [146.83, 185.0, 220.0], [110.0, 138.59, 164.81]],
    # batch-04 — F major, warm and settled: F - Dm - Bb - C (a page put right)
    "bloom": [[174.61, 220.0, 261.63], [146.83, 174.61, 220.0], [116.54, 146.83, 174.61], [130.81, 164.81, 196.0]],
    # batch-04 — E major, bright and quick: E - A - C#m - B (a deadline met)
    "spark": [[164.81, 207.65, 246.94], [110.0, 138.59, 164.81], [138.59, 164.81, 207.65], [123.47, 155.56, 185.0]],
    # batch-04 — C major, steady and wide: C - Am - F - G (a long road walked end to end)
    "steady": [[130.81, 164.81, 196.0], [110.0, 130.81, 164.81], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66]],
    # batch-04 — C# minor, glassy and exact: C#m - A - E - B (a page read under the loupe)
    "glass": [[138.59, 164.81, 207.65], [110.0, 138.59, 164.81], [164.81, 207.65, 246.94], [123.47, 155.56, 185.0]],
    # batch-04 — D major, light and chatty: D - Bm - G - A (a conversation that gets answered)
    "chat": [[146.83, 185.0, 220.0], [123.47, 146.83, 185.0], [196.0, 246.94, 293.66], [110.0, 138.59, 164.81]],
    # batch-03 — G major, open/bright: G - D - Em - C (a library opening up)
    "lift": [[196.0, 246.94, 293.66], [146.83, 185.0, 220.0], [164.81, 196.0, 246.94], [130.81, 164.81, 196.0]],
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
    elif kind == "tick":     # soft wooden tick when a questionnaire answer is picked
        ln = min(int(0.08 * sr), n - p0)
        pt = np.arange(ln) / sr
        sig = 0.25 * np.exp(-pt * 70) * np.sin(2 * np.pi * 1450 * pt) + 0.08 * np.exp(-pt * 200) * rng.standard_normal(ln)
    elif kind == "pen":      # felt-pen scratch while a mark is drawn on
        ln = min(int(0.45 * sr), n - p0)
        pt = np.arange(ln) / sr
        noise = rng.standard_normal(ln)
        noise = noise - np.convolve(noise, np.ones(6) / 6, mode="same")  # keep the hiss, drop the rumble
        sig = 0.16 * np.sin(np.pi * pt / 0.45) * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * pt)) * noise
    elif kind == "flick":    # paper card flicked into place
        ln = min(int(0.12 * sr), n - p0)
        pt = np.arange(ln) / sr
        sig = 0.14 * np.exp(-pt * 45) * np.convolve(rng.standard_normal(ln), np.ones(4) / 4, mode="same")
    elif kind == "tap":      # button press: low thump + click
        ln = min(int(0.3 * sr), n - p0)
        pt = np.arange(ln) / sr
        sig = 0.6 * np.exp(-pt * 25) * np.sin(2 * np.pi * (70 + 60 * np.exp(-pt * 40)) * pt)
        sig += 0.2 * np.exp(-pt * 300) * np.sin(2 * np.pi * 3000 * pt)
    elif kind == "swell":    # airy downward sweep under a dolly pull-back
        ln = min(int(2.2 * sr), n - p0)
        pt = np.arange(ln) / sr
        env = np.sin(np.pi * np.minimum(pt / 2.2, 1)) ** 1.5
        f = 900 - 650 * (pt / 2.2)
        tone = np.sin(2 * np.pi * np.cumsum(f) / sr)
        air = np.convolve(rng.standard_normal(ln), np.ones(30) / 30, mode="same")
        sig = env * (0.05 * tone + 0.6 * air)
    elif kind == "send":     # batch-04: message sent — short upward chirp + air
        ln = min(int(0.22 * sr), n - p0)
        pt = np.arange(ln) / sr
        f = 700 + 1600 * (pt / 0.22)
        sig = 0.13 * np.sin(np.pi * pt / 0.22) * np.sin(2 * np.pi * np.cumsum(f) / sr)
        sig += 0.05 * np.sin(np.pi * pt / 0.22) * np.convolve(rng.standard_normal(ln), np.ones(8) / 8, mode="same")
    elif kind == "pop":      # batch-04: chat bubble arrives — round two-note blip
        ln = min(int(0.18 * sr), n - p0)
        pt = np.arange(ln) / sr
        f = np.where(pt < 0.06, 880, 1320)
        sig = 0.16 * np.exp(-pt * 22) * np.sin(2 * np.pi * np.cumsum(f) / sr)
    elif kind == "scan":     # batch-04: scanner beam — soft hum that glides up
        ln = min(int(2.4 * sr), n - p0)
        pt = np.arange(ln) / sr
        env = np.sin(np.pi * np.minimum(pt / 2.4, 1)) ** 2
        f = 180 + 120 * (pt / 2.4)
        sig = 0.06 * env * (np.sin(2 * np.pi * np.cumsum(f) / sr) + 0.5 * np.sin(2 * np.pi * np.cumsum(3 * f) / sr))
    elif kind == "fix":      # batch-04: a wrong word turns right — bright glassy chime
        ln = min(int(0.5 * sr), n - p0)
        pt = np.arange(ln) / sr
        sig = 0.12 * np.exp(-pt * 9) * (np.sin(2 * np.pi * 1568 * pt) + 0.6 * np.sin(2 * np.pi * 2093 * pt))
    elif kind == "snap":     # batch-04: block snaps onto the guide — tight click + thump
        ln = min(int(0.16 * sr), n - p0)
        pt = np.arange(ln) / sr
        sig = 0.3 * np.exp(-pt * 60) * np.sin(2 * np.pi * (140 + 200 * np.exp(-pt * 80)) * pt)
        sig += 0.12 * np.exp(-pt * 400) * rng.standard_normal(ln)
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
    # Meta's published Reels requirements (checked 11 Nov 2026): H.264 High, progressive,
    # 4:2:0, fixed 30 fps, closed GOP of 2 s (Facebook's Reels API asks for 2-5 s), AAC-LC at
    # 48 kHz stereo and at least 128 kbps, VBR inside Instagram's recommended 8-12 Mbps and
    # under Facebook's 25 Mbps cap, bt709 tagged, moov up front.
    gop = int(round(FPS * spec.get("gop_seconds", 2)))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}",
           "-r", str(FPS), "-i", "-", "-i", wav,
           # Both sides of this merge implemented the same Meta spec; this keeps the other
           # session's `-use_editlist 0` (some ingests mishandle an edit list) and takes the
           # spec-overridable knobs. Bitrate mode by default, because CRF on this kind of
           # flat vector content lands around 3 Mbps -- well under Instagram's recommended
           # 8-12 -- and Meta re-encodes whatever it is handed. A spec that sets `crf`
           # explicitly still gets quality mode, capped by maxrate.
           "-c:v", "libx264", "-preset", spec.get("preset", "medium"),
           "-profile:v", "high", "-level", "4.0",
           *(["-crf", str(spec["crf"])] if spec.get("crf") is not None
             else ["-b:v", spec.get("vbitrate", "10M")]),
           "-maxrate", spec.get("maxrate", "12M"), "-bufsize", spec.get("bufsize", "20M"),
           "-g", str(gop), "-keyint_min", str(gop), "-sc_threshold", "0", "-flags", "+cgop",
           "-r", str(FPS), "-fps_mode", "cfr", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:a", "aac", "-profile:a", "aac_low", "-ar", "48000", "-ac", "2",
           "-b:a", spec.get("abitrate", "192k"),
           "-shortest", "-movflags", "+faststart", "-use_editlist", "0", out_path]
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
