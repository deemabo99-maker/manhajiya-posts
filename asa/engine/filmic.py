"""
The finish that separates a reel from a slideshow.

Everything here runs on the composed frame, after the scene has been drawn:

- `drift`   a slow push or pan that never stops. The single biggest tell of an
            amateur reel is that elements arrive and then sit perfectly still;
            real footage is always moving a little.
- `grain`   animated film grain. Flat vector fills read as clip-art; a little
            moving grain reads as camera.
- `vignette` darkens the corners so the eye goes to the middle.
- `sweep`   a band of light travelling across a sprite, for gold type.

Kept apart from reel.py so both brands' engines can use the same finish.
"""
import math

import numpy as np
from PIL import Image

RW, RH = 1080, 1920

_grain_cache = {}
_vig_cache = {}


def drift(frame, t, dur, kind="push", amount=0.06, angle=0.0):
    """Crop a slowly changing window out of the frame and blow it back up.

    kind: push (in), pull (out), pan (sideways), or float (a slow drifting arc).
    amount: how far it travels over the scene, as a fraction of the frame.
    """
    if amount <= 0:
        return frame
    p = max(0.0, min(1.0, t / max(dur, 1e-3)))
    e = p * p * (3 - 2 * p)                       # ease so the move settles

    if kind == "pull":
        z = 1 + amount * (1 - e)
        ox = oy = 0.0
    elif kind == "pan":
        z = 1 + amount
        ox = (e - 0.5) * amount * RW * math.cos(angle)
        oy = (e - 0.5) * amount * RH * math.sin(angle) * 0.4
    elif kind == "float":
        z = 1 + amount * 0.7
        ox = math.sin(t * 0.55 + angle) * amount * RW * 0.25
        oy = math.cos(t * 0.4 + angle) * amount * RH * 0.12
    else:                                          # push
        z = 1 + amount * e
        ox = oy = 0.0

    w, h = RW / z, RH / z
    l = min(max((RW - w) / 2 + ox, 0), RW - w)
    tp = min(max((RH - h) / 2 + oy, 0), RH - h)
    return frame.crop((int(l), int(tp), int(l + w), int(tp + h))).resize((RW, RH), Image.BICUBIC)


def _grain_tile(seed):
    if seed not in _grain_cache:
        rng = np.random.default_rng(seed)
        _grain_cache[seed] = rng.normal(0, 1, (RH // 2, RW // 2)).astype(np.float32)
    return _grain_cache[seed]


def grain(frame, t, strength=5.0):
    """Animated grain. Four tiles cycled so it moves without regenerating noise."""
    if strength <= 0:
        return frame
    g = _grain_tile(int(t * 24) % 4)
    g = np.repeat(np.repeat(g, 2, axis=0), 2, axis=1)[:RH, :RW]
    a = np.asarray(frame).astype(np.float32)
    a[..., :3] += (g * strength)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), frame.mode)


def _vignette(power):
    if power not in _vig_cache:
        y, x = np.mgrid[0:RH, 0:RW]
        nx = (x - RW / 2) / (RW / 2)
        ny = (y - RH / 2) / (RH / 2)
        r = np.sqrt(nx ** 2 + ny ** 2) / math.sqrt(2)
        _vig_cache[power] = np.clip(1 - power * r ** 2.2, 0, 1).astype(np.float32)
    return _vig_cache[power]


def vignette(frame, power=0.38):
    if power <= 0:
        return frame
    a = np.asarray(frame).astype(np.float32)
    a[..., :3] *= _vignette(power)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), frame.mode)


def finish(frame, t, dur, motion=None, grain_strength=5.0, vig=0.38):
    """One call for the whole finish, in the order the eye expects."""
    if motion:
        frame = drift(frame, t, dur, motion.get("kind", "push"),
                      motion.get("amount", 0.06), motion.get("angle", 0.0))
    frame = vignette(frame, vig)
    return grain(frame, t, grain_strength)


def scrim(size, top=0.0, bottom=0.78, color=(4, 16, 11)):
    """A vertical darkening wash, so text stays readable over a photograph."""
    w, h = size
    ramp = np.linspace(top, bottom, h, dtype=np.float32)[:, None]
    layer = np.zeros((h, w, 4), dtype=np.float32)
    layer[..., 0], layer[..., 1], layer[..., 2] = color
    layer[..., 3] = ramp * 255
    return Image.fromarray(layer.astype(np.uint8), "RGBA")


def cover(img, size):
    """Fill `size` completely with `img`, cropping the overflow — never letterboxed."""
    w, h = size
    iw, ih = img.size
    k = max(w / iw, h / ih)
    nw, nh = int(iw * k + 0.5), int(ih * k + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    return img.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))
