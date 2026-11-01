"""
Write reel-6: an explained walk-through of preparing a master's thesis or a
PhD dissertation, for أكاديمية العلماء العرب.

    python3 asa/posts/reels-01/build6.py

Unlike reels 1-5 this one is built around the narration rather than around the
music: the voice explains each stage and the picture follows it, so the scene
durations come from the measured length of each spoken line. All narration is
vocalised — espeak-ng mispronounces bare Arabic.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import voice  # noqa: E402

# chosen tone: slightly slow, steady, explaining
TONE = dict(length_scale=1.06, noise_scale=0.55, noise_w=0.65)

CONTACT = (
    "\n\n📞 للتواصل والاستفسار:"
    "\n📱 رقم الهاتف: 00962778597330"
    "\n💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778597330"
    "\n📧 البريد الإلكتروني: asaforconsultingandtraining@gmail.com"
)

STAGES = [
    ("١", "العُنوان", "عنوان مبتكر غير مكرر في تخصصك"),
    ("٢", "خطة البحث", "المشكلة والأهداف والأهمية والمنهج"),
    ("٣", "الإطار النظري", "مبني على دراسات سابقة حقيقية"),
    ("٤", "أدوات الدراسة", "مصمّمة ومحكّمة قبل التوزيع"),
    ("٥", "التحليل والنتائج", "مربوطة بالفرضيات ومفسّرة"),
    ("٦", "المناقشة", "تدقيق وتنسيق وتحضير ليوم العرض"),
]

NARRATION = [
    "رِسَالَتُكَ لَيْسَتْ كِتَابَةً فَقَط.. هِيَ سِتُّ مَرَاحِل.",
    "عُنْوَانٌ مُبْتَكَرٌ غَيْرُ مُكَرَّر.",
    "خُطَّةُ بَحْثٍ وَاضِحَةُ المُشْكِلَةِ وَالأَهْدَاف.",
    "إِطَارٌ نَظَرِيٌّ مِنْ دِرَاسَاتٍ حَقِيقِيَّة.",
    "أَدَوَاتٌ مُحَكَّمَةٌ قَبْلَ التَّوْزِيع.",
    "تَحْلِيلٌ يَرْبِطُ النَّتَائِجَ بِالفَرَضِيَّات.",
    "وَيَوْمُ مُنَاقَشَةٍ بِثِقَةٍ وَاسْتِعْدَاد.",
    "نُرَافِقُكَ فِي كُلِّ مَرْحَلَة.",
    "اِسْتِشَارَتُكَ الأُولَى مَجَّانِيَّة.",
]

CAPTION = (
    "🎓 رسالة الماجستير أو الدكتوراه ليست كتابة فقط.. هي ست مراحل مترابطة، "
    "وأي خلل في واحدة منها يظهر في التي بعدها.\n\n"
    "كثير من الباحثين يبدؤون من منتصف الطريق: يكتبون فصولاً قبل أن يستقر العنوان، "
    "أو يوزّعون أداة لم تُحكّم بعد، فتعود الملاحظات ويعود العمل من جديد.\n\n"
    "📚 في أكاديمية العلماء العرب نرافقك في كل مرحلة بالترتيب:\n"
    "1️⃣ اقتراح عنوان مبتكر غير مكرر في تخصصك\n"
    "2️⃣ إعداد خطة البحث: المشكلة والأهداف والأهمية والمنهج والفرضيات\n"
    "3️⃣ بناء الإطار النظري والدراسات السابقة بمراجع عربية وأجنبية\n"
    "4️⃣ تصميم أدوات الدراسة وتحكيمها قبل توزيعها\n"
    "5️⃣ التحليل الإحصائي وربط النتائج بالفرضيات وتفسيرها\n"
    "6️⃣ التدقيق اللغوي والتنسيق والتحضير ليوم المناقشة\n\n"
    "✅ متابعة وتعديلات مستمرة طوال فترة الرسالة\n"
    "🎯 ابدأ من البداية الصحيحة.. واستشارتك الأولى مجانية" + CONTACT +
    "\n\n#أكاديمية_العلماء_العرب #رسائل_ماجستير #أطروحة_دكتوراه #خطة_البحث "
    "#الدراسات_العليا #البحث_العلمي #الأردن"
)


# What a person reads aloud: the same lines without harakat. Keep both forms
# free of a gendered second person (no أنتَ / أنتِ, no ـكَ / ـكِ, no ـين verbs):
# the ad speaks to men and women alike.
READ = [
    "رسالتك ليست كتابةً فقط.. هي ست مراحل.",
    "عنوانٌ مبتكرٌ غير مكرر.",
    "خطة بحثٍ واضحة المشكلة والأهداف.",
    "إطارٌ نظريٌّ من دراساتٍ حقيقية.",
    "أدواتٌ محكَّمة قبل التوزيع.",
    "تحليلٌ يربط النتائج بالفرضيات.",
    "ويومُ مناقشةٍ بثقةٍ واستعداد.",
    "نرافقك في كل مرحلة.",
    "استشارتك الأولى مجانية.",
]


def dur(text):
    return len(voice.synth(text, **TONE)) / voice.sample_rate()


def head(text, y, size, t, anim="up", dark=True, dur_=0.6):
    e = dict(type="text", text=text, font="cairo", size=size, wght=900,
             x=540, y=y, t=t, dur=dur_, anim=anim, dark_bg=dark)
    e["gradient" if dark else "color"] = "gold" if dark else "#0F5236"
    return e


def line(text, y, size, t, color="#FBF8F1", dark=True, anim="up"):
    return dict(type="text", text=text, font="cairo", size=size, wght=700, color=color,
                x=540, y=y, t=t, dur=0.5, anim=anim, dark_bg=dark)


def main():
    d = [dur(t) for t in NARRATION]
    gap = 0.25
    starts, t = [], 0.45
    for x in d:
        starts.append(t)
        t += x + gap
    total = t + 0.4

    # scene 1 covers narration 0; scene 2 covers 1-6 (the stages); scene 3 covers 7-8
    s1 = starts[1] - 0.25
    s2 = (starts[7] - 0.3) - s1
    s3 = total - s1 - s2

    stage_els = [line("ست مراحل", 330, 54, 0.05)]
    for i, (n, title, desc) in enumerate(STAGES):
        stage_els.append(dict(type="step", n=n, title=title, desc=desc, w=900,
                              x=540, y=520 + i * 170,
                              t=max(0.05, starts[1 + i] - s1 - 0.15), dur=0.5, anim="wipe"))

    spec = dict(
        title="إعداد الرسائل والأطاريح — ست مراحل",
        service="إعداد رسائل الماجستير وأطاريح الدكتوراه من العنوان حتى المناقشة",
        format="an explained walk-through: the voice names each of the six stages and a "
               "numbered card wipes in on it, then the CTA. Scene lengths come from the "
               "measured narration, so picture and voice stay together.",
        mood="resolve", bpm=92, music_seed=4, fadein=0.05, duck=0.18,
        cover_scene=1, cover_t=min(6.0, s2 - 0.3),
        caption=CAPTION,
        vo=[dict(t=round(starts[i], 2), text=NARRATION[i], read=READ[i], **TONE)
            for i in range(len(NARRATION))],
        scenes=[
            dict(bg="night", glow="#C8A02E", dur=round(s1, 2), elements=[
                head("رسالتك", 420, 104, 0.1),
                line("ليست كتابةً فقط", 580, 56, 0.55),
                dict(type="doc", w=420, h=540, marks=0, x=540, y=1150, t=0.95, dur=0.7, anim="zoom"),
            ]),
            dict(bg="emerald", glow="#C8A02E", dur=round(s2, 2), elements=stage_els),
            dict(bg="emerald", glow="#C8A02E", dur=round(s3, 2), elements=[
                dict(type="emblem", width=150, x=540, y=270, t=0.1, dur=0.5, anim="pop"),
                line("أكاديمية العلماء العرب", 400, 46, 0.3),
                head("نرافقك في كل مرحلة", 530, 72, 0.5),
                dict(type="whatsapp", scale=1.0, x=540, y=680, t=0.9, dur=0.5, anim="pop"),
                line("الاستشارة الأولى مجانية", 790, 44, 1.2, color="#EED9A0"),
                dict(type="arch", w=720, h=1000, x=540, bottom=1960, t=0.5, dur=0.8, anim="fade"),
                dict(type="photo", name="grad-man", height=1020, x=540, bottom=1925,
                     t=0.7, dur=0.7, anim="up"),
                dict(type="badge", big="+5000", small="عمل بحثي", r=105, x=870, y=1180,
                     t=1.7, dur=0.6, anim="pop"),
            ]),
        ])

    p = os.path.join(HERE, "reel-6.json")
    json.dump(spec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"reel-6  {total:.1f}s  scenes {s1:.1f} / {s2:.1f} / {s3:.1f}")
    for i, t0 in enumerate(starts):
        print(f"  {t0:5.2f} +{d[i]:4.2f}  {NARRATION[i][:44]}")
    problems = voice.fits(spec["vo"], spec["scenes"])
    print("timing problems:", problems or "none")


if __name__ == "__main__":
    main()
