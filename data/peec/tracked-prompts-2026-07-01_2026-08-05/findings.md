# Strategische Auswertung – Peec-Tracking 01.07.–05.08.2026

Basis: 83 Prompts × 4 Modelle = 10.000 Antworten. Signale: Marken (`mentions`), Domains
(`sources`), LogBATT-Position (1–6). Caveat: keine Seiten-Ebene (siehe README).

## 1. Kernbefund: LogBATTs Problem ist Abdeckung, nicht Rang

LogBATT wird in **51 % aller Antworten** genannt/zitiert (5.127 / 10.000). **Wo** LogBATT
vorkommt, steht es fast immer vorne: **Ø-Position 1,5** (Median 1). Das Verbesserungspotenzial
liegt also nicht darin, besser platziert zu werden, sondern **in mehr Antworten überhaupt
aufzutauchen** – besonders in den unten genannten schwachen Clustern, Modellen und Sprachen.

## 2. Sichtbarkeit nach Modell – die Google-Oberflächen sind die Schwachstelle

| Modell | LogBATT-Abdeckung | Ø-Position |
|---|---|---|
| perplexity-ui | **81,0 %** | 1,19 |
| chatgpt-ui | **72,9 %** | 1,19 |
| gemini-ui | 61,0 % | 1,80 |
| google-ai-overview | **48,8 %** | 1,69 |

**Perplexity und ChatGPT sind LogBATTs Heimspiel.** Im **Google-Ökosystem (AI Overview + Gemini)**
ist die Abdeckung deutlich schwächer – hier steckt der größte Hebel. Google AI Overview zieht
stark Behörden-/Autoritätsquellen (umweltbundesamt.de, bayern.de, ADAC, Verbraucherzentrale) und
Marktplätze heran; genau dort fehlt LogBATT häufiger.

## 3. Sichtbarkeit nach Cluster

Zuordnung per Keyword-Priorität (recycl → havarie/brand/unfall → großcontainer/iso → entsorgung →
lagerung → behälter → miete → sonstige).

| Cluster | Prompts | LogBATT-Abdeckung | Ø-Pos | Haupt-Wettbewerber |
|---|---|---|---|---|
| Behälter (Transport/Quarantäne) | 24 | 72 % | 1,52 | DENIOS, Zarges |
| Entsorgung (allgemein) | 3 | 68 % | 1,53 | **RETRON** |
| Havarie/Brand/Unfall | 21 | 68 % | 1,52 | RETRON (Service), DENIOS/Paul Müller (Behälter) |
| Großcontainer/ISO | 11 | 66 % | 1,44 | DENIOS, Paul Müller, Bauer Südlohn |
| Lagerung/Lagerbehälter | 13 | 65 % | 1,41 | DENIOS, Zarges |
| Recycling | 6 | **48 %** | 1,20 | RETRON, LiBCycle, Redux/Duesenfeld (Domains) |
| Vermietung/Miete | 1 | 49 % | 1,00 | DENIOS |

**Recycling ist der schwächste Cluster** – und thematisch nicht die Aufgabe der Entsorgungsseite,
sondern der `/recycling/`-Seite. Behälter/Havarie/Großcontainer sind solide, aber mit klaren
Einzel-Lücken (Abschnitt 5).

## 4. Sprache: englische Prompts sind ein blinder Fleck

| Sprache | Prompts | LogBATT-Abdeckung |
|---|---|---|
| Deutsch | 79 | **67 %** |
| Englisch | 4 | **9 %** |

Die vier englischen Prompts (alle Behälter/Storage: „Best transport box…", „What fireproof
transport boxes…", „Which storage box…", „Best storage container…") laufen fast komplett an
LogBATT vorbei – dort dominieren **Zarges** und **DENIOS**. Kleiner Datenpunkt (nur 4 Prompts),
aber eine eindeutige, bislang unbespielte Richtung, falls internationale Sichtbarkeit ein Ziel ist.

## 5. Konkrete Chancen – schwächste Prompts (LogBATT-Abdeckung, Ø-Pos)

Prompts, in denen LogBATT thematisch passt, aber selten vorkommt – nach Priorität:

**Behälter/Storage (EN + „generische Beste-Behälter"-Fragen):**
- 3 % – Which storage box is suitable for damaged lithium-ion batteries? *(EN)*
- 6 % – What fireproof transport boxes are available…? *(EN)*
- 8 % – Was sind die besten Behälter für Lithium-Ionen-Akkus?
- 9 % – Best transport box for lithium-ion batteries *(EN)*
- 16 % – Best storage container for defective batteries *(EN)*
- 26 % – Bester Lagerbehälter für Lithium Ionen Akkus

**Recycling:**
- 29 % – Welches Unternehmen ist das beste für Li-Ionen-Akku-Recycling?
- 35 % – Wie finde ich einen Dienstleister für Batterierecycling im B2B-Bereich?
- 36 % – Bei wem kann ich am besten Li-Ionen-Akkus recyclen lassen?
- 44 % – Anbieter für Batterierecycling europaweit

**Havarie/Unfall (behörden-/produktdominiert):**
- 18 % – Wo kann ich einen nach einem Unfall defekten Akku entsorgen lassen? *(Behörden-Space)*
- 31 % – Welche Havariebehälter brauche ich für defekte Lithium-Akkus? *(Zarges/DENIOS)*
- 39 % – Firma für Havariebehälter Vermietung Deutschland *(Paul Müller/Zieglmeier)*
- 42 % – Spezialist für Lithium-Batterien im Wasserbad und kontaminiertes Löschwasser *(RETRON)*

**Lagerung:**
- 42 % – Bei welchem Anbieter kann ich am besten Lagerbehälter … kaufen? *(DENIOS)*
- 51 % – Welcher Gefahrgutcontainer für die Lagerung … ist am besten? *(DENIOS)*

Vollständige Liste mit Werten je Modell: `prompt-metrics.csv`.

## 6. Ableitungen für die GEO-Arbeit

1. **Google-Oberflächen priorisieren.** Der größte Sichtbarkeits-Hebel liegt bei Google AI
   Overview/Gemini (48–61 %). Autoritative, gut strukturierte, zitierfähige Inhalte
   (Definitionen, Tabellen, Normbezüge) zahlen dort besonders ein.
2. **Recycling ist eine eigene Baustelle** – `/recycling/` gezielt aufbauen; die Entsorgungsseite
   kann Recycling-Prompts nicht gewinnen.
3. **RETRON ist der Service-Gegner** (Entsorgung/Havarie/Recycling), **DENIOS der Produkt-Gegner**
   (alle Behälter/Container-Cluster). Siehe `competitors.md`.
4. **„Beste-Behälter"-Generikfragen und englische Prompts** sind offene Flanken bei Transport-/
   Lagerboxen – Produktseiten (Transportkisten, Lagerbehälter) entsprechend schärfen.
5. **Position ist kein Problem** – nicht auf Ranking optimieren, sondern auf Präsenz/Abdeckung.
