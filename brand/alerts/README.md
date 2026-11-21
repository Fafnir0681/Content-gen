# Alerts

Two files per alert. `alert-*.png` is the still frame; `alert-*.webm` is the
animated version — VP9 with a real alpha channel (`alpha_mode=1`, verified by
decoding frames back to RGBA). Use the WebM on stream; the PNG is for layout
mockups and for widgets that will not take video.

Rebuild with `node tools/alerts.js [name]` (stills) and
`node tools/alertanim.js [name]` (animation + encode, one command).

| File | Size | Duration | Pose |
|---|---|---|---|
| `alert-follow` | 920x420 | 4.4s | wave-2 — welcoming, not celebrating |
| `alert-sub` | 920x420 | 4.4s | celebrate-2 |
| `alert-resub` | 920x420 | 4.4s | celebrate-2 |
| `alert-giftsub` | 920x420 | 4.4s | celebrate-3 |
| `alert-bits` | 920x420 | 4.4s | celebrate-1 |
| `alert-tip` | 920x420 | 4.4s | celebrate-1 |
| `alert-raid` | 920x**460** | **5.2s** | celebrate-2, scaled up |
| `alert-ytmember` | 920x420 | 4.4s | celebrate-3 |
| `alert-kicksub` | 920x420 | 4.4s | celebrate-2 |

Raid is deliberately larger and longer than the rest: it is the only alert
that brings new viewers to the channel, so it should out-shout the others. It
also carries a stronger impact flash.

Follow uses the waving pose rather than celebrating — a follow is a greeting,
and if every alert celebrates, none of them read as special.

## Animation beats

Absolute seconds, identical across every alert so one timing note covers the
whole set:

| Time | Beat |
|---|---|
| 0.00–0.14 | red edge bar drops in from the top |
| 0.12–0.42 | panel wipes open rightward from that bar |
| 0.16–0.58 | mascot rises with an overshoot and settles |
| **0.45** | **IMPACT** — flash, edge glow, mark pop |
| 0.42–0.80 | caption, name, subline stagger in |
| 1.00–1.75 | sheen sweeps across the panel |
| last 0.42 | stage drifts left and fades out |

**The hammer strike in the sound must land at 450 ms.** That is the frame the
mascot lands the pose and the panel flashes. `alert-resub` is the one
exception: it has two impacts, at 450 ms and 630 ms, to match the
double-strike cue in `SOUNDS-TODO.md`.

The last frame is fully transparent on every file — verified. An alert that
is still opaque on its final frame hard-cuts over the scene underneath and
reads as a glitch, which is the same failure the stinger had.

## Durations

4.4s is long enough to read a username and short enough not to stack during a
raid. If you change it, change the sound length to match — the widget cuts
whichever runs longer.

## NOT DONE
- **Sound.** Every alert needs audio; none is included. Alert widgets take the
  audio as a separate input, so these are production-ready video as they
  stand — the sound drops in alongside, it is not muxed into the WebM. See
  `brand/SOUNDS-TODO.md`.

Text slots say PLACEHOLDER; the widget replaces them at runtime.

## Encoding notes
The build runs every frame through `convert PNG32:` before ffmpeg. Frames that
happen to be fully opaque otherwise save without an alpha channel, and a mixed
sequence makes ffmpeg drop alpha for the whole clip. ffprobe reports the base
stream as `yuv420p` even when alpha is present — check the container tag
`alpha_mode=1`, or decode frames back to RGBA.

## Stacking order
The red edge bar sits **behind** the mascot (`z-index:1` against the mascot's
`2`). The raid pose raises the flask across the bar's column, and anything
drawn over that hand reads as a seam through the artwork. The stills got this
free because the bar was the panel's `border-left`; splitting it into its own
element for the drop-in animation is what broke it.
