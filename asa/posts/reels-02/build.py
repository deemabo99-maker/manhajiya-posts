"""
أكاديمية العلماء العرب — reel built on photography, not on typography.

    python3 asa/posts/reels-02/build.py
    python3 asa/engine/reel.py asa/posts/reels-02/reel-1.json asa/posts/reels-02/reel-1.mp4

Everything before this set was the same thing underneath: Arabic text sliding
onto a coloured gradient, then sitting perfectly still until the next cut. That
is what made every "new idea" feel like the last one — the script changed, the
medium never did.

So this one changes the medium:
  · a photograph fills the frame in most scenes, and the type sits on it
  · nothing is ever still — every scene drifts (asa/engine/filmic.py)
  · film grain and a vignette over everything, so flat fills stop reading as clip-art
  · four or five words a scene at most; the picture carries the meaning
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

NIGHT, DEEP, EMERALD = "#071C13", "#0B2E1E", "#0F5236"
GOLD, GOLD_LT, IVORY = "#C8A02E", "#EED9A0", "#FBF8F1"

CONTACT = ("\n\n📞 للتواصل والاستفسار:"
           "\n📱 رقم الهاتف: 00962778597330"
           "\n💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778597330"
           "\n📧 البريد الإلكتروني: asaforconsultingandtraining@gmail.com")


def big(text, *, y, size, t, color=IVORY, grad=None, anim="up", dur=0.5):
    e = dict(type="text", text=text, font="cairo", size=size, wght=900,
             x=540, y=y, t=t, dur=dur, anim=anim, dark_bg=True)
    e["gradient" if grad else "color"] = grad or color
    return e


def photo_scene(dur, name, motion, els, tint=None, tint_a=0.26, scrim=0.72,
                scrim_top=0.25, sat=1.0, cut=True):
    """A scene whose background IS the photograph."""
    sc = dict(bg="flat", tint=[NIGHT, NIGHT], dur=dur, motion=motion, elements=[
        dict(type="fullbleed", name=name, tint=tint, tint_a=tint_a, scrim=scrim,
             scrim_top=scrim_top, saturate=sat, behind=DEEP,
             x=540, y=960, t=0.0, dur=0.25, anim="fade"),
    ] + els)
    if cut:
        sc["cut"] = True
    return sc


def main():
    scenes = [
        # the picture does the talking; four words on top of it
        photo_scene(3.0, "laptop.jpg", dict(kind="push", amount=0.10),
                    [big("رسالتك واقفة؟", y=430, size=104, t=0.25, grad="gold", anim="zoom", dur=0.55),
                     big("من شهور", y=580, size=60, t=0.8, color=GOLD_LT, dur=0.4)],
                    tint=EMERALD, tint_a=0.20, scrim=0.80, scrim_top=0.30, cut=False),

        photo_scene(2.3, "stressed.png", dict(kind="float", amount=0.09, angle=0.6),
                    [big("ملاحظات بترجع", y=400, size=86, t=0.1, color=IVORY, anim="up", dur=0.4)],
                    tint=DEEP, tint_a=0.30, scrim=0.62, scrim_top=0.34),

        photo_scene(2.3, "analyst.jpg", dict(kind="pan", amount=0.12, angle=0.0),
                    [big("وتحليل ما ظبط", y=400, size=86, t=0.1, color=IVORY, anim="up", dur=0.4)],
                    tint=EMERALD, tint_a=0.22, scrim=0.60, scrim_top=0.32, sat=0.85),

        photo_scene(2.9, "journal.png", dict(kind="pull", amount=0.14),
                    [big("ابدأ من الصح", y=430, size=112, t=0.1, grad="gold", anim="zoom", dur=0.5),
                     big("ومعك فريق يعرف الطريق", y=600, size=54, t=0.7, color=GOLD_LT, dur=0.4)],
                    tint=DEEP, tint_a=0.34, scrim=0.74, scrim_top=0.30),

        # the only scene that is mostly type — and it still drifts
        dict(bg="flat", tint=[DEEP, EMERALD], dur=5.2, cut=True,
             motion=dict(kind="push", amount=0.05), elements=[
            dict(type="fullbleed", name="laptop.jpg", tint=DEEP, tint_a=0.55,
                 scrim=0.80, scrim_top=0.62, saturate=0.5, behind=DEEP,
                 x=540, y=960, t=0.0, dur=0.25, anim="fade"),
            big("منرافقك في", y=360, size=54, t=0.05, color=GOLD_LT, dur=0.35),
            big("كل مرحلة", y=460, size=92, t=0.2, grad="gold", anim="zoom", dur=0.45),
            dict(type="check", text="العنوان وخطة البحث", size=44, w=820,
                 x=540, y=650, t=0.6, dur=0.4, anim="right"),
            dict(type="check", text="الإطار النظري والمراجع", size=44, w=820,
                 x=540, y=790, t=1.1, dur=0.4, anim="right"),
            dict(type="check", text="الأدوات وجمع البيانات", size=44, w=820,
                 x=540, y=930, t=1.6, dur=0.4, anim="right"),
            dict(type="check", text="التحليل الإحصائي والنتائج", size=44, w=820,
                 x=540, y=1070, t=2.1, dur=0.4, anim="right"),
            dict(type="check", text="التدقيق والمناقشة", size=44, w=820,
                 x=540, y=1210, t=2.6, dur=0.4, anim="right"),
        ]),

        photo_scene(4.4, "twograds.png", dict(kind="pull", amount=0.12),
                    [dict(type="emblem", width=132, x=540, y=250, t=0.1, dur=0.4, anim="pop"),
                     big("أكاديمية العلماء العرب", y=390, size=54, t=0.3, grad="gold", dur=0.4),
                     dict(type="whatsapp", scale=1.05, x=540, y=560, t=0.7, dur=0.45, anim="pop"),
                     big("استشارتك الأولى مجانية", y=720, size=52, t=1.1, color=IVORY, dur=0.35)],
                    tint=DEEP, tint_a=0.26, scrim=0.52, scrim_top=0.46, cut=False),
    ]

    caption = (
        "🎓 رسالتك واقفة من شهور؟ ملاحظات بترجع، وتحليل ما ظبط، ووقت بيمشي.\n\n"
        "أكثر الباحثين ما بيتأخروا لأنهم مش قادرين — بيتأخروا لأنهم بلشوا من مكان غلط، "
        "فكل مرحلة بترجّعهم للي قبلها.\n\n"
        "📚 في أكاديمية العلماء العرب منرافقك في كل مرحلة بالترتيب:\n"
        "✅ العنوان وخطة البحث (Proposal)\n"
        "✅ الإطار النظري والدراسات السابقة بمراجع عربية وأجنبية\n"
        "✅ أدوات الدراسة وتحكيمها وجمع البيانات وتفريغها\n"
        "✅ التحليل الإحصائي وربط النتائج بالفرضيات وتفسيرها\n"
        "✅ التدقيق اللغوي والتنسيق والتحضير ليوم المناقشة\n"
        "✅ النشر العلمي في Scopus Q1 / Q2 / Q3 / Q4 ومجلات Arcif\n\n"
        "📈 أكثر من 5000 عمل بحثي تم الإشراف عليه، وأكثر من 100 باحث متخصص\n"
        "🚀 ابدأ من الصح.. واستشارتك الأولى مجانية" + CONTACT +
        "\n\n#أكاديمية_العلماء_العرب #رسائل_ماجستير #أطروحة_دكتوراه #خطة_البحث "
        "#التحليل_الإحصائي #الدراسات_العليا #البحث_العلمي")

    spec = dict(
        title="الرسائل والأطاريح — بالصورة",
        service="إعداد رسائل الماجستير وأطاريح الدكتوراه",
        format="photography-led: a picture fills the frame and carries the meaning, the type "
               "is four words on top, and every scene drifts under grain and a vignette.",
        mood="resolve", bpm=94, music_seed=31, fadein=0.04,
        grain=3.2, vignette=0.42, crf=24,
        cover_scene=5, cover_t=2.2,
        caption=caption, scenes=scenes)

    p = os.path.join(HERE, "reel-1.json")
    json.dump(spec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {p}  {sum(s['dur'] for s in scenes):.1f}s  {len(scenes)} scenes")


if __name__ == "__main__":
    main()
