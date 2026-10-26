"""
Reel renderer for أكاديمية العلماء العرب (1080 x 1920, 30 fps, H.264 + original music).

    python3 engine/reel.py posts/batch-01/reel-1.json posts/batch-01/reel-1.mp4

A reel is a list of scenes; each scene has a background and animated elements.
Elements are pre-rendered sprites (2x supersampled) animated with slide / pop /
slam / fade / pulse. Text stays inside the Reels safe zone (y 250-1460).
Music: an original Hijaz-mode plucked melody over a frame-drum groove.
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
from kit import C, GOLD, GOLD_SOFT, font, linear_gradient, rgb  # noqa: E402

RW, RH, FPS = 1080, 1920, 30
SS = 2
XFADE = 0.35
FOIL = ["#9C7A22", "#E9CF7A", "#F7E7B4", "#C8A02E", "#8C6A1F"]
FOIL_DK = ["#6E500F", "#B48A22", "#D9B54F", "#A27C1C", "#6E500F"]


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_out_back(x, k=1.7):
    x -= 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def _kw(t):
    return {"direction": "rtl", "language": "ar"} if any("؀" <= ch <= "ۿ" for ch in t) else {}


def _finish(img2x):
    return img2x.resize((max(1, img2x.width // SS), max(1, img2x.height // SS)), Image.LANCZOS)


# ------------------------------------------------------------------ sprite helpers
def canvas(w, h, margin=30):
    m = margin * SS
    return Image.new("RGBA", (int(w * SS + 2 * m), int(h * SS + 2 * m)), (0, 0, 0, 0)), m


def fill_mask(img, mask, fill=None, gradient=None, angle=90):
    src = linear_gradient(img.size, gradient, angle) if gradient else Image.new("RGBA", img.size, rgb(fill))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(src, (0, 0), mask)
    img.alpha_composite(layer)


def drop_shadow(img, mask, alpha=0.4, blur=14, dy=10, color=(6, 23, 15)):
    sh = mask.filter(ImageFilter.GaussianBlur(blur * SS)).point(lambda v: int(v * alpha))
    layer = Image.new("RGBA", img.size, color + (0,))
    layer.putalpha(sh)
    img.alpha_composite(layer, (0, dy * SS))


def rrect(w, h, r, fill=None, gradient=None, angle=90, outline=None, ow=3, shadow=True):
    img, m = canvas(w, h)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([m, m, m + w * SS, m + h * SS], radius=r * SS, fill=255)
    if shadow:
        drop_shadow(img, mask)
    if fill or gradient:
        fill_mask(img, mask, fill, gradient, angle)
    if outline:
        ol = Image.new("L", img.size, 0)
        ImageDraw.Draw(ol).rounded_rectangle([m, m, m + w * SS, m + h * SS], radius=r * SS, outline=255,
                                             width=int(ow * SS))
        fill_mask(img, ol, None if isinstance(outline, list) else outline,
                  outline if isinstance(outline, list) else None, 30)
    return img, m


def draw_text(img, xy, text, f, fill=None, gradient=None, anchor="mm", angle=90):
    if gradient:
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).text(xy, text, font=f, fill=255, anchor=anchor, **_kw(text))
        box = mask.getbbox() or (0, 0, 1, 1)
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        g.paste(linear_gradient((box[2] - box[0], box[3] - box[1]), gradient, angle), box[:2])
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        layer.paste(g, (0, 0), mask)
        img.alpha_composite(layer)
    else:
        ImageDraw.Draw(img).text(xy, text, font=f, fill=rgb(fill), anchor=anchor, **_kw(text))


# ------------------------------------------------------------------ sprites
def sprite_text(e):
    f = font(e.get("font", "messiri"), e.get("size", 80), e.get("wght"))
    text = e["text"]
    l, t, r, b = f.getbbox(text, **_kw(text))
    pad = 40 * SS
    w, h = (r - l) + 2 * pad, (b - t) + 2 * pad
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - l, pad - t), text, font=f, fill=255, **_kw(text))
    if e.get("shadow", True):
        drop_shadow(img, mask, alpha=0.5 if e.get("dark_bg", True) else 0.18, blur=9, dy=6)
    g = e.get("gradient")
    stops = FOIL if g == "gold" else (FOIL_DK if g == "gold_dk" else None)
    fill_mask(img, mask, e.get("color", "#FFFFFF"), stops, 90)
    return _finish(img)


def sprite_pill(e):
    f = font(e.get("font", "messiri"), e.get("size", 36), e.get("wght", 700))
    text = e["text"]
    l, t, r, b = f.getbbox(text, **_kw(text))
    tw = (r - l) / SS
    h = e.get("h", e.get("size", 36) * 1.9)
    w = tw + 2 * e.get("padx", 44)
    style = e.get("style", "gold")
    if style == "gold":
        img, m = rrect(w, h, h / 2, gradient=GOLD_SOFT, angle=0)
        fg = C["deep"]
    elif style == "red":
        img, m = rrect(w, h, h / 2, gradient=[C["red"], "#8E2B2B"], angle=0)
        fg = "#FFFFFF"
    elif style == "outline":
        img, m = rrect(w, h, h / 2, outline=C["gold"], ow=2.5, shadow=False)
        fg = C["gold_lt"]
    else:
        img, m = rrect(w, h, h / 2, fill=C["emerald"], outline=GOLD, ow=2.5)
        fg = C["ivory"]
    draw_text(img, (m + w * SS / 2, m + h * SS / 2), text, f, fill=e.get("fg", fg))
    return _finish(img)


def sprite_whatsapp(e):
    sc = e.get("scale", 1.0)
    num = kit.CONTACT["display"]
    fnum, flab = font("latin", 40 * sc), font("messiri", 38 * sc, 700)
    nw = (fnum.getbbox(num)[2] - fnum.getbbox(num)[0]) / SS
    lb = flab.getbbox("واتساب", **_kw("واتساب"))
    lw = (lb[2] - lb[0]) / SS
    h = 108 * sc
    w = nw + lw + 176 * sc
    img, m = rrect(w + 8, h + 8, (h + 8) / 2, gradient=GOLD, angle=0)
    inner = Image.new("L", img.size, 0)
    ImageDraw.Draw(inner).rounded_rectangle([m + 4 * SS, m + 4 * SS, m + (w + 4) * SS, m + (h + 4) * SS],
                                            radius=h / 2 * SS, fill=255)
    fill_mask(img, inner, C["wa"])
    d = ImageDraw.Draw(img)
    gx, gy, r = m + (w - 56 * sc) * SS, m + (h / 2 + 4) * SS, 31 * sc * SS
    d.polygon([(gx - 0.7 * r, gy + 0.55 * r), (gx - 1.15 * r, gy + 1.15 * r), (gx - 0.15 * r, gy + 0.95 * r)], fill="#FFFFFF")
    d.ellipse([gx - r, gy - r, gx + r, gy + r], fill="#FFFFFF")
    d.text((gx, gy + 2 * SS), "☎", font=font("latin", 34 * sc), fill=rgb(C["wa"]), anchor="mm")
    d.text((gx - 54 * sc * SS, gy), "واتساب", font=flab, fill="#FFFFFF", anchor="rm", **_kw("واتساب"))
    d.text((m + 38 * sc * SS, gy + 2 * SS), num, font=fnum, fill="#FFFFFF", anchor="lm")
    return _finish(img)


def sprite_emblem(e):
    w = e.get("width", 300)
    lg = Image.open(kit.LOGO).convert("RGBA")
    h = int(w * lg.height / lg.width)
    img, m = canvas(w, h, 40)
    lg2 = lg.resize((w * SS, h * SS), Image.LANCZOS)
    mask = Image.new("L", img.size, 0)
    mask.paste(lg2.getchannel("A"), (m, m))
    drop_shadow(img, mask, alpha=0.55, blur=18, dy=12)
    img.alpha_composite(lg2, (m, m))
    return _finish(img)


def sprite_doc(e):
    w, h = e.get("w", 520), e.get("h", 680)
    img, m = rrect(w, h, 18, gradient=[C["ivory"], "#F3ECDD"], angle=90)
    d = ImageDraw.Draw(img)
    # title bar
    d.rounded_rectangle([m + 60 * SS, m + 60 * SS, m + (w - 60) * SS, m + 92 * SS], radius=10 * SS,
                        fill=rgb(C["forest"]))
    for i in range(11):
        yy = m + (140 + i * 46) * SS
        ww = (w - 120) * (0.95 if i % 4 else 0.6)
        d.rounded_rectangle([m + (w - 60) * SS - ww * SS, yy, m + (w - 60) * SS, yy + 12 * SS], radius=6 * SS,
                            fill=rgb("#DDD3C0"))
        if e.get("marks") and i in (1, 3, 4, 7, 9):
            d.line([(m + (w - 60) * SS - ww * 0.9 * SS, yy + 20 * SS), (m + (w - 60) * SS - ww * 0.15 * SS, yy + 26 * SS)],
                   fill=rgb(C["red"]), width=5 * SS)
    if e.get("marks"):
        for (x, y) in ((70, 210), (80, 400), (65, 560)):
            d.ellipse([m + x * SS, m + y * SS, m + (x + 34) * SS, m + (y + 34) * SS], outline=rgb(C["red"]), width=4 * SS)
            d.text((m + (x + 17) * SS, m + (y + 17) * SS), "?", font=font("latin", 24), fill=rgb(C["red"]), anchor="mm")
    return _finish(img)


def sprite_stamp(e):
    text = e["text"]
    col = C["red"] if e.get("color", "red") == "red" else C["jade"]
    f = font("messiri", e.get("size", 56), 700)
    l, t, r, b = f.getbbox(text, **_kw(text))
    tw = (r - l) / SS
    w, h = tw + 90, e.get("size", 56) * 2.1
    img, m = canvas(w, h, 20)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([m, m, m + w * SS, m + h * SS], radius=18 * SS, outline=rgb(col), width=8 * SS)
    d.rounded_rectangle([m + 14 * SS, m + 14 * SS, m + (w - 14) * SS, m + (h - 14) * SS], radius=10 * SS,
                        outline=rgb(col), width=3 * SS)
    d.text((m + w * SS / 2, m + h * SS / 2), text, font=f, fill=rgb(col), anchor="mm", **_kw(text))
    # ink texture: knock out speckles
    rng = np.random.default_rng(3)
    a = np.asarray(img).copy()
    holes = rng.random(a.shape[:2]) < 0.06
    a[..., 3] = np.where(holes, (a[..., 3] * 0.35).astype("uint8"), a[..., 3])
    img = Image.fromarray(a, "RGBA").rotate(e.get("rot", -12), resample=Image.BICUBIC, expand=True)
    return _finish(img)


def sprite_note(e):
    w, h = e.get("w", 820), 132
    img, m = rrect(w, h, 26, fill="#FFFFFF")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([m + (w - 16) * SS, m, m + w * SS, m + h * SS], radius=8 * SS, fill=rgb(C["red"]))
    cx, cy = m + 72 * SS, m + h / 2 * SS
    d.ellipse([cx - 34 * SS, cy - 34 * SS, cx + 34 * SS, cy + 34 * SS], fill=rgb(C["red_lt"]))
    d.text((cx, cy + 2 * SS), "!", font=font("latin", 40), fill=rgb(C["red"]), anchor="mm")
    d.text((m + (w - 50) * SS, cy), e["text"], font=font("messiri", 42, 700), fill=rgb(C["ink"]), anchor="rm",
           **_kw(e["text"]))
    return _finish(img)


def sprite_check_row(e):
    w, h = e.get("w", 840), 120
    img, m = rrect(w, h, 26, fill=(255, 255, 255, 30), outline=C["gold"], ow=2, shadow=False)
    d = ImageDraw.Draw(img)
    bx, by = m + (w - 80) * SS, m + h / 2 * SS
    d.rounded_rectangle([bx - 30 * SS, by - 30 * SS, bx + 30 * SS, by + 30 * SS], radius=10 * SS,
                        outline=rgb(C["gold_lt"]), width=4 * SS)
    d.text((bx - 70 * SS, by), e["text"], font=font("messiri", 44, 700), fill=rgb(C["ivory"]), anchor="rm",
           **_kw(e["text"]))
    return _finish(img)


def sprite_tick(e):
    r = 34
    img, m = canvas(2 * r, 2 * r, 10)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse([m, m, m + 2 * r * SS, m + 2 * r * SS], fill=255)
    fill_mask(img, mask, None, GOLD_SOFT, 45)
    ImageDraw.Draw(img).text((m + r * SS, m + r * SS + 2 * SS), "✓", font=font("latin", 44),
                             fill=rgb(C["deep"]), anchor="mm")
    return _finish(img)


def sprite_step(e):
    w, h = e.get("w", 920), 138
    img, m = rrect(w, h, 30, fill="#FFFFFF")
    d = ImageDraw.Draw(img)
    cx, cy = m + (w - 70) * SS, m + h / 2 * SS
    disc = Image.new("L", img.size, 0)
    ImageDraw.Draw(disc).ellipse([cx - 46 * SS, cy - 46 * SS, cx + 46 * SS, cy + 46 * SS], fill=255)
    fill_mask(img, disc, None, [C["emerald"], C["deep"]], 90)
    ring = Image.new("L", img.size, 0)
    ImageDraw.Draw(ring).ellipse([cx - 46 * SS, cy - 46 * SS, cx + 46 * SS, cy + 46 * SS], outline=255, width=4 * SS)
    fill_mask(img, ring, None, GOLD, 45)
    d.text((cx, cy + 2 * SS), str(e["n"]), font=font("rakkas", 54), fill=rgb(C["gold_lt"]), anchor="mm")
    d.text((cx - 80 * SS, cy - 22 * SS), e["title"], font=font("messiri", 46, 700), fill=rgb(C["forest"]),
           anchor="rm", **_kw(e["title"]))
    d.text((cx - 80 * SS, cy + 34 * SS), e["desc"], font=font("almarai", 31), fill=rgb(C["muted"]), anchor="rm",
           **_kw(e["desc"]))
    return _finish(img)


def sprite_star(e):
    r = e.get("r", 60)
    img, m = canvas(2 * r, 2 * r, 10)
    pts = []
    for k in range(16):
        rr = r if k % 2 == 0 else r * 0.76
        a = math.radians(k * 22.5)
        pts.append((m + (r + rr * math.cos(a)) * SS, m + (r + rr * math.sin(a)) * SS))
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    fill_mask(img, mask, None, GOLD_SOFT, 45)
    ImageDraw.Draw(img).ellipse([m + r * 0.62 * SS, m + r * 0.62 * SS, m + r * 1.38 * SS, m + r * 1.38 * SS],
                                fill=rgb(C["deep"]))
    return _finish(img)


def sprite_line(e):
    w = e.get("w", 600)
    img, m = canvas(w, 24, 6)
    d = ImageDraw.Draw(img)
    cy = m + 12 * SS
    d.rectangle([m, cy - 2 * SS, m + (w / 2 - 26) * SS, cy + 2 * SS], fill=rgb(C["gold"]))
    d.rectangle([m + (w / 2 + 26) * SS, cy - 2 * SS, m + w * SS, cy + 2 * SS], fill=rgb(C["gold"]))
    cx = m + w / 2 * SS
    d.polygon([(cx, cy - 12 * SS), (cx + 12 * SS, cy), (cx, cy + 12 * SS), (cx - 12 * SS, cy)], fill=rgb(C["gold"]))
    return _finish(img)


def sprite_photo(e):
    """Cut-out person from brand/people, trimmed and scaled to `height`, with a soft shadow."""
    path = os.path.join(kit.PEOPLE, e["name"] + ".png")
    im = kit.trim_alpha(Image.open(path).convert("RGBA"))
    h = e.get("height", 900)
    w = int(im.width * h / im.height)
    im = im.resize((w * SS, h * SS), Image.LANCZOS)
    img, m = canvas(w, h, 40)
    mask = Image.new("L", img.size, 0)
    mask.paste(im.getchannel("A"), (m, m))
    drop_shadow(img, mask, alpha=0.45, blur=22, dy=14)
    img.alpha_composite(im, (m, m))
    return _finish(img)


def sprite_arch(e):
    """Mihrab arch: gold rim, emerald fill with a faint star lattice, glowing top."""
    w, h = e.get("w", 760), e.get("h", 1100)
    img, m = canvas(w, h, 30)
    cx = m + w * SS / 2
    spring = m + w * 0.55 * SS

    def path(inset):
        x0, x1, y0 = m + inset * SS, m + (w - inset) * SS, m + inset * SS
        pts = [(x0, m + h * SS + 40 * SS), (x0, spring)]
        for i in range(1, 49):
            q = i / 48
            pts.append((x0 + (cx - x0) * q, spring - (spring - y0) * math.sin(q * math.pi / 2) ** 0.85))
        for i in range(1, 49):
            q = i / 48
            pts.append((cx + (x1 - cx) * q, y0 + (spring - y0) * (1 - math.cos(q * math.pi / 2)) ** 0.85))
        pts += [(x1, spring), (x1, m + h * SS + 40 * SS)]
        return pts

    outer = Image.new("L", img.size, 0)
    ImageDraw.Draw(outer).polygon(path(0), fill=255)
    drop_shadow(img, outer, alpha=0.5, blur=24, dy=10)
    fill_mask(img, outer, None, GOLD, 30)
    inner = Image.new("L", img.size, 0)
    ImageDraw.Draw(inner).polygon(path(14), fill=255)
    fill_mask(img, inner, None, [C["emerald"], C["forest"], C["deep"]], 90)
    lat = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lat)
    cell, rr = 130 * SS, 130 * SS * 0.42
    y, row = 0, 0
    while y < img.height + cell:
        x = cell / 2 if row % 2 else 0
        while x < img.width + cell:
            pts = [(x + (rr if k % 2 == 0 else rr * 0.76) * math.cos(math.radians(k * 22.5)),
                    y + (rr if k % 2 == 0 else rr * 0.76) * math.sin(math.radians(k * 22.5))) for k in range(16)]
            d.line(pts + [pts[0]], fill=rgb(C["gold"])[:3] + (60,), width=2 * SS)
            x += cell
        y += cell * 0.866
        row += 1
    lat.putalpha(Image.fromarray(np.minimum(np.asarray(lat.getchannel("A")), np.asarray(inner)), "L"))
    img.alpha_composite(lat)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - w * 0.38 * SS, m + 80 * SS, cx + w * 0.38 * SS, m + 80 * SS + w * 0.76 * SS],
                                 fill=rgb(C["gold_lt"])[:3] + (70,))
    glow = glow.filter(ImageFilter.GaussianBlur(60 * SS))
    glow.putalpha(Image.fromarray(np.minimum(np.asarray(glow.getchannel("A")), np.asarray(inner)), "L"))
    img.alpha_composite(glow)
    return _finish(img)


def sprite_badge(e):
    """Round gold badge with a big number and a small label."""
    r = e.get("r", 110)
    img, m = canvas(2 * r, 2 * r, 30)
    disc = Image.new("L", img.size, 0)
    ImageDraw.Draw(disc).ellipse([m, m, m + 2 * r * SS, m + 2 * r * SS], fill=255)
    drop_shadow(img, disc, alpha=0.5, blur=16, dy=10)
    fill_mask(img, disc, None, GOLD_SOFT, 45)
    d = ImageDraw.Draw(img)
    d.ellipse([m + 10 * SS, m + 10 * SS, m + (2 * r - 10) * SS, m + (2 * r - 10) * SS], outline=rgb(C["deep"]),
              width=3 * SS)
    cx, cy = m + r * SS, m + r * SS
    d.text((cx, cy - r * 0.16 * SS), e["big"], font=font("cairo", r * 0.56, 900), fill=rgb(C["deep"]), anchor="mm")
    d.text((cx, cy + r * 0.36 * SS), e["small"], font=font("cairo", r * 0.2, 800), fill=rgb(C["deep"]), anchor="mm",
           **_kw(e["small"]))
    return _finish(img)


SPRITES = {
    "text": sprite_text, "pill": sprite_pill, "whatsapp": sprite_whatsapp, "emblem": sprite_emblem,
    "doc": sprite_doc, "stamp": sprite_stamp, "note": sprite_note, "check": sprite_check_row,
    "tick": sprite_tick, "step": sprite_step, "star": sprite_star, "line": sprite_line,
    "photo": sprite_photo, "arch": sprite_arch, "badge": sprite_badge,
}


# ------------------------------------------------------------------ backgrounds
def background(kind):
    if kind == "ivory":
        bg = linear_gradient((RW, RH), [C["ivory"], C["cream"], C["sand"]], 90)
        col, alpha = C["gold"], 30
    elif kind == "emerald":
        bg = linear_gradient((RW, RH), [C["forest"], C["emerald"], C["deep"]], 120)
        col, alpha = C["gold"], 30
    else:
        bg = linear_gradient((RW, RH), [C["night"], C["deep"], C["emerald"]], 100)
        col, alpha = C["gold"], 30
    d = ImageDraw.Draw(bg)
    cell = 180
    rr = cell * 0.42
    c = rgb(col)[:3] + (alpha,)
    y, row = 0, 0
    while y < RH + cell:
        x = cell / 2 if row % 2 else 0
        while x < RW + cell:
            pts = []
            for k in range(16):
                q = rr if k % 2 == 0 else rr * 0.76
                a = math.radians(k * 22.5)
                pts.append((x + q * math.cos(a), y + q * math.sin(a)))
            d.line(pts + [pts[0]], fill=c, width=2)
            x += cell
        y += cell * 0.866
        row += 1
    return bg


def glow_sprite(color, r, alpha):
    size = int(r * 3)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r], fill=rgb(color)[:3] + (alpha,))
    return img.filter(ImageFilter.GaussianBlur(r * 0.45))


# ------------------------------------------------------------------ animation
def place(frame, spr, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01:
        return
    s = spr
    if abs(scale - 1.0) > 0.005:
        s = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        s = s.copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - s.width / 2), int(cy - s.height / 2)
    frame.alpha_composite(s, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


def animate(e, t):
    t0 = e.get("t", 0.0)
    dur = e.get("dur", 0.55)
    p = clamp((t - t0) / dur)
    if p <= 0:
        return None
    anim = e.get("anim", "up")
    if anim == "up":
        q = ease_out_cubic(p)
        return 0, (1 - q) * 70, q, 1.0
    if anim == "right":
        q = ease_out_cubic(p)
        return (1 - q) * 180, 0, q, 1.0
    if anim == "left":
        q = ease_out_cubic(p)
        return -(1 - q) * 180, 0, q, 1.0
    if anim == "pop":
        q = ease_out_back(p)
        return 0, 0, clamp(p * 2), 0.5 + 0.5 * q
    if anim == "slam":
        q = ease_out_cubic(clamp(p * 1.6))
        return 0, 0, clamp(p * 3), 2.4 - 1.4 * q
    if anim == "fade":
        return 0, 0, p, 1.0
    if anim == "pulse":
        q = ease_out_back(p)
        sc = 0.55 + 0.45 * q
        if p >= 1:
            sc = 1 + 0.045 * math.sin((t - t0 - dur) * 2 * math.pi * 1.1)
        return 0, 0, clamp(p * 2), sc
    if anim == "spin":   # slow rotation feel via gentle scale breathing
        return 0, 0, clamp(p * 2), 1 + 0.03 * math.sin((t - t0) * 2.2)
    return 0, 0, 1, 1


class Reel:
    def __init__(self, spec):
        self.scenes = []
        start = 0.0
        for sc in spec["scenes"]:
            bg = background(sc.get("bg", "deep"))
            light = sc.get("bg") == "ivory"
            glow = glow_sprite(sc.get("glow", C["jade"]), 380, 60 if light else 110)
            els = []
            for e in sc["elements"]:
                if e["type"] == "text":
                    e.setdefault("dark_bg", not light)
                if "bottom" in e:   # anchor the element's lower edge (people stand on the frame edge)
                    hh = e.get("height", e.get("h", 0))
                    e["y"] = e["bottom"] - hh / 2
                els.append((e, SPRITES[e["type"]](e), e["x"], e["y"]))
            self.scenes.append(dict(start=start, dur=sc["dur"], bg=bg, glow=glow, els=els,
                                    shake=sc.get("shake")))
            start += sc["dur"]
        self.total = start

    def scene_frame(self, sc, t):
        f = sc["bg"].copy()
        place(f, sc["glow"], 540 + 240 * math.sin(t * 0.6 + sc["start"]), 760 + 200 * math.cos(t * 0.45))
        for e, spr, x, y in sc["els"]:
            a = animate(e, t)
            if a is None:
                continue
            dx, dy, al, scale = a
            place(f, spr, x + dx, y + dy, al, scale)
        if sc["shake"] is not None:
            ts = sc["shake"]
            if ts <= t < ts + 0.3:
                k = 1 - (t - ts) / 0.3
                ox = int(14 * k * math.sin(t * 90))
                oy = int(10 * k * math.cos(t * 70))
                f = Image.fromarray(np.roll(np.roll(np.asarray(f), ox, axis=1), oy, axis=0), "RGBA")
        return f

    def frame(self, gt):
        for i, sc in enumerate(self.scenes):
            if sc["start"] <= gt < sc["start"] + sc["dur"] or i == len(self.scenes) - 1:
                f = self.scene_frame(sc, gt - sc["start"])
                end = sc["start"] + sc["dur"]
                if i + 1 < len(self.scenes) and gt > end - XFADE:
                    nxt = self.scene_frame(self.scenes[i + 1], 0.0)
                    f = Image.blend(f, nxt, clamp((gt - (end - XFADE)) / XFADE))
                if gt < 0.25:
                    f = Image.blend(Image.new("RGBA", f.size, (0, 0, 0, 255)), f, gt / 0.25)
                return f
        return self.scenes[-1]["bg"].copy()


# ------------------------------------------------------------------ music
def music(path, seconds, bpm=92, sr=44100, seed=1):
    """Original track: D Hijaz plucked melody, drone and a dum-tak frame drum."""
    n = int(seconds * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    beat = 60 / bpm
    # D Hijaz: D Eb F# G A Bb C D
    base = 146.83
    semis = [0, 1, 4, 5, 7, 8, 10, 12, 13, 16]
    scale = [base * 2 ** (s / 12) for s in semis]
    # drone (D + A), soft
    out += 0.05 * (np.sin(2 * np.pi * base / 2 * t) + 0.6 * np.sin(2 * np.pi * base * 0.75 * t))
    rng = np.random.default_rng(seed)
    phrase = [0, 1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4, 3, 2, 0]
    k = 0
    pos = 0.0
    while pos < seconds:
        step = beat / 2
        idx = phrase[k % len(phrase)] + (2 if (k // 16) % 2 else 0)
        fr = scale[min(idx, len(scale) - 1)] * 2
        s0 = int(pos * sr)
        ln = min(int(0.5 * sr), n - s0)
        if ln > 0 and not (k % 8 == 7):
            pt = np.arange(ln) / sr
            # Karplus-ish pluck: decaying harmonics
            tone = (np.sin(2 * np.pi * fr * pt) + 0.5 * np.sin(2 * np.pi * 2 * fr * pt)
                    + 0.25 * np.sin(2 * np.pi * 3 * fr * pt))
            out[s0:s0 + ln] += 0.09 * np.exp(-pt * 7) * tone
        pos += step
        k += 1
    # frame drum: dum (low) on 1 and 3-and, tak (high) on 2 and 4
    pattern = [("dum", 0.0), ("tak", 1.0), ("dum", 2.5), ("tak", 3.0), ("tak", 3.5)]
    bar = beat * 4
    b = 0
    while b * bar < seconds:
        for kind, off in pattern:
            s0 = int((b * bar + off * beat) * sr)
            if s0 >= n:
                continue
            ln = min(int(0.3 * sr), n - s0)
            pt = np.arange(ln) / sr
            if kind == "dum":
                out[s0:s0 + ln] += 0.38 * np.exp(-pt * 14) * np.sin(2 * np.pi * (70 + 60 * np.exp(-pt * 25)) * pt)
            else:
                out[s0:s0 + ln] += 0.10 * np.exp(-pt * 45) * rng.standard_normal(ln)
                out[s0:s0 + ln] += 0.08 * np.exp(-pt * 30) * np.sin(2 * np.pi * 420 * pt)
        b += 1
    fade = np.minimum(1, t / 1.0) * np.minimum(1, (seconds - t) / 1.5)
    out *= fade
    out /= max(1e-6, np.abs(out).max()) / 0.7
    st = np.stack([out, out], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((st * 32767).astype("<i2").tobytes())


def render(spec_path, out_path):
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    reel = Reel(spec)
    wav = out_path.replace(".mp4", ".wav")
    music(wav, reel.total, seed=spec.get("music_seed", 1))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(reel.total * FPS)
    for i in range(nframes):
        proc.stdin.write(reel.frame(i / FPS).convert("RGB").tobytes())
        if i % 120 == 0:
            print(f"frame {i}/{nframes}", flush=True)
    proc.stdin.close()
    proc.wait()
    os.remove(wav)
    last = reel.scenes[spec.get("cover_scene", -1)]
    reel.scene_frame(last, last["dur"] - 0.01).convert("RGB").save(out_path.replace(".mp4", "-cover.png"))
    print("done", out_path)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
