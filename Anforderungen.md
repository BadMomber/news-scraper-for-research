# Anforderungen: Artikel-Crawler für taz.de, zeit.de, heise.de

## Ziel

Ein Python-Crawler, der auf drei deutschen Nachrichtenseiten nach Artikeln sucht, die zu definierten Keyword-Paaren passen, und die Ergebnisse als deduplizierte CSV ausgibt.

## Rahmenbedingungen

- Python >= 3.10
- Die eingebaute Suchfunktion jeder Website nutzen (kein Full-Site-Crawling)
- Suchbegriffe werden immer paarweise verwendet (siehe unten)
- Zeitraum: 08.07.2025 – 08.02.2026
- Deduplizierung über Artikeltitel
- Bei Duplikaten: alle passenden Suchbegriff-Paare zusammenführen

## Ziel-Websites

- https://taz.de
- https://www.zeit.de
- https://www.heise.de

## Suchbegriff-Paare

### Kategorie: Grok-Skandale
| Paar | Begriff 1 | Begriff 2 |
|------|-----------|-----------|
| 1 | Grok | Hitler |
| 2 | Grok | Deepfake |
| 3 | Grok | Verantwortung |
| 4 | Grok | Elon Musk |
| 5 | Grok | X |
| 6 | Grok | xAI |

### Kategorie: Intersektion KI & Grok
| Paar | Begriff 1 | Begriff 2 |
|------|-----------|-----------|
| 7 | Künstliche Intelligenz | Hitler |
| 8 | Künstliche Intelligenz | Deepfake |
| 9 | Künstliche Intelligenz | Verantwortung |
| 10 | Künstliche Intelligenz | Elon Musk |
| 11 | Künstliche Intelligenz | X |
| 12 | Künstliche Intelligenz | xAI |

### Kategorie: Meta-Diskurs
| Paar | Begriff 1 | Begriff 2 |
|------|-----------|-----------|
| 13 | Künstliche Intelligenz | EU |
| 14 | Künstliche Intelligenz | Digital Service Act |
| 15 | Künstliche Intelligenz | Regulierung |
| 16 | Künstliche Intelligenz | Verbot |
| 17 | Künstliche Intelligenz | Sicherheit |

## Ausgabe-CSV

**Dateiformat:** UTF-8 (für Umlaute und ß)

**Spalten:**

| Spalte | Beschreibung |
|--------|-------------|
| Date | Veröffentlichungsdatum des Artikels |
| Link | URL des Artikels |
| Titel | Überschrift des Artikels |
| Autor | Autor des Artikels |
| Used Search Terms | Semikolon-getrennte Liste aller Keyword-Paare, die diesen Artikel gefunden haben (z.B. `Grok+Hitler; Grok+Deepfake`) |
| Character Count | Zeichenanzahl des Artikeltexts |

## Deduplizierung

- Artikel mit gleichem Titel werden als Duplikat behandelt
- Duplikate erscheinen nur einmal in der CSV
- Die Spalte "Used Search Terms" enthält dann alle Keyword-Paare, die den Artikel gefunden haben

## Verifikation

- Automatische Prüfung, dass alle Artikel-Links erreichbar sind
- Automatische Prüfung, dass extrahierte Metadaten (Titel, Datum) mit der verlinkten Seite übereinstimmen

## Paywall-Strategie

### Seiten-Übersicht

| Seite | Paywall-Typ | Vorgehen |
|-------|------------|----------|
| taz.de | Freiwilliges Bezahlmodell ("taz zahl ich") | Kein Problem – alle Artikel frei lesbar |
| heise.de | heise+ für manche Artikel | Teilweise geschützt, Fallback-Strategien nötig |
| zeit.de | Metered + Z+ | Referer-Trick oder requests ohne JS oft ausreichend, Z+-Artikel schwieriger |

### Stufen-Strategie (in dieser Reihenfolge)

1. **Einfacher Request mit Google-Referer** – `Referer: https://www.google.com/` im Header setzen; umgeht viele Metered Paywalls
2. **Requests ohne JavaScript** – Manche Paywalls sind rein clientseitig (Text im HTML vorhanden, nur per JS/CSS versteckt); ein einfacher `requests`-Aufruf liefert den Volltext
3. **Google-Cache** – Artikel über `webcache.googleusercontent.com` abrufen
4. **Archive-Dienste** – Fallback auf `archive.org` (Wayback Machine) oder `archive.ph`

### Character Count bei Paywall-Artikeln

- Wenn keiner der Fallbacks den Volltext liefert: Character Count auf den sichtbaren Teil beschränken und in der CSV kennzeichnen
