# Plan: AP5 — Deduplizierung & CSV-Export

## Kontext

AP5 führt alle Ergebnisse aus taz.de, heise.de und zeit.de zusammen, dedupliziert über Artikeltitel und exportiert als UTF-8 CSV.

## Entscheidungen

- **Gemeinsame Datenstruktur**: `Article` dataclass in `src/dedup.py`
- **search_terms als list[str]**: Ermöglicht einfaches Mergen bei Dedup, erst beim Export als "; "-getrennt
- **Paywall-Spalte**: "", "heise+", "Z+"
- **CSV-Dateiname**: `ergebnisse.csv`
- **Keine `to_article()` in Site-Modulen**: Konvertierung in `dedup.py` (hält Site-Module sauber)

## Dateien

| Neu | Beschreibung |
|-----|-------------|
| `src/dedup.py` | `Article` dataclass, `deduplicate()`, `to_articles()`, `export_csv()` |
| `tests/test_dedup.py` | Unit-Tests |

| Geändert | Änderung |
|----------|----------|
| `main.py` | Dedup + CSV-Export integrieren |
