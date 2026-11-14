import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon as MPoly
from shapely.geometry import shape, box
from matplotlib import font_manager as fm
SERIF="Bitstream Charter"; SANS="Inter Display"
G=__import__("os").environ.get("GEO_DIR","geo/")
def load(f): return [shape(ft["geometry"]) for ft in json.load(open(G+f))["features"]]
LAND10=load("ne_10m_land.geojson"); RIV10=load("ne_10m_rivers_lake_centerlines.geojson"); LAK10=load("ne_10m_lakes.geojson")
LAND50=load("ne_50m_land.geojson"); RIV50=load("ne_50m_rivers_lake_centerlines.geojson"); LAK50=load("ne_50m_lakes.geojson")
SEA="#151a21"; LAND="#cbb68d"; RIVER="#6f8aa3"; FR="#2b5fd9"; AU="#c8242c"; INK="#2a2118"
def polys(g):
    return [g] if g.geom_type=="Polygon" else list(getattr(g,"geoms",[]))
def base(ext, land, riv, lak, figsize=(8,11.333)):
    x0,x1,y0,y1=ext; bb=box(x0-1,y0-1,x1+1,y1+1)
    fig=plt.figure(figsize=figsize,dpi=300); ax=fig.add_axes([0,0,1,1]); ax.set_facecolor(SEA)
    lat=np.radians((y0+y1)/2)
    for g in land:
        g=g.intersection(bb)
        for p in polys(g):
            if p.is_empty or p.geom_type!="Polygon": continue
            ax.add_patch(MPoly(np.array(p.exterior.coords),fc=LAND,ec="#8a7653",lw=0.6,zorder=1))
    for g in lak:
        g=g.intersection(bb)
        for p in polys(g):
            if p.geom_type=="Polygon" and not p.is_empty: ax.add_patch(MPoly(np.array(p.exterior.coords),fc=RIVER,ec="none",zorder=2))
    for g in riv:
        g=g.intersection(bb)
        for l in ([g] if g.geom_type=="LineString" else list(getattr(g,"geoms",[]))):
            if l.geom_type=="LineString" and not l.is_empty:
                c=np.array(l.coords); ax.plot(c[:,0],c[:,1],color=RIVER,lw=0.9,zorder=2,solid_capstyle="round")
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect(1/np.cos(lat),adjustable="datalim"); ax.axis("off")
    # paper grain
    rng=np.random.default_rng(1); n=rng.normal(0,1,(900,640))
    ax.imshow(n,extent=(x0,x1,y0,y1),cmap="gray",alpha=0.07,zorder=3,aspect="auto")
    return fig,ax
def city(ax,x,y,name,dx=0.12,dy=0.0,size=14,ha="left",big=False,color=INK):
    ax.plot(x,y,"o",ms=7 if big else 5,mfc=color,mec="#f3e9d2",mew=1.2,zorder=6)
    ax.text(x+dx,y+dy,name,fontsize=size,family=SERIF,weight="bold",color=color,ha=ha,va="center",zorder=7)
def region(ax,x,y,name,size=26,color=INK,alpha=0.55,rot=0):
    ax.text(x,y,name,fontsize=size,family=SERIF,weight="bold",color=color,alpha=alpha,ha="center",va="center",zorder=4,rotation=rot,
            fontstretch="expanded")
def arrow(ax,pts,color,lw=7,label=None,lpos=None,lsize=13,rad=0.0):
    for (a,b) in zip(pts[:-1],pts[1:]):
        last=(b==pts[-1])
        ax.add_patch(FancyArrowPatch(a,b,connectionstyle=f"arc3,rad={rad}",arrowstyle="-|>,head_length=1.4,head_width=0.9" if last else "-",
            mutation_scale=18,lw=lw,color=color,zorder=8,capstyle="round"))
    if label: ax.text(*lpos,label,fontsize=lsize,family=SANS,weight="black",color="white",ha="center",va="center",zorder=9,
            bbox=dict(boxstyle="round,pad=0.45",fc=color,ec="none"))
def title(ax,ext,txt):
    x0,x1,y0,y1=ext
    ax.text((x0+x1)/2,y1-(y1-y0)*0.045,txt,fontsize=17,family=SANS,weight="black",color="#f3e9d2",ha="center",va="center",zorder=10,
            bbox=dict(boxstyle="round,pad=0.5",fc="#151a21",ec="none",alpha=0.85))
# ---- Map 1: Europe 1796
ext=(-6,22,36,56); fig,ax=base(ext,LAND50,RIV50,LAK50)
region(ax,2.5,46.6,"FRANCE",30,FR,0.75); region(ax,15.8,48.2,"AUSTRIAN\nEMPIRE",22,AU,0.75)
region(ax,-1,52.6,"BRITAIN",15,INK,0.45); region(ax,13.5,52.2,"PRUSSIA",15,INK,0.4)
city(ax,2.35,48.86,"Paris",big=True); city(ax,16.37,48.21,"Vienna",big=True,dx=0.25)
title(ax,ext,"EUROPE · 1796")
fig.savefig("maps/m1_europe.png",facecolor=SEA); 
# ---- Map 1b: plan of campaign
arrow(ax,[(5.8,48.6),(10.6,48.6)],FR,label="MAIN ARMIES",lpos=(8.1,50.9),lsize=14)
arrow(ax,[(6.4,50.8),(10.2,50.0)],FR,lw=6)
arrow(ax,[(7.0,44.0),(9.6,45.0)],FR,lw=3,label="ITALY: a sideshow",lpos=(8.6,42.9),lsize=13)
fig.savefig("maps/m2_plan.png",facecolor=SEA); plt.close(fig)
# ---- Map 3: Northern Italy campaign
ext=(6.4,12.6,43.3,46.9); fig,ax=base(ext,LAND10,RIV10,LAK10)
region(ax,7.6,46.0,"ALPS",22,INK,0.35); region(ax,8.6,43.85,"Ligurian Sea",13,"#9fb2c4",0.8)
region(ax,9.6,45.8,"LOMBARDY",15,INK,0.4); region(ax,7.65,44.75,"PIEDMONT",15,INK,0.4)
for x,y,n,dx in [(7.27,43.70,"Nice",0.08),(7.69,45.07,"Turin",0.08),(8.38,44.38,"Montenotte",-0.08),(8.93,44.41,"Genoa",0.08),
                 (9.19,45.46,"Milan",0.08),(9.50,45.31,"Lodi",0.08),(10.99,45.44,"Verona",0.08)]:
    city(ax,x,y,n,dx=dx,ha="right" if dx<0 else "left",size=15)
city(ax,10.79,45.16,"MANTUA",dx=0.1,size=15,big=True,color=AU)
ax.plot(10.79,45.16,"o",ms=40,mfc="none",mec=AU,mew=2.5,zorder=6)
arrow(ax,[(7.45,43.85),(8.35,44.3),(9.45,45.25),(10.6,45.17)],FR,lw=6)
title(ax,ext,"BONAPARTE'S CAMPAIGN · 1796")
fig.savefig("maps/m3_italy.png",facecolor=SEA); plt.close(fig)
# ---- Map 4: November 1796 converging armies
ext=(9.9,12.3,44.7,46.4); fig,ax=base(ext,LAND10,RIV10,LAK10)
for x,y,n,dx in [(10.99,45.44,"Verona",-0.06),(11.18,45.41,"Caldiero",0.05),(11.55,45.55,"Vicenza",0.05),(11.12,46.07,"Trento",0.05),(10.81,45.57,"Rivoli",-0.06),(11.73,45.77,"Bassano",0.05)]:
    city(ax,x,y,n,dx=dx,ha="right" if dx<0 else "left",size=13)
city(ax,10.79,45.16,"Mantua",dx=-0.06,ha="right",size=13)
city(ax,11.28,45.36,"ARCOLE",dx=0.06,size=16,big=True,color="#f3e9d2")
arrow(ax,[(11.95,45.62),(11.25,45.43)],AU,lw=8,label="ALVINCZY",lpos=(11.85,45.85))
arrow(ax,[(11.12,46.25),(10.88,45.7)],AU,lw=7,label="DAVIDOVICH",lpos=(11.4,46.25))
ax.plot(10.99,45.44,"o",ms=26,mfc=FR,mec="white",mew=2.5,zorder=9,alpha=0.92)
ax.text(10.99,45.30,"BONAPARTE",fontsize=12,family=SANS,weight="black",color="white",ha="center",zorder=10,bbox=dict(boxstyle="round,pad=0.4",fc=FR,ec="none"))
title(ax,ext,"NOVEMBER 1796")
fig.savefig("maps/m4_nov.png",facecolor=SEA); plt.close(fig)
print("maps ok")
