-- 001_initial.sql — Grundschema GEO-Visibility-Tracker
--
-- ZWEI STRIKT GETRENNTE EBENEN:
--
--   Ebene 1 (Source of Truth, KI-unabhängig): prompts, runs, citations, domains
--     Wird beim Scrapen geschrieben. Kein Schreibpfad hier hängt vom
--     Auswertungs-Layer ab; fällt Ebene 2 aus, sind die Rohdaten trotzdem
--     vollständig.
--
--   Ebene 2 (Auswertung, wiederholbar): evaluations, brand_mentions
--     Wird ausschließlich aus gespeicherten Ebene-1-Daten abgeleitet und darf
--     jederzeit neu erzeugt werden. Deshalb hängen beide Tabellen per
--     ON DELETE CASCADE an evaluations bzw. runs: ein neuer Auswertungslauf
--     legt eine NEUE evaluations-Zeile an, überschreibt nichts.
--
--   brands liegt dazwischen: geseedet in Ebene 1 (bekannte Wettbewerber),
--   ergänzt von Ebene 2 (offene Entdeckung, is_known = 0).

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Ebene 1 — Prompts
-- ---------------------------------------------------------------------------
CREATE TABLE prompts (
    id          INTEGER PRIMARY KEY,
    text        TEXT    NOT NULL,
    category    TEXT    NOT NULL,           -- Themen-Cluster (= Peec topic_name)
    country     TEXT    NOT NULL,           -- ISO-3166-1 alpha-2, Großschreibung
    language    TEXT    NOT NULL,           -- ISO-639-1, klein
    engines     TEXT    NOT NULL,           -- JSON-Array, z. B. ["chatgpt","perplexity"]
    active      INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL,           -- ISO-8601 UTC

    -- Ein Prompt-Text kann bewusst mehrfach existieren, aber nur einmal je
    -- Land/Sprache — sonst zählen wir dieselbe Frage doppelt.
    UNIQUE (text, country, language),
    CHECK (country = upper(country) AND length(country) = 2),
    CHECK (language = lower(language)),
    CHECK (active IN (0, 1)),
    CHECK (json_valid(engines))
);

CREATE INDEX idx_prompts_active   ON prompts (active);
CREATE INDEX idx_prompts_category ON prompts (category);
CREATE INDEX idx_prompts_country  ON prompts (country);

-- ---------------------------------------------------------------------------
-- Ebene 1 — Runs (ein Lauf = Prompt x Engine x Land x Zeitpunkt)
-- ---------------------------------------------------------------------------
-- Jeder Lauf legt eine NEUE Zeile an. Es gibt bewusst KEINEN UNIQUE-Constraint
-- auf (prompt_id, engine, country, run_date): mehrere Läufe am selben Tag sind
-- erlaubt (Nachlauf nach Fehler, Ad-hoc-Prüfung) und dürfen sich nicht
-- gegenseitig überschreiben. Die Deduplizierung "ein Lauf pro Tag" passiert im
-- Ingest-Code, nicht im Schema.
CREATE TABLE runs (
    id                  INTEGER PRIMARY KEY,
    prompt_id           INTEGER NOT NULL REFERENCES prompts (id) ON DELETE CASCADE,
    engine              TEXT    NOT NULL,   -- chatgpt | perplexity | gemini | google_ai_overview
    country             TEXT    NOT NULL,   -- Kopie aus prompts: Läufe bleiben auswertbar,
                                            -- auch wenn der Prompt später geändert wird
    language            TEXT    NOT NULL,   -- dito
    run_date            TEXT    NOT NULL,   -- YYYY-MM-DD (UTC), die Zeitreihen-Achse
    status              TEXT    NOT NULL,   -- siehe CHECK unten

    -- ---- Rohdaten (Source of Truth) --------------------------------------
    raw_response        TEXT,               -- VOLLER Antworttext als Markdown
    raw_payload         TEXT,               -- komplette Provider-JSON-Antwort, unverändert.
                                            -- Ermöglicht Re-Parsing (z. B. neuer Citation-
                                            -- Parser) ohne erneutes Scrapen.

    -- ---- Provider-/Transport-Metadaten -----------------------------------
    provider_search_id  TEXT,               -- search_metadata.id bei SearchApi
    provider_model      TEXT,               -- response_metadata.model, z. B. "gpt-5-5"
    web_search_performed INTEGER,           -- response_metadata.is_web_search_performed
    request_url         TEXT,               -- angefragte URL OHNE api_key (nie Secrets speichern)
    http_status         INTEGER,
    attempts            INTEGER NOT NULL DEFAULT 1,
    latency_ms          INTEGER,
    error               TEXT,               -- Fehlermeldung bei status = error/deferred
    requested_at        TEXT    NOT NULL,   -- ISO-8601 UTC
    completed_at        TEXT,

    -- success  = Antworttext vorhanden
    -- partial  = Antworttext vorhanden, aber unvollständig (z. B. Quellen fehlten)
    -- deferred = Provider hat die Anfrage zurückgestellt/kein Ergebnis geliefert
    --            (z. B. Google AI Overview ohne Overview) -> protokolliert, nicht verloren
    -- error    = Transport-/Parsingfehler, raw_payload wird wenn möglich trotzdem gespeichert
    CHECK (status IN ('success', 'partial', 'deferred', 'error')),
    CHECK (web_search_performed IS NULL OR web_search_performed IN (0, 1))
);

CREATE INDEX idx_runs_prompt   ON runs (prompt_id, run_date);
CREATE INDEX idx_runs_date     ON runs (run_date);
CREATE INDEX idx_runs_engine   ON runs (engine, run_date);
CREATE INDEX idx_runs_country  ON runs (country, run_date);
CREATE INDEX idx_runs_status   ON runs (status);

-- ---------------------------------------------------------------------------
-- Brands (Seed in Ebene 1, Erweiterung durch Ebene 2)
-- ---------------------------------------------------------------------------
CREATE TABLE brands (
    id             INTEGER PRIMARY KEY,
    name           TEXT    NOT NULL UNIQUE,
    aliases        TEXT    NOT NULL DEFAULT '[]',  -- JSON-Array von Schreibweisen
    is_known       INTEGER NOT NULL DEFAULT 0,     -- 1 = geseedet, 0 = von Ebene 2 entdeckt
    is_own_brand   INTEGER NOT NULL DEFAULT 0,     -- LogBATT
    is_competitor  INTEGER NOT NULL DEFAULT 1,     -- 0 = Partner (z. B. Lithium Safety Containers)
    first_seen_at  TEXT    NOT NULL,
    notes          TEXT,

    CHECK (is_known IN (0, 1)),
    CHECK (is_own_brand IN (0, 1)),
    CHECK (is_competitor IN (0, 1)),
    CHECK (json_valid(aliases))
);

-- Zuordnung Domain -> Marke. Getrennt von `domains`, weil eine Marke mehrere
-- Domains hat (logbatt.de + logbatt.com) und Domains geseedet sein können,
-- bevor sie je zitiert wurden.
CREATE TABLE brand_domains (
    id        INTEGER PRIMARY KEY,
    brand_id  INTEGER NOT NULL REFERENCES brands (id) ON DELETE CASCADE,
    domain    TEXT    NOT NULL UNIQUE,
    CHECK (domain = lower(domain))
);

-- ---------------------------------------------------------------------------
-- Ebene 1 — Domain-Register (offene Entdeckung)
-- ---------------------------------------------------------------------------
-- Jede jemals zitierte Domain bekommt hier genau eine Zeile — auch unbekannte.
-- Das ist die Grundlage für (a) das Domain-Ranking, (b) die "Neu entdeckt"-
-- Ansicht und (c) die re-runnable source_type-Klassifikation.
CREATE TABLE domains (
    id             INTEGER PRIMARY KEY,
    domain         TEXT    NOT NULL UNIQUE, -- normalisierter Host, ohne "www.", klein
    source_type    TEXT    NOT NULL DEFAULT 'other',
    is_known       INTEGER NOT NULL DEFAULT 0,  -- 0 = automatisch entdeckt, noch nicht eingeordnet
    classified_by  TEXT    NOT NULL DEFAULT 'auto', -- seed | auto | manual
    brand_id       INTEGER REFERENCES brands (id) ON DELETE SET NULL,
    first_seen_at  TEXT    NOT NULL,
    last_seen_at   TEXT,
    notes          TEXT,

    CHECK (source_type IN ('owned', 'competitor', 'earned_media', 'other')),
    CHECK (is_known IN (0, 1)),
    CHECK (domain = lower(domain))
);

CREATE INDEX idx_domains_source_type ON domains (source_type);
CREATE INDEX idx_domains_first_seen  ON domains (first_seen_at);

-- ---------------------------------------------------------------------------
-- Ebene 1 — Citations (JEDE zitierte Quelle als eigene Zeile, roh)
-- ---------------------------------------------------------------------------
CREATE TABLE citations (
    id             INTEGER PRIMARY KEY,
    run_id         INTEGER NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    cited_url      TEXT    NOT NULL,        -- URL wie vom Provider geliefert (roh)
    cited_domain   TEXT    NOT NULL,        -- normalisiert, = domains.domain
    title          TEXT,
    snippet        TEXT,
    citation_rank  INTEGER NOT NULL,        -- 1-basiert, Reihenfolge im Quellenblock

    -- source_type wird beim Ingest aus dem Domain-Register kopiert (denormalisiert,
    -- damit Dashboard-Queries nicht für jede Zeile joinen müssen). Bleibt konsistent,
    -- weil `reclassify-domains` beide Tabellen zusammen aktualisiert.
    source_type    TEXT    NOT NULL DEFAULT 'other',
    is_known       INTEGER NOT NULL DEFAULT 0,

    -- 'cited'     = Quelle, die die Antwort tatsächlich zitiert (SearchApi:
    --               reference_links). Das ist die Menge, auf der ALLE
    --               Citation-Metriken im Dashboard rechnen.
    -- 'retrieved' = von der Engine abgerufene, aber nicht zitierte Seite
    --               (SearchApi: web_results). Roh mitgespeichert, weil daraus
    --               ablesbar ist, wo wir zwar gefunden, aber nicht zitiert werden.
    origin         TEXT    NOT NULL DEFAULT 'cited',

    provider_source TEXT,                   -- Provider-Attribution ("Encyclopedia Britannica")
    provider_index  INTEGER,                -- 0-basierter index/position des Providers, roh
    ref_id          TEXT,                   -- z. B. "turn0search0" (ChatGPT)
    published_date  TEXT,                   -- ISO-8601, wenn geliefert
    raw_json        TEXT NOT NULL,          -- die einzelne Quellen-Entry roh
    created_at      TEXT NOT NULL,

    CHECK (source_type IN ('owned', 'competitor', 'earned_media', 'other')),
    CHECK (origin IN ('cited', 'retrieved')),
    CHECK (is_known IN (0, 1)),
    UNIQUE (run_id, origin, citation_rank)
);

CREATE INDEX idx_citations_run    ON citations (run_id);
CREATE INDEX idx_citations_domain ON citations (cited_domain, origin);
CREATE INDEX idx_citations_url    ON citations (cited_url);
CREATE INDEX idx_citations_type   ON citations (source_type, origin);

-- ---------------------------------------------------------------------------
-- Ebene 2 — Evaluations (wiederholbar; jeder Lauf = neue Zeile)
-- ---------------------------------------------------------------------------
-- Wird in Schritt 2 befüllt. Schema steht hier schon, damit die Migration
-- vollständig ist und Ebene 1 nie angefasst werden muss, wenn Ebene 2 startet.
CREATE TABLE evaluations (
    id                          INTEGER PRIMARY KEY,
    run_id                      INTEGER NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    logbatt_mentioned           INTEGER NOT NULL,
    logbatt_position            INTEGER,          -- = mention_rank von LogBATT, NULL wenn nicht genannt
    sentiment                   TEXT,             -- positive | neutral | negative
    problem_narrative_anchored  INTEGER,          -- LogBATT im Havarie-/Gefahrenkontext?
    share_of_voice              REAL,             -- LogBATT-Anteil an allen Brand-Nennungen des Laufs
    raw_classifier_output       TEXT NOT NULL,    -- rohes Modell-JSON, unverändert

    -- Wiederholbarkeit: ein erneuter Auswertungslauf legt eine neue Zeile an und
    -- setzt is_current der vorherigen auf 0. Nichts wird gelöscht, damit
    -- Logikänderungen nachvollziehbar bleiben.
    evaluator_version           TEXT NOT NULL,
    model                       TEXT,
    is_current                  INTEGER NOT NULL DEFAULT 1,
    created_at                  TEXT NOT NULL,

    CHECK (logbatt_mentioned IN (0, 1)),
    CHECK (sentiment IS NULL OR sentiment IN ('positive', 'neutral', 'negative')),
    CHECK (problem_narrative_anchored IS NULL OR problem_narrative_anchored IN (0, 1)),
    CHECK (is_current IN (0, 1))
);

CREATE INDEX idx_evaluations_run     ON evaluations (run_id, is_current);
CREATE INDEX idx_evaluations_current ON evaluations (is_current);

-- ---------------------------------------------------------------------------
-- Ebene 2 — Brand-Nennungen (Reihenfolge IM ANTWORTTEXT)
-- ---------------------------------------------------------------------------
CREATE TABLE brand_mentions (
    id             INTEGER PRIMARY KEY,
    run_id         INTEGER NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    evaluation_id  INTEGER NOT NULL REFERENCES evaluations (id) ON DELETE CASCADE,
    brand_id       INTEGER NOT NULL REFERENCES brands (id) ON DELETE CASCADE,
    mention_rank   INTEGER NOT NULL,   -- 1-basiert, Reihenfolge des Auftretens im Antworttext
    mention_text   TEXT,               -- die im Text gefundene Schreibweise (roh)

    UNIQUE (evaluation_id, brand_id),
    UNIQUE (evaluation_id, mention_rank)
);

CREATE INDEX idx_brand_mentions_run   ON brand_mentions (run_id);
CREATE INDEX idx_brand_mentions_brand ON brand_mentions (brand_id);
