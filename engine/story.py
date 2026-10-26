"""
WhatsApp/Instagram status versions (1080 x 1920) of a batch's feed designs.

    python3 engine/story.py posts/batch-01

For every NN.png in the batch, writes story-NN.png: the design on a branded
9:16 background, with a "message us on WhatsApp" bar underneath.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402
from kit import C, RING, font, linear_gradient, rgb  # noqa: E402

SW, SH = 1080, 1920


def story(src, dst):
    s = kit.S
    bg = linear_gradient((SW * s, SH * s), [C["night"], "#3A1250", C["purple"]], 110)
    d = ImageDraw.Draw(bg)
    # dots + plus motifs
    for i in range(7):
        for j in range(4):
            cx, cy = (820 + i * 26) * s, (1770 + j * 26) * s
            d.ellipse([cx - 3.5 * s, cy - 3.5 * s, cx + 3.5 * s, cy + 3.5 * s], fill=(255, 255, 255, 80))
    for px, py in [(980, 120), (100, 1830)]:
        d.rectangle([(px - 13) * s, (py - 4) * s, (px + 13) * s, (py + 4) * s], fill="#FFFFFF")
        d.rectangle([(px - 4) * s, (py - 13) * s, (px + 4) * s, (py + 13) * s], fill="#FFFFFF")

    # design card
    post = Image.open(src).convert("RGBA")
    cw = 960
    ch = int(cw * post.height / post.width)
    x0, y0 = (SW - cw) // 2, 230
    card = post.resize((cw * s, ch * s), Image.LANCZOS)
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.width, card.height], radius=40 * s, fill=255)
    sh = Image.new("L", bg.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([x0 * s, (y0 + 18) * s, (x0 + cw) * s, (y0 + ch + 18) * s],
                                         radius=40 * s, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(30 * s))
    shadow = Image.new("RGBA", bg.size, (10, 0, 20, 255))
    bg.paste(shadow, (0, 0), sh)
    bg.paste(card, (x0 * s, y0 * s), mask)
    # gradient frame
    ring = Image.new("L", bg.size, 0)
    ImageDraw.Draw(ring).rounded_rectangle([(x0 - 6) * s, (y0 - 6) * s, (x0 + cw + 6) * s, (y0 + ch + 6) * s],
                                           radius=46 * s, outline=255, width=6 * s)
    bg.paste(linear_gradient(bg.size, RING, 45), (0, 0), ring)

    # top line
    d = ImageDraw.Draw(bg)
    d.text((SW / 2 * s, 150 * s), "المنهجية للخدمات البحثية والعلمية", font=font("almarai-xb", 40),
           fill="#FFFFFF", anchor="mm", direction="rtl", language="ar")

    # bottom: CTA + WhatsApp pill
    yb = y0 + ch + 120
    d.text((SW / 2 * s, yb * s), "استشارة مجانية.. راسلنا الآن", font=font("kufi", 50, 900),
           fill=rgb(C["gold"]), anchor="mm", direction="rtl", language="ar")
    num = kit.CONTACT["whatsapp"]
    fnum, flab = font("latin", 40), font("almarai-xb", 36)
    nw = (fnum.getbbox(num)[2] - fnum.getbbox(num)[0]) / s
    lw = (flab.getbbox("واتساب", direction="rtl", language="ar")[2]
          - flab.getbbox("واتساب", direction="rtl", language="ar")[0]) / s
    pw, ph = nw + lw + 170, 104
    px0, py0 = (SW - pw) / 2, yb + 80
    d.rounded_rectangle([px0 * s, py0 * s, (px0 + pw) * s, (py0 + ph) * s], radius=ph / 2 * s, fill=rgb(C["green"]))
    gx, gy, r = (px0 + pw - 58) * s, (py0 + ph / 2) * s, 30 * s
    d.polygon([(gx - 0.7 * r, gy + 0.55 * r), (gx - 1.15 * r, gy + 1.15 * r), (gx - 0.15 * r, gy + 0.95 * r)], fill="#FFFFFF")
    d.ellipse([gx - r, gy - r, gx + r, gy + r], fill="#FFFFFF")
    d.text((gx, gy + 2 * s), "☎", font=font("latin", 34), fill=rgb(C["green"]), anchor="mm")
    d.text((gx - 52 * s, gy), "واتساب", font=flab, fill="#FFFFFF", anchor="rm", direction="rtl", language="ar")
    d.text(((px0 + 34) * s, gy + 2 * s), num, font=fnum, fill="#FFFFFF", anchor="lm")

    bg.resize((SW, SH), Image.LANCZOS).convert("RGB").save(dst, "PNG", optimize=True)


def main(batch):
    for src in sorted(glob.glob(os.path.join(batch, "[0-9][0-9].png"))):
        dst = os.path.join(batch, "story-" + os.path.basename(src))
        story(src, dst)
        print("story", dst)


if __name__ == "__main__":
    main(sys.argv[1])
