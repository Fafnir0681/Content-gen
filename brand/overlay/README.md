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

## Rules
- Shared panel: `rgba(17,21,26,.90)` with a 5px `#D62325` left edge.
- Never flatten the goal bar into one image.
- Text placeholders (`@yourhandle`, track title, counts) are filled by the
  widget at runtime or edited in `tools/overlay.js`.
- Verified against a mid-tone gameplay background, not just black — panels
  hold contrast on bright scenes.
