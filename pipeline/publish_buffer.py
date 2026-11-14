"""Publish a rendered video to TikTok and YouTube through the Buffer API.

Needs env BUFFER_API_KEY. The video must be at a public https URL
(GitHub Pages: https://<owner>.github.io/bonaparte-stories/videos/<file>.mp4).

Usage:
  python pipeline/publish_buffer.py schema            # print createPost input + channel fields (introspection)
  python pipeline/publish_buffer.py channels          # list connected channels (id, service, name)
  python pipeline/publish_buffer.py post <video_url> <caption_file> [--title "YouTube title"]
"""
import json, os, sys, urllib.request

API = "https://api.buffer.com"

def gql(query, variables=None):
    key = os.environ.get("BUFFER_API_KEY")
    if not key: raise SystemExit("BUFFER_API_KEY is not set")
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    out = json.load(urllib.request.urlopen(req, timeout=60))
    if out.get("errors"): raise SystemExit("Buffer error: " + json.dumps(out["errors"])[:2000])
    return out["data"]

def type_fields(name):
    q = '{ __type(name: "%s") { name kind inputFields { name type { name kind ofType { name kind ofType { name kind } } } } fields { name args { name type { name kind ofType { name } } } type { name kind ofType { name kind } } } enumValues { name } } }' % name
    return gql(q)["__type"]

def schema():
    for t in ["Query", "CreatePostInput", "AssetsInput", "VideoAssetInput", "PostInputMetaData", "SchedulingType", "ShareMode", "Channel"]:
        try: print(json.dumps(type_fields(t), indent=1)[:4000])
        except SystemExit as e: print(t, e)

def channels():
    orgs = gql("{ account { organizations { id name } } }")["account"]["organizations"]
    res = []
    for o in orgs:
        ch = gql('query($id: OrganizationId!){ channels(input: {organizationId: $id}) { id service name } }', {"id": o["id"]})["channels"]
        res += ch
    print(json.dumps(res, indent=1)); return res

def post(video_url, caption, title=None):
    chans = [c for c in channels() if c["service"].lower() in ("tiktok", "youtube")]
    if not chans: raise SystemExit("No TikTok/YouTube channel connected in Buffer")
    results = []
    for c in chans:
        meta = ""
        if c["service"].lower() == "youtube" and title:
            meta = ', metadata: { youtube: { title: %s, categoryId: "27" } }' % json.dumps(title[:100])
        m = ('mutation { createPost(input: { text: %s, channelId: "%s", schedulingType: automatic, mode: addToQueue%s, '
             'assets: [ { video: { url: "%s", metadata: { thumbnailOffset: 1500 } } } ] }) '
             '{ ... on PostActionSuccess { post { id } } ... on MutationError { message } } }') % (json.dumps(caption), c["id"], meta, video_url)
        r = gql(m)["createPost"]
        results.append({"service": c["service"], **r})
    print(json.dumps(results, indent=1))
    if any("message" in r for r in results): raise SystemExit("at least one post failed")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "schema": schema()
    elif cmd == "channels": channels()
    elif cmd == "post":
        title = sys.argv[sys.argv.index("--title") + 1] if "--title" in sys.argv else None
        post(sys.argv[2], open(sys.argv[3]).read().strip(), title)
