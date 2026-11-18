#!/usr/bin/env python3
"""Compose mark + wordmark into lockup SVGs using nested <svg> elements,
so neither source is re-derived and both stay editable.

Gap is 0.22 x mark width. Mark height matches the wordmark block height.
Usage: python3 tools/makelockup.py <branddir>
"""
import os, re, sys

def parts(path):
    s = open(path).read()
    m = re.search(r'viewBox="([^"]+)"', s)
    vb = m.group(1)
    inner = s[s.index('>', s.index('<svg')) + 1:].rsplit('</svg>', 1)[0]
    x, y, w, h = [float(v) for v in vb.split()]
    return vb, inner, w, h

def build(brand):
    wm_dir = os.path.join(brand, 'wordmark')
    out_dir = os.path.join(brand, 'lockup')
    os.makedirs(out_dir, exist_ok=True)
    marks = {'ondark': os.path.join(brand, 'mark', 'mark-full-ondark-tight.svg'),
             'onlight': os.path.join(brand, 'mark', 'mark-full-tight.svg')}
    n = 0
    for ground, mpath in marks.items():
        mvb, minner, mw, mh = parts(mpath)
        for layout in ('stacked', 'inline'):
            for labs in ('neutral', 'red'):
                wpath = os.path.join(wm_dir, f'wordmark-{layout}-{ground}-{labs}.svg')
                if not os.path.exists(wpath):
                    continue
                wvb, winner, ww, wh = parts(wpath)
                M = wh                      # mark height == wordmark block height
                gap = M * 0.22
                W, H = M + gap + ww, max(M, wh)
                svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}" '
                       f'width="{W:.0f}" height="{H:.0f}">'
                       f'<svg x="0" y="{(H-M)/2:.2f}" width="{M:.2f}" height="{M:.2f}" viewBox="{mvb}">{minner}</svg>'
                       f'<svg x="{M+gap:.2f}" y="{(H-wh)/2:.2f}" width="{ww:.2f}" height="{wh:.2f}" viewBox="{wvb}">{winner}</svg>'
                       f'</svg>')
                open(os.path.join(out_dir, f'lockup-{layout}-{ground}-{labs}.svg'), 'w').write(svg)
                n += 1
    print(f'wrote {n} lockup files to {out_dir}')

if __name__ == '__main__':
    build(sys.argv[1])
