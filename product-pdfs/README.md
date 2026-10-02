# PDF-Produktblätter für Sprachen ohne eigene Produktseiten

Für Sprachen, in denen LogBATT keine eigenen Produktseiten hat (z. B. Rumänisch), werden die
**10 SafetyBATTbox-Produktdetailseiten** (7 Transportboxen, 3 Lagerbehälter) als 2-seitige
A4-PDFs nachgebaut. Hub-/Übersichtsseiten (`/transportkisten/`, `/lagerbehaelter/`) sind bewusst
nicht enthalten.

Pro Produkt enthält das PDF dieselben Inhalte wie die deutsche Seite: H1/Untertitel,
Produkt-Bullets, ggf. Block „Kauf oder Miete“, technische Daten, alle 7 FAQ und die
Kontaktaufforderung (Button „Produktberatung anfragen“). Zusätzlich gibt es Kennzahlen-Kacheln,
die aus den technischen Daten erzeugt werden.

## Aufbau

```
products.json        Stammdaten je Produkt: deutsche Quelldatei, Live-URL, Bild (+ Bildquelle)
content/<lang>.json  Übersetzung: UI-Texte, Spec-Labels/-Werte, je Produkt Untertitel, Bullets, FAQ
template/style.css   Layout (A4, Roboto, LogBATT-Blau #2dabe3)
assets/              Logo, Roboto-Webfonts (OFL, siehe LICENSE-Roboto.txt), Produktbilder (aus logbatt.de, optimiert)
build.mjs            Generator (Chromium via Playwright -> PDF, pdf-lib -> Metadaten)
out/<lang>/          Fertige PDFs: <slug>-<lang>.pdf
```

**Technische Daten werden nicht übersetzt abgetippt**, sondern beim Build direkt aus der
deutschen Quelldatei unter `website/de/` gelesen. Zahlen, Typbezeichnungen, UN-Codierungen und
P/LP-Anweisungen gehen unverändert durch; nur Labels und Text-Werte (z. B. Werkstoff) kommen aus
der Sprachdatei.

Der Build bricht ab, wenn
- die Anzahl der übersetzten Bullets oder FAQ nicht zum deutschen Original passt,
- ein Spec-Label oder ein Text-Wert der Tabelle keine Übersetzung hat.

Ändert sich also eine deutsche Produktseite, fällt beim nächsten Build auf, dass die Übersetzung
nachgezogen werden muss.

## Build

```bash
cd product-pdfs
npm install          # playwright + pdf-lib (Browser ist im Container vorinstalliert)
node build.mjs ro            # alle Produkte
node build.mjs ro xl-2plus   # nur ein Produkt (Slug-Filter)
```

## Neue Sprache hinzufügen

1. `content/ro.json` nach `content/<lang>.json` kopieren und alle Texte übersetzen
   (Schlüssel in `spec_labels`/`spec_values` bleiben die deutschen Originale).
2. `node build.mjs <lang>`.

## PDF-Eigenschaften (für Suchmaschinen/LLMs relevant)

- Echter Text (kein Bild-PDF), eingebettete Roboto-Schrift inkl. rumänischer Diakritika (ș, ț mit Komma).
- Getaggtes PDF mit Dokumentsprache (`/Lang`), Lesezeichen aus den Überschriften.
- Metadaten: Titel (Produkt + Untertitel), Autor „LogBATT GmbH“, Betreff (erster Produkt-Bullet), Stichwörter.
- Link auf die deutsche Originalseite in der Kontaktbox.

## Status Rumänisch (`ro`)

Entwurf. Die Übersetzung wurde KI-gestützt erstellt und ist **noch nicht von einem
Muttersprachler bzw. Fachübersetzer (Gefahrgut/ADR) geprüft**. Besonders prüfen:

- ADR-Fachbegriffe: „instrucțiune de ambalare“, „grupă de ambalare“, „dispoziții speciale (DS)“,
  „aprobare BAM pentru caz individual“ (Einzelfallfestlegung), „critic defecte“.
- Lager-FAQ („Was muss ich rechtlich beachten?“): Der Text beschreibt die deutsche Praxis
  (Gefährdungsbeurteilung, Brandschutzkonzept). Für Rumänien ist der Rechtsrahmen ggf. anders.
- Kontaktdaten: Telefon/E-Mail/Website sind die deutschen (`info@logbatt.de`, `www.logbatt.de`);
  ob es für Rumänien einen anderen Ansprechpartner gibt, ist offen.

Bildauswahl: Hauptbild der jeweiligen Live-Seite; bei M-2 und S-1 ein Galeriebild, weil das
Hauptbild nur 285 px breit ist. Quelle je Bild steht in `products.json` (`image_source`).
