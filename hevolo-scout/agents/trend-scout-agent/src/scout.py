import json
import os
from datetime import datetime
import requests

TIKAPI_KEY = os.getenv("TIKAPI_KEY")

KEYWORDS = ["hack", "must have", "life changing", "problem", "fix", "clean", "organize"]

def fetch_tiktok_videos():
    url = "https://api.tikapi.io/public/explore"
    params = {
        "country": "us",
        "count": 10
    }
    headers = {
        "X-API-KEY": TIKAPI_KEY
    }
    res = requests.get(url, headers=headers, params=params)
    print(f"Status: {res.status_code} / URL: {res.url}")
    if res.status_code == 403:
        print(f"❌ Zugriff verweigert: {res.text}")
    res.raise_for_status()
    data = res.json()
    print(f"Keys: {list(data.keys())}")
    return data.get("itemList", [])

print(f"🎬 Videos erhalten: {len(data.get('itemList', []))}")

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
        stats = v.get("stats", {})
        comments_today = stats.get("comments", 0)  # Näherung

        #if stats.get("shares", 0) < 100 or stats.get("comments", 0) < 100:
            #continue
        #if comments_today < 1:
            #continue

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

    print(f"🧮 Nach Filter gültige Vorschläge: {len(new_data)}")

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "vorschlaege.json")

    existing = load_existing(path)
    save_output(path, existing + new_data)
    print(f"✅ Daten in {path} gespeichert: {len(existing + new_data)} Gesamtvorschläge")

if __name__ == "__main__":
    run()
