# Phase 1 — channel page assets

Composed from `brand/` sources via `tools/channel.js`. No generation; rebuild
any time with `node tools/channel.js [scene-name]`.

| File | Size | Platform notes |
|---|---|---|
| `twitch-banner.png` | 1200x480 | profile banner (5:2) |
| `twitch-offline.png` | 1920x1080 | video player banner — most-seen asset you own |
| `kick-banner.png` | 1920x1080 | page crops top/bottom by width; content stays centred |
| `kick-offline.png` | 1920x1080 | shows ~2 min after stream ends |
| `youtube-banner.png` | 2560x1440 | all content inside the centred 1546x423 safe band |
| `youtube-thumbnail-template.png` | 1280x720 | layered slots — headline left, subject right |
| `youtube-watermark.png` | 150x150 | mark only |
| `panel-twitch-*.png` | 320x160 | 6 panels; Twitch fixes panel width at 320 |
| `panel-kick-*.png` | 640x320 | 6 panels at Kick's 2:1 |

## Layout rules enforced in the generator

- **Two zones, never overlapping.** Type occupies the left zone, the mascot is
  contained in the right. An earlier version let the mascot cross into the
  wordmark — the zone split prevents it structurally.
- **YouTube uses the BUST, not the full figure.** The safe band is only 423px
  tall; a full figure gets its head cropped on mobile and TV. Verified by
  cropping to the exact safe rectangle.
- **Inline SVGs are width-constrained.** The source marks are 2048px intrinsic,
  so an unconstrained one blows out the layout.

## Placeholders
Panel titles are generic (About / Schedule / Rules / Specs / Commands /
Support). Social handles and schedule copy are deliberately absent — add them
to the scene definitions in `tools/channel.js` and re-render.
