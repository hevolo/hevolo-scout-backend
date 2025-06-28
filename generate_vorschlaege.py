import json
import datetime
import openai

# ⛽ GPT vorbereiten
openai.api_key = "sk-..."  # Hier wird dein echter OpenAI API-Key gesetzt

# 🔍 Simulierter Trend-Eintrag von TikTok
trendprodukt = {
    "name": "StickyRoll™ Fusselroller",
    "video_url": "https://www.tiktok.com/@trendtok/video/123456789",
    "beschreibung": "Ein wiederverwendbarer, abwaschbarer Fusselroller mit starker Haftung für Tierhaare und Kleidung."
}

# 💡 GPT: Analysiere das Produkt
prompt = f"""
Analysiere folgendes virales Produkt aus dem englischen TikTok-Markt und gib mir folgende Informationen auf Deutsch:

1. Welches Problem wird gelöst?
2. Wie sieht die Lösung konkret aus?
3. Wer ist die Zielgruppe?
4. Was ist das Alleinstellungsmerkmal (USP)?
5. Empfiehlst du dieses Produkt für einen deutschen Haushaltswaren-Shop?

Produktname: {trendprodukt['name']}
Beschreibung: {trendprodukt['beschreibung']}
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)

antwort = response.choices[0].message.content.strip().split("\n")

# 📦 AliExpress-Simulation (manuell ausgewählt)
aliexpress_url = "https://www.aliexpress.com/item/1005001234567890.html"

# 📊 Preiskalkulation
ek = 4.99
versand = 2.99
vk = 19.99
marge = vk - ek - versand

# 📅 Zeitstempel
heute = datetime.datetime.now().strftime("%d.%m.%Y")

# 📄 Vorschlag in JSON-Format
vorschlag = {
    "last_update": heute,
    "vorschlaege": [
        {
            "name": trendprodukt["name"],
            "problem": antwort[0].replace("1.", "").strip(),
            "loesung": antwort[1].replace("2.", "").strip(),
            "zielgruppe": antwort[2].replace("3.", "").strip(),
            "usp": antwort[3].replace("4.", "").strip(),
            "empfehlung": antwort[4].replace("5.", "").strip(),
            "ek": ek,
            "vk": vk,
            "versand": versand,
            "marge": round(marge, 2),
            "haendler": aliexpress_url,
            "tiktok": trendprodukt["video_url"]
        }
    ]
}

# 💾 Speichern
with open("vorschlaege.json", "w", encoding="utf-8") as f:
    json.dump(vorschlag, f, indent=2, ensure_ascii=False)

print("✅ Trend-Vorschlag erfolgreich generiert.")
