import os
import json
import datetime
import openai
import requests
import random

# API-Zugänge aus GitHub Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")
tikapi_key = os.getenv("TIKAPI_KEY")

tag = ["tiktokmademebuyit", "cleantok", "viralcleaning", "kitchenhack"]
headers = {"Authorization": f"Bearer {tikapi_key}"}
video = None

def get_tiktok_videos(tag):
    url = f"https://api.tikapi.io/public/hashtag?name={tag}&count=5"
    response = requests.get(url, headers=headers)
    print(f"TikAPI Antwort für #{tag}:", response.status_code)
    try:
        return response.json().get("data", [])
    except Exception as e:
        print("Fehler beim Verarbeiten der API-Antwort:", e)
        return []

for tag in tag:
    print(f"🔍 Versuche Hashtag: #{tag}")
    posts = get_tiktok_videos(tag)
    for v in posts:
        if v.get("desc") and v.get("id") and v.get("author"):
            video = v
            break
    if video:
        break

if not video:
    raise ValueError("Kein TikTok-Video zu den Hashtags gefunden.")

video_url = f"https://www.tiktok.com/@{video['author']['unique_id']}/video/{video['id']}"
likes = video['stats']['digg_count']
comments = video['stats']['comment_count']
date = datetime.datetime.fromtimestamp(video['create_time']).strftime('%d.%m.%Y')

beschreibung = video['desc'][:1000]
prompt = f"""
Analysiere folgendes virales TikTok-Produkt (englischsprachig) für den deutschen Haushaltsmarkt.
Gib auf Deutsch an:
1. Welches Problem löst es?
2. Wie sieht die Lösung aus?
3. Wer ist die Zielgruppe?
4. Was ist das USP?
5. Soll es im deutschen Shop verkauft werden?

Beschreibung: {beschreibung}
"""

antwort = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
).choices[0].message.content.strip().split("\n")

produktname = video['desc'].split()[0][:25]
aliexpress_url = f"https://www.aliexpress.com/wholesale?SearchText={produktname.replace(' ', '+')}"

ek = 7.99
versand = 2.99
vk = 24.99
marge = round(vk - ek - versand, 2)

vorschlag = {
    "last_update": datetime.datetime.now().strftime("%d.%m.%Y"),
    "vorschlaege": [
        {
            "name": produktname,
            "problem": antwort[0].replace("1.", "").strip(),
            "loesung": antwort[1].replace("2.", "").strip(),
            "zielgruppe": antwort[2].replace("3.", "").strip(),
            "usp": antwort[3].replace("4.", "").strip(),
            "empfehlung": antwort[4].replace("5.", "").strip(),
            "ek": ek,
            "vk": vk,
            "versand": versand,
            "marge": marge,
            "haendler": aliexpress_url,
            "tiktok": video_url,
            "likes": likes,
            "kommentare": comments,
            "veroeffentlicht": date
        }
    ]
}

with open("vorschlaege.json", "w", encoding="utf-8") as f:
    json.dump(vorschlag, f, indent=2, ensure_ascii=False)

print("✅ Vorschlag generiert: " + produktname)
