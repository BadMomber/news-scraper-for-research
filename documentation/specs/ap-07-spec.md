# Story: Gesamtlauf & Feinschliff

## User Story

Als Rechercheurin möchte ich den gesamten Crawler mit einem einzigen Befehl starten und den Fortschritt nachvollziehen können, damit ich die vollständige Artikelsuche ohne manuelle Eingriffe durchführen kann.

## Beschreibung

Alle Einzelteile (Suche, Scraping, Paywall-Handling, Deduplizierung, CSV-Export, Verifikation) werden zu einem durchgängigen Lauf zusammengefügt. Der Crawler führt alle 51 Suchen (17 Keyword-Paare × 3 Seiten) durch, verarbeitet die Ergebnisse und gibt eine finale CSV aus. Logging macht den Fortschritt und eventuelle Fehler nachvollziehbar. Der Lauf ist robust gegen Netzwerkfehler.

## Akzeptanzkriterien

### Gesamtlauf

- [ ] Ein einziger Befehl (z.B. `python main.py`) startet den kompletten Crawler
- [ ] Alle 17 Keyword-Paare werden auf allen 3 Seiten gesucht (= 51 Suchen)
- [ ] Die seed.yaml wird als Konfiguration eingelesen
- [ ] Am Ende steht eine deduplizierte CSV und ein Verifikationsbericht

### Logging

- [ ] Der Fortschritt wird auf der Konsole ausgegeben (z.B. "Suche 12/51: heise.de — Grok+xAI — 7 Treffer")
- [ ] Fehler werden geloggt, ohne den Lauf abzubrechen
- [ ] Am Ende wird eine Zusammenfassung ausgegeben (Anzahl Suchen, Anzahl Artikel, Duplikate, Paywall-Artikel)

### Robustheit

- [ ] Bei Netzwerkfehlern (Timeout, Connection Error) wird der betroffene Seitenaufruf wiederholt (max. 3 Versuche mit Backoff)
- [ ] Bei Rate-Limiting wird automatisch gewartet und wiederholt
- [ ] Ein einzelner fehlgeschlagener Seitenaufruf bricht nicht den gesamten Lauf ab
- [ ] Der Crawler kann unterbrochen und für die restlichen Suchen neu gestartet werden (optional, nice-to-have)

### Konfigurierbarkeit

- [ ] Der Dateiname der Ausgabe-CSV ist konfigurierbar (Default: `ergebnisse.csv`)
- [ ] Die Pause zwischen Seitenaufrufen ist konfigurierbar

## Abgrenzung

- Keine neuen Crawling-Funktionen — alles ist in AP2–AP4 implementiert
- Keine neue Deduplizierungs- oder Verifikationslogik — das kommt aus AP5 und AP6
- Das optionale Wiederaufsetzen nach Unterbrechung ist ein Nice-to-have, kein Muss
