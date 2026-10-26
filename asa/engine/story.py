"""
WhatsApp/Instagram status versions (1080 x 1920) of a batch's feed designs.

    python3 engine/story.py posts/batch-01

For every NN.png in the batch, writes story-NN.png: the design on an emerald
girih background with a gold frame, the emblem on top and a WhatsApp bar below.
"""
import glob
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402
from kit import C, GOLD, font, linear_gradient, rgb  # noqa: E402

SW, SH = 1080, 1920


def story(src, dst):
    s = kit.S
    bg = linear_gradient((SW * s, SH * s), [C["night"], C["deep"], C["emerald"]], 100)
    d = ImageDraw.Draw(bg)
    cell, rr = 180 * s, 180 * s * 0.42
    y, row = 0, 0
    while y < SH * s + cell:
        x = cell / 2 if row % 2 else 0
        while x < SW * s + cell:
            pts = []
            for k in range(16):
                q = rr if k % 2 == 0 else rr * 0.76
                a = math.radians(k * 22.5)
                pts.append((x + q * math.cos(a), y + q * math.sin(a)))
            d.line(pts + [pts[0]], fill=rgb(C["gold"])[:3] + (28,), width=2 * s)
            x += cell
        y += cell * 0.866
        row += 1

    # emblem + name on top
    lg = Image.open(kit.LOGO).convert("RGBA")
    ew = 120
    eh = int(ew * lg.height / lg.width)
    bg.alpha_composite(lg.resize((ew * s, eh * s), Image.LANCZOS), ((SW // 2 - ew // 2) * s, 40 * s))
    d.text((SW / 2 * s, (60 + eh) * s), kit.BRAND_AR, font=font("messiri", 40, 700), fill=rgb(C["ivory"]),
           anchor="mm", direction="rtl", language="ar")

    post = Image.open(src).convert("RGBA")
    cw = 940
    ch = int(cw * post.height / post.width)
    x0, y0 = (SW - cw) // 2, 250
    card = post.resize((cw * s, ch * s), Image.LANCZOS)
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.width, card.height], radius=34 * s, fill=255)
    sh = Image.new("L", bg.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([x0 * s, (y0 + 18) * s, (x0 + cw) * s, (y0 + ch + 18) * s],
                                         radius=34 * s, fill=160)
    bg.paste(Image.new("RGBA", bg.size, (2, 10, 6, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(30 * s)))
    bg.paste(card, (x0 * s, y0 * s), mask)
    ring = Image.new("L", bg.size, 0)
    ImageDraw.Draw(ring).rounded_rectangle([(x0 - 7) * s, (y0 - 7) * s, (x0 + cw + 7) * s, (y0 + ch + 7) * s],
                                           radius=40 * s, outline=255, width=6 * s)
    bg.paste(linear_gradient(bg.size, GOLD, 30), (0, 0), ring)

    d = ImageDraw.Draw(bg)
    yb = y0 + ch + 110
    d.text((SW / 2 * s, yb * s), "استشارتك الأولى مجانية", font=font("ruqaa", 64), fill=rgb(C["gold_lt"]),
           anchor="mm", direction="rtl", language="ar")
    num = kit.CONTACT["display"]
    fnum, flab = font("latin", 40), font("messiri", 36, 700)
    nw = (fnum.getbbox(num)[2] - fnum.getbbox(num)[0]) / s
    lb = flab.getbbox("واتساب", direction="rtl", language="ar")
    pw, ph = nw + (lb[2] - lb[0]) / s + 170, 104
    px0, py0 = (SW - pw) / 2, yb + 75
    d.rounded_rectangle([(px0 - 4) * s, (py0 - 4) * s, (px0 + pw + 4) * s, (py0 + ph + 4) * s], radius=(ph / 2 + 4) * s,
                        fill=rgb(C["gold"]))
    d.rounded_rectangle([px0 * s, py0 * s, (px0 + pw) * s, (py0 + ph) * s], radius=ph / 2 * s, fill=rgb(C["wa"]))
    gx, gy, r = (px0 + pw - 58) * s, (py0 + ph / 2) * s, 30 * s
    d.polygon([(gx - 0.7 * r, gy + 0.55 * r), (gx - 1.15 * r, gy + 1.15 * r), (gx - 0.15 * r, gy + 0.95 * r)], fill="#FFFFFF")
    d.ellipse([gx - r, gy - r, gx + r, gy + r], fill="#FFFFFF")
    d.text((gx, gy + 2 * s), "☎", font=font("latin", 34), fill=rgb(C["wa"]), anchor="mm")
    d.text((gx - 52 * s, gy), "واتساب", font=flab, fill="#FFFFFF", anchor="rm", direction="rtl", language="ar")
    d.text(((px0 + 34) * s, gy + 2 * s), num, font=fnum, fill="#FFFFFF", anchor="lm")
    d.text((SW / 2 * s, (py0 + ph + 52) * s), "Instagram  " + kit.CONTACT["instagram"], font=font("latin", 30),
           fill=rgb(C["gold_lt"]), anchor="mm")

    bg.resize((SW, SH), Image.LANCZOS).convert("RGB").save(dst, "PNG", optimize=True)


def main(batch):
    for src in sorted(glob.glob(os.path.join(batch, "[0-9][0-9].png"))):
        dst = os.path.join(batch, "story-" + os.path.basename(src))
        story(src, dst)
        print("story", dst)


if __name__ == "__main__":
    main(sys.argv[1])
