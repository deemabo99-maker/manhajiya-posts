"""
Post layouts for المنهجية. Each template takes a content dict (from a batch's
content.json) and returns a finished Canvas. Templates are reused week to week
with new copy, so the brand stays consistent while each post looks different.
"""
from kit import (C, RING, WARM, W, H, Canvas, font, measure)


def check_bullet(c, x_right, y, text, f, color, dot_fill=None, gap=58):
    """RTL bullet with a gradient check circle on the right."""
    r = 19
    cx = x_right - r
    if dot_fill:
        c.shape("ellipse", [cx - r, y - r, cx + r, y + r], fill=dot_fill)
    else:
        c.shape("ellipse", [cx - r, y - r, cx + r, y + r], gradient=WARM, angle=45)
    c.text((cx, y + 1), "✓", font("latin", 22), fill="#FFFFFF", anchor="mm")
    c.text((x_right - gap, y), text, f, fill=color, anchor="rm")


# ------------------------------------------------------------------ 1
def spotlight_dark(p):
    """Dark premium: big headline, a row of 4 badges, 3 bullets."""
    c = Canvas(C["night"])
    c.gradient_bg([C["night"], "#3A1250", C["plum"]], angle=115)
    c.glow(930, 230, 420, C["purple"], 150)
    c.glow(120, 1120, 320, C["pink"], 70)
    c.dots(70, 80, 7, 4, gap=24, color="#FFFFFF", alpha=70)
    c.plus(470, 120, color="#FFFFFF")
    c.plus(95, 560, size=18, thick=6, color=C["gold"])
    c.tri(70, 1080, 22, color="#FFFFFF", rot=0)

    c.logo(W - 165, 125, 185)

    # kicker
    kf = font("almarai-xb", 26)
    kw, _ = measure(p["kicker"], kf)
    x1 = W - 70
    c.shape("round", [x1 - kw - 44, 262, x1, 312], fill=(255, 255, 255, 0),
            outline=C["gold"], width=2.5, radius=25)
    c.text((x1 - 22, 288), p["kicker"], kf, fill=C["gold"], anchor="rm")

    c.text((W - 66, 340), p["title1"], font("kufi", 98, 900), fill="#FFFFFF", anchor="ra",
           shadow=dict(offset=(0, 8), blur=18, alpha=90, color="#000000"))
    c.text((W - 66, 470), p["title2"], font("kufi", 80, 900), gradient=list(reversed(WARM)), angle=0)

    # badges row (RTL: first badge on the right)
    n = len(p["badges"])
    bw, gap = 188, 28
    total = n * bw + (n - 1) * gap
    x_start = (W + total) / 2
    y0, y1 = 640, 640 + bw
    for i, b in enumerate(p["badges"]):
        x_r = x_start - i * (bw + gap)
        box = [x_r - bw, y0, x_r, y1]
        if i == 0:
            c.shape("round", box, gradient=RING, angle=60, radius=36,
                    shadow=dict(offset=(0, 16), blur=26, alpha=110, color="#000000"))
        else:
            c.shape("round", box, fill=(255, 255, 255, 26), radius=36,
                    outline=list(RING), width=3, angle=60)
        cx = x_r - bw / 2
        c.text((cx, y0 + bw / 2 - 10), b, font("latin", 70), fill="#FFFFFF", anchor="mm")
        c.text((cx, y1 - 30), p.get("badge_label", ""), font("almarai-bold", 22),
               fill="#FFFFFF" if i == 0 else "#D9C6E6", anchor="mm")

    y = 912
    for t in p["bullets"]:
        check_bullet(c, W - 70, y, t, font("almarai-bold", 33), "#FFFFFF")
        y += 68

    c.footer(dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 2
def steps_light(p):
    """Light background, diagonal purple header, numbered journey cards."""
    c = Canvas(C["paper"])
    c.shape("poly", [(0, 0), (W, 0), (W, 360), (0, 470)], gradient=[C["violet"], C["purple"], C["magenta"]], angle=20)
    c.dots(80, 300, 6, 3, gap=24, color="#FFFFFF", alpha=110)
    c.plus(300, 300, color="#FFFFFF")
    c.plus(1030, 470, color=C["ink"])
    c.dots(860, 1100, 6, 3, gap=22, color=C["purple"], alpha=90)

    c.logo(165, 128, 175)
    c.text((W - 66, 62), p["title1"], font("kufi", 74, 900), fill="#FFFFFF", anchor="ra",
           shadow=dict(offset=(0, 6), blur=14, alpha=80, color="#2A0F3A"))
    c.text((W - 66, 172), p["title2"], font("kufi", 74, 900), fill=C["gold"], anchor="ra",
           shadow=dict(offset=(0, 6), blur=14, alpha=80, color="#2A0F3A"))
    c.text((W - 70, 296), p["subtitle"], font("almarai-bold", 30), fill="#F3E8FA", anchor="ra")

    steps = p["steps"]
    top, row_h, gap = 512, 104, 18
    xr = W - 112
    # connector line
    c.shape("rect", [xr - 3, top + row_h / 2, xr + 3, top + (len(steps) - 1) * (row_h + gap) + row_h / 2],
            gradient=RING, angle=90)
    for i, (title, desc) in enumerate(steps):
        y0 = top + i * (row_h + gap)
        cy = y0 + row_h / 2
        c.shape("round", [70, y0, xr, y0 + row_h], fill="#FFFFFF", radius=26,
                shadow=dict(offset=(0, 8), blur=16, alpha=28))
        c.shape("ellipse", [xr - 42, cy - 42, xr + 42, cy + 42], gradient=RING, angle=60 + i * 12,
                shadow=dict(offset=(0, 6), blur=12, alpha=60))
        c.text((xr, cy + 2), str(i + 1), font("latin", 38), fill="#FFFFFF", anchor="mm")
        c.text((xr - 66, cy - 18), title, font("kufi", 31, 800), fill=C["ink"], anchor="rm")
        c.text((xr - 66, cy + 24), desc, font("almarai", 24), fill=C["muted"], anchor="rm")

    c.footer(dark=False, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 3
def chart_gradient(p):
    """Vivid purple background, white card with a chart illustration, pill list."""
    c = Canvas(C["purple"])
    c.gradient_bg([C["purple"], C["violet"], C["plum"]], angle=125)
    c.glow(90, 1180, 330, C["pink"], 90)
    c.glow(1000, 120, 300, "#C86BF0", 80)
    c.dots(860, 70, 6, 4, gap=24, color="#FFFFFF", alpha=80)
    c.plus(110, 300, color="#FFFFFF")
    c.tri(1018, 640, 22, color="#FFFFFF", rot=180)

    c.logo(165, 120, 170)
    c.text((W - 66, 240), p["title1"], font("kufi", 92, 900), fill="#FFFFFF", anchor="ra",
           shadow=dict(offset=(0, 8), blur=16, alpha=90, color="#1A0624"))
    c.text((W - 66, 400), p["title2"], font("almarai-xb", 40), fill=C["gold"], anchor="ra")

    # chart card
    x0, y0, x1, y1 = 110, 490, 970, 870
    c.shape("round", [x0, y0, x1, y1], fill="#FFFFFF", radius=40,
            shadow=dict(offset=(0, 22), blur=34, alpha=110, color="#14031C"))
    # axes
    ax0, ay1 = x0 + 90, y1 - 70
    c.shape("rect", [ax0, y0 + 100, ax0 + 4, ay1], fill="#D9CFE0")
    c.shape("rect", [ax0, ay1 - 4, x1 - 60, ay1], fill="#D9CFE0")
    for k in range(1, 4):
        gy = ay1 - k * 75
        c.shape("rect", [ax0 + 4, gy - 1, x1 - 60, gy + 1], fill="#F0EAF4")
    heights = [0.34, 0.52, 0.44, 0.68, 0.6, 0.86]
    n = len(heights)
    span = (x1 - 60) - (ax0 + 30)
    bw = span / n * 0.56
    pts = []
    for i, hgt in enumerate(heights):
        bx = ax0 + 30 + i * span / n + (span / n - bw) / 2
        by = ay1 - hgt * 280
        c.shape("round", [bx, by, bx + bw, ay1 - 4], gradient=[C["gold"], C["orange"], C["pink"], C["purple"]],
                angle=90, radius=12)
        pts.append((bx + bw / 2, by - 34))
    c.line(pts, C["plum"], 5)
    for (px, py) in pts:
        c.shape("ellipse", [px - 10, py - 10, px + 10, py + 10], fill="#FFFFFF", outline=C["plum"], width=4)
    # small stat chip on the card
    cf = font("almarai-xb", 24)
    label = p.get("card_label", "")
    if label:
        lw, _ = measure(label, cf)
        c.shape("round", [x0 + 30, y0 + 28, x0 + lw + 74, y0 + 78], gradient=RING, angle=0, radius=25)
        c.text((x0 + 52 + lw, y0 + 53), label, cf, fill="#FFFFFF", anchor="rm")

    # pills
    y = 930
    pf = font("almarai-xb", 30)
    for t in p["bullets"]:
        tw, _ = measure(t, pf)
        pw = tw + 110
        xr = W / 2 + pw / 2
        c.shape("round", [xr - pw, y - 32, xr, y + 32], fill=(255, 255, 255, 34), radius=32,
                outline="#FFFFFF", width=1.5)
        check_bullet(c, xr - 14, y, t, pf, "#FFFFFF", gap=56)
        y += 78

    c.footer(dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 4
def question_type(p):
    """Typographic hook: a big question, a highlighted answer and an offer pill."""
    c = Canvas("#FFFFFF")
    c.gradient_bg(["#FFFFFF", C["paper"], C["mist"]], angle=90)
    c.ring(165, 285, 185, 22, stops=RING, angle=45)
    c.text((165, 285), "؟", font("kufi", 230, 900), gradient=list(reversed(RING)), angle=90, anchor="mm")
    c.dots(60, 600, 5, 5, gap=22, color=C["purple"], alpha=110)
    c.plus(480, 130, color=C["ink"])
    c.plus(95, 1090, size=18, thick=6, color=C["purple"])
    c.tri(990, 1095, 24, color=C["ink"], rot=0)
    c.shape("poly", [(W, 960), (W, 1350), (690, 1350)], gradient=[C["mist"], "#E4D6EE"], angle=90)

    c.logo(W - 150, 110, 160)

    c.text((W - 66, 240), p["title1"], font("kufi", 112, 900), fill=C["ink"], anchor="ra")
    c.text((W - 66, 400), p["title2"], font("kufi", 84, 900), fill=C["purple"], anchor="ra")

    hf = font("almarai-xb", 48)
    c.highlight((W - 70, 590), p["line1"], hf, color="#FFE08A")
    c.text((W - 70, 590), p["line1"], hf, fill=C["ink"], anchor="ra")
    c.text((W - 70, 672), p["line2"], font("almarai-bold", 38), fill=C["muted"], anchor="ra")

    # offer pill
    of = font("kufi", 42, 800)
    ow, _ = measure(p["offer"], of)
    xr = W - 70
    c.shape("round", [xr - ow - 90, 780, xr, 866], gradient=RING, angle=0, radius=43,
            shadow=dict(offset=(0, 14), blur=22, alpha=80, color="#5B1A78"))
    c.text((xr - 45, 823), p["offer"], of, fill="#FFFFFF", anchor="rm")

    yy = 945
    for t in p["howto"]:
        c.text((W - 70, yy), t, font("almarai-bold", 32), fill=C["ink"], anchor="ra")
        yy += 52

    c.footer(dark=False, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 5
def grid_cards(p):
    """Purple header band and a 2x3 grid of service cards with icons."""
    c = Canvas(C["paper"])
    c.shape("poly", [(0, 0), (W, 0), (W, 440), (0, 340)], gradient=[C["magenta"], C["purple"], C["violet"]], angle=160)
    c.dots(860, 330, 6, 3, gap=22, color="#FFFFFF", alpha=100)
    c.plus(330, 300, color="#FFFFFF")

    c.logo(160, 120, 165)
    c.text((W - 66, 62), p["title1"], font("kufi", 76, 900), fill="#FFFFFF", anchor="ra",
           shadow=dict(offset=(0, 6), blur=14, alpha=80, color="#2A0F3A"))
    c.text((W - 66, 176), p["title2"], font("kufi", 60, 900), fill=C["gold"], anchor="ra",
           shadow=dict(offset=(0, 6), blur=14, alpha=80, color="#2A0F3A"))

    cards = p["cards"]
    cols, rows = 2, (len(cards) + 1) // 2
    gx0, gx1, gy0, gy1 = 70, W - 70, 470, 1112
    gap = 26
    cw = (gx1 - gx0 - gap) / cols
    ch = (gy1 - gy0 - (rows - 1) * gap) / rows
    for i, (icon, title, desc) in enumerate(cards):
        col = i % cols          # 0 = right column (RTL)
        row = i // cols
        xr = gx1 - col * (cw + gap)
        y0 = gy0 + row * (ch + gap)
        c.shape("round", [xr - cw, y0, xr, y0 + ch], fill="#FFFFFF", radius=30,
                shadow=dict(offset=(0, 10), blur=18, alpha=30))
        icx, icy = xr - 62, y0 + ch / 2
        c.shape("ellipse", [icx - 40, icy - 40, icx + 40, icy + 40], gradient=RING, angle=45 + i * 15)
        c.text((icx, icy + 2), icon, font("latin", 36), fill="#FFFFFF", anchor="mm")
        c.text((xr - 122, icy - 20), title, font("kufi", 27, 800), fill=C["ink"], anchor="rm")
        c.text((xr - 122, icy + 24), desc, font("almarai", 23), fill=C["muted"], anchor="rm")

    c.footer(dark=False, cta=p["cta"])
    return c


TEMPLATES = {
    "spotlight_dark": spotlight_dark,
    "steps_light": steps_light,
    "chart_gradient": chart_gradient,
    "question_type": question_type,
    "grid_cards": grid_cards,
}
