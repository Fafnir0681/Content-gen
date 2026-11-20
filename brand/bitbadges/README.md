# Bit badges

Eight tiers at 18, 36 and 72px, plus source SVGs. Transparent PNG.
Twitch allows up to 28 tiers; these are the eight most-used starting
points. Partner feature — upload under Creator Dashboard → Subscriptions →
Bits and Cheers → Manage Cheer Badges.

**Size limit: all three images of one badge must total under 40KB.**
The largest here is ~2.4KB, so there is plenty of headroom.

## The system
Sub badges own the **anvil** (the forge). Bit badges own the **flask**
(the lab). Different silhouette, so the two never get confused at 18px —
a round disc versus a flask reads instantly where a colour change would
not.

Tier progression is the **liquid level rising**, which is monotonic,
meaningful, and legible as overall colour mass. Once the flask is full the
level can no longer carry the progression, so the top tiers move to a
plate behind it.

| Bits | Flask |
|---|---|
| 1 | empty |
| 100 | 30% full |
| 1,000 | 55% |
| 5,000 | 80% |
| 10,000 | full |
| 25,000 | full, thick outline |
| 50,000 | full, on a black plate |
| 100,000 | full, on a red plate |

## Two failures worth remembering
- **Outline colour cannot be used for tier progression here.** A white
  outline vanishes against the white flask body and a red one merges with
  the red liquid; both collapsed to a shapeless blob.
- **The outline must contrast with whatever sits behind it.** On the black
  plate a black outline disappears and the flask reads as a bare red
  triangle, so the outline flips to white there.

## Regenerating

    python3 tools/bitbadges.py .
    node tools/rendersvg.js bitbadges/bit-1.svg out.png 18 none
