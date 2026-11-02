"""
The all-services poster for أكاديمية العلماء العرب — an arcade.

    python3 asa/engine/services_poster.py asa/posts/ads-02/asa-services.png

This brand's world is scholarly and architectural: girih geometry, gold rule,
the mihrab arch already in its reel engine. So its services are a colonnade —
six arched niches under one gold-ruled header, read like the bays of a riwaq.

It must not share a layout with المنهجية's poster, which is a route map. Two
posters in the same grid with different palettes is not two identities.
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402
from kit import C, GOLD, Canvas, font, rgb, s  # noqa: E402

# Six bays. Short titles: an arch is narrow and the eye reads it as a label.
BAYS = [
    ("الرسائل\nوالأطاريح", ["عناوين وخطة بحث", "من المقدمة للخاتمة", "مشاريع التخرج"]),
    ("الإطار النظري\nوالمراجع", ["الدراسات السابقة", "مراجع عربية وأجنبية", "الفجوة البحثية"]),
    ("أدوات الدراسة\nوجمع البيانات", ["الاستبانة وتحكيمها", "الصدق والثبات", "المقابلات والترميز"]),
    ("التحليل\nالإحصائي", ["الاختبار المناسب", "اختبار الفرضيات", "جداول بصيغة APA"]),
    ("النشر\nالعلمي", ["Scopus Q1 Q2 Q3 Q4", "مجلات Arcif", "أبحاث الترقية"]),
    ("خدمات\nمساندة", ["تدقيق وتنسيق", "فحص Turnitin", "ترجمة ودورات"]),
]


def arch_mask(size, box, rise=0.52):
    """A pointed mihrab: straight jambs, then two arcs meeting at an apex."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    spring = y0 + w * rise
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rectangle([s(x0), s(spring), s(x1), s(y1)], fill=255)
    pts = [(x0, spring)]
    steps = 40
    for i in range(steps + 1):                      # left jamb up to the apex
        t = i / steps
        pts.append((x0 + w / 2 * t, spring - (spring - y0) * math.sin(t * math.pi / 2) ** 0.85))
    for i in range(steps + 1):                      # apex down to the right jamb
        t = i / steps
        pts.append((x0 + w / 2 + w / 2 * t,
                    y0 + (spring - y0) * (1 - math.cos(t * math.pi / 2) ** 0.85)))
    pts.append((x1, spring))
    d.polygon([(s(x), s(y)) for x, y in pts], fill=255)
    return m


def main(out):
    c = Canvas()
    c.gradient_bg([C["night"], C["deep"], C["forest"]], 118)
    c.girih(alpha=18)
    c.glow(540, 160, 460, C["gold"], 42)

    # --- header band, closed by a gold rule: the lintel over the arcade
    c.logo(540, 118, 132)
    c.text((540, 212), "أكاديمية العلماء العرب", font("cairo", 44, 900),
           gradient=GOLD, angle=18, anchor="ma")
    c.text((540, 276), "للاستشارات والتدريب", font("cairo", 26, 700),
           fill=C["gold_lt"], anchor="ma")
    c.divider(540, 330, 760)
    c.text((540, 352), "كل خدماتنا تحت سقف واحد", font("cairo", 40, 900),
           fill=C["ivory"], anchor="ma")

    # --- the arcade: two rows of three bays
    cols, rows = 3, 2
    bw, bh = 316, 350
    gx, gy = 16, 26
    x0 = (1080 - (cols * bw + (cols - 1) * gx)) / 2
    y0 = 428

    for i, (title, items) in enumerate(BAYS):
        r, col = divmod(i, cols)
        col = cols - 1 - col                         # fill right to left (RTL)
        bx = x0 + col * (bw + gx)
        by = y0 + r * (bh + gy)
        box = (bx, by, bx + bw, by + bh)

        m = arch_mask(c.im.size, box)
        c.paste_masked(Image.new("RGBA", c.im.size, rgb(C["deep"])[:3] + (225,)), m)
        # gold rim: the same arch, one step larger, minus the bay itself
        outer = arch_mask(c.im.size, (bx - 3, by - 3, bx + bw + 3, by + bh + 3))
        rim = Image.composite(outer, Image.new("L", c.im.size, 0),
                              Image.eval(m, lambda v: 255 - v))
        c.paste_masked(c.grad_for(rim, GOLD, 30), rim)

        cx = bx + bw / 2
        c.star8(cx, by + 74, 26, gradient=GOLD)

        ty = by + 126
        for ln in title.split("\n"):
            c.text((cx, ty), ln, font("cairo", 27, 900), fill=C["gold_lt"], anchor="ma")
            ty += 36
        c.divider(cx, ty + 24, 150)

        iy = ty + 46
        for it in items:
            c.text((cx, iy), it, font("cairo", 20, 700), fill=C["ivory"], anchor="ma")
            iy += 32

    bottom = y0 + rows * bh + (rows - 1) * gy
    assert bottom < 1190, f"the arcade reaches {bottom}px and would hit the footer"

    c.footer(y=1254, dark=True, cta="استشارتك الأولى مجانية.. تواصل معنا")
    c.save(out)
    print("wrote", out, f"(arcade ends at {bottom}px)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "asa-services.png")
