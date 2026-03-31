# Story: Premiumzugänge für Paywall-Artikel

## User Story

Als Rechercheurin möchte ich meine Zugangsdaten für heise+ und Z+ hinterlegen können, damit der Crawler auch Paywall-Artikel im Volltext abrufen kann.

## Beschreibung

Aktuell werden bei Paywall-Artikeln (heise+, Z+) nur die sichtbaren Teaser-Texte gespeichert. Durch Hinterlegung von Username und Passwort in der `seed.yaml` soll der Crawler sich einloggen und den vollständigen Artikeltext abrufen können.

## Anforderungen

### Konfiguration

- Credentials werden in `seed.yaml` unter einem neuen Abschnitt `credentials` hinterlegt
- Format:
  ```yaml
  credentials:
    heise:
      username: "user@example.com"
      password: "geheim"
    zeit:
      username: "user@example.com"
      password: "geheim"
  ```
- Der Abschnitt ist optional — ohne ihn verhält sich der Crawler wie bisher
- Einzelne Seiten können weggelassen werden (z.B. nur heise, nicht zeit)

### Login-Verhalten

- Der Login erfolgt einmal pro Seite zu Beginn des Scraping-Blocks (nicht pro Artikel)
- Nach erfolgreichem Login werden alle Artikel dieser Seite im eingeloggten Zustand abgerufen
- Bei fehlgeschlagenem Login wird eine Warnung geloggt und ohne Login weitergemacht (Fallback auf Teaser-Text)

### Betroffene Seiten

- **heise.de**: Login über heise.de Login-Seite
- **zeit.de**: Login über zeit.de Login-Seite
- **taz.de**: Keine Paywall, kein Login nötig

### Fallback

- Ohne Credentials: Verhalten wie bisher (Teaser-Text bei Paywall-Artikeln)
- Bei Login-Fehler: Warnung loggen, Teaser-Text speichern
- Der Character Count bezieht sich immer auf den tatsächlich gespeicherten Text

## Akzeptanzkriterien

- [ ] Credentials können in `seed.yaml` hinterlegt werden
- [ ] Der Crawler loggt sich bei heise.de ein und ruft heise+-Artikel im Volltext ab
- [ ] Der Crawler loggt sich bei zeit.de ein und ruft Z+-Artikel im Volltext ab
- [ ] Ohne Credentials funktioniert der Crawler wie bisher
- [ ] Bei ungültigen Credentials wird eine Warnung geloggt und der Teaser-Text gespeichert
- [ ] Der Login erfolgt einmal pro Seite, nicht pro Artikel

## Abgrenzung

- Kein Login für taz.de (keine Paywall)
- Keine verschlüsselte Speicherung der Credentials (seed.yaml ist lokal)
- Keine 2FA-Unterstützung
- Keine Änderung an der Such-Logik — nur am Scraping
