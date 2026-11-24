# PlayForge Labs — glass variants (held for motion work)

Parked for transition/stinger animation. Not part of the static logo set.

| File | Look | Notes |
|---|---|---|
| morph-streak.svg | glassmorphism + sheen | **pick** — preserves red/black, best on dark |
| morph-clean.svg | glassmorphism, no streak | subtlest |
| morph-frosted.svg | heavier film | washes the mark slightly |
| tile-diagonal.svg | hard diagonal highlight | "glass tile" reference |
| lens-edge.svg | rim + edge only | no gloss over the face |
| dome-subtle.svg | soft top-down dome | more dated gloss read |

## Animating later
The sheen is `<linearGradient id="sheen">` — animate `x1/y1/x2/y2` to sweep light
across the disc. No raster re-export needed; render to frames at any size via
the headless-Chromium renderer.

Geometry: viewBox 2048x2048, mark circle centre (1024,1024), r=428.
Brand red #D62325 / black #110D0D / white #FFFFFF.

Glass needs something behind it to read — use over gameplay or the overlay,
not on a flat white profile page. Keep the flat mark for anything <=64px.
