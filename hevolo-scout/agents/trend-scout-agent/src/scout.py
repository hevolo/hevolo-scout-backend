import json
import os
import requests
from datetime import datetime

TIKAPI_KEY = os.getenv("TIKAPI_KEY")
HEADERS = {"X-API-KEY": TIKAPI_KEY}
KEYWORDS = ["hack", "must have", "life changing", "problem", "fix", "clean", "organize"]

def fetch_videos():
    url = "https://api.tikapi.io/public/explore"
    params = {
        "country": "us",
        "count": 30
    }
    res = requests.get(url, headers=HEADERS, params=params)
    print(f"Status: {res.status_code} / URL: {res.url}")
    res.raise_for_status()
    return res.json().get("itemList", [])

def is_problem_solver(desc):
    return any(kw in desc.lower() for kw in KEYWORDS)

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
    raw = fetch_videos()
    print(f"🎬 Videos erhalten: {len(raw)}")

    new_data = []
    for v in raw:
        stats = v.get("stats", {})
        shares = stats.get("shareCount", 0)
        comments = stats.get("commentCount", 0)
        likes = stats.get("diggCount", 0)

        if shares < 1000 or comments < 1000:
            continue
        if not is_problem_solver(v.get("desc", "")):
            continue

        eintrag = {
            "titel": v.get("desc", "")[:80],
            "tiktok_link": f"https://www.tiktok.com/@{v.get('author', {}).get('uniqueId', '')}/video/{v.get('id', '')}",
            "shares": shares,
            "kommentare_total": comments,
            "kommentare_aktuell": "nicht geprüft",
            "likes": likes,
            "video_beschreibung": v.get("desc", ""),
            "video_datum": v.get("createTime", ""),
            "problemloeser": True,
            "nische": "Küche, Haushalt & Wohnen",
            "status": "VORSCHLAG",
            "erstellt_am": datetime.today().strftime("%Y-%m-%d")
        }

        print(f"✅ Gefiltert: {eintrag['titel']} | Shares: {shares}, Comments: {comments}")
        new_data.append(eintrag)

    print(f"🧮 Gültige Vorschläge: {len(new_data)}")

    output_dir = os.path.join("hevolo-scout", "data")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "vorschlaege.json")

    existing = load_existing(path)
    save_output(path, existing + new_data)
    print(f"✅ Vorschläge gespeichert in {path}: {len(existing + new_data)} gesamt")

if __name__ == "__main__":
    run()
