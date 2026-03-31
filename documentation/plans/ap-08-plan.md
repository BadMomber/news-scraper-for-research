# Plan: AP8 — Inkrementelle CSV & Volltext-Speicherung

## Kontext

Zwei Änderungen: (1) CSV wird nach jedem Keyword-Paar aktualisiert statt erst am Ende, (2) Artikeltext wird als separate Textdatei gespeichert.

## Entscheidungen

- **Textdateien** in `texte/` Verzeichnis, Dateiname = URL-basierter Slug
- **CSV-Spalte "Textdatei"** verweist auf den Dateinamen
- **body_text** als neues Feld in allen Article-Dataclasses
- **IncrementalWriter** Klasse in `src/dedup.py` die CSV + Textdateien inkrementell schreibt
- **Dedup** läuft über einen In-Memory-Index (dict by title) der parallel zur CSV geführt wird

---

## Schritt 1: Dataclasses erweitern

Neues Feld `body_text: str` in:
- `TazArticle`, `HeiseArticle`, `ZeitArticle`
- `Article` (gemeinsame Datenstruktur)

Scrape-Funktionen speichern `body_text` statt es zu verwerfen.

## Schritt 2: Textdatei-Speicherung

Neue Funktion `_save_text_file(texte_dir, url, text) -> str`:
- Erzeugt einen Dateinamen aus der URL (Slug)
- Schreibt Text als UTF-8 `.txt` Datei
- Gibt den Dateinamen zurück

## Schritt 3: IncrementalWriter

Neue Klasse in `src/dedup.py`:

```python
class IncrementalWriter:
    def __init__(self, csv_path, texte_dir):
        # Erstellt CSV mit Header, erstellt texte/ Verzeichnis

    def add_articles(self, articles: list[Article]):
        # Dedup gegen bisherige Artikel
        # Neue Artikel: Textdatei schreiben, CSV-Zeile anhängen
        # Duplikate: search_terms im Memory-Index mergen, CSV neu schreiben
```

CSV wird bei Duplikaten komplett neu geschrieben (weil sich search_terms bestehender Zeilen ändern).

## Schritt 4: main.py anpassen

Statt am Ende `to_articles() → deduplicate() → export_csv()`:
- `IncrementalWriter` am Anfang erstellen
- Nach jedem `scrape_fn()` Aufruf → `writer.add_articles()`

## Schritt 5: Tests

- Textdatei-Erzeugung und Slug-Generierung
- IncrementalWriter: inkrementelles Schreiben, Dedup, CSV-Validität
- Integration: nach 2 Blöcken korrekte CSV + Textdateien

---

## Dateien-Übersicht

### Geänderte Dateien
| Datei | Änderung |
|-------|----------|
| `src/taz/models.py` | `body_text` Feld |
| `src/heise/models.py` | `body_text` Feld |
| `src/zeit/models.py` | `body_text` Feld |
| `src/taz/scrape.py` | `body_text` speichern |
| `src/heise/scrape.py` | `body_text` speichern |
| `src/zeit/scrape.py` | `body_text` speichern |
| `src/dedup.py` | `Article.body_text`, `IncrementalWriter`, Textdatei-Logic |
| `main.py` | IncrementalWriter nutzen |
| `tests/test_dedup.py` | Tests für IncrementalWriter |
