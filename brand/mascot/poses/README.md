# Mascot pose set

Twelve alpha cutouts, four poses x three variants, all derived from
`mascot/mascot-master.png` via reference-driven generation and cut out with
`tools/cutout.py` (tolerance 20, closing radius 11).

| Pose | Use | Note |
|---|---|---|
| `pose-celebrate-*` | follow / sub / raid alerts | strongest silhouette of the set |
| `pose-work-*` | BRB screen | introduces an anvil prop not in the master |
| `pose-wave-*` | Starting Soon, raid outro | open palm reads well at small size |
| `pose-point-*` | follow CTA, socials | foreshortened arm; weakest pose of the four |

## Picks
`celebrate-2`, `work-3`, `wave-2`, `point-1` — but all twelve are kept so
the choice can change without regenerating.

## Known defects
- `pose-work-1` and `pose-work-2`: the anvil **stand** is partly eaten by the
  cutout. The props use thinner strokes than the figure, so the closing
  radius that seals the costume does not seal them. `pose-work-3` is clean.
  If a damaged one is needed, re-cut that file with a larger closing radius
  and re-check the leg gap stays open.

## Generation
Model `gemini-3-pro-image`, chosen over the cheaper gpt-image because it
holds costume and identity across pose changes — an earlier gpt-image edit
drifted the coat, boots and belt. ~1,827 credits per variation.

Every prompt names the reference's role, states the pose change, and lists
what must stay identical. Dropping that preserve list is what caused the
earlier drift.
