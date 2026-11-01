"""
Build one artifact page carrying both brands' weekly batch and the Meta ad reels.

    python3 engine/combined_page.py <out-dir>

Reads each brand's content.json, reel-N.json, schedule/captions and ads-01/ad-copy.md,
so no Arabic is ever retyped. Writes <out-dir>/page.html plus <out-dir>/img/* — small
WEBP stills and compressed MP4 previews, published as the artifact's own files, because
the artifact CSP blocks external media and nothing may be hot-linked.
"""
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def webp(src, dst, width):
    run("ffmpeg", "-y", "-loglevel", "error", "-i", src,
        "-vf", f"scale={width}:-2:flags=lanczos", "-quality", "82", dst)


def mp4(src, dst, width=540):
    run("ffmpeg", "-y", "-loglevel", "error", "-i", src,
        "-vf", f"scale={width}:-2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
        "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", dst)


# ---------------------------------------------------------------- brand loading

def manhajiya_times():
    """Publish slots live in captions.md for this brand; pull them out in order."""
    txt = open(os.path.join(ROOT, "posts/batch-02/captions.md"), encoding="utf-8").read()
    return re.findall(r"موعد النشر:\s*(.+?)\s*—\s*(\d{2}:\d{2})", txt)


def load_manhajiya():
    base = os.path.join(ROOT, "posts/batch-02")
    posts = json.load(open(os.path.join(base, "content.json"), encoding="utf-8"))["posts"]
    slots = manhajiya_times()
    items = []
    for i, p in enumerate(posts):
        day, time = slots[i]
        items.append(dict(kind="design", src=f"{base}/{i+1:02d}.png", file=f"{i+1:02d}.png",
                          story_src=f"{base}/story-{i+1:02d}.png", story_file=f"story-{i+1:02d}.png",
                          service=p["service"], template=p.get("template", ""),
                          day=day, time=time, caption=p["caption"].strip()))
    for n in (1, 2):
        r = json.load(open(f"{base}/reel-{n}.json", encoding="utf-8"))
        day, time = slots[2 + n]
        items.append(dict(kind="reel", src=f"{base}/reel-{n}.mp4", file=f"reel-{n}.mp4",
                          cover=f"{base}/reel-{n}-cover.png", service=r.get("service", ""),
                          title=r.get("title", ""), fmt=r.get("format", ""),
                          day=day, time=time, caption=r["caption"].strip()))
    return items


def load_asa():
    base = os.path.join(ROOT, "asa/posts/batch-02")
    posts = json.load(open(os.path.join(base, "content.json"), encoding="utf-8"))["posts"]
    sched = {it["file"]: it for it in json.load(open(f"{base}/schedule.json", encoding="utf-8"))["items"]}
    items = []
    for i, p in enumerate(posts):
        f = f"{i+1:02d}.png"
        s = sched.get(f, {})
        items.append(dict(kind="design", src=f"{base}/{f}", file=f,
                          story_src=f"{base}/story-{i+1:02d}.png", story_file=f"story-{i+1:02d}.png",
                          service=p["service"], template=p.get("template", ""),
                          day=f"{s.get('day','')} {s.get('date','')}", time=s.get("time", ""),
                          caption=p["caption"].strip()))
    for n in (1, 2):
        r = json.load(open(f"{base}/reel-{n}.json", encoding="utf-8"))
        s = sched.get(f"reel-{n}.mp4", {})
        items.append(dict(kind="reel", src=f"{base}/reel-{n}.mp4", file=f"reel-{n}.mp4",
                          cover=f"{base}/reel-{n}-cover.png",
                          service=r.get("service") or r.get("title", ""),
                          title=r.get("title", ""), fmt=r.get("format", ""),
                          day=f"{s.get('day','')} {s.get('date','')}", time=s.get("time", ""),
                          caption=r["caption"].strip()))
    return items


# ------------------------------------------------------------------ ad loading

def load_ad(folder, stem, brand):
    """Pull the idea and the Ads-Manager fields out of ad-copy.md."""
    base = os.path.join(ROOT, folder)
    txt = open(os.path.join(base, "ad-copy.md"), encoding="utf-8").read()

    def block(label):
        m = re.search(r"\*\*" + label + r".*?\*\*:?\s*\n```\n(.*?)\n```", txt, re.S)
        return m.group(1).strip() if m else ""

    def inline(label):
        m = re.search(r"\*\*" + label + r".*?\*\*:?\s*`(.+?)`", txt)
        return m.group(1).strip() if m else ""

    idea = re.search(r"\*\*الفكرة:\*\*\s*(.+)", txt)
    cta = re.search(r"\*\*زر الإجراء \(CTA\):\*\*\s*(.+)", txt)
    return dict(brand=brand, base=base, stem=stem,
                idea=idea.group(1).strip() if idea else "",
                primary=block("النص الأساسي"),
                headline=inline("العنوان \\(Headline\\)"),
                desc=inline("الوصف \\(Description\\)"),
                cta=re.sub(r"`", "", cta.group(1)).strip() if cta else "")


# ------------------------------------------------------------------- rendering

def build_media(items, ads, out):
    img = os.path.join(out, "img")
    os.makedirs(img, exist_ok=True)
    for pre, lst in items:
        for k, it in enumerate(lst):
            tag = f"{pre}-{k:02d}"
            it["w_main"] = f"img/{tag}.webp"
            if it["kind"] == "design":
                webp(it["src"], os.path.join(out, it["w_main"]), 820)
                it["w_story"] = f"img/{tag}-s.webp"
                webp(it["story_src"], os.path.join(out, it["w_story"]), 420)
            else:
                webp(it["cover"], os.path.join(out, it["w_main"]), 440)
                it["w_vid"] = f"img/{tag}.mp4"
                mp4(it["src"], os.path.join(out, it["w_vid"]))
    for a in ads:
        tag = a["stem"]
        a["w_cover"] = f"img/{tag}-cover.webp"
        webp(os.path.join(a["base"], f"{tag}-cover.png"), os.path.join(out, a["w_cover"]), 440)
        for ratio in ("9x16", "4x5"):
            src = os.path.join(a["base"], f"{tag}-{ratio}.mp4")
            if os.path.exists(src):
                a[f"w_{ratio}"] = f"img/{tag}-{ratio}.mp4"
                mp4(src, os.path.join(out, a[f"w_{ratio}"]), 480)


def card(it, idx, pre):
    cid = f"{pre}{idx}"
    cap = html.escape(it["caption"])
    when = f'{html.escape(it["day"])} · {it["time"]}' if it["day"] else it["time"]
    if it["kind"] == "design":
        media = (f'<div class="m-main"><img src="{it["w_main"]}" alt="" loading="lazy"></div>'
                 f'<div class="m-side"><img src="{it["w_story"]}" alt="" loading="lazy">'
                 f'<span class="slab">ستوري</span></div>')
        files = f'<code>{it["file"]}</code><span class="sep">·</span><code class="q">{it["story_file"]}</code>'
        kind, extra = "تصميم", ""
    else:
        media = (f'<div class="m-main reel"><video src="{it["w_vid"]}" poster="{it["w_main"]}" '
                 f'controls preload="none" playsinline></video></div>')
        files = f'<code>{it["file"]}</code>'
        kind = "ريلز"
        extra = f'<p class="fmt">{html.escape(it["fmt"])}</p>' if it.get("fmt") else ""
    return f'''<article class="card" id="{cid}">
  <header class="ch"><div class="when"><strong>{when}</strong></div>
    <span class="bg {'reel' if it['kind']=='reel' else ''}">{kind}</span></header>
  <h3>{html.escape(it["service"] or it.get("title",""))}</h3>
  <div class="files">{files}</div>{extra}
  <div class="grid"><div class="mw">{media}</div>
    <div class="cw"><div class="chd"><span class="cl">الكابشن</span>
      <span class="cn">{len(it["caption"])} حرف</span>
      <button class="cp" data-t="t{cid}">نسخ الكابشن</button></div>
      <pre class="cap" id="t{cid}">{cap}</pre></div></div>
</article>'''


def ad_card(a):
    vids = ""
    for ratio, label, note in (("9x16", "9:16", "ريلز · ستوري · Advantage+"),
                               ("4x5", "4:5", "فيد فيسبوك وإنستغرام")):
        key = f"w_{ratio}"
        if a.get(key):
            vids += (f'<figure class="adv"><video src="{a[key]}" poster="{a["w_cover"]}" controls '
                     f'preload="none" playsinline></video>'
                     f'<figcaption><strong>{label}</strong><span>{note}</span>'
                     f'<code>{a["stem"]}-{ratio}.mp4</code></figcaption></figure>')
    fields = ""
    for label, val, cid in (("النص الأساسي", a["primary"], f'p{a["stem"]}'),):
        if val:
            fields += (f'<div class="fld"><div class="chd"><span class="cl">{label}</span>'
                       f'<button class="cp" data-t="{cid}">نسخ</button></div>'
                       f'<pre class="cap" id="{cid}">{html.escape(val)}</pre></div>')
    rows = ""
    for label, val in (("العنوان (Headline)", a["headline"]), ("الوصف (Description)", a["desc"]),
                       ("زر الإجراء (CTA)", a["cta"])):
        if val:
            rows += f'<div class="row"><span>{label}</span><strong>{html.escape(val)}</strong></div>'
    return f'''<article class="card ad" id="ad-{a["stem"]}">
  <header class="ch"><div class="when"><strong>{html.escape(a["brand"])}</strong></div>
    <span class="bg ad">إعلان ميتا</span></header>
  <h3>الرسائل والأطاريح من العنوان حتى المناقشة</h3>
  <p class="fmt">{html.escape(a["idea"])}</p>
  <div class="advs">{vids}</div>
  <div class="admeta">{fields}<div class="rows">{rows}</div></div>
</article>'''


HEAD = '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>محتوى الأسبوع والإعلانات</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap">
<style>
/* Layout: three tabbed runs of cards — one per brand, one for the Meta ad reels */
:root{
  --bg:#F7F5F0; --surface:#FFFFFF; --line:#E2DDD2; --ink:#1C1A24; --dim:#5F5B6B;
  --purple:#9627C4; --purplesoft:#F3E6FA;
  --emerald:#0F5236; --gold:#A8842A; --goldsoft:#F3E8CB;
  --blue:#1A5FB4; --bluesoft:#E4EDFA;
  --accent:var(--purple); --accentsoft:var(--purplesoft);
  --ff:"Cairo",system-ui,"Segoe UI",sans-serif; color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#13111A; --surface:#1C1926; --line:#302B3D; --ink:#EFECF5; --dim:#A29DB2;
  --purple:#C06AE8; --purplesoft:#2E1E3C; --emerald:#2E8B5E; --gold:#D9B758; --goldsoft:#2C2A1C;
  --blue:#6FA8E8; --bluesoft:#1B2436; color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#13111A; --surface:#1C1926; --line:#302B3D; --ink:#EFECF5; --dim:#A29DB2;
  --purple:#C06AE8; --purplesoft:#2E1E3C; --emerald:#2E8B5E; --gold:#D9B758; --goldsoft:#2C2A1C;
  --blue:#6FA8E8; --bluesoft:#1B2436; color-scheme:dark;}

*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--ff);line-height:1.75;
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 60px}
.wrap{max-width:1060px;margin:0 auto}
img,video{max-width:100%}

header.top{padding-block:32px 0}
.eye{font-size:.76rem;letter-spacing:.14em;font-weight:700;color:var(--dim);margin:0 0 6px}
h1{font-size:clamp(1.5rem,4.2vw,2.15rem);font-weight:900;margin:0;text-wrap:balance}
.lede{margin:10px 0 0;color:var(--dim);max-width:64ch;font-size:.95rem}

.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-block:22px 0;
  border-bottom:1px solid var(--line);padding-bottom:0}
.tab{font-family:var(--ff);font-size:.93rem;font-weight:700;cursor:pointer;background:none;
  border:0;border-bottom:3px solid transparent;color:var(--dim);padding:10px 4px;margin-inline-end:14px}
.tab[aria-selected="true"]{color:var(--accent);border-bottom-color:var(--accent)}
.tab:focus-visible,.cp:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
section.pane[data-brand="m"]{--accent:var(--purple);--accentsoft:var(--purplesoft)}
section.pane[data-brand="a"]{--accent:var(--emerald);--accentsoft:var(--goldsoft)}
section.pane[data-brand="ads"]{--accent:var(--blue);--accentsoft:var(--bluesoft)}

.sum{display:flex;gap:10px;flex-wrap:wrap;margin-block:20px 4px}
.chip{font-size:.82rem;font-weight:700;background:var(--accentsoft);color:var(--accent);
  border-radius:999px;padding:5px 14px}
.note{margin:14px 0 0;padding:13px 15px;background:var(--surface);border:1px solid var(--line);
  border-inline-start:4px solid var(--accent);border-radius:10px;font-size:.9rem;color:var(--dim)}
.note strong{color:var(--ink)}

.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px;
  margin-block:18px;scroll-margin-top:14px}
.ch{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding-bottom:11px;
  border-bottom:1px dashed var(--line)}
.when strong{font-size:.98rem;font-variant-numeric:tabular-nums}
.bg{margin-inline-start:auto;font-size:.73rem;font-weight:700;padding:3px 11px;border-radius:999px;
  background:var(--accentsoft);color:var(--accent)}
.bg.reel,.bg.ad{background:var(--accent);color:#fff}
.card h3{font-size:1.1rem;font-weight:700;margin:13px 0 4px;color:var(--accent);text-wrap:balance}
.files{font-family:ui-monospace,monospace;font-size:.77rem;color:var(--dim)}
.files code{background:var(--accentsoft);color:var(--accent);padding:2px 7px;border-radius:5px}
.files code.q{background:none;color:var(--dim);padding:0}
.sep{margin:0 7px;opacity:.5}
.fmt{margin:8px 0 0;font-size:.85rem;color:var(--dim);max-width:70ch}

.grid{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:20px;
  align-items:start;margin-top:14px}
@media (max-width:760px){.grid{grid-template-columns:minmax(0,1fr)}}
.mw{display:flex;gap:11px;align-items:flex-start;min-width:0}
.m-main{flex:1 1 0;min-width:0}
.m-main.reel{flex:0 0 200px}
.m-side{flex:0 0 84px}
.m-main img,.m-main video,.m-side img{width:100%;display:block;border-radius:9px;border:1px solid var(--line)}
.slab{display:block;text-align:center;font-size:.66rem;color:var(--dim);margin-top:5px}

.cw,.fld{min-width:0}
.chd{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px}
.cl{font-size:.75rem;font-weight:700;letter-spacing:.09em;color:var(--accent)}
.cn{font-size:.73rem;color:var(--dim);font-variant-numeric:tabular-nums}
.cp{margin-inline-start:auto;font-family:var(--ff);font-size:.81rem;font-weight:700;cursor:pointer;
  background:var(--accent);color:#fff;border:0;border-radius:8px;padding:7px 15px}
.cp:hover{filter:brightness(1.12)}
.cp.done{filter:saturate(.6) brightness(.85)}
pre.cap{margin:0;white-space:pre-wrap;word-break:break-word;font-family:var(--ff);font-size:.89rem;
  line-height:1.85;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:14px;
  max-height:420px;overflow:auto;user-select:all}

.advs{display:flex;gap:16px;flex-wrap:wrap;margin-top:16px}
.adv{margin:0;flex:0 0 220px}
.adv video{width:100%;display:block;border-radius:10px;border:1px solid var(--line)}
.adv figcaption{display:flex;flex-direction:column;gap:1px;margin-top:7px;font-size:.78rem;color:var(--dim)}
.adv figcaption strong{color:var(--ink);font-size:.9rem}
.adv figcaption code{font-family:ui-monospace,monospace;font-size:.71rem}
.admeta{margin-top:18px;display:grid;gap:16px}
.rows{display:grid;gap:8px}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:baseline;padding:9px 13px;background:var(--bg);
  border:1px solid var(--line);border-radius:9px;font-size:.88rem}
.row span{color:var(--dim);font-size:.8rem;min-width:9rem}
.row strong{min-width:0}

footer{margin-top:36px;padding-top:18px;border-top:1px solid var(--line);color:var(--dim);font-size:.85rem}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style></head><body><div class="wrap">
'''

SCRIPT = '''
<script>
var tabs = [].slice.call(document.querySelectorAll(".tab"));
function show(name, push){
  tabs.forEach(function(t){
    var on = t.dataset.pane === name;
    t.setAttribute("aria-selected", on ? "true" : "false");
    document.getElementById("pane-" + t.dataset.pane).hidden = !on;
  });
  if (push) { try { history.replaceState(null, "", "#" + name); } catch (e) {} }
}
tabs.forEach(function(t){ t.addEventListener("click", function(){ show(t.dataset.pane, true); }); });
var h = (location.hash || "").replace("#", "");
show(tabs.some(function(t){ return t.dataset.pane === h; }) ? h : tabs[0].dataset.pane, false);

document.querySelectorAll(".cp").forEach(function(b){
  b.addEventListener("click", function(){
    var el = document.getElementById(b.dataset.t), orig = b.textContent;
    function ok(){ b.textContent = "تم النسخ ✓"; b.classList.add("done");
      setTimeout(function(){ b.textContent = orig; b.classList.remove("done"); }, 1800); }
    function sel(){
      var r = document.createRange(); r.selectNodeContents(el);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      b.textContent = "محدّد — Ctrl+C";
      setTimeout(function(){ b.textContent = orig; }, 2600);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(el.textContent).then(ok, sel);
    } else { sel(); }
  });
});
</script></body></html>
'''


def main(out):
    os.makedirs(out, exist_ok=True)
    man, asa = load_manhajiya(), load_asa()
    ads = []
    for folder, stem, brand in (("posts/ads-01", "manhajiya-thesis-ad", "المنهجية للخدمات البحثية والعلمية"),
                                ("asa/posts/ads-01", "asa-thesis-ad", "أكاديمية العلماء العرب")):
        if os.path.exists(os.path.join(ROOT, folder, "ad-copy.md")):
            ads.append(load_ad(folder, stem, brand))
    ads = [a for a in ads if os.path.exists(os.path.join(a["base"], f'{a["stem"]}-9x16.mp4'))]

    build_media([("m", man), ("a", asa)], ads, out)

    def pane(key, brand, title, lede, chips, note, items):
        cards = "\n".join(card(it, i, key) for i, it in enumerate(items))
        ch = "".join(f'<span class="chip">{c}</span>' for c in chips)
        return (f'<section class="pane" id="pane-{key}" data-brand="{brand}" hidden>'
                f'<h2 class="vh">{title}</h2><div class="sum">{ch}</div>'
                f'<p class="note">{note}</p>{cards}</section>')

    n_new_m = len({i["template"] for i in man if i["kind"] == "design"})
    panes = pane("m", "m", "المنهجية", "",
                 [f"{len([i for i in man if i['kind']=='design'])} تصاميم",
                  "2 ريلز", f"{n_new_m} قوالب", "مجدولة على Metricool"],
                 "<strong>مجدولة تلقائياً</strong> — التصاميم والريلز نازلة لحالها على فيسبوك وإنستغرام "
                 "بالمواعيد المكتوبة. الستوري بترفعها انت يدوي على حالة الواتساب.", man)
    panes += pane("a", "a", "أكاديمية العلماء العرب", "",
                  [f"{len([i for i in asa if i['kind']=='design'])} تصاميم", "2 ريلز",
                   "7 قوالب جديدة", "رفع يدوي"],
                  "<strong>رفع يدوي</strong> — افتح Meta Business Suite، ارفع الملف المكتوب اسمه، "
                  "اضغط «نسخ الكابشن» من هنا والصقه، وجدوله على التاريخ والساعة المكتوبين.", asa)
    if ads:
        acards = "\n".join(ad_card(a) for a in ads)
        panes += ('<section class="pane" id="pane-ads" data-brand="ads" hidden>'
                  '<h2 class="vh">إعلانات ميتا</h2>'
                  '<div class="sum"><span class="chip">ريل لكل علامة</span>'
                  '<span class="chip">9:16 و 4:5</span><span class="chip">15 ثانية</span>'
                  '<span class="chip">نص Ads Manager جاهز</span></div>'
                  '<p class="note"><strong>مخصّصة للإعلانات المدفوعة</strong> — خطّاف في أول ثانية، '
                  'كل النص داخل المنطقة الآمنة لميتا، الشعار من أول ثانية، وبتنتهي بزر واتساب. '
                  'ارفعها في Ads Manager واختر هدف «الرسائل» ووجّهها على واتساب.</p>' + acards + '</section>')

    tabs = ('<nav class="tabs" role="tablist">'
            '<button class="tab" role="tab" data-pane="m">المنهجية</button>'
            '<button class="tab" role="tab" data-pane="a">أكاديمية العلماء العرب</button>'
            + ('<button class="tab" role="tab" data-pane="ads">إعلانات ميتا</button>' if ads else '')
            + '</nav>')

    body = (HEAD
            + '<style>.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}</style>'
            + '<header class="top"><p class="eye">أسبوع 2–9 تشرين الثاني 2026</p>'
            '<h1>تصاميم الأسبوع وريلزات الإعلانات</h1>'
            '<p class="lede">كل تصميم ومعه كابشنه الجاهز للنسخ ونسخة الستوري، والريلزات تشتغل من الصفحة. '
            'بدّل بين العلامتين من الأعلى.</p>' + tabs + '</header>'
            + panes
            + '<footer>الريلز يُرفع كـ Reel على فيسبوك وإنستغرام. الملفات الأصلية بالدقة الكاملة في '
              'مستودع GitHub وفي المحادثة.</footer></div>' + SCRIPT)
    open(os.path.join(out, "page.html"), "w", encoding="utf-8").write(body)
    print("wrote", os.path.join(out, "page.html"), len(body), "chars")


if __name__ == "__main__":
    main(sys.argv[1])
