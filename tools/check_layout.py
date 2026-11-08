#!/usr/bin/env python3
"""Draw every scene of every video in a real browser and fail on text that overflows or is cut off.

    python3 tools/check_layout.py            # all videos
    python3 tools/check_layout.py git aws    # some videos
"""
import asyncio
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONT = __import__("os").environ.get("LAYOUT_FONT", "")
sys.path.insert(0, str(ROOT))
import build  # noqa: E402
from playwright.async_api import async_playwright  # noqa: E402


async def main(ids):
    bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1920, "height": 1200})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        with tempfile.TemporaryDirectory() as tmp:
            for vid in ids:
                d = build.load(ROOT / "content" / f"{vid}.js")
                f = pathlib.Path(tmp) / f"{vid}.html"
                html = build.page(d, None, offline=True)
                if FONT:  # check with a specific font, e.g. the metric-compatible Arial used on Linux CI and Windows
                    html = html.replace("const SANS = '", "const SANS = '" + FONT + ", ", 1)
                f.write_text(html)
                errs.clear()
                await pg.goto(f.as_uri())
                await pg.wait_for_function("window.__reel")
                issues = await pg.evaluate("window.__drawAll()")
                r = await pg.evaluate("window.__reel")
                status = "OK" if not issues and not errs else "PROBLEMS"
                print(f"{vid:<14} {r['total'] / 60:5.1f} min  {len(r['scenes']):>3} scenes  {status}")
                for i in issues:
                    print(f"    {i['tag']}: {i['text'][:70]!r} ({i['issue']})")
                for e in errs:
                    print(f"    JS error: {e}")
                bad += len(issues) + len(errs)
        await b.close()
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:] or sorted(p.stem for p in (ROOT / "content").glob("*.js"))))
