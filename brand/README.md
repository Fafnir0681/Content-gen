# PlayForge Labs — brand assets

Visual identity for the PlayForge Labs stream. Not used by the Flask app;
this directory is storage only and has no effect on the build or deploy.

## Palette

| Role | Hex | Notes |
|---|---|---|
| Red | `#D62325` | brand red — the generated mark shipped `#F62643`, unified to this |
| Black | `#110D0D` | |
| White | `#FFFFFF` | |

## Mark — two cuts

The mark is legible down to ~64px. Below 48px it collapses, so there is a
simplified small cut. Use the right one for the size:

| Size | File |
|---|---|
| >= 64px | `mark/mark-full.svg` (light bg) / `mark-full-ondark.svg` (dark bg) |
| <= 48px | `mark/mark-small.svg` / `mark-small-ondark.svg` |

The on-dark variants exist because the black outer ring disappears against a
dark background; they carry a white ring instead.

Geometry: viewBox 2048x2048, disc centre (1024,1024), radius 428.

### Rendered sizes
`avatar-twitch-800`, `avatar-kick-128`, `discord-icon-512`, `avatar-ondark-800`
come from the full mark. `favicon-32`, `roleicon-64`, `badge-18/36/72` come from
the small cut. All transparent PNG.

## Mascot

`mascot/mascot-master.png` — the canonical character reference. Blonde braided
Viking in a lab coat; no face-cam, so the mascot carries on-screen identity.
Every derived asset (bust crop, emotes, overlay plate) must match THIS file,
including the long coat and boots.

## Glass variants

See `glass-motion/README.md`. Held for transition/stinger animation, not part
of the static logo set.

## Re-exporting

`tools/rendersvg.js` renders any SVG here to PNG at any size via headless
Chromium (Playwright):

    node brand/tools/rendersvg.js <in.svg> <out.png> <size> <light|dark|none>

## Still open
- Wordmark (must be set in real licensed type, not image-generated)
- Mascot bust crop, emote set, alpha overlay plate
- Formal type pairing
