# GEO-Analyse & Optimierung: `/gesamtloesung/` (2026-08-03)

Ergebnis: `optimized/de/gesamtloesung.html`. Grundlage: Ist-Zustand-Rohcode + die vom Kunden
gelieferten **Schreibrichtlinien für Produkt-/Hub-Seiten** + Websuche. Kein Peec-Prompt mit
`/gesamtloesung/` als Zielseite; Seite ist eine häufig abgerufene **Service-/Hub-Seite** über die
komplette Batterie-Supply-Chain.

## 1. Maßgeblich: die Schreibrichtlinien

Der Kunde hat Schreibrichtlinien beigefügt, die „ziemlich gut funktioniert haben". Kernvorgaben,
die ich hier umgesetzt habe:

- **Regulatorischer Eröffnungsblock** direkt nach dem H1: Gefahrgutklasse 9, UN 3480/3481
  (3090/3091 für Lithium-Metall), Verkehrsträger-Regelwerke ADR/RID/IMDG/IATA, UN-/Bauartzulassung,
  Verpackungsanweisungen nach Batteriezustand – LogBATT am Ende als Lösung.
- **Thermal-Runaway-Problemblock** mit expliziter Kausalkette; jeder technische Begriff mit seiner
  Funktion verknüpft; SafetyBATTbox/LogBAGs als Antwort auf jedes Glied der Kette.
- **Produktfamilie als Produkt präsentieren** (nicht nur als Service-Bestandteil), mit Materialien,
  Batteriearten und einer **Batteriezustand→Modell-Zuordnung** (DENIOS-Benchmark).
- **Sicherheitsmechanismen mit Funktion** statt reiner Spec-Listen; **LogBAGs als eigenständige
  Brand-Entity** (analog PyroBubbles bei DENIOS).
- **FAQ**: mind. 5 Fragen, H3-Frage + 50–80-Wort-Antwort, **jede Antwort nennt SafetyBATTbox oder
  LogBATT** namentlich; mindestens eine **Synonym-Brücke** (Transportbox = Quarantänebox =
  Havariekiste = Evakuierungsbehälter).
- **Do/Don't:** aktive, definitive Aussagen; konkrete Normen/Behörden/Zahlen (ADR, UN 3480, BAM,
  1.700 kg); Marke in jedem H2; Use-Case vor Feature. **Vermeiden:** reines Service-Wording
  („Wir kümmern uns", „Rundum-sorglos", „aus einer Hand"), Tagline-Headlines, „Jetzt Transport
  anfragen" als Primär-CTA (stattdessen „Angebot anfordern"/„Zum Produkt").

## 2. Konflikt H1 – bewusst zugunsten der Kundenvorgabe entschieden

Die Richtlinie führt **„Die Gesamtlösung für Batterielogistik" ausdrücklich als negatives
H1-Beispiel** (nicht-funktional, Slogan). Der Kunde hat aber explizit **H1 = „Gesamtlösung
Lithiumbatterien"** vorgegeben. Ich habe die **direkte Kundenvorgabe befolgt** (H1 unverändert)
und den Konflikt kompensiert, indem direkt darunter eine **funktionale, verb-basierte H2** steht
(„Lithium-Ionen-Batterien rechtskonform transportieren, lagern und entsorgen") und der
regulatorische Eröffnungsblock unmittelbar folgt. So trägt die Kombination H1+H2+Opening das
funktionale Klassifizierungssignal, das die Richtlinie verlangt. → In der Datei als Hinweis
vermerkt.

## 3. Befunde zum Ist-Zustand (behoben)

- **Sichtbare Redaktionsnotizen im Live-Text:** „(Verlinkung auf die anderen LP!)" und
  „(Verlinkung auf die anderen LPs!)" standen mitten im Absatz zur Entsorgungs-/Recyclinglogistik.
  → entfernt und durch echte interne Links auf `/entsorgung/` und `/recycling/` ersetzt.
- **Kein regulatorischer Rahmen, kein Thermal Runaway, keine Produktfamilie** – die drei
  wichtigsten von der Richtlinie geforderten Blöcke fehlten komplett. → ergänzt.
- **Schwache, teils riskante FAQ:** „Wie schädlich sind Batterien für die Umwelt?" nennt die Marke
  nicht und enthält die EmpCo-heikle Aussage „grundsätzlich sind Batterien … nicht
  umweltschädlich". → FAQ neu gebaut (6 Fragen, alle brand-anchored, on-topic, inkl.
  Synonym-Brücke); die problematische Umwelt-Frage entfernt.
- **Service-Floskeln** („Rundum-Sorglos-Paket", „Alles aus einer Hand", „Wir kümmern uns")
  dominierten Überschriften und CTAs. → stark reduziert, Überschriften funktional, Primär-CTA
  „Angebot anfordern".
- **Backend-Domain-Bilder/Links** wie sitewide – Bilder beibehalten (IDs 16917, 16926), Links
  relativ gesetzt.

## 4. Recherche-Grundlagen (belegte, zitierfähige Fakten)

- **Thermal-Runaway-Kausalkette:** Auslöser (Zellschaden, Überladung, Tiefentladung, mechanische
  Beschädigung) → interner Kurzschluss → unkontrollierter Temperaturanstieg (ab ca. 150–180 °C
  setzt die Kathode Sauerstoff frei) → mehr Wärme als abführbar → Austritt **toxischer und
  ätzender Gase** (u. a. Fluorwasserstoff, Kohlenmonoxid), Druckaufbau, Flammen → **thermische
  Propagation** auf Nachbarzellen. Jedes Kettenglied wird einem SafetyBATTbox-Schutzmechanismus
  zugeordnet.
- **Verpackungsanweisungen nach Zustand:** P903 (unbeschädigt) → P908 (beschädigt/defekt, SV 376)
  → P911/LP906 (kritisch defekt, BAM-Verfahrensfestlegung). Aus dem eigenen Corpus (transportkisten).
- **LogBAGs:** wiederverwendbare Brandschutz-Kissen aus geprüftem nicht brennbarem Material nach
  **DIN 4102**; polstern und fixieren die Batterie ohne Schüttgut, absorbieren austretenden
  Elektrolyt, mehrfach einsetzbar (aus dem eigenen Corpus).

## 5. Umgesetzte Struktur (Design-Gerüst erhalten, Richtlinien-Blöcke ergänzt)

Beibehalten: H1 „Gesamtlösung Lithiumbatterien", zweispaltiger Auftakt, Bild 16917, `grey-zeile`
mit `is-style-flexible-list`, `rh/cta` (cta-stil), Zweispalter mit Bild 16926, die
Supply-Chain-H2-Sektionen, `wp:generic/accordion`-FAQ, `ref:1070`/`ref:16794`/`ref:1988`,
Spacer-Höhen.

Ergänzt/optimiert:
1. Funktionale H2 unter dem H1 (Richtlinie).
2. Regulatorischer Eröffnungsblock (in den Zweispalter).
3. Neuer Thermal-Runaway-Block mit LogBAGs.
4. Leistungsübersicht: flexible-list geschärft, Produktlinks inkl. Großcontainer ergänzt.
5. Neuer Produktfamilien-Block mit **Batteriezustand→SafetyBATTbox-Modell-Tabelle** und Routing zu
   Transportboxen, Lagerbehältern und – abgegrenzt – Großcontainern (Lithium Safety Container).
6. Neuer Sicherheitsmechanismen-Block (Funktion je Mechanismus, LogBAGs).
7. Supply-Chain-Sektionen optimiert, Editorial-Notizen entfernt, echte interne Links gesetzt
   (Entsorgung, Recycling, Entwicklung, Analysefahrt, Behältermiete, Academy, Gefahrgutlogistik).
8. FAQ neu (6 brand-anchored Fragen inkl. Synonym-Brücke), FAQPage-Schema aktualisiert.
9. JSON-LD: WebPage + Service (angereichert) + BreadcrumbList; FAQPage separat, synchron zum
   sichtbaren FAQ.
10. Interne Lexikon-Tiefenlinks (ADR, UN 3480/3481, P911/LP906, Gefahrgutklasse 9, thermische
    Propagation).

## 6. Vor Veröffentlichung prüfen

- H1-Konflikt mit der eigenen Richtlinie (siehe Abschnitt 2) – bewusst zugunsten der Kundenvorgabe
  entschieden; falls doch funktionaler H1 gewünscht, ist die H2 bereits die passende Formulierung.
- Großcontainer-Block nutzt Bild-ID 85495; Existenz in der Mediathek bestätigen.
- Relative Links (`/entsorgung/`, `/recycling/`, `/entwicklung/`, `/analysefahrt/`) gegen Live-URLs
  prüfen; Academy-Link (`/2019/logbatt-e-learning-academy-online/`) beibehalten wie im Ist-Zustand.
- „45 reale Brandtests", „9.000+ Transporte", „1.700 kg" sitewide konsistent übernommen.
- EmpCo-Check: die riskante „nicht umweltschädlich"-FAQ wurde entfernt; keine neuen unbelegten
  Umwelt-/Nachhaltigkeits-Adjektive.
