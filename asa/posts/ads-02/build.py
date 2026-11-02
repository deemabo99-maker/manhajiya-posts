"""
Write the ad reel for أكاديمية العلماء العرب (ads-02) — walking the arcade.

    python3 asa/posts/ads-02/build.py
    python3 engine/ads.py asa/posts/ads-02/asa-arcade-ad.json

Same idea as this brand's services poster: a colonnade of arched bays, "كل
خدماتنا تحت سقف واحد". Here the viewer walks it — one bay fills the frame at a
time, the camera pushing through each, until the last opens onto the graduate.

المنهجية's ad is a route being travelled; this one is an arcade being walked.
A reel and a poster that share one idea within a brand is identity; two brands
sharing one script is not, and the owner has already caught that once.

All text sits inside y 0-1350 so the 4:5 cut keeps it — see brand/ADS.md.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

NIGHT, DEEP, EMERALD, FOREST = "#071C13", "#0B2E1E", "#0F5236", "#164A2F"
GOLD, GOLD_LT, IVORY, CREAM = "#C8A02E", "#EED9A0", "#FBF8F1", "#F6F0E2"

BAYS = [
    ("الرسائل والأطاريح", "من العنوان حتى المناقشة"),
    ("الإطار والمراجع", "دراسات سابقة ومراجع محكّمة"),
    ("الأدوات وجمع البيانات", "استبانة محكّمة وعيّنة مكتملة"),
    ("التحليل الإحصائي", "نتائج مربوطة بالفرضيات"),
    ("النشر العلمي", "مجلات Scopus ومجلات Arcif"),
]

CONTACT = ("\n\n📞 للتواصل والاستفسار:"
           "\n📱 رقم الهاتف: 00962778597330"
           "\n💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778597330"
           "\n📧 البريد الإلكتروني: asaforconsultingandtraining@gmail.com")


def txt(text, size, y, t, color=IVORY, grad=None, anim="up", dur=0.45, dark=True):
    e = dict(type="text", text=text, font="cairo", size=size, wght=900,
             x=540, y=y, t=t, dur=dur, anim=anim, dark_bg=dark)
    if grad:
        e["gradient"] = grad
    else:
        e["color"] = color
    return e


def main():
    scenes = []

    # 1 — the arcade, seen from outside
    scenes.append(dict(bg="flat", tint=[NIGHT, DEEP], dur=3.2, glow=GOLD,
                       camera=dict(**{"from": 1.35, "to": 1.0, "t0": 0.0, "t1": 2.4}),
                       elements=[
        dict(type="arch", w=680, h=940, x=540, bottom=1880, t=0.1, dur=0.7, anim="fade"),
        txt("كل خدماتنا", 92, 420, 0.25, grad="gold", anim="zoom", dur=0.5),
        txt("تحت سقف واحد", 76, 560, 0.7, color=GOLD_LT, dur=0.4),
        dict(type="emblem", width=118, x=540, y=1120, t=1.2, dur=0.5, anim="pop"),
    ]))

    # 2-6 — walk through it, one bay filling the frame at a time
    for i, (title, sub) in enumerate(BAYS):
        tint = [DEEP, FOREST] if i % 2 == 0 else [NIGHT, EMERALD]
        scenes.append(dict(bg="flat", tint=tint, dur=2.1, cut=True, glow=GOLD,
                           camera=dict(**{"from": 1.22, "to": 1.0, "t0": 0.0, "t1": 1.5}),
                           elements=[
            dict(type="arch", w=760, h=1020, x=540, bottom=1900, t=0.02, dur=0.3, anim="fade"),
            dict(type="star", r=30, x=540, y=430, t=0.08, dur=0.3, anim="pop"),
            txt(f"{i + 1} / {len(BAYS)}", 40, 330, 0.05, color=GOLD, anim="fade", dur=0.25),
            txt(title, 80, 540, 0.18, grad="gold", anim="zoom", dur=0.4),
            txt(sub, 46, 700, 0.5, color=IVORY, dur=0.35),
            dict(type="line", w=320, x=540, y=820, t=0.7, dur=0.3, anim="pop"),
        ]))

    # 7 — the last bay opens onto the graduate
    scenes.append(dict(bg="flat", tint=[DEEP, EMERALD], dur=2.6, cut=True, glow=GOLD,
                       elements=[
        dict(type="arch", w=760, h=1040, x=540, bottom=1930, t=0.02, dur=0.4, anim="fade"),
        txt("وآخر قوس", 72, 400, 0.08, grad="gold", anim="up", dur=0.4),
        txt("اسمه التخرّج", 92, 530, 0.45, color=GOLD_LT, anim="zoom", dur=0.45),
        dict(type="photo", name="grad-man", height=1000, x=540, bottom=1925,
             t=0.6, dur=0.6, anim="up"),
        dict(type="badge", big="+5000", small="عمل بحثي", r=92, x=858, y=1230,
             t=1.4, dur=0.5, anim="pop"),
    ]))

    # 8 — who we are
    scenes.append(dict(bg="flat", tint=[NIGHT, EMERALD], dur=4.2, glow=GOLD, elements=[
        dict(type="emblem", width=150, x=540, y=300, t=0.05, dur=0.4, anim="pop"),
        txt("أكاديمية العلماء العرب", 62, 440, 0.3, grad="gold", dur=0.4),
        txt("للاستشارات والتدريب", 48, 556, 0.5, color=GOLD_LT, dur=0.35),
        dict(type="whatsapp", scale=1.05, x=540, y=730, t=0.85, dur=0.45, anim="pop"),
        txt("استشارتك الأولى مجانية", 58, 900, 1.2, color=IVORY, dur=0.35),
        txt("أكثر من 100 باحث متخصص", 44, 1030, 1.5, color=GOLD_LT, anim="fade", dur=0.4),
        dict(type="arch", w=700, h=760, x=540, bottom=1930, t=0.4, dur=0.6, anim="fade"),
    ]))

    caption = (
        "🏛️ كل خدماتنا تحت سقف واحد.. وكل قوس منها خطوة في رسالتك.\n\n"
        "الباحث اللي بيدوّر على كل خدمة عند حدا مختلف بيدفع مرتين: مرة بالوقت، "
        "ومرة لما تطلع الفصول مش متناسقة مع بعضها.\n\n"
        "📚 في أكاديمية العلماء العرب كل شي في مكان واحد:\n"
        "1️⃣ الرسائل والأطاريح من العنوان حتى المناقشة\n"
        "2️⃣ الإطار النظري والدراسات السابقة بمراجع عربية وأجنبية\n"
        "3️⃣ أدوات الدراسة وتحكيمها وجمع البيانات وتفريغها\n"
        "4️⃣ التحليل الإحصائي وربط النتائج بالفرضيات وتفسيرها\n"
        "5️⃣ النشر العلمي في Scopus Q1 / Q2 / Q3 / Q4 و Arcif\n"
        "6️⃣ التدقيق اللغوي وفحص Turnitin والترجمة المعتمدة والعروض التقديمية\n"
        "7️⃣ دورات تدريبية أونلاين لطلبة الدراسات العليا\n\n"
        "📈 أكثر من 5000 عمل بحثي تم الإشراف عليه، وأكثر من 100 باحث متخصص\n"
        "🎓 وآخر قوس اسمه التخرّج.. واستشارتك الأولى مجانية" + CONTACT +
        "\n\n#أكاديمية_العلماء_العرب #رسائل_ماجستير #أطروحة_دكتوراه #التحليل_الإحصائي "
        "#النشر_العلمي #الدراسات_العليا #البحث_العلمي")

    spec = dict(
        title="إعلان: الأكاديمية — الأروقة",
        service="كل الخدمات — إعلان تعريفي",
        format="walking the arcade: one arched bay fills the frame per cut with the camera "
               "pushing through it, until the last opens onto the graduate.",
        mood="craft", bpm=96, music_seed=23, fadein=0.03,
        cover_scene=6, cover_t=2.0,
        caption=caption, scenes=scenes)

    p = os.path.join(HERE, "asa-arcade-ad.json")
    json.dump(spec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {p}  {sum(s['dur'] for s in scenes):.1f}s  {len(scenes)} scenes")


if __name__ == "__main__":
    main()
