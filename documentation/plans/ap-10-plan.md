# Plan: AP10 — Volltextfilter

## Kontext

Nachgelagerter Filter: Prüft ob die Suchbegriffe tatsächlich im Artikeltext vorkommen. Entfernt irrelevante Treffer aus CSV und löscht deren Textdateien.

## Entscheidungen

- **Eigenes Modul** `src/fulltext_filter.py` — keine Erweiterung von dedup.py
- **Arbeitet auf Dateien**: Liest CSV + Textdateien, schreibt bereinigte CSV, löscht Textdateien
- **Läuft nach Scraping/Dedup, vor Verifikation**
- **Case-insensitive**, exakte Wortsuche (kein Stemming, kein Fuzzy)

---

## Schritt 1: Filterlogik

`src/fulltext_filter.py`:

```python
def _keyword_pair_matches(text: str, keyword_pair: str) -> bool:
    """Check if both words of a keyword pair appear in text (case-insensitive).

    keyword_pair format: "Grok+Hitler"
    """

def filter_articles(csv_path: Path, texte_dir: Path) -> FilterResult:
    """Read CSV, check each article's text file, remove non-matching articles."""
```

Ablauf von `filter_articles()`:
1. CSV einlesen
2. Für jeden Artikel:
   - Textdatei lesen
   - "Used Search Terms" parsen (kann mehrere Paare enthalten, getrennt durch "; ")
   - Prüfen ob **mindestens ein** Paar matcht (beide Wörter im Text)
   - Beim ersten Match abbrechen (Short-Circuit)
3. Nicht-matchende Artikel: Textdatei löschen
4. Bereinigte CSV schreiben (alle Spalten, nur matchende Artikel)
5. Ergebnis loggen

## Schritt 2: FilterResult Dataclass

```python
@dataclass
class FilterResult:
    total: int          # Artikel vor Filter
    kept: int           # Artikel nach Filter
    removed: int        # Entfernte Artikel
    removed_titles: list[str]  # Titel der entfernten Artikel (für Log)
```

## Schritt 3: main.py einbinden

Zwischen IncrementalWriter und Verifikation:

```python
# --- Volltextfilter ---
filter_result = filter_articles(csv_path, texte_dir)
# Log output...

# --- Verifikation ---
verification = await verify_csv(browser, csv_path)
```

## Schritt 4: Tests

- Artikel mit beiden Wörtern → bleibt
- Artikel mit nur einem Wort → wird entfernt
- Case-insensitive: "grok" matcht "Grok"
- Mehrere Keyword-Paare: ein Match reicht
- Textdatei wird bei Entfernung gelöscht
- CSV nach Filter ist valide
- Leere CSV (kein Artikel matcht) → nur Header bleibt

---

## Dateien-Übersicht

| Datei | Änderung |
|-------|----------|
| `src/fulltext_filter.py` | Neues Modul: `filter_articles()`, `FilterResult` |
| `main.py` | Filter zwischen Scraping und Verifikation einbinden |
| `tests/test_fulltext_filter.py` | Tests für Filterlogik |
