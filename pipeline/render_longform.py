"""Assemble a finished series into one long-form 16:9 YouTube video, plus thumbnail and metadata.
Usage: python pipeline/render_longform.py <series>
Needs: series/<series>/part*.txt, series.json, longform/<series>/intro.txt and meta.json.
Output: docs/longform/<series>.mp4 (public via GitHub Pages, kept under ~90 MB),
        longform/<series>/thumbnail.jpg, title.txt, description.txt
"""
import sys, os, json, math, shutil, subprocess, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import build
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
build.set_landscape()
MAX_SHOT = 4.0          # fast cuts: a new shot every 4 s at most
COLORS = ["#FF3B5C", "#00B4D8", "#FF8C00", "#7CFC00", "#B26BFF", "#FF4D9D", "#00C2A8", "#FFC300", "#3D8BFF", "#FF6B35"]

def run(c, **k): subprocess.run(c, check=True, **k)
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))

def img_path(spec):
    if spec.startswith("map:"): return os.path.join(ROOT, "assets/maps", spec.split(":")[1] + ".png")
    return os.path.join(ROOT, "assets/images", spec.split(":")[0] + ".jpg")

def chapter_lines(path, last, outro):
    lines = [l.strip() for l in open(path) if l.strip()]
    if lines and (re.search(r"is next\. Follow", lines[-1]) or lines[-1].startswith("Follow for")):
        lines = lines[:-1]
    if last and outro: lines.append(outro)
    return lines

def main(series):
    sdir = os.path.join(ROOT, "series", series); ldir = os.path.join(ROOT, "longform", series)
    cfg = json.load(open(os.path.join(sdir, "series.json"))); meta = json.load(open(os.path.join(ldir, "meta.json")))
    nparts = len(glob.glob(os.path.join(sdir, "part*.txt")))
    work = os.path.join(ROOT, "work", f"long_{series}"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    chapters = [("intro", [l.strip() for l in open(os.path.join(ldir, "intro.txt")) if l.strip()])]
    for p in range(1, nparts + 1):
        chapters.append((p, chapter_lines(os.path.join(sdir, f"part{p}.txt"), p == nparts, meta.get("outro"))))
    # every image of the series, used as a fallback pool
    allpool = []
    for k, v in cfg.get("pools", {}).items(): allpool += [x for x in v if x not in allpool]
    for v in cfg.get("plans", {}).values():
        for sent in v:
            for x in sent:
                n = x.split(":")[0] if not x.startswith("map:") else ":".join(x.split(":")[:2])
                if n not in allpool: allpool.append(n)
    outs = []; starts = []; t = 0.0
    for ci, (key, lines) in enumerate(chapters):
        cdir = os.path.join(work, f"c{ci:02d}"); os.makedirs(cdir); os.chdir(cdir)
        open("script.txt", "w").write("\n".join(lines) + "\n")
        run([sys.executable, os.path.join(ROOT, "pipeline/tts.py"), "script.txt"], env=dict(os.environ, RATE="+6%", **({"KOKORO_VOICE": cfg["voice"]} if cfg.get("voice") else {})))
        tm = json.load(open("timing.json")); sents = tm["sents"]; total = sents[-1][1]
        run([sys.executable, os.path.join(ROOT, "pipeline/music.py"), str(total + 0.8), str(1000 + ci * 17 + len(series))])
        # image order: this part's own pool first, then the rest of the series
        own = cfg.get("pools", {}).get(str(key), []) if key != "intro" else ["aic_1", "map:m3_italy", "map:m4_nov", "arcole_r", "wounded"]
        if key != "intro" and str(key) in cfg.get("plans", {}):
            own = [x.split(":")[0] if not x.startswith("map:") else ":".join(x.split(":")[:2]) for s in cfg["plans"][str(key)] for x in s]
        order = [x for x in own if x in allpool or x.startswith("map:")] + [x for x in allpool if x not in own]
        order = [x for x in order if os.path.exists(img_path(x))]
        plan = []; k = 0
        for (a, b, _) in sents:
            n = max(1, math.ceil((b - a) / MAX_SHOT)); shots = []
            for _ in range(n):
                shots.append(img_path(order[k % len(order)])); k += 1
            plan.append(shots)
        if key == "intro": badge, title = meta.get("intro_badge", "PART 0"), meta.get("intro_title", cfg["title"])
        else: badge, title = f"CHAPTER {key}", meta["chapter_titles"][key - 1].upper()
        out = os.path.join(cdir, "chapter.mp4")
        build.build(ci, COLORS[ci % len(COLORS)], plan, out, T0=0, TT=round(min(sents[0][1] + 0.3, 6.0), 2),
                    title=title, badge=badge, music_vol=0.16, allow_repeat=True)
        outs.append(out); starts.append(t); t += dur(out)
    os.chdir(work)
    open("list.txt", "w").write("".join(f"file '{o}'\n" for o in outs))
    os.makedirs(os.path.join(ROOT, "docs/longform"), exist_ok=True)
    dst = os.path.join(ROOT, "docs/longform", f"{series}.mp4")
    vk = max(500, int((88 * 8 * 1024) / t - 100))  # keep the file under ~90 MB (GitHub limit is 100 MB)
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c:v", "libx264", "-preset", "veryfast",
         "-b:v", f"{min(vk,2500)}k", "-maxrate", f"{int(min(vk,2500)*1.3)}k", "-bufsize", f"{min(vk,2500)*2}k",
         "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", dst])
    # metadata
    def ts(x): return f"{int(x//60)}:{int(x%60):02d}"
    names = ["Intro"] + meta["chapter_titles"]
    desc = [meta.get("description", f"The full story of {cfg.get('battle', series)}, told chapter by chapter."), "",
            "Chapters:"] + [f"{ts(s)} {n}" for s, n in zip(starts, names)] + ["", "Sources: " + ", ".join(
            l.split(" ")[1] for l in open(os.path.join(sdir, "sources.md")) if l.startswith("- http")), "",
            cfg.get("hashtags", "")]
    open(os.path.join(ldir, "description.txt"), "w").write("\n".join(desc) + "\n")
    open(os.path.join(ldir, "title.txt"), "w").write(meta["title"] + "\n")
    thumbnail(meta["thumbnail"], os.path.join(ldir, "thumbnail.jpg"))
    print(json.dumps({"video": dst, "duration": round(t, 1), "size_mb": round(os.path.getsize(dst) / 1e6, 1), "chapters": len(outs)}))

def thumbnail(tcfg, path):
    """Bold YouTube thumbnail: painting on the right, two huge lines of text on the left."""
    W, H = 1280, 720
    im = Image.open(img_path(tcfg["image"])).convert("RGB")
    s = max(W / im.width, H / im.height) * 1.25; im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    fx = tcfg.get("focus_x", 0.5); fy = tcfg.get("focus_y", 0.3)
    x0 = int(min(max(im.width * fx - W * 0.68, 0), im.width - W)); y0 = int(min(max(im.height * fy - H * 0.4, 0), im.height - H))
    im = im.crop((x0, y0, x0 + W, y0 + H))
    im = ImageEnhance.Contrast(im).enhance(1.25); im = ImageEnhance.Color(im).enhance(1.3)
    grad = Image.new("L", (W, H)); gd = ImageDraw.Draw(grad)
    for x in range(W): gd.line((x, 0, x, H), fill=int(max(0, 230 - x * 0.42)))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, grad)
    d = ImageDraw.Draw(im); f = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 118)
    y = 170
    for i, line in enumerate(tcfg["text"]):
        col = "white" if i == 0 else tcfg.get("accent", "#FFD400")
        for dx, dy in [(-5,0),(5,0),(0,-5),(0,5),(-4,-4),(4,4),(-4,4),(4,-4)]: d.text((50 + dx, y + dy), line, font=f, fill="black")
        d.text((50, y), line, font=f, fill=col); y += 140
    im.save(path, quality=92)

if __name__ == "__main__":
    main(sys.argv[1])
