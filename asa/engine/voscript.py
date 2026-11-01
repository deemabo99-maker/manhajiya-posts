"""
Print the recording script for a reel, for the owner to read aloud.

    python3 asa/engine/voscript.py asa/posts/reels-01/reel-6.json [out.md]

Reads the spec's `vo` list and uses each line's `read` field — the plain,
unvocalised twin of the narration. Harakat help espeak-ng and hinder a person,
so a human never reads the `text` field.

Every line must address men and women alike: no أنتَ / أنتِ, no ـكَ / ـكِ ending,
no feminine ـين verb. This script refuses to print a line that breaks that.
"""
import json
import re
import sys
import unicodedata

GENDERED = re.compile(r"(^|\s)انت[ِ]?($|\s)|ين(ها|ه)($|\s)|تك[ِ]($|\s)")


def bare(t):
    return "".join(c for c in t if not unicodedata.combining(c))


def main(spec_path, out_path=None):
    spec = json.load(open(spec_path, encoding="utf-8"))
    vo = spec.get("vo") or []
    if not vo:
        sys.exit(f"{spec_path} has no narration")
    total = sum(s["dur"] for s in spec["scenes"])

    rows, bad = [], []
    for i, item in enumerate(vo, 1):
        text = item.get("read") or item["text"]
        if not item.get("read"):
            bad.append(f"line {i} has no plain `read` form")
        if GENDERED.search(bare(text)):
            bad.append(f"line {i} addresses one gender: {text}")
        nxt = vo[i]["t"] if i < len(vo) else total
        rows.append((i, text, max(0.5, nxt - item["t"] - 0.25)))
    if bad:
        sys.exit("refusing to print:\n  " + "\n  ".join(bad))

    out = [f"# نص التسجيل الصوتي — {spec.get('title', '')}", "",
           "اقرأ كل سطر لحاله، وخُذ نفَساً بين السطر والثاني. ما في داعي تضبط الوقت —",
           "التوقيت بنظبّطه إحنا. بس حاول ما يطول السطر عن الثواني المكتوبة جنبه بكثير.", "",
           "**طريقة التسجيل:** مسجّل الصوت بالموبايل · غرفة هادية بدون صدى · الموبايل على",
           "بُعد شبر من الفم · كل السطور بملف واحد، مع ثانيتين سكوت بين كل سطر والثاني.", "",
           "| # | السطر | الوقت المتاح |", "|---|---|---|"]
    out += [f"| {i} | {t} | ~{d:.1f} ثانية |" for i, t, d in rows]
    out += ["", "---", "", "## السطور فقط (للقراءة من الشاشة)", ""]
    out += [f"**{i}.** {t}" for i, t, _ in rows]
    text = "\n".join(out) + "\n"

    if out_path:
        open(out_path, "w", encoding="utf-8").write(text)
        print(f"wrote {out_path}  ({len(rows)} lines, {total:.1f}s reel)")
    else:
        print(text)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
