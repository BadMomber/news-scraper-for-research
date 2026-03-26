---
name: story-writer
description: "Strukturierter Dialog zur Detaillierung eines Arbeitspakets mit Anforderungen, Akzeptanzkriterien und Abgrenzung"
---

# /story-writer

Detailliert ein Arbeitspaket aus AP.md durch einen strukturierten Dialog mit dem Nutzer. Das Ergebnis ist eine präzise Spezifikation mit Anforderungen, Akzeptanzkriterien und Abgrenzung.

## Usage

```
/story-writer [AP-Nummer oder Beschreibung]
```

Beispiel: `/story-writer AP2` oder `/story-writer Crawler taz.de`

## Instructions

### Schritt 1: Kontext verstehen

Lies die folgenden Projektdateien:
- `AP.md` — Arbeitspakete und ihre Aufgaben
- `Anforderungen.md` — Fachliche Anforderungen und Rahmenbedingungen

### Schritt 2: Anforderungen klären

Stelle gezielte Rückfragen, um Mehrdeutigkeiten aufzulösen:
- Was genau soll das Arbeitspaket leisten?
- Welche Randfälle gibt es?
- Was gehört explizit **nicht** dazu (Abgrenzung)?
- Gibt es Abhängigkeiten zu anderen Arbeitspaketen?

Stelle maximal 3-4 Fragen pro Runde.

### Schritt 3: Abhängigkeiten prüfen

Prüfe in AP.md:
- Welche APs müssen vorher abgeschlossen sein?
- Welche APs bauen auf diesem AP auf?
- Gibt es gemeinsam genutzte Komponenten?

Berichte dem Nutzer, welche Abhängigkeiten identifiziert wurden.

### Schritt 4: Spezifikation schreiben

Erstelle die Spezifikation als Markdown-Datei unter `documentation/specs/` mit dem Muster `ap-NN-spec.md`.

Format:

```markdown
# Spezifikation: [AP-Titel]

## Ziel

[2-3 Sätze: Was wird umgesetzt und warum?]

## Anforderungen

### [Teilbereich 1]

- [Konkrete, prüfbare Anforderung]
- [Konkrete, prüfbare Anforderung]

### [Teilbereich 2]

- [Konkrete, prüfbare Anforderung]

## Akzeptanzkriterien

- [ ] [Prüfbare Aussage: "Wenn X, dann Y"]
- [ ] [Prüfbare Aussage]

## Abgrenzung

- [Was explizit nicht dazugehört]

## Abhängigkeiten

- [Voraussetzungen und nachfolgende APs]
```

### Schritt 5: Review

Zeige dem Nutzer die fertige Spezifikation und frage, ob Anpassungen nötig sind. Aktualisiere die Datei entsprechend.

## Verhaltensregeln

- **Sprache:** Dokumentation in Deutsch.
- **Keine technische Lösung vorschlagen** — die Spezifikation beschreibt WAS, nicht WIE.
- **Immer mit Fragen starten** — nie direkt eine Spezifikation schreiben ohne den Kontext geklärt zu haben.
- **Prüfbare Kriterien** — jedes Akzeptanzkriterium muss objektiv überprüfbar sein.
