# Subscriber badges

Eight tiers at 18, 36 and 72px, plus the source SVGs. Upload all three sizes
per tier; Twitch rejects anything that is not exactly those dimensions.

Tiers: 1, 2, 3, 6, 9, 12, 18, 24 months.

## Design constraint
18px is smaller than the emotes and far smaller than the mark's small cut.
A face is hopeless at that size and fine ornament disappears, so tiers
**cannot** differentiate by added detail — only by large colour mass.

The anvil silhouette is reused directly from `mark/mark-full.svg`, so a
badge and the mark are visibly the same object.

Progression runs light -> red -> dark, with the top two tiers marked by a
much thicker ring:

| Months | Disc | Anvil | Ring |
|---|---|---|---|
| 1 | white | black | black |
| 2 | white | red | black |
| 3 | red | white | black |
| 6 | red | black | black |
| 9 | black | white | black |
| 12 | black | red | black |
| 18 | red | white | black, thick |
| 24 | black | red | red, thick |

Every tier carries a dark outer keyline so it survives on Twitch's light
theme; an earlier version used white discs with thin coloured rings and
both vanished on `#EFEFF1`.

## Known limitation
Six of the eight read as clearly distinct at 18px. **3mo vs 18mo** and
**12mo vs 24mo** differ only by ring thickness — three brand colours across
disc, anvil and ring do not yield eight unmistakable combinations at that
size. Twitch shows the tier name on hover, so this is a real but minor
compromise. Widening the palette or dropping to five tiers would remove it.

## Regenerating

    python3 tools/badges.py .
    node tools/rendersvg.js badges/badge-01mo.svg out.png 18 none
