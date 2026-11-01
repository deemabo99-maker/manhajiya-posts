# نظام الريلز الإعلانية (Meta Ads)

Both brands share one ad standard. It lives at **`brand/ADS.md`** in the repo root — read
that file, not a copy of it.

This brand's own look, palette, fonts (Cairo, weight 600+), the young-men-only rule for
people photos, the approved claims ("أكثر من 5000 عمل بحثي"، "أكثر من 100 باحث") and the
contact block still come from `asa/brand/BRAND.md`.

Ad folders for this brand are `asa/posts/ads-NN`. Build from the repo root:

```bash
python3 engine/ads.py asa/posts/ads-NN/<stem>.json
```
