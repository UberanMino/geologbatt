# GEO analysis logbatt.com – why we lose the hardware (buy) prompts

Date: 2026-10-01 · Data: Peec AI, logbatt.com project, 2026-09-02 → 2026-10-01
(`data/peec/logbatt-com-en_2026-09-02_2026-10-01/`) + live crawl of logbatt.com and competitor
pages on 2026-10-01.

Confidence labels used below: **[data]** = computed directly from the export, **[crawl]** =
checked on the live page today, **[inference]** = my interpretation, plausible but not proven.

---

## 1. TL;DR

1. **LogBATT wins rental and service prompts but loses buy prompts.** Visibility in the 7
   "buy / which box / best box" prompts is **16 %** vs. Zarges 70 %, DENIOS 50 %, Chemstore 38 %.
   In the 3 rental prompts LogBATT has **74 %** (Zarges 10 %). **[data]**
2. **What decides a mention is whether logbatt.com is retrieved.** In buy prompts LogBATT is
   named in **80 %** of answers where a logbatt.* page was a source (74/92) and in **4 %** where it
   was not (21/510). So the problem is mostly **retrieval**, not how we are described. **[data]**
   (This is correlation. That retrieval drives mentions is an **[inference]**, but a strong one.)
3. **LogBATT gets retrieved about as often as DENIOS, but for the wrong intents.** In total,
   logbatt.* gets 581 retrievals and DENIOS gets 581. Ours go to rental (123), disposal (96) and
   category pages. **The 9 SafetyBATTbox product pages got 6 retrievals in 30 days.** One Zarges
   product page (`battery-case-40582`) got 85 by itself. **[data]**
4. **The product pages are orphaned.** `/transport-crates/`, `/storage-containers/`, the sale page
   and the rental page contain **no link to any product detail page**. The product pages can only
   be found through the sitemap and through each other. **[crawl]**
5. **The answers are written for the UK, and every competitor that wins has a UK presence.** Examples:
   `denios.co.uk` (shop with £ prices), `zarges.com/uk/` + `zargescases.co.uk`, `chemstore.co.uk`,
   `oneillgmbh.co.uk` (a German company with a .co.uk site), plus UK resellers. ChatGPT literally
   writes "UK suppliers … include: Chemstore UK, ZARGES UK, DENIOS UK, O'Neill GmbH UK". LogBATT has
   no UK page, no £ prices and no UK resellers. **[data + crawl]**
6. **Zarges is #1 because of third-party distribution.** Zarges appears on **39 third-party pages
   across 17 domains** (550 retrievals), including denios.co.uk, gwp.co.uk, lion-care.com and
   rs-online.com. LogBATT appears on 7 third-party pages across 3 domains, mostly lion-care.com.
   **[data]**
7. **The English site still has German content in places that matter**, such as the title and
   meta description of the rental page, an H2 on the homepage and the sale page, and "Preis auf
   Anfrage" in the product schema. The product schema also has `price: "0"`. **[crawl]**

---

## 2. Data overview

- 15 English prompts × 3 engines (ChatGPT, Gemini, Google AI Overview) × 30 days = 1,350 rows,
  1,301 with an answer.
- Source-URL export: **1,765 URLs** (the file is "top 10000", not only the top 100). I extracted the
  top 100 by retrievals into `source-urls/top-100-urls.csv`.

### Visibility by cluster [data]

| Cluster | Answers | LogBATT | DENIOS | Zarges | Chemstore | logbatt.* cited | Shopping module shown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hardware-buy (7 prompts) | 602 | **16 %** | 50 % | **70 %** | 38 % | 15 % | 35 % |
| hardware-rent (3 prompts) | 253 | **74 %** | 35 % | 10 % | 21 % | 69 % | 1 % |
| service (5 prompts) | 446 | 32 % | 0 % | 1 % | 0 % | 26 % | 0 % |

### Buy prompts in detail [data]

| Prompt | LogBATT | DENIOS | Zarges | Chemstore | Ø pos. LogBATT |
| --- | ---: | ---: | ---: | ---: | ---: |
| What transport boxes are available for lithium batteries? | 0 % | 31 % | 52 % | 10 % | – |
| Which containers are suitable for storing lithium batteries? | 0 % | 11 % | 28 % | 12 % | – |
| What is the best transport box for lithium-ion batteries? | 4 % | 29 % | 60 % | 4 % | 1.3 |
| Which suppliers sell safety boxes for damaged lithium batteries? | 9 % | 68 % | 95 % | 76 % | 3.9 |
| Provider of quarantine boxes for lithium-ion batteries | 22 % | 73 % | 73 % | 76 % | 3.1 |
| Which suppliers sell dangerous goods boxes for high-voltage batteries? | 34 % | 60 % | 95 % | 40 % | 2.5 |
| Which suppliers offer transport crates for lithium-ion batteries? | 40 % | 76 % | 88 % | 47 % | 3.1 |

Notes:
- Even when LogBATT is mentioned in buy prompts, it usually comes **3rd or 4th**. In rental and
  service prompts it is almost always 1st.
- "High-voltage batteries" is our best buy prompt, especially on Google AI Overview (73 %). The more
  specific the prompt is to EV or industrial use, the better LogBATT does.
- Week-by-week (KW 36–40), buy-prompt visibility moves between 12 % and 20 % with no clear trend. The
  optimized `/transport-crates/` page has been live since mid-August, so this period shows its
  effect. On its own, the page has not closed the gap. **[data]**

---

## 3. Why we lose: root causes

### 3.1 Product pages aren't reachable, so engines can't retrieve them [crawl + data]

- I checked every `<a href>` (navigation included) on `/`, `/transport-crates/`,
  `/storage-containers/`, `/transport-crates/sale-of-…/` and `/transport-crates/storage-container-leasing/`.
  **None of them link to a `/safetybattbox-…/` product page.** The product overview on
  `/transport-crates/` only links to anchors on the same page (`#safety-batt-box-xl` etc.).
  This includes the version we optimized in `optimized/en/transport-crates.html`.
- The `ItemList`/`Product` JSON-LD on the category pages has no `url` pointing to the product pages.
- Result: the product pages got 6 retrievals in 30 days. Competitors' product pages
  (Zarges battery case 85, Zarges 40583 53, DENIOS "Transport and Quarantine Solutions" 81 + "Transport box XL" 54, Chemstore battery box 94,
  Air Sea 4G box 26) are exactly what the engines cite in buy answers.
- Also found: `/storage-containers/` links to `/transport-crates/rent-storage-boxes/`, which
  returns **404**.

### 3.2 The engines answer for the UK, and our competitors look local [data + crawl + inference]

- 64 % of all answers frame the reply for the UK or use £ (ChatGPT 91 %, AI Overview 62 %, Gemini
  38 %). Most cited sources are `gov.uk`, `.co.uk` vendors and UK waste firms. I infer that the Peec
  project runs with a **UK location**. Please confirm this in Peec.
- The winners all have a UK entity, domain or subfolder: DENIOS UK (shop with prices),
  ZARGES `/uk/` + UK distributor `zargescases.co.uk`, Chemstore (UK), O'Neill (`oneillgmbh.co.uk`),
  Safelincs and GWP (UK).
- logbatt.com has a single `hreflang="en"` and no `en-GB` variant. There is no UK-specific content
  (except a UK regulations FAQ on `/storage-containers/`), no £ prices, no UK delivery or lead-time
  statement, and contact goes to `info@logbatt.de`. From here, `logbatt.co.uk` and `logbatt.uk` did
  not resolve (this could be the network proxy, so it is unverified).
- To an engine looking for "UK suppliers", LogBATT therefore looks like a German logistics company
  that also has boxes.

### 3.3 Our competitors get named on many other websites; we don't [data]

| Brand | Own pages (retrievals) | 3rd-party pages naming the brand | 3rd-party domains |
| --- | ---: | ---: | ---: |
| Zarges | 33 (621) | **39 (550)** | **17** |
| DENIOS | 42 (580) | 5 (56) | 4 |
| Chemstore | 19 (332) | 1 (7) | 1 |
| LogBATT | 33 (676) | 7 (98) | 3 (lion-care.com, manufakturhub.com, instagram) |

Zarges is the only brand that gets significant reach from distributors and resellers:
denios.co.uk itself (226 retrievals on pages naming Zarges), gwp.co.uk, lion-care.com,
rs-online.com, kaiserkraft.co.uk, cases2go.com and others. That is the main reason Zarges is #1
overall (450 mentions) even though its own site is no stronger than DENIOS's. UK resellers listing
competitor or generic products also show up often in buy answers: thetankshop.co.uk, safelincs.co.uk,
pro-equip.co.uk, unimac.co.uk, empteezy.co.uk, kingfisherdirect.co.uk.

### 3.4 Engines see LogBATT as a large-format specialist [data + inference]

- When LogBATT is named in buy answers, it is described as the option for **"EV battery packs,
  industrial, critically defective, large-scale quarantine"**. Example: "If you're dealing with EV
  traction batteries or large battery packs, I'd look at DENIOS, LogBATT, Chemstore…".
- Generic prompts ("best transport box", "containers suitable for storing") are answered for
  **e-bike, power-tool and LiPo** sizes. 53 % of buy answers mention those small formats. We have
  S-1 (10 kg), S-1-lite (15 kg) and M-2 (30 kg), but these are the least visible pages, and nothing
  on our side presents them as an answer for small batteries.
- Competitors' boxes are linked to a recognizable named feature: **PyroBubbles** comes up in 45 %
  of buy answers (DENIOS, Chemstore, O'Neill, Zarges). LogBATT's own differentiators (45 real fire
  tests, P911/LP906 approval, extinguishing without water, gas management, LogBAGs) are rarely
  repeated in the answers. "Real fire test" appears in only 11 %.

### 3.5 Commerce signals: shopping modules and prices [data + inference, medium confidence]

- A shopping module appears in **35 %** of buy answers (58 % for "best transport box"). That is
  Google AI Overview product galleries and ChatGPT shopping. LogBATT cannot appear there without a
  priced product feed.
- Our product JSON-LD contains `"price": "0", "priceCurrency": "EUR"` with
  `"description": "Preis auf Anfrage"`. Machines can read that as "free", it is in German on .com,
  and it points `seller` to `https://www.logbatt.de/#organization`. **[crawl]**
- Prices are named in only 9 % of buy answers, so price is **not** the main driver. Shopping
  visibility is a secondary lever. Whether B2B price-on-request products can get into these
  modules at all is **unclear**; it would need a Merchant Center test.

### 3.6 Localization errors on logbatt.com [crawl]

| Page | Problem |
| --- | --- |
| `/transport-crates/storage-container-leasing/` (our most retrieved page, 123) | `<title>` "Vermietung von Gefahrgutboxen \| SafetyBATTbox \| LogBATT GmbH" and German meta description |
| `/` and `/transport-crates/sale-of-…/` | H2 "Lagerbehälter – Jetzt auch zur Miete verfügbar!" |
| All product pages | Title ends with "\| LogBATT GmbH \| LogBATT GmbH" (twice); offer description "Preis auf Anfrage" |
| `/transport-crates/` | Brochure link → `Produktbroschuere-de.pdf`; mail links `info@logbatt.de`, `training@logbatt.de` |
| `/transport-crates/safetybattbox-xl-2-2-2/` | Confusing slug (it is XL 2.2; `…-xl-2-2/` is XL-2.2+) |
| `https://www.logbatt.com/llms.txt` | Written in German and links to the staging host `117655.wd50.extern.regiohelden.de` (5×) and other ccTLDs. Low impact: there is little evidence that the major engines use llms.txt. Still easy to fix. |

---

## 4. What's working (keep it that way)

- **Rental:** `/transport-crates/storage-container-leasing/` is our most retrieved page
  (123 retrievals, citation rate 1.46), and the rental prompts are clearly ours (74 %).
- **lagermax.com/en/services/battery-logistics** has the **highest citation rate in the whole export
  (2.88)**, and its titles start with "LogBATT |". It is a strong second domain, but it is
  service-focused. Its `/transport-crates` subpage got only 6 retrievals.
- **"High-voltage" and EV wording**: the more specific the prompt is to EV or industrial use, the better
  we do (Google AI Overview 73 % on the high-voltage prompt).
- **lion-care.com** (distributor, see the news post "SafetyBATTboxes now available via LionCare")
  already provides 91 retrievals of third-party pages that name LogBATT. The distribution approach
  works.

---

## 5. Action plan (prioritized)

### P0: quick fixes on logbatt.com (days, no new content needed)

1. **Link the product pages.** On `/transport-crates/`, `/storage-containers/`, the sale page and
   the rental page, give every product card/row a crawlable `<a href>` to its detail page (e.g.
   "SafetyBATTbox XL 2.2 – details & specs →"). Add `"url"` to every `Product` in the `ItemList`
   JSON-LD. Add product links in the main navigation (Transport crates → 7 products,
   Storage containers → 3 products). Expected effect: product pages become retrievable for SKU-level
   buy answers. **[inference]**
2. **Translate the remaining German strings**: rental page title and meta description, the H2 on the
   homepage and sale page, "Preis auf Anfrage" → "Price on request", the English brochure PDF (if
   one exists), and English contact addresses.
3. **Fix the product schema**: remove `"price": "0"`. Either give a real price, a
   `priceSpecification` with a `minPrice`, or leave out `price` and keep "Price on request" only in
   visible text. Point `seller` to `https://www.logbatt.com/#organization`. Remove the doubled
   "| LogBATT GmbH".
4. **Fix the 404** `/transport-crates/rent-storage-boxes/` (link it to the rental page).
5. **Rewrite llms.txt** for logbatt.com in English, with .com URLs only and no staging host.

### P1: content (2–6 weeks)

6. **Upgrade the 10 product pages into answer pages** (currently ~800 words each). Each page needs
   a "Who is this box for?" paragraph with battery types and sizes in Wh/kg (e-bike, power tool,
   module, EV pack); the approved packing instructions (P903/P908/P911, LP904–906) and the BAM
   number in the first lines; dimensions, payload and tare; delivery to the UK/EU with lead time;
   buy/rent; a fire-test video; and "compare with" links to the neighbouring sizes.
7. **Build a selection guide / comparison page**, for example "How to choose a lithium battery
   transport box: P903 vs P908 vs P911, by battery size". Include a criteria table (packing
   instruction, payload, fire-tested yes/no, filling/extinguishing system, approval number, buy/rent)
   that covers **all sizes from S-1 to XL-2.2+**. This targets "best box", "which boxes are
   available" and "which containers are suitable", where we are at 0–4 %. Compare criteria
   neutrally and don't attack other brands by name.
8. **Add a UK page** (e.g. `/uk/` or "Lithium battery transport and storage boxes for the UK"),
   covering delivery to GB/NI, CDG Regulations/ADR in GB, how the BAM design-type approval is
   handled for UK carriage (**our dangerous-goods officer has to verify this; I'm not certain**),
   VCA as the UK competent authority, the UK regulations already on the storage page (COSHH, DSEAR,
   fire risk assessment), UK references if there are any, and GBP indicative prices if the business
   agrees. Add `en-GB` hreflang if a separate GB version is created.
9. **Give our features fixed names and use them everywhere.** Pick one English name for the
   extinguishing/filling system and the gas management, and repeat it with the evidence ("45 real
   fire tests", "approved procedure P911/LP906", "DOT Special Permit") on every product page. The
   goal is a recognizable term on our side, comparable to "PyroBubbles" on theirs.

### P2: off-site and distribution (1–3 months)

10. **Get listed with UK resellers and distributors.** This is the lever behind Zarges's lead. The
    candidates below come from the data and haven't been vetted: safety and DG-packaging resellers
    that the engines already cite (thetankshop.co.uk, safelincs.co.uk, pro-equip.co.uk,
    unimac.co.uk, kingfisherdirect.co.uk, kitepackaging.co.uk, gwp.co.uk, rs-online.com,
    kaiserkraft.co.uk). Each listing should have its own SafetyBATTbox product page that names
    LogBATT.
11. **Lagermax:** have `lagermax.com/en/services/battery-logistics/transport-crates` and
    `/storage-containers` list the products with specs and link to the logbatt.com product pages.
    That domain is already highly trusted (citation rate 2.88).
12. **YouTube**: YouTube got 139 retrievals in this export, and a DENIOS video gets cited. Publish
    the fire-test videos with English titles and descriptions, e.g. "SafetyBATTbox XL-2.2 fire test
    – P911 critically defective EV battery", with links to the product pages.
13. **UK trade presence**: press releases and articles on UK battery, recycling and fleet portals
    (UK-relevant cases, e.g. from Febelauto/Recupbat-type projects).
14. **Optional, after confirming UK sales:** Merchant Center feed / product listings with prices for
    the small boxes (S-1, S-1-lite, M-2), so they can appear in shopping modules.

### Measurement

- Track in Peec: buy-cluster visibility (baseline **16 %**), LogBATT position in buy answers
  (baseline ~3), and how often product-detail URLs are retrieved (baseline **6 / 30 days**).
- Add buy prompts that include sizes and use cases, e.g. "transport box for e-bike batteries UK",
  "P911 box for damaged EV battery", "buy UN-approved box for damaged lithium batteries".
- If the UK location is only a Peec default, consider adding a second location (e.g. US or IE/EU
  English) so we don't optimize for the UK alone.

---

## 6. Open questions for LogBATT

1. Is the Peec project for logbatt.com deliberately set to the **UK**? Is the UK a target market
   for buying boxes?
2. Do we deliver to GB/NI, and are BAM-approved SafetyBATTboxes usable for UK carriage without
   further steps (especially P911/LP906)?
3. Can we publish indicative prices (at least for S-1/S-1-lite/M-2), or at least "from €/£ …"?
4. Is there an English product brochure PDF?
5. Do we have, or want, UK resellers or distributors? The LionCare partnership is the model.

---

## 7. Implementation status

- **2026-10-02 – P0 #1 (product links) on `/transport-crates/` and `/storage-containers/`: done**
  in `optimized/en/transport-crates.html` and `optimized/en/storage-containers.html`.
  - Base: the real editor versions incl. product carousel, from branch
    `claude/geo-spanish-storage-transport-udvkki` (commit 1234baa, 2026-09-18). This branch had
    started from an older state without the carousel. The earlier reconstruction attempts
    (2026-10-01/02) are obsolete.
  - Only changes: the box titles (H4) in the product overview link to the product pages, and each
    `Product` in the JSON-LD has a `url`. On transport-crates, the old XL-lite `url` is removed
    (it redirected to logbatt.se). On storage-containers, the 404 link
    `/transport-crates/rent-storage-boxes/` now points to `/transport-crates/storage-container-leasing/`.
    The carousels are unchanged.
  - The live slugs are swapped relative to the names: `/transport-crates/safetybattbox-xl-2-2/` =
    **XL-2.2+**, `/transport-crates/safetybattbox-xl-2-2-2/` = **XL 2.2**. The links follow the live
    pages.
  - **XL-lite has no English product page**, so its title stays unlinked.
