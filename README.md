# manhajiya-posts

Weekly social-media posts for **المنهجية للخدمات البحثية والعلمية** (Facebook + Instagram).

- `brand/` — logo, fonts and the brand & content guide (`BRAND.md`)
- `engine/` — the drawing kit and post templates (Python + Pillow with libraqm)
- `posts/batch-NN/` — each week's `content.json`, rendered PNGs and `captions.md`

Render a batch:

```bash
python3 engine/render.py posts/batch-01
```

Images in this public repository are what Metricool pulls when it publishes the posts.
