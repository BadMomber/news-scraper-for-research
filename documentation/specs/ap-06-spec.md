# Story: Verifikation

## User Story

Als Rechercheurin möchte ich automatisch überprüfen können, dass alle Artikel-Links in meiner CSV erreichbar sind und die extrahierten Metadaten korrekt sind, damit ich mich auf die Datenqualität meiner Ergebnisse verlassen kann.

## Beschreibung

Nach dem CSV-Export (AP5) wird eine automatische Verifikation durchgeführt. Dabei werden zwei Dinge geprüft: Sind alle Links noch erreichbar? Stimmen die extrahierten Metadaten (Titel, Datum) mit den Daten auf der Zielseite überein? Das Ergebnis ist ein Verifikationsbericht, der erfolgreiche und fehlgeschlagene Prüfungen auflistet.

## Akzeptanzkriterien

### Link-Erreichbarkeit

- [ ] Jeder Link in der CSV wird per Seitenaufruf geprüft
- [ ] Ein Link gilt als erreichbar, wenn die Seite erfolgreich geladen wird (oder eine Weiterleitung auf eine erreichbare Seite führt)
- [ ] Nicht erreichbare Links (Fehlerseiten, Timeout) werden als fehlgeschlagen markiert
- [ ] Redirects werden gefolgt und die finale URL wird geprüft

### Metadaten-Abgleich

- [ ] Für jeden erreichbaren Artikel wird der Titel auf der Zielseite extrahiert und mit dem CSV-Titel verglichen
- [ ] Für jeden erreichbaren Artikel wird das Datum auf der Zielseite extrahiert und mit dem CSV-Datum verglichen
- [ ] Kleine Abweichungen im Titel (z.B. Whitespace-Unterschiede) werden toleriert
- [ ] Bei Abweichungen wird sowohl der CSV-Wert als auch der Wert von der Zielseite im Bericht angezeigt

### Verifikationsbericht

- [ ] Der Bericht listet jeden Artikel mit seinem Prüfstatus auf
- [ ] Kategorien: bestanden, Link nicht erreichbar, Titel-Abweichung, Datum-Abweichung
- [ ] Am Ende steht eine Zusammenfassung (z.B. "142 von 150 Artikeln bestanden, 5 nicht erreichbar, 3 Titel-Abweichungen")
- [ ] Der Bericht wird als Textdatei oder auf der Konsole ausgegeben

### Robustheit

- [ ] Rate-Limiting bei der Verifikation (die gleichen Server werden erneut angefragt)
- [ ] Timeouts für jeden Verifikations-Seitenaufruf
- [ ] Die Verifikation bricht nicht ab, wenn ein einzelner Artikel fehlschlägt

## Abgrenzung

- Die CSV kommt aus AP5 — AP6 liest sie nur
- Keine Korrektur der Daten — AP6 prüft nur und berichtet
- Kein erneutes Crawling — es werden nur die bereits vorhandenen Links geprüft
