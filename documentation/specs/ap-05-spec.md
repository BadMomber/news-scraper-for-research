# Story: Deduplizierung & CSV-Export

## User Story

Als Rechercheurin möchte ich alle gefundenen Artikel aus taz.de, heise.de und zeit.de in einer einzigen, deduplizierten CSV-Datei erhalten, damit ich eine saubere Datenbasis für meine Analyse habe, ohne Artikel doppelt auswerten zu müssen.

## Beschreibung

Die Ergebnisse aus AP2–AP4 (drei Websites × 17 Keyword-Paare) werden zusammengeführt. Da derselbe Artikel von mehreren Keyword-Paaren gefunden werden kann, werden Duplikate über den Artikeltitel erkannt. Bei Duplikaten erscheint der Artikel nur einmal, und alle Keyword-Paare, die ihn gefunden haben, werden in der Spalte "Used Search Terms" zusammengeführt.

## Akzeptanzkriterien

### Zusammenführung

- [ ] Ergebnisse aus allen drei Websites werden in eine gemeinsame Liste überführt
- [ ] Jeder Artikel behält seine Herkunfts-Metadaten (Date, Link, Titel, Autor, Character Count, Paywall-Markierung)

### Deduplizierung

- [ ] Artikel mit identischem Titel werden als Duplikat erkannt
- [ ] Der Titelvergleich ist exakt (keine Fuzzy-Matching-Logik)
- [ ] Bei Duplikaten bleibt genau ein Eintrag in der Liste
- [ ] Die Spalte "Used Search Terms" des verbleibenden Eintrags enthält alle Keyword-Paare, die den Artikel gefunden haben (Semikolon-getrennt, z.B. `Grok+Hitler; Grok+Deepfake`)
- [ ] Die Reihenfolge der Keyword-Paare in "Used Search Terms" ist stabil (z.B. in der Reihenfolge, in der sie gefunden wurden)

### CSV-Export

- [ ] Die CSV-Datei wird mit UTF-8-Kodierung geschrieben (korrekte Umlaute und ß)
- [ ] Die Spalten sind: Date, Link, Titel, Autor, Used Search Terms, Character Count
- [ ] Das Datumsformat ist einheitlich (z.B. `YYYY-MM-DD`)
- [ ] Felder mit Kommas oder Semikolons werden korrekt escaped (CSV-Standard)
- [ ] Die CSV-Datei hat eine Kopfzeile
- [ ] Der Dateiname ist konfigurierbar oder hat einen sinnvollen Default

### Paywall-Kennzeichnung

- [ ] heise+ und Z+ Artikel sind in der CSV erkennbar (z.B. zusätzliche Spalte oder Markierung im Titel)

## Abgrenzung

- Das Crawling und Scraping ist in AP2–AP4 bereits abgeschlossen
- Keine Verifikation der Links oder Metadaten — das ist AP6
- Kein Fuzzy-Matching bei der Deduplizierung (nur exakter Titelvergleich)
