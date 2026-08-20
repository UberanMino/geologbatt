# RankScale – Prompt-Set für GEO-Tracking je Sprache/Land

**Stand:** 2026-08-20 · **Datei zum Import:** `rankscale-prompts-2026-08-20.csv`

RankScale-Import-Format (identisch zur Beispiel-Datei): **UTF-16LE mit BOM,
Tab-getrennt, CRLF, Datenfelder in Anführungszeichen**. Spalten:
`Topic` (= Sprache/Markt) · `SearchTerm` (= Prompt) · `Tags`.

- **8 Prompts** je Sprache · **13 Sprachen** · **104 Zeilen**.
- Nicht enthalten: **Deutsch, English, Español** (laufen über Suchhelden) sowie
  **Deutsch (Schweiz)** und **Deutsch (Österreich)** (nicht benötigt).
- `Tags` sind je Prompt sprachübergreifend identisch (`product`/`service` +
  Slug) → erlaubt den Vergleich desselben Prompts über alle Märkte hinweg.

## Die 8 Prompts (Auswahl, verifiziert 2026-08-20)

| # | Deutsch (Quelle) | Bucket | Tag |
| --- | --- | --- | --- |
| 1 | Welche Transportboxen für Lithium Batterien gibt es? | Behälter – Transport | `product, transport-box` |
| 2 | Welche Behälter eignen sich für die Lagerung von Lithium-Batterien? | Behälter – Lagerung | `product, storage-container` |
| 3 | Welche Anbieter verkaufen Havariekisten für Lithium-Batterien? | Behälter – Kauf | `product, emergency-box` |
| 4 | Anbieter für Lagercontainer für Lithium Batterien zur Miete | Behälter – Miete | `product, rental-container` |
| 5 | Welcher Dienstleister ist auf die Entsorgung von Lithium-Batterien nach Havariefällen spezialisiert? | Logistik – Entsorgung/Havarie | `service, disposal` |
| 6 | Bei welchem Unternehmen kann ich beschädigte Lithium Batterien transportieren lassen? | Logistik – Transport | `service, transport` |
| 7 | Welche Firma bietet Gefahrgutboxen für Batterien zur Miete an? | Behälter – Miete | `product, rental-dg-box` |
| 8 | Anbieter Lithium-Ionen-Batterie Quarantänebox | Behälter – Produkt (Quarantäne) | `product, quarantine-box` |

→ 6× Behälter/Produkt + 2× Batterielogistik. Produktschwerpunkt wie abgestimmt.

## Terminologie-Entscheidungen (idiomatische Fachbegriffe je Sprache)

Übersetzt wurde **nicht wörtlich, sondern nach gängigem Fach-/Suchsprachgebrauch**:

- **Gefahrgut (#7):** die etablierten ADR-Begriffe je Sprache – FR *marchandises
  dangereuses*, IT *merci pericolose*, NL *gevaarlijke goederen*, PL *towary
  niebezpieczne*, CS/SK *nebezpečné věci/veci*, SV/DA *farligt gods*, NB *farlig
  gods*, FI *vaaralliset aineet*, RO *mărfuri periculoase*, PT *mercadorias
  perigosas*, HU *veszélyes áru*.
- **Havariekiste (#3):** als „Sicherheitsbox für beschädigte Batterien" gerahmt
  (der im jeweiligen Markt gebräuchliche, auffindbare Ausdruck), da ein direktes
  Pendant zu „Havariekiste" außerhalb des Deutschen unüblich ist.
- **Havariefall (#5):** wo vorhanden das direkte Kognat – CS *havárie*, SK
  *havária*, SV/DA/NB *haveri/havari*, PL *awaria*, RO *avarie/incident*; sonst
  „nach einem Schadenfall/Sinistre" (FR *sinistre*, IT *sinistro*, PT *sinistro*,
  HU *káresemény*).
- **Quarantänebox (#8):** überall das Quarantäne-Kognat (*quarantaine/quarantena/
  kwarantanna/karanténa/karantän/karantæne/karanteeni/carantină/quarentena/
  karantén*).
- **Entsorgung (#5):** *élimination / smaltimento / utylizacja / likvidace /
  bortskaffelse / avfallshantering / hävittäminen / eliminare / eliminação /
  ártalmatlanítás*.
- **Batterie:** i. d. R. „Lithium-Batterie" (auffindbarster Suchbegriff);
  „Lithium-Ionen" nur bei #8 (entsprechend der Quelle). Sprachen mit
  Akku-Unterscheidung nutzen den Industrie-Begriff (PL *akumulatory*, HU
  *akkumulátor*, FI *akku*).

Bei einzelnen Begriffen gibt es je nach Markt gleichwertige Alternativen
(z. B. NL *calamiteitenbox* statt *veiligheidsbox*; FR *caisse ADR* statt
*caisse pour marchandises dangereuses*). Änderungswünsche bitte melden – Anpassung
ist ein Einzeiler.

## Sprachen (Reihenfolge wie im RankScale-Dropdown)

Français · Magyar · Čeština · Nederlands · Svenska · Slovenčina · Polski ·
Suomi · Română · Italiano · Português · Dansk · Norsk Bokmål
