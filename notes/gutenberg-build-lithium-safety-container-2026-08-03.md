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

## Noch offen (siehe Header-Kommentar in der Datei selbst)

1. Platzhalter-Link für die Produktbroschüre (`#TODO-PDF-URL-Produktbroschuere-einfuegen`) muss
   durch die echte PDF-URL ersetzt werden.
2. FAQ-Blockwahl (`wp:details` vs. vorhandenes Accordion-Plugin) prüfen.
3. Telefonnummer ist die von der Agentur fest angegebene Nummer (+49 7153 925080), nicht der
   sonst sitewide verwendete Platzhalter `[ProxyNumber]` – bewusst unverändert übernommen, da
   es sich um von der Agentur freigegebenen Text handelt.
