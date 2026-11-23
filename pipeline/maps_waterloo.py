"""Maps for the Waterloo series. Run from repo root: python pipeline/maps_waterloo.py
Needs Natural Earth geojson in geo/ (see pipeline/maps.py)."""
import os
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"maps.py")).read().split("# ---- Map 1")[0]
exec(src)
SERIF="DejaVu Serif"
from matplotlib.patches import Rectangle
PR="#1f1f1f"; AL=AU   # Prussians dark, Wellington red, French blue
os.makedirs("assets/maps",exist_ok=True)
def save(fig,n): fig.savefig(f"assets/maps/{n}.png",facecolor=SEA); print(n)
def badge(ax,x,y,t,c,s=12): ax.text(x,y,t,fontsize=s,family=SANS,weight="black",color="white",ha="center",va="center",zorder=10,bbox=dict(boxstyle="round,pad=0.4",fc=c,ec="none"))
# ---- Europe 1815: escape from Elba
ext=(-6,24,36,57); fig,ax=base(ext,LAND50,RIV50,LAK50)
region(ax,1.0,46.0,"FRANCE",30,FR,0.75)
region(ax,-1.5,53.0,"BRITAIN",17,AL,0.7); region(ax,13.5,52.4,"PRUSSIA",17,AL,0.7)
region(ax,16.5,47.6,"AUSTRIA",17,AL,0.7); region(ax,22.0,54.8,"RUSSIA",15,AL,0.7)
city(ax,2.35,48.86,"Paris",big=True); city(ax,10.3,42.78,"ELBA",dx=0.35,dy=-0.5,size=15,big=True,color=FR)
city(ax,7.08,43.55,"Golfe-Juan",dx=-0.25,ha="right",size=12)
arrow(ax,[(10.2,42.7),(7.3,43.4)],FR,lw=5,rad=-0.2)
arrow(ax,[(7.0,43.8),(5.75,45.1),(4.0,47.2),(2.6,48.6)],FR,lw=5,label="1 MARCH - 20 MARCH",lpos=(7.6,46.2),lsize=12)
title(ax,ext,"1815 · THE RETURN")
save(fig,"w1_elba")
# coalition arrows on top
arrow(ax,[(13.0,51.6),(7.0,50.4)],AL,lw=7); arrow(ax,[(16.0,48.0),(8.5,48.3)],AL,lw=7)
arrow(ax,[(23.0,53.8),(15.0,52.8)],AL,lw=6); arrow(ax,[(-0.5,52.0),(3.6,50.9)],AL,lw=6)
badge(ax,5.0,41.3,"1 vs ALL\nOF EUROPE",AL,17)
save(fig,"w2_coalition"); plt.close(fig)
# ---- Belgium, 15-18 June
ext=(3.7,5.4,50.15,51.0); fig,ax=base(ext,LAND10,RIV10,LAK10)
for x,y,n,dx in [(4.35,50.85,"BRUSSELS",0.03),(4.44,50.41,"Charleroi",0.03),(4.60,50.80,"Wavre",0.03)]:
    city(ax,x,y,n,dx=dx,size=15,big=n=="BRUSSELS")
city(ax,4.399,50.716,"Waterloo",dx=-0.03,ha="right",size=15,big=True,color=AL)
city(ax,4.46,50.57,"Quatre Bras",dx=-0.03,ha="right",size=14)
city(ax,4.58,50.53,"Ligny",dx=0.03,dy=-0.02,size=14)
region(ax,4.0,50.22,"FRANCE",22,FR,0.6)
arrow(ax,[(4.40,50.22),(4.44,50.40)],FR,lw=8,label="15 JUNE",lpos=(4.62,50.28),lsize=12)
badge(ax,4.22,50.62,"WELLINGTON",AL); badge(ax,4.88,50.58,"BLÜCHER",PR)
title(ax,ext,"BELGIUM · JUNE 1815")
save(fig,"w3_belgium")
arrow(ax,[(4.60,50.56),(4.60,50.78)],PR,lw=6,label="PRUSSIANS → WAVRE",lpos=(4.97,50.70),lsize=11)
arrow(ax,[(4.62,50.52),(4.66,50.70)],FR,lw=4,rad=0.1,label="GROUCHY 33,000",lpos=(5.02,50.47),lsize=11)
arrow(ax,[(4.46,50.59),(4.41,50.70)],AL,lw=5)
save(fig,"w4_grouchy"); plt.close(fig)
# ---- Battlefield schematic (real coordinates)
ext=(4.365,4.475,50.637,50.715); fig,ax=plt.subplots(figsize=(8,11.333),dpi=300); fig.subplots_adjust(0,0,1,1)
ax.add_patch(Rectangle((4.2,50.5),0.5,0.4,fc=LAND,ec="none",zorder=0)); ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect(1/np.cos(np.radians(50.67)),adjustable="datalim"); ax.axis("off")
rng=np.random.default_rng(1); ax.imshow(rng.normal(0,1,(900,640)),extent=ext,cmap="gray",alpha=0.07,zorder=3,aspect="auto")
ax.plot([4.405,4.4125,4.415,4.414],[50.705,50.68,50.672,50.64],color="#8a7653",lw=3,zorder=2)   # Brussels-Charleroi road
ax.plot([4.37,4.44],[50.683,50.683],color="#7a6a4a",lw=10,alpha=0.35,zorder=2,solid_capstyle="round") # ridge
ax.text(4.375,50.6865,"THE RIDGE",fontsize=12,family=SANS,weight="black",color="#5a4a30",zorder=4)
P={"Hougoumont":(4.393,50.670),"La Haye Sainte":(4.412,50.679),"Papelotte":(4.433,50.676),"Plancenoit":(4.434,50.662),
   "La Belle Alliance":(4.415,50.672),"Mont-St-Jean":(4.410,50.690),"Le Caillou":(4.4136,50.6545)}
for n,(x,y) in P.items():
    ha="right" if n in("Hougoumont","La Belle Alliance","Le Caillou") else "left"
    city(ax,x,y,n,dx=-0.003 if ha=="right" else 0.003,ha=ha,size=13)
ax.plot([4.385,4.44],[50.685,50.685],color=AL,lw=9,zorder=5,solid_capstyle="round"); badge(ax,4.39,50.700,"WELLINGTON 68,000",AL)
ax.plot([4.39,4.44],[50.667,50.667],color=FR,lw=9,zorder=5,solid_capstyle="round"); badge(ax,4.40,50.649,"NAPOLEON 72,000",FR)
title(ax,ext,"WATERLOO · 18 JUNE 1815")
save(fig,"w5_field")
arrow(ax,[(4.474,50.70),(4.455,50.675),(4.440,50.664)],PR,lw=8,label="PRUSSIANS",lpos=(4.455,50.705),lsize=12)
save(fig,"w6_prussians")
arrow(ax,[(4.405,50.672),(4.405,50.683)],FR,lw=9,label="IMPERIAL GUARD 19:30",lpos=(4.385,50.6765),lsize=11)
save(fig,"w7_guard"); plt.close(fig)
