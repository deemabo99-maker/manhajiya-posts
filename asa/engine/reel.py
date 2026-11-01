"""
Reel renderer for أكاديمية العلماء العرب (1080 x 1920, 30 fps, H.264 + original music).

    python3 engine/reel.py posts/batch-01/reel-1.json posts/batch-01/reel-1.mp4

A reel is a list of scenes; each scene has a background and animated elements.
Elements are pre-rendered sprites (2x supersampled) animated with slide / pop /
slam / fade / pulse. Text stays inside the Reels safe zone (y 250-1460).
Music: an original Hijaz-mode plucked melody over a frame-drum groove.

Ad-01 (Nov 2026) added: bookwall / chapter / hardcover / veil sprites, a counting-up
`counter`, a `shine` foil glint, a scene camera (pull-back / push) with HUD elements drawn
above it, impact booms on slams and counters, and spec-level fadein / cover_t.
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
    """Set `light` on an ivory scene, where the translucent card and ivory label vanish."""
    w, h = e.get("w", 840), 120
    if e.get("light"):
        img, m = rrect(w, h, 26, fill="#FFFFFF", outline=C["gold"], ow=2, shadow=True)
        label, box = rgb(C["ink"]), rgb(C["gold"])
    else:
        img, m = rrect(w, h, 26, fill=(255, 255, 255, 30), outline=C["gold"], ow=2, shadow=False)
        label, box = rgb(C["ivory"]), rgb(C["gold_lt"])
    d = ImageDraw.Draw(img)
    bx, by = m + (w - 80) * SS, m + h / 2 * SS
    d.rounded_rectangle([bx - 30 * SS, by - 30 * SS, bx + 30 * SS, by + 30 * SS], radius=10 * SS,
                        outline=box, width=4 * SS)
    d.text((bx - 70 * SS, by), e["text"], font=font("cairo", e.get("size", 44), 700),
           fill=label, anchor="rm", **_kw(e["text"]))
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


# ------------------------------------------------------------------ week-2 sprites
def sprite_seal(e):
    """Gold certification seal -- the motion twin of the seal on this week's designs."""
    r = e.get("r", 130)
    img, m = canvas(2 * r, 2 * r, 36)
    cx, cy = m + r * SS, m + r * SS
    disc = Image.new("L", img.size, 0)
    ImageDraw.Draw(disc).ellipse([m, m, m + 2 * r * SS, m + 2 * r * SS], fill=255)
    drop_shadow(img, disc, alpha=0.55, blur=20, dy=12)
    fill_mask(img, disc, None, GOLD, 40)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - (r - 17) * SS, cy - (r - 17) * SS, cx + (r - 17) * SS, cy + (r - 17) * SS],
              outline=rgb(C["deep"]), width=3 * SS)
    for k in range(16):
        a = math.radians(k * 22.5)
        px, py = cx + (r - 8) * SS * math.cos(a), cy + (r - 8) * SS * math.sin(a)
        d.polygon([(px, py - 5 * SS), (px + 5 * SS, py), (px, py + 5 * SS), (px - 5 * SS, py)],
                  fill=rgb(C["gold_dk"]))
    d.text((cx, cy - r * 0.20 * SS), e["big"], font=font("cairo", r * 0.36, 900), fill=rgb(C["deep"]),
           anchor="mm", **_kw(e["big"]))
    d.text((cx, cy + r * 0.30 * SS), e["small"], font=font("cairo", r * 0.19, 800), fill=rgb(C["deep"]),
           anchor="mm", **_kw(e["small"]))
    return _finish(img)


def sprite_scale5(e):
    """A five-point rating row; one option is already ticked in gold."""
    w, h = e.get("w", 860), 152
    img, m = rrect(w, h, 26, fill="#FFFFFF")
    d = ImageDraw.Draw(img)
    d.text((m + (w - 40) * SS, m + 46 * SS), e["text"], font=font("cairo", 38, 700),
           fill=rgb(C["ink"]), anchor="rm", **_kw(e["text"]))
    for k in range(5):
        px, py = m + (w - 70 - k * 86) * SS, m + 108 * SS
        if k == e.get("mark", 0):
            disc = Image.new("L", img.size, 0)
            ImageDraw.Draw(disc).ellipse([px - 26 * SS, py - 26 * SS, px + 26 * SS, py + 26 * SS], fill=255)
            fill_mask(img, disc, None, GOLD_SOFT, 45)
            d.text((px, py + 2 * SS), "\u2713", font=font("latin", 26), fill=rgb(C["deep"]), anchor="mm")
        else:
            d.ellipse([px - 26 * SS, py - 26 * SS, px + 26 * SS, py + 26 * SS], outline=rgb("#E0D7C2"),
                      width=4 * SS)
    return _finish(img)


def sprite_bar(e):
    """Labelled meter. Pair it with the `wipe` animation and the gold track fills RTL.
    Set `light` on an ivory scene: the translucent-white card and ivory label vanish there."""
    w, h = e.get("w", 820), 120
    if e.get("light"):
        img, m = rrect(w, h, 26, fill="#FFFFFF", outline=C["gold"], ow=2, shadow=True)
        label, track_bg = rgb(C["ink"]), rgb("#E4DAC2")
    else:
        img, m = rrect(w, h, 26, fill=(255, 255, 255, 30), outline=C["gold"], ow=2, shadow=False)
        label, track_bg = rgb(C["ivory"]), rgb("#06170F")
    d = ImageDraw.Draw(img)
    d.text((m + (w - 36) * SS, m + 40 * SS), e["text"], font=font("cairo", 36, 700),
           fill=label, anchor="rm", **_kw(e["text"]))
    tx0, tx1, ty = m + 36 * SS, m + (w - 36) * SS, m + 80 * SS
    d.rounded_rectangle([tx0, ty, tx1, ty + 22 * SS], radius=11 * SS, fill=track_bg)
    track = Image.new("L", img.size, 0)
    ImageDraw.Draw(track).rounded_rectangle([tx0, ty, tx1, ty + 22 * SS], radius=11 * SS, fill=255)
    fill_mask(img, track, None, GOLD, 0)
    return _finish(img)


def sprite_quote(e):
    """A committee question on a white card with a gold spine."""
    f = font("cairo", e.get("size", 40), 700)
    t = e["text"]
    l, tt, r, b = f.getbbox(t, **_kw(t))
    w, h = (r - l) / SS + 150, 126
    img, m = rrect(w, h, 24, fill="#FFFFFF")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([m + (w - 15) * SS, m + 10 * SS, m + (w - 4) * SS, m + (h - 10) * SS],
                        radius=5 * SS, fill=rgb(C["gold"]))
    d.text((m + 48 * SS, m + h / 2 * SS), "?", font=font("latin", 46), fill=rgb(C["sand"]), anchor="mm")
    d.text((m + (w - 42) * SS, m + h / 2 * SS), t, font=f, fill=rgb(C["ink"]), anchor="rm", **_kw(t))
    return _finish(img)


def sprite_slide_card(e):
    """A miniature defence slide: emerald title bar, text lines and a small gold chart."""
    w, h = e.get("w", 620), 376
    img, m = rrect(w, h, 20, gradient=[C["ivory"], "#F1EADB"], angle=90)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([m + 40 * SS, m + 38 * SS, m + (w - 40) * SS, m + 86 * SS], radius=10 * SS,
                        fill=rgb(C["forest"]))
    for i in range(3):
        yy = m + (126 + i * 40) * SS
        ww = (w - 96) * (0.62 if i % 2 == 0 else 0.42)
        d.rounded_rectangle([m + (w - 40) * SS - ww * SS, yy, m + (w - 40) * SS, yy + 16 * SS],
                            radius=8 * SS, fill=rgb("#DDD3C0"))
    for i, bh in enumerate((70, 112, 152)):
        bx = m + (56 + i * 62) * SS
        disc = Image.new("L", img.size, 0)
        ImageDraw.Draw(disc).rounded_rectangle(
            [bx, m + (h - 54) * SS - bh * SS, bx + 44 * SS, m + (h - 54) * SS], radius=8 * SS, fill=255)
        fill_mask(img, disc, None, GOLD_SOFT, 90)
    return _finish(img)


# ------------------------------------------------------------------ ad-01 sprites (Nov 2026)
def sprite_bookwall(e):
    """A full library wall of thesis spines on emerald shelves; one hero spine in the middle
    carries a gold-foil title, so a camera can start tight on it and pull back to the wall."""
    W, H = e.get("w", 1080), e.get("h", 1500)
    hx, hy = e.get("hero_x", 540), e.get("hero_y", 860)
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(e.get("seed", 4))
    shelf_h, board = 250, 26
    cols = [C["emerald"], C["forest"], C["deep"], C["red"], "#7A2C2C", C["sand"], "#2F6B4A", C["gold_dk"]]
    top = 0
    while top < H:
        base = top + shelf_h
        x = -20
        placed = False
        while x < W + 20:
            bw = int(rng.integers(44, 84))
            bh = int(rng.integers(170, 228))
            hero = (top <= hy < base) and not placed and x + bw > hx - 60
            if hero:   # the hero spine sits exactly centred on hero_x
                x, bw, bh = hx - 60, 120, 232
                placed = True
            col = C["emerald"] if hero else cols[int(rng.integers(0, len(cols)))]
            x0, x1, y0 = x, x + bw, base - bh
            d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, base * SS], radius=6 * SS, fill=rgb(col))
            # spine shading + gold bands
            d.rectangle([x0 * SS, y0 * SS, (x0 + 6) * SS, base * SS], fill=(0, 0, 0, 40))
            band = rgb(C["gold"])
            for by in (y0 + 18, base - 30):
                d.rectangle([(x0 + 6) * SS, by * SS, (x1 - 6) * SS, (by + 5) * SS], fill=band)
            if hero:
                f = font("cairo", 25, 900)
                txt = e.get("hero_text", "رسالة ماجستير")
                tl = Image.new("RGBA", (300 * SS, 70 * SS), (0, 0, 0, 0))
                m = Image.new("L", tl.size, 0)
                ImageDraw.Draw(m).text((tl.width / 2, tl.height / 2), txt, font=f, fill=255, anchor="mm", **_kw(txt))
                fill_mask(tl, m, None, FOIL, 0)
                tl = tl.rotate(90, expand=True)
                img.alpha_composite(tl, (int((x0 + bw / 2) * SS - tl.width / 2), int((y0 + bh / 2) * SS - tl.height / 2)))
            else:
                d.rounded_rectangle([(x0 + bw * 0.3) * SS, (y0 + 50) * SS, (x1 - bw * 0.3) * SS, (base - 50) * SS],
                                    radius=4 * SS, fill=rgb(C["gold_lt"])[:3] + (70,))
            x += bw + int(rng.integers(2, 6))
        # shelf board
        d.rectangle([0, base * SS, W * SS, (base + board) * SS], fill=rgb("#3B2A16"))
        d.rectangle([0, base * SS, W * SS, (base + 5) * SS], fill=rgb(C["gold"]))
        top = base + board
    return _finish(img)


def sprite_chapter(e):
    """A chapter page card: gold spine, chapter tag on the right, title."""
    w, h = e.get("w", 760), 112
    img, m = rrect(w, h, 18, gradient=[C["ivory"], "#F1E8D6"], angle=90)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([m + (w - 14) * SS, m, m + w * SS, m + h * SS], radius=6 * SS, fill=rgb(C["gold"]))
    tag = e.get("tag", "")
    ft = font("cairo", 28, 800)
    tb = ft.getbbox(tag, **_kw(tag))
    tw = (tb[2] - tb[0]) / SS + 40
    d.rounded_rectangle([m + (w - 40 - tw) * SS, m + (h / 2 - 26) * SS, m + (w - 40) * SS, m + (h / 2 + 26) * SS],
                        radius=26 * SS, fill=rgb(C["forest"]))
    d.text((m + (w - 40 - tw / 2) * SS, m + h / 2 * SS), tag, font=ft, fill=rgb(C["gold_lt"]), anchor="mm", **_kw(tag))
    d.text((m + (w - 64 - tw) * SS, m + h / 2 * SS), e["text"], font=font("cairo", 38, 800), fill=rgb(C["ink"]),
           anchor="rm", **_kw(e["text"]))
    return _finish(img)


def sprite_hardcover(e):
    """Bound thesis: emerald hardcover, gold double frame, star, gold-foil title."""
    w, h = e.get("w", 640), e.get("h", 700)
    img, m = rrect(w, h, 22, gradient=[C["emerald"], C["forest"], C["deep"]], angle=90)
    d = ImageDraw.Draw(img)
    d.rectangle([m, m, m + 26 * SS, m + h * SS], fill=(0, 0, 0, 60))
    for inset, wd in ((34, 4), (48, 2)):
        fr = Image.new("L", img.size, 0)
        ImageDraw.Draw(fr).rounded_rectangle([m + inset * SS, m + inset * SS, m + (w - inset) * SS, m + (h - inset) * SS],
                                             radius=14 * SS, outline=255, width=wd * SS)
        fill_mask(img, fr, None, GOLD, 30)
    cx = m + w / 2 * SS
    r = 58
    pts = []
    for k in range(16):
        rr = r if k % 2 == 0 else r * 0.76
        a = math.radians(k * 22.5)
        pts.append((cx + rr * SS * math.cos(a), m + (h * 0.3) * SS + rr * SS * math.sin(a)))
    st = Image.new("L", img.size, 0)
    ImageDraw.Draw(st).polygon(pts, fill=255)
    fill_mask(img, st, None, GOLD_SOFT, 45)
    for txt, yy, sz in ((e.get("title", "رسالة ماجستير"), 0.55, 66), (e.get("sub", ""), 0.7, 34)):
        if not txt:
            continue
        mk = Image.new("L", img.size, 0)
        ImageDraw.Draw(mk).text((cx, m + h * yy * SS), txt, font=font("cairo", sz, 900), fill=255, anchor="mm", **_kw(txt))
        fill_mask(img, mk, None, FOIL, 90)
    return _finish(img)


def sprite_veil(e):
    """Translucent deep panel / top veil that keeps HUD text readable over busy footage."""
    w, h = e.get("w", 1080), e.get("h", 400)
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    a = e.get("alpha", 215)
    if e.get("fade") == "down":   # solid at the top, fading out downwards
        col = np.array(rgb(C["night"])[:3], dtype=np.uint8)
        arr = np.zeros((h * SS, w * SS, 4), dtype=np.uint8)
        arr[..., :3] = col
        arr[..., 3] = (a * np.clip(1 - np.linspace(0, 1, h * SS) ** 1.6, 0, 1))[:, None].astype(np.uint8)
        return _finish(Image.fromarray(arr, "RGBA"))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=e.get("radius", 36) * SS,
                                          fill=rgb(C["night"])[:3] + (a,), outline=rgb(C["gold"])[:3] + (160,),
                                          width=2 * SS)
    return _finish(img)


def add_shine(spr, p):
    """Diagonal light sweep across a sprite (gold-foil glint), p = 0..1."""
    w, h = spr.size
    band = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(band)
    cx = -0.3 * w + p * 1.6 * w
    bw = w * 0.12
    d.polygon([(cx - bw, 0), (cx + bw, 0), (cx + bw - h * 0.5, h), (cx - bw - h * 0.5, h)], fill=150)
    band = band.filter(ImageFilter.GaussianBlur(max(2, bw * 0.35)))
    band = Image.fromarray(np.minimum(np.asarray(band), np.asarray(spr.getchannel("A"))), "L")
    out = spr.copy()
    white = Image.new("RGBA", (w, h), (255, 248, 225, 255))
    out.paste(white, (0, 0), band)
    out.putalpha(spr.getchannel("A"))
    return out


class Counter:
    """`counter`: a number that counts up (e.g. the approved +5000), gold foil, eased."""

    def __init__(self, e):
        self.e = e
        self.cache = {}

    def sprite(self, n):
        if n not in self.cache:
            e = self.e
            txt = f'{e.get("prefix", "+")}{n}{e.get("suffix", "")}'
            self.cache[n] = sprite_text({"text": txt, "font": "cairo", "size": e.get("size", 180), "wght": 900,
                                         "gradient": e.get("gradient", "gold"), "color": e.get("color", "#FFFFFF"),
                                         "dark_bg": e.get("dark_bg", True), "shadow": e.get("shadow", True)})
        return self.cache[n]

    def draw(self, f, t):
        e = self.e
        t0, dur = e.get("t", 0), e.get("dur", 1.2)
        if t < t0:
            return
        p = clamp((t - t0) / dur)
        q = 1 - (1 - p) ** 3
        n = int(round(e["value"] * q / e.get("step", 1))) * e.get("step", 1)
        sc = 1.0 + (0.08 * math.sin(clamp((t - t0 - dur) / 0.3) * math.pi) if t > t0 + dur else 0)
        place(f, self.sprite(n), e["x"], e["y"], clamp((t - t0) / 0.2), sc)


SPRITES = {
    "text": sprite_text, "pill": sprite_pill, "whatsapp": sprite_whatsapp, "emblem": sprite_emblem,
    "doc": sprite_doc, "stamp": sprite_stamp, "note": sprite_note, "check": sprite_check_row,
    "tick": sprite_tick, "step": sprite_step, "star": sprite_star, "line": sprite_line,
    "photo": sprite_photo, "arch": sprite_arch, "badge": sprite_badge,
    "seal": sprite_seal, "scale5": sprite_scale5, "bar": sprite_bar, "quote": sprite_quote,
    "slide": sprite_slide_card,
    "bookwall": sprite_bookwall, "chapter": sprite_chapter, "hardcover": sprite_hardcover, "veil": sprite_veil,
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
def place(frame, spr, cx, cy, alpha=1.0, scale=1.0, reveal=1.0):
    if alpha <= 0.01:
        return
    s = spr
    if abs(scale - 1.0) > 0.005:
        s = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    x, y = int(cx - s.width / 2), int(cy - s.height / 2)
    if reveal < 0.999:
        keep = max(1, int(s.width * reveal))
        x += s.width - keep                      # RTL: the right edge stays put
        s = s.crop((s.width - keep, 0, s.width, s.height))
    if alpha < 0.999:
        s = s.copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
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
    if anim == "drop":   # falls in from above and settles with a bounce
        q = ease_out_back(p, 1.5)
        return 0, -(1 - q) * 460, clamp(p * 3), 1.0
    if anim == "zoom":   # grows from small without pop's overshoot
        q = ease_out_cubic(p)
        return 0, 0, clamp(p * 2), 0.28 + 0.72 * q
    if anim == "wipe":   # revealed right-to-left, the way Arabic is read
        return 0, 0, 1.0, 1.0, ease_out_cubic(p)
    if anim == "float":  # eases up, then breathes in place
        q = ease_out_cubic(p)
        bob = 0.0 if p < 1 else 9 * math.sin((t - t0 - dur) * 1.7)
        return 0, (1 - q) * 46 + bob, q, 1.0
    return 0, 0, 1, 1


class Reel:
    def __init__(self, spec):
        self.scenes = []
        self.fadein = spec.get("fadein", 0.25)
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
                if e["type"] == "counter":
                    els.append((e, Counter(e), e["x"], e["y"]))
                    continue
                els.append((e, SPRITES[e["type"]](e), e["x"], e["y"]))
            self.scenes.append(dict(start=start, dur=sc["dur"], bg=bg, glow=glow, els=els,
                                    shake=sc.get("shake"), camera=sc.get("camera")))
            start += sc["dur"]
        self.total = start

    def scene_frame(self, sc, t):
        f = sc["bg"].copy()
        place(f, sc["glow"], 540 + 240 * math.sin(t * 0.6 + sc["start"]), 760 + 200 * math.cos(t * 0.45))
        def draw(e, spr, x, y):
            fr = holder[0]
            if isinstance(spr, Counter):
                spr.draw(fr, t)
                return
            a = animate(e, t)
            if a is None:
                return
            if len(a) == 4:
                a = a + (1.0,)
            dx, dy, al, scale, rev = a
            if "shine" in e and e["shine"] <= t < e["shine"] + e.get("shine_dur", 0.8):
                spr = add_shine(spr, (t - e["shine"]) / e.get("shine_dur", 0.8))
            place(fr, spr, x + dx, y + dy, al, scale, rev)

        holder = [f]
        for e, spr, x, y in sc["els"]:
            if not e.get("hud"):
                draw(e, spr, x, y)
        cam = sc.get("camera")
        if cam:
            # camera pull-back / push: zoom from `from` to `to` between t0 and t1 around (x, y)
            q = clamp((t - cam.get("t0", 0)) / max(cam.get("t1", 1) - cam.get("t0", 0), 1e-3))
            q = q * q * (3 - 2 * q)
            z = cam.get("from", 3.0) + (cam.get("to", 1.0) - cam.get("from", 3.0)) * q
            cx = cam.get("x", RW / 2) + (RW / 2 - cam.get("x", RW / 2)) * q
            cy = cam.get("y", RH / 2) + (RH / 2 - cam.get("y", RH / 2)) * q
            if z > 1.001:
                w, h = RW / z, RH / z
                l = clamp(cx - w / 2, 0, RW - w)
                tp = clamp(cy - h / 2, 0, RH - h)
                f = f.crop((int(l), int(tp), int(l + w), int(tp + h))).resize((RW, RH), Image.BICUBIC)
                holder[0] = f
        for e, spr, x, y in sc["els"]:
            if e.get("hud"):
                draw(e, spr, x, y)
        f = holder[0]
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
                fi = self.fadein
                if gt < fi:
                    f = Image.blend(Image.new("RGBA", f.size, (0, 0, 0, 255)), f, gt / fi)
                return f
        return self.scenes[-1]["bg"].copy()


# ------------------------------------------------------------------ music
MOODS = {
    # root: Hz of the tonic · semis: scale steps · lead: melodic voice · drum: pattern name
    # phrase: scale-degree line · swing: 0-0.25 · air: bed texture
    "hijaz": dict(root=146.83, semis=[0, 1, 4, 5, 7, 8, 10, 12, 13, 16], lead="oud", drum="maqsum",
                  phrase=[0, 1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4, 3, 2, 0], swing=0.0, air="drone",
                  bright=1.0),
    # thesis writing: warm minor, patient, resolves upward — "you will finish this"
    "resolve": dict(root=130.81, semis=[0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19], lead="oud",
                    drum="maqsum", phrase=[0, 2, 4, 2, 3, 5, 4, 2, 0, 2, 4, 7, 5, 4, 2, 0],
                    swing=0.06, air="pad", bright=0.85),
    # statistics: bright, precise, ticking — numbers clicking into place
    "insight": dict(root=174.61, semis=[0, 1, 3, 5, 7, 8, 10, 12, 13, 15, 17, 19], lead="bell",
                    drum="tick", phrase=[0, 3, 2, 5, 4, 3, 7, 5, 4, 3, 2, 3, 5, 7, 5, 3],
                    swing=0.0, air="shimmer", bright=1.25),
    # questionnaires: fast, upbeat, forward motion — responses arriving
    "pulse": dict(root=164.81, semis=[0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19], lead="pluck",
                  drum="ayyub", phrase=[0, 4, 2, 4, 5, 4, 2, 0, 2, 5, 4, 7, 5, 4, 2, 4],
                  swing=0.10, air="shaker", bright=1.15),
    # market data: low, serious, driving — a trading floor at work
    "market": dict(root=110.00, semis=[0, 2, 3, 5, 7, 8, 11, 12, 14, 15, 17], lead="pizz",
                   drum="drive", phrase=[0, 0, 3, 2, 0, 5, 3, 2, 0, 0, 7, 5, 3, 2, 0, 0],
                   swing=0.0, air="sub", bright=0.9),
    # study tools: slow, careful, hand-made — craft and validation
    "craft": dict(root=196.00, semis=[0, 1, 3, 5, 6, 8, 10, 12, 13, 15, 17], lead="felt",
                  drum="wahda", phrase=[0, 2, 1, 3, 2, 4, 3, 2, 1, 3, 5, 4, 3, 2, 1, 0],
                  swing=0.12, air="pad", bright=0.8),
}


def _lead_tone(kind, fr, pt, rng):
    """One plucked/struck note of the mood's melodic voice."""
    if kind == "bell":
        body = (np.sin(2 * np.pi * fr * pt) + 0.6 * np.sin(2 * np.pi * 2.76 * fr * pt)
                + 0.3 * np.sin(2 * np.pi * 5.4 * fr * pt))
        return np.exp(-pt * 4.5) * body
    if kind == "pluck":
        body = np.sign(np.sin(2 * np.pi * fr * pt)) * 0.35 + np.sin(2 * np.pi * fr * pt)
        return np.exp(-pt * 11) * body
    if kind == "pizz":
        body = np.sin(2 * np.pi * fr * pt) + 0.4 * np.sin(2 * np.pi * 3 * fr * pt)
        return np.exp(-pt * 16) * body + 0.25 * np.exp(-pt * 60) * rng.standard_normal(len(pt))
    if kind == "felt":
        body = np.sin(2 * np.pi * fr * pt) + 0.25 * np.sin(2 * np.pi * 2 * fr * pt)
        return (1 - np.exp(-pt * 40)) * np.exp(-pt * 3.2) * body
    # "oud": the original plucked stack
    body = (np.sin(2 * np.pi * fr * pt) + 0.5 * np.sin(2 * np.pi * 2 * fr * pt)
            + 0.25 * np.sin(2 * np.pi * 3 * fr * pt))
    return np.exp(-pt * 7) * body


DRUMS = {
    "maqsum": [("dum", 0.0), ("tak", 1.0), ("dum", 2.0), ("tak", 3.0), ("tak", 3.5)],
    "ayyub":  [("dum", 0.0), ("tak", 0.75), ("dum", 1.5), ("tak", 2.0), ("dum", 2.5), ("tak", 3.25)],
    "drive":  [("dum", 0.0), ("dum", 1.0), ("tak", 1.5), ("dum", 2.0), ("dum", 3.0), ("tak", 3.5)],
    "tick":   [("tak", 0.0), ("tak", 0.5), ("dum", 1.0), ("tak", 1.5), ("tak", 2.0),
               ("tak", 2.5), ("dum", 3.0), ("tak", 3.5)],
    "wahda":  [("dum", 0.0), ("tak", 2.0)],
}


def music(path, seconds, bpm=92, sr=44100, seed=1, hits=(), mood="hijaz"):
    """Original track. `mood` picks the scale, melodic voice, drum pattern and bed,
    so two reels in the same batch do not sound like the same cue retimed."""
    m = MOODS.get(mood, MOODS["hijaz"])
    n = int(seconds * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    beat = 60 / bpm
    base = m["root"]
    scale = [base * 2 ** (s / 12) for s in m["semis"]]
    rng = np.random.default_rng(seed)

    # bed
    air = m["air"]
    if air == "drone":
        out += 0.05 * (np.sin(2 * np.pi * base / 2 * t) + 0.6 * np.sin(2 * np.pi * base * 0.75 * t))
    elif air == "pad":
        sweep = 0.5 + 0.5 * np.sin(2 * np.pi * t / max(4.0, seconds / 2))
        out += 0.045 * (1 + 0.3 * sweep) * (np.sin(2 * np.pi * base / 2 * t)
                                            + 0.5 * np.sin(2 * np.pi * base * 1.5 * t))
    elif air == "sub":
        out += 0.07 * np.sin(2 * np.pi * base / 2 * t) * (0.8 + 0.2 * np.sin(2 * np.pi * t / 3))
    elif air == "shimmer":
        out += 0.03 * np.sin(2 * np.pi * base * 4 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 2.5))
        out += 0.035 * np.sin(2 * np.pi * base / 2 * t)
    elif air == "shaker":
        step = beat / 2
        pos = 0.0
        while pos < seconds:
            s0 = int(pos * sr)
            ln = min(int(0.08 * sr), n - s0)
            if ln > 0:
                pt = np.arange(ln) / sr
                amp = 0.035 if int(pos / step) % 2 else 0.055
                out[s0:s0 + ln] += amp * np.exp(-pt * 70) * rng.standard_normal(ln)
            pos += step

    # melody
    phrase = m["phrase"]
    swing, k, pos = m["swing"], 0, 0.0
    while pos < seconds:
        step = beat / 2
        idx = phrase[k % len(phrase)] + (2 if (k // 16) % 2 else 0)
        fr = scale[min(idx, len(scale) - 1)] * 2
        off = swing * beat if k % 2 else 0.0
        s0 = int((pos + off) * sr)
        ln = min(int(0.55 * sr), n - s0)
        if ln > 0 and not (k % 8 == 7):
            pt = np.arange(ln) / sr
            out[s0:s0 + ln] += 0.09 * m["bright"] * _lead_tone(m["lead"], fr, pt, rng)
        pos += step
        k += 1

    # drums
    pattern = DRUMS.get(m["drum"], DRUMS["maqsum"])
    bar, b = beat * 4, 0
    while b * bar < seconds:
        for kind, offb in pattern:
            s0 = int((b * bar + offb * beat) * sr)
            if s0 >= n:
                continue
            ln = min(int(0.3 * sr), n - s0)
            pt = np.arange(ln) / sr
            if kind == "dum":
                lo = 62 if m["drum"] == "drive" else 70
                out[s0:s0 + ln] += 0.38 * np.exp(-pt * 14) * np.sin(2 * np.pi * (lo + 60 * np.exp(-pt * 25)) * pt)
            else:
                out[s0:s0 + ln] += 0.10 * np.exp(-pt * 45) * rng.standard_normal(ln)
                out[s0:s0 + ln] += 0.08 * np.exp(-pt * 30) * np.sin(2 * np.pi * 420 * m["bright"] * pt)
        b += 1

    fade = np.minimum(1, t / 1.0) * np.minimum(1, (seconds - t) / 1.5)
    out *= fade
    out /= max(1e-6, np.abs(out).max()) / 0.6
    # impact accents on slams / counters landing
    for th in hits:
        s0 = int(th * sr)
        if 0 <= s0 < n:
            ln = min(int(0.8 * sr), n - s0)
            pt = np.arange(ln) / sr
            out[s0:s0 + ln] += 0.55 * np.exp(-pt * 7) * np.sin(2 * np.pi * (48 + 110 * np.exp(-pt * 20)) * pt)
            out[s0:s0 + ln] += 0.08 * np.exp(-pt * 9) * rng.standard_normal(ln)
    out = 0.89 * np.tanh(out * 1.1) / np.tanh(1.1)
    st = np.stack([out, out], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((st * 32767).astype("<i2").tobytes())


def mix_voice(wav_path, vo, seconds, duck=0.22):
    """Lay the narration over the music track in place, ducking the music under it.
    `duck` is what the music drops to while the voice speaks (0.22 = -13 dB)."""
    import voice as voice_mod

    with wave.open(wav_path, "rb") as w:
        sr, nch = w.getframerate(), w.getnchannels()
        bed = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    bed = bed.reshape(-1, nch)
    speech, gate = voice_mod.track(vo, seconds, sr)
    n = min(len(bed), len(speech))
    bed, speech, gate = bed[:n], speech[:n], gate[:n]
    ducked = bed * (1 - (1 - duck) * gate)[:, None]
    out = ducked + speech[:, None] * 0.95
    out = 0.92 * np.tanh(out * 1.15) / np.tanh(1.15)
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(nch)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())


def render(spec_path, out_path):
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    reel = Reel(spec)
    wav = out_path.replace(".mp4", ".wav")
    hits, st = [], 0.0
    for sc in spec["scenes"]:
        for e in sc["elements"]:
            if e.get("anim") == "slam":
                hits.append(st + e.get("t", 0) + e.get("dur", 0.55) * 0.6)
            elif e["type"] == "counter":
                hits.append(st + e.get("t", 0) + e.get("dur", 1.2))
        st += sc["dur"]
    music(wav, reel.total, bpm=spec.get("bpm", 92), seed=spec.get("music_seed", 1), hits=hits,
          mood=spec.get("mood", "hijaz"))
    if spec.get("vo"):
        mix_voice(wav, spec["vo"], reel.total, duck=spec.get("duck", 0.22))
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
    reel.scene_frame(last, spec.get("cover_t", last["dur"] - 0.01)).convert("RGB").save(out_path.replace(".mp4", "-cover.png"))
    print("done", out_path)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
