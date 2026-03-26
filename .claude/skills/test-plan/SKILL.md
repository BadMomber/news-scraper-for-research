---
name: test-plan
description: "Leitet aus einer AP-Spezifikation einen technischen Testplan für den Crawler ab"
---

# /test-plan

Erstellt einen technischen Testplan aus einer AP-Spezifikation. Der Testplan definiert verhaltensbasierte, implementierbare Tests — gruppiert nach fachlichen Bereichen.

## Usage

```
/test-plan [AP-Nummer]
```

Beispiel: `/test-plan AP2`

## Instructions

### Schritt 1: Spezifikation lesen

Lies die referenzierte Spezifikation unter `documentation/specs/`. Identifiziere:
- Die Akzeptanzkriterien (was muss funktionieren?)
- Die Abgrenzung (was wird nicht getestet?)

Falls keine Spezifikation existiert, empfehle `/story-writer` auszuführen.

### Schritt 2: Bestehenden Code analysieren

Untersuche den bestehenden Code:
- Welche Module und Funktionen sind betroffen?
- Welche Test-Patterns werden im Projekt bereits verwendet?
- Falls vorhanden: `CLAUDE.md` für Testing Conventions

### Schritt 3: Rückfragen klären

Stelle gezielte Rückfragen:
- Sollen HTTP-Requests in Tests gemockt oder gegen echte Seiten ausgeführt werden?
- Gibt es Testdaten (HTML-Fixtures) die erstellt werden müssen?
- Soll es Smoke Tests gegen die echten Seiten geben?

### Schritt 4: Testplan erstellen

Erstelle den Testplan als Markdown-Datei unter `documentation/specs/` mit dem Suffix `-testplan.md` (z.B. `ap-02-testplan.md`).

Format:

```markdown
# Technischer Testplan: [AP-Titel]

Abgeleitet aus [Link zur Spezifikation].

## [Fachlicher Bereich 1: z.B. Suchfunktion]

| Test | Beschreibung | Erwartung |
|------|-------------|-----------|
| [Kurztitel] | [Was wird getestet, welcher Input] | [Erwartetes Ergebnis] |

## [Fachlicher Bereich 2: z.B. Artikel-Parsing]

| Test | Beschreibung | Erwartung |
|------|-------------|-----------|
| [Kurztitel] | [Was wird getestet] | [Erwartetes Ergebnis] |

## [Fachlicher Bereich 3: z.B. Paywall-Handling]

| Test | Beschreibung | Erwartung |
|------|-------------|-----------|
| [Kurztitel] | [Was wird getestet] | [Erwartetes Ergebnis] |

## Smoke Tests (gegen echte Seiten)

| Test | Beschreibung | Erwartung |
|------|-------------|-----------|
| [Kurztitel] | [Was wird getestet] | [Erwartetes Ergebnis] |

## Testdaten / Fixtures

- [Welche HTML-Fixtures müssen erstellt werden]
- [Welche Mock-Responses werden benötigt]
```

### Schritt 5: Abgleich mit Akzeptanzkriterien

Stelle sicher, dass jedes Akzeptanzkriterium der Spezifikation durch mindestens einen Test abgedeckt ist. Falls nicht, ergänze fehlende Tests.

## Verhaltensregeln

- **Verhaltensbasiert, nicht funktionsbasiert:** Tests beschreiben WAS geprüft wird, nicht WIE.
- **Fachliche Gruppierung:** Tests nach fachlichen Bereichen gruppieren (z.B. "Suchfunktion", "Artikel-Parsing", "Paywall"), nicht nach technischen Schichten.
- **Happy Paths und Edge Cases:** Jedes Akzeptanzkriterium braucht einen Happy-Path-Test. Für Fehlerszenarien (Timeout, 404, leere Suche) eigene Edge-Case-Tests.
- **Vollständigkeit über Minimalismus:** Lieber einen Test zu viel als eine Lücke.
- **Fixtures dokumentieren:** Welche HTML-Dateien oder Mock-Responses als Testdaten benötigt werden.
