"""
Build an artifact page for a set of academy reels.

    python3 asa/engine/reelpage.py asa/posts/reels-01 <out-dir>

Reads every reel-N.json in the folder, so the Arabic is never retyped. Writes
<out-dir>/index.html plus <out-dir>/img/* — compressed MP4 previews and WEBP
covers published as the artifact's own files, because the artifact CSP blocks
external media and nothing may be hot-linked.
"""
import glob
import html
import json
import os
import subprocess
import sys

MOOD_AR = {
    "resolve": "عود دافئ · إيقاع مقسوم · هادية وبتطمّن",
    "insight": "أجراس · إيقاع سريع ومضبوط · تركيز",
    "pulse": "وتريات سريعة وشَيكر · طاقة عالية",
    "market": "باص عميق · إيقاع قوي · جدّية",
    "craft": "بيانو ناعم · إيقاع بطيء ومتأني",
    "hijaz": "عود حجاز · إيقاع إطار",
}


def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main(batch, out):
    os.makedirs(os.path.join(out, "img"), exist_ok=True)
    cards = []
    for i, spec_path in enumerate(sorted(glob.glob(os.path.join(batch, "reel-*.json"))), 1):
        r = json.load(open(spec_path, encoding="utf-8"))
        stem = os.path.basename(spec_path)[:-5]
        src = os.path.join(batch, stem + ".mp4")
        cover = os.path.join(batch, stem + "-cover.png")
        vid, cov = f"img/{stem}.mp4", f"img/{stem}.webp"
        run("ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", "scale=540:-2",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
            "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", os.path.join(out, vid))
        run("ffmpeg", "-y", "-loglevel", "error", "-i", cover,
            "-vf", "scale=440:-2:flags=lanczos", "-quality", "82", os.path.join(out, cov))
        dur = sum(s["dur"] for s in r["scenes"])
        cap = html.escape(r["caption"].strip())
        cards.append(f'''<article class="card" id="r{i}">
  <header class="ch"><span class="num">{i}</span>
    <h2>{html.escape(r["title"])}</h2>
    <span class="len">{dur:.0f} ثانية</span></header>
  <p class="svc">{html.escape(r.get("service", ""))}</p>
  <div class="grid">
    <div class="mw"><video src="{vid}" poster="{cov}" controls preload="none" playsinline></video>
      <p class="mus"><span>الموسيقى</span>{html.escape(MOOD_AR.get(r.get("mood", ""), ""))}</p>
      <p class="file"><code>{stem}.mp4</code></p></div>
    <div class="cw"><div class="chd"><span class="cl">الكابشن</span>
      <span class="cn">{len(r["caption"])} حرف</span>
      <button class="cp" data-t="c{i}">نسخ الكابشن</button></div>
      <pre class="cap" id="c{i}">{cap}</pre></div>
  </div>
</article>''')

    page = HEAD + "\n".join(cards) + TAIL
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)
    print("wrote", os.path.join(out, "index.html"), len(cards), "reels")


HEAD = '''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>ريلزات الأكاديمية الخمسة</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap">
<style>
/* Layout: a numbered run of reel cards, each video beside its caption */
:root{
  --bg:#F7F4EC; --surface:#FFFFFF; --line:#E3DBC8; --ink:#1B2A22; --dim:#5E6B61;
  --emerald:#0F5236; --gold:#A8842A; --goldsoft:#F3E8CB;
  --ff:"Cairo",system-ui,"Segoe UI",sans-serif; color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0A1711; --surface:#11241B; --line:#27402F; --ink:#EDF3EE; --dim:#9BB0A2;
  --emerald:#3FA06D; --gold:#D9B758; --goldsoft:#2A3A26; color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#0A1711; --surface:#11241B; --line:#27402F; --ink:#EDF3EE; --dim:#9BB0A2;
  --emerald:#3FA06D; --gold:#D9B758; --goldsoft:#2A3A26; color-scheme:dark;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--ff);line-height:1.75;
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 56px}
.wrap{max-width:1020px;margin:0 auto}
video,img{max-width:100%}
header.top{padding-block:34px 20px;border-bottom:2px solid var(--gold)}
.eye{font-size:.77rem;letter-spacing:.14em;font-weight:700;color:var(--gold);margin:0 0 6px}
h1{font-size:clamp(1.5rem,4.3vw,2.2rem);font-weight:900;margin:0;color:var(--emerald);text-wrap:balance}
.lede{margin:10px 0 0;color:var(--dim);max-width:64ch;font-size:.95rem}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px;
  margin-block:18px;scroll-margin-top:14px}
.ch{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding-bottom:11px;
  border-bottom:1px dashed var(--line)}
.num{width:34px;height:34px;flex:0 0 auto;border-radius:50%;background:var(--emerald);color:#fff;
  font-weight:900;display:grid;place-items:center;font-size:.95rem}
.ch h2{font-size:1.1rem;font-weight:900;margin:0;color:var(--emerald);min-width:0;text-wrap:balance}
.len{margin-inline-start:auto;font-size:.74rem;font-weight:700;padding:3px 11px;border-radius:999px;
  background:var(--goldsoft);color:var(--gold);font-variant-numeric:tabular-nums}
.svc{margin:11px 0 0;font-size:.9rem;color:var(--dim)}
.grid{display:grid;grid-template-columns:minmax(0,230px) minmax(0,1fr);gap:20px;
  align-items:start;margin-top:14px}
@media (max-width:720px){.grid{grid-template-columns:minmax(0,1fr)}}
.mw{min-width:0}
.mw video{width:100%;display:block;border-radius:10px;border:1px solid var(--line);background:#000}
.mus{margin:9px 0 0;font-size:.78rem;color:var(--dim);line-height:1.6}
.mus span{display:block;font-weight:700;color:var(--gold);font-size:.72rem;letter-spacing:.08em}
.file{margin:6px 0 0;font-family:ui-monospace,monospace;font-size:.74rem;color:var(--dim)}
.file code{background:var(--goldsoft);color:var(--gold);padding:2px 7px;border-radius:5px}
.cw{min-width:0}
.chd{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px}
.cl{font-size:.75rem;font-weight:700;letter-spacing:.09em;color:var(--gold)}
.cn{font-size:.73rem;color:var(--dim);font-variant-numeric:tabular-nums}
.cp{margin-inline-start:auto;font-family:var(--ff);font-size:.82rem;font-weight:700;cursor:pointer;
  background:var(--emerald);color:#fff;border:0;border-radius:8px;padding:7px 15px}
.cp:hover{filter:brightness(1.14)}
.cp:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
pre.cap{margin:0;white-space:pre-wrap;word-break:break-word;font-family:var(--ff);font-size:.89rem;
  line-height:1.85;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:14px;
  max-height:430px;overflow:auto;user-select:all}
footer{margin-top:34px;padding-top:18px;border-top:1px solid var(--line);color:var(--dim);font-size:.85rem}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style></head><body><div class="wrap">
<header class="top">
  <p class="eye">أكاديمية العلماء العرب</p>
  <h1>خمس ريلزات بموسيقى مختلفة</h1>
  <p class="lede">كل ريل عن خدمة، وكل واحد بموسيقى أصلية مختلفة — مقام وآلة وإيقاع وسرعة مختلفة،
  مش نفس اللحن بسرعة تانية. ثلاثة منها عن جمع البيانات.</p>
</header>
'''

TAIL = '''<footer>ترفعهم كـ Reel على فيسبوك وإنستغرام، والغلاف جاهز بملف <code>reel-N-cover.png</code>.
الملفات الأصلية بالدقة الكاملة في المحادثة وعلى GitHub.</footer></div>
<script>
document.querySelectorAll(".cp").forEach(function(b){
  b.addEventListener("click", function(){
    var el = document.getElementById(b.dataset.t), orig = b.textContent;
    function ok(){ b.textContent = "تم النسخ ✓";
      setTimeout(function(){ b.textContent = orig; }, 1800); }
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


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
