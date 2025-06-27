# hevolo-scout-render-backend

## 📦 Beschreibung
Python-Skript zur Erzeugung von Produktvorschlägen für hevolo-Scout. Kompatibel mit Render.com als Cronjob oder manuell.

## 🚀 Nutzung lokal
```bash
python generate_vorschlaege.py
```

## 🛠 Deployment auf Render
1. Neues Repo bei GitHub anlegen (z. B. hevolo-scout-agent)
2. Dieses Projekt hochladen
3. Auf [https://render.com](https://render.com) einloggen
4. → New Service → Background Worker
5. GitHub Repo auswählen
6. Start command:
```bash
python generate_vorschlaege.py
```
7. Optional: CRON aktivieren (e.g. `@weekly`)

## 📄 Ausgabe
Die Datei `vorschlaege.json` wird aktualisiert oder neu erstellt.
Diese Datei kann öffentlich ausgegeben oder mit deinem Frontend synchronisiert werden.
