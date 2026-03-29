# Plan: AP4a — zeit.de Suche

## Kontext

AP4a implementiert die Suche auf zeit.de. Folgt dem bewährten Pattern aus heise.de (AP3a).

## Entscheidungen

- **URL**: `https://www.zeit.de/suche/index?q=QUERY&sort=publishedDate&type=article&p=N`
- **Begriffe mit Leerzeichen** verknüpfen (wie heise.de)
- **10 Ergebnisse pro Seite**, Pagination via `p=N`
- **Datum**: ISO 8601 aus `<time datetime="...">`
- **Z+ Erkennung**: `zon-teaser-premium` oder `zplus` im article HTML
- **Frühes Abbruchkriterium**: Stop wenn ältester Artikel vor `date_start`
- **Cookie-Banner**: `[data-testid='uc-accept-all-button']` oder `button:has-text('Akzeptieren')`

## Dateien

| Neu | Beschreibung |
|-----|-------------|
| `src/zeit/models.py` | `ZeitSearchResult` (title, url, date, is_zplus) |
| `src/zeit/search.py` | Suchfunktion |
| `tests/test_zeit_search.py` | Unit-Tests |
| `tests/fixtures/zeit_search_results.html` | Fixture |
| `tests/fixtures/zeit_search_empty.html` | Fixture |

| Geändert | Änderung |
|----------|----------|
| `src/zeit/__init__.py` | Exports |
| `main.py` | zeit.de Suche integrieren |
