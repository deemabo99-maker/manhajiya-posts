"""
أكاديمية العلماء العرب — the thesis journey as one unbroken shot.

    python3 asa/posts/reels-02/build_oneshot.py
    python3 asa/engine/oneshot.py asa/posts/reels-02/oneshot-1.json asa/posts/reels-02/oneshot-1.mp4

No cuts. The world is laid out bottom to top — the stuck night at the bottom,
graduation at the top — and the camera flies up through it in a single take,
holding at each stage and whipping between them. Layers at four depths move at
different speeds, so the picture has real space in it.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

GOLD_LT, IVORY = "#EED9A0", "#FBF8F1"

CONTACT = ("\n\n📞 للتواصل والاستفسار:"
           "\n📱 رقم الهاتف: 00962778597330"
           "\n💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778597330"
           "\n📧 البريد الإلكتروني: asaforconsultingandtraining@gmail.com")


def T(text, *, dy, size, t=0.0, grad=None, color=IVORY, anim="up", dur=0.45, x=540):
    e = dict(type="text", text=text, font="cairo", size=size, wght=900, dark_bg=True,
             x=x, dy=dy, t=t, dur=dur, anim=anim)
    e["gradient" if grad else "color"] = grad or color
    return e


def station(y, hold, travel, *els):
    return dict(y=y, hold=hold, travel=travel, elements=list(els))


def main():
    BEAT = 0.5                      # 120 bpm
    H, TR = 3 * BEAT, 1 * BEAT      # hold 1.5 s, whip 0.5 s: one bar per station
    stations = [
        # 1 — the stuck night. the camera starts here.
        station(8400, 7 * BEAT, TR,     # the hook gets two bars
                T("رسالتك واقفة؟", dy=-330, size=104, t=0.15, grad="gold", anim="zoom", dur=0.55),
                T("من شهور", dy=-190, size=58, t=0.6, color=GOLD_LT),
                dict(type="doc", w=400, h=500, marks=0, x=540, dy=190, t=0.4, dur=0.6, anim="zoom"),
                dict(type="stamp", text="مرفوض", size=64, rot=-12, color="#B23A3A",
                     x=700, dy=120, t=1.1, dur=0.5, anim="slam")),

        # 2
        station(7050, H, TR,
                T("١ · العنوان والخطة", dy=-300, size=52, t=0.05, color=GOLD_LT, anim="fade", dur=0.3),
                T("نبدأ من الصح", dy=-190, size=96, t=0.12, grad="gold", anim="zoom", dur=0.5),
                dict(type="chapter", tag="العنوان", text="مبتكر وغير مكرر في تخصصك", w=860,
                     x=540, dy=30, t=0.45, dur=0.5, anim="wipe"),
                dict(type="chapter", tag="الخطة", text="المشكلة والأهداف والمنهج", w=860,
                     x=540, dy=190, t=0.75, dur=0.5, anim="wipe")),

        # 3
        station(5800, H, TR,
                T("٢ · الإطار والمراجع", dy=-300, size=52, t=0.05, color=GOLD_LT, anim="fade", dur=0.3),
                T("على دراسات حقيقية", dy=-190, size=88, t=0.12, grad="gold", anim="zoom", dur=0.5),
                dict(type="check", text="الدراسات السابقة والتعقيب عليها", size=42, w=860,
                     x=540, dy=20, t=0.45, dur=0.45, anim="right"),
                dict(type="check", text="مراجع عربية وأجنبية محكّمة", size=42, w=860,
                     x=540, dy=160, t=0.7, dur=0.45, anim="right")),

        # 4
        station(4550, H, TR,
                T("٣ · الأدوات والبيانات", dy=-300, size=52, t=0.05, color=GOLD_LT, anim="fade", dur=0.3),
                dict(type="counter", value=400, prefix="", suffix=" استجابة", size=140,
                     x=540, dy=-150, t=0.15, dur=1.0, step=5),
                T("استبانة محكّمة وعيّنة مكتملة", dy=60, size=50, t=0.8, color=IVORY),
                dict(type="bar", text="Excel / SPSS", w=820, x=540, dy=230,
                     t=1.0, dur=0.5, anim="wipe")),

        # 5
        station(3300, H, TR,
                T("٤ · التحليل الإحصائي", dy=-300, size=52, t=0.05, color=GOLD_LT, anim="fade", dur=0.3),
                T("أرقامك تحكي", dy=-190, size=96, t=0.12, grad="gold", anim="zoom", dur=0.5),
                dict(type="bar", text="الصدق والثبات", w=840, x=540, dy=10, t=0.4, dur=0.45, anim="wipe"),
                dict(type="bar", text="اختبار الفرضيات", w=840, x=540, dy=150, t=0.65, dur=0.45, anim="wipe"),
                dict(type="scale5", text="النتيجة", mark=4, w=840, x=540, dy=320, t=0.95, dur=0.5, anim="up")),

        # 6
        station(2050, H, TR,
                T("٥ · النشر العلمي", dy=-300, size=52, t=0.05, color=GOLD_LT, anim="fade", dur=0.3),
                T("Scopus", dy=-180, size=120, t=0.12, grad="gold", anim="zoom", dur=0.5),
                T("Q1 · Q2 · Q3 · Q4 ومجلات Arcif", dy=-40, size=48, t=0.5, color=GOLD_LT),
                dict(type="seal", big="مقبول", small="للنشر", r=120, x=540, dy=250,
                     t=0.85, dur=0.55, anim="slam")),

        # 7 — graduation. the camera ends here and holds.
        station(780, 8 * BEAT, 0.0,     # the ending holds two bars
                dict(type="emblem", width=140, x=540, dy=-560, t=0.05, dur=0.4, anim="pop"),
                T("أكاديمية العلماء العرب", dy=-440, size=56, t=0.25, grad="gold"),
                T("طريقك نحو التميّز الأكاديمي", dy=-350, size=44, t=0.45, color=GOLD_LT),
                dict(type="whatsapp", scale=1.05, x=540, dy=-210, t=0.7, dur=0.45, anim="pop"),
                T("استشارتك الأولى مجانية", dy=-80, size=50, t=1.0, color=IVORY),
                dict(type="arch", w=720, h=980, x=540, dy=560, t=0.2, dur=0.6, anim="fade"),
                dict(type="photo", name="twograds", height=980, x=540, dy=560, t=0.5, dur=0.7, anim="up"),
                dict(type="badge", big="+5000", small="عمل بحثي", r=96, x=880, dy=140,
                     t=1.5, dur=0.5, anim="pop")),
    ]

    caption = (
        "🎓 رسالتك واقفة من شهور؟ مش لأنك مش قادر.. لأن ما حدا مشى الطريق معك.\n\n"
        "الرسالة مش فصول ببعضها، هي طريق إله محطات بالترتيب: العنوان والخطة، "
        "الإطار والمراجع، الأدوات والبيانات، التحليل، والنشر. وأي محطة بتعديها غلط "
        "بترجّعك للي قبلها.\n\n"
        "📚 في أكاديمية العلماء العرب منمشي الطريق كله معك:\n"
        "1️⃣ عنوان مبتكر وخطة بحث (Proposal) مقبولة\n"
        "2️⃣ الإطار النظري والدراسات السابقة بمراجع عربية وأجنبية محكّمة\n"
        "3️⃣ أدوات الدراسة وتحكيمها، وجمع البيانات حتى تكتمل العيّنة\n"
        "4️⃣ التحليل الإحصائي وربط النتائج بالفرضيات وتفسيرها\n"
        "5️⃣ النشر في Scopus Q1 / Q2 / Q3 / Q4 ومجلات Arcif\n"
        "6️⃣ التدقيق والتنسيق والتحضير ليوم المناقشة\n\n"
        "📈 أكثر من 5000 عمل بحثي تم الإشراف عليه، وأكثر من 100 باحث متخصص\n"
        "🚀 وآخر محطة اسمها التخرّج.. واستشارتك الأولى مجانية" + CONTACT +
        "\n\n#أكاديمية_العلماء_العرب #رسائل_ماجستير #أطروحة_دكتوراه #خطة_البحث "
        "#التحليل_الإحصائي #النشر_العلمي #الدراسات_العليا")

    spec = dict(
        title="الطريق للتخرّج — لقطة واحدة",
        service="إعداد رسائل الماجستير وأطاريح الدكتوراه",
        format="one unbroken shot: the camera flies up a tall world from the stuck night to "
               "graduation, holding at each stage and whipping between them, with four "
               "parallax depths, speed-scaled motion blur and a light sweep on arrival.",
        mood="resolve", bpm=120, music_seed=41, world_h=9400, near=True,
        grain=3.0, vignette=0.42, crf=22, cover_station=6, lead=0.5, tail=0.5,
        caption=caption, stations=stations)

    p = os.path.join(HERE, "oneshot-1.json")
    json.dump(spec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total = 0.5 + sum(s["hold"] + s["travel"] for s in stations) + 0.6
    print(f"wrote {p}  ~{total:.1f}s  {len(stations)} stations, no cuts")


if __name__ == "__main__":
    main()
