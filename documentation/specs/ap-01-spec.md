# Spezifikation: AP1 – Projektstruktur & Setup

## Ziel

Die technische Basis des Crawlers aufsetzen: Abhängigkeiten, Projektstruktur, Konfiguration und eine gemeinsame HTTP-Session. Nach Abschluss von AP1 kann sofort mit der Implementierung der site-spezifischen Crawler (AP2–AP4) begonnen werden.

## Anforderungen

### Projektsetup

- **Nix** verwaltet die Entwicklungsumgebung über `flake.nix` (Python 3.12, System-Pakete)
- Die `flake.nix` wird um fehlende Pakete erweitert: `httpx`, `pyyaml`, `pytest`
- `requests` kann entfernt werden (wird durch `httpx` ersetzt)
- `.venv` mit `--system-site-packages` bleibt für Pakete, die nicht in nixpkgs verfügbar sind
- `pyproject.toml` für Projekt-Metadaten (Name, Version, Python-Version) — nicht für Dependency-Installation, das übernimmt Nix

### Konfiguration (seed.yaml)

- Die `seed.yaml` wird zur reinen Such-Konfigurationsdatei bereinigt
- Sie enthält nur noch: Suchbegriff-Paare (mit Kategorien), Ziel-Websites, Datumsbereich
- Alle Ouroboros-spezifischen Felder werden entfernt (ontology_schema, evaluation_principles, exit_conditions, metadata, goal, constraints, acceptance_criteria)
- Die Konfiguration wird beim Start eingelesen und als Datenstruktur bereitgestellt

### Projektstruktur (Feature-basiert)

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
├── main.py
├── seed.yaml
├── flake.nix
├── flake.lock
└── pyproject.toml
```

- Jedes Site-Modul ist eigenständig und in sich geschlossen
- Wiederholung wird bewusst akzeptiert — Kohäsion vor Kopplung
- Kein gemeinsames Basismodul für HTTP oder Parsing; jedes Site-Modul definiert seine eigene HTTP-Session und Parsing-Logik

### HTTP-Grundlagen (pro Site-Modul)

- Jedes Site-Modul erstellt seinen eigenen `httpx.Client` mit:
  - User-Agent (realistischer Browser-String)
  - `Referer: https://www.google.com/` (für Paywall-Umgehung)
  - Timeouts (Connect + Read)
- Rate-Limiting: Pause zwischen Requests (konfigurierbar, z.B. 1–2 Sekunden)

## Akzeptanzkriterien

- [ ] `flake.nix` enthält alle benötigten Python-Pakete (httpx, beautifulsoup4, lxml, pyyaml, pytest)
- [ ] `nix develop` startet eine Shell mit funktionierender Python-Umgebung
- [ ] `seed.yaml` enthält nur Such-Konfiguration (keine Ouroboros-Felder)
- [ ] `python -c "from src.config import load_config; load_config()"` lädt die Konfiguration fehlerfrei
- [ ] Die geladene Konfiguration enthält alle 17 Keyword-Paare, 3 Websites und den Datumsbereich
- [ ] `pytest` läuft und findet Tests (mindestens ein Basis-Test für config)
- [ ] Projektstruktur ist Feature-basiert angelegt (ein Verzeichnis pro Site)

## Abgrenzung

- Kein Crawling-Code — das ist Aufgabe von AP2–AP4
- Keine Deduplizierung oder CSV-Export — das ist AP5
- Keine Verifikation — das ist AP6
- Die Site-Module werden als leere Pakete angelegt (nur `__init__.py`), der eigentliche Code folgt in AP2–AP4

## Abhängigkeiten

- **Voraussetzungen:** Keine (AP1 ist der Startpunkt)
- **Nachfolger:** AP2, AP3, AP4 setzen die hier geschaffene Struktur und Konfiguration voraus
