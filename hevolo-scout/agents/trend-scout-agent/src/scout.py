import json
import os
from datetime import datetime
import requests
import time
import sys

TIKAPI_KEY = os.getenv("TIKAPI_KEY")
HEADERS = {"X-API-KEY": TIKAPI_KEY}
BASE_URL = "https://api.tikapi.io"
MIN_VORSCHLAEGE = 5
MAX_RUNDEN = 15
KEYWORDS = ["hack", "must have", "life changing", "problem", "fix", "clean", "organize", "storage", "solution"]
BLACKLIST = ["diy", "pet", "funny", "joke", "prank", "meme", "baby", "dance", "lip sync", "tutorial", "music"]

def fetch_videos():
    url = f"{BASE_URL}/public/hashtag"
    params = {"name": "tiktokmademebuyit", "count": 30}
    res = requests.get(url, headers=HEADERS, params=params)
    print(f"Status: {res.status_code} / URL: {res.url}")
    res.raise_for_status()
    return res.json().get("itemList", [])

def is_relevant(desc):
    if not desc:
        return False
    desc = desc.lower()
    return not any(b in desc for b in BLACKLIST) and any(k in desc for k in KEYWORDS)

def save_output(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_existing(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        print("⚠️ JSON defekt – starte neu.")
        return []

def run():
    print("🟡 Agent gestartet …")
    all_results = []
    runde = 0

    while len(all_results) < MIN_VORSCHLAEGE and runde < MAX_RUNDEN:
        runde += 1
        raw = fetch_videos()
        print(f"📥 Runde {runde}: {len(raw)} Videos geladen")

        for v in raw:
            desc = v.get("desc", "")
            stats = v.get("stats", {})
            if not is_relevant(desc):
                print(f"🚫 Kein Produktvideo laut Filter.")
                continue

            eintrag = {
                "titel": desc[:80],
                "tiktok_link": f"https://www.tiktok.com/@{v.get('author', {}).get('uniqueId', '')}/video/{v.get('id', '')}",
                "shares": stats.get("shares", 0),
                "kommentare_total": stats.get("comments", 0),
                "kommentare_aktuell": stats.get("comments", 0),
                "likes": stats.get("diggs", 0),
                "video_beschreibung": desc,
                "video_datum": v.get("createTime", ""),
                "problemloeser": any(k in desc.lower() for k in KEYWORDS),
                "nische": "Haushalt",
                "status": "VORSCHLAG",
                "erstellt_am": datetime.today().strftime("%Y-%m-%d")
            }
            all_results.append(eintrag)
            if len(all_results) >= MIN_VORSCHLAEGE:
                break
        time.sleep(1)

    print(f"🧮 Gültige Vorschläge: {len(all_results)}")

    path = os.path.join("hevolo-scout", "data", "vorschlaege.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    existing = load_existing(path)
    save_output(path, existing + all_results)
    print(f"✅ Vorschläge gespeichert in {path}: {len(existing + all_results)} gesamt")

    if len(all_results) < MIN_VORSCHLAEGE:
        print("🔁 Nicht genügend Vorschläge – Neustart empfohlen.")
        sys.exit(99)

if __name__ == "__main__":
    run()
