# Deutsche Website – Seitenübersicht (Ist-Zustand)

Rohcode aus dem WordPress-Gutenberg-Backend, Stand: 2026-07-29.
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
| `transportkisten.html` | Transportboxen (Übersicht) | `/transportkisten/` | Transport- & Brandschutzbehälter für Lithium-Ionen-Batterien \| LogBATT GmbH | CollectionPage, BreadcrumbList, ItemList (7 Produkte+Specs+Zertifikat), DefinedTerm, FAQPage (15) |
| `logistik.html` | Logistik | `/logistik/` | Lithium-Ionen-Batterielogistik 🔋 \| LogBATT GmbH | WebPage, Service |
| `recycling.html` | Recycling von Lithium-Ionen-Akkus | `/recycling/` | Europaweites Recycling von Lithium-Ionen-Akkus ♻️ \| LogBATT GmbH | FAQPage (@graph, 11) + FAQPage (7) |
| `nachhaltigkeit.html` | Klimaschutz und Nachhaltigkeit | `/nachhaltigkeit/` (vermutet) | Klimaschutz und Nachhaltigkeit \| LogBATT GmbH | – |
| `qualitaetssicherungsprogramm.html` | Qualitätssicherungsprogramm (QSP) | `/qualitaetssicherungsprogramm/` (vermutet) | Qualitätssicherung für Gefahrgutverpackungen⚠️\| BAM | – |
| `lithium-safety-container.html` | Lithium Safety Container (KIWA / PGS 37-2) | `/lithium-safety-container/` | Sichere Lagerung von Lithiumbatterien \| Lithium Safety Container | CollectionPage/ItemList u. a. – **aber irrtümlich das JSON-LD von `/transportkisten/`** (s. u.) |
| `automobil-hersteller.html` | Systemlösungen für Automobil-Hersteller | `/automobil-hersteller/` | – | – |
| `lkw-hersteller.html` | Systemlösungen für LKW-Hersteller | `/lkw-hersteller/` (vermutet) | – | – |
| `versicherungen.html` | Systemlösungen für Versicherungen | `/versicherungen/` (vermutet) | – | – |
| `behaeltermiete.html` | Transportbox mieten (Behältermiete, B2B) | `/transportbox-mieten/` (vermutet) | – | FAQPage |
| `transportkisten/verkauf-von-gefahrgutboxen.html` | Verkauf von Gefahrgutboxen | `/transportkisten/verkauf-von-gefahrgutboxen/` | Sichere Gefahrgut-Transportbehälter kaufen \| LogBATT GmbH | WebPage, Service, FAQPage (5) |
| `ueber-uns.html` | Über uns | `/ueber-uns/` | – | – |
| `lexikon.html` | Lexikon (Gefahrgutlogistik / Gefahrgutklassen) | `/lexikon/` (vermutet) | – | – (60 Begriffe A–Z als `<details>`) |

## Produktdetailseiten (SafetyBATTbox)

Alle Produktseiten enthalten je ein **Product-JSON-LD** (mit `additionalProperty`-Specs,
BAM-`hasCertification` bei Transportboxen, `offers` = „Preis auf Anfrage") plus **ItemPage +
BreadcrumbList** und eine seiteneigene **FAQPage (7 Fragen)**. Verdichtet gespeichert:
Produkttext, technische Daten-Tabelle und JSON-LD verbatim; dekoratives Slider-/Galerie-Markup
als Hinweis vermerkt.

### Lagerbehälter — `website/de/lagerbehaelter/` (Anwendung: Lagerung, kein Löschwasser)

| Datei | Produkt | Art.-Nr. | Zuladung | Werkstoff |
| --- | --- | --- | --- | --- |
| `safety-battbox-xl-storage.html` | SafetyBATTbox XL-Storage | 300030 | 1.050 kg | Pulverbeschichteter Stahl / Edelstahl |
| `safety-battbox-l-storage.html` | SafetyBATTbox L-Storage | 300041 | 357 kg | Alu / Edelstahl / verzinkt |
| `safety-battbox-m-storage.html` | SafetyBATTbox M-Storage | 300031 | 80 kg | Verzinkter Stahl |

### Transportboxen — `website/de/transportkisten/` (Anwendung: Transport + Lagerung, BAM-zugelassen)

| Datei | Produkt | Art.-Nr. | Zuladung | VG | ADR-Anweisung | BAM-Nr. |
| --- | --- | --- | --- | --- | --- | --- |
| `safety-battbox-xl-2plus.html` | SafetyBATTbox XL-2.2+ | 300076 | 1.700 kg | I | LP906 (SV376) | D-BAM 16336 (Einzelfall) |
| `safety-battbox-xl-2.html` | SafetyBATTbox XL 2.2 | 300075 | 1.129 kg | I | LP904/905/906 | D-BAM 15730 |
| `safety-battbox-xl-lite.html` | SafetyBATTbox XL-lite | 300063 | 900 kg | II | LP903/904/905 | D-BAM 16059 |
| `safety-battbox-l-2.html` | SafetyBATTbox L-2 | 300037 | 357 kg | I | P908–P911 | D-BAM 15891 |
| `safety-battbox-m-2.html` | SafetyBATTbox M-2 | 300004 | 30 kg | I | P908–P911 | D-BAM 15468 |
| `safety-battbox-s-1.html` | SafetyBATTbox S-1 | 300007 | 10 kg | I | P908–P911 | D-BAM 15937 |
| `safety-battbox-s-1-lite.html` | SafetyBATTbox S-1-lite | 300077 | 15 kg | II | P903/908/909/910 | D-BAM 16387 |

**Zubehör (auf Übersichtsseite):** LogCOVER (Brandschutzdecke), LogBAGs (Brandschutz-Kissen,
Größen XL/L/M/S+/S, DIN 4102 / EN 13501-1). **Weitere Trust-Signale hier zuerst genannt:**
45 bestandene reale Brandtests, Verfahrensfestlegungsinhaber P911/LP906, DOT U.S. Special Permit,
GPS-Tracking/Sensorik, LogBATT E-Learning Academy (training@logbatt.de).

### Auffälligkeiten in den Produktseiten (Original)
- Auf `safety-battbox-m-2.html` und `safety-battbox-s-1-lite.html` lautet die sichtbare
  FAQ-Überschrift jeweils „… zur SafetyBATTbox M-2" (Copy-Paste-Fehler); JSON-LD-@ids sind korrekt.
- `safety-battbox-xl-2plus.html` enthält den kompletten Produktblock im Original doppelt.
- Übersicht `transportkisten.html`: Kurzdaten von L-2/M-2/S-1 nennen fälschlich „LP911" statt „P911".

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

## Glossar / Lexikon (`lexikon.html`)

60 Fachbegriffe A–Z als `<details>`/`<summary>`-Accordions (Verpackungscodes 4A/4H/50A/50H,
ADR/RID/IMDG/IATA, BAM/BAM-GGR 024, Gefahrgutklassen 1–9, UN 3090/3091/3480/3481/3551/3552,
P911/LP906, Thermische Propagation, Batteriepass, LFP-/NMC-Batterien, VdS 3103 u. v. m.).
Kein JSON-LD im Rohcode – **starke DefinedTerm-/FAQ-Quelle für GEO** (Definitionen liegen
strukturiert und zitierfähig vor). Es gibt zusätzlich ein separates „Glossar" (`glossar.html`).

## Wichtige interne Verlinkungen (im Rohcode referenziert, aber noch NICHT eingepflegt)

Diese Seiten werden verlinkt, liegen aber noch nicht als Quellcode vor:
`/stellenanzeigen/`, `/2019/logbatt-e-learning-academy-online/` (LogBATT Academy),
`logbatt-academy.com` (externe Academy-Domain), Glossar-Detailseiten (`?page_id=…`).
(Inzwischen eingepflegt: `/logistik/`, `/transportkisten/` + Produktdetailseiten,
`/ueber-uns/`, `/recycling/`, `/lexikon/`.)

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
- **`lithium-safety-container.html`:** Das eingebettete JSON-LD ist NICHT der Container-Content,
  sondern 1:1 das CollectionPage-/ItemList-Markup von `/transportkisten/` (alle `@id` zeigen auf
  `…/transportkisten/#…`, gelistet werden die 7 SafetyBATTbox-Transportboxen). Für die KIWA-/PGS-37-2-
  Container (4FT/10FT/20FT/40FT) fehlt damit passendes strukturiertes Markup → **GEO-Quick-Win**.
- **`behaeltermiete.html`:** Der Seiteninhalt war im gelieferten Rohcode zweimal identisch
  enthalten (Doppel-Paste); hier einmalig übernommen.
- **`automobil-hersteller.html`, `lkw-hersteller.html`, `versicherungen.html`:** identische H1
  („Unsere ganzheitliche Lösung für Lithiumbatterielogistik – maßgeschneidert für Sie") und
  weitgehend gleicher Aufbau; kein JSON-LD, keine eigenständigen Meta-Tags im Rohcode geliefert.
