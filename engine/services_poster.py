"""
The all-services poster for المنهجية — a route map.

    python3 engine/services_poster.py posts/ads-02/manhajiya-services.png

The brand is called "المنهجية": the method, the way through. So the services are
not a grid of cards — they are stations along one ribbon that runs from the first
idea at the bottom to the defence at the top, and the reader's eye travels it.
The academy's poster is built on a different idea entirely; these two must never
be the same layout in two palettes.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402
from kit import C, RING, Canvas, font, linear_gradient, rgb, s  # noqa: E402

# Each station: (number, title, the two or three things we actually do there)
STATIONS = [
    ("١", "العنوان والخطة", ["عناوين مبتكرة غير مكررة", "خطة بحث (Proposal) كاملة"]),
    ("٢", "الإطار والمراجع", ["الدراسات السابقة والتعقيب", "مراجع عربية وأجنبية"]),
    ("٣", "الأدوات وجمع البيانات", ["استبانات وتحكيمها", "بيانات بورصة عمّان يدوياً"]),
    ("٤", "التحليل الإحصائي", ["اختبار الفرضيات", "تفسير النتائج وربطها"]),
    ("٥", "النشر العلمي", ["Scopus Q1 / Q2 / Q3 / Q4", "مجلات Arcif وأبحاث الترقية"]),
    ("٦", "التسليم والمناقشة", ["تدقيق لغوي وفحص اقتباس", "ترجمة وعروض تقديمية"]),
]


# The ribbon stays inside a narrow central band and the labels live in fixed
# columns outside it, so a label can never cross the route however the curve runs.
AMP, TOP, BOT = 150, 404, 1092
COL_R, COL_L = 712, 368


def ribbon_points():
    """A gentle S that snakes up the middle, from the first idea to the defence."""
    pts = []
    for i in range(0, 241):
        t = i / 240
        y = BOT - t * (BOT - TOP)
        x = 540 + AMP * math.sin(t * math.pi * 2.6 + 0.4)
        pts.append((x, y))
    return pts


def station_y(i, n):
    return BOT - 40 - i * ((BOT - TOP - 80) / (n - 1))


def ribbon_x(y, pts):
    return min(pts, key=lambda p: abs(p[1] - y))[0]


def main(out):
    c = Canvas()
    c.gradient_bg([C["night"], "#3A1250", C["purple"]], 120)
    c.glow(120, 1180, 430, C["magenta"], 95)
    c.glow(980, 300, 420, C["violet"], 85)
    c.dots(820, 72, 7, 3, color="#FFFFFF", alpha=65)
    c.dots(62, 1268, 7, 3, color="#FFFFFF", alpha=50)

    # --- the route itself: a thick ribbon filled with the brand's ring gradient
    pts = ribbon_points()
    mask = Image.new("L", c.im.size, 0)
    ImageDraw.Draw(mask).line([(s(x), s(y)) for x, y in pts], fill=255,
                              width=s(16), joint="curve")
    halo = mask.filter(ImageFilter.GaussianBlur(s(13)))
    c.paste_masked(Image.new("RGBA", c.im.size, rgb(C["magenta"])[:3] + (90,)), halo)
    c.paste_masked(c.grad_for(mask, RING, 60), mask)

    # --- header
    c.logo(116, 116, 126)
    c.text((956, 90), "المنهجية", font("kufi", 52, 900), fill="#FFFFFF", anchor="ra")
    c.text((956, 162), "للخدمات البحثية والعلمية", font("almarai", 28), fill="#E3D3F0", anchor="ra")
    c.text((540, 238), "خريطة رسالتك", font("kufi", 56, 900), gradient=RING, angle=20, anchor="ma")
    c.text((540, 328), "من أول فكرة حتى يوم المناقشة", font("almarai", 28),
           fill="#D9C6EA", anchor="ma")

    # --- stations: dot on the route, label in the fixed column on its side
    for i, (num, title, items) in enumerate(STATIONS):
        py = station_y(i, len(STATIONS))
        px = ribbon_x(py, pts)
        right = i % 2 == 0

        r = 36
        c.shape("ellipse", (px - r - 7, py - r - 7, px + r + 7, py + r + 7),
                fill=C["night"], opacity=235)
        c.shape("ellipse", (px - r, py - r, px + r, py + r), gradient=RING, angle=45)
        c.text((px, py + 1), num, font("kufi", 32, 900), fill="#FFFFFF", anchor="mm")

        tx = COL_R if right else COL_L
        anc = "la" if right else "ra"
        c.text((tx, py - 42), title, font("kufi", 29, 900), fill="#FFFFFF", anchor=anc)
        yy = py + 2
        for it in items:
            bx = tx + 6 if right else tx - 6
            c.shape("ellipse", (bx - 5, yy + 9, bx + 5, yy + 19), fill=C["yellow"])
            c.text((tx + 22 if right else tx - 22, yy), it, font("almarai", 22),
                   fill="#EFE4F7", anchor=anc)
            yy += 34

    c.footer(y=1236, dark=True, cta="استشارتك الأولى مجانية.. راسلنا الآن")
    c.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "manhajiya-services.png")
