"""Render one part of a series.
Usage: python pipeline/render_part.py <series> <part>
Output: docs/videos/<series>_p<part>.mp4  (public via GitHub Pages)
"""
import sys, os, json, math, shutil, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import build

MAX_SHOT = 6.0   # seconds, longest a single image stays on screen
MIN_LEN = 61.0   # TikTok monetisation needs > 60 s

def img_path(spec):
    name = spec.split(":")[1] if spec.startswith("map:") else spec.split(":")[0]
    if spec.startswith("map:"):
        p = os.path.join(ROOT, "assets/maps", name + ".png")
        rest = spec.split(":")[2:] 
    else:
        p = os.path.join(ROOT, "assets/images", name + ".jpg")
        rest = spec.split(":")[1:]
    if not os.path.exists(p): raise SystemExit("missing image " + p)
    if rest:
        nums = [float(x) for x in rest[0].split(",")]
        return (p, *nums)
    return p

def run(cmd, **kw): subprocess.run(cmd, check=True, **kw)

def main(series, part):
    sdir = os.path.join(ROOT, "series", series)
    cfg = json.load(open(os.path.join(sdir, "series.json")))
    work = os.path.join(ROOT, "work", f"{series}_p{part}")
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    os.chdir(work)
    script = os.path.join(sdir, f"part{part}.txt")
    rate = 4
    while True:
        env = dict(os.environ, RATE=f"{rate:+d}%")
        if cfg.get("voice"): env.setdefault("KOKORO_VOICE", cfg["voice"])
        run([sys.executable, os.path.join(ROOT, "pipeline/tts.py"), script], env=env)
        t = json.load(open("timing.json"))
        total = t["sents"][-1][1]
        if total + 0.8 >= MIN_LEN or rate <= -10: break
        rate -= 4   # too short: slow the voice a little and retry
    sents = t["sents"]
    seed = sum(ord(c) for c in series) * 7 + int(part) * 13
    run([sys.executable, os.path.join(ROOT, "pipeline/music.py"), str(total + 0.8), str(seed)])
    plans = cfg.get("plans", {})
    if str(part) in plans:
        plan = [[img_path(s) for s in sent] for sent in plans[str(part)]]
    else:
        pool = list(cfg["pools"][str(part)])
        # never show two files of the same artwork in one video (series.json -> same_artwork)
        groups = {}
        for g in cfg.get("same_artwork", []):
            for x in g: groups.setdefault(x, set()).update(g)
        used = set()
        plan = []
        for (a, b, _) in sents:
            n = max(1, math.ceil((b - a) / MAX_SHOT))
            shots = []
            for _ in range(n):
                while pool and (pool[0].split(":")[1] if pool[0].startswith("map:") else pool[0].split(":")[0]) in used: pool.pop(0)
                if not pool: raise SystemExit("image pool exhausted for part %s: add images" % part)
                spec = pool.pop(0); key = spec.split(":")[1] if spec.startswith("map:") else spec.split(":")[0]
                used |= groups.get(key, set()) | {key}
                shots.append(img_path(spec))
            plan.append(shots)
    color = cfg["colors"][(int(part) - 1) % len(cfg["colors"])]
    out = os.path.join(work, "final.mp4")
    build.build(int(part), color, plan, out, T0=0, TT=round(sents[0][1] + 0.3, 2), title=cfg["title"])
    dst = os.path.join(ROOT, "docs/videos", f"{series}_p{part}.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", out, "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
         "-c:a", "copy", "-movflags", "+faststart", dst])
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst]))
    print(json.dumps({"video": dst, "duration": round(dur, 1), "hook": sents[0][2]}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
