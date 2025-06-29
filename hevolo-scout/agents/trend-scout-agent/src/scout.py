import json
import os
import time
from datetime import datetime
import requests

TIKAPI_KEY = os.getenv("TIKAPI_KEY")
HEADERS = {"X-API-KEY": TIKAPI_KEY}

KEYWORDS_PRODUKTINTENTION = [
    "buy", "link in bio", "amazon", "find it", "where to buy", "tiktokmademebuyit",
    "must have", "product", "as seen", "problem", "solution", "organizer"
]

BLACKLIST_KEYWORDS = [
    "funny", "prank", "fail", "dance", "meme", "edit", "filter", "trend", "capcut",
    "fortnite", "minecraft", "baby", "relationship", "song", "music", "cat", "dog", "ai"
]

HOUSEHOLD_KEYWORDS = [
    "kitchen", "home", "clean", "organize", "dish", "fridge", "sink", "pan", "drawer",
    "storage", "closet", "laundry", "household", "gadget", "tool", "bathroom", "cook"
]

def fetch_videos():
    url = "https://api.tikapi.io/public/explore"
    params = {"country": "us", "count": 30}
    res = requests.get(url, headers=HEADERS, params=params)
    print(f"Status: {res.status_code} / URL: {res.url}")
    res.raise_for_status()
    data = res.json()
    return data.get("itemList", [])

def is_valid_video(v):
    desc = v.get("desc", "").lower()
    stats = v.get("stats", {})
    shares = stats.get("shareCount", 0)
    comments = stats.get("commentCount", 0)
    likes = stats.get("diggCount", 0)

    print(f"🔎 {shares} Shares / {comments} Comments / {likes} Likes | {desc[:80]}")
    if any(bad in desc for bad in BLACKLIST_KEYWORDS):
        print("🚫 Blacklist-Treffer – übersprungen.")
        return False
    if not any(kw in desc for kw in KEYWORDS_PRODUKTINTENTION):
        print("🚫 Keine Kauf-Intention – übersprungen.")
        return False
    if not any(hw in desc for hw in HOUSEHOLD_KEYWORDS):
        print("🚫 Keine Haushaltsnische – übersprungen.")
        return False
    if shares < 500 or comments < 200:
        print("🚫 Zu wenig Engagement – übersprungen.")
        return False
    return True

def load_existing(path):
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ JSON defekt – beginne neu.")
    return []

def save_output(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def run():
    print("🟡 Agent gestartet …")
    output_dir = os.path.join("hevolo-scout", "data")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "vorschlaege.json")

    existing = load_existing(path)
    valid = []

    for runde in range(1, 16):
        raw = fetch_videos()
        print(f"📥 Runde {runde}: {len(raw)} Videos geladen")

        for v in raw:
            if is_valid_video(v):
                eintrag = {
                    "titel": v.get("desc", "")[:80],
                    "tiktok_link": f"https://www.tiktok.com/@{v.get('author', {}).get('uniqueId', '')}/video/{v.get('id', '')}",
                    "shares": v.get("stats", {}).get("shareCount", 0),
                    "kommentare_total": v.get("stats", {}).get("commentCount", 0),
                    "likes": v.get("stats", {}).get("diggCount", 0),
                    "video_beschreibung": v.get("desc", ""),
                    "video_datum": v.get("createTime", ""),
                    "nische": "Küche, Haushalt & Wohnen",
                    "status": "VORSCHLAG",
                    "erstellt_am": datetime.today().strftime("%Y-%m-%d")
                }
                valid.append(eintrag)
                if len(valid) >= 10:
                    break
        if len(valid) >= 10:
            break
        time.sleep(2)

    print(f"🧮 Gefundene Vorschläge: {len(valid)}")
    save_output(path, existing + valid)
    print(f"✅ Vorschläge gespeichert in {path}: {len(existing + valid)} gesamt")
    if len(valid) < 10:
        print("🔁 Zu wenig gültige Vorschläge – Trigger für Neustart.")
        exit(99)

if __name__ == "__main__":
    run()
