import json
import os
from datetime import datetime
import requests
import time

TIKAPI_KEY = os.getenv("TIKAPI_KEY")
KEYWORDS = ["hack", "must have", "life changing", "problem", "fix", "clean", "organize"]

def fetch_tiktok_videos():
    url = "https://api.tikapi.io/public/hashtag"
    params = {
        "name": "tiktokmademebuyit",
        "count": 30
    }
    headers = {
        "X-API-KEY": TIKAPI_KEY
    }
    res = requests.get(url, headers=headers, params=params)
    print(f"Status: {res.status_code} / URL: {res.url}")
    res.raise_for_status()
    data = res.json()
    print(f"🎬 Videos erhalten: {len(data.get('items', []))}")
    return data.get("items", [])

def get_video_stats(video_id):
    url = "https://api.tikapi.io/video/stats"
    headers = {"X-API-KEY": TIKAPI_KEY}
    params = {"video_id": video_id}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print(f"⚠️ Fehler bei stats für Video {video_id}: {res.status_code}")
        return {}
    return res.json().get("stats", {})

def is_problem_solver(desc):
    desc = desc.lower()
    return any(kw in desc for kw in KEYWORDS)

def load_existing(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_output(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def run():
    print("🟡 Agent gestartet …")
    raw = fetch_tiktok_videos()
    print(f"🟢 API Response length: {len(raw)}")

    new_data = []
    for v in raw:
        video_id = v.get("id", "")
        if not video_id:
            continue

        stats = get_video_stats(video_id)
        shares = stats.get("share_count", 0)
        comments = stats.get("comment_count", 0)
        likes = stats.get("like_count", 0)

        if shares < 1000 or comments < 1000:
            continue

        eintrag = {
            "titel": v.get("desc", "")[:80],
            "tiktok_link": f"https://www.tiktok.com/@{v.get('author', {}).get('uniqueId', '')}/video/{video_id}",
            "shares": shares,
            "kommentare_total": comments,
            "kommentare_aktuell": "nicht verfügbar",
            "likes": likes,
            "video_beschreibung": v.get("desc", ""),
            "video_datum": v.get("createTime", ""),
            "problemloeser": is_problem_solver(v.get("desc", "")),
            "nische": "Küche, Haushalt & Wohnen",
            "status": "VORSCHLAG",
            "erstellt_am": datetime.today().strftime("%Y-%m-%d")
        }
        print(f"✅ Hinzugefügt: {eintrag['titel']} | Shares: {shares}, Comments: {comments}")
        new_data.append(eintrag)
        time.sleep(1)

    print(f"🧮 Nach Filter gültige Vorschläge: {len(new_data)}")

    output_dir = os.path.join("hevolo-scout", "data")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "vorschlaege.json")

    existing = load_existing(path)
    save_output(path, existing + new_data)
    print(f"✅ Daten in {path} gespeichert: {len(existing + new_data)} Gesamtvorschläge")

if __name__ == "__main__":
    run()
