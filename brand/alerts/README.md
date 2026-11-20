# Alert frames

Transparent PNGs. The alert widget overlays the live username and amount on
the placeholder slots. Rebuild with `node tools/alerts.js [name]`.

| File | Size | Pose |
|---|---|---|
| `alert-follow.png` | 920x420 | wave-2 — welcoming, not celebrating |
| `alert-sub.png` | 920x420 | celebrate-2 |
| `alert-resub.png` | 920x420 | celebrate-2 |
| `alert-giftsub.png` | 920x420 | celebrate-3 |
| `alert-bits.png` | 920x420 | celebrate-1 |
| `alert-tip.png` | 920x420 | celebrate-1 |
| `alert-raid.png` | 920x**460** | celebrate-2, scaled up |
| `alert-ytmember.png` | 920x420 | celebrate-3 |
| `alert-kicksub.png` | 920x420 | celebrate-2 |

Raid is deliberately larger than the rest: it is the only alert that brings
new viewers to the channel, so it should out-shout the others.

Follow uses the waving pose rather than celebrating — a follow is a greeting,
and if every alert celebrates, none of them read as special.

## NOT DONE
- **Sound.** Every alert needs audio; none is included. Sourcing it is a
  separate job.
- **Animation.** These are static frames. Animating them (entry slide, the
  glass sheen sweep in `glass-motion/`) is the remaining step before they
  are production alerts.

Text slots say PLACEHOLDER; the widget replaces them at runtime.
