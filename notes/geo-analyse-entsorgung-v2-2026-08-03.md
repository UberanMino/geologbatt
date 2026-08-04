# GEO-Analyse & Neuaufbau: `/entsorgung/` (v2, 2026-08-03)

Ersetzt die erste Analyse (`geo-analyse-entsorgung.md`, ohne Peec-Daten erstellt). Grundlage
jetzt: Ist-Zustand-Rohcode + **reale Peec-Daten** (Havariefälle- und Entsorgung-Cluster) +
Websuche zu rankenden Inhalten.

Ergebnis: `optimized/de/entsorgung.html`

## 1. Ausgangslage laut Peec

### Themen-Cluster „Entsorgung" (3 Prompts) — Ø 47 % Visibility, Ø Position 3,15

| Prompt | Vis. | Pos. | Genannt |
| --- | --- | --- | --- |
| Welcher ist der beste Anbieter für Lithium-Ionen-Akku-Entsorgung? | 50 % | 3,40 | **RETRON**, LogBATT, RLG |
| Welcher ist der beste Anbieter für Lithium-Ionen-Batterien Entsorgung? | 47 % | 3,20 | **RETRON**, LogBATT |
| Bei welchem Unternehmen kann ich am besten Lithium-Ionen-Batterien entsorgen lassen? | 44 % | 2,85 | LogBATT, RETRON |

**Befund:** In zwei von drei Prompts wird **RETRON vor LogBATT** genannt. Alle drei sind
„beste/r"-Prompts — genau die Kategorie, die laut der Master-Prompt-Analyse systematisch
schlechter performt (33 % vs. 57 %), weil LLMs dort eine begründete Vergleichsbasis erwarten.

### Themen-Cluster „Havariefälle" (11 Prompts) — Ø 51 % Visibility, Ø SoV 60 %

Oben stark, unten schwach — ein klares Gefälle:

| Prompt | Vis. |
| --- | --- |
| Dienstleister Lithium-Batterie Havariefall Abholung europaweit | 91 % |
| Welcher Dienstleister ist auf die Entsorgung von Lithium-Batterien nach Havariefällen spezialisiert? | 88 % |
| Anbieter Transport und Entsorgung abgebrannte Lithium-Batterie | 81 % |
| Welche Anbieter entsorgen Lithium-Batterien nach einem Lagerbrand oder LKW-Brand? | 75 % |
| Anbieter Lithium-Batterie Entsorgung nach Brandschaden | 66 % |
| Anbieter Havariefall Lithium Batterie Entsorgung | 66 % |
| Welche Firmen entsorgen E-Auto Batterien nach einem Unfall? | 41 % |
| **Wer entsorgt Lithium-Batterien aus einem Wasserbad inklusive kontaminiertem Wasser?** | **19 %** |
| **Spezialist für Lithium-Batterien im Wasserbad und kontaminiertes Löschwasser** | **16 %** |
| **Wer übernimmt die Entsorgung im Havariefall bei Lithium-Batterien?** | **16 %** |
| **Wo kann ich einen nach einem Unfall defekten Akku entsorgen lassen?** | **6 %** |

## 2. Der zentrale Befund: zitiert, aber nicht genannt

Über die beiden neu gelieferten Havarie-Chat-Exporte (64 Antworten) hinweg:

- `logbatt.de` ist mit **42 Zitaten die meistzitierte Quelle überhaupt** (vor retron.world 25,
  remondis-industrie-service.de 25, interzero.de 22).
- LogBATT wird **50×** in Antworten genannt.
- Aber: **7× wurde `logbatt.de` als Quelle zitiert, ohne dass LogBATT in der Antwort vorkam.**

Beispiel (Perplexity, 02.08.2026, Prompt „Welche Anbieter entsorgen Lithium-Batterien nach einem
Lagerbrand oder LKW-Brand?"): `logbatt.de` steht in den Quellen, genannt werden aber ReBattery und
Elorec. Das heißt: **Die Seite wird gefunden und gecrawlt, liefert aber zu Brand-/Havariefällen
keine extrahierbare, zitierfähige Aussage.** Genau das ist der Hebel — der Ist-Zustand von
`/entsorgung/` enthält das Wort „Havarie", „Brand(schaden)", „Lagerbrand", „Löschwasser" oder
„Wasserbad" **kein einziges Mal**.

## 3. Wettbewerbsbild

**RETRON** (33 Nennungen) ist der Hauptkonkurrent in diesem Cluster. Laut Websuche ist RETRON ein
System von **REMONDIS** und produktzentriert (RETRON BOX, UN-zugelassene Sammelbehälter, Tausch-
und Entsorgungsservice). LogBATTs Differenzierung liegt also nicht im Behälter allein, sondern in
der **Dienstleistungstiefe**: eigener Fuhrpark, EfB-Status, Verfahrensfestlegung P911/LP906,
europaweites Netzwerk, 9.000+ Transporte kritisch defekter Batterien. Das muss die Seite
explizit aussprechen, statt es implizit zu lassen.

Auffällig: LLMs ziehen bei diesem Thema stark **behördliche/verbandliche Quellen** heran —
`dguv.de` (9×), `umweltbundesamt.de` (8×), `bg-verkehr.de` (7×), `bde.de` (12×), `bayern.de` (9×).
Wer inhaltlich auf demselben Regel-Niveau argumentiert (konkrete AVV-Schlüssel, Paragraphen,
Prüfvorschriften), wird eher als gleichrangige Fachquelle zitiert.

## 4. Erkenntnisse aus der Websuche

- **Kontaminiertes Löschwasser** ist ein eigenes, gut dokumentiertes Fachthema: Löschwasser aus
  Lithium-Batteriebränden enthält Fluoride und Schwermetalle (Kobalt, Nickel, Mangan) in
  Konzentrationen, die Einleitgrenzwerte um ein Vielfaches überschreiten; es gilt als gefährlicher
  Abfall und muss aufgefangen und behandelt werden. Größenordnung laut Fachpresse: **rund 20 m³
  kontaminiertes Wasser je gekühltem Fahrzeug**. Für diesen Aspekt gibt es kaum spezialisierte
  Anbieterinhalte → echte Content-Lücke, die zu den beiden 16–19 %-Prompts passt.
- **AVV-Einstufung** ist differenzierter als bisher auf der Seite dargestellt: Nach LfU Bayern
  kommen je nach Herkunft **16 02 15\*** (aus Elektrogeräten), **16 01 21\*** (aus Fahrzeugen)
  bzw. eine Hochstufung von **16 06 05** auf **16 06 05\*** in Betracht; ein eigener AVV-Schlüssel
  für Lithiumbatterien existiert noch nicht. Die Einstufung obliegt dem **Abfallerzeuger**.
- **Kritisch defekt / P911-LP906:** Für kritisch defekte Batterien ist nach SV 376 eine
  **Verfahrensfestlegung der BAM** (Regelwerk **BAM-GGR 024**) erforderlich. LogBATT hat dazu eine
  eigene Referenz-Meldung („die flexibelste Verfahrensfestlegung im Sinne der P911/LP906") —
  starkes, verlinkbares Trust-Signal, das auf der Entsorgungsseite bisher fehlt.

## 5. Umgesetzte Maßnahmen

1. **Drei-Ebenen-Aufbau** wie vom Kunden gewünscht: allgemeine Einordnung → B2B-Pflichten →
   Havariefälle (neuer, eigener Hauptabschnitt mit H3-Unterabschnitten zu Brand/Lagerbrand/
   LKW-Brand, Löschwasser & Wasserbad, kritisch defekten Batterien).
2. **Zitierfähige Kernsätze:** Jeder Abschnitt beginnt mit einer direkten Antwort auf die
   Abschnittsfrage (erste 1–2 Sätze), damit LLMs sie als Antwortbaustein extrahieren können.
3. **„Beste-Anbieter"-Lücke geschlossen:** Neuer Abschnitt „Woran Sie einen geeigneten
   Entsorgungspartner erkennen" mit 6 überprüfbaren Auswahlkriterien — liefert die
   Vergleichsbasis, die bei superlativischen Prompts fehlt, ohne Wettbewerber abzuwerten.
4. **Rechtsgrundlagen konkret:** AVV-Tabelle (16 06 05 / 16 01 21 / 16 02 15), § 54 KrWG,
   Sammel- vs. Einzelentsorgungsnachweis inkl. 20-t-Schwelle und eANV, BattG, EU-Batterie-VO,
   SV 376, BAM-GGR 024.
5. **Interne Verlinkung** deutlich ausgebaut (bisher nur 1 Link): Gefahrgutlogistik, Recycling,
   Transportkisten, Lagerbehälter, Behältermiete, E-Auto-Batterie-Entsorgung,
   Entsorgung-Speicherbatterien, Versicherungen, Über uns/Zertifizierungen, plus vier
   Lexikon-Tiefenlinks (Abfallschlüsselnummer, Nachweisverordnung, P911/LP906, Thermische
   Propagation) und die P911/LP906-Referenzmeldung.
6. **Externe Autoritätslinks** (neu, bewusst sparsam: 3 Stück) auf BAM, Umweltbundesamt und
   BG Verkehr — genau die Quellenklasse, die LLMs in diesem Cluster ohnehin heranziehen.
   Signalisiert Einordnung in den etablierten Regelrahmen statt Selbstreferenz.
7. **JSON-LD neu:** `WebPage` + `Service` + `HowTo` (5 Schritte) + `FAQPage` (14 Fragen, atomar,
   inkl. 4 neuer Havarie-Fragen) + `BreadcrumbList`, sauber über `@id`/`hasPart` verknüpft. Behebt
   zugleich die kaputte `isPartOf`-Referenz des Ist-Zustands (zeigte auf einen nirgends
   definierten `#webpage`-Knoten).
8. **Struktur & Stil 1:1 im Seitenmuster:** `grey-zeile`-Blöcke, `wp:rh/cta`, `ref:1070`-Trenner,
   Spacer in den Original-Höhen, `wp:generic/accordion` für FAQ, zweispaltige `wp:columns` für
   Intro-Absätze, vorhandenes Bild (`entsorgung-logbatt-1.jpg`, ID 16722) übernommen.
   Textstil an der Suchhelden-Vorlage orientiert (H2 als Frage, direkter Antwortsatz,
   fett markierte Fachbegriffe, Listen mit Begriff-Doppelpunkt-Erklärung).

## 6. Vor Veröffentlichung prüfen

- **AVV 16 02 15\*** ist neu in der Tabelle (Batterien aus Elektrogeräten). Im LogBATT-Bestand ist
  bislang nur die Berechtigung für **16 06 05** und **16 01 21** dokumentiert. Die Tabelle nennt
  16 02 15\* daher als allgemeine Einstufungsinformation, **nicht** als LogBATT-Berechtigung —
  bitte trotzdem fachlich gegenprüfen lassen.
- Die Größenordnung „rund 20 m³ Löschwasser je gekühltem Fahrzeug" stammt aus der Fachpresse, nicht
  aus LogBATT-Daten — als Branchenangabe formuliert („Fachpublikationen nennen…").
- Externe Links (BAM, UBA, BG Verkehr) sind neu für diese Seite — falls sitewide unerwünscht,
  ersatzlos streichbar.
- EmpCo-Check: bewusst keine unbelegten Nachhaltigkeits-/Umwelt-Adjektive ergänzt.
