# Plan: AP9 — Premiumzugänge für Paywall-Artikel

## Kontext

Credentials für heise.de und zeit.de in `seed.yaml`, Login einmal pro Seite, Fallback auf Teaser-Text.

## Entscheidungen

- **Credentials in `seed.yaml`** unter `credentials:` (optional)
- **Login-Funktionen** als eigene Funktionen in den jeweiligen Site-Modulen (`heise/scrape.py`, `zeit/scrape.py`)
- **zeit.de Kontextwechsel**: Mit Credentials ein gemeinsamer eingeloggter Kontext statt frischem Kontext pro Artikel. Ohne Credentials bleibt das bisherige Verhalten (fresh context per article).
- **heise.de**: Bereits ein Kontext — Login am Anfang, dann weiter wie bisher
- **Credentials-Dataclass** in `config.py` mit optionalen Feldern

---

## Schritt 1: Config erweitern

`src/config.py`:
- Neue Dataclass `SiteCredentials` mit `username: str`, `password: str`
- `SearchConfig` bekommt `credentials: dict[str, SiteCredentials]` (Default: leer)
- `load_config()` liest optionalen `credentials`-Block aus seed.yaml

`seed.yaml` Beispiel:
```yaml
credentials:
  heise:
    username: "user@example.com"
    password: "geheim"
  zeit:
    username: "user@example.com"
    password: "geheim"
```

## Schritt 2: heise.de Login

`src/heise/scrape.py`:
- Neue Funktion `_login(page, username, password) -> bool`
  - Navigiert zur heise.de Login-Seite
  - Füllt Username + Passwort aus, klickt Login
  - Wartet auf Bestätigung (z.B. Profillink oder Cookie)
  - Gibt `True` bei Erfolg zurück, `False` bei Fehler
- `scrape_articles()` bekommt optionalen Parameter `credentials: SiteCredentials | None`
  - Wenn vorhanden: Login am Anfang des Kontexts
  - Bei Fehler: Warnung loggen, weiter ohne Login

## Schritt 3: zeit.de Login

`src/zeit/scrape.py`:
- Neue Funktion `_login(page, username, password) -> bool`
  - Navigiert zur zeit.de Login-Seite
  - Füllt Username + Passwort aus, klickt Login
  - Wartet auf Bestätigung
  - Gibt `True` bei Erfolg zurück, `False` bei Fehler
- `scrape_articles()` bekommt optionalen Parameter `credentials: SiteCredentials | None`
  - **Mit Credentials**: Ein gemeinsamer Kontext (eingeloggt) für alle Artikel
  - **Ohne Credentials**: Bisheriges Verhalten (fresh context per article)

## Schritt 4: main.py anpassen

- `_search_and_scrape()` bekommt `credentials`-Parameter
- Wird aus `config.credentials` für die jeweilige Seite ausgelesen
- Durchgereicht an `scrape_fn()`

## Schritt 5: Login-Flows ermitteln (Recherche)

Für heise.de und zeit.de muss der tatsächliche Login-Flow per Playwright-Inspektion ermittelt werden:
- Login-URL
- Formular-Selektoren (Username, Passwort, Submit-Button)
- Erfolgs-Indikator (z.B. Profillink, Cookie, Redirect)
- Cookie-Banner-Interaktion beim Login

**Dieser Schritt erfordert interaktive Recherche mit dem Browser.**

## Schritt 6: Tests

- Config: Credentials werden korrekt aus seed.yaml gelesen
- Config: Fehlende Credentials → leeres Dict
- Login-Funktionen: Werden mit korrekten Selektoren aufgerufen (Playwright-Mock)
- Scrape mit Credentials: Login wird aufgerufen
- Scrape ohne Credentials: Login wird nicht aufgerufen

---

## Dateien-Übersicht

| Datei | Änderung |
|-------|----------|
| `src/config.py` | `SiteCredentials`, `credentials` in `SearchConfig` |
| `seed.yaml` | Beispiel `credentials`-Block (auskommentiert) |
| `src/heise/scrape.py` | `_login()`, `credentials`-Parameter |
| `src/zeit/scrape.py` | `_login()`, Kontext-Logik, `credentials`-Parameter |
| `main.py` | Credentials durchreichen |
| `tests/test_config.py` | Credentials-Tests |

## Risiken

- Login-Flows können sich ändern (Website-Updates)
- Cookie-Banner-Interaktion beim Login-Flow unklar
- zeit.de Metered Paywall vs. harter Z+-Paywall — Login löst beides?
