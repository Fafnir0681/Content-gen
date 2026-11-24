# Wordmark

Type only, no mark. 40 SVGs. For mark + type together see `../lockup/`.

Everything here is **outlined** — the glyphs are paths, not text, so Chakra
Petch is not required to open, render or hand off these files. That is why
the press kit can be sent to a stranger without shipping a font.

Rebuild with `python3 tools/makewordmark.py`.

## Naming

    wordmark-<layout>-<ground>[-<forge>]-<labs>.svg

| Part | Values | Meaning |
|---|---|---|
| `layout` | `stacked` `inline` | two lines, or one |
| `ground` | `ondark` `onlight` | the background it is drawn for |
| `forge` | *(omitted)* `redforge` `gunmid` `gunlight` `gungrad` | how FORGE is coloured |
| `labs` | `neutral` `red` | how LABS is coloured |

`neutral` means white on dark and black on light — it follows the ground.
Omitting the `forge` part means FORGE takes the same neutral tone as PLAY.

2 layouts × 2 grounds × 5 FORGE treatments × 2 LABS colours = 40.

## The one in use

**`wordmark-stacked-ondark-redforge-neutral.svg`** and its `-inline` and
`-onlight` siblings. FORGE in brand red at the heavier weight, LABS neutral.

The `gun*` variants render FORGE in grey (`#6E757D`, `#8C949D`, or a vertical
gradient between them). They were the earlier direction and are kept because
they still read well on busy backgrounds where red competes with gameplay.

## Construction notes

PLAY is 400 weight, FORGE is 700 — the weight break is what carries the name,
so do not even out the weights.

LABS is justified to the exact width of PLAYFORGE so the two lines lock as a
block. The letter-spacing is **solved arithmetically**, not eyeballed:

    track = (width(PLAYFORGE) - width(LABS)) / (len("LABS") - 1)

If you change the size, the type or the string, re-run the generator rather
than nudging the tracking by hand.

## Colours
Red `#D62325` · Black `#110D0D` · White `#FFFFFF`
