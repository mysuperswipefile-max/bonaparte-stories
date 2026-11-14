import asyncio,edge_tts,json,subprocess
import os
VOICE=os.environ.get("VOICE","en-US-ChristopherNeural"); RATE=os.environ.get("RATE","+4%"); GAP=0.18
async def one(i,t):
    c=edge_tts.Communicate(t,VOICE,rate=RATE,boundary="WordBoundary"); w=[]
    with open(f"s{i}.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary": w.append((ch["offset"]/1e7,(ch["offset"]+ch["duration"])/1e7,ch["text"]))
    return w
async def main():
    lines=[l.strip() for l in open(__import__("sys").argv[1]) if l.strip()]
    words=[];sents=[];t0=0.0;files=[]
    for i,l in enumerate(lines):
        w=await one(i,l)
        # trim leading/trailing silence: cut audio to [first-0.05, last+0.08]
        a=max(w[0][0]-0.05,0); b=w[-1][1]+0.08
        subprocess.run(["ffmpeg","-y","-v","error","-i",f"s{i}.mp3","-ss",str(a),"-to",str(b),"-ar","48000","-ac","1",f"t{i}.wav"],check=True)
        d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"t{i}.wav"]))
        for x,y,t in w: words.append((t0+x-a,t0+y-a,t,i))
        sents.append((t0,t0+d,l)); files.append(f"t{i}.wav"); t0+=d+GAP
    open("gap.txt","w")
    subprocess.run(["ffmpeg","-y","-v","error","-f","lavfi","-i",f"anullsrc=r=48000:cl=mono","-t",str(GAP),"gap.wav"],check=True)
    lst="".join(f"file '{f}'\nfile 'gap.wav'\n" for f in files)
    open("alist.txt","w").write(lst)
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i","alist.txt","-c:a","pcm_s16le","voice.wav"],check=True)
    json.dump({"words":words,"sents":sents},open("timing.json","w"))
    print("total",t0)
asyncio.run(main())
