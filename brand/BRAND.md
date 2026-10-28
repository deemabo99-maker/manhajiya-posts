# المنهجية للخدمات البحثية والعلمية — دليل الهوية والمحتوى

This file is the source of truth for every weekly batch of posts. Read it in full
before writing copy or rendering designs.

## Identity

- **Name:** المنهجية للخدمات البحثية والعلمية
- **Logo:** `brand/logo.png` (cut out from `brand/logo-original.jpg`). Always place it on a
  white rounded badge, never directly on a coloured background.
- **Look:** vivid purple backgrounds, light-grey/white panels, a purple → magenta → pink →
  orange → yellow ring gradient, and the motifs from past ads: dot grids, bold plus signs,
  small play-triangles, circular frames with the ring gradient.
- **Format:** 1080 × 1350 PNG (4:5), works for Instagram and Facebook feed.

### Palette (see `engine/kit.py` → `C`)

| Role | Hex |
|---|---|
| Brand purple | #9627C4 |
| Violet | #7B1FA2 |
| Plum (dark) | #4B1A5E |
| Night (darkest bg) | #24092F |
| Magenta / Pink | #C2309E / #E8457E |
| Orange / Yellow | #F28C28 / #FFC21A |
| Paper (light bg) | #F5F2F7 |
| Ink (text) | #1E1A22 |
| WhatsApp green | #1FAF5A |

### Fonts (`brand/fonts`, all SIL OFL)

- Headlines: **Noto Kufi Arabic** weight 800–900
- Sub-heads and body: **Almarai** (Bold / ExtraBold / Regular)
- Latin and numbers: DejaVu Sans Bold (system)

## Contact details (must appear on every design)

- WhatsApp: **00962778707204**
- Instagram: **@methodology_center**
- Facebook and X icons in the footer
- Based in Jordan; works online with Saudi Arabia, Iraq, Kuwait, Bahrain, Oman, UAE, Qatar,
  Algeria, Libya and Egypt.

## Services (from the owner's service guide, 2026)

1. **إعداد البحوث والرسائل الأكاديمية**
   - اقتراح عناوين مبتكرة لرسائل الماجستير والدكتوراه
   - إعداد خطة البحث الكاملة (المقدمة، المشكلة، الأهمية، الأهداف، المنهج، الأدوات، الفرضيات)
   - إعداد الرسائل كاملة من المقدمة إلى الخاتمة
   - مشاريع تخرج البكالوريوس بكافة التخصصات
   - التعديل والمتابعة المستمرة طوال فترة الرسالة
2. **الدعم المنهجي وجمع البيانات**
   - توزيع الاستبيانات الإلكترونية عبر نماذج جوجل (Google Forms)
   - جمع البيانات المالية الحقيقية من بورصة عمان يدوياً وبدقة عالية للبحوث المالية والمحاسبية
   - توفير المراجع والكتب والدراسات السابقة (عربية وأجنبية)
   - إعداد الإطارين النظري والميداني واستخراج النتائج
   - إعداد أدوات الدراسة (الاستبيانات والبرامج التدريبية والإرشادية)
3. **التحليل الإحصائي والبرمجة**
   - خدمات البرمجة والدعم التقني المخصص للبحوث والأبحاث التطبيقية والتكنولوجية
   - التحليل الإحصائي للبيانات بدقة وربط النتائج بالفرضيات
   - تحكيم أدوات الدراسة والاستبيانات بنخبة من أعضاء هيئة التدريس بالجامعات العربية
4. **النشر العلمي والدراسات المتقدمة**
   - إعداد أبحاث النشر والترقية لأعضاء هيئة التدريس
   - استلال أبحاث النشر من الرسائل حتى مرحلة قبول النشر بالمجلات العالمية المصنفة
     **Scopus Q1 / Q2 / Q3 / Q4** (owner's correction: always list all four, Q1 included)
   - صياغة الأوراق العلمية في التخصصات التربوية والإنسانية والنفسية، ومقترحات البحث (Proposal)
5. **الخدمات المساندة والتعليمية**
   - التدقيق الإملائي واللغوي للأبحاث والرسائل
   - تقديم خدمات الترجمة المعتمدة بدقة عالية
   - تصميم عروض تقديمية احترافية (PowerPoint)
   - دورات تدريبية "أونلاين" لمختلف التخصصات الجامعية
6. From past ads: فحص الاقتباس ببرنامج Turnitin، التنسيق الشكلي والتنضيد، مراجعة الدراسات السابقة،
   استشارات مجانية.

## Rules for designs

- **Owner's standing request (26 Oct 2026): every design must be distinctive, innovative and
  eye-catching ("مميزة ومبتكرة وجذابة").** Reusing the same few layouts is not enough:
  - Every week, at least **2 of the 4 designs use a brand-new template** written for that
    batch (add it to `engine/templates.py`), with a new composition idea: e.g. big-number
    typography, split diagonal layouts, a mock phone/chat screen, a "before → after" panel,
    a calendar or checklist card, a journal-cover mock-up, a timeline, an infographic,
    a bold quote card, layered paper cards, isometric-style stacks, a myth vs. fact card.
  - Never repeat the same template two weeks in a row; alternate dark, vivid-purple and light
    backgrounds across the week.
  - Every design needs one strong focal point (oversized headline, illustration or number)
    and a clear visual hierarchy; it should stop the scroll on a phone screen.
  - Before scheduling, compare the batch against the last 3 batches side by side; if a
    design looks like an earlier one, redesign it.
  - Reels: new hook, new scene layouts and new motion each week (not just new text).
- One service (or one angle on a service) per post; rotate through all six groups above.
- Headline ≤ 4 words per line, max two lines; at most 3 bullets or 6 short cards.
- Every design: logo badge, WhatsApp pill with the number, social footer, a short CTA line.
- No invented claims: no prices, guarantees, percentages, counts of clients or "100%".
- Graphic illustrations only (shapes, charts, icons). No people photos unless the owner
  supplies licensed images.

## Rules for captions (owner asked for stronger captions, 26 Oct 2026)

- Modern Standard Arabic. Structure: **hook** (emoji + pain point or bold promise) →
  **problem** (one or two lines the student recognises) → **solution** (✅ / numbered list of
  the real services) → **push** (start today, first consultation free) → **contact block** →
  regions line (optional) → hashtags.
- The contact block is mandatory and always exactly:

```
📞 للتواصل والاستفسار:
📱 رقم الهاتف: 00962778707204
💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778707204
```

- 6–8 hashtags, always starting with #المنهجية.
- No invented numbers, prices or guarantees. Up to ~1,100 characters is fine.

## Weekly workflow (owner's choices, 26 Oct 2026)

Runs every **Sunday morning** (Amman time). The owner chose **direct scheduling**: no
approval step — prepare, schedule, then send the owner a summary with all files.

Each week = **3 image posts + 2 reels** (owner's change, 27 Oct 2026), plus WhatsApp-status
versions of the 3 designs.

| Slot | Content |
|---|---|
| Monday 10:00 | image post 01 |
| Tuesday 10:00 | image post 02 |
| Wednesday 10:00 | image post 03 |
| Thursday 19:00 | reel 1 |
| Saturday 19:00 | reel 2 |

Five items a week is exactly **20 a month**, the free Metricool plan's publishing cap, so a
normal week schedules in full. In a month that spans five posting weeks the cap bites: drop
image posts first and keep both reels, then tell the owner which post was dropped and why.

Steps:

1. Pick the next batch number (`posts/batch-NN`, NN = highest existing + 1). Read the
   `content.json` and every reel JSON of the last 3 batches (`reel-1.json`, `reel-2.json`,
   and `reel.json` in batch-01, which predates the two-reel week) so services, hooks,
   headlines and
   templates are not repeated, and so the reel service rotation below carries forward.
2. Create `posts/batch-NN/content.json` (3 posts: template + copy + caption) and
   `posts/batch-NN/reel-1.json` + `reel-2.json` (each with `service`, scenes and caption).
   Use 3 different templates; add a new template to `engine/templates.py` when the rotation
   gets repetitive.
3. Render: `python3 engine/render.py posts/batch-NN`,
   `python3 engine/story.py posts/batch-NN`,
   `python3 engine/reel.py posts/batch-NN/reel-1.json posts/batch-NN/reel-1.mp4`,
   `python3 engine/reel.py posts/batch-NN/reel-2.json posts/batch-NN/reel-2.mp4`.
4. Look at every PNG and a contact sheet of frames from both reels: no overlaps, no clipped
   text, phone number exactly 00962778707204, Scopus always Q1/Q2/Q3/Q4. Fix and re-render.
5. Write `posts/batch-NN/captions.md`, commit and push to `main`.
6. Media links for Metricool:
   `https://raw.githubusercontent.com/deemabo99-maker/manhajiya-posts/main/posts/batch-NN/01.png`
   (reels: `reel-1.mp4` with `reel-1-cover.png` as `videoThumbnailUrl`, same for 2).
7. **Monthly cap:** Metricool free plan publishes max **20 posts per calendar month**
   (a reel counts). Before scheduling, call getScheduledPosts for each month the week
   touches and count posts already there. If a slot would make a month exceed 20, drop an
   image post — never a reel — and tell the owner which one and why.
8. Schedule with createScheduledPost: brand id 7664477, timezone Asia/Amman,
   providers facebook + instagram, autoPublish true; images `type: POST`,
   reels `facebookData.type REEL` + `instagramData.type REEL, showReelOnFeed true`.
9. Verify with getScheduledPosts, then send the owner (SendUserFile): the 3 designs, the 3
   story PNGs, both reels and `captions.md`, with a short Arabic summary of what goes out
   when and which service each reel covers.

## Weekly reels (owner's change, 27 Oct 2026)

**Two** 9:16 reels every week (1080 × 1920, ~20 s, H.264 + original background music), built
with `engine/reel.py`, scheduled as Facebook REEL + Instagram REEL in Metricool.

Each reel covers **one service**, and the two in a week cover two different ones. Data
collection is no longer the standing subject: it is one entry in the rotation like the rest.
Work down this list and start again at the top, so no service waits more than a few weeks:

1. إعداد الرسائل والأطاريح من العنوان حتى المناقشة
2. خطة البحث (Proposal) ومشكلة الدراسة
3. جمع البيانات: بيانات بورصة عمان المالية
4. جمع البيانات: الاستبيانات الإلكترونية عبر Google Forms
5. التحليل الإحصائي وربط النتائج بالفرضيات
6. النشر العلمي في Scopus Q1 / Q2 / Q3 / Q4 و Arcif
7. أدوات الدراسة وتحكيمها
8. المراجع والدراسات السابقة
9. التدقيق اللغوي وفحص Turnitin والتنسيق
10. مشاريع تخرج البكالوريوس
11. أبحاث النشر والترقية لأعضاء هيئة التدريس
12. الترجمة المعتمدة والعروض التقديمية

Record each week's two services in `reel-1.json` / `reel-2.json` under a `"service"` key, so
the next run can read the last 3 batches and carry the rotation forward.

File names are `reel-1.json` → `reel-1.mp4` (+ `reel-1-cover.png`) and the same for 2.

### Reel creativity standard (owner, 28 Oct 2026: "٢ ريلز ابداعي" is the week's priority)

The two reels are the most important thing the weekly run produces. Judge them the way the
owner will: in the first second on a phone, does this stop the scroll? Three hard rules:

1. **Each reel is built on a visual idea, not a list of text cards.** Pick a different
   *format* for each of the two, and a format not used in the last 3 batches. Formats worth
   building, each needing its own motion: a countdown or timer driving the edit · a split
   screen comparing two paths · a phone screen being typed into · a document filling itself
   in line by line · a chart drawing itself to a result · a stamp-of-approval climax · a
   journal cover assembling · a checklist ticking off under time pressure · a question
   fired at the viewer and answered · numbers counting up · a path or timeline travelled
   end to end · one object revealed from an unexpected scale.
2. **Extend the engine every week.** Each run adds at least one genuinely new element type
   or animation to `engine/reel.py`. Today's elements are text, pill, whatsapp, logo, card,
   doc, table header/row, ring, grid, cycle; today's animations are up, right, left, pop,
   fade, pulse. Reusing only these means the reel will move like last week's — so write the
   new one the format actually needs (a counter, a typewriter, a wipe, a mask reveal, a
   draw-on line, a camera push, a shake on impact) rather than forcing the idea into the
   existing set.
3. **Check them like the owner would.** Before scheduling, pull a contact sheet of frames
   from both reels and put it beside last week's. If the pacing, layouts or motion look like
   a repeat, rebuild rather than ship it. Also confirm the first second carries a hook on
   its own, with no text clipped and the Arabic shaped correctly.

Music stays original (synthesised in numpy) and there is no voice-over. Keep each reel around
20 seconds, and vary where the CTA lands instead of always closing the same way.

## WhatsApp status versions

`engine/story.py` wraps each feed design into a 1080 × 1920 status image with the WhatsApp
pill. They are not scheduled anywhere: WhatsApp has no publishing API, so the owner posts
them by hand.

## Templates (`engine/templates.py`)

| Template | Look |
|---|---|
| `spotlight_dark` | dark plum, big headline, 4 badges, 3 bullets |
| `steps_light` | light, purple diagonal header, numbered journey (up to 5 steps) |
| `chart_gradient` | purple gradient, white chart card, 3 pill bullets |
| `question_type` | white, giant question mark ring, hook + offer pill |
| `grid_cards` | purple header band, 2 × 3 service cards with icons |
