#!/usr/bin/env python3
"""Build subscriber badges from the mark's anvil path.

At 18px a face is hopeless and fine detail vanishes, so tiers CANNOT
differentiate by added ornament. They differentiate by overall colour mass —
disc fill, anvil fill, ring — which is the only thing that survives.

The anvil silhouette is reused from mark/mark-full.svg so badges and the
mark stay the same object.

Usage: python3 tools/badges.py <branddir>
"""
import os, re, sys

RED, BLACK, WHITE = '#D62325', '#110D0D', '#FFFFFF'
# anvil bbox in the 2048 viewBox, measured: 650x369 at (701,953)
AX, AY, AW, AH = 701, 953, 650, 369
CX = CY = 1024

# month -> (disc, anvil, ring, ring width)
# Every tier keeps a DARK outer keyline so it survives on light chat, and
# tiers differ by large colour mass rather than by thin-ring detail, which
# is invisible at 18px. The progression runs light -> red -> dark, with the
# top two marked by a much thicker ring.
TIERS = [
    (1,  WHITE, BLACK, BLACK, 90),
    (2,  WHITE, RED,   BLACK, 90),
    (3,  RED,   WHITE, BLACK, 90),
    (6,  RED,   BLACK, BLACK, 90),
    (9,  BLACK, WHITE, BLACK, 90),
    (12, BLACK, RED,   BLACK, 90),
    (18, RED,   WHITE, BLACK, 210),
    (24, BLACK, RED,   RED,   210),
]

def anvil_path(brand):
    s = open(os.path.join(brand, 'mark', 'mark-full.svg')).read()
    body = s[s.index('>', s.index('<svg')) + 1:]
    return re.search(r' d="([^"]*)"', re.findall(r'<path[^>]*/?>', body)[4]).group(1)

def build(brand):
    d = anvil_path(brand)
    out = os.path.join(brand, 'badges')
    os.makedirs(out, exist_ok=True)
    R = 980
    # scale the anvil to ~70% of the disc and centre it
    s = (R * 1.40) / AW
    tx = CX - (AX + AW / 2) * s
    ty = CY - (AY + AH / 2) * s
    for months, disc, anvil, ring, rw in TIERS:
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 2048" '
               f'width="2048" height="2048">'
               f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="{ring}"/>'
               f'<circle cx="{CX}" cy="{CY}" r="{R - rw}" fill="{disc}"/>'
               f'<g transform="translate({tx:.1f},{ty:.1f}) scale({s:.5f})">'
               f'<path d="{d}" fill="{anvil}"/></g></svg>')
        open(os.path.join(out, f'badge-{months:02d}mo.svg'), 'w').write(svg)
    print(f'  wrote {len(TIERS)} badge SVGs to {out}')

if __name__ == '__main__':
    build(sys.argv[1])
