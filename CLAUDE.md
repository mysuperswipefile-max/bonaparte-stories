# Bonaparte Stories: daily run

This repo makes and publishes one short history video per day on TikTok and YouTube Shorts,
for the account "Bonaparte Stories". Read STYLE.md before writing any script.

## Each daily run
1. `pip install --break-system-packages -q edge-tts shapely matplotlib numpy scipy pillow` (ffmpeg is required).
2. Read `state.json`: `current_series` and `next_part`.
3. If `series/<series>/part<N>.txt` does not exist, the series is finished: go to "New series" below, then continue with part 1 of the new series.
4. Render: `python pipeline/render_part.py <series> <N>` -> `docs/videos/<series>_p<N>.mp4`.
   - If the image pool is exhausted, find more public-domain images (`pipeline/rijks.py`, `pipeline/autocrop.py`), add them to `assets/images/` and to the pool in `series.json`, and re-render.
   - Prefer an explicit per-sentence plan in `series.json` -> `plans` so each image matches what is being said.
5. Check the video: extract ~16 frames into a contact sheet and LOOK at it. Duration must be >= 61 s; no image repeated; captions readable; title + PART badge visible at the start. If it fails, fix and re-render. Never publish a broken video.
6. Commit and push the video. Wait until `https://mysuperswipefile-max.github.io/bonaparte-stories/videos/<series>_p<N>.mp4` returns HTTP 200 (GitHub Pages can take a few minutes).
7. Caption file: hook line + newline + series hashtags from `series.json`. YouTube title: `<Series title in Title Case> - Part <N>` (max 100 chars).
8. Publish: `python pipeline/publish_buffer.py post <url> <caption_file> --title "<title>"` (needs env BUFFER_API_KEY). If the mutation shape is rejected, run `publish_buffer.py schema`, fix the script, and retry once.
9. Update `state.json` (append to `posted` with date, series, part, Buffer post ids; increment `next_part`), commit, push.
10. On Sundays, send the owner a short report: videos published this week, any failures.
If anything fails and cannot be fixed, do not publish; send the owner a short message saying what broke.

## New series
- Take the first item of `upcoming_series` in state.json, remove it from the list, set `current_series` to a short slug, `next_part` to 1.
- Research the battle (WebSearch/WebFetch, at least 2 sources) -> `series/<slug>/sources.md`.
- Write all parts following STYLE.md -> `series/<slug>/part<N>.txt`, one sentence per line, the viewer question on its own line (no label).
- Have a separate agent fact-check every part against sources.md; apply its corrections.
- Gather 15+ fitting public-domain images per part, draw 2-4 maps, write `series/<slug>/series.json` (title, parts, colors, hashtags, plans or pools).
