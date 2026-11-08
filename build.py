#!/usr/bin/env python3
"""Build the DevOps video website into site/ (deployed to GitHub Pages by .github/workflows/pages.yml).

    python3 build.py              # everything
    python3 build.py docker       # only some videos (index and downloads are skipped)

For every video in content/<id>.js it writes:
  site/<id>.html                  the player (narration streamed from site/audio/<id>/)
  site/downloads/<id>.html        ONE self-contained file: narration embedded, works offline, can be emailed
  site/downloads/<id>-voiceover.mp3, -subtitles.srt, -script.txt
  site/downloads/devops-videos-offline.zip   all offline files in one zip
plus site/index.html (library) and site/sw.js (caches watched videos for offline replay).

Narration comes from audio/<id>/manifest.json (made by voice.py). Videos without it use the browser voice.
"""
import base64
import hashlib
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
ENGINE = (ROOT / "engine.html").read_text()
_ic = ENGINE.split("const IC = {")[1].split("};")[0]
ICONS = set(re.findall(r"^\s{2}(\w+): '", _ic, re.M)) | set(re.findall(r",\s(\w+): '", _ic))
WPS, PAD, LEAD = 2.15, 1.4, 0.35
ORDER = ["kubernetes", "docker", "linux", "shell", "python", "ansible", "terraform", "jenkins", "azure-devops",
         "istio", "cncf", "prometheus", "grafana", "elk", "aws", "azure", "gcp"]
SITE_URL = "https://srinivaskona7.github.io/devops-html/"


def load(path):
    out = subprocess.check_output(["node", "-e", f"process.stdout.write(JSON.stringify(require({json.dumps(str(path))})))"])
    d = json.loads(out)
    for s in d["scenes"]:
        s.setdefault("type", "flow" if "nodes" in s else "compare" if "cols" in s else "step")
    return d


def voiceover(d):
    """Attach the narration manifest if every narrated scene has a clip whose text hash still matches."""
    mf = ROOT / "audio" / d["id"] / "manifest.json"
    if not mf.exists():
        return None
    m = json.loads(mf.read_text())
    clips = m["clips"]
    if len(clips) != len(d["scenes"]):
        print(f"  ! {d['id']}: narration is out of date (scene count changed); run voice.py {d['id']}")
        return None
    for i, (s, c) in enumerate(zip(d["scenes"], clips)):
        text = str(s.get("n", "")).strip()
        if bool(text) != bool(c) or (c and not (ROOT / c["f"]).exists()):
            print(f"  ! {d['id']}: scene {i + 1} narration missing; run voice.py {d['id']}")
            return None
        if c and not _hash_ok(c["f"], text):
            print(f"  ! {d['id']}: scene {i + 1} text changed since recording; run voice.py {d['id']}")
            return None
    return m


def _hash_ok(f, text):
    import voice  # same hashing as the generator
    return hashlib.sha256(f"{voice.VOICE_ID}|{voice.MODEL}|{text}".encode()).hexdigest()[:10] in f


def duration(d, vo):
    raw = []
    for i, s in enumerate(d["scenes"]):
        speech = vo["clips"][i]["d"] if vo and vo["clips"][i] else len(str(s.get("n", "")).split()) / WPS
        raw.append(max(s.get("min", 5), LEAD + speech + PAD + (1.2 if s.get("cmd") else 0)))
    ncmd = sum(1 for s in d["scenes"] if s.get("cmd"))
    hold = max(0, min(8, (d.get("target", 0) * 60 * 0.985 - sum(raw)) / ncmd)) if d.get("target") and ncmd else 0
    return sum(raw) + hold * ncmd


def check(d):
    errs = []
    for k, s in enumerate(d["scenes"]):
        tag = f"{d['id']}#{k + 1} {s.get('title', s['type'])}"
        if not s.get("n"):
            errs.append(f"{tag}: missing narration")
        for key in ("items", "nodes"):
            for it in s.get(key, []):
                if it[0] not in ICONS:
                    errs.append(f"{tag}: unknown icon {it[0]}")
        for r in s.get("repos", []):
            if len(r) > 3 and r[3] not in ICONS:
                errs.append(f"{tag}: unknown icon {r[3]}")
        if s.get("icon") and s["icon"] not in ICONS:
            errs.append(f"{tag}: unknown icon {s['icon']}")
    return errs


def page(d, vo, *, offline):
    data = dict(d)
    if vo:
        clips = []
        for c in vo["clips"]:
            if not c:
                clips.append(None)
            elif offline:
                b64 = base64.b64encode((ROOT / c["f"]).read_bytes()).decode()
                clips.append({"f": "data:audio/mpeg;base64," + b64, "d": c["d"]})
            else:
                clips.append(c)
        data["vo"] = {"voice": vo["voice"], "clips": clips}
    if offline:
        data["home"] = SITE_URL
    js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = ENGINE.replace("/*__TITLE__*/", html.escape(d["title"])).replace("/*__ACCENT__*/", d["accent"]) \
        .replace("/*__DATA__*/", js)
    if not offline:  # register the service worker (works only over http/https, so not in offline files)
        out = out.replace("</body>", "<script>if('serviceWorker' in navigator&&location.protocol!=='file:')"
                                      "navigator.serviceWorker.register('sw.js').catch(()=>{});</script>\n</body>")
    return out


def words_timeline(d, vo):
    """Scene start times and per-word times, matching the player, for .srt and the timed script."""
    hold_scenes = [s for s in d["scenes"] if s.get("cmd")]
    raw = []
    for i, s in enumerate(d["scenes"]):
        speech = vo["clips"][i]["d"] if vo and vo["clips"][i] else len(str(s.get("n", "")).split()) / WPS
        raw.append((speech, max(s.get("min", 5), LEAD + speech + PAD + (1.2 if s.get("cmd") else 0))))
    hold = max(0, min(8, (d.get("target", 0) * 60 * 0.985 - sum(r for _, r in raw)) / len(hold_scenes))) \
        if d.get("target") and hold_scenes else 0
    t, rows = 0.0, []
    for s, (speech, dur) in zip(d["scenes"], raw):
        dur += hold if s.get("cmd") else 0
        rows.append((t, dur, speech, s))
        t += dur
    return rows


def srt(d, vo):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    out, n = [], 0
    for start, _dur, speech, s in words_timeline(d, vo):
        toks = str(s.get("n", "")).split()
        if not toks:
            continue
        wts = [max(2, len(re.sub(r"\W", "", w))) + (3 if re.search(r"[,;:]$", w) else 0) +
               (6 if re.search(r"[.!?]$", w) else 0) for w in toks]
        acc, tw, words = LEAD, sum(wts), []
        for w, wt in zip(toks, wts):
            dd = speech * wt / tw
            words.append((w, start + acc, start + acc + dd))
            acc += dd
        chunk = []
        for k, wd in enumerate(words):
            chunk.append(wd)
            if len(chunk) >= 7 or (re.search(r"[.!?,;:]$", wd[0]) and len(chunk) >= 3) or k == len(words) - 1:
                n += 1
                out.append(f"{n}\n{ts(chunk[0][1])} --> {ts(chunk[-1][2])}\n{' '.join(w for w, _, _ in chunk)}\n")
                chunk = []
    return "\n".join(out)


def script(d, vo):
    def tc(x):
        return f"{int(x // 60):02d}:{x % 60:04.1f}"
    lines = [f"{d['title']} - narration script", ""]
    for start, dur, _sp, s in words_timeline(d, vo):
        lines.append(f"{tc(start)}-{tc(start + dur)} | {s.get('title') or s.get('name') or s['type']} | {s.get('n', '')}")
    return "\n".join(lines) + "\n"


def voiceover_mp3(d, vo, dest):
    """One continuous narration track aligned to scene starts (for editors and podcasts)."""
    rows = words_timeline(d, vo)
    inputs, filters = [], []
    for k, ((start, _dur, _sp, _s), c) in enumerate(((r, c) for r, c in zip(rows, vo["clips"]) if c)):
        inputs += ["-i", str(ROOT / c["f"])]
        filters.append(f"[{k}:a]adelay={int(round((start + LEAD) * 1000))}:all=1[a{k}]")
    n = len(filters)
    total = rows[-1][0] + rows[-1][1]
    graph = ";".join(filters) + ";" + "".join(f"[a{k}]" for k in range(n)) + \
        f"amix=inputs={n}:normalize=0,apad=whole_dur={total:.3f}[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[out]", "-ac", "1",
                    "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "128k", str(dest)], check=True)


def card(r):
    dl = f"downloads/{r['id']}"
    extra = (f'<a href="{dl}-voiceover.mp3" download>🎧 MP3</a>' if r["voice"] else "") + \
            f'<a href="{dl}-subtitles.srt" download>CC .srt</a><a href="{dl}-script.txt" download>📝 Script</a>'
    badge = '<span class="v on">🎙 Narrated</span>' if r["voice"] else '<span class="v">🔈 Browser voice</span>'
    return f"""<article class="c" style="--a:{r['accent']}">
<a class="main" href="{r['id']}.html"><span class="k">{html.escape(r['cat'])}</span><b>{html.escape(r['title'])}</b>
<span class="m">{int(r['dur'] // 60)}:{int(r['dur'] % 60):02d} · {r['scenes']} scenes</span>{badge}
<span class="s">{html.escape(r['sub'])}</span></a>
<div class="dl"><a href="{dl}.html" download>⬇ Offline file</a>{extra}</div></article>"""


def index(rows, zip_mb):
    total = sum(r["dur"] for r in rows)
    narrated = sum(1 for r in rows if r["voice"])
    css = """body{margin:0;background:#070a12;color:#e6e9ef;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
header,main,footer,.help{max-width:1300px;margin:auto;padding-left:24px;padding-right:24px}header{padding-top:28px}
h1{margin:0;font-size:30px}p{color:#9aa4b2;margin:6px 0 0}.top{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
.btn{display:inline-block;padding:9px 14px;border-radius:10px;background:#4f8cff;color:#fff;text-decoration:none;font-weight:700}
.btn.s{background:#151b2a;color:#e6e9ef;border:1px solid rgba(255,255,255,.12)}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:14px;padding-top:18px;padding-bottom:24px}
.c{display:flex;flex-direction:column;border-radius:14px;background:#0f1420;border:1px solid rgba(255,255,255,.08);border-top:4px solid var(--a);transition:.15s}
.c:hover{transform:translateY(-2px);border-color:var(--a)}.main{display:flex;flex-direction:column;gap:6px;padding:16px;color:inherit;text-decoration:none;flex:1}
.k{font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--a)}.c b{font-size:18px}
.m{font-family:"SF Mono",Menlo,monospace;font-size:13px;color:#c9d1dc}.s{color:#9aa4b2;font-size:13.5px}
.v{align-self:flex-start;font-size:12px;padding:2px 8px;border-radius:999px;background:#151b2a;color:#9aa4b2}.v.on{background:rgba(63,185,80,.15);color:#3fb950}
.dl{display:flex;flex-wrap:wrap;gap:6px;padding:0 16px 14px}.dl a{font-size:12.5px;color:#c9d1dc;text-decoration:none;padding:4px 8px;border-radius:8px;background:#151b2a}
.dl a:hover{color:#fff;background:#1f2738}.help{color:#9aa4b2;padding-bottom:10px}.help summary{cursor:pointer;color:#e6e9ef;font-weight:700}
.help li{margin:4px 0}footer{text-align:center;color:#9aa4b2;padding-bottom:30px}"""
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DevOps video library · kona-srinivas-devops</title><meta name="description" content="{len(rows)} hands-on DevOps explainer videos with narration, captions and offline downloads.">
<style>{css}</style></head><body>
<header><h1>DevOps video library</h1>
<p>{len(rows)} hands-on explainer videos · {int(total // 3600)} h {int(total % 3600 // 60)} min · {narrated} narrated with a recorded voice, the rest use your browser's voice. Captions, 1–4× speed and MP4 export in every video.</p>
<div class="top"><a class="btn" href="downloads/devops-videos-offline.zip" download>⬇ Download all for offline ({zip_mb:.0f} MB zip)</a>
<a class="btn s" href="https://github.com/srinivaskona7/devops-html">Source on GitHub</a></div></header>
<main>{''.join(card(r) for r in rows)}</main>
<details class="help"><summary>How to listen and download</summary><ul>
<li><b>Sound:</b> press ▶ Play once; browsers start audio only after a click. Use the 🔊 button or M to mute.</li>
<li><b>Voice:</b> narrated videos play the recorded voice; pick a browser voice in the voice menu if you prefer.</li>
<li><b>Offline file:</b> one HTML file with the narration inside. Save it, copy it to any computer, open it in Chrome or Edge. No internet needed.</li>
<li><b>MP4 video:</b> open a video, choose ⬇ Download video. It records in real time (a 10-minute video takes 10 minutes); keep the tab visible.</li>
<li><b>Replay offline:</b> videos you have watched on this site are cached and play again without a connection.</li>
</ul></details>
<footer>kona-srinivas-devops</footer></body></html>"""


SW = """// Caches pages and narration as you watch, so they replay offline. Bump VERSION to refresh everything.
const VERSION = '__VERSION__', CACHE = 'devops-videos-' + VERSION;
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./', 'index.html']))); });
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin || u.pathname.includes('/downloads/') || e.request.headers.has('range')) return;
  const page = e.request.mode === 'navigate';
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(e.request);
    const net = fetch(e.request).then(r => { if (r.ok && r.status === 200) c.put(e.request, r.clone()); return r; });
    if (page) return net.catch(() => hit || c.match('index.html'));   // pages: fresh first, cache when offline
    return hit || net;                                                // audio clips: immutable, cache first
  }));
});
"""


def main():
    only = set(sys.argv[1:])
    if not only and SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "downloads").mkdir(parents=True, exist_ok=True)
    rows, bad = [], []
    for f in sorted((ROOT / "content").glob("*.js")):
        d = load(f)
        if only and d["id"] not in only:
            continue
        bad += check(d)
        vo = voiceover(d)
        (SITE / f"{d['id']}.html").write_text(page(d, vo, offline=False))
        (SITE / "downloads" / f"{d['id']}.html").write_text(page(d, vo, offline=True))
        (SITE / "downloads" / f"{d['id']}-subtitles.srt").write_text(srt(d, vo))
        (SITE / "downloads" / f"{d['id']}-script.txt").write_text(script(d, vo))
        if vo:
            shutil.copytree(ROOT / "audio" / d["id"], SITE / "audio" / d["id"], dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("manifest.json"))
            voiceover_mp3(d, vo, SITE / "downloads" / f"{d['id']}-voiceover.mp3")
        dur = duration(d, vo)
        rows.append(dict(id=d["id"], title=d["title"], sub=d.get("sub", ""), cat=d.get("cat", ""), accent=d["accent"],
                         dur=dur, scenes=len(d["scenes"]), voice=bool(vo)))
        print(f"{d['id']:<14} {int(dur // 60):>2}:{int(dur % 60):02d}  scenes {len(d['scenes']):>3}  "
              f"{'narrated' if vo else 'browser voice'}")
    if bad:
        print("\nISSUES:\n" + "\n".join(bad))
        sys.exit(1)
    if only:
        return
    rows.sort(key=lambda r: ORDER.index(r["id"]) if r["id"] in ORDER else 99)
    zpath = SITE / "downloads" / "devops-videos-offline.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for r in rows:
            z.write(SITE / "downloads" / f"{r['id']}.html", f"devops-videos/{r['id']}.html")
            z.write(SITE / "downloads" / f"{r['id']}-subtitles.srt", f"devops-videos/subtitles/{r['id']}.srt")
        z.writestr("devops-videos/README.txt", "Open any .html file in Chrome or Edge. The narration is inside each "
                   "file, so no internet is needed.\nOnline library: " + SITE_URL + "\n")
    zip_mb = zpath.stat().st_size / 1e6
    (SITE / "index.html").write_text(index(rows, zip_mb))
    stamp = hashlib.sha256("".join(sorted(p.name + str(p.stat().st_size) for p in SITE.rglob("*") if p.is_file()))
                           .encode()).hexdigest()[:12]
    (SITE / "sw.js").write_text(SW.replace("__VERSION__", stamp))
    (SITE / ".nojekyll").write_text("")
    (SITE / "404.html").write_text('<!DOCTYPE html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=./">'
                                   '<title>Not found</title><a href="./">Back to the video library</a>')
    size = sum(p.stat().st_size for p in SITE.rglob("*") if p.is_file()) / 1e6
    print(f"\nsite/: {len(rows)} videos, {sum(r['voice'] for r in rows)} narrated, {size:.1f} MB "
          f"(offline zip {zip_mb:.1f} MB)")


if __name__ == "__main__":
    main()
