import json
import os
import requests
import time
from datetime import datetime

TIKAPI_KEY = os.getenv("X-API-KEY") or os.getenv("TIKAPI_KEY")
HEADERS = {"X-API-KEY": TIKAPI_KEY}

KEYWORDS = ["hack", "must have", "life changing", "problem", "fix", "clean", "organize"]
BLACKLIST = ["diy", "funny", "prank", "recipe", "life hack", "tutorial", "hack your", "dance", "workout", "routine", "joke"]
PRODUCT_CUES = ["buy", "shop now", "amazon", "order", "made me buy", "tiktok made me buy", "link in bio", "get yours", "unboxing", "review"]

MIN_VORSCHLAEGE = 5
PAGE_SIZE = 30
MAX_ITERATIONEN = 20

def fetch_videos():
    url = "https://api.tikapi.io/public/explore"
    params = {"country": "us", "count": PAGE_SIZE}
    res = requests.get(url, headers=HEADERS, params=params)
    print(f"Status: {res.status_code} / URL: {res.url}")
    res.raise_for_status()
    return res.json().get("itemList", [])

def is_problem_solver(desc):
    return any(kw in desc.lower() for kw in KEYWORDS)

def is_product_video(desc):
    desc = desc.lower()
    if any(bad in desc for bad in BLACKLIST):
        return False
    if any(cue in desc for cue in PRODUCT_CUES):
        return True
    return False

def load_existing(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ JSON-Datei beschädigt – wird neu erstellt.")
            return []
    return []

def save_output(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def run():
    print("🟡 Agent gestartet …")
    new_data = []
    versuche = 0

    while len(new_data) < MIN_VORSCHLAEGE and versuche < MAX_ITERATIONEN:
        raw = fetch_videos()
        print(f"📥 Runde {versuche+1}: {len(raw)} Videos geladen")

        for v in raw:
            stats = v.get("stats", {})
            shares = stats.get("shareCount", 0)
            comments = stats.get("commentCount", 0)
            likes = stats.get("diggCount", 0)
            desc = v.get("desc", "")

            print(f"🔎 {shares} Shares / {comments} Comments / {likes} Likes | {desc[:60]}")

            if shares < 1000 or comments < 1000:
                continue
            if not is_problem_solver(desc):
                continue
            if not is_product_video(desc):
                print("🚫 Kein Produktvideo laut Filter.")
                continue

            eintrag = {
                "titel": desc[:80],
                "tiktok_link": f"https://www.tiktok.com/@{v.get('author', {}).get('uniqueId', '')}/video/{v.get('id', '')}",
                "shares": shares,
                "kommentare_total": comments,
                "kommentare_aktuell": "nicht geprüft",
                "likes": likes,
                "video_beschreibung": desc,
                "video_datum": v.get("createTime", ""),
                "problemloeser": True,
                "nische": "Küche, Haushalt & Wohnen",
                "status": "VORSCHLAG",
                "erstellt_am": datetime.today().strftime("%Y-%m-%d")
            }

            print(f"✅ Gefiltert: {eintrag['titel']} | Shares: {shares}, Comments: {comments}")
            new_data.append(eintrag)

            if len(new_data) >= MIN_VORSCHLAEGE:
                break

        versuche += 1
        time.sleep(1)

    print(f"🧮 Gültige Vorschläge: {len(new_data)}")

    output_dir = os.path.join("hevolo-scout", "data")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "vorschlaege.json")

    existing = load_existing(path)
    save_output(path, existing + new_data)
    print(f"✅ Vorschläge gespeichert in {path}: {len(existing + new_data)} gesamt")

if __name__ == "__main__":
    run()
