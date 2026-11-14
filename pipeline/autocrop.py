import sys,numpy as np
from PIL import Image,ImageOps
def crop(src,dst,tint=True):
    im=Image.open(src).convert("RGB"); a=np.asarray(im.convert("L")).astype(float)
    # content = rows/cols where enough dark pixels (paper is bright & uniform)
    dark=(a<150).astype(float)
    def span(v,th):
        idx=np.where(v>th)[0]; return (idx[0],idx[-1]) if len(idx) else (0,len(v)-1)
    r=dark.mean(1); c=dark.mean(0)
    y0,y1=span(r,0.08); x0,x1=span(c,0.08)
    pad=int(0.012*max(im.size)); box=(x0+pad,y0+pad,x1-pad,y1-pad)
    if box[2]-box[0]<0.3*im.width or box[3]-box[1]<0.3*im.height: box=(0,0,im.width,im.height)
    im=im.crop(box)
    if tint:
        g=ImageOps.grayscale(im); im=ImageOps.colorize(ImageOps.autocontrast(g,cutoff=1),black=(28,20,14),white=(236,222,196),mid=(140,112,82))
    im.save(dst,quality=95); return im.size
if __name__=="__main__":
    for s in sys.argv[1:]:
        n=s.split("/")[-1]; print(n,crop(s,"../vis/"+n,tint=True))
