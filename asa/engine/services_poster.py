"""
The all-services poster for أكاديمية العلماء العرب.

    python3 asa/engine/services_poster.py asa/posts/ads-02/asa-services.png

One 1080 x 1350 card listing every service, grouped so a researcher finds their
own problem in it at a glance. Built from the brand kit: emerald and gold,
Cairo, the girih field and the standard footer.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402
from kit import C, GOLD, Canvas, font  # noqa: E402

GROUPS = [
    ("الرسائل والأطاريح", [
        "عناوين مبتكرة وغير مكررة",
        "خطة البحث (Proposal) كاملة",
        "الرسالة من المقدمة للخاتمة",
        "مشاريع تخرج البكالوريوس",
    ]),
    ("الإطار النظري والمراجع", [
        "الدراسات السابقة والتعقيب عليها",
        "مراجع عربية وأجنبية حديثة",
        "تحديد الفجوة البحثية",
    ]),
    ("أدوات الدراسة وجمع البيانات", [
        "تصميم الاستبانة وتحكيمها",
        "الصدق والثبات",
        "التوزيع الإلكتروني ومتابعة العيّنة",
        "المقابلات والتفريغ والترميز",
    ]),
    ("التحليل الإحصائي", [
        "اختيار الاختبار المناسب",
        "اختبار الفرضيات وتفسير النتائج",
        "جداول ورسومات بصيغة APA",
    ]),
    ("النشر العلمي", [
        "النشر في Scopus Q1 / Q2 / Q3 / Q4",
        "مجلات Arcif وأبحاث الترقية",
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
    c.gradient_bg([C["night"], C["deep"], C["emerald"]], 118)
    c.girih(alpha=20)
    c.glow(140, 250, 400, C["gold"], 55)
    c.glow(950, 1150, 400, C["emerald"], 70)

    c.logo(120, 120, 128)
    c.text((952, 86), "أكاديمية العلماء العرب", font("cairo", 44, 900),
           gradient=GOLD, angle=20, anchor="ra")
    c.text((952, 150), "للاستشارات والتدريب", font("cairo", 30, 700),
           fill=C["gold_lt"], anchor="ra")

    c.text((540, 232), "كل خدماتنا في مكان واحد", font("cairo", 50, 900),
           gradient=GOLD, angle=18, anchor="ma")

    # Two columns, right first (RTL); each group lands in whichever column is
    # currently shorter so the two sides finish level.
    col_w, gap = 466, 18
    xs = {0: 1080 - 40 - col_w, 1: 40}
    tops = {0: 318, 1: 318}

    for title, items in GROUPS:
        col = 0 if tops[0] <= tops[1] else 1
        x, y = xs[col], tops[col]
        h = 56 + len(items) * 50 + 14

        c.shape("round", (x, y, x + col_w, y + h), fill="#FFFFFF", opacity=22, radius=22)
        c.shape("round", (x, y, x + col_w, y + h), outline=C["gold"], width=2, radius=22)
        bar_top, bar_h = y + 11, 42
        c.shape("round", (x + 13, bar_top, x + col_w - 13, bar_top + bar_h), gradient=GOLD,
                angle=18, radius=20)
        c.text((x + col_w - 29, bar_top + bar_h / 2), title, font("cairo", 24, 900),
               fill=C["deep"], anchor="rm")

        yy = y + 56 + 12
        for it in items:
            c.diamond(x + col_w - 36, yy + 15, 8, fill=C["gold_lt"])
            c.text((x + col_w - 56, yy + 1), it, font("cairo", 23, 700),
                   fill=C["ivory"], anchor="ra")
            yy += 50
        tops[col] = y + h + gap

    bottom = max(tops.values()) - gap
    assert bottom < 1150, f"cards reach {bottom}px and would hit the footer"

    c.footer(y=1250, dark=True, cta="استشارتك الأولى مجانية.. تواصل معنا")
    c.save(out)
    print("wrote", out, f"(cards end at {bottom}px)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "asa-services.png")
