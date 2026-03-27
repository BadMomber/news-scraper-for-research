# Plan: AP3a — heise.de Suche

## Kontext

AP3a implementiert die automatische Suche auf heise.de für alle 17 Keyword-Paare. heise.de ist eine React-App mit serverseitig gerendertem Content. Die Suche liefert ISO-8601-Datumsformat via `<time datetime>`, Pagination via `?p=N` URL-Parameter. Cookie-Banner muss einmalig weggeklickt werden.

## Entscheidungen

- **Cookie-Banner**: Einmalig "Agree" klicken beim Erstellen des Browser-Kontexts
- **Datumsformat**: ISO 8601 aus `<time datetime="...">` — parsen mit `date.fromisoformat()`
- **Frühes Abbruchkriterium**: Ergebnisse sind nach Datum sortiert (`sort_by=date`). Sobald alle Ergebnisse auf einer Seite außerhalb des Zeitraums liegen → Pagination stoppen. Das verhindert unnötiges Paginieren durch tausende Ergebnisse.
- **heise+ Erkennung**: Artikel mit `/select/` in der URL werden als `is_heise_plus=True` markiert
- **Retry/Rate-Limiting**: Wie bei taz.de — 5s/15s/45s Backoff, 2s Pause

---

## Schritt 1: Datenstruktur

**Datei:** `src/heise/models.py`

```python
@dataclass
class HeiseSearchResult:
    title: str
    url: str
    date: date
    is_heise_plus: bool
```

---

## Schritt 2: Suchfunktion

**Datei:** `src/heise/search.py`

### URL-Schema

```
https://www.heise.de/suche/?q={encoded_query}&sort_by=date
https://www.heise.de/suche/?q={encoded_query}&sort_by=date&p=2  (Seite 2)
```

### `search(browser, keyword_pair, date_start, date_end) -> list[HeiseSearchResult]`

1. Browser-Kontext erstellen, Cookie-Banner wegklicken
2. Suchbegriffe mit `+` verknüpfen, URL-encoden
3. Erste Seite laden, Ergebnisse parsen
4. Pagination: `p=2`, `p=3`, ... solange Ergebnisse vorhanden
5. **Frühes Abbruchkriterium**: Wenn alle Artikel einer Seite VOR dem Zeitraum liegen → Stop
6. Nach Datum filtern und zurückgeben

### `_dismiss_cookie_banner(page)`

"Agree"-Button suchen und klicken. Einmal pro Kontext.

### `_parse_results_page(page) -> list[HeiseSearchResult]`

Für jedes `<article>` Element:
- Titel aus `<h2>` oder `<h3>`
- Link aus `<a href="...">` (zu absoluter URL vervollständigen)
- Datum aus `<time datetime="...">` (ISO 8601 → `date`)
- heise+ aus `/select/` in der URL

### `_navigate_with_retry(page, url)`

Eigene Kopie (Kohäsion vor DRY, gemäß Architekturprinzip).

### Frühes Abbruchkriterium (Detail)

Da `sort_by=date` die neuesten Ergebnisse zuerst zeigt:
- Ergebnisse einer Seite parsen
- Wenn das **älteste** Datum auf der Seite VOR `date_start` liegt: Diese Seite ist die letzte (filtern, dann stoppen)
- Wenn ALLE Artikel NACH `date_end` liegen: weiter paginieren (noch nicht im Zeitraum)

---

## Schritt 3: Tests

**Datei:** `tests/test_heise_search.py`

- `test_parse_results_page` — Fixture mit typischen Ergebnissen
- `test_parse_results_page_empty` — Leere Ergebnisseite
- `test_parse_date_iso` — ISO 8601 Datum korrekt geparst
- `test_heise_plus_detection` — `/select/` URLs werden erkannt
- `test_date_filter` — Ergebnisse außerhalb des Datumsbereichs gefiltert
- `test_build_absolute_url` — Relative URLs korrekt ergänzt

### Fixtures

**Datei:** `tests/fixtures/heise_search_results.html`
**Datei:** `tests/fixtures/heise_search_empty.html`

---

## Schritt 4: Smoke Test

Live-Test gegen heise.de mit 2–3 Keyword-Paaren. Prüft:
- Werden Ergebnisse gefunden?
- Funktioniert das frühe Abbruchkriterium?
- Sind Titel, URLs, Daten plausibel?
- Werden heise+ Artikel korrekt markiert?

---

## Schritt 5: Module exportieren und main.py erweitern

**Datei:** `src/heise/__init__.py` — Exports
**Datei:** `main.py` — heise.de Suche nach taz.de integrieren

---

## Dateien-Übersicht

### Neue Dateien
| Datei | Beschreibung |
|-------|-------------|
| `src/heise/models.py` | `HeiseSearchResult` dataclass |
| `src/heise/search.py` | Suchfunktion mit Pagination, Cookie-Banner, frühes Abbruchkriterium |
| `tests/test_heise_search.py` | Unit-Tests |
| `tests/fixtures/heise_search_results.html` | HTML-Fixture |
| `tests/fixtures/heise_search_empty.html` | HTML-Fixture (leer) |

### Geänderte Dateien
| Datei | Änderung |
|-------|----------|
| `src/heise/__init__.py` | Exports hinzufügen |
| `main.py` | heise.de Suche integrieren |
