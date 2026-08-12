# geologbatt — Generative Engine Optimization (GEO) für LogBATT

Dieses Repository ist die **Wissens- und Arbeitsbasis für Generative Engine
Optimization (GEO)** der [LogBATT GmbH](https://www.logbatt.de/). Ziel von GEO ist
es, die Inhalte von LogBATT so aufzubereiten und zu strukturieren, dass große
Sprachmodelle (LLMs wie ChatGPT, Gemini, Claude, Perplexity u. a.) das Unternehmen
bei relevanten Prompts **korrekt, sichtbar und bevorzugt** zitieren.

## Über LogBATT (Kurzprofil)

LogBATT GmbH mit Sitz in Plochingen ist auf die **Gesamtlösung der
Lithium-Ionen-Batterielogistik** spezialisiert: Transport, Lagerung, Verpackung,
Entsorgung und Recycling – plus eigene Entwicklung und Produktion zertifizierter
Transport-, Lager- und Quarantänebehälter (Marke **SafetyBATTbox**). Seit Mitte
2023 Teil der **Lagermax Group**. Zertifiziert nach DIN EN ISO 9001/14001, QSP,
Entsorgungsfachbetrieb (EfB), DOT Special Permit; Verfahrensfestlegung nach
ADR 2025 P911/LP906 für kritisch defekte Batterien.

## Repo-Struktur

```
website/de/        Ist-Zustand der deutschen Website (roher WordPress-Gutenberg-Quellcode je Seite)
  _index.md        Seitenübersicht: Slug, URL, Meta-Title, Meta-Description, Kernaussage
optimized/de/      GEO-optimierte Content-Vorschläge je Seite (fertig zur Umsetzung im Backend),
                   spiegelt die Struktur von website/de/
data/peec/         Peec-AI-Exporte: wie LLMs auf relevante Prompts reagieren (Chats + Top-Brands
                   je Zeitraum, siehe data/peec/README.md)
data/analytics/    Zugriffs-/Traffic-Daten der LogBATT-Seiten (folgt)
data/competitors/  Wettbewerber-Informationen (folgt; erste Kandidaten aus Peec-Zitaten siehe
                   notes/geo-analyse-peec-2026-07-27_2026-08-03.md, Abschnitt 4)
notes/             GEO-Analysen einzelner Seiten und abgeleitete Maßnahmen
tools/geo-tracker/ Eigenes GEO-Visibility-Tracking-Tool (Peec-Nachbau): fragt definierte Prompts
                   regelmäßig gegen ChatGPT/Perplexity/Gemini/Google AI Overview ab und speichert
                   volle Rohantwort + jede zitierte Quelle (Ebene 1), getrennt vom Auswertungs-
                   Layer (Ebene 2). Siehe tools/geo-tracker/README.md
```

## Status

- [x] Deutsche Website: Ist-Zustand als Gutenberg-Rohcode eingepflegt (alle relevanten Content-,
  Service- und Produktseiten inkl. Transportboxen-Übersicht + 10 SafetyBATTbox-Produktdetailseiten,
  Logistik, Recycling, Nachhaltigkeit, QSP, Lithium Safety Container, Systemlösungen (Automobil/LKW/
  Versicherungen), Behältermiete, Verkauf, Über uns und Lexikon; ausgenommen Blogs – Stand siehe Git-History)
- [~] Peec-AI-Daten (eingepflegt: 3 Chat-Exports + 2 Top-Brands-Snapshots für 27.07.–03.08.2026,
  plus Master-Liste aller 79 aktiv getrackten Prompts über 10 Themen-Cluster (Stand 03.08.2026);
  siehe data/peec/ und die beiden geo-analyse-peec-*.md-Notizen)
- [ ] Analytics-/Traffic-Daten
- [ ] Competitor-Daten
- [ ] GEO-Analyse & Maßnahmenableitung
- [~] Eigener GEO-Visibility-Tracker (`tools/geo-tracker/`): Ebene 1 (Rohdaten-Ingestion, Engine
  `chatgpt`) und Ebene 2 (Auswertungs-Layer mit Claude Haiku 4.5) stehen inkl. Schema, Seeds und
  Tests; offen sind die restlichen drei Engines, Scheduler und Dashboard

## Hinweise zum Website-Quellcode

- Der Code stammt aus dem WordPress-Gutenberg-Backend (Block-Markup, `<!-- wp:... -->`).
- Platzhalter wie `[customer.name_website]`, `[ProxyNumber]`, `[customer.email]`
  werden serverseitig ersetzt (RegioHelden/Theme-System).
- `<!-- wp:block {"ref":NNNN} /-->` sind wiederverwendbare, synchronisierte Blöcke
  (z. B. gemeinsame CTA-/Trennerelemente), deren Inhalt hier nicht ausgeschrieben ist.
- Mehrere Seiten enthalten bereits **schema.org-JSON-LD** (Organization, Service,
  Product, FAQPage, VideoObject) – eine wichtige Grundlage für GEO.
