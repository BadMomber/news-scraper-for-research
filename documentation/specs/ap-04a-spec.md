# Story: zeit.de Suche

## User Story

Als Rechercheurin möchte ich automatisiert nach Keyword-Paaren auf zeit.de suchen und eine vollständige Liste aller passenden Artikel (Titel, Link, Datum) erhalten, damit ich keine relevanten Artikel auf zeit.de übersehe.

## Beschreibung

Der Crawler nutzt die eingebaute Suchfunktion von zeit.de, um für jedes der 17 Keyword-Paare alle Treffer zu finden. Die beiden Begriffe werden als UND-Verknüpfung gesucht. Pagination wird vollständig durchlaufen. Der Datumsfilter wird im Code angewendet.

## Akzeptanzkriterien

### Suche

- [ ] Für ein gegebenes Keyword-Paar wird eine Suchanfrage an zeit.de gestellt
- [ ] Beide Begriffe werden als UND-Verknüpfung gesucht
- [ ] Die Suche funktioniert mit allen 17 Keyword-Paaren, inklusive Umlauten ("Künstliche Intelligenz")

### Ergebnis-Parsing

- [ ] Aus jeder Suchergebnisseite werden Artikeltitel, Link und Veröffentlichungsdatum extrahiert
- [ ] Die extrahierten Links sind vollständige, absolute URLs

### Pagination

- [ ] Alle Ergebnisseiten werden durchlaufen, nicht nur die erste
- [ ] Die Pagination endet sauber, wenn keine weiteren Ergebnisse vorhanden sind

### Datumsfilter

- [ ] Artikel außerhalb des Zeitraums 08.07.2025 – 08.02.2026 werden im Code herausgefiltert

### Robustheit

- [ ] Rate-Limiting: Pause zwischen Seitenaufrufen
- [ ] Timeouts für Navigation und Selektor-Waits sind gesetzt
- [ ] Bei temporären Fehlern (Timeout, Navigation-Fehler) wird der Seitenaufruf wiederholt (mit Backoff)

## Abgrenzung

- Kein Scraping der Artikel-Detailseiten — das ist AP4b
- Keine Paywall-Behandlung — das ist AP4c
- Keine Deduplizierung oder CSV-Export — das ist AP5
