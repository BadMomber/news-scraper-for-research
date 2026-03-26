# Story: taz.de Suche

## User Story

Als Rechercheurin möchte ich automatisiert nach Keyword-Paaren auf taz.de suchen und eine vollständige Liste aller passenden Artikel (Titel, Link, Datum) erhalten, damit ich keine relevanten Artikel übersehe.

## Beschreibung

Der Crawler nutzt die eingebaute Suchfunktion von taz.de, um für jedes der 17 Keyword-Paare alle Treffer zu finden. Die beiden Begriffe eines Paares werden als UND-Verknüpfung gesucht. Pagination wird vollständig durchlaufen, damit auch bei vielen Treffern kein Artikel verloren geht. Der Datumsfilter wird im Code angewendet (nicht über die Suchfunktion), um volle Kontrolle über die Filterung zu behalten.

## Akzeptanzkriterien

### Suche

- [ ] Für ein gegebenes Keyword-Paar wird eine Suchanfrage an taz.de gestellt
- [ ] Beide Begriffe werden als UND-Verknüpfung gesucht (nur Artikel, die beide Begriffe enthalten)
- [ ] Die Suche funktioniert mit allen 17 Keyword-Paaren, inklusive Umlauten ("Künstliche Intelligenz")

### Ergebnis-Parsing

- [ ] Aus jeder Suchergebnisseite werden Artikeltitel, Link und Veröffentlichungsdatum extrahiert
- [ ] Die extrahierten Links sind vollständige, absolute URLs

### Pagination

- [ ] Alle Ergebnisseiten werden durchlaufen, nicht nur die erste
- [ ] Die Pagination endet sauber, wenn keine weiteren Ergebnisse vorhanden sind
- [ ] Auch bei hunderten oder tausenden Treffern werden alle Ergebnisse gesammelt

### Datumsfilter

- [ ] Artikel außerhalb des Zeitraums 08.07.2025 – 08.02.2026 werden im Code herausgefiltert
- [ ] Der Datumsfilter ist unabhängig von der taz.de-Suchfunktion implementiert

### Robustheit

- [ ] Rate-Limiting: Pause zwischen Seitenaufrufen, um den Server nicht zu überlasten
- [ ] Timeouts für Navigation und Selektor-Waits sind gesetzt
- [ ] Bei temporären Fehlern (Timeout, Navigation-Fehler) wird der Seitenaufruf wiederholt (mit Backoff)

## Abgrenzung

- Kein Scraping der Artikel-Detailseiten (Autor, Volltext) — das ist AP2b
- Keine Deduplizierung — das ist AP5
- Kein CSV-Export — das ist AP5
