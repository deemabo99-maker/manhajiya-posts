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


# ------------------------------------------------------------------ 6 (batch-02)
def _squiggle(c, x0, x1, y, color, amp=5, step=14, width=3.5):
    import math as _m
    pts, x = [], x0
    while x <= x1:
        pts.append((x, y + amp * _m.sin((x - x0) / step * _m.pi)))
        x += 4
    c.line(pts, color, width)


def myth_fact(p):
    """Dark: a crossed-out myth card and an overlapping bright fact card (myth vs. fact)."""
    c = Canvas(C["night"])
    c.gradient_bg([C["night"], "#2E0D3D", C["plum"]], angle=100)
    c.glow(880, 760, 420, C["purple"], 140)
    c.glow(140, 330, 300, C["pink"], 60)
    c.dots(70, 1102, 6, 2, gap=22, color="#FFFFFF", alpha=70)
    c.plus(330, 225, color=C["gold"])
    c.tri(1030, 300, 20, color="#FFFFFF", rot=0)

    c.logo(160, 118, 160)
    c.text((W - 66, 52), p["title1"], font("kufi", 74, 900), fill="#FFFFFF", anchor="ra",
           shadow=dict(offset=(0, 6), blur=14, alpha=90, color="#000000"))
    c.text((W - 66, 170), p["subtitle"], font("almarai-xb", 34), fill=C["gold"], anchor="ra")

    # --- myth card (muted, struck through)
    mx0, my0, mx1, my1 = 70, 268, W - 70, 548
    c.shape("round", [mx0, my0, mx1, my1], fill=(255, 255, 255, 22), radius=34,
            outline=C["pink"], width=2.5)
    tf = font("almarai-xb", 28)
    tw, _ = measure(p["myth_tag"], tf)
    c.shape("round", [mx1 - tw - 64, my0 - 26, mx1 - 30, my0 + 26], fill=C["pink"], radius=26)
    c.text((mx1 - 47, my0 + 1), p["myth_tag"], tf, fill="#FFFFFF", anchor="rm")
    mf = font("kufi", 46, 800)
    y = my0 + 62
    for line in p["myth"]:
        lw, lh = measure(line, mf)
        c.text((mx1 - 50, y), line, mf, fill="#CDB9D8", anchor="ra")
        sy = y + 46
        c.line([(mx1 - 50 - lw - 10, sy + 6), (mx1 - 40, sy - 6)], C["pink"], 7)
        y += 92
    # big X seal
    cx, cy, r = mx0 + 110, (my0 + my1) / 2 + 6, 74
    c.shape("ellipse", [cx - r, cy - r, cx + r, cy + r], fill=C["pink"],
            shadow=dict(offset=(0, 12), blur=20, alpha=110, color="#000000"))
    c.line([(cx - 30, cy - 30), (cx + 30, cy + 30)], "#FFFFFF", 14)
    c.line([(cx - 30, cy + 30), (cx + 30, cy - 30)], "#FFFFFF", 14)

    # --- fact card (bright, overlapping the myth card)
    fx0, fy0, fx1, fy1 = 70, 590, W - 70, 975
    c.shape("round", [fx0, fy0, fx1, fy1], fill="#FFFFFF", radius=40,
            shadow=dict(offset=(0, 26), blur=36, alpha=150, color="#0B0110"))
    c.shape("round", [fx0, fy0, fx0 + 16, fy1], gradient=RING, angle=90, radius=8)
    tw, _ = measure(p["fact_tag"], tf)
    c.shape("round", [fx1 - tw - 64, fy0 - 26, fx1 - 30, fy0 + 26], gradient=RING, angle=0, radius=26,
            shadow=dict(offset=(0, 8), blur=14, alpha=80, color="#2A0F3A"))
    c.text((fx1 - 47, fy0 + 1), p["fact_tag"], tf, fill="#FFFFFF", anchor="rm")
    c.text((fx1 - 50, fy0 + 52), p["fact"][0], font("kufi", 70, 900), gradient=[C["magenta"], C["purple"], C["violet"]],
           angle=0, anchor="ra")
    c.text((fx1 - 50, fy0 + 172), p["fact"][1], font("kufi", 44, 800), fill=C["ink"], anchor="ra")
    c.text((fx1 - 50, fy0 + 262), p["fact"][2], font("almarai-bold", 32), fill=C["muted"], anchor="ra")
    cx, cy, r = fx0 + 120, fy0 + 175, 80
    c.ring(cx, cy, r, 14, stops=RING, angle=45)
    c.text((cx, cy + 4), "✓", font("latin", 84), gradient=list(reversed(RING)), angle=90, anchor="mm")

    # chips
    cf = font("almarai-xb", 27)
    n = len(p["chips"])
    gap = 18
    cw = (W - 140 - gap * (n - 1)) / n
    for i, t in enumerate(p["chips"]):
        xr = W - 70 - i * (cw + gap)
        c.shape("round", [xr - cw, 1012, xr, 1080], fill=(255, 255, 255, 30), radius=34,
                outline=C["gold"], width=2)
        c.text((xr - cw / 2, 1046), t, cf, fill="#FFFFFF", anchor="mm")

    c.footer(dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 7 (batch-02)
def _bubble(c, side, y, lines, fill, ink, f, screen, tail=True):
    x0s, x1s = screen
    pad, lh = 26, 46
    w = max(measure(l, f)[0] for l in lines) + pad * 2
    h = lh * len(lines) + pad * 1.2
    if side == "right":
        bx1 = x1s - 22
        bx0 = bx1 - w
    else:
        bx0 = x0s + 22
        bx1 = bx0 + w
    c.shape("round", [bx0, y, bx1, y + h], fill=fill, radius=24,
            shadow=dict(offset=(0, 4), blur=6, alpha=30, color="#2A0F3A"))
    if tail:
        if side == "right":
            c.shape("poly", [(bx1 - 20, y), (bx1 + 14, y), (bx1 - 4, y + 22)], fill=fill)
        else:
            c.shape("poly", [(bx0 + 20, y), (bx0 - 14, y), (bx0 + 4, y + 22)], fill=fill)
    yy = y + pad * 0.6 + lh / 2
    for l in lines:
        c.text((bx1 - pad, yy), l, f, fill=ink, anchor="rm")
        yy += lh
    return y + h


def chat_phone(p):
    """Vivid purple: a phone mock-up with a WhatsApp-style chat as the focal point, plus floating stickers."""
    c = Canvas(C["purple"])
    c.gradient_bg([C["magenta"], C["purple"], C["violet"]], angle=140)
    c.glow(540, 760, 460, "#E08BFF", 110)
    c.glow(1000, 1200, 280, C["orange"], 70)
    c.dots(60, 420, 5, 6, gap=24, color="#FFFFFF", alpha=90)
    c.plus(1010, 330, color="#FFFFFF")
    c.plus(70, 1000, size=18, thick=6, color=C["gold"])

    c.logo(160, 118, 160)
    c.text((W - 66, 40), p["title1"], font("kufi", 80, 900), fill="#FFFFFF", anchor="ra",
           shadow=dict(offset=(0, 6), blur=14, alpha=90, color="#2A0F3A"))
    c.text((W - 66, 150), p["title2"], font("kufi", 80, 900), fill=C["gold"], anchor="ra",
           shadow=dict(offset=(0, 6), blur=14, alpha=90, color="#2A0F3A"))

    # phone body
    px0, py0, px1, py1 = 245, 300, 835, 1135
    c.shape("round", [px0, py0, px1, py1], fill=C["night"], radius=72,
            shadow=dict(offset=(0, 30), blur=40, alpha=150, color="#14031C"))
    sx0, sy0, sx1, sy1 = px0 + 18, py0 + 18, px1 - 18, py1 - 18
    c.shape("round", [sx0, sy0, sx1, sy1], fill="#EFE6F3", radius=56)
    # chat header
    c.shape("round", [sx0, sy0, sx1, sy0 + 120], fill=C["violet"], radius=56)
    c.shape("rect", [sx0, sy0 + 70, sx1, sy0 + 120], fill=C["violet"])
    c.shape("round", [(sx0 + sx1) / 2 - 60, sy0 + 12, (sx0 + sx1) / 2 + 60, sy0 + 30], fill=C["night"], radius=9)
    ax = sx1 - 70
    c.shape("ellipse", [ax - 32, sy0 + 50, ax + 32, sy0 + 114], fill="#FFFFFF")
    c.logo(ax, sy0 + 82, 44, badge=False)
    c.text((ax - 48, sy0 + 66), "المنهجية", font("almarai-xb", 30), fill="#FFFFFF", anchor="rm")
    c.text((ax - 48, sy0 + 102), "متصل الآن", font("almarai", 22), fill="#E2C9F0", anchor="rm")

    bf = font("almarai-bold", 29)
    y = sy0 + 152
    y = _bubble(c, "right", y, p["student"], "#D9FDD3", C["ink"], bf, (sx0, sx1)) + 26
    for msg in p["replies"]:
        y = _bubble(c, "left", y, msg, "#FFFFFF", C["ink"], bf, (sx0, sx1)) + 20
    # typing indicator
    c.shape("round", [sx0 + 22, y, sx0 + 132, y + 56], fill="#FFFFFF", radius=28)
    for k in range(3):
        cx = sx0 + 50 + k * 27
        c.shape("ellipse", [cx - 8, y + 20, cx + 8, y + 36], fill=[C["purple"], C["magenta"], C["pink"]][k])
    # input bar
    c.shape("round", [sx0 + 18, sy1 - 82, sx1 - 96, sy1 - 22], fill="#FFFFFF", radius=30)
    c.text((sx1 - 120, sy1 - 52), "اكتب رسالتك…", font("almarai", 24), fill=C["muted"], anchor="rm")
    c.shape("ellipse", [sx1 - 84, sy1 - 84, sx1 - 20, sy1 - 20], fill=C["green"])
    c.shape("poly", [(sx1 - 66, sy1 - 66), (sx1 - 34, sy1 - 52), (sx1 - 66, sy1 - 38)], fill="#FFFFFF")

    # floating stickers overlapping the phone edges
    sf = font("kufi", 34, 900)
    t = p["sticker1"]
    tw, _ = measure(t, sf)
    c.shape("round", [W - 40 - tw - 70, 300, W - 40, 380], gradient=list(reversed(WARM)), angle=0, radius=40,
            shadow=dict(offset=(0, 14), blur=20, alpha=110, color="#2A0F3A"))
    c.text((W - 40 - 35, 338), t, sf, fill=C["ink"], anchor="rm")
    t = p["sticker2"]
    tw, _ = measure(t, sf)
    c.shape("round", [40, 960, 40 + tw + 70, 1040], fill="#FFFFFF", radius=40,
            shadow=dict(offset=(0, 14), blur=20, alpha=110, color="#2A0F3A"))
    c.text((40 + tw + 35, 998), t, sf, fill=C["purple"], anchor="rm")

    c.footer(dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 8 (batch-02)
def before_after(p):
    """Light: the same page before (marked up, messy) and after (structured, ticked), side by side."""
    c = Canvas(C["paper"])
    c.gradient_bg(["#FFFFFF", C["paper"], C["mist"]], angle=90)
    c.shape("poly", [(0, 1350), (0, 1010), (420, 1350)], gradient=[C["mist"], "#E4D6EE"], angle=90)
    c.dots(70, 1010, 5, 3, gap=22, color=C["purple"], alpha=90)
    c.plus(500, 200, color=C["ink"])
    c.tri(1020, 300, 20, color=C["purple"], rot=0)

    c.logo(160, 118, 160)
    c.text((W - 66, 40), p["title1"], font("kufi", 84, 900), fill=C["ink"], anchor="ra")
    hf = font("kufi", 84, 900)
    c.text((W - 66, 160), p["title2"], hf, gradient=[C["magenta"], C["purple"], C["violet"]], angle=0, anchor="ra")

    top, bot = 340, 990
    # BEFORE (right side, read first in RTL)
    bx0, bx1 = 590, 1020
    c.shape("round", [bx0, top, bx1, bot], fill="#F2EEF4", radius=30, outline="#D5CBDC", width=2,
            shadow=dict(offset=(0, 10), blur=18, alpha=30))
    lf = font("almarai-xb", 28)
    c.shape("round", [bx1 - 150, top - 28, bx1 - 30, top + 28], fill="#8E8496", radius=28)
    c.text((bx1 - 90, top + 1), p["before_tag"], lf, fill="#FFFFFF", anchor="mm")
    y = top + 80
    widths = [0.9, 0.75, 0.95, 0.6, 0.85, 0.7, 0.92, 0.55, 0.8, 0.88]
    for i, wv in enumerate(widths):
        x1 = bx1 - 40
        x0 = x1 - (bx1 - bx0 - 80) * wv
        c.shape("round", [x0, y, x1, y + 14], fill="#CFC5D6", radius=7)
        if i in (1, 4, 7):
            _squiggle(c, x0, x1, y + 26, "#E0245E", amp=4, step=10, width=3)
        y += 52
    # red margin notes
    nf = font("almarai-xb", 26)
    for (ny, note) in zip((450, 640, 830), p["notes"]):
        nw, _ = measure(note, nf)
        c.shape("round", [bx0 + 40, ny, bx0 + nw + 76, ny + 48], fill="#FFE3EA", radius=12, outline="#E0245E", width=2)
        c.text((bx0 + nw + 58, ny + 24), note, nf, fill="#C21A50", anchor="rm")

    # AFTER (left side)
    ax0, ax1 = 60, 490
    c.shape("round", [ax0, top, ax1, bot], fill="#FFFFFF", radius=30,
            shadow=dict(offset=(0, 22), blur=30, alpha=70, color="#4B1A5E"))
    c.shape("round", [ax0, top, ax1, top + 92], gradient=[C["violet"], C["purple"], C["magenta"]], angle=0, radius=30)
    c.shape("rect", [ax0, top + 60, ax1, top + 92], gradient=[C["violet"], C["purple"], C["magenta"]], angle=0)
    c.shape("round", [ax1 - 150, top - 28, ax1 - 30, top + 28], gradient=list(reversed(WARM)), angle=0, radius=28,
            shadow=dict(offset=(0, 8), blur=14, alpha=70, color="#5B1A78"))
    c.text((ax1 - 90, top + 1), p["after_tag"], lf, fill=C["ink"], anchor="mm")
    c.text(((ax0 + ax1) / 2, top + 58), p["after_title"], font("kufi", 32, 800), fill="#FFFFFF", anchor="mm")
    y = top + 140
    sf = font("kufi", 31, 800)
    for i, sec in enumerate(p["sections"]):
        cy = y + i * 92
        r = 22
        cx = ax1 - 50
        c.shape("ellipse", [cx - r, cy - r, cx + r, cy + r], gradient=RING, angle=45 + i * 20)
        c.text((cx, cy + 1), "✓", font("latin", 24), fill="#FFFFFF", anchor="mm")
        c.text((cx - 40, cy), sec, sf, fill=C["ink"], anchor="rm")
        c.shape("round", [ax0 + 34, cy + 30, cx - 40, cy + 36], fill="#EFE6F5", radius=3)

    # arrow disc between the two pages
    cx, cy, r = 540, 665, 62
    c.shape("ellipse", [cx - r, cy - r, cx + r, cy + r], gradient=RING, angle=45,
            shadow=dict(offset=(0, 12), blur=20, alpha=100, color="#5B1A78"))
    c.shape("poly", [(cx - 30, cy), (cx + 4, cy - 30), (cx + 4, cy - 12), (cx + 30, cy - 12),
                     (cx + 30, cy + 12), (cx + 4, cy + 12), (cx + 4, cy + 30)], fill="#FFFFFF")

    bl = font("almarai-xb", 36)
    c.highlight((W / 2, 1030), p["line"], bl, color="#FFE08A", anchor="ma")
    c.text((W / 2, 1030), p["line"], bl, fill=C["ink"], anchor="ma")

    c.footer(dark=False, cta=p["cta"])
    return c


TEMPLATES = {
    "spotlight_dark": spotlight_dark,
    "steps_light": steps_light,
    "chart_gradient": chart_gradient,
    "question_type": question_type,
    "grid_cards": grid_cards,
    "myth_fact": myth_fact,
    "chat_phone": chat_phone,
    "before_after": before_after,
}
