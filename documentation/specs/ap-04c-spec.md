# Story: zeit.de Paywall-Handling

## User Story

Als Rechercheurin möchte ich auch für Z+ Artikel den vollständigen Artikeltext und eine korrekte Zeichenanzahl erhalten, damit meine Analyse nicht durch fehlende Volltexte verfälscht wird.

## Beschreibung

In AP4b werden Z+ Artikel erkannt und mit dem sichtbaren Teaser-Text erfasst. Dieses Arbeitspaket versucht, den Volltext über eine Stufen-Strategie zu beschaffen. Die Strategie berücksichtigt die Besonderheiten von zeit.de: viele Artikel sind über den Google-Referer zugänglich, und bei manchen ist der volle Text im HTML vorhanden, aber per JavaScript/CSS versteckt. Wenn ein Volltext beschafft werden kann, wird der Teaser-Text ersetzt und der Character Count aktualisiert. Wenn kein Fallback funktioniert, bleibt der Teaser mit der Z+ Markierung bestehen.

## Akzeptanzkriterien

### Stufen-Strategie

Die Fallbacks werden in dieser Reihenfolge versucht:

- [ ] **Stufe 1: Google-Referer** — Seitenaufruf mit Google als Referer wiederholen; prüfen ob mehr Text als der Teaser zurückkommt
- [ ] **Stufe 2: HTML-Quelltext prüfen** — Prüfen ob der volle Artikeltext im HTML vorhanden ist (auch wenn er per CSS/JS versteckt wäre); ggf. JavaScript im Browser-Kontext deaktivieren; bei zeit.de oft erfolgreich
- [ ] **Stufe 3: Google-Cache** — Artikel über `webcache.googleusercontent.com` abrufen
- [ ] **Stufe 4: Archive-Dienste** — Artikel über `archive.org` (Wayback Machine) suchen

### Volltext-Aktualisierung

- [ ] Wenn ein Fallback den Volltext liefert, wird der bisherige Teaser-Text durch den Volltext ersetzt
- [ ] Der Character Count wird auf Basis des neuen Volltexts neu berechnet
- [ ] Die Z+ Markierung bleibt bestehen (der Artikel ist weiterhin als Z+ gekennzeichnet)

### Kein Volltext verfügbar

- [ ] Wenn keiner der Fallbacks funktioniert, bleibt der Teaser-Text bestehen
- [ ] Der Character Count bleibt auf dem reduzierten Teaser-Wert
- [ ] Der Artikel wird in den Ergebnissen nicht entfernt — er bleibt mit Teaser und Markierung erhalten

### Robustheit

- [ ] Jeder Fallback hat eigene Timeouts
- [ ] Wenn ein Fallback fehlschlägt, wird sauber zum nächsten gewechselt
- [ ] Der gesamte Paywall-Prozess wird geloggt (welcher Fallback versucht wurde, ob erfolgreich)

## Abgrenzung

- Suche und Ergebnisliste kommt aus AP4a
- Basis-Scraping (Autor, Teaser, Z+ Erkennung) kommt aus AP4b — AP4c ergänzt nur den Volltext
- Die Paywall-Strategie ist spezifisch für zeit.de — heise.de hat einen eigenen Paywall-Typ (AP3c)
- Keine Deduplizierung oder CSV-Export — das ist AP5
