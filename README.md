# News Scraper for Research

Ein Python-Crawler, der auf **taz.de**, **zeit.de** und **heise.de** nach Artikeln zu definierten Suchbegriff-Paaren sucht. Er speichert die Ergebnisse als CSV-Tabelle und die Volltexte als einzelne Textdateien.

## Was der Crawler macht

1. **Sucht** auf drei Nachrichtenseiten nach vordefinierten Keyword-Paaren (z.B. "Grok + Hitler", "Künstliche Intelligenz + EU")
2. **Scrapt** jeden gefundenen Artikel (Titel, Autor, Datum, Volltext)
3. **Dedupliziert** — Artikel, die bei mehreren Suchbegriffen auftauchen, werden nur einmal gespeichert
4. **Filtert** — nur Artikel, in denen die Suchbegriffe auch tatsächlich im Text vorkommen, bleiben erhalten
5. **Verifiziert** — stichprobenartige Prüfung der Ergebnisse

### Ergebnisse

Nach einem Lauf gibt es:

- **`ergebnisse.csv`** — Tabelle mit allen Artikeln (Datum, Link, Titel, Autor, Suchbegriffe, Zeichenanzahl, Paywall-Status, Textdatei-Verweis)
- **`texte/`** — Ordner mit dem Volltext jedes Artikels als `.txt`-Datei

Die CSV lässt sich in Excel, Google Sheets oder LibreOffice Calc öffnen.

---

## Installation

Es gibt drei Wege, den Crawler einzurichten. Wähle den, der am besten zu deinem System passt:

### Weg 1: Docker (empfohlen fuer Einsteiger)

Docker verpackt alles (Python, Browser, Abhängigkeiten) in einen Container. Du musst nichts manuell installieren.

#### Voraussetzungen

- **Docker Desktop** installieren:
  - **macOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/) herunterladen und installieren
  - **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) herunterladen und installieren. Bei der Installation "Use WSL 2" aktivieren.

#### Schritte

1. **Repository herunterladen**

   Lade das Projekt als ZIP von GitHub herunter und entpacke es, oder nutze Git:

   ```bash
   git clone https://github.com/BadMomber/news-scraper-for-research.git
   cd news-scraper-for-research
   ```

2. **Konfiguration anlegen**

   Kopiere die Beispielkonfiguration:

   ```bash
   # macOS / Linux:
   cp seed.example.yaml seed.yaml

   # Windows (PowerShell):
   Copy-Item seed.example.yaml seed.yaml
   ```

   Passe `seed.yaml` nach Bedarf an (siehe [Konfiguration](#konfiguration)).

3. **Crawler starten**

   ```bash
   docker compose up --build
   ```

   Beim ersten Mal dauert der Build einige Minuten (Browser wird heruntergeladen). Danach startet der Crawler und die Ergebnisse landen in `ergebnisse.csv` und `texte/`.

4. **Ergebnisse ansehen**

   - `ergebnisse.csv` in Excel / Google Sheets / LibreOffice Calc öffnen
   - Textdateien liegen im Ordner `texte/`

---

### Weg 2: Python direkt installieren (macOS)

#### Voraussetzungen

- **Python 3.10 oder neuer** (empfohlen: 3.12)

  Python-Version prüfen:

  ```bash
  python3 --version
  ```

  Falls nicht installiert: [python.org/downloads](https://www.python.org/downloads/) oder via Homebrew:

  ```bash
  brew install python@3.12
  ```

#### Schritte

1. **Repository klonen**

   ```bash
   git clone https://github.com/BadMomber/news-scraper-for-research.git
   cd news-scraper-for-research
   ```

2. **Virtuelle Umgebung erstellen und Pakete installieren**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install playwright pyyaml pytest
   playwright install chromium
   ```

3. **Konfiguration anlegen**

   ```bash
   cp seed.example.yaml seed.yaml
   ```

   Passe `seed.yaml` nach Bedarf an (siehe [Konfiguration](#konfiguration)).

4. **Crawler starten**

   ```bash
   python main.py
   ```

---

### Weg 3: Python direkt installieren (Windows)

#### Voraussetzungen

- **Python 3.10 oder neuer**

  Herunterladen von [python.org/downloads](https://www.python.org/downloads/). Bei der Installation **unbedingt** den Haken bei "Add Python to PATH" setzen.

  Danach in PowerShell prüfen:

  ```powershell
  python --version
  ```

#### Schritte

1. **Repository herunterladen**

   Entweder als ZIP von GitHub herunterladen und entpacken, oder mit Git:

   ```powershell
   git clone https://github.com/BadMomber/news-scraper-for-research.git
   cd news-scraper-for-research
   ```

2. **Virtuelle Umgebung erstellen und Pakete installieren**

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install playwright pyyaml pytest
   playwright install chromium
   ```

3. **Konfiguration anlegen**

   ```powershell
   Copy-Item seed.example.yaml seed.yaml
   ```

   Passe `seed.yaml` nach Bedarf an (siehe [Konfiguration](#konfiguration)).

4. **Crawler starten**

   ```powershell
   python main.py
   ```

---

### Weg 4: Nix (fuer Entwickler)

Falls du [Nix](https://nixos.org/) mit Flakes nutzt:

```bash
nix develop
python main.py
```

---

## Konfiguration

Die Datei `seed.yaml` steuert den Crawler. Eine Vorlage liegt in `seed.example.yaml`.

### Suchbegriffe

```yaml
search_terms:
  kategorie_name:
    - ["Wort1", "Wort2"]
    - ["Wort1", "Wort3"]
```

Jedes Paar besteht aus zwei Begriffen. Der Crawler sucht auf allen Seiten nach Artikeln, die zu diesen Paaren passen.

### Zeitraum

```yaml
date_range:
  start: "2025-07-08"
  end: "2026-02-08"
```

Nur Artikel in diesem Zeitraum werden gesucht. Format: `JJJJ-MM-TT`.

### Premiumzugänge (optional)

Wenn du einen Account bei zeit.de hast, kannst du die Zugangsdaten hinterlegen. Dann werden Z+-Artikel im Volltext abgerufen statt nur als Teaser:

```yaml
credentials:
  zeit:
    username: "deine@email.de"
    password: "dein-passwort"
```

Ohne diesen Abschnitt funktioniert der Crawler trotzdem — Paywall-Artikel werden dann nur mit dem sichtbaren Teaser-Text gespeichert.

### Volltextfilter-Schwellwerte (optional)

```yaml
fulltext_filter:
  min_char_count: 2000
  min_term_occurrences: 4
```

Steuert, welche Artikel nach dem Crawlen aussortiert werden. Fehlt der Abschnitt, gelten die gezeigten Defaults. Was die Werte bedeuten und wie der Filter arbeitet, steht im Abschnitt [Der Volltextfilter](#der-volltextfilter).

**Wichtig:** `seed.yaml` enthält ggf. Passwörter und wird nicht ins Git eingecheckt (steht in `.gitignore`).

---

## Ergebnisse verstehen

### CSV-Spalten

| Spalte | Beschreibung |
|--------|-------------|
| Date | Erscheinungsdatum des Artikels |
| Link | URL zum Artikel |
| Titel | Artikeltitel |
| Autor | Autor(en) |
| Used Search Terms | Suchbegriff-Paare, die diesen Artikel gefunden haben |
| Character Count | Zeichenanzahl des gespeicherten Textes |
| Paywall | Leer, "heise+" oder "Z+" |
| Textdatei | Dateiname der zugehörigen Textdatei in `texte/` |

### Textdateien

Die Textdateien in `texte/` enthalten den Artikeltext im Klartext. Zwischenüberschriften sind mit Markdown-Syntax markiert:

```
Erster Absatz des Artikels...

## Zwischenüberschrift

Weiterer Absatz...
```

---

## Der Volltextfilter

Suchmaschinen von Nachrichtenseiten liefern auch Artikel, die die Suchbegriffe nur in Metadaten oder am Rande erwähnen. Der Volltextfilter sortiert solche Treffer nach dem Crawlen automatisch aus, damit im Ergebnis nur Artikel mit ausreichend Substanz und tatsächlichem Themenbezug landen.

### Wann läuft der Filter?

Automatisch bei jedem Gesamtlauf (`python main.py`), nach dem Scraping und vor der Verifikation. Zusätzlich kann er jederzeit eigenständig auf bereits vorhandene Ergebnisse angewendet werden, ohne neu zu crawlen:

```bash
python -m src.fulltext_filter
```

Optionen:

| Option | Beschreibung | Default |
|--------|-------------|---------|
| `--csv` | Pfad zur Ergebnis-CSV | `ergebnisse.csv` |
| `--texte` | Verzeichnis mit den Textdateien | `texte/` |
| `--seed` | Pfad zur `seed.yaml` mit den Schwellwerten | `seed.yaml` |

Existiert die `seed.yaml` nicht, laufen die Default-Schwellwerte (2000 Zeichen, 4 Treffer).

### Die drei Kriterien

Jeder Artikel wird gegen drei Kriterien geprüft. Verletzt er eines, wird er aussortiert; das erste verletzte Kriterium wird als Grund geloggt.

**1. Themenbezug:** Mindestens eines der Suchbegriff-Paare, über die der Artikel gefunden wurde, muss vollständig im Artikeltext vorkommen. Beide Wörter müssen irgendwo im Text stehen — nicht nebeneinander. Ein Artikel, der bei der Suche nach `["Grok", "Hitler"]` gefunden wurde, aber keines oder nur eines der Wörter im Text enthält, fliegt raus.

**2. Mindestlänge** (`min_char_count`, Default 2000): Artikel mit weniger Zeichen werden aussortiert — typischerweise Kurzmeldungen ohne Substanz. Grundlage ist die Spalte „Character Count" der CSV. Ein Artikel mit genau 2000 Zeichen bleibt erhalten.

**3. Mindest-Trefferzahl** (`min_term_occurrences`, Default 4): Der Artikel muss die Suchbegriffe insgesamt oft genug erwähnen. Gezählt wird die **Summe aller Vorkommen aller Suchwörter** aus den Paaren, über die der Artikel gefunden wurde:

- Jedes Vorkommen jedes Suchworts zählt einen Treffer
- Ein Wort, das in mehreren Paaren vorkommt, zählt nur einmal als Suchwort (seine Vorkommen werden nicht doppelt gezählt)
- Ein Artikel mit genau 4 Treffern bleibt erhalten

Beispiel: Ein Artikel wurde über das Paar `["Grok", "Hitler"]` gefunden. Im Text steht 3× „Grok" und 2× „Hitler" → 5 Treffer → der Artikel bleibt. Stünde dort nur 2× „Grok" und 1× „Hitler", wären es 3 Treffer → der Artikel wird aussortiert.

Die Suche ist in allen Kriterien **case-insensitive**, und Teilwörter zählen: „Groks Antwort" enthält „Grok".

### Was mit aussortierten Artikeln passiert

Aussortierte Artikel werden **aus der CSV entfernt und ihre Textdatei in `texte/` gelöscht**. Der Filter legt kein Backup an — wer die ungefilterten Daten behalten will, kopiert `ergebnisse.csv` und `texte/` vorher weg. Jeder entfernte Artikel wird mit Titel und Grund geloggt, am Ende steht eine Zusammenfassung:

```
INFO src.fulltext_filter: Volltextfilter: Kriterien min. 2000 Zeichen, min. 4 Suchbegriff-Treffer
INFO src.fulltext_filter: Volltextfilter: 390 Artikel → 282 behalten, 108 entfernt
INFO src.fulltext_filter:   Entfernt (unter 2000 Zeichen (948)): Beispiel-Titel ...
INFO src.fulltext_filter:   Entfernt (weniger als 4 Suchbegriff-Treffer (2)): Anderer Titel ...
```

### Bekannte Grenzen

- **Paywall-Teaser:** Konnte nur der Teaser statt des Volltexts geladen werden (kein Premiumzugang konfiguriert), greifen die Kriterien auf dem Teaser — lange Paywall-Artikel können dadurch an der Mindestlänge scheitern.
- **Abkürzungen und Synonyme:** Gezählt wird nur das wörtliche Suchwort. Ein Artikel, der durchgehend „KI" statt „Künstliche Intelligenz" schreibt, erreicht die Trefferzahl für das ausgeschriebene Suchwort nicht.

---

## Laufzeit und Hinweise

- Ein kompletter Lauf mit 17 Keyword-Paaren auf 3 Seiten dauert je nach Internetverbindung **30-60 Minuten**
- Der Crawler speichert Ergebnisse **inkrementell** — bei einem Abbruch bleiben die bisherigen Daten erhalten
- Zwischen Seitenaufrufen werden Pausen eingehalten, um die Nachrichtenseiten nicht zu überlasten
- Der zeit.de-Login (falls konfiguriert) dauert beim Start ca. 45 Sekunden (Captcha-Lösung)

---

## Fehlerbehebung

### "playwright install chromium" schlaegt fehl

Playwright braucht einen Browser. Falls der automatische Download nicht klappt:

```bash
# macOS: System-Abhängigkeiten installieren
playwright install-deps chromium
playwright install chromium

# Windows: Als Administrator in PowerShell ausfuehren
playwright install chromium
```

### Crawler bricht ab mit Timeout-Fehlern

Die Nachrichtenseiten können bei vielen Anfragen langsam reagieren. Der Crawler wiederholt fehlgeschlagene Aufrufe automatisch (bis zu 3x). Falls es trotzdem abbricht: einfach nochmal starten — die bisherigen Ergebnisse bleiben erhalten.

### CSV zeigt Sonderzeichen falsch an (Excel)

Die CSV ist UTF-8-kodiert. In Excel:

1. Datei > Öffnen > Datei auswählen
2. Im Importassistenten "Unicode (UTF-8)" als Zeichensatz wählen
3. Trennzeichen: Komma

Oder: Die Datei in **Google Sheets** oder **LibreOffice Calc** öffnen — dort funktioniert UTF-8 automatisch.

---

## Projektstruktur

```
news-scraper-for-research/
├── main.py                # Einstiegspunkt — startet den Crawler
├── seed.yaml              # Konfiguration (nicht im Git)
├── seed.example.yaml      # Konfigurations-Vorlage
├── ergebnisse.csv         # Ergebnis-Tabelle (wird erzeugt)
├── texte/                 # Volltexte der Artikel (wird erzeugt)
├── src/
│   ├── taz/               # taz.de — Suche und Scraping
│   ├── heise/             # heise.de — Suche und Scraping
│   ├── zeit/              # zeit.de — Suche, Scraping und Login
│   ├── config.py          # Liest seed.yaml ein
│   ├── dedup.py           # Deduplizierung, CSV-Export, Textdatei-Speicherung
│   ├── fulltext_filter.py # Volltextfilter
│   └── verify.py          # Ergebnis-Verifikation
├── tests/                 # Automatische Tests
├── documentation/         # Spezifikationen und Pläne
├── Dockerfile             # Docker-Container-Definition
├── docker-compose.yml     # Docker Compose Konfiguration
├── flake.nix              # Nix-Entwicklungsumgebung
└── pyproject.toml         # Python-Projektmetadaten
```

## Tests ausfuehren

```bash
pytest -v
```
