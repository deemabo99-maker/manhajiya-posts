"""
Post layouts for أكاديمية العلماء العرب للاستشارات والتدريب.

Visual language: ivory paper, deep emerald, gold foil, the emblem's ribbon red,
eight-point-star (girih) ornaments, arches and classical Arabic calligraphy -
deliberately nothing like the purple/neon look of المنهجية.
Each template takes a content dict and returns a finished Canvas.
"""
import math

from kit import (C, GOLD, GOLD_SOFT, GREEN, W, H, Canvas, font, measure, rgb)


def gold_text(c, xy, txt, f, anchor="ra", shadow=True, dark=False):
    """Gold-foil text. dark=True uses a deeper foil that reads on ivory backgrounds."""
    stops = (["#6E500F", "#B48A22", "#D9B54F", "#A27C1C", "#6E500F"] if dark
             else ["#9C7A22", "#E9CF7A", "#F7E7B4", "#C8A02E", "#8C6A1F"])
    sh = None
    if shadow:
        sh = (dict(offset=(0, 5), blur=8, alpha=55, color="#5A4310") if dark
              else dict(offset=(0, 6), blur=12, alpha=110, color="#04140C"))
    c.text(xy, txt, f, gradient=stops, angle=90, anchor=anchor, shadow=sh)


def bullet_row(c, x_right, y, text, f, color, gap=48):
    c.diamond(x_right - 12, y, 12, gradient=GOLD_SOFT)
    c.diamond(x_right - 12, y, 4, fill=C["deep"])
    c.text((x_right - gap, y), text, f, fill=color, anchor="rm")


def arch_path(x0, y0, x1, y1, steps=48):
    """Pointed (mihrab) arch outline as a polygon: straight sides, two curves meeting at a tip."""
    cx = (x0 + x1) / 2
    spring = y0 + (x1 - x0) * 0.55
    pts = [(x0, y1), (x0, spring)]
    for i in range(1, steps + 1):
        t = i / steps
        pts.append((x0 + (cx - x0) * t, spring - (spring - y0) * math.sin(t * math.pi / 2) ** 0.85))
    for i in range(1, steps + 1):
        t = i / steps
        pts.append((cx + (x1 - cx) * t, y0 + (spring - y0) * (1 - math.cos(t * math.pi / 2)) ** 0.85))
    pts += [(x1, spring), (x1, y1)]
    return pts


# ------------------------------------------------------------------ 1 arch hero
def arch_hero(p):
    c = Canvas(C["deep"])
    c.gradient_bg([C["night"], C["deep"], C["emerald"]], angle=100)
    c.girih(alpha=26, cell=170)
    c.glow(540, 520, 420, C["jade"], 70)
    c.lockup(W - 70, 110, size=104, dark=True)

    ax0, ay0, ax1, ay1 = 120, 210, 960, 1110
    arch = arch_path(ax0, ay0, ax1, ay1)
    outer = arch_path(ax0 - 14, ay0 - 14, ax1 + 14, ay1)
    c.shape("poly", outer, gradient=GOLD, angle=20,
            shadow=dict(offset=(0, 18), blur=30, alpha=120, color="#000000"))
    c.shape("poly", arch, gradient=[C["ivory"], C["cream"], C["sand"]], angle=90)
    c.girih(alpha=30, cell=120, box=(ax0, ay0 + 160, ax1, ay1), color=C["gold"])
    c.star8(540, ay0 + 120, 30, gradient=GOLD_SOFT)
    c.star8(540, ay0 + 120, 11, fill=C["emerald"])

    c.text((540, 410), p["kicker"], font("messiri", 34, 700), fill=C["red"], anchor="mm")
    c.text((540, 500), p["title1"], font("ruqaa", 80), fill=C["forest"], anchor="mm",
           shadow=dict(offset=(0, 4), blur=6, alpha=40, color="#0B2E1E"))
    gold_text(c, (540, 610), p["title2"], font("ruqaa", 72), anchor="mm", shadow=False, dark=True)
    c.divider(540, 700, 520)
    y = 765
    for t in p["bullets"]:
        bullet_row(c, 820, y, t, font("messiri", 36, 600), C["ink"])
        y += 66
    c.footer(dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 2 big stats
def laurel(c, cx, cy, r, side, n=13, start=-64, end=62):
    """One laurel branch along the side of a circle. side=-1 left, 1 right.
    Angles in degrees measured from the bottom of the circle going up the side."""
    pts_stem = []
    for i in range(n):
        t = i / (n - 1)
        deg = start + (end - start) * t
        a = math.radians(deg)
        x = cx + side * r * math.cos(a)
        y = cy - r * math.sin(a)
        pts_stem.append((x, y))
    c.line(pts_stem, C["gold_dk"], 3)
    for i, (x, y) in enumerate(pts_stem):
        t = i / (n - 1)
        deg = start + (end - start) * t
        a = math.radians(deg)
        # tangent direction (going up the branch)
        tx, ty = -side * math.sin(a), -math.cos(a)
        for k, off in ((0, 0.55), (1, -0.55)):
            # leaf direction: tangent rotated outward/inward
            nx, ny = side * math.cos(a), -math.sin(a)
            dx = tx * 0.75 + (nx if k == 0 else -nx) * 0.62
            dy = ty * 0.75 + (ny if k == 0 else -ny) * 0.62
            L = 54 - 18 * t
            Wd = 17 - 5 * t
            ang = math.atan2(dy, dx)
            leaf = []
            for j in range(28):
                u = j / 27
                px = L * u
                py = Wd * math.sin(math.pi * u) ** 0.9
                leaf.append((px, py))
            for j in range(27, -1, -1):
                u = j / 27
                leaf.append((L * u, -Wd * math.sin(math.pi * u) ** 0.9))
            poly = [(x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang))
                    for px, py in leaf]
            c.shape("poly", poly, gradient=["#9C7A22", "#E9CF7A", "#B98E25"], angle=45)
    # top leaf
    x, y = pts_stem[-1]


def stat_hero(p):
    c = Canvas(C["ivory"])
    c.gradient_bg([C["ivory"], C["cream"], C["sand"]], angle=90)
    c.girih(alpha=38, cell=150, color=C["gold"])
    c.paper_noise(4)
    c.lockup(W - 70, 110, size=104)
    c.text((540, 255), p["kicker"], font("messiri", 38, 700), fill=C["red"], anchor="mm")

    cy = 540
    laurel(c, 540, cy, 395, -1)
    laurel(c, 540, cy, 395, 1)
    gold_text(c, (540, cy - 40), p["number"], font("rakkas", 220), anchor="mm", dark=True)
    c.text((540, cy + 110), p["number_label"], font("messiri", 46, 700), fill=C["forest"], anchor="mm")
    c.divider(540, cy + 185, 300)

    # second stat in an emerald plaque
    px0, py0, px1, py1 = 150, 820, 930, 1010
    c.shape("round", [px0, py0, px1, py1], gradient=[C["emerald"], C["deep"]], angle=0, radius=34,
            shadow=dict(offset=(0, 16), blur=26, alpha=70))
    c.gold_frame([px0, py0, px1, py1], radius=34, inset=12, corners=False)
    gold_text(c, (px1 - 60, (py0 + py1) / 2 + 4), p["number2"], font("rakkas", 110), anchor="rm", shadow=False)
    c.text((px1 - 330, (py0 + py1) / 2 - 22), p["number2_label1"], font("messiri", 38, 700),
           fill=C["ivory"], anchor="rm")
    c.text((px1 - 330, (py0 + py1) / 2 + 30), p["number2_label2"], font("messiri", 28, 500),
           fill=C["gold_lt"], anchor="rm")
    c.text((540, 1080), p["line"], font("messiri", 32, 600), fill=C["muted"], anchor="mm")
    c.footer(dark=False, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 3 chat mock-up
def bubble(c, x_side, y, lines, me, maxw=360):
    f = font("almarai-bold", 25)
    lh = 36
    wmax = max(measure(t, f)[0] for t in lines)
    bw = min(maxw, wmax) + 48
    bh = lh * len(lines) + 30
    if me:   # academy (left, white)
        x0 = x_side
        box = [x0, y, x0 + bw, y + bh]
        c.shape("round", box, fill="#FFFFFF", radius=22, shadow=dict(offset=(0, 4), blur=8, alpha=25))
        tx = x0 + bw - 24
    else:    # student (right, light green)
        x1 = x_side
        box = [x1 - bw, y, x1, y + bh]
        c.shape("round", box, fill="#D9FDD3", radius=22, shadow=dict(offset=(0, 4), blur=8, alpha=25))
        tx = x1 - 24
    for i, t in enumerate(lines):
        c.text((tx, y + 18 + i * lh), t, f, fill=C["ink"], anchor="ra")
    return y + bh


def chat_mock(p):
    c = Canvas(C["emerald"])
    c.gradient_bg([C["forest"], C["emerald"], C["deep"]], angle=120)
    c.girih(alpha=22, cell=160)
    c.lockup(W - 66, 95, size=92, dark=True)
    gold_text(c, (W - 66, 170), p["title1"], font("ruqaa", 82))
    c.text((W - 66, 290), p["title2"], font("messiri", 38, 600), fill=C["ivory"], anchor="ra")

    # phone
    fx0, fy0, fx1, fy1 = 300, 370, 780, 1150
    c.shape("round", [fx0, fy0, fx1, fy1], fill="#0E1512", radius=56,
            shadow=dict(offset=(0, 24), blur=40, alpha=140, color="#000000"))
    c.shape("round", [fx0, fy0, fx1, fy1], outline=GOLD, width=3, radius=56)
    sx0, sy0, sx1, sy1 = fx0 + 16, fy0 + 16, fx1 - 16, fy1 - 16
    c.shape("round", [sx0, sy0, sx1, sy1], fill="#EFE7DC", radius=42)
    c.girih(alpha=18, cell=70, color="#8C7A5A", box=(sx0, sy0 + 100, sx1, sy1 - 20))
    # header bar
    c.shape("round", [sx0, sy0, sx1, sy0 + 100], fill="#0F5236", radius=42)
    c.shape("rect", [sx0, sy0 + 50, sx1, sy0 + 100], fill="#0F5236")
    c.logo(sx1 - 50, sy0 + 54, 50, shadow=False)
    c.text((sx1 - 86, sy0 + 40), "أكاديمية العلماء العرب", font("messiri", 25, 700), fill="#FFFFFF", anchor="rm")
    c.text((sx1 - 86, sy0 + 74), "متصل الآن", font("almarai", 19), fill="#BFE3CC", anchor="rm")
    c.shape("round", [(fx0 + fx1) / 2 - 50, fy0 + 24, (fx0 + fx1) / 2 + 50, fy0 + 36], fill="#0E1512", radius=6)

    y = sy0 + 130
    for who, lines in p["chat"]:
        if who == "student":
            y = bubble(c, sx1 - 18, y, lines, me=False) + 16
        else:
            y = bubble(c, sx0 + 18, y, lines, me=True) + 16

    # side tags
    for i, t in enumerate(p["tags"]):
        ty = 520 + i * 190
        side_r = i % 2 == 0
        f = font("messiri", 26, 700)
        tw, _ = measure(t, f)
        if side_r:
            box = [fx1 + 14, ty, min(fx1 + 14 + tw + 56, W - 20), ty + 64]
        else:
            box = [max(fx0 - 14 - tw - 56, 20), ty, fx0 - 14, ty + 64]
        c.shape("round", box, gradient=GOLD_SOFT, angle=0, radius=32,
                shadow=dict(offset=(0, 8), blur=14, alpha=90, color="#000000"))
        c.text(((box[0] + box[2]) / 2, ty + 32), t, f, fill=C["deep"], anchor="mm")

    c.footer(y=1262, dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 4 myth vs fact
def myth_fact(p):
    c = Canvas(C["ivory"])
    c.gradient_bg([C["ivory"], C["cream"]], angle=90)
    c.paper_noise(4)
    c.lockup(W - 70, 100, size=96)
    c.text((540, 210), p["kicker"], font("messiri", 36, 700), fill=C["gold_dk"], anchor="mm")

    # myth card (tilted look via offset shadow)
    mx0, my0, mx1, my1 = 90, 270, 990, 590
    c.shape("round", [mx0, my0, mx1, my1], fill="#FBEDEA", radius=36,
            shadow=dict(offset=(0, 12), blur=22, alpha=40))
    c.shape("round", [mx0, my0, mx1, my1], outline=C["red"], width=2.5, radius=36)
    c.shape("round", [mx1 - 230, my0 - 30, mx1 - 40, my0 + 30], fill=C["red"], radius=30)
    c.text((mx1 - 135, my0), "خرافة", font("messiri", 32, 700), fill="#FFFFFF", anchor="mm")
    c.shape("ellipse", [mx0 + 50, my0 + 70, mx0 + 170, my0 + 190], fill=C["red"])
    c.text((mx0 + 110, my0 + 130), "✕", font("latin", 62), fill="#FFFFFF", anchor="mm")
    y = my0 + 95
    for t in p["myth"]:
        c.text((mx1 - 50, y), t, font("messiri", 40, 700), fill="#5A1E1E", anchor="ra")
        y += 64
    # strike line across myth
    c.shape("rect", [mx0 + 200, my0 + 140, mx1 - 50, my0 + 146], fill=(178, 58, 58, 150))

    # arrow
    c.shape("poly", [(540 - 34, 612), (540 + 34, 612), (540, 662)], gradient=GOLD_SOFT, angle=90)

    # fact card
    fx0, fy0, fx1, fy1 = 70, 690, 1010, 1130
    c.shape("round", [fx0, fy0, fx1, fy1], gradient=[C["emerald"], C["deep"]], angle=120, radius=40,
            shadow=dict(offset=(0, 18), blur=30, alpha=80))
    c.girih(alpha=24, cell=120, box=(fx0, fy0, fx1, fy1))
    c.gold_frame([fx0, fy0, fx1, fy1], radius=40, inset=12)
    c.shape("round", [fx1 - 250, fy0 - 32, fx1 - 50, fy0 + 32], gradient=GOLD_SOFT, angle=0, radius=32)
    c.text((fx1 - 150, fy0), "الحقيقة", font("messiri", 34, 700), fill=C["deep"], anchor="mm")
    gold_text(c, (fx1 - 60, fy0 + 62), p["fact_title"], font("messiri", 48, 800), shadow=False)
    y = fy0 + 168
    for t in p["fact"]:
        bullet_row(c, fx1 - 60, y, t, font("messiri", 33, 600), C["ivory"])
        y += 57
    # Q badges row
    qx = fx0 + 60
    fq = font("serif", 28)
    for q in p.get("badges", []):
        bw = max(86, measure(q, fq)[0] + 36)
        c.shape("round", [qx, fy1 - 110, qx + bw, fy1 - 50], gradient=GOLD_SOFT, angle=90, radius=14)
        c.text((qx + bw / 2, fy1 - 80), q, fq, fill=C["deep"], anchor="mm")
        qx += bw + 14
    c.footer(y=1262, dark=False, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 5 checklist on paper
def checklist_paper(p):
    c = Canvas(C["deep"])
    c.gradient_bg(["#0D3B27", C["deep"], C["night"]], angle=60)
    c.girih(alpha=16, cell=200)
    c.lockup(W - 66, 95, size=92, dark=True)
    gold_text(c, (W - 66, 165), p["title1"], font("ruqaa", 66))

    # paper sheet with clip, slight perspective via polygon
    pts = [(150, 330), (950, 300), (975, 1135), (125, 1150)]
    c.shape("poly", pts, gradient=[C["ivory"], C["cream"], C["sand"]], angle=90,
            shadow=dict(offset=(10, 26), blur=34, alpha=150, color="#000000"))
    # ruled lines
    for i in range(12):
        yy = 470 + i * 56
        c.line([(175, yy + 8 - i * 0.2), (935, yy - 22 + i * 0.6)], "#E2D6BD", 1.6)
    c.shape("rect", [215, 330, 219, 1140], fill=(178, 58, 58, 120))
    # clip
    c.shape("round", [470, 270, 630, 350], gradient=GOLD, angle=0, radius=18,
            shadow=dict(offset=(0, 6), blur=10, alpha=90, color="#000000"))
    c.shape("round", [505, 290, 595, 318], fill=C["deep"], radius=10)

    c.text((900, 395), p["sheet_title"], font("messiri", 42, 700), fill=C["forest"], anchor="ra")
    y = 495
    for i, t in enumerate(p["items"]):
        yy = y + i * 98
        bx = 900
        c.shape("round", [bx - 46, yy - 23, bx, yy + 23], outline=C["forest"], width=3, radius=8)
        c.text((bx - 21, yy - 2), "✓", font("latin", 40), fill=C["red"], anchor="mm")
        c.text((bx - 70, yy), t, font("naskh", 38, 700), fill=C["ink"], anchor="rm")
    # stamp
    sx, sy = 290, 1020
    c.shape("ellipse", [sx - 95, sy - 95, sx + 95, sy + 95], outline=C["red"], width=5)
    c.shape("ellipse", [sx - 80, sy - 80, sx + 80, sy + 80], outline=C["red"], width=2)
    c.text((sx, sy - 14), p["stamp1"], font("messiri", 30, 700), fill=C["red"], anchor="mm")
    c.text((sx, sy + 26), p["stamp2"], font("messiri", 24, 600), fill=C["red"], anchor="mm")
    c.footer(y=1262, dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 6 analysis dashboard
def gauge(c, cx, cy, r, frac, label):
    steps = 60
    for i in range(steps):
        a0 = math.pi + math.pi * i / steps
        col = C["gold"] if i / steps <= frac else "#2C5A44"
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + (r - 26) * math.cos(a0), cy + (r - 26) * math.sin(a0)
        c.line([(x0, y0), (x1, y1)], col, 5)
    a = math.pi + math.pi * frac
    c.line([(cx, cy), (cx + (r - 40) * math.cos(a), cy + (r - 40) * math.sin(a))], C["ivory"], 6)
    c.shape("ellipse", [cx - 12, cy - 12, cx + 12, cy + 12], gradient=GOLD_SOFT)
    c.text((cx, cy + 40), label, font("messiri", 26, 600), fill=C["gold_lt"], anchor="mm")


def data_dashboard(p):
    c = Canvas(C["night"])
    c.gradient_bg([C["night"], C["deep"], "#0D3B27"], angle=135)
    c.girih(alpha=14, cell=140)
    c.glow(900, 300, 330, C["jade"], 60)
    c.lockup(W - 66, 95, size=92, dark=True)
    c.text((W - 66, 175), p["kicker"], font("messiri", 34, 700), fill=C["gold_lt"], anchor="ra")
    c.text((W - 66, 225), p["title1"], font("kufi", 70, 800), fill=C["ivory"], anchor="ra")
    gold_text(c, (W - 66, 320), p["title2"], font("kufi", 70, 800), shadow=False)

    # dashboard panel
    x0, y0, x1, y1 = 70, 450, 1010, 960
    c.shape("round", [x0, y0, x1, y1], fill=(255, 255, 255, 18), radius=34,
            shadow=dict(offset=(0, 20), blur=34, alpha=120, color="#000000"))
    c.shape("round", [x0, y0, x1, y1], outline=GOLD, width=2, radius=34)
    # left: gauge, right: bars
    gauge(c, 270, 640, 150, 0.78, p["gauge_label"])
    bx0, by1 = 520, 900
    vals = [0.42, 0.58, 0.5, 0.74, 0.66, 0.9]
    for i, v in enumerate(vals):
        bx = bx0 + i * 76
        c.shape("round", [bx, by1 - 330 * v, bx + 46, by1], gradient=[C["gold_lt"], C["gold"], C["gold_dk"]],
                angle=90, radius=10)
    c.shape("rect", [bx0 - 20, by1, x1 - 40, by1 + 3], fill=C["gold"])
    c.text((x1 - 50, y0 + 40), p["panel_title"], font("messiri", 28, 700), fill=C["ivory"], anchor="ra")
    # r value chip
    c.shape("round", [110, 850, 430, 920], gradient=[C["red"], "#8E2B2B"], angle=0, radius=35)
    c.text((270, 885), p["chip"], font("messiri", 28, 700), fill="#FFFFFF", anchor="mm")

    y = 1010
    row = [t for t in p["bullets"]]
    # three pills in a row
    f = font("messiri", 28, 700)
    widths = [measure(t, f)[0] + 70 for t in row]
    total = sum(widths) + 20 * (len(row) - 1)
    xr = (W + total) / 2
    for t, w in zip(row, widths):
        c.shape("round", [xr - w, y - 32, xr, y + 32], fill=(255, 255, 255, 22), radius=32,
                outline=C["gold"], width=1.6)
        c.text((xr - w / 2, y), t, f, fill=C["ivory"], anchor="mm")
        xr -= w + 20
    c.footer(y=1262, dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ 7 before / after
def before_after(p):
    c = Canvas(C["ivory"])
    # diagonal split: left/top "before" muted, right/bottom "after" emerald
    c.gradient_bg([C["cream"], C["sand"]], angle=90)
    c.shape("poly", [(0, 760), (W, 520), (W, H), (0, H)], gradient=[C["emerald"], C["deep"]], angle=90)
    c.girih(alpha=22, cell=150, box=(0, 520, W, H))
    c.shape("poly", [(0, 754), (W, 514), (W, 526), (0, 766)], gradient=GOLD, angle=0)
    c.lockup(W - 66, 95, size=92)
    c.text((W - 66, 168), p["title1"], font("ruqaa", 64), fill=C["forest"], anchor="ra")

    # BEFORE doc (left top)
    def doc(x0, y0, w, h, rot_shadow, messy):
        c.shape("round", [x0, y0, x0 + w, y0 + h], fill="#FFFFFF", radius=16,
                shadow=dict(offset=(rot_shadow, 14), blur=18, alpha=70, color="#000000"))
        for i in range(9):
            yy = y0 + 56 + i * 34
            ww = w - 70 - (i % 3) * 40
            c.shape("round", [x0 + w - 35 - ww, yy, x0 + w - 35, yy + 10], fill="#E3DCCF", radius=5)
            if messy and i in (1, 3, 4, 7):
                c.line([(x0 + w - 35 - ww * 0.8, yy + 14), (x0 + w - 35 - ww * 0.3, yy + 18)], C["red"], 3)
        return x0, y0

    doc(110, 300, 360, 340, -8, True)
    c.text((290, 290), p["before_label"], font("messiri", 34, 700), fill=C["red"], anchor="mm")
    y = 340
    for t in p["before"]:
        c.text((W - 80, y), t, font("messiri", 32, 600), fill="#7A3B33", anchor="ra")
        c.shape("ellipse", [W - 64, y + 12, W - 50, y + 26], fill=C["red"])
        y += 60

    doc(610, 640, 360, 380, 8, False)
    c.shape("ellipse", [880, 600, 990, 710], gradient=GOLD_SOFT,
            shadow=dict(offset=(0, 8), blur=12, alpha=90, color="#000000"))
    c.text((935, 655), "✓", font("latin", 58), fill=C["deep"], anchor="mm")
    c.text((790, 1050), p["after_label"], font("messiri", 34, 700), fill=C["gold_lt"], anchor="mm")
    y = 820
    for t in p["after"]:
        bullet_row(c, 560, y, t, font("messiri", 32, 600), C["ivory"])
        y += 62
    c.footer(y=1262, dark=True, cta=p["cta"])
    return c


TEMPLATES = {
    "arch_hero": arch_hero,
    "stat_hero": stat_hero,
    "chat_mock": chat_mock,
    "myth_fact": myth_fact,
    "checklist_paper": checklist_paper,
    "data_dashboard": data_dashboard,
    "before_after": before_after,
}


# ====================================================================== photo templates
# Owner (26 Oct 2026): use real-looking people (young men only), clear Cairo type.

def stack(c, x_right, y, lines, f, colors, gap=1.08, maxw=None):
    """Right-aligned stacked headline; returns y after the block. Shrinks to fit maxw."""
    if maxw:
        size = f.size / 2
        while size > 30 and max(measure(t, font("cairo", size, 900))[0] for t in lines) > maxw:
            size -= 2
        f = font("cairo", size, 900)
    asc = f.getmetrics()[0] / 2
    for i, t in enumerate(lines):
        col = colors[i % len(colors)]
        if col == "gold_dk":
            gold_text(c, (x_right, y), t, f, dark=True, shadow=False)
        elif col == "gold":
            gold_text(c, (x_right, y), t, f, shadow=True)
        else:
            c.text((x_right, y), t, f, fill=col, anchor="ra")
        y += asc * gap
    return y


def sticker(c, cx, cy, r, big, small, dark=False):
    c.shape("ellipse", [cx - r, cy - r, cx + r, cy + r], gradient=GOLD_SOFT, angle=45,
            shadow=dict(offset=(0, 10), blur=18, alpha=90, color="#04140C"))
    c.shape("ellipse", [cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], outline=C["deep"], width=2)
    c.text((cx, cy - r * 0.18), big, font("cairo", r * 0.62, 900), fill=C["deep"], anchor="mm")
    c.text((cx, cy + r * 0.38), small, font("cairo", r * 0.22, 700), fill=C["deep"], anchor="mm")


# ------------------------------------------------------------------ P1 graduate + arch
def hero_grad(p):
    c = Canvas(C["ivory"])
    c.gradient_bg([C["ivory"], C["cream"], C["sand"]], angle=90)
    c.girih(alpha=34, cell=150, color=C["gold"])
    c.lockup(W - 66, 100, size=96)
    arch = arch_path(60, 330, 520, 1150)
    c.shape("poly", arch_path(46, 316, 534, 1150), gradient=GOLD, angle=20,
            shadow=dict(offset=(0, 18), blur=30, alpha=80))
    c.shape("poly", arch, gradient=[C["emerald"], C["deep"]], angle=90)
    c.girih(alpha=40, cell=110, box=(60, 330, 520, 1150), color=C["gold"])
    c.photo(p["photo"], cx=290, bottom=1150, height=880)
    c.shape("rect", [0, 1150, W, 1156], gradient=GOLD, angle=0)
    sticker(c, 500, 1030, 86, p["sticker_big"], p["sticker_small"])

    xr = W - 64
    c.text((xr, 220), p["kicker"], font("cairo", 32, 700), fill=C["red"], anchor="ra")
    y = stack(c, xr, 270, p["title"], font("cairo", 78, 900), [C["forest"], "gold_dk"], gap=1.12, maxw=W - 64 - 600)
    c.divider(xr - 190, y + 18, 360)
    y += 60
    for t in p["bullets"]:
        bullet_row(c, xr, y + 20, t, font("cairo", 30, 700), C["ink"], gap=40)
        y += 62
    c.footer(y=1262, dark=False, cta=p["cta"])
    return c


# ------------------------------------------------------------------ P2 two graduates + big number
def stats_duo(p):
    c = Canvas(C["deep"])
    c.gradient_bg([C["night"], C["deep"], C["emerald"]], angle=100)
    c.girih(alpha=26, cell=170)
    c.glow(540, 760, 430, C["jade"], 110)
    c.lockup(W - 66, 100, size=96, dark=True)
    c.text((540, 215), p["kicker"], font("cairo", 34, 700), fill=C["gold_lt"], anchor="mm")
    gold_text(c, (540, 310), p["number"], font("cairo", 180, 900), anchor="mm")
    c.text((540, 432), p["number_label"], font("cairo", 44, 800), fill=C["ivory"], anchor="mm")
    c.ring(540, 860, 300, 10, stops=GOLD, angle=45)
    c.photo(p["photo"], cx=540, bottom=1150, height=650)
    c.shape("rect", [0, 1150, W, 1156], gradient=GOLD, angle=0)
    # side chips
    f = font("cairo", 30, 800)
    for (t, x, y, right) in ((p["chip1"], 50, 600, False), (p["chip2"], W - 50, 720, True)):
        tw, _ = measure(t, f)
        box = [x - tw - 56, y - 34, x, y + 34] if right else [x, y - 34, x + tw + 56, y + 34]
        c.shape("round", box, gradient=GOLD_SOFT, angle=0, radius=34,
                shadow=dict(offset=(0, 10), blur=16, alpha=100, color="#000000"))
        c.text(((box[0] + box[2]) / 2, y), t, f, fill=C["deep"], anchor="mm")
    c.footer(y=1262, dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ P3 man with phone + chat
def chat_bubble(c, x_right, y, text, me, f, maxw=520):
    tw, _ = measure(text, f)
    bw = min(maxw, tw) + 48
    bh = 74
    fill = "#FFFFFF" if me else "#D9FDD3"
    c.shape("round", [x_right - bw, y, x_right, y + bh], fill=fill, radius=26,
            shadow=dict(offset=(0, 8), blur=14, alpha=70, color="#000000"))
    tail = [(x_right - 6, y + bh - 20), (x_right + 14, y + bh + 6), (x_right - 30, y + bh - 2)] if not me else \
        [(x_right - bw + 6, y + bh - 20), (x_right - bw - 14, y + bh + 6), (x_right - bw + 30, y + bh - 2)]
    c.shape("poly", tail, fill=fill)
    c.text((x_right - 24, y + bh / 2), text, f, fill=C["ink"], anchor="rm")
    return y + bh + 22


def chat_person(p):
    c = Canvas(C["emerald"])
    c.gradient_bg([C["forest"], C["emerald"], C["deep"]], angle=120)
    c.girih(alpha=24, cell=160)
    c.glow(300, 820, 360, C["jade"], 120)
    c.lockup(W - 66, 100, size=96, dark=True)
    gold_text(c, (W - 66, 185), p["title"], font("cairo", 70, 900))
    c.text((W - 66, 290), p["subtitle"], font("cairo", 36, 700), fill=C["ivory"], anchor="ra")
    c.photo(p["photo"], cx=290, bottom=1150, height=800)
    c.shape("rect", [0, 1150, W, 1156], gradient=GOLD, angle=0)
    f = font("cairo", 29, 700)
    y = 420
    for who, t in p["chat"]:
        if who == "student":
            y = chat_bubble(c, W - 70, y, t, False, f)
        else:
            y = chat_bubble(c, W - 150, y, t, True, f)
    # "online" badge
    bx, by = W - 70, y + 20
    tag = p["tag"]
    tw, _ = measure(tag, font("cairo", 30, 800))
    c.shape("round", [bx - tw - 70, by, bx, by + 66], gradient=GOLD_SOFT, angle=0, radius=33,
             shadow=dict(offset=(0, 8), blur=14, alpha=90, color="#000000"))
    c.text((bx - 35 - tw / 2, by + 33), tag, font("cairo", 30, 800), fill=C["deep"], anchor="mm")
    c.footer(y=1262, dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ P4 researcher + journal badges
def publish_person(p):
    c = Canvas(C["ivory"])
    c.gradient_bg([C["ivory"], C["cream"]], angle=90)
    c.girih(alpha=30, cell=150, color=C["gold"])
    # emerald panel behind the person (right)
    c.shape("round", [590, 330, 1140, 1180], gradient=[C["emerald"], C["deep"]], angle=90, radius=60)
    c.girih(alpha=34, cell=120, box=(590, 330, 1080, 1150), color=C["gold"])
    c.photo(p["photo"], cx=850, bottom=1150, height=790)
    c.shape("rect", [0, 1150, W, 1156], gradient=GOLD, angle=0)
    c.lockup(W - 66, 100, size=96)
    xr = 520
    c.text((xr, 200), p["kicker"], font("cairo", 30, 700), fill=C["red"], anchor="ra")
    y = stack(c, xr, 245, p["title"], font("cairo", 80, 900), [C["forest"], "gold_dk"], gap=1.1, maxw=460)
    y += 30
    fq = font("cairo", 40, 900)
    cols = [p["badges"][i:i + 2] for i in range(0, len(p["badges"]), 2)]
    for row in cols:
        x = xr
        for q in row:
            bw = max(150, measure(q, fq)[0] + 60)
            c.shape("round", [x - bw, y, x, y + 76], gradient=GOLD_SOFT, angle=90, radius=20,
                    shadow=dict(offset=(0, 8), blur=12, alpha=60))
            c.text((x - bw / 2, y + 38), q, fq, fill=C["deep"], anchor="mm")
            x -= bw + 18
        y += 94
    y += 16
    for t in p["bullets"]:
        bullet_row(c, xr, y + 18, t, font("cairo", 27, 700), C["ink"], gap=40)
        y += 54
    c.footer(y=1262, dark=False, cta=p["cta"])
    return c


# ------------------------------------------------------------------ P5 laptop photo in arch + checklist
def laptop_arch(p):
    c = Canvas(C["deep"])
    c.gradient_bg([C["night"], C["deep"], C["emerald"]], angle=80)
    c.girih(alpha=22, cell=170)
    c.lockup(W - 66, 100, size=96, dark=True)
    ax0, ay0, ax1, ay1 = 150, 190, 930, 760
    c.shape("poly", arch_path(ax0 - 12, ay0 - 12, ax1 + 12, ay1 + 12), gradient=GOLD, angle=20,
            shadow=dict(offset=(0, 20), blur=30, alpha=120, color="#000000"))
    c.photo(p["photo"], box=(ax0, ay0, ax1, ay1), mask=("poly", arch_path(ax0, ay0, ax1, ay1)),
            cx=0.5, bottom=0.25, shadow=False)
    gold_text(c, (540, 800), p["title"], font("cairo", 64, 900), anchor="ma")
    gx0, gx1, gy = 70, W - 70, 920
    cw = (gx1 - gx0 - 24) / 2
    f = font("cairo", 31, 800)
    for i, t in enumerate(p["items"]):
        col, row = i % 2, i // 2
        xr = gx1 - col * (cw + 24)
        y0 = gy + row * 104
        c.shape("round", [xr - cw, y0, xr, y0 + 88], fill=C["ivory"], radius=22,
                shadow=dict(offset=(0, 8), blur=12, alpha=90, color="#000000"))
        c.shape("ellipse", [xr - 64, y0 + 20, xr - 16, y0 + 68], gradient=GOLD_SOFT, angle=45)
        c.text((xr - 40, y0 + 45), "✓", font("latin", 28), fill=C["deep"], anchor="mm")
        c.text((xr - 80, y0 + 44), t, f, fill=C["ink"], anchor="rm")
    c.footer(y=1262, dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ P6 analyst photo split
def analyst_split(p):
    c = Canvas(C["night"])
    c.photo(p["photo"], box=(400, 170, W, 1150), cx=0.3, bottom=0.0, shadow=False, fade_left=0.4, fade_top=0.12)
    c.shape("rect", [0, 1150, W, 1156], gradient=GOLD, angle=0)
    c.shape("rect", [0, 1156, W, H], fill=C["night"])
    c.lockup(W - 66, 100, size=96, dark=True)
    xr = 560
    c.shape("round", [xr - 260, 300, xr, 360], fill=(200, 160, 46, 40), outline=C["gold"], width=2, radius=30)
    c.text((xr - 130, 330), p["kicker"], font("cairo", 28, 800), fill=C["gold_lt"], anchor="mm")
    y = stack(c, xr, 395, p["title"], font("cairo", 84, 900), [C["ivory"], "gold"], gap=1.1, maxw=500)
    y += 40
    for t in p["bullets"]:
        bullet_row(c, xr, y + 20, t, font("cairo", 32, 700), C["ivory"], gap=42)
        y += 66
    c.footer(y=1262, dark=True, cta=p["cta"])
    return c


# ------------------------------------------------------------------ P7 before / after with person
def before_after_person(p):
    c = Canvas(C["ivory"])
    # right half: before (warm/red), left half: after (emerald)
    c.gradient_bg([C["ivory"], C["cream"]], angle=90)
    c.shape("rect", [540, 250, W, 1150], gradient=["#FBEDEA", "#F3D9D5"], angle=90)
    c.shape("rect", [0, 250, 540, 1150], gradient=[C["emerald"], C["deep"]], angle=90)
    c.girih(alpha=30, cell=130, box=(0, 250, 540, 1150))
    c.shape("rect", [536, 250, 544, 1150], gradient=GOLD, angle=90)
    c.shape("rect", [0, 244, W, 250], gradient=GOLD, angle=0)
    c.lockup(W - 66, 90, size=86)
    c.text((60, 125), p["title"], font("cairo", 56, 900), fill=C["forest"], anchor="lm")
    # BEFORE
    c.shape("round", [W - 230, 268, W - 66, 328], fill=C["red"], radius=30)
    c.text((W - 148, 298), p["before_label"], font("cairo", 32, 900), fill="#FFFFFF", anchor="mm")
    y = 360
    for t in p["before"]:
        c.shape("ellipse", [W - 100, y + 4, W - 66, y + 38], fill=C["red"])
        c.text((W - 83, y + 21), "✕", font("latin", 18), fill="#FFFFFF", anchor="mm")
        c.text((W - 112, y + 21), t, font("cairo", 28, 700), fill="#5A1E1E", anchor="rm")
        y += 56
    c.photo(p["photo"], cx=820, bottom=1150, height=600)
    # AFTER
    c.shape("round", [374, 268, 500, 328], gradient=GOLD_SOFT, angle=0, radius=30)
    c.text((437, 298), p["after_label"], font("cairo", 32, 900), fill=C["deep"], anchor="mm")
    # clean document
    dx0, dy0, dx1, dy1 = 120, 640, 420, 1040
    c.shape("round", [dx0, dy0, dx1, dy1], fill="#FFFFFF", radius=16,
            shadow=dict(offset=(0, 14), blur=20, alpha=110, color="#000000"))
    c.shape("round", [dx0 + 30, dy0 + 30, dx1 - 30, dy0 + 52], fill=C["forest"], radius=8)
    for i in range(9):
        yy = dy0 + 80 + i * 32
        c.shape("round", [dx0 + 30 + (i % 3) * 20, yy, dx1 - 30, yy + 10], fill="#E3DCCF", radius=5)
    c.shape("ellipse", [dx1 - 70, dy1 - 70, dx1 + 30, dy1 + 30], gradient=GOLD_SOFT,
            shadow=dict(offset=(0, 8), blur=12, alpha=90, color="#000000"))
    c.text((dx1 - 20, dy1 - 20), "✓", font("latin", 52), fill=C["deep"], anchor="mm")
    y = 360
    for t in p["after"]:
        c.shape("ellipse", [466, y + 4, 500, y + 38], gradient=GOLD_SOFT)
        c.text((483, y + 21), "✓", font("latin", 18), fill=C["deep"], anchor="mm")
        c.text((454, y + 21), t, font("cairo", 27, 700), fill=C["ivory"], anchor="rm")
        y += 56
    c.shape("rect", [0, 1150, W, 1156], gradient=GOLD, angle=0)
    c.footer(y=1262, dark=False, cta=p["cta"])
    return c


TEMPLATES.update({
    "hero_grad": hero_grad,
    "stats_duo": stats_duo,
    "chat_person": chat_person,
    "publish_person": publish_person,
    "laptop_arch": laptop_arch,
    "analyst_split": analyst_split,
    "before_after_person": before_after_person,
})
