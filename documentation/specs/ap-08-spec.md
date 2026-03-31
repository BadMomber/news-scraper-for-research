# Spezifikation: Inkrementelle CSV & Volltext-Speicherung

## Ziel

Der Crawler soll Ergebnisse während des Laufs inkrementell speichern, damit bei einem Abbruch die bisherigen Daten erhalten bleiben. Zusätzlich wird der vollständige Artikeltext als separate Textdatei gespeichert, eindeutig dem CSV-Eintrag zugeordnet.

## Anforderungen

### Inkrementelle CSV

- Die CSV wird nach jedem abgeschlossenen Keyword-Paar pro Seite aktualisiert (z.B. nach "Grok+Hitler auf taz.de")
- Neue Artikel werden an die bestehende CSV angehängt
- Die Deduplizierung läuft über die gesamte bisherige CSV (nicht nur über den aktuellen Block)
- Bei Duplikaten wird die "Used Search Terms"-Spalte im bestehenden Eintrag ergänzt
- Die CSV hat von Anfang an einen Header

### Volltext-Speicherung

- Der Artikeltext wird als separate Textdatei gespeichert (nicht in der CSV)
- Die Textdateien liegen in einem Verzeichnis `texte/`
- Der Dateiname ist ein eindeutiger Hash oder Slug, der den Artikel identifizierbar macht
- Die CSV enthält eine neue Spalte "Textdatei" mit dem Dateinamen (Zuordnung CSV ↔ Textdatei)
- Bei Paywall-Artikeln (heise+, Z+) wird der verfügbare Teaser-Text gespeichert
- Der Character Count bezieht sich weiterhin auf den gespeicherten Text

### Robustheit

- Ein Abbruch mitten im Lauf hinterlässt eine gültige CSV mit allen bis dahin verarbeiteten Artikeln
- Die Textdateien werden sofort nach dem Scraping geschrieben
- Ein Neustart überschreibt die bestehende CSV (kein Append an alte Läufe)

## Akzeptanzkriterien

- [ ] Nach dem Scraping des ersten Keyword-Paars auf der ersten Seite existiert bereits eine CSV mit Ergebnissen
- [ ] Bei einem Abbruch nach 50% des Laufs enthält die CSV ~50% der Ergebnisse
- [ ] Jeder Artikel in der CSV hat eine zugeordnete Textdatei in `texte/`
- [ ] Die Textdatei enthält den vollständigen Artikeltext (oder Teaser bei Paywall)
- [ ] Duplikate werden korrekt erkannt — ein Artikel erscheint nur einmal in der CSV, aber "Used Search Terms" enthält alle Keyword-Paare
- [ ] Die CSV ist nach jedem Schreibvorgang valide (korrekter Header, kein abgeschnittener letzter Eintrag)

## Abgrenzung

- Kein Wiederaufsetzen nach Abbruch (die CSV wird bei jedem neuen Lauf überschrieben)
- Keine Änderung an der Such- oder Scraping-Logik — nur an der Speicherung
- Die Verifikation (AP6) läuft weiterhin am Ende über die fertige CSV

## Abhängigkeiten

- Setzt auf AP5 (Dedup & CSV) auf und ersetzt dessen Speicherlogik
- AP6 (Verifikation) bleibt unverändert
