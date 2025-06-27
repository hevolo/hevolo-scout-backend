import json
from datetime import datetime

def generate():
    new = {
        "id": int(datetime.now().timestamp()),
        "name": "HeatBag™",
        "tiktok": "https://www.tiktok.com/@warmhome/video/1357924680",
        "problem": "Kalte Füße auf der Couch",
        "loesung": "Selbsterwärmende Mikrowellen-Kuscheltasche",
        "usp": "Einfach 90 Sekunden in die Mikrowelle",
        "zielgruppe": "Frauen 20–50, Winterliebhaber, Geschenkideen",
        "marge": "14,60 € bei VK 29,95 €",
        "empfehlung": "Testen empfohlen"
    }

    try:
        with open("vorschlaege.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(new)

    with open("vorschlaege.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[{datetime.now().isoformat()}] Vorschlag hinzugefügt.")

if __name__ == "__main__":
    generate()
