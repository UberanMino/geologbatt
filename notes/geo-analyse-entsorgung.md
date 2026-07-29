# GEO-Analyse: `/entsorgung/` (Lithium-Ionen-Akku-Entsorgung)

Stand der Analyse: 2026-07-29. Grundlage: `website/de/entsorgung.html` (Ist-Zustand-Rohcode)
sowie Quervergleich mit strukturell weiter entwickelten Schwesterseiten (`gefahrgutlogistik.html`,
`entsorgung-speicherbatterien.html`).

## 1. Einordnung

`/entsorgung/` ist die zentrale **Pillar-Page** für das Thema „Lithium-Ionen-Akku entsorgen" –
eine der Kernfragen, die Endkunden **und** LLMs am häufigsten stellen („Wie entsorge ich einen
Akku?", „Wo entsorgt man Lithium-Batterien?"). Die Seite hat mit 11 FAQ-Fragen bereits die
größte FAQPage im ganzen Content-Bestand – ist strukturell und inhaltlich aber die am wenigsten
ausgereifte Seite ihrer Gewichtsklasse. Das ist der größte Hebel im gesamten Content-Bestand.

## 2. Strukturelle / technische Defizite (JSON-LD)

| # | Befund | Auswirkung auf GEO |
|---|---|---|
| 1 | **Kein `WebPage`- und kein `Service`-Entity.** Die Seite hat nur ein einzelnes `FAQPage`-Schema – anders als `gefahrgutlogistik.html` oder `entsorgung-speicherbatterien.html`, die zusätzlich `WebPage` + `Service` (mit `additionalProperty`, `provider`, `areaServed`) besitzen. | LLMs/Suchmaschinen fehlt die maschinenlesbare Entity „Entsorgungs-Service von LogBATT" mit Zielgruppe, Rechtsgrundlage, Zertifizierung – genau die Fakten, die für Zitierfähigkeit zählen. |
| 2 | **Kaputte Referenz:** `"isPartOf": {"@id": "https://www.logbatt.de/entsorgung/#webpage"}` im FAQPage-Block verweist auf einen `#webpage`-Knoten, der auf dieser Seite **nirgends definiert ist** – ein „dangling reference"-Fehler im Graph. | Structured-Data-Validatoren (Google Rich Results Test, Schema-Validator) werten das als unvollständigen Graph; im schlimmsten Fall wird der Zusammenhang zwischen FAQ und Seite nicht erkannt. |
| 3 | **Keine `BreadcrumbList`.** | Kleiner, aber kostenloser GEO-Baustein zur Einordnung der Seite in die Site-Hierarchie. |
| 4 | **Zwei FAQ-Fragen enthalten je zwei zusammengefasste Fragen** in einem `name`-Feld: „Wo entsorge ich Lithiumbatterien? Wo kann man Akkus entsorgen?" und „Wie werden Lithium-Ionen-Akkus entsorgt? Wie werden Lithiumbatterien entsorgt?". | `Question.name` sollte laut schema.org **eine** Frage enthalten. LLMs extrahieren Frage/Antwort-Paare am zuverlässigsten, wenn `name` atomar ist – zusammengesetzte Fragen verwässern die Zuordnung. |
| 5 | **Inhaltliche Redundanz zwischen FAQ-Einträgen:** mehrere Fragen beantworten praktisch dasselbe („Wie entsorgt man einen Lithium-Ionen-Akku fachgerecht?" vs. die beiden Doppel-Fragen aus Punkt 4) mit sich wiederholenden Fakten (Risikoanalyse, Verpackung, Pole abkleben). | Verwässert Relevanzsignale; ein LLM, das eine prägnante Antwort sucht, bekommt vier ähnliche Antworten statt einer autoritativen. |
| 6 | Keine `HowTo`-Auszeichnung, obwohl die Kern-Suchintention „**wie** entsorge ich..." explizit prozess-/schrittbasiert ist und der Fließtext bereits einen 3-Schritte- und einen 4-Schritte-Prozess enthält (nur nicht einheitlich strukturiert). | Verschenktes Potenzial für ein zusätzliches, gut zitierbares Antwortformat. |

## 3. Inhaltliche Defizite

- **Keyword-Stuffing statt natürlicher Sprache:** Die exakte Phrase „Lithium-Ionen-Akku(s)
  Entsorgung"/„entsorgen" taucht in praktisch jeder Überschrift und jedem zweiten Satz auf
  (klassisches 2018–2020er-SEO-Muster). GEO-Systeme bevorzugen aber **klare, natürlich
  formulierte Aussagen**, die sich 1:1 als Antwort zitieren lassen – nicht Keyword-Wiederholung.
- **Keine konkreten Rechtsgrundlagen mit Nummern/Aktenzeichen**, obwohl LogBATT diese Fakten an
  anderer Stelle im eigenen Content-Bestand bereits besitzt (siehe `lexikon.html`):
  - **AVV-Abfallschlüsselnummern 16 06 05** („andere Batterien und Akkumulatoren") und
    **16 01 21** („gefährlicher Abfall") – LogBATT ist hierfür laut Lexikon-Eintrag nach
    **§ 54 KrWG** zum Transport berechtigt.
  - Unterscheidung **Sammelentsorgungsnachweis** (< 20 t/Jahr/Abfallschlüssel/Adresse, via
    Beförderer) vs. **Einzelentsorgungsnachweis** (> 20 t, inkl. eANV-Pflicht) – ein sehr
    konkretes, für Unternehmenskunden hoch relevantes und gut zitierfähiges Faktum, das auf
    `/entsorgung/` selbst komplett fehlt.
  - Verweis auf **Batteriegesetz (BattG)** und **EU-Batterieverordnung** fehlt (wird nur auf
    `/nachhaltigkeit/` beiläufig erwähnt, nicht auf der eigentlichen Entsorgungs-Pillar-Page).
  - Diese Fakten liegen bereits geprüft im eigenen Corpus (`lexikon.html`) vor – es müssen keine
    neuen Behauptungen recherchiert, nur intern verlinkt und auf die relevanteste Seite gehoben
    werden.
- **Keine interne Verlinkung zum Lexikon.** Trotz des im Repo bereits dokumentierten
  GEO-Potenzials des Glossars (`DefinedTerm`-Kandidat) verlinkt `/entsorgung/` keinen einzigen
  Fachbegriff dorthin.
- **Fehlende Prozess-Klarheit:** Der Ablauf „Abholen → Verpacken → Befördern → Recyclinganlage"
  wird über die Seite verteilt in Fließtext erwähnt, aber nie als eine klare, nummerierte
  Schritt-Folge dargestellt (im Gegensatz zur klaren 3er- bzw. 4er-Liste, die für die
  „Herausforderungen" existiert).
- **Kein Bezug zu benachbarten Themen-Clustern:** Keine Verlinkung zu
  `/entsorgung-speicherbatterien/` (Firmenkunden/Großmengen) oder `/e-auto-batterie-entsorgung/`
  (wird nur am Ende einmal erwähnt) zur Stärkung des thematischen Netzwerks.

## 4. Was inhaltlich bereits gut ist (erhalten)

- Der Absatz „Was Sie nicht tun sollten" ist bereits konkret, praktisch und nicht
  keyword-gestuffed – Vorbildcharakter für den Rest der Seite.
- Die 3 Gründe „Warum ist die Entsorgung eine Herausforderung" sind bereits sauber als
  `<ol>` strukturiert.
- Der Trust-Signal „9.000+ Transporte kritisch defekter Batterien" ist stark und wird bereits
  konsistent sitewide verwendet – bleibt erhalten.

## 5. Maßnahmen (umgesetzt in `optimized/de/entsorgung.html`)

1. `WebPage` + `Service` + `BreadcrumbList` + `HowTo` + `FAQPage` als **ein zusammenhängender
   Graph** mit sauberen `@id`-Referenzen (`hasPart` statt kaputtem `isPartOf`), analog zum
   Muster von `gefahrgutlogistik.html`/`entsorgung-speicherbatterien.html`.
2. FAQ bereinigt: Doppel-Fragen in atomare `Question`-Knoten aufgeteilt, inhaltliche Dubletten
   zusammengeführt, auf **10 nicht-redundante** Frage/Antwort-Paare verdichtet.
3. Neuer Abschnitt „Rechtliche Grundlagen" mit AVV-Codes, § 54 KrWG, Sammel-/
   Einzelentsorgungsnachweis-Schwelle (20 t), BattG/EU-Batterieverordnung – plus interne Links
   zu den passenden Lexikon-Einträgen.
4. Ablauf als klare, nummerierte 5-Schritte-Sequenz (zusätzlich als `HowTo`-Schema ausgezeichnet).
5. Fließtext entschlackt: wiederholte Keyword-Phrasen reduziert, Aussagen direkt und
   antwortfähig formuliert (jeder Abschnitt beantwortet in den ersten 1–2 Sätzen die
   Abschnittsfrage – wichtig für Extraktion durch LLMs).
6. Interne Verlinkung zu `/entsorgung-speicherbatterien/`, `/e-auto-batterie-entsorgung/`,
   `/gefahrgutlogistik/` und `/transportkisten/` ergänzt.
7. Keine neuen, unbelegten Nachhaltigkeits-/Eco-Adjektive eingeführt (Seite war und bleibt
   EmpCo-unkritisch – bewusst kein „nachhaltig"/„umweltfreundlich" ergänzt).

## 6. Offener Punkt (sitewide, nicht seitenspezifisch)

Der Knoten `https://www.logbatt.de/#website` (`WebSite`-Entity) wird sitewide in mehreren
`isPartOf`-Referenzen erwartet, ist aber in keiner bisher eingepflegten Seite tatsächlich
definiert (vermutlich Teil eines nicht erfassten globalen Theme-Snippets). Sollte einmal
zentral geprüft/ergänzt werden – betrifft nicht nur `/entsorgung/`.

## 7. Rechtlicher Hinweis

Die Nennung von „EU-Batterieverordnung (EU) 2023/1542" im optimierten Content ist die korrekte
öffentliche Bezeichnung der seit 2023 geltenden EU-Verordnung; **vor Veröffentlichung sollte
Rechts-/Fachabteilung die exakte Artikel-Zuordnung gegenprüfen**, da dies (anders als reine
Content-Verdichtung) eine neue, bisher nicht im LogBATT-Bestand vorhandene Rechtsangabe ist.
