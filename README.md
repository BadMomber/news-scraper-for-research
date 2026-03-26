# Marianne Crawler

Python-Crawler, der auf taz.de, zeit.de und heise.de nach Artikeln sucht, die zu definierten Keyword-Paaren passen, und die Ergebnisse als deduplizierte CSV ausgibt.

## Setup

```bash
nix develop
```

Das startet eine Shell mit Python 3.12 und allen Abhängigkeiten (httpx, beautifulsoup4, lxml, pyyaml, pytest).

## Ausführen

```bash
python main.py
```

## Tests

```bash
pytest -v
```

## Konfiguration

Die Suchkonfiguration liegt in `seed.yaml`:
- **search_terms** — 17 Keyword-Paare in 3 Kategorien
- **target_sites** — taz.de, zeit.de, heise.de
- **date_range** — Zeitraum für die Artikelsuche

## Projektstruktur

```
src/
├── taz/           # taz.de Crawler
├── heise/         # heise.de Crawler
├── zeit/          # zeit.de Crawler
├── dedup.py       # Deduplizierung & CSV-Export
├── verify.py      # Verifikation
└── config.py      # seed.yaml einlesen
tests/             # pytest Tests
main.py            # Einstiegspunkt
seed.yaml          # Suchkonfiguration
```
