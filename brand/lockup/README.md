# Lockup

Mark + wordmark together. 40 SVGs, one per wordmark variant.

Rebuild with `python3 tools/makelockup.py`. The generator **globs**
`../wordmark/wordmark-*.svg` rather than matching a fixed list of names, so a
new wordmark variant automatically gets a lockup. An earlier fixed-pattern
version silently produced nothing for new variants, which is the kind of
failure you only notice much later.

## Naming

Identical to the wordmark it is built from, with the prefix swapped:

    lockup-<layout>-<ground>[-<forge>]-<labs>.svg

So `wordmark-stacked-ondark-redforge-neutral.svg` becomes
`lockup-stacked-ondark-redforge-neutral.svg`. See `../wordmark/README.md` for
what each part means.

## The one in use

**`lockup-stacked-ondark-redforge-neutral.svg`** — the channel screens, the
stinger, the bumper and the vertical scenes all pull this file.

## Geometry

The gap between mark and type is deliberately tight; it was reduced from the
first pass on purpose, and the mark diameter was increased to match the
height of the stacked type so the two read as one object rather than as an
icon sitting next to some words.

If you place a lockup against a rule or divider, **measure its viewBox** —
do not assume it is vertically centred in its own box. An early channel
screen had a red rule running straight through the mark because the lockup's
occupied band was assumed rather than computed.
