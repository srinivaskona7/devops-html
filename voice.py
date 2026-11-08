#!/usr/bin/env python3
"""Generate recorded narration for videos with Fish Audio (one clip per scene).

    python3 voice.py docker            # one video
    python3 voice.py --all             # every video in content/
    python3 voice.py docker --dry-run  # show what would be generated and the character count

Clips are cached by text hash: re-running only generates scenes whose narration changed.
Output: audio/<id>/NN-<hash>.mp3 (trimmed, loudness-normalised, 44.1 kHz mono) and audio/<id>/manifest.json.
The API key is read from ~/.fishaudio_key (or FISH_API_KEY); it is never written to the repository.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).parent
VOICE_ID = os.environ.get("FISH_VOICE_ID", "eec927c9d59c4c62ae0cc07e83449f09")
MODEL = os.environ.get("FISH_MODEL", "s2.1-pro-free")
API = "https://api.fish.audio/v1/tts"
# Trim leading/trailing silence, then normalise to -16 LUFS (podcast/YouTube loudness) so every clip sounds equal.
FILTER = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse,"
          "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse,"
          "loudnorm=I=-16:TP=-1.5:LRA=11")


def key() -> str:
    k = os.environ.get("FISH_API_KEY") or (pathlib.Path.home() / ".fishaudio_key").read_text().strip()
    if not k:
        sys.exit("No Fish Audio key: set FISH_API_KEY or write it to ~/.fishaudio_key")
    return k


def load(vid: str) -> dict:
    path = ROOT / "content" / f"{vid}.js"
    out = subprocess.check_output(["node", "-e", f"process.stdout.write(JSON.stringify(require({json.dumps(str(path))})))"])
    return json.loads(out)


def tts(text: str, api_key: str, attempts: int = 5) -> bytes:
    body = json.dumps({"text": text, "reference_id": VOICE_ID, "format": "mp3", "mp3_bitrate": 192,
                       "normalize": True, "latency": "normal"}).encode()
    for n in range(attempts):
        req = urllib.request.Request(API, data=body, method="POST", headers={
            "Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "model": MODEL})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
                if len(data) > 1000:
                    return data
                raise RuntimeError(f"tiny response ({len(data)} bytes)")
        except urllib.error.HTTPError as e:
            msg = e.read()[:200].decode(errors="replace")
            if e.code in (400, 401, 402, 403):
                raise SystemExit(f"Fish Audio refused the request: HTTP {e.code} {msg}") from None
            err = f"HTTP {e.code} {msg}"
        except Exception as e:  # network errors, timeouts
            err = f"{type(e).__name__}: {e}"
        wait = 3 * 2 ** n
        print(f"    retry {n + 1}/{attempts} in {wait}s ({err})", flush=True)
        time.sleep(wait)
    raise RuntimeError(f"TTS failed after {attempts} attempts")


def clean(raw: bytes, dest: pathlib.Path) -> float:
    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
        tmp.write(raw)
        tmp.flush()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp.name, "-af", FILTER, "-ar", "44100", "-ac", "1",
                        "-c:a", "libmp3lame", "-b:a", "128k", str(dest)], check=True)
    return duration(dest)


def duration(p: pathlib.Path) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "default=nw=1:nk=1", str(p)])
    return round(float(out), 3)


def run(vid: str, dry: bool, api_key: str | None, workers: int) -> dict:
    d = load(vid)
    folder = ROOT / "audio" / vid
    folder.mkdir(parents=True, exist_ok=True)
    jobs, scenes = [], []
    for i, s in enumerate(d["scenes"]):
        text = str(s.get("n", "")).strip()
        if not text:
            scenes.append(None)
            continue
        h = hashlib.sha256(f"{VOICE_ID}|{MODEL}|{text}".encode()).hexdigest()[:10]
        f = folder / f"{i + 1:02d}-{h}.mp3"
        scenes.append((f, text))
        if not f.exists():
            jobs.append((i, f, text))
    chars = sum(len(t) for _, _, t in jobs)
    print(f"{vid}: {len(d['scenes'])} scenes, {len(jobs)} to generate ({chars:,} characters)", flush=True)
    if dry:
        return {}

    def work(job):
        i, f, text = job
        t0 = time.time()
        dur = clean(tts(text, api_key), f)
        print(f"  scene {i + 1:>2}: {dur:6.2f}s audio  ({time.time() - t0:4.1f}s)", flush=True)

    with cf.ThreadPoolExecutor(workers) as pool:
        list(pool.map(work, jobs))

    keep = {f.name for f, _ in filter(None, scenes)}
    for old in folder.glob("*.mp3"):  # remove clips for narration that no longer exists
        if old.name not in keep:
            old.unlink()
    manifest = {"voice": "Kona Srinivas (Fish Audio)", "model": MODEL, "clips": [
        None if sc is None else {"f": f"audio/{vid}/{sc[0].name}", "d": duration(sc[0])} for sc in scenes]}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=1))
    total = sum(c["d"] for c in manifest["clips"] if c)
    print(f"{vid}: done, {total / 60:.1f} min of narration", flush=True)
    return manifest


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    ids = sorted(p.stem for p in (ROOT / "content").glob("*.js")) if "--all" in sys.argv else args
    if not ids:
        sys.exit(__doc__)
    k = None if dry else key()
    for v in ids:
        run(v, dry, k, workers=int(os.environ.get("FISH_WORKERS", "3")))
