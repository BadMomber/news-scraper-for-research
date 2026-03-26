---
name: implementation-writer
description: "Setzt ein Arbeitspaket gemäß Implementierungsplan um: Implementierung, Tests, Verifikation und Dokumentations-Update"
---

# /implementation-writer

Setzt ein Arbeitspaket vollständig um — von der Implementierung über Tests bis zur Verifikation. Der Skill bildet den Entwicklungs-Workflow ab.

## Usage

```
/implementation-writer [AP-Nummer]
```

Beispiel: `/implementation-writer AP2`

## Voraussetzungen

Vor der Implementierung müssen folgende Dokumente existieren:

1. **Anforderungen.md** — Fachliche Anforderungen
2. **AP.md** — Arbeitspakete
3. **Implementierungsplan** (`documentation/plans/ap-NN-plan.md`)

Falls der Implementierungsplan fehlt, empfehle `/implementation-plan` auszuführen.

## Instructions

### Phase 1: Kontext laden

Lies folgende Dateien:
- **Anforderungen.md**, **AP.md** und den **Implementierungsplan**
- Falls vorhanden: `CLAUDE.md` für Coding Conventions
- Bestehende Implementierungen, die im Plan als Referenz genannt werden
- Alle Dateien, die laut Plan geändert werden sollen

### Phase 2: Implementierung

Setze den Plan Schritt für Schritt um:

1. **Gemeinsame Basis** (Config, HTTP-Session, Datenmodelle)
2. **Site-spezifischer Code** (Suche, Parsing, Pagination)
3. **Paywall-Handling** (Stufen-Strategie)
4. **Datenverarbeitung** (Deduplizierung, CSV-Export)
5. **Verifikation** (Link-Check, Metadaten-Abgleich)

**Inkrementelle Verifikation:** Nach jeder logisch abgeschlossenen Phase prüfen:
- `python -m py_compile [datei]` — Syntax-Check
- `pytest [test-datei]` — Zugehörige Tests ausführen

### Phase 3: Tests implementieren

Implementiere Tests mit pytest:

- **Unit Tests** für Parsing-Logik, Deduplizierung, CSV-Formatierung
- **Integration Tests** für HTTP-Requests gegen die echten Suchseiten (mit Fixtures/Mocks für CI)
- **Smoke Tests** für einen vollständigen Durchlauf mit 1-2 Keyword-Paaren

Tests liegen in `tests/` und spiegeln die Modulstruktur.

**Vollständigkeits-Check:**
- [ ] Jedes Parsing-Modul hat Tests für gültige und ungültige Eingaben
- [ ] Deduplizierungslogik hat Tests für Duplikate und Nicht-Duplikate
- [ ] CSV-Export hat Tests für UTF-8, Semikolon-Trennung in Used Search Terms
- [ ] Paywall-Fallback hat Tests für jede Stufe

### Phase 4: Smoke Test

Führe einen Live-Test gegen die echte Zielseite durch:

1. Erstelle ein temporäres Smoke-Test-Skript (nicht committen)
2. Teste mit 2–3 Keyword-Paaren aus der Konfiguration
3. Prüfe: Werden Ergebnisse gefunden? Sind Titel, URLs und Daten plausibel?
4. Falls der Smoke Test fehlschlägt: Parser/Selektoren gegen die echte DOM-Struktur korrigieren, Unit-Tests und Fixtures anpassen, erneut testen
5. Lösche das Smoke-Test-Skript nach erfolgreicher Verifikation

Der Smoke Test ist Pflicht — Unit-Tests mit Fixtures allein reichen nicht, da sich HTML-Strukturen der Zielseiten von den Fixtures unterscheiden können.

### Phase 5: Verifikation

Gleiche die Implementierung gegen Anforderungen.md ab:

1. Sind alle geforderten CSV-Spalten vorhanden?
2. Funktioniert die Deduplizierung korrekt?
3. Werden alle Keyword-Paare für die betroffene Site durchsucht?
4. Ist die UTF-8-Kodierung korrekt?

Führe alle Tests aus und bestätige, dass sie grün sind:
```bash
pytest -v
```

### Phase 6: Code Review

Führe den `/simplify` Skill aus. Behebe relevante Findings.

### Phase 7: AP.md aktualisieren

Markiere die erledigten Aufgaben im Arbeitspaket in `AP.md` mit `[x]`.

## Verhaltensregeln

- **Inkrementell verifizieren:** Nach jeder Phase testen, nicht erst am Ende.
- **Tests sind Teil der Implementierung:** Kein Arbeitspaket ist "fertig" ohne grüne Tests.
- **Keine stillen Abweichungen:** Jede Abweichung vom Plan wird dokumentiert und begründet.
- **Bestehende Patterns respektieren:** Neue Dateien orientieren sich am Stil vorhandener Dateien.
- **Robustheit:** HTTP-Requests mit Timeouts, Retries und sinnvollen Fehlermeldungen.
