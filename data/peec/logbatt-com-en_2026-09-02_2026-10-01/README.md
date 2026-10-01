# Peec AI export – logbatt.com (English prompts), 2026-09-02 → 2026-10-01

Uploaded 2026-10-01 (originally dropped in the repo root as `chatsexportlogbatt… (N).xlsx` and
`source-urls-top-10000export….xlsx`; renamed/moved here with `git mv`, content unchanged).

Analysis: [`notes/geo-analysis-com-hardware-2026-10-01.md`](../../../notes/geo-analysis-com-hardware-2026-10-01.md)

## Contents

```
chats/raw/<prompt-slug>.xlsx   15 chat exports, one per tracked English prompt
                               (30 days × 3 engines = 90 rows each; 1,350 rows total)
prompt-metrics.csv             derived: visibility per prompt/engine for LogBATT, DENIOS, Zarges,
                               Chemstore + how often logbatt.* was a cited source + shopping-module share
source-urls/
  source-urls-2026-09-02_2026-10-01.xlsx   raw Peec source-URL export (1,765 URLs, not only 100)
  top-100-urls.csv                         derived: top 100 URLs by `retrievals`
  logbatt-urls.csv                         derived: all logbatt.* and lagermax.com URLs in the export
```

## Engines and period

- Engines: `chatgpt-ui`, `gemini-ui`, `google-ai-overview` (no Perplexity in this export, unlike the
  German July/August data).
- `created` runs 2026-09-01 23:00 → 2026-09-30 23:00 UTC (= 2 Sep – 1 Oct CEST), 30 daily runs.
- 49 of 1,350 rows have no answer (engine returned nothing); they are excluded from rates.

## Prompt clusters (as used in the analysis)

| Cluster | Prompts |
| --- | --- |
| `hardware-buy` | What transport boxes are available…, Which containers are suitable for storing…, What is the best transport box…, Which suppliers sell safety boxes for damaged…, Provider of quarantine boxes…, Which suppliers sell dangerous goods boxes for high-voltage…, Which suppliers offer transport crates… |
| `hardware-rent` | Providers of storage containers … for rent, Where can I rent quarantine boxes…, Which company rents out dangerous goods boxes… |
| `service` | disposal / transport / Europe-wide collection / after-fire prompts (5) |

The clustering is ours, not Peec's (the export has no topic column).

## Column notes / caveats

- Chat exports: same schema as the German exports (see `../README.md`), plus `content_in_chat`
  (`WEB_SEARCH`, `SHOPPING`, `MAP` – which answer modules were shown).
- Source-URL export: `retrievals` = number of answers in which the URL was retrieved;
  `retrieved_percentage` = retrievals / ~1,300 answered chats; `citation_rate` = Peec metric,
  apparently average citations per retrieval (not documented in the export – **unverified**).
  `mentioned` = the page itself mentions LogBATT; `mentions` = tracked brands named on the page
  (interpretation inferred from the data, **not confirmed by Peec docs**).
- `domain_classification` is Peec's: note that `lagermax.com` (LogBATT's parent group) is
  classified as `UGC` – it is effectively an owned channel.
- The answers are strongly **UK-localised** (64 % of answers frame the reply for the UK / use £;
  ChatGPT 91 %), and most cited sources are `.co.uk`/`gov.uk`. This suggests the Peec project for
  logbatt.com is configured with a UK location – **please confirm in Peec**; it changes which
  competitors are relevant.
