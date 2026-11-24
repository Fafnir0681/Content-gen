#!/usr/bin/env python3
"""Build the PlayForge Labs wordmark as OUTLINED SVG (no font dependency).

Type: Chakra Petch (SIL Open Font License). PLAY=400, FORGE=700, LABS=600-ish
(set from the 700 master, optically tracked). Outlining glyphs into logo
artwork is permitted under the OFL; the result is artwork, not a font.

Usage: python3 tools/makewordmark.py <regular.ttf> <bold.ttf> <outdir>
"""
import sys, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

RED, BLACK, WHITE = '#D62325', '#110D0D', '#FFFFFF'
# gunmetal options for FORGE
GUN_MID, GUN_LIGHT = '#6E757D', '#8C949D'
GUN_GRAD = 'url(#gun)'
GRAD_DEF = ('<defs><linearGradient id="gun" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%" stop-color="#A8B0B8"/>'
            '<stop offset="46%" stop-color="#737B84"/>'
            '<stop offset="54%" stop-color="#5A626B"/>'
            '<stop offset="100%" stop-color="#8A929B"/></linearGradient></defs>')

class Face:
    def __init__(self, path):
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upem = self.f['head'].unitsPerEm

    def run(self, text, size, track=0.0):
        """Return (list of (d, x_offset), advance_width) in SVG px at `size`."""
        s = size / self.upem
        out, x = [], 0.0
        for ch in text:
            g = self.cmap[ord(ch)]
            pen = SVGPathPen(self.gs)
            self.gs[g].draw(pen)
            d = pen.getCommands()
            if d.strip():
                out.append((d, x))
            x += self.gs[g].width + track * self.upem
        return out, x * s, s

    def ink_bounds(self, text):
        bp = BoundsPen(self.gs)
        x = 0
        lo, hi = None, None
        for ch in text:
            g = self.cmap[ord(ch)]
            b = BoundsPen(self.gs); self.gs[g].draw(b)
            if b.bounds:
                y0, y1 = b.bounds[1], b.bounds[3]
                lo = y0 if lo is None else min(lo, y0)
                hi = y1 if hi is None else max(hi, y1)
        return lo or 0, hi or 0

def emit(runs, w, h, pad=0.0, defs=''):
    """runs: list of (paths, scale, dx, dy, fill)"""
    body = []
    for paths, s, dx, dy, fill in runs:
        for d, gx in paths:
            body.append(f'<path d="{d}" fill="{fill}" transform="translate({dx + gx*s:.2f},{dy:.2f}) scale({s:.5f},{-s:.5f})"/>')
    vb = f'{-pad:.2f} {-pad:.2f} {w+pad*2:.2f} {h+pad*2:.2f}'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'width="{w+pad*2:.0f}" height="{h+pad*2:.0f}">' + defs + ''.join(body) + '</svg>')

def build(reg, bold, outdir):
    R, B = Face(reg), Face(bold)
    SIZE = 200.0
    _, capy1 = B.ink_bounds('FORGE')
    cap = capy1 * (SIZE / B.upem)          # cap height in px

    FORGE_SETS = [('', None, ''), ('-redforge', RED, ''),
                  ('-gunmid', GUN_MID, ''), ('-gunlight', GUN_LIGHT, ''),
                  ('-gungrad', GUN_GRAD, GRAD_DEF)]
    for ground, maintone in (('ondark', WHITE), ('onlight', BLACK)):
      for fsuf, ftone, fdefs in FORGE_SETS:
        for labsname, labstone in (('neutral', maintone), ('red', RED)):
            forgetone = ftone or maintone
            # ---- stacked ----
            play, wplay, s1 = R.run('PLAY', SIZE)
            forge, wforge, s2 = B.run('FORGE', SIZE)
            # LABS is justified to the exact width of PLAYFORGE so the two
            # lines lock as one unit. Track is solved, not guessed.
            LS = SIZE * 0.335
            target = wplay + wforge
            base_paths, base_w, s3 = B.run('LABS', LS)
            solved = (target - base_w) / (len('LABS') - 1) / LS
            labs, wlabs, s3 = B.run('LABS', LS, solved)
            wlabs -= solved * LS           # drop trailing track
            gap = SIZE * 0.085
            baseline = cap
            lbase = baseline + LS * 0.92 + gap
            total_w = max(wplay + wforge, wlabs)
            total_h = lbase
            svg = emit([(play, s1, 0, baseline, maintone),
                        (forge, s2, wplay, baseline, forgetone),
                        (labs, s3, 1.0, lbase, labstone)], total_w, total_h, pad=SIZE*0.04, defs=fdefs)
            open(os.path.join(outdir, f'wordmark-stacked-{ground}{fsuf}-{labsname}.svg'), 'w').write(svg)

            # ---- inline ----
            IS = SIZE
            play2, wp2, p2s = R.run('PLAY', IS)
            forge2, wf2, f2s = B.run('FORGE', IS)
            LS2, LT2 = IS * 0.42, 0.26
            labs2, wl2, l2s = B.run('LABS', LS2, LT2)
            wl2 -= LT2 * LS2
            gap2 = IS * 0.30
            _, capy_small = B.ink_bounds('LABS')
            cap_small = capy_small * (LS2 / B.upem)
            base2 = cap                      # shared cap-height baseline
            x_labs = wp2 + wf2 + gap2
            svg2 = emit([(play2, p2s, 0, base2, maintone),
                         (forge2, f2s, wp2, base2, forgetone),
                         (labs2, l2s, x_labs, base2, labstone)],
                        x_labs + wl2, cap, pad=SIZE*0.04, defs=fdefs)
            open(os.path.join(outdir, f'wordmark-inline-{ground}{fsuf}-{labsname}.svg'), 'w').write(svg2)
    print('wrote wordmark files to', outdir)

if __name__ == '__main__':
    build(*sys.argv[1:4])
