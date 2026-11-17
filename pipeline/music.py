import numpy as np, scipy.signal as sg, scipy.io.wavfile as wf, sys
SR=48000; DUR=float(sys.argv[1]); SEED=int(sys.argv[2]) if len(sys.argv)>2 else 7
BPM=[96,104,112,120,128,136][SEED%6]; TR=[0,-2,3,-5,5,-3][(SEED//6)%6]; beat=60/BPM; s16=beat/4
N=int(SR*DUR); out=np.zeros((N,2))
rng=np.random.default_rng(SEED)
def add(sig,t,pan=0.0,g=1.0):
    i=int(t*SR); 
    if i>=N: return
    s=sig[:N-i]*g; out[i:i+len(s),0]+=s*(1-pan)/1; out[i:i+len(s),1]+=s*(1+pan)/1
def kick():
    t=np.arange(int(0.5*SR))/SR; f=45+110*np.exp(-t*28)
    ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.exp(-t*7)
def taiko():
    t=np.arange(int(0.7*SR))/SR; f=70+60*np.exp(-t*20)
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*5)
    n=sg.lfilter(*sg.butter(2,[150,900],btype='band',fs=SR),rng.standard_normal(len(t)))*np.exp(-t*25)*0.6
    return body+n
def snare():
    t=np.arange(int(0.25*SR))/SR
    n=sg.lfilter(*sg.butter(2,[1200,6000],btype='band',fs=SR),rng.standard_normal(len(t)))
    return (n*np.exp(-t*22)+0.4*np.sin(2*np.pi*190*t)*np.exp(-t*30))
def hat():
    t=np.arange(int(0.05*SR))/SR
    return sg.lfilter(*sg.butter(2,7000,btype='high',fs=SR),rng.standard_normal(len(t)))*np.exp(-t*80)
def saw(freq,dur,cut=1800):
    t=np.arange(int(dur*SR))/SR
    x=sum(np.sin(2*np.pi*freq*k*t)/k for k in range(1,14) if freq*k<12000)
    x+=0.5*sum(np.sin(2*np.pi*freq*1.004*k*t)/k for k in range(1,10) if freq*k<12000)
    x=sg.lfilter(*sg.butter(2,cut,fs=SR),x)
    env=np.minimum(1,t/0.005)*np.exp(-t*6); return x*env
def pad(freq,dur):
    t=np.arange(int(dur*SR))/SR
    x=sum(np.sin(2*np.pi*f*t) for f in (freq,freq*1.5,freq*2,freq*1.003))
    env=np.minimum(1,t/0.4)*np.minimum(1,(dur-t)/0.4); return x*env
nt=lambda m:440*2**((m-69)/12)
# progression per bar (4 beats): Dm, Bb, F, A  -> roots midi
PROGS=[[(50,[50,53,57]),(46,[46,50,53]),(41,[45,48,53]),(45,[45,49,52])],
 [(45,[45,48,52]),(41,[41,45,48]),(43,[43,47,50]),(40,[40,44,47])],
 [(50,[50,53,57]),(48,[48,52,55]),(46,[46,50,53]),(45,[45,49,52])],
 [(52,[52,55,59]),(48,[48,52,55]),(43,[43,47,50]),(47,[47,51,54])]]
prog=[(r+TR,[c+TR for c in ch]) for r,ch in PROGS[SEED%4]]
ARPS=[[0,0,1,0,2,0,1,0,0,0,1,0,2,1,0,2],[0,1,2,1,0,1,2,1,0,1,2,1,0,2,1,2],[0,2,1,2,0,2,1,2,0,2,1,2,0,1,2,0],[0,0,0,1,2,2,1,0,0,0,0,1,2,1,2,1]]
arp=ARPS[(SEED//4)%4]
bar=4*beat; nb=int(DUR/bar)+1
K,T,S,H=kick(),taiko(),snare(),hat()
for b in range(nb):
    t0=b*bar; root,ch=prog[b%4]; lvl=0.55 if b<2 else 1.0
    if t0>DUR-1.2: break
    for i in range(16):
        tt=t0+i*s16
        if tt>DUR-1.5: break
        n=nt(ch[arp[i]]+12)
        add(saw(n,s16*1.6,1500 if b<2 else 2600),tt,pan=(0.3 if i%2 else -0.3),g=0.11*lvl)
        if b>=2 and i%2==1: add(H,tt,pan=0.4,g=0.06)
        if b>=2 and i in (0,3,6,8,10,14): add(K,tt,g=0.9 if i in (0,8) else 0.55)
        if b>=4 and i in (4,12): add(S,tt,g=0.35)
        if b>=4 and i in (0,7) and b%2==0: add(T,tt,pan=-0.2,g=0.5)
    add(saw(nt(root-12),bar,500)*0+pad(nt(root-12),bar)*0.0,t0)
    tb=np.arange(int(bar*SR))/SR
    bass=sum(np.sin(2*np.pi*nt(root-12)*k*tb)/k for k in (1,2,3))*np.minimum(1,tb/0.01)*np.minimum(1,(bar-tb)/0.05)
    add(bass*(0.5 if b>=2 else 0.3),t0,g=0.25)
    add(pad(nt(root),bar)*0.05*lvl,t0)
# final hit
add(T,DUR-1.2,g=1.0); add(K,DUR-1.2,g=1.0)
out=np.tanh(out*1.3); out/=np.max(np.abs(out))*1.12
fade=int(1.0*SR); out[-fade:]*=np.linspace(1,0,fade)[:,None]
wf.write("music.wav",SR,(out*32767).astype(np.int16))
print("ok")
