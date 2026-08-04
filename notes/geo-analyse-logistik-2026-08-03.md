# GEO-Analyse & Optimierung: `/logistik/` (2026-08-03)

Ergebnis: `optimized/de/logistik.html`. Grundlage: Ist-Zustand-Rohcode + Websuche.
**Besonderheit:** Für diese Seite existiert **kein Peec-Prompt mit `/logistik/` als Zielseite** –
sie wird laut Kunde aber **häufig abgerufen**. Der GEO-Ansatz ist deshalb ein anderer als bei
`/entsorgung/`.

## 1. Rolle der Seite

`/logistik/` ist keine klassische Landingpage für einen einzelnen Suchintent, sondern die
**Hub-/Übersichtsseite** für den gesamten Geschäftsbereich Batterielogistik. Sie ist der zentrale
Einstieg aus der Navigation (Startseite verlinkt prominent auf „Logistik") und bündelt sechs
Teilbereiche. Für GEO bedeutet das zwei Ziele:

1. **Zitierfähige Autoritäts-Aussagen** über LogBATTs Logistikangebot, die ein LLM bei Prompts
   wie „Was bietet LogBATT?", „Anbieter Lithium-Ionen-Batterielogistik" oder „beschädigte
   Batterien transportieren lassen" (Transport-Cluster: LogBATT dort bereits Position 1–2,
   56–63 % Visibility) als Antwortbaustein übernehmen kann.
2. **Vollständiges internes Routing** zu allen Geschäftsbereichen – eine gut vernetzte Hub-Seite
   verteilt Autorität im Site-Graph und hilft LLMs, die Angebotsstruktur zu verstehen.

## 2. Befunde zum Ist-Zustand

- **Design & Grundgerüst sind gut** (6 klar getrennte Teilbereiche mit Bild+Text-Spalten,
  `is-style-flexible-list`, Blumenstrauß-Gesamtlösungsgrafik, CTA). → bleibt erhalten.
- **Aber die Texte sind dünn und wenig zitierfähig:** Die Intro-Absätze führen nicht mit einer
  klaren Positionierung; die Fließtexte nennen kaum die harten Fakten, die LogBATT anderswo
  besitzt. Auf der ganzen Seite fehlen **RID, IMDG, IATA-DGR**, die **9.000+ Transporte**, die
  **Verfahrensfestlegung P911/LP906**, der **EfB-Status** und die Einordnung des **Milkrun**-Begriffs.
- **Kaputte/veraltete Verlinkung:** Die „Weitere Informationen"-Buttons zeigen auf die
  Backend-Domain (`117655.wd50.extern.regiohelden.de/gesamtloesung/` bzw. `/recycling/`) statt auf
  relative `logbatt.de`-Pfade. Der Abschnitt „Entsorgungs- und Recyclinglogistik" verlinkt nur
  `/recycling/`, **nicht** die eigentliche Entsorgungsseite `/entsorgung/`.
- **Fehlende Produkt-Wegweiser:** Die Seite erwähnt die SafetyBATTbox, routet aber nicht klar zu
  den drei Produktfamilien. Insbesondere die **Großcontainer (Lithium Safety Container)** kommen
  gar nicht vor – obwohl sie ein eigener, abgegrenzter Geschäftsbereich sind.
- **Kein Lexikon-Link**, obwohl passende Tiefeneinträge (ADR, UN 3480/3481, P911/LP906,
  Gefahrgutklasse 9, thermische Propagation, Transportbehälter) existieren.

## 3. Recherche-Grundlagen (belegte, zitierfähige Fakten)

- **6-facher Luftwechsel:** Regulatorisch gestützt – bei gedeckten/bedeckten Fahrzeugen muss für
  den Transport defekter Batterien ein **mindestens sechsfacher Luftwechsel des Laderaums pro
  Stunde** möglich sein. Der bestehende Satz zu den Fahrzeugen ist damit ein echtes Trust-Signal
  und wird geschärft.
- **ADR-Zustandskategorien:** ADR unterscheidet intakte, beschädigte/defekte und **kritisch
  defekte** Batterien; für kritisch defekte ist eine **BAM-Verfahrensfestlegung nach SV 376**
  (P911/LP906) nötig – die LogBATT besitzt.
- **Milkrun:** In der Batterielogistik ein getakteter Rundlauf, bei dem Behälter (SafetyBATTbox /
  SafetyBATTbox Storage) turnusmäßig geliefert, getauscht und abgeholt werden – erklärt, statt
  nur genannt.
- **Verkehrsträger-Regelwerke:** ADR (Straße), RID (Schiene), IMDG (See), IATA-DGR (Luft) – die
  vollständige Nennung positioniert LogBATT als Gefahrgut-Vollsortimenter.

## 4. Umgesetzte Maßnahmen (Struktur bleibt, Texte optimiert)

1. **H1 „Lithium-Ionen-Batterielogistik" + H2 „zu Ende gedacht"** unverändert (inkl.
   `doppelschrift`-Klasse) – wie vom Kunden vorgegeben.
2. **Intro-Zweispalter** neu getextet: führt jetzt mit einer klaren, zitierfähigen Positionierung
   („LogBATT bündelt die komplette Lithium-Ionen-Batterielogistik … aus einer Hand") und nennt
   die vier Verkehrsträger-Regelwerke sowie die 9.000+ Transporte.
3. **Rundum-Sorglos-Liste** (`is-style-flexible-list`) beibehalten, Punkte geschärft und um interne
   Links zu Transportboxen, Lagerbehältern und Großcontainern ergänzt.
4. **Sechs Teilbereich-Sektionen** beibehalten (gleiche Bilder/IDs, gleiche Gruppen-Klassen),
   Texte GEO-optimiert und Buttons auf **relative Pfade** korrigiert:
   - *Gesamtlösung* → Button `/gesamtloesung/`, Text nennt die komplette Supply-Chain.
   - *Entsorgungs- & Recyclinglogistik* → jetzt **zwei** Buttons: `/entsorgung/` **und**
     `/recycling/` (vorher fehlte die Entsorgungsseite).
   - *Fahrzeuge* → 6-facher Luftwechsel als belegtes Detail, ADR-Ausstattung.
   - *Behältermiete* → verlinkt jetzt explizit `/behaeltermiete/`, `/transportkisten/`,
     `/lagerbehaelter/`.
   - *Verpackungsschulungen* → **LogBATT Academy** (Button auf `logbatt-academy.com`).
   - *LogBATT Networksolution* → Netzwerkgedanke geschärft.
5. **NEUER, abgegrenzter Produkt-Abschnitt „Unsere Behälter für jeden Batteriezustand"**: routet
   klar getrennt zu den drei Produktfamilien – **Transportboxen** (`/transportkisten/`),
   **Lagerbehälter** (`/lagerbehaelter/`) und – abgegrenzt – **Großcontainer / Lithium Safety
   Container** (`/lithium-safety-container/`). Genau die vom Kunden gewünschte Produktabgrenzung.
   Nutzt das vorhandene 10-FT-Containerbild (ID 85495) aus der LSC-Seite und das Stil-Muster der
   übrigen Sektionen (grey-zeile / Spalten).
6. **JSON-LD angereichert:** WebPage + Service bleiben, Service-`additionalProperty` um
   Verkehrsträger (ADR/RID/IMDG/IATA-DGR), Transporterfahrung, EfB, P911/LP906 und
   6-fachen Luftwechsel erweitert; die WebPage erhält `significantLink`-Verweise auf alle
   verlinkten Geschäftsbereiche (Hub-Signal für LLMs).
7. **Interne Lexikon-Tiefenlinks** ergänzt (ADR, UN 3480/3481, P911/LP906, Gefahrgutklasse 9).

## 5. Vor Veröffentlichung prüfen

- Der Großcontainer-Abschnitt nutzt Bild-ID **85495** (10-FT-Containerfoto von der
  Lithium-Safety-Container-Seite). Falls dort noch nicht final, ggf. anderes Containerbild wählen.
- „9.000+ Transporte kritisch defekter Batterien" wird sitewide konsistent verwendet – hier
  übernommen.
- Buttons zeigten im Ist-Zustand auf die Backend-Domain; die neuen relativen Pfade
  (`/gesamtloesung/`, `/entsorgung/`, `/recycling/`) bitte gegen die Live-URLs prüfen.
- EmpCo-Check: keine unbelegten Nachhaltigkeits-/Umwelt-Adjektive ergänzt.
