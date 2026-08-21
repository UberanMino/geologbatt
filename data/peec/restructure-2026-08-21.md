# Peec-Umbau 2026-08-21 – Internationalisierung (DE −30, EN +15, ES +15)

**Ziel:** Peec von 79 rein deutschen Prompts auf **49 DE + 15 EN + 15 ES = 79**
umstellen. Auswahl nach Fokusthemen (**Behälter/Produkt** + **Batterielogistik**,
Produktschwerpunkt), Recycling deprioritisiert, Dubletten/„doppelt gemoppelt" und
geschäftsfremde/sehr schwache Prompts raus.

> Umsetzung erfolgt manuell im Peec-Account (kein API-Zugriff). Diese Datei ist die
> abgestimmte Vorlage – Änderungswünsche vor dem Anlegen bitte melden.

---

## Teil 1 – 30 deutsche Prompts zum Entfernen

Verbleibende DE-Verteilung nach Entfernen in Klammern.

### Recycling – 5 von 6 raus (keine Priorität) → verbleibt 1
Grund: Recycling ist aktuell kein Fokusthema; schwächstes Cluster (Ø 24 %). 1 Prompt
als Minimal-Monitor bleibt („Lithium Batterie Recycling gewerblich Dienstleister").
1. Wer bietet Recycling von Lithium-Ionen-Batterien für Unternehmen an?
2. Anbieter für Batterierecycling europaweit
3. Wie finde ich einen Dienstleister für Batterierecycling im B2B-Bereich?
4. Welches Unternehmen ist das beste für Lithium-Ionen-Akku Recycling?
5. Bei wem kann ich am besten Lithium-Ionen-Akkus recyclen lassen?

### Entsorgung – 2 von 3 raus (Dublette) → verbleibt 1
Grund: 3 quasi identische „bester Anbieter für Entsorgung"-Prompts. 1 reicht.
6. Welcher ist der beste Anbieter für Lithium-Ionen-Akku-Entsorgung?
7. Welcher ist der beste Anbieter für Lithium-Ionen-Batterien Entsorgung?

### Havariefälle – 4 von 11 raus → verbleibt 7
Grund: sehr enge Nischen (Wasserbad/Löschwasser doppelt) + generische Schwachperformer.
8. Wer entsorgt Lithium-Batterien aus einem Wasserbad inklusive kontaminiertem Wasser? (19 %)
9. Spezialist für Lithium-Batterien im Wasserbad und kontaminiertes Löschwasser (16 %, Dublette zu 8)
10. Wer übernimmt die Entsorgung im Havariefall bei Lithium-Batterien? (16 %, generisch)
11. Wo kann ich einen nach einem Unfall defekten Akku entsorgen lassen? (6 %, generisch)

### Storage Container – 5 von 11 raus → verbleibt 6
Grund: redundante Größen-/Format-Varianten (10/20/40-Fuß, ISO) + Schwachperformer;
Kern-Container-Prompts bleiben erhalten.
12. Wer bietet begehbare ISO-Container für Hochvoltbatterien an? (6 %)
13. Wer verkauft 20-Fuß-Container für die Lithium-Batterien-Lagerung? (19 %)
14. Welche Firmen bieten 10-Fuß-Container für die Lagerung von Lithium-Akkus an? (41 %)
15. Anbieter 40-Fuß-Container zur Lagerung von Lithium-Batterien (50 %)
16. Begehbarer Quarantänecontainer Lithium-Ionen-Batterien Anbieter (47 %, Dublette zu „Welcher Anbieter verkauft begehbare Quarantänecontainer…")

### Transportboxen – 5 von 10 raus → verbleibt 5
Grund: „welche brauche ich"-Nullperformer + überzählige „beste …"-Varianten.
17. Welche Gefahrgutbox brauche ich für den Transport von Lithium-Batterien? (6 %)
18. Welche Quarantänebehälter brauche ich, um Lithium-Batterien zu transportieren? (6 %)
19. Beste Transportbox für Lithium Ionen Batterien (25 %)
20. Beste Quarantänekiste für den Transport von Lithium-Akkus (26 %)
21. Welche Havariebehälter gibt es, um defekte Lithium-Batterien zu transportieren? (22 %)

### Lagerbehälter – 3 von 9 raus → verbleibt 6
Grund: 0–4 %-Performer, generisch/ohne Sichtbarkeit.
22. Was sind die besten Behälter für Lithium-Ionen-Akkus? (0 %)
23. Welche Havariebehälter brauche ich für defekte Lithium-Akkus? (3 %)
24. Bester Lagerbehälter für Lithium Ionen Akkus (4 %)

### Vermietung von Gefahrgutboxen – 3 von 12 raus → verbleibt 9
Grund: stärkstes Cluster bleibt dominant; nur redundante „…Deutschland"-/„beste"-Dubletten raus.
25. Firma für Havariebehälter Vermietung Deutschland (16 %)
26. Firma für Batterie Container Vermietung Deutschland (70 %, generische Deutschland-Dublette)
27. Bester Anbieter für feuerfeste Quarantänebehälter für Lithium Batterien (46 %, Dublette zu „Quarantänekisten mieten")

### Verkauf von Gefahrgutboxen – 3 von 12 raus → verbleibt 9
Grund: direkte Dubletten zu stärkeren Verkaufs-Prompts.
28. Wer bietet Transportkisten für Lithium-Ionen-Batterien für Unternehmen an? (84 %, Dublette zu „Anbieter Transportkisten…" 96 %)
29. Anbieter Quarantänekiste für defekte Batterien B2B (74 %, Dublette zur getrackten „Quarantänebox")
30. Bei welchem Anbieter kann ich Brandschutzcontainer für defekte Batterien meines Unternehmens kaufen? (53 %, Dublette zu „Brandschutzbehälter … an Unternehmen")

**Verbleibend DE:** Vermietung 9 · Verkauf 9 · Storage Container 6 · Havariefälle 7 ·
Transportboxen 5 · Lagerbehälter 6 · Transport 3 · Lagerung 2 · Entsorgung 1 ·
Recycling 1 = **49**.

---

## Teil 2 – 15 EN + 15 ES zum Anlegen

Basis = die **8 bereits für die anderen Sprachen getrackten Prompts** (P1–P8),
plus **7 zusätzliche** (P9–P15) für maximale, distinkte Abdeckung der Fokusthemen.
Bewusst **ohne** großen Sicherheitscontainer (nur DE) und **ohne** Recycling.

| # | Cluster | Typ | Englisch | Spanisch |
| --- | --- | --- | --- | --- |
| P1 | Transportboxen | product | What transport boxes are available for lithium batteries? | ¿Qué cajas de transporte existen para baterías de litio? |
| P2 | Lagerbehälter | product | Which containers are suitable for storing lithium batteries? | ¿Qué contenedores son adecuados para el almacenamiento de baterías de litio? |
| P3 | Verkauf | product | Which suppliers sell safety boxes for damaged lithium batteries? | ¿Qué proveedores venden cajas de seguridad para baterías de litio dañadas? |
| P4 | Vermietung | product | Providers of storage containers for lithium batteries for rent | Proveedores de contenedores de almacenamiento para baterías de litio en alquiler |
| P5 | Havariefälle | service | Which service provider specializes in the disposal of lithium batteries after an incident? | ¿Qué proveedor de servicios está especializado en la eliminación de baterías de litio tras un siniestro? |
| P6 | Transport | service | Which company can transport damaged lithium batteries? | ¿Qué empresa puede transportar baterías de litio dañadas? |
| P7 | Vermietung | product | Which company rents out dangerous goods boxes for lithium batteries? | ¿Qué empresa alquila cajas para mercancías peligrosas para baterías de litio? |
| P8 | Verkauf | product | Provider of quarantine boxes for lithium-ion batteries | Proveedor de cajas de cuarentena para baterías de iones de litio |
| P9 | Verkauf | product | Which suppliers offer transport crates for lithium-ion batteries? | ¿Qué proveedores ofrecen cajones de transporte para baterías de iones de litio? |
| P10 | Verkauf | product | Which suppliers sell dangerous goods boxes for high-voltage batteries? | ¿Qué proveedores venden cajas para mercancías peligrosas para baterías de alta tensión? |
| P11 | Vermietung | product | Where can I rent quarantine boxes for defective lithium-ion batteries? | ¿Dónde puedo alquilar cajas de cuarentena para baterías de iones de litio defectuosas? |
| P12 | Havariefälle | service | Service provider for Europe-wide collection of lithium batteries after an incident | Proveedor de servicios para la recogida de baterías de litio en toda Europa tras un incidente |
| P13 | Havariefälle | service | Which providers dispose of lithium batteries after a warehouse or truck fire? | ¿Qué proveedores eliminan baterías de litio tras un incendio en almacén o de camión? |
| P14 | Entsorgung | service | Which company is best for disposing of lithium-ion batteries? | ¿Qué empresa es la mejor para la eliminación de baterías de iones de litio? |
| P15 | Transportboxen | product | What is the best transport box for lithium-ion batteries? | ¿Cuál es la mejor caja de transporte para baterías de iones de litio? |

**Balance je Sprache:** 10× Produkt/Behälter · 5× Batterielogistik (Produktschwerpunkt).
Neu ggü. den getrackten 8: Verkauf Transportkisten (P9), Verkauf Gefahrgutbox
Hochvolt/E-Auto (P10), Quarantänekiste-Miete (P11), Havarie-Abholung europaweit (P12),
Entsorgung nach Lager-/LKW-Brand (P13), allgemeine Entsorgung (P14),
Empfehlungs-Intent „beste Transportbox" (P15).

### Terminologie (idiomatische Fachbegriffe)
- **Gefahrgut** → EN *dangerous goods*, ES *mercancías peligrosas* (ADR).
- **Havariekiste / Havariefall** → EN *safety box for damaged … / after an incident*,
  ES *caja de seguridad para … dañadas / tras un siniestro* (siniestro = Schaden-/Havariefall).
- **Quarantäne** → EN *quarantine*, ES *cuarentena*.
- **Hochvoltbatterien** → EN *high-voltage batteries*, ES *baterías de alta tensión*.
- **Entsorgung** → EN *disposal*, ES *eliminación*.
- P1 vs P9 (Transportbox vs Transportkiste) sprachlich unterschieden: EN *box* vs
  *crate*, ES *caja* vs *cajón*.

## Quell-Zuordnung der 7 Zusatz-Prompts (DE-Original in Peec)
- P9 ← „Anbieter Transportkisten für Lithium-Ionen-Batterien" (96 %)
- P10 ← „Welche Anbieter verkaufen Gefahrgutboxen für Hochvoltbatterien?" (100 %)
- P11 ← „Wo kann ich Quarantänekisten für defekte Lithium-Ionen-Batterien mieten?" (81 %)
- P12 ← „Dienstleister Lithium-Batterie Havariefall Abholung europaweit" (91 %)
- P13 ← „Welche Anbieter entsorgen Lithium-Batterien nach einem Lagerbrand oder LKW-Brand?" (75 %)
- P14 ← „Bei welchem Unternehmen kann ich am besten Lithium-Ionen-Batterien entsorgen lassen?" (44 %)
- P15 ← „Bester Transportbehälter für Lithium Ionen Batterien" (52 %)
