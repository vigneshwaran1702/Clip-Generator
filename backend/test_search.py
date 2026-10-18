import urllib.request
import json
import urllib.parse

def test_search(subject):
    query = subject
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&prop=imageinfo&iiprop=url|mime|size&format=json&gsrlimit=10"
    req = urllib.request.Request(url, headers={"User-Agent": "VideoGenerator/1.0 (contact@example.com)"})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
        pages = data.get("query", {}).get("pages", {})
        valid = []
        for pid, p in pages.items():
            if "imageinfo" in p and p["imageinfo"]:
                info = p["imageinfo"][0]
                u = info.get("url", "")
                if u.lower().endswith((".jpg", ".jpeg", ".png")) and not any(bad in u.lower() for bad in ["map", "diagram", "icon", "logo", "flag", "plan", "svg"]):
                    valid.append((p.get("title"), u))
        print(f"Subject '{subject}': found {len(valid)} quality images")
        if valid:
            print("  -> Sample:", valid[0][0])

for s in ["Giza pyramid desert", "Formula 1 race car track", "Samurai sword katana forge", "Black hole space accretion"]:
    test_search(s)
