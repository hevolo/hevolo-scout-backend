import json
from datetime import datetime
import os

def generate_vorschlaege():
    neue_vorschlaege = [
        {
            "id": 100,
            "name": "SteamBrush™",
            "tiktok": "https://www.tiktok.com/@cleanerlife/video/987654321",
            "problem": "Falten in Kleidung unterwegs",
            "loesung": "Kompakte Dampfbürste für Reisen",
            "usp": "Schnell geglättet ohne Bügelbrett",
            "zielgruppe": "Pendler, Vielreisende, Minimalisten",
            "marge": "17,40 € bei VK 34,95 €",
            "empfehlung": "Testen empfohlen"
        }
    ]

    vorschlag_path = "vorschlaege.json"
    bestehende = []
    if os.path.exists(vorschlag_path):
        with open(vorschlag_path, "r", encoding="utf-8") as f:
            bestehende = json.load(f)

    alle = bestehende + neue_vorschlaege

    with open(vorschlag_path, "w", encoding="utf-8") as f:
        json.dump(alle, f, indent=2, ensure_ascii=False)

    print(f"[{datetime.now().isoformat()}] Neue Vorschläge generiert.")

if __name__ == "__main__":
    generate_vorschlaege()
