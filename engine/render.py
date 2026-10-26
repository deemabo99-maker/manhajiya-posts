"""
Render every post of a batch.

    python3 engine/render.py posts/batch-01

Reads <batch>/content.json and writes <batch>/01.png, 02.png, ...
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import TEMPLATES  # noqa: E402


def main(batch_dir):
    with open(os.path.join(batch_dir, "content.json"), encoding="utf-8") as fh:
        batch = json.load(fh)
    for i, post in enumerate(batch["posts"], start=1):
        name = f"{i:02d}.png"
        canvas = TEMPLATES[post["template"]](post)
        canvas.save(os.path.join(batch_dir, name))
        print("rendered", name, post["template"])


if __name__ == "__main__":
    main(sys.argv[1])
