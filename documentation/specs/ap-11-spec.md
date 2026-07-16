# Story: Harte Ausschlusskriterien — Mindestlänge & Mindest-Trefferzahl

## User Story

Als Rechercheurin möchte ich, dass Artikel unter 2000 Zeichen oder mit weniger als vier Suchbegriff-Treffern im Volltext automatisch aussortiert werden, damit die Ergebnismenge den harten Ausschlusskriterien meiner Masterarbeit entspricht.

## Beschreibung

Die Masterarbeit definiert zwei harte Ausschlusskriterien:

> Two hard exclusion criteria were applied: a character count below 2,000 and fewer than four searchterm matches in the article body.

Diese Kriterien werden in den bestehenden Volltextfilter (AP10) integriert. Der Filter läuft weiterhin nach dem Crawlen als lokale Operation auf `ergebnisse.csv` und `texte/` — zusätzlich ist er jetzt als eigenständiger Lauf ohne neuen Crawl aufrufbar, um bereits vorhandene lokale Ergebnisse nachträglich zu filtern.

## Anforderungen

### Kriterium 1: Mindestlänge

- Artikel mit **Character Count < 2000** werden entfernt
- Grenzwert: genau 2000 Zeichen wird **behalten** („below 2,000" schließt aus)
- Grundlage ist die CSV-Spalte „Character Count"; ist sie leer oder ungültig, wird die Länge der Textdatei verwendet

### Kriterium 2: Mindest-Trefferzahl

- Artikel mit **weniger als 4 Suchbegriff-Kombinationen** im Artikeltext werden entfernt
- Grenzwert: genau 4 Kombinationen wird **behalten** („fewer than four" schließt aus)
- **Zählweise: Anzahl verschiedener vollständig gefundener Keyword-Paare** (fachliche Entscheidung, 2026-07-16; ersetzt die zunächst gewählte Summen-Zählweise):
  - Ein Paar zählt als gefunden, wenn **beide Wörter** irgendwo im Text vorkommen — nicht nebeneinander, case-insensitive, Teilwort-Treffer zählen („Groks" enthält „Grok")
  - Wie oft die Wörter vorkommen, ist unerheblich: ein Paar zählt höchstens einmal
  - **Grundmenge sind alle im Crawl verwendeten Keyword-Paare** (Vereinigung der Spalte „Used Search Terms" über die gesamte CSV), nicht nur die dem Artikel zugeordneten Paare
  - Beispiel: Text enthält 4× „Grok" sowie je 1× „Hitler", „Deepfake", „Verantwortung", „xAI" → die Paare Grok+Hitler, Grok+Deepfake, Grok+Verantwortung, Grok+xAI sind vollständig → 4 Kombinationen → Artikel bleibt

### Filterverhalten

- Das bestehende Kriterium aus AP10 (mindestens ein vollständiges Keyword-Paar im Text) bleibt erhalten
- Entfernte Artikel: aus der CSV entfernt, Textdatei in `texte/` gelöscht
- Pro entferntem Artikel wird der **Grund geloggt** (kein Paar / unter 2000 Zeichen / unter 4 Treffer)

### Eigenständiger Aufruf (ohne neuen Crawl)

- `python -m src.fulltext_filter` wendet den Filter auf bestehende lokale Ergebnisse an
- Optionen: `--csv` (Default: `ergebnisse.csv`), `--texte` (Default: `texte/`)
- Der Filter bleibt zusätzlich Teil des normalen Gesamtlaufs (`main.py`)

## Akzeptanzkriterien

- [x] Artikel mit Character Count < 2000 werden entfernt; genau 2000 bleibt erhalten
- [x] Artikel mit weniger als 4 Suchbegriff-Kombinationen werden entfernt; genau 4 bleibt erhalten
- [x] Zählweise: Anzahl verschiedener vollständig gefundener Paare aus allen Crawl-Paaren, case-insensitive
- [x] Das AP10-Kriterium (mindestens ein Paar vollständig im Text) gilt weiterhin
- [x] Der Entfernungsgrund wird pro Artikel geloggt und im FilterResult zurückgegeben
- [x] Der Filter ist ohne neuen Crawl auf lokale Daten anwendbar (`python -m src.fulltext_filter`)
- [x] main.py bleibt unverändert lauffähig (Filter läuft weiterhin im Gesamtlauf)

## Abgrenzung

- Kein erneuter Crawl — der Filter arbeitet ausschließlich auf lokal vorhandenen Daten
- Kein Stemming oder Fuzzy-Matching — exakte Teilstring-Suche (case-insensitive) wie in AP10
- Keine Änderung an Such- oder Scraping-Logik
- Kein Backup durch den Filter selbst — wer die Originaldaten behalten will, sichert CSV und `texte/` vorher
