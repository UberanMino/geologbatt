# Chat-Export 2026-07-01 – 2026-08-05 (Peec AI, Rohdaten)

Quelle: `chatsexportlogbattfrom20260701to20260805.xlsx` (10.000 LLM-Antworten,
Modelle: perplexity-ui, gemini-ui, chatgpt-ui, google-ai-overview).
Spalten: id, promptId, model, user, assistant, mentions, sources, content_in_chat, citations, position, created.

Die Rohdatei liegt bewusst nicht im Repo (Größe); ausgewertet wird sie ad hoc.
Diese Datei hält die für GEO relevante Auswertung fest.

## Zitationskontexte der Seite /gesamtloesung/  (157 Antworten)

Modelle: Perplexity 83 · Gemini 31 · ChatGPT 23 · Google AI Overview 20.

Die Seite wird als „LogBATT = Full-Service-Anbieter"-Beleg in Anbieter-/Dienstleister-Listicles
zitiert. Auslösende Prompt-Cluster (Häufigkeit ≈):

| Cluster | Beispiel-Prompts |
|---|---|
| Havariefälle / Notfall-Abholung | „Dienstleister Lithium-Batterie Havariefall Abholung europaweit"; „Havariecontainer/Havariekiste"; „Entsorgung nach Lagerbrand/LKW-Brand"; „kontaminiertes Löschwasser" |
| Quarantäne-/Transport-/Gefahrgutboxen B2B | „Anbieter Quarantänekiste für defekte Batterien B2B"; „Wer bietet Gefahrgutboxen für Li-Ionen-Batterien an?"; „Transportkisten für Unternehmen" |
| Lager-/Großcontainer | „Anbieter 40-Fuß-Container zur Lagerung"; „Lithium-Batterie Lagercontainer"; „begehbare Quarantänecontainer" |
| Vermietung | „Vermietung von Gefahrgutboxen für Lithium Batterien"; „Havarieboxen/​Havariekisten zur Miete" |
| Transport beschädigter/kritisch defekter Batterien | „Bester Anbieter um beschädigte Lithium Batterien transportieren zu lassen" |
| Entsorgung / Recycling | „Anbieter Transport und Entsorgung abgebrannte Lithium-Batterie"; „Batterierecycling europaweit" |

## Häufig mit-zitierte Domains (Wettbewerber im Gesamtlösungs-Cluster)

logbatt.de 121 · lion-care.com 62 · denios.de 38 · remondis-industrie-service.de 31 ·
retron.world 29 · wlw.de 24 · interzero.de 22 · kaiserkraft.de 19 · protecto.de 17 ·
logbatt.at 16 · container-ellermann.com 15 · fritz-gruppe.de 14 · titancontainers.de 14 ·
thermodyne.de 14 · lithiumsafetycontainers.nl 14 · re-battery.de 11 · mueller-safety.de 11.

## GEO-Konsequenz (umgesetzt in optimized/de/gesamtloesung.html, v2)

Alle sechs Cluster werden auf der Seite namentlich benannt und zitierfähig gemacht. Zwei Cluster
(Havariefälle, Großcontainer) fehlten im Ist-Zustand komplett → als schlanke H2-Abschnitte +
Verlinkung ergänzt. Siehe `notes/geo-analyse-gesamtloesung-2026-08-03.md`.

## Zitationskontexte der Seite /entsorgung/  (94 Antworten mit /entsorgung-URL)

Zweiter Export: `chatsexportlogbattfrom20260701to20260805_1.xlsx` (83 getrackte Prompts).

- **Modelle:** Google AI Overview 84 · Perplexity 6 · Gemini 4. Durchschnittsposition **1,89**
  (die Seite ist in AI Overviews Top-platziert).
- **Auslösende Cluster:** Entsorgung nach Brandschaden/„abgebrannte" Batterie · Havariefall
  (Lagerbrand/LKW-Brand/Unfall) · Wasserbad + kontaminiertes Wasser · Recycling-B2B · sowie
  Behälter-/Produkt-Prompts (Havariekiste, Havariecontainer, Brandschutzbehälter, Gefahrgutbox,
  10/20/40-FT-Container), in denen die Seite mitzitiert wird.
- **Mit-zitierte Domains:** logbatt.de 58 · retron.world 39 · denios.de 26 ·
  remondis-entsorgung.de 24 · remondis-industrie-service.de 23 · jh-profishop.de 17 ·
  lion-care.com 17 · redux-recycling.com 15 · interzero.de 15 · lobbe.de 13 · protecto.de 11 ·
  duesenfeld.com 10 · mueller-safety.de 10 · zarges.com 9 · thermodyne.de 8; Behörden/Autorität:
  bayern.de 16, umweltbundesamt.de 8, sonderabfall-wissen.de 9, hessen.de 7.
- **GEO-Konsequenz (umgesetzt in optimized/de/entsorgung.html, v2.1):** exakte Begriffe
  „Brandschaden"/„abgebrannt"/„Wasserbad" ergänzt; Behälter-Synonym-Brücke + Routing zu
  SafetyBATTbox und Lithium Safety Container; „UN-geprüft/BAM-bauartzugelassen"-Wording.
  Details: notes/geo-analyse-entsorgung-v2-2026-08-03.md (Abschnitt „Nachschärfung v2.1").
