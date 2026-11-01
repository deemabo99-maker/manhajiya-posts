"""
Arabic voice-over for the reels.

A reel spec may carry a `vo` list:

    "vo": [{"t": 0.3, "text": "فِي أَكَادِيمِيَّةِ العُلَمَاءِ العَرَبِ..."}, ...]

`t` is the start time in seconds, measured from the start of the reel. Each line
is synthesised and laid onto a voice track; `reel.py` ducks the music underneath
it. Write the text WITH harakat: espeak-ng guesses the vowels of unvocalised
Arabic and gets them wrong often enough to matter ("العلماء" comes out as
"ʔalʕlmaːʔ" bare, and correctly as "ʔalʕulamaːʔ" vocalised).

The voice is ar_JO-kareem (Jordanian Arabic, Piper/VITS). Both the espeak-ng
phonemiser and the model are fetched from GitHub release assets on first use and
cached under ~/.cache/asa-voice, because this is the only host the sandbox can
reach — PyPI and HuggingFace are both blocked.
"""
import json
import os
import subprocess
import sys
import tarfile
import urllib.request

import numpy as np

CACHE = os.path.expanduser("~/.cache/asa-voice")
ESPEAK_URL = ("https://github.com/rhasspy/piper/releases/download/"
              "2023.11.14-2/piper_linux_x86_64.tar.gz")
VOICE_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/"
             "tts-models/vits-piper-ar_JO-kareem-medium.tar.bz2")
VOICE_DIR = "vits-piper-ar_JO-kareem-medium"
MODEL = "ar_JO-kareem-medium"

_session = None
_cfg = None


def _fetch(url, name, mode):
    """Download and unpack a release asset once; later runs reuse the cache."""
    os.makedirs(CACHE, exist_ok=True)
    marker = os.path.join(CACHE, "." + name + ".done")
    if os.path.exists(marker):
        return
    archive = os.path.join(CACHE, name)
    print(f"voice: fetching {name}", flush=True)
    urllib.request.urlretrieve(url, archive)
    with tarfile.open(archive, mode) as tf:
        tf.extractall(CACHE)
    os.remove(archive)
    open(marker, "w").close()


def ensure():
    """Make sure the phonemiser and the voice model are on disk. Returns their paths."""
    _fetch(ESPEAK_URL, "piper.tar.gz", "r:gz")
    _fetch(VOICE_URL, "voice.tar.bz2", "r:bz2")
    espeak = os.path.join(CACHE, "piper", "espeak-ng")
    os.chmod(espeak, 0o755)
    return espeak, os.path.join(CACHE, VOICE_DIR)


def _load():
    global _session, _cfg
    if _session is not None:
        return
    import onnxruntime as ort
    _, vdir = ensure()
    base = os.path.join(vdir, MODEL)
    _cfg = json.load(open(base + ".onnx.json", encoding="utf-8"))
    _session = ort.InferenceSession(base + ".onnx", providers=["CPUExecutionProvider"])


def phonemes(text):
    espeak, _ = ensure()
    env = dict(os.environ,
               LD_LIBRARY_PATH=os.path.join(CACHE, "piper"),
               ESPEAK_DATA_PATH=os.path.join(CACHE, "piper", "espeak-ng-data"))
    out = subprocess.run([espeak, "-v", "ar", "-q", "--ipa=3"],
                         input=text, capture_output=True, text=True, env=env, check=True)
    return out.stdout.strip()


def synth(text, length_scale=None):
    """One line of narration as float32 mono at the model's sample rate."""
    _load()
    idmap = _cfg["phoneme_id_map"]
    ids = list(idmap["^"])
    for ch in phonemes(text):
        if ch in idmap:
            ids += idmap[ch] + idmap["_"]
        elif ch == "\n":
            ids += idmap[" "] + idmap["_"]
    ids += idmap["$"]
    inf = _cfg["inference"]
    feed = {
        "input": np.array([ids], dtype=np.int64),
        "input_lengths": np.array([len(ids)], dtype=np.int64),
        "scales": np.array([inf["noise_scale"],
                            length_scale if length_scale else inf["length_scale"],
                            inf["noise_w"]], dtype=np.float32),
    }
    if any(i.name == "sid" for i in _session.get_inputs()):
        feed["sid"] = np.array([0], dtype=np.int64)
    au = _session.run(None, feed)[0].squeeze().astype(np.float32)
    peak = float(np.abs(au).max())
    return au / peak * 0.92 if peak > 1e-6 else au


def sample_rate():
    _load()
    return _cfg["audio"]["sample_rate"]


def track(vo, seconds, sr):
    """Lay every line onto one track, and return it with a 0..1 'voice is talking'
    envelope that reel.py uses to duck the music."""
    n = int(seconds * sr)
    out = np.zeros(n, dtype=np.float32)
    gate = np.zeros(n, dtype=np.float32)
    native = sample_rate()
    for item in vo:
        au = synth(item["text"], item.get("length_scale"))
        if sr != native:
            idx = np.linspace(0, len(au) - 1, int(len(au) * sr / native))
            au = np.interp(idx, np.arange(len(au)), au).astype(np.float32)
        s0 = int(item.get("t", 0) * sr)
        ln = min(len(au), n - s0)
        if ln <= 0:
            continue
        out[s0:s0 + ln] += au[:ln] * item.get("gain", 1.0)
        gate[max(0, s0 - int(0.15 * sr)):s0 + ln + int(0.25 * sr)] = 1.0
    # soften the duck edges so the music swells back instead of jumping
    k = int(0.12 * sr)
    if k > 1:
        gate = np.convolve(gate, np.ones(k) / k, mode="same")
    return out, np.clip(gate, 0, 1)


def fits(vo, scenes):
    """Report lines that run past the scene they belong to, so narration and
    picture do not drift apart. Returns a list of human-readable problems."""
    total = sum(s["dur"] for s in scenes)
    problems = []
    end_prev = 0.0
    for item in sorted(vo, key=lambda v: v.get("t", 0)):
        t0 = item.get("t", 0)
        dur = len(synth(item["text"], item.get("length_scale"))) / sample_rate()
        if t0 < end_prev - 0.05:
            problems.append(f"'{item['text'][:28]}…' starts at {t0:.1f}s, "
                            f"over the previous line which ends at {end_prev:.1f}s")
        if t0 + dur > total + 0.05:
            problems.append(f"'{item['text'][:28]}…' ends at {t0 + dur:.1f}s, "
                            f"past the reel's {total:.1f}s")
        end_prev = t0 + dur
    return problems


if __name__ == "__main__":
    import wave
    text = sys.argv[1] if len(sys.argv) > 1 else "مَرْحَبًا بِكَ فِي أَكَادِيمِيَّةِ العُلَمَاءِ العَرَبِ."
    au = synth(text)
    pcm = (au * 32767).astype("<i2")
    out = sys.argv[2] if len(sys.argv) > 2 else "voice.wav"
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate())
        w.writeframes(pcm.tobytes())
    print(f"{out}  {len(au)/sample_rate():.2f}s")
