# Gutenberg-Umsetzung: `/lithium-safety-container/` (Agentur-Text)

Quelle: `logbatt.de_lithiumsafetycontainer_OPTIERW_V01.docx` (Agentur Suchhelden GmbH,
Tracked-Changes-Version vom 2026-07-27, Autorin lt. Datei: Selina).
Ergebnis: `optimized/de/lithium-safety-container.html`.

## Wichtiger technischer Hinweis zur Quelldatei

Das docx enthielt **echte Word-Änderungsverfolgung** (nicht nur sichtbaren Text). Eine naive
Textextraktion (z. B. `python-docx` `.text` oder `pandoc`) liefert bei diesem Dokument
**falschen, unvollständigen Text**, weil sowohl gelöschte als auch eingefügte Textfragmente
falsch bzw. gar nicht berücksichtigt werden (typisches Symptom: abgehackte Wortfragmente wie
„sicher ufbewahr, andhab und" statt „sicher aufzubewahren, handzuhaben und"). Der Text wurde
daher über einen eigenen XML-Parser aufgelöst, der `<w:ins>`-Inhalte übernimmt und
`<w:del>`-Inhalte korrekt entfernt. Das Ergebnis wurde stichprobenartig gegen die Roh-XML
gegengeprüft.

## Entscheidungen beim Aufbau des Gutenberg-Codes

- **FAQ-Block:** als WordPress-Core-Block `wp:details` umgesetzt (nativ seit WP 6.4, rendert als
  `<details><summary>`). Falls die Live-Seite ein spezifisches Accordion-Plugin nutzt, sollten
  die 10 Frage/Antwort-Paare stattdessen in dessen Format übertragen werden.
- **Zwei "Tabellen" im Word-Dokument waren keine echten Datentabellen**, sondern optisch als Box
  formatierte Merkmalslisten (6 Punkte techn. Merkmale; Zielgruppen-Liste) → als `wp:list`
  umgesetzt. Eine dritte "Tabelle" (Absatz zur Relevanz der Normen für Unternehmen) wirkte wie
  eine Infobox → als `wp:group` mit hellgrauem Hintergrund umgesetzt (Konvention „grey-zeile"
  aus dem bestehenden Content-Bestand). Die vierte Tabelle (Container-Abmessungen je Größe) ist
  eine echte Datentabelle → als `wp:table` umgesetzt.
- **JSON-LD komplett neu aufgebaut** (ersetzt den dokumentierten Fehler, bei dem die Seite
  bisher fälschlich das JSON-LD von `/transportkisten/` einbettete, siehe `website/de/_index.md`):
  `CollectionPage` (Haupt-Entity) + `ItemList` mit 4 `Product`-Einträgen (4FT/10FT/20FT/40FT,
  je mit Abmessungen aus der Word-Tabelle als `additionalProperty`) + eigenständige
  `Organization` für den Hersteller **Lithium Safety Containers B.V.** (Domain
  `lithiumsafetycontainers.nl`, vom Kunden am 2026-08-03 als Vertriebspartner bestätigt) +
  `Service`-Entity für LogBATTs Vertriebs-/Beratungsleistung (Scope bewusst eng auf
  Deutschland/Österreich/Schweiz gehalten, da der Text explizit "D-A-CH-Region" nennt) +
  `FAQPage` (10 Fragen) + `BreadcrumbList`.
- **Ein Tippfehler** in einer H2 („Lithium Safety Containerns" → „Containern") wurde
  stillschweigend korrigiert.

## Korrektur 2026-08-03 (nach Nutzerhinweis)

Erste Fassung hatte für Bilder und die Produktbroschüre nur Platzhalter/TODO-Marker gesetzt,
obwohl die echten Assets (Cover-Hintergrund, KIWA-Logo, 10FT-/40FT-Containerfotos, allgemeine
Broschüre, vier größenspezifische Datenblatt-PDFs) bereits im selbst eingepflegten Ist-Zustand
(`website/de/lithium-safety-container.html`) sowie im ursprünglichen Rohcode-Transkript vorlagen
– hätte dort abgeglichen werden müssen, statt den Agentur-Text isoliert zu behandeln. Fehler vom
Nutzer bemerkt und behoben: Alle Medien (inkl. Media-IDs) und PDF-Links sind jetzt aus dem
Ist-Zustand übernommen, inklusive der vier einzelnen Datenblatt-Buttons (4FT/10FT/20FT/40FT
LAGERUNG), die im Agentur-Text nicht mehr vorkamen, aber als reale Assets weiter existieren.

## Zweite Korrektur 2026-08-03 (nach weiterem Nutzerhinweis)

Zwei weitere Fehler waren in der zweiten Fassung noch drin, beide dadurch entstanden, dass ich
Vorlagen-Bausteine aus anderen Seiten wiederverwendet habe, statt konsequent den für DIESE Seite
bereits vorliegenden Original-Rohcode auszuwerten:

1. **Doppelter Header:** Ich hatte den generischen synchronisierten Header-Block
   (`wp:block {"ref":17205}`) aus anderen Templates übernommen UND zusätzlich den echten
   Cover-Header dieser Seite gebaut – dadurch erschienen zwei Header-Bilder übereinander. Der
   `ref:17205`-Block existiert im Original-Rohcode dieser Seite gar nicht; der `wp:cover`-Block
   MIT dem 4FT-Bild IST hier der Seiten-Header. Entfernt.
2. **Falscher FAQ-Block:** Ich hatte den WordPress-Core-Block `wp:details` verwendet, obwohl der
   Original-Rohcode dieser Seite (und aller anderen Seiten) das sitewide Plugin
   `wp:generic/accordion` nutzt (`<div class="wp-block-generic-accordion generic-accordion">`).
   Jetzt exakt nach diesem Muster umgesetzt – die 5 bereits vorhandenen Fragen behalten ihre
   ursprünglichen Anker-IDs 1:1, für die 5 neuen Fragen aus dem Agentur-Text wurden nach
   demselben Namensschema neue Anker generiert.

## Noch offen (siehe Header-Kommentar in der Datei selbst)

1. Bild-/PDF-URLs liegen teils auf der Backend-Domain (`117655.wd50.extern.regiohelden.de`)
   statt `logbatt.de` – so bereits im Ist-Zustand, sollte gegen die aktuell gültigen
   Medien-URLs/IDs geprüft werden.
2. Ob die vier Datenblatt-PDF-Buttons bewusst von der Agentur gestrichen wurden oder einfach
   nicht Teil des Textauftrags waren, ist unklar – hier vorsorglich wieder ergänzt.
3. Telefonnummer ist die von der Agentur fest angegebene Nummer (+49 7153 925080), nicht der
   sonst sitewide verwendete Platzhalter `[ProxyNumber]` – bewusst unverändert übernommen, da
   es sich um von der Agentur freigegebenen Text handelt.
4. Die 5 neu generierten Accordion-Anker (für die 5 neuen FAQ-Fragen) einmal in der
   WordPress-Vorschau prüfen.
