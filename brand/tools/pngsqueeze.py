#!/usr/bin/env python3
"""Shrink flat-art PNGs to a 255-colour palette, preserving alpha.

Twitch's static emote cap is cited as 25KB in some sources and 1MB in others.
Under the strict reading rage-112.png failed at 27.6KB, so this removes the
doubt rather than betting on which source is right.

Flat comic art has no real gradients -- rage-112 carried 4729 unique RGBA
values, essentially all of them anti-aliasing. A 255-colour adaptive palette
is visually indistinguishable at both 112px and chat size and cuts the file
by about 4x. Plain lossless re-optimisation saves under 1%; it is not enough.

Idempotent: re-running on an already-squeezed file is a no-op in practice.

    python3 tools/pngsqueeze.py emotes/*.png
    python3 tools/pngsqueeze.py --check emotes/*.png   # report only
"""
import sys, os
from PIL import Image

CAP = 25 * 1024

def squeeze(path, check=False):
    before = os.path.getsize(path)
    im = Image.open(path).convert("RGBA")
    q = im.quantize(colors=255, method=Image.FASTOCTREE)
    if check:
        return before, before
    q.save(path, "PNG", optimize=True)
    return before, os.path.getsize(path)

def main(argv):
    check = "--check" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__); return 1
    worst = 0
    for p in sorted(paths):
        b, a = squeeze(p, check)
        worst = max(worst, a)
        flag = "  OVER CAP" if a > CAP else ""
        arrow = f"{b/1024:6.1f} -> {a/1024:6.1f} KB" if not check else f"{b/1024:6.1f} KB"
        print(f"  {arrow}  {p}{flag}")
    print(f"\n  largest: {worst/1024:.1f} KB  (cap {CAP/1024:.0f} KB)")
    return 0 if worst <= CAP else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
