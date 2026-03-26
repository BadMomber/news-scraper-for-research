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
| AP2b | taz.de Artikeldetails | ⏳ | — | Autor, Volltext, Character Count |
| AP3a | heise.de Suche | ⏳ | — | |
| AP3b | heise.de Artikeldetails | ⏳ | — | |
| AP3c | heise.de Paywall-Handling | ⏳ | — | 4-Stufen-Strategie |
| AP4a | zeit.de Suche | ⏳ | — | |
| AP4b | zeit.de Artikeldetails | ⏳ | — | |
| AP4c | zeit.de Paywall-Handling | ⏳ | — | 4-Stufen-Strategie |
| AP5 | Deduplizierung & CSV-Export | ⏳ | — | |
| AP6 | Verifikation | ⏳ | — | |
| AP7 | Gesamtlauf & Feinschliff | ⏳ | — | |

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
