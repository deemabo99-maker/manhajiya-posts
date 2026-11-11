# نظام الريلز الإعلانية (Meta Ads) — المنهجية وأكاديمية العلماء العرب

This is the standard for **paid** ad reels, adopted by the owner on 1 Nov 2026 after the
first pair shipped. It is separate from the weekly organic reels in `BRAND.md`: those are
for the feed, these are for Ads Manager and are built to different rules.

Both brands use this file. The brand's own look, palette, fonts, contact block and claims
still come from its own guide — `brand/BRAND.md` for المنهجية, `asa/brand/BRAND.md` for
أكاديمية العلماء العرب.

## Shipped so far

| Brand | Service | Folder | Stem |
|---|---|---|---|
| المنهجية | إعداد الرسائل والأطاريح من العنوان حتى المناقشة | `posts/ads-01` | `manhajiya-thesis-ad` |
| أكاديمية العلماء العرب | إعداد الرسائل والأطاريح من العنوان حتى المناقشة | `asa/posts/ads-01` | `asa-thesis-ad` |

Each folder holds the spec (`<stem>.json`), the rendered `<stem>-9x16.mp4`,
`<stem>-4x5.mp4` and `<stem>-cover.png`, and `ad-copy.md` with the Ads Manager text.

## Build

One command renders every placement:

```bash
python3 engine/ads.py posts/ads-01/<stem>.json
python3 engine/ads.py asa/posts/ads-01/<stem>.json
```

It picks the reel engine that belongs to the spec's brand, renders 9:16, cuts 4:5 and
writes the cover. Never cut the 4:5 by hand.

## The safe-area rule (learned the hard way)

The first two specs both claimed "all text in y 290–1250, 4:5 crop-safe", and on that basis
the 4:5 was cut from the centre (y=285). **It was wrong.** Both reels open with their hook
near the top of the frame, and the centre cut sliced the first line off every headline.

So the rule is now the opposite, and `engine/ads.py` enforces it:

- **4:5 is cut from the top edge** — `crop=1080:1350:0:0`.
- Compose every ad scene so that **everything that must survive is inside y 0–1350**:
  hook, body, numbers, CTA, logo, WhatsApp pill.
- Below y 1350 put only what the feed placement can lose: a person's legs, floor glow,
  background pattern. A graduate standing on the frame edge works well — the head and torso
  stay, the rest goes.
- Keep text out of the outer 60 px on the left and right.
- Check both ratios with a contact sheet before shipping. A claim in the spec's `format`
  string that the text is crop-safe proves nothing; look at the frames.

## Meta pre-flight — owner's standing rule (12 Nov 2026)

**Nothing reaches the owner — ad or reel, either brand — without passing
`python3 engine/preflight.py <video.mp4> <spec.json>` and the manual list below.**
The rule came from a real hit: Instagram flagged the first one-shot reel as
"contains a border" and throttled it, because of a heavy vignette and a flat dark
band at the top of the world. The script now catches that, plus the edit-list box
and safe-zone misses it also found in the same file.

Machine-checked (`engine/preflight.py`):
- 9:16 at 1080x1920 (or 1440x2560), H.264 yuv420p, constant 30 fps, stereo AAC
  >= 128 kbps, under 4 GB, **no edit list** — every encoder passes `-use_editlist 0`
- 6–60 s, cover image beside the file
- **no flat band along any edge** on frames sampled across the reel (border /
  reused-content flag): vignette no stronger than 0.10, texture visible to the edge,
  no layer may run out and show flat fill, whip blur clamps to the edge
- **unified safe zone**: every text, CTA, logo, number and stamp clear of the top 14 %,
  the bottom 35 % and 6 % each side. Imagery may bleed; words may not.

Checked by eye before sending:
- hook readable in the first second; the first 40 characters of the caption carry the
  hook on their own (Reels placements truncate primary text there)
- original audio only; no licensed music, no other app's watermark, no face effects
- edge-to-edge design avoided: Meta may zoom to fill ultra-tall screens
- for a boosted reel: the brand's WhatsApp number is connected to the page, or the
  WhatsApp button will be missing from the boost options

Sources: Meta Reels ad specs and the unified 9:16 safe zone as documented in 2026
(billo.app/blog/meta-ads-safe-zones, knowlify.com/articles/meta-video-ad-specs).

## What makes it an ad rather than a post

1. **A hook in the first second**, as a question the researcher is already asking
   themselves: "رسالتك عالقة عند الصفحة الأولى؟" · "تكتب رسالتك وحدك؟". It must be readable
   before anything moves.
2. **The logo from frame one.** Someone who scrolls past at 1.5 seconds should still have
   seen whose ad it was.
3. **15–16 seconds.** Long enough for one idea, short enough to finish.
4. **One service, one idea.** An ad that lists everything sells nothing.
5. **A visual spine, not text cards** — the shipped pair: a camera riding the thesis road
   milestone by milestone, and a pull-back from one gold spine to a library wall with the
   numbers counting up. Keep that bar.
6. **A CTA that is an action**: the WhatsApp pill with the number, plus
   "استشارتك الأولى مجانية". The objective in Ads Manager is Messages, pointed at WhatsApp.
7. **No invented claims.** المنهجية: no numbers at all. الأكاديمية: only
   "أكثر من 5000 عمل بحثي" and "أكثر من 100 باحث" — these are the owner's approved figures.
8. **Little enough text** that it reads on a phone at arm's length. Meta no longer rejects a
   text-heavy image, but it still buries it.

## `ad-copy.md` — what Ads Manager needs

Every ad folder carries one, in this shape, so the owner can paste straight in:

- **الفكرة** — one paragraph on what the viewer sees, in Jordanian Arabic.
- **النص الأساسي (Primary text)** — in a fenced block, ready to copy.
- **العنوان (Headline)** — one line.
- **الوصف (Description)** — one line.
- **زر الإجراء (CTA)** — Send WhatsApp message, with the brand's number.
- **الكابشن الكامل** — the longer version for posting the same reel organically on the page.

The contact block and hashtag rules are the brand's own, from its `BRAND.md`.

## Queue — what to build next

One ad per service, strongest first. Each new ad takes the next unused entry and a visual
format not used by any earlier ad:

1. ~~إعداد الرسائل والأطاريح~~ — shipped (both brands)
2. النشر العلمي في Scopus Q1 / Q2 / Q3 / Q4 و Arcif
3. التحليل الإحصائي وربط النتائج بالفرضيات
4. خطة البحث (Proposal) ومشكلة الدراسة
5. جمع البيانات: بيانات بورصة عمان والاستبيانات الإلكترونية
6. أبحاث النشر والترقية لأعضاء هيئة التدريس
7. التدقيق اللغوي وفحص Turnitin والتنسيق
8. مشاريع تخرج البكالوريوس
9. الدورات التدريبية أونلاين (الأكاديمية)
10. الترجمة المعتمدة والعروض التقديمية

Folders are numbered in order: `ads-02`, `ads-03`, … under each brand's `posts/`.

## Delivery

An ad is finished when all of these exist and have been looked at:

- `<stem>-9x16.mp4`, `<stem>-4x5.mp4`, `<stem>-cover.png`
- `ad-copy.md`
- a contact sheet of both ratios, checked for clipped text
- the files committed and pushed, and an artifact page that plays both ratios and carries
  the Ads Manager copy with a copy button (`engine/combined_page.py` builds it)
