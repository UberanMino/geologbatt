# Arbeitsregeln für dieses Repo (gilt für jede Session)

Dieses Repo ist die Arbeitsbasis für die GEO-Optimierung der LogBATT-Websites (logbatt.de, .com,
.nl, .dk, .no, .it, .es, .fr, .fi, .se, .pt …). Seiten-Code liegt als WordPress-Gutenberg-Markup in
`optimized/<sprache>/` (optimierte Fassungen) und `website/de/` (deutscher Ist-Zustand).

**Grundsatz: Es wird immer am aktuellsten Stand gearbeitet. Nie an einer alten Fassung und nie an
einem Nachbau.**

## 1. Ein Stand: der Default-Branch

- Der Default-Branch des Repos (`claude/logbatt-gen-engine-optimization-rvqy3b`) ist der **einzige
  gültige Gesamtstand**. Neue Sessions starten dort.
- **Zu Beginn jeder Session:** `bash tools/repo-status.sh` ausführen. Das Skript zeigt, ob es
  Branches mit Arbeit gibt, die noch nicht im Default-Branch ist, und welche Dateien sie ändern.
  Gibt es solche Branches und betreffen sie die Dateien der aktuellen Aufgabe, diese Arbeit zuerst
  in den eigenen Branch mergen (bzw. den Nutzer fragen), bevor irgendetwas geändert wird.
- **Am Ende jeder Aufgabe:** den Arbeitsbranch in den Default-Branch mergen (Fast-Forward/Merge,
  kein Force-Push). Nur so startet die nächste Session mit dem neuesten Stand. Vorher die Freigabe
  des Nutzers einholen, falls sie nicht schon erteilt wurde.

## 2. Bevor eine Seite geändert wird

1. **Neueste Fassung im Repo finden:**
   `git log --all --format='%h %ci %d %s' -- optimized/<sprache>/<seite>.html`
   Wenn ein anderer Branch eine neuere Fassung hat, ist **diese** die Basis.
2. **Mit der Live-Seite abgleichen:**
   `python3 tools/live-diff.py optimized/<sprache>/<seite>.html [URL]`
   Das vergleicht Überschriften, Produkt-Karussell, Bilder und Links.
   - `OK`: Die Datei im Repo ist der Live-Stand, man kann darin arbeiten.
   - **Unterschiede:** Die Seite wurde im WordPress-Editor geändert, oder die Repo-Datei ist alt.
     Dann **den Nutzer nach dem aktuellen Editor-Code fragen** (WordPress → Code-Editor → alles
     kopieren), ihn ins Repo legen und erst dann ändern.
3. **Niemals Blöcke aus dem Front-End-HTML nachbauen.** Das gilt besonders für
   `rh/block-splide` (Produkt-Karussell), `rh/*`-Blöcke und synchronisierte Blöcke. Der Block-Code
   ist von außen nicht sichtbar, und ein Nachbau sieht im Editor falsch aus. Fehlt ein Block in der
   Repo-Datei, ist die Repo-Datei veraltet (siehe Punkt 2).

## 3. Beim Ändern

- **Nur das ändern, worum gebeten wurde.** Keine Zusatztexte, keine Umstrukturierung, kein
  „Verbessern nebenbei“. Vorschläge darüber hinaus gehören in die Antwort, nicht in die Datei.
- Konventionen der jeweiligen Seite übernehmen, z. B. Links auf Produkttiteln (`<h4><a …>`) statt
  zusätzlicher Linktexte, so wie auf der deutschen Seite.
- Nach der Änderung **den Diff gegen die Ausgangsfassung zeigen**
  (`git diff <basis> -- <datei>`). Er darf nur die angefragten Zeilen enthalten.
- Prüfen: JSON-LD parst, `<!-- wp:… -->`-Blöcke sind balanciert, alle neuen Links liefern 200.
- Dem Nutzer einen **festen Link auf genau diese Version** geben (Commit-Hash, nicht Branch-Name),
  z. B. `https://raw.githubusercontent.com/UberanMino/geologbatt/<hash>/optimized/en/<seite>.html`.

## 4. Bekannte Besonderheiten

- logbatt.com/.de/… sind eine WordPress-Multisite (Site 10112): Dieselben Uploads gibt es unter allen
  Domains. Bilder auf logbatt.com müssen mit `www.logbatt.com` eingebunden sein, wegen der CSP.
- EN-Produktslugs sind gegenüber den Namen vertauscht: `/transport-crates/safetybattbox-xl-2-2/` =
  XL-2.2+, `/transport-crates/safetybattbox-xl-2-2-2/` = XL 2.2. Für die XL-lite gibt es keine EN-Seite.
- Schwedisch liegt in zwei Ordnern (`optimized/se/` und `optimized/sv/`). Noch nicht
  zusammengeführt, beim Arbeiten an schwedischen Seiten beide prüfen.
- Analysen und Daten: `notes/`, `data/peec/` (siehe READMEs dort).
