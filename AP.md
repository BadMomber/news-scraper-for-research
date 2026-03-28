# Arbeitspakete

## AP1: Projektstruktur & Setup ✅
- [x] Python-Projekt aufsetzen (flake.nix, pyproject.toml)
- [x] Projektstruktur festlegen (Feature-basiert: src/taz, src/heise, src/zeit)
- [x] Suchbegriff-Paare und Konfiguration als Datenstruktur anlegen (seed.yaml + config.py)
- [ ] ~~Gemeinsame Basis: HTTP-Session~~ → entfällt, jedes Site-Modul baut eigene Session (Kohäsion)

## AP2a: taz.de Suche ✅
- [x] Suchfunktion von taz.de analysieren (URL-Schema, Parameter)
- [x] Suchergebnisse parsen (Artikeltitel, Link, Datum)
- [x] Pagination behandeln (alle Ergebnisseiten durchlaufen)
- [x] Datumsfilter im Code anwenden (08.07.2025 – 08.02.2026)
- [ ] Test mit 2–3 Keyword-Paaren

> taz.de hat keine Paywall → idealer Startpunkt und Proof of Concept

## AP2b: taz.de Artikeldetails ✅
- [x] Artikel-Detailseite scrapen: Autor extrahieren
- [x] Artikeltext extrahieren (reiner Inhalt, ohne Navigation/Werbung)
- [x] Character Count berechnen
- [x] Datenstruktur mit allen Feldern zusammenführen
- [x] Test mit Artikeln aus AP2a

## AP3a: heise.de Suche ✅
- [x] Suchfunktion von heise.de analysieren (URL-Schema, Parameter)
- [x] Suchergebnisse parsen (Artikeltitel, Link, Datum)
- [x] Pagination behandeln (alle Ergebnisseiten durchlaufen)
- [x] Datumsfilter im Code anwenden (08.07.2025 – 08.02.2026)
- [x] Test mit 2–3 Keyword-Paaren

## AP3b: heise.de Artikeldetails ✅
- [x] Artikel-Detailseite scrapen: Autor extrahieren
- [x] Artikeltext extrahieren (reiner Inhalt)
- [x] heise+ Artikel erkennen und markieren
- [x] Bei heise+ Artikeln: Teaser-Text übernehmen, reduzierter Character Count
- [x] Test mit frei zugänglichen und heise+ Artikeln

## AP3c: heise.de Paywall-Handling
- [ ] Stufe 1: Google-Referer
- [ ] Stufe 2: Request ohne JavaScript (HTML prüfen)
- [ ] Stufe 3: Google-Cache
- [ ] Stufe 4: Archive-Dienste (archive.org)
- [ ] Bei Erfolg: Teaser durch Volltext ersetzen, Character Count aktualisieren
- [ ] Bei Misserfolg: Teaser und Markierung beibehalten

## AP4a: zeit.de Suche
- [ ] Suchfunktion von zeit.de analysieren (URL-Schema, Parameter)
- [ ] Suchergebnisse parsen (Artikeltitel, Link, Datum)
- [ ] Pagination behandeln (alle Ergebnisseiten durchlaufen)
- [ ] Datumsfilter im Code anwenden (08.07.2025 – 08.02.2026)
- [ ] Test mit 2–3 Keyword-Paaren

## AP4b: zeit.de Artikeldetails
- [ ] Artikel-Detailseite scrapen: Autor extrahieren
- [ ] Artikeltext extrahieren (reiner Inhalt)
- [ ] Z+ Artikel erkennen und markieren
- [ ] Bei Z+ Artikeln: Teaser-Text übernehmen, reduzierter Character Count
- [ ] Metered Paywall: Cookies zwischen Requests nicht persistieren
- [ ] Test mit frei zugänglichen und Z+ Artikeln

## AP4c: zeit.de Paywall-Handling
- [ ] Stufe 1: Google-Referer
- [ ] Stufe 2: Request ohne JavaScript (HTML prüfen)
- [ ] Stufe 3: Google-Cache
- [ ] Stufe 4: Archive-Dienste (archive.org)
- [ ] Bei Erfolg: Teaser durch Volltext ersetzen, Character Count aktualisieren
- [ ] Bei Misserfolg: Teaser und Markierung beibehalten

## AP5: Deduplizierung & CSV-Export
- [ ] Alle Ergebnisse aus AP2–AP4 zusammenführen
- [ ] Deduplizierung über Artikeltitel implementieren
- [ ] "Used Search Terms" bei Duplikaten zusammenführen (Semikolon-getrennt)
- [ ] CSV-Ausgabe schreiben (UTF-8, korrekte Spalten)

## AP6: Verifikation
- [ ] Link-Erreichbarkeit prüfen (HTTP-Statuscode)
- [ ] Metadaten-Abgleich: Titel und Datum auf der Zielseite mit CSV-Daten vergleichen
- [ ] Verifikationsbericht ausgeben (bestanden / fehlgeschlagen pro Artikel)

## AP7: Gesamtlauf & Feinschliff
- [ ] Alle 17 Keyword-Paare × 3 Seiten = 51 Suchen durchführen
- [ ] Logging: Fortschritt und Fehler nachvollziehbar ausgeben
- [ ] Robustheit: Fehlerbehandlung bei Timeouts, 429er, Netzwerkfehlern
- [ ] Finale CSV prüfen und ggf. Korrekturen

## Reihenfolge & Abhängigkeiten

```
AP1 → AP2 → AP3 → AP4 → AP5 → AP6 → AP7
       ↑ Proof of Concept
```

AP2–AP4 sind nach AP1 prinzipiell unabhängig voneinander, aber es empfiehlt sich, mit taz.de (AP2) zu starten, weil dort keine Paywall stört und man die Grundstruktur sauber entwickeln kann. AP3 und AP4 bauen dann auf den gleichen Mustern auf.
