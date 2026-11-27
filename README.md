# its_poetogram — content autopilot (v3, from 27 Nov 2026)

Daily plan: 3 NEW reels as Trial Reels (non-followers only, graduation MANUAL) → the next day the same 3 reels go out as main reels → plus 1 carousel. Posting slots (IST): 08:43 main+trial · 12:43 main+trial · 18:43 carousel · 21:43 main+trial.

- `content.json` — reel items: id, lines, accent, art, tag, seed, **style**, **music**(optional), **hook**, **cta**, caption
- `tools/reel3.py content.json <ids>` — v3 reels: 7 rotating styles (`tools/styles.py`: parchment, noir, diary, night, poster, dusk, chalk), line/word reveal, hook text on top, CTA pill at the end, slow push-in, original music (`tools/music2.py`: piano, sitar, strings, guitar, musicbox, santoor)
- `carousels.json` + `tools/carousel.py carousels.json <ids>` — 1080x1350 slides in the same styles → `carousels/<id>/NN.jpg`
- `schedule.json` — `queue` (reels: trial_posted / main_posted + ids/times) and `carousels` (posted)
- `lines_used.md` — every line already used (never repeat)
- Rules: never use the same style twice in a row; max 5 hashtags; captions = hook question, the lines, CTA (save/send/comment), series line, keyword line, hashtags.
- Old v2 tools (build_reel.py, make_card.py, make_music.py) kept for reference.
