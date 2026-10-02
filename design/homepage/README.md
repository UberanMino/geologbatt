# Homepage-Redesign (statisches HTML)

Neuentwurf der Startseite `https://www.logbatt.de/` als eigenständiges, responsives HTML —
gedacht als Ersatz für den Gutenberg-Aufbau der Hauptseiten, ohne das RegioHelden-/Ströer-Theme
verlassen zu müssen.

| Datei | Inhalt |
| --- | --- |
| `index.html` | Vollständige Seite. Vorschau lokal im Browser öffnen; für WordPress nur der Bereich zwischen `COPY START` und `COPY END`. |

## Was drin steckt

1. **Hero** — Bestandsvideo als Hintergrund (`Video-Startseite-Header.mp4`), keyword-starke H1
   („Die Gesamtlösung für Lithium-Ionen-Batterielogistik"), emotionale Subline, Primär-CTA
   „Kostenlose Erstberatung", Schnelleinstieg-Pills, Trust-Leiste mit allen Zertifizierungen.
2. **Nutzen-/Emotions-Sektion mit Flow-Visualisierung** — animierter Vergleich
   „Ohne Gesamtlösung" ↔ „Mit LogBATT": sechs verstreute Gewerke mit verhedderten Linien lösen sich
   in eine saubere Kette über einen Hub auf; parallel fällt der Balken „Aufwand & Restrisiko bei Ihnen"
   von *hoch* auf *gering*. Läuft beim Hineinscrollen automatisch einmal ab und ist danach umschaltbar.
   Darunter vier Nutzen-Karten und eine CTA-Bande.
3. **Lagerbehälter (interaktiv)** — Modell-Tabs M/L/XL mit animierten Kennzahlen, wechselndem
   Produktfoto, Deep-Link auf die Produktseite; interaktive Schnittdarstellung mit sechs anklickbaren
   Hotspots (Gasmanagement, Thermische Isolation, Auffangwanne, LogBAGs, Frontalbeladung, Stapelbarkeit),
   animiertem Rauchgas und eingeschlossener Flamme; maßstabsgetreuer Größenvergleich mit
   1,80-m-Referenzperson; helle CTA-Bande.
4. **Ablauf** — die vier Schritte der bestehenden Seite mit einlaufender Fortschrittslinie.
5. **Leistungen & Ihre Vorteile** — sechs Leistungskarten plus die sechs Vorteile der Ist-Seite,
   jeweils mit den bestehenden internen Links (inkl. Sprungmarken wie `/logistik/#networksolution`).
6. **Kennzahlen** — hochzählende Zahlen (9.000+ Transporte, 45 Brandtests, 30+ Länder, 10 Modelle).
7. **Über LogBATT** — der komplette Fließtext der Ist-Seite (wichtig für GEO/SEO) mit Bild.
8. **Video** — YouTube `DTB8vPQZ060` als Klick-Fassade (lädt YouTube erst nach Klick, `youtube-nocookie`).
9. **Referenzen** — Endlos-Laufband mit allen 25 Kundenlogos, Pause bei Hover.
10. **News** — drei Einstiegskarten (Blog, Informatives, Instagram).
11. **FAQ** — alle 15 Fragen der Ist-Seite als Accordion, Text 1:1 aus dem bestehenden FAQPage-JSON-LD generiert.
12. **Schluss-CTA** — Kontaktkarte mit Telefon, E-Mail, Academy, Stellenanzeigen.

Alle drei **JSON-LD-Blöcke der Ist-Startseite** (Organization/OfferCatalog/WebPage/DefinedTerm,
VideoObject, FAQPage mit 15 Fragen) sind unverändert übernommen — die GEO-Basis geht beim Umbau
nicht verloren.

## Einbau in WordPress (Gutenberg)

1. Auf der Startseite einen **„Custom HTML"-Block** (Individuelles HTML) anlegen — am besten als
   einzigen Block, damit keine Theme-Container dazwischenfunken.
2. Aus `index.html` alles zwischen `<!-- ===== COPY START ===== -->` und `<!-- ===== COPY END ===== -->`
   einfügen (Style-Block, Markup, Script — in dieser Reihenfolge, alles gehört zusammen).
3. Speichern, Cache leeren, prüfen.

### Wichtige Hinweise

- **Full-Bleed:** `.lb-page` bricht per `width:100vw; margin-left:calc(50% - 50vw)` aus dem schmalen
  Content-Container aus. Falls das Theme das nicht mitmacht (horizontaler Scrollbalken), die drei
  Zeilen im `.lb-page`-Block entfernen — die Seite läuft dann in der Theme-Breite.
- **Kein Header/Footer:** Bewusst nicht enthalten — Theme-Header, Navigation, Footer und
  Cookie-Banner bleiben unverändert bestehen.
- **CSS-Isolation:** Alle Klassen sind mit `lb-` präfixiert und sämtliche Regeln unter `.lb-page`
  gescoped. Konflikte mit Theme-Styles sind damit unwahrscheinlich; umgekehrt setzt ein kleiner
  Reset die Theme-Defaults innerhalb des Blocks zurück.
- **Schriften:** Montserrat (Headlines) und Roboto (Fließtext) lädt das Theme bereits — der
  `<link>` auf Google Fonts im `<head>` ist nur für die lokale Vorschau nötig und wird beim
  Kopieren nicht mit übernommen.
- **Farben:** Übernommen aus dem Theme (`--rh--color--ci: #29abe2`, Sekundär `#6d6e71`).
- **Telefon/E-Mail:** Aktuell hart als `+49 7153 92508-0` und `info@logbatt.de` hinterlegt.
  Wenn das Call-Tracking von RegioHelden greifen soll, die Werte durch die Platzhalter
  `[ProxyNumber]` bzw. `[customer.email]` ersetzen — vorher testen, ob die Ersetzung auch in
  Custom-HTML-Blöcken läuft.
- **Bilder/Video:** Es werden ausschließlich bereits vorhandene Assets der Mediathek verlinkt
  (absolute URLs auf `www.logbatt.de`). Nichts muss neu hochgeladen werden.
- **News-Sektion:** Statt des dynamischen `latest-posts`-Blocks stehen dort drei feste
  Einstiegskarten. Wer die drei neuesten Beiträge dynamisch will, setzt den WP-Block direkt
  unter den Custom-HTML-Block und löscht die `<section id="news">`.
- **Barrierefreiheit/Performance:** `prefers-reduced-motion` wird respektiert, Bilder sind
  `loading="lazy"`, YouTube lädt erst auf Klick, alle interaktiven Elemente sind fokussierbar
  und tastaturbedienbar.

## Inhaltliche Quellen

Alle Fakten stammen aus diesem Repository (`website/de/startseite.html`, `website/de/lagerbehaelter.html`,
`website/de/_index.md`) bzw. der Live-Seite. Zwei Stellen mit widersprüchlichen Angaben im Ist-Stand:

- **L-Storage Zuladung:** Übersichtstabelle und JSON-LD auf `/lagerbehaelter/` nennen **350 kg**,
  die Produktdetailseite 357 kg. Hier ist 350 kg übernommen.
- **9.000+ Transporte:** wie auf der Ist-Startseite formuliert („mit grünen, gelben und roten
  Batterien aller Umfänge").

## Vorschau erneuern

`index.html` lokal im Browser öffnen. Die Seite ist vollständig eigenständig; es wird nur auf
`www.logbatt.de` für Bilder/Video und (in der Vorschau) auf Google Fonts zugegriffen.
