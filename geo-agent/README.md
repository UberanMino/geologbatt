# GEO Content Agent — rekursive Content-Optimierung

Ein Drei-Agenten-Loop, der einen Content so lange überarbeitet, bis eine
generative Suchmaschine die Marke bei den Zielprompts **nennt** — statt sie nur
zu „retrieven", aber nicht zu empfehlen. Gebaut für den in diesem Repo
diagnostizierten LogBATT-Fall (starke Retrieval-Rate, schwache Brand-Mention).

Das ist die Umsetzung genau der Idee aus der Konversation: Generator schreibt →
Judge liest wie eine echte Engine → ein dritter Agent (Synthesizer) verdichtet
Generator- und Judge-Input zu Feedback → Generator optimiert weiter.

```
        ┌───────────────────────────────────────────────┐
        │                                               ▼
   ┌───────────┐   Content     ┌────────┐  Antwort   ┌────────┐
   │ GENERATOR │ ────────────► │ JUDGE  │ ─────────► │ SCORER │
   │ (Familie A)│              │(Familie B,│          │ Metriken│
   └───────────┘               │ geerdet)│           └────────┘
        ▲                       └────────┘                │
        │ Direktiven                                       │
        │                    ┌─────────────┐               │
        └──────────────────  │ SYNTHESIZER │ ◄─────────────┘
           (nur Train)       └─────────────┘
                              Content + Antwort + Metriken → Feedback

   Innen-Schleife (schnell, offline, synthetisch)
   ─────────────────────────────────────────────
   Außen-Schleife: Peec AI als Ground Truth (langsam, real) — siehe unten
```

## Schnellstart (ohne API-Key)

Der Default-Profil `mock` fährt den **kompletten Loop offline** über einen
deterministischen Heuristik-Provider. Kein Key, kein Netz.

```bash
cd geo-agent
python run.py list                       # Targets + Wettbewerber-Karten
python run.py run --target havarie       # Loop laufen lassen
python run.py show-prompt hav-05         # einen Prompt inspizieren
```

Beispielausgabe (`havarie`, mock):

```
 iter   train     val   mention  avg_pos   cited   frame
 -------------------------------------------------------
    0   0.415   0.317       50%     2.33     50%     67%
    1   0.868   0.875      100%     1.17    100%    100%
 *  2   0.925   0.925      100%     1.00    100%    100%
 Stop reason: target_reached
```

Der Mock ist **inhaltssensitiv**: Die Stärke des Kandidaten auf einem Prompt ist
die Abdeckung genau der Fakten/Anker dieses Prompts. Fügt der Generator das
hinzu, was der Synthesizer verlangt, nennt der Judge die Marke wirklich häufiger
und weiter vorne. Der Loop konvergiert, weil der Content besser wurde — nicht
weil ein Zähler hochläuft.

## Die vier Agenten

| Agent | Aufgabe | Warum getrennt |
|---|---|---|
| **Generator** | Schreibt/überarbeitet die Kandidatenseite. Harte Nebenbedingungen: Markenstimme, menschliche Lesbarkeit, Faktentreue (nur freigegebene Fakten). | — |
| **Judge** | Beantwortet den Prompt wie eine geerdete Engine (Perplexity-Stil), zitiert Quellen inline `[S1]…`. | **Andere Modellfamilie als der Generator** — sonst Self-Bias (arXiv:2412.16829). Wird erzwungen. |
| **Scorer** | Extrahiert die Metriken aus der Judge-Antwort (getrennter Schritt). | Der Generator bekommt strukturierte Signale, nicht rohen Text zum Raten. |
| **Synthesizer** | Verdichtet Entwurf + Judge-Antworten + Metriken zu wenigen, konkreten Direktiven. | „Spezifisch schlägt viel" (Self-Refine, Madaan 2023). |

## Die zwei Präzisierungen aus der Konversation — beide umgesetzt

**1. Kontext-Swap, kein Eingriff ins Wissensnetz.** Der Judge bekommt ein
Dokument-Set: `S1` = Kandidat (das Einzige, das sich pro Iteration ändert), dann
byte-identische Wettbewerber-Karten. Damit ist jede Iteration ein sauberes A/B.
Siehe `geo_agent/agents/judge.py:build_doc_set`.

**2. Grounding, um parametrisches Wissen zu minimieren.** Default
`grounding: sources_only` — der Judge antwortet nur aus den vorliegenden Quellen,
damit die Antwort maximal empfindlich auf den Kandidaten reagiert. `blended`
(Quellen + internes Wissen) existiert als sekundärer Realismus-Check, nicht als
Optimierungssignal.

**swap vs inject.** Jeder Prompt ist markiert:
- `swap` — LogBATT taucht real schon auf → Test, ob besserer Content von
  „retrieved-but-unnamed" auf „genannt" kippt.
- `inject` — LogBATT taucht kaum auf → Test „*wenn* meine Seite abgerufen würde,
  würde ich genannt?". Höhere Schwelle, im Reporting getrennt lesbar über `mode`.

## Die Zielfunktion (Dekomposition von „was ankam")

`„was ankam"` ist als messbare Signale zerlegt (`geo_agent/scoring.py`):

| Signal | Gewicht | Bedeutung |
|---|---|---|
| `mention` | 0.35 | Marke als Anbieter genannt? |
| `position` | 0.20 | Rang unter den genannten Anbietern (1 = vorne) |
| `cited_from_candidate` | 0.20 | wegen der **Kandidatenseite** zitiert (nicht beiläufig durch ein Wettbewerber-Dokument)? |
| `problem_frame` | 0.10 | Problem-Narrativ-Anker präsent? |
| `claims` | 0.15 | Kernfakten korrekt wiedergegeben? |

Gewichte anpassbar in `prompts/prompts.yaml → weights`.

## Guardrails gegen „sauber am Ziel vorbei optimieren"

- **Self-Bias:** Generator- und Judge-Familie müssen verschieden sein — wird in
  `config.assert_distinct_families()` erzwungen (Scorer/Synthesizer teilen die
  Judge-Familie, damit der Generator sich nie selbst benotet/coacht).
- **Goodhart / Overfit auf den Judge:** Jeder Cluster hat einen **Hold-out**
  (`split: val`), der bewertet, aber **nie** an den Synthesizer gefüttert wird.
  Ein wachsender Train/Val-Abstand wird im Report gewarnt.
- **Lesbarkeits-Drift:** Markenstimme + menschliche Lesbarkeit sind im
  Generator-Prompt harte **Nebenbedingungen**, keine Optimierungsziele.
- **Konvergenz:** Abbruch bei Plateau (`patience`), Zielscore (`target_score`)
  oder wenn der Synthesizer nichts Sinnvolles mehr offen sieht (`converged`).

## Die Außen-Schleife (Ground Truth)

Der Loop hier ist die **schnelle, synthetische Innen-Schleife**. Sie ist nur so
viel wert wie ihre Korrelation mit der Realität. Der Baseline-Wert jedes Prompts
(`baseline_mention_pct`, aus den echten Peec-Daten) ist der Anker: Bevor du viel
in die Innen-Schleife investierst, prüfe an ein paar Seiten, ob eine im Loop
verbesserte Kandidatenseite sich nach Publikation auch in Peec (echte
Mentions/Citations) niederschlägt. Ist die Korrelation schwach, optimierst du an
einem verzerrten Proxy.

## Live gehen (echte Modelle)

```bash
cp .env.example .env         # Keys eintragen
pip install -r requirements.txt
python run.py --profile live run --target havarie
```

Modelle/Familien in `config.yaml` (oder per `GEO_MODEL_*`-Env). Default-Setup:
Generator = Anthropic, Judge/Scorer/Synthesizer = OpenAI. Jeder Provider wird
über `"<provider>:<model>"` adressiert (`anthropic:`, `openai:`, `google:`,
`mock:`). **Model-IDs vor einem Live-Lauf beim Provider verifizieren.**

## Datengrundlage

Prompts, Cluster, Baseline-Mention-Raten und Wettbewerber-Anteile stammen aus
dem echten Peec-Export dieses Repos
(`data/peec/tracked-prompts-2026-07-01_2026-08-05/prompt-metrics.csv`). Die
Wettbewerber-Karten unter `corpus/competitors/` sind **Proxys** aus den
Peec-Beschreibungen — für einen realitätsnahen Judge durch die echten,
abgerufenen Wettbewerber-Seiten ersetzen (siehe `corpus/competitors/README.md`).

## Projektstruktur

```
geo-agent/
  run.py                    Entry point (python run.py run --target …)
  config.yaml               Modelle je Rolle, Grounding, Loop-Parameter
  prompts/prompts.yaml      Prompt-Set (train/val), Targets, Gewichte
  corpus/
    logbatt/*-seed.md       Start-Content je Target (bewusst dünn)
    competitors/*.md        Wettbewerber-Karten (Proxy)
  geo_agent/
    llm.py                  Provider-Abstraktion + Mock
    corpus.py               Loader
    scoring.py              Zielfunktion (Metriken, Aggregation)
    agents/                 generator · judge · scorer · synthesizer
    loop.py                 die Rekursivschleife + Konvergenz
    report.py               Konsole / JSON / Markdown
    cli.py
  tests/                    pytest
  runs/                     Lauf-Outputs (gitignored)
```

## Referenzen

- Madaan et al. 2023, *Self-Refine: Iterative Refinement with Self-Feedback*
- Shinn et al. 2023, *Reflexion*
- *LLMRefine* / Self-Bias, arXiv:2412.16829 — separates Feedback-Modell gegen Self-Bias

*Muster verifiziert; die konkreten Zahlen im Mock sind illustrativ, keine
gemessenen Peec-Daten.*
