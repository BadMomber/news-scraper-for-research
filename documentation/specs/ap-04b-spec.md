# Story: zeit.de Artikeldetails

## User Story

Als Rechercheurin möchte ich für jeden auf zeit.de gefundenen Artikel automatisch den Autor, die Zeichenanzahl und eine Markierung erhalten, ob es sich um einen Z+ Artikel handelt, damit ich die Artikelmetadaten vollständig erfassen und Paywall-Artikel erkennen kann.

## Beschreibung

Für jeden Artikel aus der Ergebnisliste von AP4a wird die Detailseite auf zeit.de aufgerufen. Dort werden Autor und Artikeltext extrahiert. zeit.de hat zwei Paywall-Mechanismen: eine Metered Paywall (begrenzte Anzahl freier Artikel) und eine harte Z+ Paywall. Um die Metered Paywall nicht auszulösen, wird jeder Artikel in einem frischen Browser-Kontext geöffnet (keine Cookies aus vorherigen Aufrufen). Z+ Artikel werden erkannt, markiert und mit dem sichtbaren Teaser-Text erfasst. Die Paywall-Umgehung folgt in AP4c.

## Akzeptanzkriterien

### Autor-Extraktion

- [ ] Der Autorname wird von der Artikel-Detailseite extrahiert
- [ ] Wenn kein Autor angegeben ist, wird das Feld leer gelassen
- [ ] Bei mehreren Autoren werden alle erfasst (kommagetrennt)

### Volltext und Character Count

- [ ] Der Artikeltext wird extrahiert (nur redaktioneller Inhalt, ohne Navigation, Sidebar, Werbung, Kommentare)
- [ ] Der Character Count wird als Zeichenanzahl des extrahierten Textes berechnet
- [ ] Leerzeichen und Zeilenumbrüche werden mitgezählt

### Z+ Erkennung

- [ ] Z+ Artikel werden beim Scraping der Detailseite erkannt (z.B. anhand von CSS-Klassen, Paywall-Elementen oder URL-Mustern)
- [ ] Z+ Artikel werden in den Ergebnisdaten als solche markiert (z.B. Feld `paywall: true`)
- [ ] Bei Z+ Artikeln wird der sichtbare Teaser-Text als Artikeltext übernommen
- [ ] Der Character Count bei Z+ Artikeln bezieht sich auf den Teaser-Text (reduzierter Count)

### Metered Paywall

- [ ] Jeder Artikel wird in einem frischen Browser-Kontext geöffnet (keine Cookies aus vorherigen Aufrufen)
- [ ] Frischer Browser-Kontext verhindert, dass die Metered Paywall greift

### Datenstruktur

- [ ] Jeder Artikel hat nach AP4b alle Felder: Date, Link, Titel, Autor, Character Count, Paywall-Markierung
- [ ] Das Feld "Used Search Terms" enthält das Keyword-Paar (Format: `Begriff1+Begriff2`)
- [ ] Die Ergebnisse werden als strukturierte Daten zurückgegeben

### Robustheit

- [ ] Rate-Limiting: Pause zwischen Seitenaufrufen
- [ ] Timeouts für Navigation und Selektor-Waits sind gesetzt
- [ ] Bei temporären Fehlern wird der Seitenaufruf wiederholt
- [ ] Wenn eine Artikelseite nicht geladen werden kann, wird der Fehler geloggt und der Artikel übersprungen

## Abgrenzung

- Die Suche und Ergebnisliste kommt aus AP4a
- Z+ Artikel werden erkannt und markiert, aber die Paywall wird hier **nicht** umgangen — das ist AP4c
- Keine Deduplizierung oder CSV-Export — das ist AP5
