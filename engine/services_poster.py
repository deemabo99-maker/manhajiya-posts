"""
The all-services poster for المنهجية.

    python3 engine/services_poster.py posts/ads-02/manhajiya-services.png

One 1080 x 1350 card listing every service the brand offers, grouped so a
researcher can find their own problem in it at a glance. Built from the brand
kit, so palette, fonts, logo badge and footer match everything else.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402
from kit import C, RING, Canvas, font  # noqa: E402

GROUPS = [
    ("الرسائل والأطاريح", [
        "اقتراح عناوين مبتكرة وغير مكررة",
        "إعداد خطة البحث (Proposal) كاملة",
        "الرسالة كاملة من المقدمة للخاتمة",
        "مشاريع تخرج البكالوريوس",
    ]),
    ("الدعم المنهجي وجمع البيانات", [
        "توزيع الاستبانات عبر Google Forms",
        "بيانات بورصة عمّان المالية يدوياً",
        "المراجع والدراسات السابقة",
        "إعداد أدوات الدراسة وتحكيمها",
    ]),
    ("التحليل الإحصائي والبرمجة", [
        "التحليل الإحصائي وتفسير النتائج",
        "ربط النتائج بالفرضيات",
        "خدمات البرمجة والدعم التقني",
    ]),
    ("النشر العلمي", [
        "النشر في Scopus Q1 / Q2 / Q3 / Q4",
        "مجلات Arcif وأبحاث الترقية",
        "استلال أبحاث النشر من الرسائل",
    ]),
    ("خدمات مساندة", [
        "التدقيق اللغوي والتنسيق",
        "فحص الاقتباس ببرنامج Turnitin",
        "الترجمة المعتمدة والعروض التقديمية",
        "دورات تدريبية أونلاين",
    ]),
]


def main(out):
    c = Canvas()
    c.gradient_bg([C["night"], "#3A1250", C["purple"]], 118)
    c.glow(150, 230, 420, C["magenta"], 90)
    c.glow(950, 1180, 420, C["violet"], 80)
    c.dots(820, 90, 7, 3, color="#FFFFFF", alpha=70)
    c.dots(70, 1250, 7, 3, color="#FFFFFF", alpha=55)

    c.logo(118, 118, 128)
    c.text((952, 92), "المنهجية", font("kufi", 54, 900), fill="#FFFFFF", anchor="ra")
    c.text((952, 168), "للخدمات البحثية والعلمية", font("almarai", 30), fill="#E3D3F0", anchor="ra")

    c.text((540, 246), "كل خدماتنا في مكان واحد", font("kufi", 50, 900),
           gradient=RING, angle=20, anchor="ma")

    # Two columns, right first (RTL). Each group goes into whichever column is
    # currently shorter, so the two sides finish level instead of one running long.
    col_w, gap = 466, 20
    xs = {0: 1080 - 40 - col_w, 1: 40}
    tops = {0: 325, 1: 325}

    for title, items in GROUPS:
        col = 0 if tops[0] <= tops[1] else 1
        x, y = xs[col], tops[col]
        h = 54 + len(items) * 49 + 16

        c.shape("round", (x, y, x + col_w, y + h), fill="#FFFFFF", opacity=28, radius=24)
        c.shape("round", (x, y, x + col_w, y + h), outline="#B583DC", width=2, radius=24)
        c.shape("round", (x + 14, y + 12, x + col_w - 14, y + 12 + 42), gradient=RING,
                angle=20, radius=21)
        c.text((x + col_w - 30, y + 20), title, font("kufi", 26, 900), fill="#FFFFFF", anchor="ra")

        yy = y + 54 + 13
        for it in items:
            c.shape("ellipse", (x + col_w - 42, yy + 9, x + col_w - 28, yy + 23), fill=C["yellow"])
            c.text((x + col_w - 56, yy + 2), it, font("almarai", 24), fill="#F3EAF9", anchor="ra")
            yy += 49
        tops[col] = y + h + gap

    bottom = max(tops.values()) - gap
    assert bottom < 1150, f"cards reach {bottom}px and would hit the footer"
    c.footer(y=1236, dark=True, cta="استشارتك الأولى مجانية.. راسلنا الآن")
    c.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "manhajiya-services.png")
