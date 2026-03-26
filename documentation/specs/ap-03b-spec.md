# Story: heise.de Artikeldetails

## User Story

Als Rechercheurin möchte ich für jeden auf heise.de gefundenen Artikel automatisch den Autor, die Zeichenanzahl und eine Markierung erhalten, ob es sich um einen heise+ Artikel handelt, damit ich die Artikelmetadaten vollständig erfassen und Paywall-Artikel erkennen kann.

## Beschreibung

Für jeden Artikel aus der Ergebnisliste von AP3a wird die Detailseite auf heise.de aufgerufen. Dort werden Autor und Artikeltext extrahiert. Bei heise+ Artikeln ist nur der Teaser-Text frei zugänglich — der Artikel wird trotzdem erfasst, als heise+ markiert und der Character Count bezieht sich auf den sichtbaren Teaser. Die Paywall-Umgehung folgt separat in AP3c.

## Akzeptanzkriterien

### Autor-Extraktion

- [ ] Der Autorname wird von der Artikel-Detailseite extrahiert
- [ ] Wenn kein Autor angegeben ist, wird das Feld leer gelassen
- [ ] Bei mehreren Autoren werden alle erfasst (kommagetrennt)

### Volltext und Character Count

- [ ] Der Artikeltext wird extrahiert (nur redaktioneller Inhalt, ohne Navigation, Sidebar, Werbung, Kommentare)
- [ ] Der Character Count wird als Zeichenanzahl des extrahierten Textes berechnet
- [ ] Leerzeichen und Zeilenumbrüche werden mitgezählt

### heise+ Erkennung

- [ ] heise+ Artikel werden beim Scraping der Detailseite erkannt (z.B. anhand von CSS-Klassen, Paywall-Elementen oder URL-Mustern)
- [ ] heise+ Artikel werden in den Ergebnisdaten als solche markiert (z.B. Feld `paywall: true`)
- [ ] Bei heise+ Artikeln wird der sichtbare Teaser-Text als Artikeltext übernommen
- [ ] Der Character Count bei heise+ Artikeln bezieht sich auf den Teaser-Text (reduzierter Count)

### Datenstruktur

- [ ] Jeder Artikel hat nach AP3b alle Felder: Date, Link, Titel, Autor, Character Count, Paywall-Markierung
- [ ] Das Feld "Used Search Terms" enthält das Keyword-Paar (Format: `Begriff1+Begriff2`)
- [ ] Die Ergebnisse werden als strukturierte Daten zurückgegeben

### Robustheit

- [ ] Rate-Limiting: Pause zwischen Seitenaufrufen
- [ ] Timeouts für Navigation und Selektor-Waits sind gesetzt
- [ ] Bei temporären Fehlern wird der Seitenaufruf wiederholt
- [ ] Wenn eine Artikelseite nicht geladen werden kann, wird der Fehler geloggt und der Artikel übersprungen

## Abgrenzung

- Die Suche und Ergebnisliste kommt aus AP3a
- heise+ Artikel werden erkannt und markiert, aber die Paywall wird hier **nicht** umgangen — das ist AP3c
- Keine Deduplizierung oder CSV-Export — das ist AP5
