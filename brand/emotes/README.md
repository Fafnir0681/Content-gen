# Emote set

Five emotes at the three sizes Twitch requires. Transparent PNG.

| Emote | Reads as |
|---|---|
| `laugh` | open-mouthed belly laugh |
| `rage` | red face, bared teeth |
| `pog` | wide eyes, round O mouth |
| `sad` | downturned, single bold tear |
| `smug` | goggles pulled down over the eyes |

Upload all three sizes per emote: **112, 56 and 28**. Twitch rejects
anything that is not exactly those dimensions.

## What 28px actually demands
Emotes cannot be derived from the existing art. Face crops taken from the
mascot and the pose set were tested first: readable at 112, marginal at 56,
and **indistinguishable mush at 28** — every expression collapsed into the
same blonde blob with two red dots.

They have to be drawn FOR 28px: head filling the frame, very few large flat
shapes, heavy outlines, one exaggerated feature each. `smug` is the most
legible of the set precisely because two big red lenses survive scaling
where a subtle expression does not.

## Cutout notes
Generated emotes come on a flat field and need the background removed.
Two failures worth remembering, both now handled in `tools/cutout.py`:

- **Background detection by "most common colour" fails on a close-up face**
  — the skin outnumbers the background. Pass `corners` as the 6th argument
  to sample the frame edges instead.
- **Corner sampling must inset past any border** the generator draws, and
  must take the MODE of the corner patches, not the median. A median of
  mixed corners returns a colour present nowhere in the image.

A head that bleeds off the edge of the frame cannot be cut out at all —
there is no silhouette. The prompt must demand a clear margin on all four
sides. `smug` had to be regenerated for exactly this reason.

    python3 tools/cutout.py <in.png> <out.png> 26 0.8 9 corners
