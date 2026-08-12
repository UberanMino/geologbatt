# GEO-Visibility-Tracker

Internes Analyse-Tool, das die Kernfunktionen von Peec AI nachbildet: definierte
Prompts laufen regelmäßig gegen mehrere KI-Antwortoberflächen; von jeder Antwort
werden der **volle Antworttext** und **jede einzelne zitierte Quelle** erfasst.
Darauf setzt eine separate Auswertung auf (Markennennungen, Sentiment,
Share of Voice) — und, gleichrangig, die Citation-/Source-Analyse.

> **Stand: Schritt 1 + 2 abgeschlossen** — Ebene 1 (Rohdaten-Ingestion, Engine
> `chatgpt`) und Ebene 2 (Auswertungs-Layer, Claude Haiku 4.5). Offen: die
> restlichen drei Engines, Scheduler und Dashboard.

---

## Die zwei Ebenen

```
   SearchApi (chatgpt | perplexity | gemini | google_ai_overview)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ EBENE 1 — Rohdaten-Ingestion  (Source of Truth, KI-unabhängig)  │
│                                                                  │
│   runs.raw_response   voller Antworttext (Markdown)             │
│   runs.raw_payload    komplette Provider-JSON-Antwort           │
│   citations           JEDE zitierte Quelle als eigene Zeile     │
│   domains             jede je zitierte Domain (offene Entdeckung)│
│                                                                  │
│   geotracker/ingest.py — importiert NICHTS aus Ebene 2          │
└─────────────────────────────────────────────────────────────────┘
        │  liest (nur lesend)
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ EBENE 2 — Auswertungs-Layer  (Claude Haiku 4.5, wiederholbar)   │
│                                                                  │
│   Modell liefert:  Marken in Reihenfolge, Sentiment,            │
│                    Problem-Narrativ-Verankerung                 │
│   Wir rechnen:     mention_rank, logbatt_position,              │
│                    share_of_voice (deterministisch)             │
│                                                                  │
│   geotracker/evaluate/ — liest nur, scrapt nie                  │
└─────────────────────────────────────────────────────────────────┘
```

Zwei Zusagen, die im Code festgehalten sind:

1. **Ebene 1 braucht Ebene 2 nicht.** `ingest.py` hat keinen Import aus dem
   Auswertungs-Layer und keinen Anthropic-Aufruf. Ohne `ANTHROPIC_API_KEY`
   läuft die Ingestion vollständig durch. Test:
   `test_evaluation_layer_is_not_required`.
2. **Nichts wird überschrieben.** Jeder Lauf legt einen neuen `runs`-Datensatz
   an, jeder Auswertungslauf eine neue `evaluations`-Zeile (`is_current`-Flag,
   alte bleiben stehen). Auch Fehlläufe werden gespeichert (`status = error` /
   `deferred`) — inklusive des Fehler-Bodys.

---

## Technischer Stack — und warum

| Baustein | Wahl | Begründung |
| --- | --- | --- |
| Backend | **Python** (FastAPI ab Schritt 3) | Ebene 2 läuft über das Anthropic-SDK (Prompt Caching, Batch API) — dort ist Python die reifste Anbindung. APScheduler ist die im Auftrag genannte Scheduler-Wahl und ebenfalls Python. Ein Node-Backend würde für Ebene 2 einen zweiten Prozess erzwingen. |
| Datenspeicher | **SQLite** + nummerierte SQL-Migrationen | Eine Datei, kein Server, WAL-Modus (Scheduler schreibt, Dashboard liest). Bei ~316 Läufen/Tag im Vollausbau ist das auf Jahre hinaus die richtige Größenordnung. |
| Ebene 1 | Standardbibliothek (`urllib`, `sqlite3`) | Einzige Dependency ist PyYAML für die Seeds. Die Ingestion soll auch dann laufen, wenn sonst nichts installiert ist. |
| Frontend | HTML/JS über REST (Schritt 3) | Filter- und Visualisierungslogik im Browser, Secrets bleiben serverseitig. |

---

## Schema

`geotracker/migrations/001_initial.sql` — vollständig kommentiert. Kurzfassung:

| Tabelle | Ebene | Zweck |
| --- | --- | --- |
| `prompts` | 1 | text, category, country, language, engines[], active, created_at |
| `runs` | 1 | ein Lauf = Prompt × Engine × Land × Zeitpunkt. `raw_response` (voller Text) + `raw_payload` (komplettes Provider-JSON) |
| `citations` | 1 | **jede** zitierte Quelle als eigene Zeile: cited_url, cited_domain, title, snippet, citation_rank, source_type, is_known |
| `domains` | 1 | Register **aller** je zitierten Domains — offene Entdeckung, Basis für Domain-Ranking + „Neu entdeckt" |
| `brands` / `brand_domains` | 1 ⇄ 2 | Seed = bekannte Wettbewerber; Ebene 2 darf neue anlegen (`is_known = 0`) |
| `evaluations` | 2 | logbatt_mentioned, logbatt_position, sentiment, problem_narrative_anchored, share_of_voice, raw_classifier_output |
| `brand_mentions` | 2 | mention_rank = Reihenfolge der Nennung **im Antworttext** |

### Bewusste Abweichungen vom Entwurf (jeweils additiv)

- **`runs.raw_payload`** — zusätzlich zum Antworttext wird das komplette
  Provider-JSON gespeichert. Damit lassen sich Citations neu parsen, wenn wir
  den Parser ändern, **ohne erneut zu scrapen**. Das ist dieselbe Logik, die für
  Ebene 2 gefordert ist, konsequent auf Ebene 1 angewandt.
- **`citations.origin`** (`cited` | `retrieved`) — SearchApi liefert bei ChatGPT
  zwei Blöcke: `reference_links` (tatsächlich zitiert) und `web_results` (die
  volle abgerufene Trefferliste). Beides wird roh gespeichert, aber getrennt
  markiert. **Alle Citation-Metriken rechnen ausschließlich auf `origin='cited'`.**
  `retrieved` beantwortet die für GEO sehr nützliche Frage „wo werden wir
  gefunden, aber nicht zitiert?".
- **`domains`-Register + `brand_domains`** — nötig, damit `source_type =
  competitor` überhaupt bestimmbar ist (Domain → Marke) und damit die
  Klassifikation **wiederholbar** ist: `reclassify-domains` rechnet nach einer
  Änderung an den Seeds alle gespeicherten Citations neu durch, ohne zu scrapen.
- **`brands.is_competitor`** — trennt echte Wettbewerber von Partnern
  (lithiumsafetycontainers.nl ist laut `data/competitors/README.md` **kein**
  Wettbewerber, sondern Vertriebspartner). Ohne dieses Flag würde der Partner in
  den Share-of-Voice-Vergleich rutschen.
- **`runs.status = 'deferred'`** — „defer"-Fälle werden protokolliert statt
  verworfen.

---

## ⚠️ Land & Sprache — Befund aus der SearchApi-Doku

Die Doku wurde am **2026-08-12** live geprüft (nicht geraten). Ergebnis:

| Engine | dokumentierte Parameter | Location / `gl` / `hl`? |
| --- | --- | --- |
| `chatgpt` | `q`, `web_search`, `expand_entities`, `engine`, `api_key`, `zero_retention` | **nein** |
| `perplexity` | `q`, `sources`, `engine`, `api_key`, `zero_retention` | **nein** |
| `gemini` | `q`, `engine`, `api_key`, `zero_retention` | **nein** |
| `google_ai_overview` | `page_token`, `engine`, `api_key`, `zero_retention` | **nein** (indirekt, siehe unten) |

`location`, `gl`, `hl` und `uule` gibt es nur auf der klassischen
`google`-Engine. Für `google_ai_overview` heißt das: die Lokalisierung passiert
auf dem **vorgelagerten `google`-Call**, aus dem der `page_token` stammt
(`ai_overview.page_token`, **Gültigkeit unter 1 Minute** — der Zwei-Schritt-Call
muss also unmittelbar hintereinander laufen).

**Was daraus für Ebene 1 folgt (dokumentierte Annahme, nichts geraten):**

- **Sprache** wird über die **Sprache des Prompt-Textes** gesteuert. Für
  `perplexity` und `gemini` sagt die Doku das ausdrücklich zu („the answer is
  returned in the same language as your query"). Unsere Prompts sind deutsch,
  die Antworten kommen deutsch.
- **Land** ist für `chatgpt`/`perplexity`/`gemini` heute eine reine
  **Auswertungs-Dimension** (`prompts.country`, `runs.country`) und **kein**
  Request-Parameter. Wir wissen, für welchen Markt ein Prompt gedacht ist, aber
  wir können der Engine den Markt nicht mitgeben.

**Offene Frage an SearchApi** (vor dem Ausbau auf weitere Länder zu klären):
Gibt es für die KI-Engines einen undokumentierten oder geplanten
Location-Parameter — und wenn nein, aus welcher Region werden die Sessions
gefahren? Solange das offen ist, sind Ländervergleiche außerhalb von DE nicht
belastbar. Sobald es einen Parameter gibt, ist er in
`geotracker/searchapi/parsers.py::build_params` an genau einer Stelle
nachzutragen.

---

## Einrichtung

```bash
cd tools/geo-tracker
python3 -m pip install -r requirements.txt

cp .env.example .env       # SEARCHAPI_API_KEY eintragen
python3 -m geotracker init-db
python3 -m geotracker seed
```

`seed` legt an (idempotent, löscht nie):
- **79 Prompts** aus `data/peec/prompts-master-2026-08-03.md`, 1:1 übernommen
  inklusive der 10 Peec-Themen-Cluster als `category` — damit unsere Zahlen
  direkt gegen Peec gegengeprüft werden können.
- **20 Brands** + 29 Domains (Wettbewerber-Seed aus dem Auftrag, ergänzt um die
  in `data/competitors/README.md` identifizierten Anbieter) und 1 Partner.
- **38 Domains** im Register (2 owned, 36 earned_media).

## Befehle

```bash
python3 -m geotracker ingest --engine chatgpt --limit 5     # Ebene 1: scrapen + roh speichern
python3 -m geotracker ingest --engine chatgpt --dry-run     # nur zeigen, was liefe
python3 -m geotracker runs                                  # Läufe auflisten
python3 -m geotracker show-run 1 --full                     # Lauf inkl. aller Citations
python3 -m geotracker domains                               # Domain-Ranking (zitierte Quellen)
python3 -m geotracker reclassify-domains                    # source_type neu berechnen, ohne zu scrapen
```

`ingest` läuft **sequenziell und gedrosselt** (Default 2 s Pause), respektiert
ein hartes Limit pro Aufruf (`GEOTRACKER_MAX_RUNS`) und überspringt Prompts, die
heute schon erfolgreich gelaufen sind (`--force` hebt das auf). Fehlgeschlagene
Läufe gelten **nicht** als erledigt und werden beim nächsten Aufruf erneut
versucht.

## Ebene 2 — Auswertungs-Layer

Eigener, jederzeit wiederholbarer Befehl auf **bereits gespeicherten** Läufen.
Er liest nur `runs.raw_response` und schreibt `evaluations` + `brand_mentions`;
es wird nie erneut gescrapt.

```bash
python3 -m geotracker evaluate --since 2026-08-01            # Batch API (Default)
python3 -m geotracker evaluate --engine chatgpt --limit 20 --sync
python3 -m geotracker evaluate --re-run --category Recycling # nach Logikänderung
python3 -m geotracker evaluate --dry-run                     # was liefe, + Cache-Prefix-Größe
python3 -m geotracker evaluate-collect msgbatch_...          # Batch später einsammeln
python3 -m geotracker evaluations --run-id 1 --raw           # Ergebnis inkl. Modell-JSON
```

### Arbeitsteilung Modell ↔ Code

Das ist die zentrale Design-Entscheidung dieses Layers:

| Aufgabe | Wer | Warum |
| --- | --- | --- |
| Marken im Text erkennen, **in Reihenfolge** | Modell | braucht Sprachverständnis |
| Sentiment gegenüber LogBATT | Modell | dito |
| Problem-Narrativ-Verankerung | Modell | dito |
| `mention_rank` | Code | folgt zwingend aus der Reihenfolge |
| `logbatt_position` | Code | = Rang von LogBATT in derselben Liste |
| `share_of_voice` | Code | reine Arithmetik — ein Modell rechnen zu lassen wäre eine vermeidbare Fehlerquelle |

Widersprechen sich Modell und Ableitung (z. B. `logbatt_mentioned: true`, aber
LogBATT fehlt in der Markenliste), **gewinnt die Ableitung** und der Widerspruch
wird protokolliert. Die rohe Modellantwort landet unverändert in
`evaluations.raw_classifier_output` — inklusive der Felder, die wir überschreiben.

### Markenabgleich und offene Entdeckung

Extrahierte Namen werden normalisiert abgeglichen (Kleinschreibung,
Umlaute, Rechtsform, Satzzeichen) — „ZARGES", „Zarges GmbH" und
„Zarges Aluminium" treffen dieselbe Marke. Was **nicht** matcht, wird als neue
Marke angelegt (`is_known = 0`, `is_competitor = 1`) statt verworfen. Die
Einstufung als Partner trifft niemand automatisch.

### Wiederholbarkeit

Jeder Auswertungslauf legt eine **neue** `evaluations`-Zeile an und setzt
`is_current` der vorherigen auf 0 — nichts wird gelöscht, Logikänderungen
bleiben nachvollziehbar. `EVALUATOR_VERSION` steht in `evaluate/prompt.py`:
Läufe, die mit der aktuellen Version schon ausgewertet sind, werden
übersprungen; eine **neue Version macht automatisch alle Läufe wieder fällig**,
ohne dass jemand etwas zurücksetzen muss. `--re-run` erzwingt es ad hoc.

### Kosten — und ein Befund zum Prompt Caching

- **Batch API ist der Default**, weil der tägliche Lauf keine Echtzeit braucht:
  **50 % günstiger**, meist unter einer Stunde fertig, garantiert unter 24 h.
  `--sync` gibt es für Ad-hoc-Prüfungen.
- **Prompt Caching ist korrekt implementiert** (konstanter Systemprompt mit
  Cache-Breakpoint, alles Volatile dahinter) — und ein Test hält fest, dass die
  offene Brand-Entdeckung den Prefix **nicht** verändert, weil neu entdeckte
  Marken bewusst nicht in den Systemprompt wandern.
- **Aber:** Claude Haiku 4.5 cached erst ab **4096 Tokens** Prefix. Unser
  Systemprompt liegt bei ~4.600 Zeichen (**grob geschätzt ~1.400 Tokens**), also
  darunter — dann passiert schlicht nichts: kein Fehler, nur
  `cache_creation_input_tokens = 0`. Der Wert ist eine Schätzung; `evaluate`
  gibt die tatsächlichen Cache-Zähler nach jedem Aufruf aus, sobald ein Key
  vorliegt, und `--dry-run` zeigt die Prefix-Größe.
- **Empfehlung:** so lassen. Die Ersparnis wäre klein (~0,4 €/Tag im Vollausbau),
  und den Prompt nur aufzublähen, um eine Cache-Schwelle zu reißen, wäre der
  falsche Grund. Sobald echte Antworten vorliegen, gehören ohnehin ein paar
  Few-Shot-Beispiele in den Systemprompt — das verbessert die Klassifikation
  **und** schiebt ihn nebenbei über 4096 Tokens.

## Tests

```bash
python3 tests/test_ingest.py     # Ebene 1 — ohne pytest lauffähig
python3 tests/test_evaluate.py   # Ebene 2 — ruft keine API auf
python3 -m pytest tests -q       # falls pytest da ist
```

Die Ebene-2-Tests prüfen keine Modellqualität, sondern das, was wir
verantworten: Markenabgleich, offene Entdeckung, die abgeleiteten Kennzahlen,
Wiederholbarkeit, Cache-Stabilität des Systemprompts — und dass Ebene 1 den
Auswertungs-Layer nirgends importiert.

---

## Beispiel-Lauf (Abnahme Schritt 1)

**Wichtig, damit nichts falsch verstanden wird:** dieser Lauf ist **kein
Live-Mitschnitt**. In dieser Umgebung liegt kein `SEARCHAPI_API_KEY` vor, ein
echter Call war deshalb nicht möglich. Gezeigt wird der **echte Ingest-Pfad**
(derselbe Code, der auch live läuft) mit einem abgespielten Payload:

```bash
python3 -m geotracker ingest --engine chatgpt --prompt-id 23 \
    --run-date 2026-07-27 \
    --fixture fixtures/chatgpt_lagercontainer_2026-07-27.json
```

Der Fixture-Inhalt ist **echte ChatGPT-Ausgabe**: Antworttext und Liste der
zitierten Domains stammen 1:1 aus dem Peec-Export vom 27.07.2026
(`data/peec/2026-07-27_2026-08-03/chats/anbieter-lithium-ionen-batterie-lagercontainer.md`).
Ergänzt wurde nur die SearchApi-**Hülle** (dokumentiertes Response-Schema) sowie
die vollständigen URLs und Titel — Peec exportiert nur Domains, keine Pfade.
Das ist im Fixture selbst unter `_fixture_note` vermerkt.

Ergebnis von `show-run 1`:

```
RUN #1  (success)
        Prompt: #23 Anbieter Lithium-Ionen-Batterie Lagercontainer
     Kategorie: Verkauf von Gefahrgutboxen
        Engine: chatgpt      Land/Sprache: DE / de      Datum: 2026-07-27
        Modell: gpt-5-5      Websuche: 1

--- ROHANTWORT (1596 Zeichen) ---
  [vollständiger Markdown-Text der Antwort]

--- ZITIERTE QUELLEN (10) ---
  1. lithiumionenlagerung.de   earned_media
  2. logbatt.com               owned
  3. protecto.de               competitor
  4. logbatt.de                owned
  5. loxxer.com                earned_media
  6. lion-care.com             competitor
  7. wlw.de                    earned_media
  8. relionbat.com             other         [NEU]   ← offene Entdeckung
  9. container-ellermann.com   competitor
 10. batterielagerung.de       earned_media
```

Damit sind alle drei Achsen der Citation-Analyse abgedeckt: Domain-Dominanz
(Ranking über `citations`), Eigen-Domain-Präsenz (`source_type = owned` — hier
auf Rang 2 und 4) und Earned Media (`earned_media` — hier 4 von 10 Quellen).
`relionbat.com` war in keinem Seed und wurde automatisch ins Register
aufgenommen.

**Sobald ein `SEARCHAPI_API_KEY` vorliegt, wird derselbe Befehl ohne
`--fixture` gegen die Live-API ausgeführt und der echte Lauf nachgereicht.**

---

## Nächste Schritte

3. **Engines 2–4** (`perplexity`, `gemini`, `google_ai_overview` inkl.
   `page_token`-Zweischritt — Gültigkeit unter 1 Minute, der Zweischritt muss
   also unmittelbar hintereinander laufen), **Scheduler** (APScheduler, täglich,
   konfigurierbar) und **Dashboard** (FastAPI-REST + HTML/JS) mit frei
   kombinierbaren UND-Filtern und der Citation-Achse.

**Offen aus Schritt 1 und 2:**
- Der **echte Live-Lauf** gegen SearchApi steht noch aus (kein Key vorhanden) —
  ebenso der erste echte Haiku-Aufruf. Beide Pfade sind implementiert und
  getestet, aber bis dahin ungeprüft gegen die reale API.
- **Land als Request-Parameter** (siehe Abschnitt oben) — offene Frage an
  SearchApi.
- **Few-Shot-Beispiele im Systemprompt**, sobald echte Antworten vorliegen.
