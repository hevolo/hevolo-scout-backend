# Trend-Scout-Agent

Dieser Agent scannt TikTok-Trends mithilfe der TikAPI und prüft sie anhand einer 7-Punkte-Checkliste. Ergebnisse werden in `data/vorschlaege.json` gespeichert und wöchentlich aktualisiert.

## Nutzung

- Stelle sicher, dass `TIKAPI_KEY` als GitHub Secret gesetzt ist.
- Die Action läuft jeden Montag um 8 Uhr automatisch.
