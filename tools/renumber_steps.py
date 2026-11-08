#!/usr/bin/env python3
"""Make every narrated "Step N:" match the step's real position (after scenes are added or moved).
    python3 tools/renumber_steps.py aws git
"""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import build  # noqa: E402
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = {2: 'twenty', 3: 'thirty', 4: 'forty', 5: 'fifty', 6: 'sixty', 7: 'seventy', 8: 'eighty', 9: 'ninety'}
def words(n):
    if n >= 100: return 'one hundred' + ('' if n % 100 == 0 else ' ' + words(n % 100))
    if n < 20: return ONES[n]
    return TENS[n // 10] + ('' if n % 10 == 0 else ' ' + ONES[n % 10])
NUM = sorted({words(i) for i in range(1, 200)} | {w.replace(' ', '-') for w in (words(i) for i in range(1, 200))}, key=len, reverse=True)
PAT = re.compile(r"^Step (" + "|".join(map(re.escape, NUM)) + r"):")
for vid in sys.argv[1:]:
    p = ROOT / 'content' / f'{vid}.js'; src = p.read_text(); d = build.load(p); k = changed = 0
    for s in d['scenes']:
        if s['type'] in ('step', 'flow', 'compare', 'tree', 'graph') and not s.get('x'):
            k += 1; n = s['n']; m = PAT.match(n)
            if not m: print(f'  {vid}: no "Step N:" prefix in: {n[:60]}'); continue
            if m.group(1) != words(k):
                new = PAT.sub(f'Step {words(k)}:', n, count=1); old_js = n.replace("'", "\\'")
                assert src.count(old_js) == 1, n[:50]; src = src.replace(old_js, new.replace("'", "\\'"), 1); changed += 1
    p.write_text(src); print(f'{vid}: {k} steps, {changed} renumbered')
