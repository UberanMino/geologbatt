# GEO-Analyse & Optimierung: `/gefahrgutlogistik/` (2026-08-05)

Ergebnis: `optimized/de/gefahrgutlogistik.html`. Grundlage: Original-Rohcode + Tracking-Datensatz
(Transport-/Gefahrgut-Cluster) + Schreibrichtlinien.

## 1. Zitationskontext (mit Vorbehalt)

Der Tracking-Export führt Quellen **nur auf Domain-Ebene** (`logbatt.de`), nicht seitengenau –
welche einzelne Seite zitiert wurde, ist daraus nicht isolierbar. Die ausgeschriebene
`/gefahrgutlogistik`-URL steht nur in **2 Antworten** im Text (beide Google AI Overview, beide im
Havarie-/Entsorgungskontext). Aussagekräftig ist deshalb der **thematisch relevante
Prompt-Cluster** (Transport von Lithiumbatterien als Gefahrgut):

- **Service-Fragen** („transportieren lassen", „Anbieter Transport und Entsorgung abgebrannte
  Batterie", „Bei welchem Unternehmen … transportieren lassen"): LogBATT **60–75 %**, Hauptgegner
  **RETRON**. Hier ist die Seite stark.
- **Produkt-Fragen** („Welche Gefahrgutbox brauche ich", „Beste Transportbox", „Welcher
  Gefahrgutcontainer … am besten"): LogBATT **9–22 %**, **DENIOS/Zarges** dominieren.

→ Konsequenz (deckt sich mit dem Produktmarken-Befund, `vertiefungsanalysen.md` §2b):
**Service-Framing halten UND die SafetyBATTbox als Produkt verankern + verlinken.**

## 2. Befunde zum Ist-Zustand (behoben)

- **Rambling-B2C-Intro** („Mobiltelefone, Kinderspielzeug, Herzschrittmacher, Hörgeräte") ohne
  regulatorische Substanz. → antwort-erster B2B-Auftakt.
- **Regulatorischer Rahmen fehlte im Fließtext:** kein UN 3480/3481 (bzw. 3090/3091), keine
  Gefahrgutklasse 9, keine Verpackungsanweisungen (P903/P908/P911), **IATA-DGR (Luftfracht) fehlte
  komplett** – obwohl der Text von „Flugzeug" spricht. Nur ADR/RID/IMDG waren genannt. → ergänzt.
- **SafetyBATTbox kam gar nicht vor** – die Seite nannte nur „Entwicklung von Transport-, Lager-
  und Quarantäneboxen". → SafetyBATTbox als Produkt eingeführt, Synonym-Brücke (Transportbox =
  Quarantänebox = Havariekiste), Links auf `/transportkisten/`, `/lagerbehaelter/`,
  `/lithium-safety-container/`.
- **Service-Floskeln** („Machen Sie sich keine Gedanken", „Wir kümmern uns", „überlassen Sie alles
  einfach uns") und **Keyword-Stuffing** „Batterien Gefahrgutlogistik". → reduziert, definitive
  Aussagen.
- **Off-topic H2** „Lithiumbatterien Recycling – professionell mit LogBATT" auf einer
  Gefahrgut-Transport-Seite. → zu on-topic Marken-Abschluss „Batterie-Gefahrgutlogistik –
  professionell mit LogBATT" umformuliert (Transport zur Verwertung, Produktanker, 9.000+
  Transporte, Lagermax).
- **Isolierte Aussagen** → Wirkungsketten (Ursache → Mechanismus → Nutzen), z. B. „Weil die
  Behälter thermisch isolieren und Gase kontrolliert führen, schließen sie … ein."
- **Generische, nicht brand-anchored FAQ** → 7 Fragen, jede nennt LogBATT/SafetyBATTbox;
  regulatorisch geschärft (Klasse 9, UN-Nummern, P908/P911, ADR-30-kg-Regel behalten), inkl. der
  Produkt-Frage „Welche Box brauche ich für den Gefahrguttransport?" (adressiert die schwache
  Produkt-Frage-Performance) und der Havarie-/Wasserbad-Frage (gecitetes Thema).

## 3. Struktur (unverändert)

Beibehalten: ref:17205/1070/16794, Header-Bild 17001, 4er-Galerie (17010/17013/17016/17019),
zwei `grey-zeile`-Gruppen, `rh/cta` (cta-stil, 2×), `generic/accordion`-FAQ, ADR-Checkliste-PDF,
H1 „Batterien Gefahrgutlogistik" (Kern-/Meta-Term beibehalten). JSON-LD: WebPage (significantLink)
+ Service (angereichert um Klasse 9, UN-Nummern, IATA, Verpackungsanweisungen, SafetyBATTbox) +
FAQPage synchron zu den 7 sichtbaren Fragen.

## 4. Vor Veröffentlichung prüfen

- Relative Links (`/transportkisten/`, `/lagerbehaelter/`, `/lithium-safety-container/`,
  `/entsorgung/`) gegen Live-URLs prüfen; ADR-Checkliste-PDF-URL bestätigen.
- H1 bewusst als Nominal-Term beibehalten (Meta-/Ranking-Identität); funktionales Signal trägt der
  antwort-erste Auftakt. Falls funktionaler H1 gewünscht, ist „Lithium-Ionen-Batterien
  rechtssicher transportieren" (bereits als H2 vorhanden) die Alternative.
- „6-facher Luftwechsel", „9.000+ Transporte", „P911/LP906" sitewide konsistent.
- EmpCo-Check: keine unbelegten Umwelt-/Nachhaltigkeits-Adjektive.
- Einleitenden HTML-Kommentar vor dem Einpflegen entfernen.
