# Bonaparte Stories: weekly long-form run (YouTube only)

Runs once a week. Turns every FINISHED short series into one long-form 16:9 YouTube video (about 10-12 minutes).
It never touches the daily shorts or state.json `next_part`.

## Steps
1. `python -m pip install --break-system-packages -q edge-tts kokoro-onnx soundfile shapely matplotlib numpy scipy pillow`. `git pull`.
2. Read state.json. A series is finished when every `series/<slug>/part*.txt` appears in `posted`. Read `longform/done.json` (create it as `{"done": []}` if missing) to skip series already made.
3. If no finished series is waiting: make nothing. End with one line: which series is in progress and how many parts are left before its long-form.
4. For each finished series not yet done (at most 2 per run):
   a. If `longform/<slug>/intro.txt` or `meta.json` is missing, write them (see longform/arcole for the format):
      - intro.txt: a 20-30 second cold open in the MrBeast style: the stakes in the first sentence, then a fast teaser of the biggest moments (a death, a trick, a reversal), then "This is the full story of ...". True facts only.
      - meta.json: a curiosity title (max 70 chars, e.g. "The 3 Days That Almost Destroyed Napoleon"), chapter_titles (one per part), an outro that teases the next series in state.json `upcoming_series`, and a thumbnail spec: one painting with a clear face, focus_x so the face sits on the right, two lines of 2-3 huge words.
   b. `python pipeline/render_longform.py <slug>` -> docs/longform/<slug>.mp4 (kept under ~90 MB), longform/<slug>/thumbnail.jpg, title.txt, description.txt (with chapter timestamps).
   c. Check it: extract ~24 frames across the video into a contact sheet and LOOK at it, look at the thumbnail, confirm duration and that the file is under 95 MB.
   d. Commit and push to main; wait until `https://mysuperswipefile-max.github.io/bonaparte-stories/longform/<slug>.mp4` returns HTTP 200.
   e. Add the slug to longform/done.json, commit, push.
5. End with a message for the owner, ready to upload on YouTube Studio: the video link, the thumbnail link (`https://github.com/mysuperswipefile-max/bonaparte-stories/raw/main/longform/<slug>/thumbnail.jpg`), the title, and the full description.

## Style rules (long-form)
- Fast and dynamic: a new image every 4 seconds at most, slow zooms, a new chapter card about every 70 seconds that re-hooks the viewer.
- Each chapter starts with its hook line; keep the viewer questions (they work even better in long-form).
- Music changes every chapter and stays low under the voice.
