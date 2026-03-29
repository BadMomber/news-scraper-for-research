# Plan: AP3c — heise.de Paywall-Handling

## Kontext

AP3c sollte den Volltext von heise+ Artikeln über eine 4-Stufen-Strategie beschaffen. Nach ausführlicher Recherche ist keine der Strategien automatisierbar.

## Getestete Strategien

| Strategie | Ergebnis |
|-----------|----------|
| Google Referer | Nur Teaser — serverseitige Paywall |
| JavaScript deaktiviert | Nur Teaser — Text nicht im HTML versteckt |
| Google Cache | Nicht verfügbar (Cookie-Consent-Seite) |
| Wayback Machine | Nicht archiviert (API: `archived_snapshots: {}`) |
| archive.ph | Content vorhanden, aber CAPTCHA-Wall für Bots |
| 12ft.io | SSL-Fehler, Dienst nicht erreichbar |
| Google AMP Cache | Nicht verfügbar |
| Bing Cache | Dienst nicht verfügbar |

## Entscheidung

**Kein automatisierter Paywall-Bypass möglich.** heise+ Artikel werden mit dem sichtbaren Teaser aufgenommen:

- Artikel bleibt in der CSV mit `Paywall=heise+`
- Character Count bezieht sich auf den Teaser-Text
- Autor bleibt leer (nicht auf Teaser-Seite verfügbar)
- **Manueller Workaround:** Nutzer kann Volltexte über archive.ph abrufen (CAPTCHA manuell lösen)

Beispiel-URL zum manuellen Abruf:
`https://archive.ph/newest/https://www.heise.de/select/tr/2025/6/2518114104152915063`
