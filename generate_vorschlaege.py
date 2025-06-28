import os
import json
import datetime
import openai
import requests

# API-Zugänge aus GitHub Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")
tikapi_key = os.getenv("TIKAPI_KEY")

# === TikAPI: Trending Video laden ===
headers = {"Authorization": f"Bearer {tikapi_key}"}
response = requests.get(
    "https://api.tikapi.io/public/posts/search?query=%23tiktokmademebuyit&count=1",
    headers=headers
)

data = response.json()
print(json.dumps(data, indent=2))

video = data["data"][0] if data.get("data") else None

if not video:
    raise ValueError("Kein TikTok-Video gefunden.")

video_url = f"https://www.tiktok.com/@{video['author']['unique_id']}/video/{video['id']}"
likes = video['stats']['digg_count']
comments = video['stats']['comment_count']
date = datetime.datetime.fromtimestamp(video['create_time']).strftime('%d.%m.%Y')

# === GPT: Produkt analysieren ===
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

# === Dummy AliExpress-Händlersuche ===
produktname = video['desc'].split()[0][:25]
aliexpress_url = f"https://www.aliexpress.com/wholesale?SearchText={produktname.replace(' ', '+')}"

# === Preiskalkulation (Platzhalter)
ek = 7.99
versand = 2.99
vk = 24.99
marge = round(vk - ek - versand, 2)

# === Vorschlag erzeugen ===
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
