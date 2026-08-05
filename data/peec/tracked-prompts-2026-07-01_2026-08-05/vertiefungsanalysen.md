# Drei vertiefende Auswertungen – über Peecs Standard-Dashboard hinaus

Peec liefert nativ: Visibility, Share of Voice, Sentiment und Position pro Marke und
Themen-Cluster – das deckt `findings.md`/`competitors.md` bereits ab. Die drei Analysen
hier beantworten Fragen, die ein Marken-Dashboard **nicht** auflöst. Interaktive
Visualisierung: siehe verlinktes Artefakt (Diagramme + Tabellen mit Hover-Details).

Alle Zahlen verwenden die Definition „mentioned" = Marke im `mentions`-Feld genannt
(siehe Korrektur-Hinweis in `findings.md` Abschnitt 0). Datengrundlage: 10.000 Antworten,
83 Prompts × 4 Modelle.

## 1. Ko-Okkurrenz / Substitution – verdrängt ein Wettbewerber LogBATT?

**Frage:** Schließen sich LogBATT und ein bestimmter Wettbewerber gegenseitig aus (die
Antwort nennt entweder-oder, ein „Kopf-an-Kopf"-Duell), oder tauchen beide eher gemeinsam
auf (umfassende Listicle-Antworten)?

**Methode:** Für jeden Wettbewerber X: Erwartungswert für gemeinsames Vorkommen unter der
Annahme von Unabhängigkeit (`n(X) × n(LogBATT) / N`), verglichen mit dem tatsächlichen
gemeinsamen Vorkommen. **Lift = tatsächlich / erwartet.** Lift < 1 würde Substitution
bedeuten (X verdrängt LogBATT), Lift > 1 bedeutet Koexistenz (beide erscheinen häufiger
zusammen als durch Zufall zu erwarten). Nur Marken mit ≥ 50 Nennungen berücksichtigt.

| Wettbewerber | Nennungen | davon mit LogBATT | erwartet (Zufall) | Lift | Koexistenz-Rate |
|---|---|---|---|---|---|
| Zarges | 1.905 | 998 | 976,7 | **1,02** | 52,4 % |
| LiBCycle | 116 | 67 | 59,5 | 1,13 | 57,8 % |
| Genius | 433 | 268 | 222,0 | 1,21 | 61,9 % |
| DENIOS | 3.188 | 2.038 | 1.634,5 | 1,25 | 63,9 % |
| Bauer Südlohn | 399 | 270 | 204,6 | 1,32 | 67,7 % |
| Zieglmeier | 232 | 167 | 118,9 | 1,40 | 72,0 % |
| RETRON | 1.626 | 1.191 | 833,7 | 1,43 | 73,2 % |
| GelKoh | 360 | 265 | 184,6 | 1,44 | 73,6 % |
| Paul Müller | 832 | 620 | 426,6 | 1,45 | 74,5 % |
| DellCon | 80 | 68 | 41,0 | 1,66 | 85,0 % |
| Buncker | 65 | 57 | 33,3 | **1,71** | 87,7 % |

**Ergebnis: Kein einziger Wettbewerber zeigt einen Lift unter 1.** Es gibt in diesem
Datensatz **keine reine Substitutionsbeziehung** – kein Konkurrent, dessen Erscheinen
LogBATTs Chance auf Nennung systematisch senkt. Alle Werte liegen bei oder über der
Zufalls-Erwartung: Antworten mit Wettbewerbernennung sind tendenziell **umfassende
Listicle-Antworten**, die LogBATT eher mit-nennen als ausschließen.

**Einordnung:**
- **Zarges** (Lift 1,02) ist der einzige Wettbewerber nahe der Zufalls-Baseline – am
  ehesten ein „unabhängiger" Fall: Wo Zarges auftaucht, ist die LogBATT-Quote weder
  erhöht noch verringert. Am plausibelsten dort, wo einfache Produktvergleiche ohne
  Vollständigkeitsanspruch entstehen (v. a. die schwachen Superlativ-/EN-Prompts, siehe
  Analyse 2).
- **DENIOS und RETRON** (die mengenmäßig größten Konkurrenten) zeigen moderaten positiven
  Lift (1,25 / 1,43) – sie erscheinen häufig in denselben umfassenden Antworten wie
  LogBATT, nicht anstelle davon.
- **Praktische Konsequenz:** Das Sichtbarkeitsproblem lässt sich nicht durch „gegen einen
  bestimmten Wettbewerber gewinnen" lösen. Der Hebel liegt in Abschnitt 2 – bei
  Fragetypen, in denen LogBATT grundsätzlich seltener genannt wird, unabhängig davon, wer
  sonst noch vorkommt.

## 2. Phrasing-Sensitivität – dieselbe Frage, andere Worte, andere Antwort

**Frage:** Bei nahezu identischem Informationsbedürfnis (z. B. „Gefahrgutbox für
Batterien") – ändert die grammatische Form der Frage, ob LogBATT genannt wird?

**Methode:** Alle 83 Prompts nach Frageform klassifiziert (13 Muster), LogBATT-Nennungsrate
je Muster verglichen.

| Frageform | Beispiel | Prompts | LogBATT-Nennung |
|---|---|---|---|
| „Wer bietet/verkauft/vermietet X an?" (Verb) | „Wer bietet Gefahrgutboxen … an?" | 25 | **67,0 %** |
| „Wo kann ich X kaufen/mieten?" | „Wo kann ich Lagerbehälter … mieten?" | 4 | **66,1 %** |
| „Anbieter X" (Nominalphrase, kein Verb) | „Anbieter Transportkisten für …" | 15 | **64,6 %** |
| „Bester Anbieter für/um X" | „Bester Anbieter um beschädigte …" | 2 | 54,0 % |
| „Bei welchem Anbieter kann ich …" | „Bei welchem Anbieter kann ich … mieten?" | 6 | 49,8 % |
| „Welcher ist der beste Anbieter für X?" | | 4 | 41,9 % |
| „Firma für X" (Nominalphrase) | „Firma für Havariebehälter Vermietung …" | 2 | 39,0 % |
| „Welche X gibt es / brauche ich?" (Bedarfsfrage) | „Welche Quarantäneboxen … gibt es?" | 12 | 27,7 % |
| „Bester/e X" (Superlativ, kein Anbieter) | „Beste Transportbox für …" | 5 | 25,4 % |
| „Welcher X ist am besten?" (Produkt-Superlativ) | | 2 | 24,4 % |
| „Wie finde ich einen Dienstleister?" | | 1 | 15,8 % |
| „Dienstleister/Spezialist für X" (Nominalphrase) | | 1 | 14,3 % |
| Englische Frage | | 4 | **1,6 %** |

**Muster:** Formulierungen, die explizit nach einem **Anbieter/Verkäufer/Vermieter**
fragen (Verb-geführt: „bietet an", „verkauft", „kann ich … kaufen/mieten") schneiden
durchgängig mit 50–67 % ab. Formulierungen, die nach dem **besten Produkt** oder einem
**Bedarf** fragen, ohne explizit „Anbieter" zu sagen („Bester X", „Welche X brauche ich",
„X ist am besten") fallen auf 24–28 % – die Antwort wird dann eher aus
Produktkategorie-Wissen (Zarges, DENIOS als etablierte Produktmarken) generiert statt aus
einer Anbietersuche.

### Konkrete Paare – gleiches Thema, andere Formulierung

| Thema | Anbieter-Formulierung | Bedarfs-/Superlativ-Formulierung | Delta |
|---|---|---|---|
| Lagerbehälter | „Wo kann ich Lagerbehälter … mieten?" – **94 %** | „Bester Lagerbehälter für Lithium Ionen Akkus" – **4 %** | **90 pp** |
| Gefahrgutbox | „Wer bietet Gefahrgutboxen … an?" – **85 %** | „Welche Gefahrgutbox brauche ich …?" – **9 %** | **76 pp** |
| Quarantänebehälter | „Anbieter Quarantänekiste … B2B" – **72 %** | „Welche Quarantänebehälter brauche ich …?" – **9 %** | **63 pp** |
| Havariebehälter-Vermietung | „Wer vermietet Havarieboxen …?" – **93 %** | „Firma für Havariebehälter Vermietung Deutschland" – **38 %** | **55 pp** |
| Transportbox | „Anbieter Transportkisten für …" – **72 %** | „Beste Transportbox für …" – **22 %** | **50 pp** |

Bis zu **90 Prozentpunkte Unterschied bei identischem Bedarf** – das ist der stärkste
Hebel aller drei Analysen. Es ist kein Wettbewerbsproblem (Analyse 1), sondern ein
**Content-/Antwortmuster-Problem**: Produktseiten und FAQ beantworten aktuell primär die
Frage „Wer bietet das an?", aber zu selten die Frage „Was ist der/die beste X für meinen
Fall?" mit einer expliziten, bewertenden Aussage.

## 3. Antwortformat – Websuche vs. reines Trainingswissen

**Frage:** Hängt LogBATTs Nennungsrate davon ab, ob das Modell aktiv das Web durchsucht
hat oder nur aus seinem trainierten Wissen antwortet?

| Antwortformat (`content_in_chat`) | Antworten | LogBATT-Nennung | Ø-Position | Modell-Mix |
|---|---|---|---|---|
| Karten-/Local-Ergebnisse + Websuche | 353 | 55,2 % | 1,03 | 100 % ChatGPT |
| Reine Websuche | 6.100 | 53,7 % | 1,35 | Perplexity 39 %, Google AIO 32 %, ChatGPT 25 %, Gemini 5 % |
| Shopping-Ergebnisse + Websuche | 604 | 52,5 % | 1,50 | 99 % ChatGPT |
| **Keine Websuche (Trainingswissen)** | 2.941 | **45,6 %** | 1,80 | Gemini 75 %, Google AIO 19 % |

**Ergebnis:** Antworten mit **aktiver Websuche** nennen LogBATT in 52,5–55,2 % der Fälle;
Antworten, die das Modell **ohne Websuche direkt aus dem trainierten Wissen** beantwortet,
fallen auf **45,6 %** – der niedrigste Wert aller Formate, mit der schlechtesten
Ø-Position (1,80).

**Wichtiger Vorbehalt:** Format und Modell sind stark korreliert – „Keine Websuche" ist zu
94 % Gemini/Google AI Overview ohne Grounding, „Karten"/"Shopping" sind praktisch
ausschließlich ChatGPT. Die Aussage ist also nicht „Websuche verursacht bessere
Ergebnisse" im Vakuum, sondern konkret: **Wenn Gemini/Google AI Overview ohne aktive
Websuche aus dem eigenen (trainierten) Wissen antworten, ist LogBATT dort spürbar
schwächer vertreten als in Live-Web-Ergebnissen.**

**Konsequenz:** On-Page-Content, der zur Abfragezeit gefunden wird, schlägt bereits heute
das, was die Modelle über LogBATT „auswendig gelernt" haben. Der schwächste Punkt ist
nicht die eigene Website, sondern die **Präsenz von LogBATT in den Trainingsdaten/dem
Allgemeinwissen der Modelle** (Presseerwähnungen, Wikipedia-artige Drittquellen,
Branchenverzeichnisse) – ein Hebel, der über reine On-Page-GEO-Optimierung hinausgeht und
eher PR-/Backlink-/Verzeichnis-Arbeit betrifft.
