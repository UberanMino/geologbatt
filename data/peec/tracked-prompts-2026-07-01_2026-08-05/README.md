# Peec-Tracking-Datensatz 01.07.–05.08.2026 (vollständig)

**Das ist der komplette getrackte Prompt-Satz für den Zeitraum** – alle in Peec hinterlegten
Prompts, nicht seitengefiltert. Ursprünglich als „Export für /gesamtloesung/" bzw. „für
/entsorgung/" geliefert; tatsächlich sind **beide gelieferten Dateien byte-identisch** und
enthalten den gesamten Account-Export. Damit ist dies die **kanonische Referenz** für alle
Wettbewerbs- und Sichtbarkeitsanalysen im Wissensnetz.

- Quelldatei: `chatsexportlogbattfrom20260701to20260805(_1).xlsx` (liegt aus Größengründen nicht im Repo)
- **10.000 Antworten** = **83 Prompts × 4 Modelle** (je ~2.500)
- Modelle: `chatgpt-ui`, `perplexity-ui`, `gemini-ui`, `google-ai-overview`
- Erfasster Zeitraum der Antworten: 2026-07-04 – 2026-08-04

## Spalten-Schema (und was belastbar ist)

| Spalte | Bedeutung | Belastbarkeit |
|---|---|---|
| `user` | der getrackte Prompt | ✅ |
| `model` | LLM/Oberfläche | ✅ |
| `mentions` | in der Antwort **namentlich genannte Marken** (Komma-Liste) | ✅ Marken-Ebene |
| `sources` | in der Antwort **zitierte Domains** (Komma-Liste, **nur Domains, keine Pfade**) | ✅ Domain-Ebene |
| `position` | **Rang von LogBATT** in der Antwort (1–6) – existiert nur, wenn LogBATT vorkommt | ✅ LogBATT-spezifisch |
| `citations` | Anzahl der Web-Quellen der Antwort (0 = ohne Websuche) | ✅ |
| `content_in_chat` | Antworttyp (WEB_SEARCH, SHOPPING, MAP …) | ✅ |
| `assistant` | Volltext der Antwort | ⚠️ nur für qualitative Stichproben |

### Wichtiger Caveat: keine Seiten-Ebene
`sources` enthält **ausschließlich blanke Domains** (`logbatt.de`), **nie** Pfade. Aus diesem
Export lässt sich daher **nicht** ableiten, welche einzelne LogBATT-**Seite** (`/entsorgung/`,
`/gesamtloesung/` …) zitiert wurde – nur, dass die Domain zitiert wurde. Jede Aussage auf
Seiten-Ebene bräuchte den separaten **Quellen-/URL-Export** aus Peec. Alle Auswertungen hier
bewegen sich bewusst auf **Marken- und Domain-Ebene** (plus LogBATT-Position).

## Dateien in diesem Verzeichnis

- `README.md` – dieses Dokument (Datensatz, Schema, Caveats)
- `findings.md` – **die strategische Auswertung** (Sichtbarkeit, Modelle, Cluster, Chancen)
- `competitors.md` – Wettbewerber-Leaderboard (Marken + Domains) mit Einordnung
- `prompt-metrics.csv` – maschinenlesbar: je Prompt Cluster, Sprache, LogBATT-Mention-%,
  LogBATT-Ø-Position, Mention-% je Modell, Top-5-Wettbewerber

## Reproduktion

Skript-Logik (openpyxl): `mentions`/`sources` an Komma splitten; `has_lb` = „logbatt" in
sources+mentions; `position` nur bei LogBATT-Treffern mitteln; Cluster per Keyword-Regeln
(siehe `findings.md`). Prompt-Sprache EN/DE heuristisch.
