import json,subprocess,os,math,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
W,H,FPS,XF=1080,1920,30,0.45
LAND=False
def set_landscape():
    """Switch the builder to 16:9 1920x1080 for long-form YouTube videos."""
    global W,H,LAND
    W,H,LAND=1920,1080,True
def run(c): subprocess.run(c,check=True)
def title_png(path,part,color,title="WHEN NAPOLEON ALMOST LOST",badge=None):
    """Small series label at the top of the frame, so the image stays fully visible."""
    im=Image.new("RGBA",(W,H),(0,0,0,0))
    fb="/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
    f1=ImageFont.truetype(fb,52); f2=ImageFont.truetype(fb,46)
    d=ImageDraw.Draw(im)
    t=badge or f"PART {part}"; tw=d.textlength(t,font=f2); pw,ph=tw+56,76
    lw=d.textlength(title,font=f1)
    total=pw+24+lw; x0=(W-total)/2; y=(70 if LAND else 170)
    if total>W-80:  # long title: badge on its own line
        x0=(W-pw)/2; lx=(W-lw)/2; ly=y+ph+18
    else:
        lx=x0+pw+24; ly=y+(ph-62)/2
    band=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(band).rectangle((0,y-40,W,max(ly+62,y+ph)+40),fill=(0,0,0,120))
    im=Image.alpha_composite(im,band.filter(ImageFilter.GaussianBlur(18))); d=ImageDraw.Draw(im)
    d.rounded_rectangle((x0,y,x0+pw,y+ph),radius=ph/2,fill=color)
    d.text((x0+pw/2,y+ph/2+2),t,font=f2,fill="white",anchor="mm")
    d.text((lx+2,ly+3),title,font=f1,fill=(0,0,0,200)); d.text((lx,ly),title,font=f1,fill="white")
    im.save(path)
def build(part,color,plan,out,T0=3.4,TT=3.6,title="WHEN NAPOLEON ALMOST LOST",badge=None,music_vol=0.30,allow_repeat=False):
    tm=json.load(open("timing.json")); words=tm["words"]; sents=tm["sents"]; END=sents[-1][1]+0.7
    assert len(plan)==len(sents),(len(plan),len(sents))
    shots=[]; used=set()
    for (s0,s1,_),p in zip(sents,plan):
        s1+=0.18; n=max(len(p),1)
        for k,sh in enumerate(p):
            if isinstance(sh,str): sh=(sh,)
            assert allow_repeat or sh[0] not in used, "REUSED "+sh[0]; used.add(sh[0])
            im=Image.open(sh[0]); asp=im.width/im.height
            if (not LAND and asp>0.8) or (LAND and asp<1.3):
                os.makedirs("comp",exist_ok=True); cp="comp/"+os.path.basename(sh[0]); compose(sh[0],cp)
                zin=(k%2==0)
                sh=(cp,0.5,0.40,0.5,0.40,1.0 if zin else 1.12,1.12 if zin else 1.0)
            elif len(sh)==1:
                sh=(sh[0],0.5,0.25,0.5,0.2,1.0,1.15)
            shots.append((s0+(s1-s0)*k/n,)+tuple(sh))
    shots[0]=(0.0,)+shots[0][1:]
    os.makedirs("seg",exist_ok=True); segs=[]
    for i,(s,img,fx0,fy0,fx1,fy1,z0,z1) in enumerate(shots):
        e=shots[i+1][0] if i+1<len(shots) else END
        dur=e-s+(XF if i+1<len(shots) else 0)
        n=int(round(dur*FPS)); D=max(n-1,1)
        ease=f"(0.5-0.5*cos(PI*on/{D}))"
        vf=(f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
            f"zoompan=z='{z0}+({z1}-{z0})*{ease}':x='(iw-iw/zoom)*({fx0}+({fx1}-{fx0})*{ease})':"
            f"y='(ih-ih/zoom)*({fy0}+({fy1}-{fy0})*{ease})':d={n}:s={W}x{H}:fps={FPS},"
            f"eq=contrast=1.1:saturation=0.95:brightness=-0.03,vignette=PI/4.2,format=yuv420p,setsar=1")
        o=f"seg/{i:02d}.mp4"; segs.append((o,dur))
        run(["ffmpeg","-y","-v","error","-loop","1","-i",img,"-vf",vf,"-frames:v",str(n),"-c:v","libx264","-preset","veryfast","-crf","18",o])
    # xfade chain
    inp=[];fc=[];prev="[0:v]";acc=segs[0][1]
    for o,_ in segs: inp+=["-i",o]
    for i in range(1,len(segs)):
        off=acc-XF; lab=f"[x{i}]"
        fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}{lab}"); prev=lab; acc=off+segs[i][1]
    run(["ffmpeg","-y","-v","error"]+inp+["-filter_complex",";".join(fc),"-map",prev,"-c:v","libx264","-preset","veryfast","-crf","18","video_raw.mp4"])
    # captions
    script=" ".join(l for _,_,l in sents); pos=0; chunks=[]; cur=[]
    for a,b,t,si in words:
        j=script.find(t,pos); end=j+len(t) if j>=0 else pos
        if j>=0: pos=end
        brk=script[end:end+1] in ".,:!?"
        cur.append([a,b,t])
        if brk or len(cur)==3 or len(" ".join(x[2] for x in cur))>14: chunks.append(cur); cur=[]
    if cur: chunks.append(cur)
    def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
    ass=["[Script Info]",f"PlayResX: {W}",f"PlayResY: {H}","","[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    f"Style: S,Inter Display Black,{64 if LAND else 92},&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,1,0,1,5,5,2,70,70,{80 if LAND else 560},1","","[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for k,c in enumerate(chunks):
        if c[-1][1]<T0: continue
        cend=min(chunks[k+1][0][0] if k+1<len(chunks) else c[-1][1]+0.5, c[-1][1]+0.35)
        for wi,w in enumerate(c):
            st=max(w[0],T0); en=c[wi+1][0] if wi+1<len(c) else cend
            if en<=st: continue
            pop="{\\fscx92\\fscy92\\t(0,90,\\fscx100\\fscy100)}" if wi==0 else ""
            txt=" ".join(("{\\alpha&H00&}" if xi==wi else "{\\alpha&H70&}")+x[2].upper() for xi,x in enumerate(c))
            ass.append(f"Dialogue: 0,{ts(st)},{ts(en)},S,,0,0,0,,{pop}{txt}")
    open("subs.ass","w").write("\n".join(ass)+"\n")
    title_png("title.png",part,color,title,badge)
    run(["ffmpeg","-y","-v","error","-i","video_raw.mp4","-loop","1","-t",f"{TT}","-i","title.png","-i","voice.wav","-i","music.wav",
     "-filter_complex",
     f"[1:v]format=rgba,fade=t=in:st=0:d=0.15:alpha=1,fade=t=out:st={TT-0.35}:d=0.35:alpha=1,setpts=PTS-STARTPTS[t];[0:v][t]overlay=0:0:eof_action=pass[ov];[ov]ass=subs.ass[v];"
     f"[2:a]aresample=48000,asplit=2[v1][v2];[3:a]volume={music_vol}[m];[m][v2]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=350[md];[v1][md]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]",
     "-map","[v]","-map","[a]","-t",f"{END:.2f}","-c:v","libx264","-preset","veryfast","-crf","19","-c:a","aac","-b:a","192k","-movflags","+faststart",out])
    print("OK",out,"shots",len(shots),"len",round(END,1),"maxshot",round(max(segs[i][1]-XF for i in range(len(segs)-1)),1))

def compose(src,dst):
    """Landscape/small image -> 2160x3840 canvas: blurred cover background + full image fitted."""
    from PIL import ImageEnhance
    CW,CH=W*2,H*2
    im=Image.open(src).convert("RGB")
    bg=im.copy(); s=max(CW/bg.width,CH/bg.height); bg=bg.resize((int(bg.width*s)+1,int(bg.height*s)+1))
    bg=bg.crop(((bg.width-CW)//2,(bg.height-CH)//2,(bg.width-CW)//2+CW,(bg.height-CH)//2+CH)).filter(ImageFilter.GaussianBlur(40))
    bg=ImageEnhance.Brightness(bg).enhance(0.45)
    cy=0.5 if LAND else 0.40
    if LAND:
        fh=int(CH*0.94); fw=int(im.width*fh/im.height)
        if fw>CW: fw=CW; fh=int(im.height*fw/im.width)
    else:
        fw=int(CW*1.0); fh=int(im.height*fw/im.width)
        if fh>CH*0.62: fh=int(CH*0.62); fw=int(im.width*fh/im.height)
    fg=im.resize((fw,fh),Image.LANCZOS)
    sh=Image.new("RGBA",(CW,CH),(0,0,0,0)); ImageDraw.Draw(sh).rectangle(((CW-fw)//2,int(CH*cy-fh/2)+20,(CW+fw)//2,int(CH*cy+fh/2)+20),fill=(0,0,0,200))
    bg=Image.alpha_composite(bg.convert("RGBA"),sh.filter(ImageFilter.GaussianBlur(30))).convert("RGB")
    bg.paste(fg,((CW-fw)//2,int(CH*cy-fh/2)))
    bg.save(dst,quality=93)
