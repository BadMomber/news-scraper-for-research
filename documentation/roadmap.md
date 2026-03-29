# Implementation Roadmap

## Legende

| Status | Bedeutung |
|--------|-----------|
| ✅ | Abgeschlossen |
| 🔄 | In Arbeit |
| ⏳ | Ausstehend |

## Übersicht

| AP | Beschreibung | Status | Branch | Bemerkungen |
|----|-------------|--------|--------|-------------|
| AP1 | Projektstruktur & Setup | ✅ | `main` | flake.nix, seed.yaml, config.py |
| AP2a | taz.de Suche | ✅ | `feature/ap2a-taz-search` | Suchfunktion, Pagination, Datumsfilter, 24 Tests grün |
| AP2b | taz.de Artikeldetails | ✅ | `feature/ap2b-taz-scrape` | Autor, Bodytext, Character Count, 31 Tests grün |
| AP3a | heise.de Suche | ✅ | `feature/ap3a-heise-search` | Suche, Pagination, heise+ Erkennung, frühes Abbruchkriterium, 49 Tests grün |
| AP3b | heise.de Artikeldetails | ✅ | `feature/ap3b-heise-scrape` | Autor, Bodytext, heise+ Teaser, 56 Tests grün |
| AP3c | heise.de Paywall-Handling | ⚠️ | `feature/ap3c-heise-paywall` | Nicht automatisierbar — serverseitige Paywall, Teaser-Fallback bleibt |
| AP4a | zeit.de Suche | ✅ | `feature/ap4a-zeit-search` | Suche, Pagination, Z+ Erkennung, frühes Abbruchkriterium, 68 Tests grün |
| AP4b | zeit.de Artikeldetails | ✅ | `feature/ap4b-zeit-scrape` | Autor (title-attr), Bodytext, Z+ Teaser, frischer Kontext, 75 Tests grün |
| AP4c | zeit.de Paywall-Handling | ⚠️ | `feature/ap4c-zeit-paywall` | Nicht automatisierbar — serverseitige Paywall, Teaser-Fallback bleibt |
| AP5 | Deduplizierung & CSV-Export | ✅ | `feature/ap5-dedup-csv` | Article dataclass, Dedup, CSV UTF-8, Paywall-Spalte, 92 Tests grün |
| AP6 | Verifikation | ✅ | `feature/ap6-verification` | Link-Check, Titel/Datum-Abgleich, Bericht, 102 Tests grün |
| AP7 | Gesamtlauf & Feinschliff | ✅ | `feature/ap7-polish` | Fortschritts-Logging, taz Agentur-Autoren, heise+ 0-Zeichen Fix, 103 Tests grün |

## Abhängigkeiten

```
AP1 → AP2a → AP2b ─────────────────────┐
       AP3a → AP3b → AP3c ─────────────┤
       AP4a → AP4b → AP4c ─────────────┼→ AP5 → AP6 → AP7
```

## Changelog

| Datum | AP | Änderung |
|-------|----|----------|
| 2026-03-26 | AP1 | Setup abgeschlossen, auf main committed |
| 2026-03-26 | AP2a | taz.de Suche implementiert (search.py, models.py, 17 Tests) |
| 2026-03-26 | AP2b | taz.de Artikeldetails implementiert (scrape.py, TazArticle, 7 Tests) |
| 2026-03-27 | AP3a | heise.de Suche implementiert (search.py, HeiseSearchResult, 18 Tests) |
| 2026-03-28 | AP3b | heise.de Artikeldetails implementiert (scrape.py, HeiseArticle, 7 Tests) |
| 2026-03-29 | AP4a | zeit.de Suche implementiert (search.py, ZeitSearchResult, 12 Tests) |
| 2026-03-29 | AP4b | zeit.de Artikeldetails implementiert (scrape.py, ZeitArticle, 7 Tests) |
| 2026-03-29 | AP5 | Deduplizierung & CSV-Export (dedup.py, Article, 17 Tests) |
