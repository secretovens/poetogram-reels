# its_poetogram — reel autopilot

- `content.json` — lines, accent word, art motif, caption for each reel
- `tools/build_reel.py content.json <id|all>` — builds `cards/`, `covers/`, `reels/` (line-by-line reveal, original piano music)
- `schedule.json` — posting queue; the scheduled task posts the first item with `"posted": false`
- `lines_used.md` — every line already used (never repeat)
