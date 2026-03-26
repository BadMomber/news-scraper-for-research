# Story: taz.de Artikeldetails

## User Story

Als Rechercheurin möchte ich für jeden auf taz.de gefundenen Artikel automatisch den Autor und die Zeichenanzahl des Volltexts erhalten, damit ich die Artikelmetadaten vollständig in meine Analyse aufnehmen kann.

## Beschreibung

Für jeden Artikel aus der Ergebnisliste von AP2a wird die Detailseite auf taz.de aufgerufen. Dort werden Autor und Artikeltext extrahiert. Der Character Count bezieht sich auf den reinen Artikeltext (ohne Navigation, Werbung, Kommentare etc.). Da taz.de keine Paywall hat, ist der Volltext immer zugänglich.

## Akzeptanzkriterien

### Autor-Extraktion

- [ ] Der Autorname wird von der Artikel-Detailseite extrahiert
- [ ] Wenn kein Autor angegeben ist, wird das Feld leer gelassen (nicht mit Platzhalter befüllt)
- [ ] Bei mehreren Autoren werden alle erfasst (kommagetrennt)

### Volltext und Character Count

- [ ] Der Artikeltext wird extrahiert (nur der redaktionelle Inhalt, ohne Navigation, Sidebar, Werbung, Kommentare)
- [ ] Der Character Count wird als Zeichenanzahl des extrahierten Textes berechnet
- [ ] Leerzeichen und Zeilenumbrüche werden mitgezählt

### Datenstruktur

- [ ] Jeder Artikel hat nach AP2b alle Felder: Date, Link, Titel, Autor, Character Count
- [ ] Das Feld "Used Search Terms" enthält das Keyword-Paar, das diesen Artikel gefunden hat (Format: `Begriff1+Begriff2`)
- [ ] Die Ergebnisse werden als strukturierte Daten zurückgegeben (z.B. Liste von Dicts oder Dataclasses)

### Robustheit

- [ ] Rate-Limiting: Pause zwischen Seitenaufrufen
- [ ] Timeouts für Navigation und Selektor-Waits sind gesetzt
- [ ] Bei temporären Fehlern wird der Seitenaufruf wiederholt
- [ ] Wenn eine Artikelseite nicht geladen werden kann, wird der Fehler geloggt und der Artikel übersprungen (kein Abbruch)

## Abgrenzung

- Die Suche und Ergebnisliste kommt aus AP2a — AP2b setzt darauf auf
- Keine Paywall-Behandlung nötig (taz.de hat keine Paywall)
- Keine Deduplizierung — das ist AP5
- Kein CSV-Export — das ist AP5
