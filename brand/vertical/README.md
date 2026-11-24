# Phase 5 — vertical / TikTok

All 1080x1920 (9:16).

| File | Use |
|---|---|
| `scene-starting/brb/ending.png` | vertical scene screens |
| `overlay.png` | transparent on-stream overlay (nameplate + latest strip) |
| `alert-<name>.webm` | **portrait alerts**, 9 of them, alpha |
| `alert-<name>.png` | the same alert's hold frame, as a still |
| `alert-position-guide.png` | where an alert sits in the frame, against the safe box |
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

## Alerts

Redrawn in portrait, not the horizontal art re-anchored. The horizontal alert
reads left to right — mascot, then a panel with a red left edge. Rotated into
9:16 that wastes the frame, so the portrait version stacks it: mascot above,
panel below, and the red bar becomes the panel's **top** edge. The mascot's
feet overlap into the panel exactly as they overlapped its left edge before,
and the bar passes **behind** the legs — the same stacking rule as the
horizontal set.

840x760, or 840x840 for raid. 840 fits inside the 856-wide safe box with 8px
to spare each side, and the placement guide puts it at (68, 450) — centred in
the safe rectangle.

**Timing is identical to the horizontal alerts, impact at 450ms included, so
one sound library serves both orientations.** Only the entry directions are
rotated to match the layout: the bar draws out sideways, the panel opens
downward, and the exit drifts down instead of left.

Each alert's PNG still is its own hold frame at t=2.5s, taken from the same
render, so the still and the video can never drift apart.

Rebuild: `node tools/vertical.js` (scenes, overlay, clip template) and
`node tools/valerts.js` (alerts; `valerts.js guide` re-renders only the
placement guide).
