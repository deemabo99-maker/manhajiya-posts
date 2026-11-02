"""
Write the kinetic-type ad reel for أكاديمية العلماء العرب (ads-02).

    python3 asa/posts/ads-02/build.py
    python3 engine/ads.py asa/posts/ads-02/asa-kinetic-ad.json

The same modern treatment as the المنهجية kinetic ad — flat colour fields, hard
cuts, one oversized line per cut — carried in this brand's emerald and gold.
Everything that must survive the 4:5 placement sits inside y 0-1350; see
brand/ADS.md.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

EMERALD, DEEP, NIGHT = "#0F5236", "#0B2E1E", "#071C13"
GOLD, GOLD_LT, IVORY = "#C8A02E", "#EED9A0", "#FBF8F1"
CREAM = "#F6F0E2"

CONTACT = ("\n\n📞 للتواصل والاستفسار:"
           "\n📱 رقم الهاتف: 00962778597330"
           "\n💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778597330"
           "\n📧 البريد الإلكتروني: asaforconsultingandtraining@gmail.com")


def word(text, size, y, t, color=IVORY, grad=None, anim="pop", dur=0.42, dark=True):
    e = dict(type="text", text=text, font="cairo", size=size, wght=900,
             x=540, y=y, t=t, dur=dur, anim=anim, dark_bg=dark)
    if grad:
        e["gradient"] = grad
    else:
        e["color"] = color
    return e


def beat(tint, dur, els, cut=True):
    sc = dict(bg="flat", tint=tint, dur=dur, elements=els)
    if cut:
        sc["cut"] = True
    return sc


def main():
    scenes = [
        beat([NIGHT, DEEP], 1.6, [
            word("بحثك", 160, 800, 0.05, grad="gold", anim="zoom", dur=0.5),
            word("واقف مكانه؟", 92, 1000, 0.45, anim="up", dur=0.35),
        ], cut=False),
        beat([EMERALD, DEEP], 1.2, [
            word("أسابيع", 88, 560, 0.04, anim="pop", dur=0.3),
            word("بلا تقدّم", 160, 760, 0.16, color=GOLD_LT, anim="slam", dur=0.4),
        ]),
        beat([NIGHT, EMERALD], 1.2, [
            word("ملاحظات", 88, 560, 0.04, anim="pop", dur=0.3),
            word("بترجع", 160, 760, 0.16, color=GOLD_LT, anim="slam", dur=0.4),
        ]),
        beat([EMERALD, DEEP], 1.2, [
            word("وفصل", 88, 560, 0.04, anim="pop", dur=0.3),
            word("بيضيع", 160, 760, 0.16, color=GOLD_LT, anim="slam", dur=0.4),
        ]),
        beat([CREAM, "#E8DFC8"], 1.9, [
            word("بَس", 180, 690, 0.05, color=EMERALD, anim="zoom", dur=0.45, dark=False),
            word("مش لازم تكون لحالك", 70, 910, 0.5, color="#1F2A24", anim="up",
                 dur=0.35, dark=False),
        ]),
        beat([DEEP, EMERALD], 5.8, [
            word("أكثر من ١٠٠ باحث معك", 76, 380, 0.05, grad="gold", anim="up", dur=0.4),
            dict(type="check", text="الرسائل والأطاريح من العنوان للمناقشة", size=42, w=880,
                 x=540, y=560, t=0.5, dur=0.4, anim="right"),
            dict(type="check", text="خطة البحث والإطار النظري", size=42, w=880,
                 x=540, y=695, t=1.0, dur=0.4, anim="right"),
            dict(type="check", text="أدوات الدراسة وتحكيمها وجمع البيانات", size=42, w=880,
                 x=540, y=830, t=1.5, dur=0.4, anim="right"),
            dict(type="check", text="التحليل الإحصائي وتفسير النتائج", size=42, w=880,
                 x=540, y=965, t=2.0, dur=0.4, anim="right"),
            dict(type="check", text="النشر في Scopus Q1 Q2 Q3 Q4 و Arcif", size=42, w=880,
                 x=540, y=1100, t=2.5, dur=0.4, anim="right"),
            dict(type="badge", big="+5000", small="عمل بحثي", r=88, x=540, y=1252,
                 t=3.2, dur=0.5, anim="pop"),
        ], cut=False),
        beat([NIGHT, EMERALD], 4.4, [
            dict(type="emblem", width=150, x=540, y=300, t=0.05, dur=0.4, anim="pop"),
            word("أكاديمية العلماء العرب", 62, 440, 0.3, grad="gold", anim="up", dur=0.4),
            word("طريقك نحو التميّز الأكاديمي", 52, 560, 0.5, color=GOLD_LT, anim="up", dur=0.35),
            dict(type="whatsapp", scale=1.05, x=540, y=740, t=0.85, dur=0.45, anim="pop"),
            word("استشارتك الأولى مجانية", 58, 900, 1.2, color=IVORY, anim="up", dur=0.35),
            dict(type="arch", w=700, h=980, x=540, bottom=1960, t=0.5, dur=0.7, anim="fade"),
            dict(type="photo", name="grad-man", height=980, x=540, bottom=1925,
                 t=0.7, dur=0.6, anim="up"),
        ], cut=False),
    ]

    caption = (
        "📚 بحثك واقف مكانه؟ أسابيع بلا تقدّم، وملاحظات بترجع، وفصل دراسي بيضيع..\n\n"
        "المشكلة نادراً بتكون بقدرتك. بتكون إنك ماشي لحالك بطريق إله خطوات معروفة، "
        "وكل خطوة غلط بتكلّفك شهر.\n\n"
        "🎓 في أكاديمية العلماء العرب أكثر من 100 باحث متخصص معك:\n"
        "✅ إعداد الرسائل والأطاريح من العنوان حتى المناقشة\n"
        "✅ خطة البحث (Proposal) والإطار النظري والدراسات السابقة\n"
        "✅ أدوات الدراسة وتحكيمها وجمع البيانات وتفريغها\n"
        "✅ التحليل الإحصائي وتفسير النتائج وربطها بالفرضيات\n"
        "✅ النشر العلمي في Scopus Q1 / Q2 / Q3 / Q4 و Arcif\n"
        "✅ التدقيق اللغوي وفحص Turnitin والترجمة المعتمدة والعروض التقديمية\n"
        "✅ دورات تدريبية أونلاين لطلبة الدراسات العليا\n\n"
        "📈 أكثر من 5000 عمل بحثي تم الإشراف عليه\n"
        "🚀 ابدأ من البداية الصحيحة.. واستشارتك الأولى مجانية" + CONTACT +
        "\n\n#أكاديمية_العلماء_العرب #رسائل_ماجستير #أطروحة_دكتوراه #التحليل_الإحصائي "
        "#النشر_العلمي #الدراسات_العليا #البحث_العلمي")

    spec = dict(
        title="إعلان: الأكاديمية — كينيتك",
        service="كل الخدمات — إعلان تعريفي",
        format="kinetic type: flat emerald and gold fields, hard cuts on the beat, one "
               "oversized line per cut, then the service list and the CTA.",
        mood="market", bpm=122, music_seed=14, fadein=0.03,
        cover_scene=5, cover_t=3.6,
        caption=caption, scenes=scenes)

    p = os.path.join(HERE, "asa-kinetic-ad.json")
    json.dump(spec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {p}  {sum(s['dur'] for s in scenes):.1f}s  {len(scenes)} scenes")


if __name__ == "__main__":
    main()
