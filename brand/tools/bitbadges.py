#!/usr/bin/env python3
"""Build bit badges: a flask that fills with red as the tier rises.

Sub badges own the anvil (the forge); bit badges own the flask (the lab).
Different silhouette, so the two systems never get confused at 18px — a
round disc versus a flask reads instantly where a colour change would not.

Tier progression is the liquid level, which is monotonic and legible as
overall colour mass. The top tiers add outline weight once the flask is
full and the level can no longer carry the progression.

Usage: python3 tools/bitbadges.py <branddir>
"""
import os, sys

RED, BLACK, WHITE = '#D62325', '#110D0D', '#FFFFFF'
HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 2048" '
        'width="2048" height="2048">')
# flask outline, bold enough to survive 18px
FLASK = ("M 912 470 L 1136 470 L 1136 560 L 1104 560 L 1104 858 "
         "L 1452 1452 Q 1500 1540 1400 1540 L 648 1540 Q 548 1540 596 1452 "
         "L 944 858 L 944 560 L 912 560 Z")
BODY_TOP, BODY_BOT = 858, 1540   # liquid travels between these

# (bits, liquid fraction 0-1, outline width, plate behind the flask)
# The outline stays BLACK throughout. An earlier version changed it to white
# then red for the top tiers: the white outline vanished against the white
# flask body and the red one merged with the red liquid, so both collapsed
# into a shapeless blob. Once the flask is full the progression moves to a
# plate behind it instead.
TIERS = [
    (1,       0.00, 74,  None),
    (100,     0.30, 74,  None),
    (1000,    0.55, 74,  None),
    (5000,    0.80, 74,  None),
    (10000,   1.00, 74,  None),
    (25000,   1.00, 150, None),
    (50000,   1.00, 110, BLACK),
    (100000,  1.00, 110, RED),
]

def build(brand):
    out = os.path.join(brand, 'bitbadges')
    os.makedirs(out, exist_ok=True)
    for bits, frac, ow, plate in TIERS:
        # The outline must contrast with whatever sits behind it: on the
        # black plate a black outline vanishes and the flask collapses to a
        # red triangle.
        oc = WHITE if plate == BLACK else BLACK
        if frac <= 0:
            liquid = ''
        else:
            y = BODY_BOT - (BODY_BOT - BODY_TOP) * frac
            # clip the liquid rectangle to the flask shape
            liquid = (f'<clipPath id="f"><path d="{FLASK}"/></clipPath>'
                      f'<rect x="500" y="{y:.0f}" width="1048" height="{BODY_BOT-y+60:.0f}" '
                      f'fill="{RED}" clip-path="url(#f)"/>')
        # white body first so the liquid reads against it, then the outline
        base = ''
        if plate:
            base = (f'<circle cx="1024" cy="1024" r="980" fill="{BLACK}"/>'
                    f'<circle cx="1024" cy="1024" r="890" fill="{plate}"/>')
        svg = (HEAD
               + base
               + f'<path d="{FLASK}" fill="{WHITE}"/>'
               + liquid
               + f'<path d="{FLASK}" fill="none" stroke="{oc}" stroke-width="{ow}" '
                 f'stroke-linejoin="round"/>'
               + '</svg>')
        open(os.path.join(out, f'bit-{bits}.svg'), 'w').write(svg)
    print(f'  wrote {len(TIERS)} bit badge SVGs to {out}')

if __name__ == '__main__':
    build(sys.argv[1])
