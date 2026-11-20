# Phase 5 — vertical / TikTok

All 1080x1920 (9:16).

| File | Use |
|---|---|
| `scene-starting/brb/ending.png` | vertical scene screens |
| `overlay.png` | transparent on-stream overlay (nameplate + latest strip) |
| `alert-position-follow.png` | shows where an alert sits in the vertical frame |
| `clip-template.png` | hook text + clip slots, for Shorts/Reels/TikTok cuts |
| `safe-zone-guide.png` | **check this first** — blocked areas in red, safe box in cyan |
| `tiktok-avatar-512.png` | square profile image |

## The safe zone, and why it is a guess

**No source documents TikTok LIVE's interface.** Every figure available is
for feed or ad video, and they disagree sharply:

| Source | Top | Bottom | Right |
|---|---|---|---|
| Revid | 220 | 480 | 140 |
| ScreenSnap | 120 | 250 | 150 |
| AdaptlyPost | 108 | — | — |
| Postplanify | — | — | 164 |

These assets use the **conservative union** of all of them:

    top 220   bottom 480   left 60   right 164
    usable rectangle 856 x 1220 at (60, 220)

That is deliberately pessimistic. It costs some screen area and guarantees
nothing important sits under TikTok's controls.

**Verify before relying on it.** Open `safe-zone-guide.png` as a stream
overlay, start a test live, and look at your own phone. Editor previews do
not show live controls. If the real safe area is larger, widen `SAFE` in
`tools/vertical.js` and re-render everything in one command.

## Still vertical-specific work
Vertical alerts reuse the horizontal alert art, re-anchored. If you stream
vertical often, they would read better redrawn in a portrait shape.

Rebuild: `node tools/vertical.js`
