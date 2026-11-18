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
| >= 64px | `mark/mark-full-tight.svg` (light bg) / `mark-full-ondark-tight.svg` (dark bg) |
| <= 48px | `mark/mark-small.svg` / `mark-small-ondark.svg` |

The on-dark variants exist because the black outer ring disappears against a
dark background; they carry a white ring instead.

Geometry: the generated source has viewBox 2048x2048 with the disc at centre
(1024,1024), radius 428 — i.e. the disc fills only ~42% of the frame. The
`-tight` variants crop the viewBox to the disc (~96% fill) and are what every
avatar, badge and lockup is rendered from. Use the tight variants; the
uncropped originals are kept only as the untouched source.

### Rendered sizes
`avatar-twitch-800`, `avatar-kick-128`, `discord-icon-512`, `avatar-ondark-800`
come from the full mark. `favicon-32`, `roleicon-64`, `badge-18/36/72` come from
the small cut. All transparent PNG.

## Mascot

`mascot/mascot-master.png` — the canonical character reference. Blonde braided
Viking in a lab coat; no face-cam, so the mascot carries on-screen identity.
Every derived asset (bust crop, emotes, overlay plate) must match THIS file,
including the long coat and boots.

| File | Use |
|---|---|
| `mascot-master.png` | source, baked near-black background |
| `mascot-cutout.png` | alpha cut, full 1280x720 frame |
| `mascot-plate.png` | alpha cut, trimmed to subject (484x680) — use this on the overlay |

### How the cutout works
The background is `#0E0D0C`, and the character's own outlines, boots and
armour are the SAME near-black. Colour-keying or flood-filling therefore
leaks through the outlines and hollows the figure out — verified, it does.

`tools/cutout.py` treats it as a silhouette problem instead: mark everything
unlike the background, close gaps so the outline is continuous, keep the
largest connected component, then fill interior holes so the dark regions
inside the silhouette come back. Edges stay antialiased (~0.5% of the frame
is partial alpha) with no dark halo on light or coloured grounds.

    python3 tools/cutout.py mascot/mascot-master.png out.png [tolerance] [feather]

Tolerance is insensitive between 18 and 40 — the subject measures 16.2% of
the frame across that whole range.

## Glass variants

See `glass-motion/README.md`. Held for transition/stinger animation, not part
of the static logo set.

## Re-exporting

`tools/rendersvg.js` renders any SVG here to PNG at any size via headless
Chromium (Playwright):

    node brand/tools/rendersvg.js <in.svg> <out.png> <size> <light|dark|none>

## Wordmark

Type: **Chakra Petch** (SIL Open Font License — cleared for commercial use
including merch). `PLAY` is weight 400, `FORGE` weight 700; the break makes
the compound name read as its two ideas, with emphasis landing on FORGE.

**All type is outlined to paths — these files carry no font dependency.**
Nobody needs Chakra Petch installed to open, render or print them.

### Variants (8 wordmark + 8 lockup)
- Layout: `stacked` (two lines) or `inline` (one line)
- Ground: `ondark` (white type) or `onlight` (black type)
- LABS: `neutral` (matches the type) or `red` (#D62325)

Red LABS works on either ground. The neutral MUST match the ground —
white LABS on a light background is invisible.

In the stacked lockup, `LABS` is tracked so it spans exactly the width of
`PLAYFORGE`. That track is solved arithmetically in `tools/makewordmark.py`,
not eyeballed, so it stays correct if the type ever changes.

### Clear space and minimum size
- Clear space on all sides: at least the cap height of `FORGE`.
- Stacked lockup: do not use below 200px wide. Inline: not below 240px.
- Below those sizes use the mark alone (`mark/mark-small.svg`).

## Regenerating

    python3 tools/makewordmark.py <ChakraPetch-Regular.ttf> <ChakraPetch-Bold.ttf> wordmark/
    python3 tools/makelockup.py .

The TTFs are not vendored; fetch them from Google Fonts. The outlined SVGs
are the deliverable, so this is only needed if the type or tracking changes.

## Still open
- Mascot bust crop, emote set, alpha overlay plate
- Body typeface to pair with Chakra Petch for panels and captions
