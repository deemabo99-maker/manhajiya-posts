# أكاديمية العلماء العرب للاستشارات والتدريب — دليل الهوية والمحتوى

Source of truth for every weekly batch. Read it in full before writing copy or rendering.

## Identity

- **Name:** أكاديمية العلماء العرب للاستشارات والتدريب
- **Emblem:** `brand/emblem.png` (hexagon cut from `brand/logo-original.jpg`). Use with the
  wordmark via `Canvas.lockup()`; never stretch or recolour it.
- **Look:** must be completely different from المنهجية (no purple/neon). Ivory paper,
  deep emerald, gold foil, the emblem's ribbon red as accent, eight-point-star (girih)
  lattices, mihrab arches, laurel wreaths, gold double frames, classical calligraphy.
- **Format:** feed posts 1080 × 1350 PNG; reels 1080 × 1920 MP4; status 1080 × 1920 PNG.

### Palette (`engine/kit.py` → `C`)
Emerald #0F5236 · Forest #164A2F · Deep #0B2E1E · Night #071C13 · Jade #2E8B57 ·
Gold #C8A02E / light #EED9A0 / dark #8C6A1F · Ivory #FBF8F1 · Cream #F6F0E2 · Sand #EADFC6 ·
Ink #1F2A24 · Red #B23A3A · WhatsApp #1FAF5A.

### Fonts (`brand/fonts`, SIL OFL)
**Owner's rule (26 Oct 2026): text must be clear and easy to read — no calligraphic or
decorative fonts.** Everything uses **Cairo** (Black 900 for headlines, ExtraBold/Bold for
sub-heads and body); Almarai is the fallback. The old style names in `engine/kit.py`
(ruqaa, messiri, kufi, rakkas, naskh…) are aliases that all map to Cairo.

## People photos (owner, 26 Oct 2026)

- Use photos of **young men only (no women)**, good-looking, modern, Arab look; graduation
  gowns use the brand's emerald-and-gold stole.
- Source: Canva (owner's Canva Pro account, connected to Claude). Generate with Canva AI
  (`generate-image`), remove backgrounds with `remove-background`, place them on a scratch
  holder design, export PNG, download through the built-in browser on the owner's laptop
  (Downloads), then stage them into `brand/people/` (`*.png` cut-outs, `*.jpg` framed photos).
- Every week: at least 4 of the 7 posts and both reels feature a person; generate new people
  photos regularly so faces don't repeat every week.
- Current library: grad-man, twograds, phone, journal, stressed (cut-outs); analyst, laptop
  (framed).

## Contact (on every design and every caption)

- Phone / WhatsApp: **+962 77859 7330** (caption form 00962778597330, link wa.me/962778597330)
- Email: **asaforconsultingandtraining@gmail.com**
- Instagram: **@asa_for_training** (shown in every footer)
- Online for students across the Arab world.

## Approved claims (from the owner's own ads)
- أكثر من 5000 عمل بحثي تم الإشراف عليه (+5000)
- أكثر من 100 باحث متخصص
- Slogan: طريقك نحو التميز الأكاديمي يبدأ هنا
No other numbers, prices or guarantees.

## Services (same as المنهجية, owner confirmed 26 Oct 2026)
Theses and dissertations from title to defence · title suggestions · research plan
(proposal) · theoretical framework and previous studies · references · study tools and
their validation · questionnaires / data collection · statistical analysis and interpretation ·
publishing in Scopus (always Q1 / Q2 / Q3 / Q4) and Arcif · promotion research for faculty ·
proofreading, formatting, Turnitin check, certified translation, PowerPoint for the defence,
online training courses.

## Weekly output (owner's request)
- **7 image posts + 7 captions**, **2 reels** (owner: "be creative with them"), and WhatsApp
  status versions of the 7 posts.
- Every design distinctive, innovative and eye-catching; never reuse last week's template;
  write new templates in `engine/templates.py`; alternate ivory / emerald / night backgrounds.
- Reels: motion graphics + original music (no voice-over); new hook, new layouts, new motion
  each week (`engine/reel.py`).

## Captions
Hook → problem the student recognises → services (✅ / numbered) → push (first consultation
free) → contact block exactly:

```
📞 للتواصل والاستفسار:
📱 رقم الهاتف: 00962778597330
💬 تواصل معنا مباشرة عبر واتساب: wa.me/962778597330
📧 البريد الإلكتروني: asaforconsultingandtraining@gmail.com
```
then 6–8 hashtags starting with #أكاديمية_العلماء_العرب.

## Publishing (owner uploads by hand; automation via Make agreed 1 Nov 2026)

What was ruled out, by testing rather than assumption:

- Meta Business Suite only accepts media through the operating system's file-picker dialog.
  Desktop control cannot click inside it — browsers are granted read-only and Claude's own
  app window cannot be granted at all, so the dialog is unreachable by design.
- Injecting the media into the Facebook page with JavaScript is refused by the safety
  classifier, and Facebook's CSP blocks the page from fetching media from any outside host.
- No connector in the registry publishes organic posts to Facebook or Instagram. Adspirer
  covers paid Meta Ads campaigns, not posts; Supermetrics and vidIQ are analytics/research.
- Buffer, Publer and Later have no connector at all.

**The governing constraint (measured 1 Nov 2026):** a cloud session's egress allowlist
refuses `graph.facebook.com`, `hooks.zapier.com`, `make.com`, `api.publer.io` and
`api.bufferapp.com` alike, so Claude cannot call any publishing API directly. MCP connectors
are not subject to it — they are routed by Anthropic, not through the sandbox. Hence the
rule: **a service with a connector works; a service that needs a direct HTTP call does not.**
The owner can lift this for one host via claude.ai → Settings → Capabilities, which is what
would open the free, no-middleman Meta Graph API route.

Metricool has a connector and does publish, but the account holds one brand and it is
المنهجية's (`methodology_center`); أكاديمية العلماء العرب is not a brand there, so there is
no destination to schedule to without a paid upgrade.

**Agreed route (1 Nov 2026): Make.** It has a connector, native Facebook Page and Instagram
Business publishing modules, and `scenarios_create`/`scenarios_run`, so Claude can build the
scenario as well as trigger it. The owner connects Make and authorises the academy's Page and
Instagram inside it; Claude then schedules each week from `posts/batch-NN/manifest.json`.
Until that is connected, **Claude prepares, the owner uploads.** Every run ends with all
three of these:

1. **Files on the owner's laptop** at `C:\Users\user\Downloads\ASA-weekNN` via
   `device_commit_files` — only when the laptop is linked to the session. If it is not,
   skip this silently and say so in the report; the owner picks the files up later.
2. **A published artifact page**: each design with its caption underneath, a copy button per
   caption, the story version beside it, the reels playable, and each item's file name and
   scheduled day and time. Build it from a generator script, publish the display copies as
   the artifact's `files` (external images are blocked by the artifact CSP, so never hotlink
   them). This page is what the owner actually works from, and it reaches them on any device.
3. **`SendUserFile`** with the designs, the stories, the reels and `captions.md`, so the
   originals are in the conversation too.

Slots the owner follows: one design a day at 10:00, and the two reels at 19:00 on the two
days that already carry a design. Push notification on every run — the owner reads it on
their phone.

The rendered PNGs and MP4s **are** committed from batch-02 onwards (owner's call,
1 Nov 2026). Automated publishing needs a public URL per asset, and this repository's
`raw.githubusercontent.com` links are it — so the repo must stay public or the links die.
`engine/manifest.py` turns a batch into `manifest.json`: every item with its media URL, its
caption and its publish time in Asia/Amman, derived from the batch JSON so it can never drift
from what was rendered. Cost: roughly 22 MB a week; prune old batches when the repo gets
heavy. `content.json`, `reel-N.json` and `captions.md` stay committed as before, so the next
run can read the last three batches and avoid repeating itself.

## Commands
```bash
python3 engine/render.py posts/batch-NN
python3 engine/story.py  posts/batch-NN
python3 engine/reel.py   posts/batch-NN/reel-1.json posts/batch-NN/reel-1.mp4
```

## Paid ad reels

Meta ad reels follow the shared standard in  (repo root), not the weekly
rules above. This brand's ad folders are .

## Who the copy speaks to (owner, 1 Nov 2026)

Every ad and post addresses **men and women alike**. Write no gendered second
person: no أنتَ and no أنتِ, no ـكَ / ـكِ ending, no feminine ـين verb
("تدخلينها"). Rephrase instead of picking a side — "ويومُ مناقشةٍ بثقةٍ واستعداد"
rather than "ومناقشةٌ تدخلها/تدخلينها". Unvocalised forms such as "رسالتك" and
"نرافقك" are already neutral on the page and are fine.

The owner caught a narration line written in the feminine while the same line was
masculine on screen, so the two forms of a line must be checked against each
other, not only each on its own. `asa/engine/voscript.py` refuses to print a
recording script that contains a gendered address.

## Voice-over

Reels may carry narration. A spec's `vo` list holds, per line, `t` (start, in
seconds), `text` (vocalised — espeak-ng needs the harakat and mispronounces bare
Arabic) and `read` (the plain twin a person reads aloud). On-screen text is never
vocalised; harakat belong only in `text`.

The owner heard the free synthetic voice (ar_JO-kareem, the only Arabic voice on
any host this sandbox can reach) and rejected it. **The narration is the owner's
own recording.** `asa/engine/voscript.py` prints the script with the seconds
available per line; the owner records it on a phone and sends the file back, and
`mix_voice` in `asa/engine/reel.py` lays it in and ducks the music under it.

Voice cloning is not possible here and must not be promised: every toolkit that
does it needs PyPI or HuggingFace, and both are unreachable from the sandbox
(verified 1 Nov 2026). It is also unnecessary — an ad is a handful of lines, and
a real recording beats a cloned one.
