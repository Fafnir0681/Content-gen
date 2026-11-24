# Mark

The icon on its own — no type. It does the most work of anything in the set:
all four platform avatars, the Discord icon, the favicon, the on-stream
watermark, and it is the source geometry for every sub badge and bit badge.

## Files

| File | Use |
|---|---|
| `mark-full.svg` / `mark-full-ondark.svg` | full mark, light / dark ground |
| `mark-full-tight.svg` / `mark-full-ondark-tight.svg` | **cropped to the disc** — use for avatars |
| `mark-small.svg` / `mark-small-ondark.svg` | simplified cut for 48px and below |
| `avatar-twitch-800.png` `avatar-ondark-800.png` `avatar-kick-128.png` | rendered avatars |
| `badge-18/36/72.png` | the mark at Twitch badge sizes |
| `discord-icon-512.png` `roleicon-64.png` `favicon-32.png` | platform icons |

## Why `-tight` exists

The full mark is drawn in a 2048×2048 viewBox with the disc at r=428 — about
**42% fill**. Uploaded as an avatar that renders as a small badge adrift in
whitespace, because every platform crops to a circle and adds its own
padding on top.

The `-tight` variants crop the viewBox to the disc's bounding box
(`578 578 892 892`), giving roughly **96% fill**. Use `-tight` for anything
that will be displayed as a circle or square avatar. Use the untight version
when you need the mark placed inside a composition you control.

## Why `-ondark` exists

The on-dark variants carry a **white ring**. The black ring of the standard
mark disappears entirely against a dark background, which is most of this
brand's surfaces. A dark-only logo also vanishes on YouTube's light theme,
which is why both exist rather than one.

## Below 48px

Use `mark-small`. The full cut loses legibility — this was checked at 32px
before the icon was chosen, not assumed afterwards.

## Downstream

`tools/badges.py` and `tools/bitbadges.py` read the anvil path out of this
mark (path index `[4]`) rather than redrawing it. If the mark's path order
ever changes, those two generators need the index updated — they will not
fail loudly, they will just draw the wrong shape.

## Derived
`../glass-motion/` holds glassmorphism variants of this mark, parked for
motion work. Geometry: viewBox 2048×2048, circle centre (1024,1024), r=428.
