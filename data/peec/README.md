# Peec AI – Daten zur GEO-Sichtbarkeit von LogBATT

Dieser Ordner enthält Rohdaten-Exporte aus **Peec AI** (Tool zum Monitoring, wie LLMs/AI-Search-Engines
auf relevante Prompts antworten) sowie die daraus abgeleiteten Analysen.

## Struktur

```
data/peec/
  README.md                     diese Datei
  2026-07-27_2026-08-03/        ein Zeitraum-Ordner pro Export-Batch (Woche)
    chats/                      Chat-Exporte: pro Datei ein getesteter Prompt,
                                 Tag-für-Tag-Antworten aller getrackten Engines
    top-brands/                 Top-Brands-Exporte: Sichtbarkeits-/Wettbewerbsranking
                                 innerhalb einer von Peec getrackten Themen-/Keyword-Gruppe
```

Weitere Zeiträume werden als zusätzliche `JJJJ-MM-TT_JJJJ-MM-TT/`-Ordner ergänzt, sobald neue
Exporte vorliegen.

## Spalten-Glossar (Chat-Exporte)

| Spalte | Bedeutung |
| --- | --- |
| `model` | Getestete Engine: `chatgpt-ui`, `gemini-ui`, `perplexity-ui`, `google-ai-overview` |
| `user` | Der getestete Prompt (identisch für alle Zeilen einer Datei) |
| `assistant` | Volltext der Antwort des jeweiligen Modells an diesem Tag |
| `mentions` | Von Peec aus der Antwort extrahierte Markennennungen |
| `sources` | Domains, die das Modell als Quelle zitiert/verlinkt hat (Web-Grounding) |
| `citations` | Anzahl Quellenverweise |
| `position` | Position von **LogBATT** innerhalb der genannten Marken in dieser Antwort (leer = nicht erwähnt) |
| `created` | Zeitpunkt des Abrufs |

Jede Export-Datei deckt **einen Prompt über 8 Tage × 4 Engines = 32 Antworten** ab. Die Auswahl der
hier eingepflegten Prompts ist laut Team **kein vollständiges Set**, sondern bewusst eine Mischung
aus gut und schlecht performenden Beispielen je Thema.

## Spalten-Glossar (Top-Brands-Exporte)

| Spalte | Bedeutung |
| --- | --- |
| `visibility` | Anteil der geprüften Antworten/Tage, in denen die Marke überhaupt vorkommt |
| `share_of_voice` | Anteil der Markennennungen dieser Marke an allen Nennungen im Themenfeld |
| `sentiment` | Sentiment-Score der Nennungen (Skala unklar dokumentiert – wirkt wie 0–100, höher vermutlich positiver; nicht LogBATT-seitig verifiziert) |
| `position` | Ø Position der Marke innerhalb der Antworten, in denen sie genannt wird (niedriger = weiter vorne) |
| `*_delta` | Veränderung ggü. vorherigem Beobachtungszeitraum |

**Offener Punkt:** Peec ordnet Top-Brands-Exporte einer internen „Topic"/Keyword-Gruppe zu, die im
Excel-Export selbst nicht als Klartext-Name enthalten ist (nur die Datei-ID). Die beiden Exporte in
`2026-07-27_2026-08-03/top-brands/` unterscheiden sich deutlich in der Rangfolge (Export 12: LogBATT
#1 vor Zarges/DENIOS – vermutlich das engere Themenfeld „Lithium-Batterie-Lagerung/-Transport";
Export 13: DENIOS #1 vor LogBATT – vermutlich das breitere Themenfeld „Gefahrgut-/Havariebehälter
allgemein"). Diese Zuordnung ist eine **Vermutung** und sollte mit LogBATT/Sezer bzw. direkt im
Peec-Dashboard bestätigt werden.
