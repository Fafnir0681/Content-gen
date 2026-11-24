# Phase 2 — on-stream overlay components

Transparent PNGs, positioned as sources in OBS. Rebuild with
`node tools/overlay.js [name]`.

| File | Size | Notes |
|---|---|---|
| `nameplate.png` | 640x112 | mark + name + handle |
| `chatbox.png` | 400x660 | frame only; chat widget sits inside it |
| `recent-events.png` | 460x172 | latest follower / latest sub |
| `goalbar-frame.png` | 560x84 | **frame only** |
| `goalbar-fill.png` | 560x84 | **separate file**; drops at +0+0 over the frame |
| `now-playing.png` | 460x104 | track title overlays the dash |
| `socials-strip.png` | 760x92 | inline lockup + handle |
| `label-donate/discord/commands.png` | 320x70 | call-to-action strips |
| `gameplay-frame.png` | 1920x1080 | border, with red corner accents |
| `timer-countdown.png` | 560x190 | "STARTING IN" + 00:00 slot |
| `timer-countup.png` | 560x190 | "LIVE FOR" + 00:00 slot |
| `poll-frame.png` | 600x400 | 3 options, **empty bars** |
| `poll-bar-fill.png` | 552x18 | **separate file**; drops at the container origin |
| `prediction-frame.png` | 600x300 | 2 outcomes, for Twitch predictions |

## Rules
- Shared panel: `rgba(17,21,26,.90)` with a 5px `#D62325` left edge.
- Never flatten the goal bar or the poll bars into one image — the fill has
  to be clippable.
## Bar fills — the masking convention

Every fill shares the **exact footprint of its container** and paints the red
only inside the border, using a transparent 2px border with
`background-clip: padding-box`. That means a fill drops at its container's
own origin and is aligned by construction — no per-pixel nudging, and the
container's stroke stays visible on all four sides.

| Fill | Drop at | Width for P% |
|---|---|---|
| `goalbar-fill.png` | +0+0 over `goalbar-frame.png` | `20 + round(520 * P/100)` |
| `poll-bar-fill.png` | x=24, y=144 / 236 / 328 in `poll-frame.png` | `2 + round(548 * P/100)` |
| `poll-bar-fill.png` | x=24, y=144 / 236 in `prediction-frame.png` | same |

Crop the fill from the left to the computed width; never scale it, or the
rounded cap distorts.
- Timer digits are placeholders on tabular numerals. The widget's own text
  sits on top; tabular spacing stops the digits jittering as they change.
- Predictions are a different widget from polls (two outcomes, not three
  options) and have their own frame.
- Text placeholders (`@yourhandle`, track title, counts) are filled by the
  widget at runtime or edited in `tools/overlay.js`.
- Verified against a mid-tone gameplay background, not just black — panels
  hold contrast on bright scenes.
