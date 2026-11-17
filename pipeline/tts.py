import os, certifi
# Trust the cloud environment's proxy certificate (keeps TLS verification on)
_CCR="/root/.ccr/ca-bundle.crt"
if os.path.exists(_CCR):
    _comb="/tmp/certifi_plus_ccr.pem"
    if not os.path.exists(_comb):
        open(_comb,"w").write(open(certifi.where()).read()+"\n"+open(_CCR).read())
    certifi.where=lambda: _comb
    os.environ.setdefault("SSL_CERT_FILE",_comb)
import asyncio, json, subprocess, sys, re
import numpy as np
ENGINE=os.environ.get("TTS_ENGINE","kokoro")          # "kokoro" (natural, free, local) or "edge"
KVOICE=os.environ.get("KOKORO_VOICE","bm_george")      # see series.json "voice" to override per series
VOICE=os.environ.get("VOICE","en-US-ChristopherNeural"); RATE=os.environ.get("RATE","+4%"); GAP=0.18
MODEL_DIR=os.environ.get("KOKORO_DIR","/tmp/kokoro_models")
REL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"

def ffdur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))

# ---------- Kokoro ----------
_K=None
def kokoro():
    global _K
    if _K is None:
        os.makedirs(MODEL_DIR,exist_ok=True)
        for f in ["kokoro-v1.0.onnx","voices-v1.0.bin"]:
            dst=os.path.join(MODEL_DIR,f)
            if not os.path.exists(dst) or os.path.getsize(dst)<1_000_000:
                subprocess.run(["curl","-sSL","--retry","3","-o",dst,REL+f],check=True)
        from kokoro_onnx import Kokoro
        _K=Kokoro(os.path.join(MODEL_DIR,"kokoro-v1.0.onnx"),os.path.join(MODEL_DIR,"voices-v1.0.bin"))
    return _K

def one_kokoro(i,text):
    import soundfile as sf
    pct=float(RATE.replace("%","")); speed=max(0.8,min(1.2,0.96+pct/100))
    lang="en-gb" if KVOICE.startswith("b") else "en-us"
    a,sr=kokoro().create(text,voice=KVOICE,speed=speed,lang=lang)
    a=np.asarray(a,dtype=np.float32)
    # trim silence
    env=np.abs(a); thr=max(env.max()*0.02,1e-4); idx=np.where(env>thr)[0]
    s0=max(idx[0]-int(0.03*sr),0); s1=min(idx[-1]+int(0.08*sr),len(a))
    a=a[s0:s1]
    sf.write(f"k{i}.wav",a,sr)
    subprocess.run(["ffmpeg","-y","-v","error","-i",f"k{i}.wav","-ar","48000","-ac","1",f"t{i}.wav"],check=True)
    d=ffdur(f"t{i}.wav")
    # word timings: spread over the clip by character weight (punctuation adds a small pause)
    toks=text.split(); wts=[len(re.sub(r"[^\w']","",t))+1+(3 if re.search(r"[.,;:!?]$",t) else 0) for t in toks]
    tot=sum(wts); t=0.0; out=[]
    for tok,wt in zip(toks,wts):
        dur=d*wt/tot; out.append((t,t+dur*0.9,re.sub(r"[.,;:!?]+$","",tok))); t+=dur
    return out,d

# ---------- Edge (fallback) ----------
async def one_edge(i,t):
    import edge_tts
    c=edge_tts.Communicate(t,VOICE,rate=RATE,boundary="WordBoundary"); w=[]
    with open(f"s{i}.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary": w.append((ch["offset"]/1e7,(ch["offset"]+ch["duration"])/1e7,ch["text"]))
    a=max(w[0][0]-0.05,0); b=w[-1][1]+0.08
    subprocess.run(["ffmpeg","-y","-v","error","-i",f"s{i}.mp3","-ss",str(a),"-to",str(b),"-ar","48000","-ac","1",f"t{i}.wav"],check=True)
    return [(x-a,y-a,tx) for x,y,tx in w], ffdur(f"t{i}.wav")

async def main():
    global ENGINE
    lines=[l.strip() for l in open(sys.argv[1]) if l.strip()]
    words=[];sents=[];t0=0.0;files=[]
    for i,l in enumerate(lines):
        if ENGINE=="kokoro":
            try: w,d=one_kokoro(i,l)
            except Exception as e:
                print("kokoro failed, falling back to edge:",e); ENGINE="edge"; w,d=await one_edge(i,l)
        else: w,d=await one_edge(i,l)
        for x,y,t in w: words.append((t0+x,t0+y,t,i))
        sents.append((t0,t0+d,l)); files.append(f"t{i}.wav"); t0+=d+GAP
    subprocess.run(["ffmpeg","-y","-v","error","-f","lavfi","-i","anullsrc=r=48000:cl=mono","-t",str(GAP),"gap.wav"],check=True)
    open("alist.txt","w").write("".join(f"file '{f}'\nfile 'gap.wav'\n" for f in files))
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i","alist.txt","-c:a","pcm_s16le","voice.wav"],check=True)
    json.dump({"words":words,"sents":sents,"engine":ENGINE},open("timing.json","w"))
    print("total",t0,"engine",ENGINE)
asyncio.run(main())
