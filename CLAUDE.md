# News Scraper for Research

## Tech Stack

- **Language:** Python >= 3.10 (aktuell 3.12 via Nix)
- **Browser-Automation:** Playwright (Chromium headless)
- **MCP:** @playwright/mcp für interaktive Seiteninspektion durch Claude Code
- **Config:** PyYAML (seed.yaml)
- **Testing:** pytest
- **Package Manager:** Nix (flake.nix), `.venv` nur für Pakete die nicht in nixpkgs verfügbar sind

## Directory Structure
```
crawler/
├── src/
│   ├── taz/           # Alles für taz.de (Suche, Parsing, Scraping)
│   ├── heise/         # Alles für heise.de
│   ├── zeit/          # Alles für zeit.de
│   ├── dedup.py       # Deduplizierung & CSV-Export
│   ├── verify.py      # Verifikation
│   └── config.py      # seed.yaml einlesen
├── tests/
├── documentation/
│   └── specs/         # User Stories und Spezifikationen
├── main.py
├── seed.yaml          # Such-Konfiguration (Keyword-Paare, Websites, Datumsbereich)
├── flake.nix
└── pyproject.toml     # Nur Metadaten, keine Dependency-Installation
```

## Architecture

Dieses Projekt folgt einer **Feature-basierten Struktur**: Code ist nach Website organisiert, nicht nach technischer Schicht.

- Jedes Site-Modul (`taz/`, `heise/`, `zeit/`) ist eigenständig und in sich geschlossen
- Jedes Site-Modul definiert seinen eigenen Browser-Kontext, Parsing-Logik und Paywall-Behandlung
- **Kohäsion vor DRY:** Wiederholung wird bewusst akzeptiert, um Kopplung zwischen Modulen zu vermeiden
- Kein gemeinsames Basismodul für HTTP, Parsing oder Datenmodelle
- Kein `utils/` oder `common/` Paket

## Grundregeln

- **Fachliches Projektwissen nur aus dem Repository beziehen:**
  - **Erlaubt:** Dateien im Repository (Code, Dokumentation, Anforderungen, Specs)
  - **Erlaubt:** Technische Recherche aus dem Internet (Framework-Dokumentation, API-Referenzen, Best Practices)
  - **Verboten:** Fachliches Projektwissen aus früheren Gesprächen, Session-Kontext oder Kompaktierungszusammenfassungen
  - Wenn eine fachliche Information im Repository fehlt, beim Nutzer erfragen und im Repository ergänzen — bevor sie als Grundlage für Entscheidungen dient.

## Coding Conventions

### General
- **Alle Dateien enden mit einem Newline-Zeichen.** Keine Ausnahmen.
- **Code-Kommentare auf Englisch.** Variablen, Funktionen, Klassen auf Englisch. User-facing Strings (Logging, CSV-Spalten) bleiben auf Deutsch wo sinnvoll.

### Python
- Type Hints verwenden (Python 3.10+ Syntax: `list[str]` statt `List[str]`, `str | None` statt `Optional[str]`)
- `dataclass` oder einfache Dicts für Datenstrukturen — keine ORMs, keine Pydantic (unless needed)
- Keine `*args, **kwargs` Durchreichereien — explizite Parameter bevorzugen
- Kein Over-Engineering: einfache Funktionen statt Klassen, wenn kein State nötig ist

### Playwright
- Jedes Site-Modul erstellt seinen eigenen Playwright-Browser-Kontext
- Headless Chromium als Browser
- Rate-Limiting: Pause zwischen Seitenaufrufen
- Timeouts für Navigation und Selektor-Waits

## Testing Conventions

- **Framework:** pytest
- **Tests leben in `tests/`** und spiegeln die Modulstruktur
- **Fixtures:** HTML-Testdaten als Dateien in `tests/fixtures/`
- **Naming:** `test_<modul>_<was_getestet_wird>.py`
- Tests ausführen: `pytest -v`

## Dependencies verwalten

- Neue Python-Pakete werden in `flake.nix` unter `pythonPackages` hinzugefügt
- `pip install` nur für Pakete, die nicht in nixpkgs verfügbar sind (werden über `.venv` verwaltet)
- **Nicht:** `requirements.txt` oder `pip install` als primären Weg nutzen

## Documentation

- Dokumentation lebt in `documentation/`
- User Stories und Spezifikationen unter `documentation/specs/`
- `Anforderungen.md` enthält die fachlichen Anforderungen
- `AP.md` enthält die Arbeitspakete und ihren Status
