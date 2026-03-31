# Story: Volltextfilter — Nachträgliche Relevanzprüfung

## User Story

Als Rechercheurin möchte ich, dass nur Artikel in der Ergebnis-CSV verbleiben, die tatsächlich mindestens eine der Suchbegriffkombinationen im Volltext enthalten, damit ich keine irrelevanten Treffer manuell aussortieren muss.

## Beschreibung

Die Suchmaschinen der Nachrichtenseiten liefern manchmal Artikel, die zwar zum Suchbegriff passen (z.B. im Titel oder in Metadaten), aber die Suchbegriffe nicht im Artikeltext enthalten. Ein nachgelagerter Filter prüft den gespeicherten Volltext und entfernt irrelevante Treffer.

## Anforderungen

### Filterlogik

- Der Filter prüft, ob **beide Wörter** eines Keyword-Paars im Artikeltext vorkommen
- Die Wörter müssen **nicht nebeneinander** stehen — sie müssen nur beide irgendwo im Text vorkommen
- Die Suche ist **case-insensitive**
- Ein Artikel hat ggf. mehrere zugeordnete Keyword-Paare (durch Dedup). Es reicht, wenn **mindestens ein** Keyword-Paar vollständig im Text gefunden wird
- Sobald ein Paar gefunden wird, muss nicht weiter gesucht werden

### Filterverhalten

- Der Filter ist eine **lokale Operation** — er läuft nach dem vollständigen Download aller Artikel
- Artikel, die den Filter **nicht bestehen**, werden:
  - Aus der CSV entfernt
  - Die zugehörige Textdatei in `texte/` wird gelöscht
- Der Filter loggt, wie viele Artikel entfernt wurden

### Zeitpunkt

- Der Filter läuft **nach dem Scraping und der Deduplizierung**, aber **vor der Verifikation**
- Reihenfolge: Scraping → Dedup (inkrementell) → **Volltextfilter** → Verifikation

## Akzeptanzkriterien

- [ ] Artikel ohne Treffer für mindestens ein Keyword-Paar werden aus der CSV entfernt
- [ ] Die zugehörige Textdatei wird gelöscht
- [ ] Die Prüfung ist case-insensitive
- [ ] Ein Artikel mit mehreren Keyword-Paaren bleibt erhalten, wenn mindestens eines matcht
- [ ] Der Filter loggt die Anzahl entfernter Artikel
- [ ] Nach dem Filter ist die CSV valide (korrekter Header, keine verwaisten Einträge)
- [ ] Paywall-Artikel mit nur Teaser-Text werden ebenfalls geprüft (der Teaser kann die Begriffe enthalten)

## Abgrenzung

- Kein Stemming oder Fuzzy-Matching — exakte Wortsuche (case-insensitive)
- Keine Änderung an der Such- oder Scraping-Logik
- Kein separater CLI-Befehl — der Filter ist Teil des normalen Laufs
