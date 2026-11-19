#!/usr/bin/env python3
"""Build a background-coloured occluder from the mascot silhouette.

A diagonal drawn behind the figure stays visible in the negative space
between the legs, which reads as the line cutting through him. This fills
that gap with the page colour so the figure occludes the diagonal as a
whole mass, while the outline itself is untouched.

Only the lower part of the figure is row-filled, so gaps between arm and
body higher up still show the background normally.

Usage: python3 tools/occluder.py <plate.png> <out.png> [hexcolour] [start_frac]
"""
import sys
import numpy as np
from PIL import Image

def main(src, dst, hexcol='#11151A', start=0.58):
    a = np.asarray(Image.open(src))
    al = a[:, :, 3] > 100
    h, w = al.shape
    occ = np.zeros_like(al)
    y0 = int(h * start)
    for y in range(y0, h):
        xs = np.where(al[y])[0]
        if len(xs):
            occ[y, xs.min():xs.max() + 1] = True
    rgb = tuple(int(hexcol[i:i+2], 16) for i in (1, 3, 5))
    out = np.zeros((h, w, 4), np.uint8)
    out[occ] = (*rgb, 255)
    Image.fromarray(out, 'RGBA').save(dst)
    print(f'  occluder {dst}  filled rows {y0}-{h}  {occ.sum()} px  colour {hexcol}')

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args[0], args[1],
         args[2] if len(args) > 2 else '#11151A',
         float(args[3]) if len(args) > 3 else 0.58)
