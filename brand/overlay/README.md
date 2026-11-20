# Phase 2 — on-stream overlay components

Transparent PNGs, positioned as sources in OBS. Rebuild with
`node tools/overlay.js [name]`.

| File | Size | Notes |
|---|---|---|
| `nameplate.png` | 640x112 | mark + name + handle |
| `chatbox.png` | 400x660 | frame only; chat widget sits inside it |
| `recent-events.png` | 460x172 | latest follower / latest sub |
| `goalbar-frame.png` | 560x84 | **frame only** |
| `goalbar-fill.png` | 560x84 | **separate file** so the fill can animate; clip its width to the goal percentage |
| `now-playing.png` | 460x104 | track title overlays the dash |
| `socials-strip.png` | 760x92 | inline lockup + handle |
| `label-donate/discord/commands.png` | 320x70 | call-to-action strips |
| `gameplay-frame.png` | 1920x1080 | border, with red corner accents |
| `timer-countdown.png` | 560x190 | "STARTING IN" + 00:00 slot |
| `timer-countup.png` | 560x190 | "LIVE FOR" + 00:00 slot |
| `poll-frame.png` | 600x400 | 3 options, **empty bars** |
| `poll-bar-fill.png` | 548x14 | **separate file**; clip width to the percentage |
| `prediction-frame.png` | 600x300 | 2 outcomes, for Twitch predictions |

## Rules
- Shared panel: `rgba(17,21,26,.90)` with a 5px `#D62325` left edge.
- Never flatten the goal bar or the poll bars into one image — the fill has
  to be clippable.
- **Fills are the INTERIOR size, not the outer box.** The bar container is
  18px tall with a 2px border, so a fill the same size as the container
  paints over the stroke. The poll fill is 548x14; drop it at x=26,
  y=145 / 237 / 329 within `poll-frame.png` (y=145 / 237 for
  `prediction-frame.png`).
- Timer digits are placeholders on tabular numerals. The widget's own text
  sits on top; tabular spacing stops the digits jittering as they change.
- Predictions are a different widget from polls (two outcomes, not three
  options) and have their own frame.
- Text placeholders (`@yourhandle`, track title, counts) are filled by the
  widget at runtime or edited in `tools/overlay.js`.
- Verified against a mid-tone gameplay background, not just black — panels
  hold contrast on bright scenes.
