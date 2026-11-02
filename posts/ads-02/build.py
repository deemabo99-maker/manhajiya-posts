"""
Write the ad reel for المنهجية (ads-02) — the route, travelled.

    python3 posts/ads-02/build.py
    python3 engine/ads.py posts/ads-02/manhajiya-route-ad.json

Same idea as this brand's services poster: المنهجية is the method, the way
through. The reel travels that way. Each stage slides in from the right and is
stamped done, and the counter of stages left ticks down — the viewer watches a
thesis get finished.

The academy's ad is built on a different idea (a book being bound). These two
must never be the same script in two palettes; the owner has already caught
that once.

All text sits inside y 0-1350 so the 4:5 cut keeps it — see brand/ADS.md.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

NIGHT, PLUM, PURPLE, MAGENTA = "#24092F", "#4B1A5E", "#9627C4", "#C2309E"
YELLOW, PAPER = "#FFC21A", "#F5F2F7"

STAGES = [
    ("العنوان والخطة", "عنوان مبتكر وخطة مقبولة"),
    ("الإطار والمراجع", "دراسات سابقة ومراجع"),
    ("الأدوات والبيانات", "استبانات وبورصة عمّان"),
    ("التحليل الإحصائي", "نتائج مربوطة بالفرضيات"),
    ("النشر والتسليم", "Scopus وتدقيق ومناقشة"),
]

CONTACT = ("\n\n📞 للتواصل والاستفسار:"
           "\n📱 رقم الهاتف: 00962778707204"
           "\n💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778707204")


def txt(text, size, y, t, color="#FFFFFF", grad=None, anim="up", dur=0.45,
        fnt="kufi", shadow=True):
    e = dict(type="text", text=text, font=fnt, size=size, wght=900,
             x=540, y=y, t=t, dur=dur, anim=anim, shadow=shadow)
    if grad:
        e["gradient"] = grad
    else:
        e["color"] = color
    return e


def main():
    scenes = []

    # 1 — the road ahead, and how far along you are
    scenes.append(dict(bg="flat", tint=[NIGHT, PLUM], dur=3.0, elements=[
        txt("رسالتك", 128, 470, 0.05, grad="ring", anim="zoom", dur=0.5),
        txt("فيها ٥ محطات", 78, 640, 0.5, color="#E9DCF4", dur=0.4),
        txt("وإنت واقف عند وحدة", 60, 760, 1.0, color=YELLOW, dur=0.4),
        dict(type="ring", r=150, width=16, alpha=70, x=540, y=1060, t=1.4,
             dur=0.5, anim="pop"),
        txt("١", 150, 985, 1.55, grad="ring", anim="pop", dur=0.4),
    ]))

    # 2-6 — travel the route: each stage arrives and is marked done
    for i, (title, sub) in enumerate(STAGES):
        left = len(STAGES) - i - 1
        tint = [PLUM, PURPLE] if i % 2 == 0 else [NIGHT, PLUM]
        els = [
            txt(f"المحطة {['الأولى','الثانية','الثالثة','الرابعة','الخامسة'][i]}",
                44, 330, 0.03, color="#D3BEE6", anim="fade", dur=0.25),
            txt(title, 86, 430, 0.1, grad="ring", anim="right", dur=0.35),
            txt(sub, 46, 570, 0.35, color="#F0E6F8", anim="right", dur=0.3),
        ]
        # the stages already behind you, ticked
        for k in range(i + 1):
            els.append(dict(type="pill", text="✓ " + STAGES[k][0], size=34,
                            fg="#FFFFFF", bg=MAGENTA if k == i else None,
                            outline=None if k == i else "#B07FD0",
                            x=540, y=700 + k * 86, t=0.5 + k * 0.06,
                            dur=0.28, anim="pop" if k == i else "fade"))
        els.append(txt(f"باقي {left}" if left else "خلصت",
                       64, 1180, 1.15, color=YELLOW if left else "#7BE495",
                       anim="pop", dur=0.35))
        scenes.append(dict(bg="flat", tint=tint, dur=2.0, cut=True, elements=els))

    # 7 — the payoff
    scenes.append(dict(bg="flat", tint=[PAPER, "#E6DEEE"], dur=1.9, cut=True, elements=[
        txt("وصلت", 170, 620, 0.05, color=PURPLE, anim="zoom", dur=0.45, shadow=False),
        txt("ومعك فريق كل الطريق", 62, 840, 0.5, color="#1E1A22", dur=0.35,
            fnt="almarai-xb", shadow=False),
    ]))

    # 8 — who we are
    scenes.append(dict(bg="flat", tint=[PLUM, PURPLE], dur=4.2, elements=[
        dict(type="logo", width=150, x=540, y=330, t=0.05, dur=0.4, anim="pop"),
        txt("المنهجية", 92, 520, 0.3, grad="ring", dur=0.4),
        txt("للخدمات البحثية والعلمية", 50, 640, 0.5, color="#E8DCF2", dur=0.35),
        dict(type="whatsapp", scale=1.05, x=540, y=840, t=0.85, dur=0.45, anim="pop"),
        txt("استشارتك الأولى مجانية", 58, 1010, 1.2, color=YELLOW, dur=0.35),
        txt("ماجستير · دكتوراه · بكالوريوس", 44, 1150, 1.5, color="#D8C7E8",
            anim="fade", dur=0.4),
    ]))

    caption = (
        "🎓 رسالتك فيها خمس محطات.. وإنت واقف عند وحدة منهم.\n\n"
        "العنوان والخطة، الإطار والمراجع، الأدوات وجمع البيانات، التحليل الإحصائي، "
        "وبالآخر النشر والتسليم. كل محطة إلها شروطها، وأي خطوة غلط فيها بترجّعك شهر لورا.\n\n"
        "✅ في المنهجية منمشي معك المحطات وحدة وحدة:\n"
        "1️⃣ عنوان مبتكر غير مكرر وخطة بحث مقبولة من المشرف\n"
        "2️⃣ الإطار النظري والدراسات السابقة بمراجع عربية وأجنبية\n"
        "3️⃣ أدوات الدراسة وتحكيمها، وبيانات بورصة عمّان المالية يدوياً\n"
        "4️⃣ التحليل الإحصائي وربط النتائج بالفرضيات وتفسيرها\n"
        "5️⃣ النشر في Scopus Q1 / Q2 / Q3 / Q4 و Arcif، والتدقيق والتنسيق وفحص الاقتباس\n\n"
        "🌍 أونلاين لطلاب الأردن والسعودية والعراق والكويت والإمارات وقطر وعُمان "
        "والبحرين ومصر وليبيا والجزائر\n"
        "🚀 قوللي وين واقف.. ومنكمّل من هناك. واستشارتك الأولى مجانية" + CONTACT +
        "\n\n#المنهجية #رسائل_ماجستير #أطروحة_دكتوراه #التحليل_الإحصائي #خطة_البحث "
        "#النشر_العلمي #الدراسات_العليا")

    spec = dict(
        title="إعلان: المنهجية — الطريق",
        service="كل الخدمات — إعلان تعريفي",
        format="the route travelled: five stations arrive one per cut, each ticked off "
               "as it passes and the remaining count ticking down, then the payoff.",
        music=dict(mood="drive", bpm=118), bpm=118, music_seed=21, fadein=0.03,
        cover=dict(scene=3, t=1.6), cover_scene=3, cover_t=1.6,
        caption=caption, scenes=scenes)

    p = os.path.join(HERE, "manhajiya-route-ad.json")
    json.dump(spec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {p}  {sum(s['dur'] for s in scenes):.1f}s  {len(scenes)} scenes")


if __name__ == "__main__":
    main()
