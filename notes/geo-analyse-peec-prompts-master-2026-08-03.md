# GEO-Analyse: Peec-Master-Prompt-Liste (Stand 2026-08-03)

Grundlage: `data/peec/prompts-master-2026-08-03.md` – alle 79 aktiv getrackten Prompts über
10 Themen-Cluster. Ergänzt/präzisiert die Befunde aus
`notes/geo-analyse-peec-2026-07-27_2026-08-03.md` (die 3 Chats + 2 Top-Brands-Snapshots).

## 1. Themen-Ranking: wo LogBATT stark bzw. schwach ist

| Rang | Thema | Ø Visibility | Ø Position | Ø SoV |
| --- | --- | --- | --- | --- |
| 1 | Vermietung von Gefahrgutboxen | 82% | 1,64 | 61% |
| 2 | Verkauf von Gefahrgutboxen | 78% | 2,52 | 31% |
| 3 | Lagerung | 63% | 1,91 | 48% |
| 4 | Transport | 61% | 1,62 | 43% |
| 5 | Storage Container | 54% | 2,35 | 33% |
| 6 | Havariefälle | 51% | 2,29 | 60% |
| 7 | Entsorgung | 47% | 3,15 | 44% |
| 8 | Transportboxen | 34% | 2,51 | 26% |
| 9 | Lagerbehälter | 31% | 2,15 | 22% |
| 10 | Recycling | 24% | 5,54 | 53% |

**Die Vermietung ist LogBATTs Kronjuwel** (82 % Visibility, Ø Position 1,6) – passt zur
Positionierung als Anbieter mit eigenem Mietpark und deckt sich mit dem in
`website/de/behaeltermiete.html` bereits vorhandenen Content.

**Recycling ist der klare Schwachpunkt**: Ø Position 5,5 bedeutet, dass LogBATT dort – wenn
überhaupt genannt – meist ganz hinten in der Antwort steht. Auffällig: **RETRON** (in den
bisherigen Top-Brands-Snapshots nur mit 8 % Visibility gelistet) taucht in **5 von 6
Recycling-Prompts und 11 von 11 Havariefälle-Prompts** auf – deutlich präsenter, als die
1-Wochen-Snapshots vermuten ließen. RETRON ist mit 61 Erwähnungen über alle 79 Prompts der
**zweit-/drittstärkste Wettbewerber** (nach DENIOS 62, vor Zarges 45) – nicht das Nischenprodukt,
als das es in den kurzfristigen Snapshots erschien.

## 2. Der "Beste/Empfehlung"-Effekt – statistisch klar belegt

9 Prompts sind mit `Beste/Empfehlung` getaggt (Formulierungen wie „Bester...", „Was ist der
beste...", „Welches Unternehmen ist das beste..."). Ihre Performance liegt deutlich unter dem
Schnitt der übrigen 70 Prompts:

| | Ø Visibility | Ø Share of Voice |
| --- | --- | --- |
| „Beste/Empfehlung"-Prompts (n=9) | **33 %** | **21 %** |
| Alle anderen Prompts (n=70) | 57 % | 44 % |

Zwei Prompts dieser Gruppe liegen sogar bei 0 % Visibility („Was sind die besten Behälter für
Lithium-Ionen-Akkus?", „Bester Lagerbehälter für Lithium Ionen Akkus"). **Interpretation:** Bei
superlativisch formulierten Anfragen verlangen LLMs erkennbar nach einer begründeten
Vergleichsbasis (Kriterien, Rankings, Vergleichstabellen, Drittmeinungen) – reine
Produktbeschreibungen reichen hier offenbar nicht, um als „bester Anbieter" genannt zu werden.
**Das ist der konkreteste, am klarsten belegte Hebel aus diesem Datensatz.**

## 3. Struktur-Lücken im Tracking selbst

- **Keine Marken-Prompts:** Alle 79 Prompts sind `non-branded`. Es wird nirgends getrackt, was
  LLMs antworten, wenn direkt nach „LogBATT" gefragt wird (Reputation, Fakten-Korrektheit,
  Verwechslungen). Empfehlung: 3–5 Marken-Prompts ergänzen (z. B. „Was ist LogBATT GmbH?", „Ist
  LogBATT seriös?", „LogBATT Erfahrungen").
- **Kein AT/internationaler Standort:** Alle Prompts sind `location: DE`, obwohl `logbatt.at`
  und `logbatt.com` bestätigt aktive Domains sind (siehe vorherige Analyse). Die
  AT-/internationale GEO-Sichtbarkeit ist aktuell komplett unvermessen.
- **Kaum informationelle Prompts** (nur 6 von 79): Das Set ist stark auf
  „Anbieter finden"-Absicht (commercial) getrimmt. Informationelle Prompts („Wie entsorgt man
  einen Lithium-Ionen-Akku", „Was ist ein Thermal Runaway") – also genau die Fragen, für die in
  diesem Repo bereits FAQ-/Glossar-Content existiert – werden kaum gemessen, obwohl sie
  vermutlich das größere Suchvolumen haben.

## 4. Zusammenhang mit den Top-Brands-Exporten (offene Zuordnung)

Ein direkter numerischer Abgleich mit den beiden bereits vorliegenden Top-Brands-Snapshots
(`data/peec/2026-07-27_2026-08-03/top-brands/export-12.md` und `-13.md`) bleibt uneindeutig, da
unterschiedliche Zeitfenster zugrunde liegen (Top-Brands: 1 Woche; diese Liste: rollierend seit
März 2026). Am plausibelsten passt **Export 12** (LogBATT #1, 75 % Visibility) zum starken
Cluster „Vermietung/Verkauf von Gefahrgutboxen", **Export 13** (DENIOS #1 vor LogBATT) eher zu
einem breiteren Feld wie „Lagerbehälter"/"Storage Container", in dem DENIOS strukturell stärker
zu sein scheint (u. a. wegen Position/SoV-Mustern). **Das bleibt eine Vermutung** – die exakten
Themennamen aus dem Peec-Dashboard wären weiterhin der zuverlässigste Beleg.

## 5. Priorisierte Folgemaßnahmen (ergänzt)

1. **Content für „Beste/Empfehlung"-Absicht schaffen:** Vergleichskriterien, Auswahlhilfen
   („Worauf sollten Sie bei der Wahl eines Lagerbehälters achten?"), ggf. Kundenstimmen/Reviews
   einbinden – gezielt für die 9 identifizierten Prompts plus verwandte Formulierungen.
2. **Recycling-Content grundlegend stärken** (schwächstes Thema, Ø Position 5,5) – RETRON und
   LiBCycle als spezialisierte Recycler ernst nehmen und in Peec als Wettbewerber ergänzen
   (siehe `data/competitors/README.md` – RETRON dort bereits als getrackt vermerkt, aber
   Bedeutung war unterschätzt).
3. **Lagerbehälter-Content prüfen:** Trotz vorhandenem, ausführlichem Content auf
   `lagerbehaelter.html` schwächstes Storage-Thema nach Recycling – ggf. Kandidat für die
   gleiche GEO-Analyse/Optimierung wie zuvor bei `/entsorgung/` durchgeführt.
4. **Tracking-Set erweitern:** 3–5 Marken-Prompts und einige AT/internationale Prompts ergänzen,
   sobald `logbatt.at`/`logbatt.com`-Content im Repo vorliegt.
