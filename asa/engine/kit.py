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
LOGO = os.path.join(ROOT, "brand", "emblem.png")

W, H = 1080, 1350          # Instagram/Facebook portrait feed (4:5)
S = 2                      # supersampling factor

# ---------------------------------------------------------------- palette
C = {
    "emerald": "#0F5236",    # main academy green
    "forest": "#164A2F",
    "deep": "#0B2E1E",       # darkest green background
    "night": "#071C13",
    "jade": "#2E8B57",
    "mint": "#DCEBDF",
    "gold": "#C8A02E",
    "gold_lt": "#EED9A0",
    "gold_dk": "#8C6A1F",
    "cream": "#F6F0E2",
    "ivory": "#FBF8F1",
    "sand": "#EADFC6",
    "ink": "#1F2A24",
    "muted": "#5E6B62",
    "red": "#B23A3A",        # ribbon red from the emblem
    "red_lt": "#F3D9D5",
    "white": "#FFFFFF",
    "wa": "#1FAF5A",
}

GOLD = ["#8C6A1F", "#C8A02E", "#F3DE9A", "#C8A02E", "#8C6A1F"]   # foil
GOLD_SOFT = ["#B98E25", "#E9CF7A", "#C8A02E"]
GREEN = ["#0B2E1E", "#0F5236", "#164A2F"]
RING = GOLD
WARM = GOLD_SOFT

BRAND_AR = "أكاديمية العلماء العرب"
BRAND_SUB = "للاستشارات والتدريب"

CONTACT = {
    "whatsapp": "00962778597330",
    "display": "+962 77859 7330",
    "email": "asaforconsultingandtraining@gmail.com",
    "instagram": "@asa_for_training",
}


def rgb(c):
    if isinstance(c, tuple):
        return c if len(c) == 4 else c + (255,)
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def s(v):
    return int(round(v * S))


# ---------------------------------------------------------------- fonts
# Owner asked for clear, easy-to-read type (26 Oct 2026): every Arabic style maps to
# Cairo (variable, very legible) at a suitable weight. Old style names are kept as aliases
# so templates and reel specs keep working.
CAIRO = "Cairo[slnt,wght].ttf"
FONT_FILES = {
    "cairo": (CAIRO, 700),
    "ruqaa": (CAIRO, 900),        # was calligraphic headline -> Cairo Black
    "messiri": (CAIRO, 700),
    "kufi": (CAIRO, 900),
    "naskh": (CAIRO, 700),
    "rakkas": (CAIRO, 900),       # big numbers
    "reem": (CAIRO, 800),
    "amiri": (CAIRO, 600),
    "amiri-b": (CAIRO, 800),
    "almarai": ("Almarai-Regular.ttf", None),
    "almarai-bold": ("Almarai-Bold.ttf", None),
    "almarai-xb": ("Almarai-ExtraBold.ttf", None),
    "latin": ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", None),
    "serif": ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", None),
}


@lru_cache(maxsize=512)
def font(name: str, size: float, wght: int | None = None):
    path, default_w = FONT_FILES[name]
    if not os.path.isabs(path):
        path = os.path.join(FONTS, path)
    f = ImageFont.truetype(path, s(size), layout_engine=ImageFont.Layout.RAQM)
    w = wght if wght is not None else default_w
    if w is not None:
        try:
            axes = f.get_variation_axes()
            vals = [a["default"] for a in axes]
            for i, a in enumerate(axes):
                if a["name"] in (b"Weight", "Weight"):
                    vals[i] = max(a["minimum"], min(a["maximum"], max(w, 600)))
            f.set_variation_by_axes(vals)
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
            self.paste_masked(self.grad_for(mask, gradient, angle), mask)
        elif fill is not None:
            self.paste_masked(Image.new("RGBA", self.im.size, rgb(fill)), mask)
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

    def shadow_from(self, mask, offset=(0, 14), blur=28, color="#0B2E1E", alpha=70):
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
    def logo(self, cx, cy, width, shadow=True):
        """Hexagon emblem (no badge: it already has its own gold frame)."""
        lg = Image.open(LOGO).convert("RGBA")
        h = width * lg.height / lg.width
        lg = lg.resize((s(width), s(h)), Image.LANCZOS)
        if shadow:
            m = Image.new("L", self.im.size, 0)
            m.paste(lg.getchannel("A"), (s(cx - width / 2), s(cy - h / 2)))
            self.shadow_from(m, offset=(0, 8), blur=14, color="#0B2E1E", alpha=90)
        layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        layer.paste(lg, (s(cx - width / 2), s(cy - h / 2)), lg)
        self.im = Image.alpha_composite(self.im, layer)
        return h

    def lockup(self, x_right, cy, size=96, dark=False, anchor="r"):
        """Emblem + two-line wordmark. anchor r: block ends at x_right (RTL)."""
        f1 = font("messiri", size * 0.36, 700)
        f2 = font("messiri", size * 0.24, 500)
        w1, _ = measure(BRAND_AR, f1)
        w2, _ = measure(BRAND_SUB, f2)
        tw = max(w1, w2)
        ew = size * 0.87
        total = ew + 18 + tw
        xr = x_right if anchor == "r" else x_right + total / 2
        self.logo(xr - ew / 2, cy, ew, shadow=True)
        col = C["ivory"] if dark else C["forest"]
        sub = C["gold_lt"] if dark else C["gold_dk"]
        self.text((xr - ew - 18, cy - size * 0.05), BRAND_AR, f1, fill=col, anchor="rs")
        self.text((xr - ew - 18, cy + size * 0.06), BRAND_SUB, f2, fill=sub, anchor="ra")
        return total

    # -- ornaments ------------------------------------------------------------
    def star8(self, cx, cy, r, fill=None, outline=None, width=0, gradient=None, rot=0, opacity=255):
        """Eight-pointed star (two overlapping squares)."""
        pts = []
        for k in range(16):
            rr = r if k % 2 == 0 else r * 0.76
            a = math.radians(rot + k * 22.5)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        if fill or gradient:
            self.shape("poly", pts, fill=fill, gradient=gradient, angle=45, opacity=opacity)
        if outline:
            d = ImageDraw.Draw(self.im)
            d.line([(s(x), s(y)) for x, y in pts + [pts[0]]], fill=rgb(outline)[:3] + (opacity,),
                   width=s(width), joint="curve")

    def girih(self, alpha=22, color="#C8A02E", cell=150, box=None, r=None):
        """Faint repeating 8-point-star lattice over a region (default full canvas)."""
        x0, y0, x1, y1 = box or (0, 0, W, H)
        layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        col = rgb(color)[:3] + (alpha,)
        rr = r or cell * 0.42
        y = y0
        row = 0
        while y < y1 + cell:
            x = x0 + (cell / 2 if row % 2 else 0)
            while x < x1 + cell:
                pts = []
                for k in range(16):
                    q = rr if k % 2 == 0 else rr * 0.76
                    a = math.radians(k * 22.5)
                    pts.append((s(x + q * math.cos(a)), s(y + q * math.sin(a))))
                d.line(pts + [pts[0]], fill=col, width=s(1.6))
                d.ellipse([s(x - 4), s(y - 4), s(x + 4), s(y + 4)], outline=col, width=s(1.2))
                x += cell
            y += cell * 0.866
            row += 1
        if box:
            m = Image.new("L", self.im.size, 0)
            ImageDraw.Draw(m).rectangle([s(x0), s(y0), s(x1), s(y1)], fill=255)
            layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", self.im.size, 0), m))
        self.im = Image.alpha_composite(self.im, layer)

    def gold_frame(self, box, radius=28, inset=14, corners=True):
        """Double gold frame with star corners."""
        x0, y0, x1, y1 = box
        self.shape("round", box, outline=GOLD, width=3.2, radius=radius, angle=30)
        self.shape("round", [x0 + inset, y0 + inset, x1 - inset, y1 - inset], outline=GOLD, width=1.4,
                   radius=max(radius - inset, 4), angle=30)
        if corners:
            for (cx, cy) in [(x0 + inset, y0 + inset), (x1 - inset, y0 + inset),
                             (x0 + inset, y1 - inset), (x1 - inset, y1 - inset)]:
                self.star8(cx, cy, 15, gradient=GOLD_SOFT)
                self.star8(cx, cy, 6, fill=C["deep"])

    def diamond(self, cx, cy, r, fill=None, gradient=None):
        self.shape("poly", [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill,
                   gradient=gradient, angle=45)

    def divider(self, cx, y, w, color=None):
        col = color or C["gold"]
        self.shape("rect", [cx - w / 2, y - 1.2, cx - 22, y + 1.2], fill=col)
        self.shape("rect", [cx + 22, y - 1.2, cx + w / 2, y + 1.2], fill=col)
        self.diamond(cx, y, 9, gradient=GOLD_SOFT)
        self.diamond(cx - 34, y, 4, fill=col)
        self.diamond(cx + 34, y, 4, fill=col)

    def paper_noise(self, amount=6):
        """Subtle paper grain."""
        rng = np.random.default_rng(7)
        n = rng.normal(0, amount, (self.im.height // 2, self.im.width // 2)).astype("int16")
        n = Image.fromarray(np.clip(n + 128, 0, 255).astype("uint8"), "L").resize(self.im.size)
        a = np.asarray(self.im).astype("int16")
        nn = (np.asarray(n).astype("int16") - 128)[..., None]
        a[..., :3] = np.clip(a[..., :3] + nn, 0, 255)
        self.im = Image.fromarray(a.astype("uint8"), "RGBA")

    # -- shared footer ---------------------------------------------------------
    def footer(self, y=1250, dark=False, cta="استشارتك الأولى مجانية.. تواصل معنا"):
        """Gold-rimmed WhatsApp pill + email. y = centre of the pill row."""
        ink = C["ivory"] if dark else C["forest"]
        self.text((W / 2, y - 70), cta, font("messiri", 30, 700), fill=C["gold_lt"] if dark else C["gold_dk"],
                  anchor="mm")
        num = CONTACT["display"]
        fnum = font("latin", 28)
        flab = font("messiri", 27, 700)
        nw, _ = measure(num, fnum)
        lw, _ = measure("واتساب", flab)
        pw = nw + lw + 104
        x1 = W - 66
        x0 = x1 - pw
        self.shape("round", [x0 - 3, y - 37, x1 + 3, y + 37], gradient=GOLD, angle=0, radius=37,
                   shadow=dict(offset=(0, 8), blur=16, alpha=70, color="#06170F"))
        self.shape("round", [x0, y - 34, x1, y + 34], fill=C["wa"], radius=34)
        gx = x1 - 38
        self.shape("poly", [(gx - 12, y + 10), (gx - 19, y + 20), (gx - 3, y + 16)], fill="#FFFFFF")
        self.shape("ellipse", [gx - 17, y - 17, gx + 17, y + 17], fill="#FFFFFF")
        self.text((gx, y + 1), "\u260E", font("latin", 20), fill=C["wa"], anchor="mm")
        self.text((gx - 30, y), "واتساب", flab, fill="#FFFFFF", anchor="rm")
        self.text((x0 + 22, y + 1), num, fnum, fill="#FFFFFF", anchor="lm")
        # instagram + email (left, two rows)
        fe = font("latin", 17)
        ex = 66
        icon_bg = C["gold"] if dark else C["forest"]
        icon_fg = C["deep"] if dark else C["gold_lt"]
        # instagram glyph
        iy = y - 19
        self.shape("round", [ex, iy - 15, ex + 30, iy + 15], fill=icon_bg, radius=9)
        self.shape("round", [ex + 7, iy - 8, ex + 23, iy + 8], outline=icon_fg, width=2.2, radius=5)
        self.shape("ellipse", [ex + 11, iy - 4, ex + 19, iy + 4], outline=icon_fg, width=2)
        self.text((ex + 42, iy + 1), CONTACT["instagram"], font("latin", 20), fill=ink, anchor="lm")
        # email glyph
        ey = y + 19
        self.shape("round", [ex, ey - 13, ex + 30, ey + 13], fill=icon_bg, radius=7)
        self.shape("poly", [(ex + 6, ey - 7), (ex + 15, ey + 2), (ex + 24, ey - 7)], fill=icon_fg)
        self.text((ex + 42, ey + 1), CONTACT["email"], fe, fill=ink, anchor="lm")

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


# ---------------------------------------------------------------- photos
PEOPLE = os.path.join(ROOT, "brand", "people")


def _photo_path(name):
    for ext in (".png", ".webp", ".jpg"):
        p = os.path.join(PEOPLE, name + ext)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def trim_alpha(im, pad=4):
    """Crop transparent margins of a cut-out."""
    if im.mode != "RGBA":
        return im
    box = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, im.width), min(b + pad, im.height)))


def _photo_into(self, name, cx=None, bottom=None, height=None, box=None, mask=None, shadow=True,
                fade_left=None, fade_top=None, opacity=255):
    """Place a person photo.
    Cut-outs: give cx/bottom/height; the figure is trimmed and scaled to `height`.
    Framed photos: give box=(x0,y0,x1,y1) to cover-crop into, optional `mask` polygon/("round", r)/("ellipse",).
    """
    im = Image.open(_photo_path(name)).convert("RGBA")
    if box is None:
        im = trim_alpha(im)
        h = height
        w = im.width * h / im.height
        x0, y0 = cx - w / 2, bottom - h
        lay = im.resize((s(w), s(h)), Image.LANCZOS)
        if shadow:
            m = Image.new("L", self.im.size, 0)
            m.paste(lay.getchannel("A"), (s(x0), s(y0)))
            self.shadow_from(m, offset=(10, 16), blur=24, color="#04140C", alpha=95)
        layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        layer.paste(lay, (s(x0), s(y0)), lay)
        if opacity < 255:
            layer.putalpha(layer.getchannel("A").point(lambda v: v * opacity // 255))
        self.im = Image.alpha_composite(self.im, layer)
        return (x0, y0, x0 + w, bottom)
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    sc = max(bw / im.width, bh / im.height)
    rw, rh = im.width * sc, im.height * sc
    ox = (rw - bw) * (0.5 if cx is None else cx)
    oy = (rh - bh) * (0.0 if bottom is None else bottom)
    lay = im.resize((s(rw), s(rh)), Image.LANCZOS).crop((s(ox), s(oy), s(ox) + s(bw), s(oy) + s(bh)))
    msk = Image.new("L", lay.size, 255)
    if mask is not None:
        msk = Image.new("L", lay.size, 0)
        dm = ImageDraw.Draw(msk)
        if mask[0] == "round":
            dm.rounded_rectangle([0, 0, lay.width, lay.height], radius=s(mask[1]), fill=255)
        elif mask[0] == "ellipse":
            dm.ellipse([0, 0, lay.width, lay.height], fill=255)
        elif mask[0] == "poly":
            dm.polygon([(s(px - x0), s(py - y0)) for px, py in mask[1]], fill=255)
    if fade_left:
        g = Image.linear_gradient("L").rotate(90, expand=True).resize(lay.size)   # 255 left -> 0 right
        g = g.point(lambda v: 255 - v)                                          # 0 left -> 255 right
        ramp = g.point(lambda v: min(255, int(v * 255 / max(1, fade_left * 255))))
        msk = Image.fromarray(np.minimum(np.asarray(msk), np.asarray(ramp)).astype("uint8"), "L")
    if fade_top:
        gt = Image.linear_gradient("L").resize(lay.size)                      # 0 top -> 255 bottom
        rampt = gt.point(lambda v: min(255, int(v * 255 / max(1, fade_top * 255))))
        msk = Image.fromarray(np.minimum(np.asarray(msk), np.asarray(rampt)).astype("uint8"), "L")
    big = Image.new("L", self.im.size, 0)
    big.paste(msk, (s(x0), s(y0)))
    if shadow:
        self.shadow_from(big, offset=(0, 18), blur=28, color="#04140C", alpha=90)
    layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
    layer.paste(lay, (s(x0), s(y0)), msk)
    self.im = Image.alpha_composite(self.im, layer)
    return box


Canvas.photo = _photo_into
