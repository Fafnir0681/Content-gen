
## Idle loop

`mascot-plate-idle.webm` — 484x680, 6.0s, 30fps, VP9 with a real alpha
channel (`alpha_mode=1`). Rebuild with `node tools/mascotidle.js`.

With no face-cam the plate is the only thing on screen carrying a pulse, so a
static PNG reads as a frozen stream. The amplitude is deliberately low: it has
to survive being looked at for four hours without becoming a tic.

| Beat | Period | What it does |
|---|---|---|
| breathing | 3.0s | scale from the feet, +0.6% — the chest rises, the boots do not |
| weight shift | 6.0s | ±0.22° rotation about the feet |
| forge light | 1.2s + 0.75s | summed, so the flicker never visibly repeats |
| flask glow | 1.5s + 1.0s | the liquid brightens |
| hammer rune | 2.0s | the head is still hot |
| embers | 3.0s | six, phase-offset, rising off the hammer |

### Seamlessness
Every period divides 6.0s exactly, and **frame 180 is not rendered** — it
would duplicate frame 0 and stutter the loop. Verified by pixel difference:
the wrap (179→0) is a *smaller* step than its neighbours at the same phase
(1.74 vs 1.96 and 1.84 mean absolute difference), because t=0 is where
breathing crosses zero and is moving fastest. Measuring the wrap against
slow-phase frames instead makes a seamless loop look broken — compare like
for like.

### How the glows are made
A masked, brightened copy of the artwork itself, faded in — not a coloured
blob painted on top, which flattens the linework. The mask is a radial
gradient centred on the flask and on the hammer rune, so the glow respects
the art's own alpha and never spills past the silhouette. The separate
`.halo` divs are the light spilling into the air and *are* allowed outside it.

### No blink
The spec asked for blinking. The eyes in this art are about 7x5 px of white
sclera — roughly 1.4% of the figure's width. A blink there is not perceptible
at plate size, and faking an eyelid on flat raster art risks a visible seam
across the face for no gain. Breathing, forge light and the glows carry the
"alive" read instead. If a blink is ever wanted, it needs the mascot redrawn
in layers, not a filter on the flat plate.
