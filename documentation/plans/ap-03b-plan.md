# Plan: AP3b — heise.de Artikeldetails

## Kontext

AP3b extrahiert Autor und Volltext von heise.de-Artikelseiten. Bei heise+ Artikeln ist nur der Teaser sichtbar — der Artikel wird trotzdem erfasst mit reduziertem Character Count. Die Paywall-Umgehung folgt in AP3c.

## Entscheidungen

- **Autor**: Aus `a[href*='/autor/']` oder Fallback `meta[name=author]`. Bei heise+ leer (Autor nicht auf Teaser-Seite verfügbar).
- **Artikeltext**: Aus `article p` (alle Absätze im article-Element)
- **heise+ Erkennung**: Via `is_heise_plus` Flag aus AP3a (URL-basiert)
- **Navigation**: `domcontentloaded` statt `networkidle` (Tracker-Timeouts)
- **Datenstruktur**: `HeiseArticle` dataclass analog zu `TazArticle`

---

## Schritt 1: Datenstruktur

**Datei:** `src/heise/models.py`

```python
@dataclass
class HeiseArticle:
    date: date
    url: str
    title: str
    author: str
    char_count: int
    search_terms: str
    is_heise_plus: bool
```

## Schritt 2: Scraping-Modul

**Datei:** `src/heise/scrape.py`

- `scrape_articles(browser, results, keyword_pair) -> list[HeiseArticle]`
- `_extract_author(page) -> str` — `a[href*='/autor/']`, Fallback `meta[name=author]`
- `_extract_body_text(page) -> str` — `article p` Absätze
- Cookie-Banner einmalig wegklicken
- Retry + Rate-Limiting wie bei search.py

## Schritt 3: Tests + Fixtures + Smoke Test

## Schritt 4: main.py erweitern

---

## Dateien-Übersicht

### Neue Dateien
| Datei | Beschreibung |
|-------|-------------|
| `src/heise/scrape.py` | Artikeldetails extrahieren |
| `tests/test_heise_scrape.py` | Unit-Tests |
| `tests/fixtures/heise_article.html` | Fixture: freier Artikel |
| `tests/fixtures/heise_article_plus.html` | Fixture: heise+ Artikel |

### Geänderte Dateien
| Datei | Änderung |
|-------|----------|
| `src/heise/models.py` | `HeiseArticle` dataclass |
| `src/heise/__init__.py` | Neue Exports |
| `main.py` | heise.de Scraping integrieren |
