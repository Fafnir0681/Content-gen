#!/usr/bin/env python3
"""Alpha-cut a character off a flat background.

Naive colour-keying or flood-fill fails here: the character's own outlines,
boots and armour are the SAME near-black as the background, and antialiasing
bridges them, so a fill leaks inside and hollows the figure out.

Instead: treat it as a silhouette problem.
  1. mark pixels that differ from the background colour (tight tolerance)
  2. close small gaps so the outline becomes continuous
  3. keep the largest connected component (the character)
  4. fill interior holes -> dark regions INSIDE the silhouette come back
  5. derive a soft alpha so edges stay antialiased rather than jagged

Usage: python3 tools/cutout.py <in.png> <out.png> [tolerance] [feather]
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

def main(src, dst, tol=20, feather=1.0, close=11):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    # background colour = most common pixel (flat ground)
    flat = a.reshape(-1, 3)
    uniq, counts = np.unique(flat, axis=0, return_counts=True)
    bg = uniq[counts.argmax()]
    # distance from background, per pixel
    dist = np.abs(a - bg).max(axis=2)
    solid = dist > tol
    # close gaps so antialiased outlines form a continuous boundary
    # The closing radius matters: dark trousers connect to the background
    # through the gap between the legs, so they are NOT an enclosed hole and
    # fill_holes alone leaves them transparent. A radius of 11 seals that
    # channel (trouser coverage 40% -> 98%) without closing the leg gap.
    closed = ndimage.binary_closing(solid, structure=np.ones((close, close)), iterations=2)
    # largest connected component = the character
    lab, n = ndimage.label(closed)
    if n == 0:
        raise SystemExit('no subject found')
    sizes = ndimage.sum(closed, lab, range(1, n + 1))
    keep = (lab == (sizes.argmax() + 1))
    # interior holes (black boots, armour, line work) belong to the subject
    filled = ndimage.binary_fill_holes(keep)
    # soft alpha: hard inside, antialiased at the boundary
    soft = ndimage.gaussian_filter(filled.astype(np.float32), feather)
    alpha = np.clip((soft - 0.35) / 0.45, 0, 1)
    alpha = np.maximum(alpha, filled.astype(np.float32) * 0.0)
    alpha8 = (alpha * 255).astype(np.uint8)
    out = np.dstack([np.asarray(im).astype(np.uint8), alpha8])
    Image.fromarray(out, 'RGBA').save(dst)
    pct = 100.0 * filled.mean()
    print(f'bg={tuple(int(v) for v in bg)} tol={tol} subject={pct:.2f}% of frame -> {dst}')

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args[0], args[1],
         int(args[2]) if len(args) > 2 else 20,
         float(args[3]) if len(args) > 3 else 1.0,
         int(args[4]) if len(args) > 4 else 11)
