"""
Emit the publish manifest a scheduler (Make / n8n / Zapier) consumes.

    python3 engine/manifest.py posts/batch-02

Writes <batch>/manifest.json: one entry per scheduled item, carrying the public
raw.githubusercontent.com URL of the media, the caption exactly as it must be
posted, the target networks, and the publish time in Asia/Amman. Nothing here is
typed by hand -- it is derived from content.json, reel-N.json and schedule.json,
so the manifest can never drift from what was rendered.

The URLs resolve only while the repository is public.
"""
import json
import os
import sys

RAW = "https://raw.githubusercontent.com/deemabo99-maker/manhajiya-posts/main"
OFFSET = "+03:00"          # Asia/Amman


def build(batch):
    content = json.load(open(os.path.join(batch, "content.json"), encoding="utf-8"))
    sched = json.load(open(os.path.join(batch, "schedule.json"), encoding="utf-8"))
    reels = {n: json.load(open(os.path.join(batch, f"reel-{n}.json"), encoding="utf-8"))
             for n in (1, 2)}
    rel = batch.replace(os.sep, "/").lstrip("./")
    base = f"{RAW}/asa/{rel}" if not rel.startswith("asa/") else f"{RAW}/{rel}"

    out = []
    for it in sorted(sched["items"], key=lambda i: (i["date"], i["time"])):
        when = f"{it['date']}T{it['time']}:00{OFFSET}"
        if it["kind"] == "reel":
            n = int(it["file"].split("-")[1][0])
            out.append({
                "id": f"reel-{n}", "kind": "reel", "publish_at": when,
                "networks": ["facebook", "instagram"],
                "facebook_type": "REEL", "instagram_type": "REEL",
                "media_url": f"{base}/reel-{n}.mp4",
                "cover_url": f"{base}/reel-{n}-cover.png",
                "title": reels[n]["title"], "caption": reels[n]["caption"],
            })
        else:
            i = int(it["file"][:2])
            p = content["posts"][i - 1]
            out.append({
                "id": f"{i:02d}", "kind": "image", "publish_at": when,
                "networks": ["facebook", "instagram"],
                "facebook_type": "POST", "instagram_type": "POST",
                "media_url": f"{base}/{i:02d}.png",
                "story_url": f"{base}/story-{i:02d}.png",
                "title": p["service"], "caption": p["caption"],
            })

    man = {"batch": os.path.basename(batch.rstrip("/")), "timezone": "Asia/Amman",
           "note": "Story files are for WhatsApp status and are uploaded by hand; "
                   "they are not part of the scheduled Facebook/Instagram posts.",
           "items": out}
    path = os.path.join(batch, "manifest.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote", path, "-", len(out), "items")
    for e in out:
        print(f"  {e['publish_at']}  {e['kind']:5s}  {e['media_url'].rsplit('/', 1)[-1]}")


if __name__ == "__main__":
    build(sys.argv[1])
