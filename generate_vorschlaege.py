import os
import json
import datetime
import openai
from tikapi import TikAPI, ValidationException, ResponseException

# API-Zugänge aus GitHub Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")
tikapi_key = os.getenv("TIKAPI_KEY")
print("TIKAPI_KEY vorhanden?", bool(tikapi_key))


hashtags = ["tiktokmademebuyit", "cleantok", "viralcleaning", "kitchenhack"]
api = TikAPI(tikapi_key)
video = None

for tag in hashtags:
    print(f"🔍 Suche nach Hashtag: #{tag}")
    try:
        response = api.public.hashtag(name=tag)
        hashtag_id = response.json()['challengeInfo']['challenge']['id']

        feed_response = api.public.hashtag(id=hashtag_id, count=5)
        posts = feed_response.json().get("itemList", [])

        for v in posts:
            if v.get("desc") and v.get("id") and v.get("author"):
                video = v
                break
        if video:
            break
    except ValidationException as e:
        print("Validierungsfehler:", e, e.field)
    except ResponseException as e:
        print("Antwortfehler:", e, e.response.status_code)

if not video:
    raise ValueError("Kein TikTok-Video zu den Hashtags gefunden.")

video_url = f"https://www.tiktok.com/@{video['author']['uniqueId']}/video/{video['id']}"
likes = video['stats']['diggCount']
comments = video['stats']['commentCount']
date = datetime.datetime.fromtimestamp(video['createTime']).strftime('%d.%m.%Y')

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
