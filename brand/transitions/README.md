# Stinger transition

`stinger.webm` — 1920x1080, 1.6s, 30fps, VP9 with a real alpha channel
(`alpha_mode=1` in the container, verified by decoding frames back to RGBA).

Diagonal forge shards sweep in from the right, fully cover the frame at the
midpoint, and sweep off to the left. The lockup fades in approaching the
cover, **holds through the whole shard exit**, then fades out over the last
few frames.

## What a stinger is for
It is a **transition element**, not a branding display. Its job is to cover
the screen so the scene cut is hidden. The branding is a passenger.

That is why the lockup must fade before the final frame: after the
transition point the shards sweep off to reveal the NEW scene, so anything
still opaque at the end hangs over that scene and then disappears at a hard
cut, which reads as a glitch. Frame 47 is 1.4% opaque — verified.

If you want a piece whose purpose IS to show the branding, that is a
separate asset: an intro/outro bumper, which runs longer, does not need
alpha, and holds the lockup as the subject rather than as a passenger.

## OBS setup
- **Transition point: 800ms** (frame 24 of 48) — the moment the frame is
  100% covered. Setting this wrong is what makes a stinger look like it
  cuts early.
- Known OBS behaviour: stingers can appear clipped short if the transition
  point is set past full coverage. 800ms is measured, not estimated —
  frame 24 is the first frame at 100% opaque.

## Why WebM VP9 and not MOV
MOV with alpha also works in OBS and uses less CPU, but the files run
300MB+. This encodes to ~170KB. If CPU is a problem on your machine,
re-encode the frames to MOV with alpha and compare.

## Regenerating

    node tools/stinger.js          # writes .stinger-frames/
    for f in .stinger-frames/*.png; do convert "$f" PNG32:"$f"; done
    ffmpeg -y -framerate 30 -i .stinger-frames/%04d.png \
      -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 -lag-in-frames 0 \
      -b:v 0 -crf 26 brand/transitions/stinger.webm

The PNG32 step matters: frames that are fully opaque save without an alpha
channel, and a mixed sequence makes ffmpeg drop alpha for the whole clip.

## Not done
No sound. A forge/anvil strike timed to the cover peak would suit it;
ElevenLabs can generate that (sfx node, `eleven_text_to_sound_v3`).
