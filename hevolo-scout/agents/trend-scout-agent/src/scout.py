
import json
import os
import requests
import time
from datetime import datetime

TIKAPI_KEY = os.getenv("TIKAPI_KEY")
HEADERS = {"X-API-KEY": TIKAPI_KEY}

KEYWORDS = ["hack", "must have", "life changing", "problem", "fix", "clean", "organize"]

def fetch_videos():
    url = "https://api.tikapi.io/public/explore"
    params = {
        "country": "us",
        "count": 5
    }
    res = requests.get(url, headers=HEADERS, params=params)
    print(f"Status: {res.status_code} / URL: {res.url}")
    res.raise_for_status()
    return res.json().get("itemList", [])

def get_video_stats(video_id):
    url = "https://api.tikapi.io/video/stats"
    params = {"video_id": video_id}
    res = requests.get(url, headers=HEADERS, params=params)
    if res.status_code != 200:
        print(f"⚠️ /video/stats Fehler für {video_id}")
        return {}
    return res.json().get("stats", {})

def get_video_comments(video_id):
    url = "https://api.tikapi.io/video/comments"
    params = {"video_id": video_id, "count": 30}
    res = requests.get(url, headers=HEADERS, params=params)
    if res.status_code != 200:
        print(f"⚠️ /video/comments Fehler für {video_id}")
        return []
    return res.json().get("comments", [])

def is_problem_solver(desc):
    return any(kw in desc.lower() for kw in KEYWORDS)

def load_existing(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ JSON defekt – starte neu.")
            return []
    return []

def save_output(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def run():
    print("🟡 Agent gestartet …")
    raw = fetch_videos()
    print(f"🎬 Videos erhalten: {len(raw)}")
    new_data = []

    for v in raw:
        video_id = v.get("id", "")
        if not video_id:
            continue

        stats = get_video_stats(video_id)
        comments_data = get_video_comments(video_id)
        shares = stats.get("share_count", 0)
        comments = stats.get("comment_count", 0)
        likes = stats.get("like_count", 0)

        # Checklistenfilter
        if shares < 1000 or comments < 1000:
            continue
        recent_comments = [c for c in comments_data if "create_time" in c]
        if len(recent_comments) < 10:
            continue
        if not is_problem_solver(v.get("desc", "")):
            continue

        eintrag = {
            "titel": v.get("desc", "")[:80],
            "tiktok_link": f"https://www.tiktok.com/@{v.get('author', {}).get('uniqueId', '')}/video/{video_id}",
            "shares": shares,
            "kommentare_total": comments,
            "kommentare_aktuell": len(recent_comments),
            "likes": likes,
            "video_beschreibung": v.get("desc", ""),
            "video_datum": v.get("createTime", ""),
            "problemloeser": True,
            "nische": "Küche, Haushalt & Wohnen",
            "status": "VORSCHLAG",
            "erstellt_am": datetime.today().strftime("%Y-%m-%d")
        }

        print(f"✅ Gefunden: {eintrag['titel']} | Shares: {shares}, Comments: {comments}")
        new_data.append(eintrag)
        time.sleep(1)

    print(f"🧮 Gefilterte Vorschläge: {len(new_data)}")

    output_dir = os.path.join("hevolo-scout", "data")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "vorschlaege.json")

    existing = load_existing(path)
    save_output(path, existing + new_data)
    print(f"✅ Gespeichert in {path}: {len(existing + new_data)} Gesamtvorschläge")

if __name__ == "__main__":
    run()
