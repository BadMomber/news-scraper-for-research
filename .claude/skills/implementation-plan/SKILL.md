---
name: implementation-plan
description: "Erstellt einen detaillierten technischen Implementierungsplan für ein Arbeitspaket des Crawlers"
---

# /implementation-plan

Erstellt einen detaillierten Implementierungsplan, der als Leitfaden für die Umsetzung eines Arbeitspakets dient. Der Plan definiert Schritte, betroffene Dateien, Code-Skizzen und Abhängigkeiten.

## Usage

```
/implementation-plan [AP-Nummer oder Beschreibung]
```

Beispiel: `/implementation-plan AP2` oder `/implementation-plan Crawler taz.de`

## Voraussetzungen

Vor dem Erstellen eines Implementierungsplans müssen folgende Dokumente existieren:

1. **Anforderungen.md** — Fachliche Anforderungen und Rahmenbedingungen
2. **AP.md** — Arbeitspakete mit Aufgabenliste

## Instructions

### Schritt 1: Eingaben lesen

Lies folgende Dateien:
- **Anforderungen.md** — Fachliche Anforderungen
- **AP.md** — Arbeitspakete und ihre Aufgaben
- Bestehende Implementierungen im Projekt, die als Pattern dienen
- Falls vorhanden: `CLAUDE.md` für Coding Conventions

### Schritt 2: Recherche

Für site-spezifische APs (AP2–AP4):
- Analysiere die Suchfunktion der Zielseite (URL-Schema, Parameter, Datumsfilter)
- Untersuche die HTML-Struktur der Suchergebnisseiten und Artikelseiten
- Identifiziere Pagination-Mechanismen
- Prüfe Paywall-Verhalten

### Schritt 3: Rückfragen stellen

Stelle dem Nutzer gezielte Rückfragen zu offenen technischen Entscheidungen. Typische Fragen:
- Wahl zwischen alternativen Bibliotheken oder Ansätzen
- Umgang mit Sonderfällen (leere Suchergebnisse, fehlende Metadaten)
- Rate-Limiting-Strategie
- Fehlerbehandlung bei nicht erreichbaren Seiten

Schreibe den Plan erst, wenn alle Fragen geklärt sind.

### Schritt 4: Plan erstellen

Erstelle den Implementierungsplan als Markdown-Datei unter `documentation/plans/` mit dem Muster `ap-NN-plan.md` (z.B. `ap-02-plan.md`).

Format:

```markdown
# Plan: [AP-Titel]

## Kontext

[Zusammenfassung des Arbeitspakets und der getroffenen Entscheidungen]

## Entscheidungen

- [Technische Entscheidung 1]
- [Technische Entscheidung 2]

---

## Diagramme (situativ)

Ergänze Mermaid-Diagramme wenn sie das Verständnis erleichtern:
- **Sequenzdiagramm** — Ablauf einer Suche (HTTP-Requests, Parsing, Speicherung)
- **Datenflussdiagramm** — Wie Daten von der Suche über Scraping zur CSV fließen

---

## Schritt N: [Titel]

**Datei:** `pfad/zur/datei.py`

[Beschreibung der Änderung]

```python
# Code-Skizze
```

---

## Dateien-Übersicht

### Neue Dateien
| Datei | Beschreibung |
|-------|-------------|

### Geänderte Dateien
| Datei | Änderung |
|-------|----------|
```

## Verhaltensregeln

- **Schritte nach Abhängigkeiten ordnen:** Gemeinsame Basis vor site-spezifischem Code. Jeder Schritt sollte für sich testbar sein.
- **Code-Skizzen, keine vollständige Implementierung:** Der Plan zeigt die Struktur und wichtige Details — genug, damit die Richtung klar ist.
- **Bestehende Patterns folgen:** Neue Dateien orientieren sich am Stil bestehender Dateien im Projekt.
- **Keine Abweichungen vom AP:** Der Plan implementiert genau das, was im Arbeitspaket steht — nicht mehr, nicht weniger.
