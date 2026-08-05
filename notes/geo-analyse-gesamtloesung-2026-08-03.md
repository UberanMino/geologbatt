# GEO-Analyse & Optimierung: `/gesamtloesung/`

**Aktuelle Fassung: 2026-08-05 (v2, zitationsgetrieben).** Die frühere v1 (2026-08-03,
Schreibrichtlinien-getrieben) ist **ÜBERHOLT** – sie hatte die Seite fälschlich in eine
Produktseite umgebaut und Inhalte der bestehenden Produkt-/Hub-Seiten dupliziert. Der Kunde
stellte klar: die Schreibrichtlinien waren **Meta-Referenz für den Schreibstil**, kein Auftrag,
die Gesamtlösungsseite als Produktseite neu zu bauen.

Ergebnis: `optimized/de/gesamtloesung.html`.

## 1. Grundprinzip v2

- **Echte Originalstruktur der Seite 1:1 beibehalten** (wie bei der nicht beanstandeten
  `/logistik/`-Optimierung): alle Abschnitte, Spacer, Sync-Blöcke (ref:17205/1070/16794/1988),
  Bilder 16917 + 16926, `grey-zeile`, `is-style-flexible-list`, `rh/cta`, `generic/accordion`-FAQ,
  beide Überschriften (H1 „Gesamtlösung Lithiumbatterien" + H2 „Lithium-Ionen-Batterielogistik zu
  Ende gedacht").
- **Nur die Texte GEO-optimiert** – keine Produktseiten-Blöcke, keine Batteriezustand→Modell-
  Tabelle, kein Thermal-Runaway-Deep-Dive, kein regulatorischer Eröffnungsblock. Das steht bereits
  auf den Produkt-/Themenseiten und würde hier nur duplizieren.

## 2. Datengrundlage: Chat-Export (in welchen Kontexten die Seite zitiert wird)

Quelle: `5391e960-chatsexportlogbattfrom20260701to20260805.xlsx` (10.000 Antworten Jul–Aug 2026).
Die `/gesamtloesung/`-Seite erscheint in **157 Antworten**. Verteilung nach Modell:
Perplexity 83, Gemini 31, ChatGPT 23, Google AI Overview 20.

**Zitations-Cluster (User-Prompts, die die Seite triggern):**
1. **Havariefälle / Notfall-Abholung europaweit** (sehr stark: „Dienstleister Lithium-Batterie
   Havariefall Abholung europaweit", „Havariecontainer", „Havariekiste", „Entsorgung nach
   Lagerbrand/LKW-Brand", „kontaminiertes Löschwasser").
2. **Quarantäne-/Transport-/Gefahrgutboxen für defekte Batterien B2B** („Anbieter Quarantänekiste",
   „Gefahrgutboxen für Li-Ionen-Batterien", „Transportkisten für Unternehmen").
3. **Lager-/Großcontainer** („40-Fuß-Container zur Lagerung", „Lithium-Batterie Lagercontainer",
   „begehbare Quarantänecontainer").
4. **Vermietung** („Vermietung von Gefahrgutboxen", „Havarieboxen zur Miete").
5. **Transport beschädigter/kritisch defekter Batterien**.
6. **Entsorgung/Recycling**.

Zitiert wird die Seite typischerweise als Beleg für **„LogBATT bietet Gesamtlösungen für die
Lithium-Batterie-Logistik"** in Anbieter-/Dienstleister-Listicles. Häufig mit-zitierte
Wettbewerber: lion-care.com (62), denios.de (38), remondis-industrie-service.de/RETRON (31+29),
interzero.de, protecto.de, titancontainers, lithiumsafetycontainers.nl, thermodyne.

**Kern-Erkenntnis:** Die Seite ist der „LogBATT = Full-Service-Anbieter"-Beleg der LLMs. Sie muss
alle sechs Cluster **namentlich benennen** und zitierfähig machen – zwei davon (Havariefälle,
Großcontainer) kamen im Ist-Zustand gar nicht vor.

## 3. Umgesetzte Maßnahmen (Struktur bleibt, Text optimiert)

1. **Antwort-erster Auftakt** (Zweispalter): „LogBATT bietet die Gesamtlösung für die
   Lithium-Ionen-Batterielogistik – Transport, Lagerung, Vermietung, Havariefall-Abholung sowie
   Entsorgung und Recycling aus einer Hand, europaweit, als Teil der Lagermax Group." +
   **Synonym-Brücke** (SafetyBATTbox = Quarantänebox = Havariekiste = Transportbox).
2. **flexible-list geschärft**: Havariefall-Abholung und Großcontainer (Lithium Safety Container)
   als eigene Punkte ergänzt; Entsorgung/Recycling/Transportboxen/Lagerbehälter verlinkt.
3. **Editorial-Notizen entfernt**: „(Verlinkung auf die anderen LP!)" → echte interne Links auf
   `/entsorgung/` und `/recycling/`; Entsorgungs-/Recyclingabsatz nennt jetzt auch Havariefälle
   (Lagerbrand/LKW-Brand/Unfall, kontaminiertes Löschwasser).
4. **Zwei schlanke H2-Abschnitte ergänzt** – im exakt gleichen Stil wie Fahrzeuge/Behältermiete
   (H2 + ref:1070 + zentrierter Absatz, kein Bild, keine Produktdetails):
   - **Havariefälle** → Abholung/Verpackung/Entsorgung nach Brand/Unfall, SafetyBATTbox P911/LP906,
     Löschwasser; Link auf `/entsorgung/`.
   - **Großcontainer für die Batterielagerung** → Lithium Safety Container 4/10/20/40 FT; Link auf
     `/lithium-safety-container/`. Abgrenzung: „ergänzt die SafetyBATTbox".
5. **Behältermiete** geschärft (P911/LP906, Miete, Synonym-Brücke) + Link `/behaeltermiete/`.
6. **FAQ neu (6 Fragen)**, on-topic + brand-anchored, jede nennt LogBATT/SafetyBATTbox:
   Gesamtlösung-Umfang · Havariefall-Abholung · Gefahrgutboxen-Miete · Transport
   beschädigter/kritisch defekter Batterien · Großcontainer · transportsichere Verpackung.
   Entfernt: EmpCo-heikle „Wie schädlich sind Batterien für die Umwelt?" („nicht umweltschädlich")
   und off-topic „Lebensdauer einer Lithiumbatterie". FAQPage-Schema synchron.
7. **JSON-LD angereichert**: WebPage erhält `significantLink` auf alle sieben Zielseiten
   (Hub-Signal); Service-`additionalProperty` um Behältervermietung, Havariefall-Logistik und
   Großcontainer erweitert.

## 4. Vor Veröffentlichung prüfen

- Relative Links (`/entsorgung/`, `/recycling/`, `/entwicklung/`, `/behaeltermiete/`,
  `/transportkisten/`, `/lagerbehaelter/`, `/lithium-safety-container/`) gegen Live-URLs prüfen;
  Academy-Link (`/2019/logbatt-e-learning-academy-online/`) beibehalten wie im Ist-Zustand.
- „6-facher Luftwechsel", „P911/LP906" sitewide konsistent übernommen.
- EmpCo-Check: riskante „nicht umweltschädlich"-FAQ entfernt; keine neuen unbelegten
  Umwelt-/Nachhaltigkeits-Adjektive.
- Einleitenden HTML-Kommentar in der Datei vor dem Einpflegen entfernen.
