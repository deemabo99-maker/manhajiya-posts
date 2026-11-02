"""
Write the kinetic-type ad reel for المنهجية (ads-02).

    python3 posts/ads-02/build.py
    python3 engine/ads.py posts/ads-02/manhajiya-kinetic-ad.json

A deliberate break from the brand's ornate house style: flat colour fields,
hard cuts on the beat, one oversized line per cut, no decoration. Everything
that must survive sits inside y 0-1350 so the 4:5 cut keeps it — see
brand/ADS.md.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

PURPLE, PLUM, NIGHT = "#9627C4", "#4B1A5E", "#24092F"
MAGENTA, YELLOW, PAPER = "#C2309E", "#FFC21A", "#F5F2F7"

CONTACT = ("\n\n📞 للتواصل والاستفسار:"
           "\n📱 رقم الهاتف: 00962778707204"
           "\n💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778707204")


def word(text, size, y, t, color="#FFFFFF", grad=None, anim="pop", dur=0.42, shadow=True):
    e = dict(type="text", text=text, font="kufi", size=size, wght=900,
             x=540, y=y, t=t, dur=dur, anim=anim, shadow=shadow)
    if grad:
        e["gradient"] = grad
    else:
        e["color"] = color
    return e


def beat(bg, tint, dur, els, cut=True):
    sc = dict(bg=bg, dur=dur, elements=els)
    if tint:
        sc["tint"] = tint
    if cut:
        sc["cut"] = True
    return sc


def main():
    # one claim per cut; the eye reads a single line before the next lands
    scenes = [
        beat("flat", [NIGHT, PLUM], 1.5, [
            word("رسالتك", 150, 820, 0.05, grad="ring", anim="zoom", dur=0.5),
            word("ما بتخلص؟", 96, 1010, 0.45, color="#FFFFFF", anim="up", dur=0.35),
        ], cut=False),
        beat("flat", [PURPLE, MAGENTA], 1.25, [
            word("عنوان", 92, 560, 0.04, anim="pop", dur=0.3),
            word("مرفوض", 170, 760, 0.18, color=YELLOW, anim="slam", dur=0.42),
        ]),
        beat("flat", [NIGHT, PLUM], 1.25, [
            word("خطة", 92, 560, 0.04, anim="pop", dur=0.3),
            word("رجعت", 170, 760, 0.18, color=YELLOW, anim="slam", dur=0.42),
        ]),
        beat("flat", [PURPLE, MAGENTA], 1.25, [
            word("تحليل", 92, 560, 0.04, anim="pop", dur=0.3),
            word("ما ظبط", 170, 760, 0.18, color=YELLOW, anim="slam", dur=0.42),
        ]),
        beat("flat", [PAPER, "#E6DEEE"], 1.9, [
            word("وقّف", 190, 700, 0.05, color=PURPLE, anim="zoom", dur=0.45, shadow=False),
            word("في طريقة أسهل", 78, 920, 0.5, color="#1E1A22", anim="up", dur=0.35, shadow=False),
        ]),
        beat("flat", [PLUM, PURPLE], 5.6, [
            word("منمشيها معك", 86, 400, 0.05, grad="ring", anim="up", dur=0.4),
            dict(type="card", icon="1", title="العنوان والخطة", desc="مبتكرة ومقبولة من المشرف",
                 w=900, x=540, y=610, t=0.5, dur=0.4, anim="right"),
            dict(type="card", icon="2", title="الإطار والدراسات السابقة", desc="مراجع عربية وأجنبية",
                 w=900, x=540, y=800, t=1.1, dur=0.4, anim="right"),
            dict(type="card", icon="3", title="الأدوات وجمع البيانات", desc="استبانات وبورصة عمّان",
                 w=900, x=540, y=990, t=1.7, dur=0.4, anim="right"),
            dict(type="card", icon="4", title="التحليل الإحصائي", desc="نتائج مربوطة بالفرضيات",
                 w=900, x=540, y=1180, t=2.3, dur=0.4, anim="right"),
        ], cut=False),
        beat("flat", [NIGHT, PLUM], 4.2, [
            dict(type="logo", width=150, x=540, y=330, t=0.05, dur=0.4, anim="pop"),
            word("المنهجية", 92, 520, 0.3, grad="ring", anim="up", dur=0.4),
            word("للخدمات البحثية والعلمية", 52, 640, 0.5, color="#E8DCF2", anim="up", dur=0.35),
            dict(type="whatsapp", scale=1.05, x=540, y=840, t=0.85, dur=0.45, anim="pop"),
            word("استشارتك الأولى مجانية", 60, 1010, 1.2, color=YELLOW, anim="up", dur=0.35),
            word("ماجستير · دكتوراه · بكالوريوس", 46, 1150, 1.5, color="#D8C7E8",
                 anim="fade", dur=0.4),
        ], cut=False),
    ]

    caption = (
        "🎓 رسالتك ما بتخلص؟ عنوان مرفوض، وخطة رجعت بالملاحظات، وتحليل ما ظبط..\n\n"
        "أكثر الباحثين ما بيتأخروا لأنهم مش قادرين، بيتأخروا لأن ما حدا دلّهم على الخطوة الصح "
        "بوقتها، فيعيدوا نفس الفصل ثلاث مرات.\n\n"
        "✅ في المنهجية منمشيها معك من أول خطوة:\n"
        "1️⃣ عنوان مبتكر وخطة بحث مقبولة من المشرف\n"
        "2️⃣ الإطار النظري والدراسات السابقة بمراجع عربية وأجنبية\n"
        "3️⃣ أدوات الدراسة وتحكيمها وجمع البيانات، واستخراج بيانات بورصة عمّان المالية\n"
        "4️⃣ التحليل الإحصائي وربط النتائج بالفرضيات وتفسيرها\n"
        "5️⃣ النشر العلمي في Scopus Q1 / Q2 / Q3 / Q4 و Arcif\n"
        "6️⃣ التدقيق اللغوي والتنسيق وفحص Turnitin والتحضير للمناقشة\n\n"
        "🌍 أونلاين لطلاب الأردن والسعودية والعراق والكويت والإمارات وقطر وعُمان والبحرين "
        "ومصر وليبيا والجزائر\n"
        "🚀 ابدأ اليوم.. واستشارتك الأولى مجانية" + CONTACT +
        "\n\n#المنهجية #رسائل_ماجستير #أطروحة_دكتوراه #التحليل_الإحصائي #خطة_البحث "
        "#النشر_العلمي #الدراسات_العليا")

    spec = dict(
        title="إعلان: المنهجية — كينيتك",
        service="كل الخدمات — إعلان تعريفي",
        format="kinetic type: flat colour fields, hard cuts on the beat, one oversized line "
               "per cut, no ornament. A deliberate break from the brand's patterned style.",
        music=dict(mood="drive", bpm=124), bpm=124, music_seed=12, fadein=0.03,
        cover=dict(scene=5, t=3.2), cover_scene=5, cover_t=3.2,
        caption=caption, scenes=scenes)

    p = os.path.join(HERE, "manhajiya-kinetic-ad.json")
    json.dump(spec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {p}  {sum(s['dur'] for s in scenes):.1f}s  {len(scenes)} scenes")


if __name__ == "__main__":
    main()
