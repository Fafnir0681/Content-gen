# Generators

Every derived file in `brand/` is built by something in here, and each
generator lives next to its output so the whole set rebuilds from vector
sources. Nothing in `brand/` should be edited by hand — change the generator
and re-run it.

Run from `brand/`: `node tools/<name>.js` or `python3 tools/<name>.py`.

## Identity

| Tool | Builds |
|---|---|
| `makewordmark.py` | `wordmark/` — 40 outlined SVGs, no font dependency |
| `makelockup.py` | `lockup/` — globs every wordmark, so new variants are picked up |
| `makeglass.py` | `glass-motion/` — glassmorphism variants of the mark |
| `badges.py` | `badges/` — 8 sub-badge tiers from the mark's anvil path |
| `bitbadges.py` | `bitbadges/` — a flask that fills with red as the tier rises |
| `pngsqueeze.py` | shrinks flat-art PNGs to a 255-colour palette, keeping alpha |

## Composition

| Tool | Builds |
|---|---|
| `channel.js` | `channel/` — every platform screen from one parametric composition |
| `overlay.js` | `overlay/` — the 11 on-stream components |
| `social.js` | `social/`, `discord/` |
| `vertical.js` | `vertical/` scenes, overlay, clip template, safe-zone guide |

## Motion

| Tool | Builds |
|---|---|
| `alerts.js` | `alerts/*.png` — the still frames |
| `alertanim.js` | `alerts/*.webm` — animated, alpha, and encodes in one command |
| `valerts.js` | `vertical/alert-*` — portrait alerts + placement guide |
| `mascotidle.js` | `mascot/mascot-plate-idle.webm` — the 6s idle loop |
| `stinger.js` | frames for `transitions/stinger.webm` |
| `bumper.js` | frames for `transitions/bumper.mp4` |

## Mascot

| Tool | Does |
|---|---|
| `cutout.py` | alpha-cuts a character off a flat background |
| `occluder.py` | builds a background-coloured occluder from the silhouette |
| `rendersvg.js` | headless-Chromium SVG → PNG |

## How this works

Headless Chromium is used as a **deterministic renderer** — HTML/SVG in,
exact pixels out. That is why the compositions are written as CSS rather
than drawn: a layout change is a number, not a redraw.

Two conventions worth knowing before editing anything:

- **Frame directories.** Motion tools write `.<name>-frames/` at the repo
  root and encode from there. `.gitignore` matches `.*-frames/` as a
  pattern — do not replace that with a list of names. An enumerated list
  missed a new directory twice and nearly committed 183MB of intermediates.
- **PNG32 before ffmpeg.** Frames that happen to be fully opaque save
  without an alpha channel, and one such frame makes ffmpeg drop alpha for
  the entire clip. Every motion tool normalises with `convert PNG32:` first.
  `ffprobe` reports the base stream as `yuv420p` even when alpha is present,
  so check the container tag `alpha_mode=1` instead, or decode to RGBA.

## Measure, do not assume

The recurring failure in this set was assuming geometry instead of reading
it: a glass effect sized to the canvas rather than the mark, a rule drawn
through a lockup whose occupied band was guessed, avatars built from a mark
at 42% fill. Every one cost a rebuild. If a tool needs a coordinate, compute
it from the source file.
