import json
import os
from datetime import datetime
import requests

TIKAPI_KEY = os.getenv("TIKAPI_KEY")
HEADERS = {"Authorization": f"Bearer {TIKAPI_KEY}"}
TIKAPI_URL = "https://api.tikapi.io/search/posts"

KEYWORDS = ["hack", "must have", "life changing", "problem", "fix", "clean", "organize"]

def fetch_tiktok_videos():
    query = "amazon must have for home"
    params = {
        "query": query,
        "count": 10,
        "region": "US"
    }
    res = requests.get(TIKAPI_URL, headers=HEADERS, params=params)
    res.raise_for_status()
    return res.json().get("data", [])

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
    raw = fetch_tiktok_videos()
    new_data = []
    for v in raw:
        stats = v.get("stats", {})
        comments_today = stats.get("comments", 0)  # einfache Näherung

        if stats.get("shares", 0) < 1000 or stats.get("comments", 0) < 1000:
            continue
        if comments_today < 10:
            continue

        eintrag = {
            "titel": v.get("desc", "")[:80],
            "tiktok_link": f"https://www.tiktok.com/@{v.get('author', {}).get('uniqueId', '')}/video/{v.get('id', '')}",
            "shares": stats.get("shares", 0),
            "kommentare_total": stats.get("comments", 0),
            "kommentare_aktuell": comments_today,
            "likes": stats.get("diggs", 0),
            "video_beschreibung": v.get("desc", ""),
            "video_datum": v.get("createTime", ""),
            "problemloeser": is_problem_solver(v.get("desc", "")),
            "nische": "Küche, Haushalt & Wohnen",
            "status": "VORSCHLAG",
            "erstellt_am": datetime.today().strftime("%Y-%m-%d")
        }
        new_data.append(eintrag)

    path = os.path.join("data", "vorschlaege.json")
    existing = load_existing(path)
    save_output(path, existing + new_data)

if __name__ == "__main__":
    run()
