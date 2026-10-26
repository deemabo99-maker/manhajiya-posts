"""
Drawing kit for المنهجية social posts.

Everything is drawn on a 2x canvas and downsampled at the end, so shapes and
Arabic text come out smooth. Coordinates passed to every helper are in final
pixels (1080 x 1350); the kit scales them internally.

Requires Pillow built with libraqm (Arabic shaping + RTL).
"""
from __future__ import annotations

import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "brand", "fonts")
LOGO = os.path.join(ROOT, "brand", "logo.png")

W, H = 1080, 1350          # Instagram/Facebook portrait feed (4:5)
S = 2                      # supersampling factor

# ---------------------------------------------------------------- palette
C = {
    "purple": "#9627C4",     # main brand purple (from past ads)
    "violet": "#7B1FA2",
    "plum": "#4B1A5E",       # dark purple
    "night": "#24092F",      # darkest background
    "magenta": "#C2309E",
    "pink": "#E8457E",
    "coral": "#E9686B",      # logo coral
    "orange": "#F28C28",
    "yellow": "#FFC21A",
    "gold": "#FFD45C",
    "white": "#FFFFFF",
    "paper": "#F5F2F7",      # light background
    "mist": "#EDE7F1",
    "ink": "#1E1A22",        # body text on light
    "muted": "#6B6272",
    "green": "#1FAF5A",      # WhatsApp button
}

RING = ["#9627C4", "#C2309E", "#E8457E", "#F28C28", "#FFC21A"]   # brand ring gradient
WARM = ["#FFC21A", "#F28C28", "#E8457E"]

CONTACT = {
    "whatsapp": "00962778707204",
    "instagram": "@methodology_center",
}


def rgb(c):
    if isinstance(c, tuple):
        return c if len(c) == 4 else c + (255,)
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def s(v):
    return int(round(v * S))


# ---------------------------------------------------------------- fonts
FONT_FILES = {
    "kufi": "NotoKufiArabic[wght].ttf",
    "almarai": "Almarai-Regular.ttf",
    "almarai-bold": "Almarai-Bold.ttf",
    "almarai-xb": "Almarai-ExtraBold.ttf",
    "tajawal-md": "Tajawal-Medium.ttf",
    "tajawal-b": "Tajawal-Bold.ttf",
    "tajawal-black": "Tajawal-Black.ttf",
    "lalezar": "Lalezar-Regular.ttf",
    "latin": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


@lru_cache(maxsize=256)
def font(name: str, size: float, wght: int | None = None):
    path = FONT_FILES[name]
    if not os.path.isabs(path):
        path = os.path.join(FONTS, path)
    f = ImageFont.truetype(path, s(size), layout_engine=ImageFont.Layout.RAQM)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


def _is_ar(text):
    return any("؀" <= ch <= "ۿ" for ch in text)


def _kw(text):
    if _is_ar(text):
        return {"direction": "rtl", "language": "ar"}
    return {}


def measure(text, f):
    """Width/height in final pixels."""
    l, t, r, b = f.getbbox(text, **_kw(text))
    return (r - l) / S, (b - t) / S


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, bg="#FFFFFF"):
        self.im = Image.new("RGBA", (s(W), s(H)), rgb(bg))

    # -- fills -----------------------------------------------------------
    def paste_masked(self, fill_img, mask):
        layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        layer.paste(fill_img, (0, 0), mask)
        self.im = Image.alpha_composite(self.im, layer)

    def gradient_bg(self, stops, angle=90):
        self.im = Image.alpha_composite(self.im, linear_gradient(self.im.size, stops, angle))

    def glow(self, cx, cy, r, color, alpha=120):
        layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        c = rgb(color)[:3] + (alpha,)
        d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=c)
        layer = layer.filter(ImageFilter.GaussianBlur(s(r * 0.45)))
        self.im = Image.alpha_composite(self.im, layer)

    def shape(self, kind, box, fill=None, gradient=None, angle=90, radius=0,
              outline=None, width=0, shadow=None, opacity=255):
        """kind: rect | round | ellipse | poly(box=list of points)."""
        mask = Image.new("L", self.im.size, 0)
        d = ImageDraw.Draw(mask)
        if kind == "poly":
            pts = [(s(x), s(y)) for x, y in box]
            d.polygon(pts, fill=opacity)
        else:
            b = [s(v) for v in box]
            if kind == "rect":
                d.rectangle(b, fill=opacity)
            elif kind == "round":
                d.rounded_rectangle(b, radius=s(radius), fill=opacity)
            elif kind == "ellipse":
                d.ellipse(b, fill=opacity)
        if shadow:
            self.shadow_from(mask, **shadow)
        if gradient:
            src = self.grad_for(mask, gradient, angle)
        else:
            src = Image.new("RGBA", self.im.size, rgb(fill or "#000000"))
        self.paste_masked(src, mask)
        if outline and width:
            ol = Image.new("L", self.im.size, 0)
            od = ImageDraw.Draw(ol)
            b = [s(v) for v in box] if kind != "poly" else None
            if kind == "round":
                od.rounded_rectangle(b, radius=s(radius), outline=255, width=s(width))
            elif kind == "ellipse":
                od.ellipse(b, outline=255, width=s(width))
            elif kind == "rect":
                od.rectangle(b, outline=255, width=s(width))
            if isinstance(outline, list):
                src = self.grad_for(ol, outline, angle)
            else:
                src = Image.new("RGBA", self.im.size, rgb(outline))
            self.paste_masked(src, ol)

    def shadow_from(self, mask, offset=(0, 14), blur=28, color="#2A0F3A", alpha=70):
        sh = mask.point(lambda v: int(v * alpha / 255))
        sh = sh.filter(ImageFilter.GaussianBlur(s(blur)))
        layer = Image.new("RGBA", self.im.size, rgb(color)[:3] + (0,))
        col = Image.new("RGBA", self.im.size, rgb(color))
        shifted = Image.new("L", self.im.size, 0)
        shifted.paste(sh, (s(offset[0]), s(offset[1])))
        layer.paste(col, (0, 0), shifted)
        self.im = Image.alpha_composite(self.im, layer)

    def ring(self, cx, cy, r, width, stops=RING, angle=60, shadow=False):
        mask = Image.new("L", self.im.size, 0)
        d = ImageDraw.Draw(mask)
        d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=255)
        d.ellipse([s(cx - r + width), s(cy - r + width), s(cx + r - width), s(cy + r - width)], fill=0)
        if shadow:
            full = Image.new("L", self.im.size, 0)
            ImageDraw.Draw(full).ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=255)
            self.shadow_from(full, offset=(0, 18), blur=34, alpha=60)
        self.paste_masked(self.grad_for(mask, stops, angle), mask)

    def grad_for(self, mask, stops, angle):
        """Gradient sized to the mask's bounding box, so each shape shows the full ramp."""
        box = mask.getbbox() or (0, 0, 1, 1)
        l, t, r, b = box
        g = linear_gradient((max(r - l, 1), max(b - t, 1)), stops, angle)
        src = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        src.paste(g, (l, t))
        return src

    def line(self, pts, color, width):
        d = ImageDraw.Draw(self.im)
        d.line([(s(x), s(y)) for x, y in pts], fill=rgb(color), width=s(width), joint="curve")

    # -- motifs (from the brand's past ads) ------------------------------
    def dots(self, x, y, cols, rows, gap=22, r=3.2, color="#FFFFFF", alpha=200):
        layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        c = rgb(color)[:3] + (alpha,)
        for i in range(cols):
            for j in range(rows):
                cx, cy = x + i * gap, y + j * gap
                d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=c)
        self.im = Image.alpha_composite(self.im, layer)

    def plus(self, x, y, size=22, thick=7, color="#1E1A22"):
        d = ImageDraw.Draw(self.im)
        c = rgb(color)
        d.rectangle([s(x - size / 2), s(y - thick / 2), s(x + size / 2), s(y + thick / 2)], fill=c)
        d.rectangle([s(x - thick / 2), s(y - size / 2), s(x + thick / 2), s(y + size / 2)], fill=c)

    def tri(self, x, y, size=40, color="#1E1A22", rot=0):
        pts = []
        for k in range(3):
            a = math.radians(rot + k * 120)
            pts.append((x + size * math.cos(a), y + size * math.sin(a)))
        self.shape("poly", pts, fill=color)

    # -- text -------------------------------------------------------------
    def text(self, xy, txt, f, fill="#000000", anchor="ra", gradient=None, angle=0,
             shadow=None, stroke=0, stroke_fill=None):
        x, y = xy
        kw = _kw(txt)
        if gradient or shadow:
            mask = Image.new("L", self.im.size, 0)
            ImageDraw.Draw(mask).text((s(x), s(y)), txt, font=f, fill=255, anchor=anchor, **kw)
            if shadow:
                self.shadow_from(mask, **shadow)
            if gradient:
                l, t, r, b = mask.getbbox() or (0, 0, 1, 1)
                g = linear_gradient((r - l, b - t), gradient, angle)
                src = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
                src.paste(g, (l, t))
                self.paste_masked(src, mask)
                return
        d = ImageDraw.Draw(self.im)
        d.text((s(x), s(y)), txt, font=f, fill=rgb(fill), anchor=anchor,
               stroke_width=s(stroke), stroke_fill=rgb(stroke_fill) if stroke_fill else None, **kw)

    def highlight(self, xy, txt, f, pad=(16, 2), color="#FFC21A", anchor="ra", skew=0.35):
        """Marker-style highlight behind a word (drawn before the text)."""
        w, h = measure(txt, f)
        x, y = xy
        x0 = x - w if anchor[0] == "r" else (x - w / 2 if anchor[0] == "m" else x)
        asc = f.getmetrics()[0] / S
        top = y + asc * 0.42
        bot = y + asc * 1.05
        self.shape("round", [x0 - pad[0], top, x0 + w + pad[0], bot], fill=color, radius=10)

    # -- logo ---------------------------------------------------------------
    def logo(self, cx, cy, width, badge=True, pad=18, radius=26, shadow=True):
        lg = Image.open(LOGO).convert("RGBA")
        ratio = lg.height / lg.width
        h = width * ratio
        if badge:
            box = [cx - width / 2 - pad, cy - h / 2 - pad, cx + width / 2 + pad, cy + h / 2 + pad]
            self.shape("round", box, fill="#FFFFFF", radius=radius,
                       shadow=dict(offset=(0, 10), blur=22, alpha=55) if shadow else None)
        lg = lg.resize((s(width), s(h)), Image.LANCZOS)
        layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        layer.paste(lg, (s(cx - width / 2), s(cy - h / 2)), lg)
        self.im = Image.alpha_composite(self.im, layer)
        return h

    # -- shared footer -----------------------------------------------------
    def footer(self, y=1236, dark=False, cta="للاستشارة المجانية تواصل معنا"):
        """WhatsApp pill + social handle. y = vertical centre of the row."""
        ink = "#FFFFFF" if dark else C["ink"]
        sub = "#E9DDF0" if dark else C["muted"]
        # cta line
        self.text((W / 2, y - 66), cta, font("almarai-bold", 26), fill=sub, anchor="mm")
        # WhatsApp pill (right side)
        num = CONTACT["whatsapp"]
        fnum = font("latin", 27)
        flab = font("almarai-xb", 24)
        nw, _ = measure(num, fnum)
        lw, _ = measure("واتساب", flab)
        pw = nw + lw + 96
        x1 = W - 70
        x0 = x1 - pw
        self.shape("round", [x0, y - 34, x1, y + 34], fill=C["green"], radius=34,
                   shadow=dict(offset=(0, 8), blur=16, alpha=60, color="#0B3D20"))
        # whatsapp-style glyph: white bubble with a phone
        gx = x1 - 36
        self.shape("poly", [(gx - 12, y + 10), (gx - 19, y + 20), (gx - 3, y + 16)], fill="#FFFFFF")
        self.shape("ellipse", [gx - 17, y - 17, gx + 17, y + 17], fill="#FFFFFF")
        self.text((gx, y + 1), "☎", font("latin", 20), fill=C["green"], anchor="mm")
        self.text((gx - 30, y), "واتساب", flab, fill="#FFFFFF", anchor="rm")
        self.text((x0 + 22, y + 1), num, fnum, fill="#FFFFFF", anchor="lm")
        # social (left side)
        fx = 70
        icon_r = 21
        for i, kind in enumerate(["ig", "fb", "x"]):
            cx = fx + icon_r + i * (icon_r * 2 + 12)
            self.social_icon(kind, cx, y, icon_r, dark)
        hx = fx + 3 * (icon_r * 2 + 12) + 4
        self.text((hx, y + 1), CONTACT["instagram"], font("latin", 20), fill=ink, anchor="lm")

    def social_icon(self, kind, cx, cy, r, dark=False):
        bg = "#FFFFFF" if dark else C["purple"]
        fg = C["purple"] if dark else "#FFFFFF"
        self.shape("ellipse", [cx - r, cy - r, cx + r, cy + r], fill=bg)
        if kind == "ig":
            self.shape("round", [cx - 10, cy - 10, cx + 10, cy + 10], outline=fg, width=2.6, radius=6)
            self.shape("ellipse", [cx - 4.6, cy - 4.6, cx + 4.6, cy + 4.6], outline=fg, width=2.4)
            self.shape("ellipse", [cx + 5, cy - 8, cx + 8, cy - 5], fill=fg)
        elif kind == "fb":
            self.text((cx + 1, cy + 2), "f", font("latin", 25), fill=fg, anchor="mm")
        else:
            self.text((cx, cy + 1), "X", font("latin", 20), fill=fg, anchor="mm")

    # -- output -------------------------------------------------------------
    def save(self, path):
        out = self.im.resize((W, H), Image.LANCZOS).convert("RGB")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        out.save(path, "PNG", optimize=True)
        return path


# ---------------------------------------------------------------- gradients
def linear_gradient(size, stops, angle=90):
    """angle in degrees: 0 = left->right, 90 = top->bottom."""
    w, h = size
    cols = np.array([rgb(c) for c in stops], dtype=float)
    a = math.radians(angle)
    xs = np.linspace(0, 1, w)[None, :]
    ys = np.linspace(0, 1, h)[:, None]
    t = xs * math.cos(a) + ys * math.sin(a)
    t = (t - t.min()) / max(t.max() - t.min(), 1e-6)
    n = len(stops) - 1
    pos = t * n
    idx = np.clip(pos.astype(int), 0, n - 1)
    frac = (pos - idx)[..., None]
    out = cols[idx] * (1 - frac) + cols[idx + 1] * frac
    return Image.fromarray(out.astype("uint8"), "RGBA")
