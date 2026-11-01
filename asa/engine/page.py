"""
Build the weekly artifact page for أكاديمية العلماء العرب.

    python3 engine/page.py posts/batch-02 <out-dir>

Reads <batch>/content.json, reel-N.json and schedule.json, so the Arabic copy is
never retyped by hand. Writes <out-dir>/page.html plus <out-dir>/img/* -- small
WEBP display copies and compressed MP4 previews, published as the artifact's own
files (the artifact CSP blocks external media, so nothing may be hot-linked).
"""
import datetime
import html
import json
import os
import subprocess
import sys

AR_MONTH = {1: "كانون الثاني", 2: "شباط", 3: "آذار", 4: "نيسان", 5: "أيار", 6: "حزيران",
            7: "تموز", 8: "آب", 9: "أيلول", 10: "تشرين الأول", 11: "تشرين الثاني", 12: "كانون الأول"}


def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def webp(src, dst, width, q=82):
    run("ffmpeg", "-y", "-loglevel", "error", "-i", src,
        "-vf", f"scale={width}:-2:flags=lanczos", "-quality", str(q), dst)


def preview_mp4(src, dst, width=540, crf=31):
    run("ffmpeg", "-y", "-loglevel", "error", "-i", src,
        "-vf", f"scale={width}:-2:flags=lanczos", "-c:v", "libx264", "-preset", "slow",
        "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart", dst)


def ar_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {AR_MONTH[d.month]}"


def build(batch, out):
    img = os.path.join(out, "img")
    os.makedirs(img, exist_ok=True)
    content = json.load(open(os.path.join(batch, "content.json"), encoding="utf-8"))
    sched = json.load(open(os.path.join(batch, "schedule.json"), encoding="utf-8"))
    reels = {n: json.load(open(os.path.join(batch, f"reel-{n}.json"), encoding="utf-8"))
             for n in (1, 2)}

    for i in range(1, len(content["posts"]) + 1):
        webp(os.path.join(batch, f"{i:02d}.png"), os.path.join(img, f"{i:02d}.webp"), 760)
        webp(os.path.join(batch, f"story-{i:02d}.png"), os.path.join(img, f"story-{i:02d}.webp"), 340)
    for n in (1, 2):
        webp(os.path.join(batch, f"reel-{n}-cover.png"), os.path.join(img, f"reel-{n}.webp"), 520)
        preview_mp4(os.path.join(batch, f"reel-{n}.mp4"), os.path.join(img, f"reel-{n}.mp4"))

    items = sorted(sched["items"], key=lambda it: (it["date"], it["time"]))
    toc, cards = [], []
    for k, it in enumerate(items, start=1):
        when = f"{it['day']} {ar_date(it['date'])}"
        reel = it["kind"] == "reel"
        toc.append(
            f'<a class="tocrow" href="#p{k}"><span class="tocd">{html.escape(when)} · {it["time"]}</span>'
            f'<span class="tocf">{it["file"]}</span>'
            f'<span class="tock {"reelb" if reel else ""}">{"ريلز" if reel else "صورة"}</span></a>')

        if reel:
            n = int(it["file"].split("-")[1][0])
            spec = reels[n]
            title, caption, tmpl = spec["title"], spec["caption"], "reel.py"
            media = (f'<div class="media reel"><video src="img/reel-{n}.mp4" '
                     f'poster="img/reel-{n}.webp" controls preload="none" playsinline></video></div>')
            files = (f'<code>reel-{n}.mp4</code><span class="sep">·</span>'
                     f'<code class="muted">reel-{n}-cover.png</code>')
            meta = "24 ثانية · موسيقى أصلية بدون تعليق صوتي"
        else:
            i = int(it["file"][:2])
            p = content["posts"][i - 1]
            title, caption, tmpl = p["service"], p["caption"], p["template"]
            media = (f'<div class="media"><img src="img/{i:02d}.webp" alt="تصميم {i}" loading="lazy"></div>'
                     f'<div class="media story"><img src="img/story-{i:02d}.webp" alt="ستوري {i}" '
                     f'loading="lazy"><span class="stlabel">نسخة الستوري</span></div>')
            files = (f'<code>{i:02d}.png</code><span class="sep">·</span>'
                     f'<code class="muted">story-{i:02d}.png</code>')
            meta = f"قالب جديد هذا الأسبوع · {tmpl}"

        cards.append(f'''<article class="card" id="p{k}">
  <header class="chead">
    <div class="when"><strong>{html.escape(when)}</strong><span>{it["time"]}</span></div>
    <span class="badge {"reelb" if reel else ""}">{"ريلز" if reel else "منشور صورة"}</span>
  </header>
  <h2>{html.escape(title)}</h2>
  <div class="files">{files}<span class="sep">·</span><span class="tmpl">{html.escape(meta)}</span></div>
  <div class="grid">
    <div class="mediawrap">{media}</div>
    <div class="capwrap">
      <div class="caphead"><span class="caplabel">الكابشن</span>
        <span class="count">{len(caption)} حرف</span>
        <button class="copy" data-t="c{k}">نسخ الكابشن</button></div>
      <pre class="cap" id="c{k}">{html.escape(caption)}</pre>
    </div>
  </div>
</article>''')

    page = TEMPLATE.replace("{{TOC}}", "\n".join(toc)).replace("{{CARDS}}", "\n\n".join(cards))
    with open(os.path.join(out, "page.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    print("page.html +", len(os.listdir(img)), "media files")


TEMPLATE = r"""<title>منشورات الأكاديمية — الأسبوع الثاني</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap">
<style>
:root{
  --bg:#F7F4EC; --surface:#FFFFFF; --line:#E3DBC8; --ink:#1B2A22; --dim:#5E6B61;
  --emerald:#0F5236; --gold:#A8842A; --goldsoft:#F2E7C8;
  --ff:"Cairo",system-ui,"Segoe UI",sans-serif;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0A1711; --surface:#11241B; --line:#27402F; --ink:#EDF3EE; --dim:#9BB0A2;
  --emerald:#2E8B5E; --gold:#D9B758; --goldsoft:#2A3A26; color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#0A1711; --surface:#11241B; --line:#27402F; --ink:#EDF3EE; --dim:#9BB0A2;
  --emerald:#2E8B5E; --gold:#D9B758; --goldsoft:#2A3A26; color-scheme:dark;}

body{background:var(--bg);color:var(--ink);font-family:var(--ff);direction:rtl;
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));
  padding-block:0 56px;line-height:1.75}
.wrap{max-width:1040px;margin:0 auto}

header.top{padding-block:34px 22px;border-bottom:2px solid var(--gold)}
.eyebrow{font-size:.78rem;letter-spacing:.14em;color:var(--gold);font-weight:700;margin:0 0 6px}
h1{font-size:clamp(1.55rem,4.4vw,2.3rem);font-weight:900;margin:0;text-wrap:balance;color:var(--emerald)}
.lede{margin:10px 0 0;color:var(--dim);max-width:62ch;font-size:.97rem}
.howto{margin:18px 0 0;padding:14px 16px;background:var(--surface);border:1px solid var(--line);
  border-inline-start:4px solid var(--gold);border-radius:10px;font-size:.92rem}
.howto ol{margin:6px 0 0;padding-inline-start:1.25rem}
.howto li{margin:2px 0}

nav.toc{margin-block:26px;display:grid;gap:6px}
.tocrow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;text-decoration:none;color:inherit;
  background:var(--surface);border:1px solid var(--line);border-radius:9px;padding:9px 13px;font-size:.88rem}
.tocrow:hover{border-color:var(--gold)}
.tocd{font-weight:700;min-width:0}
.tocf{font-family:ui-monospace,monospace;color:var(--dim);font-size:.8rem;min-width:0}
.tock{margin-inline-start:auto;font-size:.72rem;font-weight:700;padding:2px 9px;border-radius:999px;
  background:var(--goldsoft);color:var(--gold)}
.tock.reelb,.badge.reelb{background:var(--emerald);color:#fff}

.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  padding:18px;margin-block:18px;scroll-margin-top:16px}
.chead{display:flex;align-items:center;gap:12px;flex-wrap:wrap;
  padding-bottom:12px;border-bottom:1px dashed var(--line)}
.when{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}
.when strong{font-size:1.02rem}
.when span{color:var(--dim);font-variant-numeric:tabular-nums;font-size:.9rem}
.badge{margin-inline-start:auto;font-size:.74rem;font-weight:700;padding:3px 11px;border-radius:999px;
  background:var(--goldsoft);color:var(--gold)}
.card h2{font-size:1.14rem;font-weight:700;margin:13px 0 4px;color:var(--emerald);text-wrap:balance}
.files{font-family:ui-monospace,monospace;font-size:.78rem;color:var(--dim);margin-bottom:14px}
.files code{background:var(--goldsoft);color:var(--gold);padding:2px 7px;border-radius:5px}
.files code.muted{background:transparent;color:var(--dim);padding:0}
.files .tmpl{font-family:var(--ff);color:var(--dim)}
.sep{margin:0 7px;opacity:.5}

.grid{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:20px;align-items:start}
@media (max-width:760px){.grid{grid-template-columns:minmax(0,1fr)}}
.mediawrap{display:flex;gap:12px;align-items:flex-start;min-width:0}
.media{flex:1 1 0;min-width:0}
.media img,.media video{width:100%;max-width:100%;display:block;border-radius:9px;border:1px solid var(--line)}
.media.story{flex:0 0 86px;position:relative}
.media.reel{flex:0 0 190px}
.stlabel{display:block;text-align:center;font-size:.66rem;color:var(--dim);margin-top:5px}

.capwrap{min-width:0}
.caphead{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px}
.caplabel{font-size:.76rem;font-weight:700;letter-spacing:.1em;color:var(--gold)}
.count{font-size:.74rem;color:var(--dim);font-variant-numeric:tabular-nums}
.copy{margin-inline-start:auto;font-family:var(--ff);font-size:.82rem;font-weight:700;cursor:pointer;
  background:var(--emerald);color:#fff;border:0;border-radius:8px;padding:7px 15px}
.copy:hover{filter:brightness(1.12)}
.copy.done{background:var(--gold)}
.copy:focus-visible,.tocrow:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
pre.cap{margin:0;white-space:pre-wrap;word-break:break-word;font-family:var(--ff);font-size:.9rem;
  line-height:1.85;background:var(--bg);border:1px solid var(--line);border-radius:10px;
  padding:14px;max-height:430px;overflow:auto;user-select:all}

footer{margin-top:34px;padding-top:18px;border-top:1px solid var(--line);color:var(--dim);font-size:.85rem}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>

<div class="wrap">
<header class="top">
  <p class="eyebrow">أكاديمية العلماء العرب للاستشارات والتدريب</p>
  <h1>منشورات الأسبوع الثاني</h1>
  <p class="lede">سبعة تصاميم وريلزان، كل واحد مع كابشنه الجاهز ونسخة الستوري. كل التصاميم هذا الأسبوع على قوالب جديدة بالكامل، ما في ولا تصميم مكرر عن الأسبوع الماضي.</p>
  <div class="howto">
    <strong>طريقة النشر على Meta Business Suite</strong>
    <ol>
      <li>افتح «إنشاء منشور» واختر صفحة الفيسبوك وحساب الانستغرام.</li>
      <li>ارفع الملف المكتوب اسمه بالبطاقة (نزّله من المحادثة إذا ما وصلك على اللابتوب).</li>
      <li>اضغط «نسخ الكابشن» من هنا والصقه بخانة النص.</li>
      <li>اختار «جدولة» وحدّد التاريخ والساعة المكتوبين بالبطاقة.</li>
      <li>الستوري على الواتساب ترفعه يدوي من ملف <code>story-NN.png</code>.</li>
    </ol>
  </div>
  <nav class="toc">{{TOC}}</nav>
</header>

{{CARDS}}

<footer>الريلز يُرفع كـ Reel على الفيسبوك والانستغرام، وغطاؤه من ملف <code>reel-N-cover.png</code> إذا طلبه. الفيديوهات المعروضة هنا نسخ مصغّرة للعرض — الأصل بجودة كاملة 1080×1920 بالملفات المرفقة بالمحادثة.</footer>
</div>

<script>
document.querySelectorAll(".copy").forEach(function(b){
  b.addEventListener("click", function(){
    var el = document.getElementById(b.dataset.t);
    var txt = el.textContent;
    function ok(){ var o = b.textContent; b.textContent = "تم النسخ ✓"; b.classList.add("done");
      setTimeout(function(){ b.textContent = o; b.classList.remove("done"); }, 1800); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(ok, select);
    } else { select(); }
    function select(){
      var r = document.createRange(); r.selectNodeContents(el);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      b.textContent = "محدّد — انسخ بـ Ctrl+C";
      setTimeout(function(){ b.textContent = "نسخ الكابشن"; }, 2600);
    }
  });
});
</script>
"""

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
