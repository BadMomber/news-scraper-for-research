# Plan: AP4c — zeit.de Paywall-Handling

## Kontext

AP4c sollte den Volltext von Z+ Artikeln beschaffen. Nach Recherche ist keine Strategie automatisierbar.

## Getestete Strategien

| Strategie | Ergebnis |
|-----------|----------|
| Normal (Baseline) | Nur Teaser (527–853 Zeichen vs 1500+ bei freien Artikeln) |
| Google Referer | Identisch mit Baseline |
| JavaScript deaktiviert | Identisch mit Baseline |
| Google Referer + JS disabled | Identisch |
| Googlebot User-Agent | Identisch |

Vergleich: Freie Artikel haben 7–8 Absätze (1500–1750 Zeichen), Z+ nur 2–4 Absätze (527–853 Zeichen).

Hinweis: Die Metered Paywall wird bereits in AP4b durch frische Browser-Kontexte umgangen. Hier geht es nur um die harte Z+ Paywall.

## Entscheidung

**Kein automatisierter Bypass möglich.** Gleiche Situation wie heise+. Z+ Artikel werden mit Teaser aufgenommen:

- Artikel bleibt in der CSV mit `Paywall=Z+`
- Character Count bezieht sich auf den Teaser-Text
- Autor wird extrahiert (funktioniert auch bei Z+)
- **Manueller Workaround:** Nutzer kann Volltexte ggf. über archive.ph abrufen
