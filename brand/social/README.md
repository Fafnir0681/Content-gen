# Social and growth assets

| File | Size | Use |
|---|---|---|
| `x-header-1500x500.png` | 1500x500 | X / Twitter header (3:1) |
| `bluesky-banner-3000x1000.png` | 3000x1000 | Bluesky banner, same 3:1 at 2x |
| `header-3x1.png` | 1500x500 | generic 3:1 source for other platforms |
| `avatar-512.png` | 512x512 | square profile image |
| `schedule-square.png` | 1080x1080 | feed post |
| `schedule-story.png` | 1080x1920 | story / vertical |
| `lower-third.png` | 1280x240 | transparent, for edited video |

**Instagram has no header image** — it uses a square avatar and square or
vertical posts, so there is no IG banner here by design. Use `avatar-512`
and the schedule graphics.

Schedule day times are placeholders; edit `DAYS` and the time strings in
`tools/social.js` and re-render.

Rebuild: `node tools/social.js [name]`
