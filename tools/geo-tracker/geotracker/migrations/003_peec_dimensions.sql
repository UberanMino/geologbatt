-- 003 — Dimensionen, die das Dashboard im Peec-Zuschnitt braucht
--
-- `source_type` (owned/competitor/earned_media/other) bleibt die
-- Handlungsachse: "gehört uns / gehört der Konkurrenz / verdient / Rest".
-- `domain_type` ist die feinere ART der Quelle (Corporate, Institutional,
-- UGC, Editorial, Reference, Marketplace). Beide sind unabhängig:
-- eine Wettbewerber-Domain ist source_type=competitor UND domain_type=corporate.

ALTER TABLE domains ADD COLUMN domain_type TEXT NOT NULL DEFAULT 'corporate';

CREATE INDEX idx_domains_domain_type ON domains (domain_type);

-- URL-Typ je Citation (Product Page, How-To Guide, Article, …). Wird aus dem
-- Pfad abgeleitet und ist deshalb nur bei URL-genauen Zitaten belastbar;
-- Domain-only-Zitate (Peec-Import) bekommen 'unknown'.
ALTER TABLE citations ADD COLUMN url_type TEXT NOT NULL DEFAULT 'unknown';

CREATE INDEX idx_citations_url_type ON citations (url_type);

-- Prompt-Dimensionen aus der Peec-Master-Liste: Branding, Intent, Tags.
-- Alle bisher getrackten Prompts sind laut Master-Liste non-branded.
ALTER TABLE prompts ADD COLUMN branding TEXT NOT NULL DEFAULT 'non-branded';
ALTER TABLE prompts ADD COLUMN intent TEXT;
ALTER TABLE prompts ADD COLUMN tags TEXT NOT NULL DEFAULT '[]';
