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

## AP3c: heise.de Paywall-Handling ⚠️ (nicht automatisierbar)
- [x] Stufe 1: Google-Referer — getestet, nur Teaser
- [x] Stufe 2: Request ohne JavaScript — getestet, Text nicht im HTML
- [x] Stufe 3: Google-Cache — getestet, nicht verfügbar
- [x] Stufe 4: Archive-Dienste — archive.org nicht archiviert, archive.ph hat CAPTCHA
- [x] Bei Misserfolg: Teaser und Markierung beibehalten ✅
- Manueller Workaround: Nutzer holt Volltexte über archive.ph (CAPTCHA)

## AP4a: zeit.de Suche ✅
- [x] Suchfunktion von zeit.de analysieren (URL-Schema, Parameter)
- [x] Suchergebnisse parsen (Artikeltitel, Link, Datum)
- [x] Pagination behandeln (alle Ergebnisseiten durchlaufen)
- [x] Datumsfilter im Code anwenden (08.07.2025 – 08.02.2026)
- [x] Test mit 2–3 Keyword-Paaren

## AP4b: zeit.de Artikeldetails ✅
- [x] Artikel-Detailseite scrapen: Autor extrahieren
- [x] Artikeltext extrahieren (reiner Inhalt)
- [x] Z+ Artikel erkennen und markieren
- [x] Bei Z+ Artikeln: Teaser-Text übernehmen, reduzierter Character Count
- [x] Metered Paywall: Cookies zwischen Requests nicht persistieren
- [x] Test mit frei zugänglichen und Z+ Artikeln

## AP4c: zeit.de Paywall-Handling ⚠️ (nicht automatisierbar)
- [x] Stufe 1: Google-Referer — getestet, identisch mit Baseline
- [x] Stufe 2: JS disabled / Googlebot UA — getestet, identisch
- [x] Stufe 3: Google-Cache — nicht getestet (bei heise+ bereits gescheitert)
- [x] Stufe 4: Archive-Dienste — nicht getestet (CAPTCHA bei archive.ph)
- [x] Bei Misserfolg: Teaser und Markierung beibehalten ✅
- Metered Paywall wird durch frische Browser-Kontexte in AP4b umgangen

## AP5: Deduplizierung & CSV-Export ✅
- [x] Alle Ergebnisse aus AP2–AP4 zusammenführen
- [x] Deduplizierung über Artikeltitel implementieren
- [x] "Used Search Terms" bei Duplikaten zusammenführen (Semikolon-getrennt)
- [x] CSV-Ausgabe schreiben (UTF-8, korrekte Spalten)

## AP6: Verifikation ✅
- [x] Link-Erreichbarkeit prüfen (HTTP-Statuscode)
- [x] Metadaten-Abgleich: Titel und Datum auf der Zielseite mit CSV-Daten vergleichen
- [x] Verifikationsbericht ausgeben (bestanden / fehlgeschlagen pro Artikel)

## AP7: Gesamtlauf & Feinschliff ✅
- [x] Alle 17 Keyword-Paare × 3 Seiten = 51 Suchen durchführen
- [x] Logging: Fortschritt und Fehler nachvollziehbar ausgeben ("Suche 12/51: heise.de — Grok+xAI")
- [x] Robustheit: Fehlerbehandlung bei Timeouts, 429er, Netzwerkfehlern
- [x] Finale CSV prüfen und ggf. Korrekturen
- [x] Fix: taz.de Agentur-Autoren aus Bodytext extrahieren ("dpa |" → Autor "dpa")
- [x] Fix: heise+ Artikel mit 0 Zeichen → Fallback auf meta description

## Reihenfolge & Abhängigkeiten

```
AP1 → AP2 → AP3 → AP4 → AP5 → AP6 → AP7
       ↑ Proof of Concept
```

AP2–AP4 sind nach AP1 prinzipiell unabhängig voneinander, aber es empfiehlt sich, mit taz.de (AP2) zu starten, weil dort keine Paywall stört und man die Grundstruktur sauber entwickeln kann. AP3 und AP4 bauen dann auf den gleichen Mustern auf.
