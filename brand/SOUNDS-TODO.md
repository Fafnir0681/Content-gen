# Sound pass — do this where you can hear it

Everything visual is done, animation included; these eleven cues are the only
thing between the alerts/transitions and production ready. ElevenLabs generates them:
node type `sfx`, model `eleven_text_to_sound_v3`.

## Design rule
The brand is a forge inside a lab. Sounds should come from **metal, fire and
glass**, not from generic UI chimes. One shared sonic family: a hammer strike
is the signature, and the bigger the event, the bigger the strike.

## Alerts

| Cue | Suggested prompt | Length |
|---|---|---|
| follow | single light hammer tap on an anvil, bright metallic ring, short decay | 1.0s |
| sub | firm hammer strike on anvil with a warm metallic ring-out | 1.5s |
| resub | double hammer strike, two beats, confident | 1.5s |
| giftsub | hammer strike followed by a scatter of small metallic coins | 2.0s |
| bits | quick bright cascade of small metal pieces landing on an anvil | 1.5s |
| tip | glass flask clink, then a soft metallic shimmer | 1.5s |
| raid | heavy hammer strike, deep forge boom, rising metallic swell | 2.5s |
| ytmember | hammer strike with a brighter, higher ring | 1.5s |
| kicksub | hammer strike with a sharper, punchier attack | 1.5s |

Raid should be the loudest and longest — it is the only alert that brings
new viewers.

**Every alert strike must land at 450 ms**, the frame the animation flashes
and the mascot lands the pose. `resub` is the exception: two strikes, at
450 ms and 630 ms. The alert widget starts the audio and the video together,
so a strike that lands late reads as a sync fault rather than a style choice.

## Transitions

| Cue | Suggested prompt | Timing |
|---|---|---|
| stinger | metal sheet whoosh, then a single hard hammer strike | strike must land at **800ms**, the transition point |
| bumper | low forge rumble building to a hammer strike, then a metallic ring-out | strike around 0.9s, as the lockup lands |

## Checks before accepting a take
- Play it **at stream volume over gameplay**, not in isolation. Alerts that
  sound great solo often vanish under game audio.
- Keep every alert under 2.5s. Longer ones overlap and stack badly during a
  raid.
- Normalise the set to a consistent loudness, or the quiet ones get missed
  and the loud ones startle.
- The stinger strike MUST line up with 800ms or the cut and the sound
  disagree.

## Where they go
Alert sounds are attached in the alert widget, next to the matching
`alerts/alert-*.png`. The stinger and bumper audio get muxed into the video
files, or played as a separate OBS source.
