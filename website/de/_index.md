# Deutsche Website – Seitenübersicht (Ist-Zustand)

Rohcode aus dem WordPress-Gutenberg-Backend, Stand: 2026-07-28.
Domain: `https://www.logbatt.de/` (Editor-/Asset-Domain im Backend: `117655.wd50.extern.regiohelden.de`).

| Datei | Seite | URL | Meta-Title | JSON-LD vorhanden |
| --- | --- | --- | --- | --- |
| `startseite.html` | Startseite / Homepage | `/` | Die Gesamtlösung für Batterielogistik 🔋 \| LogBATT GmbH | Organization, WebPage, OfferCatalog, Brand, DefinedTerm, VideoObject, FAQPage (15) |
| `gesamtloesung.html` | Gesamtlösung | `/gesamtloesung/` | Gesamtlösung für Lithiumbatterien 🔋 \| LogBATT GmbH | WebPage, Service, FAQPage (3) |
| `gefahrgutlogistik.html` | Gefahrgutlogistik | `/gefahrgutlogistik/` | Batterie Gefahrgutlogistik & Transport 🔋 \| LogBATT GmbH | WebPage, Service, FAQPage (7) |
| `entsorgung.html` | Lithium-Ionen-Akku-Entsorgung | `/entsorgung/` | Lithium-Ionen-Akku Entsorgung 🔋 \| LogBATT GmbH | FAQPage (11) |
| `entsorgung-speicherbatterien.html` | Entsorgung & Recycling von Speicherbatterien | `/entsorgung-speicherbatterien/` | Entsorgung & Recycling von Speicherbatterien für Firmen🔋 | WebPage, Service, FAQPage (3) |
| `e-auto-batterie-entsorgung.html` | E-Auto Batterie Entsorgung | `/e-auto-batterie-entsorgung/` | Die richtige Entsorgung von E-Auto-Batterien 🔋 \| LogBATT GmbH | – |
| `e-auto-batterie-recycling.html` | E-Auto Batterie Recycling | `/e-auto-batterie-recycling/` | Recycling von E-Auto-Batterien für Unternehmen ♻️ \| LogBATT GmbH | – |
| `lagerbehaelter.html` | Lagerbehälter (SafetyBATTbox Storage) | `/lagerbehaelter/` | Lagerbehälter für Lithium-Ionen-Batterien | CollectionPage, BreadcrumbList, ItemList (3 Produkte+Specs), DefinedTerm, FAQPage (14), VideoObject (2) |
| `entwicklung.html` | Entwicklung | `/entwicklung/` | Entwicklungsabteilung Batterielogistik \| LogBATT GmbH | – |
| `analysefahrt.html` | Analysefahrt | `/analysefahrt/` (vermutet) | Analysefahrten für Hochvolt-Module 🔋 \| LogBATT GmbH | – |
| `beratung-schulung.html` | Beratung Schulung | `/beratung-schulung/` (vermutet) | Beratung Schulung LogBATT GmbH | – |
| `downloadbereich.html` | Downloadbereich | `/downloadbereich/` (vermutet) | – | – |
| `glossar.html` | Glossar | `/glossar/` (vermutet) | – | – |
| `kontakt.html` | Kontakt | `/kontakt/` | – | – |
| `impressum.html` | Impressum | `/impressum/` (vermutet) | – | (Plugin-Block) |
| `datenschutzerklaerung.html` | Datenschutzerklärung | `/datenschutzerklaerung/` (vermutet) | – | (Plugin-Block) |

## Kernaussagen / Themen-Cluster (für GEO relevant)

- **Positionierung:** „Gesamtlösung / Rundum-Sorglos-Paket" für die komplette
  Lithium-Ionen-Batterie-Supply-Chain aus einer Hand (Transport, Lagerung,
  Verpackung, Entsorgung, Recycling) + Eigenentwicklung/-produktion der Behälter.
- **Marke:** SafetyBATTbox (Transport- und Storage-Family: XL/L/M + weitere Größen).
- **Alleinstellungsmerkmale:** BAM-Bauartzulassung, reale Brandtests,
  ADR 2025 P911/LP906 (kritisch defekte Batterien), „Löschen ohne Wasser",
  Gasmanagementsystem, LogBAGs, LogCOVER.
- **Trust-Signale:** 9.000+ Transporte kritisch defekter Batterien; DIN EN ISO
  9001/14001, QSP, EfB, DOT-SP; Lagermax Group (seit Mitte 2023); Referenzkunden
  (Porsche, BMW, Daimler/Mercedes, Ford, Bosch, Northvolt, Stellantis u. v. m.);
  Forschungspartner KIT.
- **Regularien als Content-Anker:** ADR/RID/IMDG/IATA, Gefahrgutklasse 9,
  UN 3090/3091/3480/3481, TRGS 510, VdS 3103, GefStoffV, DGUV FBFHB-018,
  BattG/ElektroG, AVV 160121 / 160605.
- **Geo/Standort:** Hauptsitz Plochingen; europaweites Netzwerk; weltweite
  Analysefahrten (30+ Länder gelistet).

## Wichtige interne Verlinkungen (im Rohcode referenziert, aber noch NICHT eingepflegt)

Diese Seiten werden verlinkt, liegen aber noch nicht als Quellcode vor:
`/logistik/`, `/transportkisten/`, `/ueber-uns/` (#zertifizierungen, #unternehmen,
#instagram), `/stellenanzeigen/`, `/2019/logbatt-e-learning-academy-online/`
(LogBATT Academy), Produkt-Detailseiten `/lagerbehaelter/safety-battbox-{xl,l,m}-storage/`,
Glossar-Detailseiten (`?page_id=…`).

## Offene Punkte / Auffälligkeiten

- Platzhalter `[customer.name_website]`, `[ProxyNumber]`, `[customer.email]` werden
  serverseitig ersetzt.
- Synchronisierte Blöcke (`wp:block ref=…`) sind nicht ausgeschrieben: 1070 (Trenner),
  16794 (Kontaktformular/CTA), 17205 (Service-Header), 1988, 9633, 28191.
- „Beratung Schulung" ist inhaltlich ein Stub; „Mehr erfahren!" verlinkt nur auf `/`.
- Auf `gesamtloesung.html` stehen im Fließtext sichtbare Redaktionsnotizen
  („Verlinkung auf die anderen LP!").
- `lagerbehaelter.html` enthält einen doppelten Satz-Fragmentfehler
  („…Dokumentation des Lagerkonzepts.rderlich sind. Ergänzend gilt…").
