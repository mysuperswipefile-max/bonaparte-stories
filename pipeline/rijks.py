import json,urllib.request,urllib.parse,re,sys,time
UA={"User-Agent":"Mozilla/5.0","Accept":"application/ld+json"}
def g(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
def obj(oid):
    o=g(oid); t=json.dumps(o)
    iiif=re.findall(r'https://iiif\.micr\.io/[A-Za-z0-9]+',t)
    names=[n.get("content") for n in o.get("identified_by",[]) if n.get("type")=="Name"]
    return (names[0] if names else "?"), (iiif[0] if iiif else None)
def search(**kw):
    kw.setdefault("imageAvailable","true")
    s=g("https://data.rijksmuseum.nl/search/collection?"+urllib.parse.urlencode(kw))
    return [i["id"] for i in s.get("orderedItems",[])]
if __name__=="__main__":
    for q in sys.argv[1:]:
        print("##",q)
        for oid in search(title=q)[:10]:
            try: n,u=obj(oid); print("  ",oid.split("/")[-1],"|",(n or "")[:90],"|",u)
            except Exception as e: print("  err",e)
