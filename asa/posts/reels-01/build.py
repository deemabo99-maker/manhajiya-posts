"""
Write the five reel specs for أكاديمية العلماء العرب (set reels-01).

    python3 asa/posts/reels-01/build.py

Five reels, each on its own mood from asa/engine/reel.py MOODS, so no two sound
alike: resolve / insight / pulse / market / craft. Three of the five are about
data collection, which the owner asked to weight heaviest. The tone is
encouraging throughout: every reel names the pain in one breath and spends the
rest showing the way out.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

WA = "00962778597330"
CONTACT = (
    "\n\n📞 للتواصل والاستفسار:"
    f"\n📱 رقم الهاتف: {WA}"
    f"\n💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778597330"
    "\n📧 البريد الإلكتروني: asaforconsultingandtraining@gmail.com"
)


def caption(body, tags):
    return body.rstrip() + CONTACT + "\n\n" + " ".join("#أكاديمية_العلماء_العرب" if i == 0 else t
                                                       for i, t in enumerate(["_"] + tags))


def head(text, y=360, size=92, t=0.15, anim="up", color=None, grad="gold", dark=True, dur=0.6):
    """Headline. The gold gradient reads on emerald and night but washes out on ivory,
    so a headline on a light background is solid emerald instead."""
    e = dict(type="text", text=text, font="cairo", size=size, wght=900,
             x=540, y=y, t=t, dur=dur, anim=anim, dark_bg=dark)
    if color:
        e["color"] = color
    elif dark and grad:
        e["gradient"] = grad
    else:
        e["color"] = "#0F5236"
    return e


def line(text, y, size=52, t=0.6, anim="up", color="#FBF8F1", dark=True, dur=0.5):
    return dict(type="text", text=text, font="cairo", size=size, wght=700, color=color,
                x=540, y=y, t=t, dur=dur, anim=anim, dark_bg=dark)


def cta(bg="emerald", glow="#C8A02E", photo="grad-man", head_text="ابدأ رسالتك بثقة",
        dur=5.0, badge=True):
    """Closing scene: emblem, brand line, a headline, WhatsApp, and a graduate standing
    on the frame edge inside the mihrab arch."""
    els = [
        dict(type="emblem", width=150, x=540, y=270, t=0.1, dur=0.5, anim="pop"),
        line("أكاديمية العلماء العرب", 400, size=46, t=0.3, dark=True),
        head(head_text, y=530, size=78, t=0.5, anim="up"),
        dict(type="whatsapp", scale=1.0, x=540, y=680, t=0.85, dur=0.5, anim="pop"),
        line("الاستشارة الأولى مجانية", 790, size=44, t=1.1, color="#EED9A0"),
        dict(type="arch", w=720, h=1000, x=540, bottom=1960, t=0.5, dur=0.8, anim="fade"),
        dict(type="photo", name=photo, height=1020, x=540, bottom=1925, t=0.7, dur=0.7, anim="up"),
    ]
    if badge:
        els.append(dict(type="badge", big="+5000", small="عمل بحثي", r=105,
                        x=870, y=1180, t=1.5, dur=0.6, anim="pop"))
    return dict(bg=bg, glow=glow, dur=dur, elements=els)


# ---------------------------------------------------------------------------- 1
def reel_thesis():
    """Format: the blank page fills itself, chapter by chapter, up to the defence."""
    chapters = [
        ("الفصل ١", "المقدمة وخطة البحث"),
        ("الفصل ٢", "الإطار النظري والدراسات السابقة"),
        ("الفصل ٣", "منهجية الدراسة وأدواتها"),
        ("الفصل ٤", "التحليل الإحصائي والنتائج"),
        ("الفصل ٥", "المناقشة والتوصيات"),
    ]
    sc = [
        dict(bg="night", glow="#C8A02E", dur=3.6, shake=1.2, elements=[
            head("صفحة بيضاء", y=430, size=104, t=0.1),
            line("وموعد تسليم يقترب", 580, size=56, t=0.5),
            dict(type="doc", w=440, h=560, marks=0, x=540, y=1140, t=0.9, dur=0.7, anim="zoom"),
        ]),
        dict(bg="ivory", glow="#C8A02E", dur=2.2, elements=[
            head("هيك بتبدأ كل رسالة", y=380, size=72, t=0.1, dark=False),
            line("والفرق إنك ما تمشيها لحالك", 500, size=48, t=0.45, color="#1F2A24", dark=False),
            dict(type="doc", w=380, h=480, marks=3, x=540, y=1090, t=0.7, dur=0.6, anim="pop"),
        ]),
        dict(bg="ivory", glow="#C8A02E", dur=6.4, elements=(
            [line("نكتبها معك فصلاً فصلاً", 330, size=58, t=0.1, color="#1F2A24", dark=False)]
            + [dict(type="chapter", tag=tag, text=txt, w=880, x=540, y=560 + i * 160,
                    t=0.5 + i * 0.75, dur=0.55, anim="wipe") for i, (tag, txt) in enumerate(chapters)]
        )),
        dict(bg="emerald", glow="#C8A02E", dur=4.2, elements=[
            dict(type="hardcover", w=560, h=720, title="رسالتك", sub="من العنوان حتى المناقشة",
                 x=540, y=840, t=0.15, dur=0.8, anim="drop", shine=1.3),
            head("وتصير بين إيديك", y=330, size=76, t=1.3),
            dict(type="seal", big="تمّت", small="بنجاح", r=120, x=540, y=1420,
                 t=2.0, dur=0.6, anim="slam"),
        ]),
        cta(head_text="رسالتك ممكنة.. ابدأ اليوم"),
    ]
    body = (
        "🎓 صفحة بيضاء وموعد تسليم يقترب.. هيك بتبدأ كل رسالة، والفرق الوحيد إنك ما تمشيها لحالك.\n\n"
        "الباحث اللي بيتأخر مش أقل قدرة، بس غالباً ما حدا دلّه على الخطوة الجاية في وقتها: "
        "عنوان ينعتمد، خطة تعدي من المشرف، إطار نظري مبني على دراسات حقيقية، ومنهجية تخدم أسئلتك.\n\n"
        "📚 في أكاديمية العلماء العرب نكتبها معك فصلاً فصلاً:\n"
        "1️⃣ اقتراح عناوين مبتكرة وغير مكررة في تخصصك\n"
        "2️⃣ إعداد خطة البحث (Proposal) كاملة ومتماسكة\n"
        "3️⃣ الإطار النظري والدراسات السابقة بمراجع عربية وأجنبية\n"
        "4️⃣ منهجية الدراسة وأدواتها وتحكيمها\n"
        "5️⃣ التحليل الإحصائي وتفسير النتائج وربطها بالفرضيات\n"
        "6️⃣ التدقيق اللغوي والتنسيق والتحضير ليوم المناقشة\n\n"
        "✅ متابعة وتعديلات مستمرة طول فترة الرسالة\n"
        "🚀 رسالتك ممكنة.. واستشارتك الأولى مجانية"
    )
    return dict(
        title="الرسائل والأطاريح — الصفحة البيضاء تتعبّى",
        service="إعداد الرسائل والأطاريح من العنوان حتى المناقشة",
        format="the blank page fills itself: one empty sheet, then five chapter cards wipe in "
               "right-to-left, then a hardcover drops and a seal lands",
        mood="resolve", bpm=96, music_seed=3, fadein=0.05, cover_scene=3, cover_t=3.0,
        caption=caption(body, ["#رسائل_ماجستير", "#أطروحة_دكتوراه", "#خطة_البحث",
                               "#الدراسات_العليا", "#البحث_العلمي", "#الأردن"]),
        scenes=sc)


# ---------------------------------------------------------------------------- 2
def reel_stats():
    """Format: numbers click into place — bars grow, hypotheses resolve, a counter lands."""
    hyp = [("H1", "مقبولة"), ("H2", "مقبولة"), ("H3", "مرفوضة"), ("H4", "مقبولة")]
    sc = [
        dict(bg="night", glow="#C8A02E", dur=3.4, shake=1.3, elements=[
            head("عندك البيانات", y=400, size=96, t=0.1),
            line("بس الأرقام ما بتحكي لحالها", 560, size=54, t=0.5),
            dict(type="bar", text="SPSS", w=820, x=540, y=1120, t=1.0, dur=0.7, anim="wipe"),
        ]),
        dict(bg="ivory", glow="#C8A02E", dur=5.4, elements=[
            line("منحوّلها لنتائج تنقرأ", 330, size=58, t=0.1, color="#1F2A24", dark=False),
            dict(type="bar", text="الصدق والثبات", light=True, w=860, x=540, y=560, t=0.5, dur=0.6, anim="wipe"),
            dict(type="bar", text="التوزيع الطبيعي", light=True, w=860, x=540, y=720, t=1.0, dur=0.6, anim="wipe"),
            dict(type="bar", text="الارتباط والانحدار", light=True, w=860, x=540, y=880, t=1.5, dur=0.6, anim="wipe"),
            dict(type="bar", text="اختبار الفرضيات", light=True, w=860, x=540, y=1040, t=2.0, dur=0.6, anim="wipe"),
            dict(type="scale5", text="درجة الموافقة", mark=4, w=880, x=540, y=1260,
                 t=2.7, dur=0.7, anim="up"),
        ]),
        dict(bg="emerald", glow="#C8A02E", dur=4.8, elements=(
            [line("وكل فرضية بتاخد جوابها", 350, size=56, t=0.1)]
            + [dict(type="check", text=f"{h} — {v}", size=46, w=760, x=540, y=600 + i * 150,
                    t=0.6 + i * 0.6, dur=0.5, anim="pop") for i, (h, v) in enumerate(hyp)]
            + [line("ومعها التفسير.. مش بس الجدول", 1320, size=46, t=3.2, color="#EED9A0")]
        )),
        dict(bg="night", glow="#C8A02E", dur=3.6, elements=[
            line("نتائج اشتغلنا عليها", 420, size=52, t=0.1),
            dict(type="counter", value=5000, prefix="+", size=190, x=540, y=700, t=0.5, dur=1.6, step=50),
            line("عمل بحثي تم الإشراف عليه", 900, size=46, t=2.2, color="#EED9A0"),
            dict(type="stamp", text="نتائج موثوقة", size=56, rot=-10, color="#C8A02E",
                 x=540, y=1180, t=2.6, dur=0.5, anim="slam"),
        ]),
        cta(head_text="خلّي أرقامك تحكي", photo="analyst" if False else "grad-man"),
    ]
    body = (
        "📊 عندك البيانات.. بس الأرقام ما بتحكي لحالها.\n\n"
        "كثير باحثين بيوصلوا لمرحلة التحليل ومعهم ملف كامل، وبعدين بيوقفوا: أي اختبار بناسب؟ "
        "وليش الفرضية انرفضت؟ وكيف بترجم مخرجات SPSS لكلام ينحط في الرسالة ويثبت قدّام اللجنة؟\n\n"
        "📈 في أكاديمية العلماء العرب منحوّل بياناتك لنتائج تنقرأ:\n"
        "✅ حساب الصدق والثبات واختبار التوزيع الطبيعي\n"
        "✅ اختيار الاختبار المناسب لأسئلة دراستك وطبيعة بياناتك\n"
        "✅ الارتباط والانحدار وتحليل التباين واختبار الفرضيات\n"
        "✅ جداول ورسومات جاهزة للرسالة بصيغة APA\n"
        "✅ تفسير كل نتيجة وربطها بالفرضية وبالدراسات السابقة\n"
        "✅ تجهيزك للأسئلة المتوقعة عن التحليل في المناقشة\n\n"
        "🎯 التحليل مش جدول بينحط.. التحليل قصة بتحكيها بياناتك\n"
        "واستشارتك الأولى مجانية"
    )
    return dict(
        title="التحليل الإحصائي — الأرقام بتاخد مكانها",
        service="التحليل الإحصائي وربط النتائج بالفرضيات",
        format="numbers clicking into place: bars wipe in one after another, a Likert scale "
               "settles, four hypotheses resolve, then a counter runs up and a stamp lands",
        mood="insight", bpm=112, music_seed=11, fadein=0.05, cover_scene=1, cover_t=3.4,
        caption=caption(body, ["#التحليل_الإحصائي", "#SPSS", "#اختبار_الفرضيات",
                               "#الدراسات_العليا", "#البحث_العلمي", "#رسائل_ماجستير"]),
        scenes=sc)


# ---------------------------------------------------------------------------- 3
def reel_survey():
    """Format: responses arriving — a counter runs up while check rows pop in."""
    sc = [
        dict(bg="night", glow="#C8A02E", dur=3.4, shake=1.2, elements=[
            head("استبانتك جاهزة", y=400, size=96, t=0.1),
            line("بس مين رح يعبّيها؟", 560, size=56, t=0.5),
            dict(type="photo", name="phone", height=760, x=540, bottom=1880, t=0.9, dur=0.6, anim="up"),
        ]),
        dict(bg="emerald", glow="#C8A02E", dur=5.0, elements=[
            line("منوزّعها ومنتابعها", 330, size=58, t=0.1),
            dict(type="counter", value=400, prefix="", suffix=" استجابة", size=150,
                 x=540, y=640, t=0.5, dur=2.4, step=5),
            line("من العيّنة اللي بتناسب دراستك", 850, size=46, t=2.9, color="#EED9A0"),
            dict(type="check", text="نموذج جوجل مرتّب وسهل التعبئة", size=44, w=820,
                 x=540, y=1060, t=3.2, dur=0.5, anim="pop"),
            dict(type="check", text="توزيع موجّه حسب التخصص والبلد", size=44, w=820,
                 x=540, y=1200, t=3.7, dur=0.5, anim="pop"),
            dict(type="check", text="متابعة يومية لحد ما تكتمل العيّنة", size=44, w=820,
                 x=540, y=1340, t=4.2, dur=0.5, anim="pop"),
        ]),
        dict(bg="ivory", glow="#C8A02E", dur=4.4, elements=[
            head("وبتوصلك نظيفة", y=350, size=74, t=0.1, dark=False),
            line("مفرّغة ومرمّزة وجاهزة للتحليل", 480, size=48, t=0.5, color="#1F2A24", dark=False),
            dict(type="bar", text="Excel / SPSS", light=True, w=820, x=540, y=760, t=1.0, dur=0.7, anim="wipe"),
            dict(type="check", text="بدون استجابات ناقصة أو مكررة", light=True, size=44, w=820,
                 x=540, y=980, t=1.7, dur=0.5, anim="pop"),
            dict(type="check", text="كل فقرة مربوطة بمحورها", light=True, size=44, w=820,
                 x=540, y=1120, t=2.2, dur=0.5, anim="pop"),
            dict(type="stamp", text="جاهزة للتحليل", size=54, rot=-8, color="#0F5236",
                 x=540, y=1340, t=2.9, dur=0.5, anim="slam"),
        ]),
        cta(head_text="عيّنتك تكتمل.. وإنت مرتاح", photo="twograds", badge=False),
    ]
    body = (
        "📱 استبانتك جاهزة.. بس مين رح يعبّيها؟\n\n"
        "هاي أكثر مرحلة بتوقف الباحث: الأداة صارت جاهزة، والمشرف موافق، وبعدها بيضيع أسابيع "
        "وهو بيدوّر على مستجيبين، أو بيجمع استجابات ما بتمثّل مجتمع الدراسة أصلاً فيرجع يعيد التوزيع.\n\n"
        "📥 في أكاديمية العلماء العرب منجمع بياناتك بدلك:\n"
        "✅ تحويل الاستبانة لنموذج جوجل مرتّب وسهل التعبئة\n"
        "✅ توزيع إلكتروني موجّه للعيّنة اللي بتناسب دراستك تخصصاً وبلداً\n"
        "✅ متابعة يومية لحد ما تكتمل العيّنة المطلوبة\n"
        "✅ تفريغ الاستجابات وترميزها على Excel و SPSS\n"
        "✅ تنظيف البيانات من الاستجابات الناقصة والمكررة\n"
        "✅ ربط كل فقرة بمحورها وبأسئلة الدراسة\n\n"
        "🎯 بتستلم بياناتك نظيفة وجاهزة للتحليل.. وتكمّل من هناك\n"
        "واستشارتك الأولى مجانية"
    )
    return dict(
        title="جمع البيانات — الاستبانة الإلكترونية",
        service="جمع البيانات: الاستبانات الإلكترونية وتوزيعها عبر Google Forms",
        format="responses arriving: a phone, then a counter running to 400 responses while "
               "check rows pop in, then the clean file with a 'ready to analyse' stamp",
        mood="pulse", bpm=120, music_seed=5, fadein=0.05, cover_scene=1, cover_t=3.2,
        caption=caption(body, ["#جمع_البيانات", "#الاستبانة", "#Google_Forms",
                               "#عينة_الدراسة", "#الدراسات_العليا", "#البحث_العلمي"]),
        scenes=sc)


# ---------------------------------------------------------------------------- 4
def reel_ase():
    """Format: a trading floor at work — financial rows build into a dataset."""
    sc = [
        dict(bg="night", glow="#C8A02E", dur=3.6, shake=1.4, elements=[
            head("بحثك مالي؟", y=390, size=100, t=0.1),
            line("البيانات هي نصف الشغل", 550, size=56, t=0.5),
            dict(type="bar", text="بورصة عمّان", w=840, x=540, y=1100, t=1.0, dur=0.8, anim="wipe"),
        ]),
        dict(bg="emerald", glow="#C8A02E", dur=5.6, elements=[
            line("منسحبها لإلك شركة شركة", 330, size=56, t=0.1),
            dict(type="check", text="القوائم المالية السنوية", size=46, w=800,
                 x=540, y=580, t=0.5, dur=0.5, anim="right"),
            dict(type="check", text="تقارير مجلس الإدارة والحوكمة", size=46, w=800,
                 x=540, y=720, t=1.0, dur=0.5, anim="right"),
            dict(type="check", text="أسعار الإغلاق وحجم التداول", size=46, w=800,
                 x=540, y=860, t=1.5, dur=0.5, anim="right"),
            dict(type="check", text="أتعاب التدقيق والإفصاح", size=46, w=800,
                 x=540, y=1000, t=2.0, dur=0.5, anim="right"),
            dict(type="counter", value=15, prefix="", suffix=" سنة", size=130,
                 x=540, y=1230, t=2.6, dur=1.5, step=1),
            line("سلاسل زمنية كاملة بدون فجوات", 1400, size=44, t=4.2, color="#EED9A0"),
        ]),
        dict(bg="ivory", glow="#C8A02E", dur=4.2, elements=[
            head("يدوياً.. ومدقّقة", y=350, size=80, t=0.1, dark=False),
            line("لأن خطأ برقم واحد بيقلب نتيجتك", 470, size=46, t=0.5,
                 color="#1F2A24", dark=False),
            dict(type="bar", text="جاهزة على Excel و SPSS", light=True, w=860, x=540, y=760,
                 t=1.0, dur=0.7, anim="wipe"),
            dict(type="scale5", text="دقّة المطابقة", mark=5, w=860, x=540, y=1000,
                 t=1.8, dur=0.7, anim="up"),
            dict(type="stamp", text="مطابقة للمصدر", size=52, rot=-9, color="#0F5236",
                 x=540, y=1270, t=2.5, dur=0.5, anim="slam"),
        ]),
        cta(head_text="بياناتك المالية.. جاهزة"),
    ]
    body = (
        "📉 بحثك مالي أو محاسبي؟ البيانات هي نصف الشغل.\n\n"
        "سحب بيانات الشركات المدرجة من بورصة عمّان مش خطوة وحدة: قوائم مالية بسنوات متفرّقة، "
        "وتقارير حوكمة بصيغ مختلفة، وشركات غيّرت أسماءها أو اندمجت.. وخطأ برقم واحد بيقلب نتيجة الانحدار كلها.\n\n"
        "🏦 في أكاديمية العلماء العرب منسحبها لإلك شركة شركة وسنة سنة:\n"
        "✅ القوائم المالية السنوية للشركات المدرجة\n"
        "✅ تقارير مجلس الإدارة والحوكمة والإفصاح\n"
        "✅ أسعار الإغلاق وحجم التداول والقيمة السوقية\n"
        "✅ أتعاب التدقيق وبيانات مكاتب التدقيق\n"
        "✅ احتساب المتغيرات والنسب المالية اللي بتحتاجها دراستك\n"
        "✅ سلاسل زمنية كاملة بدون فجوات، مطابقة للمصدر ومرتّبة على Excel و SPSS\n\n"
        "🎯 بيانات حقيقية ومدقّقة.. تبني عليها نتيجة تثبت قدّام اللجنة\n"
        "واستشارتك الأولى مجانية"
    )
    return dict(
        title="جمع البيانات — بورصة عمّان",
        service="جمع البيانات: البيانات المالية الحقيقية من بورصة عمّان",
        format="a trading floor at work: the exchange bar, then financial sources sliding in "
               "from the right, a year counter, and an accuracy scale with a 'matches source' stamp",
        mood="market", bpm=104, music_seed=2, fadein=0.05, cover_scene=1, cover_t=4.6,
        caption=caption(body, ["#بورصة_عمان", "#جمع_البيانات", "#البحوث_المالية",
                               "#المحاسبة", "#الدراسات_العليا", "#البحث_العلمي"]),
        scenes=sc)


# ---------------------------------------------------------------------------- 5
def reel_fieldwork():
    """Format: careful hands — interviews and observation coded into a dataset."""
    sc = [
        dict(bg="ivory", glow="#C8A02E", dur=3.6, elements=[
            head("دراستك نوعية؟", y=390, size=96, t=0.1, dark=False),
            line("المقابلات أصعب من الاستبانة بكثير", 540, size=50, t=0.5,
                 color="#1F2A24", dark=False),
            dict(type="note", text="٢٠ مقابلة.. وكل وحدة ساعة", w=820, x=540, y=1080,
                 t=1.0, dur=0.6, anim="pop"),
        ]),
        dict(bg="night", glow="#C8A02E", dur=5.2, elements=[
            line("منمشيها معك خطوة خطوة", 330, size=56, t=0.1),
            dict(type="step", n=1, title="دليل المقابلة", desc="أسئلة مفتوحة مبنية على أهدافك",
                 w=880, x=540, y=600, t=0.5, dur=0.55, anim="wipe"),
            dict(type="step", n=2, title="بطاقة الملاحظة", desc="مؤشرات واضحة قابلة للرصد",
                 w=880, x=540, y=790, t=1.2, dur=0.55, anim="wipe"),
            dict(type="step", n=3, title="التفريغ الحرفي", desc="كل مقابلة مكتوبة كلمة بكلمة",
                 w=880, x=540, y=980, t=1.9, dur=0.55, anim="wipe"),
            dict(type="step", n=4, title="الترميز والمحاور", desc="استخراج الأنماط والثيمات",
                 w=880, x=540, y=1170, t=2.6, dur=0.55, anim="wipe"),
            dict(type="step", n=5, title="الصدق والتثليث", desc="مراجعة المحكّمين وتوثيق الأدلة",
                 w=880, x=540, y=1360, t=3.3, dur=0.55, anim="wipe"),
        ]),
        dict(bg="emerald", glow="#C8A02E", dur=4.4, elements=[
            head("وبتطلع بنتائج محكية", y=360, size=76, t=0.1),
            dict(type="quote", text="كل نتيجة مسنودة باقتباس من كلام المبحوثين", size=46,
                 x=540, y=720, t=0.6, dur=0.7, anim="up"),
            dict(type="check", text="مصفوفة الثيمات جاهزة للرسالة", size=44, w=820,
                 x=540, y=1050, t=1.6, dur=0.5, anim="pop"),
            dict(type="check", text="توثيق كامل لخطوات الميدان", size=44, w=820,
                 x=540, y=1190, t=2.1, dur=0.5, anim="pop"),
            dict(type="seal", big="موثّقة", small="بالأدلة", r=110, x=540, y=1420,
                 t=2.8, dur=0.6, anim="slam"),
        ]),
        cta(head_text="ميدانك بإيدين تعرف الطريق", photo="twograds", badge=False),
    ]
    body = (
        "🎙️ دراستك نوعية؟ المقابلات أصعب من الاستبانة بكثير.\n\n"
        "عشرين مقابلة، كل وحدة ساعة، وبعدها تفريغ حرفي وترميز واستخراج ثيمات.. "
        "وأكثر ملاحظة بتتكرر من اللجان: النتائج مش مسنودة بأدلة من كلام المبحوثين نفسهم.\n\n"
        "🧭 في أكاديمية العلماء العرب منمشي الميدان معك خطوة خطوة:\n"
        "1️⃣ بناء دليل المقابلة بأسئلة مفتوحة مربوطة بأهداف دراستك\n"
        "2️⃣ إعداد بطاقة الملاحظة بمؤشرات واضحة قابلة للرصد\n"
        "3️⃣ التفريغ الحرفي للمقابلات كلمة بكلمة\n"
        "4️⃣ الترميز واستخراج الأنماط والمحاور وبناء مصفوفة الثيمات\n"
        "5️⃣ التحقق من الصدق عبر التثليث ومراجعة المحكّمين\n"
        "6️⃣ توثيق كامل لخطوات الميدان ينحط في فصل المنهجية\n\n"
        "🎯 كل نتيجة مسنودة بدليل.. وهاد اللي بيثبت قدّام اللجنة\n"
        "واستشارتك الأولى مجانية"
    )
    return dict(
        title="جمع البيانات — المقابلات والميدان",
        service="جمع البيانات: المقابلات والملاحظة والتفريغ والترميز",
        format="careful hands: a note on the scale of the work, five numbered field steps "
               "wiping in, then a quote and an evidence seal",
        mood="craft", bpm=84, music_seed=9, fadein=0.05, cover_scene=1, cover_t=3.9,
        caption=caption(body, ["#جمع_البيانات", "#البحث_النوعي", "#المقابلات",
                               "#تحليل_المحتوى", "#الدراسات_العليا", "#البحث_العلمي"]),
        scenes=sc)


def main():
    reels = [reel_thesis(), reel_stats(), reel_survey(), reel_ase(), reel_fieldwork()]
    for i, r in enumerate(reels, 1):
        p = os.path.join(HERE, f"reel-{i}.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(r, fh, ensure_ascii=False, indent=1)
        total = sum(s["dur"] for s in r["scenes"])
        print(f"reel-{i}  {r['mood']:8s} bpm={r['bpm']:3d}  {total:5.1f}s  {r['title']}")


if __name__ == "__main__":
    main()
