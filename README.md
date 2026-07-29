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
data/peec/         Peec-AI-Exporte: wie LLMs auf relevante Prompts reagieren (folgt)
data/analytics/    Zugriffs-/Traffic-Daten der LogBATT-Seiten (folgt)
data/competitors/  Wettbewerber-Informationen (folgt)
notes/             Analysen, Hypothesen und abgeleitete GEO-Maßnahmen
```

## Status

- [x] Deutsche Website: Ist-Zustand als Gutenberg-Rohcode eingepflegt (Content-Seiten + Transportboxen-Übersicht + 10 SafetyBATTbox-Produktdetailseiten, Stand siehe Git-History)
- [ ] Peec-AI-Daten
- [ ] Analytics-/Traffic-Daten
- [ ] Competitor-Daten
- [ ] GEO-Analyse & Maßnahmenableitung

## Hinweise zum Website-Quellcode

- Der Code stammt aus dem WordPress-Gutenberg-Backend (Block-Markup, `<!-- wp:... -->`).
- Platzhalter wie `[customer.name_website]`, `[ProxyNumber]`, `[customer.email]`
  werden serverseitig ersetzt (RegioHelden/Theme-System).
- `<!-- wp:block {"ref":NNNN} /-->` sind wiederverwendbare, synchronisierte Blöcke
  (z. B. gemeinsame CTA-/Trennerelemente), deren Inhalt hier nicht ausgeschrieben ist.
- Mehrere Seiten enthalten bereits **schema.org-JSON-LD** (Organization, Service,
  Product, FAQPage, VideoObject) – eine wichtige Grundlage für GEO.
