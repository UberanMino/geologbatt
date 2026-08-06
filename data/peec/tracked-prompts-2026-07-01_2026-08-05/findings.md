# Strategische Auswertung – Peec-Tracking 01.07.–05.08.2026

Basis: 83 Prompts × 4 Modelle = 10.000 Antworten. Caveat: keine Seiten-Ebene (siehe README).

> **Korrektur (2026-08-05):** Die erste Fassung dieser Auswertung vermischte zwei
> unterschiedliche Signale unter der Bezeichnung „LogBATT kommt vor" – einmal nur die
> `mentions`-Spalte (Marke im Antworttext genannt, 51,3 %), einmal `sources` **oder**
> `mentions` (Marke genannt **oder** `logbatt.de` irgendwo als Quelle verlinkt, 65,9 %).
> Alle Zahlen unten verwenden jetzt durchgängig **eine** Definition: **„mentioned" = die
> Marke „LogBATT" steht im `mentions`-Feld der Antwort.** Das deckt sich exakt mit dem
> `position`-Feld (Position existiert nur, wenn LogBATT als Marke erkannt wurde) und ist
> damit die entscheidungsrelevanteste Metrik: eine LLM-Antwort, die LogBATT tatsächlich
> als Anbieter nennt, nicht nur eine Antwort, die irgendwo `logbatt.de` verlinkt.

## 0. Zwei unterschiedliche Signale – und eine Überraschung

„Marke genannt" (`mentions`, 51,3 %) und „Domain zitiert" (`sources`, 51,4 %) sind fast
gleich groß – aber **überwiegend unterschiedliche Zeilen**:

| Segment | Anteil |
|---|---|
| Nur `logbatt.de` als Quelle zitiert, Marke NICHT im Text genannt | 1.467 Antworten |
| Nur „LogBATT" im Text genannt, KEINE `logbatt.de`-Quelle verlinkt | 1.449 Antworten |
| Beides zugleich | 3.678 Antworten |
| Mindestens eines von beidem | 6.594 Antworten (65,9 %) |

Das ist selbst ein Befund: In ~1.467 Antworten wird die Domain als Link geführt, ohne dass
das Modell LogBATT im Fließtext als Anbieter nennt – eine **stille Zitation** ohne
Empfehlungswert. Umgekehrt nennen ~1.449 Antworten die Marke aus dem Trainingswissen,
ohne aktiv auf die Website zu verlinken. Für alle folgenden Abschnitte zählt nur die
strengere, aussagekräftigere Definition (Marke im Text genannt = „mentioned").

## 1. Kernbefund: LogBATTs Problem ist Abdeckung, nicht Rang

LogBATT wird in **51,3 % aller Antworten** als Marke genannt (5.127 / 10.000). **Wo**
LogBATT vorkommt, steht es fast immer vorne: **Ø-Position 1,47** über alle Antworten mit
Nennung. Das Verbesserungspotenzial liegt also nicht darin, besser platziert zu werden,
sondern **in mehr Antworten überhaupt genannt zu werden**.

## 2. Sichtbarkeit nach Modell – Gemini und ChatGPT vorn, Google AI Overview schwach

| Modell | LogBATT-Nennung | Ø-Position |
|---|---|---|
| **gemini-ui** | **60,4 %** | 1,80 |
| **chatgpt-ui** | **57,5 %** | 1,19 |
| perplexity-ui | 48,2 % | 1,19 |
| **google-ai-overview** | **38,9 %** | 1,69 |

Mit der korrigierten Metrik dreht sich die Modell-Reihenfolge gegenüber einer ersten,
fehlerhaften Einschätzung: **Perplexity fällt von Platz 1 auf Platz 3** – Perplexity
verlinkt `logbatt.de` zwar häufig als Quelle, nennt die Marke im sichtbaren Text aber
seltener namentlich als Gemini/ChatGPT (siehe Abschnitt 0). **Google AI Overview bleibt in
beiden Betrachtungen die schwächste Oberfläche** – dort dominieren häufiger
Behörden-/Marktplatz-Domains statt Markenname-Empfehlungen.

## 3. Sichtbarkeit nach Cluster

| Cluster | Prompts | LogBATT-Nennung | Ø-Pos |
|---|---|---|---|
| Behälter (Transport/Quarantäne) | 24 | 58,9 % | 1,52 |
| Großcontainer/ISO | 11 | 58,4 % | 1,44 |
| Entsorgung (allgemein) | 3 | 52,0 % | 1,53 |
| Havarie/Brand/Unfall | 21 | 50,0 % | 1,52 |
| Lagerung/Lagerbehälter | 13 | 49,8 % | 1,41 |
| Vermietung/Miete | 1 | 40,3 % | 1,00 |
| Sonstige | 4 | 36,2 % | 1,16 |
| **Recycling** | 6 | **27,7 %** | 1,20 |

**Recycling ist der schwächste Cluster** – thematisch nicht die Aufgabe der
Entsorgungsseite, sondern der `/recycling/`-Seite.

## 4. Sprache: englische Prompts sind praktisch unsichtbar

| Sprache | Prompts | LogBATT-Nennung |
|---|---|---|
| Deutsch | 79 | 52 % |
| Englisch | 4 | **2 %** |

Die vier englischen Prompts (alle Behälter/Storage) laufen fast komplett an LogBATT
vorbei – dort dominieren **Zarges** und **DENIOS**. Kleiner Datenpunkt (nur 4 Prompts),
aber eine eindeutige, unbespielte Richtung für internationale Sichtbarkeit.

## 5. Vertiefende Auswertungen (neu, mit Visualisierung)

Drei zusätzliche Analysen, die über Peecs Standard-Dashboard (Visibility/SoV/Position pro
Marke) hinausgehen – Details, Zahlen und Diagramme in `vertiefungsanalysen.md`:

1. **Ko-Okkurrenz/Substitution:** Verdrängt ein Wettbewerber LogBATT aus Antworten, oder
   taucht LogBATT einfach seltener generell auf? Ergebnis: **kein einziger Wettbewerber
   zeigt einen negativen Zusammenhang** – LogBATTs Fehlen ist nicht auf einen bestimmten
   Konkurrenten zurückzuführen, sondern auf grundsätzliche Abwesenheit in bestimmten
   Fragetypen (siehe 6.).
2. **Phrasing-Sensitivität:** Bei nahezu identischem Bedarf schwankt die LogBATT-Nennung
   je nach Formulierung um bis zu **90 Prozentpunkte**. Anbieter-suchende Formulierungen
   („Wer bietet X an?", „Wo kann ich X mieten?") schneiden systematisch besser ab als
   Superlativ-/Bedarfsformulierungen („Bester X", „Welche X brauche ich?"). **Im
   Wettbewerbsvergleich (Abschnitt 2b) ist dieser Effekt LogBATT-spezifisch in der Höhe:**
   LogBATT fällt bei Produkt-Superlativfragen am stärksten aller Marken ab, während Zarges
   sich umgekehrt verhält (dort *stärker*) – Zarges/DENIOS sind als Produktmarken verankert,
   LogBATT als Dienstleister.
3. **Antwortformat:** Antworten, die auf **aktiver Websuche** beruhen, nennen LogBATT
   häufiger (52–55 %) als Antworten aus **reinem Trainingswissen ohne Websuche** (45,6 %,
   v. a. Gemini/Google AI Overview ohne Grounding).

## 6. Ableitungen für die GEO-Arbeit

1. **Die SafetyBATTbox als Produktmarke etablieren** (Abschnitt 5.2 + 2b): Der Phrasing-Hebel
   ist bei genauerem Hinsehen ein **Entitäts-Problem** – LogBATT ist als *Dienstleister*
   verankert, nicht als *Produkt*, und verliert deshalb „Bester X"-Fragen an Produktmarken
   wie Zarges/DENIOS. Konsequenz: die SafetyBATTbox als eigenständige, benennbare Produktmarke
   aufbauen (klarer Produktname, Vergleichsinhalte „SafetyBATTbox vs. …", Produktentität in
   Verzeichnissen/Drittquellen) – nicht nur FAQ-Formulierungen anpassen.
2. **Google-Oberflächen und Trainingswissen-Antworten priorisieren** (Abschnitt 2 + 5.3):
   Strukturierte, autoritative, zitierfähige Inhalte zahlen dort am meisten ein, wo LogBATT
   aktuell am schwächsten ist.
3. **Recycling ist eine eigene Baustelle** – `/recycling/` gezielt aufbauen.
4. **Kein Wettbewerber „stiehlt" LogBATT gezielt Sichtbarkeit** – die Lücke ist Abwesenheit
   in bestimmten Fragetypen, nicht Verdrängung durch einen einzelnen Gegner.
5. **Position ist kein Problem** – nicht auf Ranking optimieren, sondern auf Nennung.
