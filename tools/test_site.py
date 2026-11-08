#!/usr/bin/env python3
"""Browser test of the built site (site/) and the offline downloads. Runs in CI after build.py.

Serves site/ through Playwright request routing at https://pages.test/ (no local server needed), then checks:
library page and links, narrated playback (audio really plays and follows seek/speed/mute), the full narration
track is complete and non-silent, MP4 export gets an audio track, offline files work from file://, and
non-narrated videos still offer the browser voice.
"""
import asyncio
import json
import mimetypes
import pathlib
import re
import subprocess
import sys

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE = "https://pages.test/"
FAILS = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


async def serve(route):
    path = route.request.url[len(BASE):].split("?")[0].split("#")[0] or "index.html"
    f = SITE / path
    if f.is_dir():
        f = f / "index.html"
    if not f.is_file():
        return await route.fulfill(status=404, body="not found")
    ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
    await route.fulfill(status=200, body=f.read_bytes(), headers={"content-type": ctype, "accept-ranges": "none"})

# Record every media play/pause so we can check what the user would hear.
SPY = """
window.__media = [];
const P = HTMLMediaElement.prototype, play = P.play, pause = P.pause;
P.play = function () { window.__media.push(['play', (this.currentSrc || this.src).split('/').pop().slice(0, 40), +this.currentTime.toFixed(2), this.playbackRate]); return play.call(this); };
P.pause = function () { window.__media.push(['pause', (this.currentSrc || this.src).split('/').pop().slice(0, 40)]); return pause.call(this); };
const MR = window.MediaRecorder;
window.MediaRecorder = function (stream, o) { window.__recTracks = { audio: stream.getAudioTracks().length, video: stream.getVideoTracks().length }; return new MR(stream, o); };
window.MediaRecorder.isTypeSupported = MR.isTypeSupported.bind(MR);
"""


async def main():
    narrated = [p.stem for p in (ROOT / "audio").iterdir() if (p / "manifest.json").exists()]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        ctx = await b.new_context(viewport={"width": 1500, "height": 950}, accept_downloads=True)
        await ctx.route(BASE + "**", serve)
        await ctx.add_init_script(SPY)
        pg = await ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))

        # ---------- library page
        await pg.goto(BASE)
        cards = await pg.locator("article.c").count()
        n_content = len(list((ROOT / "content").glob("*.js")))
        ok(cards == n_content, f"library lists all {n_content} videos ({cards})")
        hrefs = await pg.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
        local = [h for h in hrefs if not h.startswith("http")]
        missing = [h for h in local if not (SITE / h).is_file()]
        ok(not missing, f"all {len(local)} library links and downloads exist" + (f": missing {missing}" if missing else ""))
        ok(await pg.locator(".v.on").count() == len(narrated), f"{len(narrated)} video(s) marked narrated: {narrated}")

        for vid in narrated:
            # ---------- narrated player
            await pg.goto(BASE + f"{vid}.html")
            await pg.wait_for_function("window.__reel")
            reel = await pg.evaluate("window.__reel")
            ok(reel["voice"], f"{vid}: player has recorded narration")
            first = await pg.eval_on_selector("#voiceSel", "s => s.options[0] && [s.options[0].value, s.options[0].text, s.value]")
            ok(first and first[0] == "__rec" and first[2] == "__rec", f"{vid}: recorded voice selected by default: {first}")

            vb = await pg.evaluate("window.__voiceBuffer()")
            silent = [i + 1 for i, db in enumerate(vb["scenes"]) if db < -45]
            ok(abs(vb["duration"] - vb["total"]) < 0.05, f"{vid}: narration track {vb['duration']:.1f}s = video {vb['total']:.1f}s")
            ok(not silent, f"{vid}: every scene has audible narration (quietest {min(vb['scenes']):.1f} dBFS)" +
               (f"; silent scenes {silent}" if silent else ""))

            await pg.click("#tap")
            await pg.wait_for_timeout(2500)
            media = await pg.evaluate("window.__media")
            plays = [m for m in media if m[0] == "play"]
            ok(plays and plays[0][1].startswith("01-"), f"{vid}: scene 1 narration starts on play: {plays[:1]}")
            playing = await pg.evaluate("[...document.querySelectorAll('audio')].length >= 0 && window.__media.filter(m => m[0]==='play').length")
            ok(playing >= 1, f"{vid}: audio element playing")

            # seek to scene 5: its own clip must play, from the right offset
            await pg.evaluate("window.__media = []")
            st5 = reel["scenes"][4]["start"]
            await pg.evaluate(f"document.getElementById('seek').value = Math.round(({st5} + 3) / {reel['total']} * 10000);"
                              "document.getElementById('seek').dispatchEvent(new Event('input'))")
            await pg.wait_for_timeout(800)
            media = await pg.evaluate("window.__media")
            p5 = [m for m in media if m[0] == "play" and m[1].startswith("05-")]
            ok(p5 and 2.0 < p5[0][2] < 4.0, f"{vid}: seeking into scene 5 plays clip 05 near 2.6 s: {p5[:1]}")

            await pg.evaluate("window.__media = []")
            await pg.click('#speeds button[data-s="2"]')
            await pg.wait_for_timeout(1500)
            rate = await pg.evaluate("window.__media.filter(m => m[0]==='play').map(m => m[3])")
            t_txt = await pg.inner_text("#time")
            ok("@2×" in t_txt, f"{vid}: 2x speed applies ({t_txt})")
            await pg.click('#speeds button[data-s="1"]')

            await pg.evaluate("window.__media = []")
            await pg.click("#bMute")
            await pg.wait_for_timeout(600)
            media = await pg.evaluate("window.__media")
            ok(any(m[0] == "pause" for m in media) and not any(m[0] == "play" for m in media), f"{vid}: mute pauses the narration")
            await pg.click("#bMute")
            await pg.click("#bPlay")

            # download dialog: recorded narration is the default; export carries an audio track
            await pg.click("#bDl")
            opts = await pg.locator("#dlOpts input[name=dla]").evaluate_all("els => els.map(e => [e.value, e.checked, e.disabled])")
            ok(opts[0][:2] == ["rec", True], f"{vid}: download defaults to the narration: {opts}")
            await pg.click("#dlGo")
            await pg.wait_for_selector("#recbar:not([hidden])", timeout=20000)
            await pg.wait_for_timeout(2500)
            rec = await pg.evaluate("window.__recTracks")
            txt = await pg.inner_text("#recTxt")
            ok(rec == {"audio": 1, "video": 1} and "narration" in txt, f"{vid}: MP4 export records video + narration ({rec}; '{txt[:40]}...')")
            await pg.click("#recCancel")
            await pg.wait_for_timeout(500)

            # ---------- offline file from file://, no network at all
            off = await ctx.new_page()
            off_errs = []
            off.on("pageerror", lambda e: off_errs.append(str(e)))
            await ctx.set_offline(True)
            await off.goto((SITE / "downloads" / f"{vid}.html").as_uri())
            await off.wait_for_function("window.__reel")
            vb2 = await off.evaluate("window.__voiceBuffer()")
            ok(abs(vb2["duration"] - vb["duration"]) < 0.05 and min(vb2["scenes"]) > -45,
               f"{vid}: offline file plays the full narration with no network ({vb2['duration']:.1f}s)")
            home = await off.get_attribute("#home", "href")
            ok(home.startswith("https://"), f"{vid}: offline file links back to the website: {home}")
            await off.click("#tap")
            await off.wait_for_timeout(1500)
            ok(any(m[0] == "play" for m in await off.evaluate("window.__media")), f"{vid}: offline file starts narration on play")
            await ctx.set_offline(False)
            ok(not off_errs, f"{vid}: offline file has no JS errors {off_errs[:2]}")
            await off.close()

            # ---------- voice-over mp3 length
            mp3 = SITE / "downloads" / f"{vid}-voiceover.mp3"
            d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                                "-of", "default=nw=1:nk=1", str(mp3)]))
            ok(abs(d - reel["total"]) < 0.5, f"{vid}: voice-over MP3 is {d:.1f}s, video {reel['total']:.1f}s")
            srt = (SITE / "downloads" / f"{vid}-subtitles.srt").read_text()
            last = re.findall(r"--> (\d\d):(\d\d):(\d\d),(\d+)", srt)[-1]
            end = int(last[0]) * 3600 + int(last[1]) * 60 + int(last[2])
            ok(end <= reel["total"], f"{vid}: subtitles end inside the video ({end}s <= {reel['total']:.0f}s)")

        # ---------- a video without recorded narration still offers the browser voice
        other = next(v for v in ["linux", "kubernetes", "aws"] if v not in narrated)
        await pg.goto(BASE + f"{other}.html")
        await pg.wait_for_function("window.__reel")
        r2 = await pg.evaluate("[window.__reel.voice, [...document.querySelectorAll('#voiceSel option')].map(o => o.value).includes('__rec')]")
        ok(r2 == [False, False], f"{other}: no recorded narration, browser voice menu only")
        await pg.click("#tap")
        await pg.wait_for_timeout(800)
        ok("0:0" in await pg.inner_text("#time"), f"{other}: plays")

        ok(not errs, "no JavaScript errors on the site" + (f": {errs[:3]}" if errs else ""))
        await b.close()
    print(f"\n{'ALL PASSED' if not FAILS else f'{len(FAILS)} FAILED'}")
    sys.exit(1 if FAILS else 0)


asyncio.run(main())
