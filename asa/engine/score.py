"""
A score composed from the camera path, for one-shot reels.

The old track was a loop that ran regardless of what the picture did, with a
boom dropped at each station arrival. Because the camera's holds and travels
were not on the tempo, every boom landed between beats and fought the drums —
which is what "the music and effects don't match" meant.

Here the picture sets the music:

  hold    the groove plays — melody phrase over the mood's drum pattern — and the
          phrase restarts at every station so each one is a musical sentence
  travel  drums drop out and a riser builds (filtered noise + a rising tone)
          that lands exactly on the next arrival
  arrival a sub boom plus a gold chime cluster, timed with the light sweep; the
          bed ducks under it for a third of a second
  ending  a held tonic chord swells in and the drums stop, so the reel resolves
          instead of being cut off mid-loop

For this to lock, the camera's holds and travels must be whole beats and the
bar grid must start where the camera does: build_oneshot.py quantises them and
passes `lead` here as the bar offset.
"""
import math
import wave

import numpy as np

import reel as R

SR = 44100


def _env(n, a=0.01, d=0.3):
    """Attack/decay envelope in samples."""
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / max(d, 1e-4))


def _tone(fr, n, kind, rng, bright=1.0):
    pt = np.arange(n) / SR
    return R._lead_tone(kind, fr, pt, rng) * bright


def _add(out, s0, sig):
    ln = min(len(sig), len(out) - s0)
    if s0 >= 0 and ln > 0:
        out[s0:s0 + ln] += sig[:ln]


def compose(path, keys, seconds, bpm=120, mood="resolve", seed=1, lead=0.5):
    m = R.MOODS.get(mood, R.MOODS["resolve"])
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    beat = 60 / bpm
    base = m["root"]
    scale = [base * 2 ** (s / 12) for s in m["semis"]]
    bed = np.zeros(n, dtype=np.float32)
    fx = np.zeros(n, dtype=np.float32)

    holds = [(keys[i][0], keys[i + 1][0]) for i in range(0, len(keys) - 1, 2)]
    travels = [(keys[i][0], keys[i + 1][0]) for i in range(1, len(keys) - 1, 2)]
    arrivals = [k[0] for k in keys[::2]]
    last_hold = holds[-1]

    # --- bed: pad under everything, rising a little toward the end
    pad = (np.sin(2 * np.pi * base / 2 * t) + 0.5 * np.sin(2 * np.pi * base * 0.75 * t)
           + 0.35 * np.sin(2 * np.pi * base * 1.5 * t))
    swell = 0.045 + 0.03 * np.clip((t - last_hold[0]) / 2.0, 0, 1)
    bed += (pad * swell).astype(np.float32)

    # --- holds: drums on the bar grid (offset by lead) + a melodic sentence
    pattern = R.DRUMS.get(m["drum"], R.DRUMS["maqsum"])
    phrase = m["phrase"]
    for hi, (h0, h1) in enumerate(holds):
        final = hi == len(holds) - 1
        # drums: only bars that start inside this hold; the last hold gets one bar then rests
        bar = beat * 4
        b0 = math.ceil((h0 - lead) / bar - 1e-6)
        b = b0
        while (bt := lead + b * bar) < h1 - 1e-6:
            if final and b > b0:
                break
            for kind, off in pattern:
                s0 = int((bt + off * beat) * SR)
                if s0 >= n or bt + off * beat >= h1:
                    continue
                ln = min(int(0.3 * SR), n - s0)
                pt = np.arange(ln) / SR
                if kind == "dum":
                    bed[s0:s0 + ln] += 0.34 * np.exp(-pt * 14) * np.sin(
                        2 * np.pi * (70 + 60 * np.exp(-pt * 25)) * pt)
                else:
                    bed[s0:s0 + ln] += 0.09 * np.exp(-pt * 45) * rng.standard_normal(ln)
                    bed[s0:s0 + ln] += 0.07 * np.exp(-pt * 30) * np.sin(2 * np.pi * 420 * pt)
            b += 1
        # melody: eighth-notes from the phrase, restarting here, resolving on the tonic
        k, pos = 0, h0 + beat * 0.5
        while pos < h1 - beat * 0.9:
            idx = phrase[k % len(phrase)] + (2 if (hi % 2) else 0)
            fr = scale[min(idx, len(scale) - 1)] * 2
            ln = min(int(0.55 * SR), n - int(pos * SR))
            if ln > 0 and k % 8 != 7:
                _add(bed, int(pos * SR), 0.085 * m["bright"] * _tone(fr, ln, m["lead"], rng))
            pos += beat / 2
            k += 1
        res = int(max(h1 - beat, h0) * SR)
        _add(bed, res, 0.11 * m["bright"] * _tone(scale[0] * 2, int(1.1 * SR), m["lead"], rng))

    # --- travels: riser that lands on the arrival
    for (t0, t1) in travels:
        d = t1 - t0
        s0, ln = int(t0 * SR), int(d * SR)
        pt = np.arange(ln) / SR
        p = pt / d
        noise = rng.standard_normal(ln)
        # crude high-pass sweep: difference filter with rising emphasis
        hp = np.diff(noise, prepend=0.0) * (0.3 + 0.7 * p) + noise * 0.15 * (1 - p)
        riser = hp * (0.02 + 0.16 * p ** 2.2)
        sweep = np.sin(2 * np.pi * (base * 2) * (pt + 0.9 * d * p ** 2)) * (0.03 + 0.07 * p ** 2)
        _add(fx, s0, (riser + sweep).astype(np.float32))

    # --- arrivals: boom + gold chime, with the bed ducked underneath
    duck = np.ones(n, dtype=np.float32)
    for i, at in enumerate(arrivals):
        s0 = int(at * SR)
        ln = min(int(1.4 * SR), n - s0)
        if ln <= 0:
            continue
        pt = np.arange(ln) / SR
        boom = 0.6 * np.exp(-pt * 6) * np.sin(2 * np.pi * (46 + 100 * np.exp(-pt * 18)) * pt)
        _add(fx, s0, boom.astype(np.float32))
        # chime cluster: tonic, fifth, octave, third — a bell each, staggered 0..70 ms
        strong = (i == 0 or i == len(arrivals) - 1)
        for j, deg in enumerate([0, 4, 7, 9][: 4 if strong else 3]):
            fr = scale[min(deg, len(scale) - 1)] * 4
            st = s0 + int(j * 0.023 * SR)
            lc = min(int(1.6 * SR), n - st)
            _add(fx, st, (0.12 if strong else 0.085) * _env(lc, 0.004, 0.55) *
                 _tone(fr, lc, "bell", rng))
        d0, d1 = s0, min(n, s0 + int(0.35 * SR))
        duck[d0:d1] = np.minimum(duck[d0:d1], 0.45 + 0.55 * np.linspace(0, 1, d1 - d0) ** 2)

    # --- ending: tonic chord swells through the last hold, nothing else fights it
    e0 = int(last_hold[0] * SR)
    ln = n - e0
    pt = np.arange(ln) / SR
    chord = sum(np.sin(2 * np.pi * scale[d] * 2 * pt) for d in (0, 4, 7)) / 3
    chord *= np.minimum(1, pt / 1.6) * 0.14 * (1 - np.clip((pt - (seconds - last_hold[0]) + 1.2) / 1.2, 0, 1))
    _add(bed, e0, chord.astype(np.float32))

    out = bed * duck + fx
    out *= np.minimum(1, t / 0.6) * np.minimum(1, (seconds - t) / 0.9)
    out /= max(1e-6, np.abs(out).max()) / 0.9
    out = 0.92 * np.tanh(out * 1.05) / np.tanh(1.05)
    st = np.stack([out, out], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype("<i2").tobytes())
