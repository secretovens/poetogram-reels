# its_poetogram — content autopilot (v3, from 27 Nov 2026)

Daily plan: 3 NEW reels as Trial Reels (non-followers only, graduation MANUAL) → the next day the same 3 reels go out as main reels → plus 1 carousel. Posting slots (IST): 08:43 main+trial · 12:43 main+trial · 18:43 carousel · 21:43 main+trial.

- **Main look from 27 Nov evening: `scene`** — colourful flat illustration drawn in code (`tools/scene.py`) that matches the lines: sky (golden/sunrise/dusk/night/rain/day/pink) + place (rooftop/city/room/office/park/street/village/station/kitchen/balcony) + people (man/woman/oldman/oldwoman/kid/girl; pose stand/sit/back/walk; arm down/lap/shoulder/phone/up) + props (chai kite phone laptop swing lamp plant moon birds lights clock suitcase scooter train umbrella books tiffin flowers stars). Item field `scene`: {sky, place, people:[{who,pose,x,arm,shirt}], props, seed}. Music follows the sky.
- `content.json` — reel items: id, lines, accent, art, tag, seed, **style**, **music**(optional), **hook**, **cta**, caption
- `tools/reel3.py content.json <ids>` — v3 reels: 7 rotating styles (`tools/styles.py`: parchment, noir, diary, night, poster, dusk, chalk), line/word reveal, hook text on top, CTA pill at the end, slow push-in, original music (`tools/music2.py`: piano, sitar, strings, guitar, musicbox, santoor)
- `carousels.json` + `tools/carousel.py carousels.json <ids>` — 1080x1350 slides in the same styles → `carousels/<id>/NN.jpg`
- `schedule.json` — `queue` (reels: trial_posted / main_posted + ids/times) and `carousels` (posted)
- `lines_used.md` — every line already used (never repeat)
- Rules: never use the same style twice in a row; max 5 hashtags; captions = hook question, the lines, CTA (save/send/comment), series line, keyword line, hashtags.
- Old v2 tools (build_reel.py, make_card.py, make_music.py) kept for reference.

## v4 (27 Nov night) — "नज़रिया · PERSPECTIVE" series (current)
Owner direction: no emotional/family/relationship lines, no lectures. Life, individuality, the crowd, self-value — a different perspective that sparks debate, backed by verified quotes from writers/philosophers/books/studies. Classy, international, brand-grade. No carousels. Owner posts his own reel daily at 8 PM.
- `thoughts.json` + `tools/think.py thoughts.json <ids>` — 4-slide reels (~20 s): hook → quote (original language + author, work, year, optional Hindi gist) → perspective (Hindi) → debate question with options A/B + "Comment A या B". Themes ink/ivory/slate/wine rotate; motif = a quiet crowd of identical marks with one gold mark that differs (grid, flock, people, steps, chairs, ripple, arrows, umbrellas, hill, door).
- Posting: 5 new trial reels a day, the same 5 as main reels the next day.

- Music (v4): `tools/music3.py` — original cinematic score per reel (felt piano motif, string pad, cello, soft pulse after the hook, shimmer on the last slide, whoosh + low boom on every slide change), moods dark/hopeful/eastern/tense; loudness normalised to -14 LUFS (Instagram level).
