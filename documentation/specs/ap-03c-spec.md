# Story: heise.de Paywall-Handling

## User Story

Als Rechercheurin möchte ich auch für heise+ Artikel den vollständigen Artikeltext und eine korrekte Zeichenanzahl erhalten, damit meine Analyse nicht durch fehlende Volltexte verfälscht wird.

## Beschreibung

In AP3b werden heise+ Artikel erkannt und mit dem sichtbaren Teaser-Text erfasst. Dieses Arbeitspaket versucht, den Volltext über eine Stufen-Strategie zu beschaffen. Wenn ein Volltext beschafft werden kann, wird der Teaser-Text ersetzt und der Character Count aktualisiert. Wenn kein Fallback funktioniert, bleibt der Teaser mit der heise+ Markierung bestehen.

## Akzeptanzkriterien

### Stufen-Strategie

Die Fallbacks werden in dieser Reihenfolge versucht:

- [ ] **Stufe 1: Google-Referer** — Seitenaufruf mit Google als Referer wiederholen; prüfen ob mehr Text als der Teaser zurückkommt
- [ ] **Stufe 2: HTML-Quelltext prüfen** — Prüfen ob der volle Artikeltext im HTML vorhanden ist (auch wenn er per CSS/JS versteckt wäre); ggf. JavaScript im Browser-Kontext deaktivieren
- [ ] **Stufe 3: Google-Cache** — Artikel über `webcache.googleusercontent.com` abrufen
- [ ] **Stufe 4: Archive-Dienste** — Artikel über `archive.org` (Wayback Machine) suchen

### Volltext-Aktualisierung

- [ ] Wenn ein Fallback den Volltext liefert, wird der bisherige Teaser-Text durch den Volltext ersetzt
- [ ] Der Character Count wird auf Basis des neuen Volltexts neu berechnet
- [ ] Die heise+ Markierung bleibt bestehen (der Artikel ist weiterhin als heise+ gekennzeichnet)

### Kein Volltext verfügbar

- [ ] Wenn keiner der Fallbacks funktioniert, bleibt der Teaser-Text bestehen
- [ ] Der Character Count bleibt auf dem reduzierten Teaser-Wert
- [ ] Der Artikel wird in den Ergebnissen nicht entfernt — er bleibt mit Teaser und Markierung erhalten

### Robustheit

- [ ] Jeder Fallback hat eigene Timeouts
- [ ] Wenn ein Fallback fehlschlägt, wird sauber zum nächsten gewechselt
- [ ] Der gesamte Paywall-Prozess wird geloggt (welcher Fallback versucht wurde, ob erfolgreich)

## Abgrenzung

- Suche und Ergebnisliste kommt aus AP3a
- Basis-Scraping (Autor, Teaser, heise+ Erkennung) kommt aus AP3b — AP3c ergänzt nur den Volltext
- Die Paywall-Strategie ist spezifisch für heise.de — zeit.de hat einen eigenen Paywall-Typ (AP4c)
- Keine Deduplizierung oder CSV-Export — das ist AP5
